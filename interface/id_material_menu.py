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
from .. icons import get_icon_value
from .. packaging.create_id_material import ND_MATERIALS


class ND_MT_id_material_menu(bpy.types.Menu):
    bl_label = "Material Selection"
    bl_idname = "ND_MT_id_material_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        materials = list(ND_MATERIALS.keys())
        
        row = layout.row()

        column = row.column()
        for material_name in materials[:11]:
            clean_name = material_name[len("ND_ID_MAT_"):].capitalize()
            column.operator("nd.create_id_material", text=clean_name, icon_value=get_icon_value(material_name)).material_name = material_name

        column = row.column()
        for material_name in materials[11:]:
            clean_name = material_name[len("ND_ID_MAT_"):].capitalize()
            column.operator("nd.create_id_material", text=clean_name, icon_value=get_icon_value(material_name)).material_name = material_name
        

def register():
    bpy.utils.register_class(ND_MT_id_material_menu)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_id_material_menu)
