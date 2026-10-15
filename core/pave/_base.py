"""
Jeweler 3D Studio — Pavé Base Strategy
Abstract protocol that every pavé technique must implement.
"""

from abc import ABC, abstractmethod
from typing import Set
import bpy


class PaveStrategy(ABC):
    """Abstract base class for all pavé placement strategies."""

    @abstractmethod
    def create_shirt(
        self,
        context: bpy.types.Context,
        source_obj: bpy.types.Object,
    ) -> bpy.types.Object | None:
        """
        Extract the user-defined zone from *source_obj* and return a new
        'shirt' mesh that floats above that zone.

        Returns the new shirt Object, or None on failure.
        """
        ...

    @abstractmethod
    def create_distribution(
        self,
        context: bpy.types.Context,
        shirt_obj: bpy.types.Object,
        gem_size_mm: float,
        spacing_mm: float,
    ) -> Set[str]:
        """
        Populate *shirt_obj* with gemstone instances using the strategy's
        placement algorithm.

        Returns a Blender operator result set, e.g. {'FINISHED'} or {'CANCELLED'}.
        """
        ...
