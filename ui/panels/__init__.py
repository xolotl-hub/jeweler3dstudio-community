"""
Jeweler 3D Studio - UI Panels Subpackage (Community Edition)
"""

_needs_reload = "bpy" in locals()

import bpy
from . import scene_props
from . import ring
from . import gems
from . import stubs
from . import prongs
from . import cutters

if _needs_reload:
    import importlib
    scene_props = importlib.reload(scene_props)
    ring = importlib.reload(ring)
    gems = importlib.reload(gems)
    stubs = importlib.reload(stubs)
    prongs = importlib.reload(prongs)
    cutters = importlib.reload(cutters)

classes = (
    *ring.classes,
    *gems.classes,
    stubs.VIEW3D_PT_j3d_community_settings,
    *prongs.classes,
    *cutters.classes,
)


def register():
    scene_props.register()

    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception as e:
                print(f"[Jeweler 3D Community] Warning: Could not unregister {cls.__name__}: {e}")
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"[Jeweler 3D Community] Error: Could not register {cls.__name__}: {e}")


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception as e:
                print(f"[Jeweler 3D Community] Warning: Could not unregister {cls.__name__}: {e}")
        else:
            try:
                bpy.utils.unregister_class(cls)
            except Exception as e:
                print(f"[Jeweler 3D Community] Warning: Could not unregister {cls.__name__}: {e}")

    scene_props.unregister()
