"""
Jeweler 3D Community - Gems: Scene Gem Inventory & Map Analyzer

Live gemstone size detector and grouped inventory scanner for scene gemstone analysis.
"""

from typing import Dict, List, Tuple, Any
import bpy
from ..units import mm_to_bu
from ._geometry import calculate_carats


def _get_live_size_mm(obj: bpy.types.Object, context: bpy.types.Context) -> float:
    """Reads real gemstone size from current object dimensions (supports manual scaling).
    Uses dimensions.x (width) as principal reference.
    Fallback to custom prop j3d_gem_size if dimensions are invalid.
    """
    try:
        bu_per_mm = mm_to_bu(1.0, context)
        dim_x = obj.dimensions.x  # real width in BU (includes scale)
        if bu_per_mm > 1e-12 and dim_x > 1e-12:
            return dim_x / bu_per_mm
    except Exception:
        pass
    return float(obj.get("j3d_gem_size", 0.0))


def get_scene_gem_inventory(context: bpy.types.Context) -> Dict[str, Any]:
    """Scans the scene for 3D gemstones and returns the grouped inventory.
    Size is read live from obj.dimensions to reflect manual scaling.
    """
    scene = context.scene
    gems_found = []
    for obj in scene.objects:
        if obj.get("j3d_type") == "GEM" or ("j3d_gem_cut" in obj and "j3d_gem_size" in obj):
            cut = obj.get("j3d_gem_cut", "ROUND")
            stone = obj.get("j3d_gem_stone", "DIAMOND")
            # Live dimensional reading
            size = _get_live_size_mm(obj, context)
            carat = calculate_carats(stone, cut, size) if size > 0.0 else 0.0
            gems_found.append({
                "obj_name": obj.name,
                "cut": cut,
                "stone": stone,
                "size": size,
                "carat": carat,
            })

    # Group by (cut, stone, rounded size)
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
