# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

from math import inf

key_mapping = {
    'ZERO': '0',
    'ONE': '1',
    'TWO': '2',
    'THREE': '3',
    'FOUR': '4',
    'FIVE': '5',
    'SIX': '6',
    'SEVEN': '7',
    'EIGHT': '8',
    'NINE': '9',
    'NUMPAD_0': '0',
    'NUMPAD_1': '1',
    'NUMPAD_2': '2',
    'NUMPAD_3': '3',
    'NUMPAD_4': '4',
    'NUMPAD_5': '5',
    'NUMPAD_6': '6',
    'NUMPAD_7': '7',
    'NUMPAD_8': '8',
    'NUMPAD_9': '9',
    'MINUS': '-',
    'NUMPAD_MINUS': '-',
    'PERIOD': '.',
    'NUMPAD_PERIOD': '.',
}

def update_stream(input_stream, type):
    ok, value, raw = input_stream

    if type in key_mapping:
        next = key_mapping[type]
        raw = raw + next if raw else next
    
    if type == 'BACK_SPACE':
        raw = raw[:-1] if raw else None

    try:
        value = float(raw)
        ok = True
    except:
        ok = False

    if not raw:
        return True, None, None

    return ok, value, raw


def no_stream(input_stream):
    ok, value, raw = input_stream

    return value is None


def get_stream_value(input_stream, factor=1, default=0, minValue=-inf, maxValue=inf):
    ok, value, raw = input_stream

    computed_value = value * factor if ok and value is not None else default

    return max(minValue, min(maxValue, computed_value))


def new_stream():
    return True, None, None