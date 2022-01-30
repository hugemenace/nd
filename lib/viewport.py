import bpy


def set_3d_cursor(location, rotation):
    cursor = bpy.context.scene.cursor
    cursor.location = location

    if cursor.rotation_mode == 'QUATERNION':
        cursor.rotation_quaternion = rotation
    elif cursor.rotation_mode == 'AXIS_ANGLE':
        cursor.rotation_axis_angle = rotation.to_axis_angle()
    else:
        cursor.rotation_euler = rotation.to_euler(cursor.rotation_mode)





