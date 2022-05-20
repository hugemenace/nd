# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

bl_info = {
    "name": "HugeMenace — ND",
    "author": "HugeMenace",
    "version": (1, 27, 0),
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
        default=False,
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
        default=False,
    )

    overlay_pinned: BoolProperty(
        name="Overlay Pinned",
        default=False,
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
        column = box.column(align=True)
        row = column.row()
        row.prop(self, "utils_collection_name")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "use_fast_booleans")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "recon_poly_solidify")

        box2 = box.box()
        column = box2.column(align=True)
        row = column.row()
        row.label(text="Set a path for a custom screw heads .blend file")
        column = box2.column(align=True)
        row = column.row()
        row.prop(self, "custom_screw_heads_path")

        box3 = box.box()
        column = box3.column(align=True)
        row = column.row()
        row.label(text="Enable deprecated features for short term backwards compatibility", icon="ERROR")
        column = box3.column(align=True)
        row = column.row()
        row.prop(self, "enable_deprecated_features")

    
    def draw_ui(self, box):
        column = box.column(align=True)
        row = column.row()
        row.prop(self, "overlay_dpi")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "enable_mouse_values")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "mouse_value_scalar")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "enable_quick_favourites")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "lock_overlay_pinning")
        
        column = box.column(align=True)
        row = column.row()
        row.prop(self, "enable_axis_helper")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "axis_base_thickness")
        row.prop(self, "axis_active_thickness")
        row.prop(self, "axis_inactive_opacity")

    
    def draw_keymap(self, box):
        column = box.column(align=True)
        row = column.row()
        row.label(text="Overlay Keybinds")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "overlay_pin_key")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "overlay_pause_key")
        
        column = box.column(align=True)
        row = column.row()
        row.prop(self, "overlay_reset_key")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "overlay_increase_factor")

        column = box.column(align=True)
        row = column.row()
        row.prop(self, "overlay_decrease_factor")

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

    lib.preferences.get_preferences().update_available = lib.updates.update_available(bl_info['version'])


def unregister():
    for registerable in registerables:
        registerable.unregister()

    bpy.utils.unregister_class(NDPreferences)