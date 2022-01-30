import importlib
from . import events
from . import math
from . import objects
from . import overlay
from . import viewport


def reload():
    importlib.reload(events)
    importlib.reload(math)
    importlib.reload(objects)
    importlib.reload(overlay)
    importlib.reload(viewport)

    overlay.unregister_draw_handler()