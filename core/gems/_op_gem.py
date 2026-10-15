"""
Jeweler 3D Studio - Gems: Add & Swap Gemstone Operators

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


class J3DComm_OT_swap_gems(Operator):
    """Swap cut, stone, or size of selected gemstone(s)"""
    bl_idname = "j3d_community.swap_gems"
    bl_label = "Swap Gems"
    bl_description = (
        "Changes cut, stone, and/or size of selected gem(s). "
        "If attached cutter exists, regenerates it automatically."
    )
    bl_options = {'REGISTER', 'UNDO'}

    new_cut: EnumProperty(name="New Cut", items=get_cut_enum_items)  # type: ignore
    new_stone: EnumProperty(name="New Stone", items=STONE_ITEMS, default="DIAMOND")  # type: ignore
    new_size: FloatProperty(name="New Size (mm)", default=3.0, min=0.5, max=50.0, step=10, precision=2)  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return (
            context.mode == 'OBJECT'
            and any(obj.get("j3d_type") == "GEM" for obj in context.selected_objects)
        )

    def invoke(self, context: bpy.types.Context, event) -> set:
        scene = context.scene
        j3d = getattr(scene, "j3d", None)
        if j3d and hasattr(j3d, "swap_cut"):
            self.new_cut = j3d.swap_cut
        elif hasattr(scene, "j3d_swap_cut"):
            self.new_cut = scene.j3d_swap_cut

        if j3d and hasattr(j3d, "swap_stone"):
            self.new_stone = j3d.swap_stone
        elif hasattr(scene, "j3d_swap_stone"):
            self.new_stone = scene.j3d_swap_stone

        if j3d and hasattr(j3d, "swap_size"):
            self.new_size = j3d.swap_size
        elif hasattr(scene, "j3d_swap_size"):
            self.new_size = scene.j3d_swap_size

        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set:
        scene = context.scene
        j3d = getattr(scene, "j3d", None)
        if not self.properties.is_property_set("new_cut"):
            if j3d and hasattr(j3d, "swap_cut"):
                self.new_cut = j3d.swap_cut
            elif hasattr(scene, "j3d_swap_cut"):
                self.new_cut = scene.j3d_swap_cut

        if not self.properties.is_property_set("new_stone"):
            if j3d and hasattr(j3d, "swap_stone"):
                self.new_stone = j3d.swap_stone
            elif hasattr(scene, "j3d_swap_stone"):
                self.new_stone = scene.j3d_swap_stone

        if not self.properties.is_property_set("new_size"):
            if j3d and hasattr(j3d, "swap_size"):
                self.new_size = j3d.swap_size
            elif hasattr(scene, "j3d_swap_size"):
                self.new_size = scene.j3d_swap_size

        from ..cutters import rebuild_cutter_for_gem, find_cutter_for_gem

        gems = [o for o in context.selected_objects if o.get("j3d_type") == "GEM"]
        if not gems:
            self.report({'WARNING'}, "Select at least one gemstone first.")
            return {'CANCELLED'}

        swapped = 0
        for gem_obj in gems:
            new_mesh = create_gem_mesh(
                cut_key=self.new_cut,
                name=f"Gem_{self.new_cut.title()}_{self.new_size:.1f}mm_Mesh",
                size_mm=self.new_size,
                context=context,
            )
            old_mesh = gem_obj.data
            gem_obj.data = new_mesh
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)

            new_mat = get_or_create_gem_material(self.new_stone)
            if not gem_obj.data.materials:
                gem_obj.data.materials.append(new_mat)
            else:
                gem_obj.data.materials[0] = new_mat

            ct = calculate_carats(self.new_stone, self.new_cut, self.new_size)
            gem_obj["j3d_gem_cut"]   = self.new_cut
            gem_obj["j3d_gem_stone"] = self.new_stone
            gem_obj["j3d_gem_size"]  = self.new_size
            gem_obj["j3d_carat"]     = ct

            cutter_obj = find_cutter_for_gem(gem_obj)
            if cutter_obj is not None:
                rebuild_cutter_for_gem(cutter_obj, self.new_cut, self.new_size, context)

            swapped += 1

        self.report(
            {'INFO'},
            f"{swapped} gem(s) -> {self.new_cut.title()} {self.new_size:.1f}mm {self.new_stone.title()}"
        )
        return {'FINISHED'}
