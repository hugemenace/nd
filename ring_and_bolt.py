import bpy
import bmesh
from math import radians
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from . utils import add_single_vertex_object, align_object_to_3d_cursor


class ND_OT_ring_and_bolt(bpy.types.Operator):
    bl_idname = "nd.ring_and_bolt"
    bl_label = "Ring & Bolt"
    bl_description = "Adds a ring or ring_and_bolt face at the 3D cursor"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        radius_factor = (self.base_radius_factor / 10.0) if event.shift else self.base_radius_factor
        width_factor = (self.base_width_factor / 10.0) if event.shift else self.base_width_factor
        segment_factor = 1 if event.shift else 2

        self.key_shift = event.shift
        self.key_alt = event.alt
        self.key_ctrl = event.ctrl

        if event.type == 'P' and event.value == 'PRESS':
            self.pin_overlay = not self.pin_overlay

        elif event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'} and event.value == 'PRESS':
            if event.alt:
                self.base_radius_factor = min(1, self.base_radius_factor * 10.0)
            elif event.ctrl:
                self.base_width_factor = min(1, self.base_width_factor * 10.0)

        elif event.type in {'MINUS', 'NUMPAD_MINUS'} and event.value == 'PRESS':
            if event.alt:
                self.base_radius_factor = max(0.001, self.base_radius_factor / 10.0)
            elif event.ctrl:
                self.base_width_factor = max(0.001, self.base_width_factor / 10.0)
        
        elif event.type == 'WHEELUPMOUSE':
            if event.alt:
                self.radius += radius_factor
            elif event.ctrl:
                self.width += width_factor
            else:
                self.segments = 4 if self.segments == 3 else self.segments + segment_factor

        elif event.type == 'WHEELDOWNMOUSE':
            if event.alt:
                self.radius = max(0, self.radius - radius_factor)
            elif event.ctrl:
                self.width = max(0, self.width - width_factor)
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
        update_overlay(self, context, event, pinned=self.pin_overlay, x_offset=300, lines=3)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.base_radius_factor = 0.001
        self.base_width_factor = 0.001

        self.mouse_x = 0
        self.mouse_y = 0

        self.segments = 3
        self.radius = 0
        self.width = 0.05

        self.key_shift = False
        self.key_alt = False
        self.key_ctrl = False

        bpy.ops.object.select_all(action='DESELECT')

        add_single_vertex_object(self, context, "Bolt")
        align_object_to_3d_cursor(self, context)

        self.add_displace_modifier()
        self.add_screw_x_modifier()
        self.add_screw_z_modifer()

        self.pin_overlay = False
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def add_displace_modifier(self):
        displace = self.obj.modifiers.new("ND — Radius", 'DISPLACE')
        displace.mid_level = 0.5
        displace.strength = self.radius
        displace.direction = 'X'
        displace.space = 'LOCAL'
        
        self.displace = displace


    def add_screw_x_modifier(self):
        screwX = self.obj.modifiers.new("ND — Width", 'SCREW')
        screwX.axis = 'X'
        screwX.angle = 0
        screwX.screw_offset = self.width
        screwX.steps = 1
        screwX.render_steps = 1
        screwX.use_merge_vertices = True
        screwX.merge_threshold = 0.0001

        self.screwX = screwX
    

    def add_screw_z_modifer(self):
        screwZ = self.obj.modifiers.new("ND — Segments", 'SCREW')
        screwZ.axis = 'Z'
        screwZ.steps = self.segments
        screwZ.render_steps = self.segments
        screwZ.use_merge_vertices = True
        screwZ.merge_threshold = 0.0001

        self.screwZ = screwZ


    def operate(self, context):
        self.screwX.screw_offset = self.width
        self.screwZ.steps = self.segments
        self.screwZ.render_steps = self.segments
        self.displace.strength = self.radius


    def select_ring_and_bolt(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)


    def finish(self, context):
        self.select_ring_and_bolt(context)
        unregister_draw_handler()


    def revert(self, context):
        self.select_ring_and_bolt(context)
        bpy.ops.object.delete()
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Segments: {}".format(self.segments), 
        "(±2)  |  Shift (±1)",
        active=(not self.key_ctrl and not self.key_alt), 
        alt_mode=False)

    draw_property(
        self, 
        "Radius: {0:.0f}mm".format(self.radius * 1000), 
        "Alt (±{0:.1f}mm)  |  Shift + Alt (±{1:.1f}mm)".format(self.base_radius_factor * 1000, (self.base_radius_factor / 10) * 1000),
        active=(not self.key_ctrl and self.key_alt), 
        alt_mode=(not self.key_ctrl and self.key_alt and self.key_shift))

    draw_property(
        self, 
        "Width: {0:.0f}mm".format(self.width * 1000), 
        "Ctrl (±{0:.1f}mm)  |  Shift + Ctrl (±{1:.1f}mm)".format(self.base_width_factor * 1000, (self.base_width_factor / 10) * 1000),
        active=(self.key_ctrl and not self.key_alt), 
        alt_mode=(self.key_ctrl and not self.key_alt and self.key_shift))


def menu_func(self, context):
    self.layout.operator(ND_OT_ring_and_bolt.bl_idname, text=ND_OT_ring_and_bolt.bl_label)


def register():
    bpy.utils.register_class(ND_OT_ring_and_bolt)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_ring_and_bolt)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()


if __name__ == "__main__":
    register()
