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
from .. lib.collections import hide_all_utils, isolate_utils, has_visible_utils, get_util_objects_for, get_all_util_objects


class ND_OT_capture_utils(bpy.types.Operator):
    bl_idname = "nd.capture_utils"
    bl_label = "Capture Utils"
    bl_description = """Display and select all utils in the scene.
SHIFT — Only display and select utils for the selected objects"""


    def invoke(self, context, event):
        util_objects = []

        if event.shift and len(context.selected_objects) > 0:
            selected_objects = context.selected_objects.copy()
            util_objects.extend(get_util_objects_for(selected_objects))
        else:
            util_objects.extend(get_all_util_objects())

        isolate_utils(util_objects)

        bpy.ops.object.select_all(action='DESELECT')
        for obj in util_objects:
            obj.select_set(True)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_capture_utils)


def unregister():
    bpy.utils.unregister_class(ND_OT_capture_utils)
