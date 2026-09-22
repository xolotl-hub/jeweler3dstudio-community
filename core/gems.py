"""
Jeweler 3D Studio - Core Gems Module
Provides 3D gem generation, preview icon integration (17 luxury cuts),
realistic BSDF material generation, commercial size charts by cut, carat estimation, and UI operators.
"""

import os
import math
from typing import Dict, List, Tuple, Any
import bpy
import bmesh
import bpy.utils.previews
from bpy.props import EnumProperty, FloatProperty
from bpy.types import Operator
from .units import mm_to_bu
from .gem_data import GEM_MESH_DATA

# ── 17 Gem Cut Definitions & Icon Mappings ───────────────────────────────────
CUT_DEFS = [
    ("ROUND",     "Redondo",   "round.png"),
    ("OVAL",      "Oval",      "oval.png"),
    ("CUSHION",   "Cushion",   "cushion.png"),
    ("PEAR",      "Pera",      "pear.png"),
    ("MARQUISE",  "Marquesa",  "marquise.png"),
    ("PRINCESS",  "Princesa",  "princess.png"),
    ("BAGUETTE",  "Baguette",  "baguette.png"),
    ("SQUARE",    "Cuadrado",  "square.png"),
    ("EMERALD",   "Esmeralda", "emerald.png"),
    ("ASSCHER",   "Asscher",   "asscher.png"),
    ("RADIANT",   "Radiante",  "radiant.png"),
    ("FLANDERS",  "Flanders",  "flanders.png"),
    ("OCTAGON",   "Octagono",  "octagon.png"),
    ("HEART",     "Corazon",   "heart.png"),
    ("TRILLION",  "Trillon",   "trillion.png"),
    ("TRILLIANT", "Trillante", "trilliant.png"),
    ("TRIANGLE",  "Triangulo", "triangle.png"),
]

# ── Gem Stones & Physical Properties ─────────────────────────────────────────
GEM_STONES: Dict[str, Dict] = {
    "DIAMOND":       {"name": "Diamante",   "ior": 2.417, "density": 3.52, "color": (1.0, 1.0, 1.0, 1.0)},
    "RUBY":          {"name": "Rubi",       "ior": 1.770, "density": 4.02, "color": (0.85, 0.02, 0.08, 1.0)},
    "SAPPHIRE":      {"name": "Zafiro",     "ior": 1.770, "density": 4.02, "color": (0.05, 0.15, 0.85, 1.0)},
    "EMERALD":       {"name": "Esmeralda",  "ior": 1.580, "density": 2.76, "color": (0.02, 0.75, 0.25, 1.0)},
    "AQUAMARINE":    {"name": "Aquamarina", "ior": 1.575, "density": 2.72, "color": (0.35, 0.85, 0.95, 1.0)},
    "AMETHYST":      {"name": "Amatista",   "ior": 1.544, "density": 2.65, "color": (0.45, 0.08, 0.65, 1.0)},
    "CUBIC_ZIRCONIA":{"name": "Circonia",   "ior": 2.150, "density": 5.65, "color": (0.95, 0.95, 1.0, 1.0)},
    "MOISSANITE":    {"name": "Moissanita", "ior": 2.650, "density": 3.22, "color": (0.98, 0.99, 1.0, 1.0)},
    "MORGANITE":     {"name": "Morganita",  "ior": 1.580, "density": 2.76, "color": (0.95, 0.65, 0.60, 1.0)},
    "TANZANITE":     {"name": "Tanzanita",  "ior": 1.695, "density": 3.35, "color": (0.20, 0.15, 0.75, 1.0)},
}

STONE_ITEMS = [(k, v["name"], f"Piedra {v['name']}") for k, v in GEM_STONES.items()]

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

