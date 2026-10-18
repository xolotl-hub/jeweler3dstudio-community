"""
Jeweler 3D Studio - UI Stubs Panels Module
Placeholder panels for upcoming modules: Settings (Prongs/Bezel/Pavé), Baskets, and Metrics/Quoting.
"""

from bpy.types import Panel, Context


# ===================================================================
# PANEL: Settings (Prongs & Bezel)
# ===================================================================

class VIEW3D_PT_j3d_community_settings(Panel):
    bl_label = "Settings (Prongs & Bezel)"
    bl_idname = "VIEW3D_PT_j3d_community_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"

    def draw(self, context: Context) -> None:
        pass


class VIEW3D_PT_j3d_community_sub_bezel(Panel):
    bl_label = "Bezel"
    bl_idname = "VIEW3D_PT_j3d_community_sub_bezel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"
    bl_parent_id = "VIEW3D_PT_j3d_community_settings"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        col = self.layout.column(align=True)
        col.label(text="Bezel Setting (PRO)", icon='INFO')


class VIEW3D_PT_j3d_community_sub_pave(Panel):
    bl_label = "Pavé"
    bl_idname = "VIEW3D_PT_j3d_community_sub_pave"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"
    bl_parent_id = "VIEW3D_PT_j3d_community_settings"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        col = self.layout.column(align=True)
        col.label(text="Pavé Distribution (PRO)", icon='INFO')



# PANEL: Metrics & Quoting
# ===================================================================

class VIEW3D_PT_j3d_community_metrics(Panel):
    bl_label = "Metrics & Costs"
    bl_idname = "VIEW3D_PT_j3d_community_metrics"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"

    def draw(self, context: Context) -> None:
        pass


class VIEW3D_PT_j3d_community_sub_weights(Panel):
    bl_label = "Weights & Metals"
    bl_idname = "VIEW3D_PT_j3d_community_sub_weights"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"
    bl_parent_id = "VIEW3D_PT_j3d_community_metrics"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        col = self.layout.column(align=True)
        col.label(text="Metal Weight Calculator (PRO)", icon='INFO')


class VIEW3D_PT_j3d_community_sub_quotation(Panel):
    bl_label = "Quoting & Technical Sheet"
    bl_idname = "VIEW3D_PT_j3d_community_sub_quotation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"
    bl_parent_id = "VIEW3D_PT_j3d_community_metrics"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        col = self.layout.column(align=True)
        col.label(text="Quotation Generator (PRO)", icon='INFO')


classes = (
    VIEW3D_PT_j3d_community_settings,
    VIEW3D_PT_j3d_community_sub_bezel,
    VIEW3D_PT_j3d_community_sub_pave,
    VIEW3D_PT_j3d_community_metrics,
    VIEW3D_PT_j3d_community_sub_weights,
    VIEW3D_PT_j3d_community_sub_quotation,
)
