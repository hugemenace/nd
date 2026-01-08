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
from .. lib.preferences import get_preferences
from .. lib.polling import ctx_obj_mode, list_ok, app_minor_version
from .. lib.objects import configure_object_as_util


class ND_OT_hydrate(BaseOperator):
    bl_idname = "nd.hydrate"
    bl_label = "Hydrate"
    bl_description = "Convert a boolean reference object into solidified geometry"
    bl_options = {'UNDO'}


    key_callbacks = {
        'C': lambda cls, context, event: cls.handle_toggle_clear_parent(context, event),
    }

    modal_config = {
        'MOVEMENT_PASSTHROUGH': True,
        'ON_CANCEL': lambda cls, context: cls.revert(context),
        'ON_CONFIRM': lambda cls, context: cls.finish(context),
    }


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context)
        return ctx_obj_mode(context) and list_ok(valid_objects)


    def do_modal(self, context, event):
        if self.key_step_up:
            if self.key_no_modifiers:
                self.active_collection = (self.active_collection + 1) % len(self.scene_collections)
                self.mark_dirty()

        if self.key_step_down:
            if self.key_no_modifiers:
                self.active_collection = (self.active_collection - 1) % len(self.scene_collections)
                self.mark_dirty()

        if get_preferences().enable_mouse_values:
            if self.key_no_modifiers and self.has_mouse_step:
                self.active_collection = (self.active_collection + self.mouse_step) % len(self.scene_collections)
                self.mark_dirty()


    def do_invoke(self, context, event):
        self.clear_parent = True
        self.scene_collections = [bpy.context.scene.collection]
        self.scene_collections.extend(bpy.context.scene.collection.children_recursive)
        self.collection_names = [c.name for c in self.scene_collections]
        self.active_collection = 0

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def handle_toggle_clear_parent(self, context, event):
        self.clear_parent = not self.clear_parent


    def get_valid_objects(self, context):
        return [obj for obj in context.selected_objects if obj.type == 'MESH']


    def finish(self, context):
        valid_objects = self.get_valid_objects(context)
        new_objects = []
        for obj in valid_objects:
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            new_obj.animation_data_clear()

            if self.clear_parent:
                world_matrix = new_obj.matrix_world.copy()
                new_obj.parent = None
                new_obj.matrix_world = world_matrix

            bpy.context.scene.collection.objects.link(new_obj)
            if self.active_collection != 0:
                bpy.context.scene.collection.objects.unlink(new_obj)
                self.scene_collections[self.active_collection].objects.link(new_obj)

            configure_object_as_util(new_obj, util=False)
            new_objects.append(new_obj)

        bpy.ops.object.select_all(action='DESELECT')
        for new_obj in new_objects:
            new_obj.select_set(True)

        unregister_draw_handler()


    def revert(self, context):
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Collection: {self.collection_names[self.active_collection]}",
        "Where to place the new object...",
        active=True,
        mouse_value=True,
        alt_mode=False)

    draw_hint(
        self,
        f"Clear Parent [C]: {self.yes_no_str(self.clear_parent)}",
        "Unparent the new object from the original target object")


def register():
    bpy.utils.register_class(ND_OT_hydrate)


def unregister():
    bpy.utils.unregister_class(ND_OT_hydrate)
    unregister_draw_handler()
