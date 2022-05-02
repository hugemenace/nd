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
from .. lib.viewport import set_3d_cursor
from .. lib.events import capture_modifier_keys


class ND_OT_geo_lift(bpy.types.Operator):
    bl_idname = "nd.geo_lift"
    bl_label = "Geo Lift"
    bl_description = """Lift geometry out of a non-destructive object
SHIFT — Ignore bevels when calculating selectable geometry"""
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

        elif self.key_confirm:
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

        elif self.key_confirm_alternative:
            return self.finish(context)

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.selection_type = 2 # ['VERT', 'EDGE', 'FACE']
        self.register_mode()
        
        self.ignore_bevels = event.shift

        self.prepare_face_selection_mode(context)

        capture_modifier_keys(self)
        
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.object.type == 'MESH'


    def register_mode(self):
        self.mode = ['VERT', 'EDGE', 'FACE'][self.selection_type]


    def set_selection_mode(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode = (self.selection_type == 0, self.selection_type == 1, self.selection_type == 2)
        self.register_mode()


    def prepare_face_selection_mode(self, context):
        bpy.ops.object.duplicate()

        if self.ignore_bevels:
            mods = [mod.name for mod in context.object.modifiers if mod.type == 'BEVEL' and mod.affect == 'EDGES']
            for mod in mods:
                bpy.ops.object.modifier_remove(modifier=mod)

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.object.evaluated_get(depsgraph)

        context.object.modifiers.clear()
        context.object.show_in_front = True

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        bm.to_mesh(context.object.data)
        bm.free()

        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={self.mode})
        bpy.ops.mesh.select_all(action='DESELECT')

        context.object.name = 'ND — Geo Lift'
        context.object.data.name = 'ND — Geo Lift'

    
    def isolate_geometry(self, context):
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type=self.mode)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.customdata_custom_splitnormals_clear()


    def has_invalid_selection(self, context):
        mesh = bmesh.from_edit_mesh(context.object.data)

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

        context.object.show_in_front = False

        if remove_lifted_geometry:
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
    self.layout.operator(ND_OT_geo_lift.bl_idname, text=ND_OT_geo_lift.bl_label)


def register():
    bpy.utils.register_class(ND_OT_geo_lift)


def unregister():
    bpy.utils.unregister_class(ND_OT_geo_lift)
    unregister_draw_handler()
