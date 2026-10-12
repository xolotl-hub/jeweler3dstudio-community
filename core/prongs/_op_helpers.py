"""
Jeweler 3D Studio - Prongs Operator Shared Helpers
Mesh application, property persistence, and redo UI layout.
"""

try:
    import bpy
    from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
    from mathutils import Vector
except ImportError:
    pass

from ._presets import TIP_TYPE_ITEMS
from ._single import generate_prongs_bmesh

_MAX_PRONG_SETS = 2


def get_prong_children(gem_obj):
    """Devuelve lista de hijos PRONGS ordenados por j3d_prong_slot (ascendente)."""
    children = [ch for ch in gem_obj.children if ch.get("j3d_type") == "PRONGS"]
    children.sort(key=lambda o: int(o.get("j3d_prong_slot", 0)))
    return children


def build_and_apply_mesh(prongs_obj, bm, mesh_name):
    """Reemplaza la malla de prongs_obj con el BMesh dado."""
    old_mesh = prongs_obj.data
    new_mesh = bpy.data.meshes.new(mesh_name)
    bm.to_mesh(new_mesh)
    bm.free()
    prongs_obj.data = new_mesh
    bpy.data.meshes.remove(old_mesh)
    for poly in new_mesh.polygons:
        poly.use_smooth = True
    return new_mesh


def ensure_subsurf(prongs_obj, level):
    subsurf = next((m for m in prongs_obj.modifiers if m.type == "SUBSURF"), None)
    if subsurf is None:
        subsurf = prongs_obj.modifiers.new(name="Subdivision", type="SUBSURF")
    subsurf.levels = level
    subsurf.render_levels = level


def build_prongs_bm(op, gem):
    """Genera el BMesh de garras con los parámetros actuales del operador."""
    cut = gem.get("j3d_gem_cut", "ROUND")
    dim = gem.dimensions.copy()
    if max(dim.x, dim.y) < 0.05:
        dim = Vector((1.0, 1.0, 0.6))
    return generate_prongs_bmesh(
        gem_dim=dim, cut_name=cut, number=op.number,
        diameter=op.diameter, z_top=op.z_top, z_bottom=op.z_bottom,
        tip_type=op.tip_type, bump_scale=op.bump_scale,
        v_size=op.v_size, v_wall=op.v_wall, v_depth=op.v_depth,
        claw_tip_dia=op.claw_tip_dia, claw_offset=op.claw_offset,
        taper=op.taper, position_deg=op.position_deg,
        girdle_offset=op.girdle_offset, inward_deg=op.inward_deg,
        use_symmetry=op.use_symmetry, detalization=op.detalization,
        crease_val=op.crease_val,
    )


SAVED_PROPS = (
    "number", "tip_type", "diameter", "z_top", "z_bottom",
    "position_deg", "girdle_offset", "inward_deg", "taper", "bump_scale",
    "claw_tip_dia", "claw_offset", "v_size", "v_wall", "v_depth",
    "detalization", "subsurf_level", "crease_val", "use_symmetry",
)


def load_props_from(op, source_obj):
    """Restaura SAVED_PROPS desde las propiedades guardadas en source_obj."""
    restored = False
    for k in SAVED_PROPS:
        saved_key = f"j3d_p_{k}"
        if saved_key in source_obj:
            try:
                setattr(op, k, source_obj[saved_key])
                restored = True
            except Exception:
                pass
    return restored


def save_props_to(op, prongs_obj):
    """Persiste SAVED_PROPS del operador en las propiedades del objeto."""
    for k in SAVED_PROPS:
        prongs_obj[f"j3d_p_{k}"] = getattr(op, k)


PRONG_PROPS = dict(
    number       = IntProperty(name="Prong Count",       default=4,    min=1,    max=16),
    tip_type     = EnumProperty(name="Tip Style",        items=TIP_TYPE_ITEMS, default="DOME"),
    diameter     = FloatProperty(name="Diameter (mm)",   default=0.50, min=0.1,  max=3.0,  step=5,  precision=2),
    z_top        = FloatProperty(name="Height Above (mm)", default=0.35, min=0.05, max=5.0, step=5, precision=2),
    z_bottom     = FloatProperty(name="Height Below (mm)", default=1.00, min=0.2, max=15.0, step=10, precision=2),
    position_deg = FloatProperty(name="Angle Offset",    default=45.0, min=-180.0, max=180.0, step=50, precision=1),
    girdle_offset= FloatProperty(name="Girdle Offset (mm)",
                    description="Radial distance from gem girdle",
                    default=0.0, min=-3.0, max=5.0, step=1, precision=2),
    inward_deg   = FloatProperty(name="Inward Tilt",     default=3.0,  min=-30.0, max=45.0, step=10, precision=1),
    taper        = FloatProperty(name="Taper Factor",    default=0.0,  min=0.0,  max=1.0,  step=5,  precision=2),
    bump_scale   = FloatProperty(name="Dome Rounding",   default=1.00, min=0.0,  max=1.5,  step=10, precision=2),
    claw_tip_dia = FloatProperty(name="Tip Diameter (mm)", default=0.15, min=0.0, max=2.0, step=1, precision=2),
    claw_offset  = FloatProperty(name="Tip Offset (mm)",  default=0.15, min=-1.0, max=2.0, step=1, precision=2),
    v_size       = FloatProperty(name="V Size (mm)",     default=0.27, min=0.05, max=3.0, step=2, precision=2),
    v_wall       = FloatProperty(name="V Wall (mm)",     default=0.20, min=0.02, max=1.0, step=1, precision=2),
    v_depth      = FloatProperty(name="V Depth (mm)",    default=0.15, min=0.0,  max=2.0, step=1, precision=2),
    detalization = IntProperty(name="Resolution",        default=16, min=6, max=48),
    subsurf_level= IntProperty(name="Subsurface Level",  default=2, min=0, max=6),
    crease_val   = FloatProperty(name="Crease",          default=0.85, min=0.0, max=1.0, step=5, precision=2),
    use_symmetry = BoolProperty(name="Use Symmetry",     default=False),
)


def draw_prong_params(op, layout):
    """Panel de Redo común a add y readjust."""
    col = layout.column()
    col.prop(op, "number")
    col.prop(op, "position_deg")
    col.prop(op, "use_symmetry")
    col.separator()
    col.prop(op, "tip_type")
    if op.tip_type == "DOME":
        box = col.box(); box.label(text="Round Shape", icon='MESH_UVSPHERE')
        box.prop(op, "diameter"); box.prop(op, "bump_scale")
    elif op.tip_type == "FLAT":
        box = col.box(); box.label(text="Flat Shape", icon='MESH_CYLINDER')
        box.prop(op, "diameter")
    elif op.tip_type == "CLAW":
        box = col.box(); box.label(text="Claw Shape", icon='CONE')
        box.prop(op, "diameter"); box.prop(op, "claw_tip_dia"); box.prop(op, "claw_offset")
    elif op.tip_type == "V_PRONG":
        box = col.box(); box.label(text="V-Prong Shape", icon='MOD_MIRROR')
        box.prop(op, "v_size"); box.prop(op, "v_wall"); box.prop(op, "v_depth")
    col.separator()
    col.prop(op, "z_top"); col.prop(op, "z_bottom"); col.prop(op, "taper")
    col.separator()
    col.prop(op, "girdle_offset"); col.prop(op, "inward_deg"); col.prop(op, "detalization")
    col.separator()
    col.prop(op, "subsurf_level"); col.prop(op, "crease_val")
