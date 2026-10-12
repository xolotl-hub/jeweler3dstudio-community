r"""
Jeweler 3D Studio - Prongs Geometry Engine (Facade)
Backward-compatible re-export of single and cluster prongs geometry engines.
Submodules:
  _tips    — Tip profiles, creases, caps and loop helpers
  _single  — Single prong geometry and radial array distribution
  _cluster — Multi-gem spatial clustering, Voronoi/Apollonius and shared prongs
"""

from ._tips import (
    _circle_verts,
    _bridge_loops,
    _mark_loop_crease,
    _mark_vertical_creases,
    _build_bottom_cap,
    _build_top_flat_cap,
    _build_v_prong_coords,
    _build_tip,
)
from ._single import (
    create_single_prong,
    generate_prongs_bmesh,
)
from ._cluster import (
    _get_gem_spatial_info,
    calculate_cluster_prong_positions,
    generate_cluster_prongs_bmesh,
)

__all__ = [
    "create_single_prong",
    "generate_prongs_bmesh",
    "_get_gem_spatial_info",
    "calculate_cluster_prong_positions",
    "generate_cluster_prongs_bmesh",
]
