"""
Jeweler 3D Studio - Central Addon Entrypoint
Blender 4.2+ compatible extension registration and unregistration lifecycle management.
"""

import sys
import importlib

# Dynamic module importing & reloading support
modules_names = [
    "core",
    "ui",
    "assets.node_groups",
]

imported_modules = []

for mod_name in modules_names:
    full_mod_name = f"{__name__}.{mod_name}"
    if full_mod_name in sys.modules:
        imported_modules.append(importlib.reload(sys.modules[full_mod_name]))
    else:
        imported_modules.append(importlib.import_module(full_mod_name))


def register():
    """Register all addon submodules in sequential order."""
    for mod in imported_modules:
        if hasattr(mod, "register"):
            mod.register()


def unregister():
    """Unregister all addon submodules in reverse order to prevent dependency errors."""
    for mod in reversed(imported_modules):
        if hasattr(mod, "unregister"):
            mod.unregister()


if __name__ == "__main__":
    register()
