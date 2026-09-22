"""
Jeweler 3D Studio - Core Metrics Module
Provides metal density definitions and net mesh volume/weight calculations.
"""

from typing import Dict, Tuple, List, Optional
import bpy
import bmesh

# Real-world metal densities in g/cm³
METAL_DENSITIES: Dict[str, float] = {
    "GOLD_24K": 19.32,
    "GOLD_18K_YELLOW": 15.58,
    "GOLD_18K_WHITE": 15.90,
    "GOLD_14K": 13.07,
    "PLATINUM_950": 20.50,
    "SILVER_925": 10.36,
    "TITANIUM": 4.51,
}

METAL_ENUM_ITEMS: List[Tuple[str, str, str]] = [
    ("GOLD_24K", "Oro 24K", "Oro puro (19.32 g/cm³)"),
    ("GOLD_18K_YELLOW", "Oro 18K Amarillo", "Aleación de Oro 18K Amarillo (15.58 g/cm³)"),
    ("GOLD_18K_WHITE", "Oro 18K Blanco", "Aleación de Oro 18K Blanco (15.90 g/cm³)"),
    ("GOLD_14K", "Oro 14K", "Aleación de Oro 14K (13.07 g/cm³)"),
    ("PLATINUM_950", "Platino 950", "Platino 950 (20.50 g/cm³)"),
    ("SILVER_925", "Plata 925", "Plata esterlina 925 (10.36 g/cm³)"),
    ("TITANIUM", "Titanio", "Titanio Grado 5 (4.51 g/cm³)"),
]


def get_metal_density(metal_key: str) -> float:
    """Return density in g/cm³ for given metal identifier."""
    return METAL_DENSITIES.get(metal_key, METAL_DENSITIES["GOLD_18K_YELLOW"])


def calculate_mesh_volume_cm3(
    obj: bpy.types.Object,
    depsgraph: Optional[bpy.types.Depsgraph] = None
) -> float:
    """
    Calculate net volume of mesh object in cm³ accounting for active modifiers and scene scale.
    """
    if obj is None or obj.type != 'MESH':
        return 0.0

    if depsgraph is None:
        depsgraph = bpy.context.evaluated_depsgraph_get()

    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.transform(eval_obj.matrix_world)

    # Compute raw mesh volume in Blender internal cubic units
    raw_volume: float = abs(bm.calc_volume())

    bm.free()
    eval_obj.to_mesh_clear()

    # Scale conversion to cubic centimeters (cm³)
    # Standard Blender unit scale: 1 unit = 1m = 100cm -> volume factor = 100^3 = 1,000,000
    # Millimeter scale (unit_scale = 0.001): 1 unit = 1mm = 0.1cm -> volume factor = 0.1^3 = 0.001
    unit_scale: float = bpy.context.scene.unit_settings.scale_length
    conversion_factor: float = (unit_scale * 100.0) ** 3

    volume_cm3: float = raw_volume * conversion_factor
    return volume_cm3


def calculate_mesh_weight(
    obj: bpy.types.Object,
    metal_key: str,
    depsgraph: Optional[bpy.types.Depsgraph] = None
) -> float:
    """
    Calculate evaluated net weight in grams for a given mesh object and metal type.
    """
    volume_cm3: float = calculate_mesh_volume_cm3(obj, depsgraph)
    density: float = get_metal_density(metal_key)
    return volume_cm3 * density
