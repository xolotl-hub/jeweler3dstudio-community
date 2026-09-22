"""
Jeweler 3D Studio - Core Ring Shank, Size and Profile Module
Provides:
  - US Ring Size chart (inner diameter, mm)
  - Bezier curve / cylinder mesh reference for ring sizing
  - 8 parametric ring profile cross-sections (sweep BMesh)
  - Subdivision Surface support with automatic Edge Crease (Shift+E) on sharp corners
  - Orientation selector (Top XY, Front XZ, Side YZ)
  - Operators J3DComm_OT_create_ring_size and J3DComm_OT_create_ring_profile

Scale standard: 1 BU = 1 mm direct jewelry modeling.
Inner diameter = US ring size specification (touching-finger surface).
"""

from typing import Dict, Tuple, List, Set
import math
import bpy
import bmesh
from bpy.props import EnumProperty, FloatProperty, IntProperty, BoolProperty
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from .units import mm_to_bu

# US Ring Size Chart (US Size -> Inner Diameter in mm)
US_RING_SIZES: Dict[str, float] = {
    "3.0": 14.05, "3.5": 14.45, "4.0": 14.86, "4.5": 15.27,
    "5.0": 15.70, "5.5": 16.10, "6.0": 16.51, "6.5": 16.92,
    "7.0": 17.32,  # Default
    "7.5": 17.73, "8.0": 18.14, "8.5": 18.54, "9.0": 18.95,
    "9.5": 19.35, "10.0": 19.76, "10.5": 20.17, "11.0": 20.57,
    "11.5": 20.98, "12.0": 21.39, "12.5": 21.79,
    "13.0": 22.20, "13.5": 22.61,
}

US_SIZE_ITEMS: List[Tuple[str, str, str]] = [
    (k, f"US {k} ({v:.2f} mm)", f"US Size {k} - Inner diameter {v:.2f} mm")
    for k, v in US_RING_SIZES.items()
]

GEOMETRY_TYPE_ITEMS: List[Tuple[str, str, str, str, int]] = [
    ("CURVE",    "Bezier Curve",  "Generate 3D circular Bezier curve", "CURVE_NCIRCLE", 0),
    ("CYLINDER", "Mesh Cylinder", "Generate 3D cylinder reference",     "MESH_CYLINDER", 1),
]

ORIENTATION_ITEMS: List[Tuple[str, str, str, str, int]] = [
    ("TOP",   "Top (XY)",   "Ring lying flat in horizontal XY plane (finger along Z)", "ORIENTATION_GLOBAL", 0),
    ("FRONT", "Front (XZ)", "Ring standing upright seen from front in XZ plane (finger along Y)", "ORIENTATION_VIEW",   1),
    ("SIDE",  "Side (YZ)",  "Ring standing upright seen from side in YZ plane (finger along X)",  "ORIENTATION_LOCAL",  2),
]


def _get_orientation_euler(orientation_key: str) -> Tuple[float, float, float]:
    """Calculates Euler rotation (radians) for the selected orientation."""
    if orientation_key == "FRONT":
        return (math.radians(90.0), 0.0, 0.0)
    elif orientation_key == "SIDE":
        return (0.0, math.radians(90.0), 0.0)
    return (0.0, 0.0, 0.0)


# 8 Ring Profile Definitions
# Normalized cross-section: u_norm [0=inner..1=outer], v_norm [-0.5..0.5 = width]
# Actual 3D: r = inner_radius + u_norm * height_mm,  z = v_norm * width_mm

RING_PROFILE_ITEMS: List[Tuple[str, str, str, int]] = [
    ("MEDIA_CANA", "Half Round",  "Flat inner edge, domed outer - classic half-round",         0),
    ("PLANO",      "Flat",        "Flat rectangular cross-section - modern minimalist",         1),
    ("CONFORT",    "Comfort Fit", "Flat outside, comfort domed inside - comfortable to wear",  2),
    ("OVAL",       "Oval",        "Symmetric elliptical cross-section",                         3),
    ("KNIFE_EDGE", "Knife Edge",  "Sharp knife-edge outer ridge",                               4),
    ("EURO_SHANK", "Euro Shank",  "Flat exterior shape with elegant corner bevels",             5),
    ("BEVELED",    "Beveled",     "Flat top with 45-degree angled side bevels",                 6),
    ("CONCAVE",    "Concave",     "Recessed concave center groove",                             7),
]


