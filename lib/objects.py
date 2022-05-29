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


def create_duplicate_liftable_geometry(context, mode, name, ignore_complex_geo=True):
    bpy.ops.object.duplicate()

    if ignore_complex_geo:
        mods = list(context.object.modifiers)
        for mod in mods:
            if mod.type == 'SUBSURF':
                context.object.modifiers.remove(mod)
            
            if mod.type == 'BEVEL' and mod.affect == 'EDGES' and mod.limit_method == 'ANGLE':
                if mod.segments > 1 or (mod.segments == 1 and mod.harden_normals):
                    context.object.modifiers.remove(mod)
            
            if "— ND WNB" in mod.name:
                context.object.modifiers.remove(mod)

    depsgraph = context.evaluated_depsgraph_get()
    object_eval = context.object.evaluated_get(depsgraph)

    context.object.modifiers.clear()
    context.object.show_in_front = True

    vertex_groups = context.object.vertex_groups.values()
    for vg in vertex_groups:
        context.object.vertex_groups.remove(vg)

    bm = bmesh.new()
    bm.from_mesh(object_eval.data)

    bevel_weight_layer = bm.edges.layers.bevel_weight.verify()

    selected_edges = list(bm.edges)
    for edge in selected_edges:
        edge[bevel_weight_layer] = 0

    bm.to_mesh(context.object.data)
    bm.free()

    bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode=mode)
    bpy.ops.mesh.select_all(action='DESELECT')

    context.object.name = name
    context.object.data.name = name

    bpy.ops.mesh.customdata_custom_splitnormals_clear()