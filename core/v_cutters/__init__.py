"""
Jeweler 3D Studio - Core V-Cutters Package

Three independent cutter operators for fishtail / castle / micro-pavé setting:

  1. J3DComm_OT_add_u_cutter       — U-slot transversal a cada gema del arreglo
  2. J3DComm_OT_add_v_cutter_long  — V-cuña longitudinal entre par de gemas (a lo largo)
  3. J3DComm_OT_add_v_cutter_trans — V-cuña transversal entre par de gemas (a lo ancho)
"""

import bpy

from ._geometry import _build_v_wedge_bm, _build_u_slot_bm
from ._utils import (
    _gem_up,
    _mat4,
    _mat_at_gem_in_chain,
    _mat_between_gems,
    _sort_chain,
    _merge_bm_into,
    _finalize_cutter_obj,
    _apply_boolean_if_allowed,
    _avg_gem_size,
)
from ._u_slot import J3DComm_OT_add_u_cutter
from ._v_wedge import J3DComm_OT_add_v_cutter_long, J3DComm_OT_add_v_cutter_trans

classes = (
    J3DComm_OT_add_u_cutter,
    J3DComm_OT_add_v_cutter_trans,
)


def register():
    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
