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
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, ensure_tail_mod_consistency
from .. lib.polling import ctx_obj_mode, list_ok, app_minor_version


class ND_OT_weighted_normal(bpy.types.Operator):
    bl_idname = "nd.wn"
    bl_label = "Weighted Normals"
    bl_description = """Add a weighted normal modifier to the selected objects
SHIFT — Don't keep sharp edges
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
            remove_modifiers_ending_with(valid_objects, ' — ND WN')
            return {'FINISHED'}

        self.keep_sharp = not event.shift

        for obj in valid_objects:
            if any(' — ND WN' in mod.name for mod in obj.modifiers):
                continue

            mod = new_modifier(obj, 'Weighted Normal — ND WN', 'WEIGHTED_NORMAL', rectify=False)
            mod.keep_sharp = self.keep_sharp
            mod.weight = 100
            mod.use_face_influence = True

            if app_minor_version() > (4, 1):
                mod.use_pin_to_last = True

            ensure_tail_mod_consistency(obj, force=True)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_weighted_normal)


def unregister():
    bpy.utils.unregister_class(ND_OT_weighted_normal)
