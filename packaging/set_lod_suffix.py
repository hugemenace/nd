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
from .. lib.polling import ctx_obj_mode, ctx_min_objects_selected


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
        return ctx_obj_mode(context) and ctx_min_objects_selected(context, 1)


    def execute(self, context):
        for obj in context.selected_objects:
            new_name = obj.name
            has_prexisting_lod = False

            if "_low" in obj.name or "_high" in obj.name:
                # Replace "_low" or "_high" with the self.mode value
                new_name = obj.name.replace("_low", f"_{self.mode.lower()}").replace("_high", f"_{self.mode.lower()}")
                has_prexisting_lod = True

            # Remove Blender's .001, .002, etc naming convention
            new_name = re.sub(r"(.+?)(?:\.[0-9]+)+$", r"\1", new_name)

            # Remove ZenSet's _1, _2, etc naming convention
            new_name = re.sub(r"(.+?)(?:_[0-9]+)+$", r"\1", new_name)

            # Append the new LOD suffix if there wasn't a pre-existing one
            if not has_prexisting_lod:
                new_name += f"_{self.mode.lower()}"

            obj.name = new_name

            if obj.data:
                obj.data.name = new_name

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_set_lod_suffix)


def unregister():
    bpy.utils.unregister_class(ND_OT_set_lod_suffix)
