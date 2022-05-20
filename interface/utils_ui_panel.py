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
from . ops import object_names_ops, object_transform_ops, object_properties_ops, misc_ops
from . common import create_box, render_ops


class ND_PT_utils_ui_panel(bpy.types.Panel):
    bl_label = "ND v%s — Utils" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_PT_utils_ui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HugeMenace"


    def draw(self, context):
        layout = self.layout
        
        box = create_box("Object Names", 'SCENE_DATA', layout)
        render_ops(object_names_ops, box)

        box = create_box("Object Transform", 'ORIENTATION_GIMBAL', layout)
        render_ops(object_transform_ops, box)

        box = create_box("Object Properties", 'MESH_DATA', layout)
        render_ops(object_properties_ops, box)

        box = create_box("Miscellaneous", 'ASSET_MANAGER', layout)
        render_ops(misc_ops, box)

        
def register():
    bpy.utils.register_class(ND_PT_utils_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_utils_ui_panel)
