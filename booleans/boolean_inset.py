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
import bmesh
from math import radians
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream
from .. lib.modifiers import new_modifier, remove_problematic_boolean_mods, ensure_tail_mod_consistency
from .. lib.objects import get_real_active_object, set_object_util_visibility
from .. lib.polling import obj_exists, objs_are_mesh, ctx_objects_selected, ctx_obj_mode, app_minor_version
from .. lib.math import round_dec


class ND_OT_bool_inset(BaseOperator):
    bl_idname = "nd.bool_inset"
    bl_label = "Inset/Outset"
    bl_description = "Perform a boolean operation on the selected objects"


    def do_modal(self, context, event):
        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.thickness_input_stream = update_stream(self.thickness_input_stream, event.type)
                self.thickness = get_stream_value(self.thickness_input_stream, 0.001)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.thickness_input_stream) and self.hard_stream_reset or no_stream(self.thickness_input_stream):
                    self.thickness = 0
                    self.dirty = True
                self.thickness_input_stream = new_stream()

        if pressed(event, {'M'}):
            self.outset = not self.outset
            self.dirty = True

        if self.key_step_up:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
                self.thickness = round_dec(self.thickness + self.step_size)
                self.dirty = True

        if self.key_step_down:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
                self.thickness = max(0, round_dec(self.thickness - self.step_size))
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
                self.thickness = max(0, self.thickness + self.mouse_value)
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        self.dirty = False
        self.base_thickness_factor = 0.01

        self.thickness = 0.02
        self.outset = False

        self.thickness_input_stream = new_stream()

        solver = 'FAST' if get_preferences().use_fast_booleans else 'EXACT'

        a, b = context.selected_objects
        self.reference_obj = a if a.name != context.active_object.name else b

        self.target_obj = context.active_object

        self.intersecting_obj = context.active_object.copy()
        self.intersecting_obj.data = context.active_object.data.copy()
        self.intersecting_obj.animation_data_clear()
        context.collection.objects.link(self.intersecting_obj)

        self.boolean_diff = new_modifier(self.target_obj, "Inset/Outset — ND Bool", 'BOOLEAN', rectify=True)
        self.boolean_diff.operation = 'UNION' if self.outset else 'DIFFERENCE'
        self.boolean_diff.object = self.intersecting_obj
        self.boolean_diff.solver = solver
        if app_minor_version() >= (4, 0):
            self.boolean_diff.material_mode = 'TRANSFER'

        self.solidify = new_modifier(self.intersecting_obj, "Thickness — ND Bool", 'SOLIDIFY', rectify=False)
        self.solidify.use_even_offset = True
        self.solidify.offset = 0

        self.boolean_isect = new_modifier(self.intersecting_obj, "Intersection — ND Bool", 'BOOLEAN', rectify=False)
        self.boolean_isect.operation = 'INTERSECT'
        self.boolean_isect.object = self.reference_obj
        self.boolean_isect.solver = solver
        if app_minor_version() >= (4, 0):
            self.boolean_isect.material_mode = 'TRANSFER'
        self.boolean_isect.show_expanded = False

        self.reference_obj_name_prev = self.reference_obj.name

        set_object_util_visibility(self.reference_obj, hidden=True)
        self.reference_obj.data.name = self.reference_obj.name
        self.reference_obj.hide_set(True)

        remove_problematic_boolean_mods(self.reference_obj)

        set_object_util_visibility(self.intersecting_obj, hidden=True)
        self.intersecting_obj.data.name = self.intersecting_obj.name

        remove_problematic_boolean_mods(self.intersecting_obj)

        if not self.reference_obj.parent:
            self.reference_obj.parent = self.target_obj
            self.reference_obj.matrix_parent_inverse = self.target_obj.matrix_world.inverted()

        self.intersecting_obj.parent = self.target_obj
        self.intersecting_obj.matrix_parent_inverse = self.target_obj.matrix_world.inverted()

        bpy.ops.object.select_all(action='DESELECT')

        ensure_tail_mod_consistency(self.target_obj)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and obj_exists(target_object) and objs_are_mesh(context.selected_objects) and ctx_objects_selected(context, 2)


    def operate(self, context):
        self.solidify.thickness = self.thickness
        self.boolean_diff.operation = 'UNION' if self.outset else 'DIFFERENCE'

        self.dirty = False


    def finish(self, context):
        self.reference_obj.hide_set(False)

        bpy.ops.object.select_all(action='DESELECT')
        self.reference_obj.select_set(True)
        self.intersecting_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_obj

        unregister_draw_handler()


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.boolean_diff.name)
        bpy.data.meshes.remove(self.intersecting_obj.data, do_unlink=True)

        set_object_util_visibility(self.reference_obj, hidden=False)
        self.reference_obj.name = self.reference_obj_name_prev
        self.reference_obj.data.name = self.reference_obj_name_prev
        self.reference_obj.parent = None
        self.reference_obj.hide_set(False)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    display_unit_scale = self.unit_scale / self.unit_factor

    draw_property(
        self,
        f"Thickness: {(self.thickness * display_unit_scale):.2f}{self.unit_suffix}",
        self.unit_step_hint,
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.thickness_input_stream)

    draw_hint(
        self,
        "Mode [M]: {0}".format('Outset' if self.outset else 'Inset'),
        "Create an Inset or Outset")


def register():
    bpy.utils.register_class(ND_OT_bool_inset)


def unregister():
    bpy.utils.unregister_class(ND_OT_bool_inset)
    unregister_draw_handler()
