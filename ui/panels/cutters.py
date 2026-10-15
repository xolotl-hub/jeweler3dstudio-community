"""
Jeweler 3D Studio - UI Cutters Panels Module (Community Edition)
Only the Seat & Hole Cutter subpanel is available.
"""

import bpy
from bpy.types import Panel, Context


class VIEW3D_PT_j3d_community_cutters(Panel):
    bl_label = "Cutters"
    bl_idname = "VIEW3D_PT_j3d_community_cutters"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Jeweler 3D Community'

    def draw(self, context: Context) -> None:
        pass


class VIEW3D_PT_j3d_community_sub_cutter_seat(Panel):
    bl_label = "Seat & Hole Cutter"
    bl_idname = "VIEW3D_PT_j3d_community_sub_cutter_seat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Jeweler 3D Community'
    bl_parent_id = "VIEW3D_PT_j3d_community_cutters"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        layout = self.layout
        col = layout.column(align=True)
        col.operator("j3d_community.add_cutter_to_gem", icon='ADD', text="Add Cutter to Gem")


classes = (
    VIEW3D_PT_j3d_community_cutters,
    VIEW3D_PT_j3d_community_sub_cutter_seat,
)
