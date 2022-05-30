# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)
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


mod_displace = "Offset — ND SOL"
mod_solidify = "Thickness — ND SOL"
mod_summon_list = [mod_displace, mod_solidify]


class ND_OT_solidify(bpy.types.Operator):
    bl_idname = "nd.solidify"
    bl_label = "Solidify"
    bl_description = "Adds a solidify modifier, and enables smoothing"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        thickness_factor = (self.base_thickness_factor / 10.0) if self.key_shift else self.base_thickness_factor
        offset_factor = (self.base_offset_factor / 10.0) if self.key_shift else self.base_offset_factor

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
                self.thickness_input_stream = update_stream(self.thickness_input_stream, event.type)
                self.thickness = get_stream_value(self.thickness_input_stream, 0.001)
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = update_stream(self.offset_input_stream, event.type)
                self.offset = get_stream_value(self.offset_input_stream, 0.001)
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.thickness_input_stream = new_stream()
                self.thickness = 0
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = new_stream()
                self.offset = 0
                self.dirty = True

        elif pressed(event, {'W'}):
            self.weighting = self.weighting + 1 if self.weighting < 1 else -1
            self.dirty = True

        elif self.key_increase_factor:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
                self.base_thickness_factor = min(1, self.base_thickness_factor * 10.0)
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)

        elif self.key_decrease_factor:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
               self.base_thickness_factor = max(0.001, self.base_thickness_factor / 10.0)
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)

        elif self.key_step_up:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
                self.thickness += thickness_factor
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += offset_factor
                self.dirty = True
            
        elif self.key_step_down:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
                self.thickness = max(0, self.thickness - thickness_factor)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset -= offset_factor
                self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.thickness_input_stream) and self.key_no_modifiers:
                self.thickness = max(0, self.thickness + self.mouse_value)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.mouse_value
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_thickness_factor = 0.01
        self.base_offset_factor = 0.001

        self.thickness_input_stream = new_stream()
        self.offset_input_stream = new_stream()

        mods = context.active_object.modifiers
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
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.object.type == 'MESH'

    
    def prepare_new_operator(self, context):
        self.summoned = False

        self.thickness = 0
        self.weighting = 0
        self.offset = 0

        self.add_smooth_shading(context)
        self.add_displace_modifier(context)
        self.add_solidify_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.solidify = mods[mod_solidify]
        self.displace = mods[mod_displace]

        self.thickness_prev = self.thickness = self.solidify.thickness
        self.weighting_prev = self.weighting = self.solidify.offset
        self.offset_prev = self.offset = self.displace.strength


    def add_smooth_shading(self, context):
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        context.object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))


    def add_displace_modifier(self, context):
        displace = context.object.modifiers.new(mod_displace, 'DISPLACE')
        displace.mid_level = 0

        self.displace = displace


    def add_solidify_modifier(self, context):
        solidify = context.object.modifiers.new(mod_solidify, 'SOLIDIFY')
        solidify.use_even_offset = True

        self.solidify = solidify
    

    def operate(self, context):
        self.solidify.thickness = self.thickness
        self.solidify.offset = self.weighting
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
            self.displace.strength = self.offset_prev
        
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Thickness: {0:.1f}".format(self.thickness * 1000), 
        "(±{0:.1f})  |  Shift + (±{1:.1f})".format(self.base_thickness_factor * 1000, (self.base_thickness_factor / 10) * 1000),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.thickness_input_stream)

    draw_property(
        self, 
        "Offset: {0:.1f}".format(self.offset * 1000), 
        "Ctrl (±{0:.1f})  |  Shift + Ctrl (±{1:.1f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.offset_input_stream)

    draw_hint(
        self,
        "Weighting [W]: {}".format(['Negative', 'Neutral', 'Positive'][1 + round(self.weighting)]),
        "Negative, Neutral, Positive")


def register():
    bpy.utils.register_class(ND_OT_solidify)


def unregister():
    bpy.utils.unregister_class(ND_OT_solidify)
    unregister_draw_handler()
