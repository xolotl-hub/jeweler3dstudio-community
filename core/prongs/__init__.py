"""
Jeweler 3D Studio - Core Prongs Package (Community Edition)
"""

_needs_reload = "bpy" in locals()

from ._presets import TIP_TYPE_ITEMS, get_default_prong_presets
from ._single import (
    create_single_prong,
    generate_prongs_bmesh,
)
from .arrangements import get_prong_positions
from ._operator_single import J3DComm_OT_add_prongs, J3DComm_OT_readjust_prongs

if _needs_reload:
    import importlib
    from . import _presets, _tips, _single, _op_helpers, _operator_single, arrangements
    _presets         = importlib.reload(_presets)
    _tips            = importlib.reload(_tips)
    _single          = importlib.reload(_single)
    _op_helpers      = importlib.reload(_op_helpers)
    _operator_single = importlib.reload(_operator_single)
    arrangements     = importlib.reload(arrangements)

    TIP_TYPE_ITEMS             = _presets.TIP_TYPE_ITEMS
    get_default_prong_presets  = _presets.get_default_prong_presets
    create_single_prong        = _single.create_single_prong
    generate_prongs_bmesh      = _single.generate_prongs_bmesh
    get_prong_positions        = arrangements.get_prong_positions
    J3DComm_OT_add_prongs      = _operator_single.J3DComm_OT_add_prongs
    J3DComm_OT_readjust_prongs = _operator_single.J3DComm_OT_readjust_prongs

classes = (
    J3DComm_OT_add_prongs,
    J3DComm_OT_readjust_prongs,
)


def register() -> None:
    from ._operator_single import register as _reg
    _reg()


def unregister() -> None:
    from ._operator_single import unregister as _unreg
    _unreg()
