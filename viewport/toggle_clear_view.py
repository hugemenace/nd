import bpy
from .. lib.preferences import get_preferences


class ND_OT_toggle_clear_view(bpy.types.Operator):
    bl_idname = "nd.toggle_clear_view"
    bl_label = "Clear View"
    bl_description = "Toggle clear view mode"


    def execute(self, context):
        enabled = bpy.context.space_data.overlay.show_cursor

        bpy.context.space_data.overlay.show_floor = not enabled
        bpy.context.space_data.overlay.show_object_origins = not enabled
        bpy.context.space_data.overlay.show_cursor = not enabled
        bpy.context.space_data.overlay.show_axis_x = not enabled
        bpy.context.space_data.overlay.show_axis_y = not enabled
        bpy.context.space_data.overlay.show_relationship_lines = not enabled
        bpy.context.space_data.overlay.show_extras = not enabled
        bpy.context.space_data.overlay.show_bones = not enabled
        bpy.context.space_data.overlay.show_motion_paths = not enabled

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ND_OT_toggle_clear_view.bl_idname, text=ND_OT_toggle_clear_view.bl_label)


def register():
    bpy.utils.register_class(ND_OT_toggle_clear_view)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_toggle_clear_view)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
