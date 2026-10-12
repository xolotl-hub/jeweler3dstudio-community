"""
Jeweler 3D Studio - Core V-Cutters Module

Three independent cutter operators for fishtail / castle / micro-pavé setting:

  1. J3DComm_OT_add_u_cutter           — U-slot transversal a cada gema del arreglo
  2. J3DComm_OT_add_v_cutter_long      — V-cuña longitudinal entre par de gemas (a lo largo)
  3. J3DComm_OT_add_v_cutter_trans     — V-cuña transversal entre par de gemas (a lo ancho)
"""

import math
from typing import List
import bpy
import bmesh
from mathutils import Vector, Matrix
from bpy.props import FloatProperty
from bpy.types import Operator, Context
from .units import mm_to_bu


# ─────────────────────────────────────────────────────────────────────────────
# GEOMETRY BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# TRANSFORM HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _gem_up(gem: bpy.types.Object) -> Vector:
    mw = gem.matrix_world
    return Vector((mw[0][2], mw[1][2], mw[2][2])).normalized()


def _mat4(u_x: Vector, u_y: Vector, u_z: Vector, pos: Vector) -> Matrix:
    return Matrix([
        [u_x.x, u_y.x, u_z.x, pos.x],
        [u_x.y, u_y.y, u_z.y, pos.y],
        [u_x.z, u_y.z, u_z.z, pos.z],
        [0.0,   0.0,   0.0,   1.0  ],
    ])


def _mat_at_gem_in_chain(chain: List[bpy.types.Object], idx: int, offset_z_bu: float) -> Matrix:
    """Matriz alineada con el riel en la posición de chain[idx].
    
    X → a lo largo de la cadena (u_chain)
    Y → cruzando el riel transversalmente (u_cross)
    Z → normal gema (u_z)
    """
    gem = chain[idx]
    loc = gem.matrix_world.translation.copy()
    u_z = _gem_up(gem)

    if len(chain) >= 2:
        if idx == 0:
            u_chain = chain[1].matrix_world.translation - loc
        elif idx == len(chain) - 1:
            u_chain = loc - chain[-2].matrix_world.translation
        else:
            u_chain = chain[idx + 1].matrix_world.translation - chain[idx - 1].matrix_world.translation
        if u_chain.length < 1e-5:
            u_chain = Vector((0.0, 1.0, 0.0))
        else:
            u_chain = u_chain.normalized()
    else:
        mw_rot = gem.matrix_world.to_3x3()
        cand = (mw_rot @ Vector((0.0, 1.0, 0.0))).normalized()
        if abs(cand.dot(u_z)) > 0.95:
            cand = (mw_rot @ Vector((1.0, 0.0, 0.0))).normalized()
        u_chain = cand

    u_cross = u_z.cross(u_chain)
    if u_cross.length < 1e-4:
        u_cross = Vector((1.0, 0.0, 0.0))
    else:
        u_cross = u_cross.normalized()

    u_chain = u_cross.cross(u_z).normalized()
    pos = loc + u_z * offset_z_bu
    return _mat4(u_chain, u_cross, u_z, pos)


def _mat_between_gems(ga: bpy.types.Object, gb: bpy.types.Object,
                      offset_z_bu: float, transversal: bool = False) -> Matrix:
    """Matriz en el punto medio entre dos gemas contiguas.

    transversal=False → Y local a lo largo de la cadena (longitudinal)
    transversal=True  → Y local perpendicular al riel   (transversal)
    """
    loc_a = ga.matrix_world.translation
    loc_b = gb.matrix_world.translation
    mid   = (loc_a + loc_b) * 0.5

    u_chain = loc_b - loc_a
    if u_chain.length < 1e-6:
        u_chain = Vector((0.0, 1.0, 0.0))
    u_chain = u_chain.normalized()

    u_z_raw = _gem_up(ga) + _gem_up(gb)
    if u_z_raw.length < 1e-4:
        u_z_raw = Vector((0.0, 0.0, 1.0))
    else:
        u_z_raw = u_z_raw.normalized()

    u_cross = u_z_raw.cross(u_chain)
    if u_cross.length < 1e-4:
        u_cross = Vector((1.0, 0.0, 0.0))
    else:
        u_cross = u_cross.normalized()

    u_z = u_chain.cross(u_cross).normalized()
    pos = mid + u_z * offset_z_bu

    if transversal:
        u_x, u_y = u_chain, u_cross
    else:
        u_x, u_y = u_cross, u_chain

    return _mat4(u_x, u_y, u_z, pos)


