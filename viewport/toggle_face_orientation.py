import bpy


class ND_OT_toggle_face_orientation(bpy.types.Operator):
    bl_idname = "nd.toggle_face_orientation"
    bl_label = "Face Orientation"
    bl_description = "Toggle face orientation"


    def execute(self, context):
        bpy.context.space_data.overlay.show_face_orientation = not bpy.context.space_data.overlay.show_face_orientation

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ND_OT_toggle_face_orientation.bl_idname, text=ND_OT_toggle_face_orientation.bl_label)


def register():
    bpy.utils.register_class(ND_OT_toggle_face_orientation)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_toggle_face_orientation)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
