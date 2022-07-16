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


class ND_OT_toggle_clear_view(bpy.types.Operator):
    bl_idname = "nd.toggle_clear_view"
    bl_label = "Overlays (All)"
    bl_description = "Toggle the visibility of all overlays"


    def execute(self, context):
        bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_toggle_clear_view)


def unregister():
    bpy.utils.unregister_class(ND_OT_toggle_clear_view)
