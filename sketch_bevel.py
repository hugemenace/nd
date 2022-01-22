import bpy


class ND_OT_sketch_bevel(bpy.types.Operator):
    """Adds a vertex group based bevel and weld modifier"""
    bl_idname = "nd.sketch_bevel"
    bl_label = "Sketch Bevel"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}


    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            factor = 0.001 if event.shift else 0.01
            self.adjust_bevel_width(event.mouse_x * factor)
        
        elif event.type == 'WHEELUPMOUSE':
            self.adjust_bevel_segments(1)
            
        elif event.type == 'WHEELDOWNMOUSE':
            self.adjust_bevel_segments(-1)

        elif event.type == 'LEFTMOUSE':
            self.add_weld_modifier(context)

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        return self.handle_modal(context)
    

    def execute(self, context):
        return self.handle_modal(context)


    def handle_modal(self, context):
        if context.object and context.object.type == 'MESH' and context.mode == 'EDIT_MESH' and context.object.data.total_vert_sel > 0:
            self.add_vertex_group(context)
            self.add_bevel_modifier(context)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


    def add_vertex_group(self, context):
        context.object.vertex_groups.new(name = "ND — Bevel")
        bpy.ops.object.vertex_group_assign()
    

    def add_bevel_modifier(self, context):
        bevel = context.object.modifiers.new("ND — Sketch Bevel", type = 'BEVEL')
        bevel.affect = 'VERTICES'
        bevel.limit_method = 'VGROUP'
        bevel.vertex_group = context.object.vertex_groups[-1].name
        bevel.segments = 8

        self.bevel = bevel
    

    def add_weld_modifier(self, context):
        weld = context.object.modifiers.new("ND — Weld", type = 'WELD')
        weld.merge_threshold = 0.00001


    def adjust_bevel_width(self, width):
        self.bevel.width = width


    def adjust_bevel_segments(self, amount):
        self.bevel.segments += amount


def menu_func(self, context):
    self.layout.operator(ND_OT_sketch_bevel.bl_idname, text=ND_OT_sketch_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_sketch_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_sketch_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
