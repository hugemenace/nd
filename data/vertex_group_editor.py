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
import random
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


class ND_OT_vertex_group_editor(BaseOperator):
    bl_idname = "nd.vertex_group_editor"
    bl_label = "Vertex Group Editor"
    bl_description = "Edit vertex groups and member vertex weights interactively"


    key_callbacks = {
        'S': lambda cls, context, event: cls.handle_toggle_set_weight(context, event),
        'R': lambda cls, context, event: cls.handle_randomize_weights(context, event),
    }

    modal_config = {
        'MOVEMENT_PASSTHROUGH': True,
        'ON_CANCEL': lambda cls, context: cls.revert(context),
        'ON_CONFIRM': lambda cls, context: cls.finish(context),
    }


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_edit_mode(context) and obj_is_mesh(target_object) and ctx_objects_selected(context, 1)


    def do_modal(self, context, event):
        weight_factor = 0.01 if self.key_shift else 0.1

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.weight_input_stream = update_stream(self.weight_input_stream, event.type)
                self.weight = get_stream_value(self.weight_input_stream)
                self.mark_dirty()

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.weight_input_stream) and self.hard_stream_reset or no_stream(self.weight_input_stream):
                    if not self.offset_distance:
                        self.distance = sum(self.starting_distances) / len(self.starting_distances)
                    else:
                        self.distance = 0
                    self.mark_dirty()
                self.weight_input_stream = new_stream()

        if self.key_step_up:
            if not self.is_editing and self.key_no_modifiers:
                self.vertex_group_index = (self.vertex_group_index + 1) % len(self.vertex_groups)
                self.mark_dirty()
            elif self.is_editing and self.key_no_modifiers:
                self.weight = min(self.weight + weight_factor, 1.0)
                self.mark_dirty()

        if self.key_step_down:
            if not self.is_editing and self.key_no_modifiers:
                self.vertex_group_index = (self.vertex_group_index - 1) % len(self.vertex_groups)
                self.mark_dirty()
            elif self.is_editing and self.key_no_modifiers:
                self.weight = max(self.weight - weight_factor, 0.0)
                self.mark_dirty()

        if get_preferences().enable_mouse_values:
            if no_stream(self.weight_input_stream) and self.key_no_modifiers:
                self.weight = max(0, min(1, self.weight + self.mouse_value))
                self.mark_dirty()


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        self.target_object = context.active_object
        self.world_matrix = context.active_object.matrix_world

        self.weight_input_stream = new_stream()
        self.weight = 1.0
        self.is_editing = False

        self.set_random_seed()

        self.bm = bmesh.from_edit_mesh(context.active_object.data)
        self.bm.verts.ensure_lookup_table()

        self.selected_verts = [v for v in self.bm.verts if v.select]
        self.selected_vert_indices = [v.index for v in self.selected_verts]
        self.points = [self.world_matrix @ v.co for v in self.selected_verts]

        if len(self.selected_verts) == 0:
            self.report({'INFO'}, "No vertices selected.")
            return {'CANCELLED'}

        self.vertex_groups = context.active_object.vertex_groups
        if not self.vertex_groups:
            self.report({'INFO'}, "No vertex groups found, please create one.")
            return {'CANCELLED'}

        self.vertex_group_index = 0

        self.backup = {}
        for vgroup in self.vertex_groups:
            self.backup[vgroup.index] = {}
            for vert_index in self.selected_vert_indices:
                try:
                    self.backup[vgroup.index][vert_index] = vgroup.weight(vert_index)
                except Exception as e:
                    continue

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        init_points(self)
        register_points_handler(self)

        context.window_manager.modal_handler_add(self)

        self.update_point_visualisation()
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'RUNNING_MODAL'}


    def handle_toggle_set_weight(self, context, event):
        self.weight = 1.0
        self.is_editing = not self.is_editing


    def handle_randomize_weights(self, context, event):
        self.set_vertex_weights(randomize=True)


    def update_point_visualisation(self):
        if not self.is_editing:
            self.primary_points = []
            self.secondary_points = self.points
        else:
            self.primary_points = self.points
            self.secondary_points = []


    def set_random_seed(self):
        self.random_seed = round_dec(random.random() * 1000000, 0)
        random.seed(self.random_seed)


    def set_vertex_weights(self, randomize=False):
        if not randomize:
            self.vertex_groups[self.vertex_group_index].add(self.selected_vert_indices, self.weight, 'REPLACE')
            return

        self.set_random_seed()
        for v in self.selected_vert_indices:
            self.vertex_groups[self.vertex_group_index].add([v], random.uniform(0.0, 1.0), 'REPLACE')


    def operate(self, context):
        if self.is_editing:
            self.set_vertex_weights()

        self.update_point_visualisation()


    def finish(self, context):
        unregister_draw_handler()
        unregister_points_handler()
        bpy.ops.object.mode_set(mode='EDIT')


    def revert(self, context):
        for vert_index in self.selected_vert_indices:
            for vgroup_index, original_weights in self.backup.items():
                if vert_index in original_weights:
                    self.vertex_groups[vgroup_index].add([vert_index], original_weights[vert_index], 'REPLACE')
                else:
                    self.vertex_groups[vgroup_index].remove([vert_index])

        unregister_draw_handler()
        unregister_points_handler()
        bpy.ops.object.mode_set(mode='EDIT')


def draw_text_callback(self):
    draw_header(self)

    draw_hint(
        self,
        f"Vertex Group ({self.vertex_group_index + 1}/{len(self.vertex_groups)}): {self.vertex_groups[self.vertex_group_index].name}",
        "Cycle between vertex groups")

    draw_hint(
        self,
        f"Set Weight [S]: {self.yes_no_str(self.is_editing)}",
        "Set the vertex weights for the selected group")

    if self.is_editing:
        draw_property(
            self,
            f"Weight: {self.weight:.2f}",
            self.generate_step_hint(0.1, 0.01),
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.weight_input_stream)


    if not self.is_editing:
        draw_hint(
            self,
            "Randomize Weights [R]",
            "Randomize the vertex weights for the selected group")

        draw_hint(
            self,
            f"Random Seed: {self.random_seed:.0f}",
            "The auto-generated seed used for randomizing weights")


def register():
    bpy.utils.register_class(ND_OT_vertex_group_editor)


def unregister():
    bpy.utils.unregister_class(ND_OT_vertex_group_editor)
    unregister_draw_handler()
    unregister_points_handler()
