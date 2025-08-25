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
from .. lib.polling import ctx_edit_mode, ctx_obj_mode, ctx_min_objects_selected, objs_are_mesh, obj_is_mesh, obj_edges_selected


class ND_OT_clear_edge_marks(bpy.types.Operator):
    bl_idname = "nd.clear_edge_marks"
    bl_label = "Clear Edge Marks"
    bl_description = "Remove edge marks from the selected edges"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if ctx_obj_mode(context):
            return ctx_min_objects_selected(context, 1) and objs_are_mesh(context.selected_objects)

        if ctx_edit_mode(context):
            return obj_is_mesh(get_real_active_object(context))


    def execute(self, context):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        if ctx_edit_mode(context) and not obj_edges_selected(context.active_object):
            self.report({'INFO'}, "No edges selected.")
            return {'CANCELLED'}

        if ctx_obj_mode(context):
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.mesh.mark_seam(clear=True)
            bpy.ops.mesh.mark_freestyle_edge(clear=True)
            bpy.ops.object.mode_set(mode='OBJECT')

            return {'FINISHED'}

        bpy.ops.mesh.mark_sharp(clear=True)
        bpy.ops.mesh.mark_seam(clear=True)
        bpy.ops.mesh.mark_freestyle_edge(clear=True)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_clear_edge_marks)


def unregister():
    bpy.utils.unregister_class(ND_OT_clear_edge_marks)
