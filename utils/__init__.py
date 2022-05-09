# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import importlib
from . import name_sync
from . import set_lod_suffix
from . import set_origin
from . import smooth
from . import seams
from . import hydrate
from . import clear_vgs
from . import cycle
from . import flare
from . import points
from . import triangulate


registerables = (
    name_sync,
    set_lod_suffix,
    set_origin,
    smooth,
    seams,
    hydrate,
    clear_vgs,
    cycle,
    flare,
    points,
    triangulate
)


def reload():
    for registerable in registerables:
        importlib.reload(registerable)


def register():
    for registerable in registerables:
        registerable.register()


def unregister():
    for registerable in registerables:
        registerable.unregister()
