import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys


class ND_OT_vertex_bevel(bpy.types.Operator):
    bl_idname = "nd.vertex_bevel"
    bl_label = "Vertex Bevel"
    bl_description = "Adds a vertex group bevel and weld modifier"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        width_factor = (self.base_width_factor / 10.0) if self.key_shift else self.base_width_factor
        segment_factor = 1 if self.key_shift else 2

        if self.key_toggle_pin_overlay:
            toggle_pin_overlay(self)

        elif self.key_increase_factor:
            self.base_width_factor = min(1, self.base_width_factor * 10.0)

        elif self.key_decrease_factor:
            self.base_width_factor = max(0.001, self.base_width_factor / 10.0)
        
        elif self.key_step_up:
            if self.key_alt:
                self.width += width_factor
            elif self.key_no_modifiers:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
        
        elif self.key_step_down:
            if self.key_alt:
                self.width = max(0, self.width - width_factor)
            elif self.key_no_modifiers:
                self.segments = max(1, self.segments - segment_factor)

        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}
        
        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        self.operate(context)
        update_overlay(self, context, event, x_offset=300, lines=2)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.base_width_factor = 0.01

        self.segments = 1
        self.width = 0

        self.add_vertex_group(context)
        self.add_bevel_modifier(context)

        capture_modifier_keys(self)

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
        bevel.offset_type = 'WIDTH'
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
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers)

    draw_property(
        self, 
        "Width: {0:.1f}".format(self.width * 1000), 
        "Alt (±{0:.1f})  |  Shift + Alt (±{1:.1f})".format(self.base_width_factor * 1000, (self.base_width_factor / 10) * 1000),
        active=self.key_alt,
        alt_mode=self.key_shift_alt)


def menu_func(self, context):
    self.layout.operator(ND_OT_vertex_bevel.bl_idname, text=ND_OT_vertex_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_vertex_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_vertex_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
