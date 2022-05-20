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


class ND_OT_clear_vgs(bpy.types.Operator):
    bl_idname = "nd.clear_vgs"
    bl_label = "Clear Vertex Groups"
    bl_description = "Remove the active vertices from all vertex groups on the selected object"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH':
            mesh = bmesh.from_edit_mesh(context.object.data)
            return len([vert for vert in mesh.verts if vert.select]) >= 1


    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        selected_vert_indices = [vert.index for vert in bm.verts if vert.select]
        bm.free()

        bpy.ops.object.mode_set(mode='OBJECT')

        for vg in context.object.vertex_groups:
            vg.remove(selected_vert_indices)

        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ND_OT_clear_vgs.bl_idname, text=ND_OT_clear_vgs.bl_label)


def register():
    bpy.utils.register_class(ND_OT_clear_vgs)


def unregister():
    bpy.utils.unregister_class(ND_OT_clear_vgs)
