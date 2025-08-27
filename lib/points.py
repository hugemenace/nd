# ███╗   ██╗██████╗
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝
#
# ND (Non-Destructive) Blender Add-on
# Copyright (C) 2024 Tristan S. & Ian J. (HugeMenace)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ---
# Contributors: Tristo (HM)
# ---

import bpy
import gpu
from mathutils import Matrix
from gpu_extras.batch import batch_for_shader
from . preferences import get_preferences, is_vulkan
from . polling import app_minor_version


dot_vertex_shader = '''
    void main() {
        gl_Position = viewProjectionMatrix * vec4(pos, 1.0);
    }
'''

dot_fragment_shader = '''
    float circle(in vec2 st, in float radius, in float smoothing) {
        float perc = distance(st, vec2(0.5));
        return 1.0 - smoothstep(radius, radius + smoothing, perc);
    }

    void main() {
        vec4 c = vec4(circle(gl_PointCoord, 0.4, 0.1));
        float gamma = 2.2;
        fragColor = pow(c * color, vec4(gamma));
    }
'''


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

    cls.line_shader = None
    cls.circle_shader = None

    if app_minor_version() < (4, 0):
        cls.line_shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

    if app_minor_version() >= (4, 0) and not is_vulkan():
        cls.line_shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    if app_minor_version() >= (4, 5) and is_vulkan():
        cls.line_shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')

    if app_minor_version() >= (4, 5) and is_vulkan():
        cls.circle_shader = gpu.shader.from_builtin('POINT_UNIFORM_COLOR')
    else:
        circle_shader_info = gpu.types.GPUShaderCreateInfo()
        circle_shader_info.vertex_source(dot_vertex_shader)
        circle_shader_info.fragment_source(dot_fragment_shader)
        circle_shader_info.vertex_in(0, 'VEC3', 'pos')
        circle_shader_info.push_constant('MAT4', 'viewProjectionMatrix')
        circle_shader_info.push_constant('VEC4', 'color')
        circle_shader_info.fragment_out(0, 'VEC4', 'fragColor')

        cls.circle_shader = gpu.shader.create_from_info(circle_shader_info)


def draw_circles(shader, points, radius, color):
    gpu.state.program_point_size_set(False)

    if app_minor_version() >= (4, 5) and is_vulkan():
        # For 4.5+ & Vulkan, we have to draw squares instead of circles,
        # so reduce the size slightly so they're not obnoxiously large.
        gpu.state.point_size_set(radius * 0.65)
    else:
        gpu.state.point_size_set(radius)

    gpu.state.blend_set("ALPHA")

    if app_minor_version() < (4, 5) or not is_vulkan():
        view_projection_matrix = bpy.context.region_data.perspective_matrix
        shader.uniform_float("viewProjectionMatrix", Matrix(view_projection_matrix))

    shader.uniform_float("color", color)

    batch = batch_for_shader(shader, 'POINTS', {"pos": points})

    shader.bind()
    batch.draw(shader)


def draw_guideline(shader, line, size, color):
    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(size)

    shader.uniform_float("color", color)

    if app_minor_version() >= (4, 5) and is_vulkan():
        shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])
        shader.uniform_float("lineWidth", size)

    batch = batch_for_shader(shader, 'LINES', {"pos": line})

    shader.bind()
    batch.draw(shader)


def update_points(cls):
    draw_guideline(cls.line_shader, cls.guide_line, 3, get_preferences().points_guide_line_color)

    draw_circles(cls.circle_shader, cls.primary_points, 20, get_preferences().points_primary_color)
    draw_circles(cls.circle_shader, cls.secondary_points, 15, get_preferences().points_secondary_color)
    draw_circles(cls.circle_shader, cls.tertiary_points, 25, get_preferences().points_tertiary_color)

    redraw_regions()
