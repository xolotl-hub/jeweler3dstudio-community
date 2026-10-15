"""
Jeweler 3D Studio - Cutters Operators
Operadores interactivos para anadir, reajustar y gestionar cortadores booleanos
en gemas individuales o selecciones multiples.
"""

import bpy
from mathutils import Matrix
from bpy.props import IntProperty, FloatProperty
from bpy.types import Operator
from .units import mm_to_bu
from .cutters_outlines import (
    CUTTER_TOP_RATIO, CUTTER_TABLE_RATIO, CUTTER_GIRDLE_TOP_RATIO,
    CUTTER_GIRDLE_BOT_RATIO, CUTTER_SEAT_RATIO, CUTTER_DEPTH_RATIO,
    CUTTER_R_TABLE, CUTTER_R_GIRDLE, CUTTER_R_HOLE,
)


def _sync_cutter_props_from_op(ctr_obj: bpy.types.Object, op) -> None:
    """Sincroniza propiedades de objeto del cortador desde las propiedades del operador."""
    ctr_obj.j3d_cutter_segments = op.segments
    ctr_obj.j3d_cutter_crease = op.crease
    ctr_obj.j3d_cutter_r_top = op.r_top
    ctr_obj.j3d_cutter_z_top = op.z_top
    ctr_obj.j3d_cutter_r_table = op.r_table
    ctr_obj.j3d_cutter_z_table = op.z_table
    ctr_obj.j3d_cutter_r_girdle_top = op.r_girdle_top
    ctr_obj.j3d_cutter_z_girdle_top = op.z_girdle_top
    ctr_obj.j3d_cutter_r_girdle_bot = op.r_girdle_bot
    ctr_obj.j3d_cutter_z_girdle_bot = op.z_girdle_bot
    ctr_obj.j3d_cutter_r_seat = op.r_seat
    ctr_obj.j3d_cutter_z_seat = op.z_seat
    ctr_obj.j3d_cutter_r_hole_bot = op.r_hole_bot
    ctr_obj.j3d_cutter_z_hole_bot = op.z_hole_bot


def _process_gem_cutter(gem_obj: bpy.types.Object, op, base_levels: list, ref_size: float, context) -> None:
    """Genera o actualiza el cortador booleano parametrico para una gema individual."""
    from .cutters import (
        build_cutter_bmesh_from_levels,
        create_cutter_mesh,
        find_cutter_for_gem,
        find_prongs_for_gem,
        apply_seat_cutter_boolean_to_prongs,
    )
    if gem_obj.get("j3d_type") != "GEM":
        gem_obj["j3d_type"] = "GEM"
    cut_key = gem_obj.get("j3d_gem_cut", "ROUND")
    size_mm = float(gem_obj.get("j3d_gem_size", 0.0))
    if size_mm < 0.01:
        size_mm = max(gem_obj.dimensions.x, gem_obj.dimensions.y)
    size_mm = max(size_mm, 0.5)
    ctr_name = "CTR_" + gem_obj.name

    scale = 1.0 if abs(size_mm - ref_size) < 1e-4 else (size_mm / ref_size)
    levels = base_levels if scale == 1.0 else [(r * scale, z * scale) for r, z in base_levels]

    existing = find_cutter_for_gem(gem_obj)
    if existing:
        bm = build_cutter_bmesh_from_levels(cut_key, op.segments, op.crease, levels, context)
        bm.to_mesh(existing.data)
        bm.free()
        existing.data.update()
        if existing.parent != gem_obj:
            existing.parent = gem_obj
            existing.matrix_parent_inverse = Matrix.Identity(4)
            existing.location = existing.rotation_euler = (0.0, 0.0, 0.0)
            existing.scale = (1.0, 1.0, 1.0)
        _sync_cutter_props_from_op(existing, op)
        ctr_target = existing
    else:
        orphan = bpy.data.objects.get(ctr_name)
        if orphan and orphan.parent != gem_obj:
            bpy.data.objects.remove(orphan, do_unlink=True)
        mesh = create_cutter_mesh(cut_key, ctr_name + "_Mesh", size_mm, op.segments, op.crease, levels, context)
        ctr_obj = bpy.data.objects.new(ctr_name, mesh)
        col = gem_obj.users_collection[0] if gem_obj.users_collection else context.scene.collection
        col.objects.link(ctr_obj)
        ctr_obj.parent = gem_obj
        ctr_obj.matrix_parent_inverse = Matrix.Identity(4)
        ctr_obj.location = ctr_obj.rotation_euler = (0.0, 0.0, 0.0)
        ctr_obj.scale = (1.0, 1.0, 1.0)
        ctr_obj.display_type, ctr_obj.show_in_front = 'WIRE', True
        ctr_obj["j3d_type"], ctr_obj["j3d_cutter_for"] = "CUTTER", gem_obj.name
        ctr_obj["j3d_gem_cut"], ctr_obj["j3d_gem_size"] = cut_key, size_mm
        _sync_cutter_props_from_op(ctr_obj, op)
        gem_obj["j3d_has_cutter"] = ctr_name
        ctr_target = ctr_obj

    prongs = find_prongs_for_gem(gem_obj)
    if prongs:
        apply_seat_cutter_boolean_to_prongs(prongs, ctr_target)


