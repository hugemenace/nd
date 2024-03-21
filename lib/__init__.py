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

import importlib
from . import events
from . import math
from . import objects
from . import overlay
from . import axis
from . import points
from . import viewport
from . import assets
from . import updates
from . import preferences
from . import addons
from . import collections
from . import modifiers
from . import numeric_input
from . import overlay_keys
from . import base_operator


registerables = (
    events,
    math,
    objects,
    overlay,
    axis,
    points,
    viewport,
    assets,
    updates,
    preferences,
    addons,
    collections,
    modifiers,
    numeric_input,
    overlay_keys,
    base_operator,
)


def reload():
    for registerable in registerables:
        importlib.reload(registerable)

    overlay.unregister_draw_handler()
    axis.unregister_axis_handler()
    points.unregister_points_handler()
