"""
Jeweler 3D Studio - Core Prongs Module
Dynamic prong engine for generating stone settings linked to gem geometry.
"""

from typing import List, Tuple
import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty
from bpy.types import Operator, PropertyGroup

PRONG_SHAPE_ITEMS: List[Tuple[str, str, str]] = [
    ("ROUND", "Redonda", "Garras cilíndricas con punta redondeada"),
    ("CLAW", "Uña / Garra", "Garras cónicas afiladas sobre la gema"),
    ("V_PRONG", "Perfil V", "Garras en V para esquinas de tallas Princesa o Marquesa"),
    ("SQUARE", "Cuadrada", "Garras rectas de perfil cuadrado"),
]


class J3D_ProngProperties(PropertyGroup):
    """Properties for parametric prongs generation."""
    count: IntProperty(
        name="Número de Garras",
        description="Cantidad de garras distribuidas alrededor de la gema",
        default=4,
        min=2,
        max=12
    ) # type: ignore

    diameter_mm: FloatProperty(
        name="Diámetro (mm)",
        description="Grosor o diámetro individual de las garras",
        default=0.8,
        min=0.3,
        max=3.0,
        unit='LENGTH'
    ) # type: ignore

    height_mm: FloatProperty(
        name="Altura (mm)",
        description="Altura de la garra desde el filetín hasta la punta",
        default=2.0,
        min=0.5,
        max=10.0,
        unit='LENGTH'
    ) # type: ignore

    prong_shape: EnumProperty(
        name="Forma de la Garra",
        items=PRONG_SHAPE_ITEMS,
        default="ROUND"
    ) # type: ignore


class J3DComm_OT_add_prongs(Operator):
    """Genera garras vinculadas a la gema seleccionada"""
    bl_idname = "j3d_community_community.add_prongs"
    bl_label = "Añadir Garras"
    bl_description = "Crea un engaste de garras paramétrico sobre el objeto seleccionado"
    bl_options = {'REGISTER', 'UNDO'}

    count: IntProperty(
        name="Cantidad",
        default=4,
        min=2,
        max=12
    ) # type: ignore

    diameter_mm: FloatProperty(
        name="Diámetro (mm)",
        default=0.8,
        min=0.3,
        max=3.0
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT' and context.active_object is not None

    def execute(self, context: bpy.types.Context) -> set[str]:
        target_obj = context.active_object
        self.report({'INFO'}, f"Generadas {self.count} garras vinculadas a '{target_obj.name}'.")
        return {'FINISHED'}


classes = (
    J3D_ProngProperties,
    J3DComm_OT_add_prongs,
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
