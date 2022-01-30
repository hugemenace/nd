import bpy
from .. import bl_info


keys = []


class ND_MT_main_menu(bpy.types.Menu):
    bl_label = "ND v%s" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_idname = "ND_MT_main_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.face_sketch", icon='FACESEL')
        layout.operator("nd.blank_sketch", icon='GREASEPENCIL')
        layout.operator("nd.vertex_bevel", icon='MOD_BEVEL')
        layout.separator()
        layout.operator("nd.weighted_normal_bevel", icon='MOD_BEVEL')
        layout.operator("nd.solidify", icon='MOD_SOLIDIFY')
        layout.operator("nd.screw", icon='MOD_SCREW')
        layout.separator()
        layout.operator("nd.ring_and_bolt", icon='MESH_CYLINDER')


def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_main_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_main_menu)
    bpy.types.INFO_HT_header.append(draw_item)
   
    keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    entry = keymap.keymap_items.new("wm.call_menu", 'TWO', 'PRESS', shift = True)
    entry.properties.name = "nd.main_menu"

    keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_MT_main_menu)
    bpy.types.INFO_HT_header.remove(draw_item)
