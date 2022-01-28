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
        offset_factor = (self.base_offset_factor / 10.0) if event.shift else self.base_offset_factor

        self.key_shift = event.shift
        self.key_alt = event.alt
        self.key_ctrl = event.ctrl

        if event.type == 'P' and event.value == 'PRESS':
            self.pin_overlay = not self.pin_overlay

        elif event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'} and event.value == 'PRESS':
            if event.ctrl:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)
            else:
                self.base_thickness_factor = min(1, self.base_thickness_factor * 10.0)

        elif event.type in {'MINUS', 'NUMPAD_MINUS'} and event.value == 'PRESS':
            if event.ctrl:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)
            else:
               self.base_thickness_factor = max(0.001, self.base_thickness_factor / 10.0)

        elif event.type == 'WHEELUPMOUSE':
            if event.alt:
                self.weighting = min(1, self.weighting + 1)
            elif event.ctrl:
                self.offset += offset_factor
            else:
                self.thickness += thickness_factor
            
        elif event.type == 'WHEELDOWNMOUSE':
            if event.alt:
                self.weighting = max(-1, self.weighting - 1)
            elif event.ctrl:
                self.offset -= offset_factor
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
        update_overlay(self, context, event, pinned=self.pin_overlay, x_offset=300, lines=3)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.base_thickness_factor = 0.001
        self.base_offset_factor = 0.001

        self.thickness = 0.001
        self.weighting = 0
        self.offset = 0

        self.key_shift = False
        self.key_alt = False
        self.key_ctrl = False

        self.add_smooth_shading(context)
        self.add_displace_modifier(context)
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


    def add_displace_modifier(self, context):
        displace = context.object.modifiers.new("ND — Offset", 'DISPLACE')
        displace.strength = self.offset

        self.displace = displace


    def add_solidify_modifier(self, context):
        solidify = context.object.modifiers.new("ND — Thickness", 'SOLIDIFY')
        solidify.thickness = self.thickness
        solidify.offset = self.weighting

        self.solidify = solidify
    

    def operate(self, context):
        self.solidify.thickness = self.thickness
        self.solidify.offset = self.weighting
        self.displace.strength = self.offset


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.displace.name)
        bpy.ops.object.modifier_remove(modifier=self.solidify.name)
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self, 
        "Thickness: {0:.1f}mm".format(self.thickness * 1000), 
        "(±{0:.1f}mm)  |  Shift + (±{1:.1f}mm)".format(self.base_thickness_factor * 1000, (self.base_thickness_factor / 10) * 1000),
        active=(not self.key_alt and not self.key_ctrl),
        alt_mode=(self.key_shift and not self.key_alt and not self.key_ctrl))

    draw_property(
        self, 
        "Offset: {}".format(['Negative', 'Neutral', 'Positive'][1 + self.weighting]),
        "Alt (Negative, Neutral, Positive)",
        active=(self.key_alt and not self.key_ctrl),
        alt_mode=False)

    draw_property(
        self, 
        "Offset: {0:.1f}mm".format(self.offset * 1000), 
        "Ctrl (±{0:.1f}mm)  |  Shift + Ctrl (±{1:.1f}mm)".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=(not self.key_alt and self.key_ctrl),
        alt_mode=(self.key_shift and not self.key_alt and self.key_ctrl))


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
