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
from math import radians
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, rectify_smooth_by_angle
from .. lib.polling import ctx_obj_mode, list_ok


class ND_OT_decimate(bpy.types.Operator):
    bl_idname = "nd.decimate"
    bl_label = "Decimate"
    bl_description = """Add a decimate modifier to the selected objects
CTRL — Remove existing modifiers"""
    bl_options = {'UNDO'}


    def get_valid_objects(self, context):
        return [obj for obj in context.selected_objects if obj.type == 'MESH']


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context)
        return ctx_obj_mode(context) and list_ok(valid_objects)


    def invoke(self, context, event):
        valid_objects = self.get_valid_objects(context)

        if event.ctrl:
            remove_modifiers_ending_with(valid_objects, ' — ND SD')
            return {'FINISHED'}

        for obj in valid_objects:
            decimate = new_modifier(obj, 'Decimate — ND SD', 'DECIMATE', rectify=True)
            decimate.decimate_type = 'DISSOLVE'
            decimate.angle_limit = radians(1)

            rectify_smooth_by_angle(obj)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_decimate)


def unregister():
    bpy.utils.unregister_class(ND_OT_decimate)
