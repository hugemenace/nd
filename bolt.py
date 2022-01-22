import bpy
import bmesh
from math import radians


class NDBolt(bpy.types.Operator):
    """Adds a bolt using the 3D cursor position & rotation"""
    bl_idname = "nd.bolt"
    bl_label = "Bolt (& Hole Cutter)"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}


    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            factor = 0.001 if event.shift else 0.01
            
            if event.alt:
                self.solidify.thickness = max(0, event.mouse_x * factor)
            elif event.ctrl:
                self.displace.strength = event.mouse_x * factor
            else:
                self.screwX.screw_offset = max(0, event.mouse_x * factor)
        
        elif event.type == 'WHEELUPMOUSE':
            self.adjust_segments(1)
            
        elif event.type == 'WHEELDOWNMOUSE':
            self.adjust_segments(-1)

        elif event.type == 'LEFTMOUSE':
            self.handle_optional_boolean_ops(context)
            
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.add_object(context)
        self.add_screw_x_modifier()
        self.add_screw_z_modifer()
        self.add_decimate_modifier()
        self.add_displace_modifier()
        self.add_solidify_modifier()
        self.align_object_to_3d_cursor(context)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    

    def add_object(self, context):
        mesh = bpy.data.meshes.new("ND — Bolt")
        obj = bpy.data.objects.new("ND — Bolt", mesh)
        bpy.data.collections[context.collection.name].objects.link(obj)
        bm = bmesh.new()
        bm.verts.new()
        bm.to_mesh(mesh)
        bm.free()
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = radians(30)

        self.obj = obj
    

    def add_screw_x_modifier(self):
        screwX = self.obj.modifiers.new("ND — Radius", 'SCREW')
        screwX.axis = 'X'
        screwX.angle = 0
        screwX.screw_offset = 1
        screwX.steps = 1
        screwX.render_steps = 1
        screwX.use_merge_vertices = True

        self.screwX = screwX
    

    def add_screw_z_modifer(self):
        screwZ = self.obj.modifiers.new("ND — Segments", 'SCREW')
        screwZ.axis = 'Z'
        screwZ.steps = 32
        screwZ.render_steps = 32
        screwZ.use_merge_vertices = True

        self.screwZ = screwZ


    def adjust_segments(self, amount):
        self.screwZ.steps = max(3, self.screwZ.steps + amount)
        self.screwZ.render_steps = max(3, self.screwZ.render_steps + amount)


    def add_decimate_modifier(self):
        decimate = self.obj.modifiers.new("ND — Decimate", 'DECIMATE')
        decimate.decimate_type = 'DISSOLVE'
        decimate.angle_limit = radians(.25)
    

    def add_displace_modifier(self):
        displace = self.obj.modifiers.new("ND — Displace", 'DISPLACE')
        displace.mid_level = 0.5
        displace.strength = 0
        
        self.displace = displace
    

    def add_solidify_modifier(self):
        solidify = self.obj.modifiers.new("ND — Solidify", 'SOLIDIFY')
        solidify.thickness = 0.50
        solidify.offset = 1

        self.solidify = solidify
    

    def align_object_to_3d_cursor(self, context):
        self.obj.location = context.scene.cursor.location
        self.obj.rotation_euler = context.scene.cursor.rotation_euler
        

    def handle_optional_boolean_ops(self, context):
        if len(context.selected_objects) > 1:
            self.obj.display_type = 'WIRE'
            targets = [o for o in context.selected_objects if not (o == self.obj)]

            for target in targets:
                boolean = target.modifiers.new("ND — Bolt Hole", 'BOOLEAN')
                boolean.object = self.obj
        else:
            self.obj.display_type = 'SOLID'


def menu_func(self, context):
    self.layout.operator(NDBolt.bl_idname, text=NDBolt.bl_label)


def register():
    bpy.utils.register_class(NDBolt)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(NDBolt)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
