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

import bpy
import bmesh
from .. __init__ import bl_info
from .. lib.objects import is_planar, get_real_active_object
from . ops import build_icon_lookup_table
from .. lib.addons import is_addon_enabled
from .. lib.polling import ctx_edit_mode


SECTION_COUNT = 1
NO_SECTION_COUNT = 0

keys = []
icons = build_icon_lookup_table()


class ND_MT_fast_menu(bpy.types.Menu):
    bl_label = "ND v%s — Fast (Predict)" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_MT_fast_menu"


    def draw(self, context):
        objs = context.selected_objects
        target_object = get_real_active_object(context)
        has_target = target_object is not None
        has_soft_target = context.active_object is not None
        edit_mode = ctx_edit_mode(context)

        total_sections = 0

        if not edit_mode and len(objs) == 0:
            total_sections += self.draw_no_object_predictions(context)
        elif edit_mode and has_soft_target:
            total_sections += self.draw_single_object_predictions(context)
        elif not has_target and len(objs) > 0:
            total_sections += self.draw_no_active_target(context)
        elif has_target and len(objs) == 1:
            total_sections += self.draw_single_object_predictions(context)
        elif has_target and len(objs) == 2:
            total_sections += self.draw_two_object_predictions(context)
        elif has_target and len(objs) > 2:
            total_sections += self.draw_many_object_predictions(context)

        if total_sections == 0:
            return self.draw_no_predictions(context)


    def draw_no_predictions(self, context):
        layout = self.layout
        layout.label(text="No predictions available", icon='GHOST_DISABLED')


    def draw_no_active_target(self, context):
        layout = self.layout
        layout.label(text="No active target object selected", icon='RESTRICT_SELECT_OFF')

        return NO_SECTION_COUNT


    def draw_make_edge_face_ops(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.separator()

        text = "F » Make Edge/Face"
        icon = 'MOD_SIMPLIFY'

        if is_addon_enabled("bl_ext.blender_org.f2") or is_addon_enabled("mesh_f2"):
            try:
                layout.operator("mesh.f2", text=text, icon=icon)
            except:
                layout.operator("mesh.edge_face_add", text=text, icon=icon)
        else:
            layout.operator("mesh.edge_face_add", text=text, icon=icon)


    def draw_no_object_predictions(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.operator("nd.single_vertex", icon=icons['nd.single_vertex'])
        layout.operator("nd.recon_poly", icon=icons['nd.recon_poly'])
        layout.separator()
        layout.operator("mesh.primitive_plane_add", icon='MESH_PLANE')
        layout.operator("mesh.primitive_cube_add", icon='MESH_CUBE')

        return SECTION_COUNT


    def draw_two_object_predictions(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        obj_names = [obj.name for obj in context.selected_objects]
        if all(["Bool —" in name for name in obj_names]):
            layout.operator("nd.hydrate", icon=icons['nd.hydrate'])
            layout.operator("nd.swap_solver", text="Swap Solver (Booleans)", icon=icons['nd.swap_solver'])

            return SECTION_COUNT

        layout.operator("nd.bool_vanilla", text="Difference", icon=icons['nd.bool_vanilla+DIFFERENCE']).mode = 'DIFFERENCE'
        layout.operator("nd.bool_vanilla", text="Union", icon=icons['nd.bool_vanilla+UNION']).mode = 'UNION'
        layout.operator("nd.bool_vanilla", text="Intersect", icon=icons['nd.bool_vanilla+INTERSECT']).mode = 'INTERSECT'
        layout.operator("nd.bool_slice", icon=icons['nd.bool_slice'])
        layout.operator("nd.bool_inset", icon=icons['nd.bool_inset'])
        layout.separator()
        layout.operator("nd.mirror", icon=icons['nd.mirror'])
        layout.operator("nd.circular_array", icon=icons['nd.circular_array'])
        layout.operator("nd.snap_align", icon=icons['nd.snap_align'])
        layout.separator()
        layout.operator("nd.smooth", icon=icons['nd.smooth'])
        layout.operator("nd.wn", icon=icons['nd.wn'])

        return SECTION_COUNT


    def draw_single_object_predictions(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        target_object = context.active_object

        if context.mode == 'EDIT_MESH':
            layout.operator("nd.vertex_bevel", icon=icons['nd.vertex_bevel'])
            layout.operator("nd.edge_bevel", icon=icons['nd.edge_bevel'])
            layout.operator("nd.make_manifold", icon=icons['nd.make_manifold'])
            layout.operator("nd.clear_vgs", icon=icons['nd.clear_vgs'])
            layout.separator()
            layout.operator("nd.mirror", icon=icons['nd.mirror'])
            layout.operator("nd.screw", icon=icons['nd.screw'])
            layout.operator("nd.profile_extrude", icon=icons['nd.profile_extrude'])
            layout.operator("nd.pipe_extrude", icon=icons['nd.pipe_extrude'])

            self.draw_make_edge_face_ops(context)

            return SECTION_COUNT

        if context.mode == 'OBJECT':
            if target_object.type == 'MESH':
                return self.draw_single_object_mesh_predictions(context, layout)
            elif target_object.type == 'CURVE':
                return self.draw_single_object_curve_predictions(context, layout)

        return NO_SECTION_COUNT


    def draw_single_object_curve_predictions(self, context, layout):
        layout.operator("nd.screw", icon=icons['nd.screw'])
        layout.operator("nd.mirror", icon=icons['nd.mirror'])
        layout.operator("nd.array_cubed", icon=icons['nd.array_cubed'])
        layout.operator("nd.simple_deform", icon=icons['nd.simple_deform'])

        return SECTION_COUNT


    def draw_single_object_mesh_predictions(self, context, layout):
        target_object = get_real_active_object(context)
        if target_object is None:
            return NO_SECTION_COUNT

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = target_object.evaluated_get(depsgraph)

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)

        self.verts = [vert for vert in bm.verts]
        self.edges = [edge for edge in bm.edges]
        self.faces = [face for face in bm.faces]
        self.sketch = len(self.faces) >= 1 and is_planar(bm)
        self.profile = len(self.faces) == 0 and len(self.edges) > 0
        self.has_faces = len(self.faces) >= 1
        self.manifold = all([len(edge.link_faces) == 2 for edge in self.edges])
        self.has_loose_edges = any([len(edge.link_faces) == 0 for edge in self.edges])

        bm.free()

        mod_names = [mod.name for mod in target_object.modifiers]

        has_mod_profile_extrude = False
        has_mod_pipe_extrude = False
        has_mod_solidify = False
        has_mod_boolean = False
        has_mod_screw = False
        has_mod_array_cubed = False
        has_mod_circular_array = False
        has_mod_circularize = False
        has_mod_recon_poly = False

        for name in mod_names:
            has_mod_profile_extrude = has_mod_profile_extrude or bool("— ND PE" in name)
            has_mod_pipe_extrude = has_mod_pipe_extrude or bool("— ND PIPE" in name)
            has_mod_solidify = has_mod_solidify or bool("— ND SOL" in name)
            has_mod_boolean = has_mod_boolean or bool("— ND Bool" in name)
            has_mod_screw = has_mod_screw or bool("— ND SCR" in name)
            has_mod_array_cubed = has_mod_array_cubed or bool("Array³" in name)
            has_mod_circular_array = has_mod_circular_array or bool("— ND CA" in name)
            has_mod_recon_poly = has_mod_recon_poly or bool("— ND RCP" in name)
            has_mod_circularize = has_mod_circularize or bool("— ND CIRC" in name)

        was_profile_extrude = has_mod_profile_extrude and not has_mod_solidify

        replay_prediction_count = 0

        if has_mod_boolean:
            layout.operator("nd.cycle", icon=icons['nd.cycle'])
            layout.separator()
            replay_prediction_count += 1

        if (not self.manifold and self.has_faces) or has_mod_solidify:
            layout.operator("nd.solidify", icon=icons['nd.solidify'])
            has_mod_solidify = True
            replay_prediction_count += 1

        if (not self.manifold and self.has_loose_edges) or has_mod_profile_extrude:
            layout.operator("nd.profile_extrude", icon=icons['nd.profile_extrude'])
            has_mod_profile_extrude = True
            replay_prediction_count += 1

        if (not self.manifold and self.has_loose_edges) or has_mod_pipe_extrude:
            layout.operator("nd.pipe_extrude", icon=icons['nd.pipe_extrude'])
            has_mod_pipe_extrude = True
            replay_prediction_count += 1

        if has_mod_screw:
            layout.operator("nd.screw", icon=icons['nd.screw'])
            replay_prediction_count += 1

        if has_mod_array_cubed:
            layout.operator("nd.array_cubed", icon=icons['nd.array_cubed'])
            replay_prediction_count += 1

        if has_mod_circular_array:
            layout.operator("nd.circular_array", icon=icons['nd.circular_array'])
            replay_prediction_count += 1

        if has_mod_recon_poly:
            layout.operator("nd.recon_poly", icon=icons['nd.recon_poly'])
            replay_prediction_count += 1

        if has_mod_circularize:
            layout.operator("nd.circularize", icon=icons['nd.circularize'])
            replay_prediction_count += 1

        if target_object.display_type == 'WIRE' and "Bool —" in target_object.name:
            layout.operator("nd.mirror", icon=icons['nd.mirror'])
            layout.separator()
            layout.operator("nd.hydrate", icon=icons['nd.hydrate'])
            layout.operator("nd.swap_solver", text="Swap Solver (Booleans)", icon=icons['nd.swap_solver'])

            return SECTION_COUNT

        if was_profile_extrude or self.sketch:
            layout.operator("nd.solidify", icon=icons['nd.solidify']) if not has_mod_solidify else None
            layout.operator("nd.circularize", icon=icons['nd.circularize']) if not has_mod_circularize else None
            layout.separator()
            layout.operator("nd.mirror", icon=icons['nd.mirror'])
            layout.operator("nd.screw", icon=icons['nd.screw']) if not has_mod_screw else None

            return SECTION_COUNT

        if self.profile:
            layout.operator("nd.profile_extrude", icon=icons['nd.profile_extrude']) if not has_mod_profile_extrude else None
            layout.operator("nd.pipe_extrude", icon=icons['nd.pipe_extrude']) if not has_mod_profile_extrude else None
            layout.operator("nd.screw", icon=icons['nd.screw']) if not has_mod_screw else None
            layout.operator("nd.mirror", icon=icons['nd.mirror'])

            return SECTION_COUNT

        if self.has_faces:
            layout.separator()
            layout.operator("nd.bevel", icon=icons['nd.bevel'])
            layout.separator()
            layout.operator("nd.array_cubed", icon=icons['nd.array_cubed']) if not has_mod_array_cubed else None
            layout.operator("nd.circular_array", icon=icons['nd.circular_array']) if not has_mod_circular_array else None
            layout.operator("nd.mirror", icon=icons['nd.mirror'])
            layout.separator()
            layout.operator("nd.panel", icon=icons['nd.panel'])
            layout.operator("nd.geo_lift", icon=icons['nd.geo_lift'])
            layout.operator("nd.view_align", icon=icons['nd.view_align'])
            layout.separator()
            layout.operator("nd.smooth", icon=icons['nd.smooth'])
            layout.operator("nd.wn", icon=icons['nd.wn'])

            return SECTION_COUNT

        return NO_SECTION_COUNT + replay_prediction_count


    def draw_many_object_predictions(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        obj_names = [obj.name for obj in context.selected_objects]
        if all(["Bool —" in name for name in obj_names]):
            layout.operator("nd.hydrate", icon=icons['nd.hydrate'])
            layout.operator("nd.swap_solver", text="Swap Solver (Booleans)", icon=icons['nd.swap_solver'])

            return SECTION_COUNT

        layout.operator("nd.mirror", icon=icons['nd.mirror'])
        layout.operator("nd.triangulate", icon=icons['nd.triangulate'])
        layout.separator()
        layout.operator("nd.name_sync", icon=icons['nd.name_sync'])
        layout.operator("nd.set_lod_suffix", text="Low LOD", icon=icons['nd.set_lod_suffix+LOW']).mode = 'LOW'
        layout.operator("nd.set_lod_suffix", text="High LOD", icon=icons['nd.set_lod_suffix+HIGH']).mode = 'HIGH'
        layout.separator()
        layout.operator("nd.smooth", icon=icons['nd.smooth'])
        layout.operator("nd.wn", icon=icons['nd.wn'])

        return SECTION_COUNT


def register():
    bpy.utils.register_class(ND_MT_fast_menu)

    for mapping in [('Mesh', 'EMPTY'), ('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])
        entry = keymap.keymap_items.new("wm.call_menu", 'F', 'PRESS')
        entry.properties.name = "ND_MT_fast_menu"
        keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_MT_fast_menu)
