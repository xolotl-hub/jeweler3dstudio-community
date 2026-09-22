"""
Jeweler 3D Studio - UI Gizmos Module
Provides interactive viewport GizmoGroups for visual manipulation of gems, prongs, and cutters.
"""

from typing import Optional
import bpy
from bpy.types import GizmoGroup, Context


class J3DComm_GGT_gem_controls(GizmoGroup):
    """GizmoGroup para manipular tiradores visuales de gemas y cortadores en el viewport 3D."""
    bl_idname = "J3DComm_GGT_gem_controls"
    bl_label = "Jeweler 3D Gem Controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        obj = context.active_object
        return (
            context.mode == 'OBJECT'
            and obj is not None
            and obj.type in {'MESH', 'CURVE'}
            and "j3d_community_type" in obj
        )

    def setup(self, context: Context) -> None:
        """Inicializa tiradores interactivos (Gizmos) en pantalla."""
        # Standard dial / arrow gizmo handle hook
        gz = self.gizmos.new("GIZMO_GT_arrow_3d")
        gz.target_set_prop("matrix", context.active_object, "matrix_world")
        gz.draw_style = 'BOX'
        gz.color = (0.2, 0.8, 1.0)
        gz.alpha = 0.5
        gz.color_highlight = (1.0, 0.9, 0.1)
        gz.alpha_highlight = 0.8
        self.gem_gizmo = gz

    def refresh(self, context: Context) -> None:
        """Actualiza la posición y escala de los gizmos según la matriz del objeto."""
        obj = context.active_object
        if obj and hasattr(self, "gem_gizmo"):
            self.gem_gizmo.matrix_basis = obj.matrix_world.normalized()


classes = (
    J3DComm_GGT_gem_controls,
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            try:
                bpy.utils.unregister_class(cls)
                bpy.utils.register_class(cls)
            except Exception:
                pass


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
        except Exception:
            pass


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        else:
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass
