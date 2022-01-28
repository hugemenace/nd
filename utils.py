import bpy
import bmesh
from math import radians
from mathutils import Vector, Matrix


def averaged_vector(vector_list, size=3):
    vector_sum = Vector.Fill(size)

    for vector in vector_list:
        vector_sum += vector

    return vector_sum / len(vector_list)


def create_rotation_matrix_from_face(world_matrix, face):
    normal = (world_matrix.to_3x3() @ face.normal).normalized()
    tangent = (world_matrix.to_3x3() @ face.calc_tangent_edge_pair()).normalized()
    binormal = normal.cross(tangent)

    rotation = Matrix()
    rotation[0].xyz = tangent
    rotation[1].xyz = binormal
    rotation[2].xyz = normal

    return rotation.transposed()


def set_3d_cursor(location, rotation):
    cursor = bpy.context.scene.cursor
    cursor.location = location

    if cursor.rotation_mode == 'QUATERNION':
        cursor.rotation_quaternion = rotation
    elif cursor.rotation_mode == 'AXIS_ANGLE':
        cursor.rotation_axis_angle = rotation.to_axis_angle()
    else:
        cursor.rotation_euler = rotation.to_euler(cursor.rotation_mode)


def add_single_vertex_object(cls, context, name):
    mesh = bpy.data.meshes.new("ND — " + name)
    obj = bpy.data.objects.new("ND — " + name, mesh)
    bpy.data.collections[context.collection.name].objects.link(obj)
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


def capture_modifier_keys(cls, event=None):
    cls.key_no_modifiers = True if event is None else not event.ctrl and not event.alt
    cls.key_ctrl = False if event is None else event.ctrl and not event.alt
    cls.key_shift_ctrl = False if event is None else event.shift and cls.key_ctrl
    cls.key_alt = False if event is None else not event.ctrl and event.alt
    cls.key_shift_alt = False if event is None else event.shift and cls.key_alt
    cls.key_ctrl_alt = False if event is None else event.ctrl and event.alt
    cls.key_shift_ctrl_alt = False if event is None else event.shift and cls.key_ctrl_alt
    cls.key_shift =False if event is None else event.shift
    cls.key_shift_no_modifiers = False if event is None else event.shift and cls.key_no_modifiers
    cls.key_toggle_pin_overlay = False if event is None else event.type == 'P' and event.value == 'PRESS'
    cls.key_increase_factor = False if event is None else event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'} and event.value == 'PRESS'
    cls.key_decrease_factor = False if event is None else event.type in {'MINUS', 'NUMPAD_MINUS'} and event.value == 'PRESS'
    cls.key_step_up = False if event is None else event.type == 'WHEELUPMOUSE'
    cls.key_step_down = False if event is None else event.type == 'WHEELDOWNMOUSE'
    cls.key_confirm = False if event is None else event.type == 'LEFTMOUSE'
    cls.key_confirm_alternative = False if event is None else event.type == 'SPACE'
    cls.key_cancel = False if event is None else event.type in {'RIGHTMOUSE', 'ESC'}
    cls.key_movement_passthrough = False if event is None else event.type == 'MIDDLEMOUSE' or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF')