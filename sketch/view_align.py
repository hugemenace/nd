# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)
# 
# ---
# Contributors: Tristo (HM)
# ---

import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_hint, draw_property
from .. lib.math import v3_average, create_rotation_matrix_from_vertex, create_rotation_matrix_from_edge, create_rotation_matrix_from_face, v3_center
from .. lib.viewport import set_3d_cursor
from .. lib.events import capture_modifier_keys, pressed
from .. lib.objects import create_duplicate_liftable_geometry


class ND_OT_view_align(bpy.types.Operator):
    bl_idname = "nd.view_align"
    bl_label = "View Align"
    bl_description = """Orientate the view to the selected geometry
SHIFT — Do not clean duplicate mesh before extraction
ALT — Skip geometry selection and use the active object"""
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        elif self.key_toggle_pin_overlay:
            toggle_pin_overlay(self, event)

        elif self.operator_passthrough:
            update_overlay(self, context, event)

            return {'PASS_THROUGH'}

        elif self.key_cancel:
            self.clean_up(context)

            return {'CANCELLED'}

        elif pressed(event, {'S'}):
            self.selection_type = (self.selection_type + 1) % 3
            self.set_selection_mode(context)

        elif self.key_one:
            self.selection_type = 0
            self.set_selection_mode(context)

        elif self.key_two:
            self.selection_type = 1
            self.set_selection_mode(context)

        elif self.key_three:
            self.selection_type = 2
            self.set_selection_mode(context)

        elif self.key_confirm_alternative:
            return self.finish(context)

        elif self.key_left_click:
            return {'PASS_THROUGH'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.selection_type = 2 # ['VERT', 'EDGE', 'FACE']

        self.skip_geo_select = event.alt
        if self.skip_geo_select:
            bpy.ops.object.mode_set(mode='EDIT')
            context.tool_settings.mesh_select_mode = (True, False, False)
            bpy.ops.mesh.select_all(action='SELECT')

            self.determine_selection_type(context)
            context.tool_settings.mesh_select_mode = (self.selection_type == 0, self.selection_type == 1, self.selection_type == 2)

            return self.finish(context)
        
        create_duplicate_liftable_geometry(context, {'FACE'}, 'ND — View Align', not event.shift)

        capture_modifier_keys(self)
        
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
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

    
    def clean_up(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        if not self.skip_geo_select:
            context.active_object.show_in_front = False
            bpy.ops.object.delete()

        unregister_draw_handler()
    

def draw_text_callback(self):
    draw_header(self)

    draw_hint(self, "Confirm Geometry [Space]", "Comfirm the geometry to extract")

    draw_hint(
        self,
        "Selection Type [S,1,2,3]: {0}".format(['Vertex', 'Edge', 'Face'][self.selection_type]),
        "Type of geometry to select (Vertex, Edge, Face)")


def register():
    bpy.utils.register_class(ND_OT_view_align)


def unregister():
    bpy.utils.unregister_class(ND_OT_view_align)
    unregister_draw_handler()
