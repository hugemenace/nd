# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy
from .. lib.collections import move_to_utils_collection
from .. lib.preferences import get_preferences


class ND_OT_bool_vanilla(bpy.types.Operator):
    bl_idname = "nd.bool_vanilla"
    bl_label = "Boolean"
    bl_description = "Perform a boolean operation on the selected objects"
    bl_options = {'UNDO'}

    
    mode: bpy.props.EnumProperty(items=[
        ('DIFFERENCE', 'Difference', 'Perform a difference operation'),
        ('UNION', 'Union', 'Perform a union operation'),
        ('INTERSECT', 'Intersect', 'Perform an intersect operation'),
    ], name="Mode", default='DIFFERENCE')


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 2 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        solver = 'FAST' if get_preferences().use_fast_booleans else 'EXACT'

        a, b = context.selected_objects
        reference_obj = a if a.name != context.object.name else b
        
        boolean = context.object.modifiers.new(" — ".join([self.mode.capitalize(), "ND Bool"]), 'BOOLEAN')
        boolean.operation = self.mode
        boolean.object = reference_obj
        boolean.solver = solver

        reference_obj.display_type = 'WIRE'
        reference_obj.hide_render = True
        reference_obj.name = " — ".join(['Bool', reference_obj.name])
        reference_obj.data.name = reference_obj.name

        reference_obj.parent = context.object
        reference_obj.matrix_parent_inverse = context.object.matrix_world.inverted()

        move_to_utils_collection(reference_obj)

        bpy.ops.object.select_all(action='DESELECT')
        reference_obj.select_set(True)
        bpy.context.view_layer.objects.active = reference_obj

        return {'FINISHED'}

    
def menu_func(self, context):
    self.layout.operator(ND_OT_bool_vanilla.bl_idname, text=ND_OT_bool_vanilla.bl_label)


def register():
    bpy.utils.register_class(ND_OT_bool_vanilla)


def unregister():
    bpy.utils.unregister_class(ND_OT_bool_vanilla)
