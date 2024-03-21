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
from .create_id_material import ND_MATERIALS, create_id_material
from random import sample


class ND_OT_bulk_create_id_materials(bpy.types.Operator):
    bl_idname = "nd.bulk_create_id_materials"
    bl_label = "Bulk Assign Materials"
    bl_description = "Assign a random ID material to each of the selected objects"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) > 0 and \
            len(context.selected_objects) <= len(ND_MATERIALS) and \
            all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        material_names = sample(list(ND_MATERIALS.keys()), k=len(context.selected_objects))
        existing_material_names = bpy.data.materials.keys()

        for i, object in enumerate(context.selected_objects):
            object.data.materials.clear()

            material_name = material_names[i]
            material = None
            if material_name in existing_material_names:
                material = bpy.data.materials[material_name]
            else:
                material = create_id_material(material_name)

            object.active_material = material

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_bulk_create_id_materials)


def unregister():
    bpy.utils.unregister_class(ND_OT_bulk_create_id_materials)
