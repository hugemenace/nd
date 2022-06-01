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
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_hint, draw_property, draw_hint
from .. lib.viewport import set_3d_cursor
from .. lib.events import capture_modifier_keys, pressed
from .. lib.objects import create_duplicate_liftable_geometry


class ND_OT_geo_lift(bpy.types.Operator):
    bl_idname = "nd.geo_lift"
    bl_label = "Geo Lift"
    bl_description = """Lift geometry out of a non-destructive object
SHIFT — Do not clean duplicate mesh before extraction"""
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

        elif self.key_confirm_alternative:
            return self.finish(context)

        elif self.key_left_click:
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

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.selection_type = 2 # ['VERT', 'EDGE', 'FACE']
        self.register_mode()
        
        self.target_obj = context.active_object

        create_duplicate_liftable_geometry(context, {self.mode}, 'ND — Geo Lift', not event.shift)

        capture_modifier_keys(self)
        
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'


    def register_mode(self):
        self.mode = ['VERT', 'EDGE', 'FACE'][self.selection_type]


    def set_selection_mode(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode = (self.selection_type == 0, self.selection_type == 1, self.selection_type == 2)
        self.register_mode()


    def isolate_geometry(self, context):
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type=self.mode)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.customdata_custom_splitnormals_clear()


    def has_invalid_selection(self, context):
        mesh = bmesh.from_edit_mesh(context.active_object.data)

        selected_vertices = len([v for v in mesh.verts if v.select])
        selected_edges = len([e for e in mesh.edges if e.select])
        selected_faces = len([f for f in mesh.faces if f.select])

        if self.selection_type == 0:
            return selected_vertices < 1
        elif self.selection_type == 1:
            return selected_edges < 1
        elif self.selection_type == 2:
            return selected_faces < 1

        return False


    def finish(self, context):
        if self.has_invalid_selection(context):
            self.clean_up(context)
            self.report({'ERROR_INVALID_INPUT'}, "Ensure at least a single peice of geometry is selected.")

            return {'CANCELLED'}

        self.isolate_geometry(context)
        self.clean_up(context, remove_lifted_geometry=False)

        return {'FINISHED'}

    
    def clean_up(self, context, remove_lifted_geometry=True):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        context.active_object.show_in_front = False

        if remove_lifted_geometry:
            bpy.ops.object.delete()
            bpy.ops.object.select_all(action='DESELECT')
            self.target_obj.select_set(True)
            bpy.context.view_layer.objects.active = self.target_obj

        unregister_draw_handler()
    

def draw_text_callback(self):
    draw_header(self)

    draw_hint(self, "Confirm Geometry [Space]", "Comfirm the geometry to extract")

    draw_hint(
        self,
        "Selection Type [S,1,2,3]: {0}".format(['Vertex', 'Edge', 'Face'][self.selection_type]),
        "Type of geometry to select (Vertex, Edge, Face)")


def register():
    bpy.utils.register_class(ND_OT_geo_lift)


def unregister():
    bpy.utils.unregister_class(ND_OT_geo_lift)
    unregister_draw_handler()
