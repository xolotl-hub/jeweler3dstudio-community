"""
Jeweler 3D Studio - Core Cutters Module
Procedural gem seat cutters with 5-zone calibrated profile and live parametric editing:
  Zona 1: Extension superior (tubo cilindrico superior por encima de la tabla)
  Zona 2: Cono de corona (transicion tabla <-> girdle)
  Zona 3: Anillo de girdle (ajuste y tolerancia)
  Zona 4: Cono de asiento (pabellon de la gema)
  Zona 5: Canal de perforacion inferior (taladro / orificio de luz)

Outlines 2D adaptativos para los 17 cortes estandar.
Control en vivo de segmentos, crease (Shift+E) y dimension/Z independiente por cada perimetro.
"""

import math
import bpy
import bmesh
from bpy.props import IntProperty, FloatProperty
from bpy.types import Operator
from .units import mm_to_bu

# -- Proporciones normalizadas del cortador segun estandares de joyeria ----------
CUTTER_TOP_RATIO        =  0.576   # Extension cilindrica superior (por encima de la tabla)
CUTTER_TABLE_RATIO      =  0.210   # Nivel de la tabla / transicion de corona
CUTTER_GIRDLE_TOP_RATIO =  0.048   # Borde superior del girdle
CUTTER_GIRDLE_BOT_RATIO = -0.026   # Borde inferior del girdle / asiento
CUTTER_SEAT_RATIO       = -0.266   # Cono de asiento (pabellon)
CUTTER_DEPTH_RATIO      =  1.010   # Profundidad del canal de perforacion inferior

# Ratios de radio (relativo a r_half = size_mm * 0.5)
CUTTER_R_TABLE  = 0.635   # Radio de tabla / tubo superior
CUTTER_R_GIRDLE = 1.045   # Radio del girdle (con margen de tolerancia)
CUTTER_R_HOLE   = 0.488   # Radio del canal inferior de luz / perforacion


# -- Grupos de cortes por familia de silueta ---------------------------------------
_ROUND_CUTS    = {"ROUND"}
_RECT_CUTS     = {"PRINCESS", "ASSCHER", "SQUARE", "FLANDERS", "OCTAGON"}
_BAGUETTE_CUTS = {"BAGUETTE", "EMERALD", "RADIANT"}
_OVAL_CUTS     = {"OVAL", "CUSHION"}
_PEAR_CUTS     = {"PEAR"}
_MARQUISE_CUTS = {"MARQUISE"}
_HEART_CUTS    = {"HEART"}
_TRIANGLE_CUTS = {"TRILLION", "TRILLIANT", "TRIANGLE"}


# -- Generadores de outline 2D (coordenadas normalizadas, radio aprox 1.0) ---------

def _circle(n: int):
    """Circulo perfecto: N puntos equidistantes."""
    return [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n))
            for i in range(n)]


def _ellipse(n: int, a: float = 1.0, b: float = 0.72):
    """Elipse para ovales y cojines."""
    return [(a * math.cos(2 * math.pi * i / n), b * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def _superellipse(n: int, a: float = 1.0, b: float = 1.0, p: float = 4.5):
    """Rectangulo con esquinas suavizadas (superelipse).
    p=4.5 da bordes levemente redondeados; p=2 da circulo.
    """
    pts = []
    for i in range(n):
        ang = 2 * math.pi * i / n
        c = math.cos(ang)
        s = math.sin(ang)
        denom = (abs(c / a) ** p + abs(s / b) ** p)
        r = denom ** (-1.0 / p) if denom > 1e-12 else 1.0
        pts.append((c * r * a, s * r * b))
    return pts


def _triangle_rounded(n: int, r_factor: float = 0.18):
    """Triangulo equilatero con vertices redondeados."""
    pts = []
    for i in range(n):
        ang = 2 * math.pi * i / n + math.pi / 2
        c = math.cos(ang)
        s = math.sin(ang)
        p_tri = 0.65
        denom = abs(c) ** p_tri + abs(s) ** p_tri
        r_tri = denom ** (-1.0 / p_tri) if denom > 1e-12 else 1.0
        r = r_tri * (1.0 - r_factor) + 1.0 * r_factor
        pts.append((c * r * 0.82, s * r * 0.82))
    return pts


def _pear(n: int):
    """Forma de pera: extremo inferior redondeado, punta superior."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r_base = 0.75 + 0.25 * math.cos(t)
        offset_y = -0.18 * math.sin(t)
        x = r_base * math.cos(t)
        y = r_base * math.sin(t) + offset_y
        pts.append((x, y))
    return pts


def _marquise(n: int):
    """Marquesa / lente: puntiaguda en los extremos laterales."""
    pts = []
    a, b = 1.0, 0.48
    for i in range(n):
        ang = 2 * math.pi * i / n
        c = math.cos(ang)
        s = math.sin(ang)
        p = 0.55
        denom = (abs(c / a) ** p + abs(s / b) ** p)
        r = denom ** (-1.0 / p) if denom > 1e-12 else 1.0
        pts.append((c * r * a, s * r * b))
    return pts


def _heart(n: int):
    """Corazon parametrico clasico normalizado."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n - math.pi / 2
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t)
              - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x / 16.5, y / 17.5))
    return pts


