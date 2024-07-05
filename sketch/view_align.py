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
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_hint, draw_property
from .. lib.math import v3_average, create_rotation_matrix_from_vertex, create_rotation_matrix_from_edge, create_rotation_matrix_from_face, v3_center
from .. lib.viewport import set_3d_cursor
from .. lib.preferences import get_preferences
from .. lib.events import capture_modifier_keys, pressed
from .. lib.objects import create_duplicate_liftable_geometry


class ND_OT_view_align(BaseOperator):
    bl_idname = "nd.view_align"
    bl_label = "View Align"
    bl_description = """Orientate the view to the selected geometry
SHIFT — Do not clean duplicate mesh before extraction"""
    bl_options = {'UNDO'}


    def do_modal(self, context, event):
        if pressed(event, {'S'}):
            self.selection_type = (self.selection_type + 1) % 3
            self.set_selection_mode(context)

        if pressed(event, {'E'}):
            self.xray_mode = not self.xray_mode
            self.dirty = True

        if self.key_one:
            self.selection_type = 0
            self.set_selection_mode(context)

        if self.key_two:
            self.selection_type = 1
            self.set_selection_mode(context)

        if self.key_three:
            self.selection_type = 2
            self.set_selection_mode(context)

        if self.key_confirm_alternative:
            return self.finish(context)

        if self.key_select:
            return {'PASS_THROUGH'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        self.dirty = False
        self.xray_mode = False
        self.selection_type = 2 # ['VERT', 'EDGE', 'FACE']

        self.active_object = context.active_object

        create_duplicate_liftable_geometry(context, {'FACE'}, 'ND — View Align', not event.shift)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and context.active_object is not None:
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'


    def set_selection_mode(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode = (self.selection_type == 0, self.selection_type == 1, self.selection_type == 2)


    def get_face_transform(self, mesh, world_matrix):
        selected_faces = [f for f in mesh.faces if f.select]
        center = v3_average([f.calc_center_median_weighted() for f in selected_faces])
        location = world_matrix @ center
        rotation = create_rotation_matrix_from_face(world_matrix, selected_faces[0])

        return (location, rotation)


    def get_edge_transform(self, mesh, world_matrix):
        selected_edges = [e for e in mesh.edges if e.select]
        center = v3_average([v3_center(*e.verts) for e in selected_edges])
        location = world_matrix @ center
        rotation = create_rotation_matrix_from_edge(world_matrix, selected_edges[0])

        return (location, rotation)


    def get_vertex_transform(self, mesh, world_matrix):
        selected_vertices = [v for v in mesh.verts if v.select]
        center = v3_average([v.co for v in selected_vertices])
        location = world_matrix @ center
        rotation = create_rotation_matrix_from_vertex(world_matrix, selected_vertices[0])

        return (location, rotation)


    def set_custom_transform_orientation(self):
        bpy.ops.transform.create_orientation(name="ND — Sketch Surface", use=True)


    def prepare_view_align(self, context):
        mesh = bmesh.from_edit_mesh(context.active_object.data)
        world_matrix = context.active_object.matrix_world

        if self.selection_type == 0:
            selected_vertices = len([v for v in mesh.verts if v.select])
            if selected_vertices == 3:
                bpy.ops.mesh.edge_face_add()
                context.tool_settings.mesh_select_mode = (False, False, True)
                self.selection_type = 2

        bpy.ops.view3d.view_axis(type='TOP', align_active=True)
        context.space_data.region_3d.view_perspective = 'ORTHO'

        self.set_custom_transform_orientation()

        if self.selection_type == 0:
            (location, rotation) = self.get_vertex_transform(mesh, world_matrix)
            set_3d_cursor(location, rotation.to_quaternion())
        elif self.selection_type == 1:
            (location, rotation) = self.get_edge_transform(mesh, world_matrix)
            set_3d_cursor(location, rotation.to_quaternion())
        elif self.selection_type == 2:
            (location, rotation) = self.get_face_transform(mesh, world_matrix)
            set_3d_cursor(location, rotation.to_quaternion())


    def has_invalid_selection(self, context):
        mesh = bmesh.from_edit_mesh(context.active_object.data)

        selected_vertices = len([v for v in mesh.verts if v.select])
        selected_edges = len([e for e in mesh.edges if e.select])
        selected_faces = len([f for f in mesh.faces if f.select])

        if self.selection_type == 0:
            return selected_vertices != 1 and selected_vertices != 3
        elif self.selection_type == 1:
            return selected_edges != 1
        elif self.selection_type == 2:
            return selected_faces != 1

        return False


    def determine_selection_type(self, context):
        self.selection_type = 0

        mesh = bmesh.from_edit_mesh(context.active_object.data)

        selected_vertices = len([v for v in mesh.verts if v.select])
        selected_edges = len([e for e in mesh.edges if e.select])
        selected_faces = len([f for f in mesh.faces if f.select])

        if selected_vertices >= 1 and selected_faces == 0 and selected_edges == 0:
            return

        if selected_edges >= 1 and selected_faces == 0:
            self.selection_type = 1

        if selected_faces >= 1:
            self.selection_type = 2


    def operate(self, context):
        context.active_object.show_in_front = self.xray_mode
        self.dirty = False


    def finish(self, context):
        if self.has_invalid_selection(context):
            self.clean_up(context)
            if self.selection_type == 0:
                self.report({'ERROR_INVALID_INPUT'}, "Ensure only a single vertex, or exactly 3 vertices are selected.")
            else:
                self.report({'ERROR_INVALID_INPUT'}, "Ensure only a single edge or face is selected.")

            return {'CANCELLED'}

        self.prepare_view_align(context)
        self.clean_up(context)

        return {'FINISHED'}


    def clean_up(self, context, revert=False):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        context.active_object.show_in_front = False
        bpy.ops.object.delete()

        if revert:
            context.view_layer.objects.active = self.active_object
            self.active_object.select_set(True)

        unregister_draw_handler()


    def revert(self, context):
        self.clean_up(context, True)


def draw_text_callback(self):
    draw_header(self)

    draw_hint(self, "Confirm Geometry [Space]", "Comfirm the geometry to extract")

    draw_hint(
        self,
        "Selection Type [S,1,2,3]: {0}".format(['Vertex', 'Edge', 'Face'][self.selection_type]),
        "Type of geometry to select (Vertex, Edge, Face)")

    draw_hint(
        self,
        "Exclusive View [E]: {0}".format("On" if self.xray_mode else "Off"),
        "Show the target object in front of all other objects")


def register():
    bpy.utils.register_class(ND_OT_view_align)


def unregister():
    bpy.utils.unregister_class(ND_OT_view_align)
    unregister_draw_handler()
