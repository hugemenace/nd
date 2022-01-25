import bpy
import bmesh
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_hint
from . utils import averaged_vector, set_3d_cursor, create_rotation_matrix_from_face


class ND_OT_view_alignment(bpy.types.Operator):
    bl_idname = "nd.view_alignment"
    bl_label = "View Alignment"
    bl_description = "Orientates the view so it is looking directly at a face"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            update_overlay(self, context, event)

        elif event.type == 'LEFTMOUSE':
            return {'PASS_THROUGH'}
        
        elif event.type == 'SPACE':
            self.finish(context)

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.revert(context)

            return {'CANCELLED'}
        
        elif event.type == 'MIDDLEMOUSE' or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF'):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.prepare_face_selection_mode(context)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback, "nd_draw_view_alignment")

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

        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'FACE'})

    
    def set_3d_cursor_to_face(self, context):
        mesh = bmesh.from_edit_mesh(context.object.data)
        world_matrix = context.object.matrix_world

        selected_faces = [f for f in mesh.faces if f.select]

        center = averaged_vector([f.calc_center_median_weighted() for f in selected_faces])

        loc = world_matrix @ center

        face = mesh.faces.active if mesh.faces.active and mesh.faces.active in selected_faces else selected_faces[0]
        rot = create_rotation_matrix_from_face(world_matrix, face)

        set_3d_cursor(location=loc, rotation=rot.to_quaternion())


    def set_face_transform_orientation(self):
        bpy.ops.transform.create_orientation(name="ND — View Plane", use=True)


    def finish(self, context):
        bpy.ops.view3d.view_axis(type='TOP', align_active=True)
        self.set_face_transform_orientation()
        self.set_3d_cursor_to_face(context)
        self.revert(context)

    
    def revert(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.delete()
        unregister_draw_handler(self, "nd_draw_view_alignment")
    

def draw_text_callback(self):
    draw_header(self, "ND — View Plane")

    draw_hint(self, "Select a single face", "Press space to confirm")


def menu_func(self, context):
    self.layout.operator(
        ND_OT_view_alignment.bl_idname, 
        text=ND_OT_view_alignment.bl_label)


def register():
    bpy.utils.register_class(ND_OT_view_alignment)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_view_alignment)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler(self, "nd_draw_view_alignment")


if __name__ == "__main__":
    register()
