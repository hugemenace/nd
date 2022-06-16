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
from .. lib.collections import hide_utils_collection, isolate_in_utils_collection


class ND_OT_cycle(bpy.types.Operator):
    bl_idname = "nd.cycle"
    bl_label = "Cycle"
    bl_description = """Scroll through the active object's utilties, or modifier stack
SHIFT — Cycle through the modifier stack"""
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

        elif pressed(event, {'M'}):
            self.mod_cycle = not self.mod_cycle
            self.prepare_mode(context)

            self.dirty = True

        elif pressed(event, {'F'}):
            if not self.mod_cycle:
                self.toggle_frozen_util()
                self.dirty = True

        elif pressed(event, {'D'}):
            if not self.mod_cycle:
                self.toggle_mod()
                self.dirty = True

        elif pressed(event, {'W'}):
            self.show_wireframe = not self.show_wireframe
            self.dirty = True

        elif self.key_step_up:
            if self.mod_cycle:
                self.mod_current_index = min(self.mod_current_index + 1, self.mod_count - 1)
                self.dirty = True
            elif not self.mod_cycle and self.util_count > 0:
                self.util_current_index = (self.util_current_index + 1) % self.util_count
                self.dirty = True
            
        elif self.key_step_down:
            if self.mod_cycle:
                self.mod_current_index = max(self.mod_current_index - 1, -1)
                self.dirty = True
            elif not self.mod_cycle and self.util_count > 0:
                self.util_current_index = (self.util_current_index - 1) % self.util_count
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

        self.mod_cycle = event.shift
        self.show_wireframe = False
        self.target_obj = context.active_object

        self.show_wireframe_prev = self.target_obj.show_wire

        self.mod_count = len(self.target_obj.modifiers)
        self.mod_names = [mod.name for mod in self.target_obj.modifiers]
        self.mod_snapshot = [mod.show_viewport for mod in self.target_obj.modifiers]
        
        self.frozen_utils = set(())

        self.util_mods = [mod for mod in self.target_obj.modifiers if mod.type == 'BOOLEAN' and mod.object]
        self.util_mod_names = [mod.name for mod in self.util_mods]
        self.util_count = len(self.util_mods)

        self.mod_current_index = -1
        self.util_current_index = 0

        self.prepare_mode(context)

        self.operate(context)

        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and self.target_obj.type == 'MESH'


    def set_mod_visible(self, mod, visible):
        mod.show_viewport = visible

    
    def toggle_frozen_util(self):
        obj = self.util_mods[self.util_current_index].object

        if obj in self.frozen_utils:
            self.frozen_utils.remove(obj)
        else:
            self.frozen_utils.add(obj)


    def toggle_mod(self):
        mod = self.util_mods[self.util_current_index]
        mod.show_viewport = not mod.show_viewport


    def operate(self, context):
        if self.mod_cycle:
            for counter, mod in enumerate(self.target_obj.modifiers):
                if not self.mod_snapshot[counter]:
                    continue
                self.set_mod_visible(mod, counter <= self.mod_current_index)
        elif self.util_count > 0:
            util_obj = self.util_mods[self.util_current_index].object
            isolate_in_utils_collection(self.frozen_utils.union({util_obj}))
            bpy.ops.object.select_all(action='DESELECT')
            util_obj.select_set(True)
            bpy.context.view_layer.objects.active = util_obj

        self.target_obj.show_wire = self.show_wireframe

        self.dirty = False


    def revert_mods(self, context):
        for counter, mod in enumerate(self.target_obj.modifiers):
            mod.show_viewport = self.mod_snapshot[counter]


    def prepare_mode(self, context):
        hide_utils_collection(True)
        
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


    def finish(self, context):
        if self.mod_cycle:
            self.revert_mods(context)

        if self.util_count > 0:
            bpy.ops.object.select_all(action='DESELECT')

            all_objects = self.frozen_utils.union({self.util_mods[self.util_current_index].object})
            for obj in all_objects:
                obj.select_set(True)

            bpy.context.view_layer.objects.active = self.util_mods[self.util_current_index].object

        self.target_obj.show_wire = self.show_wireframe_prev

        unregister_draw_handler()


    def revert(self, context):
        hide_utils_collection(True)

        self.revert_mods(context)
        self.target_obj.show_wire = self.show_wireframe_prev

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    if self.mod_cycle:
        if self.mod_count > 0:
            draw_property(
                self,
                "Modifier: {0}".format("None" if self.mod_current_index == -1 else self.mod_names[self.mod_current_index]),
                "Active: {0}  /  Total: {1}".format(self.mod_current_index + 1, self.mod_count),
                active=True,
                alt_mode=False)
        else:
            draw_hint(self, "Whoops", "Looks like there are no modifiers to view.")
    else:
        if self.util_count > 0:
            draw_property(
                self,
                "Utility: {0}".format(self.util_mod_names[self.util_current_index]),
                "Current: {0}  /  Total: {1}".format(self.util_current_index + 1, self.util_count),
                active=True,
                alt_mode=False)

            draw_hint(
                self,
                "Frozen [F]: {0}".format("Yes" if self.util_mods[self.util_current_index].object in self.frozen_utils else "No"),
                "Keep the current utility selected while cycling")

            draw_hint(
                self,
                "Disable Modifier [D]: {0}".format("Yes" if not self.util_mods[self.util_current_index].show_viewport else "No"),
                "Disable the associated boolean modifier")
        else:
            draw_hint(self, "Whoops", "Looks like there are no utilities to cycle through.")

    draw_hint(
        self,
        "Mode [M]: {0}".format("Modifier" if self.mod_cycle else "Utility"),
        "Switch modes (Modifier, Utility)")

    draw_hint(
        self,
        "Wireframe [W]: {0}".format("Yes" if self.show_wireframe else "No"),
        "Display the object's wireframe while cycling")
    

def register():
    bpy.utils.register_class(ND_OT_cycle)


def unregister():
    bpy.utils.unregister_class(ND_OT_cycle)
    unregister_draw_handler()
