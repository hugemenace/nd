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
from .. import bl_info
from .. import lib
from . import ops
from . common import create_box, render_ops, web_link


links = [
    ("https://docs.nd.hugemenace.co", "Documentation", 'HOME'),
    ("https://hugemenace.co/youtube", "YouTube Channel", 'VIEW_CAMERA'),
    ("https://hugemenace.co/nd/feedback", "Feature Requests / Bugs", 'FILE_SCRIPT'),
    ("https://hugemenace.co/discord", "Discord Server", 'SYNTAX_ON'),
    ("https://hugemenace.co/patreon", "Support ND on Patreon", 'SOLO_ON'),
]


op_sections = [
    ("Standalone", ops.standalone_ops),
    ("Sketch", ops.sketch_ops),
    ("Booleans", ops.boolean_ops),
    ("Bevels", ops.bevel_ops),
    ("Extrusion", ops.extrusion_ops),
    ("Replicate", ops.replicate_ops),
    ("Deform", ops.deform_ops),
    ("Simplify", ops.simplify_ops),
    ("Utils", ops.util_ops),
    ("Viewport", ops.viewport_ops),
]


class ND_PT_main_ui_panel(bpy.types.Panel):
    bl_label = "ND v%s — Core" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_PT_main_ui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HugeMenace"


    def draw(self, context):
        layout = self.layout

        if lib.preferences.get_preferences().update_available:
            box = layout.box()
            column = box.column()

            row = column.row(align=True)
            row.scale_y = 1.5
            row.alert = True
            web_link("https://hugemenace.gumroad.com/l/nd-blender-addon", "Update Available!", "PACKAGE", row)

            row = column.row(align=True)
            row.scale_y = 1.2
            web_link("https://docs.nd.hugemenace.co/#/getting-started/changelog", "View Changelog", "DOCUMENTS", row)
        
        box = create_box("Useful Links", None, layout)
        for url, label, icon in links:
            row = box.row(align=True)
            row.scale_y = 1.2
            web_link(url, label, icon, row)

        for label, collection in op_sections:
            box = create_box(label, None, layout)
            render_ops(collection, box)

        
def register():
    bpy.utils.register_class(ND_PT_main_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_main_ui_panel)
