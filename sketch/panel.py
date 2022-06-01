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
from mathutils import Matrix
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_hint, draw_property, draw_hint
from .. lib.viewport import set_3d_cursor
from .. lib.preferences import get_preferences
from .. lib.events import capture_modifier_keys, pressed
from .. lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream
from .. lib.objects import create_duplicate_liftable_geometry


class ND_OT_panel(bpy.types.Operator):
    bl_idname = "nd.panel"
    bl_label = "Panel"
    bl_description = """Combination operator which allows you to select faces, inset, and then solidify them
SHIFT — Do not clean duplicate mesh before extraction"""
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        inset_factor = (self.base_inset_factor / 10.0) if self.key_shift else self.base_inset_factor

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        elif self.key_toggle_pin_overlay:
            toggle_pin_overlay(self, event)

        elif self.operator_passthrough:
            update_overlay(self, context, event)
            
            return {'PASS_THROUGH'}

        elif self.key_increase_factor:
            if self.stage == 1:
                if no_stream(self.inset_input_stream) and self.key_no_modifiers:
                    self.base_inset_factor = min(1, self.base_inset_factor * 10.0)

        elif self.key_decrease_factor:
            if self.stage == 1:
                if no_stream(self.inset_input_stream) and self.key_no_modifiers:
                    self.base_inset_factor = max(0.001, self.base_inset_factor / 10.0)

        elif self.key_numeric_input:
            if self.stage == 1:
                if self.key_no_modifiers:
                    self.inset_input_stream = update_stream(self.inset_input_stream, event.type)
                    self.inset = get_stream_value(self.inset_input_stream, 0.001)
                    self.dirty = True

        elif self.key_reset:
            if self.stage == 1:
                if self.key_no_modifiers:
                    self.inset_input_stream = new_stream()
                    self.inset = 0
                    self.dirty = True

        elif pressed(event, {'F'}):
            self.individual = not self.individual
            self.dirty = True

        elif self.key_step_up:
            if self.stage == 1:
                if no_stream(self.inset_input_stream) and self.key_no_modifiers:
                    self.inset += inset_factor
                    self.dirty = True
        
        elif self.key_step_down:
            if self.stage == 1:
                if no_stream(self.inset_input_stream) and self.key_no_modifiers:
                    self.inset = max(0, self.inset - inset_factor)
                    self.dirty = True

        elif self.stage == 0 and self.key_confirm_alternative:
            if self.has_valid_selection(context):
                self.isolate_geometry(context)
                self.stage = 1
                self.dirty = True
            
        elif self.stage == 1 and self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.stage == 0 and self.key_left_click:
            return {'PASS_THROUGH'}

        elif self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if get_preferences().enable_mouse_values:
            if self.stage == 1:
                if no_stream(self.inset_input_stream) and self.key_no_modifiers:
                    self.inset = max(0, self.inset + self.mouse_value)
                    self.dirty = True

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.base_inset_factor = 0.01

        self.dirty = False

        self.individual = False
        self.inset = 0
        self.stage = 0
        self.target_obj = context.active_object

        create_duplicate_liftable_geometry(context, {'FACE'}, 'ND — Panel', not event.shift)
        self.panel_obj = context.active_object

        self.inset_input_stream = new_stream()

        capture_modifier_keys(self)
        
        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'


    def isolate_geometry(self, context):
        self.panel_bm = bmesh.from_edit_mesh(self.panel_obj.data)

        self.delete_unselected_panel_geometry()
        self.update_panel_edit_mesh(True)

        self.panel_mesh_snapshot = self.panel_obj.data.copy()

    
    def delete_unselected_panel_geometry(self):
        verts = [v for v in self.panel_bm.verts if not v.select]
        bmesh.ops.delete(self.panel_bm, geom=verts, context='VERTS')

        faces = [f for f in self.panel_bm.faces if not f.select]
        bmesh.ops.delete(self.panel_bm, geom=faces, context='FACES')

    
    def update_panel_edit_mesh(self, update_data=False):
        bmesh.update_edit_mesh(self.panel_obj.data)
        if update_data:
            self.panel_obj.update_from_editmode()


    def delete_panel_faces(self, faces):
        bmesh.ops.delete(self.panel_bm, geom=faces, context='FACES')


    def operate(self, context):
        if self.stage == 1:
            bmesh.ops.delete(self.panel_bm, geom=self.panel_bm.verts, context='VERTS')
            self.panel_bm.from_mesh(self.panel_mesh_snapshot)

            if self.individual:
                faces = list(self.panel_bm.faces)
                for face in faces:
                    result = self.inset_faces([face])
                    self.delete_panel_faces(result['faces'])
            else:
                result = self.inset_faces(self.panel_bm.faces)
                self.delete_panel_faces(result['faces'])
            
            self.update_panel_edit_mesh()
        
        self.dirty = False


    def inset_faces(self, faces):
        return bmesh.ops.inset_region(
            self.panel_bm,
            faces=faces,
            use_boundary=True,
            use_even_offset=True,
            use_interpolate=True,
            use_relative_offset=False,
            use_edge_rail=True,
            thickness=self.inset,
            depth=0,
            use_outset=False)


    def has_valid_selection(self, context):
        mesh = bmesh.from_edit_mesh(context.active_object.data)
        selected_faces = len([f for f in mesh.faces if f.select])
        
        return selected_faces > 0


    def finish(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        self.panel_obj.show_in_front = False

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        
        unregister_draw_handler()

        bpy.ops.nd.solidify('INVOKE_DEFAULT')

    
    def revert(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.data.objects.remove(self.panel_obj, do_unlink=True)

        bpy.ops.object.select_all(action='DESELECT')
        self.target_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.target_obj

        unregister_draw_handler()
    

def draw_text_callback(self):
    draw_header(self)

    if self.stage == 0:
        draw_hint(self, "Confirm Geometry [Space]", "Comfirm the geometry to extract")

    if self.stage == 1:
        draw_property(
            self,
            "Inset Amount: {0:.1f}".format(self.inset * 1000),
            "(±{0:.1f})  |  Shift (±{1:.1f})".format(self.base_inset_factor * 1000, (self.base_inset_factor / 10) * 1000),
            active=self.key_no_modifiers,
            alt_mode=self.key_shift_no_modifiers,
            mouse_value=True,
            input_stream=self.inset_input_stream)

        draw_hint(
            self,
            "Individual Faces [F]: {}".format("Yes" if self.individual else "No"),
            "Inset individual faces (Yes, No)")


def register():
    bpy.utils.register_class(ND_OT_panel)


def unregister():
    bpy.utils.unregister_class(ND_OT_panel)
    unregister_draw_handler()
