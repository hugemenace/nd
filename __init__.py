bl_info = {
    "name": "HugeMenace — ND",
    "author": "HugeMenace",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "N Panel, Shift + 2",
    "description": "Non-destructive operations, tools, and generators.",
    "warning": "",
    "doc_url": "https://hugemenace.co",
    "category": "3D View"
}

import importlib
from . import overlay
from . import utils
from . import bolt 
from . import faux_bevel
from . import sketch_bevel
from . import view_align
from . import thickener
from . import ui_panel
from . import menu


def register():
    importlib.reload(overlay)
    importlib.reload(utils)
    
    importlib.reload(bolt)
    importlib.reload(faux_bevel)
    importlib.reload(sketch_bevel)
    importlib.reload(view_align)
    importlib.reload(thickener)
    importlib.reload(ui_panel)
    importlib.reload(menu)
    
    bolt.register()
    faux_bevel.register()
    sketch_bevel.register()
    view_align.register()
    thickener.register()
    ui_panel.register()
    menu.register()


def unregister():
    bolt.unregister()
    faux_bevel.unregister()
    sketch_bevel.unregister()
    view_align.unregister()
    thickener.unregister()
    ui_panel.unregister()
    menu.unregister()