def get_cut_outline(cut_key: str, n: int):
    """Devuelve N puntos 2D normalizados del outline del corte dado."""
    k = cut_key.upper()
    n = max(4, n)
    if k in _ROUND_CUTS:
        return _circle(n)
    elif k in _RECT_CUTS:
        return _superellipse(n, a=1.0, b=1.0, p=4.5)
    elif k in _BAGUETTE_CUTS:
        return _superellipse(n, a=1.0, b=0.58, p=4.5)
    elif k in _OVAL_CUTS:
        return _ellipse(n, a=1.0, b=0.72)
    elif k in _PEAR_CUTS:
        return _pear(n)
    elif k in _MARQUISE_CUTS:
        return _marquise(n)
    elif k in _HEART_CUTS:
        return _heart(n)
    elif k in _TRIANGLE_CUTS:
        return _triangle_rounded(n)
    else:
        return _circle(n)


# -- Constructor de BMesh para Cortadores -----------------------------------------

def build_cutter_bmesh_from_levels(
    cut_key: str,
    segments: int,
    crease: float,
    levels_mm: list,
    context=None,
) -> bmesh.types.BMesh:
    """
    Construye un BMesh con 6 anillos a partir de [(r_mm, z_mm), ...] con tapas y crease.
    """
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

    # Conectar anillos consecutivos con quads
    for ri in range(len(rings) - 1):
        ra, rb = rings[ri], rings[ri + 1]
        for i in range(n):
            ni = (i + 1) % n
            try:
                bm.faces.new([ra[i], ra[ni], rb[ni], rb[i]])
            except Exception:
                pass

    # Tapa superior en la cima de la extension (fan desde centro)
    top_z = float(levels_mm[0][1]) * bu
    top_c = bm.verts.new((0.0, 0.0, top_z))
    for i in range(n):
        ni = (i + 1) % n
        try:
            bm.faces.new([top_c, rings[0][ni], rings[0][i]])
        except Exception:
            pass

    # Tapa inferior (fan desde centro)
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

    # Aplicar crease a todas las aristas horizontales (mismo Z)
    if crease > 0.0:
        crease_layer = bm.edges.layers.float.get("crease_edge")
        if crease_layer is None:
            crease_layer = bm.edges.layers.float.new("crease_edge")
        for edge in bm.edges:
            z0 = edge.verts[0].co.z
            z1 = edge.verts[1].co.z
            if abs(z0 - z1) < 1e-5:
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
    """
    Genera un mesh de cortador booleano profesional en 5 zonas.
    """
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


# -- Inicializacion y Actualizacion en Vivo de Propiedades de Objeto --------------

_UPDATING_CUTTER = False

def update_cutter_object_props_callback(self, context):
    """Callback invocado en tiempo real cuando el usuario mueve cualquier slider en la UI."""
    global _UPDATING_CUTTER
    if _UPDATING_CUTTER:
        return
    if self.get("j3d_community_type") != "CUTTER" or not self.data:
        return
    rebuild_cutter_from_object_props(self, context)


