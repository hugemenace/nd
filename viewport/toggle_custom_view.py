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


class ND_OT_toggle_custom_view(bpy.types.Operator):
    bl_idname = "nd.toggle_custom_view"
    bl_label = "Overlays (Custom)"
    bl_description = "Toggle the visibility of all overlays defined in the addon preferences"


    def execute(self, context):
        self.overlay_options = ["show_annotation", "show_axis_x", "show_axis_y", "show_axis_z",
        "show_bones", "show_cursor", "show_extras", "show_floor",
        "show_motion_paths", "show_object_origins", "show_object_origins_all", "show_ortho_grid",
        "show_outline_selected", "show_relationship_lines", "show_stats", "show_text"]

        self.prefs = get_preferences()
        self.pref_keys = list(self.prefs.keys())
        self.overlay = bpy.context.space_data.overlay

        if not bpy.context.space_data.overlay.show_overlays:
            return self.handle_recovery_mode()

        return self.handle_standard_mode()
    

    def handle_standard_mode(self):
        bpy.context.space_data.overlay.show_overlays = True

        toggle = any([not "overlay_" + option in self.pref_keys and getattr(self.overlay, option) for option in self.overlay_options])
        for option in self.overlay_options:
            pref_option = "overlay_" + option
            if pref_option in self.pref_keys:
                setattr(self.overlay, option, self.prefs[pref_option])
            else:
                setattr(self.overlay, option, not toggle)

        return {'FINISHED'}


    def handle_recovery_mode(self):
        bpy.context.space_data.overlay.show_overlays = True

        for option in self.overlay_options:
            pref_option = "overlay_" + option
            if pref_option in self.pref_keys:
                setattr(self.overlay, option, self.prefs[pref_option])
            else:
                setattr(self.overlay, option, False)
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_toggle_custom_view)


def unregister():
    bpy.utils.unregister_class(ND_OT_toggle_custom_view)
