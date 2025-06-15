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
from .. lib.collections import isolate_utils, get_util_objects_for
from .. lib.polling import ctx_obj_mode, list_ok


keys = []


class ND_OT_smart_duplicate(bpy.types.Operator):
    bl_idname = "nd.smart_duplicate"
    bl_label = "Smart Duplicate"
    bl_description = """Duplicate the selected objects with their utils
SHIFT — Deep duplicate (includes children)"""


    hotkeyed: bpy.props.BoolProperty(
        name="Hotkeyed",
        description="Indicates if this operator was invoked via a hotkey",
        default=False
    )

    mode: bpy.props.EnumProperty(items=[
        ('DUPLICATE', 'Duplicate', 'Perform a duplicate operation'),
        ('LINKED', 'Linked', 'Perform a linked duplicate operation'),
    ], name="Mode", default='DUPLICATE')

    deep: bpy.props.BoolProperty(
        name="Deep Duplicate",
        description="Include children of selected objects in the duplication",
        default=False
    )


    @classmethod
    def poll(cls, context):
        return ctx_obj_mode(context) and list_ok(context.selected_objects)


    def perform_duplicate(self, context):
        if self.mode == 'LINKED':
            bpy.ops.object.duplicate_move_linked('INVOKE_DEFAULT')
        else:
            bpy.ops.object.duplicate_move('INVOKE_DEFAULT')


    def invoke(self, context, event):
        deep_duplicate = (not self.hotkeyed and event.shift) or self.deep
        util_objects = get_util_objects_for(context.selected_objects, include_children=deep_duplicate)
        isolate_utils(util_objects)

        for obj in util_objects:
            obj.select_set(True)

        if deep_duplicate:
            for obj in context.selected_objects:
                child_objects = list(obj.children_recursive)
                for child in child_objects:
                    if child not in util_objects:
                        child.select_set(True)

        self.perform_duplicate(context)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ND_OT_smart_duplicate)

    for mapping in [('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])

        entry = keymap.keymap_items.new("nd.smart_duplicate", 'D', 'PRESS', shift=True, alt=True)
        entry.properties.mode = "DUPLICATE"
        entry.properties.deep = False
        entry.properties.hotkeyed = True
        keys.append((keymap, entry))

        entry = keymap.keymap_items.new("nd.smart_duplicate", 'D', 'PRESS', shift=True, ctrl=True, alt=True)
        entry.properties.mode = "DUPLICATE"
        entry.properties.deep = True
        entry.properties.hotkeyed = True
        keys.append((keymap, entry))

        entry = keymap.keymap_items.new("nd.smart_duplicate", 'S', 'PRESS', shift=True, alt=True)
        entry.properties.mode = "LINKED"
        entry.properties.deep = False
        entry.properties.hotkeyed = True
        keys.append((keymap, entry))

        entry = keymap.keymap_items.new("nd.smart_duplicate", 'S', 'PRESS', shift=True, ctrl=True, alt=True)
        entry.properties.mode = "LINKED"
        entry.properties.deep = True
        entry.properties.hotkeyed = True
        keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_OT_smart_duplicate)
