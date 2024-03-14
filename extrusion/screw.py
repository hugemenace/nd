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
from math import radians, degrees
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with


mod_displace = "Offset — ND SCR"
mod_screw = "Screw — ND SCR"
mod_mesh_summon_list = [mod_displace, mod_screw]
mod_curve_summon_list = [mod_screw]


class ND_OT_screw(BaseOperator):
    bl_idname = "nd.screw"
    bl_label = "Screw"
    bl_description = """Adds a screw modifier tuned for converting a sketch into a cylindrical object
CTRL — Remove existing modifiers"""


    def do_modal(self, context, event):
        segment_factor = 1 if self.key_shift else 2
        angle_factor = 1 if self.key_shift else 10

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=3))
                self.dirty = True
            elif self.key_alt:
                self.angle_input_stream = update_stream(self.angle_input_stream, event.type)
                self.angle = get_stream_value(self.angle_input_stream)
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = update_stream(self.offset_input_stream, event.type)
                self.offset = get_stream_value(self.offset_input_stream, self.unit_scaled_factor)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                self.segments_input_stream = new_stream()
                self.segments = 3
                self.dirty = True
            elif self.key_alt:
                self.angle_input_stream = new_stream()
                self.angle = 360
                self.dirty = True
            elif self.key_ctrl:
                self.offset_input_stream = new_stream()
                self.offset = 0
                self.dirty = True

        if pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        if pressed(event, {'O'}):
            self.offset_axis = (self.offset_axis + 1) % 3
            self.dirty = True

        if pressed(event, {'F'}):
            self.flip_normals = not self.flip_normals
            self.dirty = True

        if self.key_step_up:
            if no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.step_size
                self.dirty = True
            elif no_stream(self.angle_input_stream) and self.key_alt:
                self.angle = min(360, self.angle + angle_factor)
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = 4 if self.segments == 3 else self.segments + segment_factor
                self.dirty = True
            
        if self.key_step_down:
            if no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset -= self.step_size
                self.dirty = True
            elif no_stream(self.angle_input_stream) and self.key_alt:
                self.angle = max(-360, self.angle - angle_factor)
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = max(3, self.segments - segment_factor)
                self.dirty = True
        
        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.offset_input_stream) and self.key_ctrl:
                self.offset += self.mouse_value
                self.dirty = True
            elif no_stream(self.angle_input_stream) and self.key_alt:
                self.angle = max(-360, min(360, self.angle + self.mouse_value_mag))
                self.dirty = True
            elif no_stream(self.segments_input_stream) and self.key_no_modifiers:
                self.segments = max(3, self.segments + self.mouse_step)
                self.dirty = True


    def do_invoke(self, context, event):
        if event.ctrl:
            remove_modifiers_ending_with(context.selected_objects, ' — ND SCR')
            return {'FINISHED'}

        self.dirty = False
        self.object_type = context.active_object.type

        self.axis = 2 # X (0), Y (1), Z (2)
        self.offset_axis = 1 # X (0), Y (1), Z (2)
        self.segments = 3
        self.angle = 360
        self.offset = 0
        self.flip_normals = True

        self.offset_input_stream = new_stream()
        self.angle_input_stream = new_stream()
        self.segments_input_stream = new_stream()

        if len(context.selected_objects) == 1:
            mods = context.active_object.modifiers
            mod_names = list(map(lambda x: x.name, mods))
            
            previous_op = False 
            if self.object_type == 'MESH':
                previous_op = all(m in mod_names for m in mod_mesh_summon_list)
            else:
                previous_op = all(m in mod_names for m in mod_curve_summon_list)

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

        init_axis(self, context.active_object, self.axis)
        register_axis_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.active_object.type in ['MESH', 'CURVE']


    def prepare_new_operator(self, context):
        self.summoned = False

        if self.object_type == 'MESH':
            self.add_smooth_shading(context)
            self.add_displace_modifier(context)

        self.add_screw_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        if self.object_type == 'MESH':
            self.displace = mods[mod_displace]

        self.screw = mods[mod_screw]

        if self.object_type == 'MESH':
            self.offset_prev = self.offset = self.displace.strength
            self.offset_axis_prev = self.offset_axis = {'X': 0, 'Y': 1, 'Z': 2}[self.displace.direction]

        self.axis_prev = self.axis = {'X': 0, 'Y': 1, 'Z': 2}[self.screw.axis]
        self.segments_prev = self.segments = self.screw.steps
        self.segments_prev = self.segments = self.screw.render_steps
        self.angle_prev = self.angle = degrees(self.screw.angle)
        self.flip_normals_prev = self.flip_normals = self.screw.use_normal_flip


    def add_smooth_shading(self, context):
        if bpy.app.version >= (4, 1, 0):
            return
            
        bpy.ops.object.shade_smooth()
        context.active_object.data.use_auto_smooth = True
        context.active_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))


    def add_displace_modifier(self, context):
        displace = new_modifier(context.active_object, mod_displace, 'DISPLACE', rectify=True)
        displace.mid_level = 0
        displace.space = 'LOCAL'

        self.displace = displace


    def add_screw_modifier(self, context):
        screw = new_modifier(context.active_object, mod_screw, 'SCREW', rectify=True)
        screw.screw_offset = 0
        screw.use_merge_vertices = True 
        screw.merge_threshold = 0.0001
        screw.use_normal_calculate = True

        self.screw = screw
    

    def operate(self, context):
        if self.object_type == 'MESH':
            self.displace.strength = self.offset
            self.displace.direction = ['X', 'Y', 'Z'][self.offset_axis]

        self.screw.axis = ['X', 'Y', 'Z'][self.axis]
        self.screw.steps = self.segments
        self.screw.render_steps = self.segments
        self.screw.angle = radians(self.angle)
        self.screw.use_normal_flip = self.flip_normals

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.screw.name)

            if self.object_type == 'MESH':
                bpy.ops.object.modifier_remove(modifier=self.displace.name)

        if self.summoned:
            if self.object_type == 'MESH':
                self.displace.strength = self.offset_prev
                self.displace.direction = ['X', 'Y', 'Z'][self.offset_axis_prev]

            self.screw.axis = ['X', 'Y', 'Z'][self.axis_prev]
            self.screw.steps = self.segments_prev
            self.screw.render_steps = self.segments_prev
            self.screw.angle = radians(self.angle_prev)

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        "Segments: {}".format(self.segments),
        self.generate_step_hint(2, 1),
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.segments_input_stream)
    
    draw_property(
        self,
        "Angle: {0:.2f}°".format(self.angle),
        self.generate_key_hint("Alt", self.generate_step_hint(10, 1)),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.angle_input_stream)

    if self.object_type == 'MESH':
        draw_property(
            self,
            f"Offset: {(self.offset * self.display_unit_scale):.2f}{self.unit_suffix}",
            self.generate_key_hint("Ctrl", self.unit_step_hint),
            active=self.key_ctrl,
            alt_mode=self.key_shift_ctrl,
            mouse_value=True,
            input_stream=self.offset_input_stream)

    draw_hint(
        self,
        "Screw Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
        "Axis to revolve around (X, Y, Z)")

    if self.object_type == 'MESH':
        draw_hint(
            self,
            "Offset Axis [O]: {}".format(['X', 'Y', 'Z'][self.offset_axis]),
            "Axis to offset origin along (X, Y, Z)")

    draw_hint(
        self,
        "Flip Normals [F]: {}".format("Yes" if self.flip_normals else "No"),
        "Flip the normals of the resulting mesh")


def register():
    bpy.utils.register_class(ND_OT_screw)


def unregister():
    bpy.utils.unregister_class(ND_OT_screw)
    unregister_draw_handler()
