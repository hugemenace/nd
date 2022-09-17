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


class ND_OT_assign_id_material(bpy.types.Operator):
    bl_idname = "nd.assign_id_material"
    bl_label = "Assign ID Material"
    bl_description = "Assign an existing ID material to the selected object or geometry"
    bl_options = {'UNDO'}


    material: bpy.props.StringProperty(name="Material Name")


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) >= 1 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        if self.material not in bpy.data.materials.keys():
            self.report({'ERROR'}, "The specified material does not exist.")

            return {'CANCELLED'}

        for object in context.selected_objects:
            object.active_material = bpy.data.materials[self.material]

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_assign_id_material)


def unregister():
    bpy.utils.unregister_class(ND_OT_assign_id_material)
