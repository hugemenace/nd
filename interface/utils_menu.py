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


keys = []


class ND_MT_utils_menu(bpy.types.Menu):
    bl_label = "ND v%s — Utils" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_MT_utils_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.name_sync", icon='FILE_REFRESH')
        layout.operator("nd.set_lod_suffix", text="Low LOD", icon='ALIASED').mode = 'LOW'
        layout.operator("nd.set_lod_suffix", text="High LOD", icon='ANTIALIASED').mode = 'HIGH'
        layout.separator()
        layout.operator("nd.set_origin", icon='TRANSFORM_ORIGINS')
        layout.operator("nd.snap_align", icon='SNAP_ON')
        layout.separator()
        layout.operator("nd.smooth", icon='MOD_SMOOTH')
        layout.operator("nd.seams", icon='UV_DATA')
        layout.operator("nd.clear_vgs", icon='GROUP_VERTEX')
        layout.operator("nd.triangulate", icon='MOD_TRIANGULATE')
        layout.operator("nd.apply_modifiers", icon='ORPHAN_DATA')
        layout.separator()
        layout.operator("nd.hydrate", icon='SHADING_RENDERED')
        layout.operator("nd.swap_solver", text="Swap Solver (Booleans)", icon='CON_OBJECTSOLVER')
        layout.operator("nd.flare", text="Flare (Lighting)", icon='LIGHT_AREA')
        

def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_utils_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_utils_menu)

    for mapping in [('3D View', 'VIEW_3D'), ('Mesh', 'EMPTY'), ('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])
        entry = keymap.keymap_items.new("wm.call_menu", 'T', 'PRESS', alt = True)
        entry.properties.name = "ND_MT_utils_menu"
        keys.append((keymap, entry))
   

def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_MT_utils_menu)
