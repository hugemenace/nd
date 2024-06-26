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
import re


class ND_OT_set_lod_suffix(bpy.types.Operator):
    bl_idname = "nd.set_lod_suffix"
    bl_label = "Set LOD Suffix"
    bl_description = "Suffixes all selected objects with the specified LOD"
    bl_options = {'UNDO'}


    mode: bpy.props.EnumProperty(items=[
        ('HIGH', 'High', 'Updates the selected object names with a _high suffix'),
        ('LOW', 'Low', 'Updates the selected object names with a _low suffix'),
    ], name="Suffix", default='HIGH')


    @classmethod
    def poll(cls, context):
        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        return context.mode == 'OBJECT' and len(mesh_objects) > 0


    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            # Remove Blender's .001, .002, etc naming convention
            old_name = re.sub(r"(.+?)(?:\.[0-9]+)+$", r"\1", obj.name)

            # Remove ZenSet's _1, _2, etc naming convention
            old_name = re.sub(r"(.+?)(?:_[0-9]+)+$", r"\1", old_name)

            name_segments = old_name.split("_")

            # Remove existing _high / _low suffixes.
            if name_segments[-1].lower() in ['high', 'low']:
                name_segments.pop()

            name_segments.append(self.mode.lower())
            new_name = "_".join(name_segments)

            obj.name = new_name
            obj.data.name = new_name

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_set_lod_suffix)


def unregister():
    bpy.utils.unregister_class(ND_OT_set_lod_suffix)
