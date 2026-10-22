"""
Jeweler 3D Community - Prongs Trillion & Triangular Arrangement
Calculates triangular vertex and side prong positions for Trillion, Trilliant, Triangle cuts.
"""

from math import atan2, cos, radians, sin, sqrt
from typing import List, Optional
from ._round import ProngPosition

_COS30 = sqrt(3.0) / 2.0
_SIN30 = 0.5


def get_trillion_positions(
    dim_x: float,
    dim_y: float,
    count: int = 3,
    girdle_offset: float = 0.0,
    user_angle_deg: float = 60.0,
    rad_prong: float = 0.25,
    tip_type: str = "V_PRONG",
) -> List[ProngPosition]:
    """Generates 3 vertex (or 6 edge) prongs for triangular gemstones."""
    a = max(0.2, dim_x / 2.0)
    b = max(0.2, dim_y / 2.0)

    # 3 corner vertices (30°, 150°, 270°)
    corners = [
        ( a * _COS30,  b * _SIN30,  _COS30,  _SIN30, True),   # Right apex (30°)
        (-a * _COS30,  b * _SIN30, -_COS30,  _SIN30, True),   # Left apex (150°)
        (        0.0,         -b,      0.0,    -1.0, True),   # Bottom apex (270°)
    ]

    # Optional 3 mid-edge points (90°, 210°, 330°)
    mid_edges = [
        (        0.0,   b * 0.45,      0.0,     1.0, False),  # Top edge
        (-a * 0.55, -b * 0.45, -_COS30, -_SIN30, False),  # Left edge
        ( a * 0.55, -b * 0.45,  _COS30, -_SIN30, False),  # Right edge
    ]

    if count >= 6:
        raw_points = [
            corners[0], mid_edges[0],
            corners[1], mid_edges[1],
            corners[2], mid_edges[2],
        ]
    else:
        raw_points = corners[:max(1, count)]

    positions = []
    for px, py, ux, uy, is_corner in raw_points:
        tip_override = "V_PRONG" if (is_corner and tip_type == "V_PRONG") else None
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
