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
from . import main_ui_panel
from . import utils_ui_panel
from . import viewport_ui_panel
from . import main_menu
from . import sketch_menu
from . import utils_menu
from . import boolean_menu
from . import bevel_menu
from . import extrude_menu
from . import replicate_menu
from . import deform_menu
from . import viewport_menu
from . import ops
from . import common


registerables = (
    main_ui_panel,
    utils_ui_panel,
    viewport_ui_panel,
    main_menu,
    sketch_menu,
    utils_menu,
    boolean_menu,
    bevel_menu,
    extrude_menu,
    replicate_menu,
    deform_menu,
    viewport_menu
)


def reload():
    importlib.reload(ops)
    importlib.reload(common)

    for registerable in registerables:
        importlib.reload(registerable)


def register():
    for registerable in registerables:
        registerable.register()


def unregister():
    for registerable in registerables:
        registerable.unregister()
