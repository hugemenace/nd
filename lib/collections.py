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
from . preferences import get_preferences


def create_utils_collection():
    collection = bpy.data.collections.new(get_preferences().utils_collection_name)
    bpy.context.scene.collection.children.link(collection)
    collection.color_tag = 'COLOR_02'
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


def hide_utils_collection(hide):
    data = get_utils_layer()
    if data is not None:
        layer, collection = data

        layer.hide_viewport = hide
        collection.hide_viewport = hide

        obj_names = [obj.name for obj in collection.all_objects]
        for obj_name in obj_names:
            obj = bpy.data.objects[obj_name]
            obj.hide_set(hide)
            obj.hide_viewport = hide


def isolate_in_utils_collection(target_objs):
    data = get_utils_layer()
    if data is not None:
        layer, collection = data
        
        layer.hide_viewport = False
        collection.hide_viewport = False

        obj_names = [obj.name for obj in collection.all_objects]
        target_obj_names = [obj.name for obj in target_objs]

        for obj_name in obj_names:
            obj = bpy.data.objects[obj_name]
            obj.hide_set(obj.name not in target_obj_names)
            obj.hide_viewport = obj.name not in target_obj_names