# ── Commercial Gem Sizes by Cut (International Jewelry Trade Standards) ──────
CUT_COMMERCIAL_SIZES: Dict[str, List[Tuple[str, str, float]]] = {
    "ROUND": [
        ("1.0", "1.0 mm  (~0.005 ct)", 1.0),
        ("1.3", "1.3 mm  (~0.010 ct / 1 pt)", 1.3),
        ("1.5", "1.5 mm  (~0.015 ct)", 1.5),
        ("1.7", "1.7 mm  (~0.020 ct / 2 pt)", 1.7),
        ("2.0", "2.0 mm  (~0.030 ct / 3 pt)", 2.0),
        ("2.5", "2.5 mm  (~0.060 ct / 6 pt)", 2.5),
        ("3.0", "3.0 mm  (~0.100 ct / 1/10 ct)", 3.0),
        ("3.5", "3.5 mm  (~0.160 ct)", 3.5),
        ("4.0", "4.0 mm  (~0.250 ct / 1/4 ct)", 4.0),
        ("4.5", "4.5 mm  (~0.350 ct)", 4.5),
        ("5.0", "5.0 mm  (~0.500 ct / 1/2 ct)", 5.0),
        ("5.5", "5.5 mm  (~0.650 ct)", 5.5),
        ("6.0", "6.0 mm  (~0.800 ct)", 6.0),
        ("6.5", "6.5 mm  (~1.000 ct / 1 ct)", 6.5),
        ("7.0", "7.0 mm  (~1.250 ct)", 7.0),
        ("7.5", "7.5 mm  (~1.500 ct / 1.5 ct)", 7.5),
        ("8.0", "8.0 mm  (~2.000 ct / 2 ct)", 8.0),
        ("9.0", "9.0 mm  (~3.000 ct / 3 ct)", 9.0),
        ("10.0", "10.0 mm (~4.000 ct / 4 ct)", 10.0),
    ],
    "OVAL": [
        ("4.0", "4.0 x 3.0 mm  (~0.15 ct)", 4.0),
        ("5.0", "5.0 x 3.0 mm  (~0.25 ct)", 5.0),
        ("6.0", "6.0 x 4.0 mm  (~0.50 ct / 1/2 ct)", 6.0),
        ("7.0", "7.0 x 5.0 mm  (~0.85 ct)", 7.0),
        ("8.0", "8.0 x 6.0 mm  (~1.30 ct)", 8.0),
        ("9.0", "9.0 x 7.0 mm  (~2.00 ct / 2 ct)", 9.0),
        ("10.0", "10.0 x 8.0 mm (~3.00 ct / 3 ct)", 10.0),
        ("11.0", "11.0 x 9.0 mm (~4.20 ct)", 11.0),
        ("12.0", "12.0 x 10.0 mm (~5.50 ct)", 12.0),
    ],
    "CUSHION": [
        ("3.5", "3.5 x 3.5 mm  (~0.20 ct)", 3.5),
        ("4.0", "4.0 x 4.0 mm  (~0.35 ct)", 4.0),
        ("4.5", "4.5 x 4.5 mm  (~0.50 ct)", 4.5),
        ("5.0", "5.0 x 5.0 mm  (~0.65 ct)", 5.0),
        ("5.5", "5.5 x 5.5 mm  (~0.85 ct)", 5.5),
        ("6.0", "6.0 x 6.0 mm  (~1.10 ct / 1 ct)", 6.0),
        ("6.5", "6.5 x 6.5 mm  (~1.40 ct)", 6.5),
        ("7.0", "7.0 x 7.0 mm  (~1.75 ct)", 7.0),
        ("8.0", "8.0 x 8.0 mm  (~2.60 ct / 2.5 ct)", 8.0),
        ("9.0", "9.0 x 9.0 mm  (~3.70 ct)", 9.0),
    ],
    "PEAR": [
        ("4.0", "4.0 x 2.5 mm  (~0.12 ct)", 4.0),
        ("5.0", "5.0 x 3.0 mm  (~0.25 ct)", 5.0),
        ("6.0", "6.0 x 4.0 mm  (~0.50 ct / 1/2 ct)", 6.0),
        ("7.0", "7.0 x 5.0 mm  (~0.85 ct)", 7.0),
        ("8.0", "8.0 x 5.0 mm  (~1.10 ct / 1 ct)", 8.0),
        ("8.5", "8.5 x 5.5 mm  (~1.30 ct)", 8.5),
        ("9.0", "9.0 x 6.0 mm  (~1.75 ct)", 9.0),
        ("10.0", "10.0 x 7.0 mm (~2.50 ct / 2.5 ct)", 10.0),
        ("11.0", "11.0 x 7.5 mm (~3.50 ct)", 11.0),
        ("12.0", "12.0 x 8.0 mm (~4.50 ct)", 12.0),
    ],
    "MARQUISE": [
        ("4.0", "4.0 x 2.0 mm  (~0.10 ct)", 4.0),
        ("5.0", "5.0 x 2.5 mm  (~0.18 ct)", 5.0),
        ("6.0", "6.0 x 3.0 mm  (~0.30 ct)", 6.0),
        ("7.0", "7.0 x 3.5 mm  (~0.50 ct / 1/2 ct)", 7.0),
        ("8.0", "8.0 x 4.0 mm  (~0.75 ct)", 8.0),
        ("9.0", "9.0 x 4.5 mm  (~1.00 ct / 1 ct)", 9.0),
        ("10.0", "10.0 x 5.0 mm (~1.50 ct / 1.5 ct)", 10.0),
        ("11.0", "11.0 x 5.5 mm (~2.00 ct / 2 ct)", 11.0),
        ("12.0", "12.0 x 6.0 mm (~2.60 ct)", 12.0),
    ],
    "PRINCESS": [
        ("1.5", "1.5 x 1.5 mm  (~0.025 ct)", 1.5),
        ("2.0", "2.0 x 2.0 mm  (~0.050 ct)", 2.0),
        ("2.5", "2.5 x 2.5 mm  (~0.100 ct)", 2.5),
        ("3.0", "3.0 x 3.0 mm  (~0.180 ct)", 3.0),
        ("3.5", "3.5 x 3.5 mm  (~0.280 ct)", 3.5),
        ("4.0", "4.0 x 4.0 mm  (~0.400 ct)", 4.0),
        ("4.5", "4.5 x 4.5 mm  (~0.550 ct)", 4.5),
        ("5.0", "5.0 x 5.0 mm  (~0.750 ct / 3/4 ct)", 5.0),
        ("5.5", "5.5 x 5.5 mm  (~1.000 ct / 1 ct)", 5.5),
        ("6.0", "6.0 x 6.0 mm  (~1.250 ct)", 6.0),
        ("6.5", "6.5 x 6.5 mm  (~1.550 ct / 1.5 ct)", 6.5),
        ("7.0", "7.0 x 7.0 mm  (~2.000 ct / 2 ct)", 7.0),
        ("8.0", "8.0 x 8.0 mm  (~3.000 ct / 3 ct)", 8.0),
    ],
    "BAGUETTE": [
        ("2.5", "2.5 x 1.5 mm  (~0.03 ct)", 2.5),
        ("3.0", "3.0 x 1.5 mm  (~0.05 ct)", 3.0),
        ("3.5", "3.5 x 1.75 mm (~0.08 ct)", 3.5),
        ("4.0", "4.0 x 2.0 mm  (~0.12 ct)", 4.0),
        ("4.5", "4.5 x 2.25 mm (~0.18 ct)", 4.5),
        ("5.0", "5.0 x 2.5 mm  (~0.25 ct / 1/4 ct)", 5.0),
        ("6.0", "6.0 x 3.0 mm  (~0.45 ct)", 6.0),
        ("7.0", "7.0 x 3.5 mm  (~0.75 ct)", 7.0),
    ],
    "SQUARE": [
        ("1.5", "1.5 x 1.5 mm  (~0.025 ct)", 1.5),
        ("2.0", "2.0 x 2.0 mm  (~0.050 ct)", 2.0),
        ("2.5", "2.5 x 2.5 mm  (~0.100 ct)", 2.5),
        ("3.0", "3.0 x 3.0 mm  (~0.180 ct)", 3.0),
        ("3.5", "3.5 x 3.5 mm  (~0.280 ct)", 3.5),
        ("4.0", "4.0 x 4.0 mm  (~0.400 ct)", 4.0),
        ("5.0", "5.0 x 5.0 mm  (~0.750 ct)", 5.0),
        ("6.0", "6.0 x 6.0 mm  (~1.250 ct)", 6.0),
        ("7.0", "7.0 x 7.0 mm  (~2.000 ct)", 7.0),
    ],
    "EMERALD": [
        ("4.0", "4.0 x 2.0 mm  (~0.12 ct)", 4.0),
        ("5.0", "5.0 x 3.0 mm  (~0.30 ct)", 5.0),
        ("6.0", "6.0 x 4.0 mm  (~0.60 ct)", 6.0),
        ("7.0", "7.0 x 5.0 mm  (~1.00 ct / 1 ct)", 7.0),
        ("8.0", "8.0 x 6.0 mm  (~1.75 ct)", 8.0),
        ("9.0", "9.0 x 7.0 mm  (~2.75 ct)", 9.0),
        ("10.0", "10.0 x 8.0 mm (~3.80 ct / 4 ct)", 10.0),
        ("11.0", "11.0 x 9.0 mm (~5.20 ct)", 11.0),
        ("12.0", "12.0 x 10.0 mm (~7.00 ct)", 12.0),
    ],
    "ASSCHER": [
        ("3.0", "3.0 x 3.0 mm  (~0.18 ct)", 3.0),
        ("3.5", "3.5 x 3.5 mm  (~0.28 ct)", 3.5),
        ("4.0", "4.0 x 4.0 mm  (~0.42 ct)", 4.0),
        ("4.5", "4.5 x 4.5 mm  (~0.58 ct)", 4.5),
        ("5.0", "5.0 x 5.0 mm  (~0.78 ct)", 5.0),
        ("5.5", "5.5 x 5.5 mm  (~1.00 ct / 1 ct)", 5.5),
        ("6.0", "6.0 x 6.0 mm  (~1.30 ct)", 6.0),
        ("6.5", "6.5 x 6.5 mm  (~1.65 ct)", 6.5),
        ("7.0", "7.0 x 7.0 mm  (~2.10 ct / 2 ct)", 7.0),
        ("8.0", "8.0 x 8.0 mm  (~3.20 ct)", 8.0),
    ],
    "RADIANT": [
        ("4.5", "4.5 x 3.5 mm  (~0.35 ct)", 4.5),
        ("5.0", "5.0 x 4.0 mm  (~0.50 ct / 1/2 ct)", 5.0),
        ("6.0", "6.0 x 4.5 mm  (~0.85 ct)", 6.0),
        ("6.5", "6.5 x 5.0 mm  (~1.10 ct / 1 ct)", 6.5),
        ("7.0", "7.0 x 5.5 mm  (~1.50 ct)", 7.0),
        ("8.0", "8.0 x 6.0 mm  (~2.20 ct / 2 ct)", 8.0),
        ("9.0", "9.0 x 7.0 mm  (~3.30 ct)", 9.0),
    ],
    "FLANDERS": [
        ("3.0", "3.0 x 3.0 mm  (~0.15 ct)", 3.0),
        ("4.0", "4.0 x 4.0 mm  (~0.35 ct)", 4.0),
        ("5.0", "5.0 x 5.0 mm  (~0.70 ct)", 5.0),
        ("5.5", "5.5 x 5.5 mm  (~0.95 ct / 1 ct)", 5.5),
        ("6.0", "6.0 x 6.0 mm  (~1.20 ct)", 6.0),
        ("6.5", "6.5 x 6.5 mm  (~1.55 ct)", 6.5),
        ("7.0", "7.0 x 7.0 mm  (~2.00 ct / 2 ct)", 7.0),
    ],
    "OCTAGON": [
        ("3.0", "3.0 x 3.0 mm  (~0.15 ct)", 3.0),
        ("4.0", "4.0 x 4.0 mm  (~0.35 ct)", 4.0),
        ("5.0", "5.0 x 5.0 mm  (~0.70 ct)", 5.0),
        ("6.0", "6.0 x 6.0 mm  (~1.20 ct)", 6.0),
        ("7.0", "7.0 x 7.0 mm  (~2.00 ct)", 7.0),
        ("8.0", "8.0 x 8.0 mm  (~3.00 ct)", 8.0),
    ],
    "HEART": [
        ("3.0", "3.0 x 3.0 mm  (~0.12 ct)", 3.0),
        ("4.0", "4.0 x 4.0 mm  (~0.25 ct / 1/4 ct)", 4.0),
        ("4.5", "4.5 x 4.5 mm  (~0.38 ct)", 4.5),
        ("5.0", "5.0 x 5.0 mm  (~0.50 ct / 1/2 ct)", 5.0),
        ("5.5", "5.5 x 5.5 mm  (~0.75 ct / 3/4 ct)", 5.5),
        ("6.0", "6.0 x 6.0 mm  (~1.00 ct / 1 ct)", 6.0),
        ("6.5", "6.5 x 6.5 mm  (~1.30 ct)", 6.5),
        ("7.0", "7.0 x 7.0 mm  (~1.65 ct)", 7.0),
        ("8.0", "8.0 x 8.0 mm  (~2.20 ct / 2 ct)", 8.0),
    ],
    "TRILLION": [
        ("3.0", "3.0 x 3.0 mm  (~0.10 ct)", 3.0),
        ("4.0", "4.0 x 4.0 mm  (~0.22 ct)", 4.0),
        ("4.5", "4.5 x 4.5 mm  (~0.32 ct)", 4.5),
        ("5.0", "5.0 x 5.0 mm  (~0.45 ct)", 5.0),
        ("5.5", "5.5 x 5.5 mm  (~0.65 ct)", 5.5),
        ("6.0", "6.0 x 6.0 mm  (~0.85 ct)", 6.0),
        ("6.5", "6.5 x 6.5 mm  (~1.05 ct / 1 ct)", 6.5),
        ("7.0", "7.0 x 7.0 mm  (~1.35 ct)", 7.0),
        ("8.0", "8.0 x 8.0 mm  (~2.10 ct / 2 ct)", 8.0),
    ],
    "TRILLIANT": [
        ("3.0", "3.0 x 3.0 mm  (~0.10 ct)", 3.0),
        ("4.0", "4.0 x 4.0 mm  (~0.22 ct)", 4.0),
        ("5.0", "5.0 x 5.0 mm  (~0.45 ct)", 5.0),
        ("6.0", "6.0 x 6.0 mm  (~0.85 ct)", 6.0),
        ("7.0", "7.0 x 7.0 mm  (~1.35 ct)", 7.0),
    ],
    "TRIANGLE": [
        ("3.0", "3.0 x 3.0 mm  (~0.10 ct)", 3.0),
        ("4.0", "4.0 x 4.0 mm  (~0.22 ct)", 4.0),
        ("5.0", "5.0 x 5.0 mm  (~0.45 ct)", 5.0),
        ("6.0", "6.0 x 6.0 mm  (~0.85 ct)", 6.0),
        ("7.0", "7.0 x 7.0 mm  (~1.35 ct)", 7.0),
    ],
}