def _make_profile_media_cana(n: int = 8) -> List[Tuple[float, float]]:
    """Media Cana: flat inner edge, domed outer. Classic half-round."""
    pts = [(0.0, -0.5), (0.0, 0.5)]
    seg = max(2, n)
    for i in range(1, seg):
        t = i / seg
        pts.append((math.sin(math.pi * t), 0.5 - t))
    return pts


def _make_profile_plano(n: int = 1) -> List[Tuple[float, float]]:
    """Plano: pure rectangle."""
    return [(0.0, -0.5), (0.0, 0.5), (1.0, 0.5), (1.0, -0.5)]


def _make_profile_confort(n: int = 8) -> List[Tuple[float, float]]:
    """Confort: flat outer, inner has gentle comfort dome (no sharp inner edges)."""
    pts = [(1.0, -0.5), (1.0, 0.5)]
    pts.append((0.10, 0.5))
    seg = max(2, n)
    for i in range(1, seg):
        t = i / seg
        u = 0.10 * math.sin(math.pi * t)
        pts.append((u, 0.5 - t))
    pts.append((0.10, -0.5))
    return pts


def _make_profile_oval(n: int = 16) -> List[Tuple[float, float]]:
    """Oval: full ellipse cross-section. Center at (0.5, 0)."""
    pts = []
    seg = max(4, n)
    for i in range(seg):
        angle = 2.0 * math.pi * i / seg
        u = 0.5 + 0.5 * math.cos(angle)
        v = 0.5 * math.sin(angle)
        pts.append((u, v))
    return pts


def _make_profile_knife_edge(n: int = 1) -> List[Tuple[float, float]]:
    """Filo (Knife Edge): triangular - flat inner, sharp outer ridge at center."""
    return [(0.0, -0.5), (0.0, 0.5), (1.0, 0.0)]


def _make_profile_euro_shank(n: int = 1) -> List[Tuple[float, float]]:
    """Aro Europeo: square with small chamfers on outer corners."""
    c = 0.10
    return [
        (0.0,       -0.5),
        (0.0,        0.5),
        (1.0 - c,    0.5),
        (1.0,        0.5 - c),
        (1.0,       -(0.5 - c)),
        (1.0 - c,   -0.5),
    ]


def _make_profile_beveled(n: int = 1) -> List[Tuple[float, float]]:
    """Biseado: rectangle with outer corner bevels."""
    b = 0.18
    return [
        (0.0,      -0.5),
        (0.0,       0.5),
        (1.0 - b,   0.5),
        (1.0,       0.5 - b),
        (1.0,      -(0.5 - b)),
        (1.0 - b,  -0.5),
    ]


def _make_profile_concave(n: int = 8) -> List[Tuple[float, float]]:
    """Concavo: concave outer surface (grooved channel)."""
    pts = [(0.0, -0.5), (0.0, 0.5)]
    pts.append((1.0, 0.5))
    seg = max(2, n)
    for i in range(1, seg):
        t = i / seg
        u = 1.0 - 0.35 * math.sin(math.pi * t)
        pts.append((u, 0.5 - t))
    pts.append((1.0, -0.5))
    return pts


_PROFILE_FNS = {
    "MEDIA_CANA": _make_profile_media_cana,
    "PLANO":      _make_profile_plano,
    "CONFORT":    _make_profile_confort,
    "OVAL":       _make_profile_oval,
    "KNIFE_EDGE": _make_profile_knife_edge,
    "EURO_SHANK": _make_profile_euro_shank,
    "BEVELED":    _make_profile_beveled,
    "CONCAVE":    _make_profile_concave,
}


def _find_sharp_corner_indices(pts: List[Tuple[float, float]], threshold_cos: float = 0.866) -> List[int]:
    """
    Identifica los indices de vertices en el perfil que representan esquinas vivas
    (cambio de direccion > ~30 grados entre segmentos adyacentes).
    """
    M = len(pts)
    if M <= 4:
        return list(range(M))
    
    corner_indices = []
    for j in range(M):
        p_prev = pts[(j - 1) % M]
        p_curr = pts[j]
        p_next = pts[(j + 1) % M]
        
        v1_x = p_curr[0] - p_prev[0]
        v1_y = p_curr[1] - p_prev[1]
        v2_x = p_next[0] - p_curr[0]
        v2_y = p_next[1] - p_curr[1]
        
        len1 = math.hypot(v1_x, v1_y)
        len2 = math.hypot(v2_x, v2_y)
        if len1 < 1e-6 or len2 < 1e-6:
            continue
        
        cos_ang = (v1_x * v2_x + v1_y * v2_y) / (len1 * len2)
        if cos_ang < threshold_cos:
            corner_indices.append(j)
            
    return corner_indices