# ─────────────────────────────────────────────────────────────────────────────
# CHAIN SORT
# ─────────────────────────────────────────────────────────────────────────────

def _sort_chain(gems: List[bpy.types.Object]) -> List[bpy.types.Object]:
    if len(gems) <= 2:
        return list(gems)
    avg = sum((g.matrix_world.translation for g in gems), Vector()) / len(gems)
    start = max(gems, key=lambda g: (g.matrix_world.translation - avg).length_squared)
    chain, unvisited = [start], set(gems) - {start}
    while unvisited:
        nxt = min(unvisited, key=lambda g: (
            g.matrix_world.translation - chain[-1].matrix_world.translation).length_squared)
        chain.append(nxt)
        unvisited.remove(nxt)
    return chain


# ─────────────────────────────────────────────────────────────────────────────
# MERGE & FINALIZE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _merge_bm_into(source_bm: bmesh.types.BMesh,
                   master_bm: bmesh.types.BMesh,
                   t_mat: Matrix) -> None:
    source_bm.transform(t_mat)
    tmp = bpy.data.meshes.new("_vc_tmp")
    source_bm.to_mesh(tmp)
    source_bm.free()
    v_base = len(master_bm.verts)
    for v in tmp.vertices:
        master_bm.verts.new(v.co)
    master_bm.verts.ensure_lookup_table()
    for poly in tmp.polygons:
        try:
            master_bm.faces.new([master_bm.verts[v_base + li] for li in poly.vertices])
        except Exception:
            pass
    bpy.data.meshes.remove(tmp)


def _finalize_cutter_obj(master_bm: bmesh.types.BMesh,
                         context: bpy.types.Context,
                         root_gem: bpy.types.Object,
                         obj_name: str,
                         j3d_type: str) -> bpy.types.Object:
    existing = next(
        (o for o in bpy.data.objects
         if o.name == obj_name or (o.parent == root_gem and o.get("j3d_type") == j3d_type)),
        None,
    )
    if existing:
        master_bm.to_mesh(existing.data)
        master_bm.free()
        return existing

    mesh = bpy.data.meshes.new(f"{obj_name}_Mesh")
    master_bm.to_mesh(mesh)
    master_bm.free()

    obj = bpy.data.objects.new(obj_name, mesh)
    context.collection.objects.link(obj)
    obj.parent = root_gem
    obj.matrix_parent_inverse = root_gem.matrix_world.inverted()
    obj.matrix_basis = Matrix.Identity(4)
    obj["j3d_type"] = j3d_type
    obj.display_type = 'WIRE'
    return obj


