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


class ND_OT_name_sync(bpy.types.Operator):
    bl_idname = "nd.name_sync"
    bl_label = "Name & Data Sync"
    bl_description = "Updates all data names to match their corresponding object names"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) >= 1 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        for obj in context.selected_objects:
            obj.data.name = obj.name

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_name_sync)


def unregister():
    bpy.utils.unregister_class(ND_OT_name_sync)
