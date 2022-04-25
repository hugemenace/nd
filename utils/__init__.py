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


def reload():
    importlib.reload(name_sync)
    importlib.reload(set_lod_suffix)
    importlib.reload(set_origin)
    importlib.reload(smooth)
    importlib.reload(seams)
    importlib.reload(hydrate)


def register():
    name_sync.register()
    set_lod_suffix.register()
    set_origin.register()
    smooth.register()
    seams.register()
    hydrate.register()


def unregister():
    name_sync.unregister()
    set_lod_suffix.unregister()
    set_origin.unregister()
    smooth.unregister()
    seams.unregister()
    hydrate.unregister()
