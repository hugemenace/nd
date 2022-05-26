# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)
# 
# ---
# Contributors: Tristo (HM)
# ---

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
        
        layout.operator("nd.cycle", icon='LONGDISPLAY')
        layout.menu("ND_MT_sketch_menu", text="Sketch", icon='GROUP_UVS')

        layout.separator()
        layout.menu("ND_MT_boolean_menu", icon='MOD_BOOLEAN')
        layout.menu("ND_MT_bevel_menu", icon='MOD_BEVEL')
        layout.menu("ND_MT_extrude_menu", icon='MOD_SOLIDIFY')
        layout.menu("ND_MT_replicate_menu", icon='MOD_ARRAY')
        layout.menu("ND_MT_deform_menu", icon='MOD_SIMPLEDEFORM')
        layout.menu("ND_MT_simplify_menu", icon='MOD_REMESH')
        layout.separator()
        layout.operator("nd.recon_poly", icon='SURFACE_NCURVE')
        layout.operator("nd.screw_head", icon='CANCEL')
        layout.separator()
        layout.menu("ND_MT_utils_menu", text="Utils", icon='PLUGIN')
        layout.menu("ND_MT_viewport_menu", text="Viewport", icon='RESTRICT_VIEW_OFF')

        if lib.preferences.get_preferences().enable_quick_favourites:
            layout.separator()
            layout.menu("SCREEN_MT_user_menu", icon='SOLO_ON')


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
