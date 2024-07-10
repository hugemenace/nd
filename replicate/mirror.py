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
from math import radians
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.viewport import set_3d_cursor
from .. lib.math import v3_average, create_rotation_matrix_from_vertex, create_rotation_matrix_from_edge, create_rotation_matrix_from_face, v3_center
from .. lib.collections import move_to_utils_collection, isolate_in_utils_collection
from .. lib.modifiers import new_modifier, remove_modifiers_starting_with
from .. lib.objects import get_real_active_object
from .. lib.polling import object_supports_mods, object_is_curve, object_exists, is_edit_mode, is_object_mode, has_objects_selected, has_min_objects_selected


class ND_OT_mirror(BaseOperator):
    bl_idname = "nd.mirror"
    bl_label = "Mirror"
    bl_description = """Mirror an object in isolation, or across another object
ALT — Mirror across selected object's geometry
SHIFT — Place modifiers at the top of the stack
CTRL — Remove existing modifiers"""
    bl_options = {'UNDO'}


    def do_modal(self, context, event):
        if pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        if pressed(event, {'F'}):
            self.flip = not self.flip
            self.dirty = True

        if not self.geometry_mode and pressed(event, {'S'}):
            self.symmetrize = not self.symmetrize
            self.dirty = True

        if self.key_one:
            if self.geometry_mode and not self.geometry_ready:
                self.geometry_selection_type = 0
                self.set_selection_mode(context)

        if self.key_two:
            if self.geometry_mode and not self.geometry_ready:
                self.geometry_selection_type = 1
                self.set_selection_mode(context)

        if self.key_three:
            if self.geometry_mode and not self.geometry_ready:
                self.geometry_selection_type = 2
                self.set_selection_mode(context)

        if self.geometry_mode and pressed(event, {'S'}):
            self.geometry_selection_type = (self.geometry_selection_type + 1) % 3
            self.set_selection_mode(context)

        if self.key_confirm_alternative:
            if self.geometry_mode and not self.geometry_ready:
                return self.complete_geometry_mode(context)

        if self.key_select and self.geometry_mode and not self.geometry_ready:
            return {'PASS_THROUGH'}

        if self.key_confirm:
            if self.geometry_mode and not self.geometry_ready:
                return {'PASS_THROUGH'}
            elif not self.geometry_mode or (self.geometry_mode and self.geometry_ready):
                self.finish(context)

                return {'FINISHED'}

        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}


    def do_invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        if event.ctrl:
            remove_modifiers_starting_with(context.selected_objects, 'Mirror —')
            return {'FINISHED'}

        self.edit_mode = is_edit_mode(context)
        self.geometry_mode = event.alt
        self.early_apply = event.shift
        self.geometry_ready = False
        self.geometry_selection_type = 2 # ['VERT', 'EDGE', 'FACE']

        self.dirty = False
        self.axis = 2 if self.geometry_mode else 0
        self.flip = self.geometry_mode
        self.symmetrize = False
        self.reference_objs = [context.active_object]
        self.mirror_obj = None

        if object_is_curve(context.active_object) and self.geometry_mode:
            self.report({'ERROR_INVALID_INPUT'}, "The mirror across selected geometry feature cannot be used on curves")
            return {'CANCELLED'}

        if self.edit_mode and self.geometry_mode:
            self.report({'ERROR_INVALID_INPUT'}, "The mirror across selected geometry feature cannot be used in edit mode")
            return {'CANCELLED'}

        if has_min_objects_selected(context, 2):
            self.reference_objs = [obj for obj in context.selected_objects if obj != context.active_object]
            self.mirror_obj = context.active_object

        if self.geometry_mode:
            self.prepare_evaluated_geometry(context)
        else:
            self.add_mirror_modifiers()

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        if not self.geometry_mode:
            init_axis(self, self.reference_objs[0] if self.mirror_obj is None else self.mirror_obj, self.axis)
            register_axis_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        if is_object_mode(context):
            if has_objects_selected(context, 1) and object_supports_mods(target_object):
                return True

            if has_min_objects_selected(context, 2) and object_exists(target_object):
                return all(obj.type in ['MESH', 'CURVE'] for obj in context.selected_objects if obj.name != target_object.name)

        if is_edit_mode(context):
            return has_objects_selected(context, 1) and object_supports_mods(target_object)


    def set_selection_mode(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode = (self.geometry_selection_type == 0, self.geometry_selection_type == 1, self.geometry_selection_type == 2)


    def prepare_evaluated_geometry(self, context):
        active_object = context.active_object

        bpy.ops.object.select_all(action='DESELECT')
        active_object.select_set(True)
        bpy.context.view_layer.objects.active = active_object

        bpy.ops.object.duplicate()

        self.evaluated_geometry = context.active_object

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.active_object.evaluated_get(depsgraph)

        self.evaluated_geometry.modifiers.clear()
        self.evaluated_geometry.show_in_front = True

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        bm.to_mesh(self.evaluated_geometry.data)
        bm.free()

        mode = ['VERT', 'EDGE', 'FACE'][self.geometry_selection_type]
        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={mode})
        bpy.ops.mesh.select_all(action='DESELECT')

        self.evaluated_geometry.name = 'ND — Mirror Geometry'
        self.evaluated_geometry.data.name = 'ND — Mirror Geometry'


    def get_face_transform(self, mesh, world_matrix):
        selected_faces = [f for f in mesh.faces if f.select]
        center = v3_average([f.calc_center_median_weighted() for f in selected_faces])
        location = world_matrix @ center
        rotation = create_rotation_matrix_from_face(world_matrix, selected_faces[0])

        return (location, rotation)


    def get_edge_transform(self, mesh, world_matrix):
        selected_edges = [e for e in mesh.edges if e.select]
        center = v3_average([v3_center(*e.verts) for e in selected_edges])
        location = world_matrix @ center
        rotation = create_rotation_matrix_from_edge(world_matrix, selected_edges[0])

        return (location, rotation)


    def get_vertex_transform(self, mesh, world_matrix):
        selected_vertices = [v for v in mesh.verts if v.select]
        center = v3_average([v.co for v in selected_vertices])
        location = world_matrix @ center
        rotation = create_rotation_matrix_from_vertex(world_matrix, selected_vertices[0])

        return (location, rotation)


    def get_geometry_transform(self, context):
        mesh = bmesh.from_edit_mesh(context.active_object.data)
        world_matrix = context.active_object.matrix_world

        if self.geometry_selection_type == 0:
            selected_vertices = len([v for v in mesh.verts if v.select])
            if selected_vertices == 3:
                bpy.ops.mesh.edge_face_add()
                context.tool_settings.mesh_select_mode = (False, False, True)
                self.geometry_selection_type = 2

        if self.geometry_selection_type == 0:
            return self.get_vertex_transform(mesh, world_matrix)
        elif self.geometry_selection_type == 1:
            return self.get_edge_transform(mesh, world_matrix)
        elif self.geometry_selection_type == 2:
            return self.get_face_transform(mesh, world_matrix)


    def has_invalid_selection(self, context):
        mesh = bmesh.from_edit_mesh(context.active_object.data)

        selected_vertices = len([v for v in mesh.verts if v.select])
        selected_edges = len([e for e in mesh.edges if e.select])
        selected_faces = len([f for f in mesh.faces if f.select])

        if self.geometry_selection_type == 0:
            return selected_vertices != 1 and selected_vertices != 3
        elif self.geometry_selection_type == 1:
            return selected_edges != 1
        elif self.geometry_selection_type == 2:
            return selected_faces != 1

        return False


    def complete_geometry_mode(self, context):
        if self.has_invalid_selection(context):
            bpy.ops.object.mode_set(mode='OBJECT')
            self.evaluated_geometry.show_in_front = False
            bpy.ops.object.delete()

            self.select_reference_objs(context)

            unregister_draw_handler()
            unregister_axis_handler()

            if self.geometry_selection_type == 0:
                self.report({'ERROR_INVALID_INPUT'}, "Ensure only a single vertex, or exactly 3 vertices are selected.")
            else:
                self.report({'ERROR_INVALID_INPUT'}, "Ensure only a single edge or face is selected.")

            return {'CANCELLED'}

        (location, rotation) = self.get_geometry_transform(context)

        bpy.ops.object.mode_set(mode='OBJECT')
        self.evaluated_geometry.show_in_front = False
        bpy.ops.object.delete()

        empty = bpy.data.objects.new("empty", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.empty_display_size = 1
        empty.empty_display_type = 'PLAIN_AXES'
        empty.location = location
        empty.rotation_euler = rotation.to_euler()

        if len(self.reference_objs) == 1:
            empty.parent = self.reference_objs[0]
            empty.matrix_parent_inverse = self.reference_objs[0].matrix_world.inverted()

        empty.name = "ND — Mirror Geometry"

        move_to_utils_collection(empty)
        isolate_in_utils_collection([empty])

        self.mirror_obj = empty

        self.add_mirror_modifiers()

        init_axis(self, self.mirror_obj, self.axis)
        register_axis_handler(self)

        self.geometry_ready = True
        self.operate(context)

        return {'RUNNING_MODAL'}


    def add_mirror_modifiers(self):
        self.mirrors = []

        for obj in self.reference_objs:
            mirror = new_modifier(obj, 'Mirror — ND', 'MIRROR', rectify=True)
            mirror.use_clip = True
            mirror.merge_threshold = 1e-05
            mirror.bisect_threshold = 1e-05

            if self.mirror_obj != None:
                mirror.mirror_object = self.mirror_obj

            self.mirrors.append(mirror)

            if self.early_apply:
                while obj.modifiers[0].name != mirror.name:
                    if bpy.app.version < (4, 0, 0):
                        bpy.ops.object.modifier_move_up({'object': obj}, modifier=mirror.name)
                    else:
                        with bpy.context.temp_override(object=obj):
                            bpy.ops.object.modifier_move_up(modifier=mirror.name)


    def operate(self, context):
        if self.geometry_mode and not self.geometry_ready:
            pass

        elif not self.geometry_mode or (self.geometry_mode and self.geometry_ready):
            for mirror in self.mirrors:
                for i in range(3):
                    active = self.axis == i
                    mirror.use_axis[i] = active
                    mirror.use_bisect_axis[i] = active
                    mirror.use_bisect_flip_axis[i] = self.flip and active

        self.dirty = False


    def select_reference_objs(self, context):
        if self.edit_mode:
            return

        bpy.ops.object.select_all(action='DESELECT')
        for obj in self.reference_objs:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_objs[0]


    def finish(self, context):
        self.select_reference_objs(context)

        if self.edit_mode and self.symmetrize:
            bpy.ops.object.mode_set(mode='OBJECT')
            for mirror in self.mirrors:
                bpy.ops.object.modifier_apply(modifier=mirror.name)
            bpy.ops.object.mode_set(mode='EDIT')

        if not self.edit_mode and self.symmetrize:
            for mirror in self.mirrors:
                bpy.ops.object.modifier_apply(modifier=mirror.name)

        unregister_draw_handler()
        unregister_axis_handler()


    def revert(self, context):
        if self.geometry_mode and not self.geometry_ready:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.delete()

        self.select_reference_objs(context)

        if not self.geometry_mode or (self.geometry_mode and self.geometry_ready):
            for obj in self.reference_objs:
                obj.modifiers.remove(self.mirrors[self.reference_objs.index(obj)])

        if self.geometry_mode and self.geometry_ready:
            bpy.data.objects.remove(self.mirror_obj, do_unlink=True)

        unregister_draw_handler()
        unregister_axis_handler()


def draw_text_callback(self):
    draw_header(self)

    if self.geometry_mode and not self.geometry_ready:
        draw_hint(self, "Confirm Geometry [Space]", "Comfirm the geometry to mirrored across")

        draw_hint(
            self,
            "Selection Type [S,1,2,3]: {0}".format(['Vertex', 'Edge', 'Face'][self.geometry_selection_type]),
            "Type of geometry to select (Vertex, Edge, Face)")
    elif not self.geometry_mode or (self.geometry_mode and self.geometry_ready):
        draw_hint(
            self,
            "Axis [A]: {}".format(['X', 'Y', 'Z'][self.axis]),
            "Axis to mirror across (X, Y, Z)")

        draw_hint(
            self,
            "Flipped [F]: {}".format('Yes' if self.flip else 'No'),
            "Flip the mirror direction")

        draw_hint(
            self,
            "Symmetrize [S]: {}".format('Yes' if self.symmetrize else 'No'),
            "Immediately apply the mirror modifier")


def register():
    bpy.utils.register_class(ND_OT_mirror)


def unregister():
    bpy.utils.unregister_class(ND_OT_mirror)
    unregister_draw_handler()