class J3DComm_OT_add_cutter_to_gem(Operator):
    """Add procedural boolean seat cutter to selected gemstone(s)"""
    bl_idname = "j3d_community.add_cutter_to_gem"
    bl_label = "Add Cutter to Gem"
    bl_description = "Generates a 5-zone procedural seat cutter for selected gemstone(s)."
    bl_options = {'REGISTER', 'UNDO'}

    segments: IntProperty(name="Segments", default=16, min=4, max=64)  # type: ignore
    crease: FloatProperty(name="Crease", default=0.90, min=0.0, max=1.0, precision=2)  # type: ignore

    r_top: FloatProperty(name="Top Radius", default=0.350, min=0.001, precision=3)  # type: ignore
    z_top: FloatProperty(name="Top Z", default=1.250, precision=3)  # type: ignore
    r_table: FloatProperty(name="Table Radius", default=0.350, min=0.001, precision=3)  # type: ignore
    z_table: FloatProperty(name="Table Z", default=0.220, precision=3)  # type: ignore
    r_girdle_top: FloatProperty(name="Upper Girdle Radius", default=0.580, min=0.001, precision=3)  # type: ignore
    z_girdle_top: FloatProperty(name="Upper Girdle Z", default=0.060, precision=3)  # type: ignore
    r_girdle_bot: FloatProperty(name="Lower Girdle Radius", default=0.580, min=0.001, precision=3)  # type: ignore
    z_girdle_bot: FloatProperty(name="Lower Girdle Z", default=-0.030, precision=3)  # type: ignore
    r_seat: FloatProperty(name="Seat Radius", default=0.317, min=0.001, precision=3)  # type: ignore
    z_seat: FloatProperty(name="Seat Z", default=-0.266, precision=3)  # type: ignore
    r_hole_bot: FloatProperty(name="Hole Radius", default=0.317, min=0.001, precision=3)  # type: ignore
    z_hole_bot: FloatProperty(name="Hole Z", default=-2.200, precision=3)  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT' and (
            any(o.get("j3d_type") == "GEM" or "gem" in o.name.lower() for o in context.selected_objects)
            or (context.active_object and (context.active_object.get("j3d_type") == "GEM" or "gem" in context.active_object.name.lower()))
        )

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set:
        active_gem = next((o for o in context.selected_objects if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()), context.active_object)
        if active_gem:
            size_mm = float(active_gem.get("j3d_gem_size", 0.0))
            if size_mm < 0.01:
                size_mm = max(active_gem.dimensions.x, active_gem.dimensions.y)
            size_mm = max(size_mm, 0.5)
            r_half = size_mm * 0.5
            self.r_top = self.r_table = r_half * CUTTER_R_TABLE
            self.z_top = size_mm * CUTTER_TOP_RATIO
            self.z_table = size_mm * CUTTER_TABLE_RATIO
            self.r_girdle_top = self.r_girdle_bot = r_half * CUTTER_R_GIRDLE
            self.z_girdle_top = size_mm * CUTTER_GIRDLE_TOP_RATIO
            self.z_girdle_bot = size_mm * CUTTER_GIRDLE_BOT_RATIO
            self.r_seat = self.r_hole_bot = r_half * CUTTER_R_HOLE
            self.z_seat = size_mm * CUTTER_SEAT_RATIO
            self.z_hole_bot = -size_mm * CUTTER_DEPTH_RATIO
            j3d = getattr(context.scene, "j3d", None)
            self.segments = int(getattr(j3d, "cutter_segments", getattr(context.scene, "j3d_cutter_segments", 16)))
            self.crease = float(getattr(j3d, "cutter_crease", getattr(context.scene, "j3d_cutter_crease", 0.90)))
        return self.execute(context)

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "segments", text="Segments", icon='MESH_CIRCLE')
        col.prop(self, "crease", text="Crease", icon='EDGESEL')
        layout.separator()
        box = layout.box()
        box.label(text="Cutter Profile (Radius & Z):", icon='DRIVER_DISTANCE')
        rings_info = [
            ("1. Top", "r_top", "z_top"), ("2. Table", "r_table", "z_table"),
            ("3. Upper Girdle", "r_girdle_top", "z_girdle_top"), ("4. Lower Girdle", "r_girdle_bot", "z_girdle_bot"),
            ("5. Seat", "r_seat", "z_seat"), ("6. Hole Bottom", "r_hole_bot", "z_hole_bot"),
        ]
        for label, r_prop, z_prop in rings_info:
            row = box.row(align=True)
            row.label(text=label)
            row.prop(self, r_prop, text="R")
            row.prop(self, z_prop, text="Z")

    def execute(self, context: bpy.types.Context) -> set:
        context.view_layer.update()
        gems = [o for o in context.selected_objects if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()]
        if not gems and context.active_object and (context.active_object.get("j3d_type") == "GEM" or "gem" in context.active_object.name.lower()):
            gems = [context.active_object]
        if not gems:
            self.report({'WARNING'}, "Select at least one gemstone first.")
            return {'CANCELLED'}

        base_levels = [
            (self.r_top, self.z_top), (self.r_table, self.z_table),
            (self.r_girdle_top, self.z_girdle_top), (self.r_girdle_bot, self.z_girdle_bot),
            (self.r_seat, self.z_seat), (self.r_hole_bot, self.z_hole_bot),
        ]
        active_gem = next((o for o in context.selected_objects if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()), context.active_object)
        ref_size = float(active_gem.get("j3d_gem_size", 0.0)) if active_gem else 0.0
        if ref_size < 0.01 and active_gem:
            ref_size = max(active_gem.dimensions.x, active_gem.dimensions.y)
        ref_size = max(ref_size, 0.5)

        for gem in gems:
            _process_gem_cutter(gem, self, base_levels, ref_size, context)

        self.report({'INFO'}, f"{len(gems)} cutter(s) processed.")
        context.view_layer.update()
        return {'FINISHED'}


