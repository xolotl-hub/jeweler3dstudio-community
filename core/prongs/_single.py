r"""
Jeweler 3D Studio - Single Gem Prongs Engine
Builds single prongs and parametric radial/symmetry prong arrays around a gemstone.
"""

from math import cos, pi, radians, sin, tau

try:
    import bmesh
    from bmesh.types import BMesh, BMVert, BMEdge, BMFace
    from mathutils import Matrix, Vector
except ImportError:
    BMesh = BMVert = BMEdge = BMFace = object  # type: ignore
    Matrix = Vector = object  # type: ignore

from ._tips import (
    _circle_verts,
    _bridge_loops,
    _mark_loop_crease,
    _mark_vertical_creases,
    _build_bottom_cap,
    _build_top_flat_cap,
    _build_v_prong_coords,
    _build_tip,
)
from .arrangements import get_prong_positions



def create_single_prong(
    diameter: float, z_top: float, z_bottom: float,
    tip_type: str = "DOME", bump_scale: float = 0.5,
    v_size: float = 0.27, v_wall: float = 0.20, v_depth: float = 0.15,
    claw_tip_dia: float = 0.0, claw_offset: float = 0.15,
    taper: float = 0.0, detalization: int = 16, crease_val: float = 0.85,
) -> BMesh:

    """Builds a single vertical prong BMesh with support loops, inset caps, and edge creases."""
    bm = bmesh.new()
    rad_top    = max(0.05, diameter / 2.0)
    rad_bottom = rad_top * (1.0 + max(0.0, taper))
    h_supp     = min(0.04, max(0.015, (z_top + z_bottom) * 0.04))

    if tip_type == "V_PRONG":
        s = max(0.05, v_size)
        t = max(0.02, v_wall)
        d = max(0.0,  v_depth)
        taper_factor = 1.0 + max(0.0, taper)

        c_top = _build_v_prong_coords(z_top, s, t, d)
        c_bot = _build_v_prong_coords(-z_bottom, s * taper_factor, t * taper_factor, d * taper_factor)

        f_bot_supp = h_supp / (z_top + z_bottom)
        f_top_supp = 1.0 - f_bot_supp
        c_bot_supp = [
            (c_bot[i][0] + (c_top[i][0] - c_bot[i][0]) * f_bot_supp,
             c_bot[i][1] + (c_top[i][1] - c_bot[i][1]) * f_bot_supp,
             -z_bottom + h_supp)
            for i in range(6)
        ]
        c_top_supp = [
            (c_bot[i][0] + (c_top[i][0] - c_bot[i][0]) * f_top_supp,
             c_bot[i][1] + (c_top[i][1] - c_bot[i][1]) * f_top_supp,
             z_top - h_supp)
            for i in range(6)
        ]

        loop_bot_rim  = [bm.verts.new(c) for c in c_bot]
        loop_bot_supp = [bm.verts.new(c) for c in c_bot_supp]
        loop_top_supp = [bm.verts.new(c) for c in c_top_supp]
        loop_top_rim  = [bm.verts.new(c) for c in c_top]

        _bridge_loops(bm, loop_bot_rim, loop_bot_supp)
        _bridge_loops(bm, loop_bot_supp, loop_top_supp)
        _bridge_loops(bm, loop_top_supp, loop_top_rim)

        # Bottom cap: split into two quads via center edge [0]→[3]
        bm.faces.new([loop_bot_rim[0], loop_bot_rim[3], loop_bot_rim[2], loop_bot_rim[1]])
        bm.faces.new([loop_bot_rim[0], loop_bot_rim[5], loop_bot_rim[4], loop_bot_rim[3]])
        # Top cap: reversed winding → normal +Z
        bm.faces.new([loop_top_rim[0], loop_top_rim[1], loop_top_rim[2], loop_top_rim[3]])
        bm.faces.new([loop_top_rim[0], loop_top_rim[3], loop_top_rim[4], loop_top_rim[5]])

        _mark_loop_crease(bm, loop_bot_rim, crease_val)
        _mark_loop_crease(bm, loop_top_rim, crease_val)

        crease_layer = bm.edges.layers.float.get("crease_edge") or bm.edges.layers.float.new("crease_edge")
        for loop in (loop_bot_rim, loop_top_rim):
            e = bm.edges.get((loop[0], loop[3]))
            if e:
                e[crease_layer] = crease_val

        _mark_vertical_creases(bm, loop_bot_rim,  loop_bot_supp, crease_val)
        _mark_vertical_creases(bm, loop_bot_supp, loop_top_supp, crease_val)
        _mark_vertical_creases(bm, loop_top_supp, loop_top_rim,  crease_val)

    else:
        # Cylindrical prongs: DOME, FLAT, CLAW
        total_h   = z_top + z_bottom
        f_supp    = h_supp / max(0.1, total_h)
        rad_bot_supp = rad_bottom - (rad_bottom - rad_top) * f_supp
        rad_top_supp = rad_top    + (rad_bottom - rad_top) * f_supp

        loop_bot_rim  = _circle_verts(bm, rad_bottom,   -z_bottom,          detalization)
        loop_bot_supp = _circle_verts(bm, rad_bot_supp, -z_bottom + h_supp, detalization)
        loop_top_supp = _circle_verts(bm, rad_top_supp,  z_top - h_supp,    detalization)
        loop_top_rim  = _circle_verts(bm, rad_top,       z_top,             detalization)

        _bridge_loops(bm, loop_bot_rim,  loop_bot_supp)
        _bridge_loops(bm, loop_bot_supp, loop_top_supp)
        _bridge_loops(bm, loop_top_supp, loop_top_rim)

        _build_bottom_cap(bm, loop_bot_rim, inset_scale=0.75, crease_val=crease_val)

        if tip_type == "FLAT":
            _build_top_flat_cap(bm, loop_top_rim, inset_scale=0.75, crease_val=crease_val)
        elif tip_type == "CLAW":
            _mark_loop_crease(bm, loop_top_rim, crease_val)
            apex_z  = z_top + (rad_top * max(0.5, bump_scale * 1.5))
            tip_r   = max(0.0, min(rad_top, claw_tip_dia / 2.0))
            offset_y = -claw_offset
            if tip_r < 0.005:
                apex = bm.verts.new((0.0, offset_y, apex_z))
                for i in range(detalization):
                    bm.faces.new((loop_top_rim[i], loop_top_rim[(i + 1) % detalization], apex))
            else:
                angle_step = tau / detalization
                tip_loop = [
                    bm.verts.new((sin(i * angle_step) * tip_r, offset_y + cos(i * angle_step) * tip_r, apex_z))
                    for i in range(detalization)
                ]
                _build_top_flat_cap(bm, tip_loop, inset_scale=0.75, crease_val=crease_val)
                _bridge_loops(bm, loop_top_rim, tip_loop)
        elif tip_type == "DOME":
            if bump_scale > 0.001:
                layers    = max(2, int(detalization / 4))
                prev_loop = loop_top_rim
                for layer in range(1, layers):
                    phi   = (pi / 2.0) * (layer / layers)
                    cur_r = rad_top * cos(phi)
                    cur_z = z_top + (rad_top * bump_scale * sin(phi))
                    cur_loop = _circle_verts(bm, cur_r, cur_z, detalization)
                    _bridge_loops(bm, prev_loop, cur_loop)
                    prev_loop = cur_loop
                apex = bm.verts.new((0.0, 0.0, z_top + (rad_top * bump_scale)))
                for i in range(detalization):
                    bm.faces.new((prev_loop[i], prev_loop[(i + 1) % detalization], apex))
            else:
                _build_top_flat_cap(bm, loop_top_rim, inset_scale=0.75, crease_val=crease_val)

    return bm


