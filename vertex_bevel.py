import bpy
import bmesh
from . overlay import update_overlay, init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property


class ND_OT_vertex_bevel(bpy.types.Operator):
    bl_idname = "nd.vertex_bevel"
    bl_label = "Vertex Bevel"
    bl_description = "Adds a vertex group bevel and weld modifier"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        width_factor = (self.base_width_factor / 10.0) if event.shift else self.base_width_factor
        segment_factor = 1 if event.shift else 2

        self.key_shift = event.shift
        self.key_alt = event.alt

        if event.type == 'P' and event.value == 'PRESS':
            self.pin_overlay = not self.pin_overlay

        elif event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'} and event.value == 'PRESS':
            self.base_width_factor = min(1, self.base_width_factor * 10.0)

        elif event.type in {'MINUS', 'NUMPAD_MINUS'} and event.value == 'PRESS':
            self.base_width_factor = max(0.001, self.base_width_factor / 10.0)
        
        elif event.type == 'WHEELUPMOUSE':
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
        
        elif event.type == 'MIDDLEMOUSE' or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF'):
            return {'PASS_THROUGH'}

        self.operate(context)
        update_overlay(self, context, event, pinned=self.pin_overlay, x_offset=300, lines=2)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.base_width_factor = 0.01

        self.segments = 1
        self.width = 0.001

        self.key_shift = False
        self.key_alt = False

        self.add_vertex_group(context)
        self.add_bevel_modifier(context)

        self.pin_overlay = False
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


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
        unregister_draw_handler()
    

    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.bevel.name)
        context.object.vertex_groups.remove(self.vgroup)
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Segments: {}".format(self.segments), 
        "(±2)  |  Shift (±1)",
        active=(not self.key_alt),
        alt_mode=(self.key_shift and not self.key_alt))

    draw_property(
        self, 
        "Width: {0:.1f}mm".format(self.width * 1000), 
        "Alt (±{0:.1f}mm)  |  Shift + Alt (±{1:.1f}mm)".format(self.base_width_factor * 1000, (self.base_width_factor / 10) * 1000),
        active=(self.key_alt),
        alt_mode=(self.key_shift and self.key_alt))


def menu_func(self, context):
    self.layout.operator(ND_OT_vertex_bevel.bl_idname, text=ND_OT_vertex_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_vertex_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_vertex_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()


if __name__ == "__main__":
    register()
