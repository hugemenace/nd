import bpy
import bmesh
from math import radians
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property


class ND_OT_screw(bpy.types.Operator):
    bl_idname = "nd.screw"
    bl_label = "Screw"
    bl_description = "Adds a screw modifier tuned for converting a sketch into a cylindrical object"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        segment_factor = 1 if event.shift else 2
        angle_factor = 1 if event.shift else 10
        offset_factor = (self.base_offset_factor / 10.0) if event.shift else self.base_offset_factor

        self.key_shift = event.shift
        self.key_alt = event.alt
        self.key_ctrl = event.ctrl

        if not self.pin_overlay and event.type == 'MOUSEMOVE':
            update_overlay(self, context, event)
        
        elif event.type == 'P' and event.value == 'PRESS':
            self.pin_overlay = not self.pin_overlay
            update_overlay(self, context, event, pinned=self.pin_overlay, x_offset=360, lines=4)

        elif event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'} and event.value == 'PRESS':
            if event.alt and event.ctrl:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)

        elif event.type in {'MINUS', 'NUMPAD_MINUS'} and event.value == 'PRESS':
            if event.alt and event.ctrl:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)

        elif event.type == 'WHEELUPMOUSE':
            if event.alt and event.ctrl:
                self.offset += offset_factor
            elif event.alt:
                if event.shift:
                    self.offset_axis = (self.offset_axis + 1) % 3
                else:
                    self.screw_axis = (self.screw_axis + 1) % 3
            elif event.ctrl:
                self.angle = min(360, self.angle + angle_factor)
            else:
                self.segments = 4 if self.segments == 3 else self.segments + segment_factor
                
            
        elif event.type == 'WHEELDOWNMOUSE':
            if event.alt and event.ctrl:
                self.offset -= offset_factor
            elif event.alt:
                if event.shift:
                    self.offset_axis = (self.offset_axis + 1) % 3
                else:
                    self.screw_axis = (self.screw_axis + 1) % 3
            elif event.ctrl:
                self.angle = max(0, self.angle - angle_factor)
            else:
                self.segments = max(3, self.segments - segment_factor)
        
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
        self.base_offset_factor = 0.01

        self.screw_axis = 2 # X (0), Y (1), Z (2)
        self.offset_axis = 1 # X (0), Y (1), Z (2)
        self.segments = 3
        self.angle = 360
        self.offset = 0

        self.key_shift = False
        self.key_alt = False
        self.key_ctrl = False

        self.add_smooth_shading(context)
        self.add_displace_modifier(context)
        self.add_screw_modifier(context)

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
        displace.mid_level = 0.5
        displace.strength = self.offset
        displace.space = 'LOCAL'
        displace.direction = ['X', 'Y', 'Z'][self.offset_axis]
        
        self.displace = displace


    def add_screw_modifier(self, context):
        screw = context.object.modifiers.new("ND — Screw", 'SCREW')
        screw.angle = radians(self.angle)
        screw.screw_offset = 0
        screw.axis = ['X', 'Y', 'Z'][self.screw_axis]
        screw.steps = self.segments
        screw.render_steps = self.segments
        screw.use_merge_vertices = True 
        screw.merge_threshold = 0.0001

        self.screw = screw
    

    def operate(self, context):
        self.displace.strength = self.offset
        self.displace.direction = ['X', 'Y', 'Z'][self.offset_axis]

        self.screw.axis = ['X', 'Y', 'Z'][self.screw_axis]
        self.screw.steps = self.segments
        self.screw.render_steps = self.segments
        self.screw.angle = radians(self.angle)


    def finish(self, context):
        unregister_draw_handler(self)


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.screw.name)
        bpy.ops.object.modifier_remove(modifier=self.displace.name)
        unregister_draw_handler(self)


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self,
        "Segments: {}".format(self.segments),
        "Alt (±2)  |  Shift + Alt (±1)",
        active=(not self.key_alt and not self.key_ctrl),
        alt_mode=(self.key_shift and not self.key_alt and not self.key_ctrl))
    
    draw_property(
        self,
        "Screw Axis: {} // Offset Axis: {}".format(['X', 'Y', 'Z'][self.screw_axis], ['X', 'Y', 'Z'][self.offset_axis]),
        "(Screw X, Y, Z)  |  Shift (Offset X, Y, Z)",
        active=(self.key_alt and not self.key_ctrl),
        alt_mode=(self.key_shift and self.key_alt and not self.key_ctrl))

    draw_property(
        self,
        "Angle: {0:.0f}°".format(self.angle),
        "Ctrl (±10)  |  Shift + Ctrl (±1)",
        active=(not self.key_alt and self.key_ctrl),
        alt_mode=(self.key_shift and self.key_ctrl and not self.key_alt))

    draw_property(
        self,
        "Offset: {0:.3f}".format(self.offset),
        "Ctrl + Alt (±{0:.1f}mm)  |  Shift + Ctrl + Alt (±{1:.1f}mm)".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=(self.key_ctrl and self.key_alt),
        alt_mode=(self.key_ctrl and self.key_alt and self.key_shift))


def menu_func(self, context):
    self.layout.operator(ND_OT_screw.bl_idname, text=ND_OT_screw.bl_label)


def register():
    bpy.utils.register_class(ND_OT_screw)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_screw)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler(self, ND_OT_screw.bl_label)


if __name__ == "__main__":
    register()
