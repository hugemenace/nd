import importlib
from . import vanilla
from . import boolean_slice
from . import boolean_inset


def reload():
    importlib.reload(vanilla)
    importlib.reload(boolean_slice)
    importlib.reload(boolean_inset)


def register():
    vanilla.register()
    boolean_slice.register()
    boolean_inset.register()


def unregister():
    vanilla.unregister()
    boolean_slice.unregister()
    boolean_inset.unregister()
