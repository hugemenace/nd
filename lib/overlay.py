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
import blf
from . preferences import get_preferences
from . polling import app_minor_version


def register_draw_handler(cls, callback):
    handler = bpy.app.driver_namespace.get('nd.overlay')

    if not handler:
        handler = bpy.types.SpaceView3D.draw_handler_add(callback, (cls, ), 'WINDOW', 'POST_PIXEL')
        dns = bpy.app.driver_namespace
        dns['nd.overlay'] = handler

        redraw_regions()


def unregister_draw_handler():
    handler = bpy.app.driver_namespace.get('nd.overlay')

    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        del bpy.app.driver_namespace['nd.overlay']

        redraw_regions()


def redraw_regions():
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    region.tag_redraw()


def toggle_pin_overlay(cls, event):
    cls.overlay_x = event.mouse_x - cls.region_offset_x + cls.overlay_offset_x
    cls.overlay_y = event.mouse_y - cls.region_offset_y + cls.overlay_offset_y

    cls.pin_overlay = not cls.pin_overlay

    if get_preferences().lock_overlay_pinning:
        get_preferences().overlay_pinned = cls.pin_overlay
        get_preferences().overlay_pin_x = cls.overlay_x
        get_preferences().overlay_pin_y = cls.overlay_y


def toggle_operator_passthrough(cls):
    cls.operator_passthrough = not cls.operator_passthrough


def init_overlay(cls, event):
    cls.overlay_offset_x = 25
    cls.overlay_offset_y = -15

    cls.line_step = 0
    cls.dpi = get_preferences().overlay_dpi
    cls.dpi_scalar = cls.dpi / 72
    cls.line_spacer = 40 * cls.dpi_scalar

    cls.region_offset_x = event.mouse_x - event.mouse_region_x
    cls.region_offset_y = event.mouse_y - event.mouse_region_y

    cls.overlay_x = event.mouse_x - cls.region_offset_x + cls.overlay_offset_x
    cls.overlay_y = event.mouse_y - cls.region_offset_y + cls.overlay_offset_y

    cls.pin_overlay = False
    cls.operator_passthrough = False
    cls.mouse_warped = False

    if get_preferences().lock_overlay_pinning:
        cls.pin_overlay = get_preferences().overlay_pinned
        cls.overlay_x = get_preferences().overlay_pin_x
        cls.overlay_y = get_preferences().overlay_pin_y


def update_overlay(cls, context, event):
    if not cls.pin_overlay:
        cls.overlay_x = event.mouse_x - cls.region_offset_x + cls.overlay_offset_x
        cls.overlay_y = event.mouse_y - cls.region_offset_y + cls.overlay_offset_y

    if not cls.operator_passthrough and get_preferences().enable_mouse_values:
        wrap_cursor(cls, context, event)

    redraw_regions()


def wrap_cursor(cls, context, event):
    if event.mouse_region_x <= 0:
        mouse_x = context.region.width + cls.region_offset_x - 10
        context.window.cursor_warp(mouse_x, event.mouse_y)
        cls.mouse_warped = True

    if event.mouse_region_x >= context.region.width - 1:
        mouse_x = cls.region_offset_x + 10
        context.window.cursor_warp(mouse_x, event.mouse_y)
        cls.mouse_warped = True

    if event.mouse_region_y <= 0:
        mouse_y = context.region.height + cls.region_offset_y - 10
        context.window.cursor_warp(event.mouse_x, mouse_y)

    if event.mouse_region_y >= context.region.height - 1:
        mouse_y = cls.region_offset_y + 100
        context.window.cursor_warp(event.mouse_x, mouse_y)


def draw_header(cls):
    is_summoned = getattr(cls, "summoned", False)

    if cls.operator_passthrough:
        r, g, b = get_preferences().overlay_header_paused_color
        blf.color(0, r, g, b, 1.0)
    elif is_summoned and not cls.operator_passthrough:
        r, g, b = get_preferences().overlay_header_recalled_color
        blf.color(0, r, g, b, 1.0)
    else:
        r, g, b = get_preferences().overlay_header_standard_color
        blf.color(0, r, g, b, 1.0)

    if cls.operator_passthrough or is_summoned or cls.pin_overlay:
        if app_minor_version() < (4, 0):
            blf.size(0, 11, cls.dpi)
        else:
            blf.size(0, 11 * cls.dpi_scalar)

        blf.position(0, cls.overlay_x + (1 * cls.dpi_scalar), cls.overlay_y + (26 * cls.dpi_scalar), 0)

        states = []
        if cls.operator_passthrough:
            states.append("PAUSED")
        if is_summoned:
            states.append("RECALL")
        if cls.pin_overlay:
            states.append("PINNED")

        blf.draw(0, " // ".join(states))

    if app_minor_version() < (4, 0):
        blf.size(0, 24, cls.dpi)
    else:
        blf.size(0, 24 * cls.dpi_scalar)
    blf.position(0, cls.overlay_x, cls.overlay_y, 0)
    blf.draw(0, "ND — " + cls.bl_label)

    cls.line_step = 0


