"""
Jeweler 3D Studio - UI Package Initialization
Registers user interface panels, dialogs, and viewport gizmo groups.
"""

_needs_reload = "bpy" in locals()

import bpy
from . import (
    i18n,
    panels,
    # menus, (Disabled in baseline)
    preferences,
    # pave_panel, (Lab tier only)
)

if _needs_reload:
    import importlib
    i18n = importlib.reload(i18n)
    panels = importlib.reload(panels)
    # menus = importlib.reload(menus) (Disabled in baseline)
    preferences = importlib.reload(preferences)
    # pave_panel = importlib.reload(pave_panel) (Lab tier only)

modules = (
    i18n,
    preferences,
    panels,
    # menus, (Disabled in baseline)
    # pave_panel, (Lab tier only)
)


def register():
    for mod in modules:
        if hasattr(mod, "register"):
            mod.register()


def unregister():
    for mod in reversed(modules):
        if hasattr(mod, "unregister"):
            mod.unregister()
