"""
Jeweler 3D Community - Prongs Arrangements Subpackage
Dispatches adaptive prong placement calculations tailored to each of the 17 gem cut silhouettes.
Pure Python reference implementation.
"""

_needs_reload = "_round" in locals()

from typing import List
from . import _round
from . import _oval
from . import _rect
from . import _trillion
from . import _heart
from . import _pear
from . import _marquise

if _needs_reload:
    import importlib
    _round = importlib.reload(_round)
    _oval = importlib.reload(_oval)
    _rect = importlib.reload(_rect)
    _trillion = importlib.reload(_trillion)
    _heart = importlib.reload(_heart)
    _pear = importlib.reload(_pear)
    _marquise = importlib.reload(_marquise)

from ._round import ProngPosition, get_round_positions
from ._oval import get_oval_positions
from ._rect import get_rect_positions
from ._trillion import get_trillion_positions
from ._heart import get_heart_positions
from ._pear import get_pear_positions
from ._marquise import get_marquise_positions


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
