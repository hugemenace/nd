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
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, rectify_smooth_by_angle


class ND_OT_weld(bpy.types.Operator):
    bl_idname = "nd.weld"
    bl_label = "Weld"
    bl_description = """Add a weld modifier to the selected objects
CTRL — Remove existing modifiers"""
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) > 0:
            return all(obj.type == 'MESH' for obj in context.selected_objects)


    def invoke(self, context, event):
        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND SW')
            return {'FINISHED'}

        for obj in context.selected_objects:
            weld = new_modifier(obj, 'Weld — ND SW', 'WELD', rectify=True)
            weld.merge_threshold = 0.001

            rectify_smooth_by_angle(obj)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_weld)


def unregister():
    bpy.utils.unregister_class(ND_OT_weld)
