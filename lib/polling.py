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


def obj_exists(obj):
    return obj is not None


def obj_is(obj, type={}):
    return obj_exists(obj) and obj.type in type


def obj_is_mesh(obj):
    return obj_is(obj, {'MESH'})


def obj_is_curve(obj):
    return obj_is(obj, {'CURVE'})


def objs_are(objs, type={}):
    return all([obj_is(obj, type) for obj in objs])


def objs_are_mesh(objs):
    return objs_are(objs, {'MESH'})


def objs_are_curve(objs):
    return objs_are(objs, {'CURVE'})


def obj_moddable(obj):
    return obj_is(obj, {'MESH', 'CURVE'})


def ctx_objects_selected(context, count=1):
    return len(context.selected_objects) == count


def ctx_min_objects_selected(context, count=1):
    return len(context.selected_objects) >= count


def ctx_mode(context, mode={}):
    return context.mode in mode


def ctx_multi_mode(context):
    return ctx_mode(context, {'OBJECT', 'EDIT_MESH'})


def ctx_obj_mode(context):
    return ctx_mode(context, {'OBJECT'})


def ctx_edit_mode(context):
    return ctx_mode(context, {'EDIT_MESH'})


def obj_verts_selected(obj):
    mesh = bmesh.from_edit_mesh(obj.data)
    return len([vert for vert in mesh.verts if vert.select]) > 0


def obj_edges_selected(obj):
    mesh = bmesh.from_edit_mesh(obj.data)
    return len([edge for edge in mesh.edges if edge.select]) > 0


def list_populated(objs):
    return len(objs) > 0


def list_gt(objs, count):
    return len(objs) > count


def list_lte(objs, count):
    return len(objs) <= count
