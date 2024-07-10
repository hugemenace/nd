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
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_edit_mode, obj_exists, obj_verts_selected


class ND_OT_clear_vgs(bpy.types.Operator):
    bl_idname = "nd.clear_vgs"
    bl_label = "Clear Vertex Groups"
    bl_description = "Remove the active vertices from all vertex groups on the selected object"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_edit_mode(context) and obj_exists(target_object) and obj_verts_selected(target_object)


    def execute(self, context):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(context.active_object.data)
        selected_vert_indices = [vert.index for vert in bm.verts if vert.select]
        bm.free()

        bpy.ops.object.mode_set(mode='OBJECT')

        for vg in context.active_object.vertex_groups:
            vg.remove(selected_vert_indices)

        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_clear_vgs)


def unregister():
    bpy.utils.unregister_class(ND_OT_clear_vgs)
