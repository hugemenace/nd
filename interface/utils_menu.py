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
from . import ops
from . common import render_ops
from .. import bl_info


keys = []


class ND_MT_utils_menu(bpy.types.Menu):
    bl_label = "ND v%s — Utils" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_MT_utils_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        render_ops(ops.util_ops, layout, new_row=False, use_separator=True)
        

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
