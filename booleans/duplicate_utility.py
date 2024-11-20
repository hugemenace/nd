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
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, ctx_objects_selected
from .. lib.modifiers import move_mod_to_index


class ND_OT_duplicate_utility(bpy.types.Operator):
    bl_idname = "nd.duplicate_utility"
    bl_label = "Duplicate Utility"
    bl_description = """Duplicate the selected utility object and the associated modifier(s)
SHIFT — Do not duplicate intersect target objects
ALT — Create a linked duplicate"""


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and ctx_objects_selected(context, 1)


    def invoke(self, context, event):
        self.ignore_intersects = event.shift
        self.linked_duplicate = event.alt

        old_utility_object = context.active_object

        if self.linked_duplicate:
            bpy.ops.object.duplicate_move_linked()
        else:
            bpy.ops.object.duplicate()

        new_utility_object = context.active_object

        targets = []
        all_scene_objects = [obj for obj in bpy.context.view_layer.objects if obj.type == 'MESH']

        # Get all objects with boolean modifiers that reference the utility object
        for obj in all_scene_objects:
            if obj == old_utility_object:
                continue

            obj_mods = list(obj.modifiers)
            applicable_mods = []
            for index, mod in enumerate(obj_mods):
                if mod.type == 'BOOLEAN' and mod.object == old_utility_object:
                    applicable_mods.append((mod, index))

            if len(applicable_mods) > 0:
                targets.append((obj, applicable_mods))

        for obj, applicable_mods in targets:
            for old_mod, old_mod_index in applicable_mods:
                # If the intersect target is not being ignored, duplicate the intersect target object
                # and set it as the new object for the boolean modifier.
                if not self.ignore_intersects and old_mod.operation == 'INTERSECT':
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                    bpy.ops.object.duplicate()
                    obj = context.active_object

                # Create a new boolean modifier with the same properties as the old one.
                new_mod = obj.modifiers.new(old_mod.name, 'BOOLEAN')
                old_mod_props = inspect.getmembers(old_mod, lambda a: not(inspect.isroutine(a)))
                for prop in old_mod_props:
                    try:
                        setattr(new_mod, prop[0], prop[1])
                    except:
                        pass

                new_mod.object = new_utility_object
                move_mod_to_index(obj, new_mod.name, old_mod_index+1)

                if not self.ignore_intersects and old_mod.operation == 'INTERSECT':
                    bpy.ops.object.modifier_remove(modifier=old_mod.name)

        bpy.ops.object.select_all(action='DESELECT')
        new_utility_object.select_set(True)
        context.view_layer.objects.active = new_utility_object
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_duplicate_utility)


def unregister():
    bpy.utils.unregister_class(ND_OT_duplicate_utility)
