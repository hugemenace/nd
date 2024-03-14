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
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.modifiers import new_modifier, remove_modifiers_ending_with


mod_bevel = "Bevel — ND VB"
mod_weld = "Weld — ND VB"
mod_weld_la = "Weld — ND VB LA" # For late-application of the modifier
mod_summon_list = [mod_bevel, mod_weld]


class ND_OT_vertex_bevel(BaseOperator):
    bl_idname = "nd.vertex_bevel"
    bl_label = "Vertex Bevel"
    bl_description = """Adds a vertex group bevel and weld modifier
SHIFT — Place modifiers at the bottom of the stack
ALT — Create a vertex group edge bevel
CTRL — Remove existing modifiers"""


    def do_modal(self, context, event):
        profile_factor = 0.01 if self.key_shift else 0.1
        segment_factor = 1 if self.key_shift else 2

        if self.key_numeric_input:
            if self.key_no_modifiers:
                self.width_input_stream = update_stream(self.width_input_stream, event.type)
                self.width = get_stream_value(self.width_input_stream, self.unit_scaled_factor)
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = update_stream(self.segments_input_stream, event.type)
                self.segments = int(get_stream_value(self.segments_input_stream, min_value=1))
                self.dirty = True
            elif self.key_ctrl:
                self.profile_input_stream = update_stream(self.profile_input_stream, event.type)
                self.profile = get_stream_value(self.profile_input_stream)
                self.dirty = True

        if self.key_reset:
            if self.key_no_modifiers:
                self.width_input_stream = new_stream()
                self.width = 0
                self.dirty = True
            elif self.key_alt:
                self.segments_input_stream = new_stream()
                self.segments = 1
                self.dirty = True
            elif self.key_ctrl:
                self.profile_input_stream = new_stream()
                self.profile = 0.5
                self.dirty = True

        if pressed(event, {'W'}):
            self.target_object.show_wire = not self.target_object.show_wire
            self.target_object.show_in_front = not self.target_object.show_in_front

        if self.key_step_up:
            if no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = min(1, self.profile + profile_factor)
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width += self.step_size
                self.dirty = True
        
        if self.key_step_down:
            if no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(1, self.segments - segment_factor)
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = max(0, self.profile - profile_factor)
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(0, self.width - self.step_size)
                self.dirty = True

        if self.key_confirm:
            self.finish(context)

            return {'FINISHED'}
        
        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if no_stream(self.segments_input_stream) and self.key_alt:
                self.segments = max(1, self.segments + self.mouse_step)
                self.dirty = True
            elif no_stream(self.width_input_stream) and self.key_no_modifiers:
                self.width = max(0, self.width + self.mouse_value)
                self.dirty = True
            elif no_stream(self.profile_input_stream) and self.key_ctrl:
                self.profile = max(0, min(1, self.profile + self.mouse_value))
                self.dirty = True


    def do_invoke(self, context, event):
        if event.ctrl:
            old_vgroup_names = []
            for object in context.selected_objects:
                active_vgroup_names = [vgroup.name for vgroup in object.vertex_groups]

                for mod in object.modifiers:
                    if mod.type == 'BEVEL' and ' — ND VB' in mod.name and mod.vertex_group and mod.vertex_group in active_vgroup_names:
                        old_vgroup_names.append(mod.vertex_group)

                for vgroup_name in old_vgroup_names:
                    object.vertex_groups.remove(object.vertex_groups[vgroup_name])

            remove_modifiers_ending_with(context.selected_objects, ' — ND VB')
            remove_modifiers_ending_with(context.selected_objects, ' — ND VB LA')

            return {'FINISHED'}

        self.late_apply = event.shift
        self.edge_mode = event.alt

        self.dirty = False

        self.segments = 1
        self.width = 0
        self.profile = 0.5

        self.segments_input_stream = new_stream()
        self.width_input_stream = new_stream()
        self.profile_input_stream = new_stream()

        self.target_object = context.active_object

        previous_op = False

        bm = bmesh.from_edit_mesh(context.active_object.data)
        selected_vert_indices = [vert.index for vert in bm.verts if vert.select]

        self.vgroup_match = None
        for group in context.active_object.vertex_groups:
            vgroup_vert_indices = [vert.index for vert in context.active_object.data.vertices if group.index in [i.group for i in vert.groups]]
            if len(set(vgroup_vert_indices) & set(selected_vert_indices)) > 0:
                if self.vgroup_match:
                    self.report({'ERROR_INVALID_INPUT'}, "Multiple vertex groups selected, unable to continue operation.")
                    return {'CANCELLED'}
                self.vgroup_match = (group, vgroup_vert_indices)
        
        if self.vgroup_match:
            group, vgroup_vert_indices = self.vgroup_match

            self.group = group
            self.vgroup_difference = [i for i in selected_vert_indices if i not in vgroup_vert_indices]

            bpy.ops.object.mode_set(mode='OBJECT')
            self.group.add(self.vgroup_difference, 1.0, 'ADD')
            bpy.ops.object.mode_set(mode='EDIT')

            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.vertex_group_set_active(group=self.group.name)
            bpy.ops.object.vertex_group_select()

            for mod in context.active_object.modifiers:
                if mod.type == "BEVEL" and mod.vertex_group == self.group.name:
                    previous_op = True
                    self.bevel = mod
                    break

        if previous_op:
            self.summon_old_operator(context)
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
            return len([vert for vert in mesh.verts if vert.select]) >= 1


    def summon_old_operator(self, context):
        self.summoned = True

        self.width_prev = self.width = self.bevel.width
        self.segments_prev = self.segments = self.bevel.segments
        self.profile_prev = self.profile = self.bevel.profile


    def prepare_new_operator(self, context):
        self.summoned = False

        self.add_smooth_shading(context)
        self.add_vertex_group(context)
        self.add_bevel_modifier(context)


    def add_smooth_shading(self, context):
        if bpy.app.version >= (4, 1, 0):
            return
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()
        context.active_object.data.use_auto_smooth = True
        context.active_object.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))
        bpy.ops.object.mode_set(mode='EDIT')


    def add_vertex_group(self, context):
        vgroup = context.active_object.vertex_groups.new(name="ND — Bevel")
        bpy.ops.object.vertex_group_assign()

        self.vgroup = vgroup


    def add_bevel_modifier(self, context):
        bevel = new_modifier(context.active_object, mod_bevel, 'BEVEL', rectify=False)
        bevel.affect = 'EDGES' if self.edge_mode else 'VERTICES'
        bevel.limit_method = 'VGROUP'
        bevel.offset_type = 'WIDTH'
        bevel.vertex_group = self.vgroup.name

        self.bevel = bevel

        if not self.late_apply:
            while context.active_object.modifiers[0].name != self.bevel.name:
                bpy.ops.object.modifier_move_up(modifier=self.bevel.name)
    

    def add_weld_modifier(self, context):
        mods = context.active_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if self.late_apply or not previous_op:
            weld = new_modifier(context.active_object, mod_weld_la if self.late_apply else mod_weld, 'WELD', rectify=False)
            weld.merge_threshold = 0.00001
            weld.mode = 'CONNECTED'

            self.weld = weld

            if not self.late_apply:
                while context.active_object.modifiers[1].name != self.weld.name:
                    bpy.ops.object.modifier_move_up(modifier=self.weld.name)


    def operate(self, context):
        self.bevel.width = self.width
        self.bevel.segments = self.segments
        self.bevel.profile = self.profile

        self.dirty = False


    def finish(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False
        self.add_weld_modifier(context)

        # TODO: Find a better solution. This is a workaround for the fact that
        # the vertex group <> modifier combo's are not being detected by the recall 
        # algorithm directly after they've been created while in edit mode.
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        unregister_draw_handler()
    

    def revert(self, context):
        self.target_object.show_wire = False
        self.target_object.show_in_front = False

        if self.summoned:
            self.bevel.width = self.width_prev
            self.bevel.segments = self.segments_prev
            self.bevel.profile = self.profile_prev

            if self.vgroup_match:
                bpy.ops.object.mode_set(mode='OBJECT')
                self.group.remove(self.vgroup_difference)
                bpy.ops.object.mode_set(mode='EDIT')

        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.bevel.name)
            context.active_object.vertex_groups.remove(self.vgroup)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self,
        f"Width: {(self.width * self.display_unit_scale):.2f}{self.unit_suffix}", 
        self.unit_step_hint,
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers,
        mouse_value=True,
        input_stream=self.width_input_stream)

    draw_property(
        self,
        "Segments: {}".format(self.segments),
        self.generate_key_hint("Alt", self.generate_step_hint(2, 1)),
        active=self.key_alt,
        alt_mode=self.key_shift_alt,
        mouse_value=True,
        input_stream=self.segments_input_stream)

    draw_property(
        self, 
        "Profile: {0:.2f}".format(self.profile),
        self.generate_key_hint("Ctrl", self.generate_step_hint(0.1, 0.01)),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl,
        mouse_value=True,
        input_stream=self.profile_input_stream)

    draw_hint(
        self,
        "Enhanced Wireframe [W]: {0}".format("Yes" if self.target_object.show_wire else "No"),
        "Display the objects's wireframe over solid shading")


def register():
    bpy.utils.register_class(ND_OT_vertex_bevel)


def unregister():
    bpy.utils.unregister_class(ND_OT_vertex_bevel)
    unregister_draw_handler()
