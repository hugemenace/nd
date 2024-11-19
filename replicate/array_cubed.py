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
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from .. lib.modifiers import new_modifier, remove_modifiers_starting_with
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, obj_moddable, ctx_objects_selected


mod_array_x = "Array³ X — ND"
mod_array_y = "Array³ Y — ND"
mod_array_z = "Array³ Z — ND"
mod_summon_list = [mod_array_x, mod_array_y, mod_array_z]

IDX_MOD      = 0
IDX_COUNT    = 1
IDX_OFFSET   = 2
IDX_RELATIVE = 3

class ND_OT_array_cubed(BaseOperator):
    bl_idname = "nd.array_cubed"
    bl_label = "Array³"
    bl_description = """Array an object in up to three dimensions
CTRL — Remove existing modifiers"""


    def do_modal(self, context, event):
        relative_offset_step_size = 0.1 if self.key_shift else 1

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.count_streams[self.axis] = update_stream(self.count_streams[self.axis], event.type)
                self.axes[self.axis][IDX_COUNT] = int(get_stream_value(self.count_streams[self.axis]))
                self.dirty = True
            elif self.key_ctrl:
                self.offset_streams[self.axis] = update_stream(self.offset_streams[self.axis], event.type)
                if self.axes[self.axis][IDX_RELATIVE]:
                    self.axes[self.axis][IDX_OFFSET] = get_stream_value(self.offset_streams[self.axis])
                else:
                    self.axes[self.axis][IDX_OFFSET] = get_stream_value(self.offset_streams[self.axis], self.unit_scaled_factor)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.offset_streams[self.axis]) and self.hard_stream_reset or no_stream(self.offset_streams[self.axis]):
                    self.axes[self.axis][IDX_COUNT] = 1
                    self.axes[self.axis][IDX_OFFSET] = abs(self.axes[self.axis][IDX_OFFSET])
                    self.dirty = True
                self.count_streams[self.axis] = new_stream()
            elif self.key_ctrl:
                if has_stream(self.offset_streams[self.axis]) and self.hard_stream_reset or no_stream(self.offset_streams[self.axis]):
                    self.axes[self.axis][IDX_OFFSET] = 0
                    self.dirty = True
                self.offset_streams[self.axis] = new_stream()

        if pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        if pressed(event, {'D'}):
            relative = self.axes[self.axis][IDX_RELATIVE]
            self.axes[self.axis][IDX_RELATIVE] = not relative
            self.dirty = True

        if self.key_step_up:
            if no_stream(self.count_streams[self.axis]) and self.key_no_modifiers:
                new_count = self.axes[self.axis][IDX_COUNT] + (1 if self.axes[self.axis][IDX_OFFSET] >= 0 else -1)

                if new_count == 1:
                    self.axes[self.axis][IDX_COUNT] = 1
                    self.axes[self.axis][IDX_OFFSET] = self.axes[self.axis][IDX_OFFSET] * -1
                else:
                    self.axes[self.axis][IDX_COUNT] = new_count

                self.dirty = True
            elif no_stream(self.offset_streams[self.axis]) and self.key_ctrl:
                self.axes[self.axis][IDX_OFFSET] += relative_offset_step_size if self.axes[self.axis][IDX_RELATIVE] else self.step_size
                self.dirty = True

        if self.key_step_down:
            if no_stream(self.count_streams[self.axis]) and self.key_no_modifiers:
                new_count = self.axes[self.axis][IDX_COUNT] - (1 if self.axes[self.axis][IDX_OFFSET] >= 0 else -1)

                if new_count == 0:
                    self.axes[self.axis][IDX_COUNT] = 2
                    self.axes[self.axis][IDX_OFFSET] = self.axes[self.axis][IDX_OFFSET] * -1
                else:
                    self.axes[self.axis][IDX_COUNT] = new_count

                self.dirty = True
            elif no_stream(self.offset_streams[self.axis]) and self.key_ctrl:
                self.axes[self.axis][IDX_OFFSET] -= relative_offset_step_size if self.axes[self.axis][IDX_RELATIVE] else self.step_size
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.count_streams[self.axis]) and self.key_no_modifiers and abs(self.mouse_step) > 0:
                if self.mouse_step > 0:
                    new_count = self.axes[self.axis][IDX_COUNT] + (1 if self.axes[self.axis][IDX_OFFSET] >= 0 else -1)
                elif self.mouse_step < 0:
                    new_count = self.axes[self.axis][IDX_COUNT] - (1 if self.axes[self.axis][IDX_OFFSET] >= 0 else -1)

                if new_count == 0:
                    self.axes[self.axis][IDX_COUNT] = 2
                    self.axes[self.axis][IDX_OFFSET] = self.axes[self.axis][IDX_OFFSET] * -1
                else:
                    self.axes[self.axis][IDX_COUNT] = new_count

                self.dirty = True
            elif no_stream(self.offset_streams[self.axis]) and self.key_ctrl:
                self.axes[self.axis][IDX_OFFSET] += self.mouse_value
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        if event.ctrl:
            remove_modifiers_starting_with(context.selected_objects, 'Array³')
            return {'FINISHED'}

        self.dirty = False

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
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and obj_moddable(target_object) and ctx_objects_selected(context, 1)


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
            self.axes_prev[axis] = [array, array.count, offset, array.use_relative_offset]
            self.axes[axis] = [array, array.count, offset, array.use_relative_offset]

        if get_preferences().lock_overlay_parameters_on_recall:
            self.count_streams = [set_stream(self.axes[0][IDX_COUNT]), set_stream(self.axes[1][IDX_COUNT]), set_stream(self.axes[2][IDX_COUNT])]
            self.offset_streams = [set_stream(self.axes[0][IDX_OFFSET]), set_stream(self.axes[1][IDX_OFFSET]), set_stream(self.axes[2][IDX_OFFSET])]


    def add_array_modifier(self, context, name, axis):
        array = new_modifier(context.active_object, name, 'ARRAY', rectify=True)
        array.use_relative_offset = True

        self.axes[axis] = [array, 1, 2, True]


    def operate(self, context):
        for axis, conf in enumerate(self.axes):
            array, count, offset, relative = conf
            array.count = count
            array.relative_offset_displace = [offset if i == axis else 0 for i in range(3)]
            array.constant_offset_displace = [offset if i == axis else 0 for i in range(3)]
            array.use_relative_offset = relative
            array.use_constant_offset = not relative

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
                array, count, offset, relative = conf
                array.count = count
                array.relative_offset_displace = [offset if i == axis else 0 for i in range(3)]
                array.use_relative_offset = relative
                array.use_constant_offset = not relative

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Count: {0}".format(self.axes[self.axis][IDX_COUNT]),
        self.generate_step_hint(1),
        active=self.key_no_modifiers,
        alt_mode=False,
        mouse_value=True,
        input_stream=self.count_streams[self.axis])

    if self.axes[self.axis][IDX_RELATIVE]:
        draw_property(
            self,
            f"Offset: {(self.axes[self.axis][IDX_OFFSET]):.2f}",
            self.generate_key_hint("Ctrl", self.generate_step_hint(1, 0.1)),
            active=self.key_ctrl,
            alt_mode=self.key_shift_ctrl,
            mouse_value=True,
            input_stream=self.offset_streams[self.axis])
    else:
        draw_property(
            self,
            f"Offset: {(self.axes[self.axis][IDX_OFFSET] * self.display_unit_scale):.2f}{self.unit_suffix}",
            self.generate_key_hint("Ctrl", self.unit_step_hint),
            active=self.key_ctrl,
            alt_mode=self.key_shift_ctrl,
            mouse_value=True,
            input_stream=self.offset_streams[self.axis])

    draw_hint(
        self,
        "Displacement [D]: {}".format("Relative" if self.axes[self.axis][IDX_RELATIVE] else "Constant"),
        "Relative or constant displacement")

    draw_hint(
        self,
        "Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Axis replicate across (X, Y, Z)")


def register():
    bpy.utils.register_class(ND_OT_array_cubed)


def unregister():
    bpy.utils.unregister_class(ND_OT_array_cubed)
    unregister_draw_handler()
