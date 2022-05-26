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


class ND_MT_extrude_menu(bpy.types.Menu):
    bl_label = "Extrusion"
    bl_idname = "ND_MT_extrude_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.solidify", icon='MOD_SOLIDIFY')
        layout.operator("nd.screw", icon='MOD_SCREW')
        layout.operator("nd.profile_extrude", icon='EMPTY_SINGLE_ARROW')
        

def register():
    bpy.utils.register_class(ND_MT_extrude_menu)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_extrude_menu)
