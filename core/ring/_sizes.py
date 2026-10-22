"""
Jeweler 3D Community - Ring: Size Standards & Orientation

International ring sizing tables (US, UK, EU/ISO, JP), diameter/circumference calculations,
and orientation plane transformations.
"""

from typing import Dict, Tuple, List
import math

# International Ring Size Charts (Size -> Inner Diameter in mm)

# 1. US / Canada (US Size -> Inner Diameter mm)
US_RING_SIZES: Dict[str, float] = {
    "3.0": 14.05, "3.5": 14.45, "4.0": 14.86, "4.5": 15.27,
    "5.0": 15.70, "5.5": 16.10, "6.0": 16.51, "6.5": 16.92,
    "7.0": 17.32,  # Default
    "7.5": 17.73, "8.0": 18.14, "8.5": 18.54, "9.0": 18.95,
    "9.5": 19.35, "10.0": 19.76, "10.5": 20.17, "11.0": 20.57,
    "11.5": 20.98, "12.0": 21.39, "12.5": 21.79,
    "13.0": 22.20, "13.5": 22.61,
}

# 2. UK / Australia / South Africa (Letter Size -> Inner Diameter mm)
UK_RING_SIZES: Dict[str, float] = {
    "F": 14.05, "F 1/2": 14.25, "G": 14.45, "G 1/2": 14.65,
    "H": 14.86, "H 1/2": 15.06, "I": 15.27, "I 1/2": 15.40,
    "J": 15.49, "J 1/2": 15.70, "K": 15.90, "K 1/2": 16.10,
    "L": 16.31, "L 1/2": 16.51, "M": 16.71, "M 1/2": 16.92,
    "N": 17.12, "N 1/2": 17.32, "O": 17.53, "O 1/2": 17.73,
    "P": 17.93, "P 1/2": 18.14, "Q": 18.34, "Q 1/2": 18.54,
    "R": 18.75, "R 1/2": 18.95, "S": 19.15, "S 1/2": 19.35,
    "T": 19.56, "T 1/2": 19.76, "U": 19.96, "U 1/2": 20.17,
    "V": 20.37, "V 1/2": 20.57, "W": 20.78, "W 1/2": 20.98,
    "X": 21.18, "X 1/2": 21.39, "Y": 21.59, "Z": 21.99,
    "Z+1": 22.40, "Z+2": 22.81, "Z+3": 23.22, "Z+4": 23.62,
}

# 3. EU / ISO 8653 (Inner Circumference mm -> Inner Diameter mm = C / pi)
EU_RING_SIZES: Dict[str, float] = {
    "44": 14.01, "45": 14.32, "46": 14.64, "47": 14.96, "48": 15.28,
    "49": 15.60, "50": 15.92, "51": 16.23, "52": 16.55, "53": 16.87,
    "54": 17.19, "55": 17.51, "56": 17.83, "57": 18.14, "58": 18.46,
    "59": 18.78, "60": 19.10, "61": 19.42, "62": 19.74, "63": 20.05,
    "64": 20.37, "65": 20.69, "66": 21.01, "67": 21.33, "68": 21.65,
    "69": 21.96, "70": 22.28, "72": 22.92,
}

# 4. Japan / China / Asia (Numerical Size 1-27 -> Inner Diameter mm)
JP_RING_SIZES: Dict[str, float] = {
    "1": 13.00, "2": 13.33, "3": 13.67, "4": 14.00, "5": 14.33,
    "6": 14.67, "7": 15.00, "8": 15.33, "9": 15.67, "10": 16.00,
    "11": 16.33, "12": 16.67, "13": 17.00, "14": 17.33, "15": 17.67,
    "16": 18.00, "17": 18.33, "18": 18.67, "19": 19.00, "20": 19.33,
    "21": 19.67, "22": 20.00, "23": 20.33, "24": 20.67, "25": 21.00,
    "26": 21.33, "27": 21.67,
}

