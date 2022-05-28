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

bl_info = {
    "name": "HugeMenace — ND",
    "author": "HugeMenace",
    "version": (1, 28, 4),
    "blender": (3, 0, 0),
    "location": "N Panel, Shift + 2",
    "description": "Non-destructive operations, tools, and generators.",
    "warning": "",
    "doc_url": "https://hugemenace.co",
    "category": "3D View"
}


import bpy
import rna_keymap_ui
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, IntProperty, StringProperty, EnumProperty, FloatProperty
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

    local_user_prefs_version: StringProperty(
        name="Local user preferences version",
        default="0.0.0",
    )

    update_available: BoolProperty(
        name="Update Available",
        default=False,
    )

    enable_quick_favourites: BoolProperty(
        name="Enable Quick Favourites",
        default=False,
    )

    enable_deprecated_features: BoolProperty(
        name="Compatibility Mode",
        default=False,
    )

    recon_poly_solidify: BoolProperty(
        name="Automatically run Solidify after Recon Poly",
        default=False,
    )

    enable_mouse_values: BoolProperty(
        name="Enable Mouse Values",
        default=True,
    )

    use_fast_booleans: BoolProperty(
        name="Use Fast Booleans",
        default=True,
    )

    enable_axis_helper: BoolProperty(
        name="Enable Axis Visualization",
        default=True,
    )

    lock_overlay_pinning: BoolProperty(
        name="Lock Overlay Pinning",
        default=True,
    )

    overlay_pinned: BoolProperty(
        name="Overlay Pinned",
        default=False,
    )

    enable_update_check: BoolProperty(
        name="Enable Update Check",
        default=True,
    )

    overlay_pin_x: IntProperty(
        name="Overlay Pin X Coordinate",
        default=0,
    )

    overlay_pin_y: IntProperty(
        name="Overlay Pin Y Coordinate",
        default=0,
    )

    axis_base_thickness: FloatProperty(
        name="Axis Base Thickness",
        default=2,
        min=0,
        max=100,
        step=1,
    )

    axis_active_thickness: FloatProperty(
        name="Axis Active Thickness",
        default=4,
        min=0,
        max=100,
        step=1,
    )

    axis_inactive_opacity: FloatProperty(
        name="Axis Inactive Opacity",
        default=0.2,
        min=0,
        max=1,
        step=0.1,
    )

    mouse_value_scalar: FloatProperty(
        name="Mouse Value Scalar",
        default=0.0025,
        min=0.0001,
        max=10,
        precision=4,
        step=0.01,
    )

    mouse_value_scalar: FloatProperty(
        name="Mouse Value Scalar",
        default=0.0025,
        min=0.0001,
        max=10,
        precision=4,
        step=0.01,
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

    tabs: EnumProperty(
        name="Tabs",
        items=[
            ("GENERAL", "General", ""),
            ("UI", "UI", ""),
            ("KEYMAP", "Keymap", ""),
        ],
        default="GENERAL",
    )

    default_smoothing_angle: EnumProperty(
        name="Default Smooting Angle",
        items=[
            ("30", "30°", ""),
            ("45", "45°", ""),
            ("60", "60°", ""),
        ],
        default="30",
    )

    overlay_pause_key: EnumProperty(
        name="Pause Key",
        items=lib.overlay_keys.overlay_keys_enum,
        default="BACK_SLASH",
    )

    overlay_pin_key: EnumProperty(
        name="Pin Key",
        items=lib.overlay_keys.overlay_keys_enum,
        default="P",
    )

    overlay_reset_key: EnumProperty(
        name="Reset Option Key",
        items=lib.overlay_keys.overlay_keys_enum,
        default="X",
    )

    overlay_increase_factor: EnumProperty(
        name="Increase Option Factor",
        items=lib.overlay_keys.overlay_keys_enum,
        default="RIGHT_BRACKET",
    )

    overlay_decrease_factor: EnumProperty(
        name="Decrease Option Factor",
        items=lib.overlay_keys.overlay_keys_enum,
        default="LEFT_BRACKET",
    )

    custom_screw_heads_path: StringProperty(
        name="Custom Screw Heads",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        row = column.row()
        row.prop(self, "tabs", expand=True)

        box = layout.box()

        if self.tabs == "GENERAL":
            self.draw_general(box)
        elif self.tabs == "UI":
            self.draw_ui(box)
        elif self.tabs == "KEYMAP":
            self.draw_keymap(box)


    def draw_general(self, box):
        general_prefs = [
            "utils_collection_name",
            "use_fast_booleans",
            "recon_poly_solidify"]

        for pref in general_prefs:
            column = box.column(align=True)
            row = column.row()
            row.prop(self, pref)

        general_boxed_prefs = [
            ["The default angle to use for bevel and smoothing operations", "default_smoothing_angle", True],
            ["Set a path for a custom screw heads .blend file", "custom_screw_heads_path", False],
            ["Automatically check if addon is up to date when Blender starts", "enable_update_check", False],
            ["Enable deprecated features for short term backwards compatibility", "enable_deprecated_features", False]]

        for label, prop, expanded in general_boxed_prefs:
            pref_box = box.box()
            column = pref_box.column(align=True)
            row = column.row()
            row.label(text=label)
            column = pref_box.column(align=True)
            row = column.row()
            row.prop(self, prop, expand=expanded)

    
    def draw_ui(self, box):
        ui_prefs = [
            ["overlay_dpi"],
            ["enable_mouse_values"],
            ["mouse_value_scalar"],
            ["enable_quick_favourites"],
            ["lock_overlay_pinning"],
            ["enable_axis_helper"],
            ["axis_base_thickness", "axis_active_thickness", "axis_inactive_opacity"]]

        for prefs in ui_prefs:
            column = box.column(align=True)
            row = column.row()
            for pref in prefs:
                row.prop(self, pref)


    def draw_keymap(self, box):
        overlay_prefs = [
            "overlay_pin_key",
            "overlay_pause_key",
            "overlay_reset_key",
            "overlay_increase_factor",
            "overlay_decrease_factor"]

        column = box.column(align=True)
        row = column.row()
        row.label(text="Overlay Keybinds")

        for pref in overlay_prefs:
            column = box.column(align=True)
            row = column.row()
            row.prop(self, pref)

        name = "ND v%s" % ('.'.join([str(v) for v in bl_info['version']]))
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        
        for keymap in ['3D View', 'Mesh', 'Object Mode']:
            km = kc.keymaps.get(keymap)

            column = box.column(align=True)
            row = column.row()
            row.label(text=keymap)

            for kmi in km.keymap_items:
                if kmi.idname == "wm.call_menu" and kmi.name.startswith(name):
                    column = box.column(align=True)
                    row = column.row()
                    rna_keymap_ui.draw_kmi(["ADDON", "USER", "DEFAULT"], kc, km, kmi, row, 0)


def register():
    lib.reload()

    for registerable in registerables:
        registerable.reload()
        registerable.register()

    bpy.utils.register_class(NDPreferences)

    version = '.'.join([str(v) for v in bl_info['version']])
    prefs = lib.preferences.get_preferences()

    if prefs.enable_update_check:
        prefs.update_available = lib.updates.update_available(bl_info['version'])
    else:
        prefs.update_available = False

    if prefs.local_user_prefs_version != version:
        if version.startswith("1.28"):
            prefs.overlay_pin_key = "P"
            prefs.overlay_pause_key = "BACK_SLASH"
            prefs.overlay_reset_key = "X"
            prefs.overlay_increase_factor = "RIGHT_BRACKET"
            prefs.overlay_decrease_factor = "LEFT_BRACKET"
            prefs.lock_overlay_pinning = True
            prefs.enable_mouse_values = True
            prefs.local_user_prefs_version = version

    print("""
███╗   ██╗██████╗ 
████╗  ██║██╔══██╗
██╔██╗ ██║██║  ██║
██║╚██╗██║██║  ██║
██║ ╚████║██████╔╝
╚═╝  ╚═══╝╚═════╝
HugeMenace — ND Addon v%s
    """ % (version));


def unregister():
    for registerable in registerables:
        registerable.unregister()

    bpy.utils.unregister_class(NDPreferences)