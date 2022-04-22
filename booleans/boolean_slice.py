import bpy
from .. lib.collections import move_to_utils_collection
from .. lib.preferences import get_preferences


class ND_OT_bool_slice(bpy.types.Operator):
    bl_idname = "nd.bool_slice"
    bl_label = "Slice"
    bl_description = "Perform a boolean operation on the selected objects"
    bl_options = {'UNDO'}

    
    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 2 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        solver = 'FAST' if get_preferences().use_fast_booleans else 'EXACT'

        a, b = context.selected_objects
        reference_obj = a if a.name != context.object.name else b
        
        difference_obj = context.object

        intersecting_obj = context.object.copy()
        intersecting_obj.data = context.object.data.copy()
        intersecting_obj.animation_data_clear()
        context.collection.objects.link(intersecting_obj)

        boolean_diff = difference_obj.modifiers.new("Difference — ND Bool", 'BOOLEAN')
        boolean_diff.operation = 'DIFFERENCE'
        boolean_diff.object = reference_obj
        boolean_diff.solver = solver

        boolean_isect = intersecting_obj.modifiers.new("Intersection — ND Bool", 'BOOLEAN')
        boolean_isect.operation = 'INTERSECT'
        boolean_isect.object = reference_obj
        boolean_isect.solver = solver

        reference_obj.display_type = 'WIRE'
        reference_obj.hide_render = True
        reference_obj.name = " — ".join(['Bool', reference_obj.name])
        reference_obj.data.name = reference_obj.name

        reference_obj.parent = difference_obj
        intersecting_obj.parent = difference_obj

        reference_obj.matrix_parent_inverse = difference_obj.matrix_world.inverted()
        intersecting_obj.matrix_parent_inverse = difference_obj.matrix_world.inverted()

        move_to_utils_collection(reference_obj)

        bpy.ops.object.select_all(action='DESELECT')
        reference_obj.select_set(True)
        bpy.context.view_layer.objects.active = reference_obj

        return {'FINISHED'}

    
def menu_func(self, context):
    self.layout.operator(ND_OT_bool_slice.bl_idname, text=ND_OT_bool_slice.bl_label)


def register():
    bpy.utils.register_class(ND_OT_bool_slice)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_bool_slice)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
