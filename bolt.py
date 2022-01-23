import bpy
import bmesh
import blf
from math import radians


class ND_OT_bolt(bpy.types.Operator):
    bl_idname = "nd.bolt"
    bl_label = "Bolt (& Hole Cutter)"
    bl_description = "Adds a bolt using the 3D cursor position & rotation"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        offset_factor = 0.001 if event.shift else 0.01
        radius_factor = 0.001 if event.shift else 0.01
        thickness_factor = 0.001 if event.shift else 0.01

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        
        if event.type == 'WHEELUPMOUSE':
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

        elif event.type in {'MIDDLEMOUSE'} or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF'):
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

        self.add_object(context)
        self.add_screw_x_modifier()
        self.add_screw_z_modifer()
        self.add_decimate_modifier()
        self.add_displace_modifier()
        self.add_solidify_modifier()
        self.align_object_to_3d_cursor(context)

        self.register_draw_handler(context)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    

    def register_draw_handler(self, context):
        handler = bpy.app.driver_namespace.get('nd_draw_bolt')

        if not handler:
            handler = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback, (self, context), 'WINDOW', 'POST_PIXEL')
            dns = bpy.app.driver_namespace
            dns['nd_draw_bolt'] = handler

            self.redraw_regions(context)

    
    def unregister_draw_handler(self, context):
        handler = bpy.app.driver_namespace.get('nd_draw_bolt')

        if handler:
            bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
            del bpy.app.driver_namespace['nd_draw_bolt']

            self.redraw_regions(context)


    def redraw_regions(self, context):
        for area in context.window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


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
    

    def add_screw_x_modifier(self):
        screwX = self.obj.modifiers.new("ND — Radius", 'SCREW')
        screwX.axis = 'X'
        screwX.angle = 0
        screwX.screw_offset = self.radius
        screwX.steps = 1
        screwX.render_steps = 1
        screwX.use_merge_vertices = True

        self.screwX = screwX
    

    def add_screw_z_modifer(self):
        screwZ = self.obj.modifiers.new("ND — Segments", 'SCREW')
        screwZ.axis = 'Z'
        screwZ.steps = self.segments
        screwZ.render_steps = self.segments
        screwZ.use_merge_vertices = True

        self.screwZ = screwZ


    def adjust_segments(self, amount):
        self.screwZ.steps = max(3, self.screwZ.steps + amount)
        self.screwZ.render_steps = max(3, self.screwZ.render_steps + amount)


    def add_decimate_modifier(self):
        decimate = self.obj.modifiers.new("ND — Decimate", 'DECIMATE')
        decimate.decimate_type = 'DISSOLVE'
        decimate.angle_limit = radians(.25)
        decimate.show_viewport = False if self.segments <= 3 else True

        self.decimate = decimate
    

    def add_displace_modifier(self):
        displace = self.obj.modifiers.new("ND — Displace", 'DISPLACE')
        displace.mid_level = 0.5
        displace.strength = self.offset
        
        self.displace = displace
    

    def add_solidify_modifier(self):
        solidify = self.obj.modifiers.new("ND — Solidify", 'SOLIDIFY')
        solidify.thickness = self.thickness
        solidify.offset = 1

        self.solidify = solidify
    

    def align_object_to_3d_cursor(self, context):
        self.obj.location = context.scene.cursor.location
        self.obj.rotation_euler = context.scene.cursor.rotation_euler
        

    def handle_optional_boolean_ops(self, context):
        if len(context.selected_objects) > 1:
            self.obj.display_type = 'WIRE'
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
        self.unregister_draw_handler(context)


    def revert(self, context):
        self.select_bolt(context)
        bpy.ops.object.delete()
        self.unregister_draw_handler(context)


def draw_text_callback(self, context):
    cursor_offset_x = 20
    cursor_offset_y = -100
    
    blf.size(0, 24, 72)
    blf.color(0, 1.0, 0.529, 0.216, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y, 0)
    blf.draw(0, "ND — Bolt")

    blf.size(0, 16, 72)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 25, 0)
    blf.draw(0, "Segments: {}".format(self.segments))

    blf.size(0, 11, 72)
    blf.color(0, 1.0, 1.0, 1.0, 0.3)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 40, 0)
    blf.draw(0, "(±1)")
    
    blf.size(0, 16, 72)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 65, 0)
    blf.draw(0, "Radius: {0:.0f}mm".format(self.radius * 1000))

    blf.size(0, 11, 72)
    blf.color(0, 1.0, 1.0, 1.0, 0.3)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 80, 0)
    blf.draw(0, "Alt (±10mm)  |  Shift + Alt (±1mm)")

    blf.size(0, 16, 72)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 105, 0)
    blf.draw(0, "Thickness: {0:.0f}mm".format(self.thickness * 1000))

    blf.size(0, 11, 72)
    blf.color(0, 1.0, 1.0, 1.0, 0.3)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 120, 0)
    blf.draw(0, "Ctrl (±10mm)  |  Shift + Ctrl (±1mm)")

    blf.size(0, 16, 72)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 145, 0)
    blf.draw(0, "Offset: {0:.3f}".format(self.offset))

    blf.size(0, 11, 72)
    blf.color(0, 1.0, 1.0, 1.0, 0.3)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 160, 0)
    blf.draw(0, "Ctrl + Alt (±0.01)  |  Shift + Ctrl + Alt (±0.001)")

    self.redraw_regions(context)


def menu_func(self, context):
    self.layout.operator(ND_OT_bolt.bl_idname, text=ND_OT_bolt.bl_label)


def register():
    bpy.utils.register_class(ND_OT_bolt)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_bolt)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
