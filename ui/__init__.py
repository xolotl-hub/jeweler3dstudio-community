"""Jeweler 3D Community UI panels and translations."""

_needs_reload = "bpy" in locals()

import bpy
from . import i18n, panels

if _needs_reload:
    import importlib
    i18n = importlib.reload(i18n)
    panels = importlib.reload(panels)

modules = (i18n, panels)


def register():
    for mod in modules:
        if hasattr(mod, "register"):
            mod.register()


def unregister():
    for mod in reversed(modules):
        if hasattr(mod, "unregister"):
            mod.unregister()