def _apply_boolean_if_allowed(context: bpy.types.Context,
                               cutter_obj: bpy.types.Object) -> None:
    try:
        is_community = (
            "community" in context.scene.get("bl_idname_prefix", "").lower()
            or "community" in getattr(bpy.context, "package", "").lower()
        )
        if is_community:
            return
        metal = next(
            (o for o in context.selected_objects
             if o.type == 'MESH' and o != cutter_obj
             and o.get("j3d_type") not in ("GEM", "CUTTER", "V_CUTTER_LONG",
                                            "V_CUTTER_TRANS", "U_CUTTER")),
            None,
        )
        if not metal:
            return
        if any(m.type == 'BOOLEAN' and m.object == cutter_obj for m in metal.modifiers):
            return
        mod = metal.modifiers.new(name=f"Cut_{cutter_obj.name}", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter_obj
        mod.solver = 'EXACT'
        mod.show_viewport = False
        mod.show_render = True
    except Exception:
        pass


def _avg_gem_size(gems: List[bpy.types.Object]) -> float:
    sizes = [float(g.get("j3d_gem_size", 0.0)) for g in gems]
    avg = sum(sizes) / len(sizes) if sizes else 0.0
    if avg < 0.01:
        avg = sum(max(g.dimensions.x, g.dimensions.y) for g in gems) / len(gems)
    return max(avg, 0.5)


# ─────────────────────────────────────────────────────────────────────────────
# OPERATOR 1: U-CUTTER  (transversal a la gema)
# ─────────────────────────────────────────────────────────────────────────────

class J3DComm_OT_add_u_cutter(Operator):
    """Slot en U transversal centrado en cada gema seleccionada"""
    bl_idname = "j3d_community.add_u_cutter"
    bl_label = "Add U-Cutter to Gems"
    bl_description = (
        "Slot en forma de U perpendicular al riel en cada gema. "
        "Abre el canal con fondo redondeado para asentar gemas."
    )
    bl_options = {'REGISTER', 'UNDO'}

    width:      FloatProperty(name="Ancho slot (X)",  default=0.50, min=0.01, precision=3, step=5)   # type: ignore
    band_width: FloatProperty(name="Ancho riel (Y)",  default=3.50, min=0.10, precision=3, step=20)  # type: ignore
    handle_z:   FloatProperty(name="Handle (Z1)",     default=0.35, min=0.01, precision=3, step=5)   # type: ignore
    depth:      FloatProperty(name="Profundidad (Z2)", default=0.55, min=0.01, precision=3, step=10) # type: ignore
    offset_z:   FloatProperty(name="Offset Z",        default=0.00, precision=3, step=5)             # type: ignore
    angle_deg:  FloatProperty(                                                                        # type: ignore
        name="Ángulo (deg)",
        description="Rotación del slot alrededor de Z (0° = perpendicular al riel). "
                    "Con 1 gema permite alinear manualmente el U-Cutter.",
        default=0.0, min=-180.0, max=180.0, step=100, precision=1,
    )

    @classmethod
    def poll(cls, context: Context) -> bool:
        return any(o.get("j3d_type") == "GEM" or "gem" in o.name.lower()
                   for o in context.selected_objects)

    def invoke(self, context: Context, event: bpy.types.Event) -> set:
        gems = [o for o in context.selected_objects
                if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()]
        if gems:
            s = _avg_gem_size(gems)
            self.width      = round(s * 0.50, 3)
            self.band_width = round(max(3.50, s * 2.80), 3)
            self.handle_z   = round(s * 0.35, 3)
            self.depth      = round(s * 0.55, 3)
            self.offset_z   = 0.000
            self.angle_deg  = 0.0
        return self.execute(context)

    def draw(self, context: Context) -> None:
        box = self.layout.box()
        box.label(text="U-Cutter Profile (mm):", icon='META_PLANE')
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, "width")
        row.prop(self, "band_width")
        row2 = col.row(align=True)
        row2.prop(self, "handle_z")
        row2.prop(self, "depth")
        col.prop(self, "offset_z")
        col.prop(self, "angle_deg")

    def execute(self, context: Context) -> set:
        gems = [o for o in context.selected_objects
                if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()]
        if not gems:
            self.report({'WARNING'}, "Selecciona al menos 1 gema.")
            return {'CANCELLED'}

        chain = _sort_chain(gems)
        bu  = mm_to_bu(1.0, context)
        w   = self.width      * bu
        bw  = self.band_width * bu
        hz  = self.handle_z   * bu
        d   = self.depth      * bu
        off = self.offset_z   * bu
        angle_rad = math.radians(self.angle_deg)

        master_bm = bmesh.new()
        for i in range(len(chain)):
            mat = _mat_at_gem_in_chain(chain, i, off)
            # Aplicar rotación adicional alrededor del eje local Z del slot.
            if abs(angle_rad) > 1e-6:
                rot_z = Matrix.Rotation(angle_rad, 4, 'Z')
                mat = mat @ rot_z
            _merge_bm_into(_build_u_slot_bm(w, bw, hz, d), master_bm, mat)

        bmesh.ops.recalc_face_normals(master_bm, faces=master_bm.faces)
        root = chain[0]
        obj  = _finalize_cutter_obj(master_bm, context, root,
                                    f"U_Cutters_{root.name}", "U_CUTTER")
        _apply_boolean_if_allowed(context, obj)
        self.report({'INFO'}, f"U-Cutter: {len(chain)} slots generados.")
        return {'FINISHED'}



# ─────────────────────────────────────────────────────────────────────────────
# OPERATOR 2: V-CUTTER LONGITUDINAL  (a lo largo de la cadena)
# ─────────────────────────────────────────────────────────────────────────────