GLOBAL_COMMERCIAL_SIZES = CUT_COMMERCIAL_SIZES["ROUND"]


def get_gem_size_preset_items(self, context) -> List[Tuple[str, str, str, int, int]]:
    """Callback dinámico para EnumProperty que entrega los calibres comerciales según el corte activo."""
    cut_key = getattr(context.scene, "j3d_community_gem_cut", "ROUND") if context and context.scene else "ROUND"
    sizes_list = CUT_COMMERCIAL_SIZES.get(cut_key, GLOBAL_COMMERCIAL_SIZES)

    items = []
    for i, (key, label, _) in enumerate(sizes_list):
        items.append((key, label, f"Calibre comercial {label}", 0, i))
    items.append(("CUSTOM", "Personalizado (mm libre)...", "Ajuste milimétrico manual libre", 0, len(items)))
    return items


def get_effective_gem_size(scene) -> float:
    """Calcula el tamaño milimétrico efectivo según el corte y preset comercial activo."""
    if not scene:
        return 1.0
    preset_key = getattr(scene, "j3d_community_gem_size_preset", "1.0")
    if preset_key == "CUSTOM":
        return getattr(scene, "j3d_community_gem_size", 1.0)

    cut_key = getattr(scene, "j3d_community_gem_cut", "ROUND")
    sizes_list = CUT_COMMERCIAL_SIZES.get(cut_key, GLOBAL_COMMERCIAL_SIZES)
    for key, _, mm_val in sizes_list:
        if key == preset_key:
            return mm_val
    try:
        return float(preset_key)
    except Exception:
        return 1.0