def generate_prongs_bmesh(
    gem_dim, cut_name: str = "ROUND", number: int = 4,
    diameter: float = 0.5, z_top: float = 0.35, z_bottom: float = 1.0,
    tip_type: str = "DOME", bump_scale: float = 1.0,
    v_size: float = 0.27, v_wall: float = 0.20, v_depth: float = 0.15,
    claw_tip_dia: float = 0.0, claw_offset: float = 0.15,
    taper: float = 0.0, position_deg: float = 45.0,
    girdle_offset: float = 0.0, inward_deg: float = 3.0,
    use_symmetry: bool = False, symmetry_pivot_deg: float = 0.0,
    detalization: int = 16, crease_val: float = 0.85,
) -> BMesh:

    """Generates the combined multi-prong BMesh adaptively distributed around the gem."""
    rad_prong = diameter / 2.0
    dim_x = getattr(gem_dim, "x", gem_dim[0] if hasattr(gem_dim, "__getitem__") else 1.0)
    dim_y = getattr(gem_dim, "y", gem_dim[1] if hasattr(gem_dim, "__getitem__") else 1.0)

    positions = get_prong_positions(
        cut_name=cut_name,
        dim_x=dim_x,
        dim_y=dim_y,
        count=number,
        girdle_offset=girdle_offset,
        user_angle_deg=position_deg,
        rad_prong=rad_prong,
        tip_type=tip_type,
    )

    if not positions:
        return bmesh.new()

    master_bm = bmesh.new()
    crease_dst = master_bm.edges.layers.float.get("crease_edge") or master_bm.edges.layers.float.new("crease_edge")

    for pos in positions:
        eff_tip = pos.tip_type or tip_type
        single_bm = create_single_prong(
            diameter=diameter,
            z_top=z_top,
            z_bottom=z_bottom,
            tip_type=eff_tip,
            bump_scale=bump_scale,
            v_size=v_size,
            v_wall=v_wall,
            v_depth=v_depth,
            claw_tip_dia=claw_tip_dia,
            claw_offset=claw_offset,
            taper=taper,
            detalization=detalization,
            crease_val=crease_val,
        )

        if abs(inward_deg) > 0.01:
            single_bm.transform(Matrix.Rotation(radians(-inward_deg), 4, "X"))

        single_bm.transform(Matrix.Rotation(pos.rot_z_rad, 4, "Z"))
        single_bm.transform(Matrix.Translation((pos.x, pos.y, 0.0)))

        crease_src = single_bm.edges.layers.float.get("crease_edge")
        vert_map: dict = {}
        for v in single_bm.verts:
            vert_map[v] = master_bm.verts.new(v.co)
        for e in single_bm.edges:
            ne = master_bm.edges.new((vert_map[e.verts[0]], vert_map[e.verts[1]]))
            if crease_src and crease_dst:
                ne[crease_dst] = e[crease_src]
        for f in single_bm.faces:
            master_bm.faces.new([vert_map[v] for v in f.verts])

        single_bm.free()

    master_bm.verts.ensure_lookup_table()
    master_bm.edges.ensure_lookup_table()
    master_bm.faces.ensure_lookup_table()

    if use_symmetry:
        mat_scale = Matrix.Scale(-1.0, 4, (0.0, 1.0, 0.0))
        dup       = bmesh.ops.duplicate(master_bm, geom=master_bm.verts[:] + master_bm.edges[:] + master_bm.faces[:])
        dup_verts = [e for e in dup["geom"] if isinstance(e, BMVert)]
        dup_faces = [e for e in dup["geom"] if isinstance(e, BMFace)]
        bmesh.ops.transform(master_bm, matrix=mat_scale, verts=dup_verts)
        bmesh.ops.reverse_faces(master_bm, faces=dup_faces)
        if abs(symmetry_pivot_deg) > 0.01:
            master_bm.transform(Matrix.Rotation(radians(-symmetry_pivot_deg), 4, "Z"))

    bmesh.ops.recalc_face_normals(master_bm, faces=master_bm.faces[:])
    return master_bm

