import importlib
from . import ring_and_bolt
from . import screw_head


def reload():
    importlib.reload(ring_and_bolt)
    importlib.reload(screw_head)


def register():
    ring_and_bolt.register()
    screw_head.register()


def unregister():
    ring_and_bolt.unregister()
    screw_head.unregister()

    