# ── Preview Collections Management ───────────────────────────────────────────
_preview_collections = {}


def get_cut_preview_collection():
    """Carga y cachea los iconos PNG de los 17 cortes.
    Busca primero en assets/gems/png (generados por el script),
    con fallback a assets/gems/dark (iconos legacy).
    """
    global _preview_collections
    if "cuts" in _preview_collections:
        return _preview_collections["cuts"]

    pcoll = bpy.utils.previews.new()
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Prioridad: png/ (script) → dark/ (legacy)
    png_dir  = os.path.join(base_dir, "assets", "gems", "png")
    dark_dir = os.path.join(base_dir, "assets", "gems", "dark")
    icons_dir = png_dir if os.path.isdir(png_dir) else dark_dir

    if os.path.isdir(icons_dir):
        for key, label, icon_file in CUT_DEFS:
            icon_path = os.path.join(icons_dir, icon_file)
            if not os.path.isfile(icon_path):
                icon_path = os.path.join(icons_dir, f"{key.lower()}.png")
            if os.path.isfile(icon_path):
                pcoll.load(key, icon_path, 'IMAGE')

    _preview_collections["cuts"] = pcoll
    return pcoll


def clear_previews():
    """Libera la memoria de previews al desregistrar."""
    global _preview_collections
    for pcoll in _preview_collections.values():
        try:
            bpy.utils.previews.remove(pcoll)
        except Exception:
            pass
    _preview_collections.clear()


