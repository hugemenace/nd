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


keys = []


class ND_MT_sketch_menu(bpy.types.Menu):
    bl_label = "Sketch — ND v%s" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_MT_sketch_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        render_ops(ops.sketch_ops, layout, new_row=False, use_separator=True)

        if context.mode == 'OBJECT':
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.separator()

            layout.operator("object.scale_clear", text="S » Clear Scale", icon='DRIVER_DISTANCE')

        if context.mode == 'EDIT_MESH':
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.separator()

            layout.operator("transform.shrink_fatten", text="S » Shrink/Fatten", icon='FACESEL')


def register():
    bpy.utils.register_class(ND_MT_sketch_menu)

    for mapping in [('Mesh', 'EMPTY'), ('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])
        entry = keymap.keymap_items.new("wm.call_menu", 'S', 'PRESS', alt=True)
        entry.properties.name = "ND_MT_sketch_menu"
        keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_MT_sketch_menu)
