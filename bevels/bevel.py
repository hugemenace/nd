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
from math import radians, degrees
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, add_smooth_by_angle, rectify_smooth_by_angle


mod_bevel = "Bevel — ND B"
mod_weld = "Weld — ND B"
mod_summon_list = [mod_bevel]


class ND_OT_bevel(BaseOperator):
    bl_idname = "nd.bevel"
    bl_label = "Bevel"
    bl_description = """Adds a bevel modifier to the selected object
CTRL — Remove existing modifiers
SHIFT — Create a stacked bevel modifier"""


    def do_modal(self, context, event):
        profile_factor = 0.01 if self.key_shift else 0.1
        segment_factor = 1 if self.key_shift else 2
        angle_factor = 1 if self.key_shift else 15

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.width_input_stream = update_stream(self.width_input_stream, event.type)
                self.width = get_stream_value(self.width_input_stream, self.unit_scaled_factor)
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=1))
                self.dirty = True
            elif self.key_ctrl:
                self.profile_input_stream = update_stream(self.profile_input_stream, event.type)
                self.profile = get_stream_value(self.profile_input_stream)
                self.dirty = True
            elif self.key_ctrl_alt:
                self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                self.angle = get_stream_value(self.angle_input_stream, min_value=0, max_value=360)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                self.width_input_stream = new_stream()
                self.width = 0
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = new_stream()
                self.segments = 1
                self.dirty = True
            elif self.key_ctrl:
                self.profile_input_stream = new_stream()
                self.profile = 0.5
                self.dirty = True
            elif self.key_ctrl_alt:
                self.angle_input_stream = new_stream()
                self.angle = int(get_preferences().default_smoothing_angle)
                self.dirty = True

        if pressed(event, {'H'}):
            self.harden_normals = not self.harden_normals
            self.dirty = True

        if pressed(event, {'C'}):
            self.clamp_overlap = not self.clamp_overlap
            self.dirty = True

        if pressed(event, {'S'}):
            self.loop_slide = not self.loop_slide
            self.dirty = True

        if pressed(event, {'W'}):
            self.target_object.show_wire = not self.target_object.show_wire
            self.target_object.show_in_front = not self.target_object.show_in_front

        if pressed(event, {'R'}) and len(self.current_bevel_mods) > 1:
            self.summoned_mod_index = (self.summoned_mod_index + 1) % len(self.current_bevel_mods)
            self.revert(context, True)
            self.summon_old_operator(context)

        if self.key_step_up:
            if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = min(1, self.profile + profile_factor)
                self.dirty = True
            elif no_stream(self.angle_input_stream) and self.key_ctrl_alt:
                self.angle = min(360, self.angle + angle_factor)
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width += self.step_size
                self.dirty = True

        if self.key_step_down:
            if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = max(1, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(1, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = max(0, self.profile - profile_factor)
                self.dirty = True
            elif no_stream(self.angle_input_stream) and self.key_ctrl_alt:
                self.angle = max(0, self.angle - angle_factor)
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(0, self.width - self.step_size)
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(1, self.segments + self.mouse_step)
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = max(0, min(1, self.profile + self.mouse_value))
                self.dirty = True
            elif no_stream(self.angle_input_stream) and self.key_ctrl_alt:
                self.angle = self.angle = max(0, min(360, self.angle + self.mouse_value_mag))
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(0, self.width + self.mouse_value)
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        self.mods = context.active_object.modifiers
        self.mod_names = list(map(lambda x: x.name, self.mods))
        self.current_bevel_mods = list(filter(lambda x: any(m in x for m in mod_summon_list), self.mod_names))

        if event.ctrl:
            if len(self.current_bevel_mods) == 0:
                return {'FINISHED'}

            last_bevel_mod = self.current_bevel_mods[-1] if self.current_bevel_mods else None

            if last_bevel_mod == None:
                return {'FINISHED'}

            last_bevel_mod_tail = last_bevel_mod.split(' — ')[-1]

            remove_modifiers_ending_with(context.selected_objects, f'Bevel — {last_bevel_mod_tail}', True)
            remove_modifiers_ending_with(context.selected_objects, f'Weld — {last_bevel_mod_tail}', True)

            return {'FINISHED'}

        self.stacked = event.shift
        self.dirty = False

        self.segments = 1
        self.width = 0
        self.profile = 0.5
        self.angle = int(get_preferences().default_smoothing_angle)
        self.harden_normals = False
        self.loop_slide = False
        self.clamp_overlap = False

        self.segments_input_stream = new_stream()
        self.width_input_stream = new_stream()
        self.profile_input_stream = new_stream()
        self.angle_input_stream = new_stream()

        self.target_object = context.active_object
        self.summoned_mod_index = 0

        previous_op = all(m in self.mod_names for m in mod_summon_list)

        if not self.stacked and previous_op:
            self.summon_old_operator(context)
        else:
            self.prepare_new_operator(context)

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

        self.add_smooth_shading(context)
        self.add_bevel_modifier(context)

        rectify_smooth_by_angle(self.target_object)


    def summon_old_operator(self, context):
        self.summoned = True

        mod_name = self.current_bevel_mods[self.summoned_mod_index]
        self.bevel = self.mods[mod_name]

        self.width_prev = self.width = self.bevel.width
        self.segments_prev = self.segments = self.bevel.segments
        self.profile_prev = self.profile = self.bevel.profile
        self.harden_normals_prev = self.harden_normals = self.bevel.harden_normals
        self.loop_slide_prev = self.loop_slide = self.bevel.loop_slide
        self.clamp_overlap_prev = self.clamp_overlap = self.bevel.use_clamp_overlap
        self.angle_prev = self.angle = degrees(self.bevel.angle_limit)


    def add_smooth_shading(self, context):
        if not get_preferences().enable_auto_smooth:
            return

        if bpy.app.version >= (4, 1, 0):
            add_smooth_by_angle(self.target_object)
            return

        bpy.ops.object.shade_smooth()
        self.target_object.data.use_auto_smooth = True
        self.target_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))


    def add_bevel_modifier(self, context):
        bevel = new_modifier(self.target_object, mod_bevel, 'BEVEL', rectify=False)
        bevel.offset_type = 'WIDTH'
        bevel.miter_outer = 'MITER_ARC'
        bevel.face_strength_mode = 'FSTR_AFFECTED'

        self.bevel = bevel


    def add_weld_modifier(self, context):
        weld = new_modifier(self.target_object, mod_weld, 'WELD', rectify=False)
        weld.merge_threshold = 0.00001
        weld.mode = 'CONNECTED'

        self.weld = weld


    def operate(self, context):
        self.bevel.width = self.width
        self.bevel.segments = self.segments
        self.bevel.profile = self.profile
        self.bevel.harden_normals = self.harden_normals
        self.bevel.angle_limit = radians(self.angle)
        self.bevel.loop_slide = self.loop_slide
        self.bevel.use_clamp_overlap = self.clamp_overlap

        self.dirty = False


    def finish(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False

        if not self.summoned:
            self.add_weld_modifier(context)
            rectify_smooth_by_angle(self.target_object)

        unregister_draw_handler()


    def revert(self, context, soft=False):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False

        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.bevel.name)

        if self.summoned:
            self.bevel.width = self.width_prev
            self.bevel.segments = self.segments_prev
            self.bevel.profile = self.profile_prev
            self.bevel.angle_limit = radians(self.angle_prev)
            self.bevel.loop_slide = self.loop_slide_prev
            self.bevel.use_clamp_overlap = self.clamp_overlap_prev

        if not soft:
            unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Width: {(self.width * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.unit_step_hint,
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.width_input_stream)

    draw_property(
        self,
        "Segments: {}".format(self.segments),
        self.generate_key_hint("Alt / Scroll" if self.extend_mouse_values else "Alt", self.generate_step_hint(2, 1)),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.segments_input_stream)

    draw_property(
        self,
        "Profile: {0:.2f}".format(self.profile),
        self.generate_key_hint("Ctrl", self.generate_step_hint(0.1, 0.01)),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.profile_input_stream)

    draw_property(
        self,
        "Angle: {0:.0f}°".format(self.angle),
        self.generate_key_hint("Ctrl + Alt", self.generate_step_hint(15, 1)),
        active=self.key_ctrl_alt,
        alt_mode=self.key_shift_ctrl_alt,
        mouse_value=True,
        input_stream=self.angle_input_stream)

    draw_hint(
        self,
        "Harden Normals [H]: {0}".format("Yes" if self.harden_normals else "No"),
        "Match normals of new faces to adjacent faces")

    draw_hint(
        self,
        "Enhanced Wireframe [W]: {0}".format("Yes" if self.target_object.show_wire else "No"),
        "Display the objects's wireframe over solid shading")

    draw_hint(
        self,
        "Clamp Overlap [C]: {0}".format("Yes" if self.clamp_overlap else "No"),
        "Clamp the width to avoid overlap")

    draw_hint(
        self,
        "Loop Slide [S]: {0}".format("Yes" if self.loop_slide else "No"),
        "Prefer sliding along edges to having even widths")

    if len(self.current_bevel_mods) > 1:
        draw_hint(
            self,
            "Recall bevel [R]: {0}".format(self.current_bevel_mods[self.summoned_mod_index]),
            "Switch between summoned bevels")


def register():
    bpy.utils.register_class(ND_OT_bevel)


def unregister():
    bpy.utils.unregister_class(ND_OT_bevel)
    unregister_draw_handler()
