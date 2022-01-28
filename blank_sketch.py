import bpy
import bmesh
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_hint
from . utils import add_single_vertex_object, align_object_to_3d_cursor


class ND_OT_blank_sketch(bpy.types.Operator):
    bl_idname = "nd.blank_sketch"
    bl_label = "Blank Sketch"
    bl_description = "Helps with vertex-extrude based sketching"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        if event.type == 'P' and event.value == 'PRESS':
            self.pin_overlay = not self.pin_overlay

        elif event.type == 'SPACE':
            self.finish(context)

            return {'FINISHED'}

        elif event.shift and event.type == 'D' and event.value == 'PRESS':
            return {'PASS_THROUGH'}

        elif event.alt and event.type == 'Z' and event.value == 'PRESS':
            return {'PASS_THROUGH'}

        elif event.type in {'LEFTMOUSE', 'E', 'G', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.ctrl:
            return {'PASS_THROUGH'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.revert(context)

            return {'CANCELLED'}

        elif event.type == 'MIDDLEMOUSE' or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF'):
            return {'PASS_THROUGH'}

        update_overlay(self, context, event, pinned=self.pin_overlay, x_offset=280, lines=1)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        add_single_vertex_object(self, context, "Sketch")
        align_object_to_3d_cursor(self, context)

        self.start_sketch_editing(context)

        self.pin_overlay = False
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

        unregister_draw_handler(self)


    def revert(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)
        bpy.ops.object.delete()

        unregister_draw_handler(self)


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
    unregister_draw_handler(self)


if __name__ == "__main__":
    register()
