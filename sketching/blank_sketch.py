import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_hint
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor
from .. lib.events import capture_modifier_keys


class ND_OT_blank_sketch(bpy.types.Operator):
    bl_idname = "nd.blank_sketch"
    bl_label = "Blank Sketch"
    bl_description = "Helps with vertex-extrude based sketching"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        elif self.key_toggle_pin_overlay:
            toggle_pin_overlay(self)

        elif self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        elif self.operator_passthrough:
            self.update_overlay_wrapper(context, event)
            
            return {'PASS_THROUGH'}

        elif self.key_confirm_alternative:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        self.update_overlay_wrapper(context, event)

        return {'RUNNING_MODAL'}


    def update_overlay_wrapper(self, context, event):
        update_overlay(self, context, event, x_offset=280, lines=1)


    def invoke(self, context, event):
        add_single_vertex_object(self, context, "Sketch")
        align_object_to_3d_cursor(self, context)

        self.start_sketch_editing(context)

        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 0


    def start_sketch_editing(self, context):
        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'VERT'})
        bpy.ops.mesh.select_all(action='SELECT')


    def finish(self, context):
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.001)
        bpy.ops.mesh.edge_face_add()

        unregister_draw_handler()


    def revert(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)
        bpy.ops.object.delete()

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_hint(self, "Start sketching...", "Press space to confirm")


def menu_func(self, context):
    self.layout.operator(ND_OT_blank_sketch.bl_idname, text=ND_OT_blank_sketch.bl_label)


def register():
    bpy.utils.register_class(ND_OT_blank_sketch)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_blank_sketch)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