class J3DComm_OT_reset_cutter_defaults(Operator):
    """Reset cutter rings of active cutter to standard proportions"""
    bl_idname = "j3d_community.reset_cutter_defaults"
    bl_label = "Reset Cutter Defaults"
    bl_description = "Restores cutter dimensions to standard gemstone proportions"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        from .cutters import find_cutter_for_gem
        obj = context.active_object
        return bool(obj and (obj.get("j3d_type") == "CUTTER" or find_cutter_for_gem(obj)))

    def execute(self, context: bpy.types.Context) -> set:
        from .cutters import find_cutter_for_gem, init_cutter_object_props, rebuild_cutter_from_object_props
        obj = context.active_object
        ctr_obj = obj if obj.get("j3d_type") == "CUTTER" else find_cutter_for_gem(obj)
        if not ctr_obj:
            self.report({'WARNING'}, "No active cutter found.")
            return {'CANCELLED'}
        cut_key = ctr_obj.get("j3d_gem_cut", "ROUND")
        size_mm = float(ctr_obj.get("j3d_gem_size", 1.0))
        segs = int(getattr(ctr_obj, "j3d_cutter_segments", 8))
        crease = float(getattr(ctr_obj, "j3d_cutter_crease", 0.8))
        init_cutter_object_props(ctr_obj, cut_key, size_mm, segments=segs, crease=crease)
        rebuild_cutter_from_object_props(ctr_obj, context)
        self.report({'INFO'}, f"Cutter {ctr_obj.name} reset to defaults.")
        return {'FINISHED'}


class J3DComm_OT_add_cutters(Operator):
    """Add Base Cutter"""
    bl_idname = "j3d_community.add_cutters"
    bl_label = "Add Cutter"
    bl_description = "Adds a boolean cutter; uses selected gems as reference if present"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT'

    def execute(self, context: bpy.types.Context) -> set:
        from .cutters import init_cutter_object_props
        if any(o.get("j3d_type") == "GEM" for o in context.selected_objects):
            return bpy.ops.j3d_community.add_cutter_to_gem()
        size_bu = mm_to_bu(3.0, context)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=size_bu * 0.5, depth=size_bu * 0.7, location=context.scene.cursor.location,
        )
        obj = context.active_object
        obj.name = "CTR_Base"
        obj.display_type = 'WIRE'
        init_cutter_object_props(obj, "ROUND", 3.0, 8, 0.8)
        self.report({'INFO'}, "Base cutter added.")
        return {'FINISHED'}