RING_SIZE_SYSTEMS: Dict[str, Dict[str, float]] = {
    "US": US_RING_SIZES,
    "UK": UK_RING_SIZES,
    "EU": EU_RING_SIZES,
    "JP": JP_RING_SIZES,
}

RING_SYSTEM_ITEMS: List[Tuple[str, str, str]] = [
    ("US", "US / Canada", "United States & Canada numerical ring sizing standard (3.0 - 13.5)"),
    ("UK", "UK / Australia", "United Kingdom & Australia letter ring sizing standard (F - Z+4)"),
    ("EU", "EU / ISO (Circumference)", "European / ISO 8653 inner circumference in mm (44 - 72)"),
    ("JP", "Japan / Asia", "Japan, China & Asian numerical ring sizing standard (1 - 27)"),
]

US_SIZE_ITEMS: List[Tuple[str, str, str]] = [
    (k, f"US {k} (Ø {v:.2f} mm)", f"US Size {k} - Inner diameter {v:.2f} mm (Circumference {v*math.pi:.1f} mm)")
    for k, v in US_RING_SIZES.items()
]

UK_SIZE_ITEMS: List[Tuple[str, str, str]] = [
    (k, f"UK {k} (Ø {v:.2f} mm)", f"UK Size {k} - Inner diameter {v:.2f} mm (Circumference {v*math.pi:.1f} mm)")
    for k, v in UK_RING_SIZES.items()
]

EU_SIZE_ITEMS: List[Tuple[str, str, str]] = [
    (k, f"EU {k} (Ø {v:.2f} mm / Circ {k} mm)", f"EU Size {k} - Inner circumference {k} mm (Diameter {v:.2f} mm)")
    for k, v in EU_RING_SIZES.items()
]

JP_SIZE_ITEMS: List[Tuple[str, str, str]] = [
    (k, f"JP {k} (Ø {v:.2f} mm)", f"Japan Size {k} - Inner diameter {v:.2f} mm (Circumference {v*math.pi:.1f} mm)")
    for k, v in JP_RING_SIZES.items()
]


def get_ring_diameter(system: str = "US", size_key: str = "7.0") -> float:
    """Returns the inner diameter in mm for the given system and size key."""
    table = RING_SIZE_SYSTEMS.get(system, US_RING_SIZES)
    if size_key in table:
        return table[size_key]
    return US_RING_SIZES.get(size_key, 17.32)


def get_ring_circumference(diameter_mm: float) -> float:
    """Calculates inner circumference in mm from inner diameter."""
    return diameter_mm * math.pi


GEOMETRY_TYPE_ITEMS: List[Tuple[str, str, str, str, int]] = [
    ("CURVE",    "Bezier Curve",  "Generate 3D circular Bezier curve", "CURVE_NCIRCLE", 0),
    ("CYLINDER", "Mesh Cylinder", "Generate 3D cylinder reference",     "MESH_CYLINDER", 1),
]

ORIENTATION_ITEMS: List[Tuple[str, str, str, str, int]] = [
    ("TOP",   "Top (XY)",   "Ring lying flat in horizontal XY plane (finger along Z)", "ORIENTATION_GLOBAL", 0),
    ("FRONT", "Front (XZ)", "Ring standing upright seen from front in XZ plane (finger along Y)", "ORIENTATION_VIEW",   1),
    ("SIDE",  "Side (YZ)",  "Ring standing upright seen from side in YZ plane (finger along X)",  "ORIENTATION_LOCAL",  2),
]


def _get_orientation_euler(orientation_key: str) -> Tuple[float, float, float]:
    """Calculates Euler rotation (radians) for the selected orientation."""
    if orientation_key == "FRONT":
        return (math.radians(90.0), 0.0, 0.0)
    elif orientation_key == "SIDE":
        return (0.0, math.radians(90.0), 0.0)
    return (0.0, 0.0, 0.0)
