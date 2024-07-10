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
from .. lib.polling import is_object_mode, list_gt


class ND_OT_name_sync(bpy.types.Operator):
    bl_idname = "nd.name_sync"
    bl_label = "Name & Data Sync"
    bl_description = "Updates all data names to match their corresponding object names"
    bl_options = {'UNDO'}


    def get_valid_objects(self, context):
        return [obj for obj in context.selected_objects if obj.data]


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context)
        return is_object_mode(context) and list_gt(valid_objects, 0)


    def execute(self, context):
        valid_objects = self.get_valid_objects(context)

        for obj in valid_objects:
            obj.data.name = obj.name

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_name_sync)


def unregister():
    bpy.utils.unregister_class(ND_OT_name_sync)
