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


class ND_OT_apply_modifiers(bpy.types.Operator):
    bl_idname = "nd.apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = """Prepare the selected object(s) for destructive operations by applying applicable modifiers
SHIFT — Hard apply (apply all modifiers)"""
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) > 0:
            return all([obj.type == 'MESH' for obj in context.selected_objects])


    def execute(self, context):
        bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)

        for obj in context.selected_objects:
            self.collapse_modifiers(obj)
            self.remove_vertex_groups(obj)
            self.remove_edge_weights(obj)

        return {'FINISHED'}

    
    def invoke(self, context, event):
        self.hard_apply = event.shift

        return self.execute(context)


    def collapse_modifiers(self, obj):
        safe_mod_types = ['WEIGHTED_NORMAL', 'TRIANGULATE', 'NODES']
        
        mods = [mod for mod in obj.modifiers]
        mods_to_apply = []
        mods_to_remove = []

        if self.hard_apply:
            mods_to_apply = [mod.name for mod in mods if mod.show_viewport]
            mods_to_remove = [mod.name for mod in mods if not mod.show_viewport]

        if not self.hard_apply:
            skip_weld = False

            for index, mod in enumerate(mods):
                if mod.type in safe_mod_types:
                    continue

                if "— ND WNB" in mod.name:
                    continue

                if skip_weld and mod.type == 'WELD' and "— ND B" in mod.name:
                    skip_weld = False
                    continue

                if mod.type == 'BEVEL' and mod.affect == 'EDGES' and mod.limit_method == 'ANGLE':
                    if mod.segments > 1 or (mod.segments == 1 and mod.harden_normals):
                        skip_weld = True
                        continue

                if not mod.show_viewport:
                    mods_to_remove.append(mod.name)
                else:
                    mods_to_apply.append(mod.name)

        for mod_name in mods_to_apply:
            try:
                bpy.ops.object.modifier_apply({'object': obj}, modifier=mod_name)
            except:
                # If the modifier is disabled, just remove it.
                bpy.ops.object.modifier_remove({'object': obj}, modifier=mod_name)

        for mod_name in mods_to_remove:
            bpy.ops.object.modifier_remove({'object': obj}, modifier=mod_name)


    def remove_vertex_groups(self, obj):
        vertex_groups = obj.vertex_groups.values()
        for vg in vertex_groups:
            obj.vertex_groups.remove(vg)


    def remove_edge_weights(self, obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        bevel_weight_layer = bm.edges.layers.bevel_weight.verify()

        edges = list(bm.edges)
        for edge in edges:
            edge[bevel_weight_layer] = 0

        bm.to_mesh(obj.data)
        bm.free()


def register():
    bpy.utils.register_class(ND_OT_apply_modifiers)


def unregister():
    bpy.utils.unregister_class(ND_OT_apply_modifiers)
