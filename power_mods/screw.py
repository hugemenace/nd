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
from math import radians, degrees
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler


mod_displace = "Offset — ND SCR"
mod_screw = "Screw — ND SCR"
mod_summon_list = [mod_displace, mod_screw]


class ND_OT_screw(bpy.types.Operator):
    bl_idname = "nd.screw"
    bl_label = "Screw"
    bl_description = "Adds a screw modifier tuned for converting a sketch into a cylindrical object"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        segment_factor = 1 if self.key_shift else 2
        angle_factor = 1 if self.key_shift else 10
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

        elif pressed(event, {'R'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        elif pressed(event, {'O'}):
            self.offset_axis = (self.offset_axis + 1) % 3
            self.dirty = True

        elif self.key_increase_factor:
            if self.key_ctrl_alt:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_ctrl_alt:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)

        elif self.key_step_up:
            if self.key_ctrl_alt:
                self.offset += offset_factor
            elif self.key_alt:
                if self.key_shift:
                    self.offset_axis = (self.offset_axis + 1) % 3
                else:
                    self.axis = (self.axis + 1) % 3
            elif self.key_ctrl:
                self.angle = min(360, self.angle + angle_factor)
            else:
                self.segments = 4 if self.segments == 3 else self.segments + segment_factor

            self.dirty = True
            
        elif self.key_step_down:
            if self.key_ctrl_alt:
                self.offset -= offset_factor
            elif self.key_alt:
                if self.key_shift:
                    self.offset_axis = (self.offset_axis + 1) % 3
                else:
                    self.axis = (self.axis + 1) % 3
            elif self.key_ctrl:
                self.angle = max(0, self.angle - angle_factor)
            else:
                self.segments = max(3, self.segments - segment_factor)
                
            self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.key_ctrl_alt:
                self.offset += self.mouse_value
            elif self.key_ctrl:
                self.angle = max(0, min(360, self.angle + self.mouse_value_mag))

            self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_offset_factor = 0.01

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

        self.axis = 2 # X (0), Y (1), Z (2)
        self.offset_axis = 1 # X (0), Y (1), Z (2)
        self.segments = 3
        self.angle = 360
        self.offset = 0

        self.add_smooth_shading(context)
        self.add_displace_modifier(context)
        self.add_screw_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.displace = mods[mod_displace]
        self.screw = mods[mod_screw]

        self.offset_prev = self.offset = self.displace.strength
        self.offset_axis_prev = self.offset_axis = {'X': 0, 'Y': 1, 'Z': 2}[self.displace.direction]
        self.axis_prev = self.axis = {'X': 0, 'Y': 1, 'Z': 2}[self.screw.axis]
        self.segments_prev = self.segments = self.screw.steps
        self.segments_prev = self.segments = self.screw.render_steps
        self.angle_prev = self.angle = degrees(self.screw.angle)


    def add_smooth_shading(self, context):
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        context.object.data.auto_smooth_angle = radians(30)


    def add_displace_modifier(self, context):
        displace = context.object.modifiers.new(mod_displace, 'DISPLACE')
        displace.mid_level = 0.5
        displace.space = 'LOCAL'
        
        self.displace = displace


    def add_screw_modifier(self, context):
        screw = context.object.modifiers.new(mod_screw, 'SCREW')
        screw.screw_offset = 0
        screw.use_merge_vertices = True 
        screw.merge_threshold = 0.0001
        screw.use_normal_calculate = True

        self.screw = screw
    

    def operate(self, context):
        self.displace.strength = self.offset
        self.displace.direction = ['X', 'Y', 'Z'][self.offset_axis]
        self.screw.axis = ['X', 'Y', 'Z'][self.axis]
        self.screw.steps = self.segments
        self.screw.render_steps = self.segments
        self.screw.angle = radians(self.angle)

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.screw.name)
            bpy.ops.object.modifier_remove(modifier=self.displace.name)

        if self.summoned:
            self.displace.strength = self.offset_prev
            self.displace.direction = ['X', 'Y', 'Z'][self.offset_axis_prev]
            self.screw.axis = ['X', 'Y', 'Z'][self.axis_prev]
            self.screw.steps = self.segments_prev
            self.screw.render_steps = self.segments_prev
            self.screw.angle = radians(self.angle_prev)

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Segments: {}".format(self.segments),
        "(±2)  |  Shift (±1)",
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers)
    
    draw_property(
        self,
        "Screw Axis [R]: {}  /  Offset Axis [O]: {}".format(['X', 'Y', 'Z'][self.axis], ['X', 'Y', 'Z'][self.offset_axis]),
        "Alt (Screw X, Y, Z)  |  Shift + Alt (Offset X, Y, Z)",
        active=self.key_alt,
        alt_mode=self.key_shift_alt)

    draw_property(
        self,
        "Angle: {0:.0f}°".format(self.angle),
        "Ctrl (±10)  |  Shift + Ctrl (±1)",
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True)

    draw_property(
        self,
        "Offset: {0:.3f}".format(self.offset),
        "Ctrl + Alt (±{0:.1f})  |  Shift + Ctrl + Alt (±{1:.1f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=self.key_ctrl_alt,
        alt_mode=self.key_shift_ctrl_alt,
        mouse_value=True)


def menu_func(self, context):
    self.layout.operator(ND_OT_screw.bl_idname, text=ND_OT_screw.bl_label)


def register():
    bpy.utils.register_class(ND_OT_screw)


def unregister():
    bpy.utils.unregister_class(ND_OT_screw)
    unregister_draw_handler()
