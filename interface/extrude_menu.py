import bpy
from .. import bl_info


class ND_MT_extrude_menu(bpy.types.Menu):
    bl_label = "Extrusion"
    bl_idname = "ND_MT_extrude_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.solidify", icon='MOD_SOLIDIFY')
        layout.operator("nd.screw", icon='MOD_SCREW')
        layout.operator("nd.profile_extrude", icon='EMPTY_SINGLE_ARROW')
        

def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_extrude_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_extrude_menu)
    bpy.types.INFO_HT_header.append(draw_item)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_extrude_menu)
    bpy.types.INFO_HT_header.remove(draw_item)
