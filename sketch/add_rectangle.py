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
# Contributors: Shaddow
# ---

import bpy
import bpy_extras
import mathutils
from math import radians
from ..lib.base_operator import BaseOperator
from ..lib.overlay import init_overlay, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from ..lib.events import capture_modifier_keys, pressed
from ..lib.preferences import get_preferences, get_scene_unit_factor
from ..lib.numeric_input import update_stream, no_stream, get_stream_value, new_stream, has_stream, set_stream
from ..lib.objects import get_real_active_object
from ..lib.polling import ctx_edit_mode, obj_is_mesh, ctx_objects_selected, app_minor_version
from ..lib.math import v3_distance, v3_average
from .. lib.points import init_points, register_points_handler, unregister_points_handler


class ND_OT_add_rectangle(BaseOperator):
    bl_idname = "nd.add_rectangle"
    bl_label = "Add rectangle"
    bl_description = """Interactivly add a rectangle"""

    def do_invoke(self, context, event):
        self.dirty = False
        
        self.active = False
        self.override_orientation = False
        
        self.start_point = None
        self.end_point = None
        self.target_obj = None
        self.face_index = None
        self.hit_normal = None
        self.normal = None
        self.tangent = None
        self.bitangent = None
        
        self.from_center = False
        self.force_dimensions = False
        self.orientations = ["Local", "World", "Cursor", "View"]
        self.local_orientation = ["Default", "Closest Edge", "Longest Edge"]
        self.current_orientation = 0
        self.current_local_orientation = 0

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)       
        
        init_points(self)
        register_points_handler(self)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def do_modal(self, context, event):
        if self.key_confirm and not self.active: 
                hit, location, hit_normal, face_index, target_obj = self.get_mouse_raycast(context, event)
                if hit:
                    self.start_point = location
                    self.hit_normal = hit_normal
                    self.target_obj = target_obj
                    self.face_index = face_index

                    self.set_plane_axes(context)
                    self.end_point = location
                    self.active = True
                else:
                    self.current_orientation = 3
                    self.set_plane_axes(context)
                    
                    region = context.region
                    rv3d = context.space_data.region_3d
                    coord = (event.mouse_region_x, event.mouse_region_y)

                    view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
                    ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
                    cursor_pos = context.scene.cursor.location
                    
                    self.start_point = self.ray_plane_intersection(ray_origin, view_vector, cursor_pos, self.normal)
                    self.active = True
                    self.override_orientation = True
                    
                    
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}
    
        if pressed(event, {'C'}):
            self.from_center = not self.from_center

            self.dirty = True
            
        if pressed(event, {'D'}):
            self.force_dimensions = not self.force_dimensions
            
            self.dirty
            
        if pressed(event, {'A'}) and not self.override_orientation:
            self.current_orientation = (self.current_orientation + 1) % len(self.orientations)
            if self.active: self.set_plane_axes(context)
            self.dirty = True
            
        if pressed(event, {'S'}) and not self.override_orientation:
            self.current_local_orientation = (self.current_local_orientation + 1) % len(self.local_orientation)
            if self.active: self.set_plane_axes(context)
            self.dirty = True

        if event.type == 'MOUSEMOVE' and self.active:
            region = context.region
            rv3d = context.space_data.region_3d
            coord = (event.mouse_region_x, event.mouse_region_y)

            view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            end_point = self.ray_plane_intersection(ray_origin, view_vector, self.start_point, self.normal)

            if end_point is not None:
                self.end_point = end_point
            
            self.dirty = True
            
        if self.key_movement_passthrough:
            return {'PASS_THROUGH'}


        return {'RUNNING_MODAL'}


    def operate(self, context):
        if self.active:
            if not self.from_center:
                self.primary_points = [self.calculate_rectangle()[0], self.calculate_rectangle()[2]]
                self.secondary_points = [self.calculate_rectangle()[1], self.calculate_rectangle()[3]]
                self.outline = self.calculate_rectangle()
            else:
                self.primary_points = [self.start_point, self.calculate_rectangle()[2]]
                self.secondary_points = [self.calculate_rectangle()[0], self.calculate_rectangle()[1], self.calculate_rectangle()[3]]
                self.outline = self.calculate_rectangle()
            
        self.dirty = False


    def finish(self, context):
        mesh = bpy.data.meshes.new("ND - Plane")
        mesh.from_pydata(self.calculate_rectangle(local=True), [], [(0, 1, 2, 3)])
        mesh.update()
        
        obj = bpy.data.objects.new("ND - Plane", mesh)
        bpy.context.collection.objects.link(obj)
        
        obj.location = self.start_point
        obj.rotation_euler = self.calculate_matrix().to_euler()
        
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        unregister_draw_handler()
        unregister_points_handler()  
        bpy.ops.nd.solidify('INVOKE_DEFAULT')
        
        
    def revert(self, context):
        unregister_draw_handler()
        unregister_points_handler()


    def get_mouse_raycast(self, context, event):
        region = context.region
        rv3d = context.space_data.region_3d
        coord = (event.mouse_region_x, event.mouse_region_y)

        depsgraph = context.evaluated_depsgraph_get()

        view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        result, location, normal, face_index, obj, _ = context.scene.ray_cast(depsgraph, ray_origin, view_vector)

        return result, location, normal, face_index, obj


    def calculate_rectangle(self, local=False):
        local_vector = self.end_point - self.start_point
        x_len = local_vector.dot(self.tangent)
        y_len = local_vector.dot(self.bitangent)
        if self.force_dimensions: 
            max_abs = max(abs(x_len), abs(y_len))

            x_len = -max_abs if x_len < 0 else max_abs
            y_len = -max_abs if y_len < 0 else max_abs
        
        if not self.from_center:
            corners = [
                mathutils.Vector((0, 0, 0)),
                mathutils.Vector((x_len, 0, 0)),
                mathutils.Vector((x_len, y_len, 0)),
                mathutils.Vector((0, y_len, 0)),
            ]
        else:
            corners = [
                mathutils.Vector((-x_len, -y_len, 0)),
                mathutils.Vector((x_len, -y_len, 0)),
                mathutils.Vector((x_len, y_len, 0)),
                mathutils.Vector((-x_len, y_len, 0)),
            ]

        if not local:
            matrix = self.calculate_matrix()
            corners = [(matrix @ point) + self.start_point for point in corners]
            return corners
        else:
            return corners
    
    
    def calculate_matrix(self):
        z_axis = self.normal.normalized()
        x_axis = self.tangent.normalized()
        y_axis = self.bitangent.normalized()
        
        rotation_matrix = mathutils.Matrix((
            x_axis.to_4d(),
            y_axis.to_4d(),
            z_axis.to_4d(),
            (0, 0, 0, 1)
        )).transposed()
        return rotation_matrix


    def set_plane_axes(self ,context):
        if self.current_orientation == 0:
            if self.current_local_orientation == 0:
                cross_vector = self.target_obj.matrix_world.col[0].xyz.normalized()
                if abs(self.hit_normal.dot(cross_vector)) > 0.999:
                    cross_vector = self.target_obj.matrix_world.col[1].xyz.normalized()
                tangent = self.hit_normal.cross(cross_vector).normalized()
                bitangent = self.hit_normal.cross(tangent).normalized()
                self.normal = self.hit_normal
                
            elif self.current_local_orientation == 1:
                v1, v2 = self.get_closest_edge()
                edge_direction = (v2 - v1).normalized()
                tangent = self.hit_normal.cross(edge_direction).normalized()
                bitangent = self.hit_normal.cross(tangent).normalized()
                self.normal = self.hit_normal
                
            elif self.current_local_orientation == 2:
                v1, v2 = self.get_longest_edge()
                edge_direction = (v2 - v1).normalized()
                tangent = self.hit_normal.cross(edge_direction).normalized()
                bitangent = self.hit_normal.cross(tangent).normalized()
                self.normal = self.hit_normal
                
        elif self.current_orientation == 1:
            tangent = mathutils.Vector((1.0, 0.0, 0.0))
            bitangent = mathutils.Vector((0.0, 1.0, 0.0))
            self.normal = mathutils.Vector((0.0, 0.0, 1.0))
            
        elif self.current_orientation == 2:
            matrix = context.scene.cursor.matrix.to_3x3()
            tangent = matrix.col[0]
            bitangent = matrix.col[1]
            self.normal = matrix.col[2]
            
        elif self.current_orientation == 3:
            matrix = context.space_data.region_3d.view_rotation.to_matrix()
            tangent = matrix.col[0]
            bitangent = matrix.col[1]
            self.normal = matrix.col[2]

        self.tangent, self.bitangent = tangent, bitangent


    def ray_plane_intersection(self, ray_origin, ray_direction, plane_point, plane_normal):
        denom = ray_direction.dot(plane_normal)
        if abs(denom) < 1e-6:
            return None
        d = (plane_point - ray_origin).dot(plane_normal) / denom
        if d < 0:
            return None
        return ray_origin + ray_direction * d


    def get_closest_edge(self):
        mesh = self.target_obj.data
        vert_indices = mesh.polygons[self.face_index].vertices

        min_distance = float('inf')
        closest_edge = None
        verts_world = [self.target_obj.matrix_world @ mesh.vertices[i].co for i in vert_indices]

        for i in range(len(verts_world)):
            v1 = verts_world[i]
            v2 = verts_world[(i + 1) % len(verts_world)]
            
            closest_point = mathutils.geometry.intersect_point_line(self.start_point, v1, v2)[0]
            distance = (self.start_point - closest_point).length

            if distance < min_distance:
                min_distance = distance
                closest_edge = (v1, v2)

        return closest_edge
    
    
    def get_longest_edge(self):
        mesh = self.target_obj.data
        vert_indices = mesh.polygons[self.face_index].vertices

        max_length = -1
        longest_edge = None

        verts_world = [self.target_obj.matrix_world @ mesh.vertices[i].co for i in vert_indices]

        num_verts = len(verts_world)

        for i in range(num_verts):
            v1 = verts_world[i]
            v2 = verts_world[(i + 1) % num_verts]

            edge_length = (v2 - v1).length

            if edge_length > max_length:
                max_length = edge_length
                longest_edge = (v1, v2)

        return longest_edge
        
    
def draw_text_callback(self):
    draw_header(self)

    draw_hint(
        self,
        "From Center [C]: {}".format('True' if self.from_center else 'False'),
        "False, True")
    
    draw_hint(
        self,
        "Force Dimensions [D]: {}".format('True' if self.force_dimensions else 'False'),
        "False, True")
    
    if not self.override_orientation:
        draw_hint(
            self,
            "Orientation [A]: {}".format(self.orientations[self.current_orientation].capitalize()),
            ", ".join([m.capitalize() for m in self.orientations]))
        
    else:
        draw_hint(
            self,
            "Orientation Overwritten : {}".format(self.orientations[self.current_orientation].capitalize()),
            "Orientation Overwritten")
    
    if self.current_orientation == 0:
        draw_hint(
            self,
            "Rotation [S]: {}".format(self.local_orientation[self.current_local_orientation].capitalize()),
            ", ".join([m.capitalize() for m in self.local_orientation]))


def register():
    bpy.utils.register_class(ND_OT_add_rectangle)


def unregister():
    bpy.utils.unregister_class(ND_OT_add_rectangle)
    unregister_draw_handler()
    unregister_points_handler()

