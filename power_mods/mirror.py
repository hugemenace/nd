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
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler


class ND_OT_mirror(bpy.types.Operator):
    bl_idname = "nd.mirror"
    bl_label = "Mirror"
    bl_description = "Mirror an object in isolation, or across another object"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

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

        elif pressed(event, {'F'}):
            self.flip = not self.flip
            self.dirty = True

        elif self.key_step_up:
            if self.key_alt:
                self.flip = not self.flip
            else:
                self.axis = (self.axis + 1) % 3

            self.dirty = True
            
        elif self.key_step_down:
            if self.key_alt:
                self.flip = not self.flip
            else:
                self.axis = (self.axis - 1) % 3

            self.dirty = True        
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.axis = 0
        self.flip = False
        self.reference_objs = [context.active_object]
        self.mirror_obj = None

        if len(context.selected_objects) >= 2:
            self.reference_objs = [obj for obj in context.selected_objects if obj != context.active_object]
            self.mirror_obj = context.active_object

        self.add_mirror_modifiers()
        self.operate(context)

        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        init_axis(self, self.reference_objs[0] if self.mirror_obj is None else self.mirror_obj, self.axis)
        register_axis_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            if len(context.selected_objects) == 1 and context.object.type == 'MESH':
                return True

            if len(context.selected_objects) >= 2:
                return all(obj.type == 'MESH' for obj in context.selected_objects if obj.name != context.object.name)


    def add_mirror_modifiers(self):
        self.mirrors = []

        for obj in self.reference_objs:
            mirror = obj.modifiers.new('Mirror — ND', 'MIRROR')
            mirror.use_clip = True
            mirror.merge_threshold = 0.0001

            if self.mirror_obj != None:
                mirror.mirror_object = self.mirror_obj

            self.mirrors.append(mirror)
    

    def operate(self, context):
        for mirror in self.mirrors:
            for i in range(3):
                active = self.axis == i
                mirror.use_axis[i] = active
                mirror.use_bisect_axis[i] = active
                mirror.use_bisect_flip_axis[i] = self.flip and active

        self.dirty = False


    def select_reference_objs(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in self.reference_objs:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_objs[0]


    def finish(self, context):
        self.select_reference_objs(context)

        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        self.select_reference_objs(context)

        for obj in self.reference_objs:
            obj.modifiers.remove(self.mirrors[self.reference_objs.index(obj)])

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Axis [R]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "X, Y, Z",
        active=self.key_no_modifiers,
        alt_mode=False)

    draw_property(
        self, 
        "Flipped [F]: {}".format('Yes' if self.flip else 'No'),
        "Alt (Yes, No)",
        active=self.key_alt,
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_mirror.bl_idname, text=ND_OT_mirror.bl_label)


def register():
    bpy.utils.register_class(ND_OT_mirror)


def unregister():
    bpy.utils.unregister_class(ND_OT_mirror)
    unregister_draw_handler()
