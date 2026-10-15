"""
Jeweler 3D Studio - Ring: Ring Size Operator

Operator for generating 3D circular Bezier curve or cylinder ring sizing reference.
"""

import bpy
from bpy.props import EnumProperty, FloatProperty, StringProperty
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from ._sizes import (
    RING_SYSTEM_ITEMS,
    US_SIZE_ITEMS,
    GEOMETRY_TYPE_ITEMS,
    ORIENTATION_ITEMS,
    get_ring_diameter,
    get_ring_circumference,
    _get_orientation_euler,
)
from ._geometry import create_ring_bezier_curve, create_ring_cylinder_mesh


class J3DComm_OT_create_ring_size(Operator, AddObjectHelper):
    """Generates base ring sizing geometry (Curve or Cylinder)"""
    bl_idname = "j3d_community.create_ring_size"
    bl_label = "Create Ring Size"
    bl_options = {'REGISTER', 'UNDO'}

    ring_system: EnumProperty(
        name="System",
        description="Ring sizing standard (US, UK, EU, JP)",
        items=RING_SYSTEM_ITEMS,
        default="US"
    )  # type: ignore

    ring_size: StringProperty(
        name="Size",
        description="Ring size in the selected system",
        default="7.0"
    )  # type: ignore

    us_size: EnumProperty(
        name="US Size",
        description="Standard US ring size selection (legacy / direct access)",
        items=US_SIZE_ITEMS,
        default="7.0"
    )  # type: ignore

    geometry_type: EnumProperty(
        name="Geometry Type",
        description="Geometry type to generate",
        items=GEOMETRY_TYPE_ITEMS,
        default="CURVE"
    )  # type: ignore

    orientation: EnumProperty(
        name="Orientation",
        description="Orientation plane for ring creation",
        items=ORIENTATION_ITEMS,
        default="FRONT"
    )  # type: ignore

    cylinder_depth: FloatProperty(
        name="Cylinder Depth (mm)",
        description="Depth/width of reference cylinder in mm",
        default=2.0,
        min=0.5,
        max=20.0,
        step=10,
        precision=2
    )  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT'

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "ring_system")
        if self.ring_system == "US":
            layout.prop(self, "us_size", text="US Size")
        else:
            layout.prop(self, "ring_size", text="Size")
        layout.prop(self, "geometry_type")
        layout.prop(self, "orientation")
        if self.geometry_type == 'CYLINDER':
            layout.prop(self, "cylinder_depth")
        layout.separator()
        layout.prop(self, "align", text="Alignment")
        layout.prop(self, "location", text="Location")
        layout.prop(self, "rotation", text="Rotation")

    def execute(self, context: bpy.types.Context) -> set:
        system = self.ring_system
        size_key = self.ring_size if self.ring_size else self.us_size
        if system == "US" and (not self.ring_size or self.ring_size == "7.0") and self.us_size:
            size_key = self.us_size

        dia_mm = get_ring_diameter(system, size_key)
        radius_mm = dia_mm / 2.0
        circ_mm = get_ring_circumference(dia_mm)
        obj_name = f"Ring_Size_{system}_{size_key.replace(' ', '_')}"

        if self.geometry_type == 'CURVE':
            obdata = create_ring_bezier_curve(f"{obj_name}_Curve", radius_mm)
        else:
            obdata = create_ring_cylinder_mesh(
                f"{obj_name}_Mesh", radius_mm, self.cylinder_depth
            )

        obj = object_data_add(context, obdata, operator=self)
        if all(abs(r) < 1e-5 for r in self.rotation):
            obj.rotation_euler = _get_orientation_euler(self.orientation)
        obj.name = obj_name
        obj["j3d_type"] = "RING_SIZE"
        obj["j3d_ring_system"] = system
        obj["j3d_ring_size"] = size_key
        obj["j3d_us_size"] = self.us_size
        obj["j3d_diameter_mm"] = dia_mm
        obj["j3d_circ_mm"] = circ_mm
        obj["j3d_radius_mm"] = radius_mm
        obj["j3d_orientation"] = self.orientation
        self.report(
            {'INFO'},
            f"Ring Size {system} {size_key} (Ø {dia_mm:.2f} mm | Circ {circ_mm:.1f} mm) created in {self.orientation}: {obj_name}"
        )
        return {'FINISHED'}
