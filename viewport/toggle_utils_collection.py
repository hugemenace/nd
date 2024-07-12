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
from .. lib.collections import hide_utils_collection, get_utils_layer, isolate_in_utils_collection, has_visible_utils
from .. lib.objects import get_all_util_objects


keys = []


class ND_OT_toggle_utils_collection(bpy.types.Operator):
    bl_idname = "nd.toggle_utils_collection"
    bl_label = "Utils Visibility"
    bl_description = """Toggle utils collection visibility
SHIFT — Display all utils for the selected objects"""


    mode: bpy.props.EnumProperty(items=[
        ('DYNAMIC', 'Dynamic', 'Run the operator with alt modes enabled'),
        ('RESTRICTED', 'Restricted', 'Run the operator with alt modes disabled'),
    ], name="Mode", default='DYNAMIC')


    def execute(self, context):
        data = get_utils_layer()
        if data is not None:
            hide_utils_collection(has_visible_utils())

        return {'FINISHED'}


    def invoke(self, context, event):
        isolated_object_mode = event.shift and not self.mode == 'RESTRICTED'

        if isolated_object_mode and len(context.selected_objects) > 0:
            data = get_utils_layer()
            if data is None:
                return {'FINISHED'}

            selected_objects = context.selected_objects.copy()

            util_objects = get_all_util_objects(selected_objects)
            util_objects.extend(selected_objects)

            hide_utils_collection(True)
            isolate_in_utils_collection(util_objects)

            return {'FINISHED'}

        return self.execute(context)


def register():
    bpy.utils.register_class(ND_OT_toggle_utils_collection)

    for mapping in [('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])

        entry = keymap.keymap_items.new("nd.toggle_utils_collection", 'T', 'PRESS', shift=True)
        entry.properties.mode = 'RESTRICTED'
        keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_OT_toggle_utils_collection)
