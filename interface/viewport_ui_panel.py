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
from . ops import toggle_ops
from . common import create_box, render_ops


class ND_PT_viewport_ui_panel(bpy.types.Panel):
    bl_label = "ND v%s — Viewport" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_PT_viewport_ui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HugeMenace"


    def draw(self, context):
        layout = self.layout
        
        box = create_box("Toggles", 'CON_ACTION', layout)
        render_ops(toggle_ops, box)

        
def register():
    bpy.utils.register_class(ND_PT_viewport_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_viewport_ui_panel)
