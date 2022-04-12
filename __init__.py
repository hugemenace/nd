bl_info = {
    "name": "HugeMenace — ND",
    "author": "HugeMenace",
    "version": (1, 18, 0),
    "blender": (3, 0, 0),
    "location": "N Panel, Shift + 2",
    "description": "Non-destructive operations, tools, and generators.",
    "warning": "",
    "doc_url": "https://hugemenace.co",
    "category": "3D View"
}


import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, IntProperty, StringProperty
from . import lib
from . import booleans
from . import interface
from . import sketching
from . import power_mods
from . import generators
from . import utils
from . import viewport


registerables = (
    booleans,
    interface,
    sketching,
    power_mods,
    generators,
    utils,
    viewport,
)


class NDPreferences(AddonPreferences):
    bl_idname = __name__
    
    update_available: BoolProperty(
        name="Update Available",
        default=False,
    )

    enable_quick_favourites: BoolProperty(
        name="Enable Quick Favourites",
        default=False,
    )

    utils_collection_name: StringProperty(
        name="Utils Collection Name",
        default="Utils",
    )

    overlay_dpi: IntProperty(
        name="Overlay DPI",
        default=72,
        min=1,
        max=300,
        step=1,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "overlay_dpi")
        layout.prop(self, "utils_collection_name")
        layout.prop(self, "enable_quick_favourites")


def register():
    lib.reload()

    for registerable in registerables:
        registerable.reload()
        registerable.register()

    bpy.utils.register_class(NDPreferences)

    lib.preferences.get_preferences().update_available = lib.updates.update_available(bl_info['version'])


def unregister():
    for registerable in registerables:
        registerable.unregister()

    bpy.utils.unregister_class(NDPreferences)