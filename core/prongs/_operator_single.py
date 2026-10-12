"""
Jeweler 3D Studio - Single Gem Prongs Operator
Blender Operators: J3DComm_OT_add_prongs (always creates new set, max 2 per gem)
                   J3DComm_OT_readjust_prongs (reajusta el set de prongs seleccionado)
"""

try:
    import bpy
    from bpy.types import Context, Operator
    from mathutils import Matrix, Vector
except ImportError:
    Operator = object  # type: ignore
    Context = object   # type: ignore

from ._presets import get_default_prong_presets
from ._op_helpers import (
    _MAX_PRONG_SETS,
    PRONG_PROPS,
    SAVED_PROPS,
    build_and_apply_mesh,
    build_prongs_bm,
    draw_prong_params,
    ensure_subsurf,
    get_prong_children,
    load_props_from,
    save_props_to,
)


class J3DComm_OT_add_prongs(Operator):
    """Crea un nuevo set de garras como hijo de la gema seleccionada (máx 2 por gema)"""
    bl_idname  = "j3d_community.add_prongs"
    bl_label   = "Add Prongs"
    bl_description = "Generates a new prong set as child of active gemstone (max 2 per gem)"
    bl_options = {'REGISTER', 'UNDO'}

    number:       PRONG_PROPS["number"]        # type: ignore
    tip_type:     PRONG_PROPS["tip_type"]      # type: ignore
    diameter:     PRONG_PROPS["diameter"]      # type: ignore
    z_top:        PRONG_PROPS["z_top"]         # type: ignore
    z_bottom:     PRONG_PROPS["z_bottom"]      # type: ignore
    position_deg: PRONG_PROPS["position_deg"]  # type: ignore
    girdle_offset:PRONG_PROPS["girdle_offset"] # type: ignore
    inward_deg:   PRONG_PROPS["inward_deg"]    # type: ignore
    taper:        PRONG_PROPS["taper"]         # type: ignore
    bump_scale:   PRONG_PROPS["bump_scale"]    # type: ignore
    claw_tip_dia: PRONG_PROPS["claw_tip_dia"]  # type: ignore
    claw_offset:  PRONG_PROPS["claw_offset"]   # type: ignore
    v_size:       PRONG_PROPS["v_size"]        # type: ignore
    v_wall:       PRONG_PROPS["v_wall"]        # type: ignore
    v_depth:      PRONG_PROPS["v_depth"]       # type: ignore
    detalization: PRONG_PROPS["detalization"]  # type: ignore
    subsurf_level:PRONG_PROPS["subsurf_level"] # type: ignore
    crease_val:   PRONG_PROPS["crease_val"]    # type: ignore
    use_symmetry: PRONG_PROPS["use_symmetry"]  # type: ignore

    _SAVED_PROPS = SAVED_PROPS

    def draw(self, context: Context) -> None:
        draw_prong_params(self, self.layout)

    @classmethod
    def poll(cls, context: Context) -> bool:
        if context.mode != 'OBJECT':
            return False
        return any(
            o.get("j3d_type") == "GEM" or "gem" in o.name.lower()
            for o in context.selected_objects
        )

    def invoke(self, context: Context, event) -> set:
        gem = context.active_object
        if gem and gem.get("j3d_type") == "PRONGS" and gem.parent:
            gem = gem.parent
        sets = get_prong_children(gem) if gem else []
        if sets:
            load_props_from(self, sets[-1])
        else:
            if gem:
                cut = gem.get("j3d_gem_cut", "ROUND")
                dim = gem.dimensions.copy() if gem else Vector((1.0, 1.0, 0.6))
                for k, v in get_default_prong_presets(dim, cut).items():
                    if hasattr(self, k):
                        setattr(self, k, v)
        return self.execute(context)

    def execute(self, context: Context) -> set:
        gems = [o for o in context.selected_objects
                if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()]
        if not gems:
            active = context.active_object
            if active and active.get("j3d_type") not in ("PRONGS", "CUTTER", "V_CUTTER"):
                gems = [active]
        if not gems:
            self.report({'ERROR'}, "No active gemstone selected.")
            return {'CANCELLED'}

        created = 0
        last_prongs = None

        for gem in gems:
            if gem.get("j3d_type") == "PRONGS":
                gem = gem.parent or gem

            bm = build_prongs_bm(self, gem)

            existing_sets = get_prong_children(gem)
            if len(existing_sets) >= _MAX_PRONG_SETS:
                oldest = existing_sets[0]
                old_mesh = oldest.data
                bpy.data.objects.remove(oldest)
                bpy.data.meshes.remove(old_mesh)
                existing_sets = get_prong_children(gem)

            used_slots = {int(o.get("j3d_prong_slot", 0)) for o in existing_sets}
            slot = next((s for s in range(_MAX_PRONG_SETS) if s not in used_slots), 0)

            obj_name  = f"Prongs_{gem.name}_S{slot}"
            mesh_data = bpy.data.meshes.new(f"{obj_name}_Mesh")
            bm.to_mesh(mesh_data)
            bm.free()

            prongs_obj = bpy.data.objects.new(obj_name, mesh_data)
            target_col = (gem.users_collection[0] if gem.users_collection
                          else context.scene.collection)
            target_col.objects.link(prongs_obj)
            prongs_obj.parent                = gem
            prongs_obj.matrix_parent_inverse = Matrix.Identity(4)
            prongs_obj.location              = (0.0, 0.0, 0.0)
            prongs_obj["j3d_type"]           = "PRONGS"
            prongs_obj["j3d_gem_target"]     = gem.name
            prongs_obj["j3d_prong_slot"]     = slot

            for poly in mesh_data.polygons:
                poly.use_smooth = True

            ensure_subsurf(prongs_obj, self.subsurf_level)

            try:
                from ..cutters import find_cutter_for_gem, apply_seat_cutter_boolean_to_prongs
                ctr_obj = find_cutter_for_gem(gem)
                if ctr_obj:
                    apply_seat_cutter_boolean_to_prongs(prongs_obj, ctr_obj)
            except Exception:
                pass

            save_props_to(self, prongs_obj)
            last_prongs = prongs_obj
            created += 1

        if last_prongs:
            bpy.ops.object.select_all(action='DESELECT')
            last_prongs.select_set(True)
            context.view_layer.objects.active = last_prongs

        self.report({'INFO'}, f"Garras '{self.tip_type}' ({self.number}x) añadidas a {created} gema(s).")
        return {'FINISHED'}


