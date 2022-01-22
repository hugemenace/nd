bl_info = {
    "name": "ND",
    "author": "HugeMenace",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "HugeMance ND — N Panel",
    "description": "Non-destructive operations, tools, and workflows.",
    "warning": "",
    "doc_url": "https://hugemenace.co",
    "category": "3D View"
}

from . import bolt 
from . import faux_bevel
from . import sketch_bevel
from . import ui_panel

def register():
    bolt.register()
    faux_bevel.register()
    sketch_bevel.register()
    ui_panel.register()

def unregister():
    bolt.unregister()
    faux_bevel.unregister()
    sketch_bevel.unregister()
    ui_panel.unregister()