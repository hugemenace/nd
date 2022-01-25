import bpy
import bmesh
from math import radians
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property


class ND_OT_faux_bevel(bpy.types.Operator):
    bl_idname = "nd.faux_bevel"
    bl_label = "Faux Bevel"
    bl_description = "Adds a single segment bevel and a weighted normal modifier"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        width_factor = 0.0001 if event.shift else 0.001

        self.key_shift = event.shift

        if event.type == 'MOUSEMOVE':
            update_overlay(self, context, event)

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

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.mouse_x = 0
        self.mouse_y = 0

        self.width = 0.001

        self.key_shift = False

        self.add_smooth_shading(context)
        self.add_bevel_modifier(context)
        self.add_weighted_normal_modifer(context)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback, "nd_draw_faux_bevel")

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1


    def add_smooth_shading(self, context):
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
        unregister_draw_handler(self, "nd_draw_faux_bevel")


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.bevel.name)
        bpy.ops.object.modifier_remove(modifier=self.wn.name)
        unregister_draw_handler(self, "nd_draw_faux_bevel")


def draw_text_callback(self):
    draw_header(self, "ND — Faux Bevel")
    
    draw_property(
        self, 
        "Width: {0:.1f}mm".format(self.width * 1000), 
        "(±1mm)  |  Shift (±0.1mm)",
        active=True,
        alt_mode=self.key_shift)


def menu_func(self, context):
    self.layout.operator(ND_OT_faux_bevel.bl_idname, text=ND_OT_faux_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_faux_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_faux_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler(self, "nd_draw_faux_bevel")


if __name__ == "__main__":
    register()
