"""
Jeweler 3D Studio - Core Units Module
Standardized unit conversion and Blender Scene Units synchronization for jewelry design.
Supports both Direct 1 BU = 1 mm (Jewelry standard) and Scene Physical scaling.
"""

from typing import Optional, List, Tuple
import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

SCALE_MODE_ITEMS: List[Tuple[str, str, str]] = [
    ("DIRECT_MM", "1 BU = 1 mm (Directo)", "Modo modelado directo: 5 mm = 5.0 unidades en Blender"),
    ("SCENE_PHYSICAL", "Físico Real (Escena)", "Modo físico: 5 mm = 0.005 m adaptado a la escala de la escena"),
]


def get_unit_scale(context: Optional[bpy.types.Context] = None) -> float:
    """Retorna la escala de longitud actual de la escena (unit_settings.scale_length)."""
    try:
        ctx = context or bpy.context
        scale = ctx.scene.unit_settings.scale_length
        return scale if scale > 0.0 else 1.0
    except Exception:
        return 1.0


def mm_to_bu(value_mm: float, context: Optional[bpy.types.Context] = None) -> float:
    """Convierte una longitud en milímetros a Blender Units (BU) según el modo de escala activo.

    - DIRECT_MM: 1 BU = 1 mm (5.0 mm -> 5.0 BU)
    - SCENE_PHYSICAL: (value_mm / 1000.0) / unit_scale (5.0 mm -> 0.005 BU en escala 1.0)
    """
    try:
        ctx = context or bpy.context
        scale_mode = getattr(ctx.scene, "j3d_community_scale_mode", "DIRECT_MM")
        if scale_mode == "DIRECT_MM":
            return float(value_mm)

        scale = ctx.scene.unit_settings.scale_length
        scale = scale if scale > 0.0 else 1.0
        return (value_mm / 1000.0) / scale
    except Exception:
        return float(value_mm)


def bu_to_mm(value_bu: float, context: Optional[bpy.types.Context] = None) -> float:
    """Convierte una longitud en Blender Units (BU) a milímetros."""
    try:
        ctx = context or bpy.context
        scale_mode = getattr(ctx.scene, "j3d_community_scale_mode", "DIRECT_MM")
        if scale_mode == "DIRECT_MM":
            return float(value_bu)

        scale = ctx.scene.unit_settings.scale_length
        scale = scale if scale > 0.0 else 1.0
        return value_bu * scale * 1000.0
    except Exception:
        return float(value_bu)


class J3DComm_OT_set_scene_units(Operator):
    """Configura las unidades de la escena de Blender para diseño de joyería (Milímetros)."""
    bl_idname = "j3d_community.set_scene_units"
    bl_label = "Configurar Unidades de Escena"
    bl_description = "Ajusta la escena a Sistema Métrico, escala 0.001 (1 BU = 1 mm) y unidades en milímetros"
    bl_options = {'REGISTER', 'UNDO'}

    preset: EnumProperty(
        name="Preajuste de Unidades",
        items=[
            ("MILLIMETERS", "Milímetros Joyería (0.001)", "Escala 0.001, longitud en milímetros, masa en gramos"),
            ("METERS", "Metros Estándar (1.0)", "Escala 1.0, longitud en metros, masa en kilogramos"),
        ],
        default="MILLIMETERS"
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.scene is not None

    def execute(self, context: bpy.types.Context) -> set[str]:
        scene = context.scene
        units = scene.unit_settings

        if self.preset == "MILLIMETERS":
            units.system = 'METRIC'
            units.scale_length = 0.001
            units.length_unit = 'MILLIMETERS'
            units.mass_unit = 'GRAMS'

            # Optimizar clipping de 3D Viewport para escala milimétrica
            if hasattr(context, "screen") and context.screen:
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                space.clip_start = 0.1  # 0.1 mm
                                space.clip_end = 1000.0 # 1000 mm = 1 m
                                if hasattr(space, "overlay") and hasattr(space.overlay, "grid_scale"):
                                    space.overlay.grid_scale = 0.001

            self.report({'INFO'}, "Escena configurada a Milímetros (Escala 0.001, mm, g).")
        else:
            units.system = 'METRIC'
            units.scale_length = 1.0
            units.length_unit = 'METERS'
            units.mass_unit = 'KILOGRAMS'

            if hasattr(context, "screen") and context.screen:
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                space.clip_start = 0.01
                                space.clip_end = 1000.0
                                if hasattr(space, "overlay") and hasattr(space.overlay, "grid_scale"):
                                    space.overlay.grid_scale = 1.0

            self.report({'INFO'}, "Escena configurada a Metros (Escala 1.0, m, kg).")

        return {'FINISHED'}


classes = (
    J3DComm_OT_set_scene_units,
)


def register():
    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        try:
            bpy.utils.register_class(cls)
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
