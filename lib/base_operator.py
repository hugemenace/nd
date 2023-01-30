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
from . preferences import is_scene_compatible, get_scene_unit_factor, get_scene_unit_suffix


class BaseOperator(bpy.types.Operator):
    bl_options = {'UNDO'}


    def invoke(self, context, event):
        self.unit_factor = get_scene_unit_factor()
        self.unit_suffix = get_scene_unit_suffix()

        return self.do_invoke(context, event)
