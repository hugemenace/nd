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
from math import radians
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import new_modifier


mod_bevel = "Bevel — ND EB"
mod_weld = "Weld — ND EB"
mod_summon_list = [mod_bevel, mod_weld]


class ND_OT_edge_bevel(bpy.types.Operator):
    bl_idname = "nd.edge_bevel"
    bl_label = "Edge Bevel"
    bl_description = """Adds a weighted edge bevel modifier to the selected object
SHIFT — Place modifiers at the top of the stack"""
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        weight_factor = 0.01 if self.key_shift else 0.1
        width_factor = 0.01 if self.key_shift else 0.1
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

        elif self.key_numeric_input:
            if self.key_no_modifiers:
                self.weight_input_stream = update_stream(self.weight_input_stream, event.type)
                self.weight = get_stream_value(self.weight_input_stream)
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=1))
                self.dirty = True
            elif self.key_ctrl:
                self.profile_input_stream = update_stream(self.profile_input_stream, event.type)
                self.profile = get_stream_value(self.profile_input_stream)
                self.dirty = True
            elif self.key_ctrl_alt:
                self.width_input_stream = update_stream(self.width_input_stream, event.type)
                self.width = get_stream_value(self.width_input_stream, 0.001)
                self.dirty = True

        elif self.key_reset:
            if self.key_no_modifiers:
                self.weight_input_stream = new_stream()
                self.weight = 0
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = new_stream()
                self.segments = 1
                self.dirty = True
            elif self.key_ctrl:
                self.profile_input_stream = new_stream()
                self.profile = 0.5
                self.dirty = True
            elif self.key_ctrl_alt:
                self.width_input_stream = new_stream()
                self.width = 0.5
                self.dirty = True

        elif pressed(event, {'H'}):
            self.harden_normals = not self.harden_normals
            self.dirty = True

        elif pressed(event, {'W'}):
            self.target_object.show_wire = not self.target_object.show_wire
            self.target_object.show_in_front = not self.target_object.show_in_front

        elif self.key_increase_factor:
            if no_stream(self.weight_input_stream) and self.key_no_modifiers:
                self.base_weight_factor = min(1, self.base_weight_factor * 10.0)

        elif self.key_decrease_factor:
            if no_stream(self.weight_input_stream) and self.key_no_modifiers:
                self.base_weight_factor = max(0.001, self.base_weight_factor / 10.0)
        
        elif self.key_step_up:
            if no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = min(1, self.profile + profile_factor)
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_ctrl_alt:
                self.width = max(0, self.width + width_factor)
                self.dirty = True
            elif no_stream(self.weight_input_stream) and self.key_no_modifiers:
                self.weight = max(0, min(1, self.weight + weight_factor))
                self.dirty = True
        
        elif self.key_step_down:
            if no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(1, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = max(0, self.profile - profile_factor)
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_ctrl_alt:
                self.width = max(0, self.width - width_factor)
                self.dirty = True
            elif no_stream(self.weight_input_stream) and self.key_no_modifiers:
                self.weight = max(0, min(1, self.weight - weight_factor))
                self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.width_input_stream) and self.key_ctrl_alt:
                self.width = max(0, self.width + self.mouse_value)
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = max(0, min(1, self.profile + self.mouse_value))
                self.dirty = True
            elif no_stream(self.weight_input_stream) and self.key_no_modifiers:
                self.weight = max(0, min(1, self.weight + self.mouse_value))
                self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.early_apply = event.shift

        self.segments = 1
        self.weight = 0
        self.width = 0.5
        self.profile = 0.5
        self.harden_normals = False

        self.segments_input_stream = new_stream()
        self.weight_input_stream = new_stream()
        self.width_input_stream = new_stream()
        self.profile_input_stream = new_stream()

        self.target_object = context.active_object

        if not context.active_object.data.use_customdata_edge_bevel:
            context.active_object.data.use_customdata_edge_bevel = True

        self.take_edges_snapshot(context)

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
        if context.mode == 'EDIT_MESH':
            mesh = bmesh.from_edit_mesh(context.active_object.data)
            return len([edge for edge in mesh.edges if edge.select]) >= 1


    def prepare_new_operator(self, context):
        self.summoned = False

        self.add_smooth_shading(context)
        self.add_bevel_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.bevel = mods[mod_bevel]

        self.width_prev = self.width = self.bevel.width
        self.segments_prev = self.segments = self.bevel.segments
        self.profile_prev = self.profile = self.bevel.profile
        self.harden_normals_prev = self.harden_normals = self.bevel.harden_normals
        self.weight = self.edge_weight_average


    def add_smooth_shading(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()
        context.active_object.data.use_auto_smooth = True
        context.active_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))
        bpy.ops.object.mode_set(mode='EDIT')


    def add_bevel_modifier(self, context):
        bevel = new_modifier(context.active_object, mod_bevel, 'BEVEL', rectify=False)
        bevel.offset_type = 'WIDTH'
        bevel.limit_method = 'WEIGHT'

        self.bevel = bevel

        if self.early_apply:
            while context.active_object.modifiers[0].name != self.bevel.name:
                bpy.ops.object.modifier_move_up(modifier=self.bevel.name)


    def add_weld_modifier(self, context):
        mods = context.active_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if not previous_op:
            weld = new_modifier(context.active_object, mod_weld, 'WELD', rectify=False)
            weld.merge_threshold = 0.00001

            self.weld = weld

            if self.early_apply:
                while context.active_object.modifiers[1].name != self.weld.name:
                    bpy.ops.object.modifier_move_up(modifier=self.weld.name)


    def take_edges_snapshot(self, context):
        self.edges_snapshot = {}
        self.edge_weight_average = 0
        
        data = context.active_object.data
        bm = bmesh.from_edit_mesh(data)
        bevel_weight_layer = bm.edges.layers.bevel_weight.verify()
    
        selected_edges = [edge for edge in bm.edges if edge.select]
        for edge in selected_edges:
            self.edges_snapshot[edge.index] = edge[bevel_weight_layer]
            self.edge_weight_average += edge[bevel_weight_layer]

        self.edge_weight_average /= len(selected_edges)


    def operate(self, context):
        self.bevel.width = self.width
        self.bevel.segments = self.segments
        self.bevel.profile = self.profile
        self.bevel.harden_normals = self.harden_normals

        data = context.active_object.data
        bm = bmesh.from_edit_mesh(data)
        bevel_weight_layer = bm.edges.layers.bevel_weight.verify()
    
        selected_edges = [edge for edge in bm.edges if edge.select]
        for edge in selected_edges:
            edge[bevel_weight_layer] = self.weight
    
        bmesh.update_edit_mesh(data)

        self.dirty = False


    def finish(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False
        self.add_weld_modifier(context)
        unregister_draw_handler()


    def revert(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False

        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.bevel.name)

        if self.summoned:
            self.bevel.width = self.width_prev
            self.bevel.segments = self.segments_prev
            self.bevel.profile = self.profile_prev

        data = context.active_object.data
        bm = bmesh.from_edit_mesh(data)
        bevel_weight_layer = bm.edges.layers.bevel_weight.verify()
    
        selected_edges = [edge for edge in bm.edges if edge.select]
        for edge in selected_edges:
            edge[bevel_weight_layer] = self.edges_snapshot[edge.index]
    
        bmesh.update_edit_mesh(data)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self,
        "Weight: {0:.2f} ({1:.2f})".format(self.weight, self.width * 1000 * self.weight),
        "(±0.1)  |  Shift (±0.01)",
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.weight_input_stream)

    draw_property(
        self,
        "Segments: {}".format(self.segments), 
        "Alt (±2)  |  Shift (±1)",
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        input_stream=self.segments_input_stream)

    draw_property(
        self, 
        "Profile: {0:.2f}".format(self.profile),
        "Ctrl (±0.1)  |  Shift + Ctrl (±0.01)",
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.profile_input_stream)

    draw_property(
        self,
        "Width: {0:.2f}".format(self.width * 1000),
        "Ctrl + Alt (±100) | Shift + Ctrl + Alt (±10)",
        active=self.key_ctrl_alt,
        alt_mode=self.key_shift_ctrl_alt,
        mouse_value=True,
        input_stream=self.width_input_stream)

    draw_hint(
        self,
        "Harden Normals [H]: {0}".format("Yes" if self.harden_normals else "No"),
        "Match normals of new faces to adjacent faces")

    draw_hint(
        self,
        "Enhanced Wireframe [W]: {0}".format("Yes" if self.target_object.show_wire else "No"),
        "Display the objects's wireframe over solid shading")


def register():
    bpy.utils.register_class(ND_OT_edge_bevel)


def unregister():
    bpy.utils.unregister_class(ND_OT_edge_bevel)
    unregister_draw_handler()
