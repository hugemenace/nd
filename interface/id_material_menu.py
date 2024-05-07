# ███╗   ██╗██████╗
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝
#
# ND (Non-Destructive) Blender Add-on
# Copyright (C) 2024 Tristan S. & Ian J. (HugeMenace)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