def get_cut_enum_items(self, context):
    """Callback dinámico para EnumProperty con iconos de previsualización para los 17 cortes."""
    try:
        pcoll = get_cut_preview_collection()
    except Exception:
        pcoll = None

    items = []
    for i, (key, label, icon_file) in enumerate(CUT_DEFS):
        icon_id = 0
        if pcoll is not None and key in pcoll:
            icon_id = pcoll[key].icon_id
        items.append((key, label, f"Corte {label}", icon_id, i))
    return items


# ── Carat Weight Estimator ───────────────────────────────────────────────────
def calculate_carats(stone_key: str, cut_key: str, size_mm: float) -> float:
    """Calcula el peso estimado en quilates basado en densidad física, corte y volumen."""
    density = GEM_STONES.get(stone_key, GEM_STONES["DIAMOND"])["density"]
    vol_factor = CUT_VOLUME_FACTORS.get(cut_key, 1.00)
    # Calibración: Diamante Redondo 5.0mm = ~0.50 ct
    base_ct = (size_mm / 5.0) ** 3 * 0.50 * (density / 3.52) * vol_factor
    return max(0.001, round(base_ct, 3))


# ── BSDF Material Builder ────────────────────────────────────────────────────
def get_or_create_gem_material(stone_key: str):
    """Crea o reutiliza un material BSDF realista para la gema seleccionada."""
    mat_name = "J3D_Material_" + stone_key
    mat = bpy.data.materials.get(mat_name)
    if mat is not None:
        return mat

    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

    props = GEM_STONES.get(stone_key, GEM_STONES["DIAMOND"])
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 1.0
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 1.0

    bsdf.inputs['Base Color'].default_value = props["color"]
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['IOR'].default_value = props["ior"]
    return mat


