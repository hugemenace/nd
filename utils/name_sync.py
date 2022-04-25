# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy


class ND_OT_name_sync(bpy.types.Operator):
    bl_idname = "nd.name_sync"
    bl_label = "Name & Data Sync"
    bl_description = "Updates all data names to match their corresponding object names"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) >= 1 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        for obj in context.selected_objects:
            obj.data.name = obj.name

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ND_OT_name_sync.bl_idname, text=ND_OT_name_sync.bl_label)


def register():
    bpy.utils.register_class(ND_OT_name_sync)


def unregister():
    bpy.utils.unregister_class(ND_OT_name_sync)
