def capture_modifier_keys(cls, event=None):
    cls.key_no_modifiers = True if event is None else not event.ctrl and not event.alt
    cls.key_ctrl = False if event is None else event.ctrl and not event.alt
    cls.key_shift_ctrl = False if event is None else event.shift and cls.key_ctrl
    cls.key_alt = False if event is None else not event.ctrl and event.alt
    cls.key_shift_alt = False if event is None else event.shift and cls.key_alt
    cls.key_ctrl_alt = False if event is None else event.ctrl and event.alt
    cls.key_shift_ctrl_alt = False if event is None else event.shift and cls.key_ctrl_alt
    cls.key_shift =False if event is None else event.shift
    cls.key_shift_no_modifiers = False if event is None else event.shift and cls.key_no_modifiers
    cls.key_toggle_pin_overlay = False if event is None else event.type == 'P' and event.value == 'PRESS'
    cls.key_toggle_operator_passthrough = False if event is None else event.type == 'BACK_SLASH' and event.value == 'PRESS'
    cls.key_increase_factor = False if event is None else event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'} and event.value == 'PRESS'
    cls.key_decrease_factor = False if event is None else event.type in {'MINUS', 'NUMPAD_MINUS'} and event.value == 'PRESS'
    cls.key_step_up = False if event is None else event.type == 'WHEELUPMOUSE'
    cls.key_step_down = False if event is None else event.type == 'WHEELDOWNMOUSE'
    cls.key_confirm = False if event is None else event.type == 'LEFTMOUSE'
    cls.key_confirm_alternative = False if event is None else event.type == 'SPACE'
    cls.key_cancel = False if event is None else event.type in {'RIGHTMOUSE', 'ESC'}
    cls.key_movement_passthrough = False if event is None else event.type == 'MIDDLEMOUSE' or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}) or event.type.startswith('NDOF')