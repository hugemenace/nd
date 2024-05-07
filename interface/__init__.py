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
from . import main_ui_panel
from . import main_menu
from . import sketch_menu
from . import utils_menu
from . import fast_menu
from . import boolean_menu
from . import packaging_menu
from . import id_material_menu
from . import scene_menu
from . import bevel_menu
from . import simplify_menu
from . import shading_menu
from . import extrude_menu
from . import replicate_menu
from . import deform_menu
from . import viewport_menu
from . import reset_theme
from . import ops
from . import common


registerables = (
    main_ui_panel,
    main_menu,
    sketch_menu,
    utils_menu,
    fast_menu,
    boolean_menu,
    packaging_menu,
    id_material_menu,
    scene_menu,
    bevel_menu,
    simplify_menu,
    shading_menu,
    extrude_menu,
    replicate_menu,
    deform_menu,
    viewport_menu,
    reset_theme,
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
