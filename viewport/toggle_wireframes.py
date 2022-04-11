import bpy


class ND_OT_toggle_wireframes(bpy.types.Operator):
    bl_idname = "nd.toggle_wireframes"
    bl_label = "Wireframes"
    bl_description = "Toggle wireframe visibility"


    def execute(self, context):
        bpy.context.space_data.overlay.show_wireframes = not bpy.context.space_data.overlay.show_wireframes

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ND_OT_toggle_wireframes.bl_idname, text=ND_OT_toggle_wireframes.bl_label)


def register():
    bpy.utils.register_class(ND_OT_toggle_wireframes)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_toggle_wireframes)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
