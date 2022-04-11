import bpy
from . preferences import get_preferences

def has_utils_collection():
    for collection in bpy.data.collections:
        if collection.name == get_preferences().utils_collection_name:
            return (True, collection)
    
    return (False, None)
        

def create_utils_collection():
    collection = bpy.data.collections.new(get_preferences().utils_collection_name)
    bpy.context.scene.collection.children.link(collection)
    collection.color_tag = 'COLOR_02'
    collection.hide_render = True

    return collection


def move_to_utils_collection(obj):
    (has_utils, utils_collection) = has_utils_collection()
    if not has_utils:
        utils_collection = create_utils_collection()
    
    remove_obj_from_all_collections(obj)
    utils_collection.objects.link(obj)


def remove_obj_from_all_collections(obj):
    for collection in obj.users_collection[:]:
        collection.objects.unlink(obj)