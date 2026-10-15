"""
Jeweler 3D Studio — Pavé Package
=================================
Subpaquete modular para distribución de gemas tipo pavé.

Técnicas disponibles
--------------------
  face_shirt   → Camisa de Cara (MVP): selección/pintura → offset → Poisson + BVH
  curve_follow → [stub] distribución a lo largo de curva
  uv_grid      → [stub] cuadrícula proyectada sobre UV
  gn_driver    → [stub] Geometry Nodes no-destructivo
  geodesic     → [stub] frente geodésico

Los 3 operadores del flujo MVP:
  j3d.pave_enter_zone     — Pintado / Selección
  j3d.pave_create_shirt   — Crear Camisa
  j3d.pave_distribute     — Crear Distribución
"""

_needs_reload = "bpy" in locals()

from . import _face_shirt

if _needs_reload:
    import importlib
    _face_shirt = importlib.reload(_face_shirt)

# Strategies publicly accessible
from ._base import PaveStrategy
from ._face_shirt import FaceShirtStrategy

classes = _face_shirt.classes


def register():
    _face_shirt.register()


def unregister():
    _face_shirt.unregister()
