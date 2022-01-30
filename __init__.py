bl_info = {
    "name": "HugeMenace — ND",
    "author": "HugeMenace",
    "version": (1, 1, 1),
    "blender": (3, 0, 0),
    "location": "N Panel, Shift + 2",
    "description": "Non-destructive operations, tools, and generators.",
    "warning": "",
    "doc_url": "https://hugemenace.co",
    "category": "3D View"
}

from . import ui_panel
from . import menu
from . import lib
from . import sketching
from . import power_mods
from . import generators


def register():
    lib.reload()

    importlib.reload(ui_panel)
    importlib.reload(menu)

    sketching.reload()
    power_mods.reload()
    generators.reload()
    
    ui_panel.register()
    menu.register()

    sketching.register()
    power_mods.register()
    generators.register()


def unregister():
    ui_panel.unregister()
    menu.unregister()

    sketching.unregister()
    power_mods.unregister()
    generators.unregister()