import importlib
from . import toggle_wireframes
from . import toggle_face_orientation
from . import toggle_utils_collection
from . import toggle_clear_view


def reload():
    importlib.reload(toggle_wireframes)
    importlib.reload(toggle_face_orientation)
    importlib.reload(toggle_utils_collection)
    importlib.reload(toggle_clear_view)


def register():
    toggle_wireframes.register()
    toggle_face_orientation.register()
    toggle_utils_collection.register()
    toggle_clear_view.register()


def unregister():
    toggle_wireframes.unregister()
    toggle_face_orientation.unregister()
    toggle_utils_collection.unregister()
    toggle_clear_view.unregister()
