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
import inspect
from .. lib.collections import hide_utils_collection, get_utils_layer, isolate_in_utils_collection
from .. lib.objects import get_all_util_objects, get_real_active_object
from .. lib.polling import ctx_obj_mode, ctx_objects_selected
from .. lib.modifiers import move_mod_to_index


class ND_OT_duplicate_utility(bpy.types.Operator):
    bl_idname = "nd.duplicate_utility"
    bl_label = "Duplicate Utility"
    bl_description = """Duplicate the selected utility object and auto-create the associated modifier"""


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and ctx_objects_selected(context, 1)


    def invoke(self, context, event):
        utility_object = context.active_object
        all_scene_objects = [obj for obj in bpy.context.view_layer.objects if obj.type == 'MESH']

        target_object = None
        target_object_mod = None
        target_object_mod_index = 0

        for ref_obj in all_scene_objects:
            if ref_obj == utility_object:
                continue

            ref_mods = list(ref_obj.modifiers)
            for index, ref_mod in enumerate(ref_mods):
                if ref_mod.type == 'BOOLEAN' and ref_mod.object == utility_object:
                    target_object = ref_obj
                    target_object_mod = ref_mod
                    target_object_mod_index = index
                    break

        if target_object_mod is None:
            self.report({'ERROR'}, "This utility object has no associated boolean modifier")
            return {'CANCELLED'}

        new_mod = target_object.modifiers.new(target_object_mod.name, 'BOOLEAN')
        target_object_mod_props = inspect.getmembers(target_object_mod, lambda a: not(inspect.isroutine(a)))
        for prop in target_object_mod_props:
            try:
                setattr(new_mod, prop[0], prop[1])
            except:
                pass

        move_mod_to_index(target_object, new_mod.name, target_object_mod_index+1)

        bpy.ops.object.duplicate_move('INVOKE_DEFAULT')
        utility_object = context.active_object

        target_object.modifiers[new_mod.name].object = utility_object

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_duplicate_utility)


def unregister():
    bpy.utils.unregister_class(ND_OT_duplicate_utility)
