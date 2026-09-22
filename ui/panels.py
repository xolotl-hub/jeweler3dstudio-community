"""
Jeweler 3D Studio - UI Panels Module
Clean panel and subpanel architecture for Viewport N-Panel ('Jeweler 3D' tab).
All subpanels default to closed ('DEFAULT_CLOSED') to keep UI clean, except Gem Visor.
Scale standard: 1 BU = 1 mm direct jewelry modeling.
"""

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, BoolProperty
from bpy.types import Panel, Context
from ..core.ring import US_SIZE_ITEMS, GEOMETRY_TYPE_ITEMS, RING_PROFILE_ITEMS, ORIENTATION_ITEMS
from ..core.gems import (
    get_cut_enum_items,
    STONE_ITEMS,
    get_gem_size_preset_items,
    get_effective_gem_size,
    calculate_carats,
    get_cut_preview_collection,
    get_scene_gem_inventory,
    _get_live_size_mm,
)


# ===================================================================
# 1. PANEL 1: Ring & Size
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


# ===================================================================
# 2. PANEL 2: Gems
# ===================================================================

class VIEW3D_PT_j3d_community_gems(Panel):
    bl_label = "Gems"
    bl_idname = "VIEW3D_PT_j3d_community_gems"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"

    def draw(self, context: Context) -> None:
        pass


class VIEW3D_PT_j3d_community_sub_gem_visor(Panel):
    bl_label = "Add Gem"
    bl_idname = "VIEW3D_PT_j3d_community_sub_gem_visor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"
    bl_parent_id = "VIEW3D_PT_j3d_community_gems"

    def draw(self, context: Context) -> None:
        layout = self.layout
        scene = context.scene
        col = layout.column(align=True)

        col.prop(scene, "j3d_community_gem_cut", text="Cut")

        pcoll = get_cut_preview_collection()
        if pcoll and scene.j3d_community_gem_cut in pcoll:
            preview = col.box()
            row = preview.row(align=True)
            row.alignment = 'EXPAND'
            row.scale_y = 0.75
            row.template_icon(icon_value=pcoll[scene.j3d_community_gem_cut].icon_id, scale=10)

        col.separator()
        col.prop(scene, "j3d_community_gem_stone", text="Stone")
        col.prop(scene, "j3d_community_gem_size_preset", text="Size / ct")

        if scene.j3d_community_gem_size_preset == "CUSTOM":
            col.prop(scene, "j3d_community_gem_size", text="Size (mm)")
            effective_size = scene.j3d_community_gem_size
        else:
            effective_size = get_effective_gem_size(scene)

        # Dynamic carat estimator
        carats = calculate_carats(scene.j3d_community_gem_stone, scene.j3d_community_gem_cut, effective_size)
        box = col.box()
        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=f"Size: {effective_size:.2f} mm  |  Weight: {carats:.3f} ct", icon='INFO')

        col.separator()
        op = col.operator("j3d_community.add_gem", icon='MESH_ICOSPHERE', text="Add 3D Gem")

        # --- Studio PRO Promo Box (Community Edition) ---
        box = layout.box()
        col = box.column(align=True)
        col.label(text="💎 Unlock Jeweler 3D Studio PRO", icon="SOLO_ON")
        col.label(text="• 17 Luxury Faceted Cuts (GIA/ISO)", icon="DOT")
        col.label(text="• 8 Metal Shank Profiles + Edge Crease", icon="DOT")
        col.label(text="• 5-Zone Calibrated Boolean Cutters", icon="DOT")
        col.label(text="• Live Gem Map & Interactive Inventory", icon="DOT")
        col.label(text="• Shift+A Add Menu & Redo Panel (F9)", icon="DOT")
        col.separator()
        col.operator("wm.url_open", text="Get Studio PRO on Blender Market", icon="URL").url = "https://blendermarket.com"

        op.cut = scene.j3d_community_gem_cut
        op.stone = scene.j3d_community_gem_stone
        op.size = effective_size


# --- Subpanels (Gem Map, Gem Swap) and Panels 3-6 omitted in Community Edition ---

# ===================================================================
# REGISTRO DE CLASES
# ===================================================================

classes = (
    VIEW3D_PT_j3d_community_ring_size,
    VIEW3D_PT_j3d_community_sub_size,
    VIEW3D_PT_j3d_community_sub_profile,
    VIEW3D_PT_j3d_community_gems,
    VIEW3D_PT_j3d_community_sub_gem_visor,
)


