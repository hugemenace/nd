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
from .. lib.events import capture_modifier_keys, pressed
from .. lib.collections import move_to_utils_collection
from .. lib.preferences import get_preferences
from .. lib.objects import set_origin


mod_array = 'Circular Array — ND CA'
mod_summon_list = [mod_array]


class ND_OT_circular_array(bpy.types.Operator):
    bl_idname = "nd.circular_array"
    bl_label = "Circular Array"
    bl_description = """Array an object around another in a circular fashion
ALT — Use faux origin translation (for origin-reliant geometry)
SHIFT — Do not place rotator object in utils collection
"""
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        angle_factor = 1 if self.key_shift else 15
        count_factor = 1 if self.key_shift else 2

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

        elif self.key_step_up:
            if self.key_alt:
                self.axis = (self.axis + 1) % 3
            elif self.key_ctrl:
                self.angle = min(360, self.angle + angle_factor)
            else:
                self.count = 2 if self.count == 1 else self.count + count_factor

            self.dirty = True
            
        elif self.key_step_down:
            if self.key_alt:
                self.axis = (self.axis - 1) % 3
            elif self.key_ctrl:
                self.angle = max(-360, self.angle - angle_factor)
            else:
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

            self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.skip_utils = event.shift
        self.faux_origin = event.alt

        self.dirty = False
        self.axis = 2
        self.count = 2
        self.angle = 360

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
        if context.mode == 'OBJECT' and len(context.selected_objects) == 2:
            a, b = context.selected_objects
            reference_obj = a if a.name != context.object.name else b

            return reference_obj.type == 'MESH'
        elif context.mode == 'OBJECT' and len(context.selected_objects) == 1 and context.object.type == 'MESH':
            return True
        else:
            return False


    def prepare_new_operator(self, context):
        self.summoned = False

        a, b = context.selected_objects
        self.reference_obj = a if a.name != context.object.name else b
        self.rotator_obj = context.active_object

        self.reference_obj_prev_location = self.reference_obj.location.copy()
        self.reference_obj_prev_rotation = self.reference_obj.rotation_euler.copy()
        self.reference_obj_prev_matrix_world = self.reference_obj.matrix_world.copy()
        
        self.new_empty = False
        if self.rotator_obj.type != 'EMPTY':
            empty_rotator_obj = bpy.data.objects.new("empty", None)
            bpy.context.scene.collection.objects.link(empty_rotator_obj)
            empty_rotator_obj.empty_display_size = 1
            empty_rotator_obj.empty_display_type = 'PLAIN_AXES'
            empty_rotator_obj.parent = self.rotator_obj
            empty_rotator_obj.location = (0, 0, 0)
            empty_rotator_obj.rotation_euler = (0, 0, 0)
            empty_rotator_obj.scale = (1, 1, 1)

            self.rotator_obj = empty_rotator_obj
            self.new_empty = True

        if self.faux_origin:
            bpy.ops.nd.set_origin()
        else:
            mx = self.rotator_obj.matrix_world
            set_origin(self.reference_obj, mx)

        self.rotation_snapshot = self.rotator_obj.rotation_euler.copy()
        bpy.data.objects[self.reference_obj.name]["NDCA_rotation_snapshot"] = self.rotation_snapshot.copy()

        self.reference_obj.rotation_euler = context.active_object.rotation_euler.copy()

        self.add_array_modifier()

    
    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.array = mods[mod_array]
        self.reference_obj = context.object
        self.rotator_obj = self.array.offset_object

        if self.rotator_obj is None:
            bpy.ops.object.modifier_remove(modifier=self.array.name)
            self.prepare_new_operator(context)
            return

        self.angle = self.angle_prev = bpy.data.objects[self.reference_obj.name]["NDCA_angle"]
        self.axis = self.axis_prev = bpy.data.objects[self.reference_obj.name]["NDCA_axis"]
        self.rotation_snapshot = self.rotation_snapshot_prev = bpy.data.objects[self.reference_obj.name]["NDCA_rotation_snapshot"]
        self.count = self.count_prev = self.array.count


    def add_array_modifier(self):
        array = self.reference_obj.modifiers.new(mod_array, 'ARRAY')
        array.use_relative_offset = False
        array.use_object_offset = True
        array.offset_object = self.rotator_obj

        self.array = array
    

    def operate(self, context):
        self.set_operational_state(self.count, self.angle, self.axis, self.rotation_snapshot)

        self.dirty = False


    def set_operational_state(self, count, angle, axis, rotation_snapshot):
        corrected_count = count if abs(angle) == 360 else count - 1
        final_rotation = radians(angle / corrected_count)
        rotation_axis = ['X', 'Y', 'Z'][axis]

        bpy.data.objects[self.reference_obj.name]["NDCA_angle"] = angle
        bpy.data.objects[self.reference_obj.name]["NDCA_axis"] = axis

        self.rotator_obj.rotation_euler = rotation_snapshot
        self.rotator_obj.rotation_euler.rotate_axis(rotation_axis, final_rotation)

        self.array.count = count


    def select_reference_obj(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.reference_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_obj


    def finish(self, context):
        if not self.summoned:
            if not self.skip_utils:
                move_to_utils_collection(self.rotator_obj)

            self.select_reference_obj(context)
            self.rotator_obj.parent = self.reference_obj
            self.rotator_obj.matrix_parent_inverse = self.reference_obj.matrix_world.inverted()

        unregister_draw_handler()


    def revert(self, context):
        if self.summoned:
            self.set_operational_state(self.count_prev, self.angle_prev, self.axis_prev, self.rotation_snapshot_prev)

        if not self.summoned:
            self.rotator_obj.rotation_euler = self.rotation_snapshot
            self.select_reference_obj(context)
            bpy.ops.object.modifier_remove(modifier=self.array.name)
            
            self.select_reference_obj(context)

            self.reference_obj.rotation_euler = self.reference_obj_prev_rotation

            if self.faux_origin:
                modifier_names = [mod.name for mod in self.reference_obj.modifiers]
                for name in modifier_names:
                    if "Axis Displace" in name:
                        bpy.ops.object.modifier_remove(modifier=name)

            if not self.faux_origin:
                set_origin(self.reference_obj, self.reference_obj_prev_matrix_world)

            self.reference_obj.location = self.reference_obj_prev_location

            if self.new_empty:
                bpy.context.scene.collection.objects.unlink(self.rotator_obj)
                bpy.data.objects.remove(self.rotator_obj)
        
        unregister_draw_handler()


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


def menu_func(self, context):
    self.layout.operator(ND_OT_circular_array.bl_idname, text=ND_OT_circular_array.bl_label)


def register():
    bpy.utils.register_class(ND_OT_circular_array)


def unregister():
    bpy.utils.unregister_class(ND_OT_circular_array)
    unregister_draw_handler()
