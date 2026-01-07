# ███╗   ██╗██████╗
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝
#
# ND (Non-Destructive) Blender Add-on
# Copyright (C) 2024 Tristan S. & Ian J. (HugeMenace)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ---
# Contributors: Tristo (HM)
# ---

import bpy
import bmesh
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.polling import ctx_obj_mode


class ND_OT_silhouette(BaseOperator):
    bl_idname = "nd.silhouette"
    bl_label = "Silhouette"
    bl_description = "Apply flat black shading all objects in the viewport to help assess thier silhouette"
    bl_options = {'UNDO'}


    def do_modal(self, context, event):
        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if pressed(event, {'D'}):
            self.inverted = not self.inverted
            self.dirty = True

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}


    def do_invoke(self, context, event):
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
        return ctx_obj_mode(context)


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

    display_str = "Inverted" if self.inverted else "Normal"
    draw_hint(
        self,
        f"Display [D]: {display_str}",
        "Invert the object and viewport colors")


def register():
    bpy.utils.register_class(ND_OT_silhouette)


def unregister():
    bpy.utils.unregister_class(ND_OT_silhouette)
    unregister_draw_handler()
