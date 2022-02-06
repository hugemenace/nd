import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_hint, draw_property
from .. lib.viewport import set_3d_cursor
from .. lib.events import capture_modifier_keys


class ND_OT_geo_lift(bpy.types.Operator):
    bl_idname = "nd.geo_lift"
    bl_label = "Geo Lift"
    bl_description = "Lift geometry out of a non-destructive object"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        elif self.key_toggle_pin_overlay:
            toggle_pin_overlay(self)

        elif self.key_cancel:
            self.clean_up(context)

            return {'CANCELLED'}

        elif self.operator_passthrough:
            self.update_overlay_wrapper(context, event)
            
            return {'PASS_THROUGH'}

        elif self.key_confirm:
            return {'PASS_THROUGH'}
        
        elif self.key_confirm_alternative:
            return self.finish(context)

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        self.update_overlay_wrapper(context, event)

        return {'RUNNING_MODAL'}

    
    def update_overlay_wrapper(self, context, event):
        update_overlay(self, context, event, x_offset=320, lines=1)


    def invoke(self, context, event):
        self.prepare_face_selection_mode(context)

        capture_modifier_keys(self)
        
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1


    def prepare_face_selection_mode(self, context):
        bpy.ops.object.duplicate()

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.object.evaluated_get(depsgraph)

        context.object.modifiers.clear()
        context.object.show_in_front = True

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        bm.to_mesh(context.object.data)
        bm.free()

        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'VERT', 'EDGE', 'FACE'})

        context.object.name = 'ND — Geo Lift'
        context.object.data.name = 'ND — Geo Lift'

    
    def isolate_geometry(self, context):
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.customdata_custom_splitnormals_clear()


    def finish(self, context):
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


def menu_func(self, context):
    self.layout.operator(ND_OT_geo_lift.bl_idname, text=ND_OT_geo_lift.bl_label)


def register():
    bpy.utils.register_class(ND_OT_geo_lift)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_geo_lift)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
