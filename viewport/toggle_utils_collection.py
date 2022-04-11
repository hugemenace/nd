import bpy
from .. lib.preferences import get_preferences


class ND_OT_toggle_utils_collection(bpy.types.Operator):
    bl_idname = "nd.toggle_utils_collection"
    bl_label = "Utils Visibility"
    bl_description = "Toggle utils collection visibility"


    def execute(self, context):
        collection = bpy.data.collections.get(get_preferences().utils_collection_name)
        if collection is not None:
            collection.hide_viewport = not collection.hide_viewport
            for obj in collection.all_objects:
                obj.hide_set(collection.hide_viewport)
                obj.hide_viewport = collection.hide_viewport

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ND_OT_toggle_utils_collection.bl_idname, text=ND_OT_toggle_utils_collection.bl_label)


def register():
    bpy.utils.register_class(ND_OT_toggle_utils_collection)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_toggle_utils_collection)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
