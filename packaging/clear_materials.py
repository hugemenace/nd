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
from .. lib.polling import ctx_obj_mode, list_ok


class ND_OT_clear_materials(bpy.types.Operator):
    bl_idname = "nd.clear_materials"
    bl_label = "Clear All Materials"
    bl_description = "Remove the material slots from all selected objects"
    bl_options = {'UNDO'}


    def get_valid_objects(self, context):
        return [obj for obj in context.selected_objects if obj.type in {'MESH', 'CURVE'}]


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context)
        return ctx_obj_mode(context) and list_ok(valid_objects)


    def execute(self, context):
        valid_objects = self.get_valid_objects(context)

        for obj in valid_objects:
            obj.data.materials.clear()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_clear_materials)


def unregister():
    bpy.utils.unregister_class(ND_OT_clear_materials)