def register():
    bpy.types.Scene.j3d_community_us_size = EnumProperty(
        name="US Ring Size",
        description="Standard US ring size selection (includes half sizes)",
        items=US_SIZE_ITEMS,
        default="7.0"
    ) # type: ignore

    bpy.types.Scene.j3d_community_geometry_type = EnumProperty(
        name="Geometry Type",
        description="Output geometry format for ring sizing",
        items=GEOMETRY_TYPE_ITEMS,
        default="CURVE"
    ) # type: ignore

    bpy.types.Scene.j3d_community_ring_orientation = EnumProperty(
        name="Orientation",
        description="Orientation plane for ring creation",
        items=ORIENTATION_ITEMS,
        default="FRONT"
    ) # type: ignore

    bpy.types.Scene.j3d_community_ring_profile = EnumProperty(
        name="Profile",
        description="Ring shank cross-section profile",
        items=RING_PROFILE_ITEMS,
        default="MEDIA_CANA"
    ) # type: ignore

    bpy.types.Scene.j3d_community_ring_width = FloatProperty(
        name="Width",
        description="Ring band width in mm",
        default=3.0,
        min=1.0,
        max=20.0,
        step=10,
        precision=2
    ) # type: ignore

    bpy.types.Scene.j3d_community_ring_height = FloatProperty(
        name="Thickness",
        description="Ring band thickness in mm (grows outwards from inner diameter)",
        default=1.5,
        min=0.3,
        max=10.0,
        step=10,
        precision=2
    ) # type: ignore

    bpy.types.Scene.j3d_community_ring_radial_segments = IntProperty(
        name="Radial Segments",
        description="Number of circumferential divisions along the ring",
        default=16,
        min=8,
        max=256
    ) # type: ignore

    bpy.types.Scene.j3d_community_ring_profile_segments = IntProperty(
        name="Profile Resolution",
        description="Number of subdivisions for curved profile sections",
        default=2,
        min=2,
        max=64
    ) # type: ignore

    bpy.types.Scene.j3d_community_ring_use_subsurf = BoolProperty(
        name="Subdivision Surface",
        description="Add Subdivision Surface modifier",
        default=True
    ) # type: ignore

    bpy.types.Scene.j3d_community_ring_subsurf_levels = IntProperty(
        name="Subsurf Level",
        description="Subdivision level for viewport and render",
        default=2,
        min=1,
        max=5
    ) # type: ignore

    bpy.types.Scene.j3d_community_ring_crease = FloatProperty(
        name="Edge Crease",
        description="Crease factor (Shift+E) on sharp corners (0.8 = natural polished edge)",
        default=0.8,
        min=0.0,
        max=1.0,
        step=5,
        precision=2
    ) # type: ignore

    bpy.types.Scene.j3d_community_gem_cut = EnumProperty(
        name="Cut",
        description="Gemstone cut selection",
        items=get_cut_enum_items
    ) # type: ignore

    bpy.types.Scene.j3d_community_gem_stone = EnumProperty(
        name="Stone",
        description="Gemstone material type",
        items=STONE_ITEMS,
        default="DIAMOND"
    ) # type: ignore

    bpy.types.Scene.j3d_community_gem_size_preset = EnumProperty(
        name="Commercial Size",
        description="Standard commercial market sizes for selected cut",
        items=get_gem_size_preset_items,
        default=0
    ) # type: ignore

    bpy.types.Scene.j3d_community_gem_size = FloatProperty(
        name="Size",
        description="Gemstone size in millimeters (custom mode)",
        default=1.0,
        min=0.5,
        max=50.0,
        step=10,
        precision=2
    ) # type: ignore

    bpy.types.Scene.j3d_community_swap_cut = EnumProperty(
        name="New Cut",
        description="Cut selection for gem replacement",
        items=get_cut_enum_items
    ) # type: ignore

    bpy.types.Scene.j3d_community_swap_stone = EnumProperty(
        name="New Stone",
        description="Gemstone material type for replacement",
        items=STONE_ITEMS,
        default="DIAMOND"
    ) # type: ignore

    bpy.types.Scene.j3d_community_swap_size = FloatProperty(
        name="New Size",
        description="New size in millimeters for replacement",
        default=3.0,
        min=0.5,
        max=50.0,
        step=10,
        precision=2
    ) # type: ignore

    bpy.types.Scene.j3d_community_cutter_segments = IntProperty(
        name="Cutter Segments",
        description="Radial segments for seat cutter (default 8)",
        default=8,
        min=4,
        max=64
    ) # type: ignore

    bpy.types.Scene.j3d_community_cutter_crease = FloatProperty(
        name="Cutter Crease",
        description="Edge crease (Shift+E) for Subdivision Surface",
        default=0.8,
        min=0.0,
        max=1.0,
        step=10,
        precision=2
    ) # type: ignore

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

    for prop in (
        "j3d_community_us_size", "j3d_community_geometry_type", "j3d_community_ring_orientation",
        "j3d_community_ring_profile", "j3d_community_ring_width", "j3d_community_ring_height",
        "j3d_community_ring_radial_segments", "j3d_community_ring_profile_segments",
        "j3d_community_ring_use_subsurf", "j3d_community_ring_subsurf_levels", "j3d_community_ring_crease",
        "j3d_community_gem_cut", "j3d_community_gem_stone", "j3d_community_gem_size_preset", "j3d_community_gem_size",
        "j3d_community_swap_cut", "j3d_community_swap_stone", "j3d_community_swap_size",
        "j3d_community_cutter_segments", "j3d_community_cutter_crease"
    ):
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
            except Exception:
                pass
