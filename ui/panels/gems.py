"""
Jeweler 3D Studio - UI Gems Panels Module
Panel for Gemstone creation and cut previews.
"""

import bpy
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
        j3d = context.scene.j3d
        col = layout.column(align=True)

        col.prop(j3d, "gem_cut", text="Cut")

        pcoll = get_cut_preview_collection()
        if pcoll and j3d.gem_cut in pcoll:
            preview = col.box()
            row = preview.row(align=True)
            row.alignment = 'EXPAND'
            row.scale_y = 0.75
            row.template_icon(icon_value=pcoll[j3d.gem_cut].icon_id, scale=10)

        col.separator()
        col.prop(j3d, "gem_stone", text="Stone")
        col.prop(j3d, "gem_size_preset", text="Size / ct")

        if j3d.gem_size_preset == "CUSTOM":
            col.prop(j3d, "gem_size", text="Size (mm)")
            effective_size = j3d.gem_size
        else:
            effective_size = get_effective_gem_size(context.scene)

        carats = calculate_carats(j3d.gem_stone, j3d.gem_cut, effective_size)
        box = col.box()
        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=f"Size: {effective_size:.2f} mm  |  Weight: {carats:.3f} ct", icon='INFO')

        col.separator()
        op = col.operator("j3d_community.add_gem", icon='MESH_ICOSPHERE', text="Add 3D Gem")
        op.cut = j3d.gem_cut
        op.stone = j3d.gem_stone
        op.size = effective_size


classes = (
    VIEW3D_PT_j3d_community_gems,
    VIEW3D_PT_j3d_community_sub_gem_visor,
)
