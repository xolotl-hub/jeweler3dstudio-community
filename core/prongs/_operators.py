"""
Jeweler 3D Studio - Prongs Operators (Facade)
Backward-compatible re-export of single and cluster prongs operators.
Submodules:
  _operator_single  — J3DComm_OT_add_prongs (Single gem)
  _operator_cluster — J3DComm_OT_prongs_on_gems (Cluster / Halo)
"""

try:
    import bpy
except ImportError:
    pass

from ._operator_single import J3DComm_OT_add_prongs, J3DComm_OT_readjust_prongs
from ._operator_cluster import J3DComm_OT_prongs_on_gems

classes = (
    J3DComm_OT_add_prongs,
    J3DComm_OT_readjust_prongs,
    J3DComm_OT_prongs_on_gems,
)


def register() -> None:
    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass

__all__ = [
    "J3DComm_OT_add_prongs",
    "J3DComm_OT_readjust_prongs",
    "J3DComm_OT_prongs_on_gems",
    "classes",
    "register",
    "unregister",
]
