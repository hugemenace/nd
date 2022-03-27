import bpy


def get_registered_addon_name():
    return __name__.partition('.')[0]


def get_preferences():
    return bpy.context.preferences.addons[get_registered_addon_name()].preferences