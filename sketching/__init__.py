# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import importlib
from . import view_align
from . import geo_lift
from . import single_vertex
from . import make_manifold


registerables = (
    view_align,
    geo_lift,
    single_vertex,
    make_manifold
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
    