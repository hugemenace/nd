# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy
from .. lib.collections import hide_utils_collection, get_utils_layer


class ND_OT_toggle_utils_collection(bpy.types.Operator):
    bl_idname = "nd.toggle_utils_collection"
    bl_label = "Utils Visibility"
    bl_description = "Toggle utils collection visibility"


    def execute(self, context):
        data = get_utils_layer()
        if data is not None:
            layer, collection = data
            hide_utils_collection(not layer.hide_viewport)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ND_OT_toggle_utils_collection.bl_idname, text=ND_OT_toggle_utils_collection.bl_label)


def register():
    bpy.utils.register_class(ND_OT_toggle_utils_collection)


def unregister():
    bpy.utils.unregister_class(ND_OT_toggle_utils_collection)
