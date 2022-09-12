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

# (ID!, ICON!, CUSTOM_LABEL, MODE, DEPRECATED?)

standalone_ops = [
    ("nd.cycle", 'LONGDISPLAY', None, None, False),
]

sketch_ops = [
    ("nd.single_vertex", 'DOT', None, None, False),
    ("nd.make_manifold", 'OUTLINER_DATA_SURFACE', None, None, False),
    ("nd.clear_vgs", 'GROUP_VERTEX', None, None, False),
    None, # Separator
    ("nd.view_align", 'ORIENTATION_VIEW', None, None, False),
    None, # Separator
    ("nd.geo_lift", 'FACESEL', None, None, False),
    ("nd.panel", 'MOD_EXPLODE', None, None, False),
    None, # Separator
    ("nd.recon_poly", 'SURFACE_NCURVE', None, None, False),
    ("nd.screw_head", 'CANCEL', None, None, False),
]

boolean_ops = [
    ("nd.bool_vanilla", 'SELECT_SUBTRACT', "Difference", 'DIFFERENCE', False),
    ("nd.bool_vanilla", 'SELECT_EXTEND', "Union", 'UNION', False),
    ("nd.bool_vanilla", 'SELECT_INTERSECT', "Intersect", 'INTERSECT', False),
    None, # Separator
    ("nd.bool_slice", 'FCURVE', None, None, False),
    ("nd.bool_inset", 'MOD_BOOLEAN', None, None, False),
    None, # Separator
    ("nd.hydrate", 'SHADING_RENDERED', None, None, False),
    ("nd.swap_solver", 'CON_OBJECTSOLVER', None, None, False),
]

bevel_ops = [
    ("nd.vertex_bevel", 'VERTEXSEL', None, None, False),
    ("nd.edge_bevel", 'EDGESEL', None, None, False),
    None, # Separator
    ("nd.bevel", 'MOD_BEVEL', None, None, False),
    ("nd.weighted_normal_bevel", 'NORMALS_VERTEX_FACE', None, None, False),
]

extrusion_ops = [
    ("nd.solidify", 'MOD_SOLIDIFY', None, None, False),
    ("nd.screw", 'MOD_SCREW', None, None, False),
    ("nd.profile_extrude", 'EMPTY_SINGLE_ARROW', None, None, False),
]

replicate_ops = [
    ("nd.array_cubed", 'PARTICLES', None, None, False),
    ("nd.circular_array", 'DRIVER_ROTATIONAL_DIFFERENCE', None, None, False),
    ("nd.mirror", 'MOD_MIRROR', None, None, False),
]

deform_ops = [
    ("nd.lattice", 'MOD_LATTICE', None, None, False),
    ("nd.simple_deform", 'MOD_SIMPLEDEFORM', None, None, False),
]

simplify_ops = [
    ("nd.decimate", 'MOD_DECIM', None, None, False),
    ("nd.weld", 'AUTOMERGE_ON', None, None, False),
]

export_ops = [
    ("nd.name_sync", 'FILE_REFRESH', None, None, False),
    ("nd.set_lod_suffix", 'ALIASED', "Low LOD", 'LOW', False),
    ("nd.set_lod_suffix", 'ANTIALIASED', "High LOD", 'HIGH', False),
    None, # Separator
    ("nd.seams", 'UV_DATA', None, None, False),
    ("nd.triangulate", 'MOD_TRIANGULATE', None, None, False),
    None, # Separator
    ("nd.apply_modifiers", 'ORPHAN_DATA', None, None, False),
]

scene_ops = [
    ("nd.flare", 'LIGHT_AREA', "Flare (Lighting)", None, False),
    None, # Separator
    ("nd.clean_utils", 'MOD_FLUIDSIM', None, None, False),
]

util_ops = [
    ("nd.set_origin", 'TRANSFORM_ORIGINS', None, None, False),
    ("nd.snap_align", 'SNAP_ON', None, None, False),
    None, # Separator
    ("nd.smooth", 'MOD_SMOOTH', None, None, False),
]

viewport_ops = [
    ("nd.toggle_wireframes", 'MOD_WIREFRAME', None, None, False),
    ("nd.toggle_face_orientation", "ORIENTATION_NORMAL", None, None, False),
    ("nd.toggle_utils_collection", "OUTLINER_COLLECTION", None, None, False),
    None, # Separator
    ("nd.toggle_custom_view", "OVERLAY", None, None, False),
    ("nd.toggle_clear_view", "OVERLAY", None, None, False),
]


def build_icon_lookup_table():
    icon_lookup = {}
    for op in standalone_ops + sketch_ops + boolean_ops + bevel_ops + extrusion_ops + replicate_ops + deform_ops + simplify_ops + scene_ops + export_ops + util_ops + viewport_ops:
        if op is None:
            continue

        key = f'{op[0]}+{op[3]}' if op[3] is not None else op[0]
        icon_lookup[key] = op[1]

    return icon_lookup