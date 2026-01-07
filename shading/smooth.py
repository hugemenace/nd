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
from .. lib.modifiers import add_smooth_by_angle, set_smoothing_angle
from .. lib.polling import ctx_obj_mode, list_ok, app_minor_version


class ND_OT_smooth(BaseOperator):
    bl_idname = "nd.smooth"
    bl_label = "Smooth Shading"
    bl_description = "Set and configure object smoothing properties"
    bl_options = {'UNDO'}


    modal_config = {
        'MOVEMENT_PASSTHROUGH': True,
        'ON_CANCEL': lambda cls, context: cls.revert(context),
        'ON_CONFIRM': lambda cls, context: cls.finish(context),
    }


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context)
        return ctx_obj_mode(context) and list_ok(valid_objects)


    def do_modal(self, context, event):
        angle_factor = 1 if self.key_shift else self.base_angle_factor

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                self.angle = get_stream_value(self.angle_input_stream)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.angle_input_stream) and self.hard_stream_reset or no_stream(self.angle_input_stream):
                    self.angle = float(get_preferences().default_smoothing_angle)
                    self.dirty = True
                self.angle_input_stream = new_stream()

        if self.key_step_up:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = min(180, self.angle + angle_factor)
                self.dirty = True

        if self.key_step_down:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = max(0, self.angle - angle_factor)
                self.dirty = True

        if app_minor_version() >= (4, 1) and pressed(event, {'S'}):
            self.ignore_sharpness = not self.ignore_sharpness
            self.dirty = True

        if get_preferences().enable_mouse_values:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = max(0, min(180, self.angle + self.mouse_value_mag))
                self.dirty = True


    def do_invoke(self, context, event):
        self.base_angle_factor = 15
        self.angle = float(get_preferences().default_smoothing_angle)
        self.angle_input_stream = new_stream()
        self.ignore_sharpness = True

        self.valid_objects = self.get_valid_objects(context)

        self.add_smooth_shading(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def get_valid_objects(self, context):
        return [obj for obj in context.selected_objects if obj.type == 'MESH']


    def add_smooth_shading(self, context):
        if app_minor_version() >= (4, 1):
            for obj in self.valid_objects:
                add_smooth_by_angle(context, obj)
            return

        bpy.ops.object.shade_smooth()

        for obj in self.valid_objects:
            obj.data.use_auto_smooth = True


    def operate(self, context):
        if app_minor_version() >= (4, 1):
            for obj in self.valid_objects:
                set_smoothing_angle(context, obj, radians(self.angle), self.ignore_sharpness)
        else:
            for obj in context.selected_objects:
                if obj.type != 'MESH':
                    continue
                obj.data.auto_smooth_angle = radians(self.angle)


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Angle: {self.angle:.2f}°",
        self.generate_step_hint(self.base_angle_factor, 1),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.angle_input_stream)

    if app_minor_version() >= (4, 1):
        draw_hint(
            self,
            f"Ignore Sharpness [S]: {self.yes_no_str(self.ignore_sharpness)}",
            "Ignore edges marked as sharp")


def register():
    bpy.utils.register_class(ND_OT_smooth)


def unregister():
    bpy.utils.unregister_class(ND_OT_smooth)
    unregister_draw_handler()
