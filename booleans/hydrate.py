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
from .. lib.preferences import get_preferences


class ND_OT_hydrate(bpy.types.Operator):
    bl_idname = "nd.hydrate"
    bl_label = "Hydrate"
    bl_description = "Convert a boolean reference object into solidified geometry"
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

        elif pressed(event, {'C'}):
            self.clear_parent = not self.clear_parent
            self.dirty = True

        elif self.key_step_up:
            if self.key_no_modifiers:
                self.active_collection = (self.active_collection + 1) % (len(self.all_collections) + 1)
                self.dirty = True
            
        elif self.key_step_down:
            if self.key_no_modifiers:
                self.active_collection = (self.active_collection - 1) % (len(self.all_collections) + 1)
                self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.key_no_modifiers:
                self.active_collection = (self.active_collection + self.mouse_step) % (len(self.all_collections) + 1)
                self.dirty = True

        if self.dirty:
            self.operate(context)
            
        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False

        self.active_object = context.active_object

        self.clear_parent = False
        self.all_collections = [c.name for c in bpy.data.collections]
        self.active_collection = len(self.all_collections)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) > 0 and all(obj.type == 'MESH' for obj in context.selected_objects)

    
    def operate(self, context):
        self.dirty = False


    def finish(self, context):
        new_objects = []
        for obj in context.selected_objects:
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            new_obj.animation_data_clear()

            if new_obj.name.startswith("Bool — "):
                new_obj.name = new_obj.name[6:]
                new_obj.data.name = new_obj.name
            
            if self.active_collection >= len(self.all_collections):
                bpy.context.collection.objects.link(new_obj)
            else:
                bpy.data.collections[self.active_collection].objects.link(new_obj)

            new_obj.display_type = 'SOLID'
            new_obj.hide_render = False
            
            new_objects.append((new_obj, obj))

            if self.clear_parent:
                if bpy.app.version < (4, 0, 0):
                    bpy.ops.object.parent_clear({'object': new_obj}, type='CLEAR_KEEP_TRANSFORM')
                else:
                    with bpy.context.temp_override(object=new_obj):
                        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        bpy.ops.object.select_all(action='DESELECT')
        for new_obj, orig_obj in new_objects:
            new_obj.select_set(True)
            if orig_obj == self.active_object:
                bpy.context.view_layer.objects.active = new_obj

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
