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
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream
from .. lib.modifiers import add_smooth_by_angle, set_smoothing_angle


class ND_OT_seams(BaseOperator):
    bl_idname = "nd.seams"
    bl_label = "UV Seams"
    bl_description = """Interactively set UV seams & sharp edges
SHIFT — Skip interactive mode and immediately apply the default settings"""
    bl_options = {'UNDO'}


    def do_modal(self, context, event):
        angle_factor = 1 if self.key_shift else self.base_angle_factor

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                self.angle = get_stream_value(self.angle_input_stream)
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.angle_input_stream) and self.hard_stream_reset or no_stream(self.angle_input_stream):
                    self.angle = degrees(context.active_object.data.auto_smooth_angle)
                    self.dirty = True
                self.angle_input_stream = new_stream()

        elif pressed(event, {'A'}):
            self.commit_auto_smooth = not self.commit_auto_smooth
            self.dirty = True

        elif self.key_step_up:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = min(180, self.angle + angle_factor)
                self.dirty = True

        elif self.key_step_down:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = max(0, self.angle - angle_factor)
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


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        self.dirty = False
        self.fast_apply = event.shift

        self.base_angle_factor = 15
        self.angle = int(get_preferences().default_smoothing_angle)
        self.commit_auto_smooth = get_preferences().enable_auto_smooth

        self.angle_input_stream = new_stream()

        self.target_object = context.active_object

        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'EDGE'})
        bpy.ops.mesh.select_all(action='DESELECT')

        self.operate(context)

        if self.fast_apply:
            self.finish(context)

            return {'FINISHED'}

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and context.active_object is not None:
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'


    def operate(self, context):
        self.clear_edges(context)

        bpy.ops.mesh.edges_select_sharp(sharpness=radians(self.angle))

        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.mark_sharp(clear=False)

        bpy.ops.mesh.select_all(action='DESELECT')

        self.dirty = False


    def clear_edges(self, context):
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.mark_seam(clear=True)
        bpy.ops.mesh.mark_sharp(clear=True)

        bpy.ops.mesh.select_all(action='DESELECT')


    def finish(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')

        if self.commit_auto_smooth:
            if bpy.app.version >= (4, 1, 0):
                mod = add_smooth_by_angle(self.target_object)
                set_smoothing_angle(self.target_object, mod, radians(180), False)
            else:
                bpy.ops.object.shade_smooth()
                self.target_object.data.use_auto_smooth = True
                self.target_object.data.auto_smooth_angle = radians(180)

        unregister_draw_handler()


    def revert(self, context):
        self.clear_edges(context)
        bpy.ops.object.mode_set(mode='OBJECT')

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Angle: {0:.2f}°".format(self.angle),
        self.generate_step_hint(self.base_angle_factor, 1),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.angle_input_stream)

    draw_hint(
        self,
        "Auto Smooth [A]: {0}".format("Yes" if self.commit_auto_smooth else "No"),
        "Set auto smooth angle to 180° on completion")


def register():
    bpy.utils.register_class(ND_OT_seams)


def unregister():
    bpy.utils.unregister_class(ND_OT_seams)
    unregister_draw_handler()
