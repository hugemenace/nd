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


class ND_MT_deform_menu(bpy.types.Menu):
    bl_label = "Deform"
    bl_idname = "ND_MT_deform_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.lattice", icon='MOD_LATTICE')
        layout.operator("nd.simple_deform", icon='MOD_SIMPLEDEFORM')


def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_deform_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_deform_menu)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_deform_menu)
