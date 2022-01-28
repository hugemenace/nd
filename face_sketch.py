import bpy
import bmesh
from math import radians
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_hint, draw_property
from . utils import averaged_vector, set_3d_cursor, create_rotation_matrix_from_face


class ND_OT_face_sketch(bpy.types.Operator):
    bl_idname = "nd.face_sketch"
    bl_label = "Face Sketch"
    bl_description = "Orientate the view to a face, and optionally lift a copy of the face as a new starting sketch"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        self.key_alt = event.alt

        if event.type == 'P' and event.value == 'PRESS':
            self.pin_overlay = not self.pin_overlay

        elif event.type == 'WHEELUPMOUSE':
            if event.alt:
                self.face_operation_mode = (self.face_operation_mode + 1) % 2
            
        elif event.type == 'WHEELDOWNMOUSE':
            if event.alt:
                self.face_operation_mode = (self.face_operation_mode - 1) % 2

        elif event.type == 'LEFTMOUSE':
            return {'PASS_THROUGH'}
        
        elif event.type == 'SPACE':
            self.finish(context)

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.clean_up(context)

            return {'CANCELLED'}
        
        elif event.type == 'MIDDLEMOUSE' or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF'):
            return {'PASS_THROUGH'}

        update_overlay(self, context, event, pinned=self.pin_overlay, x_offset=320, lines=2)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.face_operation_mode = 0 # Sketch Only (0), Extract & Sketch (1)

        self.key_alt = False

        self.prepare_face_selection_mode(context)

        self.pin_overlay = False
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

        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'FACE'})

        context.object.name = 'ND — Face Extract'
        context.object.data.name = 'ND — Face Extract'

    
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
        bpy.ops.transform.create_orientation(name="ND — Sketch Surface", use=True)


    def prepare_face_sketch(self, context):
        bpy.ops.view3d.view_axis(type='TOP', align_active=True)
        self.set_face_transform_orientation()
        self.set_3d_cursor_to_face(context)


    def isolate_face(self, context):
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')


    def finish(self, context):
        self.isolate_face(context)
        self.prepare_face_sketch(context)
        self.clean_up(context)

    
    def clean_up(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        context.object.show_in_front = False

        if self.face_operation_mode == 0:
            bpy.ops.object.delete()

        unregister_draw_handler(self)
    

def draw_text_callback(self):
    draw_header(self)

    draw_hint(self, "Select a single face...", "Press space to confirm")

    draw_property(
        self,
        "Face Mode: {0}".format(['Sketch Only', 'Extract & Sketch'][self.face_operation_mode]),
        "Alt (Sketch Only, Extract & Sketch)",
        active=(self.key_alt),
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_face_sketch.bl_idname, text=ND_OT_face_sketch.bl_label)


def register():
    bpy.utils.register_class(ND_OT_face_sketch)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_face_sketch)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler(self)


if __name__ == "__main__":
    register()
