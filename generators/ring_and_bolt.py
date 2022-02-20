import bpy
import bmesh
from math import radians
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor
from .. lib.events import capture_modifier_keys


mod_displace = "Radius — ND R&B"
mod_screw_1 = "Width — ND R&B"
mod_screw_2 = "Segments — ND R&B"
mod_decimate = "Decimate — ND R&B"
mod_summon_list = [mod_displace, mod_screw_1, mod_screw_2]


class ND_OT_ring_and_bolt(bpy.types.Operator):
    bl_idname = "nd.ring_and_bolt"
    bl_label = "Ring & Bolt"
    bl_description = "Adds a ring or ring_and_bolt face at the 3D cursor"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        inner_radius_factor = (self.base_inner_radius_factor / 10.0) if self.key_shift else self.base_inner_radius_factor
        width_factor = (self.base_width_factor / 10.0) if self.key_shift else self.base_width_factor
        segment_factor = 1 if self.key_shift else 2

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        elif self.key_toggle_pin_overlay:
            toggle_pin_overlay(self)

        elif self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        elif self.operator_passthrough:
            self.update_overlay_wrapper(context, event)

            return {'PASS_THROUGH'}

        elif self.key_increase_factor:
            if self.key_alt:
                self.base_inner_radius_factor = min(1, self.base_inner_radius_factor * 10.0)
            elif self.key_ctrl:
                self.base_width_factor = min(1, self.base_width_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_alt:
                self.base_inner_radius_factor = max(0.001, self.base_inner_radius_factor / 10.0)
            elif self.key_ctrl:
                self.base_width_factor = max(0.001, self.base_width_factor / 10.0)
        
        elif self.key_step_up:
            if self.key_alt:
                self.inner_radius += inner_radius_factor
            elif self.key_ctrl:
                self.width += width_factor
            elif self.key_no_modifiers:
                self.segments = 4 if self.segments == 3 else self.segments + segment_factor

        elif self.key_step_down:
            if self.key_alt:
                self.inner_radius = max(0, self.inner_radius - inner_radius_factor)
                self.width = max(self.inner_radius * -0.5, self.width)
            elif self.key_ctrl:
                self.width = max(self.inner_radius * -0.5, self.width - width_factor)
            elif self.key_no_modifiers:
                self.segments = max(3, self.segments - segment_factor)

        elif self.key_confirm:
            self.finish(context)
            
            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}
        
        self.operate(context)
        self.update_overlay_wrapper(context, event)

        return {'RUNNING_MODAL'}


    def update_overlay_wrapper(self, context, event):
        update_overlay(self, context, event, x_offset=300, lines=3)


    def invoke(self, context, event):
        self.base_inner_radius_factor = 0.001
        self.base_width_factor = 0.001

        if len(context.selected_objects) == 1:
            mods = context.active_object.modifiers
            mod_names = list(map(lambda x: x.name, mods))
            previous_op = all(m in mod_names for m in mod_summon_list)

            if previous_op:
                self.summon_old_operator(context, mods)
            else:
                self.prepare_new_operator(context)
        else:
            self.prepare_new_operator(context)
        
        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    

    def prepare_new_operator(self, context):
        self.summoned = False

        self.segments = 3
        self.inner_radius = 0
        self.width = 0.05

        bpy.ops.object.select_all(action='DESELECT')

        add_single_vertex_object(self, context, "Bolt")
        align_object_to_3d_cursor(self, context)

        self.add_displace_modifier()
        self.add_screw_x_modifier()
        self.add_screw_z_modifer()

    
    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.try_remove_decimate_modifier(context)

        self.displace = mods[mod_displace]
        self.screwX = mods[mod_screw_1]
        self.screwZ = mods[mod_screw_2]

        self.segments_prev = self.segments = self.screwZ.steps
        self.inner_radius_prev = self.inner_radius = self.displace.strength
        self.width_prev = self.width = self.screwX.screw_offset

        self.obj = context.active_object


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def add_displace_modifier(self):
        displace = self.obj.modifiers.new(mod_displace, 'DISPLACE')
        displace.mid_level = 0.5
        displace.strength = self.inner_radius
        displace.direction = 'X'
        displace.space = 'LOCAL'
        
        self.displace = displace


    def add_screw_x_modifier(self):
        screwX = self.obj.modifiers.new(mod_screw_1, 'SCREW')
        screwX.axis = 'X'
        screwX.angle = 0
        screwX.screw_offset = self.width
        screwX.steps = 1
        screwX.render_steps = 1
        screwX.use_merge_vertices = True
        screwX.merge_threshold = 0.0001

        self.screwX = screwX
    

    def add_screw_z_modifer(self):
        screwZ = self.obj.modifiers.new(mod_screw_2, 'SCREW')
        screwZ.axis = 'Z'
        screwZ.steps = self.segments
        screwZ.render_steps = self.segments
        screwZ.use_merge_vertices = True
        screwZ.merge_threshold = 0.0001
        screwZ.use_normal_calculate = True

        self.screwZ = screwZ

    
    def add_decimate_modifier(self):
        decimate = self.obj.modifiers.new(mod_decimate, 'DECIMATE')
        decimate.decimate_type = 'DISSOLVE'
        decimate.angle_limit = radians(1)
        
        self.decimate = decimate

        all_mods = self.obj.modifiers.values()
        decimate_index = all_mods.index(self.screwZ) + 1

        while self.obj.modifiers[decimate_index].name != self.decimate.name:
            bpy.ops.object.modifier_move_up(modifier=self.decimate.name)


    def try_remove_decimate_modifier(self, context):
        self.had_decimate_mod = False

        try:
            mod = context.active_object.modifiers[mod_decimate]
            context.active_object.modifiers.remove(mod)
            self.had_decimate_mod = True
        except:
            self.had_decimate_mod = False


    def operate(self, context):
        self.screwX.screw_offset = self.width
        self.screwZ.steps = self.segments
        self.screwZ.render_steps = self.segments
        self.displace.strength = self.inner_radius


    def select_ring_and_bolt(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)


    def finish(self, context):
        if not self.summoned:
            self.select_ring_and_bolt(context)

        if self.segments > 3:
            self.add_decimate_modifier()

        unregister_draw_handler()


    def revert(self, context):
        if not self.summoned:
            self.select_ring_and_bolt(context)
            bpy.ops.object.delete()
        elif self.had_decimate_mod or self.segments > 3:
            self.add_decimate_modifier()

        if self.summoned:
            self.screwX.screw_offset = self.width_prev
            self.screwZ.steps = self.segments_prev
            self.screwZ.render_steps = self.segments_prev
            self.displace.strength = self.inner_radius_prev
            
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Segments: {}".format(self.segments), 
        "(±2)  |  Shift (±1)",
        active=self.key_no_modifiers, 
        alt_mode=False)

    draw_property(
        self, 
        "Inner Radius: {0:.1f}".format(self.inner_radius * 1000), 
        "Alt (±{0:.1f})  |  Shift + Alt (±{1:.1f})".format(self.base_inner_radius_factor * 1000, (self.base_inner_radius_factor / 10) * 1000),
        active=self.key_alt, 
        alt_mode=self.key_shift_alt)

    draw_property(
        self, 
        "{0}: {1:.1f}".format("Width" if self.inner_radius > 0 else "Radius", self.width * 2000),
        "Ctrl (±{0:.1f})  |  Shift + Ctrl (±{1:.1f})".format(self.base_width_factor * 1000, (self.base_width_factor / 10) * 1000),
        active=self.key_ctrl, 
        alt_mode=self.key_shift_ctrl)


def menu_func(self, context):
    self.layout.operator(ND_OT_ring_and_bolt.bl_idname, text=ND_OT_ring_and_bolt.bl_label)


def register():
    bpy.utils.register_class(ND_OT_ring_and_bolt)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_ring_and_bolt)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
