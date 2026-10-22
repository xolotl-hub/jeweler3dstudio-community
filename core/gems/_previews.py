"""
Jeweler 3D Community - Gems: Preview Collections Management

Thumbnail preview collection loader for 17 luxury cuts and dynamic EnumProperty callbacks.
"""

import os
from pathlib import Path
import bpy
import bpy.utils.previews
from ._constants import CUT_DEFS, AVAILABLE_CUTS

_preview_collections = {}


def get_cut_preview_collection():
    """Load and cache gem cut preview icons.

    Look first in assets/gems/png, then fall back to assets/gems/dark.
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
    """Release preview memory when unregistering the add-on."""
    global _preview_collections
    for pcoll in _preview_collections.values():
        try:
            bpy.utils.previews.remove(pcoll)
        except Exception:
            pass
    _preview_collections.clear()


def get_cut_enum_items(self, context):
    """Return dynamic EnumProperty items with preview icons for available cuts."""
    try:
        pcoll = get_cut_preview_collection()
    except Exception:
        pcoll = None

    items = []
    for key, label, icon_file in CUT_DEFS:
        if key not in AVAILABLE_CUTS:
            continue
        icon_id = 0
        if pcoll is not None and key in pcoll:
            icon_id = pcoll[key].icon_id
        description = f"{bpy.app.translations.pgettext_iface('Cut')} {label}"
        items.append((key, label, description, icon_id, len(items)))
    return items
