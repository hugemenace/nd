import importlib
from . import vanilla
from . import boolean_slice


def reload():
    importlib.reload(vanilla)
    importlib.reload(boolean_slice)


def register():
    vanilla.register()
    boolean_slice.register()


def unregister():
    vanilla.unregister()
    boolean_slice.unregister()
