"""
Jeweler 3D Community - UI Panels Subpackage 
"""

_needs_reload = "bpy" in locals()

import bpy
from bpy.types import Panel, Context
from . import scene_props
from . import ring
from . import gems
from . import prongs
from . import cutters

if _needs_reload:
    import importlib
    scene_props = importlib.reload(scene_props)
    ring = importlib.reload(ring)
    gems = importlib.reload(gems)
    prongs = importlib.reload(prongs)
    cutters = importlib.reload(cutters)


class VIEW3D_PT_j3d_community_settings(Panel):
    bl_label = "Settings (Prongs)"
    bl_idname = "VIEW3D_PT_j3d_community_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Jeweler 3D Community'

    def draw(self, context: Context) -> None:
        pass


classes = (
    *ring.classes,
    *gems.classes,
    VIEW3D_PT_j3d_community_settings,
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
