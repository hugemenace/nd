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
from . preferences import get_scene_unit_factor, get_scene_unit_suffix, get_scene_unit_scale, get_preferences
from .. lib.overlay import update_overlay, toggle_pin_overlay, toggle_operator_passthrough
from .. lib.events import capture_modifier_keys


class BaseOperator(bpy.types.Operator):
    bl_options = {'UNDO'}


    def generate_step_hint(self, regular, precise = None):
        if not precise:
            return f"(±{regular})"

        return f"(±{regular}  /  SHIFT ±{precise})"


    def generate_key_hint(self, key, hint):
        return f"{key}  —  {hint}"


    def operate(self, context):
        pass

    
    def invoke(self, context, event):
        self.unit_factor = get_scene_unit_factor()
        self.unit_suffix = get_scene_unit_suffix()
        self.unit_scale  = get_scene_unit_scale()

        self.unit_scaled_factor = self.unit_factor / self.unit_scale
        self.display_unit_scale = self.unit_scale / self.unit_factor

        unit_increment_size = get_preferences().unit_increment_size
        self.unit_step_hint = self.generate_step_hint(f"{(self.unit_scale * unit_increment_size):.2f}{self.unit_suffix}", f"{(self.unit_scale * 0.1 * unit_increment_size):.2f}{self.unit_suffix}")

        return self.do_invoke(context, event)


    def modal(self, context, event):
        capture_modifier_keys(self, event)

        self.step_size = ((0.1 if self.key_shift else 1) * self.unit_factor) * get_preferences().unit_increment_size

        if self.key_toggle_operator_passthrough:
            toggle_operator_passthrough(self)

        if self.key_toggle_pin_overlay:
            toggle_pin_overlay(self, event)

        if self.operator_passthrough:
            update_overlay(self, context, event)

            return {'PASS_THROUGH'}

        if self.key_cancel:
            self.revert(context)

            return {'CANCELLED'}

        # Subclass hook-in
        override_return = self.do_modal(context, event)

        if self.dirty:
            self.operate(context)

        update_overlay(self, context, event)

        return override_return if override_return else {'RUNNING_MODAL'}
