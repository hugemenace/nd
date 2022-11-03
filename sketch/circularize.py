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
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with


mod_bevel = "Bevel — ND CIRC"
mod_weld = "Weld — ND CIRC"
mod_summon_list = [mod_bevel, mod_weld]


class ND_OT_circularize(bpy.types.Operator):
    bl_idname = "nd.circularize"
    bl_label = "Circularize"
    bl_description = "Adds a vertex bevel operator to the selected plane to convert it into a circular shape"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        segment_factor = 1 if self.key_shift else 2

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
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=1))
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.segments_input_stream = new_stream()
                self.segments = 1
                self.dirty = True

        elif self.key_step_up:
            if no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
                self.dirty = True
        
        elif self.key_step_down:
            if no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = max(1, self.segments - segment_factor)
                self.dirty = True

        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}
        
        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = max(1, self.segments + self.mouse_step)
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND CIRC')

            return {'FINISHED'}

        self.dirty = False
        self.segments = 2

        self.segments_input_stream = new_stream()
        self.width_input_stream = new_stream()
        self.profile_input_stream = new_stream()

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


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.bevel = mods[mod_bevel]

        self.segments_prev = self.segments = self.bevel.segments


    def prepare_new_operator(self, context):
        self.summoned = False

        self.add_smooth_shading(context)
        self.add_bevel_modifier(context)


    def add_smooth_shading(self, context):
        bpy.ops.object.shade_smooth()
        context.active_object.data.use_auto_smooth = True
        context.active_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))


    def add_bevel_modifier(self, context):
        bevel = new_modifier(context.active_object, mod_bevel, 'BEVEL', rectify=False)
        bevel.affect = 'VERTICES'
        bevel.limit_method = 'NONE'
        bevel.offset_type = 'PERCENT'
        bevel.width_pct = 50

        self.bevel = bevel


    def add_weld_modifier(self, context):
        weld = new_modifier(context.active_object, mod_weld, 'WELD', rectify=False)
        weld.merge_threshold = 0.00001

        self.weld = weld


    def operate(self, context):
        self.bevel.segments = self.segments

        self.dirty = False


    def finish(self, context):
        if not self.summoned:
            self.add_weld_modifier(context)

        unregister_draw_handler()
    

    def revert(self, context):
        if self.summoned:
            self.bevel.segments = self.segments_prev

        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.bevel.name)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Segments: {}".format(self.segments), 
        "Alt (±2)  |  Shift (±1)",
        active=self.key_no_modifiers,
        mouse_value=True,
        input_stream=self.segments_input_stream)


def register():
    bpy.utils.register_class(ND_OT_circularize)


def unregister():
    bpy.utils.unregister_class(ND_OT_circularize)
    unregister_draw_handler()