# Geometry Builders

def create_ring_bezier_curve(name: str, radius: float) -> bpy.types.Curve:
    """Crea curva Bezier circular 3D (referencia de talla)."""
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
    """Crea cilindro de referencia de talla con BMesh."""
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
    """
    Genera malla 3D completa sweepando la seccion transversal
    alrededor del circulo interior (radio = Talla US diametro / 2).

    inner_radius_mm : radio INTERIOR - define la talla US (superficie del dedo).
    width_mm        : ancho del aro en eje del dedo.
    height_mm       : grosor radial del metal (crece hacia afuera).
    n_ring          : numero de divisiones radiales alrededor del aro.
    profile_segments: resolucion de subdivision en secciones curvas del perfil.
    crease_value    : pliegue (Shift+E) asignado a las aristas longitudinales de esquinas vivas.
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


# Operators

class J3DComm_OT_create_ring_size(Operator, AddObjectHelper):
    """Generates base ring sizing geometry (Curve or Cylinder)"""
    bl_idname = "j3d_community.create_ring_size"
    bl_label = "Create Ring Size"
    bl_options = {'REGISTER', 'UNDO'}

    us_size: EnumProperty(
        name="US Size",
        description="Standard US ring size selection",
        items=US_SIZE_ITEMS,
        default="7.0"
    )  # type: ignore

    geometry_type: EnumProperty(
        name="Geometry Type",
        description="Geometry type to generate",
        items=GEOMETRY_TYPE_ITEMS,
        default="CURVE"
    )  # type: ignore

    orientation: EnumProperty(
        name="Orientation",
        description="Orientation plane for ring creation",
        items=ORIENTATION_ITEMS,
        default="FRONT"
    )  # type: ignore

    cylinder_depth: FloatProperty(
        name="Cylinder Depth (mm)",
        description="Depth/width of reference cylinder in mm",
        default=2.0,
        min=0.5,
        max=20.0,
        step=10,
        precision=2
    )  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT'

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "us_size")
        layout.prop(self, "geometry_type")
        layout.prop(self, "orientation")
        if self.geometry_type == 'CYLINDER':
            layout.prop(self, "cylinder_depth")
        layout.separator()
        layout.prop(self, "align", text="Alignment")
        layout.prop(self, "location", text="Location")
        layout.prop(self, "rotation", text="Rotation")

    def execute(self, context: bpy.types.Context) -> set:
        dia_mm = US_RING_SIZES.get(self.us_size, 17.32)
        radius_mm = dia_mm / 2.0
        obj_name = f"Ring_Size_US_{self.us_size}"

        if self.geometry_type == 'CURVE':
            obdata = create_ring_bezier_curve(f"{obj_name}_Curve", radius_mm)
        else:
            obdata = create_ring_cylinder_mesh(
                f"{obj_name}_Mesh", radius_mm, self.cylinder_depth
            )

        obj = object_data_add(context, obdata, operator=self)
        if all(abs(r) < 1e-5 for r in self.rotation):
            obj.rotation_euler = _get_orientation_euler(self.orientation)
        obj.name = obj_name
        obj["j3d_type"] = "RING_SIZE"
        obj["j3d_us_size"] = self.us_size
        obj["j3d_diameter_mm"] = dia_mm
        obj["j3d_radius_mm"] = radius_mm
        obj["j3d_orientation"] = self.orientation
        self.report(
            {'INFO'},
            f"Ring Size US {self.us_size} ({dia_mm:.2f} mm) created in {self.orientation}: {obj_name}"
        )
        return {'FINISHED'}


class J3DComm_OT_create_ring_profile(Operator, AddObjectHelper):
    """Creates complete 3D ring shank with parametric cross-section profile and subdivision crease"""
    bl_idname = "j3d_community.create_ring_profile"
    bl_label = "Create Ring Shank"
    bl_options = {'REGISTER', 'UNDO'}

    us_size: EnumProperty(
        name="US Size",
        description="Defines INNER diameter of ring (finger touching surface)",
        items=US_SIZE_ITEMS, default="7.0"
    )  # type: ignore

    profile_type: EnumProperty(
        name="Profile",
        description="Metal cross-section shape",
        items=RING_PROFILE_ITEMS, default="MEDIA_CANA"
    )  # type: ignore

    orientation: EnumProperty(
        name="Orientation",
        description="Orientation plane for ring creation",
        items=ORIENTATION_ITEMS,
        default="FRONT"
    )  # type: ignore

    width_mm: FloatProperty(
        name="Width (mm)",
        description="Ring width along finger axis in mm",
        default=3.0, min=1.0, max=20.0, step=10, precision=2
    )  # type: ignore

    height_mm: FloatProperty(
        name="Thickness (mm)",
        description="Radial metal thickness in mm (grows outwards from inner diameter)",
        default=1.5, min=0.3, max=10.0, step=10, precision=2
    )  # type: ignore

    radial_segments: IntProperty(
        name="Radial Segments",
        description="Number of circumferential divisions around the ring",
        default=16, min=8, max=256
    )  # type: ignore

    profile_segments: IntProperty(
        name="Profile Resolution",
        description="Number of subdivisions on curved profile sections",
        default=2, min=2, max=64
    )  # type: ignore

    use_subsurf: BoolProperty(
        name="Subdivision Surface",
        description="Add Subdivision Surface modifier",
        default=True
    )  # type: ignore

    subsurf_levels: IntProperty(
        name="Subsurf Level",
        description="Subdivision level for viewport and render",
        default=2, min=1, max=5
    )  # type: ignore

    crease_value: FloatProperty(
        name="Edge Crease",
        description="Crease sharpness (Shift+E) on sharp corners (0.8 gives subtle polished rounding)",
        default=0.8, min=0.0, max=1.0, step=5, precision=2
    )  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'OBJECT'

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "us_size")
        layout.prop(self, "profile_type")
        layout.prop(self, "orientation")
        layout.separator()
        layout.prop(self, "width_mm")
        layout.prop(self, "height_mm")
        layout.separator()
        layout.prop(self, "radial_segments")
        layout.prop(self, "profile_segments")
        layout.separator()
        layout.prop(self, "use_subsurf")
        if self.use_subsurf:
            layout.prop(self, "subsurf_levels")
            layout.prop(self, "crease_value")
        layout.separator()
        layout.prop(self, "align", text="Alignment")
        layout.prop(self, "location", text="Location")
        layout.prop(self, "rotation", text="Rotation")

    def execute(self, context: bpy.types.Context) -> set:
        inner_dia_mm = US_RING_SIZES.get(self.us_size, 17.32)
        inner_radius_mm = inner_dia_mm / 2.0  # INNER, touches finger

        obj_name = (
            f"Ring_US{self.us_size}_{self.profile_type}"
            f"_{self.width_mm:.1f}x{self.height_mm:.1f}mm"
        )
        mesh = create_ring_profile_mesh(
            name=obj_name + "_Mesh",
            inner_radius_mm=inner_radius_mm,
            width_mm=self.width_mm,
            height_mm=self.height_mm,
            profile_key=self.profile_type,
            n_ring=self.radial_segments,
            profile_segments=self.profile_segments,
            crease_value=self.crease_value if self.use_subsurf else 0.0,
        )

        obj = object_data_add(context, mesh, operator=self)
        if all(abs(r) < 1e-5 for r in self.rotation):
            obj.rotation_euler = _get_orientation_euler(self.orientation)
        obj.name = obj_name
        obj["j3d_type"] = "RING_PROFILE"
        obj["j3d_us_size"] = self.us_size
        obj["j3d_inner_dia_mm"] = inner_dia_mm
        obj["j3d_profile"] = self.profile_type
        obj["j3d_orientation"] = self.orientation
        obj["j3d_width_mm"] = self.width_mm
        obj["j3d_height_mm"] = self.height_mm
        obj["j3d_radial_segments"] = self.radial_segments
        obj["j3d_profile_segments"] = self.profile_segments
        obj["j3d_crease"] = self.crease_value

        if self.use_subsurf:
            subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            subsurf.levels = self.subsurf_levels
            subsurf.render_levels = max(self.subsurf_levels, 2)

        self.report(
            {'INFO'},
            f"Ring Shank US {self.us_size} | {self.profile_type} | "
            f"Inner Dia {inner_dia_mm:.2f}mm | {self.orientation}"
        )
        return {'FINISHED'}


# Registration

classes = (
    J3DComm_OT_create_ring_size,
    J3DComm_OT_create_ring_profile,
)


def register():
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
