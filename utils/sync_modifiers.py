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
import inspect


property_ignore_list = {
    '__doc__',
    '__module__',
    '__slotnames__',
    '__slots__',
    'armature',
    'auxiliary_target',
    'bl_rna',
    'bone_from',
    'bone_to',
    'cache_file',
    'collection',
    'curve',
    'custom_profile',
    'debug_options',
    'delimit',
    'driver',
    'end_cap',
    'execution_time',
    'face_count',
    'falloff_curve',
    'filepath',
    'grid_name',
    'has_velocity',
    'is_active',
    'is_bind',
    'is_bound',
    'is_cached',
    'is_external',
    'is_override_data',
    'map_curve',
    'mask_tex_map_bone',
    'mask_tex_map_object',
    'mask_tex_uv_layer',
    'mask_texture',
    'mask_vertex_group',
    'matrix_inverse',
    'mirror_object',
    'name',
    'object_from',
    'object_path',
    'object_to',
    'object',
    'offset_object',
    'origin',
    'persistent_uid',
    'projectors',
    'read_velocity',
    'rim_vertex_group',
    'rna_type',
    'shell_vertex_group',
    'show_expanded',
    'show_in_editmode',
    'show_on_cage',
    'show_render',
    'show_viewport',
    'start_cap',
    'start_position_object',
    'subtarget',
    'target',
    'texture_coords_bone',
    'texture_coords_object',
    'texture',
    'total_levels',
    'type',
    'use_bone_envelopes',
    'use_vertex_groups',
    'uv_layer',
    'vertex_group_a',
    'vertex_group_b',
    'vertex_group',
    'vertex_indices_set',
    'vertex_indices',
    'vertex_velocities',
}


class ND_OT_sync_modifiers(bpy.types.Operator):
    bl_idname = "nd.sync_modifiers"
    bl_label = "Sync Modifiers"
    bl_description = """Sync modifier settings from the active object to the selected objects
SHIFT — Clone the active object's modifiers"""


    def get_valid_objects(self, context, target_object_type):
        if target_object_type == 'MESH':
            return [obj for obj in context.selected_objects if obj.type == 'MESH']

        return [obj for obj in context.selected_objects if obj.type == 'CURVE']


    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False

        target_object_type = context.active_object.type
        valid_objects = cls.get_valid_objects(cls, context, target_object_type)

        return context.mode == 'OBJECT' and len(valid_objects) > 1


    def invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        valid_objects = self.get_valid_objects(context, context.active_object.type)

        self.master_object = context.active_object
        self.copy_objects = [obj for obj in valid_objects if obj != self.master_object]

        self.clone = event.shift

        if self.clone:
            for obj in self.copy_objects:
                obj.modifiers.clear()

        for master_modifier in self.master_object.modifiers:
            for obj in self.copy_objects:
                if master_modifier.type == 'NODES':
                    continue

                mod = None

                if self.clone:
                    mod = obj.modifiers.new(master_modifier.name, master_modifier.type)
                else:
                    mod = obj.modifiers.get(master_modifier.name)

                if mod is None:
                    continue

                if mod.type != master_modifier.type:
                    continue

                mod_props = inspect.getmembers(master_modifier, lambda a: not(inspect.isroutine(a)))
                mod_props = [prop for prop in mod_props if not(prop[0] in property_ignore_list)]

                for prop in mod_props:
                    self.create_driver(master_modifier, mod, prop[0])

        return {'FINISHED'}


    def create_driver(self, master_mod, copy_mod, prop):
        try:
            driver = copy_mod.driver_add(prop)
            var = driver.driver.variables.new()
            var.name = prop
            var.targets[0].data_path = f'modifiers["{master_mod.name}"].{prop}'
            var.targets[0].id_type = 'OBJECT'
            var.targets[0].id = self.master_object
            driver.driver.expression = prop
        except:
            pass


def register():
    bpy.utils.register_class(ND_OT_sync_modifiers)


def unregister():
    bpy.utils.unregister_class(ND_OT_sync_modifiers)
