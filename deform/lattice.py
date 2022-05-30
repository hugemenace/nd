# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)
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


mod_lattice = "Lattice — ND L"
mod_summon_list = [mod_lattice]


class ND_OT_lattice(bpy.types.Operator):
    bl_idname = "nd.lattice"
    bl_label = "Lattice"
    bl_description = "Adds a lattice modifier to the selected object"
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

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False

        self.uniform = True
        self.lattice_points_u = 2
        self.lattice_points_v = 2
        self.lattice_points_w = 2

        self.lattice_points_u_input_stream = new_stream()
        self.lattice_points_v_input_stream = new_stream()
        self.lattice_points_w_input_stream = new_stream()

        self.reference_object = context.object

        mods = context.active_object.modifiers
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
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.object.type == 'MESH'


    def prepare_new_operator(self, context):
        self.summoned = False

        self.add_lattice_object(context)
        self.select_reference_object(context)
        self.add_lattice_modifier(context)

    
    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.lattice = mods[mod_lattice]
        self.lattice_obj = self.lattice.object

        if self.lattice_obj:
            self.lattice_points_u = self.lattice_points_u_prev = self.lattice_obj.data.points_u
            self.lattice_points_v = self.lattice_points_v_prev = self.lattice_obj.data.points_v
            self.lattice_points_w = self.lattice_points_w_prev = self.lattice_obj.data.points_w


    def add_lattice_object(self, context):
        bpy.ops.object.duplicate()

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.object.evaluated_get(depsgraph)
        context.object.modifiers.clear()

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        bm.to_mesh(context.object.data)
        bm.free()

        eval_obj = context.active_object

        coords = [vert for vert in eval_obj.data.vertices]
        box = generate_bounding_box(coords)
        center = v3_average(box)

        bpy.ops.object.add(type='LATTICE', enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))

        context.active_object.location = eval_obj.matrix_world @ center
        context.active_object.rotation_euler = eval_obj.rotation_euler
        context.active_object.dimensions = eval_obj.dimensions * 1.001
        context.active_object.name = "ND — Lattice"
        context.active_object.data.name = "ND — Lattice"
        context.active_object.data.use_outside = True

        self.lattice_obj = context.active_object
        self.lattice_obj.parent = self.reference_object

        bpy.data.meshes.remove(eval_obj.data, do_unlink=True)


    def select_reference_object(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.reference_object.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_object


    def select_lattice_object(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.lattice_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.lattice_obj


    def add_lattice_modifier(self, context):
        lattice = context.object.modifiers.new(mod_lattice, 'LATTICE')
        lattice.object = self.lattice_obj

        self.lattice = lattice

    
    def operate(self, context):
        self.lattice_obj.data.points_u = self.lattice_points_u
        self.lattice_obj.data.points_v = self.lattice_points_v
        self.lattice_obj.data.points_w = self.lattice_points_w

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
        input_stream=self.lattice_points_u_input_stream)

    draw_property(
        self,
        "V Points: {}".format(self.lattice_points_v),
        "Alt (±1)",
        active=(self.uniform or self.key_alt),
        alt_mode=False,
        input_stream=self.lattice_points_v_input_stream)

    draw_property(
        self,
        "W Points: {}".format(self.lattice_points_w),
        "Ctrl (±1)",
        active=(self.uniform or self.key_ctrl),
        alt_mode=False,
        input_stream=self.lattice_points_w_input_stream)

    draw_hint(
        self,
        "Uniform [U]: {}".format("Yes" if self.uniform else "No"),
        "Adjust all points uniformly")


def register():
    bpy.utils.register_class(ND_OT_lattice)


def unregister():
    bpy.utils.unregister_class(ND_OT_lattice)
    unregister_draw_handler()
