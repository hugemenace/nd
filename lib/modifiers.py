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


def new_modifier(object, mod_name, mod_type, rectify=True):
    mod = object.modifiers.new(mod_name, mod_type)

    mod.show_viewport = True
    mod.show_in_editmode = True
    mod.show_on_cage = True
    mod.show_expanded = False

    if rectify:
        rectify_mod_order(object, mod.name)

    return mod


def rectify_mod_order(object, mod_name):
    mods = list(object.modifiers)

    if len(mods) < 2:
        return

    matching_mod_index = None
    for index, mod in enumerate(mods):
        if "— ND WNB" in mod.name:
            matching_mod_index = index
            break

        if "Weld — ND SW" in mod.name:
            matching_mod_index = index
            break
        
        if "Weld — ND B" in mod.name:
            matching_mod_index = index
            break
        
        if "Decimate — ND SD" in mod.name:
            matching_mod_index = index
            break
        
        if mod.type == 'BEVEL' and mod.affect == 'EDGES' and mod.limit_method == 'ANGLE':
            if mod.segments > 1 or (mod.segments == 1 and mod.harden_normals):
                matching_mod_index = index
                break
        
    if matching_mod_index is None:
        return

    bpy.ops.object.modifier_move_to_index({'object': object}, modifier=mod_name, index=matching_mod_index)


def remove_problematic_bevels(object):
    mods = [mod for mod in object.modifiers]
    remove_mods = []

    for mod in mods:
        if "— ND WNB" in mod.name:
            remove_mods.append(mod)
            continue
        elif mod.type == 'BEVEL' and mod.affect == 'EDGES' and mod.limit_method == 'ANGLE':
            if mod.segments > 1 or (mod.segments == 1 and mod.harden_normals):
                remove_mods.append(mod)
                continue

    for mod in remove_mods:
        object.modifiers.remove(mod)
