# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import importlib
from . import vanilla
from . import boolean_slice
from . import boolean_inset


def reload():
    importlib.reload(vanilla)
    importlib.reload(boolean_slice)
    importlib.reload(boolean_inset)


def register():
    vanilla.register()
    boolean_slice.register()
    boolean_inset.register()


def unregister():
    vanilla.unregister()
    boolean_slice.unregister()
    boolean_inset.unregister()
