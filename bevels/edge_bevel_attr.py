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
from .. lib.polling import ctx_edit_mode, obj_edges_selected, obj_is_mesh, app_minor_version
from .. lib.math import round_dec


MIN_BLENDER_VERSION = (4, 3)


mod_bevel = "Bevel — ND EBA"
mod_weld = "Weld — ND EBA"
mod_summon_list = [mod_bevel, mod_weld]


class ND_OT_edge_bevel_attr(BaseOperator):
    bl_idname = "nd.edge_bevel_attr"
    bl_label = "Edge Bevel (Attribute)"
    bl_description = """Adds an attribute-based edge bevel modifier to the selected object
SHIFT — Place modifiers at the top of the stack
CTRL — Remove existing modifiers

Min Blender Version: """ + '.'.join([str(v) for v in MIN_BLENDER_VERSION])


    def do_modal(self, context, event):
        weight_factor = 0.01 if self.key_shift else 0.1
        profile_factor = 0.01 if self.key_shift else 0.1
        segment_factor = 1 if self.key_shift else 2
        percent_factor = 1 if self.key_shift else 10

        if self.key_numeric_input:
            if not self.is_width_percent() and self.key_no_modifiers:
                self.width_input_stream = update_stream(self.width_input_stream, event.type)
                self.width = get_stream_value(self.width_input_stream, self.unit_scaled_factor)
                self.dirty = True
            elif self.is_width_percent() and self.key_no_modifiers:
                self.percentage_input_stream = update_stream(self.percentage_input_stream, event.type)
                self.percentage = get_stream_value(self.percentage_input_stream, min_value=0, max_value=100)
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=1))
                self.dirty = True
            elif self.key_ctrl:
                self.profile_input_stream = update_stream(self.profile_input_stream, event.type)
                self.profile = get_stream_value(self.profile_input_stream)
                self.dirty = True

        if self.key_reset:
            if not self.is_width_percent() and self.key_no_modifiers:
                if has_stream(self.width_input_stream) and self.hard_stream_reset or no_stream(self.width_input_stream):
                    self.width = 0
                    self.dirty = True
                self.width_input_stream = new_stream()
            elif self.is_width_percent() and self.key_no_modifiers:
                if has_stream(self.percentage_input_stream) and self.hard_stream_reset or no_stream(self.percentage_input_stream):
                    self.percentage = 0
                    self.dirty = True
                self.percentage_input_stream = new_stream()
            elif self.key_alt:
                if has_stream(self.segments_input_stream) and self.hard_stream_reset or no_stream(self.segments_input_stream):
                    self.segments = 1
                    self.dirty = True
                self.segments_input_stream = new_stream()
            elif self.key_ctrl:
                if has_stream(self.profile_input_stream) and self.hard_stream_reset or no_stream(self.profile_input_stream):
                    self.profile = 0.5
                    self.dirty = True
                self.profile_input_stream = new_stream()

        if pressed(event, {'H'}):
            self.harden_normals = not self.harden_normals
            self.dirty = True

        if pressed(event, {'C'}):
            self.clamp_overlap = not self.clamp_overlap
            self.dirty = True

        if pressed(event, {'S'}):
            self.loop_slide = not self.loop_slide
            self.dirty = True

        if pressed(event, {'E'}):
            self.target_object.show_wire = not self.target_object.show_wire
            self.target_object.show_in_front = not self.target_object.show_in_front

        if pressed(event, {'W'}):
            self.width_type = (self.width_type + 1) % len(self.width_types)
            self.dirty = True

        if self.key_step_up:
            if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = min(1, round_dec(self.profile + profile_factor))
                self.dirty = True
            elif not self.is_width_percent() and not self.extend_mouse_values and no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = round_dec(self.width + self.step_size)
                self.dirty = True
            elif self.is_width_percent() and not self.extend_mouse_values and no_stream(self.percentage_input_stream) and self.key_no_modifiers:
                self.percentage = min(100, round_dec(self.percentage + percent_factor))
                self.dirty = True

        if self.key_step_down:
            if self.extend_mouse_values and no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = max(1, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(1, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = max(0, round_dec(self.profile - profile_factor))
                self.dirty = True
            elif not self.is_width_percent() and not self.extend_mouse_values and no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(0, round_dec(self.width - self.step_size))
                self.dirty = True
            elif self.is_width_percent() and not self.extend_mouse_values and no_stream(self.percentage_input_stream) and self.key_no_modifiers:
                self.percentage = max(0, round_dec(self.percentage - percent_factor))
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
            elif not self.is_width_percent() and no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(0.0, self.width + self.mouse_value)
                self.dirty = True
            elif self.is_width_percent() and no_stream(self.percentage_input_stream) and self.key_no_modifiers:
                self.percentage = max(0.0, min(100.0, self.percentage + self.mouse_value_mag))
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = max(0.0, min(1.0, self.profile + self.mouse_value))
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        if not obj_edges_selected(context.active_object):
            self.report({'INFO'}, "No edges selected.")
            return {'CANCELLED'}

        self.target_object = context.active_object

        self.mods = self.target_object.modifiers
        self.mod_names = list(map(lambda x: x.name, self.mods))
        self.current_bevel_mods = list(filter(lambda x: any(m in x for m in mod_summon_list), self.mod_names))

        if event.ctrl:
            if len(self.current_bevel_mods) == 0:
                return {'FINISHED'}

            last_bevel_mod = self.current_bevel_mods[-1] if self.current_bevel_mods else None

            if last_bevel_mod == None:
                return {'FINISHED'}

            last_bevel_mod_tail = last_bevel_mod.split(' — ')[-1]

            remove_modifiers_ending_with(context.selected_objects, ' — ND EBA')
            remove_modifiers_ending_with(context.selected_objects, ' — ND EBA')

            bpy.ops.object.mode_set(mode='OBJECT')
            for attr in self.target_object.data.attributes:
                if attr.name.startswith("ND.") and attr.domain == 'EDGE':
                    print(f"Removing attribute {attr.name} from {self.target_object.name}")
                    self.target_object.data.attributes.remove(attr)
            bpy.ops.object.mode_set(mode='EDIT')

            return {'FINISHED'}

        self.dirty = False
        self.early_apply = event.shift

        self.segments = 1
        self.width_types = ['OFFSET', 'WIDTH', 'DEPTH', 'PERCENT', 'ABSOLUTE']
        self.width_type = self.width_types.index('WIDTH')
        self.width = 0.05 * self.unit_factor
        self.percentage = 0
        self.profile = 0.5
        self.harden_normals = False
        self.loop_slide = False
        self.clamp_overlap = False

        self.segments_input_stream = new_stream()
        self.width_input_stream = new_stream()
        self.percentage_input_stream = new_stream()
        self.profile_input_stream = new_stream()

        self.edge_attribute = None
        self.edge_attribute_name = None

        previous_op = False

        self.bm = bmesh.from_edit_mesh(self.target_object.data)
        self.bm.edges.ensure_lookup_table()
        self.selected_edges_indexes = [edge.index for edge in self.bm.edges if edge.select]
        self.bm.free()

        bpy.ops.object.mode_set(mode='OBJECT')

        attribute_matches = []
        for attr in self.target_object.data.attributes:
            if attr.name.startswith("ND.") and attr.domain == 'EDGE':
                if any(attr.data[edge].value > 0 for edge in self.selected_edges_indexes):
                    attribute_matches.append(attr)

        bpy.ops.object.mode_set(mode='EDIT')

        if len(attribute_matches) > 1:
            self.report({'INFO'}, "Multiple edge attributes are active, unable to continue operation.")
            return {'CANCELLED'}

        if len(attribute_matches) == 1:
            attribute_match = attribute_matches[0]
            for mod in self.target_object.modifiers:
                if mod.type == 'BEVEL' and mod.limit_method == 'WEIGHT' and mod.edge_weight == attribute_match.name:
                    previous_op = True
                    self.bevel = mod
                    self.edge_attribute = attribute_match
                    self.edge_attribute_name = attribute_match.name
                    break

        if previous_op:
            self.summon_old_operator(context)
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
        if app_minor_version() < MIN_BLENDER_VERSION:
            return False

        target_object = context.active_object
        return ctx_edit_mode(context) and obj_is_mesh(target_object)


    def prepare_new_operator(self, context):
        self.summoned = False

        self.add_new_edge_attribute(context)
        self.add_smooth_shading(context)
        self.add_bevel_modifier(context)

        ensure_tail_mod_consistency(self.target_object)


    def summon_old_operator(self, context):
        self.summoned = True

        self.width_type_prev = self.width_type = self.width_types.index(self.bevel.offset_type)
        self.width_prev = self.width = self.bevel.width
        self.percentage_prev = self.percentage = self.bevel.width_pct
        self.segments_prev = self.segments = self.bevel.segments
        self.profile_prev = self.profile = self.bevel.profile
        self.harden_normals_prev = self.harden_normals = self.bevel.harden_normals
        self.loop_slide_prev = self.loop_slide = self.bevel.loop_slide
        self.clamp_overlap_prev = self.clamp_overlap = self.bevel.use_clamp_overlap

        if get_preferences().lock_overlay_parameters_on_recall:
            self.segments_input_stream = set_stream(self.segments)
            self.width_input_stream = set_stream(self.width)
            self.percentage_input_stream = set_stream(self.percentage)
            self.profile_input_stream = set_stream(self.profile)

        # Set the edge attribute value for all new edges selected in the
        # current summoning, and keep track of them (for reverting).
        bpy.ops.object.mode_set(mode='OBJECT')
        self.post_summon_new_edges = []
        self.edge_attribute = self.target_object.data.attributes.get(self.edge_attribute_name)
        for edge in self.selected_edges_indexes:
            if self.edge_attribute.data[edge].value <= 0:
                self.post_summon_new_edges.append(edge)
                self.edge_attribute.data[edge].value = 1.0
        bpy.ops.object.mode_set(mode='EDIT')


    def add_new_edge_attribute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')

        self.edge_attribute = self.target_object.data.attributes.new(name="ND.EdgeWeight", type='FLOAT', domain='EDGE')
        self.edge_attribute_name = self.edge_attribute.name

        for edge in self.selected_edges_indexes:
            self.edge_attribute.data[edge].value = 1.0

        bpy.ops.object.mode_set(mode='EDIT')


    def add_smooth_shading(self, context):
        if not get_preferences().enable_auto_smooth:
            return

        if app_minor_version() >= (4, 1):
            bpy.ops.object.mode_set(mode='OBJECT')
            add_smooth_by_angle(context, self.target_object)
            bpy.ops.object.mode_set(mode='EDIT')
            return

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()
        self.target_object.data.use_auto_smooth = True
        self.target_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))
        bpy.ops.object.mode_set(mode='EDIT')


    def add_bevel_modifier(self, context):
        bevel = new_modifier(self.target_object, mod_bevel, 'BEVEL', rectify=True)
        bevel.offset_type = 'WIDTH'
        bevel.limit_method = 'WEIGHT'
        bevel.miter_outer = 'MITER_ARC'
        bevel.face_strength_mode = 'FSTR_AFFECTED'
        bevel.edge_weight = self.edge_attribute_name

        self.bevel = bevel

        if self.early_apply:
            while self.target_object.modifiers[0].name != self.bevel.name:
                bpy.ops.object.modifier_move_up(modifier=self.bevel.name)


    def add_weld_modifier(self, context):
        mods = self.target_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if not previous_op:
            weld = new_modifier(self.target_object, mod_weld, 'WELD', rectify=True)
            weld.merge_threshold = 0.00001
            weld.mode = 'CONNECTED'

            self.weld = weld

            if self.early_apply:
                while self.target_object.modifiers[1].name != self.weld.name:
                    bpy.ops.object.modifier_move_up(modifier=self.weld.name)


    def is_width_percent(self):
        return self.width_type == self.width_types.index('PERCENT')


    def operate(self, context):
        self.bevel.offset_type = self.width_types[self.width_type]

        final_width = self.percentage if self.is_width_percent() else self.width
        self.bevel.width_pct = final_width
        self.bevel.width = final_width

        self.bevel.segments = self.segments
        self.bevel.profile = self.profile
        self.bevel.harden_normals = self.harden_normals
        self.bevel.loop_slide = self.loop_slide
        self.bevel.use_clamp_overlap = self.clamp_overlap

        self.dirty = False


    def finish(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False
        self.add_weld_modifier(context)

        ensure_tail_mod_consistency(self.target_object)

        unregister_draw_handler()


    def revert(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False

        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.bevel.name)

        if self.summoned:
            self.bevel.offset_type = self.width_types[self.width_type_prev]
            self.bevel.width = self.width_prev
            self.bevel.width_pct = self.percentage_prev
            self.bevel.segments = self.segments_prev
            self.bevel.profile = self.profile_prev
            self.bevel.loop_slide = self.loop_slide_prev
            self.bevel.use_clamp_overlap = self.clamp_overlap_prev

            bpy.ops.object.mode_set(mode='OBJECT')
            self.edge_attribute = self.target_object.data.attributes.get(self.edge_attribute_name)
            for edge in self.post_summon_new_edges:
                self.edge_attribute.data[edge].value = 0.0
            bpy.ops.object.mode_set(mode='EDIT')

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    if self.is_width_percent():
        draw_property(
            self,
            f"Percentage: {self.percentage:.2f}%",
            self.generate_step_hint(10, 1),
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.percentage_input_stream)
    else:
        draw_property(
            self,
            f"{self.width_types[self.width_type].capitalize()}: {(self.width * self.display_unit_scale):.2f}{self.unit_suffix}",
            self.unit_step_hint,
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.width_input_stream)

    draw_property(
        self,
        "Segments: {}".format(self.segments),
        self.generate_key_hint("Alt / Scroll" if self.extend_mouse_values else "Alt", self.generate_step_hint(2, 1)),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.segments_input_stream)

    draw_property(
        self,
        "Profile: {0:.2f}".format(self.profile),
        self.generate_key_hint("Ctrl", self.generate_step_hint(0.1, 0.01)),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.profile_input_stream)

    draw_hint(
        self,
        "Width Type [W]: {0}".format(self.width_types[self.width_type].capitalize()),
        "{}".format(", ".join([m.capitalize() for m in self.width_types])))

    draw_hint(
        self,
        "Harden Normals [H]: {0}".format("Yes" if self.harden_normals else "No"),
        "Match normals of new faces to adjacent faces")

    draw_hint(
        self,
        "Enhanced Wireframe [E]: {0}".format("Yes" if self.target_object.show_wire else "No"),
        "Display the objects's wireframe over solid shading")

    draw_hint(
        self,
        "Clamp Overlap [C]: {0}".format("Yes" if self.clamp_overlap else "No"),
        "Clamp the width to avoid overlap")

    draw_hint(
        self,
        "Loop Slide [S]: {0}".format("Yes" if self.loop_slide else "No"),
        "Prefer sliding along edges to having even widths")


def register():
    bpy.utils.register_class(ND_OT_edge_bevel_attr)


def unregister():
    bpy.utils.unregister_class(ND_OT_edge_bevel_attr)
    unregister_draw_handler()
