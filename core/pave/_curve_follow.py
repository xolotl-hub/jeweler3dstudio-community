"""
Jeweler 3D Studio — Pavé: Curve Follow  [STUB]
Distribuye gemas a lo largo de una curva Bézier/NURBS respetando la superficie
del objeto de referencia mediante Shrinkwrap.

Estado: stub — pendiente de implementación.
"""
from ._base import PaveStrategy


class CurveFollowStrategy(PaveStrategy):
    """Distribución pavé a lo largo de curva."""

    def create_shirt(self, context, source_obj):  # type: ignore[override]
        raise NotImplementedError("CurveFollowStrategy.create_shirt — pendiente")

    def create_distribution(self, context, shirt_obj, gem_size_mm=1.5, spacing_mm=0.2):  # type: ignore[override]
        raise NotImplementedError("CurveFollowStrategy.create_distribution — pendiente")
