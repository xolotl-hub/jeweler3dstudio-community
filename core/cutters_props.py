"""
Jeweler 3D Studio - Cutters Object Properties & Class Registration
Definiciones de propiedades de objeto de cortadores booleanos (5 zonas)
y ciclo de vida de registro de clases y operadores.
"""

import bpy
from bpy.props import IntProperty, FloatProperty

OBJECT_CUTTER_PROPS = (
    "j3d_cutter_segments", "j3d_cutter_crease",
    "j3d_cutter_r_top", "j3d_cutter_z_top",
    "j3d_cutter_r_table", "j3d_cutter_z_table",
    "j3d_cutter_r_girdle_top", "j3d_cutter_z_girdle_top",
    "j3d_cutter_r_girdle_bot", "j3d_cutter_z_girdle_bot",
    "j3d_cutter_r_seat", "j3d_cutter_z_seat",
    "j3d_cutter_r_hole_bot", "j3d_cutter_z_hole_bot",
)

_FLOAT_PROP_SPECS = [
    ("j3d_cutter_crease", "Crease", "Pliegue (Shift+E)", 0.90, 0.0, 1.0, 2),
    ("j3d_cutter_r_top", "Radio Cima", "Radio perimetro cima superior (mm)", 0.350, 0.001, 100.0, 3),
    ("j3d_cutter_z_top", "Z Cima", "Posicion Z cima superior (mm)", 1.250, -100.0, 100.0, 3),
    ("j3d_cutter_r_table", "Radio Tabla", "Radio perimetro tabla (mm)", 0.350, 0.001, 100.0, 3),
    ("j3d_cutter_z_table", "Z Tabla", "Posicion Z tabla (mm)", 0.220, -100.0, 100.0, 3),
    ("j3d_cutter_r_girdle_top", "Radio Filetin Sup.", "Radio superior filetin (mm)", 0.580, 0.001, 100.0, 3),
    ("j3d_cutter_z_girdle_top", "Z Filetin Sup.", "Posicion Z superior filetin (mm)", 0.060, -100.0, 100.0, 3),
    ("j3d_cutter_r_girdle_bot", "Radio Filetin Inf.", "Radio inferior filetin (mm)", 0.580, 0.001, 100.0, 3),
    ("j3d_cutter_z_girdle_bot", "Z Filetin Inf.", "Posicion Z inferior filetin (mm)", -0.030, -100.0, 100.0, 3),
    ("j3d_cutter_r_seat", "Radio Asiento", "Radio cono de asiento (mm)", 0.317, 0.001, 100.0, 3),
    ("j3d_cutter_z_seat", "Z Asiento", "Posicion Z asiento (mm)", -0.266, -100.0, 100.0, 3),
    ("j3d_cutter_r_hole_bot", "Radio Perforacion", "Radio canal perforacion (mm)", 0.317, 0.001, 100.0, 3),
    ("j3d_cutter_z_hole_bot", "Z Perforacion", "Posicion Z fondo perforacion (mm)", -2.200, -100.0, 100.0, 3),
]


def register_cutter_properties(update_callback, classes):
    """Registra propiedades de cortadores en bpy.types.Object y registra clases de operadores."""
    bpy.types.Object.j3d_cutter_segments = IntProperty(
        name="Segmentos", description="Subdivisiones radiales", default=16, min=4, max=64,
        update=update_callback,
    )  # type: ignore

    for attr, name, desc, default, p_min, p_max, prec in _FLOAT_PROP_SPECS:
        prop = FloatProperty(
            name=name, description=desc, default=default, min=p_min, max=p_max,
            step=10, precision=prec, update=update_callback,
        )
        setattr(bpy.types.Object, attr, prop)

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


def unregister_cutter_properties(classes):
    """Desregistra clases y elimina atributos de propiedades en bpy.types.Object."""
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

    for prop in OBJECT_CUTTER_PROPS:
        if hasattr(bpy.types.Object, prop):
            try:
                delattr(bpy.types.Object, prop)
            except Exception:
                pass
