"""
Jeweler 3D Studio - Unified Scene PropertyGroup
All add-on scene-level properties collected in one J3D_SceneSettings group
and registered as ``bpy.types.Scene.j3d``.  Access from panels / operators:

    scene.j3d.us_size
    scene.j3d.gem_cut
    ...
"""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup

from ...core.ring import (
    GEOMETRY_TYPE_ITEMS,
    ORIENTATION_ITEMS,
    RING_PROFILE_ITEMS,
    US_SIZE_ITEMS,
)
from ...core.gems import (
    STONE_ITEMS,
    get_cut_enum_items,
    get_gem_size_preset_items,
)


def _on_gem_cut_update(self, context) -> None:
    """Resets or validates gem_size_preset when gem_cut changes to prevent stale enum keys."""
    try:
        from ...core.gems import CUT_COMMERCIAL_SIZES, GLOBAL_COMMERCIAL_SIZES
        sizes_list = CUT_COMMERCIAL_SIZES.get(self.gem_cut, GLOBAL_COMMERCIAL_SIZES)
        valid_keys = {k for k, _, _ in sizes_list}
        valid_keys.add("CUSTOM")
        if self.gem_size_preset not in valid_keys and sizes_list:
            self.gem_size_preset = sizes_list[0][0]
    except Exception:
        pass


class J3D_SceneSettings(PropertyGroup):
    """Unified scene settings for Jeweler 3D Studio."""

    # ------------------------------------------------------------------
    # Ring & Size
    # ------------------------------------------------------------------

    us_size: EnumProperty(
        name="US Ring Size",
        description="Standard US ring size selection (includes half sizes)",
        items=US_SIZE_ITEMS,
        default="7.0",
    )  # type: ignore

    geometry_type: EnumProperty(
        name="Geometry Type",
        description="Output geometry format for ring sizing",
        items=GEOMETRY_TYPE_ITEMS,
        default="CURVE",
    )  # type: ignore

    ring_orientation: EnumProperty(
        name="Orientation",
        description="Orientation plane for ring creation",
        items=ORIENTATION_ITEMS,
        default="FRONT",
    )  # type: ignore

    # ------------------------------------------------------------------
    # Metal Profile / Shank
    # ------------------------------------------------------------------

    ring_profile: EnumProperty(
        name="Profile",
        description="Ring shank cross-section profile",
        items=RING_PROFILE_ITEMS,
        default="MEDIA_CANA",
    )  # type: ignore

    ring_width: FloatProperty(
        name="Width",
        description="Ring band width in mm",
        default=3.0,
        min=1.0,
        max=20.0,
        step=10,
        precision=2,
    )  # type: ignore

    ring_height: FloatProperty(
        name="Thickness",
        description="Ring band thickness in mm (grows outwards from inner diameter)",
        default=1.5,
        min=0.3,
        max=10.0,
        step=10,
        precision=2,
    )  # type: ignore

    ring_radial_segments: IntProperty(
        name="Radial Segments",
        description="Number of circumferential divisions along the ring",
        default=16,
        min=8,
        max=256,
    )  # type: ignore

    ring_profile_segments: IntProperty(
        name="Profile Resolution",
        description="Number of subdivisions for curved profile sections",
        default=2,
        min=2,
        max=64,
    )  # type: ignore

    ring_use_subsurf: BoolProperty(
        name="Subdivision Surface",
        description="Add Subdivision Surface modifier",
        default=True,
    )  # type: ignore

    ring_subsurf_levels: IntProperty(
        name="Subsurf Level",
        description="Subdivision level for viewport and render",
        default=2,
        min=1,
        max=5,
    )  # type: ignore

    ring_crease: FloatProperty(
        name="Edge Crease",
        description="Crease factor (Shift+E) on sharp corners (0.8 = natural polished edge)",
        default=0.8,
        min=0.0,
        max=1.0,
        step=5,
        precision=2,
    )  # type: ignore

    # ------------------------------------------------------------------
    # Gems – Add Gem panel
    # ------------------------------------------------------------------

    gem_cut: EnumProperty(
        name="Cut",
        description="Gemstone cut selection",
        items=get_cut_enum_items,
        update=_on_gem_cut_update,
    )  # type: ignore

    gem_stone: EnumProperty(
        name="Stone",
        description="Gemstone material type",
        items=STONE_ITEMS,
        default="DIAMOND",
    )  # type: ignore

    gem_size_preset: EnumProperty(
        name="Commercial Size",
        description="Standard commercial market sizes for selected cut",
        items=get_gem_size_preset_items,
        default=0,
    )  # type: ignore

    gem_size: FloatProperty(
        name="Size",
        description="Gemstone size in millimeters (custom mode)",
        default=1.0,
        min=0.5,
        max=50.0,
        step=10,
        precision=2,
    )  # type: ignore

    # ------------------------------------------------------------------
    # Gems – Swap Gems panel
    # ------------------------------------------------------------------

    swap_cut: EnumProperty(
        name="New Cut",
        description="Cut selection for gem replacement",
        items=get_cut_enum_items,
    )  # type: ignore

    swap_stone: EnumProperty(
        name="New Stone",
        description="Gemstone material type for replacement",
        items=STONE_ITEMS,
        default="DIAMOND",
    )  # type: ignore

    swap_size: FloatProperty(
        name="New Size",
        description="New size in millimeters for replacement",
        default=3.0,
        min=0.5,
        max=50.0,
        step=10,
        precision=2,
    )  # type: ignore

    # ------------------------------------------------------------------
    # Cutters
    # ------------------------------------------------------------------

    cutter_segments: IntProperty(
        name="Cutter Segments",
        description="Radial segments for seat cutter (default 8)",
        default=8,
        min=4,
        max=64,
    )  # type: ignore

    cutter_crease: FloatProperty(
        name="Cutter Crease",
        description="Edge crease (Shift+E) for Subdivision Surface",
        default=0.8,
        min=0.0,
        max=1.0,
        step=10,
        precision=2,
    )  # type: ignore


# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------

def register() -> None:
    bpy.utils.register_class(J3D_SceneSettings)
    bpy.types.Scene.j3d = PointerProperty(type=J3D_SceneSettings)  # type: ignore


def unregister() -> None:
    if hasattr(bpy.types.Scene, "j3d"):
        del bpy.types.Scene.j3d
    bpy.utils.unregister_class(J3D_SceneSettings)
