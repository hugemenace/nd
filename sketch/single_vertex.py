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
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor
from .. lib.polling import ctx_obj_mode


class ND_OT_single_vertex(bpy.types.Operator):
    bl_idname = "nd.single_vertex"
    bl_label = "Single Vertex"
    bl_description = "Creates a single vertex object at the 3D cursor"
    bl_options = {'UNDO'}


    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        add_single_vertex_object(self, context, "Sketch")
        align_object_to_3d_cursor(self, context)

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        self.start_sketch_editing(context)

        return {'FINISHED'}


    @classmethod
    def poll(cls, context):
        return ctx_obj_mode(context)


    def start_sketch_editing(self, context):
        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'VERT'})
        bpy.ops.mesh.select_all(action='SELECT')


def register():
    bpy.utils.register_class(ND_OT_single_vertex)


def unregister():
    bpy.utils.unregister_class(ND_OT_single_vertex)
