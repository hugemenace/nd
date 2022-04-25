# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy
from .. import bl_info
from .. import lib


class ND_MT_array_menu(bpy.types.Menu):
    bl_label = "Arrays"
    bl_idname = "ND_MT_array_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.array_cubed", icon='PARTICLES')
        layout.operator("nd.circular_array", icon='DRIVER_ROTATIONAL_DIFFERENCE')

        if lib.preferences.get_preferences().enable_deprecated_features:
            layout.operator("nd.square_array", icon='LIGHTPROBE_GRID')
        

def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_array_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_array_menu)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_array_menu)
