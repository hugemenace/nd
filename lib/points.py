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
import gpu
import bgl
from mathutils import Vector, Matrix
from gpu_extras.batch import batch_for_shader


def register_points_handler(cls):
    handler = bpy.app.driver_namespace.get('nd.points')

    if not handler:
        handler = bpy.types.SpaceView3D.draw_handler_add(update_points, (cls, ), 'WINDOW', 'POST_VIEW')
        dns = bpy.app.driver_namespace
        dns['nd.points'] = handler

        redraw_regions()


def unregister_points_handler():
    handler = bpy.app.driver_namespace.get('nd.points')

    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        del bpy.app.driver_namespace['nd.points']

        redraw_regions()


def redraw_regions():
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    region.tag_redraw()


def init_points(cls):
    cls.primary_points = []
    cls.secondary_points = []
    cls.tertiary_points = []
    cls.guide_line = ()


def draw_points(shader, points, size, color):
    gpu.state.point_size_set(size)
    batch = batch_for_shader(shader, 'POINTS', {"pos": points})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def draw_guideline(shader, line, size, color):
    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(size)
    batch = batch_for_shader(shader, 'LINES', {"pos": line})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def update_points(cls):
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

    draw_points(shader, cls.primary_points, 10, (82/255, 224/255, 82/255, 1.))
    draw_points(shader, cls.secondary_points, 6, (255/255, 135/255, 55/255, 1.0))
    draw_points(shader, cls.tertiary_points, 12, (82/255, 224/255, 82/255, 1.0))
    draw_guideline(shader, cls.guide_line, 2, (82/255, 224/255, 82/255, 0.5))

    redraw_regions()
