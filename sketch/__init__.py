# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)
# 
# ---
# Contributors: Tristo (HM)
# ---

import importlib
from . import view_align
from . import geo_lift
from . import panel
from . import single_vertex
from . import recon_poly
from . import screw_head
from . import clear_vgs
from . import make_manifold


registerables = (
    view_align,
    geo_lift,
    panel,
    single_vertex,
    recon_poly,
    screw_head,
    clear_vgs,
    make_manifold,
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
    