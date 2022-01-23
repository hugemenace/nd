import bpy
import bmesh
from bpy.props import IntProperty


class ND_OT_sketch_bevel(bpy.types.Operator):
    bl_idname = "nd.sketch_bevel"
    bl_label = "Sketch Bevel"
    bl_description = "Adds a vertex group bevel and weld modifier"
    bl_options = {'UNDO'}

    def modal(self, context, event):
        width_factor = 0.001 if event.shift else 0.01
        segment_factor = 1 if event.shift else 2

        if event.type == 'WHEELUPMOUSE':
            if event.alt:
                self.segments = 2 if self.segments == 1 else self.segments + segment_factor
            else:
                self.width += width_factor
        
        elif event.type == 'WHEELDOWNMOUSE':
            if event.alt:
                self.segments = max(1, self.segments - segment_factor)
            else:
                self.width = max(0, self.width - width_factor)

        elif event.type == 'LEFTMOUSE':
            self.finish(context)

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.revert(context)

            return {'CANCELLED'}

        self.operate(context)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.segments = 1
        self.width = 0.001

        self.add_vertex_group(context)
        self.add_bevel_modifier(context)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH':
            mesh = bmesh.from_edit_mesh(context.object.data)
            return len([vert for vert in mesh.verts if vert.select]) >= 1


    def add_vertex_group(self, context):
        vgroup = context.object.vertex_groups.new(name="ND — Bevel")
        bpy.ops.object.vertex_group_assign()

        self.vgroup = vgroup


    def add_bevel_modifier(self, context):
        bevel = context.object.modifiers.new("ND — Sketch Bevel", type='BEVEL')
        bevel.affect = 'VERTICES'
        bevel.limit_method = 'VGROUP'
        bevel.vertex_group = self.vgroup.name
        bevel.segments = self.segments
        bevel.width = self.width

        self.bevel = bevel
    

    def add_weld_modifier(self, context):
        weld = context.object.modifiers.new("ND — Weld", type='WELD')
        weld.merge_threshold = 0.00001

        self.weld = weld


    def operate(self, context):
        self.bevel.width = self.width
        self.bevel.segments = self.segments


    def finish(self, context):
        self.add_weld_modifier(context)
    

    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.bevel.name)
        context.object.vertex_groups.remove(self.vgroup)


def menu_func(self, context):
    self.layout.operator(
        ND_OT_sketch_bevel.bl_idname, 
        text=ND_OT_sketch_bevel.bl_label)


def register():
    bpy.utils.register_class(ND_OT_sketch_bevel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_sketch_bevel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
