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
# Contributors: Shaddow, Tristo (HM)
# ---

import bpy
import bmesh
from math import radians
from .. lib.base_operator import BaseOperator
from .. lib.overlay import init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences, get_scene_unit_factor
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_edit_mode, obj_is_mesh, ctx_objects_selected, app_minor_version
from .. lib.math import v3_distance, v3_average, v3_direction, round_dec
from .. lib.points import init_points, register_points_handler, unregister_points_handler


class ND_OT_edge_length(BaseOperator):
    bl_idname = "nd.edge_length"
    bl_label = "Edge length"
    bl_description = """Accurately define or offset the length of any selected disconnected edges"""


    def do_modal(self, context, event):
        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.distance_input_stream = update_stream(self.distance_input_stream, event.type)
                self.distance = get_stream_value(self.distance_input_stream, self.unit_scaled_factor)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.distance_input_stream) and self.hard_stream_reset or no_stream(self.distance_input_stream):
                    if not self.offset_distance:
                        self.distance = sum(self.starting_distances) / len(self.starting_distances)
                    else:
                        self.distance = 0
                    self.dirty = True
                self.distance_input_stream = new_stream()

        if pressed(event, {'A'}):
            self.current_anchor = (self.current_anchor + 1) % len(self.anchors)
            self.dirty = True

        if pressed(event, {'D'}):
            self.offset_distance = not self.offset_distance

            offset_distance = (sum(self.starting_distances) / len(self.starting_distances)) * -1.0
            absolute_distance = sum(self.starting_distances) / len(self.starting_distances)

            self.distance += absolute_distance if not self.offset_distance else offset_distance
            self.dirty = True

        if self.key_step_up:
            if no_stream(self.distance_input_stream) and self.key_no_modifiers:
                self.distance = round_dec(self.distance + self.step_size)
                self.dirty = True

        if self.key_step_down:
            if no_stream(self.distance_input_stream) and self.key_no_modifiers:
                self.distance = round_dec(self.distance - self.step_size)
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.distance_input_stream) and self.key_no_modifiers:
                self.distance = max(0, self.distance + self.mouse_value) if not self.offset_distance else self.distance + self.mouse_value
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        self.dirty = False

        self.revert_distance = False
        self.anchors = ["Center", "Start", "End"]
        self.current_anchor = 0
        self.distance = 0

        self.target_object = context.active_object
        self.world_matrix = context.active_object.matrix_world

        self.distance_input_stream = new_stream()

        self.bm = bmesh.from_edit_mesh(context.active_object.data)
        self.bm.verts.ensure_lookup_table()

        selected_verts = [v for v in self.bm.verts if v.select]
        selected_edges = [e for e in self.bm.edges if e.select]

        self.single_edge = len(selected_verts) == 2
        self.offset_distance = not self.single_edge

        if not self.single_edge and len([v.index for e in selected_edges for v in e.verts]) != len(selected_verts):
            self.report({'INFO'}, "Selected edges must be disconnected.")
            return {'CANCELLED'}

        self.selected_vertex_pairs = []
        if not self.single_edge:
            self.selected_vertex_pairs = [
                [edge.verts[0].index, edge.verts[1].index]
                if self.compare_distance_to_cursor(context, edge.verts[0].co, edge.verts[1].co) else
                [edge.verts[1].index, edge.verts[0].index]
                for edge in selected_edges
            ]
        else:
            self.selected_vertex_pairs = [
                [selected_verts[0].index, selected_verts[1].index]
                if self.compare_distance_to_cursor(context, selected_verts[0].co, selected_verts[0].co) else
                [selected_verts[1].index, selected_verts[0].index]
            ]

        self.current_positions = [[
            self.bm.verts[vert_pair[0]].co,
            self.bm.verts[vert_pair[1]].co
        ] for vert_pair in self.selected_vertex_pairs]

        self.starting_positions = [[
            self.bm.verts[vert_pair[0]].co.copy(),
            self.bm.verts[vert_pair[1]].co.copy()
        ] for vert_pair in self.selected_vertex_pairs]

        self.midpoints = [v3_average(pos_pair) for pos_pair in self.starting_positions]
        self.directions = [v3_direction(pos_pair[0], pos_pair[1]) for pos_pair in self.starting_positions]
        self.starting_distances = [v3_distance(pos_pair[0], pos_pair[1]) for pos_pair in self.starting_positions]

        if not self.offset_distance:
            self.distance = sum(self.starting_distances) / len(self.starting_distances)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        init_points(self)
        register_points_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_edit_mode(context) and obj_is_mesh(target_object) and ctx_objects_selected(context, 1)


    def operate(self, context):
        for index, vertex_pair in enumerate(self.selected_vertex_pairs):
            self.move_verts(context, vertex_pair, index)

        if self.current_anchor == 0:
            self.secondary_points = [self.world_matrix @ point for point in self.midpoints]
            self.primary_points = []
            for index, vertex_pair in enumerate(self.selected_vertex_pairs):
                self.primary_points.extend([
                    self.world_matrix @ self.bm.verts[vertex_pair[0]].co,
                    self.world_matrix @ self.bm.verts[vertex_pair[1]].co
                ])

        if self.current_anchor == 1:
            self.secondary_points = [self.world_matrix @ point[0] for point in self.starting_positions]
            self.primary_points = []
            for index, vertex_pair in enumerate(self.selected_vertex_pairs):
                self.primary_points.extend([
                    self.world_matrix @ self.bm.verts[vertex_pair[1]].co,
                ])

        if self.current_anchor == 2:
            self.secondary_points = [self.world_matrix @ point[1] for point in self.starting_positions]
            self.primary_points = []
            for index, vertex_pair in enumerate(self.selected_vertex_pairs):
                self.primary_points.extend([
                    self.world_matrix @ self.bm.verts[vertex_pair[0]].co,
                ])

        self.dirty = False


    def move_verts(self, context, vertex_pair, index):
        vertex_0 = self.bm.verts[vertex_pair[0]]
        vertex_1 = self.bm.verts[vertex_pair[1]]

        match self.current_anchor:
            case 0:
                vertex_0.co = self.get_reference_position(vertex_pair, index, 1) - self.directions[index] * self.get_distance()
                vertex_1.co = self.get_reference_position(vertex_pair, index, 0) + self.directions[index] * self.get_distance()
            case 1:
                vertex_0.co = self.starting_positions[index][0]
                vertex_1.co = self.get_reference_position(vertex_pair, index, 0) + self.directions[index] * self.get_distance()
            case 2:
                vertex_1.co = self.starting_positions[index][1]
                vertex_0.co = self.get_reference_position(vertex_pair, index, 1) - self.directions[index] * self.get_distance()

        bmesh.update_edit_mesh(context.active_object.data)


    def get_distance(self ):
        return self.distance if not self.current_anchor == 0 else self.distance / 2


    def get_reference_position(self, vertex_pair, pos_index, vert_index):
        if self.revert_distance:
            return self.bm.verts[vertex_pair[vert_index]].co

        if self.offset_distance:
            return self.starting_positions[pos_index][not vert_index]

        if self.current_anchor == 0:
            return self.midpoints[pos_index]

        return self.starting_positions[pos_index][vert_index]


    def compare_distance_to_cursor(self, context, coords_0, coords_1):
        cursor_pos = context.scene.cursor.location
        return v3_distance(cursor_pos, coords_0) < v3_distance(cursor_pos, coords_1)


    def finish(self, context):
        unregister_draw_handler()
        unregister_points_handler()


    def revert(self, context):
        self.offset_distance = True
        self.distance = 0
        self.operate(context)

        unregister_draw_handler()
        unregister_points_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Distance: {(self.distance * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.unit_step_hint,
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.distance_input_stream)

    draw_hint(
        self,
        f"Anchor [A]: {self.anchors[self.current_anchor].capitalize()}",
        self.list_options_str(self.anchors))

    distance_types = ['Absolute', 'Offset']
    draw_hint(
        self,
        f"Distance Type [D]: {'Offset' if self.offset_distance else 'Absolute'}",
        self.list_options_str(distance_types))


def register():
    bpy.utils.register_class(ND_OT_edge_length)


def unregister():
    bpy.utils.unregister_class(ND_OT_edge_length)
    unregister_draw_handler()
    unregister_points_handler()
