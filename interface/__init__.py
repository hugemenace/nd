# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import importlib
from . import main_ui_panel
from . import utils_ui_panel
from . import viewport_ui_panel
from . import main_menu
from . import utils_menu
from . import boolean_menu
from . import bevel_menu
from . import extrude_menu
from . import array_menu
from . import viewport_menu


def reload():
    importlib.reload(main_ui_panel)
    importlib.reload(utils_ui_panel)
    importlib.reload(viewport_ui_panel)
    importlib.reload(main_menu)
    importlib.reload(utils_menu)
    importlib.reload(boolean_menu)
    importlib.reload(bevel_menu)
    importlib.reload(extrude_menu)
    importlib.reload(array_menu)
    importlib.reload(viewport_menu)


def register():
    main_ui_panel.register()
    utils_ui_panel.register()
    viewport_ui_panel.register()
    main_menu.register()
    utils_menu.register()
    boolean_menu.register()
    bevel_menu.register()
    extrude_menu.register()
    array_menu.register()
    viewport_menu.register()


def unregister():
    main_ui_panel.unregister()
    utils_ui_panel.unregister()
    viewport_ui_panel.unregister()
    main_menu.unregister()
    utils_menu.unregister()
    boolean_menu.unregister()
    bevel_menu.unregister()
    extrude_menu.unregister()
    array_menu.unregister()
    viewport_menu.unregister()