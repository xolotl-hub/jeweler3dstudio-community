r"""
Jeweler 3D Studio - Prongs Tip & Loop Geometry Helpers
Pure BMesh helper functions for circular loops, creases, caps and tip styles.
"""

from math import cos, pi, sin, sqrt, tau
from typing import Optional

try:
    import bmesh
    from bmesh.types import BMesh, BMVert, BMEdge, BMFace
    from mathutils import Matrix, Vector
except ImportError:
    BMesh = BMVert = BMEdge = BMFace = object  # type: ignore
    Matrix = Vector = object  # type: ignore


# ---------------------------------------------------------------------------
# Low-level loop helpers
# ---------------------------------------------------------------------------

def _circle_verts(bm: BMesh, radius: float, z: float, detalization: int) -> list:
    """Creates a horizontal ring of vertices at height z."""
    angle_step = tau / detalization
    return [
        bm.verts.new((sin(i * angle_step) * radius, cos(i * angle_step) * radius, z))
        for i in range(detalization)
    ]


def _bridge_loops(bm: BMesh, loop_bottom: list, loop_top: list) -> list:
    """Connects two vertex loops with quad faces and returns created faces."""
    n = min(len(loop_bottom), len(loop_top))
    faces = []
    for i in range(n):
        next_i = (i + 1) % n
        faces.append(bm.faces.new((loop_bottom[i], loop_bottom[next_i], loop_top[next_i], loop_top[i])))
    return faces


def _mark_loop_crease(bm: BMesh, loop_verts: list, crease_val: float = 1.0) -> None:
    """Marks all edges along a vertex loop with crease (Shift+E) for Subsurf."""
    if crease_val <= 0.0 or not loop_verts:
        return
    crease_layer = bm.edges.layers.float.get("crease_edge") or bm.edges.layers.float.new("crease_edge")
    n = len(loop_verts)
    for i in range(n):
        v1, v2 = loop_verts[i], loop_verts[(i + 1) % n]
        e = bm.edges.get((v1, v2))
        if e:
            e[crease_layer] = float(crease_val)


def _mark_vertical_creases(bm: BMesh, loop1: list, loop2: list, crease_val: float = 1.0) -> None:
    """Marks vertical longitudinal edges connecting corresponding vertices with crease."""
    if crease_val <= 0.0:
        return
    crease_layer = bm.edges.layers.float.get("crease_edge") or bm.edges.layers.float.new("crease_edge")
    n = min(len(loop1), len(loop2))
    for i in range(n):
        e = bm.edges.get((loop1[i], loop2[i]))
        if e:
            e[crease_layer] = float(crease_val)


def _build_bottom_cap(bm: BMesh, bot_rim_verts: list, inset_scale: float = 0.75, crease_val: float = 1.0) -> None:
    """Builds an inset concentric face on the bottom cap and sets crease on the outer rim."""
    n = len(bot_rim_verts)
    if n < 3:
        return
    cx = sum(v.co.x for v in bot_rim_verts) / n
    cy = sum(v.co.y for v in bot_rim_verts) / n
    cz = bot_rim_verts[0].co.z
    inset_verts = [
        bm.verts.new((cx + (v.co.x - cx) * inset_scale, cy + (v.co.y - cy) * inset_scale, cz))
        for v in bot_rim_verts
    ]
    _bridge_loops(bm, bot_rim_verts, inset_verts)
    bm.faces.new(inset_verts)
    _mark_loop_crease(bm, bot_rim_verts, crease_val)


def _build_top_flat_cap(bm: BMesh, top_rim_verts: list, inset_scale: float = 0.75, crease_val: float = 1.0) -> None:
    """Builds an inset concentric face on the top flat cap and sets crease on the outer rim."""
    n = len(top_rim_verts)
    if n < 3:
        return
    cx = sum(v.co.x for v in top_rim_verts) / n
    cy = sum(v.co.y for v in top_rim_verts) / n
    cz = top_rim_verts[0].co.z
    inset_verts = [
        bm.verts.new((cx + (v.co.x - cx) * inset_scale, cy + (v.co.y - cy) * inset_scale, cz))
        for v in top_rim_verts
    ]
    _bridge_loops(bm, inset_verts, top_rim_verts)
    bm.faces.new(inset_verts).normal_flip()
    _mark_loop_crease(bm, top_rim_verts, crease_val)


