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
from bpy.props import BoolProperty, PointerProperty
from .. __init__ import bl_info
from .. import lib
from . import ops
from . common import create_box, render_ops, web_link
from .. lib.preferences import get_preferences


links = [
    ("https://docs.nd.hugemenace.co", "Documentation", 'HOME'),
    ("https://hugemenace.co/youtube", "YouTube Channel", 'VIEW_CAMERA'),
    ("https://hugemenace.co/nd/feedback", "Feature Requests / Bugs", 'FILE_SCRIPT'),
    ("https://hugemenace.co/discord", "Discord Server", 'SYNTAX_ON'),
    ("https://hugemenace.co/patreon", "Support ND on Patreon", 'SOLO_ON'),
]


op_sections = [
    ("Standalone", ops.standalone_ops, "standalone", [("nd.cycle", None)]),
    ("Sketch", ops.sketch_ops, "sketch", [("nd.single_vertex", None), ("nd.panel", None), ("nd.recon_poly", None)]),
    ("Generators", ops.generator_ops, "generators", [("nd.hole_generator", None), ("nd.pipe_generator", None)]),
    ("Booleans", ops.boolean_ops, "booleans", [("nd.bool_vanilla", "DIFFERENCE"), ("nd.bool_vanilla", "UNION"), ("nd.bool_vanilla", "INTERSECT")]),
    ("Bevels", ops.bevel_ops, "bevels", [("nd.bevel", None), ("nd.vertex_bevel", None), ("nd.edge_bevel", None)]),
    ("Extrusion", ops.extrusion_ops, "extrusion", [("nd.solidify", None), ("nd.screw", None), ("nd.profile_extrude", None)]),
    ("Replicate", ops.replicate_ops, "replicate", [("nd.array_cubed", None), ("nd.circular_array", None), ("nd.mirror", None)]),
    ("Deform", ops.deform_ops, "deform", [("nd.lattice", None), ("nd.simple_deform", None)]),
    ("Simplify", ops.simplify_ops, "simplify", [("nd.decimate", None), ("nd.weld", None)]),
    ("Shading", ops.shading_ops, "shading", [("nd.smooth", None), ("nd.wn", None)]),
    ("Scene", ops.scene_ops, "scene", [("nd.flare", None), ("nd.clean_utils", None)]),
    ("Data", ops.data_ops, "data", [("nd.clear_vgs", None)]),
    ("Packaging", ops.packaging_ops, "packaging", [("nd.set_lod_suffix", "LOW"), ("nd.set_lod_suffix", "HIGH"), ("nd.triangulate", None)]),
    ("Utils", ops.util_ops, "utils", [("nd.set_origin", None), ("nd.snap_align", None), ("nd.apply_modifiers", None)]),
    ("Viewport", ops.viewport_ops, "viewport", [("nd.toggle_wireframes", None), ("nd.toggle_utils", 'DYNAMIC'), ("nd.toggle_clear_view", None)]),
]


icons = ops.build_icon_lookup_table()


class MainUIPanelProps(bpy.types.PropertyGroup):
    display_links: BoolProperty(default=False)
    standalone: BoolProperty(default=False)
    sketch: BoolProperty(default=False)
    generators: BoolProperty(default=False)
    booleans: BoolProperty(default=False)
    bevels: BoolProperty(default=False)
    extrusion: BoolProperty(default=False)
    replicate: BoolProperty(default=False)
    deform: BoolProperty(default=False)
    simplify: BoolProperty(default=False)
    shading: BoolProperty(default=False)
    scene: BoolProperty(default=False)
    data: BoolProperty(default=False)
    packaging: BoolProperty(default=False)
    utils: BoolProperty(default=False)
    viewport: BoolProperty(default=False)


class ND_OT_toggle_sections(bpy.types.Operator):
    bl_idname = "nd.toggle_sections"
    bl_label = "Toggle Sections"
    bl_description = "Toggle the visibility of all sections below"

    def execute(self, context):
        props = context.window_manager.nd_panel_props
        toggle = True

        for prop in list(props.keys()):
            toggle = not getattr(props, prop)

        props.display_links = toggle
        props.standalone = toggle
        props.sketch = toggle
        props.generators = toggle
        props.booleans = toggle
        props.bevels = toggle
        props.extrusion = toggle
        props.replicate = toggle
        props.deform = toggle
        props.simplify = toggle
        props.shading = toggle
        props.scene = toggle
        props.data = toggle
        props.packaging = toggle
        props.export = toggle
        props.utils = toggle
        props.viewport = toggle

        return {'FINISHED'}


class ND_PT_main_ui_panel(bpy.types.Panel):
    bl_label = "Main Panel — ND v%s" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_PT_main_ui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HugeMenace"


    def draw(self, context):
        props = context.window_manager.nd_panel_props
        layout = self.layout

        row = layout.column()
        row.operator("nd.toggle_sections")
        row.separator()

        if not lib.addons.is_extension() and lib.preferences.get_preferences().update_available:
            box = layout.box()
            column = box.column()

            row = column.row(align=True)
            row.scale_y = 1.5
            row.alert = True
            web_link("https://hugemenace.gumroad.com/l/nd-blender-addon", "Update Available!", "PACKAGE", row)

            row = column.row(align=True)
            row.scale_y = 1.2
            web_link("https://docs.nd.hugemenace.co/#/getting-started/changelog", "View Changelog", "DOCUMENTS", row)

        if not lib.addons.is_extension():
          box = create_box("Useful Links", layout, props, "display_links", icons, [])
          if props.display_links:
              for url, label, icon in links:
                  row = box.row(align=True)
                  row.scale_y = 1.2
                  web_link(url, label, icon, row)

        for label, collection, prop, shortcuts in op_sections:
            box = create_box(label, layout, props, prop, icons, shortcuts)
            if getattr(props, prop):
                render_ops(collection, box)


def register():
    if get_preferences().enable_sidebar:
        bpy.utils.register_class(ND_PT_main_ui_panel)
        bpy.utils.register_class(ND_OT_toggle_sections)
        bpy.utils.register_class(MainUIPanelProps)

        bpy.types.WindowManager.nd_panel_props = PointerProperty(type=MainUIPanelProps)


def unregister():
    if get_preferences().enable_sidebar:
        bpy.utils.unregister_class(ND_PT_main_ui_panel)
        bpy.utils.unregister_class(ND_OT_toggle_sections)
        bpy.utils.unregister_class(MainUIPanelProps)

        del bpy.types.WindowManager.nd_panel_props
