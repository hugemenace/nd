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
from numpy.linalg import norm
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.points import init_points, register_points_handler, unregister_points_handler
from .. lib.math import v3_average, v3_distance, create_rotation_matrix_from_vertex, create_rotation_matrix_from_edge, create_rotation_matrix_from_face


class ND_OT_snap_align(bpy.types.Operator):
    bl_idname = "nd.snap_align"
    bl_label = "Snap Align"
    bl_description = "Align and snap one object to another"
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

        elif pressed(event, {'C'}):
            if self.snap_point and len(self.capture_points) < 2:
                self.capture_points.append(self.snap_point)

                if len(self.capture_points) == 1:
                    self.guide_line = (self.capture_points[0][0], self.reference_obj.location)
                else:
                    self.guide_line = (self.capture_points[0][0], self.capture_points[1][0])

                self.dirty = True

        elif pressed(event, {'R'}):
            self.capture_points = []
            self.guide_line = ()
                
            self.dirty = True

        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        elif event.type == 'MOUSEMOVE':
            coords = (event.mouse_region_x, event.mouse_region_y)
            self.recalculate_points(context, coords)

        if self.dirty:
            self.operate(context)
            
        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False
        self.hit_location = None
        self.capture_points = []
        self.primary_points = []
        self.secondary_points = []
        self.tertiary_points = []
        self.snap_point = None

        a, b = context.selected_objects
        self.reference_obj = a if a.name != context.active_object.name else b
        self.reference_obj_original_location = self.reference_obj.location.copy()
        self.reference_obj_original_rotation = self.reference_obj.rotation_euler.copy()

        self.affected_boolean_modifiers = {}
        for mod in context.active_object.modifiers:
            if mod.type == 'BOOLEAN' and mod.object == self.reference_obj:
                self.affected_boolean_modifiers[mod.name] = mod.show_viewport
                mod.show_viewport = False

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.active_object.evaluated_get(depsgraph)

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        
        world_matrix = context.active_object.matrix_world

        vert_points = []
        for vert in bm.verts:
            vert_matrix = create_rotation_matrix_from_vertex(world_matrix, vert)
            vert_points.append((world_matrix @ vert.co, vert_matrix))

        edge_points = []
        edge_lengths = []
        for edge in bm.edges:
            edge_matrix = create_rotation_matrix_from_edge(world_matrix, edge)
            edge_points.append((world_matrix @ v3_average([v.co for v in edge.verts]), edge_matrix))
            edge_lengths.append(v3_distance(world_matrix @ edge.verts[0].co, world_matrix @ edge.verts[1].co))

        face_points = []
        for face in bm.faces:
            face_matrix = create_rotation_matrix_from_face(world_matrix, face)
            face_points.append((world_matrix @ face.calc_center_median(), face_matrix))

        average_edge_length = sum(edge_lengths) / len(edge_lengths)
        self.snap_distance_factor = average_edge_length / 2.0

        self.points_cache = vert_points + edge_points + face_points

        bm.free()

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        init_points(self)
        register_points_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 2 and context.active_object.type == 'MESH'

    
    def operate(self, context):
        self.tertiary_points = [cap[0] for cap in self.capture_points]

        if len(self.capture_points) == 2:
            self.primary_points = []
            self.secondary_points = []

            self.reference_obj.rotation_euler = self.capture_points[0][1].to_euler()
            mid_point = v3_average([self.capture_points[0][0], self.capture_points[1][0]])
            self.reference_obj.location = mid_point
            self.tertiary_points.append(mid_point)

        elif self.snap_point:
            vect, rotation_matrix = self.snap_point
            self.reference_obj.location = vect
            if len(self.capture_points) == 0:
                self.reference_obj.rotation_euler = rotation_matrix.to_euler()
            else:
                self.reference_obj.rotation_euler = self.capture_points[0][1].to_euler()
                
        elif self.hit_location:
            self.reference_obj.location = self.hit_location

        self.dirty = False


    def recalculate_points(self, context, mouse_coords):
        if len(self.capture_points) == 2:
            return

        self.reference_obj.hide_set(True)

        region = context.region
        region_data = context.space_data.region_3d

        view_vector = region_2d_to_vector_3d(region, region_data, mouse_coords)
        ray_origin = region_2d_to_origin_3d(region, region_data, mouse_coords)

        ray_target = ray_origin + view_vector
        ray_direction = ray_target - ray_origin

        depsgraph = context.evaluated_depsgraph_get()

        hit, location, normal, face_index, object, matrix = context.scene.ray_cast(depsgraph, ray_origin, ray_direction)
        hidden_objects = []
        while hit and object.name != context.active_object.name:
            hidden_objects.append(object)
            object.hide_set(True)
            hit, location, normal, face_index, object, matrix = context.scene.ray_cast(depsgraph, location + 0.001 * ray_direction, ray_direction)

        for obj in hidden_objects:
            obj.hide_set(False)

        if hit:
            self.hit_location = location

            self.primary_points = []
            self.secondary_points = []
            snap_points = []
            for (vect, rotation_matrix) in self.points_cache:
                if v3_distance(vect, location) <= (0.2 * self.snap_distance_factor):
                    snap_points.append((vect, rotation_matrix))
                elif v3_distance(vect, location) <= (0.8 * self.snap_distance_factor):
                    self.secondary_points.append(vect)
            
            snap_points.sort(key=lambda p: v3_distance(p[0], location))
            self.snap_point = snap_points[0] if snap_points else None
            self.primary_points = [self.snap_point[0]] if self.snap_point else []
        else:
            self.hit_location = None
            self.primary_points = []
            self.secondary_points = []
        
        self.reference_obj.hide_set(False)

        self.dirty = True
        self.operate(context)


    def clean_up(self, context):
        for mod in context.active_object.modifiers:
            if mod.type == 'BOOLEAN' and mod.object == self.reference_obj:
                mod.show_viewport = self.affected_boolean_modifiers[mod.name]

        bpy.ops.object.select_all(action='DESELECT')
        self.reference_obj.select_set(True)
        context.view_layer.objects.active = self.reference_obj


    def finish(self, context):
        self.clean_up(context)

        unregister_draw_handler()
        unregister_points_handler()


    def revert(self, context):
        self.clean_up(context)

        self.reference_obj.location = self.reference_obj_original_location
        self.reference_obj.rotation_euler = self.reference_obj_original_rotation

        unregister_draw_handler()
        unregister_points_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_hint(self, "Select Snap Point", "Hover over the selected object to view snap points")

    draw_property(
        self,
        "Capture Point [C]  /  Reset [R]",
        "{}".format("{}/2 Snap points captured!".format(len(self.capture_points)) if len(self.capture_points) > 0 else "No points captured..."),
        active=len(self.capture_points) > 0,
        alt_mode=len(self.capture_points) == 1)


def register():
    bpy.utils.register_class(ND_OT_snap_align)


def unregister():
    bpy.utils.unregister_class(ND_OT_snap_align)
    unregister_draw_handler()
