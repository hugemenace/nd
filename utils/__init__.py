import importlib
from . import name_sync
from . import set_lod_suffix


def reload():
    importlib.reload(name_sync)
    importlib.reload(set_lod_suffix)


def register():
    name_sync.register()
    set_lod_suffix.register()


def unregister():
    name_sync.unregister()
    set_lod_suffix.unregister()