def init_cutter_object_props(ctr_obj: bpy.types.Object, cut_key: str, size_mm: float, segments: int = 8, crease: float = 0.8):
    """Inicializa las propiedades del objeto cortador segun calibre y tipo de corte."""
    global _UPDATING_CUTTER
    _UPDATING_CUTTER = True
    try:
        r_half = size_mm * 0.5
        ctr_obj["j3d_community_type"] = "CUTTER"
        ctr_obj["j3d_community_gem_cut"] = cut_key
        ctr_obj["j3d_community_gem_size"] = size_mm
        ctr_obj.j3d_community_cutter_segments = max(4, int(segments))
        ctr_obj.j3d_community_cutter_crease = max(0.0, min(1.0, float(crease)))

        ctr_obj.j3d_community_cutter_r_top = r_half * CUTTER_R_TABLE
        ctr_obj.j3d_community_cutter_z_top = size_mm * CUTTER_TOP_RATIO

        ctr_obj.j3d_community_cutter_r_table = r_half * CUTTER_R_TABLE
        ctr_obj.j3d_community_cutter_z_table = size_mm * CUTTER_TABLE_RATIO

        ctr_obj.j3d_community_cutter_r_girdle_top = r_half * CUTTER_R_GIRDLE
        ctr_obj.j3d_community_cutter_z_girdle_top = size_mm * CUTTER_GIRDLE_TOP_RATIO

        ctr_obj.j3d_community_cutter_r_girdle_bot = r_half * CUTTER_R_GIRDLE
        ctr_obj.j3d_community_cutter_z_girdle_bot = size_mm * CUTTER_GIRDLE_BOT_RATIO

        ctr_obj.j3d_community_cutter_r_seat = r_half * CUTTER_R_HOLE
        ctr_obj.j3d_community_cutter_z_seat = size_mm * CUTTER_SEAT_RATIO

        ctr_obj.j3d_community_cutter_r_hole_bot = r_half * CUTTER_R_HOLE
        ctr_obj.j3d_community_cutter_z_hole_bot = -size_mm * CUTTER_DEPTH_RATIO
    finally:
        _UPDATING_CUTTER = False


def rebuild_cutter_from_object_props(ctr_obj: bpy.types.Object, context=None):
    """Regenera la malla del cortador in-place a partir de sus propiedades de objeto."""
    cut_key = ctr_obj.get("j3d_community_gem_cut", "ROUND")
    segments = int(getattr(ctr_obj, "j3d_community_cutter_segments", 8))
    crease = float(getattr(ctr_obj, "j3d_community_cutter_crease", 0.8))

    levels_mm = [
        (float(getattr(ctr_obj, "j3d_community_cutter_r_top", 1.588)),        float(getattr(ctr_obj, "j3d_community_cutter_z_top", 2.880))),
        (float(getattr(ctr_obj, "j3d_community_cutter_r_table", 1.588)),      float(getattr(ctr_obj, "j3d_community_cutter_z_table", 1.050))),
        (float(getattr(ctr_obj, "j3d_community_cutter_r_girdle_top", 2.610)), float(getattr(ctr_obj, "j3d_community_cutter_z_girdle_top", 0.240))),
        (float(getattr(ctr_obj, "j3d_community_cutter_r_girdle_bot", 2.610)), float(getattr(ctr_obj, "j3d_community_cutter_z_girdle_bot", -0.130))),
        (float(getattr(ctr_obj, "j3d_community_cutter_r_seat", 1.220)),       float(getattr(ctr_obj, "j3d_community_cutter_z_seat", -1.330))),
        (float(getattr(ctr_obj, "j3d_community_cutter_r_hole_bot", 1.220)),   float(getattr(ctr_obj, "j3d_community_cutter_z_hole_bot", -5.050))),
    ]

    bm = build_cutter_bmesh_from_levels(cut_key, segments, crease, levels_mm, context)
    mesh = ctr_obj.data
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -- Utilidades de asociacion Gema <-> Cortador -----------------------------------

def find_cutter_for_gem(gem_obj: bpy.types.Object):
    """Busca el cortador asociado a una gema."""
    if not gem_obj:
        return None
    cutter_name = gem_obj.get("j3d_community_has_cutter", "")
    if cutter_name and cutter_name in bpy.data.objects:
        return bpy.data.objects[cutter_name]
    expected = "CTR_" + gem_obj.name
    if expected in bpy.data.objects:
        return bpy.data.objects[expected]
    return None


def rebuild_cutter_for_gem(
    cutter_obj: bpy.types.Object,
    cut_key: str,
    size_mm: float,
    context=None,
):
    """Regenera el mesh de un cortador al cambiar gema, preservando segmentos y crease."""
    segs = int(getattr(cutter_obj, "j3d_community_cutter_segments", 8))
    crease = float(getattr(cutter_obj, "j3d_community_cutter_crease", 0.8))
    init_cutter_object_props(cutter_obj, cut_key, size_mm, segments=segs, crease=crease)
    rebuild_cutter_from_object_props(cutter_obj, context)


