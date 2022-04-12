import importlib
from . import name_sync
from . import set_lod_suffix
from . import set_origin
from . import smooth
from . import seams
from . import hydrate


def reload():
    importlib.reload(name_sync)
    importlib.reload(set_lod_suffix)
    importlib.reload(set_origin)
    importlib.reload(smooth)
    importlib.reload(seams)
    importlib.reload(hydrate)


def register():
    name_sync.register()
    set_lod_suffix.register()
    set_origin.register()
    smooth.register()
    seams.register()
    hydrate.register()


def unregister():
    name_sync.unregister()
    set_lod_suffix.unregister()
    set_origin.unregister()
    smooth.unregister()
    seams.unregister()
    hydrate.unregister()
