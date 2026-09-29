"""
Jeweler 3D Studio - Gem Topology Data Subpackage
Exports GEM_MESH_DATA (17 luxury cuts) assembled from per-family modules.
"""

_needs_reload = "_stepped" in locals()

from typing import Dict, Any

from . import _stepped, _fancy, _octagon, _round, _trillion

if _needs_reload:
    import importlib
    _stepped = importlib.reload(_stepped)
    _fancy = importlib.reload(_fancy)
    _octagon = importlib.reload(_octagon)
    _round = importlib.reload(_round)
    _trillion = importlib.reload(_trillion)

GEM_MESH_DATA: Dict[str, Dict[str, Any]] = (
    _stepped.DATA | _fancy.DATA | _octagon.DATA | _round.DATA | _trillion.DATA
)

__all__ = ["GEM_MESH_DATA"]
