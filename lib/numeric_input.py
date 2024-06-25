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


def set_stream(value):
    return True, value, str(value)


def no_stream(input_stream):
    ok, value, raw = input_stream

    return value is None


def has_stream(input_stream):
    ok, value, raw = input_stream

    return value is not None


def get_stream_value(input_stream, factor=1, default=0, min_value=-inf, max_value=inf):
    ok, value, raw = input_stream

    computed_value = value * factor if ok and value is not None else default

    return max(min_value, min(max_value, computed_value))


def new_stream():
    return True, None, None
