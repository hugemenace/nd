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
from . import ops
from . common import render_ops


class ND_MT_export_menu(bpy.types.Menu):
    bl_label = "Export"
    bl_idname = "ND_MT_export_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        render_ops(ops.export_ops, layout, new_row=False, use_separator=True)
        

def register():
    bpy.utils.register_class(ND_MT_export_menu)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_export_menu)
