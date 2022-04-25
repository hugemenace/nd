# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_hint, draw_property
from .. lib.math import v3_average, create_rotation_matrix_from_vertex, create_rotation_matrix_from_edge, create_rotation_matrix_from_face, v3_center
from .. lib.viewport import set_3d_cursor
from .. lib.events import capture_modifier_keys


class ND_OT_view_align(bpy.types.Operator):
    bl_idname = "nd.view_align"
    bl_label = "View Align"
    bl_description = "Orientate the view to the selected geometry"
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

        elif self.key_step_up:
            if self.key_alt:
                self.selection_type = (self.selection_type + 1) % 3
                self.set_selection_mode(context)
            
        elif self.key_step_down:
            if self.key_alt:
                self.selection_type = (self.selection_type - 1) % 3
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

        elif self.key_confirm:
            return {'PASS_THROUGH'}
        
        elif self.key_confirm_alternative:
            return self.finish(context)

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.selection_type = 2 # ['VERT', 'EDGE', 'FACE']
        self.prepare_evaluated_geometry(context)

        capture_modifier_keys(self)
        
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.object.type == 'MESH'


    def set_selection_mode(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode = (self.selection_type == 0, self.selection_type == 1, self.selection_type == 2)


    def prepare_evaluated_geometry(self, context):
        bpy.ops.object.duplicate()

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.object.evaluated_get(depsgraph)

        context.object.modifiers.clear()
        context.object.show_in_front = True

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        bm.to_mesh(context.object.data)
        bm.free()

        mode = ['VERT', 'EDGE', 'FACE'][self.selection_type]
        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={mode})
        bpy.ops.mesh.select_all(action='DESELECT')

        context.object.name = 'ND — View Align'
        context.object.data.name = 'ND — View Align'

    
    def set_3d_cursor_to_face(self, mesh, world_matrix):
        selected_faces = [f for f in mesh.faces if f.select]
        center = v3_average([f.calc_center_median_weighted() for f in selected_faces])
        location = world_matrix @ center
        rotation = create_rotation_matrix_from_face(world_matrix, selected_faces[0])

        return (location, rotation)


    def set_3d_cursor_to_edge(self, mesh, world_matrix):
        selected_edges = [e for e in mesh.edges if e.select]
        center = v3_average([v3_center(*e.verts) for e in selected_edges])
        location = world_matrix @ center
        rotation = create_rotation_matrix_from_edge(world_matrix, selected_edges[0])

        return (location, rotation)

    
    def set_3d_cursor_to_vertex(self, mesh, world_matrix):
        selected_vertices = [v for v in mesh.verts if v.select]
        center = v3_average([v.co for v in selected_vertices])
        location = world_matrix @ center
        rotation = create_rotation_matrix_from_vertex(world_matrix, selected_vertices[0])

        return (location, rotation)


    def set_custom_transform_orientation(self):
        bpy.ops.transform.create_orientation(name="ND — Sketch Surface", use=True)


    def prepare_view_align(self, context):
        mesh = bmesh.from_edit_mesh(context.object.data)
        world_matrix = context.object.matrix_world

        if self.selection_type == 0:
            selected_vertices = len([v for v in mesh.verts if v.select])
            if selected_vertices == 3:
                bpy.ops.mesh.edge_face_add()
                context.tool_settings.mesh_select_mode = (False, False, True)
                self.selection_type = 2

        bpy.ops.view3d.view_axis(type='TOP', align_active=True)
        
        self.set_custom_transform_orientation()

        if self.selection_type == 0:
            (location, rotation) = self.set_3d_cursor_to_vertex(mesh, world_matrix)
            set_3d_cursor(location, rotation.to_quaternion())
        elif self.selection_type == 1:
            (location, rotation) = self.set_3d_cursor_to_edge(mesh, world_matrix)
            set_3d_cursor(location, rotation.to_quaternion())
        elif self.selection_type == 2:
            (location, rotation) = self.set_3d_cursor_to_face(mesh, world_matrix)
            set_3d_cursor(location, rotation.to_quaternion())


    def has_invalid_selection(self, context):
        mesh = bmesh.from_edit_mesh(context.object.data)

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

        context.object.show_in_front = False

        bpy.ops.object.delete()

        unregister_draw_handler()
    

def draw_text_callback(self):
    draw_header(self)

    draw_hint(self, "Select geometry...", "Press space to confirm")

    draw_property(
        self,
        "Selection Type: {0}".format(['Vertex', 'Edge', 'Face'][self.selection_type]),
        "Alt / 1, 2, 3 (Vertex, Edge, Face)",
        active=self.key_alt,
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_view_align.bl_idname, text=ND_OT_view_align.bl_label)


def register():
    bpy.utils.register_class(ND_OT_view_align)


def unregister():
    bpy.utils.unregister_class(ND_OT_view_align)
    unregister_draw_handler()
