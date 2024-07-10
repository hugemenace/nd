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
from .. lib.polling import ctx_obj_mode, list_ok


class ND_OT_hydrate(BaseOperator):
    bl_idname = "nd.hydrate"
    bl_label = "Hydrate"
    bl_description = "Convert a boolean reference object into solidified geometry"
    bl_options = {'UNDO'}


    def do_modal(self, context, event):
        if pressed(event, {'C'}):
            self.clear_parent = not self.clear_parent
            self.dirty = True

        if self.key_step_up:
            if self.key_no_modifiers:
                self.active_collection = (self.active_collection + 1) % (len(self.all_collections) + 1)
                self.dirty = True

        if self.key_step_down:
            if self.key_no_modifiers:
                self.active_collection = (self.active_collection - 1) % (len(self.all_collections) + 1)
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.key_no_modifiers:
                self.active_collection = (self.active_collection + self.mouse_step) % (len(self.all_collections) + 1)
                self.dirty = True


    def do_invoke(self, context, event):
        self.dirty = False

        self.clear_parent = False
        self.all_collections = [c.name for c in bpy.data.collections]
        self.active_collection = len(self.all_collections)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def get_valid_objects(self, context):
        return [obj for obj in context.selected_objects if obj.type == 'MESH']


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context)
        return ctx_obj_mode(context) and list_ok(valid_objects)


    def operate(self, context):
        self.dirty = False


    def finish(self, context):
        valid_objects = self.get_valid_objects(context)
        new_objects = []
        for obj in valid_objects:
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            new_obj.animation_data_clear()

            if new_obj.name.startswith("Bool — "):
                new_obj.name = new_obj.name[7:]
                new_obj.data.name = new_obj.name

            if self.active_collection >= len(self.all_collections):
                bpy.context.collection.objects.link(new_obj)
            else:
                bpy.data.collections[self.active_collection].objects.link(new_obj)

            new_obj.display_type = 'SOLID'
            new_obj.hide_render = False

            new_objects.append((new_obj, obj))

            if self.clear_parent:
                bpy.ops.object.select_all(action='DESELECT')
                new_obj.select_set(True)
                bpy.context.view_layer.objects.active = new_obj

                if bpy.app.version < (4, 0, 0):
                    bpy.ops.object.parent_clear({'object': new_obj}, type='CLEAR_KEEP_TRANSFORM')
                else:
                    with bpy.context.temp_override(object=new_obj):
                        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        bpy.ops.object.select_all(action='DESELECT')
        for new_obj, orig_obj in new_objects:
            new_obj.select_set(True)

        unregister_draw_handler()


    def revert(self, context):
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Collection: {0}".format("N/A — Scene" if self.active_collection >= len(self.all_collections) else self.all_collections[self.active_collection]),
        "Where to place the new object...",
        active=True,
        mouse_value=True,
        alt_mode=False)

    draw_hint(
        self,
        "Clear Parent [C]: {0}".format("Yes" if self.clear_parent else "No"),
        "Unparent the new object from the original target object")


def register():
    bpy.utils.register_class(ND_OT_hydrate)


def unregister():
    bpy.utils.unregister_class(ND_OT_hydrate)
    unregister_draw_handler()
