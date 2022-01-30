import importlib
from . import name_sync


def reload():
    importlib.reload(name_sync)


def register():
    name_sync.register()


def unregister():
    name_sync.unregister()
