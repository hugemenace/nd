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


from . import lib
from . import interface
from . import sketching
from . import power_mods
from . import generators


registerables = (
    interface,
    sketching,
    power_mods,
    generators,
)


def register():
    lib.reload()

    for registerable in registerables:
        registerable.reload()
        registerable.register()


def unregister():
    for registerable in registerables:
        registerable.unregister()