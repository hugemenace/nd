import bpy
from .. import bl_info
from .. import lib


class ND_PT_main_ui_panel(bpy.types.Panel):
    bl_label = "ND v%s — Core" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_PT_main_ui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HugeMenace"


    def draw(self, context):
        layout = self.layout

        if lib.preferences.get_preferences().update_available:
            box = layout.box()
            column = box.column()
            row = column.row(align=True)
            row.scale_y = 1.5
            row.alert = True
            row.operator("wm.url_open", text="Update Available!", icon='PACKAGE').url = "https://hugemenace.gumroad.com/l/nd-blender-addon"
        
        box = layout.box()
        box.label(text="Documentation", icon='INFO')
        column = box.column()
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("wm.url_open", text="View Online Docs", icon='HOME').url = "https://docs.nd.hugemenace.co"
        # TODO: Re-enable this when the YouTube channel is ready
        # row.operator("wm.url_open", text="YouTube", icon='FILE_MOVIE').url = "https://www.youtube.com/watch?v=bg4qpt2hkHg&list=PLZmp_NXXf0kDj5wSa3VpftsNx62YNXEc6"

        box = layout.box()
        box.label(text="Sketching", icon='GREASEPENCIL')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.geo_lift", icon='FACESEL')
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.view_align", icon='ORIENTATION_VIEW')

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
        row.operator("nd.bool_vanilla", text="Difference", icon='MOD_BOOLEAN').mode = 'DIFFERENCE'
        row.operator("nd.bool_vanilla", text="Union", icon='MOD_BOOLEAN').mode = 'UNION'

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.bool_vanilla", text="Intersect", icon='MOD_BOOLEAN').mode = 'INTERSECT'
        row.operator("nd.bool_slice", icon='MOD_BOOLEAN')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.weighted_normal_bevel", icon='MOD_BEVEL')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.solidify", icon='MOD_SOLIDIFY')
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.screw", icon='MOD_SCREW')
        
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.mirror", icon='MOD_MIRROR')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.profile_extrude", icon='EMPTY_SINGLE_ARROW')

        box = layout.box()
        box.label(text="Generators", icon='GHOST_ENABLED')
        column = box.column()

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.recon_poly", icon='SURFACE_NCURVE')

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("nd.screw_head", icon='CANCEL')
        
        
def register():
    bpy.utils.register_class(ND_PT_main_ui_panel)


def unregister():
    bpy.utils.unregister_class(ND_PT_main_ui_panel)
