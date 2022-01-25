import bpy
import bmesh
from math import radians
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property


class ND_OT_thickener(bpy.types.Operator):
    bl_idname = "nd.thickener"
    bl_label = "Thickener"
    bl_description = "Adds a solidify modifier, and enables smoothing"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        thickness_factor = 0.0001 if event.shift else 0.001

        self.key_shift = event.shift
        self.key_alt = event.alt

        if event.type == 'MOUSEMOVE':
            update_overlay(self, context, event)

        elif event.type == 'WHEELUPMOUSE':
            if event.alt:
                self.offset = min(1, self.offset + 1)
            else:
                self.thickness += thickness_factor
            
        elif event.type == 'WHEELDOWNMOUSE':
            if event.alt:
                self.offset = max(-1, self.offset - 1)
            else:
                self.thickness = max(0, self.thickness - thickness_factor)
        
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
        self.thickness = 0.001
        self.offset = 0

        self.key_shift = False
        self.key_alt = False

        self.add_smooth_shading(context)
        self.add_solidify_modifier(context)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback, "nd_draw_thickener")

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


    def add_solidify_modifier(self, context):
        solidify = context.object.modifiers.new("ND — Thickener", 'SOLIDIFY')
        solidify.thickness = self.thickness
        solidify.offset = self.offset

        self.solidify = solidify
    

    def operate(self, context):
        self.solidify.thickness = self.thickness
        self.solidify.offset = self.offset


    def finish(self, context):
        unregister_draw_handler(self, "nd_draw_thickener")


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.solidify.name)
        unregister_draw_handler(self, "nd_draw_thickener")


def draw_text_callback(self):
    draw_header(self, self.bl_label)
    
    draw_property(
        self, 
        "Thickness: {0:.1f}mm".format(self.thickness * 1000), 
        "(±1mm)  |  Shift (±0.1mm)",
        active=(not self.key_alt),
        alt_mode=(self.key_shift and not self.key_alt))

    draw_property(
        self, 
        "Offset: {}".format(self.offset), 
        "Alt (±1)",
        active=(self.key_alt),
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_thickener.bl_idname, text=ND_OT_thickener.bl_label)


def register():
    bpy.utils.register_class(ND_OT_thickener)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_thickener)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler(self, "nd_draw_thickener")


if __name__ == "__main__":
    register()
