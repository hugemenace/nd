# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)
# 
# ---
# Contributors: Tristo (HM)
# ---

import bpy
import bmesh
from math import radians, isclose, cos
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import new_modifier


mod_displace = "Radius — ND RCP"
mod_screw_1 = "Width — ND RCP"
mod_screw_2 = "Segments — ND RCP"
mod_decimate = "Decimate — ND RCP"
mod_summon_list = [mod_displace, mod_screw_1, mod_screw_2]


class ND_OT_recon_poly(BaseOperator):
    bl_idname = "nd.recon_poly"
    bl_label = "Recon Poly"
    bl_description = "Adds a regular convex polygon at the 3D cursor"


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        inner_radius_factor = ((self.base_inner_radius_factor / 10.0) if self.key_shift else self.base_inner_radius_factor) * self.unit_factor
        width_factor = ((self.base_width_factor / 10.0) if self.key_shift else self.base_width_factor) * self.unit_factor
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

        elif self.key_numeric_input:
            if self.key_no_modifiers:
                self.width_input_stream = update_stream(self.width_input_stream, event.type)
                self.width = get_stream_value(self.width_input_stream, 0.001 * self.unit_factor)
                self.dirty = True
            elif self.key_ctrl:
                self.inner_radius_input_stream = update_stream(self.inner_radius_input_stream, event.type)
                self.inner_radius = get_stream_value(self.inner_radius_input_stream, 0.001 * self.unit_factor)
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=3))
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.width_input_stream = new_stream()
                self.width = 0.05
                self.dirty = True
            elif self.key_ctrl:
                self.inner_radius_input_stream = new_stream()
                self.inner_radius = 0
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = new_stream()
                self.segments = 3
                self.dirty = True

        elif pressed(event, {'R'}):
            self.natural_rotation = not self.natural_rotation
            self.dirty = True

        elif pressed(event, {'E'}):
            self.inscribed = not self.inscribed
            self.dirty = True

        elif self.key_increase_factor:
            if no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.base_width_factor = min(1, self.base_width_factor * 10.0)
            elif no_stream(self.inner_radius_input_stream) and self.key_ctrl:
                self.base_inner_radius_factor = min(1, self.base_inner_radius_factor * 10.0)

        elif self.key_decrease_factor:
            if no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.base_width_factor = max(0.001, self.base_width_factor / 10.0)
            elif no_stream(self.inner_radius_input_stream) and self.key_ctrl:
                self.base_inner_radius_factor = max(0.001, self.base_inner_radius_factor / 10.0)
        
        elif self.key_step_up:
            if no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = 4 if self.segments == 3 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.inner_radius_input_stream) and self.key_ctrl:
                self.inner_radius += inner_radius_factor
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width += width_factor
                self.dirty = True

        elif self.key_step_down:
            if no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(3, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.inner_radius_input_stream) and self.key_ctrl:
                self.inner_radius = max(0, self.inner_radius - inner_radius_factor)
                self.width = max(self.computed_inner_radius() * -1, self.width)
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(self.computed_inner_radius() * -1, self.width - width_factor)
                self.dirty = True

        elif self.key_confirm:
            self.finish(context)
            
            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}
        
        if get_preferences().enable_mouse_values:
            if no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(self.computed_inner_radius() * -1, self.width + self.mouse_value)
                self.dirty = True
            elif no_stream(self.inner_radius_input_stream) and self.key_ctrl:
                self.inner_radius = max(0, self.inner_radius + self.mouse_value)
                self.width = max(self.computed_inner_radius() * -1, self.width)
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(3, self.segments + self.mouse_step)
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def do_invoke(self, context, event):
        self.dirty = False
        self.base_inner_radius_factor = 0.001
        self.base_width_factor = 0.001

        self.segments_input_stream = new_stream()
        self.inner_radius_input_stream = new_stream()
        self.width_input_stream = new_stream()

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
        
        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    

    def prepare_new_operator(self, context):
        self.summoned = False

        self.segments = 3
        self.inner_radius = 0
        self.width = 0.05
        self.natural_rotation = False
        self.inscribed = get_preferences().recon_poly_inscribed

        bpy.ops.object.select_all(action='DESELECT')

        add_single_vertex_object(self, context, "Recon Poly")
        align_object_to_3d_cursor(self, context)

        self.add_displace_modifier()
        self.add_screw_x_modifier()
        self.add_screw_z_modifer()

        self.rotation_snapshot = self.obj.rotation_euler.copy()

    
    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.try_remove_decimate_modifier(context)

        self.displace = mods[mod_displace]
        self.screwX = mods[mod_screw_1]
        self.screwZ = mods[mod_screw_2]
        
        self.obj = context.active_object

        self.computed_width_prev = self.screwX.screw_offset
        self.computed_inner_radius_prev = self.displace.strength

        self.segments_prev = self.segments = self.screwZ.steps

        computed_inner_radius = self.displace.strength
        try:
            computed_inner_radius = float(bpy.data.objects[self.obj.name]["NDRCP_inner_radius"])
        except:
            pass
        self.inner_radius_prev = self.inner_radius = computed_inner_radius
        
        computed_width = self.screwX.screw_offset
        try:
            computed_width = float(bpy.data.objects[self.obj.name]["NDRCP_width"])
        except:
            pass
        self.width_prev = self.width = computed_width
        
        computed_natural_rotation = False
        try:
            computed_natural_rotation = bool(bpy.data.objects[self.obj.name]["NDRCP_natural_rotation"])
        except:
            pass
        self.natural_rotation_prev = self.natural_rotation = computed_natural_rotation

        computed_inscribed = get_preferences().recon_poly_inscribed
        try:
            computed_inscribed = bool(bpy.data.objects[self.obj.name]["NDRCP_inscribed"])
        except:
            pass
        self.inscribed_prev = self.inscribed = computed_inscribed

        self.rotation_snapshot = self.obj.rotation_euler.copy()
        self.rotation_prev = self.obj.rotation_euler.copy()

        if self.natural_rotation:
            self.rotation_prev = self.obj.rotation_euler.copy()
            self.obj.rotation_euler.rotate_axis('Z', radians((360 / self.segments) / 2) * -1)
            self.rotation_snapshot = self.obj.rotation_euler.copy()
            self.obj.rotation_euler = self.rotation_prev


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def add_displace_modifier(self):
        displace = new_modifier(self.obj, mod_displace, 'DISPLACE', rectify=False)
        displace.mid_level = 0
        displace.direction = 'X'
        displace.space = 'LOCAL'
        
        self.displace = displace


    def add_screw_x_modifier(self):
        screwX = new_modifier(self.obj, mod_screw_1, 'SCREW', rectify=False)
        screwX.axis = 'X'
        screwX.angle = 0
        screwX.steps = 1
        screwX.render_steps = 1
        screwX.use_merge_vertices = True
        screwX.merge_threshold = 0.0001

        self.screwX = screwX
    

    def add_screw_z_modifer(self):
        screwZ = new_modifier(self.obj, mod_screw_2, 'SCREW', rectify=False)
        screwZ.axis = 'Z'
        screwZ.use_merge_vertices = True
        screwZ.merge_threshold = 0.0001
        screwZ.use_normal_calculate = True

        self.screwZ = screwZ

    
    def add_decimate_modifier(self):
        decimate = new_modifier(self.obj, mod_decimate, 'DECIMATE', rectify=False)
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

    
    def computed_width(self):
        if self.inscribed or self.inner_radius > 0:
            return self.width

        theta = radians((360 / self.segments) / 2)
        return self.width / cos(theta)


    def computed_inner_radius(self):
        if self.inscribed or self.inner_radius == 0:
            return self.inner_radius

        theta = radians((360 / self.segments) / 2)
        return self.inner_radius / cos(theta)


    def operate(self, context):
        bpy.data.objects[self.obj.name]["NDRCP_natural_rotation"] = self.natural_rotation
        bpy.data.objects[self.obj.name]["NDRCP_inscribed"] = self.inscribed
        bpy.data.objects[self.obj.name]["NDRCP_width"] = self.width
        bpy.data.objects[self.obj.name]["NDRCP_inner_radius"] = self.inner_radius

        self.screwX.screw_offset = self.computed_width()
        self.displace.strength = self.computed_inner_radius()

        self.screwZ.steps = self.segments
        self.screwZ.render_steps = self.segments

        self.obj.rotation_euler = self.rotation_snapshot

        if self.natural_rotation:
            self.obj.rotation_euler.rotate_axis('Z', radians((360 / self.segments) / 2))

        self.dirty = False


    def select_recon_poly(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)


    def finish(self, context):
        if not self.summoned:
            self.select_recon_poly(context)

        if self.segments > 3:
            self.add_decimate_modifier()

        unregister_draw_handler()

        if not self.summoned and get_preferences().recon_poly_solidify:
            bpy.ops.nd.solidify('INVOKE_DEFAULT')


    def revert(self, context):
        if not self.summoned:
            self.select_recon_poly(context)
            bpy.ops.object.delete()
        elif self.had_decimate_mod or self.segments > 3:
            self.add_decimate_modifier()

        if self.summoned:
            self.screwX.screw_offset = self.computed_width_prev
            self.displace.strength = self.computed_inner_radius_prev
            self.screwZ.steps = self.segments_prev
            self.screwZ.render_steps = self.segments_prev
            self.obj.rotation_euler = self.rotation_prev

            bpy.data.objects[self.obj.name]["NDRCP_natural_rotation"] = self.natural_rotation_prev
            bpy.data.objects[self.obj.name]["NDRCP_inscribed"] = self.inscribed_prev
            bpy.data.objects[self.obj.name]["NDRCP_width"] = self.width_prev
            bpy.data.objects[self.obj.name]["NDRCP_inner_radius"] = self.inner_radius_prev
            
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    unit_scale = (1000 * bpy.data.scenes["Scene"].unit_settings.scale_length) / self.unit_factor

    draw_property(
        self,
        f"{('Width' if self.inner_radius > 0 else 'Radius')}: {(self.width * unit_scale):.2f}{self.unit_suffix}",
        f"(±{(self.base_width_factor * 1.0):.2f}{self.unit_suffix})  |  Shift (±{((self.base_width_factor / 10) * 1.0):.2f}{self.unit_suffix})",
        active=self.key_no_modifiers, 
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.width_input_stream)

    draw_property(
        self,
        "Segments: {}".format(self.segments), 
        "Alt (±2)  |  Shift + Alt (±1)",
        active=self.key_alt, 
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.segments_input_stream)

    draw_property(
        self,
        f"Inner Radius: {(self.inner_radius * unit_scale):.2f}{self.unit_suffix}", 
        f"Ctrl (±{(self.base_inner_radius_factor * 1.0):.2f}{self.unit_suffix})  |  Shift + Ctrl (±{((self.base_inner_radius_factor / 10) * 1.0):.2f}{self.unit_suffix})",
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.inner_radius_input_stream)

    draw_hint(
        self,
        "Natural Rotation [R]: {}".format("Yes" if self.natural_rotation else "No"),
        "Ensure the rightmost edge is perpendicular to the X axis")

    draw_hint(
        self,
        "Extents [E]: {}".format("Inscribed" if self.inscribed else "Circumscribed"),
        "The extents of the polygon (inscribed or circumscribed)")


def register():
    bpy.utils.register_class(ND_OT_recon_poly)


def unregister():
    bpy.utils.unregister_class(ND_OT_recon_poly)
    unregister_draw_handler()
