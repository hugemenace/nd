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
from . preferences import get_preferences


def is_util_object(obj):
    if obj.name not in bpy.context.view_layer.objects:
        return False

    return obj.type == 'EMPTY' or obj.display_type == 'WIRE'


def get_all_util_objects():
    return [obj for obj in bpy.context.scene.objects if is_util_object(obj)]


def get_util_objects_for(target_objs):
    util_objects = set()  # Use set to avoid duplicates
    processed_objects = set()  # Track processed objects to avoid infinite loops

    def process_object(obj):
        if obj in processed_objects:
            return
        processed_objects.add(obj)

        # 1. Check if this object itself is a util object
        if is_util_object(obj):
            util_objects.add(obj)

        # 2. Process all children recursively
        for child in obj.children:
            process_object(child)

        # 3. Check modifier references
        if hasattr(obj, 'modifiers'):
            for modifier in obj.modifiers:
                referenced_obj = get_modifier_object_reference(modifier)
                if referenced_obj and is_util_object(referenced_obj):
                    util_objects.add(referenced_obj)
                    # Recursively process the referenced object too
                    process_object(referenced_obj)

    def get_modifier_object_reference(modifier):
        # Common object reference properties across different modifiers
        object_properties = [
            'object',          # Boolean, Array, Mirror, etc.
            'target',          # Shrinkwrap, Surface Deform, etc.
            'mirror_object',   # Mirror modifier
            'offset_object',   # Array modifier
            'start_cap',       # Array modifier
            'end_cap',         # Array modifier
            'curve_object',    # Curve modifier
            'auxiliary_target' # Surface Deform
        ]

        for prop in object_properties:
            if hasattr(modifier, prop):
                obj_ref = getattr(modifier, prop)
                if obj_ref is not None:
                    return obj_ref

        return None

    # Process each target object
    for target_obj in target_objs:
        if target_obj is not None:
            process_object(target_obj)

    return list(util_objects)


def isolate_utils(target_objs):
    for obj in target_objs:
        obj.hide_set(False)


def hide_all_utils(hide):
    for obj in get_all_util_objects():
        obj.hide_set(hide)


def has_visible_utils():
    for obj in get_all_util_objects():
        if not obj.hide_get():
            return True
    return False