# ---------------------------------------------------------------------------
# V-Prong cross-section helper
# ---------------------------------------------------------------------------

def _build_v_prong_coords(z: float, s: float, t: float, d: float) -> list:
    """Calculates the 6 coordinates of a V-Prong cross section at height z (Rust native con fallback)."""
    try:
        from .. import _rust_bridge as rb
        if rb.has_rust_engine():
            res = rb.calc_v_prong_coords(s, t, d)
            if res is not None and len(res) == 6:
                return [(x, y, z) for (x, y) in res]
    except Exception:
        pass

    L = sqrt(s * s + d * d)
    if L > 1e-6:
        nx = d / L
        ny = s / L
        apex_y = d + t * (L / s)
    else:
        nx, ny = 0.7071, 0.7071
        apex_y = d + t * 1.4142

    return [
        ( 0.0,            apex_y, z),  # 0 (A) outer apex
        ( s + t * nx,     t * ny, z),  # 1 (B) right outer wing
        ( s,              0.0,    z),  # 2 (C) right inner wing
        ( 0.0,            d,      z),  # 3 (D) inner notch
        (-s,              0.0,    z),  # 4 (E) left  inner wing
        (-(s + t * nx),   t * ny, z),  # 5 (F) left  outer wing
    ]


# ---------------------------------------------------------------------------
# Tip builder (cylindrical prongs)
# ---------------------------------------------------------------------------

def _build_tip(
    bm: BMesh,
    radius: float,
    z_top: float,
    tip_type: str,
    bump_scale: float,
    claw_tip_dia: float = 0.0,
    claw_offset: float = 0.15,
    detalization: int = 16,
) -> list:
    """Generates the top tip geometry for cylindrical prongs."""
    if tip_type == "DOME":
        if bump_scale > 0.001:
            layers = max(2, int(detalization / 4))
            prev_loop = _circle_verts(bm, radius, z_top, detalization)
            base_loop = prev_loop
            for layer in range(1, layers):
                phi = (pi / 2.0) * (layer / layers)
                cur_r = radius * cos(phi)
                cur_z = z_top + (radius * bump_scale * sin(phi))
                cur_loop = _circle_verts(bm, cur_r, cur_z, detalization)
                _bridge_loops(bm, prev_loop, cur_loop)
                prev_loop = cur_loop
            apex = bm.verts.new((0.0, 0.0, z_top + (radius * bump_scale)))
            for i in range(detalization):
                bm.faces.new((prev_loop[i], prev_loop[(i + 1) % detalization], apex))
            return base_loop
        else:
            loop = _circle_verts(bm, radius, z_top, detalization)
            _build_top_flat_cap(bm, loop, inset_scale=0.75, crease_val=1.0)
            return loop

    elif tip_type == "FLAT":
        loop = _circle_verts(bm, radius, z_top, detalization)
        _build_top_flat_cap(bm, loop, inset_scale=0.75, crease_val=1.0)
        return loop

    elif tip_type == "CLAW":
        base_loop = _circle_verts(bm, radius, z_top, detalization)
        _mark_loop_crease(bm, base_loop, 1.0)
        apex_z = z_top + (radius * max(0.5, bump_scale * 1.5))
        tip_r = max(0.0, min(radius, claw_tip_dia / 2.0))
        offset_y = -claw_offset
        if tip_r < 0.005:
            apex = bm.verts.new((0.0, offset_y, apex_z))
            for i in range(detalization):
                bm.faces.new((base_loop[i], base_loop[(i + 1) % detalization], apex))
        else:
            angle_step = tau / detalization
            tip_loop = [
                bm.verts.new((sin(i * angle_step) * tip_r, offset_y + cos(i * angle_step) * tip_r, apex_z))
                for i in range(detalization)
            ]
            _build_top_flat_cap(bm, tip_loop, inset_scale=0.75, crease_val=1.0)
            _bridge_loops(bm, base_loop, tip_loop)
        return base_loop

    return _circle_verts(bm, radius, z_top, detalization)
