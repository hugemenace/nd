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
    bl_description = """Allows you to accuratly set the distance between two selected vertices"""


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
            self.anchored = not self.anchored
            self.dirty = True

        if pressed(event, {'F'}):
            self.flip = not self.flip
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
                self.distance = max(0, self.distance + self.mouse_value)
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}
        
        self.dirty = False

        self.anchored = False
        self.flip = False

        self.target_object = context.active_object

        self.distance_input_stream = new_stream()

        bm = bmesh.from_edit_mesh(context.active_object.data)
        self.selected_vertices_indexes = [v.index for v in bm.verts if v.select]
        self.starting_positions = [bm.verts[n].co.copy() for n in self.selected_vertices_indexes]
        self.midpoint = v3_average(self.starting_positions)
        self.direction = (self.starting_positions[1] - self.starting_positions[0]).normalized()

        if len(self.selected_vertices_indexes) != 2:
            self.report({'WARNING'}, "Please select exactly two vertices for this operator to function.")
            return {'CANCELLED'}


        self.starting_distance = self.distance = v3_distance(bm.verts[self.selected_vertices_indexes[0]].co - bm.verts[self.selected_vertices_indexes[1]].co)


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
        bm = bmesh.from_edit_mesh(self.target_object.data)
        bm.verts.ensure_lookup_table()

        vertex_0 = bm.verts[self.selected_vertices_indexes[0]]
        vertex_1 = bm.verts[self.selected_vertices_indexes[1]]

        

        if not self.anchored:
            vertex_0.co = self.midpoint - self.direction * (self.distance / 2)
            vertex_1.co = self.midpoint + self.direction * (self.distance / 2)

        elif not self.flip:
            vertex_0.co = self.starting_positions[0]
            vertex_1.co = vertex_0.co + self.direction * self.distance

        else:
            vertex_1.co = self.starting_positions[1]
            vertex_0.co = vertex_1.co - self.direction * self.distance


        bmesh.update_edit_mesh(context.active_object.data)

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        self.distance = self.starting_distance
        self.operate(context)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"distance: {(self.distance * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.unit_step_hint,
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.distance_input_stream)


    draw_hint(
        self,
        "Anchored [A]: {}".format('Yes' if self.anchored else 'No'),
        "Create an Inset or Outset")

    draw_hint(
        self,
        "Flip [F]: {}".format('Yes' if self.flip else 'No'),
        "Create an Inset or Outset")


def register():
    bpy.utils.register_class(ND_OT_edge_length)


def unregister():
    bpy.utils.unregister_class(ND_OT_edge_length)
    unregister_draw_handler()
