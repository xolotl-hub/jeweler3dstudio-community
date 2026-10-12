"""
Jeweler 3D Studio - Prongs Rectangular & Stepped Arrangement
Calculates corner, chamfer, and side prong positions for Princess, Emerald, Baguette, Radiant, Asscher.
"""

from math import atan2, sqrt
from typing import List, Optional
from ._round import ProngPosition

_SQRT2_INV = 1.0 / sqrt(2.0)


def get_rect_positions(
    cut_name: str,
    dim_x: float,
    dim_y: float,
    count: int = 4,
    girdle_offset: float = 0.0,
    user_angle_deg: float = 45.0,
    rad_prong: float = 0.25,
    tip_type: str = "DOME",
) -> List[ProngPosition]:
    """Generates corner and side prong placements for rectangular and cut-corner stones."""
    a = max(0.2, dim_x / 2.0)
    b = max(0.2, dim_y / 2.0)
    cut = cut_name.upper()

    is_cut_corner = cut in {"EMERALD", "RADIANT", "ASSCHER", "OCTAGON", "FLANDERS"}
    is_sharp_square = cut in {"PRINCESS", "SQUARE"}

    # Chamfer amount for beveled corners
    c = min(a, b) * 0.22 if is_cut_corner else 0.0
    corner_x = a - c * 0.5
    corner_y = b - c * 0.5

    # 4 corner positions with diagonal 45-degree outward normals
    corners = [
        ( corner_x,  corner_y,  _SQRT2_INV,  _SQRT2_INV),  # Top-Right
        (-corner_x,  corner_y, -_SQRT2_INV,  _SQRT2_INV),  # Top-Left
        (-corner_x, -corner_y, -_SQRT2_INV, -_SQRT2_INV),  # Bottom-Left
        ( corner_x, -corner_y,  _SQRT2_INV, -_SQRT2_INV),  # Bottom-Right
    ]

    # Additional side points for 6 or 8 prongs
    side_points = []
    if count >= 6:
        if b >= a:
            # Longer in Y: place side prongs on left and right
            side_points.extend([
                ( a, 0.0,  1.0, 0.0),
                (-a, 0.0, -1.0, 0.0),
            ])
        else:
            # Longer in X: place side prongs on top and bottom
            side_points.extend([
                (0.0,  b, 0.0,  1.0),
                (0.0, -b, 0.0, -1.0),
            ])

    if count >= 8:
        if b >= a:
            side_points.extend([
                (0.0,  b, 0.0,  1.0),
                (0.0, -b, 0.0, -1.0),
            ])
        else:
            side_points.extend([
                ( a, 0.0,  1.0, 0.0),
                (-a, 0.0, -1.0, 0.0),
            ])

    selected_points = corners + side_points
    if count < len(selected_points):
        selected_points = selected_points[:count]

    positions = []
    for px, py, ux, uy in selected_points:
        is_corner = (abs(abs(ux) - _SQRT2_INV) < 0.01)
        tip_override = "V_PRONG" if (is_sharp_square and is_corner and tip_type == "V_PRONG") else None

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
