import os
import bpy.utils.previews


icons_collection = None
icons_directory = os.path.dirname(__file__)


def get_icon_value(name):
    return get_icon(name).icon_id


def get_icon(name):
    if name in icons_collection:
        return icons_collection[name]

    return icons_collection.load(name, os.path.join(icons_directory, name + ".png"), "IMAGE")


def reload():
    pass


def register():
    global icons_collection
    icons_collection = bpy.utils.previews.new()


def unregister():
    bpy.utils.previews.remove(icons_collection)