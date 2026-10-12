"""
Jeweler 3D Studio - Prongs Presets & Enums
Tip-type enum items, placement mode items, and adaptive default presets per gem cut/size.
"""

try:
    from mathutils import Vector
except ImportError:
    Vector = object  # type: ignore


TIP_TYPE_ITEMS = (
    ("DOME", "Round / Dome", "Classic rounded hemispherical dome tip"),
)

PLACEMENT_MODE_ITEMS = (
    ("SHARED",      "Shared / Common (Halo & Pavé)",
     "Garras compartidas en los valles entre piedras adyacentes para evitar colisiones"),
    ("INDEPENDENT", "Independent (Per-Gem)",
     "Garras independientes en cada gema según su preset individual"),
)


def get_default_prong_presets(gem_dim, cut_name: str) -> dict:
    """Returns optimal default prong parameters for a given gem cut and size."""
    size_y = max(0.5, gem_dim.y)
    gem_r  = size_y / 2.0

    if size_y <= 1.2:
        dia, z_top, z_bottom, inward, bump = 0.50, 0.35, 1.00, 3.0, 1.00
    elif size_y <= 2.0:
        dia, z_top, z_bottom, inward, bump = 0.60, 0.40, 1.40, 3.5, 0.80
    elif size_y <= 3.5:
        dia, z_top, z_bottom, inward, bump = 0.70, 0.50, 1.80, 4.0, 0.70
    else:
        dia, z_top, z_bottom, inward, bump = 0.80, 0.60, 2.20, 4.0, 0.50

    v_size_def   = round(max(0.15, gem_r * 0.54), 2)
    v_wall_def   = round(max(0.05, gem_r * 0.40), 2)
    v_depth_def  = round(max(0.05, gem_r * 0.30), 2)
    claw_off_def = round(max(0.05, dia * 0.30), 2)

    presets = {
        "number":        4,
        "diameter":      dia,
        "z_top":         z_top,
        "z_bottom":      z_bottom,
        "tip_type": "DOME",
        "position_deg":  45.0,
        "girdle_offset": 0.0,
        "inward_deg":    inward,
        "v_size":        v_size_def,
        "v_wall":        v_wall_def,
        "v_depth":       v_depth_def,
        "claw_tip_dia":  0.15,
        "claw_offset":   claw_off_def,
        "taper":         0.0,
        "bump_scale":    bump,
        "use_symmetry":  False,
        "detalization":  16,
    }

    cut = cut_name.upper()
    if cut in {"PRINCESS", "SQUARE"}:
        presets.update({
            "number":        4,
            "diameter":      0.40 if size_y <= 2.0 else 0.50,
            "position_deg":  45.0,
            "girdle_offset": -0.07,
            "tip_type": "DOME",
        })
    elif cut in {"OCTAGON", "EMERALD", "BAGUETTE"}:
        presets.update({
            "number":        4,
            "position_deg":  45.0,
            "girdle_offset": 0.0,
            "tip_type": "DOME",
        })
    elif cut in {"OVAL", "CUSHION", "MARQUISE"}:
        presets.update({
            "number":        4,
            "position_deg":  45.0,
            "girdle_offset": 0.0,
            "tip_type": "DOME",
        })
    elif cut in {"PEAR", "HEART"}:
        presets.update({
            "number":        4,
            "position_deg":  45.0,
            "girdle_offset": 0.0,
            "tip_type": "DOME",
        })
    elif cut in {"TRILLION", "TRILLIANT", "TRIANGLE"}:
        presets.update({
            "number":        3,
            "position_deg":  60.0,
            "girdle_offset": -0.07,
            "tip_type": "DOME",
        })

    return presets
