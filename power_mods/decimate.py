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
from math import radians
from .. lib.modifiers import rectify_mod_order


class ND_OT_decimate(bpy.types.Operator):
    bl_idname = "nd.decimate"
    bl_label = "Decimate"
    bl_description = "Add a decimate modifier to the selected objects"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) > 0:
            return all(obj.type == 'MESH' for obj in context.selected_objects)


    def invoke(self, context, event):
        for obj in context.selected_objects:
            modifier = obj.modifiers.new('Decimate — ND', 'DECIMATE')
            modifier.decimate_type = 'DISSOLVE'
            modifier.angle_limit = radians(1)
            rectify_mod_order(obj, modifier.name)

        return {'FINISHED'}

    
def register():
    bpy.utils.register_class(ND_OT_decimate)


def unregister():
    bpy.utils.unregister_class(ND_OT_decimate)
