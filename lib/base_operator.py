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
from . preferences import get_scene_unit_factor, get_scene_unit_suffix, get_scene_unit_scale, get_preferences
from .. lib.overlay import update_overlay, toggle_pin_overlay, toggle_operator_passthrough
from .. lib.events import capture_modifier_keys


class BaseOperator(bpy.types.Operator):
    bl_options = {'UNDO'}


    def generate_step_hint(self, regular, precise = None):
        if not precise:
            return f"(±{regular})"

        return f"(±{regular}  /  SHIFT ±{precise})"


    def generate_key_hint(self, key, hint):
        return f"{key}  —  {hint}"


    def operate(self, context):
        pass


    def invoke(self, context, event):
        self.unit_factor = get_scene_unit_factor()
        self.unit_suffix = get_scene_unit_suffix()
        self.unit_scale  = get_scene_unit_scale()

        self.unit_scaled_factor = self.unit_factor / self.unit_scale
        self.display_unit_scale = self.unit_scale / self.unit_factor

        unit_increment_size = get_preferences().unit_increment_size
        self.unit_step_hint = self.generate_step_hint(f"{(self.unit_scale * unit_increment_size):.2f}{self.unit_suffix}", f"{(self.unit_scale * 0.1 * unit_increment_size):.2f}{self.unit_suffix}")

        self.extend_mouse_values = get_preferences().enable_mouse_values and get_preferences().extend_mouse_values
        self.hard_stream_reset = get_preferences().overlay_reset_key_behaviour == 'RESET'

        return self.do_invoke(context, event)


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        self.step_size = ((0.1 if self.key_shift else 1) * self.unit_factor) * get_preferences().unit_increment_size

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        if self.key_toggle_pin_overlay:
            toggle_pin_overlay(self, event)

        if self.operator_passthrough:
            update_overlay(self, context, event)

            return {'PASS_THROUGH'}

        if self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        # Subclass hook-in
        override_return = self.do_modal(context, event)

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return override_return if override_return else {'RUNNING_MODAL'}


    def yes_no_str(self, value):
        return "Yes" if value else "No"


    def list_options_str(self, options, capitalize=True):
        def fmt(opt):
            return str(opt).capitalize() if capitalize else str(opt)

        options_list = list(options)
        options_str = ""
        if len(options_list) == 1:
            options_str = fmt(options_list[0])
        elif len(options_list) == 2:
            options_str = " or ".join([fmt(opt) for opt in options_list])
        else:
            options_str = ", ".join([fmt(opt) for opt in options_list[:-1]]) + ", or " + fmt(options_list[-1])

        return f"Options: {options_str}"
