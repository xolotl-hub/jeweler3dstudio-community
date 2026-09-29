"""
Jeweler 3D Studio - UI Panels Subpackage (Community Edition)
"""

_needs_reload = "bpy" in locals()

import bpy
from . import ring
from . import gems
from . import scene_props

if _needs_reload:
    import importlib
    scene_props = importlib.reload(scene_props)
    ring = importlib.reload(ring)
    gems = importlib.reload(gems)

classes = (
    *ring.classes,
    *gems.classes,
)


def register():
    scene_props.register()

    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        else:
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass

    scene_props.unregister()
