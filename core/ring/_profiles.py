"""
Jeweler 3D Community - Ring: Cross-Section Profiles

8 parametric ring profile cross-sections and sharp corner detection for edge creasing.
"""

from typing import Tuple, List
import math

# 8 Ring Profile Definitions
# Normalized cross-section: u_norm [0=inner..1=outer], v_norm [-0.5..0.5 = width]
# Actual 3D: r = inner_radius + u_norm * height_mm,  z = v_norm * width_mm

RING_PROFILE_ITEMS: List[Tuple[str, str, str, int]] = [
    ("MEDIA_CANA", "Half Round",  "Flat inner edge, domed outer - classic half-round",         0),
    ("PLANO",      "Flat",        "Flat rectangular cross-section - modern minimalist",         1),
    ("CONFORT",    "Comfort Fit", "Flat outside, comfort domed inside - comfortable to wear",  2),
    ("OVAL",       "Oval",        "Symmetric elliptical cross-section",                         3),
    ("KNIFE_EDGE", "Knife Edge",  "Sharp knife-edge outer ridge",                               4),
    ("EURO_SHANK", "Euro Shank",  "Flat exterior shape with elegant corner bevels",             5),
    ("BEVELED",    "Beveled",     "Flat top with 45-degree angled side bevels",                 6),
    ("CONCAVE",    "Concave",     "Recessed concave center groove",                             7),
]


def _make_profile_media_cana(n: int = 8) -> List[Tuple[float, float]]:
    """Return a half-round profile with a flat inner edge and domed outer edge."""
    pts = [(0.0, -0.5), (0.0, 0.5)]
    seg = max(2, n)
    for i in range(1, seg):
        t = i / seg
        pts.append((math.sin(math.pi * t), 0.5 - t))
    return pts


def _make_profile_plano(n: int = 1) -> List[Tuple[float, float]]:
    """Return a rectangular profile."""
    return [(0.0, -0.5), (0.0, 0.5), (1.0, 0.5), (1.0, -0.5)]


def _make_profile_confort(n: int = 8) -> List[Tuple[float, float]]:
    """Return a comfort-fit profile with a flat outer edge and gently domed inner edge."""
    pts = [(1.0, -0.5), (1.0, 0.5)]
    pts.append((0.10, 0.5))
    seg = max(2, n)
    for i in range(1, seg):
        t = i / seg
        u = 0.10 * math.sin(math.pi * t)
        pts.append((u, 0.5 - t))
    pts.append((0.10, -0.5))
    return pts


def _make_profile_oval(n: int = 16) -> List[Tuple[float, float]]:
    """Return an elliptical cross-section centered at (0.5, 0)."""
    pts = []
    seg = max(4, n)
    for i in range(seg):
        angle = 2.0 * math.pi * i / seg
        u = 0.5 + 0.5 * math.cos(angle)
        v = 0.5 * math.sin(angle)
        pts.append((u, v))
    return pts


def _make_profile_knife_edge(n: int = 1) -> List[Tuple[float, float]]:
    """Return a knife-edge profile with a flat inner edge and a sharp outer ridge."""
    return [(0.0, -0.5), (0.0, 0.5), (1.0, 0.0)]


def _make_profile_euro_shank(n: int = 1) -> List[Tuple[float, float]]:
    """Return a square European shank profile with small outer chamfers."""
    c = 0.10
    return [
        (0.0,       -0.5),
        (0.0,        0.5),
        (1.0 - c,    0.5),
        (1.0,        0.5 - c),
        (1.0,       -(0.5 - c)),
        (1.0 - c,   -0.5),
    ]


def _make_profile_beveled(n: int = 1) -> List[Tuple[float, float]]:
    """Return a rectangular profile with beveled outer corners."""
    b = 0.18
    return [
        (0.0,      -0.5),
        (0.0,       0.5),
        (1.0 - b,   0.5),
        (1.0,       0.5 - b),
        (1.0,      -(0.5 - b)),
        (1.0 - b,  -0.5),
    ]


def _make_profile_concave(n: int = 8) -> List[Tuple[float, float]]:
    """Return a profile with a concave outer surface forming a groove."""
    pts = [(0.0, -0.5), (0.0, 0.5)]
    pts.append((1.0, 0.5))
    seg = max(2, n)
    for i in range(1, seg):
        t = i / seg
        u = 1.0 - 0.35 * math.sin(math.pi * t)
        pts.append((u, 0.5 - t))
    pts.append((1.0, -0.5))
    return pts


_PROFILE_FNS = {
    "MEDIA_CANA": _make_profile_media_cana,
    "PLANO":      _make_profile_plano,
    "CONFORT":    _make_profile_confort,
    "OVAL":       _make_profile_oval,
    "KNIFE_EDGE": _make_profile_knife_edge,
    "EURO_SHANK": _make_profile_euro_shank,
    "BEVELED":    _make_profile_beveled,
    "CONCAVE":    _make_profile_concave,
}


def _find_sharp_corner_indices(pts: List[Tuple[float, float]], threshold_cos: float = 0.866) -> List[int]:
    """Identify profile vertex indices that represent sharp corners.

    A sharp corner has a direction change greater than about 30 degrees between adjacent segments.
    """
    M = len(pts)
    if M <= 4:
        return list(range(M))

    corner_indices = []
    for j in range(M):
        p_prev = pts[(j - 1) % M]
        p_curr = pts[j]
        p_next = pts[(j + 1) % M]

        v1_x = p_curr[0] - p_prev[0]
        v1_y = p_curr[1] - p_prev[1]
        v2_x = p_next[0] - p_curr[0]
        v2_y = p_next[1] - p_curr[1]

        len1 = math.hypot(v1_x, v1_y)
        len2 = math.hypot(v2_x, v2_y)
        if len1 < 1e-6 or len2 < 1e-6:
            continue

        cos_ang = (v1_x * v2_x + v1_y * v2_y) / (len1 * len2)
        if cos_ang < threshold_cos:
            corner_indices.append(j)

    return corner_indices
