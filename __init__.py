"""
Jeweler 3D Studio - Central Addon Entrypoint
Blender 4.2+ compatible extension registration and unregistration lifecycle management.
"""

_needs_reload = "bpy" in locals()

import bpy
from . import (
    core,
    ui,
)

if _needs_reload:
    import importlib
    core = importlib.reload(core)
    ui = importlib.reload(ui)


def register():
    """Register all addon submodules in sequential order."""
    core.register()
    ui.register()


def unregister():
    """Unregister all addon submodules in reverse order to prevent dependency errors."""
    ui.unregister()
    core.unregister()


if __name__ == "__main__":
    register()
