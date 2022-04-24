from . preferences import get_preferences


def has(event): return event != None
def pressed(event, keys): return has(event) and event.type in keys and event.value == 'PRESS'
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
    
    cls.key_one = pressed(event, {'ONE'})
    cls.key_two = pressed(event, {'TWO'})
    cls.key_three = pressed(event, {'THREE'})
    
    cls.key_toggle_pin_overlay = pressed(event, {get_preferences().overlay_pin_key})
    cls.key_toggle_operator_passthrough = pressed(event, {get_preferences().overlay_pause_key})
    
    cls.key_increase_factor = pressed(event, {'PLUS', 'EQUAL', 'NUMPAD_PLUS'})
    cls.key_decrease_factor = pressed(event, {'MINUS', 'NUMPAD_MINUS'})

    cls.key_step_up = detected(event, {'WHEELUPMOUSE'}) or pressed(event, {'UP_ARROW'}) or pressed(event, {'RIGHT_ARROW'}) or pressed(event, {'D'}) or pressed(event, {'W'})
    cls.key_step_down = detected(event, {'WHEELDOWNMOUSE'}) or pressed(event, {'DOWN_ARROW'}) or pressed(event, {'LEFT_ARROW'}) or pressed(event, {'A'}) or pressed(event, {'S'})
    
    cls.key_confirm = detected(event, {'LEFTMOUSE'})
    cls.key_confirm_alternative = pressed(event, {'SPACE'})
    cls.key_cancel = detected(event, {'RIGHTMOUSE'}) or pressed(event, {'ESC'})

    cls.key_movement_passthrough = detected(event, {'MIDDLEMOUSE'}) or (has(event) and event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or (has(event) and event.type.startswith('NDOF'))

    cls.mouse_delta = 0 if event == None else (event.mouse_x - cls.prev_mouse_x) * get_preferences().mouse_value_scalar
    cls.mouse_value = cls.mouse_delta * (0.1 if cls.key_shift else 1)
    cls.prev_mouse_x = mouse_x if event == None else event.mouse_x

    if event == None or cls.mouse_warped:
        cls.mouse_delta = 0
        cls.mouse_value = 0
        cls.mouse_warped = False

    cls.mouse_value_mag = cls.mouse_value * 100