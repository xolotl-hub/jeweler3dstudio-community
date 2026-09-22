"""
Jeweler 3D Studio - UI Panels Subpackage (Community Edition)
"""

import bpy
from . import ring
from . import gems

classes = (
    *ring.classes,
    *gems.classes,
)


def register():
    ring.register_properties()
    gems.register_properties()

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

    ring.unregister_properties()
    gems.unregister_properties()
