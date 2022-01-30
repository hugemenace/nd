import bpy


class ND_OT_name_sync(bpy.types.Operator):
    bl_idname = "nd.name_sync"
    bl_label = "Name & Data Sync"
    bl_description = "Updates all data names to match their corresponding object names"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) >= 1


    def execute(self, context):
        for obj in context.selected_objects:
            obj.data.name = obj.name

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ND_OT_name_sync.bl_idname, text=ND_OT_name_sync.bl_label)


def register():
    bpy.utils.register_class(ND_OT_name_sync)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_name_sync)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
