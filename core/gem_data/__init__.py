"""
Jeweler 3D Studio - Gem Topology Data Subpackage
Exports GEM_MESH_DATA (17 luxury cuts) assembled from per-family modules.
"""
from typing import Dict, Any

from ._stepped import DATA as _stepped_data
from ._fancy import DATA as _fancy_data
from ._octagon import DATA as _octagon_data
from ._round import DATA as _round_data
from ._trillion import DATA as _trillion_data

GEM_MESH_DATA: Dict[str, Dict[str, Any]] = (
    _stepped_data | _fancy_data | _octagon_data | _round_data | _trillion_data
)

__all__ = ["GEM_MESH_DATA"]
