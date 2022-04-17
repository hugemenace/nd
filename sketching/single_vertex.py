import bpy
from .. lib.objects import add_single_vertex_object, align_object_to_3d_cursor


class ND_OT_single_vertex(bpy.types.Operator):
    bl_idname = "nd.single_vertex"
    bl_label = "Single Vertex"
    bl_description = "Creates a single vertex object at the 3D cursor"
    bl_options = {'UNDO'}


    def execute(self, context):
        add_single_vertex_object(self, context, "Sketch")
        align_object_to_3d_cursor(self, context)
        self.start_sketch_editing(context)

        return {'FINISHED'}


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def start_sketch_editing(self, context):
        bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'VERT'})
        bpy.ops.mesh.select_all(action='SELECT')


def menu_func(self, context):
    self.layout.operator(ND_OT_single_vertex.bl_idname, text=ND_OT_single_vertex.bl_label)


def register():
    bpy.utils.register_class(ND_OT_single_vertex)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_single_vertex)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
