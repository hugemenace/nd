# ███╗   ██╗██████╗
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝
#
# ND (Non-Destructive) Blender Add-on
# Copyright (C) 2024 Tristan S. & Ian J. (HugeMenace)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ---
# Contributors: Tristo (HM)
# ---

import bpy
from . import ops
from . common import render_ops
from .. __init__ import bl_info
from .. import lib


keys = []


class ND_MT_main_menu(bpy.types.Menu):
    bl_label = "ND v%s" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_MT_main_menu"


    def draw(self, context):
        layout = self.layout

        if not lib.addons.is_extension() and lib.preferences.get_preferences().update_available:
            layout.operator("wm.url_open", text="Update Available!", icon='PACKAGE').url = "https://hugemenace.gumroad.com/l/nd-blender-addon"
            layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'

        render_ops(ops.standalone_ops, layout, new_row=False, use_separator=True)

        layout.menu("ND_MT_sketch_menu", text="Sketch", icon='GROUP_UVS')
        layout.separator()
        layout.menu("ND_MT_boolean_menu", icon='MOD_BOOLEAN')
        layout.menu("ND_MT_bevel_menu", icon='MOD_BEVEL')
        layout.menu("ND_MT_extrude_menu", icon='MOD_SOLIDIFY')
        layout.menu("ND_MT_replicate_menu", icon='MOD_ARRAY')
        layout.menu("ND_MT_deform_menu", icon='MOD_SIMPLEDEFORM')
        layout.menu("ND_MT_simplify_menu", icon='MOD_REMESH')
        layout.separator()
        layout.menu("ND_MT_shading_menu", icon='SHADING_RENDERED')
        layout.menu("ND_MT_scene_menu", icon='SCENE_DATA')
        layout.separator()
        layout.menu("ND_MT_packaging_menu", text="Packaging", icon='OUTLINER_COLLECTION')
        layout.menu("ND_MT_utils_menu", text="Utils", icon='PLUGIN')
        layout.menu("ND_MT_viewport_menu", text="Viewport", icon='RESTRICT_VIEW_OFF')

        if lib.preferences.get_preferences().enable_quick_favourites:
            layout.separator()
            layout.menu("SCREEN_MT_user_menu", icon='SOLO_ON')


def register():
    bpy.utils.register_class(ND_MT_main_menu)

    for mapping in [('Mesh', 'EMPTY'), ('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])
        entry = keymap.keymap_items.new("wm.call_menu", 'TWO', 'PRESS', shift = True)
        entry.properties.name = "ND_MT_main_menu"
        keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_MT_main_menu)
