import bpy
from mathutils import Vector


class ND_OT_set_origin(bpy.types.Operator):
    bl_idname = "nd.set_origin"
    bl_label = "Set Origin"
    bl_description = "Set the origin of the active object to that of another"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 2


    def execute(self, context):
        a, b = context.selected_objects
        reference_obj = a if a.name != context.object.name else b
        
        (x_dest, y_dest, z_dest) = context.object.location
        (x_orig, y_orig, z_orig) = reference_obj.location

        context.object.location = reference_obj.location

        self.add_displace_modifier(context, 'X', x_dest - x_orig)
        self.add_displace_modifier(context, 'Y', y_dest - y_orig)
        self.add_displace_modifier(context, 'Z', z_dest - z_orig)

        return {'FINISHED'}

    
    def add_displace_modifier(self, context, axis, strength):
        displace = context.object.modifiers.new("{} Axis Displace — ND".format(axis), 'DISPLACE')
        displace.direction = axis 
        displace.space = 'GLOBAL'
        displace.mid_level = 0
        displace.strength = strength


def menu_func(self, context):
    self.layout.operator(ND_OT_set_origin.bl_idname, text=ND_OT_set_origin.bl_label)


def register():
    bpy.utils.register_class(ND_OT_set_origin)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_set_origin)
    bpy.types.VIEW3D_MT_object.remove(menu_func)