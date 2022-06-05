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
from mathutils.geometry import distance_point_to_plane, normal
from . preferences import get_preferences


def add_single_vertex_object(cls, context, name):
    mesh = bpy.data.meshes.new("ND — " + name)
    obj = bpy.data.objects.new("ND — " + name, mesh)

    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    bm.verts.new()
    bm.to_mesh(mesh)
    bm.free()
    
    obj.select_set(True)
    
    context.view_layer.objects.active = obj
    
    bpy.ops.object.shade_smooth()
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = radians(float(get_preferences().default_smoothing_angle))
    
    cls.obj = obj


def align_object_to_3d_cursor(cls, context):
    cls.obj.location = context.scene.cursor.location
    cls.obj.rotation_euler = context.scene.cursor.rotation_euler


def set_origin(obj, mx):
    update_child_matrices(obj, mx)

    new_matrix = mx.inverted_safe() @ obj.matrix_world

    obj.matrix_world = mx
    obj.data.transform(new_matrix)
    obj.data.update()


def update_child_matrices(obj, mx):
    orig_matrix = obj.matrix_world.copy()
    new_matrix = mx.inverted_safe() @ orig_matrix

    for c in obj.children:
        parent_matrix = c.matrix_parent_inverse
        c.matrix_parent_inverse = new_matrix @ parent_matrix


def create_duplicate_liftable_geometry(context, mode, object_name, ignore_complex_geo=True):
    bpy.ops.object.duplicate()

    if ignore_complex_geo:
        mods = [(mod.name, mod) for mod in context.active_object.modifiers]
        for name, mod in mods:
            if not mod:
                continue

            if mod.type == 'SUBSURF':
                bpy.ops.object.modifier_remove(modifier=name)
                continue
            
            if mod.type == 'BEVEL' and mod.affect == 'EDGES' and mod.limit_method == 'ANGLE':
                if mod.segments > 1 or (mod.segments == 1 and mod.harden_normals):
                    bpy.ops.object.modifier_remove(modifier=name)
                    continue
            
            if "— ND WNB" in mod.name:
                bpy.ops.object.modifier_remove(modifier=name)
                continue

    depsgraph = context.evaluated_depsgraph_get()
    object_eval = context.active_object.evaluated_get(depsgraph)

    context.active_object.modifiers.clear()
    context.active_object.show_in_front = True

    vertex_groups = context.active_object.vertex_groups.values()
    for vg in vertex_groups:
        context.active_object.vertex_groups.remove(vg)

    bm = bmesh.new()
    bm.from_mesh(object_eval.data)

    bevel_weight_layer = bm.edges.layers.bevel_weight.verify()

    selected_edges = list(bm.edges)
    for edge in selected_edges:
        edge[bevel_weight_layer] = 0

    bm.to_mesh(context.active_object.data)
    bm.free()

    bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode=mode)
    bpy.ops.mesh.select_all(action='DESELECT')

    context.active_object.name = object_name
    context.active_object.data.name = object_name

    bpy.ops.mesh.customdata_custom_splitnormals_clear()


def is_planar(bm, tolerance=0.001):
    faces = list(bm.faces)

    if len(faces) < 1:
        return True
    
    head = faces[0]

    if len(faces) == 1 and len(head.verts) == 3:
        return True

    co = head.verts[0].co
    norm = normal([v.co for v in head.verts[:3]])

    tail = faces[1:]
    for f in tail:
        verts = [v.co for v in f.verts]
        for v in verts:
            if not abs(distance_point_to_plane(v, co, norm)) < tolerance:
                return False

    return True