# ── Procedural Gem Geometry Engine ───────────────────────────────────────────
def create_gem_mesh(
    cut_key: str = "ROUND",
    name: str = "Gem_Mesh",
    size_mm: float = 1.0,
    context: object = None,
) -> bpy.types.Mesh:
    """Genera una malla 3D procedural paramétrica para cualquiera de los 17 cortes estándar.
    Escala los vértices normalizados multiplicando por mm_to_bu(size_mm, context).
    """
    scale_bu = mm_to_bu(size_mm, context)
    key_upper = cut_key.upper() if cut_key else "ROUND"
    data = GEM_MESH_DATA.get(key_upper, GEM_MESH_DATA.get("ROUND"))

    bm = bmesh.new()
    verts = [
        bm.verts.new((v[0] * scale_bu, v[1] * scale_bu, v[2] * scale_bu))
        for v in data["verts"]
    ]
    bm.verts.ensure_lookup_table()

    for face_indices in data["faces"]:
        try:
            bm.faces.new([verts[i] for i in face_indices])
        except Exception:
            pass

    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = False

    mesh.update()
    return mesh


def create_round_brilliant_mesh(name: str = "Round_Diamond_Mesh", size_mm: float = 1.0, context: object = None) -> bpy.types.Mesh:
    """Genera una malla 3D de Talla Brillante Redonda."""
    return create_gem_mesh(cut_key="ROUND", name=name, size_mm=size_mm, context=context)


# ── Operators ─────────────────────────────────────────────────────────────────
class J3DComm_OT_dummy_cube(Operator):
    """Aniadir Cubo de Prueba 5mm"""
    bl_idname = "j3d_community.dummy_cube"
    bl_label = "Aniadir Cubo"
    bl_description = "Aniade un cubo de 5mm de referencia a la escena"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        cube_size = mm_to_bu(5.0, context)
        bpy.ops.mesh.primitive_cube_add(
            size=cube_size,
            location=context.scene.cursor.location
        )
        self.report({'INFO'}, "Cubo de 5 mm creado.")
        return {'FINISHED'}


class J3DComm_OT_add_gem(Operator):
    """Aniadir Gema 3D Facetada"""
    bl_idname = "j3d_community.add_gem"
    bl_label = "Aniadir Gema 3D"
    bl_description = "Aniade una gema 3D facetada en la posicion del cursor 3D"
    bl_options = {'REGISTER', 'UNDO'}

    cut: EnumProperty(name="Corte", items=get_cut_enum_items)
    stone: EnumProperty(name="Piedra", items=STONE_ITEMS, default="DIAMOND")
    size: FloatProperty(name="Tamano (mm)", default=0.0, min=0.0, max=50.0, step=10, precision=2)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        scene = context.scene
        cut_key = self.cut if self.cut else getattr(scene, "j3d_community_gem_cut", "ROUND")
        stone_key = self.stone if self.stone else getattr(scene, "j3d_community_gem_stone", "DIAMOND")

        if self.size > 0.0:
            size_mm = self.size
        else:
            size_mm = get_effective_gem_size(scene)

        mesh_data = create_gem_mesh(
            cut_key=cut_key,
            name=f"Gem_{cut_key.title()}_{size_mm:.1f}mm_Mesh",
            size_mm=size_mm,
            context=context
        )

        obj = bpy.data.objects.new(f"Gem_{stone_key.title()}_{cut_key.title()}_{size_mm:.1f}mm", mesh_data)
        context.collection.objects.link(obj)
        obj.location = context.scene.cursor.location

        obj["j3d_community_type"] = "GEM"
        obj["j3d_community_gem_cut"] = cut_key
        obj["j3d_community_gem_stone"] = stone_key
        obj["j3d_community_gem_size"] = size_mm

        ct = calculate_carats(stone_key, cut_key, size_mm)
        obj["j3d_community_carat"] = ct

        mat = get_or_create_gem_material(stone_key)
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

        for o in context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Gema {stone_key} {cut_key} ({size_mm:.1f} mm / {ct:.3f} ct) creada con éxito.")
        return {'FINISHED'}


# ── Scene Gem Inventory & Map Analyzer ────────────────────────────────────────
def _get_live_size_mm(obj: bpy.types.Object, context: bpy.types.Context) -> float:
    """Lee el tamaño real de la gema desde sus dimensiones actuales (soporta escala manual).
    Usa dimensions.x (anchura) como referencia principal.
    Fallback a custom prop j3d_community_gem_size si las dimensiones no son válidas.
    """
    try:
        bu_per_mm = mm_to_bu(1.0, context)
        dim_x = obj.dimensions.x  # anchura real en BU (incluye scale)
        if bu_per_mm > 1e-12 and dim_x > 1e-12:
            return dim_x / bu_per_mm
    except Exception:
        pass
    return float(obj.get("j3d_community_gem_size", 0.0))


