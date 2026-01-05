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
from .. lib.polling import ctx_obj_mode, list_ok



class ND_OT_bevel_resolution(BaseOperator):
    bl_idname = "nd.bevel_resolution"
    bl_label = "Bevel Resolution"
    bl_description = """Adjust all bevel resolutions for the selected objects"""


    def do_modal(self, context, event):
        segment_factor = 1 if self.key_shift or self.change_mode == self.change_modes.index("FACTOR") else 2

        if self.key_reset:
            self.segment_change = 0
            self.dirty = True

        if pressed(event, {'E'}):
            for obj in self.selected_objects:
                obj.show_wire = not obj.show_wire
                obj.show_in_front = not obj.show_in_front

        if pressed(event, {'C'}):
            self.change_mode = (self.change_mode + 1) % len(self.change_modes)
            self.segment_change = 0
            self.dirty = True

        if pressed(event, {'A'}):
            self.affect_mode = (self.affect_mode + 1) % len(self.affect_modes)
            self.reset_mods()
            self.capture_mods(context)
            self.dirty = True

        if self.change_mode == self.change_modes.index('FACTOR'):
            if pressed(event, {'R'}):
                self.round_mode = (self.round_mode + 1) % len(self.round_modes)
                self.dirty = True

        if self.key_step_up:
            if self.key_no_modifiers:
                self.segment_change = self.segment_change + segment_factor
                self.dirty = True
            elif self.extend_mouse_values:
                self.segment_change = self.segment_change + segment_factor
                self.dirty = True
            elif self.key_ctrl:
                self.minimum_segments = self.minimum_segments + 1
                self.dirty = True

        if self.key_step_down:
            if self.key_no_modifiers:
                self.segment_change = self.segment_change - segment_factor
                self.dirty = True
            elif self.extend_mouse_values:
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
                

                
        if self.change_mode == self.change_modes.index('FACTOR'):
            self.segment_change = max( -9, min(9, self.segment_change))

        if self.key_confirm:
            self.finish(context)
            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}


    def do_invoke(self, context, event):
        self.bevel_mods = []
        self.bevel_segments_prev = []

        self.selected_objects = context.selected_objects

        self.dirty = False

        self.segment_change = 0
        self.minimum_segments = 2

        self.change_modes = ['COUNT', 'FACTOR']
        self.change_mode = self.change_modes.index('COUNT')

        self.affect_modes = ['EDGE BEVELS', 'VERTEX BEVELS', 'ALL']
        self.affect_mode = self.affect_modes.index('EDGE BEVELS')

        self.round_modes = ['ROUND', 'CEIL', 'FLOOR']
        self.round_mode = self.round_modes.index('ROUND')

        self.segment_change_input_stream = new_stream()

        self.target_object = context.active_object
        
        self.capture_mods(context)

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

            if len(mods) == 0:
                pass

            elif self.affect_mode == self.affect_modes.index('EDGE BEVELS'):
                mods = [mod for mod in mods if mod.affect == 'EDGES']
                
            elif self.affect_mode == self.affect_modes.index('VERTEX BEVELS'):
                mods = [mod for mod in mods if mod.affect == 'VERTICES']

            else:
                pass

            self.bevel_mods.extend(mods)
            self.bevel_segments_prev.extend([mod.segments for mod in mods])


    def reset_mods(self):
        for mod in self.bevel_mods:
            mod.segments = self.bevel_segments_prev[self.bevel_mods.index(mod)]
            

    def calc_change_factor(self):
        if self.segment_change >= 0:
            return self.segment_change +1
        else:
            return 1 / (-self.segment_change +1)
        
        
    def format_change_factor(self):
        if self.segment_change >= 0:
            return self.segment_change +1
        else:
            return "1 / {}".format(-self.segment_change +1)


    @classmethod
    def poll(cls, context):
        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        return ctx_obj_mode(context) and list_ok(mesh_objects)


    def operate(self, context):
        print(self.change_mode + self.change_modes.index('COUNT'))
        for mod in self.bevel_mods:
            
            segment_prev = self.bevel_segments_prev[self.bevel_mods.index((mod))]
            if self.change_mode == self.change_modes.index('FACTOR'):
                segment_new = segment_prev * self.calc_change_factor()
                
                if self.round_mode == self.round_modes.index('ROUND'):
                    mod.segments = max(round(segment_new), self.minimum_segments)
                elif self.round_mode == self.round_modes.index('CEIL'):
                    mod.segments = max(ceil(segment_new), self.minimum_segments)
                elif self.round_mode == self.round_modes.index('FLOOR'):
                    mod.segments = max(floor(segment_new), self.minimum_segments)
                    
            elif self.change_mode == self.change_modes.index('COUNT'):
                mod.segments = max(segment_prev + self.segment_change, self.minimum_segments)

        self.dirty = False


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

    if self.change_mode == self.change_modes.index('FACTOR'):
        draw_property(
            self,
            "Factor: {}".format(self.format_change_factor()),
            self.generate_step_hint(1),
            active=self.key_no_modifiers,
            mouse_value=True,
            input_stream=self.segment_change_input_stream)
    else:
        draw_property(
            self,
            "Offset: {}".format(self.segment_change),
            self.generate_step_hint(2, 1),
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.segment_change_input_stream)
    
    draw_property(
            self,
            "Minimum: {}".format(self.minimum_segments),
            self.generate_key_hint("Ctrl", self.generate_step_hint(1)),
            active=self.key_ctrl,
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

    if self.change_mode == self.change_modes.index('FACTOR'):
        draw_hint(
            self,
            "Round [R]: {}".format(self.round_modes[self.round_mode].capitalize()),
            ", ".join([m.capitalize() for m in self.round_modes]))

    draw_hint(
        self,
        "Enhanced Wireframe [E]: {0}".format("Yes" if self.target_object.show_wire else "No"),
        "Display the object's wireframe over solid shading")


def register():
    bpy.utils.register_class(ND_OT_bevel_resolution)


def unregister():
    bpy.utils.unregister_class(ND_OT_bevel_resolution)
    unregister_draw_handler()
