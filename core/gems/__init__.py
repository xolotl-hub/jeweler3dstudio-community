"""
Jeweler 3D Community - Core Gems Package

Modular gemstone suite: 17 luxury cut generation, preview collections,
BSDF materials, commercial size charts, carat estimation, and UI operators.
"""

_needs_reload = "bpy" in locals()

import bpy

from ._constants import (
    CUT_DEFS,
    AVAILABLE_CUTS,
    GEM_STONES,
    STONE_ITEMS,
    CUT_VOLUME_FACTORS,
)
from ._sizes_data import CUT_COMMERCIAL_SIZES
from ._sizes import (
    GLOBAL_COMMERCIAL_SIZES,
    get_gem_size_preset_items,
    get_effective_gem_size,
)
from ._previews import (
    _preview_collections,
    get_cut_preview_collection,
    clear_previews,
    get_cut_enum_items,
)
from ._geometry import (
    calculate_carats,
    get_or_create_gem_material,
    create_gem_mesh,
    create_round_brilliant_mesh,
)
from ._inventory import (
    _get_live_size_mm,
    get_scene_gem_inventory,
)
from ._op_gem import (
    J3DComm_OT_add_gem,
)
from ._operators import classes

if _needs_reload:
    import importlib
    from . import _constants, _sizes_data, _sizes, _previews, _geometry, _inventory, _op_gem, _operators
    _constants = importlib.reload(_constants)
    _sizes_data = importlib.reload(_sizes_data)
    _sizes = importlib.reload(_sizes)
    _previews = importlib.reload(_previews)
    _geometry = importlib.reload(_geometry)
    _inventory = importlib.reload(_inventory)
    _op_gem = importlib.reload(_op_gem)
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
    clear_previews()
