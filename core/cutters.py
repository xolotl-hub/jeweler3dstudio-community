"""
Jeweler 3D Community - Core Cutters Module
Procedural gem seat cutters with 5-zone calibrated profile and live parametric editing.
"""

_needs_reload = "bpy" in locals()

import bpy
import bmesh
from .units import mm_to_bu
from . import cutters_outlines, cutters_props, cutters_ops

if _needs_reload:
    import importlib
    cutters_outlines = importlib.reload(cutters_outlines)
    cutters_props = importlib.reload(cutters_props)
    cutters_ops = importlib.reload(cutters_ops)

from .cutters_outlines import (
    CUTTER_TOP_RATIO, CUTTER_TABLE_RATIO, CUTTER_GIRDLE_TOP_RATIO,
    CUTTER_GIRDLE_BOT_RATIO, CUTTER_SEAT_RATIO, CUTTER_DEPTH_RATIO,
    CUTTER_R_TABLE, CUTTER_R_GIRDLE, CUTTER_R_HOLE, get_cut_outline,
)
from .cutters_ops import (
    J3DComm_OT_add_cutter_to_gem,
)
from .cutters_props import (
    OBJECT_CUTTER_PROPS, register_cutter_properties, unregister_cutter_properties,
)

classes = (J3DComm_OT_add_cutter_to_gem,)



# -- Constructor de BMesh para Cortadores -----------------------------------------

def build_cutter_bmesh_from_levels(
    cut_key: str,
    segments: int,
    crease: float,
    levels_mm: list,
    context=None,
) -> bmesh.types.BMesh:
    """Build a BMesh with six rings from [(r_mm, z_mm), ...], including caps and crease."""
    segments = max(4, int(segments))
    bu = mm_to_bu(1.0, context)
    outline = get_cut_outline(cut_key, segments)
    n = len(outline)
    bm = bmesh.new()
    rings = []

    for r_mm, z_mm in levels_mm:
        ring = []
        r_bu = max(0.001, float(r_mm)) * bu
        z_bu = float(z_mm) * bu
        for ox, oy in outline:
            ring.append(bm.verts.new((ox * r_bu, oy * r_bu, z_bu)))
        rings.append(ring)

    bm.verts.ensure_lookup_table()
    for ri in range(len(rings) - 1):
        ra, rb = rings[ri], rings[ri + 1]
        for i in range(n):
            ni = (i + 1) % n
            try:
                bm.faces.new([ra[i], ra[ni], rb[ni], rb[i]])
            except Exception:
                pass

    top_z = float(levels_mm[0][1]) * bu
    top_c = bm.verts.new((0.0, 0.0, top_z))
    for i in range(n):
        ni = (i + 1) % n
        try:
            bm.faces.new([top_c, rings[0][ni], rings[0][i]])
        except Exception:
            pass

    bot_z = float(levels_mm[-1][1]) * bu
    bot_c = bm.verts.new((0.0, 0.0, bot_z))
    for i in range(n):
        ni = (i + 1) % n
        try:
            bm.faces.new([bot_c, rings[-1][i], rings[-1][ni]])
        except Exception:
            pass

    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    if crease > 0.0:
        crease_layer = bm.edges.layers.float.get("crease_edge") or bm.edges.layers.float.new("crease_edge")
        for ring in rings:
            for i in range(n):
                edge = bm.edges.get((ring[i], ring[(i + 1) % n]))
                if edge is not None:
                    edge[crease_layer] = float(crease)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def create_cutter_mesh(
    cut_key: str = "ROUND",
    name: str = "Cutter_Mesh",
    size_mm: float = 1.0,
    segments: int = 8,
    crease: float = 0.8,
    custom_levels: list = None,
    context=None,
) -> bpy.types.Mesh:
    """Generate a five-zone boolean cutter mesh."""
    if custom_levels is None:
        r_half = size_mm * 0.5
        levels_mm = [
            (r_half * CUTTER_R_TABLE,  +size_mm * CUTTER_TOP_RATIO),
            (r_half * CUTTER_R_TABLE,  +size_mm * CUTTER_TABLE_RATIO),
            (r_half * CUTTER_R_GIRDLE, +size_mm * CUTTER_GIRDLE_TOP_RATIO),
            (r_half * CUTTER_R_GIRDLE, +size_mm * CUTTER_GIRDLE_BOT_RATIO),
            (r_half * CUTTER_R_HOLE,   +size_mm * CUTTER_SEAT_RATIO),
            (r_half * CUTTER_R_HOLE,   -size_mm * CUTTER_DEPTH_RATIO),
        ]
    else:
        levels_mm = custom_levels

    bm = build_cutter_bmesh_from_levels(cut_key, segments, crease, levels_mm, context)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


# -- Inicializacion y Actualizacion en Vivo (Thread-Safe por Objeto) --------------
_UPDATING_OBJECTS = set()


def update_cutter_object_props_callback(self, context):
    """Callback invoked when the user changes a UI slider."""
    name = getattr(self, "name", "")
    if name in _UPDATING_OBJECTS:
        return
    if self.get("j3d_type") != "CUTTER" or not getattr(self, "data", None):
        return
    rebuild_cutter_from_object_props(self, context)


