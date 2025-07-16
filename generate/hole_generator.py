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
from .. lib.overlay import init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor, get_real_active_object
from .. lib.preferences import get_preferences, get_scene_unit_factor
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, ensure_tail_mod_consistency, add_smooth_by_angle
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, ctx_objects_selected_range, ctx_objects_selected, app_minor_version
from .. lib.math import round_dec


MIN_BLENDER_VERSION = (4, 3)


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
    "countersink": 2,
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
default_countersink_angle = 45
default_drill_point_angle = 45

MODE_HOLE = 0
MODE_COUNTER = 1
MODE_DRILL = 2

modes = ["Hole", "Counter", "Drill"]


class ND_OT_hole_generator(BaseOperator):
    bl_idname = "nd.hole_generator"
    bl_label = "Hole Generator"
    bl_description = """Generates a drill hole with the option to counterbore or countersink.

Min Blender Version: %s""" % ('.'.join([str(v) for v in MIN_BLENDER_VERSION]))


    def do_modal(self, context, event):
        segment_factor = 1 if self.key_shift else 2
        angle_factor = 1 if self.key_shift else 5

        if self.key_numeric_input:
            if self.mode == MODE_HOLE:
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
            if self.mode == MODE_COUNTER:
                if self.key_no_modifiers and not self.is_simple_hole():
                    self.counter_diameter_input_stream = update_stream(self.counter_diameter_input_stream, event.type)
                    self.counter_diameter = get_stream_value(self.counter_diameter_input_stream, self.unit_scaled_factor)
                    self.dirty = True
                elif self.key_ctrl and self.is_counterbore_hole():
                    self.counterbore_depth_input_stream = update_stream(self.counterbore_depth_input_stream, event.type)
                    self.counterbore_depth = get_stream_value(self.counterbore_depth_input_stream, self.unit_scaled_factor)
                    self.dirty = True
                elif self.key_ctrl and self.is_countersink_hole():
                    self.countersink_angle_input_stream = update_stream(self.countersink_angle_input_stream, event.type)
                    self.countersink_angle = get_stream_value(self.countersink_angle_input_stream, min_value=0, max_value=90)
                    self.dirty = True
            if self.mode == MODE_DRILL:
                if self.key_no_modifiers and self.is_drill_angle():
                    self.drill_point_angle_input_stream = update_stream(self.drill_point_angle_input_stream, event.type)
                    self.drill_point_angle = get_stream_value(self.drill_point_angle_input_stream, min_value=0, max_value=90)
                    self.dirty = True

        if self.key_reset:
            if self.mode == MODE_HOLE:
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
            if self.mode == MODE_COUNTER:
                if self.key_no_modifiers and not self.is_simple_hole():
                    if has_stream(self.counter_diameter_input_stream) and self.hard_stream_reset or no_stream(self.counter_diameter_input_stream):
                        self.counter_diameter = None
                        self.dirty = True
                    self.counter_diameter_input_stream = new_stream()
                elif self.key_ctrl and self.is_counterbore_hole():
                    if has_stream(self.counterbore_depth_input_stream) and self.hard_stream_reset or no_stream(self.counterbore_depth_input_stream):
                        self.counterbore_depth = None
                        self.dirty = True
                    self.counterbore_depth_input_stream = new_stream()
                elif self.key_ctrl and self.is_countersink_hole():
                    if has_stream(self.countersink_angle_input_stream) and self.hard_stream_reset or no_stream(self.countersink_angle_input_stream):
                        self.countersink_angle = default_countersink_angle
                        self.dirty = True
                    self.countersink_angle_input_stream = new_stream()
            if self.mode == MODE_DRILL:
                if self.key_no_modifiers and self.is_drill_angle():
                    if has_stream(self.drill_point_angle_input_stream) and self.hard_stream_reset or no_stream(self.drill_point_angle_input_stream):
                        self.drill_point_angle = default_drill_point_angle
                        self.dirty = True
                    self.drill_point_angle_input_stream = new_stream()

        if pressed(event, {'H'}) and self.mode == MODE_COUNTER:
            self.hole_type = (self.hole_type + 1) % len(hole_types)
            self.dirty = True

        if pressed(event, {'D'}) and self.mode == MODE_DRILL:
            self.drill_point = (self.drill_point + 1) % len(drill_points)
            self.dirty = True

        if pressed(event, {'C'}):
            self.mode = (self.mode + 1) % len(modes)
            self.dirty = True

        if pressed(event, {'R'}) and self.mode == MODE_COUNTER:
            if not self.is_simple_hole():
                self.counter_diameter = None
                self.counterbore_depth = None
                self.dirty = True

        if self.key_step_up:
            if self.mode == MODE_HOLE:
                if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                    self.segments = 4 if self.segments == 3 else self.segments + segment_factor
                    self.dirty = True
                elif no_stream(self.segments_input_stream) and self.key_alt:
                    self.segments = 4 if self.segments == 3 else self.segments + segment_factor
                    self.dirty = True
                elif no_stream(self.hole_diameter_input_stream) and self.key_no_modifiers:
                    self.hole_diameter = round_dec(self.hole_diameter + self.step_size)
                    self.dirty = True
                elif no_stream(self.hole_depth_input_stream) and self.key_ctrl:
                    self.hole_depth = round_dec(self.hole_depth + self.step_size)
                    self.dirty = True
            if self.mode == MODE_COUNTER:
                if no_stream(self.counter_diameter_input_stream) and self.key_no_modifiers and not self.is_simple_hole():
                    (isCounterDiameterSet, counter_diameter) = self.get_counter_diameter()
                    if not isCounterDiameterSet:
                        self.counter_diameter = counter_diameter
                    self.counter_diameter = round_dec(self.counter_diameter + self.step_size)
                    self.dirty = True
                elif no_stream(self.counterbore_depth_input_stream) and self.key_ctrl and self.is_counterbore_hole():
                    (isCounterboreDepthSet, counterbore_depth) = self.get_counterbore_depth()
                    if not isCounterboreDepthSet:
                        self.counterbore_depth = counterbore_depth
                    self.counterbore_depth = round_dec(self.counterbore_depth + self.step_size)
                    self.dirty = True
                elif no_stream(self.countersink_angle_input_stream) and self.key_ctrl and self.is_countersink_hole():
                    self.countersink_angle = min(90, self.countersink_angle + angle_factor)
                    self.dirty = True
            if self.mode == MODE_DRILL:
                if no_stream(self.drill_point_angle_input_stream) and self.key_no_modifiers and self.is_drill_angle():
                    self.drill_point_angle = min(90, self.drill_point_angle + angle_factor)
                    self.dirty = True

        if self.key_step_down:
            if self.mode == MODE_HOLE:
                if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                    self.segments = max(3, self.segments - segment_factor)
                    self.dirty = True
                elif no_stream(self.segments_input_stream) and self.key_alt:
                    self.segments = max(3, self.segments - segment_factor)
                    self.dirty = True
                elif no_stream(self.hole_diameter_input_stream) and self.key_no_modifiers:
                    self.hole_diameter = max(0, round_dec(self.hole_diameter - self.step_size))
                    self.dirty = True
                elif no_stream(self.hole_depth_input_stream) and self.key_ctrl:
                    self.hole_depth = round_dec(self.hole_depth - self.step_size)
                    self.dirty = True
            if self.mode == MODE_COUNTER:
                if no_stream(self.counter_diameter_input_stream) and self.key_no_modifiers and not self.is_simple_hole():
                    (isCounterDiameterSet, counter_diameter) = self.get_counter_diameter()
                    if not isCounterDiameterSet:
                        self.counter_diameter = counter_diameter
                    self.counter_diameter = max(0, round_dec(self.counter_diameter - self.step_size))
                    self.dirty = True
                elif no_stream(self.counterbore_depth_input_stream) and self.key_ctrl and self.is_counterbore_hole():
                    (isCounterboreDepthSet, counterbore_depth) = self.get_counterbore_depth()
                    if not isCounterboreDepthSet:
                        self.counterbore_depth = counterbore_depth
                    self.counterbore_depth = round_dec(self.counterbore_depth - self.step_size)
                    self.dirty = True
                elif no_stream(self.countersink_angle_input_stream) and self.key_ctrl and self.is_countersink_hole():
                    self.countersink_angle = max(0, self.countersink_angle - angle_factor)
                    self.dirty = True
            if self.mode == MODE_DRILL:
                if no_stream(self.drill_point_angle_input_stream) and self.key_no_modifiers and self.is_drill_angle():
                    self.drill_point_angle = max(0, self.drill_point_angle - angle_factor)
                    self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.mode == MODE_HOLE:
                if no_stream(self.hole_diameter_input_stream) and self.key_no_modifiers:
                    self.hole_diameter = max(0, self.hole_diameter + self.mouse_value)
                    self.dirty = True
                elif no_stream(self.segments_input_stream) and self.key_alt:
                    self.segments = max(3, self.segments + self.mouse_step)
                    self.dirty = True
                elif no_stream(self.hole_depth_input_stream) and self.key_ctrl:
                    self.hole_depth += self.mouse_value
                    self.dirty = True
            if self.mode == MODE_COUNTER:
                if no_stream(self.counter_diameter_input_stream) and self.key_no_modifiers:
                    if self.mouse_value != 0:
                        (isCounterDiameterSet, counter_diameter) = self.get_counter_diameter()
                        if not isCounterDiameterSet:
                            self.counter_diameter = counter_diameter
                        self.counter_diameter = max(0, self.counter_diameter + self.mouse_value)
                        self.dirty = True
                elif no_stream(self.counterbore_depth_input_stream) and self.key_ctrl and self.is_counterbore_hole():
                    if self.mouse_value != 0:
                        (isCounterboreDepthSet, counterbore_depth) = self.get_counterbore_depth()
                        if not isCounterboreDepthSet:
                            self.counterbore_depth = counterbore_depth
                        self.counterbore_depth = max(0, self.counterbore_depth + self.mouse_value)
                        self.dirty = True
                elif no_stream(self.countersink_angle_input_stream) and self.key_ctrl and self.is_countersink_hole():
                    self.countersink_angle = self.countersink_angle = max(0, min(90, self.countersink_angle + self.mouse_value_mag))
                    self.dirty = True
            if self.mode == MODE_DRILL:
                if no_stream(self.drill_point_angle_input_stream) and self.key_no_modifiers and self.is_drill_angle():
                    self.drill_point_angle = self.drill_point_angle = max(0, min(90, self.drill_point_angle + self.mouse_value_mag))
                    self.dirty = True

    def do_invoke(self, context, event):
        try:
            bpy.data.node_groups['ND.HoleGenerator']
        except:
            self.report({'ERROR'}, "ND.HoleGenerator node group not found. Please restart Blender.")
            return {'CANCELLED'}

        self.dirty = False

        self.selected_objects = context.selected_objects

        self.mode = MODE_HOLE

        self.segments_input_stream = new_stream()
        self.hole_diameter_input_stream = new_stream()
        self.hole_depth_input_stream = new_stream()
        self.counter_diameter_input_stream = new_stream()
        self.counterbore_depth_input_stream = new_stream()
        self.countersink_angle_input_stream = new_stream()
        self.drill_point_angle_input_stream = new_stream()

        self.hole_type = hole_types["simple"]
        self.drill_point = drill_points["flat"]

        self.segments = default_segments
        self.hole_diameter = default_hole_diameter
        self.hole_depth = default_hole_depth
        self.counter_diameter = None
        self.counterbore_depth = None
        self.countersink_angle = default_countersink_angle
        self.drill_point_angle = default_drill_point_angle

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
        if app_minor_version() < MIN_BLENDER_VERSION:
            return False

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
        self.counterbore_depth_prev = self.counterbore_depth = self.hole_gen[socket_map["counterbore_depth"]]
        self.countersink_angle_prev = self.countersink_angle = degrees(self.hole_gen[socket_map["countersink_angle"]])
        self.hole_type_prev = self.hole_type = self.hole_gen[socket_map["hole_type"]]
        self.drill_point_prev = self.drill_point = self.hole_gen[socket_map["drill_point"]]
        self.drill_point_angle_prev = self.drill_point_angle = degrees(self.hole_gen[socket_map["drill_point_angle"]])

        if get_preferences().lock_overlay_parameters_on_recall:
            self.hole_diameter_input_stream = set_stream(self.hole_diameter)
            self.segments_input_stream = set_stream(self.segments)
            self.hole_depth_input_stream = set_stream(self.hole_depth)
            self.counter_diameter_input_stream = set_stream(self.counter_diameter)
            self.counterbore_depth_input_stream = set_stream(self.counterbore_depth)
            self.countersink_angle_input_stream = set_stream(self.countersink_angle)
            self.drill_point_angle_input_stream = set_stream(self.drill_point_angle)


    def add_hole_generator(self, context):
        hole_gen = new_modifier(context.active_object, 'Hole Generator — ND', 'NODES', rectify=False)
        hole_gen.node_group = bpy.data.node_groups['ND.HoleGenerator']

        hole_gen[socket_map["protrusion_distance"]] = 0.005

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


    def get_counter_diameter(self):
        if self.counter_diameter != None:
            return (True, self.counter_diameter)

        return (False, self.hole_diameter * 1.8)


    def get_counterbore_depth(self):
        if self.counterbore_depth != None:
            return (True, self.counterbore_depth)

        return (False, min(self.hole_depth * 0.15, self.hole_diameter * 0.5))


    def is_countersink_hole(self):
        return self.hole_type == hole_types["countersink"]


    def is_counterbore_hole(self):
        return self.hole_type == hole_types["counterbore"]


    def is_simple_hole(self):
        return self.hole_type == hole_types["simple"]


    def is_drill_flat(self):
        return self.drill_point == drill_points["flat"]


    def is_drill_angle(self):
        return self.drill_point == drill_points["angle"]


    def operate(self, context):
        (isCounterDiameterSet, counter_diameter) = self.get_counter_diameter()
        (isCounterboreDepthSet, counterbore_depth) = self.get_counterbore_depth()

        if isCounterDiameterSet:
            self.counter_diameter = counter_diameter

        if isCounterboreDepthSet:
            self.counterbore_depth = counterbore_depth

        self.hole_gen[socket_map["segments"]] = int(self.segments)
        self.hole_gen[socket_map["hole_diameter"]] = self.hole_diameter
        self.hole_gen[socket_map["counter_diameter"]] = counter_diameter
        self.hole_gen[socket_map["hole_depth"]] = self.hole_depth
        self.hole_gen[socket_map["hole_type"]] = self.hole_type
        self.hole_gen[socket_map["drill_point"]] = self.drill_point
        self.hole_gen[socket_map["drill_point_angle"]] = radians(self.drill_point_angle)
        self.hole_gen[socket_map["counterbore_depth"]] = counterbore_depth
        self.hole_gen[socket_map["countersink_angle"]] = radians(self.countersink_angle)

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
            self.counterbore_depth = self.counterbore_depth_prev
            self.countersink_angle = self.countersink_angle
            self.hole_type = self.hole_type_prev
            self.drill_point = self.drill_point_prev
            self.drill_point_angle = self.drill_point_angle

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

    if self.mode == MODE_HOLE:
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

    if self.mode == MODE_COUNTER:
        if not self.is_simple_hole():
            (isSet, counter_diameter) = self.get_counter_diameter()
            auto_suffix = "" if isSet else " (Auto)"
            draw_property(
                self,
                f"Counter Diameter: {(counter_diameter * self.display_unit_scale):.2f}{self.unit_suffix}{auto_suffix}",
                self.unit_step_hint,
                active=self.key_no_modifiers,
                alt_mode=self.key_shift_no_modifiers,
                mouse_value=True,
                input_stream=self.counter_diameter_input_stream)

        if self.is_counterbore_hole():
            (isSet, counterbore_depth) = self.get_counterbore_depth()
            auto_suffix = "" if isSet else " (Auto)"
            draw_property(
                self,
                f"Counterbore Depth: {(counterbore_depth * self.display_unit_scale):.2f}{self.unit_suffix}{auto_suffix}",
                self.generate_key_hint("Ctrl", self.unit_step_hint),
                active=self.key_ctrl,
                alt_mode=self.key_shift_ctrl,
                mouse_value=True,
                input_stream=self.counterbore_depth_input_stream)

        if self.is_countersink_hole():
            draw_property(
                self,
                f"Countersink Angle: {(self.countersink_angle):.0f}°",
                self.generate_key_hint("Ctrl", self.generate_step_hint(5, 1)),
                active=self.key_ctrl,
                alt_mode=self.key_shift_ctrl,
                mouse_value=True,
                input_stream=self.countersink_angle_input_stream)

        if not self.is_simple_hole():
            draw_hint(self, "Reset Automation [R]", "Set all parameters to automatic")

        draw_hint(
            self,
            "Hole Type [H]: {}".format(hole_type_names[self.hole_type]),
            ", ".join(hole_type_names))

    if self.mode == MODE_DRILL:
        if self.drill_point == drill_points["angle"]:
            draw_property(
                self,
                f"Drill Point Angle: {(self.drill_point_angle):.0f}°",
                self.generate_step_hint(5, 1),
                active=self.key_no_modifiers,
                alt_mode=self.key_shift_no_modifiers,
                mouse_value=True,
                input_stream=self.drill_point_angle_input_stream)

        draw_hint(
            self,
            "Drill Point [D]: {}".format(drill_point_names[self.drill_point]),
            ", ".join(drill_point_names))

    draw_hint(
        self,
        "Configuration Mode [C]: {}".format(modes[self.mode]),
        "Switch modes: {}".format(", ".join(modes)))


def register():
    bpy.utils.register_class(ND_OT_hole_generator)


def unregister():
    bpy.utils.unregister_class(ND_OT_hole_generator)
    unregister_draw_handler()
