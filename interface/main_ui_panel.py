import bpy
from .. import bl_info


class ND_PT_main_ui_panel(bpy.types.Panel):
    bl_label = "ND v%s" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_PT_main_ui_panel"
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
        row.operator("wm.url_open", text="Website", icon='HOME').url = "https://docs.nd.hugemenace.co"
        row.operator("wm.url_open", text="YouTube", icon='FILE_MOVIE').url = "https://www.youtube.com/channel/UCS9HsDPcaWQbo-4Brd7Yjmg"

        box = layout.box()
        box.label(text="Sketching", icon='GREASEPENCIL')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.face_sketch", icon='FACESEL')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.blank_sketch", icon='GREASEPENCIL')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.vertex_bevel", icon='MOD_BEVEL')

        box = layout.box()
        box.label(text="Power Mods", icon='MODIFIER')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.weighted_normal_bevel", icon='MOD_BEVEL')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.solidify", icon='MOD_SOLIDIFY')
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.screw", icon='MOD_SCREW')

        box = layout.box()
        box.label(text="Generators", icon='GHOST_ENABLED')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.ring_and_bolt", icon='MESH_CYLINDER')
        
        
def register():
    bpy.utils.register_class(ND_PT_main_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_main_ui_panel)
