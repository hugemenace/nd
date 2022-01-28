import bpy
import bmesh
from math import radians
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property


class ND_OT_weighted_normal_bevel(bpy.types.Operator):
    bl_idname = "nd.weighted_normal_bevel"
    bl_label = "WN Bevel"
    bl_description = "Adds a single segment bevel and a weighted normal modifier"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        width_factor = (self.base_width_factor / 10.0) if event.shift else self.base_width_factor

        self.key_shift = event.shift

        if event.type == 'P' and event.value == 'PRESS':
            self.pin_overlay = not self.pin_overlay

        elif event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'} and event.value == 'PRESS':
            self.base_width_factor = min(1, self.base_width_factor * 10.0)

        elif event.type in {'MINUS', 'NUMPAD_MINUS'} and event.value == 'PRESS':
            self.base_width_factor = max(0.001, self.base_width_factor / 10.0)

        elif event.type == 'WHEELUPMOUSE':
            self.width += width_factor
            
        elif event.type == 'WHEELDOWNMOUSE':
            self.width = max(0, self.width - width_factor)
        
        elif event.type == 'LEFTMOUSE':
            self.finish(context)

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.revert(context)

            return {'CANCELLED'}

        elif event.type == 'MIDDLEMOUSE' or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF'):
            return {'PASS_THROUGH'}

        self.operate(context)
        update_overlay(self, context, event, pinned=self.pin_overlay, x_offset=270, lines=1)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.base_width_factor = 0.001
        
        self.width = 0.001

        self.key_shift = False

        self.add_smooth_shading(context)
        self.add_bevel_modifier(context)
        self.add_weighted_normal_modifer(context)

        self.pin_overlay = False
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1


    def add_smooth_shading(self, context):
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        context.object.data.auto_smooth_angle = radians(30)


    def add_bevel_modifier(self, context):
        bevel = context.object.modifiers.new("ND — Bevel", 'BEVEL')
        bevel.segments = 1
        bevel.width = self.width

        self.bevel = bevel
    

    def add_weighted_normal_modifer(self, context):
        wn = context.object.modifiers.new("ND — Weighted Normal", 'WEIGHTED_NORMAL')
        wn.weight = 100

        self.wn = wn


    def operate(self, context):
        self.bevel.width = self.width


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.bevel.name)
        bpy.ops.object.modifier_remove(modifier=self.wn.name)
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self,
        "Width: {0:.1f}mm".format(self.width * 1000), 
        "Alt (±{0:.1f}mm)  |  Shift (±{1:.1f}mm)".format(self.base_width_factor * 1000, (self.base_width_factor / 10) * 1000),
        active=True,
        alt_mode=self.key_shift)


def menu_func(self, context):
    self.layout.operator(ND_OT_weighted_normal_bevel.bl_idname, text=ND_OT_weighted_normal_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_weighted_normal_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_weighted_normal_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()


if __name__ == "__main__":
    register()
