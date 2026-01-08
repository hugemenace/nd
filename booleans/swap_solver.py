# ███╗   ██╗██████╗
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝
#
# ND (Non-Destructive) Blender Add-on
# Copyright (C) 2024 Tristan S. & Ian J. (HugeMenace)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ---
# Contributors: Tristo (HM), Ian (HM)
# ---

import bpy
import bmesh
from .. lib.base_operator import BaseOperator
from .. lib.overlay import update_overlay, init_overlay, toggle_pin_overlay, toggle_operator_passthrough, register_draw_handler, unregister_draw_handler, draw_header, draw_property, draw_hint
from .. lib.events import capture_modifier_keys, pressed
from .. lib.polling import ctx_obj_mode, list_ok, app_minor_version, obj_moddable


class ND_OT_swap_solver(BaseOperator):
    bl_idname = "nd.swap_solver"
    bl_label = "Swap Solver"
    bl_description = "Swap the solver mode of the boolean modifiers referencing the selected utility objects"
    bl_options = {'UNDO'}


    key_callbacks = {
        'S': lambda cls, context, event: cls.handle_toggle_solve_mode(context, event),
    }

    modal_config = {
        'MOVEMENT_PASSTHROUGH': True,
        'ON_CANCEL': lambda cls, context: cls.revert(context),
        'ON_CONFIRM': lambda cls, context: cls.finish(context),
    }


    @classmethod
    def poll(cls, context):
        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        return ctx_obj_mode(context) and list_ok(mesh_objects)


    def do_invoke(self, context, event):
        self.solve_mode = None
        self.boolean_mods = set()
        self.boolean_mods_snapshot = {}

        self.solver_options = ['FAST', 'EXACT']
        if app_minor_version() >= (4, 5):
            self.solver_options.append('MANIFOLD')
        if app_minor_version() >= (5, 0):
            self.solver_options[0] = 'FLOAT'

        all_scene_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        mesh_object_names = [obj.name for obj in context.selected_objects if obj.type == 'MESH']
        fast_solver_count = 0
        exact_solver_count = 0

        for obj in all_scene_objects:
            mods = [mod for mod in obj.modifiers if mod.type == 'BOOLEAN']
            for mod in mods:
                if mod.object and mod.object.name in mesh_object_names:
                    self.boolean_mods.add(mod)

        for obj in context.selected_objects:
            if not obj_moddable(obj):
                continue
            mods = [mod for mod in obj.modifiers if mod.type == 'BOOLEAN']
            self.boolean_mods.update(mods)

        for mod in self.boolean_mods:
            self.boolean_mods_snapshot[mod] = mod.solver

        detected_solver_types = []
        for mod in self.boolean_mods:
            detected_solver_types.append(mod.solver)

        if len(set(detected_solver_types)) == 1:
            self.solve_mode = detected_solver_types[0]

        capture_modifier_keys(self, None, event.mouse_x)

        init_overlay(self, event)
        register_draw_handler(self, draw_text_callback)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def handle_toggle_solve_mode(self, context, event):
        if self.solve_mode is None:
            self.solve_mode = self.solver_options[0]
            return

        solve_mode_index = self.solver_options.index(self.solve_mode)
        self.solve_mode = self.solver_options[(solve_mode_index + 1) % len(self.solver_options)]


    def operate(self, context):
        for mod in self.boolean_mods:
            mod.solver = self.solve_mode


    def finish(self, context):
        unregister_draw_handler()


    def revert(self, context):
        for mod in self.boolean_mods:
            mod.solver = self.boolean_mods_snapshot[mod]

        unregister_draw_handler()


def draw_text_callback(self):
    draw_header(self)

    solver_str = self.solve_mode.capitalize() if self.solve_mode else "Mixed"
    draw_hint(self, f"Solver [S]: {solver_str}", self.list_options_str(self.solver_options))


def register():
    bpy.utils.register_class(ND_OT_swap_solver)


def unregister():
    bpy.utils.unregister_class(ND_OT_swap_solver)
    unregister_draw_handler()
