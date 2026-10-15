"""
Jeweler 3D Studio — Pavé: Geometry Nodes Driver  [STUB]
Genera un árbol de Geometry Nodes que distribuye instancias de gemas
proceduralmente sobre la zona seleccionada, completamente no-destructivo.

Estado: stub — pendiente de implementación.
"""
from ._base import PaveStrategy


class GNDriverStrategy(PaveStrategy):
    """Distribución pavé via Geometry Nodes (no-destructiva)."""

    def create_shirt(self, context, source_obj):  # type: ignore[override]
        raise NotImplementedError("GNDriverStrategy.create_shirt — pendiente")

    def create_distribution(self, context, shirt_obj, gem_size_mm=1.5, spacing_mm=0.2):  # type: ignore[override]
        raise NotImplementedError("GNDriverStrategy.create_distribution — pendiente")
