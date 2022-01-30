import bpy
from .. import bl_info


class ND_PT_utils_ui_panel(bpy.types.Panel):
    bl_label = "ND v%s — Utils" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_PT_utils_ui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HugeMenace"


    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Scene Management", icon='SCENE_DATA')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.name_sync", icon='FILE_REFRESH')

        
def register():
    bpy.utils.register_class(ND_PT_utils_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_utils_ui_panel)
