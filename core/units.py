"""
Jeweler 3D Community - Core Units Module
Standardized unit conversion and Blender Scene Units synchronization for jewelry design.
Supports both Direct 1 BU = 1 mm (jewelry unit) and Scene Physical scaling.
"""

from typing import Optional
import bpy
from bpy.props import EnumProperty
from bpy.types import Operator



def get_unit_scale(context: Optional[bpy.types.Context] = None) -> float:
    """Return the current scene length scale (unit_settings.scale_length)."""
    try:
        ctx = context or bpy.context
        scale = ctx.scene.unit_settings.scale_length
        return scale if scale > 0.0 else 1.0
    except Exception:
        return 1.0


def mm_to_bu(value_mm: float, context: Optional[bpy.types.Context] = None) -> float:
    """Convert a length in millimeters to Blender Units (BU) using the active scale mode.

    - DIRECT_MM: 1 BU = 1 mm (5.0 mm -> 5.0 BU)
    - SCENE_PHYSICAL: (value_mm / 1000.0) / unit_scale (5.0 mm -> 0.005 BU en escala 1.0)
    """
    try:
        ctx = context or bpy.context
        scale_mode = getattr(ctx.scene, "j3d_scale_mode", "DIRECT_MM")
        if scale_mode == "DIRECT_MM":
            return float(value_mm)

        scale = ctx.scene.unit_settings.scale_length
        scale = scale if scale > 0.0 else 1.0
        return (value_mm / 1000.0) / scale
    except Exception:
        return float(value_mm)


def bu_to_mm(value_bu: float, context: Optional[bpy.types.Context] = None) -> float:
    """Convert a length in Blender Units (BU) to millimeters."""
    try:
        ctx = context or bpy.context
        scale_mode = getattr(ctx.scene, "j3d_scale_mode", "DIRECT_MM")
        if scale_mode == "DIRECT_MM":
            return float(value_bu)

        scale = ctx.scene.unit_settings.scale_length
        scale = scale if scale > 0.0 else 1.0
        return value_bu * scale * 1000.0
    except Exception:
        return float(value_bu)


class J3DComm_OT_set_scene_units(Operator):
    """Sets Blender scene units for jewelry design (millimeters)."""
    bl_idname = "j3d_community.set_scene_units"
    bl_label = "Set Scene Units"
    bl_description = "Sets metric units and 0.001 scale (1 BU = 1 mm) with millimeter display"
    bl_options = {'REGISTER', 'UNDO'}

    preset: EnumProperty(
        name="Unit Preset",
        items=[
            ("MILLIMETERS", "Jewelry Millimeters (0.001)", "Scale 0.001, millimeters for length, grams for mass"),
            ("METERS", "Meters (1.0)", "Scale 1.0, meters for length, kilograms for mass"),
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

            self.report({'INFO'}, "Scene configured to Millimeters (Scale 0.001, mm, g).")
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

            self.report({'INFO'}, "Scene configured to Meters (Scale 1.0, m, kg).")

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
