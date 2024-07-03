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
from .. lib.collections import move_to_utils_collection, isolate_in_utils_collection
from .. lib.preferences import get_preferences
from .. lib.modifiers import new_modifier, remove_problematic_boolean_mods, rectify_smooth_by_angle


keys = []


class ND_OT_bool_vanilla(bpy.types.Operator):
    bl_idname = "nd.bool_vanilla"
    bl_label = "Boolean"
    bl_description = """Perform a boolean operation on the selected objects
SHIFT — Protect the reference object (do not convert into utility)
ALT — Do not clean the reference object's mesh"""
    bl_options = {'UNDO'}


    mode: bpy.props.EnumProperty(items=[
        ('DIFFERENCE', 'Difference', 'Perform a difference operation'),
        ('UNION', 'Union', 'Perform a union operation'),
        ('INTERSECT', 'Intersect', 'Perform an intersect operation'),
    ], name="Mode", default='DIFFERENCE')


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and context.active_object is not None:
            return len(context.selected_objects) == 2 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        solver = 'FAST' if get_preferences().use_fast_booleans else 'EXACT'

        target_obj = context.active_object

        a, b = context.selected_objects
        reference_obj = a if a.name != target_obj.name else b

        boolean = new_modifier(target_obj, " — ".join([self.mode.capitalize(), "ND Bool"]), 'BOOLEAN', rectify=True)
        boolean.operation = self.mode
        boolean.object = reference_obj
        boolean.solver = solver

        if not self.protect_reference_obj:
            reference_obj.display_type = 'WIRE'
            reference_obj.hide_render = True
            reference_obj.name = " — ".join(['Bool', reference_obj.name])
            reference_obj.data.name = reference_obj.name

            if not self.do_not_clean_mesh:
                remove_problematic_boolean_mods(reference_obj)

        reference_obj.parent = target_obj
        reference_obj.matrix_parent_inverse = target_obj.matrix_world.inverted()

        if not self.protect_reference_obj:
            move_to_utils_collection(reference_obj)
            isolate_in_utils_collection([reference_obj])

        bpy.ops.object.select_all(action='DESELECT')
        reference_obj.select_set(True)
        bpy.context.view_layer.objects.active = reference_obj

        rectify_smooth_by_angle(target_obj)

        return {'FINISHED'}


    def invoke(self, context, event):
        self.protect_reference_obj = event.shift
        self.do_not_clean_mesh = event.alt

        return self.execute(context)


def register():
    bpy.utils.register_class(ND_OT_bool_vanilla)

    for mapping in [('Mesh', 'EMPTY'), ('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])

        entry = keymap.keymap_items.new("nd.bool_vanilla", 'NUMPAD_MINUS', 'PRESS', ctrl=True)
        entry.properties.mode = "DIFFERENCE"
        keys.append((keymap, entry))

        entry = keymap.keymap_items.new("nd.bool_vanilla", 'NUMPAD_PLUS', 'PRESS', ctrl=True)
        entry.properties.mode = "UNION"
        keys.append((keymap, entry))

        entry = keymap.keymap_items.new("nd.bool_vanilla", 'NUMPAD_ASTERIX', 'PRESS', ctrl=True)
        entry.properties.mode = "INTERSECT"
        keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_OT_bool_vanilla)
