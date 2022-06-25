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
import re
from mathutils import Vector
from math import radians
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys
from .. lib.assets import get_asset_path
from .. lib.objects import align_object_to_3d_cursor
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import new_modifier


mod_displace = "Offset — ND SH"


class ND_OT_screw_head(bpy.types.Operator):
    bl_idname = "nd.screw_head"
    bl_label = "Screw Head"
    bl_description = "Quickly create a variety of common screw heads"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        offset_factor = (self.base_offset_factor / 10.0) if self.key_shift else self.base_offset_factor
        scale_factor = (self.base_scale_factor / 10.0) if self.key_shift else self.base_scale_factor

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
            if self.key_alt:
                self.scale_input_stream = update_stream(self.scale_input_stream, event.type)
                self.scale = get_stream_value(self.scale_input_stream, 0.01)
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = update_stream(self.offset_input_stream, event.type)
                self.offset = get_stream_value(self.offset_input_stream, 0.001)
                self.dirty = True

        elif self.key_reset:
            if self.key_alt:
                self.scale_input_stream = new_stream()
                self.scale = 1
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = new_stream()
                self.offset = 0
                self.dirty = True

        elif self.key_increase_factor:
            if no_stream(self.offset_input_stream) and self.key_ctrl:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)
            elif no_stream(self.scale_input_stream) and self.key_alt:
                self.base_scale_factor = min(1, self.base_scale_factor * 10.0)

        elif self.key_decrease_factor:
            if no_stream(self.offset_input_stream) and self.key_ctrl:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)
            elif no_stream(self.scale_input_stream) and self.key_alt:
                self.base_scale_factor = max(0.001, self.base_scale_factor / 10.0)

        elif self.key_step_up:
            if self.key_no_modifiers:
                self.head_type_index = (self.head_type_index + 1) % len(self.objects)
                self.update_head_type(context)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += offset_factor
                self.dirty = True
            elif no_stream(self.scale_input_stream) and self.key_alt:
                self.scale += scale_factor
                self.dirty = True
            
        elif self.key_step_down:
            if self.key_no_modifiers:
                self.head_type_index = (self.head_type_index - 1) % len(self.objects)
                self.update_head_type(context)
                self.dirty = True
            elif no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset -= offset_factor
                self.dirty = True
            elif no_stream(self.scale_input_stream) and self.key_alt:
                self.scale -= scale_factor
                self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.mouse_value
            elif no_stream(self.scale_input_stream) and self.key_alt:
                self.scale += self.mouse_value

            self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_offset_factor = 0.01
        self.base_scale_factor = 0.01

        self.head_type_index = 0
        self.offset = 0
        self.scale = 1

        self.offset_input_stream = new_stream()
        self.scale_input_stream = new_stream()

        self.target_object = context.active_object if len(context.selected_objects) > 0 else None

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
            bpy.ops.object.modifier_remove(modifier=self.displace.name)
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

        self.add_displace_modifier(context)


    def add_displace_modifier(self, context):
        displace = new_modifier(self.obj, mod_displace, 'DISPLACE', rectify=False)
        displace.direction = 'Z'
        displace.space = 'LOCAL'
        displace.mid_level = 0

        self.displace = displace


    def operate(self, context):
        self.displace.strength = self.offset
        self.obj.scale = Vector((self.scale, self.scale, self.scale))

        self.dirty = False


    def finish(self, context):
        objects_to_remove = [obj[0] for obj in self.objects if obj[0].name != self.obj.name]
        for obj in objects_to_remove:
            bpy.data.meshes.remove(obj.data, do_unlink=True)

        if self.offset != 0:
            bpy.ops.object.modifier_apply(modifier=self.displace.name)
        else:
            bpy.ops.object.modifier_remove(modifier=self.displace.name)

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        name = "ND — {} Head".format(re.sub(r"(.+?)(\.[0-9]{3})$", r"\1", self.obj.name))
        self.obj.name = name
        self.obj.data.name = name

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
        "Browsing {} types...".format("custom" if self.objects[self.head_type_index][2] else "built-in"),
        active=self.key_no_modifiers,
        alt_mode=False)

    draw_property(
        self,
        "Scale: {0:.2f}%".format(self.scale * 100),
        "Alt (±{0:.2f}%)  |  Shift + Alt (±{1:.2f}%)".format(self.base_scale_factor * 100, (self.base_scale_factor / 10) * 100),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.scale_input_stream)

    draw_property(
        self,
        "Offset: {0:.2f}".format(self.offset * 1000), 
        "Ctrl (±{0:.2f})  |  Shift + Ctrl (±{1:.2f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.offset_input_stream)


def register():
    bpy.utils.register_class(ND_OT_screw_head)


def unregister():
    bpy.utils.unregister_class(ND_OT_screw_head)
    unregister_draw_handler()