# -- Operadores -------------------------------------------------------------------

class J3DComm_OT_add_cutter_to_gem(Operator):
    """Añadir cortador booleano procedural a la(s) gema(s) seleccionadas"""
    bl_idname = "j3d_community.add_cutter_to_gem"
    bl_label = "Añadir Cortador a Gema"
    bl_description = (
        "Genera un cortador de asiento procedural (5 zonas) para cada gema seleccionada. "
        "Permite ajuste interactivo en el panel inferior izquierdo (F9 / Ajustar última operación)."
    )
    bl_options = {'REGISTER', 'UNDO'}

    segments: IntProperty(  # type: ignore
        name="Segmentos",
        description="Subdivisiones radiales/facetas del cortador",
        default=8,
        min=4,
        max=64,
    )

    crease: FloatProperty(  # type: ignore
        name="Crease",
        description="Pliegue de aristas horizontales (Shift+E) para Subdivision Surface",
        default=0.8,
        min=0.0,
        max=1.0,
        step=10,
        precision=2,
    )

    # 1. Cima Superior
    r_top: FloatProperty(name="Radio Cima", default=1.588, min=0.001, precision=3, step=10)  # type: ignore
    z_top: FloatProperty(name="Z Cima", default=2.880, precision=3, step=10)  # type: ignore

    # 2. Tabla / Transicion Superior
    r_table: FloatProperty(name="Radio Tabla", default=1.588, min=0.001, precision=3, step=10)  # type: ignore
    z_table: FloatProperty(name="Z Tabla", default=1.050, precision=3, step=10)  # type: ignore

    # 3. Filetin Superior
    r_girdle_top: FloatProperty(name="Radio Filetín Sup.", default=2.610, min=0.001, precision=3, step=10)  # type: ignore
    z_girdle_top: FloatProperty(name="Z Filetín Sup.", default=0.240, precision=3, step=10)  # type: ignore

    # 4. Filetin Inferior
    r_girdle_bot: FloatProperty(name="Radio Filetín Inf.", default=2.610, min=0.001, precision=3, step=10)  # type: ignore
    z_girdle_bot: FloatProperty(name="Z Filetín Inf.", default=-0.130, precision=3, step=10)  # type: ignore

    # 5. Asiento Pabellon
    r_seat: FloatProperty(name="Radio Asiento", default=1.220, min=0.001, precision=3, step=10)  # type: ignore
    z_seat: FloatProperty(name="Z Asiento", default=-1.330, precision=3, step=10)  # type: ignore

    # 6. Perforacion Inferior
    r_hole_bot: FloatProperty(name="Radio Perforación", default=1.220, min=0.001, precision=3, step=10)  # type: ignore
    z_hole_bot: FloatProperty(name="Z Perforación", default=-5.050, precision=3, step=10)  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return (
            context.mode == 'OBJECT'
            and (
                any(obj.get("j3d_community_type") == "GEM" for obj in context.selected_objects)
                or (context.active_object and context.active_object.get("j3d_community_type") == "GEM")
            )
        )

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set:
        active_gem = next((o for o in context.selected_objects if o.get("j3d_community_type") == "GEM"), None)
        if not active_gem and context.active_object and context.active_object.get("j3d_community_type") == "GEM":
            active_gem = context.active_object

        if active_gem:
            size_mm = float(active_gem.get("j3d_community_gem_size", 5.0))
            r_half = size_mm * 0.5
            self.r_top = r_half * CUTTER_R_TABLE
            self.z_top = size_mm * CUTTER_TOP_RATIO

            self.r_table = r_half * CUTTER_R_TABLE
            self.z_table = size_mm * CUTTER_TABLE_RATIO

            self.r_girdle_top = r_half * CUTTER_R_GIRDLE
            self.z_girdle_top = size_mm * CUTTER_GIRDLE_TOP_RATIO

            self.r_girdle_bot = r_half * CUTTER_R_GIRDLE
            self.z_girdle_bot = size_mm * CUTTER_GIRDLE_BOT_RATIO

            self.r_seat = r_half * CUTTER_R_HOLE
            self.z_seat = size_mm * CUTTER_SEAT_RATIO

            self.r_hole_bot = r_half * CUTTER_R_HOLE
            self.z_hole_bot = -size_mm * CUTTER_DEPTH_RATIO

            self.segments = int(getattr(context.scene, "j3d_community_cutter_segments", 8))
            self.crease = float(getattr(context.scene, "j3d_community_cutter_crease", 0.8))

        return self.execute(context)

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "segments", text="Segmentos")
        col.prop(self, "crease", text="Crease (Shift+E)")

        layout.label(text="Perímetros Horizontales (Radio y Z):", icon='MESH_CIRCLE')

        rings_info = [
            ("1. Cima Superior (Extensión)", "r_top",        "z_top"),
            ("2. Tabla / Corona",            "r_table",      "z_table"),
            ("3. Filetín Superior",          "r_girdle_top", "z_girdle_top"),
            ("4. Filetín Inferior",          "r_girdle_bot", "z_girdle_bot"),
            ("5. Asiento (Pabellón)",        "r_seat",       "z_seat"),
            ("6. Perforación Inferior",      "r_hole_bot",   "z_hole_bot"),
        ]

        for label_txt, r_prop, z_prop in rings_info:
            pbox = layout.box()
            pbox.label(text=label_txt)
            row = pbox.row(align=True)
            row.prop(self, r_prop, text="Radio (mm)")
            row.prop(self, z_prop, text="Z (mm)")

    def execute(self, context: bpy.types.Context) -> set:
        gems = [o for o in context.selected_objects if o.get("j3d_community_type") == "GEM"]
        if not gems and context.active_object and context.active_object.get("j3d_community_type") == "GEM":
            gems = [context.active_object]

        if not gems:
            self.report({'WARNING'}, "Selecciona al menos una gema primero.")
            return {'CANCELLED'}

        custom_levels = [
            (self.r_top,        self.z_top),
            (self.r_table,      self.z_table),
            (self.r_girdle_top, self.z_girdle_top),
            (self.r_girdle_bot, self.z_girdle_bot),
            (self.r_seat,       self.z_seat),
            (self.r_hole_bot,   self.z_hole_bot),
        ]

        created = 0
        for gem_obj in gems:
            cut_key  = gem_obj.get("j3d_community_gem_cut", "ROUND")
            size_mm  = float(gem_obj.get("j3d_community_gem_size", 1.0))
            ctr_name = "CTR_" + gem_obj.name

            existing_ctr = find_cutter_for_gem(gem_obj)
            if existing_ctr:
                bm = build_cutter_bmesh_from_levels(cut_key, self.segments, self.crease, custom_levels, context)
                bm.to_mesh(existing_ctr.data)
                bm.free()
                existing_ctr.data.update()
                # Sincronizar propiedades de objeto
                existing_ctr.j3d_community_cutter_segments = self.segments
                existing_ctr.j3d_community_cutter_crease = self.crease
                existing_ctr.j3d_community_cutter_r_top = self.r_top
                existing_ctr.j3d_community_cutter_z_top = self.z_top
                existing_ctr.j3d_community_cutter_r_table = self.r_table
                existing_ctr.j3d_community_cutter_z_table = self.z_table
                existing_ctr.j3d_community_cutter_r_girdle_top = self.r_girdle_top
                existing_ctr.j3d_community_cutter_z_girdle_top = self.z_girdle_top
                existing_ctr.j3d_community_cutter_r_girdle_bot = self.r_girdle_bot
                existing_ctr.j3d_community_cutter_z_girdle_bot = self.z_girdle_bot
                existing_ctr.j3d_community_cutter_r_seat = self.r_seat
                existing_ctr.j3d_community_cutter_z_seat = self.z_seat
                existing_ctr.j3d_community_cutter_r_hole_bot = self.r_hole_bot
                existing_ctr.j3d_community_cutter_z_hole_bot = self.z_hole_bot
                created += 1
                continue

            mesh = create_cutter_mesh(
                cut_key=cut_key,
                name=ctr_name + "_Mesh",
                size_mm=size_mm,
                segments=self.segments,
                crease=self.crease,
                custom_levels=custom_levels,
                context=context,
            )

            ctr_obj = bpy.data.objects.new(ctr_name, mesh)
            context.collection.objects.link(ctr_obj)
            ctr_obj.location       = gem_obj.location.copy()
            ctr_obj.rotation_euler = gem_obj.rotation_euler.copy()
            ctr_obj.display_type   = 'WIRE'

            ctr_obj["j3d_community_type"] = "CUTTER"
            ctr_obj["j3d_community_cutter_for"] = gem_obj.name
            ctr_obj["j3d_community_gem_cut"] = cut_key
            ctr_obj["j3d_community_gem_size"] = size_mm
            ctr_obj.j3d_community_cutter_segments = self.segments
            ctr_obj.j3d_community_cutter_crease = self.crease
            ctr_obj.j3d_community_cutter_r_top = self.r_top
            ctr_obj.j3d_community_cutter_z_top = self.z_top
            ctr_obj.j3d_community_cutter_r_table = self.r_table
            ctr_obj.j3d_community_cutter_z_table = self.z_table
            ctr_obj.j3d_community_cutter_r_girdle_top = self.r_girdle_top
            ctr_obj.j3d_community_cutter_z_girdle_top = self.z_girdle_top
            ctr_obj.j3d_community_cutter_r_girdle_bot = self.r_girdle_bot
            ctr_obj.j3d_community_cutter_z_girdle_bot = self.z_girdle_bot
            ctr_obj.j3d_community_cutter_r_seat = self.r_seat
            ctr_obj.j3d_community_cutter_z_seat = self.z_seat
            ctr_obj.j3d_community_cutter_r_hole_bot = self.r_hole_bot
            ctr_obj.j3d_community_cutter_z_hole_bot = self.z_hole_bot

            gem_obj["j3d_community_has_cutter"] = ctr_name
            created += 1

        self.report({'INFO'}, f"{created} cortador(es) generado(s).")
        return {'FINISHED'}


