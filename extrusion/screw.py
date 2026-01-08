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
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, add_smooth_by_angle, ensure_tail_mod_consistency
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, ctx_edit_mode, obj_moddable, ctx_objects_selected, app_minor_version
from .. lib.math import round_dec


mod_displace = "Offset — ND SCR"
mod_screw = "Screw — ND SCR"
mod_mesh_summon_list = [mod_displace, mod_screw]
mod_curve_summon_list = [mod_screw]


class ND_OT_screw(BaseOperator):
    bl_idname = "nd.screw"
    bl_label = "Screw"
    bl_description = """Adds a screw modifier tuned for converting a sketch into a cylindrical object
CTRL — Remove existing modifiers"""


    key_callbacks = {
        'A': lambda cls, context, event: cls.handle_cycle_screw_axis(context, event),
        'O': lambda cls, context, event: cls.handle_cycle_offset_axis(context, event),
        'F': lambda cls, context, event: cls.handle_toggle_flip_normals(context, event),
    }

    modal_config = {
        'MOVEMENT_PASSTHROUGH': True,
        'ON_CANCEL': lambda cls, context: cls.revert(context),
        'ON_CONFIRM': lambda cls, context: cls.finish(context),
    }


    @classmethod
    def poll(cls, context):
        if ctx_obj_mode(context):
            target_object = get_real_active_object(context)
            return obj_moddable(target_object) and ctx_objects_selected(context, 1)

        if ctx_edit_mode(context):
            return obj_moddable(context.active_object)


    def do_modal(self, context, event):
        segment_factor = 1 if self.key_shift else 2
        angle_factor = 1 if self.key_shift else 10

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=3))
                self.mark_dirty()
            elif self.key_alt:
                self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                self.angle = get_stream_value(self.angle_input_stream)
                self.mark_dirty()
            elif self.key_ctrl:
                self.offset_input_stream = update_stream(self.offset_input_stream, event.type)
                self.offset = get_stream_value(self.offset_input_stream, self.unit_scaled_factor)
                self.mark_dirty()

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.segments_input_stream) and self.hard_stream_reset or no_stream(self.segments_input_stream):
                    self.segments = 3
                    self.mark_dirty()
                self.segments_input_stream = new_stream()
            elif self.key_alt:
                if has_stream(self.angle_input_stream) and self.hard_stream_reset or no_stream(self.angle_input_stream):
                    self.angle = 360
                    self.mark_dirty()
                self.angle_input_stream = new_stream()
            elif self.key_ctrl:
                if has_stream(self.offset_input_stream) and self.hard_stream_reset or no_stream(self.offset_input_stream):
                    self.offset = 0
                    self.mark_dirty()
                self.offset_input_stream = new_stream()

        if self.key_step_up:
            if no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset = round_dec(self.offset + self.step_size)
                self.mark_dirty()
            elif no_stream(self.angle_input_stream) and self.key_alt:
                self.angle = min(360, self.angle + angle_factor)
                self.mark_dirty()
            elif no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = 4 if self.segments == 3 else self.segments + segment_factor
                self.mark_dirty()

        if self.key_step_down:
            if no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset = round_dec(self.offset - self.step_size)
                self.mark_dirty()
            elif no_stream(self.angle_input_stream) and self.key_alt:
                self.angle = max(-360, self.angle - angle_factor)
                self.mark_dirty()
            elif no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = max(3, self.segments - segment_factor)
                self.mark_dirty()

        if get_preferences().enable_mouse_values:
            if no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.mouse_value
                self.mark_dirty()
            elif no_stream(self.angle_input_stream) and self.key_alt:
                self.angle = max(-360, min(360, self.angle + self.mouse_value_mag))
                self.mark_dirty()
            elif no_stream(self.segments_input_stream) and self.key_no_modifiers and self.has_mouse_step:
                self.segments = max(3, self.segments + self.mouse_step)
                self.mark_dirty()


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND SCR')
            return {'FINISHED'}

        self.target_object = context.active_object
        self.object_type = self.target_object.type
        self.edit_mode = context.mode == 'EDIT_MESH'

        self.axis = 2 # X (0), Y (1), Z (2)
        self.offset_axis = 1 # X (0), Y (1), Z (2)
        self.segments = 3
        self.angle = 360
        self.offset = 0
        self.flip_normals = True

        self.offset_input_stream = new_stream()
        self.angle_input_stream = new_stream()
        self.segments_input_stream = new_stream()

        mods = self.target_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = False

        if self.object_type == 'MESH':
            previous_op = all(m in mod_names for m in mod_mesh_summon_list)
        else:
            previous_op = all(m in mod_names for m in mod_curve_summon_list)

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


    def handle_cycle_screw_axis(self, context, event):
        self.axis = (self.axis + 1) % 3


    def handle_cycle_offset_axis(self, context, event):
        self.offset_axis = (self.offset_axis + 1) % 3


    def handle_toggle_flip_normals(self, context, event):
        self.flip_normals = not self.flip_normals


    def prepare_new_operator(self, context):
        self.summoned = False

        if self.object_type == 'MESH':
            self.add_smooth_shading(context)
            self.add_displace_modifier(context)

        self.add_screw_modifier(context)

        ensure_tail_mod_consistency(self.target_object)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        if self.object_type == 'MESH':
            self.displace = mods[mod_displace]

        self.screw = mods[mod_screw]

        if self.object_type == 'MESH':
            self.offset_prev = self.offset = self.displace.strength
            self.offset_axis_prev = self.offset_axis = {'X': 0, 'Y': 1, 'Z': 2}[self.displace.direction]

        self.axis_prev = self.axis = {'X': 0, 'Y': 1, 'Z': 2}[self.screw.axis]
        self.segments_prev = self.segments = self.screw.steps
        self.segments_prev = self.segments = self.screw.render_steps
        self.angle_prev = self.angle = degrees(self.screw.angle)
        self.flip_normals_prev = self.flip_normals = self.screw.use_normal_flip

        if get_preferences().lock_overlay_parameters_on_recall:
            self.offset_input_stream = set_stream(self.offset)
            self.angle_input_stream = set_stream(self.angle)
            self.segments_input_stream = set_stream(self.segments)


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


    def add_displace_modifier(self, context):
        displace = new_modifier(self.target_object, mod_displace, 'DISPLACE', rectify=True)
        displace.mid_level = 0
        displace.space = 'LOCAL'

        self.displace = displace


    def add_screw_modifier(self, context):
        screw = new_modifier(self.target_object, mod_screw, 'SCREW', rectify=True)
        screw.screw_offset = 0
        screw.use_merge_vertices = True
        screw.merge_threshold = 0.0001
        screw.use_normal_calculate = True

        self.screw = screw


    def operate(self, context):
        if self.object_type == 'MESH':
            self.displace.strength = self.offset
            self.displace.direction = ['X', 'Y', 'Z'][self.offset_axis]

        self.screw.axis = ['X', 'Y', 'Z'][self.axis]
        self.screw.steps = self.segments
        self.screw.render_steps = self.segments
        self.screw.angle = radians(self.angle)
        self.screw.use_normal_flip = self.flip_normals


    def finish(self, context):
        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.screw.name)

            if self.object_type == 'MESH':
                bpy.ops.object.modifier_remove(modifier=self.displace.name)

        if self.summoned:
            if self.object_type == 'MESH':
                self.displace.strength = self.offset_prev
                self.displace.direction = ['X', 'Y', 'Z'][self.offset_axis_prev]

            self.screw.axis = ['X', 'Y', 'Z'][self.axis_prev]
            self.screw.steps = self.segments_prev
            self.screw.render_steps = self.segments_prev
            self.screw.angle = radians(self.angle_prev)

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Segments: {self.segments}",
        self.generate_step_hint(2, 1),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.segments_input_stream)

    draw_property(
        self,
        f"Angle: {self.angle:.2f}°",
        self.generate_key_hint("Alt", self.generate_step_hint(10, 1)),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.angle_input_stream)

    if self.object_type == 'MESH':
        draw_property(
            self,
            f"Offset: {(self.offset * self.display_unit_scale):.2f}{self.unit_suffix}",
            self.generate_key_hint("Ctrl", self.unit_step_hint),
            active=self.key_ctrl,
            alt_mode=self.key_shift_ctrl,
            mouse_value=True,
            input_stream=self.offset_input_stream)

    axes = ['X', 'Y', 'Z']

    draw_hint(self, f"Screw Axis [A]: {axes[self.axis]}", self.list_options_str(axes))

    if self.object_type == 'MESH':
        draw_hint(self, f"Offset Axis [O]: {axes[self.offset_axis]}", self.list_options_str(axes))

    draw_hint(
        self,
        f"Flip Normals [F]: {self.yes_no_str(self.flip_normals)}",
        "Flip the normals of the resulting mesh")


def register():
    bpy.utils.register_class(ND_OT_screw)


def unregister():
    bpy.utils.unregister_class(ND_OT_screw)
    unregister_draw_handler()
