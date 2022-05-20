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
from math import radians, degrees
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream


mod_deform = "Deform — ND SD"
mod_summon_list = [mod_deform]


class ND_OT_simple_deform(bpy.types.Operator):
    bl_idname = "nd.simple_deform"
    bl_label = "Simple Deform"
    bl_description = "Twist, bend, taper, or stretch the selected object"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        factor_factor = 0.01 if self.key_shift else 0.1
        angle_factor = 1 if self.key_shift else 10

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
                if self.is_angular[self.methods[self.current_method]]:
                    self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                    self.angle = get_stream_value(self.angle_input_stream)
                else:
                    self.factor_input_stream = update_stream(self.factor_input_stream, event.type)
                    self.factor = get_stream_value(self.factor_input_stream)

                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                if self.is_angular[self.methods[self.current_method]]:
                    self.angle_input_stream = new_stream()
                    self.angle = 0
                else:
                    self.factor_input_stream = new_stream()
                    self.factor = 0

                self.dirty = True

        elif pressed(event, {'M'}):
            self.current_method = (self.current_method + 1) % len(self.methods)
            self.dirty = True

        elif pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        elif self.key_step_up:
            if self.key_no_modifiers:
                if no_stream(self.angle_input_stream) and self.is_angular[self.methods[self.current_method]]:
                    self.angle = min(360, self.angle + angle_factor)
                elif no_stream(self.factor_input_stream):
                    self.factor += factor_factor
                
                self.dirty = True
            
        elif self.key_step_down:
            if self.key_no_modifiers:
                if no_stream(self.angle_input_stream) and self.is_angular[self.methods[self.current_method]]:
                    self.angle = min(360, self.angle - angle_factor)
                elif no_stream(self.factor_input_stream):
                    self.factor -= factor_factor
                
                self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.key_no_modifiers:
                if no_stream(self.angle_input_stream) and self.is_angular[self.methods[self.current_method]]:
                    self.angle = max(-360, min(360, self.angle + self.mouse_value_mag))
                elif no_stream(self.factor_input_stream):
                    self.factor += self.mouse_value
            
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.methods = ['TWIST', 'BEND', 'TAPER', 'STRETCH']
        self.current_method = 0
        self.is_angular = {'TWIST': True, 'BEND': True, 'TAPER': False, 'STRETCH': False}

        self.angle_input_stream = new_stream()
        self.factor_input_stream = new_stream()

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
        self.angle = 0
        self.factor = 0

        self.add_simple_deform_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.deform = mods[mod_deform]

        self.axis_prev = self.axis = {'X': 0, 'Y': 1, 'Z': 2}[self.deform.deform_axis]
        self.method_prev = self.current_method = self.methods.index(self.deform.deform_method)
        self.angle_prev = self.angle = degrees(self.deform.angle)
        self.factor_prev = self.factor = self.deform.factor


    def add_simple_deform_modifier(self, context):
        deform = context.object.modifiers.new(mod_deform, 'SIMPLE_DEFORM')

        self.deform = deform


    def operate(self, context):
        axis = ['X', 'Y', 'Z'][self.axis]

        self.deform.deform_method = self.methods[self.current_method]
        self.deform.deform_axis = axis

        if self.is_angular[self.methods[self.current_method]]:
            self.deform.angle = radians(self.angle)
        else:
            self.deform.factor = self.factor

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.deform.name)

        if self.summoned:
            axis = ['X', 'Y', 'Z'][self.axis_prev]

            self.deform.deform_method = self.methods[self.method_prev]
            self.deform.deform_axis = axis

            if self.is_angular[self.methods[self.method_prev]]:
                self.deform.angle = radians(self.angle_prev)
            else:
                self.deform.factor = self.factor_prev
        
        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    if self.is_angular[self.methods[self.current_method]]:
        draw_property(
            self,
            "Angle: {0:.0f}°".format(self.angle),
            "(±10)  |  Shift (±1)",
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.angle_input_stream)
    else:
        draw_property(
            self,
            "Factor: {0:.2f}".format(self.factor),
            "(±0.1)  |  Shift (±0.01)",
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.factor_input_stream)

    draw_hint(
        self,
        "Method [M]: {}".format(self.methods[self.current_method].capitalize()),
        "Deformation method ({})".format(", ".join([m.capitalize() for m in self.methods])))

    draw_hint(
        self,
        "Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Deformation axis (X, Y, Z)")


def menu_func(self, context):
    self.layout.operator(ND_OT_simple_deform.bl_idname, text=ND_OT_simple_deform.bl_label)


def register():
    bpy.utils.register_class(ND_OT_simple_deform)


def unregister():
    bpy.utils.unregister_class(ND_OT_simple_deform)
    unregister_draw_handler()
