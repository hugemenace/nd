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
# Contributors: Shaddow
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
from .. lib.math import v3_distance, v3_average



class ND_OT_edge_length(BaseOperator):
    bl_idname = "nd.edge_length"
    bl_label = "Set edge length"
    bl_description = """Allows you to accuratly set the distance between two selected vertices or n not connected selected edges"""


    def do_modal(self, context, event):
        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.distance_input_stream = update_stream(self.distance_input_stream, event.type)
                self.distance = get_stream_value(self.distance_input_stream, self.unit_scaled_factor)
                self.dirty = True


        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.distance_input_stream) and self.hard_stream_reset or no_stream(self.distance_input_stream):
                    self.distance = self.starting_distance
                    self.dirty = True
                self.distance_input_stream = new_stream()
            

        if pressed(event, {'A'}):
            self.current_affect_mode = (self.current_affect_mode + 1) % len(self.affect_modes)
            self.dirty = True


        if pressed(event, {'D'}):
            self.offset_distance = not self.offset_distance
            self.distance += sum(self.starting_distances) / len(self.starting_distances) if not self.offset_distance else - sum(self.starting_distances) / len(self.starting_distances) 
            self.dirty = True


        if self.key_step_up:
            if no_stream(self.distance_input_stream) and self.key_no_modifiers:
                self.distance += self.step_size
                self.dirty = True


        if self.key_step_down:
            if no_stream(self.distance_input_stream) and self.key_no_modifiers:
                self.distance = self.distance - self.step_size
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

        self.affect_modes = ["Both", "Start", "End"]
        self.current_affect_mode = 0

        self.target_object = context.active_object

        self.distance_input_stream = new_stream()

        bm = bmesh.from_edit_mesh(context.active_object.data)
        selected_verts = [v for v in bm.verts if v.select]
        selected_edges = [e for e in bm.edges if e.select]
        self.one_pair = len(selected_verts) == 2
        self.offset_distance = not self.one_pair

        if not self.one_pair and len([v.index for e in selected_edges for v in e.verts]) != len(selected_verts):
            self.report({'INFO'}, "Select two vertices or n edges")
            return {'CANCELLED'}
        
        
        self.selected_vertex_pairs = []
        if not self.one_pair:
            self.selected_vertex_pairs = [
                (e.verts[0].index, e.verts[1].index) 
                for e in selected_edges
            ]
        else:
            self.selected_vertex_pairs = [
                (selected_verts[0].index, selected_verts[1].index)
            ]

        self.starting_positions = [
            (bm.verts[vertex_pair[0]].co.copy(), bm.verts[vertex_pair[1]].co.copy()) for vertex_pair in self.selected_vertex_pairs] 
        self.midpoints = [
            v3_average(position_pair) for position_pair in self.starting_positions]
        self.directions = [
            (position_pair[1] - position_pair[0]).normalized() for position_pair in self.starting_positions]
        self.starting_distances = [
            v3_distance(position_pair[0], position_pair[1]) for position_pair in self.starting_positions]
        self.distance = sum(self.starting_distances) / len(self.starting_distances) if not self.offset_distance else 0

        bm.free()

        
        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_edit_mode(context) and obj_is_mesh(target_object) and ctx_objects_selected(context, 1)



    def operate(self, context):
        for index, vertex_pair in enumerate(self.selected_vertex_pairs):
            self.move_verts(context, vertex_pair, index)

        self.dirty = False

    def move_verts(self, context, vertex_pair, index):
        bm = bmesh.from_edit_mesh(self.target_object.data)
        bm.verts.ensure_lookup_table()

        vertex_0 = bm.verts[vertex_pair[0]]
        vertex_1 = bm.verts[vertex_pair[1]]
        
        match self.current_affect_mode:
            case 0:
                vertex_0.co = self.get_reference_position(bm, vertex_pair, index, 1) - self.directions[index] * self.get_distance()
                vertex_1.co = self.get_reference_position(bm, vertex_pair, index, 0) + self.directions[index] * self.get_distance()
            case 1:
                vertex_0.co = self.starting_positions[index][0]
                vertex_1.co = self.get_reference_position(bm, vertex_pair, index, 0) + self.directions[index] * self.get_distance()
            case 2:
                vertex_1.co = self.starting_positions[index][1]
                vertex_0.co = self.get_reference_position(bm, vertex_pair, index, 1) - self.directions[index] * self.get_distance()


        bmesh.update_edit_mesh(context.active_object.data)


    def get_distance(self ):
        return self.distance if not self.current_affect_mode == 0 else self.distance / 2
 
    
    def get_reference_position(self, bm, vertex_pair, index, index_of_vert):
        if self.revert_distance:
            return bm.verts[vertex_pair[index_of_vert]].co
        elif not self.offset_distance:
            if self.current_affect_mode == 0:
                return self.midpoints[index]
            else:
                return self.starting_positions[index][index_of_vert]
        else:
            return self.starting_positions[index][not index_of_vert]

    

    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        self.offset_distance = True
        self.distance = 0
        self.operate(context)

        unregister_draw_handler()


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
        "Affect [A]: {}".format(self.affect_modes[self.current_affect_mode].capitalize()),
        "Affect ({})".format(", ".join([m.capitalize() for m in self.affect_modes])))
    

    draw_hint(
        self,
        "Distance [D]: {}".format('Offset' if self.offset_distance else 'Overwrite'),
        "Overwrite, Offset")
    


def register():
    bpy.utils.register_class(ND_OT_edge_length)


def unregister():
    bpy.utils.unregister_class(ND_OT_edge_length)
    unregister_draw_handler()
