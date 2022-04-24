import bpy
import bmesh
from math import radians
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys
from .. lib.preferences import get_preferences


class ND_OT_smooth(bpy.types.Operator):
    bl_idname = "nd.smooth"
    bl_label = "Smooth Shading"
    bl_description = "Set and configure object smoothing properties"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        angle_factor = 1 if self.key_shift else self.base_angle_factor

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
            self.angle = min(180, self.angle + angle_factor)

            self.dirty = True
            
        elif self.key_step_down:
            self.angle = max(0, self.angle - angle_factor)

            self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            self.angle = max(0, min(180, self.angle + self.mouse_value_mag))

            self.dirty = True

        if self.dirty:
            self.operate(context)
            
        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_angle_factor = 15
        self.angle = 30

        self.add_smooth_shading(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.object.type == 'MESH'

    
    def add_smooth_shading(self, context):
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True


    def operate(self, context):
        context.object.data.auto_smooth_angle = radians(self.angle)

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Angle: {0:.0f}°".format(self.angle), 
        "(±{0:.0f})  |  Shift + (±1)".format(self.base_angle_factor),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True)


def menu_func(self, context):
    self.layout.operator(ND_OT_smooth.bl_idname, text=ND_OT_smooth.bl_label)


def register():
    bpy.utils.register_class(ND_OT_smooth)


def unregister():
    bpy.utils.unregister_class(ND_OT_smooth)
    unregister_draw_handler()
