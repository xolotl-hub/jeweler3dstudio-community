"""
Jeweler 3D Studio - Gems: Map Calculation & Selection Operators

Operators for calculating scene gem inventory/carat total and batch selection in viewport.
"""

import bpy
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.types import Operator
from ._inventory import get_scene_gem_inventory, _get_live_size_mm


class J3DComm_OT_calculate_gem_map(Operator):
    """Calculate and review gemstone inventory in the scene"""
    bl_idname = "j3d_community.calculate_gem_map"
    bl_label = "Calculate / Review Gem Map"
    bl_description = "Scans the scene and analyzes gemstones, sizes, and total carat weight"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT'

    def execute(self, context: bpy.types.Context):
        inv = get_scene_gem_inventory(context)
        count = inv["total_count"]
        carats = inv["total_carats"]
        if count == 0:
            self.report({'INFO'}, "Gem Map: No gemstones detected in active scene.")
        else:
            n_groups = len(inv["records"])
            self.report(
                {'INFO'},
                f"Gem Map: {count} gems ({n_groups} distinct sizes) — {carats:.3f} ct total."
            )
        return {'FINISHED'}


class J3DComm_OT_select_gems(Operator):
    """Select gemstones in scene by batch or all"""
    bl_idname = "j3d_community.select_gems"
    bl_label = "Select Gems"
    bl_description = "Selects matching gemstones in 3D viewport or all gems"
    bl_options = {'REGISTER', 'UNDO'}

    cut: StringProperty(name="Cut", default="")  # type: ignore
    stone: StringProperty(name="Stone", default="")  # type: ignore
    size_mm: FloatProperty(name="Size (mm)", default=0.0, precision=2)  # type: ignore
    select_all: BoolProperty(name="Select All", default=False)  # type: ignore
    extend: BoolProperty(name="Extend Selection", default=False)  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT'

    def execute(self, context: bpy.types.Context):
        scene = context.scene
        if not self.extend:
            bpy.ops.object.select_all(action='DESELECT')

        matched = []
        for obj in scene.objects:
            if obj.get("j3d_type") == "GEM" or ("j3d_gem_cut" in obj and "j3d_gem_size" in obj):
                if self.select_all:
                    matched.append(obj)
                    continue

                obj_cut = str(obj.get("j3d_gem_cut", ""))
                obj_stone = str(obj.get("j3d_gem_stone", ""))
                obj_size = round(_get_live_size_mm(obj, context), 2)

                cut_match = (not self.cut) or (obj_cut.upper() == self.cut.upper())
                stone_match = (not self.stone) or (obj_stone.upper() == self.stone.upper())
                size_match = (self.size_mm <= 0.0) or (abs(obj_size - round(self.size_mm, 2)) < 0.05)

                if cut_match and stone_match and size_match:
                    matched.append(obj)

        if not matched:
            self.report({'INFO'}, "No matching gemstones found.")
            return {'CANCELLED'}

        for obj in matched:
            obj.select_set(True)

        if matched:
            context.view_layer.objects.active = matched[0]

        if self.select_all:
            self.report({'INFO'}, f"Selected {len(matched)} gemstones in scene.")
        else:
            self.report(
                {'INFO'},
                f"Selected {len(matched)} gems: {self.cut.title()} {self.stone.title()} {self.size_mm:.1f}mm"
            )
        return {'FINISHED'}
