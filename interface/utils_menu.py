import bpy
from .. import bl_info


class ND_MT_utils_menu(bpy.types.Menu):
    bl_label = "Utils"
    bl_idname = "ND_MT_utils_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.name_sync", icon='FILE_REFRESH')
        layout.operator("nd.set_lod_suffix", text="Low LOD", icon='ALIASED').suffix = 'LOW'
        layout.operator("nd.set_lod_suffix", text="High LOD", icon='ANTIALIASED').suffix = 'HIGH'
        layout.separator()
        layout.operator("nd.set_origin", icon='TRANSFORM_ORIGINS')
        


def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_utils_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_utils_menu)
    bpy.types.INFO_HT_header.append(draw_item)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_utils_menu)
    bpy.types.INFO_HT_header.remove(draw_item)