class J3DComm_OT_readjust_prongs(Operator):
    """Reajusta el set de garras seleccionado conservando sus parámetros guardados"""
    bl_idname  = "j3d_community.readjust_prongs"
    bl_label   = "Readjust Prongs"
    bl_description = "Regenerates this prong set in-place with current/modified parameters"
    bl_options = {'REGISTER', 'UNDO'}

    number:       PRONG_PROPS["number"]        # type: ignore
    tip_type:     PRONG_PROPS["tip_type"]      # type: ignore
    diameter:     PRONG_PROPS["diameter"]      # type: ignore
    z_top:        PRONG_PROPS["z_top"]         # type: ignore
    z_bottom:     PRONG_PROPS["z_bottom"]      # type: ignore
    position_deg: PRONG_PROPS["position_deg"]  # type: ignore
    girdle_offset:PRONG_PROPS["girdle_offset"] # type: ignore
    inward_deg:   PRONG_PROPS["inward_deg"]    # type: ignore
    taper:        PRONG_PROPS["taper"]         # type: ignore
    bump_scale:   PRONG_PROPS["bump_scale"]    # type: ignore
    claw_tip_dia: PRONG_PROPS["claw_tip_dia"]  # type: ignore
    claw_offset:  PRONG_PROPS["claw_offset"]   # type: ignore
    v_size:       PRONG_PROPS["v_size"]        # type: ignore
    v_wall:       PRONG_PROPS["v_wall"]        # type: ignore
    v_depth:      PRONG_PROPS["v_depth"]       # type: ignore
    detalization: PRONG_PROPS["detalization"]  # type: ignore
    subsurf_level:PRONG_PROPS["subsurf_level"] # type: ignore
    crease_val:   PRONG_PROPS["crease_val"]    # type: ignore
    use_symmetry: PRONG_PROPS["use_symmetry"]  # type: ignore

    _SAVED_PROPS = SAVED_PROPS

    def draw(self, context: Context) -> None:
        draw_prong_params(self, self.layout)

    @classmethod
    def poll(cls, context: Context) -> bool:
        if context.mode != 'OBJECT':
            return False
        obj = context.active_object
        return bool(obj and obj.get("j3d_type") == "PRONGS" and obj.parent)

    def invoke(self, context: Context, event) -> set:
        prongs_obj = context.active_object
        load_props_from(self, prongs_obj)
        return self.execute(context)

    def execute(self, context: Context) -> set:
        prongs_obj = context.active_object
        if not prongs_obj or prongs_obj.get("j3d_type") != "PRONGS" or not prongs_obj.parent:
            self.report({'ERROR'}, "Select a Prongs object to readjust.")
            return {'CANCELLED'}

        gem = prongs_obj.parent
        bm  = build_prongs_bm(self, gem)
        build_and_apply_mesh(prongs_obj, bm, prongs_obj.data.name)
        ensure_subsurf(prongs_obj, self.subsurf_level)
        save_props_to(self, prongs_obj)

        self.report({'INFO'}, f"Garras '{self.tip_type}' ({self.number}x) reajustadas.")
        return {'FINISHED'}


classes = (
    J3DComm_OT_add_prongs,
    J3DComm_OT_readjust_prongs,
)


def register() -> None:
    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
