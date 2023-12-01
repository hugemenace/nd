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
        removal_count = 0

        active_util_object_names = set()
        all_scene_objects = [obj for obj in bpy.context.view_layer.objects if obj.type == 'MESH']
        util_mods = ['BOOLEAN', 'ARRAY', 'MIRROR', 'LATTICE']

        for obj in all_scene_objects:
            remove_mods = []
            for mod in obj.modifiers:
                if mod.type not in util_mods:
                    continue

                if mod.type == 'BOOLEAN':
                    if mod.show_viewport and mod.object:
                        active_util_object_names.add(mod.object.name)
                    else:
                        remove_mods.append(mod)
                        removal_count += 1
                    continue 

                if mod.type == 'ARRAY':
                    if mod.offset_object:
                        active_util_object_names.add(mod.offset_object.name)
                    continue

                if mod.type == 'LATTICE':
                    if mod.object:
                        active_util_object_names.add(mod.object.name)
                    continue

                if mod.type == 'MIRROR':
                    if mod.mirror_object:
                        active_util_object_names.add(mod.mirror_object.name)
                    continue

            for mod in remove_mods:
                obj.modifiers.remove(mod)
        
        all_util_objects = get_all_util_objects()
        deleted_objects = []

        for obj in all_util_objects:
            if obj and obj.name not in active_util_object_names:
                deleted_objects.append(obj)
                removal_count += 1
        
        if bpy.app.version < (4, 0, 0):
            bpy.ops.object.delete({'active_object': None, 'object': None, 'selected_objects': deleted_objects}, use_global=False)
        else:
            with bpy.context.temp_override(active_object=None, object=None, selected_objects=deleted_objects):
                bpy.ops.object.delete(use_global=False)

        return removal_count

    
def register():
    bpy.utils.register_class(ND_OT_clean_utils)


def unregister():
    bpy.utils.unregister_class(ND_OT_clean_utils)
