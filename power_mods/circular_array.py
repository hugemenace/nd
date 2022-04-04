import bpy
import bmesh
from math import radians
from mathutils import Euler
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys


class ND_OT_circular_array(bpy.types.Operator):
    bl_idname = "nd.circular_array"
    bl_label = "Circular Array"
    bl_description = "Array an object around another in a circular fashion"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        angle_factor = 1 if self.key_shift else 15

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

        elif self.key_step_up:
            if self.key_alt:
                self.count = self.count + 1
            elif self.key_ctrl:
                self.angle = min(360, self.angle + angle_factor)
            else:
                self.axis = (self.axis + 1) % 3

            self.dirty = True
            
        elif self.key_step_down:
            if self.key_alt:
                self.count = max(2, self.count - 1)
            elif self.key_ctrl:
                self.angle = max(0, self.angle - angle_factor)
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
        self.axis = 2
        self.count = 2
        self.angle = 360

        a, b = context.selected_objects
        self.reference_obj = a if a.name != context.object.name else b
        self.rotator_obj = context.active_object

        self.rotation_snapshot = self.rotator_obj.rotation_euler.copy()
        self.add_array_modifier()
        self.operate(context)

        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 2


    def add_array_modifier(self):
        array = self.reference_obj.modifiers.new('Circular Array — ND', 'ARRAY')
        array.use_relative_offset = False
        array.use_object_offset = True
        array.offset_object = self.rotator_obj

        self.array = array
    

    def operate(self, context):
        count = self.count if self.angle == 360 else self.count - 1
        final_rotation = radians(self.angle / count)
        rotation_axis = ['X', 'Y', 'Z'][self.axis]

        self.rotator_obj.rotation_euler = self.rotation_snapshot
        self.rotator_obj.rotation_euler.rotate_axis(rotation_axis, final_rotation)

        self.array.count = self.count

        self.dirty = False


    def select_reference_obj(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.reference_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_obj


    def finish(self, context):
        self.select_reference_obj(context)

        unregister_draw_handler()


    def revert(self, context):
        self.rotator_obj.rotation_euler = self.rotation_snapshot
        self.select_reference_obj(context)
        bpy.ops.object.modifier_remove(modifier=self.array.name)
        
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Axis: {}".format(['X', 'Y', 'Z'][self.axis]),
        "X, Y, Z",
        active=self.key_no_modifiers,
        alt_mode=False)

    draw_property(
        self, 
        "Count: {}".format(self.count),
        "Alt (±1)",
        active=self.key_alt,
        alt_mode=False)

    draw_property(
        self, 
        "{}".format('Full (360°)' if self.angle == 360 else "Angle: {}°".format(self.angle)),
        "Ctrl (±15)  |  Shift (±1)",
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl)


def menu_func(self, context):
    self.layout.operator(ND_OT_circular_array.bl_idname, text=ND_OT_circular_array.bl_label)


def register():
    bpy.utils.register_class(ND_OT_circular_array)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_circular_array)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
