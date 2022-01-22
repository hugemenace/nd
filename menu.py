import bpy

keys = []

class NDMenu(bpy.types.Menu):
    bl_label = "HugeMenace ND"
    bl_idname = "HM_MT_nd"


    def draw(self, context):
        layout = self.layout
        layout.operator("nd.sketch_bevel", icon = 'MOD_BEVEL')
        layout.operator("nd.faux_bevel", icon = 'MOD_BEVEL')
        layout.separator()
        layout.operator("nd.bolt", icon = 'GHOST_ENABLED')


def draw_item(self, context):
    layout = self.layout
    layout.menu(NDMenu.bl_idname)


def register():
    bpy.utils.register_class(NDMenu)
    bpy.types.INFO_HT_header.append(draw_item)
   
    keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name = "3D View", space_type = 'VIEW_3D')
    entry = keymap.keymap_items.new("wm.call_menu", 'TWO', 'PRESS', shift = True)
    entry.properties.name = "HM_MT_nd"

    keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(NDMenu)
    bpy.types.INFO_HT_header.remove(draw_item)


if __name__ == "__main__":
    register()