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
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with
from .. lib.polling import ctx_obj_mode, list_ok


class ND_OT_triangulate(bpy.types.Operator):
    bl_idname = "nd.triangulate"
    bl_label = "Triangulate"
    bl_description = """Add a triangulate modifier to the selected objects
CTRL — Remove existing modifiers
ALT — Do not preserve custom normals (Blender <4.2)
SHIFT — Only triangulate ngons (5+ vertices)"""
    bl_options = {'UNDO'}


    def get_valid_objects(self, context):
        return [obj for obj in context.selected_objects if obj.type in {'MESH', 'CURVE'}]


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context)
        return ctx_obj_mode(context) and list_ok(valid_objects)


    def invoke(self, context, event):
        self.preserve_normals = not event.alt
        self.only_ngons = event.shift
        self.remove_mods = event.ctrl

        valid_objects = self.get_valid_objects(context)

        if self.remove_mods:
            remove_modifiers_ending_with(valid_objects, 'Triangulate — ND', False)
            return {'FINISHED'}

        for obj in valid_objects:
            triangulate = new_modifier(obj, 'Triangulate — ND', 'TRIANGULATE', rectify=False)

            if bpy.app.version < (4, 1, 0):
                triangulate.keep_custom_normals = self.preserve_normals

            triangulate.quad_method = 'FIXED' if self.preserve_normals else 'BEAUTY'
            triangulate.min_vertices = 5 if self.only_ngons else 4

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_triangulate)


def unregister():
    bpy.utils.unregister_class(ND_OT_triangulate)
