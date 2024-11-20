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


def create_utils_collection():
    collection = bpy.data.collections.new(get_preferences().utils_collection_name)
    bpy.context.scene.collection.children.link(collection)
    collection.color_tag = get_preferences().utils_collection_color
    collection.hide_render = True

    return collection


def move_to_utils_collection(obj):
    collection = bpy.data.collections.get(get_preferences().utils_collection_name)
    if collection is None:
        collection = create_utils_collection()

    remove_obj_from_all_collections(obj)
    collection.objects.link(obj)


def remove_obj_from_all_collections(obj):
    for collection in obj.users_collection[:]:
        collection.objects.unlink(obj)


def get_utils_layer():
    layers = bpy.context.view_layer.layer_collection
    for layer in layers.children:
        if layer.name == get_preferences().utils_collection_name:
            return (layer, layer.collection)

    return None


def get_all_util_objects():
    data = get_utils_layer()

    if data is None:
        return []

    layer, collection = data
    return collection.all_objects


def hide_utils_collection(hide):
    data = get_utils_layer()
    if data is not None:
        layer, collection = data

        layer.hide_viewport = False
        collection.hide_viewport = False

        should_hide_viewport = get_preferences().disable_utils_in_viewport

        obj_names = [obj.name for obj in collection.all_objects]
        for obj_name in obj_names:
            obj = bpy.data.objects[obj_name]
            obj.hide_set(hide)
            obj.hide_viewport = should_hide_viewport and hide


def has_visible_utils():
    data = get_utils_layer()
    if data is not None:
        layer, collection = data

        obj_names = [obj.name for obj in collection.all_objects]
        for obj_name in obj_names:
            obj = bpy.data.objects[obj_name]
            if not obj.hide_get() and not obj.hide_viewport:
                return True

    return False


def isolate_in_utils_collection(target_objs):
    data = get_utils_layer()
    if data is not None:
        layer, collection = data

        layer.hide_viewport = False
        collection.hide_viewport = False

        should_hide_viewport = get_preferences().disable_utils_in_viewport

        obj_names = [obj.name for obj in collection.all_objects]
        target_obj_names = [obj.name for obj in target_objs]

        for obj_name in obj_names:
            obj = bpy.data.objects[obj_name]
            obj.hide_set(obj.name not in target_obj_names)
            obj.hide_viewport = should_hide_viewport and hide


def show_utils(target_objs):
    data = get_utils_layer()
    if data is not None:
        layer, collection = data

        layer.hide_viewport = False
        collection.hide_viewport = False

        for obj in target_objs:
            obj.hide_set(False)
            obj.hide_viewport = False
