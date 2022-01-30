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