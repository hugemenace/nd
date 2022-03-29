import bpy


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
            return len(context.selected_objects) == 2


    def execute(self, context):
        a, b = context.selected_objects
        reference_obj = a if a.name != context.object.name else b
        
        boolean = context.object.modifiers.new(" — ".join([self.mode.capitalize(), "ND Bool"]), 'BOOLEAN')
        boolean.operation = self.mode
        boolean.object = reference_obj
        boolean.solver = 'EXACT'

        reference_obj.display_type = 'WIRE'
        reference_obj.hide_render = True

        return {'FINISHED'}

    
def menu_func(self, context):
    self.layout.operator(ND_OT_bool_vanilla.bl_idname, text=ND_OT_bool_vanilla.bl_label)


def register():
    bpy.utils.register_class(ND_OT_bool_vanilla)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_bool_vanilla)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
