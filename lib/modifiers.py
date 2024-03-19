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
import re
from math import radians
from .. lib.preferences import get_preferences


def new_modifier(object, mod_name, mod_type, rectify=True):
    mod = object.modifiers.new(mod_name, mod_type)

    mod.show_viewport = True
    mod.show_in_editmode = True
    mod.show_expanded = False

    show_cage_mods = ['DISPLACE']
    if mod_type in show_cage_mods:
        mod.show_on_cage = True

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

    if bpy.app.version < (4, 0, 0):
        bpy.ops.object.modifier_move_to_index({'object': object}, modifier=mod_name, index=matching_mod_index)
    else:
        with bpy.context.temp_override(object=object):
            bpy.ops.object.modifier_move_to_index(modifier=mod_name, index=matching_mod_index)


def add_smooth_by_angle(object):
    if bpy.app.version < (4, 1, 0):
        return

    for mod in object.modifiers:
        if mod.name == "Smooth — ND SBA":
            return mod

    with bpy.context.temp_override(object=object):
        bpy.ops.object.shade_smooth()
        bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")
        
        mod = object.modifiers[-1]

        mod.name = "Smooth — ND SBA"
        mod["Input_1"] = radians(float(get_preferences().default_smoothing_angle))
        mod["Socket_1"] = True

        object.data.update()

        return mod


def set_smoothing_angle(object, mod, angle, ignore_sharpness=False):
    mod["Input_1"] = angle
    mod["Socket_1"] = ignore_sharpness

    object.data.update()


def rectify_smooth_by_angle(object):
    if bpy.app.version < (4, 1, 0):
        return

    mods = list(object.modifiers)
    smoothing_mods = ['Smooth — ND SBA']
    smoothing_mods = [mod for mod in mods if mod.name in smoothing_mods]

    for index, mod in enumerate(smoothing_mods):
        if bpy.app.version < (4, 0, 0):
            bpy.ops.object.modifier_move_to_index({'object': object}, modifier=mod.name, index=len(mods) - 1)
        else:
            with bpy.context.temp_override(object=object):
                bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=len(mods) - 1)


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


def remove_modifiers_ending_with(objects, suffix, strict=False):
    for object in objects:
        mods = object.modifiers
        mod_names = [mod.name for mod in mods]
        for mod_name in mod_names:
            base_name = re.sub(r"(.+?)(\.[0-9]{3})$", r"\1", mod_name) if not strict else mod_name
            if base_name.endswith(suffix):
                if bpy.app.version < (4, 0, 0):
                    bpy.ops.object.modifier_remove({'object': object}, modifier=mod_name)
                else:
                    with bpy.context.temp_override(object=object):
                        bpy.ops.object.modifier_remove(modifier=mod_name)


def remove_modifiers_starting_with(objects, suffix):
    for object in objects:
        mods = object.modifiers
        mod_names = [mod.name for mod in mods]
        for mod_name in mod_names:
            base_name = re.sub(r"(.+?)(\.[0-9]{3})$", r"\1", mod_name)
            if base_name.startswith(suffix):
                if bpy.app.version < (4, 0, 0):
                    bpy.ops.object.modifier_remove({'object': object}, modifier=mod_name)
                else:
                    with bpy.context.temp_override(object=object):
                        bpy.ops.object.modifier_remove(modifier=mod_name)