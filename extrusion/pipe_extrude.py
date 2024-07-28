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
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with, ensure_tail_mod_consistency, add_smooth_by_angle
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, ctx_edit_mode, obj_is_mesh, ctx_objects_selected, app_minor_version


mod_skin = "Skin — ND PIPE"
mod_bevel = "Bevel — ND PIPE"
mod_weld = "Weld — ND PIPE"
mod_summon_list = [mod_skin, mod_bevel, mod_weld]


class ND_OT_pipe_extrude(BaseOperator):
    bl_idname = "nd.pipe_extrude"
    bl_label = "Pipe Extrude"
    bl_description = """Extrudes a pipe along the selected edge."""


    def do_modal(self, context, event):
        segment_factor = 1 if self.key_shift else 2

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.extrusion_diameter_input_stream = update_stream(self.extrusion_diameter_input_stream, event.type)
                self.extrusion_diameter = get_stream_value(self.extrusion_diameter_input_stream, self.unit_scaled_factor)
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=1))
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.extrusion_diameter_input_stream) and self.hard_stream_reset or no_stream(self.extrusion_diameter_input_stream):
                    self.extrusion_diameter = 0
                    self.dirty = True
                self.extrusion_diameter_input_stream = new_stream()
            elif self.key_alt:
                if has_stream(self.segments_input_stream) and self.hard_stream_reset or no_stream(self.segments_input_stream):
                    self.segments = 1
                    self.dirty = True
                self.segments_input_stream = new_stream()

        if self.key_step_up:
            if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
                self.dirty = True
            elif not self.extend_mouse_values and no_stream(self.extrusion_diameter_input_stream) and self.key_no_modifiers:
                self.extrusion_diameter += self.step_size
                self.dirty = True

        if self.key_step_down:
            if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = max(1, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(1, self.segments - segment_factor)
                self.dirty = True
            elif not self.extend_mouse_values and no_stream(self.extrusion_diameter_input_stream) and self.key_no_modifiers:
                self.extrusion_diameter = max(0, self.extrusion_diameter - self.step_size)
                self.dirty = True

        if pressed(event, {'S'}):
            self.skin_smooth_shading = not self.skin_smooth_shading
            self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(1, self.segments + self.mouse_step)
                self.dirty = True
            elif no_stream(self.extrusion_diameter_input_stream) and self.key_no_modifiers:
                self.extrusion_diameter = max(0, self.extrusion_diameter + self.mouse_value)
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND PIPE')
            return {'FINISHED'}

        self.dirty = False

        self.extrusion_diameter_input_stream = new_stream()
        self.segments_input_stream = new_stream()
        self.edit_mode = ctx_edit_mode(context)

        self.target_object = context.active_object

        mods = self.target_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if previous_op:
            self.summon_old_operator(context, mods)
        else:
            self.prepare_new_operator(context)

        if self.edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if ctx_obj_mode(context):
            target_object = get_real_active_object(context)
            return obj_is_mesh(target_object) and ctx_objects_selected(context, 1)

        if ctx_edit_mode(context):
            return obj_is_mesh(context.active_object)


    def prepare_new_operator(self, context):
        self.summoned = False

        self.extrusion_diameter = 0
        self.segments = 1
        self.skin_smooth_shading = get_preferences().enable_auto_smooth

        self.add_smooth_shading(context)
        self.add_skin_modifier(context)
        self.add_bevel_modifier(context)
        self.add_weld_modifier(context)

        ensure_tail_mod_consistency(self.target_object)


    def get_max_skin_vert_radius(self):
        radius = 0
        skin_verts = self.target_object.data.skin_vertices[''].data
        for vert in skin_verts:
            radius = max(radius, vert.radius[0])

        return radius


    def set_skin_vert_radius(self, radius):
        skin_verts = self.target_object.data.skin_vertices[''].data
        for vert in skin_verts:
            vert.radius = (radius, radius)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.calculate_edges = True
        self.skin = mods[mod_skin]
        self.bevel = mods[mod_bevel]
        self.weld = mods[mod_weld]

        self.segments_prev = self.segments = self.bevel.segments
        self.extrusion_diameter_prev = self.extrusion_diameter = self.get_max_skin_vert_radius()
        self.skin_smooth_shading_prev = self.skin_smooth_shading = self.skin.use_smooth_shade

        if get_preferences().lock_overlay_parameters_on_recall:
            self.extrusion_diameter_input_stream = set_stream(self.extrusion_diameter)
            self.segments_input_stream = set_stream(self.segments)


    def add_smooth_shading(self, context):
        if not get_preferences().enable_auto_smooth:
            return

        return_to_edit = False
        if self.edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')
            return_to_edit = True

        if app_minor_version() >= (4, 1):
            add_smooth_by_angle(self.target_object)
            if return_to_edit:
                bpy.ops.object.mode_set(mode='EDIT')
            return

        bpy.ops.object.shade_smooth()
        self.target_object.data.use_auto_smooth = True
        self.target_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))

        if return_to_edit:
            bpy.ops.object.mode_set(mode='EDIT')


    def add_skin_modifier(self, context):
        skin = new_modifier(self.target_object, mod_skin, 'SKIN', rectify=False)
        skin.use_x_symmetry = True
        skin.use_y_symmetry = True
        skin.use_z_symmetry = True

        self.skin = skin


    def add_bevel_modifier(self, context):
        bevel = new_modifier(self.target_object, mod_bevel, 'BEVEL', rectify=False)
        bevel.offset_type = 'PERCENT'
        bevel.width_pct = 50
        bevel.segments = self.segments

        self.bevel = bevel


    def add_weld_modifier(self, context):
        weld = new_modifier(self.target_object, mod_weld, 'WELD', rectify=False)

        self.weld = weld


    def operate(self, context):
        self.bevel.segments = self.segments
        self.set_skin_vert_radius(self.extrusion_diameter)
        self.skin.use_smooth_shade = self.skin_smooth_shading

        self.dirty = False


    def finish(self, context):
        if self.edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')

        unregister_draw_handler()


    def revert(self, context):
        if self.edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')

        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.bevel.name)
            bpy.ops.object.modifier_remove(modifier=self.skin.name)
            bpy.ops.object.modifier_remove(modifier=self.weld.name)

        if self.summoned:
            self.bevel.segments = self.segments_prev
            self.set_skin_vert_radius(self.extrusion_diameter_prev)
            self.skin.use_smooth_shade = self.skin_smooth_shading_prev

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Diameter: {(self.extrusion_diameter * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.unit_step_hint,
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.extrusion_diameter_input_stream)

    draw_property(
        self,
        "Segments: {}".format(self.segments),
        self.generate_key_hint("Alt / Scroll" if self.extend_mouse_values else "Alt", self.generate_step_hint(2, 1)),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.segments_input_stream)

    draw_hint(
        self,
        "Smooth Shading [S]: {0}".format("Yes" if self.skin_smooth_shading else "No"),
        "Enables smooth shading on the skin modifier")


def register():
    bpy.utils.register_class(ND_OT_pipe_extrude)


def unregister():
    bpy.utils.unregister_class(ND_OT_pipe_extrude)
    unregister_draw_handler()
