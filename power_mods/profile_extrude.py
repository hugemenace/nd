# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream


mod_screw = "Extrusion — ND PE"
mod_offset = "Offset — ND PE"
mod_summon_list = [mod_screw, mod_offset]


class ND_OT_profile_extrude(bpy.types.Operator):
    bl_idname = "nd.profile_extrude"
    bl_label = "Profile Extrude"
    bl_description = "Extrudes a profile along a specified axis"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        extrude_factor = (self.base_extrude_factor / 10.0) if self.key_shift else self.base_extrude_factor

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
                self.extrusion_length_input_stream = update_stream(self.extrusion_length_input_stream, event.type)
                self.extrusion_length = get_stream_value(self.extrusion_length_input_stream, 0.001)
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.extrusion_length_input_stream = new_stream()
                self.extrusion_length = 0
                self.dirty = True

        elif pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        elif pressed(event, {'W'}):
            self.weighting = self.weighting + 1 if self.weighting < 1 else -1
            self.dirty = True

        elif self.key_increase_factor:
            self.base_extrude_factor = min(1, self.base_extrude_factor * 10.0)

        elif self.key_decrease_factor:
            self.base_extrude_factor = max(0.001, self.base_extrude_factor / 10.0)

        elif self.key_step_up:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.extrusion_length += extrude_factor
                self.dirty = True
            
        elif self.key_step_down:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.extrusion_length = max(0, self.extrusion_length - extrude_factor)
                self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.extrusion_length = max(0, self.extrusion_length + self.mouse_value)
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_extrude_factor = 0.01

        self.extrusion_length_input_stream = new_stream()

        if len(context.selected_objects) == 1:
            mods = context.active_object.modifiers
            mod_names = list(map(lambda x: x.name, mods))
            previous_op = all(m in mod_names for m in mod_summon_list)

            if previous_op:
                self.summon_old_operator(context, mods)
            else:
                self.prepare_new_operator(context)
        else:
            self.prepare_new_operator(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        init_axis(self, context.active_object, self.axis)
        register_axis_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.object.type == 'MESH'

    
    def prepare_new_operator(self, context):
        self.summoned = False

        self.axis = 0
        self.extrusion_length = 0
        self.weighting = 0

        self.add_offset_modifier(context)
        self.add_screw_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.screw = mods[mod_screw]
        self.offset = mods[mod_offset]

        self.axis_prev = self.axis = {'X': 0, 'Y': 1, 'Z': 2}[self.screw.axis]
        self.extrusion_length_prev = self.extrusion_length = self.screw.screw_offset
        self.weighting_prev = self.weighting = self.calculate_existing_weighting()


    def calculate_offset_strength(self):
        if self.weighting == -1:
            return self.extrusion_length * -2
        elif self.weighting == 0:
            return self.extrusion_length * -1
        elif self.weighting == 1:
            return 0

    
    def calculate_existing_weighting(self):
        offset = abs(self.offset.strength)
        extrusion = self.screw.screw_offset
        factor = offset / extrusion

        return max(-1, min(1, 1 - round(factor)))


    def add_offset_modifier(self, context):
        offset = context.object.modifiers.new(mod_offset, 'DISPLACE')
        offset.space = 'LOCAL'
        offset.mid_level = 0

        self.offset = offset


    def add_screw_modifier(self, context):
        screw = context.object.modifiers.new(mod_screw, 'SCREW')
        screw.steps = 0
        screw.render_steps = 0
        screw.angle = 0
        screw.use_normal_calculate = True

        self.screw = screw
    

    def operate(self, context):
        axis = ['X', 'Y', 'Z'][self.axis]

        self.screw.axis = axis
        self.screw.screw_offset = self.extrusion_length
        self.offset.direction = axis
        self.offset.strength = self.calculate_offset_strength()

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.offset.name)
            bpy.ops.object.modifier_remove(modifier=self.screw.name)

        if self.summoned:
            axis = ['X', 'Y', 'Z'][self.axis_prev]

            self.screw.axis = axis
            self.screw.screw_offset = self.extrusion_length_prev
            self.offset.direction = axis
            self.offset.strength = self.calculate_offset_strength()
        
        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Extrusion: {0:.1f}".format(self.extrusion_length * 1000),
        "(±{0:.1f})  |  Shift + (±{1:.1f})".format(self.base_extrude_factor * 1000, (self.base_extrude_factor / 10) * 1000),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.extrusion_length_input_stream)

    draw_hint(
        self,
        "Weighting [W]: {}".format(['Negative', 'Neutral', 'Positive'][1 + round(self.weighting)]),
        "Negative, Neutral, Positive")

    draw_hint(
        self,
        "Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Axis to extrude along (X, Y, Z)")


def menu_func(self, context):
    self.layout.operator(ND_OT_profile_extrude.bl_idname, text=ND_OT_profile_extrude.bl_label)


def register():
    bpy.utils.register_class(ND_OT_profile_extrude)


def unregister():
    bpy.utils.unregister_class(ND_OT_profile_extrude)
    unregister_draw_handler()
