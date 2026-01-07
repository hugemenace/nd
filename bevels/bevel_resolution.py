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
# Contributors: Shaddow, Tristo (HM)
# ---

import bpy
from math import ceil, floor
from .. lib.base_operator import BaseOperator
from .. lib.overlay import init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream
from .. lib.polling import ctx_obj_mode, objs_are_mesh


class ND_OT_bevel_resolution(BaseOperator):
    bl_idname = "nd.bevel_resolution"
    bl_label = "Bevel Resolution"
    bl_description = """Adjust all bevel resolutions for the selected objects"""


    key_callbacks = {
        'E': lambda cls, context, event: cls.handle_toggle_enhanced_wireframe(context, event),
        'M': lambda cls, context, event: cls.handle_cycle_mode(context, event),
        'A': lambda cls, context, event: cls.handle_cycle_affect(context, event),
        'R': lambda cls, context, event: cls.handle_cycle_rounding(context, event),
    }

    modal_config = {
        'MOVEMENT_PASSTHROUGH': True,
        'ON_CANCEL': lambda cls, context: cls.revert(context),
        'ON_CONFIRM': lambda cls, context: cls.finish(context),
    }


    @classmethod
    def poll(cls, context):
        return ctx_obj_mode(context) and objs_are_mesh(context.selected_objects)


    def do_modal(self, context, event):
        is_factor_mode = self.change_mode == self.change_modes.index("FACTOR")
        segment_factor = 1 if self.key_shift or is_factor_mode else 2

        if self.key_reset:
            self.segment_change = 0
            self.dirty = True

        if self.key_step_up:
            if self.key_no_modifiers:
                self.segment_change = self.segment_change + segment_factor
                self.dirty = True
            elif self.key_ctrl:
                self.minimum_segments = self.minimum_segments + 1
                self.dirty = True

        if self.key_step_down:
            if self.key_no_modifiers:
                self.segment_change = self.segment_change - segment_factor
                self.dirty = True
            elif self.key_ctrl:
                self.minimum_segments = max(self.minimum_segments - 1, 1)
                self.dirty = True

        if get_preferences().enable_mouse_values:
            if self.key_no_modifiers:
                self.segment_change = self.segment_change + self.mouse_step
                self.dirty = True
            elif self.key_ctrl:
                self.minimum_segments = max(self.minimum_segments + self.mouse_step, 1)
                self.dirty = True


    def do_invoke(self, context, event):
        self.bevel_mods = []
        self.bevel_segments_prev = []

        self.selected_objects = context.selected_objects

        self.segment_change = 0
        self.minimum_segments = 2

        self.change_modes = ['COUNT', 'FACTOR']
        self.change_mode = self.change_modes.index('COUNT')

        self.affect_modes = ['EDGES', 'VERTICES', 'ALL']
        self.affect_mode = self.affect_modes.index('EDGES')

        self.round_modes = ['ROUND', 'CEIL', 'FLOOR']
        self.round_mode = self.round_modes.index('ROUND')

        self.target_object = context.active_object

        self.capture_mods(context)
        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def handle_toggle_enhanced_wireframe(self, context, event):
        for obj in self.selected_objects:
            obj.show_wire = not obj.show_wire
            obj.show_in_front = not obj.show_in_front


    def handle_cycle_mode(self, context, event):
        self.change_mode = (self.change_mode + 1) % len(self.change_modes)
        self.segment_change = 0


    def handle_cycle_affect(self, context, event):
        self.affect_mode = (self.affect_mode + 1) % len(self.affect_modes)
        self.reset_mods()
        self.capture_mods(context)


    def handle_cycle_rounding(self, context, event):
        self.round_mode = (self.round_mode + 1) % len(self.round_modes)


    def capture_mods(self, context):
        self.bevel_mods = []
        self.bevel_segments_prev = []

        affect_type = self.affect_modes[self.affect_mode]

        for obj in self.selected_objects:
            mods = [mod for mod in obj.modifiers if mod.type == 'BEVEL']

            if affect_type != 'ALL':
                mods = [mod for mod in mods if mod.affect == affect_type]

            self.bevel_mods.extend(mods)
            self.bevel_segments_prev.extend([mod.segments for mod in mods])


    def reset_mods(self):
        for i, mod in enumerate(self.bevel_mods):
            mod.segments = self.bevel_segments_prev[i]


    def calc_change_factor(self):
        if self.segment_change >= 0:
            return self.segment_change + 1
        return 1 / (-self.segment_change + 1)


    def format_change_factor(self):
        if self.segment_change >= 0:
            return self.segment_change + 1
        return "1 / {}".format(-self.segment_change + 1)


    rounding_funcs = {
        'ROUND': round,
        'CEIL': ceil,
        'FLOOR': floor
    }

    def operate(self, context):
        rounding_func = self.rounding_funcs[self.round_modes[self.round_mode]]

        for i, mod in enumerate(self.bevel_mods):
            segment_prev = self.bevel_segments_prev[i]

            if self.change_mode == self.change_modes.index('FACTOR'):
                segment_new = segment_prev * self.calc_change_factor()
                mod.segments = max(rounding_func(segment_new), self.minimum_segments)
            elif self.change_mode == self.change_modes.index('COUNT'):
                mod.segments = max(segment_prev + self.segment_change, self.minimum_segments)


    def finish(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False

        unregister_draw_handler()


    def revert(self, context):
        self.reset_mods()

        self.target_object.show_wire = False
        self.target_object.show_in_front = False

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    is_factor_mode = self.change_mode == self.change_modes.index('FACTOR')

    if is_factor_mode:
        draw_property(
            self,
            f"Factor: {self.format_change_factor()}",
            self.generate_step_hint(1),
            active=self.key_no_modifiers,
            mouse_value=True)
    else:
        draw_property(
            self,
            f"Offset: {self.segment_change}",
            self.generate_step_hint(2, 1),
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True)

    draw_property(
            self,
            f"Minimum: {self.minimum_segments}",
            self.generate_key_hint("Ctrl", self.generate_step_hint(1)),
            active=self.key_ctrl,
            mouse_value=True)

    draw_hint(
        self,
        f"Mode [M]: {self.change_modes[self.change_mode].capitalize()}",
        self.list_options_str(self.change_modes))

    draw_hint(
        self,
        f"Affect [A]: {self.affect_modes[self.affect_mode].capitalize()}",
        self.list_options_str(self.affect_modes))

    if is_factor_mode:
        draw_hint(
            self,
            f"Rounding [R]: {self.round_modes[self.round_mode].capitalize()}",
            self.list_options_str(self.round_modes))

    draw_hint(
        self,
        f"Enhanced Wireframe [E]: {self.yes_no_str(self.target_object.show_wire)}",
        "Display the object's wireframe over solid shading")


def register():
    bpy.utils.register_class(ND_OT_bevel_resolution)


def unregister():
    bpy.utils.unregister_class(ND_OT_bevel_resolution)
    unregister_draw_handler()
