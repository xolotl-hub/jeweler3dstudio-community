"""
Jeweler 3D Studio — Pavé: UV Grid  [STUB]
Proyecta una cuadrícula regular sobre el espacio UV del objeto y coloca gemas
en las intersecciones, proyectando de vuelta al espacio 3D.

Estado: stub — pendiente de implementación.
"""
from ._base import PaveStrategy


class UVGridStrategy(PaveStrategy):
    """Distribución pavé en grilla UV."""

    def create_shirt(self, context, source_obj):  # type: ignore[override]
        raise NotImplementedError("UVGridStrategy.create_shirt — pendiente")

    def create_distribution(self, context, shirt_obj, gem_size_mm=1.5, spacing_mm=0.2):  # type: ignore[override]
        raise NotImplementedError("UVGridStrategy.create_distribution — pendiente")
