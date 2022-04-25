# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy
import bmesh


class ND_OT_make_manifold(bpy.types.Operator):
    bl_idname = "nd.make_manifold"
    bl_label = "Make Manifold"
    bl_description = "Attempts to turn the current sketch into a manifold polygon"
    bl_options = {'UNDO'}


    def execute(self, context):
        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'VERT'})
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.edge_face_add()

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'


def menu_func(self, context):
    self.layout.operator(ND_OT_make_manifold.bl_idname, text=ND_OT_make_manifold.bl_label)


def register():
    bpy.utils.register_class(ND_OT_make_manifold)


def unregister():
    bpy.utils.unregister_class(ND_OT_make_manifold)
