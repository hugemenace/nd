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
from .. lib.collections import isolate_utils, hide_all_utils
from .. lib.preferences import get_preferences
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, obj_is_mesh, ctx_objects_selected, app_minor_version


class ND_OT_cycle(BaseOperator):
    bl_idname = "nd.cycle"
    bl_label = "Cycle"
    bl_description = """Scroll through the active object's utilties, or modifier stack
SHIFT — Cycle through the modifier stack"""
    bl_options = {'UNDO'}


    key_callbacks = {
        'M': lambda cls, context, event: cls.handle_toggle_mod_cycle(context, event),
        'F': lambda cls, context, event: cls.handle_toggle_freeze_state(context, event),
        'A': lambda cls, context, event: cls.handle_toggle_applied_util(context, event),
        'D': lambda cls, context, event: cls.handle_toggle_mod(context, event),
        'W': lambda cls, context, event: cls.handle_toggle_wireframe(context, event),
    }

    modal_config = {
        'MOVEMENT_PASSTHROUGH': True,
        'ON_CANCEL': lambda cls, context: cls.revert(context),
        'ON_CONFIRM': lambda cls, context: cls.finish(context),
    }


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        return ctx_obj_mode(context) and obj_is_mesh(target_object) and ctx_objects_selected(context, 1)


    def do_modal(self, context, event):
        if self.key_step_up:
            if self.mod_cycle:
                self.mod_current_index = min(self.mod_current_index + 1, self.mod_count - 1)
                self.dirty = True
            elif not self.mod_cycle and self.util_count > 0:
                self.util_current_index = (self.util_current_index + 1) % self.util_count
                self.dirty = True

        if self.key_step_down:
            if self.mod_cycle:
                self.mod_current_index = max(self.mod_current_index - 1, -1)
                self.dirty = True
            elif not self.mod_cycle and self.util_count > 0:
                self.util_current_index = (self.util_current_index - 1) % self.util_count
                self.dirty = True

        if get_preferences().enable_mouse_values:
            if self.mod_cycle:
                self.mod_current_index = max(-1, min(self.mod_current_index + self.mouse_step, self.mod_count - 1))
                self.dirty = True
            elif not self.mod_cycle and self.util_count > 0:
                self.util_current_index = (self.util_current_index + self.mouse_step) % self.util_count
                self.dirty = True


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        self.mod_cycle = event.shift
        self.show_wireframe = False
        self.target_obj = context.active_object
        self.freeze_mod_cycle_state = False

        self.show_wireframe_prev = self.target_obj.show_wire

        self.mod_count = len(self.target_obj.modifiers)
        self.mod_names = [mod.name for mod in self.target_obj.modifiers]
        self.mod_snapshot = [mod.show_viewport for mod in self.target_obj.modifiers]

        self.frozen_utils = set(())
        self.applied_utils = set(())

        self.util_mods = [mod for mod in self.target_obj.modifiers if mod.type == 'BOOLEAN' and mod.object]
        self.util_mod_names = [mod.name for mod in self.util_mods]
        self.util_count = len(self.util_mods)

        self.mod_current_index = -1
        self.util_current_index = 0

        self.prepare_mode(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def handle_toggle_mod_cycle(self, context, event):
        self.mod_cycle = not self.mod_cycle
        self.prepare_mode(context)


    def handle_toggle_freeze_state(self, context, event):
        if self.mod_cycle:
            self.freeze_mod_cycle_state = not self.freeze_mod_cycle_state
        else:
            self.toggle_frozen_util()


    def handle_toggle_applied_util(self, context, event):
        if not self.mod_cycle:
            self.toggle_applied_util()


    def handle_toggle_mod(self, context, event):
        if not self.mod_cycle:
            self.toggle_mod()


    def handle_toggle_wireframe(self, context, event):
        self.show_wireframe = not self.show_wireframe


    def set_mod_visible(self, mod, visible):
        mod.show_viewport = visible


    def toggle_frozen_util(self):
        obj = self.util_mods[self.util_current_index].object

        if obj in self.frozen_utils:
            self.frozen_utils.remove(obj)
        else:
            self.frozen_utils.add(obj)


    def toggle_applied_util(self):
        obj = self.util_mods[self.util_current_index].object

        if obj in self.applied_utils:
            self.applied_utils.remove(obj)
        else:
            self.applied_utils.add(obj)


    def toggle_mod(self):
        mod = self.util_mods[self.util_current_index]
        mod.show_viewport = not mod.show_viewport


    def revert_mods(self, context):
        for counter, mod in enumerate(self.target_obj.modifiers):
            mod.show_viewport = self.mod_snapshot[counter]


    def prepare_mode(self, context):
        self.revert_mods(context)

        if self.mod_cycle:
            self.prepare_mod_cycle(context)
        else:
            self.prepare_util_cycle(context)


    def prepare_mod_cycle(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.target_obj.select_set(True)
        context.view_layer.objects.active = self.target_obj

        self.mod_current_index = -1

        for mod in self.target_obj.modifiers:
            self.set_mod_visible(mod, False)


    def prepare_util_cycle(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        self.util_current_index = 0
        self.frozen_utils.clear()


    def operate(self, context):
        if self.mod_cycle:
            for counter, mod in enumerate(self.target_obj.modifiers):
                self.set_mod_visible(mod, counter <= self.mod_current_index)
        elif self.util_count > 0:
            util_obj = self.util_mods[self.util_current_index].object
            hide_all_utils(True)
            isolate_utils(self.frozen_utils.union({util_obj}))
            bpy.ops.object.select_all(action='DESELECT')
            util_obj.select_set(True)
            bpy.context.view_layer.objects.active = util_obj

        self.target_obj.show_wire = self.show_wireframe


    def finish(self, context):
        if self.mod_cycle and not self.freeze_mod_cycle_state:
            self.revert_mods(context)

        if self.util_count > 0:
            bpy.ops.object.select_all(action='DESELECT')

            all_objects = self.frozen_utils.union({self.util_mods[self.util_current_index].object})
            for obj in all_objects:
                obj.select_set(True)

            for apply_obj in self.applied_utils:
                for mod in self.target_obj.modifiers:
                    if mod.type == 'BOOLEAN' and mod.object == apply_obj:
                        if app_minor_version() < (4, 0):
                            bpy.ops.object.modifier_apply({'object': self.target_obj}, modifier=mod.name)
                        else:
                            with bpy.context.temp_override(object=self.target_obj):
                                bpy.ops.object.modifier_apply(modifier=mod.name)

            bpy.context.view_layer.objects.active = self.util_mods[self.util_current_index].object

        self.target_obj.show_wire = self.show_wireframe_prev

        unregister_draw_handler()


    def revert(self, context):
        self.revert_mods(context)
        self.target_obj.show_wire = self.show_wireframe_prev

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    if self.mod_cycle:
        if self.mod_count > 0:
            modifier_str = "None" if self.mod_current_index == -1 else self.mod_names[self.mod_current_index]
            draw_property(
                self,
                f"Modifier: {modifier_str}",
                f"Active: {self.mod_current_index + 1}  /  Total: {self.mod_count}",
                active=True,
                mouse_value=True,
                alt_mode=False)

            draw_hint(
                self,
                f"Freeze State [F]: {self.yes_no_str(self.freeze_mod_cycle_state)}",
                "Retain the current modifier state(s) on exit")
        else:
            draw_hint(self, "Whoops", "Looks like there are no modifiers to view.")
    else:
        if self.util_count > 0:
            draw_property(
                self,
                f"Utility: {self.util_mod_names[self.util_current_index]}",
                f"Current: {self.util_current_index + 1}  /  Total: {self.util_count}",
                active=True,
                mouse_value=True,
                alt_mode=False)

            draw_hint(
                self,
                f"Frozen [F]: {self.yes_no_str(self.util_mods[self.util_current_index].object in self.frozen_utils)}",
                "Keep the current utility selected while cycling")

            draw_hint(
                self,
                f"Disable Modifier [D]: {self.yes_no_str(not self.util_mods[self.util_current_index].show_viewport)}",
                "Disable the associated boolean modifier")

            draw_hint(
                self,
                f"Apply Modifier [A]: {self.yes_no_str(self.util_mods[self.util_current_index].object in self.applied_utils)}",
                "Apply the associated boolean modifier")
        else:
            draw_hint(self, "Whoops", "Looks like there are no utilities to cycle through.")

    modes = ["Modifier", "Utility"]
    draw_hint(
        self,
        f"Mode [M]: {modes[0] if self.mod_cycle else modes[1]}",
        self.list_options_str(modes))

    draw_hint(
        self,
        f"Wireframe [W]: {self.yes_no_str(self.show_wireframe)}",
        "Display the object's wireframe while cycling")


def register():
    bpy.utils.register_class(ND_OT_cycle)


def unregister():
    bpy.utils.unregister_class(ND_OT_cycle)
    unregister_draw_handler()
