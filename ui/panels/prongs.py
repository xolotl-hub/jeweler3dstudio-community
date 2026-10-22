"""
Jeweler 3D Community - UI Prongs Panel Module
Interactive N-Panel controls for parametric BMesh prongs.
"""

import bpy
from bpy.types import Context, Panel


class VIEW3D_PT_j3d_community_sub_prongs(Panel):
    bl_label = "Prongs"
    bl_idname = "VIEW3D_PT_j3d_community_sub_prongs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"
    bl_parent_id = "VIEW3D_PT_j3d_community_settings"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        layout = self.layout
        obj = context.active_object
        selected_gems = [ob for ob in context.selected_objects if ob.get("j3d_type") == "GEM" or "gem" in ob.name.lower()]
        is_gem = obj and (obj.get("j3d_type") == "GEM" or "gem" in obj.name.lower())
        is_prongs = obj and obj.get("j3d_type") == "PRONGS"

        if is_prongs:
            box = layout.box()
            slot = int(obj.get("j3d_prong_slot", 0)) + 1
            box.label(text=f"Prongs: {obj.name} (Set {slot})", icon='MOD_SOLIDIFY')
            target = obj.get("j3d_gem_target", "")
            if target:
                box.label(text=f"Linked to: {target}", icon='LINKED')
            box.operator("j3d_community.readjust_prongs", text="Readjust Prongs", icon='FILE_REFRESH')
        elif is_gem or selected_gems:
            col = layout.column(align=True)
            col.operator("j3d_community.add_prongs", text="Add Prongs (New Set)", icon='ADD')
            if is_gem:
                prong_children = [ch for ch in obj.children if ch.get("j3d_type") == "PRONGS"]
                if prong_children:
                    prong_children.sort(key=lambda o: int(o.get("j3d_prong_slot", 0)))
                    box = layout.box()
                    box.label(text=f"Active sets ({len(prong_children)}/2):", icon='MESH_UVSPHERE')
                    for s in prong_children:
                        slot = int(s.get("j3d_prong_slot", 0)) + 1
                        tip = s.get("j3d_p_tip_type", "DOME")
                        row = box.row()
                        row.label(text=f"  Set {slot}: {s.name} ({tip})")
        else:
            col = layout.column(align=True)
            col.enabled = False
            col.operator("j3d_community.add_prongs", text="Add Prongs", icon='ADD')
            box = layout.box()
            box.label(text="Select a gem to enable", icon='INFO')

classes = (
    VIEW3D_PT_j3d_community_sub_prongs,
)


def register():
    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
