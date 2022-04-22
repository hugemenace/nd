import importlib
from . import events
from . import math
from . import objects
from . import overlay
from . import axis
from . import viewport
from . import assets
from . import updates
from . import preferences
from . import collections
from . import overlay_keys


def reload():
    importlib.reload(events)
    importlib.reload(math)
    importlib.reload(objects)
    importlib.reload(overlay)
    importlib.reload(axis)
    importlib.reload(viewport)
    importlib.reload(assets)
    importlib.reload(updates)
    importlib.reload(preferences)
    importlib.reload(collections)
    importlib.reload(overlay_keys)

    overlay.unregister_draw_handler()
    axis.unregister_axis_handler()
