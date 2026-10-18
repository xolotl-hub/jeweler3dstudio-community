"""
Jeweler 3D Studio - Gallery Geometric Mesh Generators
Procedural bmesh generators for under-gallery structures:
  - Wire Gallery: tubular wire frame below the gem seat
  - Knife Gallery: thin knife-edge wall with cutaway windows
  - Milgrain Gallery: decorative bead-edge wire rail
Strictly kept < 250 lines.
"""

import math
from typing import List, Tuple
import bmesh
from mathutils import Vector, Matrix


def _ellipse_pt(rx: float, ry: float, theta: float) -> Tuple[float, float]:
    return rx * math.cos(theta), ry * math.sin(theta)


def _tube_ring(
    bm: bmesh.types.BMesh,
    center: Vector,
    rx: float, ry: float,
    tube_r: float,
    seg_ring: int = 28,
    seg_tube: int = 8,
) -> None:
    """Aro toroidal elíptico cerrado."""
    rings: List[List[bmesh.types.BMVert]] = []
    for i in range(seg_ring):
        theta = (i / seg_ring) * math.tau
        cx = center.x + rx * math.cos(theta)
        cy = center.y + ry * math.sin(theta)
        norm = Vector((math.cos(theta), math.sin(theta), 0.0)).normalized()
        binorm = Vector((0.0, 0.0, 1.0))
        ring: List[bmesh.types.BMVert] = []
        for j in range(seg_tube):
            phi = (j / seg_tube) * math.tau
            disp = (norm * math.cos(phi) + binorm * math.sin(phi)) * tube_r
            ring.append(bm.verts.new(Vector((cx, cy, center.z)) + disp))
        rings.append(ring)

    for i in range(seg_ring):
        r1, r2 = rings[i], rings[(i + 1) % seg_ring]
        for j in range(seg_tube):
            bm.faces.new((r1[j], r2[j], r2[(j + 1) % seg_tube], r1[(j + 1) % seg_tube]))


def _cyl_open(
    bm: bmesh.types.BMesh,
    start: Vector, end: Vector,
    radius: float, segments: int = 10,
) -> None:
    """Cilindro abierto (sin tapas)."""
    vec = end - start
    if vec.length < 1e-5:
        return
    z_ax = vec.normalized()
    up = Vector((0, 0, 1)) if abs(z_ax.z) < 0.9 else Vector((1, 0, 0))
    x_ax = z_ax.cross(up).normalized()
    y_ax = x_ax.cross(z_ax).normalized()
    bot: List[bmesh.types.BMVert] = []
    top: List[bmesh.types.BMVert] = []
    for i in range(segments):
        theta = (i / segments) * math.tau
        off = (x_ax * math.cos(theta) + y_ax * math.sin(theta)) * radius
        bot.append(bm.verts.new(start + off))
        top.append(bm.verts.new(end + off))
    for i in range(segments):
        i2 = (i + 1) % segments
        bm.faces.new((bot[i], top[i], top[i2], bot[i2]))


def build_wire_gallery_bmesh(
    gem_dim_bu: Vector,
    wire_r_bu: float,
    n_rails: int,
    rail_spacing_bu: float,
    n_bridges: int,
    bridge_r_bu: float,
) -> bmesh.types.BMesh:
    """
    Wire Gallery: aros elípticos apilados (rails) + puentes verticales (bridges).
    """
    bm = bmesh.new()
    rx = gem_dim_bu.x * 0.5
    ry = gem_dim_bu.y * 0.5

    z_offsets = [-(i * rail_spacing_bu) for i in range(n_rails)]

    for z in z_offsets:
        _tube_ring(bm, Vector((0.0, 0.0, z)), rx, ry, wire_r_bu)

    if n_bridges > 0 and n_rails > 1:
        for i in range(n_bridges):
            theta = (i / n_bridges) * math.tau
            cx, cy = _ellipse_pt(rx, ry, theta)
            _cyl_open(
                bm,
                Vector((cx, cy, z_offsets[-1])),
                Vector((cx, cy, z_offsets[0])),
                bridge_r_bu,
            )

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build_knife_gallery_bmesh(
    gem_dim_bu: Vector,
    wall_bu: float,
    height_bu: float,
    window_count: int,
    window_arc_deg: float,
    segments: int = 48,
) -> bmesh.types.BMesh:
    """
    Knife Gallery: pared elíptica delgada con ventanas para paso de luz.
    """
    bm = bmesh.new()
    rx = gem_dim_bu.x * 0.5
    ry = gem_dim_bu.y * 0.5
    z_top = 0.0
    z_bot = -height_bu

    solid_sections: List[Tuple[float, float]] = []
    if window_count <= 0:
        solid_sections = [(0.0, math.tau)]
    else:
        step = math.tau / window_count
        gap = min(math.radians(window_arc_deg), step * 0.7)
        for i in range(window_count):
            base = i * step
            solid_sections.append((base + gap, base + step))

    for a_start, a_end in solid_sections:
        span = a_end - a_start
        if span <= 1e-4:
            continue
        steps = max(2, int(segments * span / math.tau))
        it_v, ot_v, ib_v, ob_v = [], [], [], []
        for i in range(steps + 1):
            theta = a_start + (i / steps) * span
            ct, st = math.cos(theta), math.sin(theta)
            it_v.append(bm.verts.new(Vector((rx * ct, ry * st, z_top))))
            ot_v.append(bm.verts.new(Vector(((rx + wall_bu) * ct, (ry + wall_bu) * st, z_top))))
            ib_v.append(bm.verts.new(Vector((rx * ct, ry * st, z_bot))))
            ob_v.append(bm.verts.new(Vector(((rx + wall_bu) * ct, (ry + wall_bu) * st, z_bot))))
        for i in range(steps):
            bm.faces.new((it_v[i], ot_v[i], ot_v[i + 1], it_v[i + 1]))
            bm.faces.new((ot_v[i], ob_v[i], ob_v[i + 1], ot_v[i + 1]))
            bm.faces.new((it_v[i], it_v[i + 1], ib_v[i + 1], ib_v[i]))
            bm.faces.new((ib_v[i], ib_v[i + 1], ob_v[i + 1], ob_v[i]))
        bm.faces.new((it_v[0], ib_v[0], ob_v[0], ot_v[0]))
        bm.faces.new((it_v[-1], ot_v[-1], ob_v[-1], ib_v[-1]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build_milgrain_gallery_bmesh(
    gem_dim_bu: Vector,
    bead_r_bu: float,
    n_beads: int,
    z_offset_bu: float,
    wire_r_bu: float,
) -> bmesh.types.BMesh:
    """
    Milgrain Gallery: aro base + cuentas/bolitas decorativas equidistantes.
    """
    bm = bmesh.new()
    rx = gem_dim_bu.x * 0.5
    ry = gem_dim_bu.y * 0.5

    _tube_ring(bm, Vector((0.0, 0.0, z_offset_bu)), rx, ry, wire_r_bu)

    if n_beads > 0:
        for i in range(n_beads):
            theta = (i / n_beads) * math.tau
            cx, cy = _ellipse_pt(rx, ry, theta)
            bmesh.ops.create_uvsphere(
                bm,
                u_segments=8, v_segments=6,
                radius=bead_r_bu,
                matrix=Matrix.Translation(Vector((cx, cy, z_offset_bu))),
                calc_uvs=False,
            )

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
