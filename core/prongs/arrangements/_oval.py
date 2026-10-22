"""
Jeweler 3D Community - Prongs Oval & Cushion Arrangement
Calculates quadrant-symmetric positions for Oval and Cushion cuts.
"""

from math import atan2, cos, radians, sin, sqrt, tau
from typing import List
from ._round import ProngPosition


def get_oval_positions(
    dim_x: float,
    dim_y: float,
    count: int = 4,
    girdle_offset: float = 0.0,
    user_angle_deg: float = 45.0,
    rad_prong: float = 0.25,
    tip_type: str = "DOME",
) -> List[ProngPosition]:
    """Generates quadrant-symmetric prongs for Oval / Cushion gems."""
    a = max(0.2, dim_x / 2.0)
    b = max(0.2, dim_y / 2.0)

    if tip_type == "V_PRONG":
        dist = girdle_offset
    else:
        dist = rad_prong + girdle_offset

    n = max(1, count)

    if n == 4:
        # 4 prongs: exact quadrant symmetry across X and Y axes
        ang = radians(abs(user_angle_deg))
        ca, sa = cos(ang), sin(ang)

        px, py = a * ca, b * sa
        nx, ny = b * ca, a * sa
        l = sqrt(nx * nx + ny * ny) or 1.0
        ux, uy = nx / l, ny / l

        x0, y0 = px + ux * dist, py + uy * dist
        rz0 = atan2(-ux,  uy)
        rz1 = atan2( ux,  uy)
        rz2 = atan2( ux, -uy)
        rz3 = atan2(-ux, -uy)

        return [
            ProngPosition(x= x0, y= y0, rot_z_rad=rz0, tip_type=None),
            ProngPosition(x=-x0, y= y0, rot_z_rad=rz1, tip_type=None),
            ProngPosition(x=-x0, y=-y0, rot_z_rad=rz2, tip_type=None),
            ProngPosition(x= x0, y=-y0, rot_z_rad=rz3, tip_type=None),
        ]

    elif n == 6:
        # 6 prongs: 4 flank prongs + 2 waist prongs in bilateral symmetry
        ang = radians(55.0)
        ca, sa = cos(ang), sin(ang)
        px, py = a * ca, b * sa
        nx, ny = b * ca, a * sa
        l = sqrt(nx * nx + ny * ny) or 1.0
        ux, uy = nx / l, ny / l
        x0, y0 = px + ux * dist, py + uy * dist
        rz0 = atan2(-ux,  uy)
        rz1 = atan2( ux,  uy)
        rz2 = atan2( ux, -uy)
        rz3 = atan2(-ux, -uy)

        x_waist = a + dist

        return [
            ProngPosition(x= x0, y= y0, rot_z_rad=rz0, tip_type=None),
            ProngPosition(x= x_waist, y= 0.0, rot_z_rad=radians(-90.0), tip_type=None),
            ProngPosition(x= x0, y=-y0, rot_z_rad=rz3, tip_type=None),
            ProngPosition(x=-x0, y=-y0, rot_z_rad=rz2, tip_type=None),
            ProngPosition(x=-x_waist, y= 0.0, rot_z_rad=radians(90.0), tip_type=None),
            ProngPosition(x=-x0, y= y0, rot_z_rad=rz1, tip_type=None),
        ]

    else:
        step = tau / n
        positions = []
        for i in range(n):
            t = i * step + radians(user_angle_deg - 45.0)
            px, py = a * cos(t), b * sin(t)
            nx, ny = b * cos(t), a * sin(t)
            l = sqrt(nx * nx + ny * ny) or 1.0
            ux, uy = nx / l, ny / l
            positions.append(ProngPosition(
                x=px + ux * dist,
                y=py + uy * dist,
                rot_z_rad=atan2(-ux, uy),
                tip_type=None,
            ))
        return positions
