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
