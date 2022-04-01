import bpy
import bmesh
from math import radians
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys


class ND_OT_mirror(bpy.types.Operator):
    bl_idname = "nd.mirror"
    bl_label = "Mirror"
    bl_description = "Mirror an object in isolation, or across another object"
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
            self.axis = (self.axis + 1) % 3
            
        elif self.key_step_down:
            self.axis = (self.axis - 1) % 3
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        self.operate(context)
        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.axis = 0
        reference_obj = context.active_object
        mirror_obj = None

        if len(context.selected_objects) == 2:
            a, b = context.selected_objects
            reference_obj = a if a.name != context.object.name else b
            mirror_obj = context.active_object

        self.add_mirror_modifier(reference_obj, mirror_obj)

        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) > 0 and len(context.selected_objects) <= 2


    def add_mirror_modifier(self, reference_obj, mirror_obj):
        mirror = reference_obj.modifiers.new('Mirror — ND', 'MIRROR')
        mirror.use_axis[0] = self.axis == 0
        mirror.use_clip = True
        mirror.merge_threshold = 0.0001

        if mirror_obj != None:
            mirror.mirror_object = mirror_obj

        self.mirror = mirror
    

    def operate(self, context):
        self.mirror.use_axis[0] = self.axis == 0
        self.mirror.use_axis[1] = self.axis == 1
        self.mirror.use_axis[2] = self.axis == 2


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.mirror.name)
        
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Axis: {}".format(['X', 'Y', 'Z'][self.axis]),
        "X, Y, Z",
        active=True,
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_mirror.bl_idname, text=ND_OT_mirror.bl_label)


def register():
    bpy.utils.register_class(ND_OT_mirror)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_mirror)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
