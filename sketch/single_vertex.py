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
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor


class ND_OT_single_vertex(bpy.types.Operator):
    bl_idname = "nd.single_vertex"
    bl_label = "Single Vertex"
    bl_description = "Creates a single vertex object at the 3D cursor"
    bl_options = {'UNDO'}


    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        add_single_vertex_object(self, context, "Sketch")
        align_object_to_3d_cursor(self, context)

        self.start_sketch_editing(context)

        return {'FINISHED'}


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def start_sketch_editing(self, context):
        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'VERT'})
        bpy.ops.mesh.select_all(action='SELECT')


def register():
    bpy.utils.register_class(ND_OT_single_vertex)


def unregister():
    bpy.utils.unregister_class(ND_OT_single_vertex)
