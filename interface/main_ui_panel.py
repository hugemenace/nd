# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy
from .. import bl_info
from .. import lib
from . ops import sketching_ops, power_mod_ops, generator_ops
from . common import create_box, render_ops, web_link


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
        
        box = create_box("Useful Links", 'INFO', layout)
        
        row = box.row(align=True)
        row.scale_y = 1.3
        web_link("https://docs.nd.hugemenace.co", "Documentation", 'HOME', row)

        row = box.row(align=True)
        row.scale_y = 1.3
        web_link("https://hugemenace.co/youtube", "YouTube Channel", 'VIEW_CAMERA', row)

        row = box.row(align=True)
        row.scale_y = 1.3
        web_link("https://hugemenace.co/nd/feedback", "Feature Requests / Bugs", 'FILE_SCRIPT', row)

        row = box.row(align=True)
        row.scale_y = 1.3
        web_link("https://hugemenace.co/discord", "Discord Server", 'SYNTAX_ON', row)

        row = box.row(align=True)
        row.scale_y = 1.3
        web_link("https://hugemenace.co/patreon", "Support ND on Patreon", 'SOLO_ON', row)

        box = create_box("Sketching", 'GREASEPENCIL', layout)
        render_ops(sketching_ops, box)

        box = create_box("Power Mod", 'MODIFIER', layout)
        render_ops(power_mod_ops, box)

        box = create_box("Generators", 'GHOST_ENABLED', layout)
        render_ops(generator_ops, box)
        
        
def register():
    bpy.utils.register_class(ND_PT_main_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_main_ui_panel)
