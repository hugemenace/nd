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
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor
from .. lib.preferences import get_preferences, get_scene_unit_factor
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, ensure_tail_mod_consistency, add_smooth_by_angle
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, ctx_edit_mode, obj_is_mesh, ctx_objects_selected, app_minor_version
from .. lib.points import init_points, register_points_handler, unregister_points_handler


socket_map = {
    "profile_segments": "Socket_5",
    "profile_radius": "Socket_2",
    "base_corner_segments": "Socket_11",
    "base_corner_radius": "Socket_12",
    "fill_caps": "Socket_6",
    "start_connector": "Socket_16",
    "start_connector_rotation": "Socket_18",
    "end_connector": "Socket_17",
    "end_connector_rotation": "Socket_19",
    "vertex_merge_distance": "Socket_7",
}


default_profile_radius = 0.01
default_profile_segments = 16
default_base_corner_radius = 0.02
default_base_corner_segments = 8

MODE_PIPE = 0
MODE_CORNERS = 1
MODE_ENDS = 2

modes = ["Pipe", "Corners", "Ends"]


class ND_OT_pipe_generator(BaseOperator):
    bl_idname = "nd.pipe_generator"
    bl_label = "Pipe Generator"
    bl_description = """Generates a pipe from an edge path with customisable corner parameters
CTRL — Remove existing modifiers"""


    def do_modal(self, context, event):
        segment_factor = 1 if self.key_shift else 2
        angle_factor = 1 if self.key_shift else 10

        if self.key_numeric_input:
            if self.mode == MODE_CORNERS:
                if self.key_ctrl:
                    self.vertex_radius_input_streams[self.selected_vertex_index] = update_stream(self.vertex_radius_input_streams[self.selected_vertex_index], event.type)
                    self.vertex_radius_attr.data[self.selected_vertex_index].value = get_stream_value(self.vertex_radius_input_streams[self.selected_vertex_index], self.unit_scaled_factor)
                    self.dirty = True
                elif self.key_alt:
                    self.vertex_segments_input_streams[self.selected_vertex_index] = update_stream(self.vertex_segments_input_streams[self.selected_vertex_index], event.type)
                    self.vertex_segments_attr.data[self.selected_vertex_index].value = int(get_stream_value(self.vertex_segments_input_streams[self.selected_vertex_index], min_value=0))
                    self.dirty = True
            if self.mode == MODE_PIPE:
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
            if self.mode == MODE_ENDS:
                if self.key_ctrl:
                    self.start_connector_rotation_input_stream = update_stream(self.start_connector_rotation_input_stream, event.type)
                    self.start_connector_rotation = get_stream_value(self.start_connector_rotation_input_stream)
                    if self.sync_connectors:
                        self.end_connector_rotation_input_stream = self.start_connector_rotation_input_stream
                        self.end_connector_rotation = self.start_connector_rotation
                    self.dirty = True
                elif not self.sync_connectors and self.key_ctrl_alt:
                    self.end_connector_rotation_input_stream = update_stream(self.end_connector_rotation_input_stream, event.type)
                    self.end_connector_rotation = get_stream_value(self.end_connector_rotation_input_stream)
                    self.dirty = True

        if self.key_reset:
            if self.mode == MODE_CORNERS:
                if self.key_ctrl:
                    if has_stream(self.vertex_radius_input_streams[self.selected_vertex_index]) and self.hard_stream_reset or no_stream(self.vertex_radius_input_streams[self.selected_vertex_index]):
                        self.vertex_radius_attr.data[self.selected_vertex_index].value = 0.0
                        self.dirty = True
                    self.vertex_radius_input_streams[self.selected_vertex_index] = new_stream()
                elif self.key_alt:
                    if has_stream(self.vertex_segments_input_streams[self.selected_vertex_index]) and self.hard_stream_reset or no_stream(self.vertex_segments_input_streams[self.selected_vertex_index]):
                        self.vertex_segments_attr.data[self.selected_vertex_index].value = 0
                        self.dirty = True
                    self.vertex_segments_input_streams[self.selected_vertex_index] = new_stream()
            if self.mode == MODE_PIPE:
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
            if self.mode == MODE_ENDS:
                if self.key_ctrl:
                    if has_stream(self.start_connector_rotation_input_stream) and self.hard_stream_reset or no_stream(self.start_connector_rotation_input_stream):
                        self.start_connector_rotation = 0
                        if self.sync_connectors:
                            self.end_connector_rotation = 0
                        self.dirty = True
                    self.start_connector_rotation_input_stream = new_stream()
                    if self.sync_connectors:
                        self.end_connector_rotation_input_stream = new_stream()
                elif not self.sync_connectors and self.key_ctrl_alt:
                    if has_stream(self.end_connector_rotation_input_stream) and self.hard_stream_reset or no_stream(self.end_connector_rotation_input_stream):
                        self.end_connector_rotation = 0
                        self.dirty = True
                    self.end_connector_rotation_input_stream = new_stream()

        if self.mode == MODE_PIPE and pressed(event, {'F'}):
            self.fill_caps = not self.fill_caps
            self.dirty = True

        if pressed(event, {'C'}):
            self.mode = (self.mode + 1) % len(modes)
            self.dirty = True

        if self.mode == MODE_CORNERS and pressed(event, {'R'}):
            vertex = self.vertex_cache[self.selected_vertex_index][0]
            self.vertex_radius_attr.data[vertex.index].value = 0.0
            self.vertex_segments_attr.data[vertex.index].value = 0

        if self.mode == MODE_ENDS and pressed(event, {'R'}):
            self.selected_start_connector_index = None
            self.start_connector_rotation = 0
            self.selected_end_connector_index = None
            self.end_connector_rotation = 0
            self.sync_connectors = True
            self.dirty = True

        if self.mode == MODE_CORNERS and pressed(event, {'A'}):
            for i, attr in enumerate(self.vertex_radius_attr.data):
                attr.value = 0.0

            for i, attr in enumerate(self.vertex_segments_attr.data):
                attr.value = 0

        if self.mode == MODE_ENDS and pressed(event, {'S'}):
            self.sync_connectors = not self.sync_connectors
            self.dirty = True

        if self.key_step_up:
            if self.mode == MODE_CORNERS:
                if self.key_no_modifiers:
                    self.selected_vertex_index = (self.selected_vertex_index + 1) % len(self.vertex_cache)
                    self.dirty = True
                elif no_stream(self.vertex_radius_input_streams[self.selected_vertex_index]) and self.key_ctrl:
                    vertex = self.vertex_cache[self.selected_vertex_index][0]
                    vertex_radius = self.vertex_radius_attr.data[vertex.index].value
                    vertex_radius += self.step_size
                    self.vertex_radius_attr.data[vertex.index].value = vertex_radius
                    self.dirty = True
                elif no_stream(self.vertex_segments_input_streams[self.selected_vertex_index]) and self.key_alt:
                    vertex = self.vertex_cache[self.selected_vertex_index][0]
                    vertex_segments = self.vertex_segments_attr.data[vertex.index].value
                    vertex_segments += 1
                    self.vertex_segments_attr.data[vertex.index].value = vertex_segments
                    self.dirty = True
            if self.mode == MODE_PIPE:
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
            if self.mode == MODE_ENDS:
                if self.key_no_modifiers:
                    if self.selected_start_connector_index is None:
                        self.selected_start_connector_index = 0
                    elif self.selected_start_connector_index == len(self.connectors) - 1:
                        self.selected_start_connector_index = None
                    else:
                        self.selected_start_connector_index += 1
                    self.dirty = True
                elif not self.sync_connectors and self.key_alt:
                    if self.selected_end_connector_index is None:
                        self.selected_end_connector_index = 0
                    elif self.selected_end_connector_index == len(self.connectors) - 1:
                        self.selected_end_connector_index = None
                    else:
                        self.selected_end_connector_index += 1
                    self.dirty = True
                elif no_stream(self.start_connector_rotation_input_stream) and self.key_ctrl:
                    self.start_connector_rotation = min(360, self.start_connector_rotation + angle_factor)
                    self.dirty = True
                elif no_stream(self.end_connector_rotation_input_stream) and not self.sync_connectors and self.key_ctrl_alt:
                    self.end_connector_rotation = min(360, self.end_connector_rotation + angle_factor)
                    self.dirty = True

        if self.key_step_down:
            if self.mode == MODE_CORNERS:
                if self.key_no_modifiers:
                    self.selected_vertex_index = (self.selected_vertex_index - 1) % len(self.vertex_cache)
                    self.dirty = True
                elif no_stream(self.vertex_radius_input_streams[self.selected_vertex_index]) and self.key_ctrl:
                    vertex = self.vertex_cache[self.selected_vertex_index][0]
                    vertex_radius = self.vertex_radius_attr.data[vertex.index].value
                    vertex_radius = max(0, vertex_radius - self.step_size)
                    self.vertex_radius_attr.data[vertex.index].value = vertex_radius
                    self.dirty = True
                elif no_stream(self.vertex_segments_input_streams[self.selected_vertex_index]) and self.key_alt:
                    vertex = self.vertex_cache[self.selected_vertex_index][0]
                    vertex_segments = self.vertex_segments_attr.data[vertex.index].value
                    vertex_segments = max(0, vertex_segments - 1)
                    self.vertex_segments_attr.data[vertex.index].value = vertex_segments
                    self.dirty = True
            if self.mode == MODE_PIPE:
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
                    self.base_corner_radius = max(0, self.base_corner_radius - self.step_size)
                    self.dirty = True
                elif no_stream(self.base_corner_segments_input_stream) and self.key_ctrl_alt:
                    self.base_corner_segments = max(1, self.base_corner_segments - segment_factor)
                    self.dirty = True
            if self.mode == MODE_ENDS:
                if self.key_no_modifiers:
                    if self.selected_start_connector_index is None:
                        self.selected_start_connector_index = len(self.connectors) - 1
                    elif self.selected_start_connector_index == 0:
                        self.selected_start_connector_index = None
                    else:
                        self.selected_start_connector_index -= 1
                    self.dirty = True
                elif not self.sync_connectors and self.key_alt:
                    if self.selected_end_connector_index is None:
                        self.selected_end_connector_index = len(self.connectors) - 1
                    elif self.selected_end_connector_index == 0:
                        self.selected_end_connector_index = None
                    else:
                        self.selected_end_connector_index -= 1
                    self.dirty = True
                elif no_stream(self.start_connector_rotation_input_stream) and self.key_ctrl:
                    self.start_connector_rotation = max(-360, self.start_connector_rotation - angle_factor)
                    self.dirty = True
                elif no_stream(self.end_connector_rotation_input_stream) and not self.sync_connectors and self.key_ctrl_alt:
                    self.end_connector_rotation = max(-360, self.end_connector_rotation - angle_factor)
                    self.dirty = True

        if self.key_confirm:
            self.finish(context)
            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.mode == MODE_CORNERS:
                if self.key_ctrl:
                    vertex = self.vertex_cache[self.selected_vertex_index][0]
                    vertex_radius = self.vertex_radius_attr.data[vertex.index].value
                    vertex_radius = max(0, vertex_radius + self.mouse_value)
                    self.vertex_radius_attr.data[vertex.index].value = vertex_radius
                    self.dirty = True
                elif self.key_alt:
                    vertex = self.vertex_cache[self.selected_vertex_index][0]
                    vertex_segments = self.vertex_segments_attr.data[vertex.index].value
                    vertex_segments = max(0, vertex_segments + self.mouse_step)
                    self.vertex_segments_attr.data[vertex.index].value = vertex_segments
                    self.dirty = True
            if self.mode == MODE_PIPE:
                if no_stream(self.profile_radius_input_stream) and self.key_no_modifiers:
                    self.profile_radius = max(0, self.profile_radius + self.mouse_value)
                    self.dirty = True
                elif no_stream(self.profile_segments_input_stream) and self.key_alt:
                    self.profile_segments = max(3, self.profile_segments + self.mouse_step)
                    self.dirty = True
                elif no_stream(self.base_corner_radius_input_stream) and self.key_ctrl:
                    self.base_corner_radius = max(0, self.base_corner_radius + self.mouse_value)
                    self.dirty = True
                elif no_stream(self.base_corner_segments_input_stream) and self.key_ctrl_alt:
                    self.base_corner_segments = max(1, self.base_corner_segments + self.mouse_step)
                    self.dirty = True
            if self.mode == MODE_ENDS:
                if no_stream(self.start_connector_rotation_input_stream) and self.key_ctrl:
                    self.start_connector_rotation = min(360, max(-360, self.start_connector_rotation + self.mouse_value_mag))
                    if self.sync_connectors:
                        self.end_connector_rotation = self.start_connector_rotation
                    self.dirty = True
                elif not self.sync_connectors and no_stream(self.end_connector_rotation_input_stream) and self.key_ctrl_alt:
                    self.end_connector_rotation = min(360, max(-360, self.end_connector_rotation + self.mouse_value_mag))
                    self.dirty = True


    def do_invoke(self, context, event):
        try:
            bpy.data.node_groups['ND.PipeGenerator']
        except:
            self.report({'ERROR'}, "ND.PipeGenerator node group not found. Please restart Blender.")
            return {'CANCELLED'}

        self.dirty = False
        self.edit_mode = ctx_edit_mode(context)

        self.profile_segments_input_stream = new_stream()
        self.profile_radius_input_stream = new_stream()
        self.base_corner_segments_input_stream = new_stream()
        self.base_corner_radius_input_stream = new_stream()
        self.start_connector_rotation_input_stream = new_stream()
        self.end_connector_rotation_input_stream = new_stream()

        self.mode = MODE_PIPE

        self.fill_caps = True
        self.profile_segments = default_profile_segments
        self.profile_radius = default_profile_radius
        self.base_corner_segments = default_base_corner_segments
        self.base_corner_radius = default_base_corner_radius

        self.selected_vertex_index = 0
        self.sync_connectors = True
        self.selected_start_connector_index = None
        self.start_connector_rotation = 0
        self.selected_end_connector_index = None
        self.end_connector_rotation = 0

        self.bm = bmesh.new()
        self.bm.from_mesh(context.active_object.data)
        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()

        self.attributes = context.active_object.data.attributes
        self.vertex_radius_attr = None
        self.vertex_segments_attr = None

        raw_connectors = []
        for collection in bpy.data.collections:
            if collection.name == "ND.Connectors":
                raw_connectors = list(collection.children)
                break

        raw_connectors = list(filter(lambda c: not c.name.startswith("ND._"), raw_connectors))

        self.connectors = [(c.name.lstrip("ND."), c) for c in raw_connectors]
        self.supports_connectors = len(self.connectors) > 0

        if len(self.bm.edges) < 1:
            self.report({'INFO'}, "Selected object has no edges")
            return {'CANCELLED'}

        if self.edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')

        self.configure_attributes(context)

        self.vertex_radius_input_streams = [new_stream() for _ in self.vertex_radius_attr.data]
        self.vertex_segments_input_streams = [new_stream() for _ in self.vertex_segments_attr.data]

        previous_op = False
        for mod in context.active_object.modifiers:
            if mod.type == 'NODES' and mod.node_group.name == 'ND.PipeGenerator':
                self.pipe_gen = mod
                previous_op = True
                break

        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, 'Pipe Generator — ND')
            remove_modifiers_ending_with(context.selected_objects, '— ND SBA')

            for attr in self.vertex_radius_attr.data:
                attr.value = 0.0

            for attr in self.vertex_segments_attr.data:
                attr.value = 0

            return {'FINISHED'}

        if previous_op:
            self.summon_old_operator(context)
        else:
            self.prepare_new_operator(context)

        self.world_matrix = context.active_object.matrix_world
        self.vertex_cache = [(v, self.world_matrix @ v.co) for v in self.bm.verts if len(v.link_edges) == 2]

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        init_points(self)
        register_points_handler(self)

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

        self.pipe_gen_object = get_real_active_object(context)

        self.add_pipe_generator(context)
        self.add_smooth_shading(context)


    def summon_old_operator(self, context):
        self.summoned = True

        self.pipe_gen_object = get_real_active_object(context)

        self.profile_radius_prev = self.profile_radius = self.pipe_gen[socket_map["profile_radius"]]
        self.profile_segments_prev = self.profile_segments = self.pipe_gen[socket_map["profile_segments"]]
        self.base_corner_radius_prev = self.base_corner_radius = self.pipe_gen[socket_map["base_corner_radius"]]
        self.base_corner_segments_prev = self.base_corner_segments = self.pipe_gen[socket_map["base_corner_segments"]]
        self.fill_caps_prev = self.fill_caps = self.pipe_gen[socket_map["fill_caps"]]
        self.vertex_merge_distance_prev = self.vertex_merge_distance = self.pipe_gen[socket_map["vertex_merge_distance"]]
        self.start_connector_rotation_prev = self.start_connector_rotation = degrees(self.pipe_gen[socket_map["start_connector_rotation"]])
        self.end_connector_rotation_prev = self.end_connector_rotation = degrees(self.pipe_gen[socket_map["end_connector_rotation"]])

        self.selected_start_connector_index = None
        self.selected_end_connector_index = None
        self.sync_connectors = False

        for i, connector in enumerate(self.connectors):
            if connector[1] == self.pipe_gen[socket_map["start_connector"]]:
                self.selected_start_connector_index = i
            if connector[1] == self.pipe_gen[socket_map["end_connector"]]:
                self.selected_end_connector_index = i

        if self.selected_start_connector_index == self.selected_end_connector_index \
                and self.start_connector_rotation == self.end_connector_rotation:
            self.sync_connectors = True

        if get_preferences().lock_overlay_parameters_on_recall:
            self.profile_radius_input_stream = set_stream(self.profile_radius)
            self.profile_segments_input_stream = set_stream(self.profile_segments)
            self.base_corner_radius_input_stream = set_stream(self.base_corner_radius)
            self.base_corner_segments_input_stream = set_stream(self.base_corner_segments)
            self.start_connector_rotation_input_stream = set_stream(self.start_connector_rotation)
            self.end_connector_rotation_input_stream = set_stream(self.end_connector_rotation)

            for i, attr in enumerate(self.vertex_radius_attr.data):
                if attr.value != 0.0:
                    self.vertex_radius_input_streams[i] = set_stream(attr.value)

            for i, attr in enumerate(self.vertex_segments_attr.data):
                if attr.value != 0:
                    self.vertex_segments_input_streams[i] = set_stream(attr.value)

        self.prev_vertex_radii = [attr.value for attr in self.vertex_radius_attr.data]
        self.prev_vertex_segments = [attr.value for attr in self.vertex_segments_attr.data]


    def add_pipe_generator(self, context):
        pipe_gen = new_modifier(context.active_object, 'Pipe Generator — ND', 'NODES', rectify=False)
        pipe_gen.node_group = bpy.data.node_groups['ND.PipeGenerator']

        self.pipe_gen = pipe_gen


    def configure_attributes(self, context):
        self.vertex_radius_attr = self.attributes.get("ND.VertexRadius")
        if self.vertex_radius_attr == None:
            self.vertex_radius_attr = self.attributes.new(name="ND.VertexRadius", type='FLOAT', domain='POINT')

        self.vertex_segments_attr = self.attributes.get("ND.VertexSegments")
        if self.vertex_segments_attr == None:
            self.vertex_segments_attr = self.attributes.new(name="ND.VertexSegments", type='INT', domain='POINT')


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
        self.primary_points = []
        self.secondary_points = []

        if self.mode == MODE_CORNERS:
            selected_vertex = self.vertex_cache[self.selected_vertex_index]

            self.primary_points = [selected_vertex[1]]
            self.secondary_points = [point for _v, point in self.vertex_cache if point != selected_vertex[1]]

        if self.mode == MODE_PIPE:
            self.pipe_gen[socket_map["profile_radius"]] = self.profile_radius
            self.pipe_gen[socket_map["profile_segments"]] = int(self.profile_segments)
            self.pipe_gen[socket_map["base_corner_radius"]] = self.base_corner_radius
            self.pipe_gen[socket_map["base_corner_segments"]] = int(self.base_corner_segments)
            self.pipe_gen[socket_map["fill_caps"]] = self.fill_caps

            if not self.summoned:
                self.pipe_gen[socket_map["vertex_merge_distance"]] = min(self.profile_radius, self.base_corner_radius) * 0.1

            self.pipe_gen.node_group.interface_update(context)

        if self.mode == MODE_ENDS:
            start_connector = None
            if self.supports_connectors and self.selected_start_connector_index != None:
                start_connector = self.connectors[self.selected_start_connector_index][1]

            end_connector = None
            if self.supports_connectors and self.selected_end_connector_index != None:
                end_connector = self.connectors[self.selected_end_connector_index][1]

            if self.sync_connectors:
                end_connector = start_connector
                self.end_connector_rotation = self.start_connector_rotation
                self.selected_end_connector_index = self.selected_start_connector_index

            self.pipe_gen[socket_map["start_connector"]] = start_connector
            self.pipe_gen[socket_map["start_connector_rotation"]] = radians(self.start_connector_rotation)
            self.pipe_gen[socket_map["end_connector"]] = end_connector
            self.pipe_gen[socket_map["end_connector_rotation"]] = radians(self.end_connector_rotation)

            self.pipe_gen.node_group.interface_update(context)

            scene_children = bpy.context.scene.collection.children

            if start_connector != None and scene_children.get(start_connector.name) == None:
                # NOTE: This is a hack to ensure the start connector correctly updates in the viewport.
                scene_children.link(start_connector)
                scene_children.unlink(start_connector)

            if end_connector != None and scene_children.get(end_connector.name) == None:
                # NOTE: This is a hack to ensure the end connector correctly updates in the viewport.
                scene_children.link(end_connector)
                scene_children.unlink(end_connector)

        self.dirty = False


    def finish(self, context):
        if self.edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')

        unregister_draw_handler()
        unregister_points_handler()


    def revert(self, context):
        if self.summoned:
            self.profile_radius = self.profile_radius_prev
            self.profile_segments = self.profile_segments_prev
            self.base_corner_radius = self.base_corner_radius_prev
            self.base_corner_segments = self.base_corner_segments_prev
            self.fill_caps = self.fill_caps_prev
            self.vertex_merge_distance = self.vertex_merge_distance_prev
            self.start_connector_rotation = self.start_connector_rotation_prev
            self.end_connector_rotation = self.end_connector_rotation_prev

            for i, attr in enumerate(self.vertex_radius_attr.data):
                attr.value = self.prev_vertex_radii[i]

            for i, attr in enumerate(self.vertex_segments_attr.data):
                attr.value = self.prev_vertex_segments[i]

            self.operate(context)

        if not self.summoned:
            remove_modifiers_ending_with([context.active_object], 'Pipe Generator — ND')
            remove_modifiers_ending_with([context.active_object], '— ND SBA')

        if self.edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')

        unregister_draw_handler()
        unregister_points_handler()


