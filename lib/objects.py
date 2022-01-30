import bpy 
import bmesh
from math import radians


def add_single_vertex_object(cls, context, name):
    mesh = bpy.data.meshes.new("ND — " + name)
    obj = bpy.data.objects.new("ND — " + name, mesh)

    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    bm.verts.new()
    bm.to_mesh(mesh)
    bm.free()
    
    obj.select_set(True)
    
    context.view_layer.objects.active = obj
    
    bpy.ops.object.shade_smooth()
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = radians(30)
    
    cls.obj = obj


def align_object_to_3d_cursor(cls, context):
    cls.obj.location = context.scene.cursor.location
    cls.obj.rotation_euler = context.scene.cursor.rotation_euler