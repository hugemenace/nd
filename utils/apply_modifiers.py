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
import bmesh


class ND_OT_apply_modifiers(bpy.types.Operator):
    bl_idname = "nd.apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = "Prepare the selected object(s) for destructive operations by applying applicable modifiers"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) > 0:
            return all([obj.type == 'MESH' for obj in context.selected_objects])


    def execute(self, context):
        for obj in context.selected_objects:
            self.collapse_modifiers(obj)

        return {'FINISHED'}


    def collapse_modifiers(self, obj):
        safe_mod_types = ['WEIGHTED_NORMAL', 'TRIANGULATE', 'NODES']

        mods = [(mod.name, mod.type, mod) for mod in obj.modifiers]
        for name, type, mod in mods:
            if type in safe_mod_types:
                continue

            if "— ND WNB" in name:
                continue

            if type == 'BEVEL' and mod.segments == 1 and mod.harden_normals:
                continue

            try:
                bpy.ops.object.modifier_apply({'object': obj}, modifier=name)
            except:
                # If the modifier is disabled, just remove it.
                bpy.ops.object.modifier_remove({'object': obj}, modifier=name)


def register():
    bpy.utils.register_class(ND_OT_apply_modifiers)


def unregister():
    bpy.utils.unregister_class(ND_OT_apply_modifiers)
