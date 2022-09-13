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
from .. lib.modifiers import new_modifier


class ND_OT_weighted_normal(bpy.types.Operator):
    bl_idname = "nd.wn"
    bl_label = "Weighted Normals"
    bl_description = "Add a weighted normal modifier to the selected objects"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) > 0:
            return all(obj.type == 'MESH' for obj in context.selected_objects)


    def invoke(self, context, event):
        for obj in context.selected_objects:
            new_modifier(obj, 'Weighted Normal — ND WN', 'WEIGHTED_NORMAL', rectify=False)

        return {'FINISHED'}

    
def register():
    bpy.utils.register_class(ND_OT_weighted_normal)


def unregister():
    bpy.utils.unregister_class(ND_OT_weighted_normal)
