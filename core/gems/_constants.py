"""
Jeweler 3D Studio - Gems: Constants & Physical Definitions

17 gem cut definitions, tier release flags, gemstone physical properties,
and volumetric calibration factors.
"""

from typing import Dict, List, Tuple

# ── 17 Gem Cut Definitions & Icon Mappings ───────────────────────────────────
CUT_DEFS: List[Tuple[str, str, str]] = [
    ("ROUND",     "Round Brilliant", "round.png"),
    ("OVAL",      "Oval",            "oval.png"),
    ("CUSHION",   "Cushion",         "cushion.png"),
    ("PEAR",      "Pear",            "pear.png"),
    ("MARQUISE",  "Marquise",        "marquise.png"),
    ("PRINCESS",  "Princess",        "princess.png"),
    ("BAGUETTE",  "Baguette",        "baguette.png"),
    ("SQUARE",    "Square",          "square.png"),
    ("EMERALD",   "Emerald",         "emerald.png"),
    ("ASSCHER",   "Asscher",         "asscher.png"),
    ("RADIANT",   "Radiant",         "radiant.png"),
    ("FLANDERS",  "Flanders",        "flanders.png"),
    ("OCTAGON",   "Octagon",         "octagon.png"),
    ("HEART",     "Heart",           "heart.png"),
    ("TRILLION",  "Trillion",        "trillion.png"),
    ("TRILLIANT", "Trilliant",       "trilliant.png"),
    ("TRIANGLE",  "Triangle",        "triangle.png"),
]

# Cortes visibles en tiers de producción (Community / Essential / Standard / Pro).
# Lab siempre muestra todos los cortes definidos en CUT_DEFS.
CUTS_RELEASED = {"ROUND", "OVAL"}


def _is_lab_tier() -> bool:
    """Detecta en runtime si el addon activo es el tier Lab (jeweler3dstudio_lab).
    En Blender 4.2+, __package__ es '<addon_id>.core.gems' o '<addon_id>.core',
    por lo que se extrae el primer componente delimitado por punto.
    """
    try:
        pkg = __package__ or ""
        root = pkg.split(".")[0]
        return root.endswith("_lab")
    except Exception:
        pass
    return False


# ── Gem Stones & Physical Properties ─────────────────────────────────────────
GEM_STONES: Dict[str, Dict] = {
    "DIAMOND":       {"name": "Diamond",        "ior": 2.417, "density": 3.52, "color": (1.0, 1.0, 1.0, 1.0)},
    "RUBY":          {"name": "Ruby",           "ior": 1.770, "density": 4.02, "color": (0.85, 0.02, 0.08, 1.0)},
    "SAPPHIRE":      {"name": "Sapphire",       "ior": 1.770, "density": 4.02, "color": (0.05, 0.15, 0.85, 1.0)},
    "EMERALD":       {"name": "Emerald",        "ior": 1.580, "density": 2.76, "color": (0.02, 0.75, 0.25, 1.0)},
    "AQUAMARINE":    {"name": "Aquamarine",     "ior": 1.575, "density": 2.72, "color": (0.35, 0.85, 0.95, 1.0)},
    "AMETHYST":      {"name": "Amethyst",       "ior": 1.544, "density": 2.65, "color": (0.45, 0.08, 0.65, 1.0)},
    "CUBIC_ZIRCONIA":{"name": "Cubic Zirconia", "ior": 2.150, "density": 5.65, "color": (0.95, 0.95, 1.0, 1.0)},
    "MOISSANITE":    {"name": "Moissanite",     "ior": 2.650, "density": 3.22, "color": (0.98, 0.99, 1.0, 1.0)},
    "MORGANITE":     {"name": "Morganite",      "ior": 1.580, "density": 2.76, "color": (0.95, 0.65, 0.60, 1.0)},
    "TANZANITE":     {"name": "Tanzanite",      "ior": 1.695, "density": 3.35, "color": (0.20, 0.15, 0.75, 1.0)},
}

STONE_ITEMS = [(k, v["name"], f"{v['name']} gemstone") for k, v in GEM_STONES.items()]

# ── Relative Volumetric Factors for Carat Estimation ─────────────────────────
CUT_VOLUME_FACTORS: Dict[str, float] = {
    "ROUND": 1.00,
    "PRINCESS": 1.45,
    "CUSHION": 1.25,
    "ASSCHER": 1.35,
    "EMERALD": 1.15,
    "OVAL": 0.95,
    "PEAR": 0.95,
    "MARQUISE": 0.85,
    "HEART": 0.95,
    "RADIANT": 1.20,
    "BAGUETTE": 0.90,
    "TRILLION": 0.85,
    "TRILLIANT": 0.85,
    "TRIANGLE": 0.85,
    "FLANDERS": 1.30,
    "OCTAGON": 1.25,
    "SQUARE": 1.40,
}
