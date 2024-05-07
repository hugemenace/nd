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


class ND_OT_reset_theme(bpy.types.Operator):
    bl_idname = "nd.reset_theme"
    bl_label = "Reset ND Theme"
    bl_description = "Reset the ND theme colors back to their original values"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return True


    def execute(self, context):
        # Overlay
        get_preferences().overlay_header_standard_color = (255/255, 135/255, 55/255)
        get_preferences().overlay_header_recalled_color = (82/255, 224/255, 82/255)
        get_preferences().overlay_header_paused_color = (238/255, 59/255, 43/255)
        get_preferences().overlay_option_active_color = (55/255, 174/255, 255/255)
        get_preferences().overlay_base_color = (255/255, 255/255, 255/255)
        get_preferences().overlay_option_manual_override_color = (237/255, 185/255, 94/255)

        # Points
        get_preferences().points_primary_color = (82/255, 224/255, 82/255, 1.0)
        get_preferences().points_secondary_color = (255/255, 135/255, 55/255, 1.0)
        get_preferences().points_tertiary_color = (82/255, 224/255, 82/255, 1.0)
        get_preferences().points_guide_line_color = (82/255, 224/255, 82/255, 0.5)

        # Axis
        get_preferences().axis_x_color = (226/255, 54/255, 54/255)
        get_preferences().axis_y_color = (130/255, 221/255, 85/255)
        get_preferences().axis_z_color = (74/255, 144/255, 226/255)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_reset_theme)


def unregister():
    bpy.utils.unregister_class(ND_OT_reset_theme)
