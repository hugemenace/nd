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


class ND_OT_set_origin(bpy.types.Operator):
    bl_idname = "nd.set_origin"
    bl_label = "Set Origin"
    bl_description = """Set the origin of the active object to that of another
ALT — Use faux origin translation (for origin-reliant geometry)"""
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT' and len(context.selected_objects) == 2:
            a, b = context.selected_objects
            reference_obj = a if a.name != context.object.name else b

            return reference_obj.type == 'MESH'


    def execute(self, context):
        a, b = context.selected_objects
        reference_obj = a if a.name != context.object.name else b
        
        (x_dest, y_dest, z_dest) = reference_obj.location
        (x_orig, y_orig, z_orig) = context.object.location

        reference_obj.location = context.object.location

        self.add_displace_modifier(reference_obj, 'X', x_dest - x_orig)
        self.add_displace_modifier(reference_obj, 'Y', y_dest - y_orig)
        self.add_displace_modifier(reference_obj, 'Z', z_dest - z_orig)

        return {'FINISHED'}

    
    def invoke(self, context, event):
        if event.alt:
            return self.execute(context)
        else:
            a, b = context.selected_objects
            reference_obj = a if a.name != context.object.name else b

            mx = context.object.matrix_world
            set_origin(reference_obj, mx)

            return {'FINISHED'}

    
    def add_displace_modifier(self, reference_obj, axis, strength):
        displace = reference_obj.modifiers.new("{} Axis Displace — ND".format(axis), 'DISPLACE')
        displace.direction = axis 
        displace.space = 'GLOBAL'
        displace.mid_level = 0
        displace.strength = strength


def register():
    bpy.utils.register_class(ND_OT_set_origin)


def unregister():
    bpy.utils.unregister_class(ND_OT_set_origin)
