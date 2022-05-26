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


class ND_OT_weld(bpy.types.Operator):
    bl_idname = "nd.weld"
    bl_label = "Weld"
    bl_description = "Add a weld modifier to the selected objects"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) > 0:
            return all(obj.type == 'MESH' for obj in context.selected_objects)


    def invoke(self, context, event):
        for obj in context.selected_objects:
            modifier = obj.modifiers.new('Weld — ND', 'WELD')
            modifier.merge_threshold = 0.001

        return {'FINISHED'}

    
def register():
    bpy.utils.register_class(ND_OT_weld)


def unregister():
    bpy.utils.unregister_class(ND_OT_weld)
