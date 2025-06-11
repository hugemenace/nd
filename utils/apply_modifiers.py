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
from .. lib.polling import ctx_obj_mode, list_ok, app_minor_version


class ND_OT_apply_modifiers(bpy.types.Operator):
    bl_idname = "nd.apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = """Prepare the selected object(s) for destructive operations by applying applicable modifiers
SHIFT — Hard apply (apply all modifiers)
ALT — Duplicate mesh before applying modifiers"""
    bl_options = {'UNDO'}


    def get_valid_objects(self, context):
        return [obj for obj in context.selected_objects if obj.type in {'MESH', 'CURVE'}]


    @classmethod
    def poll(cls, context):
        valid_objects = cls.get_valid_objects(cls, context)
        return ctx_obj_mode(context) and list_ok(valid_objects)


    def execute(self, context):
        valid_objects = self.get_valid_objects(context)

        bpy.ops.object.select_all(action='DESELECT')
        for obj in valid_objects:
            obj.select_set(True)

        if self.duplicate:
            bpy.ops.object.duplicate()
            valid_objects = context.selected_objects.copy()

        bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)

        mesh_objects = [obj for obj in valid_objects if obj.type == 'MESH']
        for obj in mesh_objects:
            self.collapse_modifiers(obj)
            self.remove_vertex_groups(obj)
            self.remove_edge_weights(obj)

        curve_objects = [obj for obj in valid_objects if obj.type == 'CURVE']
        if len(curve_objects) > 0:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in curve_objects:
                obj.select_set(True)
            bpy.ops.object.convert(target='MESH')

        bpy.ops.object.select_all(action='DESELECT')
        for obj in valid_objects:
            obj.select_set(True)

        return {'FINISHED'}


    def invoke(self, context, event):
        self.hard_apply = event.shift
        self.duplicate = event.alt

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
                if app_minor_version() < (4, 0):
                    bpy.ops.object.modifier_apply({'object': obj}, modifier=mod_name)
                else:
                    with bpy.context.temp_override(object=obj):
                        bpy.ops.object.modifier_apply(modifier=mod_name)
            except:
                # If the modifier is disabled, just remove it.
                if app_minor_version() < (4, 0):
                    bpy.ops.object.modifier_remove({'object': obj}, modifier=mod_name)
                else:
                    with bpy.context.temp_override(object=obj):
                        bpy.ops.object.modifier_remove(modifier=mod_name)

        for mod_name in mods_to_remove:
            if app_minor_version() < (4, 0):
                bpy.ops.object.modifier_remove({'object': obj}, modifier=mod_name)
            else:
                with bpy.context.temp_override(object=obj):
                    bpy.ops.object.modifier_remove(modifier=mod_name)


    def remove_vertex_groups(self, obj):
        vertex_groups = obj.vertex_groups.values()
        for vg in vertex_groups:
            if not vg.name.startswith("ND —"):
                continue
            obj.vertex_groups.remove(vg)


    def remove_edge_weights(self, obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        bevel_weight_layer = None

        if app_minor_version() < (4, 0):
            bevel_weight_layer = bm.edges.layers.bevel_weight.verify()
        else:
            bevel_weight_layer = bm.edges.layers.float.get("bevel_weight_edge", None)

        if bevel_weight_layer is not None:
            edges = list(bm.edges)
            for edge in edges:
                edge[bevel_weight_layer] = 0

        bm.to_mesh(obj.data)
        bm.free()


def register():
    bpy.utils.register_class(ND_OT_apply_modifiers)


def unregister():
    bpy.utils.unregister_class(ND_OT_apply_modifiers)
