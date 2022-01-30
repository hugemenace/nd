import importlib
from . import main_ui_panel
from . import utils_ui_panel
from . import main_menu


def reload():
    importlib.reload(main_ui_panel)
    importlib.reload(utils_ui_panel)
    importlib.reload(main_menu)


def register():
    main_ui_panel.register()
    utils_ui_panel.register()
    main_menu.register()


def unregister():
    main_ui_panel.unregister()
    utils_ui_panel.unregister()
    main_menu.unregister()