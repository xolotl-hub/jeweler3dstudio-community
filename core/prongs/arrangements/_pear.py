"""
Jeweler 3D Community - Prongs Pear Arrangement
Calculates prong positions for Pear cut gemstones (top sharp apex + bottom rounded lobe).
"""

from math import atan2, cos, sin
from typing import List, Optional
from ._round import ProngPosition


def get_pear_positions(
    dim_x: float,
    dim_y: float,
    count: int = 4,
    girdle_offset: float = 0.0,
    user_angle_deg: float = 60.0,
    rad_prong: float = 0.25,
    tip_type: str = "V_PRONG",
) -> List[ProngPosition]:
    """Generates protective prongs on top apex and rounded base of a Pear cut gem."""
    a = max(0.2, dim_x / 2.0)
    b = max(0.2, dim_y / 2.0)

    # Reference points
    # (px, py, normal_x, normal_y, is_sharp_apex)
    p_apex     = ( 0.0,        b,         0.0,    1.0, True)   # Sharp top point (90°)
    p_bot_c    = ( 0.0,       -b,         0.0,   -1.0, False)  # Bottom center (270°)
    p_bot_r    = ( a * 0.72,  -b * 0.70,  0.707, -0.707, False) # Bottom-right curve
    p_bot_l    = (-a * 0.72,  -b * 0.70, -0.707, -0.707, False) # Bottom-left curve
    p_shldr_r  = ( a * 0.95,   0.0,       1.0,    0.0, False)  # Right shoulder
    p_shldr_l  = (-a * 0.95,   0.0,      -1.0,    0.0, False)  # Left shoulder

    if count == 3:
        raw_points = [p_apex, p_bot_r, p_bot_l]
    elif count == 4:
        raw_points = [p_apex, p_bot_r, p_bot_c, p_bot_l]
    elif count == 5:
        raw_points = [p_apex, p_shldr_r, p_bot_r, p_bot_l, p_shldr_l]
    elif count >= 6:
        raw_points = [p_apex, p_shldr_r, p_bot_r, p_bot_c, p_bot_l, p_shldr_l]
    else:
        raw_points = [p_apex, p_bot_r, p_bot_l][:count]

    positions = []
    for px, py, ux, uy, is_apex in raw_points:
        tip_override = "V_PRONG" if (is_apex and tip_type == "V_PRONG") else None
        eff_tip = tip_override or tip_type

        if eff_tip == "V_PRONG":
            dist = girdle_offset
        else:
            dist = rad_prong + girdle_offset

        x = px + ux * dist
        y = py + uy * dist
        rot_z = atan2(-ux, uy)
        positions.append(ProngPosition(x=x, y=y, rot_z_rad=rot_z, tip_type=tip_override))

    return positions
