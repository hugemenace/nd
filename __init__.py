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
from . overlay import unregister_draw_handler
from . import overlay
from . import utils
from . import ring_and_bolt 
from . import weighted_normal_bevel
from . import vertex_bevel
from . import face_sketch
from . import solidify
from . import screw
from . import blank_sketch
from . import ui_panel
from . import menu


def register():
    importlib.reload(overlay)
    importlib.reload(utils)
    
    importlib.reload(ring_and_bolt)
    importlib.reload(weighted_normal_bevel)
    importlib.reload(vertex_bevel)
    importlib.reload(face_sketch)
    importlib.reload(solidify)
    importlib.reload(screw)
    importlib.reload(blank_sketch)
    importlib.reload(ui_panel)
    importlib.reload(menu)
    
    ring_and_bolt.register()
    weighted_normal_bevel.register()
    vertex_bevel.register()
    face_sketch.register()
    solidify.register()
    screw.register()
    blank_sketch.register()
    ui_panel.register()
    menu.register()


def unregister():
    unregister_draw_handler()
    
    ring_and_bolt.unregister()
    weighted_normal_bevel.unregister()
    vertex_bevel.unregister()
    face_sketch.unregister()
    solidify.unregister()
    screw.unregister()
    blank_sketch.unregister()
    ui_panel.unregister()
    menu.unregister()