def get_scene_gem_inventory(context: bpy.types.Context) -> Dict[str, Any]:
    """Escanea la escena en busca de gemas 3D y devuelve el inventario agrupado.
    El tamaño se lee en vivo desde obj.dimensions para reflejar escalas manuales.
    """
    scene = context.scene
    gems_found = []
    for obj in scene.objects:
        if obj.get("j3d_community_type") == "GEM" or ("j3d_community_gem_cut" in obj and "j3d_community_gem_size" in obj):
            cut = obj.get("j3d_community_gem_cut", "ROUND")
            stone = obj.get("j3d_community_gem_stone", "DIAMOND")
            # Lectura dimensional en vivo
            size = _get_live_size_mm(obj, context)
            carat = calculate_carats(stone, cut, size) if size > 0.0 else 0.0
            gems_found.append({
                "obj_name": obj.name,
                "cut": cut,
                "stone": stone,
                "size": size,
                "carat": carat,
            })

    # Agrupar por (cut, stone, size redondeado)
    grouped: Dict[Tuple[str, str, float], Dict[str, Any]] = {}
    for g in gems_found:
        key = (g["cut"], g["stone"], round(g["size"], 2))
        if key not in grouped:
            grouped[key] = {
                "cut": g["cut"],
                "stone": g["stone"],
                "size": g["size"],
                "count": 0,
                "total_carats": 0.0,
                "unit_carat": g["carat"],
            }
        grouped[key]["count"] += 1
        grouped[key]["total_carats"] += g["carat"]

    total_count = len(gems_found)
    total_carats = sum(g["carat"] for g in gems_found)
    records = list(grouped.values())
    records.sort(key=lambda r: (r["stone"], r["cut"], -r["size"]))

    return {
        "total_count": total_count,
        "total_carats": round(total_carats, 3),
        "records": records,
    }


class J3DComm_OT_calculate_gem_map(Operator):
    """Calcular y revisar el inventario de gemas en la escena"""
    bl_idname = "j3d_community.calculate_gem_map"
    bl_label = "Calcular / Revisar Gemas"
    bl_description = "Escanea la escena y contabiliza las piedras preciosas, calibres y quilates totales"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT'

    def execute(self, context: bpy.types.Context):
        inv = get_scene_gem_inventory(context)
        count = inv["total_count"]
        carats = inv["total_carats"]
        if count == 0:
            self.report({'INFO'}, "Mapa de Gemas: No se detectaron gemas en la escena activa.")
        else:
            n_groups = len(inv["records"])
            self.report(
                {'INFO'},
                f"Mapa de Gemas: {count} gemas ({n_groups} calibres distintos) — {carats:.3f} ct total."
            )
        return {'FINISHED'}


class J3DComm_OT_select_gems(Operator):
    """Seleccionar gemas en la escena por lote o todas"""
    bl_idname = "j3d_community.select_gems"
    bl_label = "Seleccionar Gemas"
    bl_description = "Selecciona en el viewport 3D las gemas coincidentes de este lote o todas las gemas"
    bl_options = {'REGISTER', 'UNDO'}

    cut: bpy.props.StringProperty(name="Corte", default="")  # type: ignore
    stone: bpy.props.StringProperty(name="Piedra", default="")  # type: ignore
    size_mm: bpy.props.FloatProperty(name="Calibre (mm)", default=0.0, precision=2)  # type: ignore
    select_all: bpy.props.BoolProperty(name="Seleccionar Todas", default=False)  # type: ignore
    extend: bpy.props.BoolProperty(name="Extender Selección", default=False)  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT'

    def execute(self, context: bpy.types.Context):
        scene = context.scene
        if not self.extend:
            bpy.ops.object.select_all(action='DESELECT')

        matched = []
        for obj in scene.objects:
            if obj.get("j3d_community_type") == "GEM" or ("j3d_community_gem_cut" in obj and "j3d_community_gem_size" in obj):
                if self.select_all:
                    matched.append(obj)
                    continue

                obj_cut = str(obj.get("j3d_community_gem_cut", ""))
                obj_stone = str(obj.get("j3d_community_gem_stone", ""))
                obj_size = round(_get_live_size_mm(obj, context), 2)

                cut_match = (not self.cut) or (obj_cut.upper() == self.cut.upper())
                stone_match = (not self.stone) or (obj_stone.upper() == self.stone.upper())
                size_match = (self.size_mm <= 0.0) or (abs(obj_size - round(self.size_mm, 2)) < 0.05)

                if cut_match and stone_match and size_match:
                    matched.append(obj)

        if not matched:
            self.report({'INFO'}, "No se encontraron gemas coincidentes.")
            return {'CANCELLED'}

        for obj in matched:
            obj.select_set(True)

        if matched:
            context.view_layer.objects.active = matched[0]

        if self.select_all:
            self.report({'INFO'}, f"Seleccionadas {len(matched)} gemas en la escena.")
        else:
            self.report(
                {'INFO'},
                f"Seleccionadas {len(matched)} gemas: {self.cut.title()} {self.stone.title()} {self.size_mm:.1f}mm"
            )
        return {'FINISHED'}


