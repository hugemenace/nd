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

import bmesh


def object_exists(obj):
    return obj is not None


def object_is(obj, type={}):
    return object_exists(obj) and obj.type in type


def object_is_mesh(obj):
    return object_is(obj, {'MESH'})


def object_is_curve(obj):
    return object_is(obj, {'CURVE'})


def all_objects_are(objs, type={}):
    return all([object_is(obj, type) for obj in objs])


def all_objects_are_mesh(objs):
    return all_objects_are(objs, {'MESH'})


def all_objects_are_curve(objs):
    return all_objects_are(objs, {'CURVE'})


def object_supports_mods(obj):
    return object_is(obj, {'MESH', 'CURVE'})


def all_objects_support_mods(objs):
    return all([object_supports_mods(obj) for obj in objs])


def has_objects_selected(context, count=1):
    return len(context.selected_objects) == count


def has_min_objects_selected(context, count=1):
    return len(context.selected_objects) >= count


def is_mode(context, mode={}):
    return context.mode in mode


def is_object_edit_mode(context):
    return is_mode(context, {'OBJECT', 'EDIT_MESH'})


def is_object_mode(context):
    return is_mode(context, {'OBJECT'})


def is_edit_mode(context):
    return is_mode(context, {'EDIT_MESH'})


def has_verts_selected(obj):
    mesh = bmesh.from_edit_mesh(obj.data)
    return len([vert for vert in mesh.verts if vert.select]) > 0


def has_edges_selected(obj):
    mesh = bmesh.from_edit_mesh(obj.data)
    return len([edge for edge in mesh.edges if edge.select]) > 0


def has_faces_selected(obj):
    mesh = bmesh.from_edit_mesh(obj.data)
    return len([face for face in mesh.faces if face.select]) > 0


def not_empty(objs):
    return len(objs) > 0


def list_gt(objs, count):
    return len(objs) > count


def list_lt(objs, count):
    return len(objs) < count


def list_gte(objs, count):
    return len(objs) >= count


def list_lte(objs, count):
    return len(objs) <= count
