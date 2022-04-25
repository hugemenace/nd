# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import importlib
from . import blank_sketch
from . import view_align
from . import geo_lift
from . import single_vertex
from . import make_manifold


def reload():
    importlib.reload(blank_sketch)
    importlib.reload(view_align)
    importlib.reload(geo_lift)
    importlib.reload(single_vertex)
    importlib.reload(make_manifold)


def register():
    blank_sketch.register()
    view_align.register()
    geo_lift.register()
    single_vertex.register()
    make_manifold.register()


def unregister():
    blank_sketch.unregister()
    view_align.unregister()
    geo_lift.unregister()
    single_vertex.unregister()
    make_manifold.unregister()

    