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


class ND_MT_bevel_menu(bpy.types.Menu):
    bl_label = "Bevels"
    bl_idname = "ND_MT_bevel_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.vertex_bevel", icon='VERTEXSEL')
        layout.operator("nd.edge_bevel", icon='EDGESEL')
        layout.separator()
        layout.operator("nd.bevel", icon='MOD_BEVEL')
        layout.operator("nd.weighted_normal_bevel", icon='MOD_BEVEL')
        

def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_bevel_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_bevel_menu)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_bevel_menu)
