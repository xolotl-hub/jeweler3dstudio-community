"""
Jeweler 3D Studio - V-Cutters: Geometry Builders

BMesh constructors for U-slot and V-wedge profiles.
No bpy imports — pure math and bmesh.
"""

import math
import bmesh


def _build_v_wedge_bm(width_bu: float, length_bu: float,
                      handle_z_bu: float, wedge_z_bu: float) -> bmesh.types.BMesh:
    """Cuña en V simétrica en coordenadas locales.

    Perfil (vista a lo largo de Y):
        4───0   z = +handle_z
        │   │
        3   1   z = 0
         \\ /
          2     z = -wedge_z  (punta V)

    Ejes locales:
      X → ancho (width_bu)  |  Y → largo (length_bu)  |  Z → normal gema
    """
    bm = bmesh.new()
    x  = max(1e-4, width_bu)  * 0.5
    y  = max(1e-4, length_bu) * 0.5
    z1 = max(1e-4, handle_z_bu)
    z2 = max(1e-4, wedge_z_bu)

    coords_front = [
        ( x,  y,  z1),
        ( x,  y,  0.0),
        (0.0, y, -z2),
        (-x,  y,  0.0),
        (-x,  y,  z1),
    ]
    coords_back = [(px, -y, pz) for px, py, pz in coords_front]

    vf = [bm.verts.new(co) for co in coords_front]
    vb = [bm.verts.new(co) for co in coords_back]

    bm.faces.new([vf[0], vf[1], vf[3], vf[4]])
    bm.faces.new([vf[1], vf[2], vf[3]])
    bm.faces.new([vb[4], vb[3], vb[1], vb[0]])
    bm.faces.new([vb[3], vb[2], vb[1]])
    bm.faces.new([vf[0], vb[0], vb[1], vf[1]])
    bm.faces.new([vf[1], vb[1], vb[2], vf[2]])
    bm.faces.new([vf[2], vb[2], vb[3], vf[3]])
    bm.faces.new([vf[3], vb[3], vb[4], vf[4]])
    bm.faces.new([vf[4], vb[4], vb[0], vf[0]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def _build_u_slot_bm(width_bu: float, length_bu: float,
                     handle_z_bu: float, depth_bu: float,
                     segments: int = 12) -> bmesh.types.BMesh:
    """Perfil en U simétrico con fondo semicilíndrico.

    Perfil en X-Z:
        4─────────0    z = +handle_z (techo plano)
        │         │
        3         1    z = -z_straight (comienza arco)
         \\       /     arco semicircular radio r = width / 2
          '--2--'      z = -z_straight - r (punto inferior)

    Ejes locales:
      X → ancho slot (width_bu)  |  Y → largo transversal (length_bu)  |  Z ↑ normal gema
    """
    bm = bmesh.new()
    r = max(1e-4, width_bu) * 0.5
    y = max(1e-4, length_bu) * 0.5
    z_top = max(1e-4, handle_z_bu)
    total_d = max(r + 1e-4, depth_bu)
    z_straight = max(0.0, total_d - r)

    coords_front = [(r, y, z_top), (r, y, -z_straight)]
    for i in range(1, segments):
        angle = -math.pi * (i / segments)
        px = r * math.cos(angle)
        pz = -z_straight + r * math.sin(angle)
        coords_front.append((px, y, pz))
    coords_front.append((-r, y, -z_straight))
    coords_front.append((-r, y, z_top))

    coords_back = [(px, -y, pz) for px, py, pz in coords_front]

    vf = [bm.verts.new(co) for co in coords_front]
    vb = [bm.verts.new(co) for co in coords_back]

    bm.faces.new(list(reversed(vf)))
    bm.faces.new(vb)

    n = len(vf)
    for i in range(n - 1):
        bm.faces.new([vf[i], vf[i + 1], vb[i + 1], vb[i]])

    bm.faces.new([vf[-1], vf[0], vb[0], vb[-1]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