class J3DComm_OT_swap_gems(Operator):
    """Intercambiar corte, piedra o calibre de gema(s) seleccionadas"""
    bl_idname = "j3d_community.swap_gems"
    bl_label = "Intercambiar Gemas"
    bl_description = (
        "Cambia el corte, la piedra y/o el calibre de las gemas seleccionadas. "
        "Si tienen cortador asociado, lo regenera automaticamente."
    )
    bl_options = {'REGISTER', 'UNDO'}

    new_cut: EnumProperty(name="Nuevo Corte", items=get_cut_enum_items)  # type: ignore
    new_stone: EnumProperty(name="Nueva Piedra", items=STONE_ITEMS, default="DIAMOND")  # type: ignore
    new_size: FloatProperty(name="Nuevo Calibre (mm)", default=3.0, min=0.5, max=50.0, step=10, precision=2)  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return (
            context.mode == 'OBJECT'
            and any(obj.get("j3d_community_type") == "GEM" for obj in context.selected_objects)
        )

    def invoke(self, context: bpy.types.Context, event) -> set:
        scene = context.scene
        if hasattr(scene, "j3d_community_swap_cut"):
            self.new_cut = scene.j3d_community_swap_cut
        if hasattr(scene, "j3d_community_swap_stone"):
            self.new_stone = scene.j3d_community_swap_stone
        if hasattr(scene, "j3d_community_swap_size"):
            self.new_size = scene.j3d_community_swap_size
        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set:
        # Sincronizar con scene si no se definio explicitamente
        scene = context.scene
        if not self.properties.is_property_set("new_cut") and hasattr(scene, "j3d_community_swap_cut"):
            self.new_cut = scene.j3d_community_swap_cut
        if not self.properties.is_property_set("new_stone") and hasattr(scene, "j3d_community_swap_stone"):
            self.new_stone = scene.j3d_community_swap_stone
        if not self.properties.is_property_set("new_size") and hasattr(scene, "j3d_community_swap_size"):
            self.new_size = scene.j3d_community_swap_size

        # Importacion diferida para evitar importacion circular en el nivel de modulo
        from .cutters import rebuild_cutter_for_gem, find_cutter_for_gem

        gems = [o for o in context.selected_objects if o.get("j3d_community_type") == "GEM"]
        if not gems:
            self.report({'WARNING'}, "Selecciona al menos una gema primero.")
            return {'CANCELLED'}

        swapped = 0
        for gem_obj in gems:
            # Generar nuevo mesh
            new_mesh = create_gem_mesh(
                cut_key=self.new_cut,
                name=f"Gem_{self.new_cut.title()}_{self.new_size:.1f}mm_Mesh",
                size_mm=self.new_size,
                context=context,
            )
            # Reemplazar mesh preservando transforms
            old_mesh = gem_obj.data
            gem_obj.data = new_mesh
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)

            # Actualizar material si la piedra cambio
            new_mat = get_or_create_gem_material(self.new_stone)
            if not gem_obj.data.materials:
                gem_obj.data.materials.append(new_mat)
            else:
                gem_obj.data.materials[0] = new_mat

            # Actualizar custom props
            ct = calculate_carats(self.new_stone, self.new_cut, self.new_size)
            gem_obj["j3d_community_gem_cut"]   = self.new_cut
            gem_obj["j3d_community_gem_stone"] = self.new_stone
            gem_obj["j3d_community_gem_size"]  = self.new_size
            gem_obj["j3d_community_carat"]     = ct

            # Regenerar cortador asociado si existe
            cutter_obj = find_cutter_for_gem(gem_obj)
            if cutter_obj is not None:
                rebuild_cutter_for_gem(cutter_obj, self.new_cut, self.new_size, context)

            swapped += 1

        self.report(
            {'INFO'},
            f"{swapped} gema(s) -> {self.new_cut.title()} {self.new_size:.1f}mm {self.new_stone.title()}"
        )
        return {'FINISHED'}


classes = (
    J3DComm_OT_dummy_cube,
    J3DComm_OT_add_gem,
    J3DComm_OT_calculate_gem_map,
    J3DComm_OT_select_gems,
    J3DComm_OT_swap_gems,
)


def register():
    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        else:
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass
    clear_previews()

# ── Community Edition: restrict available cuts ──────────────────────────────
_COMMUNITY_CUTS = {'ROUND', 'OVAL', 'PRINCESS'}
CUT_DEFS = [entry for entry in CUT_DEFS if entry[0] in _COMMUNITY_CUTS]
CUT_COMMERCIAL_SIZES = {k: v for k, v in CUT_COMMERCIAL_SIZES.items() if k in _COMMUNITY_CUTS}
GLOBAL_COMMERCIAL_SIZES = CUT_COMMERCIAL_SIZES['ROUND']
