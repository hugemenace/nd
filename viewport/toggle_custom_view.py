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
from .. lib.preferences import get_preferences


class ND_OT_toggle_custom_view(bpy.types.Operator):
    bl_idname = "nd.toggle_custom_view"
    bl_label = "Overlays (Custom)"
    bl_description = "Toggle the visibility of all overlays defined in the addon preferences"


    def execute(self, context):
        self.prefs = get_preferences()
        self.overlay = bpy.context.space_data.overlay

        if not bpy.context.space_data.overlay.show_overlays:
            return self.handle_recovery_mode()

        return self.handle_standard_mode()


    def handle_standard_mode(self):
        bpy.context.space_data.overlay.show_overlays = True

        self.overlay.show_annotation = self.prefs.overlay_show_annotation or not self.overlay.show_annotation
        self.overlay.show_axis_x = self.prefs.overlay_show_axis_x or not self.overlay.show_axis_x
        self.overlay.show_axis_y = self.prefs.overlay_show_axis_y or not self.overlay.show_axis_y
        self.overlay.show_axis_z = self.prefs.overlay_show_axis_z or not self.overlay.show_axis_z
        self.overlay.show_bones = self.prefs.overlay_show_bones or not self.overlay.show_bones
        self.overlay.show_cursor = self.prefs.overlay_show_cursor or not self.overlay.show_cursor
        self.overlay.show_extras = self.prefs.overlay_show_extras or not self.overlay.show_extras
        self.overlay.show_floor = self.prefs.overlay_show_floor or not self.overlay.show_floor
        self.overlay.show_motion_paths = self.prefs.overlay_show_motion_paths or not self.overlay.show_motion_paths
        self.overlay.show_object_origins = self.prefs.overlay_show_object_origins or not self.overlay.show_object_origins
        self.overlay.show_object_origins_all = self.prefs.overlay_show_object_origins_all or not self.overlay.show_object_origins_all
        self.overlay.show_ortho_grid = self.prefs.overlay_show_ortho_grid or not self.overlay.show_ortho_grid
        self.overlay.show_outline_selected = self.prefs.overlay_show_outline_selected or not self.overlay.show_outline_selected
        self.overlay.show_relationship_lines = self.prefs.overlay_show_relationship_lines or not self.overlay.show_relationship_lines
        self.overlay.show_stats = self.prefs.overlay_show_stats or not self.overlay.show_stats
        self.overlay.show_text = self.prefs.overlay_show_text or not self.overlay.show_text

        return {'FINISHED'}


    def handle_recovery_mode(self):
        bpy.context.space_data.overlay.show_overlays = True

        self.overlay.show_annotation = self.prefs.overlay_show_annotation
        self.overlay.show_axis_x = self.prefs.overlay_show_axis_x
        self.overlay.show_axis_y = self.prefs.overlay_show_axis_y
        self.overlay.show_axis_z = self.prefs.overlay_show_axis_z
        self.overlay.show_bones = self.prefs.overlay_show_bones
        self.overlay.show_cursor = self.prefs.overlay_show_cursor
        self.overlay.show_extras = self.prefs.overlay_show_extras
        self.overlay.show_floor = self.prefs.overlay_show_floor
        self.overlay.show_motion_paths = self.prefs.overlay_show_motion_paths
        self.overlay.show_object_origins = self.prefs.overlay_show_object_origins
        self.overlay.show_object_origins_all = self.prefs.overlay_show_object_origins_all
        self.overlay.show_ortho_grid = self.prefs.overlay_show_ortho_grid
        self.overlay.show_outline_selected = self.prefs.overlay_show_outline_selected
        self.overlay.show_relationship_lines = self.prefs.overlay_show_relationship_lines
        self.overlay.show_stats = self.prefs.overlay_show_stats
        self.overlay.show_text = self.prefs.overlay_show_text

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_toggle_custom_view)


def unregister():
    bpy.utils.unregister_class(ND_OT_toggle_custom_view)
