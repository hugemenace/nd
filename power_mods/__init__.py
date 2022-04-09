import importlib
from . import screw
from . import solidify
from . import weighted_normal_bevel
from . import vertex_bevel
from . import mirror
from . import profile_extrude
from . import circular_array
from . import square_array
from . import bevel


def reload():
    importlib.reload(screw)
    importlib.reload(solidify)
    importlib.reload(weighted_normal_bevel)
    importlib.reload(vertex_bevel)
    importlib.reload(mirror)
    importlib.reload(profile_extrude)
    importlib.reload(circular_array)
    importlib.reload(square_array)
    importlib.reload(bevel)


def register():
    screw.register()
    solidify.register()
    weighted_normal_bevel.register()
    vertex_bevel.register()
    mirror.register()
    profile_extrude.register()
    circular_array.register()
    square_array.register()
    bevel.register()


def unregister():
    screw.unregister()
    solidify.unregister()
    weighted_normal_bevel.unregister()
    vertex_bevel.unregister()
    mirror.unregister()
    profile_extrude.unregister()
    circular_array.unregister()
    square_array.unregister()
    bevel.unregister()

    