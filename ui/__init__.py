"""
Jeweler 3D Studio - UI Package Initialization
Registers user interface panels, dialogs, and viewport gizmo groups.
"""

_needs_reload = "bpy" in locals()

import bpy
from . import (
    i18n,
    panels,
    # menus, (Disabled in Community)
    preferences,
    pave_panel,
)

if _needs_reload:
    import importlib
    i18n = importlib.reload(i18n)
    panels = importlib.reload(panels)
    # menus = importlib.reload(menus) (Disabled in Community)
    preferences = importlib.reload(preferences)
    pave_panel = importlib.reload(pave_panel)

modules = (
    i18n,
    preferences,
    panels,
    # menus, (Disabled in Community)
    pave_panel,
)


def register():
    for mod in modules:
        if hasattr(mod, "register"):
            mod.register()


def unregister():
    for mod in reversed(modules):
        if hasattr(mod, "unregister"):
            mod.unregister()
