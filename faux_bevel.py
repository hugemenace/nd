import bpy
import bmesh
import blf
from math import radians


class ND_OT_faux_bevel(bpy.types.Operator):
    bl_idname = "nd.faux_bevel"
    bl_label = "Faux Bevel"
    bl_description = "Adds a single segment bevel and a weighted normal modifier"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        width_factor = 0.0001 if event.shift else 0.001

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        if event.type == 'WHEELUPMOUSE':
            self.width += width_factor
            
        elif event.type == 'WHEELDOWNMOUSE':
            self.width = max(0, self.width - width_factor)
        
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

        self.width = 0.001

        self.add_bevel_modifier(context)
        self.add_weighted_normal_modifer(context)

        self.register_draw_handler(context)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def register_draw_handler(self, context):
        handler = bpy.app.driver_namespace.get('nd_draw_faux_bevel')

        if not handler:
            handler = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback, (self, context), 'WINDOW', 'POST_PIXEL')
            dns = bpy.app.driver_namespace
            dns['nd_draw_faux_bevel'] = handler

            self.redraw_regions(context)

    
    def unregister_draw_handler(self, context):
        handler = bpy.app.driver_namespace.get('nd_draw_faux_bevel')

        if handler:
            bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
            del bpy.app.driver_namespace['nd_draw_faux_bevel']

            self.redraw_regions(context)


    def redraw_regions(self, context):
        for area in context.window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1


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
        self.unregister_draw_handler(context)


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.bevel.name)
        bpy.ops.object.modifier_remove(modifier=self.wn.name)
        self.unregister_draw_handler(context)


def draw_text_callback(self, context):
    cursor_offset_x = 20
    cursor_offset_y = -100

    blf.size(0, 24, 72)
    blf.color(0, 1.0, 0.529, 0.216, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y, 0)
    blf.draw(0, "ND — Faux Bevel")
    
    blf.size(0, 16, 72)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 25, 0)
    blf.draw(0, "Width: {0:.1f}mm".format(self.width * 1000))
    
    blf.size(0, 11, 72)
    blf.color(0, 1.0, 1.0, 1.0, 0.3)
    blf.position(0, self.mouse_x + cursor_offset_x, self.mouse_y + cursor_offset_y - 40, 0)
    blf.draw(0, "(±1mm)  |  Shift (±0.1mm)")

    self.redraw_regions(context)


def menu_func(self, context):
    self.layout.operator(ND_OT_faux_bevel.bl_idname, text=ND_OT_faux_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_faux_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_faux_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
