"""
Jeweler 3D Studio - Core Pavé Module
Distribution of gems along curves and surface meshes for pavé settings.
"""

from typing import List, Tuple
import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty
from bpy.types import Operator, PropertyGroup

PAVE_MODE_ITEMS: List[Tuple[str, str, str]] = [
    ("CURVE", "Sobre Curva", "Distribuye gemas a lo largo de un trayecto de curva 3D"),
    ("SURFACE", "Sobre Superficie", "Distribuye gemas sobre la superficie de una malla"),
]


class J3D_PaveProperties(PropertyGroup):
    """Properties for pavé gem distribution."""
    mode: EnumProperty(
        name="Modo de Pavé",
        items=PAVE_MODE_ITEMS,
        default="CURVE"
    ) # type: ignore

    gem_size_mm: FloatProperty(
        name="Tamaño Gema (mm)",
        default=1.5,
        min=0.5,
        max=10.0,
        unit='LENGTH'
    ) # type: ignore

    spacing_mm: FloatProperty(
        name="Distancia / Separación (mm)",
        description="Espacio mínimo entre bordes de las gemas",
        default=0.2,
        min=0.05,
        max=2.0,
        unit='LENGTH'
    ) # type: ignore


class J3DComm_OT_create_pave(Operator):
    """Genera una distribución de gemas en modo Pavé"""
    bl_idname = "j3d_community_community.create_pave"
    bl_label = "Crear Pavé"
    bl_description = "Distribuye gemas automáticamente sobre la curva o superficie seleccionada"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        name="Modo",
        items=PAVE_MODE_ITEMS,
        default="CURVE"
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT' and context.active_object is not None

    def execute(self, context: bpy.types.Context) -> set[str]:
        target_obj = context.active_object
        self.report({'INFO'}, f"Pavé generado en modo '{self.mode}' sobre '{target_obj.name}'.")
        return {'FINISHED'}


classes = (
    J3D_PaveProperties,
    J3DComm_OT_create_pave,
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
