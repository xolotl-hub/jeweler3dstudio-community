"""
Jeweler 3D Studio - Prongs Arrangements Subpackage
Dispatches adaptive prong placement calculations tailored to each of the 17 gem cut silhouettes.
Delegates to high-performance native Rust engine (jeweler_core) when available.
"""

from typing import List, Optional
from ... import _rust_bridge as rb
from ._round import ProngPosition, get_round_positions
from ._oval import get_oval_positions
from ._rect import get_rect_positions
from ._trillion import get_trillion_positions
from ._heart import get_heart_positions
from ._pear import get_pear_positions
from ._marquise import get_marquise_positions


def _native_prong_dispatch(
    cut: str, dim_x: float, dim_y: float, count: int,
    girdle_offset: float, user_angle_deg: float, rad_prong: float, tip_type: str,
) -> Optional[List[ProngPosition]]:
    """Attempts native Rust engine execution for all 17 cuts."""
    if not rb.has_rust_engine():
        return None

    dist = girdle_offset if tip_type == "V_PRONG" else (rad_prong + girdle_offset)

    raw = None
    if cut in {"OVAL", "CUSHION"}:
        raw = rb.calc_oval_prongs(dim_x, dim_y, count, user_angle_deg, dist)
    elif cut in {"PRINCESS", "SQUARE", "EMERALD", "BAGUETTE", "RADIANT", "ASSCHER", "OCTAGON", "FLANDERS"}:
        is_cut = cut in {"EMERALD", "RADIANT", "ASSCHER", "OCTAGON", "FLANDERS"}
        raw = rb.calc_rect_prongs(dim_x, dim_y, count, is_cut, dist)
    elif cut in {"TRILLION", "TRILLIANT", "TRIANGLE"}:
        raw = rb.calc_trillion_prongs(dim_x, dim_y, count, dist)
    elif cut == "HEART":
        raw = rb.calc_heart_prongs(dim_x, dim_y, count, dist)
    elif cut == "PEAR":
        raw = rb.calc_pear_prongs(dim_x, dim_y, count, dist)
    elif cut == "MARQUISE":
        raw = rb.calc_marquise_prongs(dim_x, dim_y, count, dist)
    elif cut == "ROUND":
        gem_r = max(0.2, dim_y / 2.0)
        round_dist = (gem_r + girdle_offset) if tip_type == "V_PRONG" else (gem_r + rad_prong + girdle_offset)
        raw = rb.calc_round_prongs(dim_x, dim_y, count, user_angle_deg, round_dist)

    if raw is None:
        return None

    positions = []
    for x, y, rot_z, is_corner in raw:
        tip_override = "V_PRONG" if (is_corner and tip_type == "V_PRONG") else None
        positions.append(ProngPosition(x=x, y=y, rot_z_rad=rot_z, tip_type=tip_override))
    return positions


def get_prong_positions(
    cut_name: str,
    dim_x: float,
    dim_y: float,
    count: int = 4,
    girdle_offset: float = 0.0,
    user_angle_deg: float = 45.0,
    rad_prong: float = 0.25,
    tip_type: str = "DOME",
) -> List[ProngPosition]:
    """Calculates optimal prong coordinates and tangential Z-orientations for the given cut."""
    cut = (cut_name or "ROUND").upper()

    # 1. Primary: Native Rust engine execution
    native_res = _native_prong_dispatch(
        cut=cut, dim_x=dim_x, dim_y=dim_y, count=count,
        girdle_offset=girdle_offset, user_angle_deg=user_angle_deg,
        rad_prong=rad_prong, tip_type=tip_type,
    )
    if native_res is not None:
        return native_res

    # 2. Secondary fallback (Community tier or environments without compiled binary)
    if cut in {"OVAL", "CUSHION"}:
        return get_oval_positions(dim_x=dim_x, dim_y=dim_y, count=count,
                                  girdle_offset=girdle_offset, user_angle_deg=user_angle_deg,
                                  rad_prong=rad_prong, tip_type=tip_type)

    if cut in {"PRINCESS", "SQUARE", "EMERALD", "BAGUETTE", "RADIANT", "ASSCHER", "OCTAGON", "FLANDERS"}:
        return get_rect_positions(cut_name=cut, dim_x=dim_x, dim_y=dim_y, count=count,
                                  girdle_offset=girdle_offset, user_angle_deg=user_angle_deg,
                                  rad_prong=rad_prong, tip_type=tip_type)

    if cut in {"TRILLION", "TRILLIANT", "TRIANGLE"}:
        return get_trillion_positions(dim_x=dim_x, dim_y=dim_y, count=count,
                                      girdle_offset=girdle_offset, user_angle_deg=user_angle_deg,
                                      rad_prong=rad_prong, tip_type=tip_type)

    if cut == "HEART":
        return get_heart_positions(dim_x=dim_x, dim_y=dim_y, count=count,
                                   girdle_offset=girdle_offset, user_angle_deg=user_angle_deg,
                                   rad_prong=rad_prong, tip_type=tip_type)

    if cut == "PEAR":
        return get_pear_positions(dim_x=dim_x, dim_y=dim_y, count=count,
                                  girdle_offset=girdle_offset, user_angle_deg=user_angle_deg,
                                  rad_prong=rad_prong, tip_type=tip_type)

    if cut == "MARQUISE":
        return get_marquise_positions(dim_x=dim_x, dim_y=dim_y, count=count,
                                      girdle_offset=girdle_offset, user_angle_deg=user_angle_deg,
                                      rad_prong=rad_prong, tip_type=tip_type)

    return get_round_positions(dim_x=dim_x, dim_y=dim_y, count=count,
                               girdle_offset=girdle_offset, user_angle_deg=user_angle_deg,
                               rad_prong=rad_prong, tip_type=tip_type)


__all__ = [
    "ProngPosition",
    "get_prong_positions",
    "get_round_positions",
    "get_oval_positions",
    "get_rect_positions",
    "get_trillion_positions",
    "get_heart_positions",
    "get_pear_positions",
    "get_marquise_positions",
]
