"""
Jeweler 3D Studio - Prongs Marquise Arrangement
Calculates prong positions for Marquise cut gemstones (polar sharp tips and side belly).
"""

from math import atan2
from typing import List, Optional
from ._round import ProngPosition


def get_marquise_positions(
    dim_x: float,
    dim_y: float,
    count: int = 4,
    girdle_offset: float = 0.0,
    user_angle_deg: float = 45.0,
    rad_prong: float = 0.25,
    tip_type: str = "V_PRONG",
) -> List[ProngPosition]:
    """Generates protective prongs on both polar tips and side curves of a Marquise gem."""
    a = max(0.2, dim_x / 2.0)
    b = max(0.2, dim_y / 2.0)

    # Polar tips (sharp points)
    p_tip_top = (0.0,  b, 0.0,  1.0, True)   # Top apex (90°)
    p_tip_bot = (0.0, -b, 0.0, -1.0, True)   # Bottom apex (270°)

    # Belly sides
    p_belly_r = ( a, 0.0,  1.0, 0.0, False)  # Right flank (0°)
    p_belly_l = (-a, 0.0, -1.0, 0.0, False)  # Left flank (180°)

    # 4 Flanks for 6-prong settings
    p_flank_tr = ( a * 0.82,  b * 0.38,  0.894,  0.447, False)
    p_flank_tl = (-a * 0.82,  b * 0.38, -0.894,  0.447, False)
    p_flank_br = ( a * 0.82, -b * 0.38,  0.894, -0.447, False)
    p_flank_bl = (-a * 0.82, -b * 0.38, -0.894, -0.447, False)

    if count == 2:
        raw_points = [p_tip_top, p_tip_bot]
    elif count == 4:
        raw_points = [p_tip_top, p_belly_r, p_tip_bot, p_belly_l]
    elif count >= 6:
        raw_points = [p_tip_top, p_flank_tr, p_flank_br, p_tip_bot, p_flank_bl, p_flank_tl]
    else:
        raw_points = [p_tip_top, p_tip_bot][:count]

    positions = []
    for px, py, ux, uy, is_tip in raw_points:
        tip_override = "V_PRONG" if (is_tip and tip_type == "V_PRONG") else None
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