class J3DComm_OT_reset_cutter_defaults(Operator):
    """Restablecer los 6 perimetros del cortador activo a sus proporciones estandar de joyeria"""
    bl_idname = "j3d_community.reset_cutter_defaults"
    bl_label = "Restablecer Cotas por Defecto"
    bl_description = "Restaura los 6 perimetros del cortador a las proporciones estandar de la gema"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        obj = context.active_object
        if not obj:
            return False
        return obj.get("j3d_community_type") == "CUTTER" or find_cutter_for_gem(obj) is not None

    def execute(self, context: bpy.types.Context) -> set:
        obj = context.active_object
        ctr_obj = obj if obj.get("j3d_community_type") == "CUTTER" else find_cutter_for_gem(obj)
        if not ctr_obj:
            self.report({'WARNING'}, "No se encontro cortador activo.")
            return {'CANCELLED'}

        cut_key = ctr_obj.get("j3d_community_gem_cut", "ROUND")
        size_mm = float(ctr_obj.get("j3d_community_gem_size", 1.0))
        segs = int(getattr(ctr_obj, "j3d_community_cutter_segments", 8))
        crease = float(getattr(ctr_obj, "j3d_community_cutter_crease", 0.8))

        init_cutter_object_props(ctr_obj, cut_key, size_mm, segments=segs, crease=crease)
        rebuild_cutter_from_object_props(ctr_obj, context)
        self.report({'INFO'}, f"Cortador {ctr_obj.name} restablecido a cotas estándar.")
        return {'FINISHED'}


