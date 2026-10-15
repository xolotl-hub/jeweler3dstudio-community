"""
Jeweler 3D Studio - Cutters 2D Outlines & Standard Ratios
Generadores matematicos de siluetas 2D adaptativas para cortes estandar de joyeria
y proporciones normalizadas de cortadores de 5 zonas.
"""

import math

# -- Proporciones normalizadas del cortador segun estandares de joyeria ----------
CUTTER_TOP_RATIO        =  1.250   # Extension cilindrica superior (por encima de la tabla)
CUTTER_TABLE_RATIO      =  0.220   # Nivel de la tabla / transicion de corona
CUTTER_GIRDLE_TOP_RATIO =  0.060   # Borde superior del girdle
CUTTER_GIRDLE_BOT_RATIO = -0.030   # Borde inferior del girdle / asiento
CUTTER_SEAT_RATIO       = -0.266   # Cono de asiento (pabellon)
CUTTER_DEPTH_RATIO      =  2.200   # Profundidad del canal de perforacion inferior

# Ratios de radio (relativo a r_half = size_mm * 0.5)
CUTTER_R_TABLE  = 0.700   # Radio de tabla / tubo superior (0.350 mm para gema de 1.0 mm)
CUTTER_R_GIRDLE = 1.160   # Radio del girdle con tolerancia (0.580 mm para gema de 1.0 mm)
CUTTER_R_HOLE   = 0.634   # Radio de asiento y canal inferior (0.317 mm para gema de 1.0 mm)


# -- Grupos de cortes por familia de silueta ---------------------------------------
_ROUND_CUTS    = {"ROUND"}
_RECT_CUTS     = {"PRINCESS", "ASSCHER", "SQUARE", "FLANDERS", "OCTAGON"}
_BAGUETTE_CUTS = {"BAGUETTE", "EMERALD", "RADIANT"}
_OVAL_CUTS     = {"OVAL"}
_CUSHION_CUTS  = {"CUSHION"}
_PEAR_CUTS     = {"PEAR"}
_MARQUISE_CUTS = {"MARQUISE"}
_HEART_CUTS    = {"HEART"}
_TRIANGLE_CUTS = {"TRILLION", "TRILLIANT", "TRIANGLE"}


# -- Generadores de outline 2D (coordenadas normalizadas, radio aprox 1.0) ---------

def _circle(n: int):
    """Circulo perfecto: N puntos equidistantes."""
    return [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n))
            for i in range(n)]


def _ellipse(n: int, a: float = 0.625, b: float = 1.0):
    """Elipse para corte Oval calibrado (ancho relativo a largo = 0.625)."""
    return [(a * math.cos(2 * math.pi * i / n), b * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def _superellipse(n: int, a: float = 1.0, b: float = 1.0, p: float = 4.5):
    """Rectangulo con esquinas suavizadas (superelipse).
    p=4.5 da bordes levemente redondeados; p=2 da circulo; p=2.8 da cojin (cushion).
    """
    pts = []
    for i in range(n):
        ang = 2 * math.pi * i / n
        c = math.cos(ang)
        s = math.sin(ang)
        denom = (abs(c / a) ** p + abs(s / b) ** p)
        r = denom ** (-1.0 / p) if denom > 1e-12 else 1.0
        pts.append((c * r * a, s * r * b))
    return pts


def _triangle_rounded(n: int, r_factor: float = 0.1585):
    """Triangulo curvado (Trillion) con 3 vertices redondeados y vertice inferior hacia -Y."""
    pts = []
    for i in range(n):
        ang = 2 * math.pi * i / n
        r = (1.0 - r_factor) + r_factor * math.sin(3.0 * ang)
        pts.append((r * math.cos(ang), r * math.sin(ang)))
    return pts


def _pear(n: int):
    """Forma de pera: punta aguda hacia +Y, base redondeada hacia -Y."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r_base = 0.75 + 0.25 * math.cos(t)
        offset_y = -0.18 * math.sin(t)
        x_raw = r_base * math.cos(t)
        y_raw = r_base * math.sin(t) + offset_y
        pts.append((-y_raw, x_raw))
    return pts


def _marquise(n: int):
    """Marquesa / lente: puntiaguda en los extremos polares (+Y, -Y)."""
    pts = []
    a, b = 0.48, 1.0
    for i in range(n):
        ang = 2 * math.pi * i / n
        c = math.cos(ang)
        s = math.sin(ang)
        p = 0.55
        denom = (abs(c / a) ** p + abs(s / b) ** p)
        r = denom ** (-1.0 / p) if denom > 1e-12 else 1.0
        pts.append((c * r * a, s * r * b))
    return pts


def _heart(n: int):
    """Corazon parametrico clasico normalizado con punta aguda hacia -Y."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n - math.pi / 2
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t)
              - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x / 16.5, -y / 17.5))
    return pts


def get_cut_outline(cut_key: str, n: int):
    """Devuelve N puntos 2D normalizados del outline del corte dado."""
    k = cut_key.upper()
    n = max(4, n)

    if k in _ROUND_CUTS:
        return _circle(n)
    elif k in _RECT_CUTS:
        return _superellipse(n, a=1.0, b=1.0, p=4.5)
    elif k in _BAGUETTE_CUTS:
        return _superellipse(n, a=0.58, b=1.0, p=4.5)
    elif k in _OVAL_CUTS:
        return _ellipse(n, a=0.625, b=1.0)
    elif k in _CUSHION_CUTS:
        return _superellipse(n, a=1.0, b=1.0, p=2.8)
    elif k in _PEAR_CUTS:
        return _pear(n)
    elif k in _MARQUISE_CUTS:
        return _marquise(n)
    elif k in _HEART_CUTS:
        return _heart(n)
    elif k in _TRIANGLE_CUTS:
        return _triangle_rounded(n)
    else:
        return _circle(n)
