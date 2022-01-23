import bpy
import bmesh
from math import radians


class ND_OT_faux_bevel(bpy.types.Operator):
    """Adds a single segment bevel and a weighted normal modifier"""
    bl_idname = "nd.faux_bevel"
    bl_label = "Faux Bevel"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}


    def modal(self, context, event):
        if event.type == 'WHEELUPMOUSE':
            step = 0.0001 if event.shift else 0.001
            self.adjust_bevel_width(step)
            
        elif event.type == 'WHEELDOWNMOUSE':
            step = 0.0001 if event.shift else 0.001
            self.adjust_bevel_width(-step)
        
        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        return self.handle_modal(context)
    

    def execute(self, context):
        return self.handle_modal(context)


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1


    def handle_modal(self, context):
        self.add_bevel_modifier(context)
        self.add_weighted_normal_modifer(context)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def add_bevel_modifier(self, context):
        bevel = context.object.modifiers.new("ND — Bevel", 'BEVEL')
        bevel.segments = 1
        bevel.width = 0

        self.bevel = bevel
    

    def add_weighted_normal_modifer(self, context):
        wn = context.object.modifiers.new("ND — Weighted Normal", 'WEIGHTED_NORMAL')
        wn.weight = 100


    def adjust_bevel_width(self, amount):
        self.bevel.width += amount


def menu_func(self, context):
    self.layout.operator(ND_OT_faux_bevel.bl_idname, text=ND_OT_faux_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_faux_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_faux_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
