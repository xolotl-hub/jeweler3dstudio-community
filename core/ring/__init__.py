"""
Jeweler 3D Studio - Core Ring Package

Parametric ring shank modeling: international ring sizing standards (US, UK, EU, JP),
Bezier curve references, cylinder references, 8 cross-section profiles, and UI operators.
"""

_needs_reload = "bpy" in locals()

import bpy

from ._sizes import (
    US_RING_SIZES,
    UK_RING_SIZES,
    EU_RING_SIZES,
    JP_RING_SIZES,
    RING_SIZE_SYSTEMS,
    RING_SYSTEM_ITEMS,
    US_SIZE_ITEMS,
    UK_SIZE_ITEMS,
    EU_SIZE_ITEMS,
    JP_SIZE_ITEMS,
    get_ring_diameter,
    get_ring_circumference,
    GEOMETRY_TYPE_ITEMS,
    ORIENTATION_ITEMS,
    _get_orientation_euler,
)
from ._profiles import (
    RING_PROFILE_ITEMS,
    _PROFILE_FNS,
    _find_sharp_corner_indices,
    _make_profile_media_cana,
    _make_profile_plano,
    _make_profile_confort,
    _make_profile_oval,
    _make_profile_knife_edge,
    _make_profile_euro_shank,
    _make_profile_beveled,
    _make_profile_concave,
)
from ._geometry import (
    create_ring_bezier_curve,
    create_ring_cylinder_mesh,
    create_ring_profile_mesh,
)
from ._op_size import J3DComm_OT_create_ring_size
from ._op_profile import J3DComm_OT_create_ring_profile
from ._operators import classes

if _needs_reload:
    import importlib
    from . import _sizes, _profiles, _geometry, _op_size, _op_profile, _operators
    _sizes = importlib.reload(_sizes)
    _profiles = importlib.reload(_profiles)
    _geometry = importlib.reload(_geometry)
    _op_size = importlib.reload(_op_size)
    _op_profile = importlib.reload(_op_profile)
    _operators = importlib.reload(_operators)


def register():
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
