import importlib
from . import events
from . import math
from . import objects
from . import overlay
from . import viewport
from . import assets


def reload():
    importlib.reload(events)
    importlib.reload(math)
    importlib.reload(objects)
    importlib.reload(overlay)
    importlib.reload(viewport)
    importlib.reload(assets)

    overlay.unregister_draw_handler()