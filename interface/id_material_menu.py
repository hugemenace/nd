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


class ND_MT_id_material_menu(bpy.types.Menu):
    bl_label = "ID Material"
    bl_idname = "ND_MT_id_material_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        render_ops(ops.id_material_ops, layout, new_row=False, use_separator=True)

        existing_material_names = bpy.data.materials.keys()
        if any(name.startswith("ND_ID_MAT_") for name in existing_material_names):
            layout.separator()
            for material in bpy.data.materials:
                if material.name.startswith("ND_ID_MAT_"):
                    clean_name = material.name[len("ND_ID_MAT_"):].capitalize()
                    layout.operator("nd.assign_id_material", text=clean_name, icon='LAYER_ACTIVE').material = material.name
        

def register():
    bpy.utils.register_class(ND_MT_id_material_menu)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_id_material_menu)
