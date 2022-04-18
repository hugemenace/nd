import bpy
import bmesh
from math import radians, degrees
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys
from .. lib.preferences import get_preferences


class ND_OT_seams(bpy.types.Operator):
    bl_idname = "nd.seams"
    bl_label = "UV Seams"
    bl_description = "Interactively set UV seams & sharp edges"
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
            if self.key_alt:
                self.commit_auto_smooth = not self.commit_auto_smooth
            else:
                self.angle = min(180, self.angle + angle_factor)

            self.dirty = True
            
        elif self.key_step_down:
            if self.key_alt:
                self.commit_auto_smooth = not self.commit_auto_smooth
            else:
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
        self.angle = degrees(context.object.data.auto_smooth_angle)
        self.commit_auto_smooth = False

        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'EDGE'})
        bpy.ops.mesh.select_all(action='DESELECT')

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1

    
    def operate(self, context):
        self.clear_edges(context)

        bpy.ops.mesh.edges_select_sharp(sharpness=radians(self.angle))

        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.mark_sharp(clear=False)

        bpy.ops.mesh.select_all(action='DESELECT')

        self.dirty = False


    def clear_edges(self, context):
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.mark_seam(clear=True)
        bpy.ops.mesh.mark_sharp(clear=True)

        bpy.ops.mesh.select_all(action='DESELECT')


    def finish(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')

        if self.commit_auto_smooth:
            bpy.ops.object.shade_smooth()
            context.object.data.use_auto_smooth = True
            context.object.data.auto_smooth_angle = radians(self.angle)

        unregister_draw_handler()


    def revert(self, context):
        self.clear_edges(context)
        bpy.ops.object.mode_set(mode='OBJECT')

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
    
    draw_property(
        self, 
        "Sync Auto Smooth: {0}".format("Yes" if self.commit_auto_smooth else "No"),
        "Alt (Yes / No)",
        active=self.key_alt,
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_seams.bl_idname, text=ND_OT_seams.bl_label)


def register():
    bpy.utils.register_class(ND_OT_seams)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_seams)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
