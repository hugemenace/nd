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
import bmesh
from math import radians, degrees
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, set_stream, has_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, add_smooth_by_angle, ensure_tail_mod_consistency
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, objs_are_mesh, app_minor_version
from .. lib.math import round_dec


class ND_OT_bevel_resolution(BaseOperator):
    bl_idname = "nd.bevel_resolution"
    bl_label = "Adjust Bevel Resolution"
    bl_description = """Adjust Bevel resolution of selected objects by some constant offset or a factor"""


    def do_modal(self, context, event):

        if self.key_numeric_input:
            self.segment_change_input_stream = update_stream(self.segment_change_input_stream, event.type)
            self.segment_change = get_stream_value(self.segment_change_input_stream)
            self.dirty = True

        if self.key_reset:
            if has_stream(self.segment_change_input_stream) and self.hard_stream_reset or no_stream(self.segment_change_input_stream):
                self.segment_change = 0
                self.dirty = True
            self.segment_change_input_stream = new_stream()

        if pressed(event, {'E'}):
            for obj in self.selected_objects:
                obj.show_wire = not self.target_object.show_wire
                obj.show_in_front = not self.target_object.show_in_front

        if pressed(event, {'C'}):
            self.change_mode = (self.change_mode + 1) % len(self.change_modes)
            self.segment_change = 0
            self.dirty = True

        if pressed(event, {'A'}):
            self.affect_mode = (self.affect_mode + 1) % len(self.affect_modes)
            self.dirty = True

        if self.change_mode == self.change_modes.index['MULTIPLICATIVE']:
            if pressed(event, {'R'}):
                self.round_mode = (self.round_mode + 1) % len(self.round_modes)
                self.dirty = True

        if self.key_step_up:
            if no_stream(self.distance_input_stream) and self.key_no_modifiers:
                self.distance = round_dec(self.distance + self.step_size)
                self.dirty = True

        if self.key_step_down:
            if no_stream(self.distance_input_stream) and self.key_no_modifiers:
                self.distance = round_dec(self.distance - self.step_size)
                self.dirty = True

        if self.key_confirm:
            self.finish(context)
            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.segment_change_input_stream):
                self.segment_change = max(1, self.segment_change + self.mouse_step)
                self.dirty = True



    def do_invoke(self, context, event):
        self.bevel_mods = []
        self.bevel_segments_prev = []

        self.selected_objects = context.selected_objects

        self.dirty = False

        self.segment_change = 0

        self.change_modes = ['ADDATIVE', 'MULTIPLICATIVE']
        self.change_mode = self.change_modes.index('ADDATIVE')

        self.affect_modes = ['EDGE_BEVELS', 'LAST', 'ALL']
        self.affect_mode = self.affect_modes.index('EDGE_BEVELS')

        self.round_modes = ['ROUND', 'CEIL', 'FLOOR']
        self.round_mode = self.round_modes.index['ROUND']

        self.segment_change_input_stream = new_stream()

        self.target_object = context.active_object
        self.summoned_mod_index = 0

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def capture_mods(self, context):
        self.bevel_mods = []
        self.bevel_segments_prev = []

        for obj in self.selected_objects:
            mods = [mod for mod in obj.modifiers if mod.type == 'BEVEL']

            if mods.len == 0:
                pass

            elif self.affect_mode == self.affect_modes.index('EDGE_BEVELS'):
                mods = [mod for mod in mods if "ND - B" in mod.name]

            elif self.affect_mode == self.affect_modes.index('LAST'):
                mods = [[mods[-1]]]

            else:
                pass

            self.bevel_mods.extend(mods)
            self.bevel_segments_prev.extend([count for count in mods.segments])


    def reset_mods(self, context):

        for mod in self.bevel_mods:
            mod.segments = self.bevel_segments_prev[self.bevel_mods.index[mod]]

    @classmethod
    def poll(cls, context):
        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        return ctx_obj_mode(context) and list_ok(mesh_objects)

    def operate(self, context):

        for mod in self.bevel_mods:
            segment_prev = self.bevel_segments_prev[self.bevel_mods.index[mod]]
            if self.change_mode == self.change_modes.index['MULTIPLICATIVE']:
                if self.segment_change >= 0:
                    segment_new = segment_prev * segment_change
                else:
                    segment_new = segment_prev / - segment_change

                if self.round_mode == self.round_modes.index['ROUND']:
                    mod.segments = round(segment_new)
                elif self.round_mode == self.round_modes.index['CEIL']:
                    mod.segments = ceil(segment_new)
                elif self.round_mode == self.round_modes.index['FLOOR']:
                    mod.segments = floor(segment_new)

            elif self.change_mode == self.change_modes.index['ADDATIVE']:
                mod.segments = max(0, segment_prev - segment_change)

        self.dirty = False


    def finish(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False

        unregister_draw_handler()


    def revert(self, context):
        self.reset_mods(context)

        self.target_object.show_wire = False
        self.target_object.show_in_front = False


def draw_text_callback(self):
    draw_header(self)

    if self.change_mode == self.change_modes.index['MULTIPLICATIVE']:
        if self.segment_change >= 0:
            change_factor = str(self.segment_change)
        else:
            change_factor =  "1 / " + str(-self.segment_change)
        draw_property(
            self,
            "Change Factor: {}".format(change_factor),
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.segment_change_input_stream)

    draw_hint(
        self,
        "Mode [C]: {}".format(self.change_modes[self.change_mode].capitalize()),
        ", ".join([m.capitalize() for m in self.change_modes]))

    draw_hint(
        self,
        "Affect [A]: {}".format(self.affect_modes[self.affect_mode].capitalize()),
        ", ".join([m.capitalize() for m in self.affect_modes]))

    if self.change_mode == self.change_modes.index['MULTIPLICATIVE']:
        draw_hint(
            self,
            "Round [R]: {}".format(self.round_modes[self.round_mode].capitalize()),
            ", ".join([m.capitalize() for m in self.round_modes]))

    draw_hint(
        self,
        "Enhanced Wireframe [E]: {0}".format("Yes" if self.target_object.show_wire else "No"),
        "Display the object's wireframe over solid shading")

def register():
    bpy.utils.register_class(ND_OT_bevel)


def unregister():
    bpy.utils.unregister_class(ND_OT_bevel)
    unregister_draw_handler()
