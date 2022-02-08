import bpy
import bmesh
from math import radians
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys


mod_displace = "Offset — ND SOL"
mod_solidify = "Thickness — ND SOL"
mod_summon_list = [mod_displace, mod_solidify]


class ND_OT_solidify(bpy.types.Operator):
    bl_idname = "nd.solidify"
    bl_label = "Solidify"
    bl_description = "Adds a solidify modifier, and enables smoothing"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        thickness_factor = (self.base_thickness_factor / 10.0) if self.key_shift else self.base_thickness_factor
        offset_factor = (self.base_offset_factor / 10.0) if self.key_shift else self.base_offset_factor

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
            if self.key_ctrl:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)
            elif self.key_no_modifiers:
                self.base_thickness_factor = min(1, self.base_thickness_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_ctrl:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)
            elif self.key_no_modifiers:
               self.base_thickness_factor = max(0.001, self.base_thickness_factor / 10.0)

        elif self.key_step_up:
            if self.key_alt:
                self.weighting = min(1, self.weighting + 1)
            elif self.key_ctrl:
                self.offset += offset_factor
            elif self.key_no_modifiers:
                self.thickness += thickness_factor
            
        elif self.key_step_down:
            if self.key_alt:
                self.weighting = max(-1, self.weighting - 1)
            elif self.key_ctrl:
                self.offset -= offset_factor
            elif self.key_no_modifiers:
                self.thickness = max(0, self.thickness - thickness_factor)
        
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
        self.base_thickness_factor = 0.01
        self.base_offset_factor = 0.001

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


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1

    
    def prepare_new_operator(self, context):
        self.summoned = False

        self.thickness = 0.02
        self.weighting = 0
        self.offset = 0

        self.add_smooth_shading(context)
        self.add_displace_modifier(context)
        self.add_solidify_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.solidify = mods[mod_solidify]
        self.displace = mods[mod_displace]

        self.thickness_prev = self.thickness = self.solidify.thickness
        self.weighting_prev = self.weighting = self.solidify.offset
        self.offset_prev = self.offset = self.displace.strength


    def add_smooth_shading(self, context):
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        context.object.data.auto_smooth_angle = radians(30)


    def add_displace_modifier(self, context):
        displace = context.object.modifiers.new(mod_displace, 'DISPLACE')
        displace.strength = self.offset

        self.displace = displace


    def add_solidify_modifier(self, context):
        solidify = context.object.modifiers.new(mod_solidify, 'SOLIDIFY')
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
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.displace.name)
            bpy.ops.object.modifier_remove(modifier=self.solidify.name)

        if self.summoned:
            self.solidify.thickness = self.thickness_prev
            self.solidify.offset = self.weighting_prev
            self.displace.strength = self.offset_prev
        
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "Thickness: {0:.1f}".format(self.thickness * 1000), 
        "(±{0:.1f})  |  Shift + (±{1:.1f})".format(self.base_thickness_factor * 1000, (self.base_thickness_factor / 10) * 1000),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers)

    draw_property(
        self, 
        "Weighting: {}".format(['Negative', 'Neutral', 'Positive'][1 + round(self.weighting)]),
        "Alt (Negative, Neutral, Positive)",
        active=self.key_alt,
        alt_mode=False)

    draw_property(
        self, 
        "Offset: {0:.1f}".format(self.offset * 1000), 
        "Ctrl (±{0:.1f})  |  Shift + Ctrl (±{1:.1f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl)


def menu_func(self, context):
    self.layout.operator(ND_OT_solidify.bl_idname, text=ND_OT_solidify.bl_label)


def register():
    bpy.utils.register_class(ND_OT_solidify)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_solidify)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler(self, ND_OT_solidify.bl_label)
