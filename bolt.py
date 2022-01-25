import bpy
import bmesh
from math import radians
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property


class ND_OT_bolt(bpy.types.Operator):
    bl_idname = "nd.bolt"
    bl_label = "Bolt (& Hole Cutter)"
    bl_description = "Adds a bolt using the 3D cursor position & rotation"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        offset_factor = 0.001 if event.shift else 0.01
        radius_factor = 0.001 if event.shift else 0.01
        thickness_factor = 0.001 if event.shift else 0.01

        self.key_shift = event.shift
        self.key_alt = event.alt
        self.key_ctrl = event.ctrl

        if event.type == 'MOUSEMOVE':
            update_overlay(self, context, event)
        
        elif event.type == 'WHEELUPMOUSE':
            if event.alt and event.ctrl:
                self.offset += offset_factor
            elif event.alt:
                self.radius += radius_factor
            elif event.ctrl:
                self.thickness += thickness_factor
            else:
                self.segments += 1

        elif event.type == 'WHEELDOWNMOUSE':
            if event.alt and event.ctrl:
                self.offset -= offset_factor
            elif event.alt:
                self.radius = max(0, self.radius - radius_factor)
            elif event.ctrl:
                self.thickness = max(0, self.thickness - thickness_factor)
            else:
                self.segments = max(3, self.segments - 1)

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

        self.segments = 3
        self.radius = 0.02
        self.thickness = 0.02
        self.offset = 0

        self.key_shift = False
        self.key_alt = False
        self.key_ctrl = False

        self.add_object(context)
        self.add_screw_x_modifier()
        self.add_screw_z_modifer()
        self.add_decimate_modifier()
        self.add_displace_modifier()
        self.add_solidify_modifier()
        self.align_object_to_3d_cursor(context)
        self.set_cutter_visibility(context)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback, "nd_draw_bolt")

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def add_object(self, context):
        mesh = bpy.data.meshes.new("ND — Bolt")
        obj = bpy.data.objects.new("ND — Bolt", mesh)
        bpy.data.collections[context.collection.name].objects.link(obj)
        bm = bmesh.new()
        bm.verts.new()
        bm.to_mesh(mesh)
        bm.free()
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = radians(30)
        
        self.obj = obj
    

    def set_cutter_visibility(self, context):
        if len(context.selected_objects) > 1:
            self.obj.show_in_front = True
            self.obj.color[3] = 0.2


    def add_screw_x_modifier(self):
        screwX = self.obj.modifiers.new("ND — Radius", 'SCREW')
        screwX.axis = 'X'
        screwX.angle = 0
        screwX.screw_offset = self.radius
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


    def add_decimate_modifier(self):
        decimate = self.obj.modifiers.new("ND — Decimate", 'DECIMATE')
        decimate.decimate_type = 'DISSOLVE'
        decimate.angle_limit = radians(.25)
        decimate.show_viewport = False if self.segments <= 3 else True

        self.decimate = decimate
    

    def add_displace_modifier(self):
        displace = self.obj.modifiers.new("ND — Offset", 'DISPLACE')
        displace.mid_level = 0.5
        displace.strength = self.offset
        
        self.displace = displace
    

    def add_solidify_modifier(self):
        solidify = self.obj.modifiers.new("ND — Thickness", 'SOLIDIFY')
        solidify.thickness = self.thickness
        solidify.offset = 1

        self.solidify = solidify
    

    def align_object_to_3d_cursor(self, context):
        self.obj.location = context.scene.cursor.location
        self.obj.rotation_euler = context.scene.cursor.rotation_euler
        

    def handle_optional_boolean_ops(self, context):
        if len(context.selected_objects) > 1:
            self.obj.display_type = 'WIRE'
            self.obj.show_in_front = False
            self.obj.color[3] = 1.0

            targets = [o for o in context.selected_objects if not (o == self.obj)]

            for target in targets:
                boolean = target.modifiers.new("ND — Bolt Hole", 'BOOLEAN')
                boolean.object = self.obj
        else:
            self.obj.display_type = 'SOLID'


    def operate(self, context):
        self.decimate.show_viewport = False if self.segments <= 3 else True
        self.screwX.screw_offset = self.radius
        self.screwZ.steps = self.segments
        self.screwZ.render_steps = self.segments
        self.solidify.thickness = self.thickness
        self.displace.strength = self.offset


    def select_bolt(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)


    def finish(self, context):
        self.handle_optional_boolean_ops(context)
        self.select_bolt(context)
        unregister_draw_handler(self, "nd_draw_bolt")


    def revert(self, context):
        self.select_bolt(context)
        bpy.ops.object.delete()
        unregister_draw_handler(self, "nd_draw_bolt")


def draw_text_callback(self):
    draw_header(self, self.bl_label)

    draw_property(
        self, 
        "Segments: {}".format(self.segments), 
        "(±1)", 
        active=(not self.key_ctrl and not self.key_alt), 
        alt_mode=False)

    draw_property(
        self, 
        "Radius: {0:.0f}mm".format(self.radius * 1000), 
        "Alt (±10mm)  |  Shift + Alt (±1mm)", 
        active=(not self.key_ctrl and self.key_alt), 
        alt_mode=(not self.key_ctrl and self.key_alt and self.key_shift))

    draw_property(
        self, 
        "Thickness: {0:.0f}mm".format(self.thickness * 1000), 
        "Ctrl (±10mm)  |  Shift + Ctrl (±1mm)", 
        active=(self.key_ctrl and not self.key_alt), 
        alt_mode=(self.key_ctrl and not self.key_alt and self.key_shift))

    draw_property(
        self, 
        "Offset: {0:.3f}".format(self.offset), 
        "Ctrl + Alt (±0.01)  |  Shift + Ctrl + Alt (±0.001)", 
        active=(self.key_ctrl and self.key_alt), 
        alt_mode=(self.key_ctrl and self.key_alt and self.key_shift))


def menu_func(self, context):
    self.layout.operator(ND_OT_bolt.bl_idname, text=ND_OT_bolt.bl_label)


def register():
    bpy.utils.register_class(ND_OT_bolt)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_bolt)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler(self, "nd_draw_bolt")


if __name__ == "__main__":
    register()
