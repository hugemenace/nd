import bpy
import bmesh
from math import radians
from mathutils import Vector, Matrix


def averaged_vector(vector_list, size=3):
    vector_sum = Vector.Fill(size)

    for vector in vector_list:
        vector_sum += vector

    return vector_sum / len(vector_list)


def create_rotation_matrix_from_face(world_matrix, face):
    normal = (world_matrix.to_3x3() @ face.normal).normalized()
    tangent = (world_matrix.to_3x3() @ face.calc_tangent_edge_pair()).normalized()
    binormal = normal.cross(tangent)

    rotation = Matrix()
    rotation[0].xyz = tangent
    rotation[1].xyz = binormal
    rotation[2].xyz = normal

    return rotation.transposed()


def set_3d_cursor(location, rotation):
    cursor = bpy.context.scene.cursor
    cursor.location = location

    if cursor.rotation_mode == 'QUATERNION':
        cursor.rotation_quaternion = rotation
    elif cursor.rotation_mode == 'AXIS_ANGLE':
        cursor.rotation_axis_angle = rotation.to_axis_angle()
    else:
        cursor.rotation_euler = rotation.to_euler(cursor.rotation_mode)


def add_single_vertex_object(self, context, name):
    mesh = bpy.data.meshes.new("ND — " + name)
    obj = bpy.data.objects.new("ND — " + name, mesh)
    bpy.data.collections[context.collection.name].objects.link(obj)
    bm = bmesh.new()
    bm.verts.new()
    bm.to_mesh(mesh)
    bm.free()
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = radians(30)
    
    self.obj = obj


def align_object_to_3d_cursor(self, context):
    self.obj.location = context.scene.cursor.location
    self.obj.rotation_euler = context.scene.cursor.rotation_euler