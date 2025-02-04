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
import bgl
from mathutils import Matrix
from gpu_extras.batch import batch_for_shader
from . preferences import get_preferences
from . polling import app_minor_version


generic_vertex_shader = '''
    uniform mat4 viewProjectionMatrix;
    in vec3 pos;

    void main() {
        gl_Position = viewProjectionMatrix * vec4(pos, 1.0);
    }
'''

circle_fragment_shader = '''
    uniform vec4 color;
    out vec4 fragColor;

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

disc_fragment_shader = '''
    uniform vec4 color;
    out vec4 fragColor;

    float disc(in vec2 st, in float radius, in float thickness, in float smoothing) {
        float perc = distance(st, vec2(0.5));
        float outline = 1.0 - smoothstep(radius, radius + smoothing, perc);
        float center = smoothstep(radius - thickness, (radius - thickness) + smoothing, perc);

        return outline * center;
    }

    void main() {
        vec4 d = vec4(disc(gl_PointCoord, 0.4, 0.018, 0.02));
        float gamma = 2.2;
        fragColor = pow(d * color, vec4(gamma));
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
    cls.disc_points = []
    cls.secondary_points = []
    cls.tertiary_points = []
    cls.guide_line = ()


def draw_discs(shader, points, radius, color):
    gpu.state.point_size_set(radius)
    batch = batch_for_shader(shader, 'POINTS', {"pos": points})
    gpu.state.blend_set("ALPHA")
    shader.bind()
    view_projection_matrix = bpy.context.region_data.perspective_matrix
    shader.uniform_float("viewProjectionMatrix", Matrix(view_projection_matrix))
    shader.uniform_float("color", color)
    batch.draw(shader)


def draw_circles(shader, points, radius, color):
    gpu.state.point_size_set(radius)
    batch = batch_for_shader(shader, 'POINTS', {"pos": points})
    gpu.state.blend_set("ALPHA")
    shader.bind()
    view_projection_matrix = bpy.context.region_data.perspective_matrix
    shader.uniform_float("viewProjectionMatrix", Matrix(view_projection_matrix))
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
    shader = None
    circle_shader = gpu.types.GPUShader(generic_vertex_shader, circle_fragment_shader)
    disc_shader = gpu.types.GPUShader(generic_vertex_shader, disc_fragment_shader)

    if app_minor_version() < (4, 0):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    else:
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    draw_guideline(shader, cls.guide_line, 2, get_preferences().points_guide_line_color)
    draw_circles(circle_shader, cls.primary_points, 20, get_preferences().points_primary_color)
    draw_circles(circle_shader, cls.secondary_points, 15, get_preferences().points_secondary_color)
    draw_circles(circle_shader, cls.tertiary_points, 25, get_preferences().points_tertiary_color)
    draw_discs(disc_shader, cls.disc_points, 200, get_preferences().points_primary_color)

    redraw_regions()
