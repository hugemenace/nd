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
from math import radians, degrees
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, rectify_smooth_by_angle
from .. lib.objects import get_real_active_object
from .. lib.polling import obj_exists, obj_moddable, ctx_obj_mode, ctx_objects_selected


mod_deform = "Deform — ND SD"
mod_summon_list = [mod_deform]


class ND_OT_simple_deform(BaseOperator):
    bl_idname = "nd.simple_deform"
    bl_label = "Simple Deform"
    bl_description = """Twist, bend, taper, or stretch the selected object
CTRL — Remove existing modifiers"""
    bl_options = {'UNDO'}


    def do_modal(self, context, event):
        factor_factor = 0.01 if self.key_shift else 0.1
        angle_factor = 1 if self.key_shift else 10

        if self.key_numeric_input:
            if self.key_no_modifiers:
                if self.is_angular[self.methods[self.current_method]]:
                    self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                    self.angle = get_stream_value(self.angle_input_stream)
                else:
                    self.factor_input_stream = update_stream(self.factor_input_stream, event.type)
                    self.factor = get_stream_value(self.factor_input_stream)

                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if self.is_angular[self.methods[self.current_method]]:
                    if has_stream(self.angle_input_stream) and self.hard_stream_reset or no_stream(self.angle_input_stream):
                        self.angle = 0
                        self.dirty = True
                    self.angle_input_stream = new_stream()
                else:
                    if has_stream(self.factor_input_stream) and self.hard_stream_reset or no_stream(self.factor_input_stream):
                        self.factor = 0
                        self.dirty = True
                    self.factor_input_stream = new_stream()

        if pressed(event, {'M'}):
            self.current_method = (self.current_method + 1) % len(self.methods)
            self.angle_input_stream = new_stream()
            self.factor_input_stream = new_stream()
            self.factor = 0
            self.angle = 0
            self.dirty = True

        if pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        if self.key_step_up:
            if self.key_no_modifiers:
                if no_stream(self.angle_input_stream) and self.is_angular[self.methods[self.current_method]]:
                    self.angle = min(360, self.angle + angle_factor)
                elif no_stream(self.factor_input_stream):
                    self.factor += factor_factor

                self.dirty = True

        if self.key_step_down:
            if self.key_no_modifiers:
                if no_stream(self.angle_input_stream) and self.is_angular[self.methods[self.current_method]]:
                    self.angle = min(360, self.angle - angle_factor)
                elif no_stream(self.factor_input_stream):
                    self.factor -= factor_factor

                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.key_no_modifiers:
                if no_stream(self.angle_input_stream) and self.is_angular[self.methods[self.current_method]]:
                    self.angle = max(-360, min(360, self.angle + self.mouse_value_mag))
                elif no_stream(self.factor_input_stream):
                    self.factor += self.mouse_value

                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND SD')
            return {'FINISHED'}

        self.dirty = False
        self.methods = ['TWIST', 'BEND', 'TAPER', 'STRETCH']
        self.current_method = 0
        self.is_angular = {'TWIST': True, 'BEND': True, 'TAPER': False, 'STRETCH': False}

        self.angle_input_stream = new_stream()
        self.factor_input_stream = new_stream()

        self.target_object = context.active_object

        mods = self.target_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if previous_op:
            self.summon_old_operator(context, mods)
        else:
            self.prepare_new_operator(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        init_axis(self, self.target_object, self.axis)
        register_axis_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and obj_exists(target_object) and obj_moddable(target_object) and ctx_objects_selected(context, 1)


    def prepare_new_operator(self, context):
        self.summoned = False

        self.axis = 0
        self.angle = 0
        self.factor = 0

        self.add_simple_deform_modifier(context)

        rectify_smooth_by_angle(self.target_object)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.deform = mods[mod_deform]

        self.axis_prev = self.axis = {'X': 0, 'Y': 1, 'Z': 2}[self.deform.deform_axis]
        self.method_prev = self.current_method = self.methods.index(self.deform.deform_method)
        self.angle_prev = self.angle = degrees(self.deform.angle)
        self.factor_prev = self.factor = self.deform.factor

        if get_preferences().lock_overlay_parameters_on_recall:
            self.angle_input_stream = set_stream(self.angle)
            self.factor_input_stream = set_stream(self.factor)


    def add_simple_deform_modifier(self, context):
        deform = new_modifier(self.target_object, mod_deform, 'SIMPLE_DEFORM', rectify=True)

        self.deform = deform


    def operate(self, context):
        axis = ['X', 'Y', 'Z'][self.axis]

        self.deform.deform_method = self.methods[self.current_method]
        self.deform.deform_axis = axis

        if self.is_angular[self.methods[self.current_method]]:
            self.deform.angle = radians(self.angle)
        else:
            self.deform.factor = self.factor

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.deform.name)

        if self.summoned:
            axis = ['X', 'Y', 'Z'][self.axis_prev]

            self.deform.deform_method = self.methods[self.method_prev]
            self.deform.deform_axis = axis

            if self.is_angular[self.methods[self.method_prev]]:
                self.deform.angle = radians(self.angle_prev)
            else:
                self.deform.factor = self.factor_prev

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    if self.is_angular[self.methods[self.current_method]]:
        draw_property(
            self,
            "Angle: {0:.2f}°".format(self.angle),
            self.generate_step_hint(10, 1),
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.angle_input_stream)
    else:
        draw_property(
            self,
            "Factor: {0:.2f}".format(self.factor),
            self.generate_step_hint(0.1, 0.01),
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.factor_input_stream)

    draw_hint(
        self,
        "Method [M]: {}".format(self.methods[self.current_method].capitalize()),
        "Deformation method ({})".format(", ".join([m.capitalize() for m in self.methods])))

    draw_hint(
        self,
        "Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Deformation axis (X, Y, Z)")


def register():
    bpy.utils.register_class(ND_OT_simple_deform)


def unregister():
    bpy.utils.unregister_class(ND_OT_simple_deform)
    unregister_draw_handler()
