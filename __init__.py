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

bl_info = {
    "name": "HugeMenace — ND",
    "author": "HugeMenace",
    "version": (1, 43, 1),
    "blender": (4, 0, 0),
    "location": "N Panel, Shift + 2",
    "description": "Non-destructive operations, tools, and generators.",
    "warning": "",
    "doc_url": "https://docs.nd.hugemenace.co/",
    "category": "3D View"
}


import bpy
import rna_keymap_ui
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, IntProperty, StringProperty, EnumProperty, FloatProperty, FloatVectorProperty
from . import lib
from . import interface
from . import booleans
from . import bevels
from . import deform
from . import extrusion
from . import replicate
from . import simplify
from . import shading
from . import scene
from . import packaging
from . import sketch
from . import standalone
from . import utils
from . import viewport
from . import icons


registerables = (
    interface,
    booleans,
    bevels,
    deform,
    extrusion,
    replicate,
    simplify,
    shading,
    scene,
    packaging,
    sketch,
    standalone,
    utils,
    viewport,
    icons,
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

    enable_right_click_select: BoolProperty(
        name="Enable Right Click Select",
        default=False,
    )

    enable_deprecated_features: BoolProperty(
        name="Compatibility Mode",
        default=False,
    )

    enable_experimental_features: BoolProperty(
        name="Experimental Mode",
        default=False,
    )

    recon_poly_solidify: BoolProperty(
        name="Automatically run Solidify after Recon Poly",
        default=False,
    )

    recon_poly_inscribed: BoolProperty(
        name="Automatically set Recon Poly extents to Inscribed (vs. Circumscribed)",
        default=True,
    )

    enable_mouse_values: BoolProperty(
        name="Enable Mouse Values (move mouse to change values)",
        default=True,
    )

    extend_mouse_values: BoolProperty(
        name="Extend Mouse Values (scroll wheel override)",
        default=True,
    )

    use_fast_booleans: BoolProperty(
        name="Use Fast Booleans",
        default=True,
    )

    enable_sidebar: BoolProperty(
        name="Enable the sidebar / N-panel (requires Blender restart)",
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

    unit_increment_size: FloatProperty(
        name="Unit Increment Size",
        default=1,
        min=0.01,
        max=100,
        precision=2,
        step=0.1,
    )

    mouse_value_steps: IntProperty(
        name="Mouse Value Steps",
        default=100,
        min=1,
        step=1,
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

    overlay_header_standard_color: FloatVectorProperty(
        name="Overlay Header Standard Color",
        default=(255/255, 135/255, 55/255),
        subtype='COLOR_GAMMA',
        size=3,
    )

    overlay_header_recalled_color: FloatVectorProperty(
        name="Overlay Header Recalled Color",
        default=(82/255, 224/255, 82/255),
        subtype='COLOR_GAMMA',
        size=3,
    )

    overlay_header_paused_color: FloatVectorProperty(
        name="Overlay Header Paused Color",
        default=(238/255, 59/255, 43/2555),
        subtype='COLOR_GAMMA',
        size=3,
    )

    overlay_base_color: FloatVectorProperty(
        name="Overlay Base Color",
        default=(255/255, 255/255, 255/255),
        subtype='COLOR_GAMMA',
        size=3,
    )

    overlay_option_active_color: FloatVectorProperty(
        name="Overlay Option Active Color",
        default=(55/255, 174/255, 255/255),
        subtype='COLOR_GAMMA',
        size=3,
    )

    overlay_option_manual_override_color: FloatVectorProperty(
        name="Overlay Option Manual Override Color",
        default=(237/255, 185/255, 94/255),
        subtype='COLOR_GAMMA',
        size=3,
    )

    points_primary_color: FloatVectorProperty(
        name="Points Primary Color",
        default=(82/255, 224/255, 82/255, 1.0),
        subtype='COLOR_GAMMA',
        size=4,
    )

    points_secondary_color: FloatVectorProperty(
        name="Points Secondary Color",
        default=(255/255, 135/255, 55/255, 1.0),
        subtype='COLOR_GAMMA',
        size=4,
    )

    points_tertiary_color: FloatVectorProperty(
        name="Points Tertiary Color",
        default=(82/255, 224/255, 82/255, 1.0),
        subtype='COLOR_GAMMA',
        size=4,
    )

    points_guide_line_color: FloatVectorProperty(
        name="Points Guide Line Color",
        default=(82/255, 224/255, 82/255, 0.5),
        subtype='COLOR_GAMMA',
        size=4,
    )

    axis_x_color: FloatVectorProperty(
        name="Axis X Color",
        default=(226/255, 54/255, 54/255),
        subtype='COLOR_GAMMA',
        size=3,
    )

    axis_y_color: FloatVectorProperty(
        name="Axis Y Color",
        default=(130/255, 221/255, 85/255),
        subtype='COLOR_GAMMA',
        size=3,
    )

    axis_z_color: FloatVectorProperty(
        name="Axis Z Color",
        default=(74/255, 144/255, 226/255),
        subtype='COLOR_GAMMA',
        size=3,
    )

    tabs: EnumProperty(
        name="Tabs",
        items=[
            ("GENERAL", "General", ""),
            ("UI", "UI", ""),
            ("KEYMAP", "Keymap", ""),
            ("THEME", "Theme", ""),
        ],
        default="GENERAL",
    )

    enable_auto_smooth: BoolProperty(
        name="Enable Auto Smoothing",
        default=True,
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

    custom_screw_heads_path: StringProperty(
        name="Custom Screw Heads",
        subtype='FILE_PATH',
    )

    overlay_show_annotation: BoolProperty(
        name="Show Annotations",
        default=False
    )

    overlay_show_axis_x: BoolProperty(
        name="Show X Axis",
        default=False
    )

    overlay_show_axis_y: BoolProperty(
        name="Show Y Axis",
        default=False
    )

    overlay_show_axis_z: BoolProperty(
        name="Show Z Axis",
        default=False
    )

    overlay_show_bones: BoolProperty(
        name="Show Bones",
        default=False
    )

    overlay_show_cursor: BoolProperty(
        name="Show Cursor",
        default=False
    )

    overlay_show_extras: BoolProperty(
        name="Show Extras",
        default=False
    )

    overlay_show_floor: BoolProperty(
        name="Show Floor",
        default=False
    )

    overlay_show_motion_paths: BoolProperty(
        name="Show Motion Paths",
        default=False
    )

    overlay_show_object_origins: BoolProperty(
        name="Show Object Origins",
        default=False
    )

    overlay_show_object_origins_all: BoolProperty(
        name="Show Object Origins (All)",
        default=False
    )

    overlay_show_ortho_grid: BoolProperty(
        name="Show Ortho Grid",
        default=False
    )

    overlay_show_outline_selected: BoolProperty(
        name="Show Outline Selected",
        default=False
    )

    overlay_show_relationship_lines: BoolProperty(
        name="Show Relationship Lines",
        default=False
    )

    overlay_show_stats: BoolProperty(
        name="Show Stats",
        default=False
    )

    overlay_show_text: BoolProperty(
        name="Show Text",
        default=False
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
        elif self.tabs == "THEME":
            self.draw_theme(box)


    def draw_general(self, box):
        general_prefs = [
            "utils_collection_name",
            "use_fast_booleans",
            "recon_poly_solidify",
            "recon_poly_inscribed",
            "enable_right_click_select",
            "enable_auto_smooth"]

        for pref in general_prefs:
            column = box.column(align=True)
            row = column.row()
            row.prop(self, pref)

        general_boxed_prefs = [
            ["The default angle to use for bevel and smoothing operations", "default_smoothing_angle", True, True],
            ["Set a path for a custom screw heads .blend file", "custom_screw_heads_path", False, True],
            ["Automatically check if ND is up to date when Blender starts", "enable_update_check", False, not lib.addons.is_extension()],
            ["Enable deprecated features for short term backwards compatibility", "enable_deprecated_features", False, True],
            ["Enable experimental features. Use at your own risk!", "enable_experimental_features", False, True]]

        for label, prop, expanded, visible in general_boxed_prefs:
            if not visible:
                continue

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
            ["extend_mouse_values"],
            ["mouse_value_scalar"],
            ["mouse_value_steps"],
            ["unit_increment_size"],
            ["enable_quick_favourites"],
            ["lock_overlay_pinning"],
            ["enable_sidebar"],
            ["enable_axis_helper"],
            ["axis_base_thickness", "axis_active_thickness", "axis_inactive_opacity"]]

        for prefs in ui_prefs:
            column = box.column(align=True)
            row = column.row()
            for pref in prefs:
                row.prop(self, pref)

        overlay_prefs = [
            "overlay_show_annotation",
            "overlay_show_axis_x",
            "overlay_show_axis_y",
            "overlay_show_axis_z",
            "overlay_show_bones",
            "overlay_show_cursor",
            "overlay_show_extras",
            "overlay_show_floor",
            "overlay_show_motion_paths",
            "overlay_show_object_origins",
            "overlay_show_object_origins_all",
            "overlay_show_ortho_grid",
            "overlay_show_outline_selected",
            "overlay_show_relationship_lines",
            "overlay_show_stats",
            "overlay_show_text",
        ]

        pref_box = box.box()
        column = pref_box.column(align=True)
        row = column.row()
        row.label(text="Custom Overlay Options")
        for counter, pref in enumerate(overlay_prefs):
            if counter % 4 == 0:
                row = column.row()
            row.prop(self, pref)


    def draw_keymap(self, box):
        overlay_prefs = [
            "overlay_pin_key",
            "overlay_pause_key",
            "overlay_reset_key"]

        column = box.column(align=True)
        row = column.row()
        row.label(text="Overlay Keybinds")

        for pref in overlay_prefs:
            column = box.column(align=True)
            row = column.row()
            row.prop(self, pref)

        version = (1, 43, 1)

        name = "ND v%s" % ('.'.join([str(v) for v in version]))
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        for keymap in ['Mesh', 'Object Mode']:
            km = kc.keymaps.get(keymap)

            column = box.column(align=True)
            row = column.row()
            row.label(text=keymap)

            for kmi in km.keymap_items:
                if (kmi.idname == "wm.call_menu" and kmi.name.startswith(name)) or kmi.idname.startswith("nd."):
                    column = box.column(align=True)
                    row = column.row()
                    rna_keymap_ui.draw_kmi(["ADDON", "USER", "DEFAULT"], kc, km, kmi, row, 0)


    def draw_theme(self, box):
        column = box.column(align=True)
        row = column.row()
        row.label(text="ND Theme Colors")

        row.operator("nd.reset_theme")

        colors = [
            "overlay_header_standard_color",
            "overlay_header_recalled_color",
            "overlay_header_paused_color",
            "overlay_base_color",
            "overlay_option_active_color",
            "overlay_option_manual_override_color",
            "points_primary_color",
            "points_secondary_color",
            "points_tertiary_color",
            "points_guide_line_color",
            "axis_x_color",
            "axis_y_color",
            "axis_z_color"]

        for pref in colors:
            column = box.column(align=True)
            row = column.row()
            row.prop(self, pref)


def register():
    lib.reload()

    bpy.utils.register_class(NDPreferences)

    for registerable in registerables:
        registerable.reload()
        registerable.register()

    version = (1, 43, 1)
    prefs = lib.preferences.get_preferences()

    if not lib.addons.is_extension() and prefs.enable_update_check:
        prefs.update_available = lib.updates.update_available(version)
    else:
        prefs.update_available = False


def unregister():
    for registerable in registerables:
        registerable.unregister()

    bpy.utils.unregister_class(NDPreferences)
