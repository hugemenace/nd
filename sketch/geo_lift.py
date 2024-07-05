# ███╗   ██╗██████╗
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝
#
# ND (Non-Destructive) Blender Add-on
# Copyright (C) 2024 Tristan S. & Ian J. (HugeMenace)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ---
# Contributors: Tristo (HM)
# ---

import bpy
import bmesh
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_hint, draw_property, draw_hint
from .. lib.viewport import set_3d_cursor
from .. lib.events import capture_modifier_keys, pressed
from .. lib.preferences import get_preferences
from .. lib.objects import create_duplicate_liftable_geometry


class ND_OT_geo_lift(BaseOperator):
    bl_idname = "nd.geo_lift"
    bl_label = "Geo Lift"
    bl_description = """Lift geometry out of a non-destructive object
SHIFT — Do not clean duplicate mesh before extraction"""
    bl_options = {'UNDO'}


    def do_modal(self, context, event):
        if self.key_select:
            return {'PASS_THROUGH'}

        elif self.key_confirm_alternative:
            return self.finish(context)

        elif self.key_cancel:
            self.clean_up(context)

            return {'CANCELLED'}

        elif pressed(event, {'S'}):
            self.selection_type = (self.selection_type + 1) % 3
            self.set_selection_mode(context)

        elif pressed(event, {'E'}):
            self.xray_mode = not self.xray_mode
            self.dirty = True

        elif self.key_one:
            self.selection_type = 0
            self.set_selection_mode(context)

        elif self.key_two:
            self.selection_type = 1
            self.set_selection_mode(context)

        elif self.key_three:
            self.selection_type = 2
            self.set_selection_mode(context)

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        self.dirty = False
        self.selection_type = 2 # ['VERT', 'EDGE', 'FACE']
        self.xray_mode = False
        self.register_mode()

        self.target_obj = context.active_object

        create_duplicate_liftable_geometry(context, {self.mode}, 'ND — Geo Lift', not event.shift)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and context.active_object is not None:
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'


    def register_mode(self):
        self.mode = ['VERT', 'EDGE', 'FACE'][self.selection_type]


    def set_selection_mode(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode = (self.selection_type == 0, self.selection_type == 1, self.selection_type == 2)
        self.register_mode()


    def isolate_geometry(self, context):
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type=self.mode)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.customdata_custom_splitnormals_clear()


    def has_invalid_selection(self, context):
        mesh = bmesh.from_edit_mesh(context.active_object.data)

        selected_vertices = len([v for v in mesh.verts if v.select])
        selected_edges = len([e for e in mesh.edges if e.select])
        selected_faces = len([f for f in mesh.faces if f.select])

        if self.selection_type == 0:
            return selected_vertices < 1
        elif self.selection_type == 1:
            return selected_edges < 1
        elif self.selection_type == 2:
            return selected_faces < 1

        return False


    def operate(self, context):
        context.active_object.show_in_front = self.xray_mode
        self.dirty = False


    def finish(self, context):
        if self.has_invalid_selection(context):
            self.clean_up(context)
            self.report({'ERROR_INVALID_INPUT'}, "Ensure at least a single peice of geometry is selected.")

            return {'CANCELLED'}

        self.isolate_geometry(context)
        self.clean_up(context, remove_lifted_geometry=False)

        return {'FINISHED'}


    def clean_up(self, context, remove_lifted_geometry=True):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        context.active_object.show_in_front = False

        if remove_lifted_geometry:
            bpy.ops.object.delete()
            bpy.ops.object.select_all(action='DESELECT')
            self.target_obj.select_set(True)
            bpy.context.view_layer.objects.active = self.target_obj

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_hint(self, "Confirm Geometry [Space]", "Comfirm the geometry to extract")

    draw_hint(
        self,
        "Selection Type [S,1,2,3]: {0}".format(['Vertex', 'Edge', 'Face'][self.selection_type]),
        "Type of geometry to select (Vertex, Edge, Face)")

    draw_hint(
        self,
        "Exclusive View [E]: {0}".format("On" if self.xray_mode else "Off"),
        "Show the target object in front of all other objects")


def register():
    bpy.utils.register_class(ND_OT_geo_lift)


def unregister():
    bpy.utils.unregister_class(ND_OT_geo_lift)
    unregister_draw_handler()
