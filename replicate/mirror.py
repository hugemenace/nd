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
from .. lib.axis import init_axis, register_axis_handler, unregister_axis_handler
from .. lib.viewport import set_3d_cursor
from .. lib.math import v3_average, create_rotation_matrix_from_vertex, create_rotation_matrix_from_edge, create_rotation_matrix_from_face, v3_center
from .. lib.collections import move_to_utils_collection, isolate_in_utils_collection

class ND_OT_mirror(bpy.types.Operator):
    bl_idname = "nd.mirror"
    bl_label = "Mirror"
    bl_description = """Mirror an object in isolation, or across another object
ALT — Mirror across selected object's geometry
SHIFT — Place modifiers at the top of the stack"""
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

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

        elif pressed(event, {'A'}):
            self.axis = (self.axis + 1) % 3
            self.dirty = True

        elif pressed(event, {'F'}):
            self.flip = not self.flip
            self.dirty = True

        elif self.key_one:
            if self.geometry_mode and not self.geometry_ready:
                self.geometry_selection_type = 0
                self.set_selection_mode(context)

        elif self.key_two:
            if self.geometry_mode and not self.geometry_ready:
                self.geometry_selection_type = 1
                self.set_selection_mode(context)

        elif self.key_three:
            if self.geometry_mode and not self.geometry_ready:
                self.geometry_selection_type = 2
                self.set_selection_mode(context)

        elif pressed(event, {'S'}):
            self.geometry_selection_type = (self.geometry_selection_type + 1) % 3
            self.set_selection_mode(context)

        elif self.key_confirm_alternative:
            if self.geometry_mode and not self.geometry_ready:
                return self.complete_geometry_mode(context)

        elif self.key_left_click and self.geometry_mode and not self.geometry_ready:
            return {'PASS_THROUGH'}

        elif self.key_confirm:
            if self.geometry_mode and not self.geometry_ready:
                return {'PASS_THROUGH'}
            elif not self.geometry_mode or (self.geometry_mode and self.geometry_ready):
                self.finish(context)

                return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.geometry_mode = event.alt
        self.early_apply = event.shift
        self.geometry_ready = False
        self.geometry_selection_type = 2 # ['VERT', 'EDGE', 'FACE']

        if self.geometry_mode and len(context.selected_objects) > 1:
            self.report({'ERROR'}, "Please select only one object")

        self.dirty = False
        self.axis = 2 if self.geometry_mode else 0
        self.flip = self.geometry_mode
        self.reference_objs = [context.active_object]
        self.mirror_obj = None

        if len(context.selected_objects) >= 2:
            self.reference_objs = [obj for obj in context.selected_objects if obj != context.active_object]
            self.mirror_obj = context.active_object

        if self.geometry_mode:
            self.prepare_evaluated_geometry(context)
        else:
            self.add_mirror_modifiers()

        self.operate(context)

        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        if not self.geometry_mode:
            init_axis(self, self.reference_objs[0] if self.mirror_obj is None else self.mirror_obj, self.axis)
            register_axis_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            if len(context.selected_objects) == 1 and context.object.type == 'MESH':
                return True

            if len(context.selected_objects) >= 2:
                return all(obj.type == 'MESH' for obj in context.selected_objects if obj.name != context.object.name)


    def set_selection_mode(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode = (self.geometry_selection_type == 0, self.geometry_selection_type == 1, self.geometry_selection_type == 2)


    def prepare_evaluated_geometry(self, context):
        bpy.ops.object.duplicate()

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.object.evaluated_get(depsgraph)

        context.object.modifiers.clear()
        context.object.show_in_front = True

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        bm.to_mesh(context.object.data)
        bm.free()

        mode = ['VERT', 'EDGE', 'FACE'][self.geometry_selection_type]
        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={mode})
        bpy.ops.mesh.select_all(action='DESELECT')

        context.object.name = 'ND — Mirror Geometry'
        context.object.data.name = 'ND — Mirror Geometry'

    
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
        mesh = bmesh.from_edit_mesh(context.object.data)
        world_matrix = context.object.matrix_world

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
        mesh = bmesh.from_edit_mesh(context.object.data)

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
            context.object.show_in_front = False
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
        context.object.show_in_front = False
        bpy.ops.object.delete()

        empty = bpy.data.objects.new("empty", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.empty_display_size = 1
        empty.empty_display_type = 'PLAIN_AXES'
        empty.location = location
        empty.rotation_euler = rotation.to_euler()
        empty.parent = self.reference_objs[0]
        empty.matrix_parent_inverse = self.reference_objs[0].matrix_world.inverted()

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
            mirror = obj.modifiers.new('Mirror — ND', 'MIRROR')
            mirror.use_clip = True
            mirror.merge_threshold = 0.0001

            if self.mirror_obj != None:
                mirror.mirror_object = self.mirror_obj

            self.mirrors.append(mirror)

            if self.early_apply:
                while obj.modifiers[0].name != mirror.name:
                    bpy.ops.object.modifier_move_up({'object': obj}, modifier=mirror.name)
    

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
        bpy.ops.object.select_all(action='DESELECT')
        for obj in self.reference_objs:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_objs[0]


    def finish(self, context):
        self.select_reference_objs(context)

        context.object.show_in_front = False

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

        context.object.show_in_front = False

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


def register():
    bpy.utils.register_class(ND_OT_mirror)


def unregister():
    bpy.utils.unregister_class(ND_OT_mirror)
    unregister_draw_handler()
