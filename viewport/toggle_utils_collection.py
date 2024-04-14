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
from .. lib.collections import hide_utils_collection, get_utils_layer, isolate_in_utils_collection


class ND_OT_toggle_utils_collection(bpy.types.Operator):
    bl_idname = "nd.toggle_utils_collection"
    bl_label = "Utils Visibility"
    bl_description = """Toggle utils collection visibility
SHIFT — Display all utils for the selected objects"""


    def execute(self, context):
        data = get_utils_layer()
        if data is not None:
            layer, collection = data
            hide_utils_collection(not layer.hide_viewport)

        return {'FINISHED'}

    
    def invoke(self, context, event):
        if event.shift and len(context.selected_objects) > 0:
            data = get_utils_layer()
            if data is None:
                return {'FINISHED'}

            layer, collection = data
            visible = not layer.hide_viewport

            if not visible:
                hide_utils_collection(visible)

            all_util_objects = set(())
            for obj in context.selected_objects:
                local_util_objects = [mod.object for mod in obj.modifiers if mod.type == 'BOOLEAN' and mod.object]
                all_util_objects.update(local_util_objects)

            isolate_in_utils_collection(all_util_objects)
            
            return {'FINISHED'}

        return self.execute(context)


def register():
    bpy.utils.register_class(ND_OT_toggle_utils_collection)


def unregister():
    bpy.utils.unregister_class(ND_OT_toggle_utils_collection)
