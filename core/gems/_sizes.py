"""
Jeweler 3D Community - Gems: Commercial Size Charts & Presets

Standard commercial size tables by cut according to international jewelry trade standards,
dynamic callbacks for EnumProperty presets, and effective millimeter size calculation.
"""

from typing import Dict, List, Tuple
import bpy
from ._sizes_data import CUT_COMMERCIAL_SIZES

GLOBAL_COMMERCIAL_SIZES = CUT_COMMERCIAL_SIZES["ROUND"]


def get_gem_size_preset_items(self, context) -> List[Tuple[str, str, str, int, int]]:
    """Return commercial size presets for the active cut as EnumProperty items."""
    cut_key = "ROUND"
    if hasattr(self, "gem_cut") and self.gem_cut:
        cut_key = self.gem_cut
    elif context and context.scene:
        j3d = getattr(context.scene, "j3d", None)
        if j3d and hasattr(j3d, "gem_cut") and j3d.gem_cut:
            cut_key = j3d.gem_cut
        else:
            cut_key = getattr(context.scene, "j3d_gem_cut", "ROUND") or "ROUND"

    sizes_list = CUT_COMMERCIAL_SIZES.get(cut_key, GLOBAL_COMMERCIAL_SIZES)

    items = []
    for i, (key, label, _) in enumerate(sizes_list):
        description = f"{bpy.app.translations.pgettext_iface('Commercial size')} {label}"
        items.append((key, label, description, 0, i))
    custom_label = bpy.app.translations.pgettext_iface("Custom (free mm)...")
    custom_description = bpy.app.translations.pgettext_iface("Free manual millimeter size")
    items.append(("CUSTOM", custom_label, custom_description, 0, len(items)))
    return items


def get_effective_gem_size(scene) -> float:
    """Calculate the effective millimeter size from the active cut and size preset."""
    if not scene:
        return 1.0
    j3d = getattr(scene, "j3d", None)
    if j3d and hasattr(j3d, "gem_size_preset"):
        preset_key = j3d.gem_size_preset
    else:
        preset_key = getattr(scene, "j3d_gem_size_preset", "1.0")

    if preset_key == "CUSTOM":
        if j3d and hasattr(j3d, "gem_size"):
            return float(j3d.gem_size)
        return float(getattr(scene, "j3d_gem_size", 1.0))

    if j3d and hasattr(j3d, "gem_cut") and j3d.gem_cut:
        cut_key = j3d.gem_cut
    else:
        cut_key = getattr(scene, "j3d_gem_cut", "ROUND") or "ROUND"

    sizes_list = CUT_COMMERCIAL_SIZES.get(cut_key, GLOBAL_COMMERCIAL_SIZES)
    for key, _, mm_val in sizes_list:
        if key == preset_key:
            return mm_val
    try:
        return float(preset_key)
    except Exception:
        return 1.0
