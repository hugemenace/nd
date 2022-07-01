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
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import new_modifier


mod_bevel = "Bevel — ND WNB"
mod_wn = "Weighted Normal — ND WNB"
mod_summon_list = [mod_bevel, mod_wn]


class ND_OT_weighted_normal_bevel(bpy.types.Operator):
    bl_idname = "nd.weighted_normal_bevel"
    bl_label = "WN Bevel"
    bl_description = "Adds a single segment bevel and a weighted normal modifier"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        width_factor = (self.base_width_factor / 10.0) if event.shift else self.base_width_factor

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
                self.width_input_stream = update_stream(self.width_input_stream, event.type)
                self.width = get_stream_value(self.width_input_stream, 0.001)
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.width_input_stream = new_stream()
                self.width = 0
                self.dirty = True

        elif pressed(event, {'W'}):
            self.target_object.show_wire = not self.target_object.show_wire
            self.target_object.show_in_front = not self.target_object.show_in_front

        elif pressed(event, {'A'}):
            self.angle = (self.angle + 1) % len(self.angles)

        elif self.key_increase_factor:
            if no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.base_width_factor = min(1, self.base_width_factor * 10.0)

        elif self.key_decrease_factor:
            if no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.base_width_factor = max(0.001, self.base_width_factor / 10.0)

        elif self.key_step_up:
            if no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width += width_factor
                self.dirty = True
            
        elif self.key_step_down:
            if no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(0, self.width - width_factor)
                self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(0, self.width + self.mouse_value)
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_width_factor = 0.001
        self.angles = [30, 45, 60]

        self.width_input_stream = new_stream()

        self.target_object = context.active_object

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
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'


    def prepare_new_operator(self, context):
        self.summoned = False

        self.width = 0.001
        self.angle = self.angles.index(int(get_preferences().default_smoothing_angle))

        self.add_smooth_shading(context)
        self.add_bevel_modifier(context)
        self.add_weighted_normal_modifer(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.bevel = mods[mod_bevel]
        self.wn = mods[mod_wn]

        self.width_prev = self.width = self.bevel.width
        try:
            self.angle_prev = self.angle = self.angles.index(int(degrees(self.bevel.angle_limit)))
        except:
            self.angle_prev = self.angle = self.angles.index(int(get_preferences().default_smoothing_angle))


    def add_smooth_shading(self, context):
        bpy.ops.object.shade_smooth()
        context.active_object.data.use_auto_smooth = True
        context.active_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))


    def add_bevel_modifier(self, context):
        bevel = new_modifier(context.active_object, mod_bevel, 'BEVEL', rectify=False)
        bevel.segments = 1
        bevel.offset_type = 'WIDTH'
        bevel.face_strength_mode = 'FSTR_AFFECTED'

        self.bevel = bevel
    

    def add_weighted_normal_modifer(self, context):
        wn = new_modifier(context.active_object, mod_wn, 'WEIGHTED_NORMAL', rectify=False)
        wn.weight = 100
        wn.use_face_influence = True

        self.wn = wn


    def operate(self, context):
        self.bevel.width = self.width
        self.bevel.angle_limit = radians(self.angles[self.angle])

        self.dirty = False


    def finish(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False
        unregister_draw_handler()


    def revert(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False

        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.bevel.name)
            bpy.ops.object.modifier_remove(modifier=self.wn.name)

        if self.summoned:
            self.bevel.width = self.width_prev
            self.bevel.angle_limit = radians(self.angles[self.angle_prev])

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self,
        "Width: {0:.2f}".format(self.width * 1000), 
        "(±{0:.2f})  |  Shift (±{1:.2f})".format(self.base_width_factor * 1000, (self.base_width_factor / 10) * 1000),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.width_input_stream)

    draw_hint(
        self,
        "Enhanced Wireframe [W]: {0}".format("Yes" if self.target_object.show_wire else "No"),
        "Display the objects's wireframe over solid shading")

    draw_hint(
        self,
        "Angle [A]: {0}°".format(self.angles[self.angle]),
        "Edge angle limit ({})".format(", ".join(["{0}°".format(a) for a in self.angles])))


def register():
    bpy.utils.register_class(ND_OT_weighted_normal_bevel)


def unregister():
    bpy.utils.unregister_class(ND_OT_weighted_normal_bevel)
    unregister_draw_handler()
