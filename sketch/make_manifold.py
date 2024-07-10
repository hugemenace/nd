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
from .. lib.polling import is_edit_mode


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
        return is_edit_mode(context)


def register():
    bpy.utils.register_class(ND_OT_make_manifold)


def unregister():
    bpy.utils.unregister_class(ND_OT_make_manifold)
