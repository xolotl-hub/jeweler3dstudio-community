"""
Jeweler 3D Community - Prongs Round & Radial Arrangement
Calculates uniform radial positions for round and circular gemstones.
"""

from math import cos, radians, sin, tau
from typing import List, NamedTuple, Optional


class ProngPosition(NamedTuple):
    x: float
    y: float
    rot_z_rad: float
    tip_type: Optional[str] = None


def get_round_positions(
    dim_x: float,
    dim_y: float,
    count: int = 4,
    girdle_offset: float = 0.0,
    user_angle_deg: float = 45.0,
    rad_prong: float = 0.25,
    tip_type: str = "DOME",
) -> List[ProngPosition]:
    """Generates uniform radial prong placements around a round gemstone."""
    gem_r = max(0.2, dim_y / 2.0)
    if tip_type == "V_PRONG":
        dist = gem_r + girdle_offset
    else:
        dist = (gem_r + rad_prong) + girdle_offset

    n = max(1, count)
    step = tau / n
    base_angle = radians(-user_angle_deg)

    positions = []
    for i in range(n):
        ang = base_angle + i * step
        # Base prong at (0, dist, 0) rotated around Z by ang:
        px = -dist * sin(ang)
        py = dist * cos(ang)
        positions.append(ProngPosition(x=px, y=py, rot_z_rad=ang, tip_type=None))

    return positions
