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
from .. lib.objects import configure_object_as_util
from .. lib.polling import ctx_obj_mode, ctx_min_objects_selected, objs_are_mesh


class ND_OT_mark_as_util(bpy.types.Operator):
    bl_idname = "nd.mark_as_util"
    bl_label = "Mark as Utility"
    bl_description = """Mark the selected objects as utilities
CTRL — Unmark the selected objects as utilities
ALT — Do not use the last object as a parent
SHIFT — Recursively mark all children of the selected objects as utilities"""


    @classmethod
    def poll(cls, context):
        return ctx_obj_mode(context) and \
               ctx_min_objects_selected(context, 1) and \
               objs_are_mesh(context.selected_objects)


    def invoke(self, context, event):
        revert = event.ctrl
        deep = event.shift
        no_parent = event.alt

        if revert:
            for obj in bpy.context.selected_objects:
                self.set_util_visibility(obj, False, deep=deep)
                if obj.parent:
                    obj_matrix_world = obj.matrix_world.copy()
                    obj.parent = None
                    obj.matrix_world = obj_matrix_world
            return {'FINISHED'}

        multi_select = len(context.selected_objects) > 1
        if not multi_select or no_parent:
            for obj in bpy.context.selected_objects:
                self.set_util_visibility(obj, True, deep=deep)
        else:
            selection = context.selected_objects.copy()
            selection.remove(context.active_object)
            for obj in selection:
                self.set_util_visibility(obj, True, deep=deep)
                if obj.parent:
                    obj_matrix_world = obj.matrix_world.copy()
                    obj.parent = None
                    obj.matrix_world = obj_matrix_world
                obj.parent = context.active_object
                obj.matrix_parent_inverse = context.active_object.matrix_world.inverted()

        return {'FINISHED'}


    def set_util_visibility(self, obj, set_util, deep=False):
        configure_object_as_util(obj, set_util)

        if deep:
            for child in obj.children:
                self.set_util_visibility(child, set_util, deep=True)


def register():
    bpy.utils.register_class(ND_OT_mark_as_util)


def unregister():
    bpy.utils.unregister_class(ND_OT_mark_as_util)
