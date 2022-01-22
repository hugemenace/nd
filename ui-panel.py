import bpy


class NDPanel(bpy.types.Panel):
    bl_label = "ND"
    bl_idname = "PT_nd"
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
        
        
def register():
    bpy.utils.register_class(NDPanel)


def unregister():
    bpy.utils.unregister_class(NDPanel)


if __name__ == "__main__":
    register()
