import bpy
import bmesh
from math import radians


class ND_OT_faux_bevel(bpy.types.Operator):
    bl_idname = "nd.faux_bevel"
    bl_label = "Faux Bevel"
    bl_description = "Adds a single segment bevel and a weighted normal modifier"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        width_factor = 0.0001 if event.shift else 0.001

        if event.type == 'WHEELUPMOUSE':
            self.bevel_width += width_factor
            
        elif event.type == 'WHEELDOWNMOUSE':
            self.bevel_width = max(0, self.bevel_width - width_factor)
        
        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.revert(context)

            return {'CANCELLED'}

        self.operate(context)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.bevel_width = 0.001

        self.add_bevel_modifier(context)
        self.add_weighted_normal_modifer(context)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1


    def add_bevel_modifier(self, context):
        bevel = context.object.modifiers.new("ND — Bevel", 'BEVEL')
        bevel.segments = 1
        bevel.width = self.bevel_width

        self.bevel = bevel
    

    def add_weighted_normal_modifer(self, context):
        wn = context.object.modifiers.new("ND — Weighted Normal", 'WEIGHTED_NORMAL')
        wn.weight = 100

        self.wn = wn


    def operate(self, context):
        self.bevel.width = self.bevel_width


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.bevel.name)
        bpy.ops.object.modifier_remove(modifier=self.wn.name)


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
