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
from .. lib.overlay import init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences, get_scene_unit_factor
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, ensure_tail_mod_consistency, add_smooth_by_angle
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, obj_is_mesh, ctx_objects_selected, app_minor_version


mod_displace = "Offset — ND SOL"
mod_solidify = "Thickness — ND SOL"
mod_summon_list = [mod_displace, mod_solidify]


class ND_OT_solidify(BaseOperator):
    bl_idname = "nd.solidify"
    bl_label = "Solidify"
    bl_description = """Adds a solidify modifier, and enables smoothing
CTRL — Remove existing modifiers"""


    def do_modal(self, context, event):
        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.thickness_input_stream = update_stream(self.thickness_input_stream, event.type)
                self.thickness = get_stream_value(self.thickness_input_stream, self.unit_scaled_factor)
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = update_stream(self.offset_input_stream, event.type)
                self.offset = get_stream_value(self.offset_input_stream, self.unit_scaled_factor)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.thickness_input_stream) and self.hard_stream_reset or no_stream(self.thickness_input_stream):
                    self.thickness = 0
                    self.dirty = True
                self.thickness_input_stream = new_stream()
            elif self.key_ctrl:
                if has_stream(self.offset_input_stream) and self.hard_stream_reset or no_stream(self.offset_input_stream):
                    self.offset = 0
                    self.dirty = True
                self.offset_input_stream = new_stream()

        if pressed(event, {'W'}):
            self.weighting = self.weighting + 1 if self.weighting < 1 else -1
            self.dirty = True

        if pressed(event, {'M'}):
            self.complex_mode = not self.complex_mode
            self.dirty = True

        if self.key_step_up:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
                self.thickness += self.step_size
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.step_size
                self.dirty = True

        if self.key_step_down:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
                self.thickness = max(0, self.thickness - self.step_size)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset -= self.step_size
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
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.mouse_value
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND SOL')
            return {'FINISHED'}

        self.dirty = False
        self.complex_mode = False

        self.target_object = context.active_object

        self.thickness_input_stream = new_stream()
        self.offset_input_stream = new_stream()

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

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and obj_is_mesh(target_object) and ctx_objects_selected(context, 1)


    def prepare_new_operator(self, context):
        self.summoned = False

        self.thickness = 0
        self.weighting = 0
        self.offset = 0

        self.add_smooth_shading(context)
        self.add_displace_modifier(context)
        self.add_solidify_modifier(context)

        ensure_tail_mod_consistency(self.target_object)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.solidify = mods[mod_solidify]
        self.displace = mods[mod_displace]

        self.thickness_prev = self.thickness = self.solidify.thickness
        self.weighting_prev = self.weighting = self.solidify.offset
        self.complex_mode_prev = self.complex_mode = (self.solidify.solidify_mode == 'NON_MANIFOLD')
        self.offset_prev = self.offset = self.displace.strength

        if get_preferences().lock_overlay_parameters_on_recall:
            self.thickness_input_stream = set_stream(self.thickness)
            self.offset_input_stream = set_stream(self.offset)


    def add_smooth_shading(self, context):
        if not get_preferences().enable_auto_smooth:
            return

        if app_minor_version() >= (4, 1):
            add_smooth_by_angle(context, self.target_object)
            return

        bpy.ops.object.shade_smooth()
        self.target_object.data.use_auto_smooth = True
        self.target_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))


    def add_displace_modifier(self, context):
        displace = new_modifier(self.target_object, mod_displace, 'DISPLACE', rectify=True)
        displace.mid_level = 0

        self.displace = displace


    def add_solidify_modifier(self, context):
        solidify = new_modifier(self.target_object, mod_solidify, 'SOLIDIFY', rectify=True)
        solidify.use_even_offset = True
        solidify.nonmanifold_thickness_mode = 'CONSTRAINTS'
        solidify.use_quality_normals = True

        self.solidify = solidify


    def operate(self, context):
        self.solidify.thickness = self.thickness
        self.solidify.offset = self.weighting
        self.solidify.solidify_mode = 'NON_MANIFOLD' if self.complex_mode else 'EXTRUDE'
        self.displace.strength = self.offset

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.displace.name)
            bpy.ops.object.modifier_remove(modifier=self.solidify.name)

        if self.summoned:
            self.solidify.thickness = self.thickness_prev
            self.solidify.offset = self.weighting_prev
            self.solidify.solidify_mode = 'NON_MANIFOLD' if self.complex_mode_prev else 'EXTRUDE'
            self.displace.strength = self.offset_prev

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Thickness: {(self.thickness * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.unit_step_hint,
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.thickness_input_stream)

    draw_property(
        self,
        f"Offset: {(self.offset * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.generate_key_hint("Ctrl", self.unit_step_hint),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.offset_input_stream)

    draw_hint(
        self,
        "Weighting [W]: {}".format(['Negative', 'Neutral', 'Positive'][1 + round(self.weighting)]),
        "Negative, Neutral, Positive")

    draw_hint(
        self,
        "Mode [M]: {}".format("Complex" if self.complex_mode else "Simple"),
        "Extrusion Algorithm (Simple, Complex)")


def register():
    bpy.utils.register_class(ND_OT_solidify)


def unregister():
    bpy.utils.unregister_class(ND_OT_solidify)
    unregister_draw_handler()
