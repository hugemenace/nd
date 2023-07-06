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
from .. lib.modifiers import new_modifier


class ND_OT_triangulate(bpy.types.Operator):
    bl_idname = "nd.triangulate"
    bl_label = "Triangulate"
    bl_description = """Add a triangulate modifier to the selected objects
ALT — Do not preserve custom normals
SHIFT — Only triangulate ngons (5+ vertices)"""
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) > 0:
            return all(obj.type == 'MESH' for obj in context.selected_objects)


    def invoke(self, context, event):
        self.preserve_normals = not event.alt
        self.only_ngons = event.shift

        for obj in context.selected_objects:
            triangulate = new_modifier(obj, 'Triangulate — ND', 'TRIANGULATE', rectify=False)
            triangulate.keep_custom_normals = self.preserve_normals
            triangulate.quad_method = 'FIXED' if self.preserve_normals else 'BEAUTY'
            triangulate.min_vertices = 5 if self.only_ngons else 4

        return {'FINISHED'}

    
def register():
    bpy.utils.register_class(ND_OT_triangulate)


def unregister():
    bpy.utils.unregister_class(ND_OT_triangulate)
