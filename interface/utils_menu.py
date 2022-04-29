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


class ND_MT_utils_menu(bpy.types.Menu):
    bl_label = "Utils"
    bl_idname = "ND_MT_utils_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.name_sync", icon='FILE_REFRESH')
        layout.operator("nd.set_lod_suffix", text="Low LOD", icon='ALIASED').suffix = 'LOW'
        layout.operator("nd.set_lod_suffix", text="High LOD", icon='ANTIALIASED').suffix = 'HIGH'
        layout.separator()
        layout.operator("nd.set_origin", icon='TRANSFORM_ORIGINS')
        layout.separator()
        layout.operator("nd.smooth", icon='MOD_SMOOTH')
        layout.operator("nd.seams", icon='UV_DATA')
        layout.operator("nd.hydrate", icon='SHADING_RENDERED')
        layout.operator("nd.clear_vgs", icon='GROUP_VERTEX')
        

def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_utils_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_utils_menu)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_utils_menu)
