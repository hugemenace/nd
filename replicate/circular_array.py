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
from math import radians
from mathutils import Euler
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.events import capture_modifier_keys, pressed
from .. lib.collections import move_to_utils_collection, hide_utils_collection
from .. lib.preferences import get_preferences
from .. lib.objects import set_origin
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with
from .. lib.objects import get_real_active_object
from .. lib.polling import obj_exists, obj_is_mesh, ctx_obj_mode, ctx_objects_selected
from .. lib.math import round_dec


mod_displace = 'Displace — ND CA'
mod_array = 'Circular Array — ND CA'
mod_summon_list = [mod_displace, mod_array]


class ND_OT_circular_array(BaseOperator):
    bl_idname = "nd.circular_array"
    bl_label = "Circular Array"
    bl_description = """Array an object around another in a circular fashion
ALT — Use faux origin (for origin-reliant procedural geometry)
CTRL — Remove existing modifiers"""


    def do_modal(self, context, event):
        angle_factor = 1 if self.key_shift else 15
        count_factor = 1 if self.key_shift else 2

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.count_input_stream = update_stream(self.count_input_stream, event.type)
                self.count = int(get_stream_value(self.count_input_stream, min_value=2))
                self.dirty = True
            elif self.key_alt:
                self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                self.angle = get_stream_value(self.angle_input_stream)
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = update_stream(self.offset_input_stream, event.type)
                self.offset = get_stream_value(self.offset_input_stream, self.unit_scaled_factor)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.count_input_stream) and self.hard_stream_reset or no_stream(self.count_input_stream):
                    self.count = 2
                    self.dirty = True
                self.count_input_stream = new_stream()
            elif self.key_alt:
                if has_stream(self.angle_input_stream) and self.hard_stream_reset or no_stream(self.angle_input_stream):
                    self.angle = 360
                    self.dirty = True
                self.angle_input_stream = new_stream()
            elif self.key_ctrl:
                if has_stream(self.offset_input_stream) and self.hard_stream_reset or no_stream(self.offset_input_stream):
                    self.offset = self.reference_obj.dimensions[self.axis] if self.single_obj_mode else 0
                    self.dirty = True
                self.offset_input_stream = new_stream()

        if pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        if pressed(event, {'D'}):
            self.displace_axis = (self.displace_axis + 1) % 3
            self.dirty = True

        if self.key_step_up:
            if no_stream(self.angle_input_stream) and self.key_alt:
                self.angle = min(360, self.angle + angle_factor)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset = round_dec(self.offset + self.step_size)
                self.dirty = True
            elif no_stream(self.count_input_stream) and self.key_no_modifiers:
                self.count = 2 if self.count == 1 else self.count + count_factor
                self.dirty = True

        if self.key_step_down:
            if no_stream(self.angle_input_stream) and self.key_alt:
                self.angle = max(-360, self.angle - angle_factor)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset = round_dec(self.offset - self.step_size)
                self.dirty = True
            elif no_stream(self.count_input_stream) and self.key_no_modifiers:
                self.count = max(2, self.count - count_factor)
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.angle_input_stream) and self.key_alt:
                self.angle = max(-360, min(360, self.angle + self.mouse_value_mag))
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.mouse_value
                self.dirty = True
            elif no_stream(self.count_input_stream) and self.key_no_modifiers:
                self.count = max(2, self.count + self.mouse_step)
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND CA')
            return {'FINISHED'}

        self.dirty = False

        self.faux_origin = event.alt
        self.base_offset_factor = 0.001

        self.axis = 2
        self.displace_axis = 0
        self.count = 2
        self.angle = 360
        self.offset = 0
        self.single_obj_mode = len(context.selected_objects) == 1

        self.count_input_stream = new_stream()
        self.angle_input_stream = new_stream()
        self.offset_input_stream = new_stream()

        mods = context.active_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if previous_op:
            self.summon_old_operator(context, mods)
        else:
            self.prepare_new_operator(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        init_axis(self, self.reference_obj, self.axis)

        register_axis_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        if ctx_obj_mode(context) and obj_exists(target_object) and ctx_objects_selected(context, 2):
            a, b = context.selected_objects
            reference_obj = a if a.name != target_object.name else b

            return reference_obj.type == 'MESH'
        elif ctx_obj_mode(context) and obj_is_mesh(target_object) and ctx_objects_selected(context, 1):
            return True
        else:
            return False


    def prepare_new_operator(self, context):
        self.summoned = False

        if not self.single_obj_mode:
            a, b = context.selected_objects
            self.reference_obj = a if a.name != context.active_object.name else b
            self.target_obj = context.active_object
        else:
            self.reference_obj = context.active_object

        bpy.data.objects[self.reference_obj.name]["NDCA_single_obj_mode"] = self.single_obj_mode

        if not self.single_obj_mode:
            self.reference_obj_prev_location = self.reference_obj.location.copy()
            self.reference_obj_prev_rotation = self.reference_obj.rotation_euler.copy()
            self.reference_obj.location = context.active_object.location.copy()
            self.reference_obj.rotation_euler = context.active_object.rotation_euler.copy()
            self.reference_obj_matrix_world_backup = self.reference_obj.matrix_world.copy()

        self.rotator_obj = bpy.data.objects.new("empty", None)
        self.rotator_obj.name = "ND — Circular Array Rotator"
        self.rotator_obj.empty_display_size = 1
        self.rotator_obj.empty_display_type = 'PLAIN_AXES'

        bpy.context.scene.collection.objects.link(self.rotator_obj)

        if self.single_obj_mode or self.faux_origin:
            self.rotator_obj.location = (0, 0, 0)
        else:
            self.rotator_obj.location = self.target_obj.location.copy()

        self.rotator_obj.rotation_euler = (0, 0, 0)
        self.rotator_obj.scale = (1, 1, 1)

        self.rotator_obj.parent = self.reference_obj
        if not self.faux_origin and not self.single_obj_mode:
            self.rotator_obj.matrix_parent_inverse = self.reference_obj.matrix_world.inverted()

        if self.faux_origin:
            self.add_displace_tranform_modifiers()
        elif not self.faux_origin and not self.single_obj_mode:
            mx = self.target_obj.matrix_world
            set_origin(self.reference_obj, mx)

        self.add_displace_modifier()
        self.add_array_modifier()

        self.select_reference_obj()


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.displace = mods[mod_displace]
        self.array = mods[mod_array]
        self.reference_obj = context.active_object
        self.rotator_obj = self.array.offset_object

        if self.rotator_obj is None:
            return

        self.angle = self.angle_prev = bpy.data.objects[self.reference_obj.name]["NDCA_angle"]
        self.axis = self.axis_prev = bpy.data.objects[self.reference_obj.name]["NDCA_axis"]
        self.single_obj_mode = bpy.data.objects[self.reference_obj.name]["NDCA_single_obj_mode"]
        self.displace_axis = self.displace_axis_prev = ['X', 'Y', 'Z'].index(self.displace.direction)
        self.count = self.count_prev = self.array.count
        self.offset = self.offset_prev = self.displace.strength

        if get_preferences().lock_overlay_parameters_on_recall:
            self.count_input_stream = set_stream(self.count)
            self.angle_input_stream = set_stream(self.angle)
            self.offset_input_stream = set_stream(self.offset)


    def add_array_modifier(self):
        array = new_modifier(self.reference_obj, mod_array, 'ARRAY', rectify=True)
        array.use_relative_offset = False
        array.use_object_offset = True
        array.offset_object = self.rotator_obj

        self.array = array


    def add_displace_tranform_modifiers(self):
        self.displace_transforms = []

        if not self.single_obj_mode:
            for index, axis in enumerate(['X', 'Y', 'Z']):
                displace = new_modifier(self.reference_obj, "Translate {} — ND FO".format(axis), 'DISPLACE', rectify=True)
                displace.direction = axis
                displace.space = 'LOCAL'
                displace.mid_level = 0
                displace.strength = self.reference_obj_prev_location[index] - self.reference_obj.location[index]

                self.displace_transforms.append(displace)


    def add_displace_modifier(self):
        displace = new_modifier(self.reference_obj, mod_displace, 'DISPLACE', rectify=True)
        displace.space = 'LOCAL'
        displace.mid_level = 0

        if self.single_obj_mode:
            self.offset = self.reference_obj.dimensions[self.axis]
            displace.strength = self.offset

        self.displace = displace


    def operate(self, context):
        altered_count = self.count if abs(self.angle) == 360 else self.count - 1
        rotation = radians(self.angle / altered_count)
        rotation_axis = ['X', 'Y', 'Z'][self.axis]

        self.rotator_obj.rotation_euler = (0, 0, 0)
        self.rotator_obj.rotation_euler.rotate_axis(rotation_axis, rotation)

        self.array.count = self.count

        if rotation_axis in ['Y', 'Z']:
            self.displace.direction = 'X'
        else:
            self.displace.direction = 'Y'

        self.displace.strength = self.offset
        self.displace.direction = ['X', 'Y', 'Z'][self.displace_axis]

        bpy.data.objects[self.reference_obj.name]["NDCA_angle"] = self.angle
        bpy.data.objects[self.reference_obj.name]["NDCA_axis"] = self.axis

        self.dirty = False


    def select_reference_obj(self):
        bpy.ops.object.select_all(action='DESELECT')
        self.reference_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_obj


    def finish(self, context):
        if not self.summoned:
            move_to_utils_collection(self.rotator_obj)
            hide_utils_collection(True)

        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if self.summoned:
            self.angle = self.angle_prev
            self.axis = self.axis_prev
            self.count = self.count_prev
            self.offset = self.offset_prev
            self.displace_axis = self.displace_axis_prev

            self.operate(context)

        if not self.summoned:
            if self.faux_origin:
                for displace in self.displace_transforms:
                    self.reference_obj.modifiers.remove(displace)

            self.reference_obj.modifiers.remove(self.displace)
            self.reference_obj.modifiers.remove(self.array)

            bpy.data.objects.remove(self.rotator_obj, do_unlink=True)

            if not self.single_obj_mode:
                if not self.faux_origin:
                    set_origin(self.reference_obj, self.reference_obj_matrix_world_backup)

                self.reference_obj.location = self.reference_obj_prev_location
                self.reference_obj.rotation_euler = self.reference_obj_prev_rotation

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    display_unit_scale = self.unit_scale / self.unit_factor

    draw_property(
        self,
        "Count: {}".format(self.count),
        self.generate_step_hint(2, 1),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.count_input_stream)

    draw_property(
        self,
        "Angle: {}".format('Circle (360°)' if abs(self.angle) == 360 else "Arc ({0:.2f}°)".format(self.angle)),
        self.generate_key_hint("Alt", self.generate_step_hint(15, 1)),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.angle_input_stream)

    draw_property(
        self,
        f"Offset: {(self.offset * display_unit_scale):.2f}{self.unit_suffix}",
        self.generate_key_hint("Ctrl", self.unit_step_hint),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.offset_input_stream)

    draw_hint(
        self,
        "Rotation Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Axis to revolve around (X, Y, Z)")

    draw_hint(
        self,
        "Displacement Axis [D]: {}".format(['X', 'Y', 'Z'][self.displace_axis]),
        "Local axis to displace along (X, Y, Z)")


def register():
    bpy.utils.register_class(ND_OT_circular_array)


def unregister():
    bpy.utils.unregister_class(ND_OT_circular_array)
    unregister_draw_handler()
