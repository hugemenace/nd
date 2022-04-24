import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys
from .. lib.preferences import get_preferences
from .. lib.collections import move_to_utils_collection


mod_lattice = "Lattice — ND L"


class ND_OT_lattice(bpy.types.Operator):
    bl_idname = "nd.lattice"
    bl_label = "Lattice"
    bl_description = "Adds a lattice modifier to the selected object"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        elif self.key_toggle_pin_overlay:
            toggle_pin_overlay(self, event)

        elif self.operator_passthrough:
            update_overlay(self, context, event)

            return {'PASS_THROUGH'}

        elif self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        elif self.key_increase_factor:
            if self.key_no_modifiers:
                self.base_width_factor = min(1, self.base_width_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_no_modifiers:
                self.base_width_factor = max(0.001, self.base_width_factor / 10.0)
        
        elif self.key_step_up:
            if self.key_shift_no_modifiers:
                self.uniform = not self.uniform
                if self.uniform:
                    self.lattice_points_v = self.lattice_points_u
                    self.lattice_points_w = self.lattice_points_u
            elif self.uniform:
                self.lattice_points_u += 1
                self.lattice_points_v = self.lattice_points_u
                self.lattice_points_w = self.lattice_points_u
            else:
                if self.key_no_modifiers:
                    self.lattice_points_u += 1
                elif self.key_alt:
                    self.lattice_points_v += 1
                elif self.key_ctrl:
                    self.lattice_points_w += 1

            self.dirty = True
        
        elif self.key_step_down:
            if self.key_shift_no_modifiers:
                self.uniform = not self.uniform
                if self.uniform:
                    self.lattice_points_v = self.lattice_points_u
                    self.lattice_points_w = self.lattice_points_u
            elif self.uniform:
                self.lattice_points_u = max(2, self.lattice_points_u - 1)
                self.lattice_points_v = self.lattice_points_u
                self.lattice_points_w = self.lattice_points_u
            else:
                if self.key_no_modifiers:
                    self.lattice_points_u = max(2, self.lattice_points_u - 1)
                elif self.key_alt:
                    self.lattice_points_v = max(2, self.lattice_points_v - 1)
                elif self.key_ctrl:
                    self.lattice_points_w = max(2, self.lattice_points_w - 1)
            
            self.dirty = True
        
        elif self.key_confirm:
            self.finish(context)

            return {'FINISHED'}

        elif self.key_movement_passthrough:
            return {'PASS_THROUGH'}

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.dirty = False

        self.uniform = True
        self.lattice_points_u = 2
        self.lattice_points_v = 2
        self.lattice_points_w = 2

        self.reference_object = context.object
        
        self.add_lattice_object(context)
        self.select_reference_object(context)
        self.add_lattice_modifier(context)

        self.operate(context)

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1 and context.object.type == 'MESH'


    def add_lattice_object(self, context):
        bpy.ops.object.duplicate()

        depsgraph = context.evaluated_depsgraph_get()
        object_eval = context.object.evaluated_get(depsgraph)
        context.object.modifiers.clear()

        bm = bmesh.new()
        bm.from_mesh(object_eval.data)
        bm.to_mesh(context.object.data)
        bm.free()

        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        eval_obj = context.active_object

        bpy.ops.object.add(type='LATTICE', enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))

        context.active_object.location = eval_obj.location
        context.active_object.rotation_euler = eval_obj.rotation_euler
        context.active_object.dimensions = eval_obj.dimensions * 1.001
        context.active_object.name = "ND — Lattice"
        context.active_object.data.name = "ND — Lattice"
        context.active_object.data.use_outside = True

        self.lattice_obj = context.active_object

        bpy.data.meshes.remove(eval_obj.data, do_unlink=True)


    def select_reference_object(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.reference_object.select_set(True)
        bpy.context.view_layer.objects.active = self.reference_object


    def select_lattice_object(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.lattice_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.lattice_obj


    def add_lattice_modifier(self, context):
        lattice = context.object.modifiers.new(mod_lattice, 'LATTICE')
        lattice.object = self.lattice_obj

        self.lattice = lattice

    
    def operate(self, context):
        self.lattice_obj.data.points_u = self.lattice_points_u
        self.lattice_obj.data.points_v = self.lattice_points_v
        self.lattice_obj.data.points_w = self.lattice_points_w

        self.dirty = False


    def finish(self, context):
        move_to_utils_collection(self.lattice_obj)
        self.select_lattice_object(context)

        unregister_draw_handler()


    def revert(self, context):
        bpy.ops.object.modifier_remove(modifier=self.lattice.name)
        bpy.data.lattices.remove(self.lattice_obj.data, do_unlink=True)

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)
    
    draw_property(
        self,
        "U Points: {0}  /  Uniform: {1}".format(self.lattice_points_u, "Yes" if self.uniform else "No"),
        "(±1)  |  Shift (Yes, No)",
        active=(self.uniform or self.key_no_modifiers),
        alt_mode=self.key_shift_no_modifiers)

    draw_property(
        self,
        "V Points: {0}".format(self.lattice_points_v),
        "(±1)",
        active=(self.uniform or self.key_alt),
        alt_mode=False)

    draw_property(
        self,
        "W Points: {0}".format(self.lattice_points_w),
        "(±1)",
        active=(self.uniform or self.key_ctrl),
        alt_mode=False)


def menu_func(self, context):
    self.layout.operator(ND_OT_lattice.bl_idname, text=ND_OT_lattice.bl_label)


def register():
    bpy.utils.register_class(ND_OT_lattice)


def unregister():
    bpy.utils.unregister_class(ND_OT_lattice)
    unregister_draw_handler()
