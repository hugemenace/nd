# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy
import bmesh
from numpy.linalg import norm
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.points import init_points, register_points_handler, unregister_points_handler
from .. lib.math import v3_average, v3_distance, create_rotation_matrix_from_vertex, create_rotation_matrix_from_edge, create_rotation_matrix_from_face


class ND_OT_points(bpy.types.Operator):
    bl_idname = "nd.points"
    bl_label = "Points"
    bl_description = "Show all possible snap points on selected object"
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
            if self.snap_point:
                self.snap_point_rotation_cache = self.snap_point[1].copy()

                self.dirty = True

        elif pressed(event, {'R'}):
            self.snap_point_rotation_cache = None
                
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
        self.primary_points = []
        self.secondary_points = []
        self.snap_point = None
        self.snap_point_rotation_cache = None

        a, b = context.selected_objects
        self.reference_obj = a if a.name != context.object.name else b
        self.reference_obj_original_location = self.reference_obj.location.copy()
        self.reference_obj_original_rotation = self.reference_obj.rotation_euler.copy()

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.object.evaluated_get(depsgraph)

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        
        world_matrix = context.object.matrix_world

        vert_points = []
        for vert in bm.verts:
            vert_matrix = create_rotation_matrix_from_vertex(world_matrix, vert)
            vert_points.append((world_matrix @ vert.co, vert_matrix))

        edge_points = []
        for edge in bm.edges:
            edge_matrix = create_rotation_matrix_from_edge(world_matrix, edge)
            edge_points.append((world_matrix @ v3_average([v.co for v in edge.verts]), edge_matrix))

        face_points = []
        for face in bm.faces:
            face_matrix = create_rotation_matrix_from_face(world_matrix, face)
            face_points.append((world_matrix @ v3_average([v.co for v in face.verts]), face_matrix))

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
            return len(context.selected_objects) == 2 and all(obj.type == 'MESH' for obj in context.selected_objects)

    
    def operate(self, context):
        if self.snap_point:
            vect, rotation_matrix = self.snap_point
            self.reference_obj.location = vect
            if self.snap_point_rotation_cache is None:
                self.reference_obj.rotation_euler = rotation_matrix.to_euler()
            else:
                self.reference_obj.rotation_euler = self.snap_point_rotation_cache.to_euler()
        elif self.hit_location:
            self.reference_obj.location = self.hit_location

        self.dirty = False


    def recalculate_points(self, context, mouse_coords):
        self.reference_obj.hide_set(True)

        region = context.region
        region_data = context.space_data.region_3d

        view_vector = region_2d_to_vector_3d(region, region_data, mouse_coords)
        ray_origin = region_2d_to_origin_3d(region, region_data, mouse_coords)

        ray_target = ray_origin + view_vector
        ray_direction = ray_target - ray_origin

        depsgraph = context.evaluated_depsgraph_get()

        hit, location, normal, face_index, object, matrix = context.scene.ray_cast(depsgraph, ray_origin, ray_direction)

        if hit and object.name == context.object.name:
            self.hit_location = location

            self.primary_points = []
            self.secondary_points = []
            snap_points = []
            for (vect, rotation_matrix) in self.points_cache:
                if v3_distance(vect, location) <= 0.2:
                    snap_points.append((vect, rotation_matrix))
                elif v3_distance(vect, location) <= 0.5:
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


    def finish(self, context):
        unregister_draw_handler()
        unregister_points_handler()


    def revert(self, context):
        self.reference_obj.location = self.reference_obj_original_location
        self.reference_obj.rotation_euler = self.reference_obj_original_rotation

        unregister_draw_handler()
        unregister_points_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_hint(self, "Select snap point", "Hover over the selected object to select a snap point")

    draw_property(
        self, 
        "Capture Rotation [C] / Reset [R]".format(),
        "{}".format("Snap point rotation captured!" if self.snap_point_rotation_cache else "Free rotation enabled..."),
        active=self.snap_point_rotation_cache is not None,
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_points.bl_idname, text=ND_OT_points.bl_label)


def register():
    bpy.utils.register_class(ND_OT_points)


def unregister():
    bpy.utils.unregister_class(ND_OT_points)
    unregister_draw_handler()
