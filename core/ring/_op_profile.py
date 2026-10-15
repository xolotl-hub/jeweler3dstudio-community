"""
Jeweler 3D Studio - Ring: Ring Profile Shank Operator

Operator for creating full 3D ring shanks with parametric cross-sections and subdivision crease.
"""

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, BoolProperty, StringProperty
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from ._sizes import (
    RING_SYSTEM_ITEMS,
    US_SIZE_ITEMS,
    ORIENTATION_ITEMS,
    get_ring_diameter,
    get_ring_circumference,
    _get_orientation_euler,
)
from ._profiles import RING_PROFILE_ITEMS
from ._geometry import create_ring_profile_mesh


class J3DComm_OT_create_ring_profile(Operator, AddObjectHelper):
    """Creates complete 3D ring shank with parametric cross-section profile and subdivision crease"""
    bl_idname = "j3d_community.create_ring_profile"
    bl_label = "Create Ring Shank"
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
        description="Defines INNER diameter of ring (legacy / direct access)",
        items=US_SIZE_ITEMS, default="7.0"
    )  # type: ignore

    profile_type: EnumProperty(
        name="Profile",
        description="Metal cross-section shape",
        items=RING_PROFILE_ITEMS, default="MEDIA_CANA"
    )  # type: ignore

    orientation: EnumProperty(
        name="Orientation",
        description="Orientation plane for ring creation",
        items=ORIENTATION_ITEMS,
        default="FRONT"
    )  # type: ignore

    width_mm: FloatProperty(
        name="Width (mm)",
        description="Ring width along finger axis in mm",
        default=3.0, min=1.0, max=20.0, step=10, precision=2
    )  # type: ignore

    height_mm: FloatProperty(
        name="Thickness (mm)",
        description="Radial metal thickness in mm (grows outwards from inner diameter)",
        default=1.5, min=0.3, max=10.0, step=10, precision=2
    )  # type: ignore

    radial_segments: IntProperty(
        name="Radial Segments",
        description="Number of circumferential divisions around the ring",
        default=16, min=8, max=256
    )  # type: ignore

    profile_segments: IntProperty(
        name="Profile Resolution",
        description="Number of subdivisions on curved profile sections",
        default=2, min=2, max=64
    )  # type: ignore

    use_subsurf: BoolProperty(
        name="Subdivision Surface",
        description="Add Subdivision Surface modifier",
        default=True
    )  # type: ignore

    subsurf_levels: IntProperty(
        name="Subsurf Level",
        description="Subdivision level for viewport and render",
        default=2, min=1, max=5
    )  # type: ignore

    crease_value: FloatProperty(
        name="Edge Crease",
        description="Crease sharpness (Shift+E) on sharp corners (0.8 gives subtle polished rounding)",
        default=0.8, min=0.0, max=1.0, step=5, precision=2
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
        layout.prop(self, "profile_type")
        layout.prop(self, "orientation")
        layout.separator()
        layout.prop(self, "width_mm")
        layout.prop(self, "height_mm")
        layout.separator()
        layout.prop(self, "radial_segments")
        layout.prop(self, "profile_segments")
        layout.separator()
        layout.prop(self, "use_subsurf")
        if self.use_subsurf:
            layout.prop(self, "subsurf_levels")
            layout.prop(self, "crease_value")
        layout.separator()
        layout.prop(self, "align", text="Alignment")
        layout.prop(self, "location", text="Location")
        layout.prop(self, "rotation", text="Rotation")

    def execute(self, context: bpy.types.Context) -> set:
        system = self.ring_system
        size_key = self.ring_size if self.ring_size else self.us_size
        if system == "US" and (not self.ring_size or self.ring_size == "7.0") and self.us_size:
            size_key = self.us_size

        inner_dia_mm = get_ring_diameter(system, size_key)
        inner_radius_mm = inner_dia_mm / 2.0
        circ_mm = get_ring_circumference(inner_dia_mm)

        obj_name = (
            f"Ring_{system}{size_key.replace(' ', '_')}_{self.profile_type}"
            f"_{self.width_mm:.1f}x{self.height_mm:.1f}mm"
        )
        mesh = create_ring_profile_mesh(
            name=obj_name + "_Mesh",
            inner_radius_mm=inner_radius_mm,
            width_mm=self.width_mm,
            height_mm=self.height_mm,
            profile_key=self.profile_type,
            n_ring=self.radial_segments,
            profile_segments=self.profile_segments,
            crease_value=self.crease_value if self.use_subsurf else 0.0,
        )

        obj = object_data_add(context, mesh, operator=self)
        if all(abs(r) < 1e-5 for r in self.rotation):
            obj.rotation_euler = _get_orientation_euler(self.orientation)
        obj.name = obj_name
        obj["j3d_type"] = "RING_PROFILE"
        obj["j3d_ring_system"] = system
        obj["j3d_ring_size"] = size_key
        obj["j3d_us_size"] = self.us_size
        obj["j3d_inner_dia_mm"] = inner_dia_mm
        obj["j3d_circ_mm"] = circ_mm
        obj["j3d_profile"] = self.profile_type
        obj["j3d_orientation"] = self.orientation
        obj["j3d_width_mm"] = self.width_mm
        obj["j3d_height_mm"] = self.height_mm
        obj["j3d_radial_segments"] = self.radial_segments
        obj["j3d_profile_segments"] = self.profile_segments
        obj["j3d_crease"] = self.crease_value

        if self.use_subsurf:
            subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            subsurf.levels = self.subsurf_levels
            subsurf.render_levels = max(self.subsurf_levels, 2)

        self.report(
            {'INFO'},
            f"Ring Shank {system} {size_key} | {self.profile_type} | "
            f"Inner Dia {inner_dia_mm:.2f}mm (Circ {circ_mm:.1f}mm) | {self.orientation}"
        )
        return {'FINISHED'}
