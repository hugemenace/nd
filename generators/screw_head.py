import bpy
import bmesh
import re
from mathutils import Vector
from math import radians
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys
from .. lib.assets import get_asset_path
from .. lib.objects import align_object_to_3d_cursor


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
            toggle_pin_overlay(self)

        elif self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        elif self.operator_passthrough:
            self.update_overlay_wrapper(context, event)

            return {'PASS_THROUGH'}

        elif self.key_increase_factor:
            if self.key_alt:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)
            elif self.key_ctrl:
                self.base_scale_factor = min(1, self.base_scale_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_alt:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)
            elif self.key_ctrl:
                self.base_scale_factor = max(0.001, self.base_scale_factor / 10.0)

        elif self.key_step_up:
            if self.key_no_modifiers:
                self.head_type_index = (self.head_type_index + 1) % len(self.objects)
                self.update_head_type(context)
            elif self.key_alt:
                self.offset += offset_factor
            elif self.key_ctrl:
                self.scale += scale_factor
            
        elif self.key_step_down:
            if self.key_no_modifiers:
                self.head_type_index = (self.head_type_index - 1) % len(self.objects)
                self.update_head_type(context)
            elif self.key_alt:
                self.offset -= offset_factor
            elif self.key_ctrl:
                self.scale -= scale_factor
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        self.operate(context)
        self.update_overlay_wrapper(context, event)

        return {'RUNNING_MODAL'}

    
    def update_overlay_wrapper(self, context, event):
        update_overlay(self, context, event, x_offset=290, lines=3)


    def invoke(self, context, event):
        self.base_offset_factor = 0.01
        self.base_scale_factor = 0.01

        self.head_type_index = 0
        self.offset = 0
        self.scale = 1

        self.target_object = context.active_object if len(context.selected_objects) > 0 else None

        filepath = get_asset_path('screw_heads')
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = data_from.objects
        
        self.obj = None
        self.objects = data_to.objects

        self.update_head_type(context)

        capture_modifier_keys(self)

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

        self.obj = self.objects[self.head_type_index]
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
        displace = self.obj.modifiers.new("ND — Offset", 'DISPLACE')
        displace.strength = self.offset
        displace.direction = 'Z'
        displace.space = 'LOCAL'

        self.displace = displace


    def operate(self, context):
        self.displace.strength = self.offset
        self.obj.scale = Vector((self.scale, self.scale, self.scale))


    def finish(self, context):
        objects_to_remove = [obj for obj in self.objects if obj.name != self.obj.name]
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
        self.finish(context)
        bpy.data.objects.remove(self.obj, do_unlink=True)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self,
        "Type: {0}".format(re.sub(r"(.+?)(\.[0-9]{3})$", r"\1", self.obj.name)),
        "Select the head type...",
        active=self.key_no_modifiers,
        alt_mode=False)

    draw_property(
        self, 
        "Offset: {0:.1f}".format(self.offset * 1000), 
        "Alt (±{0:.1f})  |  Shift + Alt (±{1:.1f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=self.key_alt,
        alt_mode=self.key_shift_alt)

    draw_property(
        self, 
        "Scale: {0:.2f}".format(self.scale), 
        "Ctrl (±{0:.2f})  |  Shift + Ctrl (±{1:.2f})".format(self.base_scale_factor, self.base_scale_factor / 10),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl)


def menu_func(self, context):
    self.layout.operator(ND_OT_screw_head.bl_idname, text=ND_OT_screw_head.bl_label)


def register():
    bpy.utils.register_class(ND_OT_screw_head)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_screw_head)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
