import bpy
import blf


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


def toggle_pin_overlay(cls):
    cls.pin_overlay = not cls.pin_overlay


def toggle_operator_passthrough(cls):
    cls.operator_passthrough = not cls.operator_passthrough


def init_overlay(cls, event):
    cls.overlay_offset_x = 25
    cls.overlay_offset_y = -15

    cls.line_step = 0
    cls.line_spacer = 40
    
    cls.region_offset_x = event.mouse_x - event.mouse_region_x
    cls.region_offset_y = event.mouse_y - event.mouse_region_y

    cls.overlay_x = event.mouse_x - cls.region_offset_x + cls.overlay_offset_x
    cls.overlay_y = event.mouse_y - cls.region_offset_y + cls.overlay_offset_y

    cls.pin_overlay = False
    cls.operator_passthrough = False


def update_overlay(cls, context, event, x_offset=400, lines=1):
    cls.overlay_x = event.mouse_x - cls.region_offset_x + cls.overlay_offset_x
    cls.overlay_y = event.mouse_y - cls.region_offset_y + cls.overlay_offset_y

    if cls.pin_overlay:
        cls.overlay_x = context.region.width - x_offset
        cls.overlay_y = 45 + (lines * cls.line_spacer)

    redraw_regions()


def draw_header(cls):
    if cls.operator_passthrough:
        blf.size(0, 12, 72)
        blf.color(0, .933, 0.231, 0.169, 1.0)
        blf.position(0, cls.overlay_x + 1, cls.overlay_y + 26, 0)
        blf.draw(0, "HALTED")

    blf.size(0, 24, 72)

    if cls.operator_passthrough:
        blf.color(0, .933, 0.231, 0.169, 1.0)
    else:
        blf.color(0, 1.0, 0.529, 0.216, 1.0)

    blf.position(0, cls.overlay_x, cls.overlay_y, 0)
    blf.draw(0, "ND — " + cls.bl_label)

    cls.line_step = 0


def draw_property(cls, property_content, metadata_content, active=False, alt_mode=False):
    blf.size(0, 28, 72)
    
    if cls.operator_passthrough:
        blf.color(0, 1.0, 1.0, 1.0, 0.2)
    elif active:
        blf.color(0, 0.216, 0.686, 1.0, 1.0)
    else:
        blf.color(0, 1.0, 1.0, 1.0, 0.1)
    
    blf.position(0, cls.overlay_x, cls.overlay_y - (38 + (cls.line_spacer * cls.line_step)), 0)
    
    if alt_mode:
        blf.draw(0, "◑")
    else:
        blf.draw(0, "●")

    blf.size(0, 16, 72)

    if cls.operator_passthrough:
        blf.color(0, 1.0, 1.0, 1.0, 0.2)
    else:
        blf.color(0, 1.0, 1.0, 1.0, 1.0)

    blf.position(0, cls.overlay_x + 25, cls.overlay_y - (25 + (cls.line_spacer * cls.line_step)), 0)
    blf.draw(0, property_content)
    
    blf.size(0, 11, 72)
    
    if cls.operator_passthrough:
        blf.color(0, 1.0, 1.0, 1.0, 0.2)
    else:
        blf.color(0, 1.0, 1.0, 1.0, 0.3)

    blf.position(0, cls.overlay_x + 25, cls.overlay_y - (40 + (cls.line_spacer * cls.line_step)), 0)
    blf.draw(0, metadata_content)

    cls.line_step += 1


def draw_hint(cls, hint_content, metadata_content):
    blf.size(0, 22, 72)
    
    if cls.operator_passthrough:
        blf.color(0, 1.0, 1.0, 1.0, 0.2)
    else:
        blf.color(0, 1.0, 1.0, 1.0, 0.5)

    blf.position(0, cls.overlay_x - 3, cls.overlay_y - (36 + (cls.line_spacer * cls.line_step)), 0)
    blf.draw(0, "◈")

    blf.size(0, 16, 72)

    if cls.operator_passthrough:
        blf.color(0, 1.0, 1.0, 1.0, 0.2)
    else:
        blf.color(0, 1.0, 1.0, 1.0, 1.0)

    blf.position(0, cls.overlay_x + 25, cls.overlay_y - (25 + (cls.line_spacer * cls.line_step)), 0)
    blf.draw(0, hint_content)
    
    blf.size(0, 11, 72)
    
    if cls.operator_passthrough:
        blf.color(0, 1.0, 1.0, 1.0, 0.2)
    else:
        blf.color(0, 1.0, 1.0, 1.0, 0.3)

    blf.position(0, cls.overlay_x + 25, cls.overlay_y - (40 + (cls.line_spacer * cls.line_step)), 0)
    blf.draw(0, metadata_content)

    cls.line_step += 1