class J3DComm_OT_add_v_cutter_long(Operator):
    """V-cuña longitudinal entre cada par de gemas contiguas"""
    bl_idname = "j3d_community.add_v_cutter_long"
    bl_label = "V-Cutter Longitudinal"
    bl_description = (
        "Cuñas en V a LO LARGO de la cadena. "
        "El perfil V se ve al mirar desde el extremo de la fila."
    )
    bl_options = {'REGISTER', 'UNDO'}

    width:         FloatProperty(name="Ancho V (X)",       default=0.35, min=0.01, precision=3, step=5)   # type: ignore
    factor_length: FloatProperty(name="Factor Largo (Y)",  default=0.85, min=0.10, max=1.50, precision=2, step=5, # type: ignore
                                 description="Proporción del largo respecto a la distancia entre centros de cada par de gemas (0.85 = 85%)")
    handle_z:      FloatProperty(name="Handle (Z1)",      default=0.30, min=0.01, precision=3, step=5)   # type: ignore
    wedge_z:       FloatProperty(name="Cuña V (Z2)",      default=0.55, min=0.01, precision=3, step=10)  # type: ignore
    offset_z:      FloatProperty(name="Offset Z",         default=-0.05, precision=3, step=5)            # type: ignore

    @classmethod
    def poll(cls, context: Context) -> bool:
        return sum(1 for o in context.selected_objects
                   if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()) >= 2

    def invoke(self, context: Context, event: bpy.types.Event) -> set:
        gems = [o for o in context.selected_objects
                if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()]
        if gems:
            s = _avg_gem_size(gems)
            self.factor_length = 0.85
            self.width    = round(s * 0.35, 3)
            self.handle_z = round(s * 0.30, 3)
            self.wedge_z  = round(s * 0.55, 3)
            self.offset_z = round(s * -0.05, 3)
        return self.execute(context)

    def draw(self, context: Context) -> None:
        box = self.layout.box()
        box.label(text="V-Cutter Long.:", icon='DRIVER_DISTANCE')
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, "width")
        row.prop(self, "factor_length")
        row2 = col.row(align=True)
        row2.prop(self, "handle_z")
        row2.prop(self, "wedge_z")
        col.prop(self, "offset_z")

    def execute(self, context: Context) -> set:
        gems = [o for o in context.selected_objects
                if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()]
        if len(gems) < 2:
            self.report({'WARNING'}, "Selecciona al menos 2 gemas.")
            return {'CANCELLED'}

        chain = _sort_chain(gems)
        bu  = mm_to_bu(1.0, context)
        w   = self.width    * bu
        hz  = self.handle_z * bu
        wz  = self.wedge_z  * bu
        off = self.offset_z * bu

        master_bm = bmesh.new()
        for i in range(len(chain) - 1):
            ga = chain[i]
            gb = chain[i + 1]
            dist_centers = (gb.matrix_world.translation - ga.matrix_world.translation).length
            lng_i = max(1e-4, dist_centers * self.factor_length) * bu
            mat = _mat_between_gems(ga, gb, off, transversal=False)
            _merge_bm_into(_build_v_wedge_bm(w, lng_i, hz, wz), master_bm, mat)

        bmesh.ops.recalc_face_normals(master_bm, faces=master_bm.faces)
        root = chain[0]
        obj  = _finalize_cutter_obj(master_bm, context, root,
                                    f"VLong_{root.name}", "V_CUTTER_LONG")
        _apply_boolean_if_allowed(context, obj)
        self.report({'INFO'}, f"V-Cutter Long: {len(chain)-1} cuñas adaptativas.")
        return {'FINISHED'}


# ─────────────────────────────────────────────────────────────────────────────
# OPERATOR 3: V-CUTTER TRANSVERSAL  (a lo ancho del riel, entre gemas)
# ─────────────────────────────────────────────────────────────────────────────

