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


class ND_PT_viewport_ui_panel(bpy.types.Panel):
    bl_label = "ND v%s — Viewport" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_PT_viewport_ui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HugeMenace"


    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Toggles", icon='CON_ACTION')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.toggle_wireframes", icon='MOD_WIREFRAME')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.toggle_face_orientation", icon="ORIENTATION_NORMAL")

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.toggle_utils_collection", icon="OUTLINER_COLLECTION")
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.toggle_clear_view", icon="OUTLINER_DATA_VOLUME")

        
def register():
    bpy.utils.register_class(ND_PT_viewport_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_viewport_ui_panel)
