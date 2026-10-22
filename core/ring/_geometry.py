"""
Jeweler 3D Community - Ring: Geometry Builders

BMesh procedural mesh and curve generators: 3D circular Bezier sizing curve,
sizing reference cylinder, and 3D swept shank mesh with automatic edge creasing.
"""

from typing import List, Set, Optional
import math
import bpy
import bmesh
from ._profiles import _PROFILE_FNS, _make_profile_media_cana, _find_sharp_corner_indices


def create_ring_bezier_curve(name: str, radius: float) -> bpy.types.Curve:
    """Create a circular 3D Bezier curve as a ring-size reference."""
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.use_cyclic_u = True
    k = 0.5522847498307936 * radius
    pts = [
        (radius,  0.0,    0.0,   radius,  k,      0.0,   radius, -k,     0.0),
        (0.0,     radius, 0.0,  -k,       radius,  0.0,   k,      radius, 0.0),
        (-radius, 0.0,    0.0,  -radius, -k,      0.0,  -radius,  k,     0.0),
        (0.0,    -radius, 0.0,   k,      -radius,  0.0,  -k,     -radius, 0.0),
    ]
    spline.bezier_points.add(3)
    for i, (px, py, pz, hrx, hry, hrz, hlx, hly, hlz) in enumerate(pts):
        bp = spline.bezier_points[i]
        bp.co = (px, py, pz)
        bp.handle_right = (hrx, hry, hrz)
        bp.handle_left = (hlx, hly, hlz)
    return curve_data


def create_ring_cylinder_mesh(name: str, radius: float, depth: float) -> bpy.types.Mesh:
    """Create a ring-size reference cylinder with BMesh."""
    mesh_data = bpy.data.meshes.new(name=name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=64, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh_data)
    bm.free()
    return mesh_data


def create_ring_profile_mesh(
    name: str,
    inner_radius_mm: float,
    width_mm: float,
    height_mm: float,
    profile_key: str,
    n_ring: int = 16,
    profile_segments: int = 2,
    crease_value: float = 0.8,
) -> bpy.types.Mesh:
    """Generate the complete 3D mesh by sweeping the cross-section
    around the inner circle (radius = US ring size diameter / 2).

    inner_radius_mm : inner radius defining the US ring size at the finger surface.
    width_mm        : band width along the finger axis.
    height_mm       : radial metal thickness extending outward.
    n_ring          : number of radial divisions around the ring.
    profile_segments: subdivision resolution for curved profile sections.
    crease_value    : crease (Shift+E) assigned to longitudinal edges at sharp corners.
    """
    profile_fn = _PROFILE_FNS.get(profile_key, _make_profile_media_cana)
    try:
        profile_pts = profile_fn(n=profile_segments)
    except TypeError:
        profile_pts = profile_fn()
    M = len(profile_pts)
    sharp_corners = set(_find_sharp_corner_indices(profile_pts))

    bm = bmesh.new()
    crease_layer = None
    if crease_value > 0.0:
        crease_layer = bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')

    # Generar todos los vertices: n_ring x M
    verts: List[List] = []
    for ring_i in range(n_ring):
        theta = 2.0 * math.pi * ring_i / n_ring
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        ring_row = []
        for (u_norm, v_norm) in profile_pts:
            r = inner_radius_mm + u_norm * height_mm
            z = v_norm * width_mm
            ring_row.append(bm.verts.new((r * cos_t, r * sin_t, z)))
        verts.append(ring_row)

    bm.verts.ensure_lookup_table()

    # Generar caras (quads) entre segmentos adyacentes del sweep
    for ring_i in range(n_ring):
        ring_next = (ring_i + 1) % n_ring
        for prof_j in range(M):
            prof_next = (prof_j + 1) % M
            v0 = verts[ring_i][prof_j]
            v1 = verts[ring_i][prof_next]
            v2 = verts[ring_next][prof_next]
            v3 = verts[ring_next][prof_j]
            try:
                bm.faces.new((v0, v1, v2, v3))
            except Exception:
                pass  # saltar caras degeneradas (ej. knife_edge triangulo)

    bm.edges.ensure_lookup_table()

    # Asignar Crease en aristas longitudinales de esquinas vivas
    if crease_layer is not None and crease_value > 0.0:
        for ring_i in range(n_ring):
            ring_next = (ring_i + 1) % n_ring
            for prof_j in sharp_corners:
                v_a = verts[ring_i][prof_j]
                v_b = verts[ring_next][prof_j]
                for e in v_a.link_edges:
                    if e.other_vert(v_a) == v_b:
                        e[crease_layer] = crease_value
                        break

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh_data = bpy.data.meshes.new(name)
    bm.to_mesh(mesh_data)
    bm.free()

    for poly in mesh_data.polygons:
        poly.use_smooth = True

    mesh_data.update()
    return mesh_data