class J3DComm_OT_add_v_cutter_trans(Operator):
    """V-cuña transversal cruzando el riel en cada gap entre gemas"""
    bl_idname = "j3d_community.add_v_cutter_trans"
    bl_label = "V-Cutter Transversal"
    bl_description = (
        "Cuñas en V que cruzan PERPENDICULARMENTE el riel en cada gap. "
        "El perfil V se ve al mirar desde el lateral."
    )
    bl_options = {'REGISTER', 'UNDO'}

    gap_width:  FloatProperty(name="Ancho gap (X)", default=0.35, min=0.01, precision=3, step=5)   # type: ignore
    band_width: FloatProperty(name="Ancho riel (Y)",default=3.50, min=0.10, precision=3, step=20)  # type: ignore
    handle_z:   FloatProperty(name="Handle (Z1)",   default=0.35, min=0.01, precision=3, step=5)   # type: ignore
    wedge_z:    FloatProperty(name="Cuña V (Z2)",   default=0.50, min=0.01, precision=3, step=10)  # type: ignore
    offset_z:   FloatProperty(name="Offset Z",      default=-0.05, precision=3, step=5)            # type: ignore
    cap_ends:   bpy.props.BoolProperty(name="Rematar extremos", default=True,                      # type: ignore
                                       description="Genera cuñas en V en los extremos exteriores de la fila")

    @classmethod
    def poll(cls, context: Context) -> bool:
        return sum(1 for o in context.selected_objects
                   if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()) >= 2

    def invoke(self, context: Context, event: bpy.types.Event) -> set:
        gems = [o for o in context.selected_objects
                if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()]
        if gems:
            s     = _avg_gem_size(gems)
            chain = _sort_chain(gems)
            if len(chain) >= 2:
                gaps = [(chain[i+1].matrix_world.translation
                         - chain[i].matrix_world.translation).length
                        for i in range(len(chain) - 1)]
                avg_gap = sum(gaps) / len(gaps)
                gap_between = max(avg_gap - s, 0.05)
                # 85% del valor resultante que da entre gema y gema
                self.gap_width = round(gap_between * 0.85, 3)
            else:
                self.gap_width = round(s * 0.30 * 0.85, 3)
            self.band_width = round(max(3.50, s * 2.80), 3)
            self.handle_z   = round(s * 0.35, 3)
            self.wedge_z    = round(s * 0.50, 3)
            self.offset_z   = round(s * -0.05, 3)
        return self.execute(context)

    def draw(self, context: Context) -> None:
        box = self.layout.box()
        box.label(text="V-Cutter Trans. (mm):", icon='MOD_BOOLEAN')
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, "gap_width")
        row.prop(self, "band_width")
        row2 = col.row(align=True)
        row2.prop(self, "handle_z")
        row2.prop(self, "wedge_z")
        col.prop(self, "offset_z")
        box.prop(self, "cap_ends")

    def execute(self, context: Context) -> set:
        gems = [o for o in context.selected_objects
                if o.get("j3d_type") == "GEM" or "gem" in o.name.lower()]
        if len(gems) < 2:
            self.report({'WARNING'}, "Selecciona al menos 2 gemas.")
            return {'CANCELLED'}

        chain = _sort_chain(gems)
        bu  = mm_to_bu(1.0, context)
        gw  = self.gap_width  * bu
        bw  = self.band_width * bu
        hz  = self.handle_z   * bu
        wz  = self.wedge_z    * bu
        off = self.offset_z   * bu

        master_bm = bmesh.new()
        total_wedges = 0

        # Cuñas intermedias entre cada par de gemas
        for i in range(len(chain) - 1):
            mat = _mat_between_gems(chain[i], chain[i + 1], off, transversal=True)
            _merge_bm_into(_build_v_wedge_bm(gw, bw, hz, wz), master_bm, mat)
            total_wedges += 1

        # Remates exteriores en los extremos
        if self.cap_ends and len(chain) >= 2:
            # Extremo inicial (antes de chain[0])
            loc_0 = chain[0].matrix_world.translation
            loc_1 = chain[1].matrix_world.translation
            v_step_0 = loc_1 - loc_0
            u_chain_0 = v_step_0.normalized()
            pos_start = loc_0 - u_chain_0 * (v_step_0.length * 0.5)
            u_z_0 = _gem_up(chain[0])
            u_cross_0 = (u_z_0.cross(u_chain_0)).normalized()
            u_z_0 = (u_chain_0.cross(u_cross_0)).normalized()
            mat_start = _mat4(u_chain_0, u_cross_0, u_z_0, pos_start + u_z_0 * off)
            _merge_bm_into(_build_v_wedge_bm(gw, bw, hz, wz), master_bm, mat_start)
            total_wedges += 1

            # Extremo final (después de chain[-1])
            loc_n1 = chain[-1].matrix_world.translation
            loc_n2 = chain[-2].matrix_world.translation
            v_step_n = loc_n1 - loc_n2
            u_chain_n = v_step_n.normalized()
            pos_end = loc_n1 + u_chain_n * (v_step_n.length * 0.5)
            u_z_n = _gem_up(chain[-1])
            u_cross_n = (u_z_n.cross(u_chain_n)).normalized()
            u_z_n = (u_chain_n.cross(u_cross_n)).normalized()
            mat_end = _mat4(u_chain_n, u_cross_n, u_z_n, pos_end + u_z_n * off)
            _merge_bm_into(_build_v_wedge_bm(gw, bw, hz, wz), master_bm, mat_end)
            total_wedges += 1

        bmesh.ops.recalc_face_normals(master_bm, faces=master_bm.faces)
        root = chain[0]
        obj  = _finalize_cutter_obj(master_bm, context, root,
                                    f"VTrans_{root.name}", "V_CUTTER_TRANS")
        _apply_boolean_if_allowed(context, obj)
        self.report({'INFO'}, f"V-Cutter Trans: {total_wedges} cuñas.")
        return {'FINISHED'}


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRATION
# ─────────────────────────────────────────────────────────────────────────────

classes = (
    J3DComm_OT_add_u_cutter,
    J3DComm_OT_add_v_cutter_long,
    J3DComm_OT_add_v_cutter_trans,
)


def register():
    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
