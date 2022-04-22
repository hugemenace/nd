import bpy
import bmesh
from math import radians
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys
from .. lib.preferences import get_preferences


mod_bevel = "Bevel — ND WNB"
mod_wn = "Weighted Normal — ND WNB"
mod_summon_list = [mod_bevel, mod_wn]


class ND_OT_weighted_normal_bevel(bpy.types.Operator):
    bl_idname = "nd.weighted_normal_bevel"
    bl_label = "WN Bevel"
    bl_description = "Adds a single segment bevel and a weighted normal modifier"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        width_factor = (self.base_width_factor / 10.0) if event.shift else self.base_width_factor

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
            self.base_width_factor = min(1, self.base_width_factor * 10.0)

        elif self.key_decrease_factor:
            self.base_width_factor = max(0.001, self.base_width_factor / 10.0)

        elif self.key_step_up:
            self.width += width_factor

            self.dirty = True
            
        elif self.key_step_down:
            self.width = max(0.0001, self.width - width_factor)

            self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            self.width = max(0.0001, self.width + self.mouse_value)

            self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.base_width_factor = 0.001

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

        self.width = 0.001

        self.add_smooth_shading(context)
        self.add_bevel_modifier(context)
        self.add_weighted_normal_modifer(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.bevel = mods[mod_bevel]
        self.wn = mods[mod_wn]

        self.width_prev = self.width = self.bevel.width


    def add_smooth_shading(self, context):
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        context.object.data.auto_smooth_angle = radians(30)


    def add_bevel_modifier(self, context):
        bevel = context.object.modifiers.new(mod_bevel, 'BEVEL')
        bevel.segments = 1
        bevel.offset_type = 'WIDTH'

        self.bevel = bevel
    

    def add_weighted_normal_modifer(self, context):
        wn = context.object.modifiers.new(mod_wn, 'WEIGHTED_NORMAL')
        wn.weight = 100

        self.wn = wn


    def operate(self, context):
        self.bevel.width = self.width

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.bevel.name)
            bpy.ops.object.modifier_remove(modifier=self.wn.name)

        if self.summoned:
            self.bevel.width = self.width_prev

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self,
        "Width: {0:.1f}".format(self.width * 1000), 
        "(±{0:.1f})  |  Shift (±{1:.1f})".format(self.base_width_factor * 1000, (self.base_width_factor / 10) * 1000),
        active=True,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True)


def menu_func(self, context):
    self.layout.operator(ND_OT_weighted_normal_bevel.bl_idname, text=ND_OT_weighted_normal_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_weighted_normal_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_weighted_normal_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
