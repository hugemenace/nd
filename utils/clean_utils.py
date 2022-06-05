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
from .. lib.collections import get_all_util_objects


class ND_OT_clean_utils(bpy.types.Operator):
    bl_idname = "nd.clean_utils"
    bl_label = "Clean Utils"
    bl_description = "Removes unused boolean modifiers and utility objects"


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def invoke(self, context, event):
        while self.remove_utils() > 0:
            continue

        return {'FINISHED'}


    def remove_utils(self):
        removed_object_count = 0

        active_util_object_names = set()
        all_scene_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        all_util_objects = get_all_util_objects()

        for obj in all_scene_objects:
            mods = list(obj.modifiers)
            for mod in mods:
                if mod.type != 'BOOLEAN':
                    continue
                if mod.object:
                    active_util_object_names.add(mod.object.name)
                    continue
                obj.modifiers.remove(mod)
        
        for obj in all_util_objects:
            if obj.name not in active_util_object_names:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed_object_count += 1

        return removed_object_count

    
def register():
    bpy.utils.register_class(ND_OT_clean_utils)


def unregister():
    bpy.utils.unregister_class(ND_OT_clean_utils)
