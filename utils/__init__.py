import importlib
from . import name_sync
from . import set_lod_suffix
from . import set_origin


def reload():
    importlib.reload(name_sync)
    importlib.reload(set_lod_suffix)
    importlib.reload(set_origin)


def register():
    name_sync.register()
    set_lod_suffix.register()
    set_origin.register()


def unregister():
    name_sync.unregister()
    set_lod_suffix.unregister()
    set_origin.unregister()
