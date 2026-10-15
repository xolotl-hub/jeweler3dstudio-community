"""
Jeweler 3D Studio - Gems: Preview Collections Management

Thumbnail preview collection loader for 17 luxury cuts and dynamic EnumProperty callbacks.
"""

import os
from pathlib import Path
import bpy
import bpy.utils.previews
from ._constants import CUT_DEFS, CUTS_RELEASED, _is_lab_tier

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
    base_dir = Path(__file__).resolve().parents[2]

    # Prioridad: png/ (script) → dark/ (legacy)
    png_dir = base_dir / "assets" / "gems" / "png"
    dark_dir = base_dir / "assets" / "gems" / "dark"
    icons_dir = png_dir if png_dir.is_dir() else dark_dir

    if icons_dir.is_dir():
        for key, label, icon_file in CUT_DEFS:
            icon_path = icons_dir / icon_file
            if not icon_path.is_file():
                icon_path = icons_dir / f"{key.lower()}.png"
            if icon_path.is_file():
                pcoll.load(key, str(icon_path), 'IMAGE')

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
    """Callback dinámico para EnumProperty con iconos de previsualización.
    En tiers de producción solo muestra los cortes de CUTS_RELEASED (Round y Oval).
    El tier Lab siempre expone los 17 cortes.
    """
    try:
        pcoll = get_cut_preview_collection()
    except Exception:
        pcoll = None

    lab = _is_lab_tier()
    items = []
    for key, label, icon_file in CUT_DEFS:
        if not lab and key not in CUTS_RELEASED:
            continue
        icon_id = 0
        if pcoll is not None and key in pcoll:
            icon_id = pcoll[key].icon_id
        items.append((key, label, f"Corte {label}", icon_id, len(items)))
    return items
