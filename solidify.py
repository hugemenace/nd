import bpy
import bmesh
from math import radians
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property


class ND_OT_solidify(bpy.types.Operator):
    bl_idname = "nd.solidify"
    bl_label = "Solidify"
    bl_description = "Adds a solidify modifier, and enables smoothing"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        thickness_factor = (self.base_thickness_factor / 10.0) if event.shift else self.base_thickness_factor

        self.key_shift = event.shift
        self.key_alt = event.alt

        if event.type == 'P' and event.value == 'PRESS':
            self.pin_overlay = not self.pin_overlay

        elif event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'} and event.value == 'PRESS':
            self.base_thickness_factor = min(1, self.base_thickness_factor * 10.0)

        elif event.type in {'MINUS', 'NUMPAD_MINUS'} and event.value == 'PRESS':
            self.base_thickness_factor = max(0.001, self.base_thickness_factor / 10.0)

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
        update_overlay(self, context, event, pinned=self.pin_overlay, x_offset=260, lines=2)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.base_thickness_factor = 0.001

        self.thickness = 0.001
        self.offset = 0

        self.key_shift = False
        self.key_alt = False

        self.add_smooth_shading(context)
        self.add_solidify_modifier(context)

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


    def add_solidify_modifier(self, context):
        solidify = context.object.modifiers.new("ND — solidify", 'SOLIDIFY')
        solidify.thickness = self.thickness
        solidify.offset = self.offset

        self.solidify = solidify
    

    def operate(self, context):
        self.solidify.thickness = self.thickness
        self.solidify.offset = self.offset


    def finish(self, context):
        unregister_draw_handler(self)


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.solidify.name)
        unregister_draw_handler(self)


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self, 
        "Thickness: {0:.1f}mm".format(self.thickness * 1000), 
        "(±{0:.1f}mm)  |  Shift + (±{1:.1f}mm)".format(self.base_thickness_factor * 1000, (self.base_thickness_factor / 10) * 1000),
        active=(not self.key_alt),
        alt_mode=(self.key_shift and not self.key_alt))

    draw_property(
        self, 
        "Offset: {}".format(self.offset), 
        "Alt (±1)",
        active=(self.key_alt),
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_solidify.bl_idname, text=ND_OT_solidify.bl_label)


def register():
    bpy.utils.register_class(ND_OT_solidify)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_solidify)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler(self, ND_OT_solidify.bl_label)


if __name__ == "__main__":
    register()
