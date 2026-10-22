"""
Jeweler 3D Community - Prongs Heart Arrangement
Calculates anatomical prong positions for Heart cut gemstones (lobes, flanks, and bottom V-tip).
"""

from math import atan2, radians
from typing import List
from ._round import ProngPosition


def get_heart_positions(
    dim_x: float,
    dim_y: float,
    count: int = 4,
    girdle_offset: float = 0.0,
    user_angle_deg: float = 45.0,
    rad_prong: float = 0.25,
    tip_type: str = "DOME",
) -> List[ProngPosition]:
    """Generates anatomically fitted prongs on lobes, flanks, and apex of a Heart gem."""
    a = max(0.2, dim_x / 2.0)
    b = max(0.2, dim_y / 2.0)

    # 1. Top lobe prongs: reference round of diameter dim_x (at 45° and 135°)
    # Matches the upper lobe crest of the heart
    x_top = a * 0.7071
    y_top = b * 0.7071
    ux_top, uy_top = 0.7071, 0.7071
    p_lobe_r = ( x_top, y_top,  ux_top, uy_top, False)
    p_lobe_l = (-x_top, y_top, -ux_top, uy_top, False)

    # 2. Bottom flank prongs: reference round of ~85% dim_x (at 315° and 225°)
    # Matches the lower converging flanks of the heart
    x_bot = (a * 0.85) * 0.7071
    y_bot = -(b * 0.85) * 0.7071
    ux_bot, uy_bot = 0.866, -0.50
    p_flank_r = ( x_bot, y_bot,  ux_bot, uy_bot, False)
    p_flank_l = (-x_bot, y_bot, -ux_bot, uy_bot, False)

    # 3. Bottom apex point (pointed V-tip)
    p_tip = (0.0, -b, 0.0, -1.0, True)

    if count == 3:
        raw_points = [p_tip, p_lobe_r, p_lobe_l]
    elif count == 4:
        # Default 4 prongs: 2 upper lobes + 2 lower flanks
        raw_points = [p_lobe_r, p_flank_r, p_flank_l, p_lobe_l]
    elif count >= 5:
        # 5 prongs: 2 upper lobes + 2 lower flanks + 1 bottom V-tip
        raw_points = [p_tip, p_flank_r, p_lobe_r, p_lobe_l, p_flank_l]
    else:
        raw_points = [p_lobe_r, p_flank_r, p_flank_l, p_lobe_l][:count]

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
