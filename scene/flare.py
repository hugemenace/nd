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
from math import radians, degrees, copysign
from random import random, uniform, randrange
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, obj_is, ctx_objects_selected


class ND_OT_flare(BaseOperator):
    bl_idname = "nd.flare"
    bl_label = "Flare"
    bl_description = "Adds a new lighting rig targeting selected objects position"
    bl_options = {'UNDO'}


    def do_modal(self, context, event):
        rotation_factor = 1 if self.key_shift else 15
        height_factor = 0.1 if self.key_shift else 1
        scale_factor = 0.01 if self.key_shift else 0.1
        energy_factor = 1000 if self.key_shift else 10000

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.rotation_input_stream = update_stream(self.rotation_input_stream, event.type)
                self.rotation = get_stream_value(self.rotation_input_stream)
                self.dirty = True
            elif self.key_alt:
                self.height_offset_input_stream = update_stream(self.height_offset_input_stream, event.type)
                self.height_offset = get_stream_value(self.height_offset_input_stream)
                self.dirty = True
            elif self.key_ctrl:
                self.scale_input_stream = update_stream(self.scale_input_stream, event.type)
                self.scale = get_stream_value(self.scale_input_stream)
                self.dirty = True
            elif self.key_ctrl_alt:
                self.energy_offset_input_stream = update_stream(self.energy_offset_input_stream, event.type)
                self.energy_offset = get_stream_value(self.energy_offset_input_stream)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                if has_stream(self.rotation_input_stream) and self.hard_stream_reset or no_stream(self.rotation_input_stream):
                    self.rotation = 0
                    self.dirty = True
                self.rotation_input_stream = new_stream()
            elif self.key_alt:
                if has_stream(self.height_offset_input_stream) and self.hard_stream_reset or no_stream(self.height_offset_input_stream):
                    self.height_offset = 0
                    self.dirty = True
                self.height_offset_input_stream = new_stream()
            elif self.key_ctrl:
                if has_stream(self.scale_input_stream) and self.hard_stream_reset or no_stream(self.scale_input_stream):
                    self.scale = 1
                    self.dirty = True
                self.scale_input_stream = new_stream()
            elif self.key_ctrl_alt:
                if has_stream(self.enery_offset_input_stream) and self.hard_stream_reset or no_stream(self.enery_offset_input_stream):
                    self.enery_offset = 0
                    self.dirty = True
                self.enery_offset_input_stream = new_stream()

        if pressed(event, {'R'}):
            self.generate_rig(context)

        if pressed(event, {'C'}):
            self.randomise_colors(context)

        if pressed(event, {'E'}):
            self.randomise_energy(context)

        if self.key_step_up:
            if no_stream(self.rotation_input_stream) and self.key_no_modifiers:
                self.rotation = (self.rotation + rotation_factor) % 360
            elif no_stream(self.height_offset_input_stream) and self.key_alt:
                self.height_offset += height_factor
            elif no_stream(self.scale_input_stream) and self.key_ctrl:
                self.scale += scale_factor
            elif no_stream(self.energy_offset_input_stream) and self.key_ctrl_alt:
                self.energy_offset += energy_factor

            self.dirty = True

        if self.key_step_down:
            if no_stream(self.rotation_input_stream) and self.key_no_modifiers:
                self.rotation = (self.rotation - rotation_factor) % 360
            elif no_stream(self.height_offset_input_stream) and self.key_alt:
                self.height_offset -= height_factor
            elif no_stream(self.scale_input_stream) and self.key_ctrl:
                self.scale = max(0, self.scale - scale_factor)
            elif no_stream(self.energy_offset_input_stream) and self.key_ctrl_alt:
                self.energy_offset -= energy_factor

            self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.height_offset_input_stream) and self.key_alt:
                self.height_offset += self.mouse_value
            elif no_stream(self.scale_input_stream) and self.key_ctrl:
                self.scale = max(0, self.scale + self.mouse_value)
            elif no_stream(self.energy_offset_input_stream) and self.key_ctrl_alt:
                self.energy_offset += self.mouse_value * 2500
            elif no_stream(self.rotation_input_stream) and self.key_no_modifiers:
                self.rotation = (self.rotation + self.mouse_value_mag) % 360

            self.dirty = True


    def reset_values(self, context):
        self.rotation_input_stream = new_stream()
        self.height_offset_input_stream = new_stream()
        self.energy_offset_input_stream = new_stream()
        self.scale_input_stream = new_stream()

        self.rotation = 0
        self.height_offset = 0
        self.scale = 1
        self.energy_offset = 0


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        self.dirty = False
        self.summoned = False
        self.regenerated_rig = False

        self.reset_values(context)

        self.last_rotation = 0
        self.last_height_offset = 0
        self.last_scale = 1
        self.last_energy_offset = 0

        self.rotation_input_stream = new_stream()
        self.height_offset_input_stream = new_stream()
        self.energy_offset_input_stream = new_stream()
        self.scale_input_stream = new_stream()

        if context.active_object.type == 'EMPTY':
            self.summoned = True
            self.empty = context.active_object
            self.rotation_prev = self.rotation = degrees(self.empty.rotation_euler[2])
            self.scale_prev = self.scale = self.empty.scale[0]

            existing_lights = [light for light in self.empty.children if light.type == 'LIGHT' and light.data.type == 'AREA']

            if not existing_lights:
                self.report({'ERROR'}, "Please select a valid Flare Lighting Rig")
                return {'CANCELLED'}

            self.lights = [(light, light.location[2], light.data.energy) for light in existing_lights]
            self.prev_lights_snapshot = [(light.data.energy, light.data.size, light.data.color.copy(), light.location.copy()) for light in existing_lights]
        else:
            self.create_empty(context)
            self.generate_rig(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and obj_is(target_object, {'MESH', 'EMPTY'}) and ctx_objects_selected(context, 1)


    def create_empty(self, context):
        empty = bpy.data.objects.new("empty", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.name = "ND — Flare Rig"
        empty.empty_display_size = 1
        empty.empty_display_type = 'SPHERE'
        empty.location = context.active_object.location.copy()
        empty.rotation_euler = (0, 0, radians(self.rotation))
        empty.scale = (1, 1, 1)

        self.empty = empty


    def remove_lights(self, context):
        for light, height, energy in self.lights:
            bpy.data.lights.remove(light.data, do_unlink=True)

        self.lights = []


    def generate_rig(self, context):
        self.regenerated_rig = True
        self.lights = getattr(self, 'lights', [])

        self.remove_lights(context)

        for i in range(0, randrange(3, 5)):
            self.lights.append(self.add_light(context))

        self.reset_values(context)
        self.operate(context)


    def randomise_colors(self, context):
        for light, height, energy in self.lights:
            light.data.color = (random(), random(), random())


    def randomise_energy(self, context):
        self.energy_offset_input_stream = new_stream()
        self.energy_offset = 0

        for i in range(0, len(self.lights)):
            light, height, energy = self.lights[i]
            light.data.energy = uniform(1000, 25000)
            self.lights[i] = (light, height, light.data.energy)


    def add_light(self, context, energy=None, size=None, color=None, location=None):
        light_data = bpy.data.lights.new(name="ND — Flare Light.001", type='AREA')
        light_data.energy = uniform(1000, 25000) if energy is None else energy
        light_data.size = uniform(5, 30) if size is None else size
        light_data.color = (random(), random(), random()) if color is None else color

        light_object = bpy.data.objects.new(name="ND — Flare Light.001", object_data=light_data)
        light_object.parent = self.empty

        bpy.context.scene.collection.objects.link(light_object)

        light_object.location = (uniform(-30, 30), uniform(-30, 30), uniform(5, 50)) if location is None else location

        damped_track = light_object.constraints.new('DAMPED_TRACK')
        damped_track.target = self.empty
        damped_track.track_axis = 'TRACK_NEGATIVE_Z'

        return (light_object, light_object.location[2], light_data.energy)


    def operate(self, context):
        if self.rotation != self.last_rotation:
            self.empty.rotation_euler = (0, 0, radians(self.rotation))
            self.last_rotation = self.rotation

        if self.scale != self.last_scale:
            self.empty.scale = (self.scale, self.scale, self.scale)
            self.last_scale = self.scale

        if self.height_offset != self.last_height_offset:
            for light, height, energy in self.lights:
                light.location[2] = height + self.height_offset
            self.last_height_offset = self.height_offset

        if self.energy_offset != self.last_energy_offset:
            for light, height, energy in self.lights:
                light.data.energy = max(0, energy + self.energy_offset)
            self.last_energy_offset = self.energy_offset

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        if self.summoned:
            self.empty.rotation_euler = (0, 0, radians(self.rotation_prev))
            self.empty.scale = (self.scale_prev, self.scale_prev, self.scale_prev)

            self.remove_lights(context)
            for energy, size, color, location in self.prev_lights_snapshot:
                self.lights.append(self.add_light(context, energy, size, color, location))
        else:
            self.remove_lights(context)
            bpy.data.objects.remove(self.empty, do_unlink=True)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Rotation: {0:.2f}".format(self.rotation),
        self.generate_step_hint(15, 1),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.rotation_input_stream)

    draw_property(
        self,
        "Height Offset: {0:.2f}".format(self.height_offset),
        self.generate_key_hint("Alt", self.generate_step_hint(1, 0.1)),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.height_offset_input_stream)

    draw_property(
        self,
        "Scale: {0:.2f}".format(self.scale),
        self.generate_key_hint("Ctrl", self.generate_step_hint(0.1, 0.01)),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.scale_input_stream)

    draw_property(
        self,
        "Energy Offset: {0:.1e}".format(self.energy_offset),
        self.generate_key_hint("Ctrl + Alt", self.generate_step_hint("10k", "1k")),
        active=self.key_ctrl_alt,
        alt_mode=self.key_shift_ctrl_alt,
        mouse_value=True,
        input_stream=self.energy_offset_input_stream)

    draw_hint(self, "New Rig [R]", "Generate a new randomised rig and reset light options")
    draw_hint(self, "New Colors [C]", "Generate new randomised colors for the lights")
    draw_hint(self, "New Energy [E]", "Generate new randomised energy for the lights")


def register():
    bpy.utils.register_class(ND_OT_flare)


def unregister():
    bpy.utils.unregister_class(ND_OT_flare)
    unregister_draw_handler()