class J3DComm_OT_add_cutters(Operator):
    """Aniadir Cortador Base"""
    bl_idname = "j3d_community.add_cutters"
    bl_label = "Aniadir Cortador"
    bl_description = "Anade un cortador booleano; si hay gemas seleccionadas las usa como referencia"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT'

    def execute(self, context: bpy.types.Context) -> set:
        if any(o.get("j3d_community_type") == "GEM" for o in context.selected_objects):
            return bpy.ops.j3d_community.add_cutter_to_gem()
        size_bu = mm_to_bu(3.0, context)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=size_bu * 0.5,
            depth=size_bu * 0.7,
            location=context.scene.cursor.location,
        )
        obj = context.active_object
        obj.name = "CTR_Base"
        obj.display_type = 'WIRE'
        init_cutter_object_props(obj, "ROUND", 3.0, 8, 0.8)
        self.report({'INFO'}, "Cortador base anadido (sin gema asociada).")
        return {'FINISHED'}


OBJECT_CUTTER_PROPS = (
    "j3d_community_cutter_segments",
    "j3d_community_cutter_crease",
    "j3d_community_cutter_r_top",
    "j3d_community_cutter_z_top",
    "j3d_community_cutter_r_table",
    "j3d_community_cutter_z_table",
    "j3d_community_cutter_r_girdle_top",
    "j3d_community_cutter_z_girdle_top",
    "j3d_community_cutter_r_girdle_bot",
    "j3d_community_cutter_z_girdle_bot",
    "j3d_community_cutter_r_seat",
    "j3d_community_cutter_z_seat",
    "j3d_community_cutter_r_hole_bot",
    "j3d_community_cutter_z_hole_bot",
)

