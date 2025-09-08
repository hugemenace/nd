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
from .. lib.objects import get_real_active_object
from .. lib.polling import ctx_obj_mode, obj_exists, list_gt, app_minor_version


hard_ignore_list = {
    '__doc__',
    '__module__',
    '__slotnames__',
    '__slots__',
    'bl_rna',
    'custom_profile',
    'execution_time',
    'is_active',
    'is_bind',
    'is_bound',
    'is_cached',
    'is_external',
    'is_override_data',
    'persistent_uid',
    'rna_type',
    'show_expanded',
    'show_in_editmode',
    'show_on_cage',
    'show_render',
    'show_viewport',
    'type',
}

object_ignore_list = {
    'object',
    'offset_object',
}

property_ignore_list = {
    'armature',
    'auxiliary_target',
    'bone_from',
    'bone_to',
    'cache_file',
    'collection',
    'curve',
    'debug_options',
    'delimit',
    'driver',
    'end_cap',
    'face_count',
    'falloff_curve',
    'filepath',
    'grid_name',
    'has_velocity',
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
    'origin',
    'projectors',
    'read_velocity',
    'rim_vertex_group',
    'shell_vertex_group',
    'start_cap',
    'start_position_object',
    'subtarget',
    'target',
    'texture_coords_bone',
    'texture_coords_object',
    'texture',
    'total_levels',
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
SHIFT — Clone the active object's modifiers
CTRL — Remove all drivers (retaining values)
ALT — Override util references on all sync'd objects"""


    def get_valid_objects(self, context, target_object_type):
        if target_object_type == 'MESH':
            return [obj for obj in context.selected_objects if obj.type == 'MESH']

        return [obj for obj in context.selected_objects if obj.type == 'CURVE']


    @classmethod
    def poll(cls, context):
        target_object = get_real_active_object(context)
        if not obj_exists(target_object):
            return False

        target_object_type = target_object.type
        valid_objects = cls.get_valid_objects(cls, context, target_object_type)

        return ctx_obj_mode(context) and list_gt(valid_objects, 0)


    def invoke(self, context, event):
        if context.active_object is None:
            self.report({'INFO'}, "No active target object selected.")
            return {'CANCELLED'}

        valid_objects = self.get_valid_objects(context, context.active_object.type)

        self.master_object = context.active_object
        self.copy_objects = [obj for obj in valid_objects if obj != self.master_object]

        self.clone = event.shift
        self.clear_drivers = event.ctrl
        self.override_utils = event.alt

        if not self.clear_drivers and len(valid_objects) == 1:
            self.report({'INFO'}, "At least two objects need to be selected in order to sync modifiers.")
            return {'CANCELLED'}

        if self.clear_drivers:
            for obj in valid_objects:
                for mod in obj.modifiers:
                    mod_props = inspect.getmembers(mod, lambda a: not(inspect.isroutine(a)))
                    for prop in mod_props:
                        try:
                            mod.driver_remove(prop[0])
                        except:
                            pass

                    if mod.type == 'NODES':
                        key_table = self.build_gn_key_table(mod)
                        for key in key_table:
                            try:
                                mod.driver_remove(f'["{key}"]')
                            except:
                                pass

                obj.data.update()

            return {'FINISHED'}

        if self.clone:
            for obj in self.copy_objects:
                obj.modifiers.clear()

        pinned_mods = []
        for master_modifier in self.master_object.modifiers:
            for obj in self.copy_objects:
                mod = None
                new_mod = False

                if self.clone:
                    mod = obj.modifiers.new(master_modifier.name, master_modifier.type)
                    new_mod = True
                else:
                    mod = obj.modifiers.get(master_modifier.name)

                if mod is None:
                    continue

                if mod.type != master_modifier.type:
                    continue

                if master_modifier.type == 'NODES':
                    self.sync_node_group(master_modifier, mod)
                else:
                    self.sync_vanilla_mod(master_modifier, mod)

                if new_mod and app_minor_version() >= (4, 2) and master_modifier.use_pin_to_last:
                    pinned_mods.append(mod)

        for mod in pinned_mods:
            mod.use_pin_to_last = True

        return {'FINISHED'}


    def build_gn_key_table(self, mod):
        # Build a dictionary of all the properties and their optional attributes to more
        # effectively sync them as drivers cannot be added to properties with use_attribute set.
        keys = list(mod.keys())
        key_table = dict()
        for key in keys:
            if not key.endswith("_use_attribute") and not key.endswith("_attribute_name"):
                key_table[key] = {}
                key_table[key]["value"] = mod[key]
            if key.endswith("_use_attribute"):
                key_table[key[:-14]]["_use_attribute"] = mod[key]
            if key.endswith("_attribute_name"):
                key_table[key[:-15]]["_attribute_name"] = mod[key]

        return key_table


    def sync_node_group(self, master_modifier, mod):
        mod.node_group = master_modifier.node_group
        mod.show_group_selector = master_modifier.show_group_selector

        key_table = self.build_gn_key_table(master_modifier)

        for key in key_table:
            mod[key] = key_table[key]["value"]

            if "_use_attribute" in key_table[key]:
                use_attribute = key_table[key]["_use_attribute"]
                mod[key + "_use_attribute"] = bool(use_attribute)
                if not use_attribute:
                    self.create_gnmod_driver(master_modifier, mod, key)

            if "_attribute_name" in key_table[key]:
                mod[key + "_attribute_name"] = key_table[key]["_attribute_name"]


    def sync_vanilla_mod(self, master_modifier, mod):
        mod_props = inspect.getmembers(master_modifier, lambda a: not(inspect.isroutine(a)))
        mod_props = [prop for prop in mod_props if not(prop[0] in hard_ignore_list)]

        for prop in mod_props:
            try:
                obj_key = prop[0] in object_ignore_list
                if not obj_key or (obj_key and self.override_utils):
                    setattr(mod, prop[0], prop[1])
            except:
                pass

            if not prop[0] in property_ignore_list:
                self.create_vmod_driver(master_modifier, mod, prop[0])


    def create_vmod_driver(self, master_mod, copy_mod, prop):
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


    def create_gnmod_driver(self, master_mod, copy_mod, prop):
        try:
            driver = copy_mod.driver_add(f'["{prop}"]')
            var = driver.driver.variables.new()
            var.name = prop
            var.targets[0].data_path = f'modifiers["{master_mod.name}"]["{prop}"]'
            var.targets[0].id_type = 'OBJECT'
            var.targets[0].id = self.master_object
            driver.driver.expression = prop
        except:
            pass


def register():
    bpy.utils.register_class(ND_OT_sync_modifiers)


def unregister():
    bpy.utils.unregister_class(ND_OT_sync_modifiers)
