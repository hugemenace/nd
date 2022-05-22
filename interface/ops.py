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

sketching_ops = [
    ("nd.single_vertex", 'DOT', None, None, False),
    ("nd.make_manifold", 'OUTLINER_DATA_SURFACE', None, None, False),
    ("nd.geo_lift", 'FACESEL', None, None, False),
    ("nd.view_align", 'ORIENTATION_VIEW', None, None, False),
]

power_mod_ops = [
    ("nd.bool_vanilla", 'MOD_BOOLEAN', "Difference", 'DIFFERENCE', False),
    ("nd.bool_vanilla", 'MOD_BOOLEAN', "Union", 'UNION', False),
    ("nd.bool_vanilla", 'MOD_BOOLEAN', "Intersect", 'INTERSECT', False),
    ("nd.bool_slice", 'MOD_BOOLEAN', None, None, False),
    ("nd.bool_inset", 'MOD_BOOLEAN', None, None, False),
    ("nd.vertex_bevel", 'VERTEXSEL', None, None, False),
    ("nd.edge_bevel", 'EDGESEL', None, None, False),
    ("nd.bevel", 'MOD_BEVEL', None, None, False),
    ("nd.weighted_normal_bevel", 'MOD_BEVEL', None, None, False),
    ("nd.solidify", 'MOD_SOLIDIFY', None, None, False),
    ("nd.screw", 'MOD_SCREW', None, None, False),
    ("nd.profile_extrude", 'EMPTY_SINGLE_ARROW', None, None, False),
    ("nd.array_cubed", 'PARTICLES', None, None, False),
    ("nd.circular_array", 'DRIVER_ROTATIONAL_DIFFERENCE', None, None, False),
    ("nd.mirror", 'MOD_MIRROR', None, None, False),
    ("nd.lattice", 'MOD_LATTICE', None, None, False),
    ("nd.simple_deform", 'MOD_SIMPLEDEFORM', None, None, False),
]

generator_ops = [
    ("nd.recon_poly", 'SURFACE_NCURVE', None, None, False),
    ("nd.screw_head", 'CANCEL', None, None, False),
]

object_names_ops = [
    ("nd.name_sync", 'FILE_REFRESH', None, None, False),
    ("nd.set_lod_suffix", 'ALIASED', "Low LOD", 'LOW', False),
    ("nd.set_lod_suffix", 'ANTIALIASED', "High LOD", 'HIGH', False),
]

object_transform_ops = [
    ("nd.set_origin", 'TRANSFORM_ORIGINS', None, None, False),
    ("nd.snap_align", 'SNAP_ON', None, None, False),
]

object_properties_ops = [
    ("nd.cycle", 'LONGDISPLAY', None, None, False),
    ("nd.smooth", 'MOD_SMOOTH', None, None, False),
    ("nd.seams", 'UV_DATA', None, None, False),
    ("nd.clear_vgs", 'GROUP_VERTEX', None, None, False),
    ("nd.triangulate", 'MOD_TRIANGULATE', None, None, False),
    ("nd.apply_modifiers", 'ORPHAN_DATA', None, None, False),
]

misc_ops = [
    ("nd.hydrate", 'SHADING_RENDERED', None, None, False),
    ("nd.swap_solver", 'CON_OBJECTSOLVER', None, None, False),
    ("nd.flare", 'LIGHT_AREA', "Flare (Lighting)", None, False),
]

toggle_ops = [
    ("nd.toggle_wireframes", 'MOD_WIREFRAME', None, None, False),
    ("nd.toggle_face_orientation", "ORIENTATION_NORMAL", None, None, False),
    ("nd.toggle_utils_collection", "OUTLINER_COLLECTION", None, None, False),
    ("nd.toggle_clear_view", "OUTLINER_DATA_VOLUME", None, None, False),
]