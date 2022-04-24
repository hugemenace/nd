import bpy
from .. import bl_info


class ND_MT_boolean_menu(bpy.types.Menu):
    bl_label = "Booleans"
    bl_idname = "ND_MT_boolean_menu"


    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nd.bool_vanilla", text="Difference", icon='MOD_BOOLEAN').mode = 'DIFFERENCE'
        layout.operator("nd.bool_vanilla", text="Union", icon='MOD_BOOLEAN').mode = 'UNION'
        layout.operator("nd.bool_vanilla", text="Intersect", icon='MOD_BOOLEAN').mode = 'INTERSECT'
        layout.operator("nd.bool_slice", icon='MOD_BOOLEAN')
        

def draw_item(self, context):
    layout = self.layout
    layout.menu(ND_MT_boolean_menu.bl_idname)


def register():
    bpy.utils.register_class(ND_MT_boolean_menu)
   

def unregister():
    bpy.utils.unregister_class(ND_MT_boolean_menu)
