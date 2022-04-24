import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences


mod_bevel = "Bevel — ND B"
mod_weld = "Weld — ND B"
mod_summon_list = [mod_bevel, mod_weld]


class ND_OT_bevel(bpy.types.Operator):
    bl_idname = "nd.bevel"
    bl_label = "Bevel"
    bl_description = "Adds a bevel modifier to the selected object"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        width_factor = (self.base_width_factor / 10.0) if self.key_shift else self.base_width_factor
        profile_factor = 0.01 if self.key_shift else 0.1
        segment_factor = 1 if self.key_shift else 2

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        elif self.key_toggle_pin_overlay:
            toggle_pin_overlay(self, event)

        elif self.operator_passthrough:
            update_overlay(self, context, event)

            return {'PASS_THROUGH'}

        elif self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        elif self.key_increase_factor:
            if self.key_no_modifiers:
                self.base_width_factor = min(1, self.base_width_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_no_modifiers:
                self.base_width_factor = max(0.001, self.base_width_factor / 10.0)
        
        elif pressed(event, {'H'}):
            self.harden_normals = not self.harden_normals
            self.dirty = True

        elif self.key_step_up:
            if self.key_alt:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
            elif self.key_ctrl:
                self.profile = min(1, self.profile + profile_factor)
            elif self.key_ctrl_alt:
                self.harden_normals = not self.harden_normals
            elif self.key_no_modifiers:
                self.width += width_factor
            
            self.dirty = True
        
        elif self.key_step_down:
            if self.key_alt:
                self.segments = max(1, self.segments - segment_factor)
            elif self.key_ctrl:
                self.profile = max(0, self.profile - profile_factor)
            elif self.key_ctrl_alt:
                self.harden_normals = not self.harden_normals
            elif self.key_no_modifiers:
                self.width = max(0, self.width - width_factor)

            self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.key_no_modifiers:
                self.width = max(0, self.width + self.mouse_value)
            elif self.key_ctrl:
                self.profile = max(0, min(1, self.profile + self.mouse_value))

            self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_width_factor = 0.01

        self.segments = 1
        self.width = 0
        self.profile = 0.5
        self.harden_normals = False

        mods = context.active_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if previous_op:
            self.summon_old_operator(context, mods)
        else:
            self.prepare_new_operator(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.object.type == 'MESH'


    def prepare_new_operator(self, context):
        self.summoned = False

        self.add_bevel_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.bevel = mods[mod_bevel]

        self.width_prev = self.width = self.bevel.width
        self.segments_prev = self.segments = self.bevel.segments
        self.profile_prev = self.profile = self.bevel.profile
        self.harden_normals_prev = self.harden_normals = self.bevel.harden_normals


    def add_bevel_modifier(self, context):
        bevel = context.object.modifiers.new(mod_bevel, 'BEVEL')
        bevel.offset_type = 'WIDTH'

        self.bevel = bevel

    
    def add_weld_modifier(self, context):
        mods = context.active_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if not previous_op:
            weld = context.object.modifiers.new(mod_weld, type='WELD')
            weld.merge_threshold = 0.00001

            self.weld = weld


    def operate(self, context):
        self.bevel.width = self.width
        self.bevel.segments = self.segments
        self.bevel.profile = self.profile
        self.bevel.harden_normals = self.harden_normals

        self.dirty = False


    def finish(self, context):
        self.add_weld_modifier(context)
        unregister_draw_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.bevel.name)

        if self.summoned:
            self.bevel.width = self.width_prev
            self.bevel.segments = self.segments_prev
            self.bevel.profile = self.profile_prev

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self,
        "Width: {0:.1f}".format(self.width * 1000), 
        "(±{0:.1f})  |  Shift (±{1:.1f})".format(self.base_width_factor * 1000, (self.base_width_factor / 10) * 1000),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True)

    draw_property(
        self,
        "Segments: {}".format(self.segments), 
        "Alt (±2)  |  Shift (±1)",
        active=self.key_alt,
        alt_mode=self.key_shift_alt)

    draw_property(
        self, 
        "Profile: {0:.2f}".format(self.profile),
        "Ctrl (±0.1)  |  Shift + Ctrl (±0.01)",
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True)

    draw_property(
        self, 
        "Harden Normals [H]: {0}".format("Yes" if self.harden_normals else "No"),
        "Ctrl + Alt (Yes, No)",
        active=self.key_ctrl_alt,
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_bevel.bl_idname, text=ND_OT_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_bevel)


def unregister():
    bpy.utils.unregister_class(ND_OT_bevel)
    unregister_draw_handler()
