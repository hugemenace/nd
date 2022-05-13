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
from math import radians
from mathutils import Euler
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.events import capture_modifier_keys, pressed
from .. lib.collections import move_to_utils_collection, hide_utils_collection
from .. lib.preferences import get_preferences
from .. lib.objects import set_origin


mod_displace = 'Displace — ND CA'
mod_array = 'Circular Array — ND CA'
mod_summon_list = [mod_displace, mod_array]


class ND_OT_circular_array(bpy.types.Operator):
    bl_idname = "nd.circular_array"
    bl_label = "Circular Array"
    bl_description = "Array an object around another in a circular fashion"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        angle_factor = 1 if self.key_shift else 15
        count_factor = 1 if self.key_shift else 2
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

        elif self.key_increase_factor:
            if self.key_ctrl_alt:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_ctrl_alt:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)

        elif self.key_step_up:
            if self.key_alt:
                self.axis = (self.axis + 1) % 3
            elif self.key_ctrl:
                self.angle = min(360, self.angle + angle_factor)
            elif self.key_ctrl_alt:
                self.offset += offset_factor
            elif self.key_no_modifiers:
                self.count = 2 if self.count == 1 else self.count + count_factor

            self.dirty = True
            
        elif self.key_step_down:
            if self.key_alt:
                self.axis = (self.axis - 1) % 3
            elif self.key_ctrl:
                self.angle = max(-360, self.angle - angle_factor)
            elif self.key_ctrl_alt:
                self.offset -= offset_factor
            elif self.key_no_modifiers:
                self.count = max(2, self.count - count_factor)

            self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}
        
        if get_preferences().enable_mouse_values:
            if self.key_ctrl:
                self.angle = max(-360, min(360, self.angle + self.mouse_value_mag))
            elif self.key_ctrl_alt:
                self.offset += self.mouse_value

            self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False

        self.base_offset_factor = 0.001

        self.axis = 2
        self.count = 2
        self.angle = 360
        self.offset = 0
        self.single_obj_mode = len(context.selected_objects) == 1

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

        if self.single_obj_mode:
            init_axis(self, self.reference_obj, self.axis)
        else:
            init_axis(self, self.target_obj, self.axis)

        register_axis_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) == 2:
            a, b = context.selected_objects
            reference_obj = a if a.name != context.object.name else b

            return reference_obj.type == 'MESH'
        elif context.mode == 'OBJECT' and context.object.type == 'MESH':
            return True
        else:
            return False


    def prepare_new_operator(self, context):
        self.summoned = False

        if not self.single_obj_mode:
            a, b = context.selected_objects
            self.reference_obj = a if a.name != context.object.name else b
            self.target_obj = context.object
        else:
            self.reference_obj = context.object

        if not self.single_obj_mode:
            self.reference_obj_prev_location = self.reference_obj.location.copy()
            self.reference_obj_prev_rotation = self.reference_obj.rotation_euler.copy()
            self.reference_obj.location = context.object.location.copy()
            self.reference_obj.rotation_euler = context.object.rotation_euler.copy()

        self.rotator_obj = bpy.data.objects.new("empty", None)
        self.rotator_obj.name = "ND — Circular Array Rotator"
        bpy.context.scene.collection.objects.link(self.rotator_obj)
        self.rotator_obj.empty_display_size = 1
        self.rotator_obj.empty_display_type = 'PLAIN_AXES'
        self.rotator_obj.parent = self.reference_obj
        self.rotator_obj.location = (0, 0, 0)
        self.rotator_obj.rotation_euler = (0, 0, 0)
        self.rotator_obj.scale = (1, 1, 1)
        
        self.add_displace_tranform_modifiers()
        self.add_displace_modifier()
        self.add_array_modifier()

        self.select_reference_obj()

    
    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.displace = mods[mod_displace]
        self.array = mods[mod_array]
        self.reference_obj = context.object
        self.rotator_obj = self.array.offset_object

        if self.rotator_obj is None:
            return

        self.angle = self.angle_prev = bpy.data.objects[self.reference_obj.name]["NDCA_angle"]
        self.axis = self.axis_prev = bpy.data.objects[self.reference_obj.name]["NDCA_axis"]
        self.count = self.count_prev = self.array.count
        self.offset = self.offset_prev = self.displace.strength


    def add_array_modifier(self):
        array = self.reference_obj.modifiers.new(mod_array, 'ARRAY')
        array.use_relative_offset = False
        array.use_object_offset = True
        array.offset_object = self.rotator_obj

        self.array = array


    def add_displace_tranform_modifiers(self):
        self.displace_transforms = []

        if not self.single_obj_mode:
            for index, axis in enumerate(['X', 'Y', 'Z']):
                displace = self.reference_obj.modifiers.new("Translate {} — ND CA".format(axis), 'DISPLACE')
                displace.direction = axis
                displace.space = 'LOCAL'
                displace.mid_level = 0
                displace.show_in_editmode = True
                displace.show_on_cage = True
                displace.strength = self.reference_obj_prev_location[index] - self.reference_obj.location[index]

                self.displace_transforms.append(displace)


    def add_displace_modifier(self):
        displace = self.reference_obj.modifiers.new(mod_displace, 'DISPLACE')
        displace.direction = 'X'
        displace.space = 'LOCAL'
        displace.mid_level = 0
        displace.show_in_editmode = True
        displace.show_on_cage = True

        if self.single_obj_mode:
            self.offset = self.reference_obj.dimensions[self.axis]
            displace.strength = self.offset

        self.displace = displace
    

    def operate(self, context):
        altered_count = self.count if abs(self.angle) == 360 else self.count - 1
        rotation = radians(self.angle / altered_count)
        rotation_axis = ['X', 'Y', 'Z'][self.axis]

        self.rotator_obj.rotation_euler = (0, 0, 0)
        self.rotator_obj.rotation_euler.rotate_axis(rotation_axis, rotation)

        self.array.count = self.count

        if rotation_axis in ['Y', 'Z']:
            self.displace.direction = 'X'
        else:
            self.displace.direction = 'Y'

        self.displace.strength = self.offset

        bpy.data.objects[self.reference_obj.name]["NDCA_angle"] = self.angle
        bpy.data.objects[self.reference_obj.name]["NDCA_axis"] = self.axis

        self.dirty = False


    def select_reference_obj(self):
        bpy.ops.object.select_all(action='DESELECT')
        self.reference_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_obj


    def finish(self, context):
        if not self.summoned:
            move_to_utils_collection(self.rotator_obj)
            hide_utils_collection(True)

        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if self.summoned:
            self.angle = self.angle_prev
            self.axis = self.axis_prev
            self.count = self.count_prev
            self.offset = self.offset_prev

            self.operate(context)

        if not self.summoned:
            for displace in self.displace_transforms:
                self.reference_obj.modifiers.remove(displace)
            
            self.reference_obj.modifiers.remove(self.displace)
            self.reference_obj.modifiers.remove(self.array)
            
            self.reference_obj.location = self.reference_obj_prev_location
            self.reference_obj.rotation_euler = self.reference_obj_prev_rotation

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Count: {}".format(self.count),
        "(±2) | Shift (±1)",
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers)

    draw_property(
        self, 
        "Axis [R]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Alt (X, Y, Z)",
        active=self.key_alt,
        alt_mode=False)

    draw_property(
        self, 
        "Angle: {}".format('Circle (360°)' if abs(self.angle) == 360 else "Arc ({0:.1f}°)".format(self.angle)),
        "Ctrl (±15)  |  Shift + Ctrl (±1)",
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True)

    draw_property(
        self, 
        "Offset: {0:.1f}".format(self.offset * 1000), 
        "Ctrl + Alt (±{0:.1f})  |  Shift + Ctrl + Alt (±{1:.1f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=self.key_ctrl_alt,
        alt_mode=self.key_shift_ctrl_alt,
        mouse_value=True)


def menu_func(self, context):
    self.layout.operator(ND_OT_circular_array.bl_idname, text=ND_OT_circular_array.bl_label)


def register():
    bpy.utils.register_class(ND_OT_circular_array)


def unregister():
    bpy.utils.unregister_class(ND_OT_circular_array)
    unregister_draw_handler()
