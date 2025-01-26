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
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor, get_real_active_object
from .. lib.preferences import get_preferences, get_scene_unit_factor
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, ensure_tail_mod_consistency, add_smooth_by_angle
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, ctx_objects_selected_range, ctx_objects_selected, app_minor_version


socket_map = {
    "hole_type": "Socket_3",
    "drill_point": "Socket_4",
    "segments": "Socket_16",
    "hole_depth": "Socket_5",
    "hole_diameter": "Socket_6",
    "counter_diameter": "Socket_21",
    "counterbore_depth": "Socket_9",
    "countersink_angle": "Socket_12",
    "drill_point_angle": "Socket_15",
    "protrusion_distance": "Socket_18",
}

hole_types = {
    "simple": 0,
    "counterbore": 1,
    "countersunk": 2,
}

hole_type_names = list(map(lambda x: x.capitalize(), hole_types.keys()))

drill_points = {
    "flat": 0,
    "angle": 1,
}

drill_point_names = list(map(lambda x: x.capitalize(), drill_points.keys()))

default_hole_diameter = 0.01
default_segments = 32
default_hole_depth = 0.01
default_counter_diameter = 0.015


class ND_OT_hole_generator(BaseOperator):
    bl_idname = "nd.hole_generator"
    bl_label = "Hole Generator"
    bl_description = """Generates a simple, counterbored, or countersunk hole with an optional drill point."""


    def do_modal(self, context, event):
        segment_factor = 1 if self.key_shift else 2

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.hole_diameter_input_stream = update_stream(self.hole_diameter_input_stream, event.type)
                self.hole_diameter = get_stream_value(self.hole_diameter_input_stream, self.unit_scaled_factor)
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=3))
                self.dirty = True
            elif self.key_ctrl:
                self.hole_depth_input_stream = update_stream(self.hole_depth_input_stream, event.type)
                self.hole_depth = get_stream_value(self.hole_depth_input_stream, self.unit_scaled_factor)
                self.dirty = True
            elif self.key_ctrl_alt:
                self.counter_diameter_input_stream = update_stream(self.counter_diameter_input_stream, event.type)
                self.counter_diameter = get_stream_value(self.counter_diameter_input_stream, self.unit_scaled_factor)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.hole_diameter_input_stream) and self.hard_stream_reset or no_stream(self.hole_diameter_input_stream):
                    self.hole_diameter = default_hole_diameter
                    self.dirty = True
                self.hole_diameter_input_stream = new_stream()
            elif self.key_alt:
                if has_stream(self.segments_input_stream) and self.hard_stream_reset or no_stream(self.segments_input_stream):
                    self.segments = default_segments
                    self.dirty = True
                self.segments_input_stream = new_stream()
            elif self.key_ctrl:
                if has_stream(self.hole_depth_input_stream) and self.hard_stream_reset or no_stream(self.hole_depth_input_stream):
                    self.hole_depth = default_hole_depth
                    self.dirty = True
                self.hole_depth_input_stream = new_stream()
            elif self.key_ctrl_alt:
                if has_stream(self.counter_diameter_input_stream) and self.hard_stream_reset or no_stream(self.counter_diameter_input_stream):
                    self.counter_diameter = default_counter_diameter
                    self.dirty = True
                self.counter_diameter_input_stream = new_stream()

        if pressed(event, {'H'}):
            self.hole_type = (self.hole_type + 1) % len(hole_types)
            self.dirty = True

        if pressed(event, {'D'}):
            self.drill_point = (self.drill_point + 1) % len(drill_points)
            self.dirty = True

        if self.key_step_up:
            if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = 4 if self.segments == 3 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = 4 if self.segments == 3 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.hole_diameter_input_stream) and self.key_no_modifiers:
                self.hole_diameter += self.step_size
                self.dirty = True
            elif no_stream(self.hole_depth_input_stream) and self.key_ctrl:
                self.hole_depth += self.step_size
                self.dirty = True
            elif no_stream(self.counter_diameter_input_stream) and self.key_ctrl_alt:
                self.counter_diameter += self.step_size
                self.dirty = True

        if self.key_step_down:
            if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = max(3, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(3, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.hole_diameter_input_stream) and self.key_no_modifiers:
                self.hole_diameter = max(0, self.hole_diameter - self.step_size)
                self.dirty = True
            elif no_stream(self.hole_depth_input_stream) and self.key_ctrl:
                self.hole_depth -= self.step_size
                self.dirty = True
            elif no_stream(self.counter_diameter_input_stream) and self.key_ctrl_alt:
                self.counter_diameter = max(0, self.counter_diameter - self.step_size)
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.hole_diameter_input_stream) and self.key_no_modifiers:
                self.hole_diameter = max(0, self.hole_diameter + self.mouse_value)
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(3, self.segments + self.mouse_step)
                self.dirty = True
            elif no_stream(self.hole_depth_input_stream) and self.key_ctrl:
                self.hole_depth += self.mouse_value
                self.dirty = True
            elif no_stream(self.counter_diameter_input_stream) and self.key_ctrl_alt:
                self.counter_diameter = max(0, self.counter_diameter + self.mouse_value)
                self.dirty = True


    def do_invoke(self, context, event):
        self.dirty = False

        self.selected_objects = context.selected_objects

        self.segments_input_stream = new_stream()
        self.hole_diameter_input_stream = new_stream()
        self.hole_depth_input_stream = new_stream()
        self.counter_diameter_input_stream = new_stream()

        self.hole_type = hole_types["simple"]
        self.drill_point = drill_points["flat"]

        self.segments = default_segments
        self.hole_diameter = default_hole_diameter
        self.hole_depth = default_hole_depth
        self.counter_diameter = default_counter_diameter

        self.target_object = get_real_active_object(context)
        previous_op = False
        if self.target_object != None:
            for mod in context.active_object.modifiers:
                if mod.type == 'NODES' and mod.node_group.name == 'ND.HoleGenerator':
                    self.hole_gen = mod
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
        return ctx_obj_mode(context) and ctx_objects_selected_range(context, 0, 1)


    def prepare_new_operator(self, context):
        self.summoned = False

        add_single_vertex_object(self, context, "Hole Generator")
        align_object_to_3d_cursor(self, context)

        self.hole_gen_object = get_real_active_object(context)
        self.boolean_object = None

        self.add_hole_generator(context)
        self.add_smooth_shading(context)
        self.add_boolean(context)


    def summon_old_operator(self, context):
        self.summoned = True

        self.hole_gen_object = get_real_active_object(context)

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


    def add_hole_generator(self, context):
        hole_gen = new_modifier(context.active_object, 'Hole Generator — ND', 'NODES', rectify=False)
        hole_gen.node_group = bpy.data.node_groups['ND.HoleGenerator']

        self.hole_gen = hole_gen


    def add_smooth_shading(self, context):
        if not get_preferences().enable_auto_smooth:
            return

        if app_minor_version() >= (4, 1):
            add_smooth_by_angle(context, self.hole_gen_object)
            return

        bpy.ops.object.shade_smooth()
        self.hole_gen_object.data.use_auto_smooth = True
        self.hole_gen_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))


    def add_boolean(self, context):
        if self.target_object == None:
            return

        if not len(self.selected_objects) == 1:
            return

        bpy.ops.object.select_all(action='DESELECT')
        self.hole_gen_object.select_set(True)
        for obj in self.selected_objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            self.boolean_object = obj

        bpy.ops.nd.bool_vanilla('INVOKE_DEFAULT', mode='DIFFERENCE')

        bpy.ops.object.select_all(action='DESELECT')
        self.hole_gen_object.select_set(True)
        bpy.context.view_layer.objects.active = self.hole_gen_object


    def operate(self, context):
        self.hole_gen[socket_map["segments"]] = int(self.segments)
        self.hole_gen[socket_map["hole_diameter"]] = self.hole_diameter
        self.hole_gen[socket_map["counter_diameter"]] = self.counter_diameter
        self.hole_gen[socket_map["hole_depth"]] = self.hole_depth
        self.hole_gen[socket_map["hole_type"]] = self.hole_type
        self.hole_gen[socket_map["drill_point"]] = self.drill_point

        if not self.summoned:
            self.hole_gen[socket_map["protrusion_distance"]] = 0.005

            if self.hole_type == hole_types["simple"]:
                self.counter_diameter = self.hole_diameter * 1.25

            self.hole_gen[socket_map["counterbore_depth"]] = self.hole_depth * 0.15

        self.hole_gen.node_group.interface_update(context)

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        if self.summoned:
            self.segments = self.segments_prev
            self.hole_diameter = self.hole_diameter_prev
            self.hole_depth = self.hole_depth_prev
            self.counter_diameter = self.counter_diameter_prev
            self.hole_type = self.hole_type_prev
            self.drill_point = self.drill_point_prev

            self.operate(context)

        if not self.summoned:
            if self.boolean_object:
                # Remove the boolean modifier from the original active object
                for mod in self.boolean_object.modifiers:
                    print(mod)
                    if mod.type == 'BOOLEAN' and mod.object == self.hole_gen_object:
                        self.boolean_object.modifiers.remove(mod)
                        break

            bpy.data.objects.remove(self.hole_gen_object, do_unlink=True)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Hole Diameter: {(self.hole_diameter * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.unit_step_hint,
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.hole_diameter_input_stream)

    draw_property(
        self,
        f"Segments: {self.segments}",
        self.generate_key_hint("Alt / Scroll" if self.extend_mouse_values else "Alt", self.generate_step_hint(2, 1)),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.segments_input_stream)

    draw_property(
        self,
        f"Hole Depth: {(self.hole_depth * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.generate_key_hint("Ctrl", self.unit_step_hint),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.hole_depth_input_stream)

    if self.hole_type == hole_types["counterbore"] or self.hole_type == hole_types["countersunk"]:
        draw_property(
            self,
            f"Counter Diameter: {(self.counter_diameter * self.display_unit_scale):.2f}{self.unit_suffix}",
            self.generate_key_hint("Ctrl + Alt", self.unit_step_hint),
            active=self.key_ctrl_alt,
            alt_mode=self.key_shift_ctrl_alt,
            mouse_value=True,
            input_stream=self.counter_diameter_input_stream)

    draw_hint(
        self,
        "Hole Type [H]: {}".format(hole_type_names[self.hole_type]),
        ", ".join(hole_type_names))

    draw_hint(
        self,
        "Drill Point [D]: {}".format(drill_point_names[self.drill_point]),
        ", ".join(drill_point_names))


def register():
    bpy.utils.register_class(ND_OT_hole_generator)


def unregister():
    bpy.utils.unregister_class(ND_OT_hole_generator)
    unregister_draw_handler()
