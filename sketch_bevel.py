import bpy
import bmesh
import blf


class ND_OT_sketch_bevel(bpy.types.Operator):
    bl_idname = "nd.sketch_bevel"
    bl_label = "Sketch Bevel"
    bl_description = "Adds a vertex group bevel and weld modifier"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        width_factor = 0.001 if event.shift else 0.01
        segment_factor = 1 if event.shift else 2
        
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        if event.type == 'WHEELUPMOUSE':
            if event.alt:
                self.width += width_factor
            else:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
        
        elif event.type == 'WHEELDOWNMOUSE':
            if event.alt:
                self.width = max(0, self.width - width_factor)
            else:
                self.segments = max(1, self.segments - segment_factor)

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
        
        self.segments = 1
        self.width = 0.001

        self.add_vertex_group(context)
        self.add_bevel_modifier(context)

        self.register_draw_handler(context)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    
    def register_draw_handler(self, context):
        handler = bpy.app.driver_namespace.get('nd_draw_sketch_bevel')

        if not handler:
            handler = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback, (self, context), 'WINDOW', 'POST_PIXEL')
            dns = bpy.app.driver_namespace
            dns['nd_draw_sketch_bevel'] = handler

            self.redraw_regions(context)

    
    def unregister_draw_handler(self, context):
        handler = bpy.app.driver_namespace.get('nd_draw_sketch_bevel')

        if handler:
            bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
            del bpy.app.driver_namespace['nd_draw_sketch_bevel']

            self.redraw_regions(context)


    def redraw_regions(self, context):
        for area in context.window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH':
            mesh = bmesh.from_edit_mesh(context.object.data)
            return len([vert for vert in mesh.verts if vert.select]) >= 1


    def add_vertex_group(self, context):
        vgroup = context.object.vertex_groups.new(name="ND — Bevel")
        bpy.ops.object.vertex_group_assign()

        self.vgroup = vgroup


    def add_bevel_modifier(self, context):
        bevel = context.object.modifiers.new("ND — Sketch Bevel", type='BEVEL')
        bevel.affect = 'VERTICES'
        bevel.limit_method = 'VGROUP'
        bevel.vertex_group = self.vgroup.name
        bevel.segments = self.segments
        bevel.width = self.width

        self.bevel = bevel
    

    def add_weld_modifier(self, context):
        weld = context.object.modifiers.new("ND — Weld", type='WELD')
        weld.merge_threshold = 0.00001

        self.weld = weld


    def operate(self, context):
        self.bevel.width = self.width
        self.bevel.segments = self.segments


    def finish(self, context):
        self.add_weld_modifier(context)
        self.unregister_draw_handler(context)
    

    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.bevel.name)
        context.object.vertex_groups.remove(self.vgroup)
        self.unregister_draw_handler(context)


def draw_text_callback(self, context):
    cursor_offset_x = 20
    cursor_offset_y = -100

    blf.size(0, 24, 72)
    blf.color(0, 1.0, 0.529, 0.216, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y, 0)
    blf.draw(0, "ND — Sketch Bevel")
    
    blf.size(0, 16, 72)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 25, 0)
    blf.draw(0, "Segments: {}".format(self.segments))
    
    blf.size(0, 11, 72)
    blf.color(0, 1.0, 1.0, 1.0, 0.3)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 40, 0)
    blf.draw(0, "(±2)  |  Shift (±1)")
    
    blf.size(0, 16, 72)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 65, 0)
    blf.draw(0, "Width: {0:.0f}mm".format(self.width * 1000))
    
    blf.size(0, 11, 72)
    blf.color(0, 1.0, 1.0, 1.0, 0.3)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 80, 0)
    blf.draw(0, "Alt (±10mm)  |  Shift + Alt (±1mm)")

    self.redraw_regions(context)


def menu_func(self, context):
    self.layout.operator(
        ND_OT_sketch_bevel.bl_idname, 
        text=ND_OT_sketch_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_sketch_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_sketch_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
