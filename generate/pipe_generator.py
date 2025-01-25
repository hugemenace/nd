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
from .. lib.overlay import init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor
from .. lib.preferences import get_preferences, get_scene_unit_factor
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, ensure_tail_mod_consistency, add_smooth_by_angle
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, ctx_objects_selected, app_minor_version


socket_map = {
    "profile_segments": "Socket_5",
    "profile_radius": "Socket_2",
    "base_corner_segments": "Socket_11",
    "base_corner_radius": "Socket_12",
    "fill_caps": "Socket_6",
    "vertex_merge_distance": "Socket_7",
}


default_profile_radius = 0.01
default_profile_segments = 16
default_base_corner_radius = 0.02
default_base_corner_segments = 8


class ND_OT_pipe_generator(BaseOperator):
    bl_idname = "nd.pipe_generator"
    bl_label = "Pipe Generator"
    bl_description = """Generates a pipe from an edge path with customisable corner parameters"""


    def do_modal(self, context, event):
        segment_factor = 1 if self.key_shift else 2

        if self.key_numeric_input:
            if not self.configure_corners:
                if self.key_no_modifiers:
                    self.profile_radius_input_stream = update_stream(self.profile_radius_input_stream, event.type)
                    self.profile_radius = get_stream_value(self.profile_radius_input_stream, self.unit_scaled_factor)
                    self.dirty = True
                elif self.key_alt:
                    self.profile_segments_input_stream = update_stream(self.profile_segments_input_stream, event.type)
                    self.profile_segments = int(get_stream_value(self.profile_segments_input_stream, min_value=3))
                    self.dirty = True
                elif self.key_ctrl:
                    self.base_corner_radius_input_stream = update_stream(self.base_corner_radius_input_stream, event.type)
                    self.base_corner_radius = get_stream_value(self.base_corner_radius_input_stream, self.unit_scaled_factor)
                    self.dirty = True
                elif self.key_ctrl_alt:
                    self.base_corner_segments_input_stream = update_stream(self.base_corner_segments_input_stream, event.type)
                    self.base_corner_segments = int(get_stream_value(self.base_corner_segments_input_stream, min_value=3))
                    self.dirty = True

        if self.key_reset:
            if not self.configure_corners:
                if self.key_no_modifiers:
                    if has_stream(self.profile_radius_input_stream) and self.hard_stream_reset or no_stream(self.profile_radius_input_stream):
                        self.profile_radius = default_profile_radius
                        self.dirty = True
                    self.profile_radius_input_stream = new_stream()
                elif self.key_alt:
                    if has_stream(self.profile_segments_input_stream) and self.hard_stream_reset or no_stream(self.profile_segments_input_stream):
                        self.profile_segments = default_profile_segments
                        self.dirty = True
                    self.profile_segments_input_stream = new_stream()
                elif self.key_ctrl:
                    if has_stream(self.base_corner_radius_input_stream) and self.hard_stream_reset or no_stream(self.base_corner_radius_input_stream):
                        self.base_corner_radius = default_base_corner_radius
                        self.dirty = True
                    self.base_corner_radius_input_stream = new_stream()
                elif self.key_ctrl_alt:
                    if has_stream(self.base_corner_segments_input_stream) and self.hard_stream_reset or no_stream(self.base_corner_segments_input_stream):
                        self.base_corner_segments = default_base_corner_segments
                        self.dirty = True
                    self.base_corner_segments_input_stream = new_stream()

        if not self.configure_corners and pressed(event, {'F'}):
            self.fill_caps = not self.fill_caps
            self.dirty = True

        if pressed(event, {'C'}):
            self.configure_corners = not self.configure_corners
            self.dirty = True

        if self.key_step_up:
            if not self.configure_corners:
                if self.extend_mouse_values and no_stream(self.profile_segments_input_stream) and self.key_no_modifiers:
                    self.profile_segments = 4 if self.profile_segments == 3 else self.profile_segments + segment_factor
                    self.dirty = True
                elif no_stream(self.profile_segments_input_stream) and self.key_alt:
                    self.profile_segments = 4 if self.profile_segments == 3 else self.profile_segments + segment_factor
                    self.dirty = True
                elif no_stream(self.profile_radius_input_stream) and self.key_no_modifiers:
                    self.profile_radius += self.step_size
                    self.dirty = True
                elif no_stream(self.base_corner_radius_input_stream) and self.key_ctrl:
                    self.base_corner_radius += self.step_size
                    self.dirty = True
                elif no_stream(self.base_corner_segments_input_stream) and self.key_ctrl_alt:
                    self.base_corner_segments = 2 if self.base_corner_segments == 1 else self.base_corner_segments + segment_factor
                    self.dirty = True

        if self.key_step_down:
            if not self.configure_corners:
                if self.extend_mouse_values and no_stream(self.profile_segments_input_stream) and self.key_no_modifiers:
                    self.profile_segments = max(3, self.profile_segments - segment_factor)
                    self.dirty = True
                elif no_stream(self.profile_segments_input_stream) and self.key_alt:
                    self.profile_segments = max(3, self.profile_segments - segment_factor)
                    self.dirty = True
                elif no_stream(self.profile_radius_input_stream) and self.key_no_modifiers:
                    self.profile_radius = max(0, self.profile_radius - self.step_size)
                    self.dirty = True
                elif no_stream(self.base_corner_radius_input_stream) and self.key_ctrl:
                    self.base_corner_radius -= self.step_size
                    self.dirty = True
                elif no_stream(self.base_corner_segments_input_stream) and self.key_ctrl_alt:
                    self.base_corner_segments = max(1, self.base_corner_segments - segment_factor)
                    self.dirty = True

        if not self.configure_corners and self.key_confirm:
            self.finish(context)
            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if not self.configure_corners:
                if no_stream(self.profile_radius_input_stream) and self.key_no_modifiers:
                    self.profile_radius = max(0, self.profile_radius + self.mouse_value)
                    self.dirty = True
                elif no_stream(self.profile_segments_input_stream) and self.key_alt:
                    self.profile_segments = max(3, self.profile_segments + self.mouse_step)
                    self.dirty = True
                elif no_stream(self.base_corner_radius_input_stream) and self.key_ctrl:
                    self.base_corner_radius += self.mouse_value
                    self.dirty = True
                elif no_stream(self.base_corner_segments_input_stream) and self.key_ctrl_alt:
                    self.base_corner_segments = max(1, self.base_corner_segments + self.mouse_step)
                    self.dirty = True


    def do_invoke(self, context, event):
        self.dirty = False

        self.profile_segments_input_stream = new_stream()
        self.profile_radius_input_stream = new_stream()
        self.base_corner_segments_input_stream = new_stream()
        self.base_corner_radius_input_stream = new_stream()

        self.fill_caps = True
        self.configure_corners = False

        self.profile_segments = default_profile_segments
        self.profile_radius = default_profile_radius
        self.base_corner_segments = default_base_corner_segments
        self.base_corner_radius = default_base_corner_radius

        self.selected_vertex = None
        self.custom_corner_radius = 0.0
        self.custom_corner_segments = 0

        previous_op = False
        for mod in context.active_object.modifiers:
            if mod.type == 'NODES' and mod.node_group.name == 'ND.PipeGenerator':
                self.pipe_gen = mod
                previous_op = True
                break

        if previous_op:
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
        return ctx_obj_mode(context) and ctx_objects_selected(context, 1)


    def prepare_new_operator(self, context):
        self.summoned = False

        self.pipe_gen_object = get_real_active_object(context)

        self.add_pipe_generator(context)
        self.add_attributes(context)
        self.add_smooth_shading(context)


    def summon_old_operator(self, context):
        self.summoned = True

        self.pipe_gen_object = get_real_active_object(context)

        self.segments_prev = self.segments = self.hole_gen[socket_map["segments"]]
        self.hole_diameter_prev = self.hole_diameter = self.hole_gen[socket_map["hole_diameter"]]
        self.hole_depth_prev = self.hole_depth = self.hole_gen[socket_map["hole_depth"]]
        self.counter_diameter_prev = self.counter_diameter = self.hole_gen[socket_map["counter_diameter"]]
        self.hole_type_prev = self.hole_type = self.hole_gen[socket_map["hole_type"]]
        self.drill_point_prev = self.drill_point = self.hole_gen[socket_map["drill_point"]]

        if get_preferences().lock_overlay_parameters_on_recall:
            self.hole_diameter_input_stream = set_stream(self.hole_diameter)
            self.segments_input_stream = set_stream(self.segments)
            self.hole_depth_input_stream = set_stream(self.hole_depth)
            self.counter_diameter_input_stream = set_stream(self.counter_diameter)


    def add_pipe_generator(self, context):
        pipe_gen = new_modifier(context.active_object, 'Pipe Generator — ND', 'NODES', rectify=False)
        pipe_gen.node_group = bpy.data.node_groups['ND.PipeGenerator']

        self.pipe_gen = pipe_gen


    def add_attributes(self, context):
        bpy.ops.geometry.attribute_add(name="ND.VertexRadius", domain='POINT', data_type='FLOAT')
        bpy.ops.geometry.attribute_add(name="ND.VertexSegments", domain='POINT', data_type='INT')


    def add_smooth_shading(self, context):
        if not get_preferences().enable_auto_smooth:
            return

        if app_minor_version() >= (4, 1):
            add_smooth_by_angle(context, self.pipe_gen_object)
            return

        bpy.ops.object.shade_smooth()
        self.pipe_gen_object.data.use_auto_smooth = True
        self.pipe_gen_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))


    def operate(self, context):
        self.pipe_gen[socket_map["profile_radius"]] = self.profile_radius
        self.pipe_gen[socket_map["profile_segments"]] = int(self.profile_segments)
        self.pipe_gen[socket_map["base_corner_radius"]] = self.base_corner_radius
        self.pipe_gen[socket_map["base_corner_segments"]] = int(self.base_corner_segments)
        self.pipe_gen[socket_map["fill_caps"]] = self.fill_caps

        if not self.summoned:
            self.pipe_gen[socket_map["vertex_merge_distance"]] = min(self.profile_radius, self.base_corner_radius) * 0.1

        self.pipe_gen.node_group.interface_update(context)

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        # if self.summoned:
        #     self.segments = self.segments_prev
        #     self.hole_diameter = self.hole_diameter_prev
        #     self.hole_depth = self.hole_depth_prev
        #     self.counter_diameter = self.counter_diameter_prev
        #     self.hole_type = self.hole_type_prev
        #     self.drill_point = self.drill_point_prev

        #     self.operate(context)

        # if not self.summoned:
        #     bpy.data.objects.remove(self.pipe_gen_object, do_unlink=True)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    if self.configure_corners:
        if not self.selected_vertex:
            draw_hint(
                self,
                "Select a corner vertex to configure",
                "Once selected, you can adjust the corner radius and segments"
            )


    if not self.configure_corners:
        draw_property(
            self,
            f"Profile Radius: {(self.profile_radius * self.display_unit_scale):.2f}{self.unit_suffix}",
            self.unit_step_hint,
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.profile_radius_input_stream)

        draw_property(
            self,
            f"Profile Segments: {self.profile_segments}",
            self.generate_key_hint("Alt / Scroll" if self.extend_mouse_values else "Alt", self.generate_step_hint(2, 1)),
            active=self.key_alt,
            alt_mode=self.key_shift_alt,
            mouse_value=True,
            input_stream=self.profile_segments_input_stream)

        draw_property(
            self,
            f"Base Corner Radius: {(self.base_corner_radius * self.display_unit_scale):.2f}{self.unit_suffix}",
            self.generate_key_hint("Ctrl", self.unit_step_hint),
            active=self.key_ctrl,
            alt_mode=self.key_shift_ctrl,
            mouse_value=True,
            input_stream=self.base_corner_radius_input_stream)

        draw_property(
            self,
            f"Base Corner Segments: {self.base_corner_segments}",
            self.generate_key_hint("Ctrl + Alt", self.generate_step_hint(2, 1)),
            active=self.key_ctrl_alt,
            alt_mode=self.key_shift_ctrl_alt,
            mouse_value=True,
            input_stream=self.base_corner_segments_input_stream)

        draw_hint(
            self,
            "Fill Caps [F]: {}".format("Yes" if self.fill_caps else "No"),
            ", ".join(["Yes", "No"]))

    draw_hint(
        self,
        "Configure Corners [C]: {}".format("Active" if self.configure_corners else "Inactive"),
        ", ".join(["Active", "Inactive"]))


def register():
    bpy.utils.register_class(ND_OT_pipe_generator)


def unregister():
    bpy.utils.unregister_class(ND_OT_pipe_generator)
    unregister_draw_handler()
