import bpy
import bmesh
from math import radians
from mathutils import Euler
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property
from .. lib.events import capture_modifier_keys


mod_first_array = "Square Array A — ND"
mod_second_array = "Square Array B — ND"
mod_summon_list = [mod_first_array, mod_second_array]


class ND_OT_square_array(bpy.types.Operator):
    bl_idname = "nd.square_array"
    bl_label = "Square Array"
    bl_description = "Array an object in a square/grid like fashion"
    bl_options = {'UNDO'}


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        offset_factor = (self.base_offset_factor / 10.0) if self.key_shift else self.base_offset_factor

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
            if self.key_ctrl or self.key_ctrl_alt:
                self.base_offset_factor = min(1, self.base_offset_factor * 10.0)

        elif self.key_decrease_factor:
            if self.key_ctrl or self.key_ctrl_alt:
                self.base_offset_factor = max(0.001, self.base_offset_factor / 10.0)

        elif self.key_step_up:
            if self.key_alt:
                if self.key_shift:
                    self.second_axis = (self.second_axis + 1) % 3
                else:
                    self.first_axis = (self.first_axis + 1) % 3
            elif self.key_ctrl:
                self.first_offset += offset_factor
            elif self.key_ctrl_alt:
                self.second_offset += offset_factor
            else:
                if self.key_shift:
                    self.second_count = self.second_count + 1
                else:
                    self.first_count = self.first_count + 1

            self.dirty = True
            
        elif self.key_step_down:
            if self.key_alt:
                if self.key_shift:
                    self.second_axis = (self.second_axis - 1) % 3
                else:
                    self.first_axis = (self.first_axis - 1) % 3
            elif self.key_ctrl:
                self.first_offset -= offset_factor
            elif self.key_ctrl_alt:
                self.second_offset -= offset_factor
            else:
                if self.key_shift:
                    self.second_count = max(2, self.second_count - 1)
                else:
                    self.first_count = max(2, self.first_count - 1)

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
        self.base_offset_factor = 0.01

        mods = context.active_object.modifiers
        mod_names = list(map(lambda x: x.name, mods))
        previous_op = all(m in mod_names for m in mod_summon_list)

        if previous_op:
            self.summon_old_operator(context, mods)
        else:
            self.prepare_new_operator(context)

        self.operate(context)

        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 1


    def prepare_new_operator(self, context):
        self.summoned = False

        self.first_axis = 0
        self.second_axis = 1
        self.first_count = 2
        self.second_count = 2
        self.first_offset = 2
        self.second_offset = 2

        self.add_first_array_modifier(context)
        self.add_second_array_modifier(context)


    def summon_old_operator(self, context, mods):
        self.summoned = True

        self.first_array = mods[mod_first_array]
        self.second_array = mods[mod_second_array]

        self.first_count_prev = self.first_count = self.first_array.count
        self.second_count_prev = self.second_count = self.second_array.count

        first_axis = 0
        first_offset = 0
        for i in range(3):
            offset = self.first_array.relative_offset_displace[i]
            if offset != 0:
                first_axis = i
                first_offset = offset
                break

        self.first_axis_prev = self.first_axis = first_axis
        self.first_offset_prev = self.first_offset = first_offset

        second_axis = 0
        second_offset = 0
        for i in range(3):
            offset = self.second_array.relative_offset_displace[i]
            if offset != 0:
                second_axis = i
                second_offset = offset
                break
        
        self.second_axis_prev = self.second_axis = second_axis
        self.second_offset_prev = self.second_offset = second_offset



    def add_first_array_modifier(self, context):
        array = context.object.modifiers.new('Square Array A — ND', 'ARRAY')
        array.use_relative_offset = True

        self.first_array = array
    
    
    def add_second_array_modifier(self, context):
        array = context.object.modifiers.new('Square Array B — ND', 'ARRAY')
        array.use_relative_offset = True

        self.second_array = array
    

    def operate(self, context):
        self.first_array.count = self.first_count
        self.first_array.relative_offset_displace = [self.first_offset if i == self.first_axis else 0 for i in range(3)]
        self.second_array.count = self.second_count
        self.second_array.relative_offset_displace = [self.second_offset if i == self.second_axis else 0 for i in range(3)]

        self.dirty = False


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        if not self.summoned:
            bpy.ops.object.modifier_remove(modifier=self.first_array.name)
            bpy.ops.object.modifier_remove(modifier=self.second_array.name)

        if self.summoned:
            self.first_array.count = self.first_count_prev
            self.first_array.relative_offset_displace = [self.first_offset_prev if i == self.first_axis_prev else 0 for i in range(3)]
            self.second_array.count = self.second_count_prev
            self.second_array.relative_offset_displace = [self.second_offset_prev if i == self.second_axis_prev else 0 for i in range(3)]
        
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_property(
        self, 
        "A Count: {0}  /  B Count: {1}".format(self.first_count, self.second_count),
        "(±1)",
        active=self.key_no_modifiers,
        alt_mode=self.key_shift_no_modifiers)

    draw_property(
        self, 
        "A Axis: {0}  /  B Axis: {1}".format(['X', 'Y', 'Z'][self.first_axis], ['X', 'Y', 'Z'][self.second_axis]),
        "Alt (X, Y, Z)",
        active=self.key_alt,
        alt_mode=self.key_shift_alt)

    draw_property(
        self,
        "A Offset: {0:.3f}".format(self.first_offset),
        "Ctrl (±{0:.1f})  |  Shift + Ctrl (±{1:.1f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=self.key_ctrl,
        alt_mode=self.key_shift_ctrl)

    draw_property(
        self,
        "B Offset: {0:.3f}".format(self.second_offset),
        "Ctrl + Alt (±{0:.1f})  |  Shift + Ctrl + Alt (±{1:.1f})".format(self.base_offset_factor * 1000, (self.base_offset_factor / 10) * 1000),
        active=self.key_ctrl_alt,
        alt_mode=self.key_shift_ctrl_alt)


def menu_func(self, context):
    self.layout.operator(ND_OT_square_array.bl_idname, text=ND_OT_square_array.bl_label)


def register():
    bpy.utils.register_class(ND_OT_square_array)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ND_OT_square_array)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_draw_handler()
