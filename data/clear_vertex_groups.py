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
from .. lib.polling import ctx_edit_mode, ctx_obj_mode, ctx_min_objects_selected, objs_are_mesh, obj_is_mesh, obj_verts_selected


class ND_OT_clear_vertex_groups(bpy.types.Operator):
    bl_idname = "nd.clear_vertex_groups"
    bl_label = "Clear Vertex Groups"
    bl_description = """Remove the active vertices from all vertex groups on the selected object
SHIFT — Do not remove empty vertex groups"""
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

        if ctx_edit_mode(context) and not obj_verts_selected(context.active_object):
            self.report({'INFO'}, "No vertices selected.")
            return {'CANCELLED'}

        # If we're in object mode simply remove all vertex groups and finish
        if ctx_obj_mode(context):
            for obj in context.selected_objects:
                for vg in obj.vertex_groups:
                    obj.vertex_groups.remove(vg)
            return {'FINISHED'}


        # If we're in edit mode, only remove the selected vertices from groups their in
        # ...

        bm = bmesh.from_edit_mesh(context.active_object.data)
        bm.verts.ensure_lookup_table()
        selected_vert_indices = [vert.index for vert in bm.verts if vert.select]
        bm.free()

        bpy.ops.object.mode_set(mode='OBJECT')

        for vg in context.active_object.vertex_groups:
            vg.remove(selected_vert_indices)

        if self.remove_empty_vertex_groups:
            for vg in context.active_object.vertex_groups:
                if self.is_vertex_group_empty(context.active_object, vg.name):
                    context.active_object.vertex_groups.remove(vg)

        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


    def invoke(self, context, event=None):
        self.remove_empty_vertex_groups = True
        if event and event.shift:
            self.remove_empty_vertex_groups = False

        return self.execute(context)


    def is_vertex_group_empty(self, obj, group_name):
        if group_name not in obj.vertex_groups:
            return True  # Group doesn't exist, so it's "empty"

        group = obj.vertex_groups[group_name]

        # Check if any vertex has weight > 0 for this group
        for vertex in obj.data.vertices:
            for group_element in vertex.groups:
                if group_element.group == group.index and group_element.weight > 0:
                    return False

        return True


def register():
    bpy.utils.register_class(ND_OT_clear_vertex_groups)


def unregister():
    bpy.utils.unregister_class(ND_OT_clear_vertex_groups)