def draw_property(cls, property_content, metadata_content, active=False, alt_mode=False, mouse_value=False, input_stream=None):
    if app_minor_version() < (4, 0):
        blf.size(0, 28, cls.dpi)
    else:
        blf.size(0, 28 * cls.dpi_scalar)

    is_ok, is_value, is_raw = input_stream or (False, None, None)
    base_r, base_g, base_b = get_preferences().overlay_base_color

    if cls.operator_passthrough:
        blf.color(0, base_r, base_g, base_b, 0.2)
    elif is_value is not None and active:
        r, g, b = get_preferences().overlay_option_manual_override_color
        blf.color(0, r, g, b, 1.0)
    elif active:
        r, g, b = get_preferences().overlay_option_active_color
        blf.color(0, r, g, b, 1.0)
    else:
        blf.color(0, base_r, base_g, base_b, 0.1)

    blf.position(0, cls.overlay_x, cls.overlay_y - ((38 * cls.dpi_scalar) + (cls.line_spacer * cls.line_step)), 0)

    if app_minor_version() >= (3, 4):
        if app_minor_version() < (4, 0):
            blf.size(0, 14, cls.dpi)
        else:
            blf.size(0, 14 * cls.dpi_scalar)
        blf.position(0, cls.overlay_x, cls.overlay_y - ((31 * cls.dpi_scalar) + (cls.line_spacer * cls.line_step)), 0)

    if not cls.operator_passthrough and alt_mode:
        blf.draw(0, "◑")
    else:
        blf.draw(0, "●")

    if get_preferences().enable_mouse_values and mouse_value:
        if app_minor_version() < (4, 0):
            blf.size(0, 22, cls.dpi)
            blf.position(0, cls.overlay_x - (15 * cls.dpi_scalar), cls.overlay_y - ((34 * cls.dpi_scalar) + (cls.line_spacer * cls.line_step)), 0)
        else:
            blf.size(0, 22 * cls.dpi_scalar)
            blf.position(0, cls.overlay_x - (15 * cls.dpi_scalar), cls.overlay_y - ((33 * cls.dpi_scalar) + (cls.line_spacer * cls.line_step)), 0)
        blf.draw(0, "»")

    if app_minor_version() < (4, 0):
        blf.size(0, 16, cls.dpi)
    else:
        blf.size(0, 16 * cls.dpi_scalar)

    if cls.operator_passthrough:
        blf.color(0, base_r, base_g, base_b, 0.2)
    else:
        blf.color(0, base_r, base_g, base_b, 1.0)

    blf.position(0, cls.overlay_x + (25 * cls.dpi_scalar), cls.overlay_y - ((25 * cls.dpi_scalar) + (cls.line_spacer * cls.line_step)), 0)
    blf.draw(0, property_content)

    if app_minor_version() < (4, 0):
        blf.size(0, 11, cls.dpi)
    else:
        blf.size(0, 11 * cls.dpi_scalar)

    if cls.operator_passthrough:
        blf.color(0, base_r, base_g, base_b, 0.2)
    else:
        blf.color(0, base_r, base_g, base_b, 0.3)

    blf.position(0, cls.overlay_x + (25 * cls.dpi_scalar), cls.overlay_y - ((40 * cls.dpi_scalar) + (cls.line_spacer * cls.line_step)), 0)

    if is_value is not None:
        reset_behaviour = get_preferences().overlay_reset_key_behaviour
        blf.draw(0, "{} — [{}] to {}.".format(metadata_content, get_preferences().overlay_reset_key, "reset" if reset_behaviour == "RESET" else "unlock"))
    else:
        blf.draw(0, metadata_content)

    cls.line_step += 1


def draw_hint(cls, hint_content, metadata_content):
    if app_minor_version() < (4, 0):
        blf.size(0, 22, cls.dpi)
    else:
        blf.size(0, 16 * cls.dpi_scalar)

    base_r, base_g, base_b = get_preferences().overlay_base_color

    if cls.operator_passthrough:
        blf.color(0, base_r, base_g, base_b, 0.2)
    else:
        blf.color(0, base_r, base_g, base_b, 0.5)

    blf.position(0, cls.overlay_x - (3 * cls.dpi_scalar), cls.overlay_y - ((36 * cls.dpi_scalar) + (cls.line_spacer * cls.line_step)), 0)
    blf.draw(0, "◈")

    if app_minor_version() < (4, 0):
        blf.size(0, 16, cls.dpi)
    else:
        blf.size(0, 16 * cls.dpi_scalar)

    if cls.operator_passthrough:
        blf.color(0, base_r, base_g, base_b, 0.2)
    else:
        blf.color(0, base_r, base_g, base_b, 1.0)

    blf.position(0, cls.overlay_x + (25 * cls.dpi_scalar), cls.overlay_y - ((25 * cls.dpi_scalar) + (cls.line_spacer * cls.line_step)), 0)
    blf.draw(0, hint_content)

    if app_minor_version() < (4, 0):
        blf.size(0, 11, cls.dpi)
    else:
        blf.size(0, 11 * cls.dpi_scalar)

    if cls.operator_passthrough:
        blf.color(0, base_r, base_g, base_b, 0.2)
    else:
        blf.color(0, base_r, base_g, base_b, 0.3)

    blf.position(0, cls.overlay_x + (25 * cls.dpi_scalar), cls.overlay_y - ((40 * cls.dpi_scalar) + (cls.line_spacer * cls.line_step)), 0)
    blf.draw(0, metadata_content)

    cls.line_step += 1
