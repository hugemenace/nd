import bpy
from . import bl_info


class ND_PT_ui_panel(bpy.types.Panel):
    bl_label = "ND v%s" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "nd.ui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HugeMenace"

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Documentation", icon='INFO')
        column = box.column()
        
        row = column.row(align=True)
        row.scale_y = 1.5
        row.operator("wm.url_open", text="Website", icon='HOME').url = "https://hugemenace.co"
        row.operator("wm.url_open", text="YouTube", icon='FILE_MOVIE').url = "https://www.youtube.com/channel/UCS9HsDPcaWQbo-4Brd7Yjmg"

        box = layout.box()
        box.label(text="Bevels", icon='MOD_BEVEL')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.sketch_bevel")
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.faux_bevel")
        
        box = layout.box()
        box.label(text="Generators", icon='GHOST_ENABLED')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.bolt")

        box = layout.box()
        box.label(text="Utilities", icon='ASSET_MANAGER')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.new_sketch", icon='IMAGE_RGB_ALPHA')
        
        
def register():
    bpy.utils.register_class(ND_PT_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_ui_panel)


if __name__ == "__main__":
    register()
