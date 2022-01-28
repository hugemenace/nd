bl_info = {
    "name": "HugeMenace — ND",
    "author": "HugeMenace",
    "version": (1, 0, 0),
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
from . import vertex_bevel
from . import face_sketch
from . import thickener
from . import spinner
from . import blank_sketch
from . import ui_panel
from . import menu


def register():
    importlib.reload(overlay)
    importlib.reload(utils)
    
    importlib.reload(bolt)
    importlib.reload(faux_bevel)
    importlib.reload(vertex_bevel)
    importlib.reload(face_sketch)
    importlib.reload(thickener)
    importlib.reload(spinner)
    importlib.reload(blank_sketch)
    importlib.reload(ui_panel)
    importlib.reload(menu)
    
    bolt.register()
    faux_bevel.register()
    vertex_bevel.register()
    face_sketch.register()
    thickener.register()
    spinner.register()
    blank_sketch.register()
    ui_panel.register()
    menu.register()


def unregister():
    bolt.unregister()
    faux_bevel.unregister()
    vertex_bevel.unregister()
    face_sketch.unregister()
    thickener.unregister()
    spinner.unregister()
    blank_sketch.unregister()
    ui_panel.unregister()
    menu.unregister()