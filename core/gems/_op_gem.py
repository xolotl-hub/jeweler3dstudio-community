"""
Jeweler 3D Community - Gems: Add & Swap Gemstone Operators

Operators for generating new 3D faceted gemstones and swapping existing ones in-place.
"""

import bpy
from bpy.props import EnumProperty, FloatProperty
from bpy.types import Operator
from ._constants import STONE_ITEMS
from ._sizes import get_effective_gem_size
from ._previews import get_cut_enum_items
from ._geometry import create_gem_mesh, calculate_carats, get_or_create_gem_material


class J3DComm_OT_add_gem(Operator):
    """Add 3D Faceted Gemstone"""
    bl_idname = "j3d_community.add_gem"
    bl_label = "Add 3D Gem"
    bl_description = "Adds a 3D faceted gemstone at the 3D cursor position"
    bl_options = {'REGISTER', 'UNDO'}

    cut: EnumProperty(name="Cut", items=get_cut_enum_items)
    stone: EnumProperty(name="Stone", items=STONE_ITEMS, default="DIAMOND")
    size: FloatProperty(name="Size (mm)", default=0.0, min=0.0, max=50.0, step=10, precision=2)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        scene = context.scene
        j3d = getattr(scene, "j3d", None)
        if self.cut:
            cut_key = self.cut
        elif j3d and hasattr(j3d, "gem_cut") and j3d.gem_cut:
            cut_key = j3d.gem_cut
        else:
            cut_key = getattr(scene, "j3d_gem_cut", "ROUND") or "ROUND"

        if self.stone:
            stone_key = self.stone
        elif j3d and hasattr(j3d, "gem_stone"):
            stone_key = j3d.gem_stone
        else:
            stone_key = getattr(scene, "j3d_gem_stone", "DIAMOND")

        if self.size > 0.0:
            size_mm = self.size
        else:
            size_mm = get_effective_gem_size(scene)

        mesh_data = create_gem_mesh(
            cut_key=cut_key,
            name=f"Gem_{cut_key.title()}_{size_mm:.1f}mm_Mesh",
            size_mm=size_mm,
            context=context
        )

        obj = bpy.data.objects.new(f"Gem_{stone_key.title()}_{cut_key.title()}_{size_mm:.1f}mm", mesh_data)
        context.collection.objects.link(obj)
        obj.location = context.scene.cursor.location

        obj["j3d_type"] = "GEM"
        obj["j3d_gem_cut"] = cut_key
        obj["j3d_gem_stone"] = stone_key
        obj["j3d_gem_size"] = size_mm

        ct = calculate_carats(stone_key, cut_key, size_mm)
        obj["j3d_carat"] = ct

        mat = get_or_create_gem_material(stone_key)
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

        for o in context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Gem {stone_key} {cut_key} ({size_mm:.1f} mm / {ct:.3f} ct) created successfully.")
        return {'FINISHED'}


