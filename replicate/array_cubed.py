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
from .. lib.modifiers import new_modifier, rectify_mod_order


mod_array_x = "Array³ X — ND"
mod_array_y = "Array³ Y — ND"
mod_array_z = "Array³ Z — ND"
mod_summon_list = [mod_array_x, mod_array_y, mod_array_z]


class ND_OT_array_cubed(bpy.types.Operator):
    bl_idname = "nd.array_cubed"
    bl_label = "Array³"
    bl_description = "Array an object in up to three dimensions"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

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
                self.count_streams[self.axis] = update_stream(self.count_streams[self.axis], event.type)
                self.axes[self.axis][1] = int(get_stream_value(self.count_streams[self.axis]))
                self.dirty = True
            elif self.key_ctrl:
                self.offset_streams[self.axis] = update_stream(self.offset_streams[self.axis], event.type)
                self.axes[self.axis][2] = get_stream_value(self.offset_streams[self.axis])
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.count_streams[self.axis] = new_stream()
                self.axes[self.axis][1] = 1
                self.axes[self.axis][2] = abs(self.axes[self.axis][2])
                self.dirty = True
            elif self.key_ctrl:
                self.offset_streams[self.axis] = new_stream()
                self.axes[self.axis][2] = 0
                self.dirty = True

        elif pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        elif self.key_increase_factor:
            if self.key_ctrl:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_ctrl:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)

        elif self.key_step_up:
            if self.key_no_modifiers:
                new_count = self.axes[self.axis][1] + (1 if self.axes[self.axis][2] >= 0 else -1)

                if new_count == 1:
                    self.axes[self.axis][1] = 1
                    self.axes[self.axis][2] = self.axes[self.axis][2] * -1
                else:
                    self.axes[self.axis][1] = new_count
                
                self.dirty = True
            elif self.key_ctrl:
                self.axes[self.axis][2] += offset_factor
                self.dirty = True
            
        elif self.key_step_down:
            if self.key_no_modifiers:
                new_count = self.axes[self.axis][1] - (1 if self.axes[self.axis][2] >= 0 else -1)

                if new_count == 0:
                    self.axes[self.axis][1] = 2
                    self.axes[self.axis][2] = self.axes[self.axis][2] * -1
                else:
                    self.axes[self.axis][1] = new_count
                
                self.dirty = True
            elif self.key_ctrl:
                self.axes[self.axis][2] -= offset_factor
                self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.key_ctrl:
                self.axes[self.axis][2] += self.mouse_value
                self.dirty = True
        
        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_offset_factor = 0.01

        self.axis = 0
        self.axes = [None, None, None]

        self.count_streams = [new_stream(), new_stream(), new_stream()]
        self.offset_streams = [new_stream(), new_stream(), new_stream()]

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

        self.add_array_modifier(context, mod_array_x, 0)
        self.add_array_modifier(context, mod_array_y, 1)
        self.add_array_modifier(context, mod_array_z, 2)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.axes_prev = [None, None, None]
        for mod in mod_summon_list:
            array = mods[mod]
            axis = 0
            offset = 0
            for i in range(3):
                offset = array.relative_offset_displace[i]
                if offset != 0:
                    axis = i
                    offset = offset
                    break
            self.axes_prev[axis] = [array, array.count, offset]
            self.axes[axis] = [array, array.count, offset]


    def add_array_modifier(self, context, name, axis):
        array = new_modifier(context.active_object, name, 'ARRAY', rectify=True)
        array.use_relative_offset = True

        self.axes[axis] = [array, 1, 2]


    def operate(self, context):
        for axis, conf in enumerate(self.axes):
            array, count, offset = conf
            array.count = count
            array.relative_offset_displace = [offset if i == axis else 0 for i in range(3)]

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if not self.summoned:
            for mod in mod_summon_list:
                bpy.ops.object.modifier_remove(modifier=mod)

        if self.summoned:
            for axis, conf in enumerate(self.axes_prev):
                array, count, offset = conf
                array.count = count
                array.relative_offset_displace = [offset if i == axis else 0 for i in range(3)]
        
        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Count: {0:.0f}".format(self.axes[self.axis][1]),
        "Alt (±1)",
        active=self.key_no_modifiers,
        alt_mode=False,
        input_stream=self.count_streams[self.axis])

    draw_property(
        self,
        "Offset: {0:.3f}".format(self.axes[self.axis][2]),
        "Ctrl (±{0:.1f})  |  Shift + Ctrl (±{1:.1f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.offset_streams[self.axis])

    draw_hint(
        self,
        "Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Axis replicate across (X, Y, Z)")


def register():
    bpy.utils.register_class(ND_OT_array_cubed)


def unregister():
    bpy.utils.unregister_class(ND_OT_array_cubed)
    unregister_draw_handler()
