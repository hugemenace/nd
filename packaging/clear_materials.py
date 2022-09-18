# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)
# 
# ---
# Contributors: Tristo (HM)
# ---

import bpy


class ND_OT_clear_materials(bpy.types.Operator):
    bl_idname = "nd.clear_materials"
    bl_label = "Clear All Materials"
    bl_description = "Remove the material slots from all selected objects"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) >= 1 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        for object in context.selected_objects:
            object.data.materials.clear()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_clear_materials)


def unregister():
    bpy.utils.unregister_class(ND_OT_clear_materials)
