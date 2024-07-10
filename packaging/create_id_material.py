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
import bmesh
import numpy
from random import choice
from .. lib.polling import is_object_edit_mode, list_gt


# Distinct color names and RGB values from:
# https://sashamaps.net/docs/resources/20-colors/
ND_MATERIALS = {
    'ND_ID_MAT_RED': (230, 25, 75),
    'ND_ID_MAT_GREEN': (60, 180, 75),
    'ND_ID_MAT_YELLOW': (255, 225, 25),
    'ND_ID_MAT_BLUE': (0, 130, 200),
    'ND_ID_MAT_ORANGE': (245, 130, 48),
    'ND_ID_MAT_PURPLE': (145, 30, 180),
    'ND_ID_MAT_CYAN': (70, 240, 240),
    'ND_ID_MAT_MAGENTA': (240, 50, 230),
    'ND_ID_MAT_LIME': (210, 245, 60),
    'ND_ID_MAT_PINK': (250, 190, 212),
    'ND_ID_MAT_TEAL': (0, 128, 128),
    'ND_ID_MAT_LAVENDER': (220, 190, 255),
    'ND_ID_MAT_BROWN': (170, 110, 40),
    'ND_ID_MAT_BEIGE': (255, 250, 200),
    'ND_ID_MAT_MAROON': (128, 0, 0),
    'ND_ID_MAT_MINT': (170, 255, 195),
    'ND_ID_MAT_OLIVE': (128, 128, 0),
    'ND_ID_MAT_APRICOT': (255, 215, 180),
    'ND_ID_MAT_NAVY': (0, 0, 128),
    'ND_ID_MAT_GREY': (128, 128, 128),
    'ND_ID_MAT_WHITE': (255, 255, 255),
    'ND_ID_MAT_BLACK': (0, 0, 0),
}


def create_id_material(name):
    r, g, b = ND_MATERIALS[name]

    r_ = pow(r / 255, 2.2)
    g_ = pow(g / 255, 2.2)
    b_ = pow(b / 255, 2.2)

    material = bpy.data.materials.new(name)
    material.diffuse_color = (r_, g_, b_, 1)
    material.specular_intensity = 0.5
    material.roughness = 0.75
    material.use_fake_user = True

    return material


class ND_OT_create_id_material(bpy.types.Operator):
    bl_idname = "nd.create_id_material"
    bl_label = "Create ID Material"
    bl_description = "Create and assign a new ID material to the selected object or geometry"
    bl_options = {'UNDO'}


    material_name: bpy.props.StringProperty(name="Material Name")


    def get_valid_objects(self, context, edit_mode):
        if edit_mode:
            return [obj for obj in context.selected_objects if obj.type == 'MESH']

        return [obj for obj in context.selected_objects if obj.type in {'MESH', 'CURVE'}]


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context, edit_mode=is_edit_mode(context))
        return is_object_edit_mode(context) and list_gt(valid_objects, 0)


    def execute(self, context):
        existing_material_names = bpy.data.materials.keys()

        material = None
        if self.material_name in existing_material_names:
            material = bpy.data.materials[self.material_name]
        else:
            material = create_id_material(self.material_name)

        if context.mode == 'OBJECT':
            valid_objects = self.get_valid_objects(context, edit_mode=False)

            for obj in valid_objects:
                obj.data.materials.clear()
                obj.active_material = material

        if context.mode == 'EDIT_MESH':
            valid_objects = self.get_valid_objects(context, edit_mode=True)

            for obj in valid_objects:
                previous_material_names = [m.name for m in obj.material_slots]
                if self.material_name not in previous_material_names:
                    obj.data.materials.append(material)

                active_materials = [slot.name for slot in obj.material_slots]

                bm = bmesh.from_edit_mesh(obj.data)
                for face in bm.faces:
                    if face.select:
                        face.material_index = active_materials.index(self.material_name)

                bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_create_id_material)


def unregister():
    bpy.utils.unregister_class(ND_OT_create_id_material)
