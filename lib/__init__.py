# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

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
from . import collections
from . import overlay_keys


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
    collections,
    overlay_keys
)


def reload():
    for registerable in registerables:
        importlib.reload(registerable)

    overlay.unregister_draw_handler()
    axis.unregister_axis_handler()
    points.unregister_points_handler()
