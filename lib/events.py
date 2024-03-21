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
# Contributors: Tristo (HM)
# ---

from math import copysign
from . preferences import get_preferences


def has(event): return event != None
def pressed(event, keys): return has(event) and event.type in keys and event.value == 'PRESS'
def clicked(event, types): return has(event) and event.type in types and event.value == 'RELEASE'
def detected(event, types): return has(event) and event.type in types


def capture_modifier_keys(cls, event=None, mouse_x=0):
    cls.key_no_modifiers = has(event) and not event.ctrl and not event.alt
    cls.key_ctrl = has(event) and event.ctrl and not event.alt
    cls.key_shift_ctrl = has(event) and event.shift and cls.key_ctrl
    cls.key_alt = has(event) and not event.ctrl and event.alt
    cls.key_shift_alt = has(event) and event.shift and cls.key_alt
    cls.key_ctrl_alt = has(event) and event.ctrl and event.alt
    cls.key_shift_ctrl_alt = has(event) and event.shift and cls.key_ctrl_alt
    cls.key_shift = has(event) and event.shift
    cls.key_shift_no_modifiers = has(event) and event.shift and cls.key_no_modifiers

    cls.key_undo = cls.key_ctrl and pressed(event, {'Z'})
    cls.key_redo = cls.key_ctrl and cls.key_shift and pressed(event, {'Z'})
    
    cls.key_one = pressed(event, {'ONE'})
    cls.key_two = pressed(event, {'TWO'})
    cls.key_three = pressed(event, {'THREE'})

    cls.key_numeric_input = pressed(event, {'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'ZERO', 'PERIOD', 'MINUS', 'NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_PERIOD', 'NUMPAD_MINUS', 'BACK_SPACE'})
    cls.key_reset = pressed(event, {get_preferences().overlay_reset_key})
    
    cls.key_toggle_pin_overlay = pressed(event, {get_preferences().overlay_pin_key})
    cls.key_toggle_operator_passthrough = pressed(event, {get_preferences().overlay_pause_key})
    
    cls.key_step_up = detected(event, {'WHEELUPMOUSE'}) or pressed(event, {'UP_ARROW'}) or pressed(event, {'RIGHT_ARROW'})
    cls.key_step_down = detected(event, {'WHEELDOWNMOUSE'}) or pressed(event, {'DOWN_ARROW'}) or pressed(event, {'LEFT_ARROW'})
    
    cls.key_confirm = clicked(event, {'LEFTMOUSE'}) or pressed(event, {'SPACE', 'RET', 'NUMPAD_ENTER'})
    cls.key_left_click = detected(event, {'LEFTMOUSE'})
    cls.key_confirm_alternative = pressed(event, {'SPACE', 'RET', 'NUMPAD_ENTER'})
    cls.key_cancel = clicked(event, {'RIGHTMOUSE'}) or pressed(event, {'ESC'})

    cls.key_movement_passthrough = detected(event, {'MIDDLEMOUSE'}) or (has(event) and event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or (has(event) and event.type.startswith('NDOF'))

    raw_mouse_delta = 0 if event == None else (event.mouse_x - cls.prev_mouse_x)

    cls.mouse_delta = raw_mouse_delta * get_preferences().mouse_value_scalar
    cls.mouse_value = cls.mouse_delta * (0.1 if cls.key_shift else 1)
    cls.prev_mouse_x = mouse_x if event == None else event.mouse_x
    
    cls.prev_mouse_travel = 0 if event == None else cls.mouse_travel
    cls.mouse_travel = 0 if event == None else cls.mouse_travel + raw_mouse_delta
    if cls.mouse_travel < 0 and cls.prev_mouse_travel < cls.mouse_travel:
        cls.mouse_travel = 0
    elif cls.mouse_travel > 0 and cls.prev_mouse_travel > cls.mouse_travel:
        cls.mouse_travel = 0

    cls.prev_mouse_travel_div = 0 if event == None else cls.mouse_travel_div
    cls.mouse_travel_div = cls.mouse_travel // get_preferences().mouse_value_steps
    if cls.prev_mouse_travel_div != cls.mouse_travel_div and abs(cls.mouse_travel) >= get_preferences().mouse_value_steps:
        cls.mouse_step = int(1 * copysign(1, cls.mouse_travel))
    else:
        cls.mouse_step = 0

    if event == None or cls.mouse_warped:
        cls.mouse_delta = 0
        cls.mouse_value = 0
        cls.mouse_warped = False

    cls.mouse_value_mag = cls.mouse_value * 100