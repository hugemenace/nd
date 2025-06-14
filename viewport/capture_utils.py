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
from .. lib.preferences import get_preferences


class ND_OT_capture_utils(bpy.types.Operator):
    bl_idname = "nd.capture_utils"
    bl_label = "Capture Utils"
    bl_description = """Display and select all utils in the scene.
SHIFT — Only display and select utils for the selected objects
ALT — Additionally add the affected utils to the Utils collection"""


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

        if event.alt:
            utils_collection_name = get_preferences().utils_collection_name
            if not utils_collection_name:
                utils_collection_name = "Utils"

            utils_collection_color = get_preferences().utils_collection_color
            if not utils_collection_color:
                utils_collection_color = "COLOR_02"

            utils_collection = bpy.data.collections.get(utils_collection_name)
            if not utils_collection:
                utils_collection = bpy.data.collections.new(utils_collection_name)
                bpy.context.scene.collection.children.link(utils_collection)

            utils_collection.color_tag = utils_collection_color

            for obj in util_objects:
                if obj.name not in utils_collection.objects:
                    utils_collection.objects.link(obj)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_capture_utils)


def unregister():
    bpy.utils.unregister_class(ND_OT_capture_utils)
