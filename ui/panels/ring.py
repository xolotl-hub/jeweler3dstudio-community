"""
Jeweler 3D Studio - UI Ring Panels Module
Panels for Ring Size references and parametric Metal Shank / Profiles.
"""

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, BoolProperty
from bpy.types import Panel, Context
from ...core.ring import US_SIZE_ITEMS, GEOMETRY_TYPE_ITEMS, RING_PROFILE_ITEMS, ORIENTATION_ITEMS


# ===================================================================
# PANEL: Ring & Size
# ===================================================================

class VIEW3D_PT_j3d_community_ring_size(Panel):
    bl_label = "Ring & Size"
    bl_idname = "VIEW3D_PT_j3d_community_ring_size"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"

    def draw(self, context: Context) -> None:
        pass


class VIEW3D_PT_j3d_community_sub_size(Panel):
    bl_label = "Size Reference"
    bl_idname = "VIEW3D_PT_j3d_community_sub_size"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"
    bl_parent_id = "VIEW3D_PT_j3d_community_ring_size"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        layout = self.layout
        scene = context.scene
        col = layout.column(align=True)

        col.prop(scene, "j3d_community_us_size", text="US Size")

        row = col.row(align=True)
        row.prop(scene, "j3d_community_geometry_type", expand=True)

        col.prop(scene, "j3d_community_ring_orientation", text="Orientation")

        col.separator()
        op = col.operator("j3d_community.create_ring_size", icon='CURVE_NCIRCLE', text="Create Ring Size")
        op.us_size = scene.j3d_community_us_size
        op.geometry_type = scene.j3d_community_geometry_type
        op.orientation = scene.j3d_community_ring_orientation


class VIEW3D_PT_j3d_community_sub_profile(Panel):
    bl_label = "Metal Profile / Shank"
    bl_idname = "VIEW3D_PT_j3d_community_sub_profile"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"
    bl_parent_id = "VIEW3D_PT_j3d_community_ring_size"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        layout = self.layout
        scene = context.scene
        col = layout.column(align=True)

        col.prop(scene, "j3d_community_ring_profile", text="Profile")
        col.prop(scene, "j3d_community_ring_orientation", text="Orientation")
        col.prop(scene, "j3d_community_ring_width", text="Width (mm)")
        col.prop(scene, "j3d_community_ring_height", text="Thickness (mm)")

        col.separator()
        row_res = col.row(align=True)
        row_res.prop(scene, "j3d_community_ring_radial_segments", text="Radial Segments")
        row_res.prop(scene, "j3d_community_ring_profile_segments", text="Profile Resolution")

        col.separator()
        box_sub = col.box()
        box_col = box_sub.column(align=True)
        box_col.prop(scene, "j3d_community_ring_use_subsurf", text="Subdivision Surface")
        if scene.j3d_community_ring_use_subsurf:
            row_sub = box_col.row(align=True)
            row_sub.prop(scene, "j3d_community_ring_subsurf_levels", text="Levels")
            row_sub.prop(scene, "j3d_community_ring_crease", text="Crease")

        col.separator()
        op = col.operator("j3d_community.create_ring_profile", icon='MESH_CYLINDER', text="Create Ring Shank")
        op.us_size = scene.j3d_community_us_size
        op.profile_type = scene.j3d_community_ring_profile
        op.orientation = scene.j3d_community_ring_orientation
        op.width_mm = scene.j3d_community_ring_width
        op.height_mm = scene.j3d_community_ring_height
        op.radial_segments = scene.j3d_community_ring_radial_segments
        op.profile_segments = scene.j3d_community_ring_profile_segments
        op.use_subsurf = scene.j3d_community_ring_use_subsurf
        op.subsurf_levels = scene.j3d_community_ring_subsurf_levels
        op.crease_value = scene.j3d_community_ring_crease


classes = (
    VIEW3D_PT_j3d_community_ring_size,
    VIEW3D_PT_j3d_community_sub_size,
    VIEW3D_PT_j3d_community_sub_profile,
)

PROPERTIES = (
    "j3d_community_us_size",
    "j3d_community_geometry_type",
    "j3d_community_ring_orientation",
    "j3d_community_ring_profile",
    "j3d_community_ring_width",
    "j3d_community_ring_height",
    "j3d_community_ring_radial_segments",
    "j3d_community_ring_profile_segments",
    "j3d_community_ring_use_subsurf",
    "j3d_community_ring_subsurf_levels",
    "j3d_community_ring_crease",
)


def register_properties():
    bpy.types.Scene.j3d_community_us_size = EnumProperty(
        name="US Ring Size",
        description="Standard US ring size selection (includes half sizes)",
        items=US_SIZE_ITEMS,
        default="7.0"
    )  # type: ignore

    bpy.types.Scene.j3d_community_geometry_type = EnumProperty(
        name="Geometry Type",
        description="Output geometry format for ring sizing",
        items=GEOMETRY_TYPE_ITEMS,
        default="CURVE"
    )  # type: ignore

    bpy.types.Scene.j3d_community_ring_orientation = EnumProperty(
        name="Orientation",
        description="Orientation plane for ring creation",
        items=ORIENTATION_ITEMS,
        default="FRONT"
    )  # type: ignore

    bpy.types.Scene.j3d_community_ring_profile = EnumProperty(
        name="Profile",
        description="Ring shank cross-section profile",
        items=RING_PROFILE_ITEMS,
        default="MEDIA_CANA"
    )  # type: ignore

    bpy.types.Scene.j3d_community_ring_width = FloatProperty(
        name="Width",
        description="Ring band width in mm",
        default=3.0,
        min=1.0,
        max=20.0,
        step=10,
        precision=2
    )  # type: ignore

    bpy.types.Scene.j3d_community_ring_height = FloatProperty(
        name="Thickness",
        description="Ring band thickness in mm (grows outwards from inner diameter)",
        default=1.5,
        min=0.3,
        max=10.0,
        step=10,
        precision=2
    )  # type: ignore

    bpy.types.Scene.j3d_community_ring_radial_segments = IntProperty(
        name="Radial Segments",
        description="Number of circumferential divisions along the ring",
        default=16,
        min=8,
        max=256
    )  # type: ignore

    bpy.types.Scene.j3d_community_ring_profile_segments = IntProperty(
        name="Profile Resolution",
        description="Number of subdivisions for curved profile sections",
        default=2,
        min=2,
        max=64
    )  # type: ignore

    bpy.types.Scene.j3d_community_ring_use_subsurf = BoolProperty(
        name="Subdivision Surface",
        description="Add Subdivision Surface modifier",
        default=True
    )  # type: ignore

    bpy.types.Scene.j3d_community_ring_subsurf_levels = IntProperty(
        name="Subsurf Level",
        description="Subdivision level for viewport and render",
        default=2,
        min=1,
        max=5
    )  # type: ignore

    bpy.types.Scene.j3d_community_ring_crease = FloatProperty(
        name="Edge Crease",
        description="Crease factor (Shift+E) on sharp corners (0.8 = natural polished edge)",
        default=0.8,
        min=0.0,
        max=1.0,
        step=5,
        precision=2
    )  # type: ignore


def unregister_properties():
    for prop in PROPERTIES:
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
            except Exception:
                pass
