"""
Jeweler 3D Studio - Core Package Initialization
Registers core property groups, geometry operators, and calculation modules.
"""

_needs_reload = "bpy" in locals()

import bpy
from . import (
    units,
    gem_data,
    ring,
    gems,
    cutters,
)

if _needs_reload:
    import importlib
    units = importlib.reload(units)
    gem_data = importlib.reload(gem_data)
    ring = importlib.reload(ring)
    gems = importlib.reload(gems)
    cutters = importlib.reload(cutters)

modules = (
    units,
    ring,
    gems,
    cutters,
)


def register():
    for mod in modules:
        if hasattr(mod, "register"):
            mod.register()


def unregister():
    for mod in reversed(modules):
        if hasattr(mod, "unregister"):
            mod.unregister()
