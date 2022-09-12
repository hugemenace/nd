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
from math import radians, degrees
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream


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

        elif self.key_numeric_input:
            if self.key_no_modifiers:
                self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                self.angle = get_stream_value(self.angle_input_stream)
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.angle_input_stream = new_stream()
                self.angle = degrees(context.active_object.data.auto_smooth_angle)
                self.dirty = True

        elif pressed(event, {'A'}):
            self.commit_auto_smooth = not self.commit_auto_smooth
            self.dirty = True

        elif self.key_step_up:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = min(180, self.angle + angle_factor)
                self.dirty = True
            
        elif self.key_step_down:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = max(0, self.angle - angle_factor)
                self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.angle_input_stream) and self.key_no_modifiers:
                self.angle = max(0, min(180, self.angle + self.mouse_value_mag))
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_angle_factor = 15
        self.angle = degrees(context.active_object.data.auto_smooth_angle)
        self.commit_auto_smooth = False

        self.angle_input_stream = new_stream()

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
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'

    
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
            context.active_object.data.use_auto_smooth = True
            context.active_object.data.auto_smooth_angle = radians(self.angle)

        unregister_draw_handler()


    def revert(self, context):
        self.clear_edges(context)
        bpy.ops.object.mode_set(mode='OBJECT')

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Angle: {0:.2f}°".format(self.angle),
        "(±{0:.0f})  |  Shift + (±1)".format(self.base_angle_factor),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.angle_input_stream)

    draw_hint(
        self,
        "Sync Auto Smooth [A]: {0}".format("Yes" if self.commit_auto_smooth else "No"),
        "Synchronize auto-smooth with seams angle on complete")
    

def register():
    bpy.utils.register_class(ND_OT_seams)


def unregister():
    bpy.utils.unregister_class(ND_OT_seams)
    unregister_draw_handler()
