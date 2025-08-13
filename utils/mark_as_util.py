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
from .. lib.objects import set_object_util_visibility
from .. lib.polling import ctx_obj_mode, ctx_min_objects_selected, objs_are_mesh


class ND_OT_mark_as_util(bpy.types.Operator):
    bl_idname = "nd.mark_as_util"
    bl_label = "Mark as Utility"
    bl_description = """Mark the selected objects as utilities
CTRL — Unmark the selected objects as utilities
SHIFT — Recursively mark all children of the selected objects as utilities"""


    @classmethod
    def poll(cls, context):
        return ctx_obj_mode(context) and \
               ctx_min_objects_selected(context, 1) and \
               objs_are_mesh(context.selected_objects)


    def invoke(self, context, event):
        revert = event.ctrl
        deep = event.shift

        for obj in bpy.context.selected_objects:
            self.set_util_visibility(obj, not revert, deep=deep)

        return {'FINISHED'}


    def set_util_visibility(self, obj, visible, deep=False):
        set_object_util_visibility(obj, visible)

        if deep:
            for child in obj.children:
                self.set_util_visibility(child, visible, deep=True)


def register():
    bpy.utils.register_class(ND_OT_mark_as_util)


def unregister():
    bpy.utils.unregister_class(ND_OT_mark_as_util)
