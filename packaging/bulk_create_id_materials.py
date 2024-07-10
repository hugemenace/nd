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
from .. lib.polling import ctx_obj_mode, list_ok, list_lte


class ND_OT_bulk_create_id_materials(bpy.types.Operator):
    bl_idname = "nd.bulk_create_id_materials"
    bl_label = "Bulk Assign Materials"
    bl_description = "Assign a random ID material to each of the selected objects"
    bl_options = {'UNDO'}


    def get_valid_objects(self, context):
        return [obj for obj in context.selected_objects if obj.type in {'MESH', 'CURVE'}]


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context)
        return ctx_obj_mode(context) and list_ok(valid_objects) and list_lte(valid_objects, len(ND_MATERIALS))


    def execute(self, context):
        valid_objects = self.get_valid_objects(context)

        material_names = sample(list(ND_MATERIALS.keys()), k=len(valid_objects))
        existing_material_names = bpy.data.materials.keys()

        for i, obj in enumerate(valid_objects):
            obj.data.materials.clear()

            material_name = material_names[i]
            material = None
            if material_name in existing_material_names:
                material = bpy.data.materials[material_name]
            else:
                material = create_id_material(material_name)

            obj.active_material = material

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_bulk_create_id_materials)


def unregister():
    bpy.utils.unregister_class(ND_OT_bulk_create_id_materials)
