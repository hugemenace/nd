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
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.collections import move_to_utils_collection, isolate_in_utils_collection


class ND_OT_bool_inset(bpy.types.Operator):
    bl_idname = "nd.bool_inset"
    bl_label = "Inset/Outset"
    bl_description = "Perform a boolean operation on the selected objects"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        thickness_factor = (self.base_thickness_factor / 10.0) if self.key_shift else self.base_thickness_factor

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

        elif pressed(event, {'M'}):
            self.outset = not self.outset
            self.dirty = True

        elif self.key_increase_factor:
            if self.key_no_modifiers:
                self.base_thickness_factor = min(1, self.base_thickness_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_no_modifiers:
               self.base_thickness_factor = max(0.001, self.base_thickness_factor / 10.0)

        elif self.key_step_up:
            if self.key_no_modifiers:
                self.thickness += thickness_factor
            elif self.key_alt:
                self.outset = not self.outset

            self.dirty = True
            
        elif self.key_step_down:
            if self.key_no_modifiers:
                self.thickness = max(0, self.thickness - thickness_factor)
            elif self.key_alt:
                self.outset = not self.outset

            self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.key_no_modifiers:
                self.thickness = max(0, self.thickness + self.mouse_value)

            self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_thickness_factor = 0.01

        self.thickness = 0.02
        self.outset = False

        solver = 'FAST' if get_preferences().use_fast_booleans else 'EXACT'

        a, b = context.selected_objects
        self.reference_obj = a if a.name != context.object.name else b
        
        self.target_obj = context.object

        self.intersecting_obj = context.object.copy()
        self.intersecting_obj.data = context.object.data.copy()
        self.intersecting_obj.animation_data_clear()
        context.collection.objects.link(self.intersecting_obj)

        self.boolean_diff = self.target_obj.modifiers.new("Inset/Outset — ND Bool", 'BOOLEAN')
        self.boolean_diff.operation = 'UNION' if self.outset else 'DIFFERENCE'
        self.boolean_diff.object = self.intersecting_obj
        self.boolean_diff.solver = solver

        self.solidify = self.intersecting_obj.modifiers.new("Thickness — ND Bool", 'SOLIDIFY')
        self.solidify.use_even_offset = True
        self.solidify.offset = 0

        self.boolean_isect = self.intersecting_obj.modifiers.new("Intersection — ND Bool", 'BOOLEAN')
        self.boolean_isect.operation = 'INTERSECT'
        self.boolean_isect.object = self.reference_obj
        self.boolean_isect.solver = solver

        self.reference_obj_display_type_prev = self.reference_obj.display_type
        self.reference_obj_hide_render_prev = self.reference_obj.hide_render
        self.reference_obj_name_prev = self.reference_obj.name

        self.reference_obj.display_type = 'WIRE'
        self.reference_obj.hide_render = True
        self.reference_obj.name = " — ".join(['Bool', self.reference_obj.name])
        self.reference_obj.data.name = self.reference_obj.name
        self.reference_obj.hide_set(True)
        
        self.intersecting_obj.display_type = 'WIRE'
        self.intersecting_obj.hide_render = True
        self.intersecting_obj.name = " — ".join(['Bool', self.intersecting_obj.name])
        self.intersecting_obj.data.name = self.intersecting_obj.name

        self.reference_obj.parent = self.target_obj
        self.intersecting_obj.parent = self.target_obj

        self.reference_obj.matrix_parent_inverse = self.target_obj.matrix_world.inverted()
        self.intersecting_obj.matrix_parent_inverse = self.target_obj.matrix_world.inverted()

        bpy.ops.object.select_all(action='DESELECT')

        self.operate(context)   

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 2 and all(obj.type == 'MESH' for obj in context.selected_objects)

    
    def operate(self, context):
        self.solidify.thickness = self.thickness
        self.boolean_diff.operation = 'UNION' if self.outset else 'DIFFERENCE'

        self.dirty = False


    def finish(self, context):
        self.reference_obj.hide_set(False)

        move_to_utils_collection(self.reference_obj)
        move_to_utils_collection(self.intersecting_obj)

        isolate_in_utils_collection([self.reference_obj, self.intersecting_obj])

        bpy.ops.object.select_all(action='DESELECT')
        self.reference_obj.select_set(True)
        self.intersecting_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_obj

        unregister_draw_handler()


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.boolean_diff.name)
        bpy.data.meshes.remove(self.intersecting_obj.data, do_unlink=True)

        self.reference_obj.display_type = self.reference_obj_display_type_prev
        self.reference_obj.hide_render = self.reference_obj_hide_render_prev
        self.reference_obj.name = self.reference_obj_name_prev
        self.reference_obj.data.name = self.reference_obj_name_prev
        self.reference_obj.parent = None
        self.reference_obj.hide_set(False)
        
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Thickness: {0:.1f}".format(self.thickness * 1000), 
        "(±{0:.1f})  |  Shift + (±{1:.1f})".format(self.base_thickness_factor * 1000, (self.base_thickness_factor / 10) * 1000),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True)

    draw_property(
        self, 
        "Mode [M]: {0}".format('Outset' if self.outset else 'Inset'),
        "(Inset, Outset)",
        active=self.key_alt,
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_bool_inset.bl_idname, text=ND_OT_bool_inset.bl_label)


def register():
    bpy.utils.register_class(ND_OT_bool_inset)


def unregister():
    bpy.utils.unregister_class(ND_OT_bool_inset)
    unregister_draw_handler()
