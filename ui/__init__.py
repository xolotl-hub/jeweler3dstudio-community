"""
Jeweler 3D Studio - UI Package Initialization
Registers user interface panels, dialogs, and viewport gizmo groups.
"""

from . import i18n
from . import panels
# from . import menus (Disabled in Community)

# Desconectados por el momento
# from . import dialogs
# from . import gizmos

modules = (
    i18n,
    panels,
    # menus, (Disabled in Community)
)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in reversed(modules):
        mod.unregister()
