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
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import add_smooth_by_angle, set_smoothing_angle


class ND_OT_smooth(bpy.types.Operator):
    bl_idname = "nd.smooth"
    bl_label = "Smooth Shading"
    bl_description = "Set and configure object smoothing properties"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        angle_factor = 1 if self.key_shift else self.base_angle_factor

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        elif self.key_toggle_pin_overlay:
            toggle_pin_overlay(self, event)

        elif self.operator_passthrough:
            update_overlay(self, context, event)

            return {'PASS_THROUGH'}

        elif self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        elif self.key_numeric_input:
            if self.key_no_modifiers:
                self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                self.angle = get_stream_value(self.angle_input_stream)
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.angle_input_stream = new_stream()
                self.angle = float(get_preferences().default_smoothing_angle)
                self.dirty = True

        elif self.key_step_up:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = min(180, self.angle + angle_factor)
                self.dirty = True

        elif self.key_step_down:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = max(0, self.angle - angle_factor)
                self.dirty = True

        elif bpy.app.version >= (4, 1, 0) and pressed(event, {'S'}):
            self.ignore_sharpness = not self.ignore_sharpness
            self.dirty = True

        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = max(0, min(180, self.angle + self.mouse_value_mag))
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_angle_factor = 15
        self.angle = float(get_preferences().default_smoothing_angle)
        self.angle_input_stream = new_stream()
        self.ignore_sharpness = True

        self.mods = []

        self.add_smooth_shading(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) >= 1 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def add_smooth_shading(self, context):
        if bpy.app.version >= (4, 1, 0):
            for object in context.selected_objects:
                smooth_mod = add_smooth_by_angle(object)

                # If the object has a WN modifier, place the smoothig mod before it.
                object_mods = list(object.modifiers)
                for index, mod in enumerate(object_mods):
                    if mod.name == "Weighted Normal — ND WN":
                        with bpy.context.temp_override(object=object):
                            bpy.ops.object.modifier_move_to_index(modifier=smooth_mod.name, index=index-1)
                        break

                self.mods.append((object, smooth_mod))
            return

        bpy.ops.object.shade_smooth()

        for object in context.selected_objects:
            object.data.use_auto_smooth = True


    def operate(self, context):
        if bpy.app.version >= (4, 1, 0):
            for object, mod in self.mods:
                set_smoothing_angle(object, mod, radians(self.angle), self.ignore_sharpness)
        else:
            for object in context.selected_objects:
                object.data.auto_smooth_angle = radians(self.angle)

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Angle: {0:.2f}°".format(self.angle),
        "(±{0:.0f})  |  Shift + (±1)".format(self.base_angle_factor),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.angle_input_stream)

    if bpy.app.version >= (4, 1, 0):
        draw_hint(
            self,
            "Ignore Sharpness [S]: {}".format("Yes" if self.ignore_sharpness else "No"),
            "Ignore sharpness when smoothing")


def register():
    bpy.utils.register_class(ND_OT_smooth)


def unregister():
    bpy.utils.unregister_class(ND_OT_smooth)
    unregister_draw_handler()
