import bpy
import blf


def register_draw_handler(self, callback, name):
    handler = bpy.app.driver_namespace.get(name)

    if not handler:
        handler = bpy.types.SpaceView3D.draw_handler_add(callback, (self, ), 'WINDOW', 'POST_PIXEL')
        dns = bpy.app.driver_namespace
        dns[name] = handler

        redraw_regions()


def unregister_draw_handler(self, name):
    handler = bpy.app.driver_namespace.get(name)

    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        del bpy.app.driver_namespace[name]

        redraw_regions()


def redraw_regions():
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    region.tag_redraw()


def init_overlay(self, event):
    self.overlay_offset_x = 25
    self.overlay_offset_y = -15

    self.line_step = 0
    self.line_spacer = 40
    
    self.region_offset_x = event.mouse_x - event.mouse_region_x
    self.region_offset_y = event.mouse_y - event.mouse_region_y

    self.overlay_x = event.mouse_x - self.region_offset_x + self.overlay_offset_x
    self.overlay_y = event.mouse_y - self.region_offset_y + self.overlay_offset_y


def update_overlay(self, context, event):
    self.overlay_x = event.mouse_x - self.region_offset_x + self.overlay_offset_x
    self.overlay_y = event.mouse_y - self.region_offset_y + self.overlay_offset_y

    region_buffer = 5

    if event.mouse_region_x <= 0:
        context.window.cursor_warp(context.region.width + self.region_offset_x - region_buffer, event.mouse_y)
    
    if event.mouse_region_x >= context.region.width - 1:
        context.window.cursor_warp(self.region_offset_x + region_buffer, event.mouse_y)
    
    if event.mouse_region_y <= 0:
        context.window.cursor_warp(event.mouse_x, context.region.height + self.region_offset_y - region_buffer)
    
    if event.mouse_region_y >= context.region.height - 1:
        context.window.cursor_warp(event.mouse_x, self.region_offset_y + region_buffer)

    redraw_regions()

def draw_header(self, content):
    blf.size(0, 24, 72)
    blf.color(0, 1.0, 0.529, 0.216, 1.0)
    blf.position(0, self.overlay_x, self.overlay_y, 0)
    blf.draw(0, content)

    self.line_step = 0


def draw_property(self, property_content, metadata_content, active=False, alt_mode=False):
    blf.size(0, 28, 72)
    
    if active:
        blf.color(0, 0.216, 0.686, 1.0, 1.0)
    else:
        blf.color(0, 1.0, 1.0, 1.0, 0.1)
    
    blf.position(0, self.overlay_x, self.overlay_y - (38 + (self.line_spacer * self.line_step)), 0)
    
    if alt_mode:
        blf.draw(0, "◑")
    else:
        blf.draw(0, "●")

    blf.size(0, 16, 72)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.position(0, self.overlay_x + 25, self.overlay_y - (25 + (self.line_spacer * self.line_step)), 0)
    blf.draw(0, property_content)
    
    blf.size(0, 11, 72)
    blf.color(0, 1.0, 1.0, 1.0, 0.3)
    blf.position(0, self.overlay_x + 25, self.overlay_y - (40 + (self.line_spacer * self.line_step)), 0)
    blf.draw(0, metadata_content)

    self.line_step += 1


def draw_hint(self, hint_content, metadata_content):
    blf.size(0, 22, 72)
    
    blf.color(0, 1.0, 1.0, 1.0, 0.5)
    blf.position(0, self.overlay_x - 3, self.overlay_y - (36 + (self.line_spacer * self.line_step)), 0)
    blf.draw(0, "◈")

    blf.size(0, 16, 72)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.position(0, self.overlay_x + 25, self.overlay_y - (25 + (self.line_spacer * self.line_step)), 0)
    blf.draw(0, hint_content)
    
    blf.size(0, 11, 72)
    blf.color(0, 1.0, 1.0, 1.0, 0.3)
    blf.position(0, self.overlay_x + 25, self.overlay_y - (40 + (self.line_spacer * self.line_step)), 0)
    blf.draw(0, metadata_content)

    self.line_step += 1
