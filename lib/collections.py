# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

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