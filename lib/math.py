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

from math import radians
from mathutils import Vector, Matrix


def v3_center(x, y):
    return x.co + (y.co - x.co) * 0.5


def v3_sum(vectors):
    total = Vector()

    for vector in vectors:
        total += vector

    return total


def v3_average(vectors):
    return v3_sum(vectors) / len(vectors)


def v3_elem(label, vector):
    return vector[{'X': 0, 'Y': 1, 'Z': 2}[label]]


def v3_distance(a, b):
    return (a - b).length


def get_edge_normal(edge):
    return v3_sum_normalized([face.normal for face in edge.link_faces])


def v3_sum_normalized(vectors):
    return v3_sum(vectors).normalized()


def create_rotation_matrix_from_vertex(world_matrix, vertex):
    normal = world_matrix.to_3x3() @ vertex.normal

    if vertex.link_edges:
        longest_edge = max([edge for edge in vertex.link_edges], key=lambda x: x.calc_length())
        binormal = (world_matrix.to_3x3() @ (longest_edge.other_vert(vertex).co - vertex.co)).normalized()
        tangent = binormal.cross(normal).normalized()
        binormal = normal.cross(tangent).normalized()
    else:
        up = calculate_object_up(world_matrix, normal)
        tangent = normal.cross(up).normalized()
        binormal = normal.cross(tangent).normalized()

    return create_transposed_rotation_matrix(tangent, binormal, normal)


def create_rotation_matrix_from_edge(world_matrix, edge):
    binormal = (world_matrix.to_3x3() @ (edge.verts[1].co - edge.verts[0].co)).normalized()

    if edge.link_faces:
        normal = (world_matrix.to_3x3() @ get_edge_normal(edge)).normalized()
        tangent = binormal.cross(normal).normalized()
        normal = tangent.cross(binormal).normalized()
    else:
        up = calculate_object_up(world_matrix, binormal)
        tangent = binormal.cross(up).normalized()
        normal = tangent.cross(binormal)

    return create_transposed_rotation_matrix(tangent, binormal, normal)


def calculate_object_up(world_matrix, normal):
    up = (world_matrix.to_3x3() @ Vector((0, 0, 1)))

    dot = normal.dot(up)
    if abs(round(dot, 6)) == 1:
        up = (world_matrix.to_3x3() @ Vector((1, 0, 0)))

    return up.normalized()


def create_rotation_matrix_from_face(world_matrix, face):
    normal = (world_matrix.to_3x3() @ face.normal).normalized()
    tangent = (world_matrix.to_3x3() @ face.calc_tangent_edge_pair()).normalized()
    binormal = normal.cross(tangent)

    return create_transposed_rotation_matrix(tangent, binormal, normal)


def create_transposed_rotation_matrix(tangent, binormal, normal):
    rotation = Matrix()
    rotation[0].xyz = tangent
    rotation[1].xyz = binormal
    rotation[2].xyz = normal

    return rotation.transposed()


def get_min_max(value):
    return (min(value), max(value))


def generate_bounding_box(coords):
    min_x, max_x = get_min_max([v3_elem('X', c.co) for c in coords])
    min_y, max_y = get_min_max([v3_elem('Y', c.co) for c in coords])
    min_z, max_z = get_min_max([v3_elem('Z', c.co) for c in coords])

    return [
        Vector((min_x, min_y, min_z)),
        Vector((min_x, min_y, max_z)),
        Vector((min_x, max_y, max_z)),
        Vector((min_x, max_y, min_z)),
        Vector((max_x, min_y, min_z)),
        Vector((max_x, min_y, max_z)),
        Vector((max_x, max_y, max_z)),
        Vector((max_x, max_y, min_z))
    ]
