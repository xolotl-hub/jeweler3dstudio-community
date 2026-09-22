"""
Jeweler 3D Studio - UI Gems Panels Module
Panel for Gemstone creation and cut previews.
"""

import bpy
from bpy.props import EnumProperty, FloatProperty
from bpy.types import Panel, Context
from ...core.gems import (
    get_cut_enum_items,
    STONE_ITEMS,
    get_gem_size_preset_items,
    get_effective_gem_size,
    calculate_carats,
    get_cut_preview_collection,
)


# ===================================================================
# PANEL: Gems (Main Header & Add Gem Subpanel)
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

        carats = calculate_carats(scene.j3d_community_gem_stone, scene.j3d_community_gem_cut, effective_size)
        box = col.box()
        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=f"Size: {effective_size:.2f} mm  |  Weight: {carats:.3f} ct", icon='INFO')

        col.separator()
        op = col.operator("j3d_community.add_gem", icon='MESH_ICOSPHERE', text="Add 3D Gem")
        op.cut = scene.j3d_community_gem_cut
        op.stone = scene.j3d_community_gem_stone
        op.size = effective_size


classes = (
    VIEW3D_PT_j3d_community_gems,
    VIEW3D_PT_j3d_community_sub_gem_visor,
)

PROPERTIES = (
    "j3d_community_gem_cut",
    "j3d_community_gem_stone",
    "j3d_community_gem_size_preset",
    "j3d_community_gem_size",
)


def register_properties():
    bpy.types.Scene.j3d_community_gem_cut = EnumProperty(
        name="Cut",
        description="Gemstone cut selection",
        items=get_cut_enum_items
    )  # type: ignore

    bpy.types.Scene.j3d_community_gem_stone = EnumProperty(
        name="Stone",
        description="Gemstone material type",
        items=STONE_ITEMS,
        default="DIAMOND"
    )  # type: ignore

    bpy.types.Scene.j3d_community_gem_size_preset = EnumProperty(
        name="Commercial Size",
        description="Standard commercial market sizes for selected cut",
        items=get_gem_size_preset_items,
        default=0
    )  # type: ignore

    bpy.types.Scene.j3d_community_gem_size = FloatProperty(
        name="Size",
        description="Gemstone size in millimeters (custom mode)",
        default=1.0,
        min=0.5,
        max=50.0,
        step=10,
        precision=2
    )  # type: ignore


def unregister_properties():
    for prop in PROPERTIES:
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
            except Exception:
                pass
