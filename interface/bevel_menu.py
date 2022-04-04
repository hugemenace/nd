import bpy
from .. import bl_info


class ND_MT_bevel_menu(bpy.types.Menu):
    bl_label = "Bevels"
    bl_idname = "ND_MT_bevel_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.vertex_bevel", icon='MOD_BEVEL')
        layout.operator("nd.bevel", icon='MOD_BEVEL')
        layout.operator("nd.weighted_normal_bevel", icon='MOD_BEVEL')
        

def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_bevel_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_bevel_menu)
    bpy.types.INFO_HT_header.append(draw_item)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_bevel_menu)
    bpy.types.INFO_HT_header.remove(draw_item)
