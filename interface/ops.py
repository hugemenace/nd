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

# (ID!, ICON!, CUSTOM_LABEL, MODE, EXPERIMENTAL?)

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
    ("nd.circularize", 'MESH_CIRCLE', None, None, False),
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
    ("nd.duplicate_utility", 'CON_SIZELIKE', None, None, True),
]

bevel_ops = [
    ("nd.bevel", 'MOD_BEVEL', None, None, False),
    None, # Separator
    ("nd.vertex_bevel", 'VERTEXSEL', None, None, False),
    ("nd.edge_bevel", 'EDGESEL', None, None, False),
]

extrusion_ops = [
    ("nd.solidify", 'MOD_SOLIDIFY', None, None, False),
    ("nd.screw", 'MOD_SCREW', None, None, False),
    ("nd.profile_extrude", 'EMPTY_SINGLE_ARROW', None, None, False),
    ("nd.pipe_extrude", 'ANIM', None, None, False),
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

shading_ops = [
    ("nd.smooth", 'MOD_SMOOTH', None, None, False),
    ("nd.wn", 'MOD_NORMALEDIT', None, None, False),
]

packaging_ops = [
    ("nd.bulk_create_id_materials", 'NODE_COMPOSITING', None, None, False),
    ("nd.clear_materials", 'NODE_MATERIAL', None, None, False),
    None, # Separator
    ("nd.name_sync", 'FILE_REFRESH', None, None, False),
    ("nd.set_lod_suffix", 'ALIASED', "Low LOD", 'LOW', False),
    ("nd.set_lod_suffix", 'ANTIALIASED', "High LOD", 'HIGH', False),
    None, # Separator
    ("nd.seams", 'UV_DATA', None, None, False),
    ("nd.triangulate", 'MOD_TRIANGULATE', None, None, False),
]

scene_ops = [
    ("nd.flare", 'LIGHT_AREA', "Flare (Lighting)", None, False),
    ("nd.clean_utils", 'MOD_FLUIDSIM', None, None, False),
]

util_ops = [
    ("nd.set_origin", 'TRANSFORM_ORIGINS', None, None, False),
    ("nd.snap_align", 'SNAP_ON', None, None, False),
    None, # Separator
    ("nd.smart_duplicate", 'DUPLICATE', "Smart Duplicate", "DUPLICATE", False),
    ("nd.smart_duplicate", 'LINKED', "Linked Duplicate", "LINKED", False),
    None, # Separator
    ("nd.sync_modifiers", 'SYSTEM', None, None, False),
    None, # Separator
    ("nd.apply_modifiers", 'ORPHAN_DATA', None, None, False),
]

viewport_ops = [
    ("nd.toggle_wireframes", 'MOD_WIREFRAME', None, None, False),
    ("nd.toggle_face_orientation", "ORIENTATION_NORMAL", None, None, False),
    ("nd.toggle_utils_collection", "OUTLINER_COLLECTION", None, "DYNAMIC", False),
    None, # Separator
    ("nd.silhouette", "CLIPUV_DEHLT", None, None, False),
    None, # Separator
    ("nd.toggle_custom_view", "OVERLAY", None, None, False),
    ("nd.toggle_clear_view", "OVERLAY", None, None, False),
]


def build_icon_lookup_table():
    icon_lookup = {}
    for op in standalone_ops + sketch_ops + boolean_ops + bevel_ops + extrusion_ops + replicate_ops + \
    deform_ops + simplify_ops + shading_ops + scene_ops + packaging_ops + util_ops + viewport_ops:
        if op is None:
            continue

        key = f'{op[0]}+{op[3]}' if op[3] is not None else op[0]
        icon_lookup[key] = op[1]

    return icon_lookup
