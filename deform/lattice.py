# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# ND (Non-Destructive) Blender Add-on
# Copyright (C) 2024 Tristan S. & Ian J. (HugeMenace)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# 
# ---
# Contributors: Tristo (HM)
# ---

import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.collections import move_to_utils_collection, isolate_in_utils_collection, hide_utils_collection
from .. lib.math import generate_bounding_box, v3_average
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, rectify_smooth_by_angle


mod_lattice = "Lattice — ND L"
mod_summon_list = [mod_lattice]


class ND_OT_lattice(bpy.types.Operator):
    bl_idname = "nd.lattice"
    bl_label = "Lattice"
    bl_description = """Adds a lattice modifier to the selected object
CTRL — Remove existing modifiers"""
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        elif self.key_toggle_pin_overlay:
            toggle_pin_overlay(self, event)

        elif self.operator_passthrough:
            update_overlay(self, context, event)

            return {'PASS_THROUGH'}

        elif self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        elif self.key_numeric_input:
            if self.key_no_modifiers:
                self.lattice_points_u_input_stream = update_stream(self.lattice_points_u_input_stream, event.type)
                self.lattice_points_u = get_stream_value(self.lattice_points_u_input_stream, min_value=2)

                if self.uniform:
                    self.lattice_points_v_input_stream = self.lattice_points_u_input_stream
                    self.lattice_points_w_input_stream = self.lattice_points_u_input_stream

                    self.lattice_points_v = self.lattice_points_u
                    self.lattice_points_w = self.lattice_points_u

                self.dirty = True
            elif self.key_alt:
                self.lattice_points_v_input_stream = update_stream(self.lattice_points_v_input_stream, event.type)
                self.lattice_points_v = get_stream_value(self.lattice_points_v_input_stream, min_value=2)
                self.dirty = True
            elif self.key_ctrl:
                self.lattice_points_w_input_stream = update_stream(self.lattice_points_w_input_stream, event.type)
                self.lattice_points_w = get_stream_value(self.lattice_points_w_input_stream, min_value=2)
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.lattice_points_u_input_stream = new_stream()
                self.lattice_points_u = 2

                if self.uniform:
                    self.lattice_points_v_input_stream = new_stream()
                    self.lattice_points_w_input_stream = new_stream()
                    self.lattice_points_v = 2
                    self.lattice_points_w = 2

                self.dirty = True
            elif self.key_alt:
                self.lattice_points_v_input_stream = new_stream()
                self.lattice_points_v = 2
                self.dirty = True
            elif self.key_ctrl:
                self.lattice_points_w_input_stream = new_stream()
                self.lattice_points_w = 2
                self.dirty = True

        elif pressed(event, {'U'}):
            self.uniform = not self.uniform

            if self.uniform:
                self.lattice_points_v_input_stream = self.lattice_points_u_input_stream
                self.lattice_points_w_input_stream = self.lattice_points_u_input_stream

                self.lattice_points_v = self.lattice_points_u
                self.lattice_points_w = self.lattice_points_u
            else:
                self.lattice_points_v_input_stream = new_stream()
                self.lattice_points_w_input_stream = new_stream()

            self.dirty = True

        elif pressed(event, {'M'}):
            self.interpolation_mode = (self.interpolation_mode + 1) % len(self.interpolation_modes)
            self.dirty = True

        elif self.key_step_up:
            if no_stream(self.lattice_points_u_input_stream) and self.uniform:
                self.lattice_points_u += 1
                self.lattice_points_v = self.lattice_points_u
                self.lattice_points_w = self.lattice_points_u
                self.dirty = True
            elif not self.uniform:
                if no_stream(self.lattice_points_u_input_stream) and self.key_no_modifiers:
                    self.lattice_points_u += 1
                    self.dirty = True
                elif no_stream(self.lattice_points_v_input_stream) and self.key_alt:
                    self.lattice_points_v += 1
                    self.dirty = True
                elif no_stream(self.lattice_points_w_input_stream) and self.key_ctrl:
                    self.lattice_points_w += 1
                    self.dirty = True
        
        elif self.key_step_down:
            if no_stream(self.lattice_points_u_input_stream) and self.uniform:
                self.lattice_points_u = max(2, self.lattice_points_u - 1)
                self.lattice_points_v = self.lattice_points_u
                self.lattice_points_w = self.lattice_points_u
                self.dirty = True
            elif not self.uniform:
                if no_stream(self.lattice_points_u_input_stream) and self.key_no_modifiers:
                    self.lattice_points_u = max(2, self.lattice_points_u - 1)
                    self.dirty = True
                elif no_stream(self.lattice_points_v_input_stream) and self.key_alt:
                    self.lattice_points_v = max(2, self.lattice_points_v - 1)
                    self.dirty = True
                elif no_stream(self.lattice_points_w_input_stream) and self.key_ctrl:
                    self.lattice_points_w = max(2, self.lattice_points_w - 1)
                    self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.lattice_points_u_input_stream) and self.uniform:
                self.lattice_points_u = max(2, self.lattice_points_u + self.mouse_step)
                self.lattice_points_v = self.lattice_points_u
                self.lattice_points_w = self.lattice_points_u
                self.dirty = True
            elif not self.uniform:
                if no_stream(self.lattice_points_u_input_stream) and self.key_no_modifiers:
                    self.lattice_points_u = max(2, self.lattice_points_u + self.mouse_step)
                    self.dirty = True
                elif no_stream(self.lattice_points_v_input_stream) and self.key_alt:
                    self.lattice_points_v = max(2, self.lattice_points_v + self.mouse_step)
                    self.dirty = True
                elif no_stream(self.lattice_points_w_input_stream) and self.key_ctrl:
                    self.lattice_points_w = max(2, self.lattice_points_w + self.mouse_step)
                    self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}
        
        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND L')
            return {'FINISHED'}

        self.dirty = False

        self.uniform = True

        self.interpolation_mode = 0
        self.interpolation_modes = ['KEY_LINEAR', 'KEY_CARDINAL', 'KEY_CATMULL_ROM', 'KEY_BSPLINE']
        self.interpolation_labels = {'KEY_LINEAR': 'Linear', 'KEY_CARDINAL': 'Cardinal', 'KEY_CATMULL_ROM': 'Catmull-Rom', 'KEY_BSPLINE': 'B-Spline'}

        self.lattice_points_u = 2
        self.lattice_points_v = 2
        self.lattice_points_w = 2

        self.lattice_points_u_input_stream = new_stream()
        self.lattice_points_v_input_stream = new_stream()
        self.lattice_points_w_input_stream = new_stream()

        self.target_object = context.active_object

        mods = self.target_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if previous_op:
            self.summon_old_operator(context, mods)
        else:
            self.prepare_new_operator(context)

        if self.lattice_obj is None:
            bpy.ops.object.modifier_remove(modifier=self.lattice.name)
            self.prepare_new_operator(context)
        
        if self.summoned:
            isolate_in_utils_collection([self.lattice_obj])

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and context.active_object is not None:
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'


    def prepare_new_operator(self, context):
        self.summoned = False

        self.add_lattice_object(context)
        self.select_reference_object(context)
        self.add_lattice_modifier(context)

        rectify_smooth_by_angle(self.target_object)

    
    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.lattice = mods[mod_lattice]
        self.lattice_obj = self.lattice.object

        if self.lattice_obj:
            self.lattice_points_u = self.lattice_points_u_prev = self.lattice_obj.data.points_u
            self.lattice_points_v = self.lattice_points_v_prev = self.lattice_obj.data.points_v
            self.lattice_points_w = self.lattice_points_w_prev = self.lattice_obj.data.points_w
            self.interpolation_mode = self.interpolation_mode_prev = self.interpolation_modes.index(self.lattice_obj.data.interpolation_type_u)


    def add_lattice_object(self, context):
        bpy.ops.object.duplicate()

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.active_object.evaluated_get(depsgraph)
        context.active_object.modifiers.clear()

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        bm.to_mesh(context.active_object.data)
        bm.free()

        eval_obj = context.active_object

        coords = [vert for vert in eval_obj.data.vertices]
        box = generate_bounding_box(coords)
        center = v3_average(box)

        bpy.ops.object.add(type='LATTICE', enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))

        context.active_object.location = eval_obj.matrix_world @ center
        context.active_object.rotation_euler = eval_obj.rotation_euler
        context.active_object.name = "ND — Lattice"
        context.active_object.data.name = "ND — Lattice"
        context.active_object.data.use_outside = True

        if bpy.app.version >= (4, 1, 0):
            context.active_object.scale = eval_obj.dimensions * 1.001
        else:
            context.active_object.dimensions = eval_obj.dimensions * 1.001

        self.lattice_obj = context.active_object
        self.lattice_obj.parent = self.target_object
        self.lattice_obj.matrix_parent_inverse = self.target_object.matrix_world.inverted()

        bpy.data.meshes.remove(eval_obj.data, do_unlink=True)


    def select_reference_object(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.target_object.select_set(True)
        bpy.context.view_layer.objects.active = self.target_object


    def select_lattice_object(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.lattice_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.lattice_obj


    def add_lattice_modifier(self, context):
        lattice = new_modifier(context.active_object, mod_lattice, 'LATTICE', rectify=True)
        lattice.object = self.lattice_obj

        self.lattice = lattice

    
    def operate(self, context):
        self.lattice_obj.data.points_u = self.lattice_points_u
        self.lattice_obj.data.points_v = self.lattice_points_v
        self.lattice_obj.data.points_w = self.lattice_points_w
        
        interpolation_mode = self.interpolation_modes[self.interpolation_mode]
        self.lattice_obj.data.interpolation_type_u = interpolation_mode
        self.lattice_obj.data.interpolation_type_v = interpolation_mode
        self.lattice_obj.data.interpolation_type_w = interpolation_mode

        self.dirty = False


    def finish(self, context):
        move_to_utils_collection(self.lattice_obj)
        isolate_in_utils_collection([self.lattice_obj])
        self.select_lattice_object(context)

        unregister_draw_handler()


    def revert(self, context):
        if self.summoned:
            self.lattice_obj.data.points_u = self.lattice_points_u_prev
            self.lattice_obj.data.points_v = self.lattice_points_v_prev
            self.lattice_obj.data.points_w = self.lattice_points_w_prev

            interpolation_mode = self.interpolation_modes[self.interpolation_mode_prev]
            self.lattice_obj.data.interpolation_type_u = interpolation_mode
            self.lattice_obj.data.interpolation_type_v = interpolation_mode
            self.lattice_obj.data.interpolation_type_w = interpolation_mode

            hide_utils_collection(True)

        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.lattice.name)
            bpy.data.lattices.remove(self.lattice_obj.data, do_unlink=True)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self,
        "U Points: {}".format(self.lattice_points_u),
        "(±1)",
        active=(self.uniform or self.key_no_modifiers),
        alt_mode=False,
        mouse_value=True,
        input_stream=self.lattice_points_u_input_stream)

    draw_property(
        self,
        "V Points: {}".format(self.lattice_points_v),
        "Alt (±1)",
        active=(self.uniform or self.key_alt),
        alt_mode=False,
        mouse_value=True,
        input_stream=self.lattice_points_v_input_stream)

    draw_property(
        self,
        "W Points: {}".format(self.lattice_points_w),
        "Ctrl (±1)",
        active=(self.uniform or self.key_ctrl),
        alt_mode=False,
        mouse_value=True,
        input_stream=self.lattice_points_w_input_stream)

    draw_hint(
        self,
        "Uniform [U]: {}".format("Yes" if self.uniform else "No"),
        "Adjust all points uniformly")

    interpolation_mode = self.interpolation_modes[self.interpolation_mode]
    draw_hint(
        self,
        "Interpolation Mode [M]: {}".format(self.interpolation_labels[interpolation_mode]),
        "Linear, Cardinal, Catmull-Rom, B-Spline")


def register():
    bpy.utils.register_class(ND_OT_lattice)


def unregister():
    bpy.utils.unregister_class(ND_OT_lattice)
    unregister_draw_handler()
