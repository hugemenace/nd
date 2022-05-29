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
from .. import bl_info


keys = []


class ND_MT_fast_menu(bpy.types.Menu):
    bl_label = "ND v%s — Fast (Predict)" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_MT_fast_menu"


    def draw(self, context):
        objs = context.selected_objects

        if len(objs) == 0:
            return self.draw_no_object_predictions(context)

        if len(objs) == 1:
            return self.draw_single_object_predictions(context)

        if len(objs) == 2:
            return self.draw_two_object_predictions(context)

        if len(objs) > 2:
            return self.draw_many_object_predictions(context)

        return self.draw_no_predictions(context)
    

    def draw_no_predictions(self, context):
        layout = self.layout
        layout.label(text="No predictions available", icon='ZOOM_SELECTED')


    def draw_make_edge_face_ops(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.separator()

        try:
            layout.operator("mesh.f2", text="[F] Make Edge/Face", icon='MOD_SIMPLIFY')
        except:
            layout.operator("mesh.edge_face_add", text="[F] Make Edge/Face", icon='MOD_SIMPLIFY')


    def draw_no_object_predictions(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.operator("nd.single_vertex", icon='DOT')
        layout.operator("nd.recon_poly", icon='SURFACE_NCURVE')
        layout.separator()
        layout.operator("mesh.primitive_plane_add", icon='MESH_PLANE')
        layout.operator("mesh.primitive_cube_add", icon='MESH_CUBE')


    def draw_two_object_predictions(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        obj_names = [obj.name for obj in context.selected_objects]
        if all(["Bool —" in name for name in obj_names]):
            layout.operator("nd.hydrate", icon='SHADING_RENDERED')
            layout.operator("nd.swap_solver", text="Swap Solver (Booleans)", icon='CON_OBJECTSOLVER')

            return

        layout.operator("nd.bool_vanilla", text="Difference", icon='MOD_BOOLEAN').mode = 'DIFFERENCE'
        layout.operator("nd.bool_vanilla", text="Union", icon='MOD_BOOLEAN').mode = 'UNION'
        layout.operator("nd.bool_vanilla", text="Intersect", icon='MOD_BOOLEAN').mode = 'INTERSECT'
        layout.operator("nd.bool_slice", icon='MOD_BOOLEAN')
        layout.operator("nd.bool_inset", icon='MOD_BOOLEAN')
        layout.separator()
        layout.operator("nd.mirror", icon='MOD_MIRROR')
        layout.operator("nd.circular_array", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        layout.operator("nd.snap_align", icon='SNAP_ON')


    def draw_single_object_predictions(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        if context.mode == 'EDIT_MESH':
            mesh = bmesh.from_edit_mesh(context.object.data)

            verts_selected = len([vert for vert in mesh.verts if vert.select]) >= 1
            edges_selected = len([edge for edge in mesh.edges if edge.select]) >= 1

            has_verts = len(mesh.verts) >= 1
            has_edges = len(mesh.edges) >= 1
            has_faces = len(mesh.faces) >= 1

            made_prediction = False

            if verts_selected:
                layout.operator("nd.vertex_bevel", icon='VERTEXSEL')
                layout.operator("nd.clear_vgs", icon='GROUP_VERTEX')
                made_prediction = True
            
            if edges_selected:
                layout.operator("nd.edge_bevel", icon='EDGESEL')
                made_prediction = True

            if has_verts and not has_faces:
                layout.operator("nd.make_manifold", icon='OUTLINER_DATA_SURFACE')
                made_prediction = True

            if verts_selected:
                self.draw_make_edge_face_ops(context)
                made_prediction = True

            if not made_prediction:
                self.draw_no_predictions(context)

            return

        if context.mode == 'OBJECT':
            depsgraph = context.evaluated_depsgraph_get()
            object_eval = context.object.evaluated_get(depsgraph)

            bm = bmesh.new()
            bm.from_mesh(object_eval.data)

            self.verts = [vert for vert in bm.verts]
            self.edges = [edge for edge in bm.edges]
            self.faces = [face for face in bm.faces]
            self.sketch = len(self.faces) == 1
            self.profile = len(self.faces) == 0 and len(self.edges) > 0
            self.form = len(self.faces) > 1

            bm.free()

            mod_names = [mod.name for mod in context.object.modifiers]

            has_mod_pe = False
            has_mod_sol = False 
            has_mod_bool = False

            for name in mod_names:
                has_mod_pe = has_mod_pe or bool("— ND PE" in name)
                has_mod_sol = has_mod_sol or bool("— ND SOL" in name)
                has_mod_bool = has_mod_bool or bool("— ND Bool" in name)

            was_profile_extrude = has_mod_pe and not has_mod_sol

            if has_mod_sol:
                layout.operator("nd.solidify", icon='MOD_SOLIDIFY')

            if has_mod_pe:
                layout.operator("nd.profile_extrude", icon='EMPTY_SINGLE_ARROW')

            if "Bool —" in context.object.name:
                layout.operator("nd.hydrate", icon='SHADING_RENDERED')
                layout.operator("nd.swap_solver", text="Swap Solver (Booleans)", icon='CON_OBJECTSOLVER')

                return

            if was_profile_extrude or self.sketch:
                layout.operator("nd.solidify", icon='MOD_SOLIDIFY')
                layout.separator()
                layout.operator("nd.mirror", icon='MOD_MIRROR')
                layout.operator("nd.screw", icon='MOD_SCREW')

                return
            
            if self.profile:
                layout.operator("nd.profile_extrude", icon='EMPTY_SINGLE_ARROW')
                layout.operator("nd.screw", icon='MOD_SCREW')

                return

            if self.form:
                if has_mod_bool:
                    layout.operator("nd.cycle", icon='LONGDISPLAY')
                    layout.separator()

                layout.operator("nd.bevel", icon='MOD_BEVEL')
                layout.operator("nd.weighted_normal_bevel", icon='MOD_BEVEL')
                layout.separator()
                layout.operator("nd.array_cubed", icon='PARTICLES')
                layout.operator("nd.circular_array", icon='DRIVER_ROTATIONAL_DIFFERENCE')
                layout.operator("nd.mirror", icon='MOD_MIRROR')

                return


    def draw_many_object_predictions(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        obj_names = [obj.name for obj in context.selected_objects]
        if all(["Bool —" in name for name in obj_names]):
            layout.operator("nd.hydrate", icon='SHADING_RENDERED')
            layout.operator("nd.swap_solver", text="Swap Solver (Booleans)", icon='CON_OBJECTSOLVER')

            return

        layout.operator("nd.mirror", icon='MOD_MIRROR')
        layout.operator("nd.triangulate", icon='MOD_TRIANGULATE')
        layout.operator("nd.name_sync", icon='FILE_REFRESH')
        layout.operator("nd.set_lod_suffix", text="Low LOD", icon='ALIASED').mode = 'LOW'
        layout.operator("nd.set_lod_suffix", text="High LOD", icon='ANTIALIASED').mode = 'HIGH'


def register():
    bpy.utils.register_class(ND_MT_fast_menu)

    for mapping in [('3D View', 'VIEW_3D'), ('Mesh', 'EMPTY'), ('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])
        entry = keymap.keymap_items.new("wm.call_menu", 'F', 'PRESS')
        entry.properties.name = "ND_MT_fast_menu"
        keys.append((keymap, entry))
   

def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_MT_fast_menu)
