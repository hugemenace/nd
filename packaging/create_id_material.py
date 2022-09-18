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
import bmesh
import numpy
from random import choice


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


class ND_OT_create_id_material(bpy.types.Operator):
    bl_idname = "nd.create_id_material"
    bl_label = "Create ID Material"
    bl_description = "Create and assign a new ID material to the selected object or geometry"
    bl_options = {'UNDO'}


    material_name: bpy.props.StringProperty(name="Material Name")


    @classmethod
    def poll(cls, context):
        if context.mode in ['OBJECT', 'EDIT_MESH']:
            return len(context.selected_objects) >= 1 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        existing_material_names = bpy.data.materials.keys()
        
        material = None
        if self.material_name not in existing_material_names:
            r, g, b = ND_MATERIALS[self.material_name]

            r_ = pow(r / 255, 2.2)
            g_ = pow(g / 255, 2.2)
            b_ = pow(b / 255, 2.2)

            material = bpy.data.materials.new(self.material_name)
            material.diffuse_color = (r_, g_, b_, 1)
            material.specular_intensity = 0.5
            material.roughness = 0.75
            material.use_fake_user = True
        else:
            material = bpy.data.materials[self.material_name]

        if context.mode == 'OBJECT':
            for object in context.selected_objects:
                object.data.materials.clear()
                object.active_material = material
        
        if context.mode == 'EDIT_MESH':
            for object in context.selected_objects:
                previous_material_names = [m.name for m in object.material_slots]
                if self.material_name not in previous_material_names:
                    object.data.materials.append(material)

                active_materials = [slot.name for slot in object.material_slots]

                bm = bmesh.from_edit_mesh(object.data)
                for face in bm.faces:
                    if face.select:
                        face.material_index = active_materials.index(self.material_name)
                
                bmesh.update_edit_mesh(object.data)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_create_id_material)


def unregister():
    bpy.utils.unregister_class(ND_OT_create_id_material)
