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
from mathutils import Vector
from .. lib.objects import set_origin
from .. lib.modifiers import new_modifier


class ND_OT_set_origin(bpy.types.Operator):
    bl_idname = "nd.set_origin"
    bl_label = "Set Origin"
    bl_description = """Set the origin of the active object to that of another
ALT — Use faux origin translation (for origin-reliant geometry)
SHIFT — Undo faux origin translation"""
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) == 2 and context.active_object is not None:
            a, b = context.selected_objects
            reference_obj = a if a.name != context.active_object.name else b

            return reference_obj.type == 'MESH'
        elif context.mode == 'OBJECT' and len(context.selected_objects) == 1 and context.active_object is not None and context.active_object.type == 'MESH':
            return True
        elif context.mode == 'EDIT_MESH' and len(context.selected_objects) == 1:
            return True


    def execute(self, context):
        a, b = context.selected_objects
        reference_obj = a if a.name != context.active_object.name else b

        (x_dest, y_dest, z_dest) = reference_obj.location
        (x_orig, y_orig, z_orig) = context.active_object.location

        reference_obj.location = context.active_object.location

        self.add_displace_modifier(reference_obj, 'X', x_dest - x_orig)
        self.add_displace_modifier(reference_obj, 'Y', y_dest - y_orig)
        self.add_displace_modifier(reference_obj, 'Z', z_dest - z_orig)

        return {'FINISHED'}


    def invoke(self, context, event):
        if context.active_object is None:
            self.report({'ERROR_INVALID_INPUT'}, "No active target object selected.")
            return {'CANCELLED'}

        if len(context.selected_objects) == 1:
            if event.shift:
                self.revert_faux_origin(context)
            if context.mode == 'EDIT_MESH':
                self.set_mesh_origin(context)
        else:
            if event.alt:
                return self.execute(context)
            else:
                a, b = context.selected_objects
                reference_obj = a if a.name != context.active_object.name else b

                mx = context.active_object.matrix_world
                set_origin(reference_obj, mx)

        return {'FINISHED'}


    def revert_faux_origin(self, context):
        location = context.active_object.location.copy()

        mods = [mod for mod in context.active_object.modifiers if mod.type == 'DISPLACE' and mod.name.endswith('— ND FO')]
        for mod in mods:
            if mod.direction == 'X':
                location.x = mod.strength
            elif mod.direction == 'Y':
                location.y = mod.strength
            elif mod.direction == 'Z':
                location.z = mod.strength

            context.active_object.modifiers.remove(mod)

        context.active_object.location = location


    def set_mesh_origin(self, context):
        cursor_location = bpy.context.scene.cursor.location.copy()
        cursor_rotation = bpy.context.scene.cursor.rotation_euler.copy()

        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.context.scene.cursor.location = cursor_location
        bpy.context.scene.cursor.rotation_euler = cursor_rotation


    def add_displace_modifier(self, reference_obj, axis, strength):
        displace = new_modifier(reference_obj, "Translate {} — ND FO".format(axis), 'DISPLACE', rectify=False)
        displace.direction = axis
        displace.space = 'GLOBAL'
        displace.mid_level = 0
        displace.strength = strength


def register():
    bpy.utils.register_class(ND_OT_set_origin)


def unregister():
    bpy.utils.unregister_class(ND_OT_set_origin)
