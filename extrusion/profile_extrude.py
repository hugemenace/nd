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
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, ensure_tail_mod_consistency, add_smooth_by_angle
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, ctx_edit_mode, obj_is_mesh, ctx_objects_selected, app_minor_version
from .. lib.math import round_dec


mod_screw = "Extrusion — ND PE"
mod_weighting = "Weighting — ND PE"
mod_offset = "Offset — ND PE"
mod_summon_list = [mod_screw, mod_weighting, mod_offset]


class ND_OT_profile_extrude(BaseOperator):
    bl_idname = "nd.profile_extrude"
    bl_label = "Profile Extrude"
    bl_description = """Extrudes a profile along a specified axis
CTRL — Remove existing modifiers"""


    def do_modal(self, context, event):
        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.extrusion_length_input_stream = update_stream(self.extrusion_length_input_stream, event.type)
                self.extrusion_length = get_stream_value(self.extrusion_length_input_stream, self.unit_scaled_factor)
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = update_stream(self.offset_input_stream, event.type)
                self.offset = get_stream_value(self.offset_input_stream, self.unit_scaled_factor)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.extrusion_length_input_stream) and self.hard_stream_reset or no_stream(self.extrusion_length_input_stream):
                    self.extrusion_length = 0
                    self.dirty = True
                self.extrusion_length_input_stream = new_stream()
            elif self.key_ctrl:
                if has_stream(self.offset_input_stream) and self.hard_stream_reset or no_stream(self.offset_input_stream):
                    self.offset = 0
                    self.dirty = True
                self.offset_input_stream = new_stream()

        if pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        if pressed(event, {'W'}):
            self.weighting = self.weighting + 1 if self.weighting < 1 else -1
            self.dirty = True

        if pressed(event, {'E'}):
            self.calculate_edges = not self.calculate_edges
            self.dirty = True

        if self.key_step_up:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.extrusion_length = round_dec(self.extrusion_length + self.step_size)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset = round_dec(self.offset + self.step_size)
                self.dirty = True

        if self.key_step_down:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.extrusion_length = max(0, round_dec(self.extrusion_length - self.step_size))
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset = round_dec(self.offset - self.step_size)
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.extrusion_length = max(0, self.extrusion_length + self.mouse_value)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.mouse_value
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND PE')
            return {'FINISHED'}

        self.dirty = False

        self.extrusion_length_input_stream = new_stream()
        self.offset_input_stream = new_stream()
        self.edit_mode = context.mode == 'EDIT_MESH'

        self.target_object = context.active_object

        mods = self.target_object.modifiers
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

        init_axis(self, self.target_object, self.axis)
        register_axis_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if ctx_obj_mode(context):
            target_object = get_real_active_object(context)
            return obj_is_mesh(target_object) and ctx_objects_selected(context, 1)

        if ctx_edit_mode(context):
            return obj_is_mesh(context.active_object)


    def prepare_new_operator(self, context):
        self.summoned = False

        self.axis = 0
        self.extrusion_length = 0
        self.weighting = 0
        self.offset = 0
        self.calculate_edges = True

        self.add_smooth_shading(context)
        self.add_weighting_modifier(context)
        self.add_offset_modifier(context)
        self.add_screw_modifier(context)

        ensure_tail_mod_consistency(self.target_object)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.calculate_edges = True
        self.screw = mods[mod_screw]
        self.weighting_offset = mods[mod_weighting]
        self.displace = mods[mod_offset]

        self.axis_prev = self.axis = {'X': 0, 'Y': 1, 'Z': 2}[self.screw.axis]
        self.extrusion_length_prev = self.extrusion_length = self.screw.screw_offset
        self.calculate_edges_prev = self.calculate_edges = self.screw.use_normal_calculate
        self.weighting = self.calculate_existing_weighting()
        self.weighting_offset_strength_prev = self.weighting_offset.strength
        self.offset_prev = self.offset = self.displace.strength

        if get_preferences().lock_overlay_parameters_on_recall:
            self.extrusion_length_input_stream = set_stream(self.extrusion_length)
            self.offset_input_stream = set_stream(self.offset)


    def calculate_weighting_offset_strength(self):
        if self.weighting == -1:
            return self.extrusion_length * -1
        elif self.weighting == 0:
            return self.extrusion_length * -0.5
        elif self.weighting == 1:
            return 0


    def calculate_existing_weighting(self):
        offset = abs(self.weighting_offset.strength)
        extrusion = self.screw.screw_offset
        factor = offset / (extrusion * 0.5)

        return max(-1, min(1, 1 - round(factor)))


    def add_smooth_shading(self, context):
        if not get_preferences().enable_auto_smooth:
            return

        return_to_edit = False
        if self.edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')
            return_to_edit = True

        if app_minor_version() >= (4, 1):
            add_smooth_by_angle(context, self.target_object)
            if return_to_edit:
                bpy.ops.object.mode_set(mode='EDIT')
            return

        bpy.ops.object.shade_smooth()
        self.target_object.data.use_auto_smooth = True
        self.target_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))

        if return_to_edit:
            bpy.ops.object.mode_set(mode='EDIT')


    def add_weighting_modifier(self, context):
        offset = new_modifier(self.target_object, mod_weighting, 'DISPLACE', rectify=True)
        offset.space = 'LOCAL'
        offset.mid_level = 0

        self.weighting_offset = offset


    def add_offset_modifier(self, context):
        offset = new_modifier(self.target_object, mod_offset, 'DISPLACE', rectify=True)
        offset.space = 'LOCAL'
        offset.mid_level = 0

        self.displace = offset


    def add_screw_modifier(self, context):
        screw = new_modifier(self.target_object, mod_screw, 'SCREW', rectify=True)
        screw.steps = 0
        screw.render_steps = 0
        screw.angle = 0

        self.screw = screw


    def operate(self, context):
        axis = ['X', 'Y', 'Z'][self.axis]

        self.screw.axis = axis
        self.screw.screw_offset = self.extrusion_length
        self.screw.use_normal_calculate = self.calculate_edges
        self.weighting_offset.direction = axis
        self.weighting_offset.strength = self.calculate_weighting_offset_strength()
        self.displace.direction = axis
        self.displace.strength = self.offset

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.displace.name)
            bpy.ops.object.modifier_remove(modifier=self.weighting_offset.name)
            bpy.ops.object.modifier_remove(modifier=self.screw.name)

        if self.summoned:
            axis = ['X', 'Y', 'Z'][self.axis_prev]

            self.screw.axis = axis
            self.screw.screw_offset = self.extrusion_length_prev
            self.weighting_offset.direction = axis
            self.weighting_offset.strength = self.weighting_offset_strength_prev
            self.displace.direction = axis
            self.displace.strength = self.offset_prev

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Extrusion: {(self.extrusion_length * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.unit_step_hint,
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.extrusion_length_input_stream)

    draw_property(
        self,
        f"Offset: {(self.offset * self.display_unit_scale):.2f}",
        self.generate_key_hint("Ctrl", self.unit_step_hint),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.offset_input_stream)

    draw_hint(
        self,
        "Weighting [W]: {}".format(['Negative', 'Neutral', 'Positive'][1 + round(self.weighting)]),
        "Negative, Neutral, Positive")

    draw_hint(
        self,
        "Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Axis to extrude along (X, Y, Z)")

    draw_hint(
        self,
        "Calculate Edges [E]: {}".format("Yes" if self.calculate_edges else "No"),
        "Calculate the order of edges (affects normals)")


def register():
    bpy.utils.register_class(ND_OT_profile_extrude)


def unregister():
    bpy.utils.unregister_class(ND_OT_profile_extrude)
    unregister_draw_handler()
