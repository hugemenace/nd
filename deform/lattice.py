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
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.math import generate_bounding_box, v3_average
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, ensure_tail_mod_consistency
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, obj_is_mesh, ctx_objects_selected, app_minor_version
from .. lib.collections import hide_obj, unhide_obj, is_obj_hidden


mod_lattice = "Lattice — ND L"
mod_summon_list = [mod_lattice]


class ND_OT_lattice(BaseOperator):
    bl_idname = "nd.lattice"
    bl_label = "Lattice"
    bl_description = """Adds a lattice modifier to the selected object
CTRL — Remove existing modifiers"""
    bl_options = {'UNDO'}


    key_callbacks = {
        'U': lambda cls, context, event: cls.handle_toggle_uniform(context, event),
        'M': lambda cls, context, event: cls.handle_cycle_interpolation_mode(context, event),
    }

    modal_config = {
        'MOVEMENT_PASSTHROUGH': True,
        'ON_CANCEL': lambda cls, context: cls.revert(context),
        'ON_CONFIRM': lambda cls, context: cls.finish(context),
    }


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and obj_is_mesh(target_object) and ctx_objects_selected(context, 1)


    def do_modal(self, context, event):
        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.lattice_points_u_input_stream = update_stream(self.lattice_points_u_input_stream, event.type)
                self.lattice_points_u = int(get_stream_value(self.lattice_points_u_input_stream, min_value=2))

                if self.uniform:
                    self.lattice_points_v_input_stream = self.lattice_points_u_input_stream
                    self.lattice_points_w_input_stream = self.lattice_points_u_input_stream

                    self.lattice_points_v = self.lattice_points_u
                    self.lattice_points_w = self.lattice_points_u

                self.dirty = True
            elif self.key_alt:
                self.lattice_points_v_input_stream = update_stream(self.lattice_points_v_input_stream, event.type)
                self.lattice_points_v = int(get_stream_value(self.lattice_points_v_input_stream, min_value=2))
                self.dirty = True
            elif self.key_ctrl:
                self.lattice_points_w_input_stream = update_stream(self.lattice_points_w_input_stream, event.type)
                self.lattice_points_w = int(get_stream_value(self.lattice_points_w_input_stream, min_value=2))
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.lattice_points_u_input_stream) and self.hard_stream_reset or no_stream(self.lattice_points_u_input_stream):
                    self.lattice_points_u = 2

                if self.uniform:
                    if has_stream(self.lattice_points_u_input_stream) and self.hard_stream_reset or no_stream(self.lattice_points_u_input_stream):
                        self.lattice_points_v = 2
                        self.lattice_points_w = 2
                    self.lattice_points_v_input_stream = new_stream()
                    self.lattice_points_w_input_stream = new_stream()

                self.lattice_points_u_input_stream = new_stream()
                self.dirty = True
            elif self.key_alt:
                if has_stream(self.lattice_points_v_input_stream) and self.hard_stream_reset or no_stream(self.lattice_points_v_input_stream):
                    self.lattice_points_v = 2
                    self.dirty = True
                self.lattice_points_v_input_stream = new_stream()
            elif self.key_ctrl:
                if has_stream(self.lattice_points_w_input_stream) and self.hard_stream_reset or no_stream(self.lattice_points_w_input_stream):
                    self.lattice_points_w = 2
                    self.dirty = True
                self.lattice_points_w_input_stream = new_stream()

        if self.key_step_up:
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

        if self.key_step_down:
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


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        if event.ctrl:
            # Remove all lattice objects
            mods = [m for m in context.active_object.modifiers if m.name.endswith(' — ND L')]
            lattice_objs = [m.object for m in mods if m.type == 'LATTICE']
            for lattice_obj in lattice_objs:
                if lattice_obj and lattice_obj.type == 'LATTICE':
                    bpy.data.lattices.remove(lattice_obj.data, do_unlink=True)

            # Remove all lattice modifiers
            for mod in mods:
                context.active_object.modifiers.remove(mod)

            return {'FINISHED'}

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

        self.unhid_lattice_obj = False
        if self.summoned and self.lattice_obj:
            if is_obj_hidden(self.lattice_obj):
                self.unhid_lattice_obj = True
                unhide_obj(self.lattice_obj)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def handle_toggle_uniform(self, context, event):
        self.uniform = not self.uniform

        if self.uniform:
            self.lattice_points_v_input_stream = self.lattice_points_u_input_stream
            self.lattice_points_w_input_stream = self.lattice_points_u_input_stream

            self.lattice_points_v = self.lattice_points_u
            self.lattice_points_w = self.lattice_points_u
        else:
            self.lattice_points_v_input_stream = new_stream()
            self.lattice_points_w_input_stream = new_stream()


    def handle_cycle_interpolation_mode(self, context, event):
        self.interpolation_mode = (self.interpolation_mode + 1) % len(self.interpolation_modes)


    def prepare_new_operator(self, context):
        self.summoned = False

        self.add_lattice_object(context)
        self.select_reference_object(context)
        self.add_lattice_modifier(context)

        ensure_tail_mod_consistency(self.target_object)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.lattice = mods[mod_lattice]
        self.lattice_obj = self.lattice.object

        if self.lattice_obj:
            self.lattice_points_u = self.lattice_points_u_prev = self.lattice_obj.data.points_u
            self.lattice_points_v = self.lattice_points_v_prev = self.lattice_obj.data.points_v
            self.lattice_points_w = self.lattice_points_w_prev = self.lattice_obj.data.points_w
            self.interpolation_mode = self.interpolation_mode_prev = self.interpolation_modes.index(self.lattice_obj.data.interpolation_type_u)
            self.uniform = self.lattice_points_v == self.lattice_points_u and self.lattice_points_w == self.lattice_points_u

        if get_preferences().lock_overlay_parameters_on_recall:
            self.lattice_points_u_input_stream = set_stream(self.lattice_points_u)
            self.lattice_points_v_input_stream = set_stream(self.lattice_points_v)
            self.lattice_points_w_input_stream = set_stream(self.lattice_points_w)


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
        context.active_object.name = "Lattice"
        context.active_object.data.name = "Lattice"
        context.active_object.data.use_outside = True

        if app_minor_version() >= (4, 1):
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


    def finish(self, context):
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

            if self.unhid_lattice_obj:
                hide_obj(self.lattice_obj)

        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.lattice.name)
            bpy.data.lattices.remove(self.lattice_obj.data, do_unlink=True)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"U Points: {self.lattice_points_u}",
        "(±1)",
        active=(self.uniform or self.key_no_modifiers),
        alt_mode=False,
        mouse_value=True,
        input_stream=self.lattice_points_u_input_stream)

    draw_property(
        self,
        f"V Points: {self.lattice_points_v}",
        "Alt (±1)",
        active=(self.uniform or self.key_alt),
        alt_mode=False,
        mouse_value=True,
        input_stream=self.lattice_points_v_input_stream)

    draw_property(
        self,
        f"W Points: {self.lattice_points_w}",
        "Ctrl (±1)",
        active=(self.uniform or self.key_ctrl),
        alt_mode=False,
        mouse_value=True,
        input_stream=self.lattice_points_w_input_stream)

    draw_hint(
        self,
        f"Uniform [U]: {self.yes_no_str(self.uniform)}",
        "Adjust all points uniformly")

    interpolation_mode = self.interpolation_modes[self.interpolation_mode]
    draw_hint(
        self,
        f"Interpolation Mode [M]: {self.interpolation_labels[interpolation_mode]}",
        self.list_options_str(self.interpolation_labels.values()))


def register():
    bpy.utils.register_class(ND_OT_lattice)


def unregister():
    bpy.utils.unregister_class(ND_OT_lattice)
    unregister_draw_handler()
