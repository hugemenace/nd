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
import re
from mathutils import Vector, Matrix
from math import radians
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys
from .. lib.assets import get_asset_path
from .. lib.objects import align_object_to_3d_cursor, get_real_active_object
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream
from .. lib.modifiers import new_modifier


mod_displace = "Offset — ND SH"


class ND_OT_screw_head(BaseOperator):
    bl_idname = "nd.screw_head"
    bl_label = "Screw Head"
    bl_description = "Quickly create a variety of common screw heads"


    def do_modal(self, context, event):
        scale_factor = 0.1 if self.key_shift else 1

        if self.key_numeric_input:
            if self.key_alt:
                self.scale_input_stream = update_stream(self.scale_input_stream, event.type)
                self.scale = get_stream_value(self.scale_input_stream, 0.01)
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = update_stream(self.offset_input_stream, event.type)
                self.offset = get_stream_value(self.offset_input_stream, self.unit_scaled_factor)
                self.dirty = True

        if self.key_reset:
            if self.key_alt:
                if has_stream(self.scale_input_stream) and self.hard_stream_reset or no_stream(self.scale_input_stream):
                    self.scale = 1
                    self.dirty = True
                self.scale_input_stream = new_stream()
            elif self.key_ctrl:
                if has_stream(self.offset_input_stream) and self.hard_stream_reset or no_stream(self.offset_input_stream):
                    self.offset = 0
                    self.dirty = True
                self.offset_input_stream = new_stream()

        if self.key_step_up:
            if self.key_no_modifiers:
                self.head_type_index = (self.head_type_index + 1) % len(self.objects)
                self.update_head_type(context)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.step_size
                self.dirty = True
            elif no_stream(self.scale_input_stream) and self.key_alt:
                self.scale += scale_factor
                self.dirty = True

        if self.key_step_down:
            if self.key_no_modifiers:
                self.head_type_index = (self.head_type_index - 1) % len(self.objects)
                self.update_head_type(context)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset -= self.step_size
                self.dirty = True
            elif no_stream(self.scale_input_stream) and self.key_alt:
                self.scale -= scale_factor
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.key_no_modifiers:
                self.head_type_index = (self.head_type_index + self.mouse_step) % len(self.objects)
                self.update_head_type(context)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.mouse_value
                self.dirty = True
            elif no_stream(self.scale_input_stream) and self.key_alt:
                self.scale += self.mouse_value
                self.dirty = True


    def do_invoke(self, context, event):
        self.dirty = False

        self.head_type_index = 0
        self.offset = 0
        self.scale = 1

        self.offset_input_stream = new_stream()
        self.scale_input_stream = new_stream()

        self.target_object = get_real_active_object(context)

        custom_objects = []
        custom_file = get_preferences().custom_screw_heads_path
        if custom_file.endswith(".blend"):
            with bpy.data.libraries.load(custom_file) as (custom_data_from, custom_data_to):
                custom_data_to.objects = custom_data_from.objects
                custom_objects = custom_data_to.objects

        filepath = get_asset_path('screw_heads')
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = data_from.objects

        self.obj = None
        self.obj_matrix_basis = None
        self.objects = data_to.objects + custom_objects
        self.objects = [(obj, re.sub(r"(.+?)(\.[0-9]{3})$", r"\1", obj.name), True if obj in custom_objects else False) for obj in self.objects]

        self.update_head_type(context)
        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def update_head_type(self, context):
        if self.obj != None:
            bpy.context.collection.objects.unlink(self.obj)

        self.obj = self.objects[self.head_type_index][0]
        bpy.context.collection.objects.link(self.obj)

        if self.target_object:
            self.obj.location = self.target_object.location
            if self.target_object.rotation_mode == 'XYZ':
                self.obj.rotation_euler = self.target_object.rotation_euler
            self.obj.scale = Vector((self.scale, self.scale, self.scale))
        else:
            align_object_to_3d_cursor(self, context)

        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)
        bpy.context.view_layer.objects.active = self.obj

        if self.obj_matrix_basis == None:
            self.obj_matrix_basis = self.obj.matrix_basis.copy()


    def operate(self, context):
        self.obj.matrix_basis = self.obj_matrix_basis @ Matrix.Translation((0.0, 0.0, self.offset))
        self.obj.scale = Vector((self.scale, self.scale, self.scale))

        self.dirty = False


    def finish(self, context):
        objects_to_remove = [obj[0] for obj in self.objects if obj[0].name != self.obj.name]
        for obj in objects_to_remove:
            bpy.data.meshes.remove(obj.data, do_unlink=True)

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        name = "ND — {} Head".format(re.sub(r"(.+?)(\.[0-9]{3})$", r"\1", self.obj.name))
        self.obj.name = name
        self.obj.data.name = name

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        unregister_draw_handler()


    def revert(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        for obj in self.objects:
            bpy.data.meshes.remove(obj[0].data, do_unlink=True)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Type: {0}".format(self.objects[self.head_type_index][1]),
        "Select from {} types".format("custom" if self.objects[self.head_type_index][2] else "built-in"),
        active=self.key_no_modifiers,
        mouse_value=True,
        alt_mode=False)

    draw_property(
        self,
        "Scale: {0:.2f}%".format(self.scale * 100),
        self.generate_key_hint("Alt", self.generate_step_hint("100%", "10%")),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.scale_input_stream)

    draw_property(
        self,
        f"Offset: {(self.offset * self.display_unit_scale):.2f}{self.unit_suffix}",
        self.generate_key_hint("Ctrl", self.unit_step_hint),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.offset_input_stream)


def register():
    bpy.utils.register_class(ND_OT_screw_head)


def unregister():
    bpy.utils.unregister_class(ND_OT_screw_head)
    unregister_draw_handler()