classes = (
    J3DComm_OT_add_cutter_to_gem,
    J3DComm_OT_reset_cutter_defaults,
    J3DComm_OT_add_cutters,
)


def register():
    # Registrar propiedades parametricas en bpy.types.Object para edicion en vivo
    bpy.types.Object.j3d_community_cutter_segments = IntProperty(
        name="Segmentos",
        description="Subdivisiones radiales/facetas del cortador",
        default=8,
        min=4,
        max=64,
        update=update_cutter_object_props_callback,
    ) # type: ignore

    bpy.types.Object.j3d_community_cutter_crease = FloatProperty(
        name="Crease",
        description="Pliegue de aristas horizontales (Shift+E) para Subdivision Surface",
        default=0.8,
        min=0.0,
        max=1.0,
        step=10,
        precision=2,
        update=update_cutter_object_props_callback,
    ) # type: ignore

    # 1. Cima Superior
    bpy.types.Object.j3d_community_cutter_r_top = FloatProperty(
        name="Radio Cima",
        description="Radio del perimetro de la cima superior (mm)",
        default=1.588,
        min=0.001,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore
    bpy.types.Object.j3d_community_cutter_z_top = FloatProperty(
        name="Z Cima",
        description="Posicion Z de la cima superior respecto al centro Z=0 (mm)",
        default=2.880,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore

    # 2. Tabla / Transicion Superior
    bpy.types.Object.j3d_community_cutter_r_table = FloatProperty(
        name="Radio Tabla",
        description="Radio del perimetro a nivel de la tabla (mm)",
        default=1.588,
        min=0.001,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore
    bpy.types.Object.j3d_community_cutter_z_table = FloatProperty(
        name="Z Tabla",
        description="Posicion Z a nivel de tabla respecto al centro Z=0 (mm)",
        default=1.050,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore

    # 3. Filetin Superior
    bpy.types.Object.j3d_community_cutter_r_girdle_top = FloatProperty(
        name="Radio Filetin Sup.",
        description="Radio del perimetro superior del filetin (mm)",
        default=2.610,
        min=0.001,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore
    bpy.types.Object.j3d_community_cutter_z_girdle_top = FloatProperty(
        name="Z Filetin Sup.",
        description="Posicion Z superior del filetin respecto al centro Z=0 (mm)",
        default=0.240,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore

    # 4. Filetin Inferior
    bpy.types.Object.j3d_community_cutter_r_girdle_bot = FloatProperty(
        name="Radio Filetin Inf.",
        description="Radio del perimetro inferior del filetin (mm)",
        default=2.610,
        min=0.001,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore
    bpy.types.Object.j3d_community_cutter_z_girdle_bot = FloatProperty(
        name="Z Filetin Inf.",
        description="Posicion Z inferior del filetin respecto al centro Z=0 (mm)",
        default=-0.130,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore

    # 5. Asiento Pabellon
    bpy.types.Object.j3d_community_cutter_r_seat = FloatProperty(
        name="Radio Asiento",
        description="Radio del cono de asiento / pabellon (mm)",
        default=1.220,
        min=0.001,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore
    bpy.types.Object.j3d_community_cutter_z_seat = FloatProperty(
        name="Z Asiento",
        description="Posicion Z del asiento respecto al centro Z=0 (mm)",
        default=-1.330,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore

    # 6. Perforacion Inferior
    bpy.types.Object.j3d_community_cutter_r_hole_bot = FloatProperty(
        name="Radio Perforacion",
        description="Radio del canal inferior de perforacion (mm)",
        default=1.220,
        min=0.001,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore
    bpy.types.Object.j3d_community_cutter_z_hole_bot = FloatProperty(
        name="Z Perforacion",
        description="Posicion Z del fondo de perforacion respecto al centro Z=0 (mm)",
        default=-5.050,
        step=10,
        precision=3,
        update=update_cutter_object_props_callback,
    ) # type: ignore

    for cls in classes:
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
            except Exception:
                pass
        else:
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass

    for prop in OBJECT_CUTTER_PROPS:
        if hasattr(bpy.types.Object, prop):
            try:
                delattr(bpy.types.Object, prop)
            except Exception:
                pass
