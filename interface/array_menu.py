import bpy
from .. import bl_info


class ND_MT_array_menu(bpy.types.Menu):
    bl_label = "Arrays"
    bl_idname = "ND_MT_array_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.circular_array", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        layout.operator("nd.square_array", icon='LIGHTPROBE_GRID')
        

def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_array_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_array_menu)
    bpy.types.INFO_HT_header.append(draw_item)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_array_menu)
    bpy.types.INFO_HT_header.remove(draw_item)
