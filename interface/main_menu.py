import bpy
from .. import bl_info
from .. import lib


keys = []


class ND_MT_main_menu(bpy.types.Menu):
    bl_label = "ND v%s" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_MT_main_menu"


    def draw(self, context):
        layout = self.layout

        if lib.preferences.get_preferences().update_available:
            layout.operator("wm.url_open", text="Update Available!", icon='PACKAGE').url = "https://hugemenace.gumroad.com/l/nd-blender-addon"
            layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.single_vertex", icon='DOT')
        layout.operator("nd.make_manifold", icon='OUTLINER_DATA_SURFACE')
        layout.operator("nd.view_align", icon='ORIENTATION_VIEW')
        layout.operator("nd.geo_lift", icon='FACESEL')

        if lib.preferences.get_preferences().enable_deprecated_features:
            layout.operator("nd.blank_sketch", icon='GREASEPENCIL')

        layout.separator()
        layout.menu("ND_MT_boolean_menu", icon='MOD_BOOLEAN')
        layout.menu("ND_MT_bevel_menu", icon='MOD_BEVEL')
        layout.menu("ND_MT_extrude_menu", icon='MOD_SOLIDIFY')
        layout.menu("ND_MT_array_menu", icon='MOD_ARRAY')
        layout.operator("nd.mirror", icon='MOD_MIRROR')
        layout.operator("nd.lattice", icon='MOD_LATTICE')
        layout.separator()
        layout.operator("nd.recon_poly", icon='SURFACE_NCURVE')
        layout.operator("nd.screw_head", icon='CANCEL')
        layout.separator()
        layout.menu("ND_MT_utils_menu", icon='PLUGIN')
        layout.menu("ND_MT_viewport_menu", text="Viewport", icon='RESTRICT_VIEW_OFF')

        if lib.preferences.get_preferences().enable_quick_favourites:
            layout.separator()
            layout.menu("SCREEN_MT_user_menu", icon='SOLO_ON')


def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_main_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_main_menu)

    for mapping in [('3D View', 'VIEW_3D'), ('Mesh', 'EMPTY'), ('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])
        entry = keymap.keymap_items.new("wm.call_menu", 'TWO', 'PRESS', shift = True)
        entry.properties.name = "ND_MT_main_menu"
        keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_MT_main_menu)
