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
        if context.mode == 'OBJECT' and len(context.selected_objects) == 2:
            a, b = context.selected_objects
            reference_obj = a if a.name != context.active_object.name else b

            return reference_obj.type == 'MESH'
        elif context.mode == 'OBJECT' and len(context.selected_objects) == 1 and context.active_object.type == 'MESH':
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
        if len(context.selected_objects) == 1:
            if event.shift:
                self.revert_faux_origin(context)
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
        print(mods)
        for mod in mods:
            if mod.direction == 'X':
                location.x = mod.strength
            elif mod.direction == 'Y':
                location.y = mod.strength
            elif mod.direction == 'Z':
                location.z = mod.strength

            context.active_object.modifiers.remove(mod)
        
        context.active_object.location = location

    
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
