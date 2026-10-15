"""
Jeweler 3D Studio — Pavé: Geodesic  [STUB]
Expande un frente geodésico desde un punto semilla sobre la superficie
del mesh, colocando gemas a distancias geodésicas uniformes.
Ideal para superficies de alta curvatura donde la grilla UV distorsiona.

Estado: stub — pendiente de implementación.
"""
from ._base import PaveStrategy


class GeodesicStrategy(PaveStrategy):
    """Distribución pavé geodésica (frente de onda sobre malla)."""

    def create_shirt(self, context, source_obj):  # type: ignore[override]
        raise NotImplementedError("GeodesicStrategy.create_shirt — pendiente")

    def create_distribution(self, context, shirt_obj, gem_size_mm=1.5, spacing_mm=0.2):  # type: ignore[override]
        raise NotImplementedError("GeodesicStrategy.create_distribution — pendiente")