def draw_text_callback(self):
    draw_header(self)

    if self.mode == MODE_PIPE:
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

        if len(self.vertex_cache) > 0:
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

    if self.mode == MODE_CORNERS:
        draw_property(
            self,
            f"Vertex: {self.selected_vertex_index + 1}/{len(self.vertex_cache)}",
            "Current active vertex",
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=False)

        vertex_radius = self.vertex_radius_attr.data[self.selected_vertex_index].value
        draw_property(
            self,
            f"Vertex Radius: {(vertex_radius * self.display_unit_scale):.2f}{self.unit_suffix}",
            self.generate_key_hint("Ctrl", self.unit_step_hint),
            active=self.key_ctrl,
            alt_mode=self.key_shift_ctrl,
            mouse_value=True,
            input_stream=self.vertex_radius_input_streams[self.selected_vertex_index])

        vertex_segments = self.vertex_segments_attr.data[self.selected_vertex_index].value
        draw_property(
            self,
            f"Vertex Segments: {vertex_segments}",
            self.generate_key_hint("Alt", self.unit_step_hint),
            active=self.key_alt,
            alt_mode=self.key_shift_alt,
            mouse_value=True,
            input_stream=self.vertex_segments_input_streams[self.selected_vertex_index])

        draw_hint(self, "Reset Corner [R]", "Reverts active corner parameters to default values")
        draw_hint(self, "Reset All Corners [A]", "Reverts ALL corner parameters to default values")

    if self.mode == MODE_ENDS:
        start_connector = "None"
        if self.supports_connectors and self.selected_start_connector_index != None:
            start_connector = self.connectors[self.selected_start_connector_index][0]

        end_connector = "None"
        if self.supports_connectors and self.selected_end_connector_index != None:
            end_connector = self.connectors[self.selected_end_connector_index][0]

        if self.sync_connectors:
            draw_property(
                self,
                "Connectors: {}".format(start_connector),
                "Select from available connectors",
                active=self.key_no_modifiers,
                alt_mode=self.key_shift_no_modifiers,
                mouse_value=False)

            draw_property(
                self,
                "Rotation: {0:.2f}°".format(self.start_connector_rotation),
                self.generate_key_hint("Ctrl", self.generate_step_hint(10, 1)),
                active=self.key_ctrl,
                alt_mode=self.key_shift_ctrl,
                mouse_value=True,
                input_stream=self.start_connector_rotation_input_stream)

        if not self.sync_connectors:
            draw_property(
                self,
                "Start Connector: {}".format(start_connector),
                "Select from available connectors",
                active=self.key_no_modifiers,
                alt_mode=self.key_shift_no_modifiers,
                mouse_value=False)

            draw_property(
                self,
                "Start Connector Rotation: {0:.2f}°".format(self.start_connector_rotation),
                self.generate_key_hint("Ctrl", self.generate_step_hint(10, 1)),
                active=self.key_ctrl,
                alt_mode=self.key_shift_ctrl,
                mouse_value=True,
                input_stream=self.start_connector_rotation_input_stream)

            draw_property(
                self,
                "End Connector: {}".format(end_connector),
                "Select from available connectors",
                active=self.key_alt,
                alt_mode=self.key_shift_alt,
                mouse_value=False)

            draw_property(
                self,
                "End Connector Rotation: {0:.2f}°".format(self.end_connector_rotation),
                self.generate_key_hint("Ctrl + Alt", self.generate_step_hint(10, 1)),
                active=self.key_ctrl_alt,
                alt_mode=self.key_shift_ctrl_alt,
                mouse_value=True,
                input_stream=self.end_connector_rotation_input_stream)

        draw_hint(
            self,
            "Sync Connectors [S]: {}".format("Yes" if self.sync_connectors else "No"),
            "Synchronizes the start and end connectors")

        draw_hint(self, "Reset Connectors [R]", "Reverts connectors to default values")

    draw_hint(
        self,
        "Configuration Mode [C]: {}".format(modes[self.mode]),
        "Switch modes: {}".format(", ".join(modes)))


def register():
    bpy.utils.register_class(ND_OT_pipe_generator)


def unregister():
    bpy.utils.unregister_class(ND_OT_pipe_generator)
    unregister_draw_handler()
