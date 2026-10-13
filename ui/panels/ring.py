"""
Jeweler 3D Studio - UI Ring Panels Module
Panels for Ring Size references and parametric Metal Shank / Profiles.
"""

import bpy
from bpy.types import Panel, Context
from ...core.ring import (
    US_SIZE_ITEMS,
    UK_SIZE_ITEMS,
    EU_SIZE_ITEMS,
    JP_SIZE_ITEMS,
    RING_SYSTEM_ITEMS,
    GEOMETRY_TYPE_ITEMS,
    RING_PROFILE_ITEMS,
    ORIENTATION_ITEMS,
    get_ring_diameter,
    get_ring_circumference,
)


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
        j3d = context.scene.j3d
        col = layout.column(align=True)

        system = j3d.ring_system
        col.prop(j3d, "ring_system", text="System")

        if system == "US":
            col.prop(j3d, "us_size", text="Size")
            active_size = j3d.us_size
        elif system == "UK":
            col.prop(j3d, "uk_size", text="Size")
            active_size = j3d.uk_size
        elif system == "EU":
            col.prop(j3d, "eu_size", text="Size")
            active_size = j3d.eu_size
        elif system == "JP":
            col.prop(j3d, "jp_size", text="Size")
            active_size = j3d.jp_size
        else:
            col.prop(j3d, "us_size", text="Size")
            active_size = j3d.us_size

        dia_mm = get_ring_diameter(system, active_size)
        circ_mm = get_ring_circumference(dia_mm)
        box_info = col.box()
        box_row = box_info.row()
        box_row.label(text=f"Ø {dia_mm:.2f} mm | Circ: {circ_mm:.1f} mm", icon='INFO')

        row = col.row(align=True)
        row.prop(j3d, "geometry_type", expand=True)

        col.prop(j3d, "ring_orientation", text="Orientation")

        col.separator()
        op = col.operator("j3d_community.create_ring_size", icon='CURVE_NCIRCLE', text="Create Ring Size")
        op.ring_system = system
        op.ring_size = active_size
        op.us_size = j3d.us_size
        op.geometry_type = j3d.geometry_type
        op.orientation = j3d.ring_orientation


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
        j3d = context.scene.j3d
        col = layout.column(align=True)

        system = j3d.ring_system
        if system == "US":
            active_size = j3d.us_size
        elif system == "UK":
            active_size = j3d.uk_size
        elif system == "EU":
            active_size = j3d.eu_size
        elif system == "JP":
            active_size = j3d.jp_size
        else:
            active_size = j3d.us_size

        col.prop(j3d, "ring_profile", text="Profile")
        col.prop(j3d, "ring_orientation", text="Orientation")
        col.prop(j3d, "ring_width", text="Width (mm)")
        col.prop(j3d, "ring_height", text="Thickness (mm)")

        col.separator()
        row_res = col.row(align=True)
        row_res.prop(j3d, "ring_radial_segments", text="Radial Segments")
        row_res.prop(j3d, "ring_profile_segments", text="Profile Resolution")

        col.separator()
        box_sub = col.box()
        box_col = box_sub.column(align=True)
        box_col.prop(j3d, "ring_use_subsurf", text="Subdivision Surface")
        if j3d.ring_use_subsurf:
            row_sub = box_col.row(align=True)
            row_sub.prop(j3d, "ring_subsurf_levels", text="Levels")
            row_sub.prop(j3d, "ring_crease", text="Crease")

        col.separator()
        op = col.operator("j3d_community.create_ring_profile", icon='MESH_CYLINDER', text="Create Ring Shank")
        op.ring_system = system
        op.ring_size = active_size
        op.us_size = j3d.us_size
        op.profile_type = j3d.ring_profile
        op.orientation = j3d.ring_orientation
        op.width_mm = j3d.ring_width
        op.height_mm = j3d.ring_height
        op.radial_segments = j3d.ring_radial_segments
        op.profile_segments = j3d.ring_profile_segments
        op.use_subsurf = j3d.ring_use_subsurf
        op.subsurf_levels = j3d.ring_subsurf_levels
        op.crease_value = j3d.ring_crease


classes = (
    VIEW3D_PT_j3d_community_ring_size,
    VIEW3D_PT_j3d_community_sub_size,
    VIEW3D_PT_j3d_community_sub_profile,
)