def init_cutter_object_props(ctr_obj: bpy.types.Object, cut_key: str, size_mm: float, segments: int = 16, crease: float = 0.9):
    """Initialize cutter object properties from the gem size and cut type."""
    name = ctr_obj.name
    _UPDATING_OBJECTS.add(name)
    try:
        r_half = size_mm * 0.5
        ctr_obj["j3d_type"], ctr_obj["j3d_gem_cut"], ctr_obj["j3d_gem_size"] = "CUTTER", cut_key, size_mm
        ctr_obj.j3d_cutter_segments = max(4, int(segments))
        ctr_obj.j3d_cutter_crease = max(0.0, min(1.0, float(crease)))
        ctr_obj.j3d_cutter_r_top = ctr_obj.j3d_cutter_r_table = r_half * CUTTER_R_TABLE
        ctr_obj.j3d_cutter_z_top = size_mm * CUTTER_TOP_RATIO
        ctr_obj.j3d_cutter_z_table = size_mm * CUTTER_TABLE_RATIO
        ctr_obj.j3d_cutter_r_girdle_top = ctr_obj.j3d_cutter_r_girdle_bot = r_half * CUTTER_R_GIRDLE
        ctr_obj.j3d_cutter_z_girdle_top = size_mm * CUTTER_GIRDLE_TOP_RATIO
        ctr_obj.j3d_cutter_z_girdle_bot = size_mm * CUTTER_GIRDLE_BOT_RATIO
        ctr_obj.j3d_cutter_r_seat = ctr_obj.j3d_cutter_r_hole_bot = r_half * CUTTER_R_HOLE
        ctr_obj.j3d_cutter_z_seat = size_mm * CUTTER_SEAT_RATIO
        ctr_obj.j3d_cutter_z_hole_bot = -size_mm * CUTTER_DEPTH_RATIO

    finally:
        _UPDATING_OBJECTS.discard(name)


def rebuild_cutter_from_object_props(ctr_obj: bpy.types.Object, context=None):
    """Rebuild the cutter mesh in place from its object properties."""
    cut_key = ctr_obj.get("j3d_gem_cut", "ROUND")
    segments = int(getattr(ctr_obj, "j3d_cutter_segments", 8))
    crease = float(getattr(ctr_obj, "j3d_cutter_crease", 0.8))
    levels_mm = [
        (float(getattr(ctr_obj, "j3d_cutter_r_top", 1.588)), float(getattr(ctr_obj, "j3d_cutter_z_top", 2.880))),
        (float(getattr(ctr_obj, "j3d_cutter_r_table", 1.588)), float(getattr(ctr_obj, "j3d_cutter_z_table", 1.050))),
        (float(getattr(ctr_obj, "j3d_cutter_r_girdle_top", 2.610)), float(getattr(ctr_obj, "j3d_cutter_z_girdle_top", 0.240))),
        (float(getattr(ctr_obj, "j3d_cutter_r_girdle_bot", 2.610)), float(getattr(ctr_obj, "j3d_cutter_z_girdle_bot", -0.130))),
        (float(getattr(ctr_obj, "j3d_cutter_r_seat", 1.220)), float(getattr(ctr_obj, "j3d_cutter_z_seat", -1.330))),
        (float(getattr(ctr_obj, "j3d_cutter_r_hole_bot", 1.220)), float(getattr(ctr_obj, "j3d_cutter_z_hole_bot", -5.050))),
    ]
    bm = build_cutter_bmesh_from_levels(cut_key, segments, crease, levels_mm, context)
    mesh = ctr_obj.data
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -- Utilidades de asociacion Gema <-> Cortador -----------------------------------

def find_cutter_for_gem(gem_obj: bpy.types.Object):
    """Find the cutter associated with a specific gem."""
    if not gem_obj:
        return None
    for ch in gem_obj.children:
        if ch.get("j3d_type") == "CUTTER" or ch.name.startswith("CTR_"):
            return ch
    cutter_name = gem_obj.get("j3d_has_cutter", "")
    if cutter_name and cutter_name in bpy.data.objects:
        obj = bpy.data.objects[cutter_name]
        if obj.parent == gem_obj or obj.get("j3d_cutter_for") == gem_obj.name:
            return obj
    return None


def find_prongs_for_gem(gem_obj: bpy.types.Object):
    """Find the prongs object associated with a gem."""
    if not gem_obj:
        return None
    for ch in gem_obj.children:
        if ch.get("j3d_type") == "PRONGS":
            return ch
    for ob in bpy.data.objects:
        if ob.get("j3d_type") == "PRONGS" and ob.get("j3d_gem_target") == gem_obj.name:
            return ob
    return None


def apply_seat_cutter_boolean_to_prongs(prongs_obj: bpy.types.Object, cutter_obj: bpy.types.Object) -> None:
    """Add a Boolean modifier to prongs for the cut seat (MANIFOLD with EXACT fallback)."""
    if not prongs_obj or not cutter_obj:
        return
    if not any(m.type == 'BOOLEAN' and m.object == cutter_obj for m in prongs_obj.modifiers):
        mod = prongs_obj.modifiers.new(name=f"SeatCut_{cutter_obj.name}", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter_obj
        solvers = [e.identifier for e in mod.bl_rna.properties['solver'].enum_items]
        mod.solver = 'MANIFOLD' if 'MANIFOLD' in solvers else 'EXACT'
        mod.show_viewport = False
        mod.show_render = True


def rebuild_cutter_for_gem(cutter_obj: bpy.types.Object, cut_key: str, size_mm: float, context=None):
    """Rebuild a cutter mesh when its gem changes, preserving segments and crease."""
    segs = int(getattr(cutter_obj, "j3d_cutter_segments", 8))
    crease = float(getattr(cutter_obj, "j3d_cutter_crease", 0.8))
    init_cutter_object_props(cutter_obj, cut_key, size_mm, segments=segs, crease=crease)
    rebuild_cutter_from_object_props(cutter_obj, context)


def register():
    register_cutter_properties(update_cutter_object_props_callback, classes)


def unregister():
    unregister_cutter_properties(classes)
