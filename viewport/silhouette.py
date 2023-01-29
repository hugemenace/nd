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
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed


class ND_OT_silhouette(bpy.types.Operator):
    bl_idname = "nd.silhouette"
    bl_label = "Silhouette"
    bl_description = "Apply flat black shading all objects in the viewport to help assess thier silhouette"
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

        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif pressed(event, {'D'}):
            self.inverted = not self.inverted
            self.dirty = True

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        elif event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.inverted = False

        self.prev_light = context.space_data.shading.light
        self.prev_color_type = context.space_data.shading.color_type
        self.prev_single_color = context.space_data.shading.single_color
        self.prev_background_type = context.space_data.shading.background_type
        self.prev_background_color = context.space_data.shading.background_color
        self.prev_show_cavity = context.space_data.shading.show_cavity
        self.prev_show_object_outline = context.space_data.shading.show_object_outline

        context.space_data.shading.show_cavity = False
        context.space_data.shading.show_object_outline = False

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def operate(self, context):
        context.space_data.shading.light = 'FLAT'
        context.space_data.shading.color_type = 'SINGLE'
        context.space_data.shading.single_color = (0, 0, 0) if self.inverted else (1, 1, 1)
        context.space_data.shading.background_type = 'VIEWPORT'
        context.space_data.shading.background_color = (1, 1, 1) if self.inverted else (0, 0, 0)

        self.dirty = False


    def finish(self, context):
        self.revert(context)

        unregister_draw_handler()


    def revert(self, context):
        context.space_data.shading.light = self.prev_light
        context.space_data.shading.color_type = self.prev_color_type
        context.space_data.shading.single_color = self.prev_single_color
        context.space_data.shading.background_type = self.prev_background_type
        context.space_data.shading.background_color = self.prev_background_color
        context.space_data.shading.show_cavity = self.prev_show_cavity
        context.space_data.shading.show_object_outline = self.prev_show_object_outline

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_hint(
        self,
        "Display [D]: {0}".format("Inverted" if self.inverted else "Normal"),
        "Invert the object and viewport colors")


def register():
    bpy.utils.register_class(ND_OT_silhouette)


def unregister():
    bpy.utils.unregister_class(ND_OT_silhouette)
    unregister_draw_handler()
