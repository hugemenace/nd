# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)
# 
# ---
# Contributors: Tristo (HM)
# ---

import bpy
import bmesh
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed


class ND_OT_swap_solver(bpy.types.Operator):
    bl_idname = "nd.swap_solver"
    bl_label = "Swap Solver"
    bl_description = "Swap the solver mode of the boolean(s) using this utility"
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

        elif pressed(event, {'S'}):
            if self.solve_mode is None:
                self.solve_mode = 'FAST'
            elif self.solve_mode == 'FAST':
                self.solve_mode = 'EXACT'
            elif self.solve_mode == 'EXACT':
                self.solve_mode = 'FAST'

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

        self.solve_mode = None

        self.all_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        self.boolean_mods = []
        self.fast_solver_count = 0
        self.exact_solver_count = 0
        
        for obj in self.all_objects:
            boolean_mods = [mod for mod in obj.modifiers if mod.type == 'BOOLEAN']
            if boolean_mods:
                self.boolean_mods += boolean_mods
                for mod in boolean_mods:
                    if mod.solver == 'FAST':
                        self.fast_solver_count += 1
                    elif mod.solver == 'EXACT':
                        self.exact_solver_count += 1
        
        if self.fast_solver_count == len(self.boolean_mods):
            self.solve_mode = 'FAST'
        elif self.exact_solver_count == len(self.boolean_mods):
            self.solve_mode = 'EXACT'
            
        capture_modifier_keys(self)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) > 0 and all(obj.type == 'MESH' for obj in context.selected_objects)

    
    def operate(self, context):
        for mod in self.boolean_mods:
            mod.solver = self.solve_mode

        self.dirty = False

    
    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    draw_hint(
        self,
        "Solver [S]: {0}".format(self.solve_mode.capitalize() if self.solve_mode else "Mixed"),
        "Select the solver mode (Fast, Exact)")


def menu_func(self, context):
    self.layout.operator(ND_OT_swap_solver.bl_idname, text=ND_OT_swap_solver.bl_label)


def register():
    bpy.utils.register_class(ND_OT_swap_solver)


def unregister():
    bpy.utils.unregister_class(ND_OT_swap_solver)
    unregister_draw_handler()
