import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys


class ND_OT_hydrate(bpy.types.Operator):
    bl_idname = "nd.hydrate"
    bl_label = "Hydrate"
    bl_description = "Convert a boolean (or other) reference object into solidified/shaded geometry"
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

        elif self.key_step_up:
            if self.key_alt:
                self.clear_parent = not self.clear_parent
            else:
                self.active_collection = (self.active_collection + 1) % (len(self.all_collections) + 1)

            self.dirty = True
            
        elif self.key_step_down:
            if self.key_alt:
                self.clear_parent = not self.clear_parent
            else:
                self.active_collection = (self.active_collection - 1) % (len(self.all_collections) + 1)

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

        self.clear_parent = False
        self.all_collections = [c.name for c in bpy.data.collections]
        self.active_collection = len(self.all_collections)

        self.operate(context)

        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.object.type == 'MESH'

    
    def operate(self, context):
        print(self.active_collection)
        self.dirty = False


    def finish(self, context):
        new_obj = context.object.copy()
        new_obj.data = context.object.data.copy()
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
        
        bpy.ops.object.select_all(action='DESELECT')
        new_obj.select_set(True)
        bpy.context.view_layer.objects.active = new_obj

        if self.clear_parent:
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        unregister_draw_handler()


    def revert(self, context):
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Collection: {0}".format("N/A — Scene" if self.active_collection >= len(self.all_collections) else self.all_collections[self.active_collection]),
        "Where to place the new object...",
        active=self.key_no_modifiers,
        alt_mode=False)

    draw_property(
        self, 
        "Clear parent: {0}".format("Yes" if self.clear_parent else "No"),
        "Alt (Yes, No)",
        active=self.key_alt,
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_hydrate.bl_idname, text=ND_OT_hydrate.bl_label)


def register():
    bpy.utils.register_class(ND_OT_hydrate)


def unregister():
    bpy.utils.unregister_class(ND_OT_hydrate)
    unregister_draw_handler()
