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
from .. lib.preferences import get_preferences
from .. lib.modifiers import new_modifier, remove_problematic_boolean_mods, ensure_tail_mod_consistency
from .. lib.objects import get_real_active_object, configure_object_as_util, get_objects_in_hierarchy
from .. lib.polling import obj_exists, objs_are_mesh, ctx_objects_selected, ctx_obj_mode, app_minor_version


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
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and obj_exists(target_object) and objs_are_mesh(context.selected_objects) and ctx_objects_selected(context, 2)


    def execute(self, context):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        solver = 'FAST' if get_preferences().use_fast_booleans else 'EXACT'
        if app_minor_version() >= (5, 0) and solver == 'FAST':
            solver = 'FLOAT'

        target_obj = context.active_object

        a, b = context.selected_objects
        reference_obj = a if a.name != target_obj.name else b

        boolean = new_modifier(target_obj, " — ".join([self.mode.capitalize(), "ND Bool"]), 'BOOLEAN', rectify=True)
        boolean.operation = self.mode
        boolean.object = reference_obj
        boolean.solver = solver
        if app_minor_version() >= (4, 0):
            boolean.material_mode = 'TRANSFER'

        if not self.protect_reference_obj:
            configure_object_as_util(reference_obj, util=True)
            reference_obj.data.name = reference_obj.name

            if not self.do_not_clean_mesh:
                remove_problematic_boolean_mods(reference_obj)

        # If the reference object doesn't have a parent, or its parent is in the hierarchy of the target object,
        # we can safely set the target object as the parent of the reference object.
        objects_in_hierarchy = get_objects_in_hierarchy(target_obj)
        if not reference_obj.parent or reference_obj.parent in objects_in_hierarchy:
            if reference_obj.parent:
                # Clear the parent first and keep the transform
                matrix_world = reference_obj.matrix_world.copy()
                reference_obj.parent = None
                reference_obj.matrix_world = matrix_world
            # Set the target object as the parent of the reference object
            reference_obj.parent = target_obj
            reference_obj.matrix_parent_inverse = target_obj.matrix_world.inverted()

        bpy.ops.object.select_all(action='DESELECT')
        reference_obj.select_set(True)
        bpy.context.view_layer.objects.active = reference_obj

        ensure_tail_mod_consistency(target_obj)

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
