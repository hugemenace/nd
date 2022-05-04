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


class ND_PT_utils_ui_panel(bpy.types.Panel):
    bl_label = "ND v%s — Utils" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_PT_utils_ui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HugeMenace"


    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Object Names", icon='SCENE_DATA')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.name_sync", icon='FILE_REFRESH')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.set_lod_suffix", text="Low LOD", icon='ALIASED').suffix = 'LOW'
        row.operator("nd.set_lod_suffix", text="High LOD", icon='ANTIALIASED').suffix = 'HIGH'

        box = layout.box()
        box.label(text="Object Transform", icon='ORIENTATION_GIMBAL')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.set_origin", icon='TRANSFORM_ORIGINS')

        box = layout.box()
        box.label(text="Object Properties", icon='MESH_DATA')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.cycle", icon='LONGDISPLAY')
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.smooth", icon='MOD_SMOOTH')
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.seams", icon='UV_DATA')
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.hydrate", icon='SHADING_RENDERED')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.clear_vgs", icon='GROUP_VERTEX')

        
def register():
    bpy.utils.register_class(ND_PT_utils_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_utils_ui_panel)
