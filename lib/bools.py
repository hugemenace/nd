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


def move_bool_under_bevels(object, bool_name):
    mods = [mod for mod in object.modifiers]
    if len(mods) >= 3:
        second_last = len(mods) - 2
        third_last = len(mods) - 3
        if "— ND WNB" in mods[second_last].name and "— ND WNB" in mods[third_last].name:
            bpy.ops.object.modifier_move_up({'object': object}, modifier=bool_name)
            bpy.ops.object.modifier_move_up({'object': object}, modifier=bool_name)
        elif mods[second_last].type == 'BEVEL' and mods[second_last].segments == 1 and mods[second_last].harden_normals:
            bpy.ops.object.modifier_move_up({'object': object}, modifier=bool_name)
            bpy.ops.object.modifier_move_up({'object': object}, modifier=bool_name)
        elif mods[third_last].type == 'BEVEL' and mods[third_last].segments == 1 and mods[third_last].harden_normals:
            bpy.ops.object.modifier_move_up({'object': object}, modifier=bool_name)
            bpy.ops.object.modifier_move_up({'object': object}, modifier=bool_name)


def remove_problematic_bevels(object):
    mods = [mod for mod in object.modifiers]
    remove_mods = []

    for mod in mods:
        if mod.type == 'BEVEL' and mod.segments == 1 and mod.harden_normals:
            remove_mods.append(mod)
        elif "— ND WNB" in mod.name:
            remove_mods.append(mod)

    for mod in remove_mods:
        object.modifiers.remove(mod)
