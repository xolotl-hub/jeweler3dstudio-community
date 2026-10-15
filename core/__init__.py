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
    prongs,
    v_cutters,
    pave,
)

if _needs_reload:
    import importlib
    units = importlib.reload(units)
    gem_data = importlib.reload(gem_data)
    ring = importlib.reload(ring)
    gems = importlib.reload(gems)
    cutters = importlib.reload(cutters)
    prongs = importlib.reload(prongs)
    v_cutters = importlib.reload(v_cutters)
    pave = importlib.reload(pave)

modules = (
    units,
    ring,
    gems,
    cutters,
    prongs,
    v_cutters,
    pave,
)


def register():
    for mod in modules:
        if hasattr(mod, "register"):
            mod.register()


def unregister():
    for mod in reversed(modules):
        if hasattr(mod, "unregister"):
            mod.unregister()
