# ███╗   ██╗██████╗
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝
#
# ND (Non-Destructive) Blender Add-on
# Copyright (C) 2024 Tristan S. & Ian J. (HugeMenace)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
        if "Weighted Normal — ND WN" in mod.name:
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


def get_sba_mod(object):
    for mod in object.modifiers:
        if mod.type == 'NODES' and (mod.name.startswith("Smooth — ND SBA") or mod.name.startswith("Smooth by Angle")):
            return mod

    return None


def has_sba_mod(object):
    return get_sba_mod(object) != None


def add_smooth_by_angle(object):
    if bpy.app.version < (4, 1, 0):
        return

    if has_sba_mod(object):
        return

    with bpy.context.temp_override(object=object):
        sba_node_group = bpy.data.node_groups.get("Smooth by Angle")

        if sba_node_group == None and bpy.app.version == (4, 1, 0):
            bpy.ops.object.shade_smooth()
            bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="",
                    relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")

        if sba_node_group == None and bpy.app.version > (4, 1, 0):
            bpy.ops.object.shade_auto_smooth()

        sba_mod = None

        if sba_node_group != None:
            sba_mod = object.modifiers.new("Smooth — ND SBA", 'NODES')
            sba_mod.node_group = sba_node_group
            if bpy.app.version > (4, 1, 0):
                sba_mod.show_group_selector = False
                sba_mod.use_pin_to_last = True

        # It isn't pretty, but it's the only way to get the modifier in modifier_add_node_group/shade_auto_smooth
        # runs asynchronously which doesn't guarantee the modifier is ready before the next chunk of code.
        count = 0
        while sba_mod is None and count < 25:
            sba_mod = get_sba_mod(object)
            if sba_mod != None:
                break
            object.data.update()
            count += 1

        # If the modifier is still None, give up.
        if sba_mod == None:
            return

        sba_mod.name = "Smooth — ND SBA"

        set_smoothing_angle(object, radians(float(get_preferences().default_smoothing_angle)), True)

        # If the object has a WN modifier, place the smoothig mod before it.
        for index, mod in enumerate(object.modifiers):
            if mod.name == "Weighted Normal — ND WN":
                bpy.ops.object.modifier_move_to_index(modifier=sba_mod.name, index=index-1)
                break


def set_smoothing_angle(object, angle, ignore_sharpness=False):
    mod = get_sba_mod(object)

    if mod is None:
        return

    mod["Input_1"] = angle
    mod["Socket_1"] = ignore_sharpness

    object.data.update()


def rectify_smooth_by_angle(object, force=False):
    # For Blender 4.1.0 and above, the smoothing and weighted normal
    # modifiers are pinned at the end of the stack by ND.
    if force == False and bpy.app.version > (4, 1, 0):
        return

    mod_order = ['Smooth by Angle', 'Smooth — ND SBA', 'Weighted Normal — ND WN']
    object_mods = [mod.name for mod in list(object.modifiers)]

    for mod_name in mod_order:
        if not(mod_name in object_mods):
            continue

        if bpy.app.version < (4, 0, 0):
            bpy.ops.object.modifier_move_to_index({'object': object}, modifier=mod_name, index=len(object_mods) - 1)
        else:
            with bpy.context.temp_override(object=object):
                bpy.ops.object.modifier_move_to_index(modifier=mod_name, index=len(object_mods) - 1)


def remove_problematic_boolean_mods(object):
    mods = [mod for mod in object.modifiers]
    remove_mods = []

    for mod in mods:
        if mod.name == "Weighted Normal — ND WN":
            remove_mods.append(mod)
            continue

        if mod.type == 'BEVEL' and mod.affect == 'EDGES' and mod.limit_method == 'ANGLE':
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
