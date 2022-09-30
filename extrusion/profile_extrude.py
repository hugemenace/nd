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
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with


mod_screw = "Extrusion — ND PE"
mod_weighting = "Weighting — ND PE"
mod_offset = "Offset — ND PE"
mod_summon_list = [mod_screw, mod_weighting, mod_offset]


class ND_OT_profile_extrude(bpy.types.Operator):
    bl_idname = "nd.profile_extrude"
    bl_label = "Profile Extrude"
    bl_description = """Extrudes a profile along a specified axis
CTRL — Remove existing modifiers"""
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        extrude_factor = (self.base_extrude_factor / 10.0) if self.key_shift else self.base_extrude_factor
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
                self.extrusion_length_input_stream = update_stream(self.extrusion_length_input_stream, event.type)
                self.extrusion_length = get_stream_value(self.extrusion_length_input_stream, 0.001)
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = update_stream(self.offset_input_stream, event.type)
                self.offset = get_stream_value(self.offset_input_stream, 0.001)
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.extrusion_length_input_stream = new_stream()
                self.extrusion_length = 0
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = new_stream()
                self.offset = 0
                self.dirty = True

        elif pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        elif pressed(event, {'W'}):
            self.weighting = self.weighting + 1 if self.weighting < 1 else -1
            self.dirty = True
        
        elif pressed(event, {'E'}):
            self.calculate_edges = not self.calculate_edges
            self.dirty = True

        elif self.key_increase_factor:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.base_extrude_factor = min(1, self.base_extrude_factor * 10.0)
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)

        elif self.key_decrease_factor:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.base_extrude_factor = max(0.001, self.base_extrude_factor / 10.0)
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)

        elif self.key_step_up:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.extrusion_length += extrude_factor
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += offset_factor
                self.dirty = True
            
        elif self.key_step_down:
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.extrusion_length = max(0, self.extrusion_length - extrude_factor)
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
            if no_stream(self.extrusion_length_input_stream) and self.key_no_modifiers:
                self.extrusion_length = max(0, self.extrusion_length + self.mouse_value)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.mouse_value
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND PE')
            return {'FINISHED'}

        self.dirty = False
        self.base_extrude_factor = 0.01
        self.base_offset_factor = 0.001

        self.extrusion_length_input_stream = new_stream()
        self.offset_input_stream = new_stream()

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
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'

    
    def prepare_new_operator(self, context):
        self.summoned = False

        self.axis = 0
        self.extrusion_length = 0
        self.weighting = 0
        self.offset = 0
        self.calculate_edges = True

        self.add_weighting_modifier(context)
        self.add_offset_modifier(context)
        self.add_screw_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.calculate_edges = True
        self.screw = mods[mod_screw]
        self.weighting_offset = mods[mod_weighting]
        self.displace = mods[mod_offset]

        self.axis_prev = self.axis = {'X': 0, 'Y': 1, 'Z': 2}[self.screw.axis]
        self.extrusion_length_prev = self.extrusion_length = self.screw.screw_offset
        self.calculate_edges_prev = self.calculate_edges = self.screw.use_normal_calculate
        self.weighting = self.calculate_existing_weighting()
        self.weighting_offset_strength_prev = self.weighting_offset.strength
        self.offset_prev = self.offset = self.displace.strength


    def calculate_weighting_offset_strength(self):
        if self.weighting == -1:
            return self.extrusion_length * -1
        elif self.weighting == 0:
            return self.extrusion_length * -0.5
        elif self.weighting == 1:
            return 0

    
    def calculate_existing_weighting(self):
        offset = abs(self.weighting_offset.strength)
        extrusion = self.screw.screw_offset
        factor = offset / (extrusion * 0.5)

        return max(-1, min(1, 1 - round(factor)))


    def add_weighting_modifier(self, context):
        offset = new_modifier(context.active_object, mod_weighting, 'DISPLACE', rectify=True)
        offset.space = 'LOCAL'
        offset.mid_level = 0

        self.weighting_offset = offset

    
    def add_offset_modifier(self, context):
        offset = new_modifier(context.active_object, mod_offset, 'DISPLACE', rectify=True)
        offset.space = 'LOCAL'
        offset.mid_level = 0

        self.displace = offset


    def add_screw_modifier(self, context):
        screw = new_modifier(context.active_object, mod_screw, 'SCREW', rectify=True)
        screw.steps = 0
        screw.render_steps = 0
        screw.angle = 0

        self.screw = screw
    

    def operate(self, context):
        axis = ['X', 'Y', 'Z'][self.axis]

        self.screw.axis = axis
        self.screw.screw_offset = self.extrusion_length
        self.screw.use_normal_calculate = self.calculate_edges
        self.weighting_offset.direction = axis
        self.weighting_offset.strength = self.calculate_weighting_offset_strength()
        self.displace.direction = axis
        self.displace.strength = self.offset

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.weighting_offset.name)
            bpy.ops.object.modifier_remove(modifier=self.screw.name)

        if self.summoned:
            axis = ['X', 'Y', 'Z'][self.axis_prev]

            self.screw.axis = axis
            self.screw.screw_offset = self.extrusion_length_prev
            self.weighting_offset.direction = axis
            self.weighting_offset.strength = self.weighting_offset_strength_prev
            self.displace.direction = axis
            self.displace.strength = self.offset_prev
        
        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Extrusion: {0:.2f}".format(self.extrusion_length * 1000),
        "(±{0:.2f})  |  Shift + (±{1:.2f})".format(self.base_extrude_factor * 1000, (self.base_extrude_factor / 10) * 1000),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.extrusion_length_input_stream)

    draw_property(
        self, 
        "Offset: {0:.2f}".format(self.offset * 1000), 
        "Ctrl (±{0:.2f})  |  Shift + Ctrl (±{1:.2f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
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
        "Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Axis to extrude along (X, Y, Z)")
    
    draw_hint(
        self,
        "Calculate Edges [E]: {}".format("Yes" if self.calculate_edges else "No"),
        "Calculate the order of edges (affects normals)")


def register():
    bpy.utils.register_class(ND_OT_profile_extrude)


def unregister():
    bpy.utils.unregister_class(ND_OT_profile_extrude)
    unregister_draw_handler()
