from . preferences import get_preferences

def capture_modifier_keys(cls, event=None):
    cls.key_no_modifiers = False if event == None else not event.ctrl and not event.alt
    cls.key_ctrl = False if event == None else event.ctrl and not event.alt
    cls.key_shift_ctrl = False if event == None else event.shift and cls.key_ctrl
    cls.key_alt = False if event == None else not event.ctrl and event.alt
    cls.key_shift_alt = False if event == None else event.shift and cls.key_alt
    cls.key_ctrl_alt = False if event == None else event.ctrl and event.alt
    cls.key_shift_ctrl_alt = False if event == None else event.shift and cls.key_ctrl_alt
    cls.key_shift = False if event == None else event.shift
    cls.key_shift_no_modifiers = False if event == None else event.shift and cls.key_no_modifiers
    cls.key_toggle_pin_overlay = False if event == None else event.type == get_preferences().overlay_pin_key and event.value == 'PRESS'
    cls.key_one = False if event == None else event.type == 'ONE' and event.value == 'PRESS'
    cls.key_two = False if event == None else event.type == 'TWO' and event.value == 'PRESS'
    cls.key_three = False if event == None else event.type == 'THREE' and event.value == 'PRESS'
    cls.key_toggle_operator_passthrough = False if event == None else event.type == get_preferences().overlay_pause_key and event.value == 'PRESS'
    cls.key_increase_factor = False if event == None else event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'} and event.value == 'PRESS'
    cls.key_decrease_factor = False if event == None else event.type in {'MINUS', 'NUMPAD_MINUS'} and event.value == 'PRESS'

    cls.key_step_up = False if event == None else event.type == 'WHEELUPMOUSE' or (
        event.value == 'PRESS' and event.type == 'UP_ARROW') or (
            event.value == 'PRESS' and event.type == 'RIGHT_ARROW') or (
                event.value == 'PRESS' and event.type == 'D') or (
                    event.value == 'PRESS' and event.type == 'W')

    cls.key_step_down = False if event == None else event.type == 'WHEELDOWNMOUSE' or (
        event.value == 'PRESS' and event.type == 'DOWN_ARROW') or (
            event.value == 'PRESS' and event.type == 'LEFT_ARROW') or (
                event.value == 'PRESS' and event.type == 'A') or (
                    event.value == 'PRESS' and event.type == 'S')
    
    cls.key_confirm = False if event == None else event.type == 'LEFTMOUSE'
    cls.key_confirm_alternative = False if event == None else event.type == 'SPACE'
    cls.key_cancel = False if event == None else event.type in {'RIGHTMOUSE', 'ESC'}

    cls.key_movement_passthrough = False if event == None else event.type == 'MIDDLEMOUSE' or (
        event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF')
