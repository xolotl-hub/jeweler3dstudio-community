"""
Jeweler 3D Studio — Pavé: Camisa de Cara (Face Shirt)
======================================================
Técnica: selección de caras o pintura de pesos → camisa offset → distribución Poisson 3D + BVH.

Flujo de 3 pasos:
  1. J3DComm_OT_pave_enter_zone   — entra al modo de selección (Face Select o Weight Paint)
  2. J3DComm_OT_pave_create_shirt — extrae la zona y genera la malla camisa flotante
  3. J3DComm_OT_pave_distribute   — Poisson Disk 3D sobre la camisa + coloca gemas orientadas
"""

from __future__ import annotations

import math
import random
from typing import List, Optional, Set, Tuple

try:
    import bpy
    import bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        StringProperty,
    )
    from bpy.types import Operator
    _IN_BLENDER = True
except ModuleNotFoundError:
    _IN_BLENDER = False
    # Headless / unit-test environment — stubs so the module can be imported
    class Operator:  # type: ignore[no-redef]
        bl_idname = ""
        bl_label = ""
        bl_description = ""
        bl_options: set = set()
    def EnumProperty(**kwargs): return None   # type: ignore[misc]  # noqa: E302
    def FloatProperty(**kwargs): return None  # type: ignore[misc]  # noqa: E302
    def IntProperty(**kwargs): return None    # type: ignore[misc]  # noqa: E302
    def BoolProperty(**kwargs): return None   # type: ignore[misc]  # noqa: E302
    def StringProperty(**kwargs): return None # type: ignore[misc]  # noqa: E302

from ._base import PaveStrategy

# ── Constants ─────────────────────────────────────────────────────────────────

SHIRT_OFFSET_MM   = 0.05   # outward offset in mm-space (applied as BU * mm_scale)
WEIGHT_THRESHOLD  = 0.5    # vertex-group weight cutoff for paint mode
VGROUP_NAME       = "j3d_pave_zone"
SHIRT_SUFFIX      = "_PaveShirt"
DIST_SUFFIX       = "_PaveDist"


# ── Zone selection mode enum ───────────────────────────────────────────────────

ZONE_MODE_ITEMS = [
    ("FACE_SELECT", "Selección de Caras",
     "Selecciona caras en Edit Mode para definir la zona pavé"),
    ("WEIGHT_PAINT", "Pintura de Pesos",
     "Pinta la zona pavé con Weight Paint (rojo = zona activa)"),
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _mm_to_bu(mm: float) -> float:
    """Convert millimetres to Blender units (scene unit scale)."""
    scene = bpy.context.scene
    unit_scale = scene.unit_settings.scale_length if scene else 0.001
    return mm * unit_scale


def _extract_shirt(
    source_obj: bpy.types.Object,
    zone_mode: str,
    offset_bu: float,
) -> Optional[bpy.types.Object]:
    """
    Extract the painted/selected faces from *source_obj* and return a new
    object — the 'camisa' — that offsets those faces along their normals.

    Returns None if no faces qualify.
    """
    if source_obj is None or source_obj.type != 'MESH':
        return None

    # ---- Build BMesh from source -------------------------------------------
    src_mesh = source_obj.data
    bm = bmesh.new()
    bm.from_mesh(src_mesh)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    selected_faces = []

    if zone_mode == "FACE_SELECT":
        # Cara-selección: las caras marcadas en Edit Mode quedan en select=True
        selected_faces = [f for f in bm.faces if f.select]

    elif zone_mode == "WEIGHT_PAINT":
        # Pintura: buscar vertex group j3d_pave_zone
        vgroup_idx = source_obj.vertex_groups.find(VGROUP_NAME)
        if vgroup_idx < 0:
            bm.free()
            return None

        deform_layer = bm.verts.layers.deform.active
        if deform_layer is None:
            bm.free()
            return None

        # Una cara pertenece a la zona si todos sus vértices superan el umbral
        for face in bm.faces:
            weights = [v[deform_layer].get(vgroup_idx, 0.0) for v in face.verts]
            if weights and min(weights) >= WEIGHT_THRESHOLD:
                selected_faces.append(face)

    if not selected_faces:
        bm.free()
        return None

    # ---- Build a new BMesh with only the selected faces --------------------
    bm_shirt = bmesh.new()
    vert_map: dict = {}

    for face in selected_faces:
        new_verts = []
        for v in face.verts:
            if v.index not in vert_map:
                nv = bm_shirt.verts.new(v.co.copy())
                vert_map[v.index] = nv
            new_verts.append(vert_map[v.index])
        try:
            bm_shirt.faces.new(new_verts)
        except ValueError:
            pass  # duplicate face — skip

    bm_shirt.normal_update()

    # ---- Subdivide con suavizado para respetar curvatura --------------------
    # smooth=1.0 interpola a lo largo de las normales de vértice
    bmesh.ops.subdivide_edges(
        bm_shirt,
        edges=list(bm_shirt.edges),
        cuts=4,
        use_grid_fill=True,
        smooth=1.0,
    )
    bm_shirt.normal_update()

    # ---- Shrinkwrap: snap a la superficie original -------------------------
    # Empujamos cada vértice HACIA ADENTRO antes del snap para que
    # find_nearest los lleve a la curvatura real (no se queden en el plano).
    bm_src_for_bvh = bmesh.new()
    bm_src_for_bvh.from_mesh(src_mesh)
    src_bvh = BVHTree.FromBMesh(bm_src_for_bvh)
    bm_shirt.verts.ensure_lookup_table()
    bm_shirt.normal_update()  # normales antes del push
    INWARD = offset_bu * 4   # empuje hacia adentro (4x el offset)
    for v in bm_shirt.verts:
        v.co -= v.normal * INWARD  # mover hacia el interior del objeto
    for v in bm_shirt.verts:
        loc, norm, _, _ = src_bvh.find_nearest(v.co)
        if loc is not None and norm is not None:
            v.co = loc + norm.normalized() * offset_bu
    bm_src_for_bvh.free()

    # Normales coherentes: todas apuntando hacia fuera
    bmesh.ops.recalc_face_normals(bm_shirt, faces=list(bm_shirt.faces))
    bm_shirt.normal_update()

    # ---- Create mesh + object -----------------------------------------------
    shirt_mesh = bpy.data.meshes.new(source_obj.name + SHIRT_SUFFIX + "_Mesh")
    bm_shirt.to_mesh(shirt_mesh)
    bm_shirt.free()
    bm.free()

    shirt_obj = bpy.data.objects.new(source_obj.name + SHIRT_SUFFIX, shirt_mesh)
    shirt_obj.matrix_world = source_obj.matrix_world.copy()
    shirt_obj["j3d_type"]       = "PAVE_SHIRT"
    shirt_obj["j3d_source"]     = source_obj.name
    shirt_obj["j3d_zone_mode"]  = zone_mode

    bpy.context.collection.objects.link(shirt_obj)
    return shirt_obj


def _poisson_disk_on_mesh(
    shirt_obj: bpy.types.Object,
    gem_size_mm: float,
    spacing_mm: float,
    max_attempts: int = 30,
) -> List[Tuple[Vector, Vector]]:
    """
    Poisson Disk Sampling 3D sobre la superficie de *shirt_obj*.

    Retorna lista de (position_world, normal_world) para cada gema.
    La distancia mínima entre centros = gem_size_mm + spacing_mm (en BU).
    """
    min_dist_bu = _mm_to_bu(gem_size_mm + spacing_mm)

    shirt_mesh = shirt_obj.data
    mw = shirt_obj.matrix_world
    mw3 = mw.to_3x3()  # para transformar normales a world space

    # ---- Sample random points on the shirt surface -------------------------
    bm = bmesh.new()
    bm.from_mesh(shirt_mesh)
    bm.faces.ensure_lookup_table()

    # Weighted face area list for uniform sampling
    areas = [f.calc_area() for f in bm.faces]
    total_area = sum(areas)
    if total_area < 1e-12:
        bm.free()
        return []

    placed: List[Tuple[Vector, Vector]] = []

    def _random_point_on_face(face: bmesh.types.BMFace) -> Vector:
        """Uniform random point inside a polygon via fan triangulation."""
        verts = [v.co.copy() for v in face.verts]
        if len(verts) == 3:
            r1, r2 = random.random(), random.random()
            if r1 + r2 > 1.0:
                r1, r2 = 1.0 - r1, 1.0 - r2
            return verts[0] + r1 * (verts[1] - verts[0]) + r2 * (verts[2] - verts[0])
        else:
            pivoto = verts[0]
            tris = [(pivoto, verts[i], verts[i + 1]) for i in range(1, len(verts) - 1)]
            tri_areas = [
                0.5 * (b - a).cross(c - a).length for a, b, c in tris
            ]
            total = sum(tri_areas) or 1.0
            rnd = random.uniform(0, total)
            cumul = 0.0
            chosen = tris[0]
            for tri, ta in zip(tris, tri_areas):
                cumul += ta
                if rnd <= cumul:
                    chosen = tri
                    break
            a, b, c = chosen
            r1, r2 = random.random(), random.random()
            if r1 + r2 > 1.0:
                r1, r2 = 1.0 - r1, 1.0 - r2
            return a + r1 * (b - a) + r2 * (c - a)

    # ---- Poisson dart-throwing -------------------------------------------
    cumul = 0.0
    cum_areas = []
    for a in areas:
        cumul += a
        cum_areas.append(cumul)

    def _pick_random_face() -> bmesh.types.BMFace:
        rnd = random.uniform(0, total_area)
        lo, hi = 0, len(cum_areas) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cum_areas[mid] < rnd:
                lo = mid + 1
            else:
                hi = mid
        return bm.faces[lo]

    max_samples = int(total_area / (math.pi * (min_dist_bu / 2) ** 2)) * 3
    max_samples = max(100, min(max_samples, 8000))

    for _ in range(max_samples):
        face = _pick_random_face()
        local_pt = _random_point_on_face(face)
        world_pt = mw @ local_pt

        # Conflict check en world space
        too_close = any(
            (world_pt - p).length < min_dist_bu for p, _ in placed
        )
        if too_close:
            continue

        # Usar la normal de la cara directamente (siempre coherente y normalizada)
        local_nrm = face.normal.copy()
        if local_nrm.length < 1e-6:
            continue

        world_pos = mw @ local_pt
        world_nrm = (mw3 @ local_nrm).normalized()
        placed.append((world_pos, world_nrm))

    bm.free()
    return placed


# ── Strategy class ─────────────────────────────────────────────────────────────

class FaceShirtStrategy(PaveStrategy):
    """Camisa de Cara: face/paint selection → offset shirt → Poisson + BVH."""

    def create_shirt(
        self,
        context: bpy.types.Context,
        source_obj: bpy.types.Object,
        zone_mode: str = "FACE_SELECT",
    ) -> Optional[bpy.types.Object]:
        offset_bu = _mm_to_bu(SHIRT_OFFSET_MM)
        return _extract_shirt(source_obj, zone_mode, offset_bu)

    def create_distribution(
        self,
        context: bpy.types.Context,
        shirt_obj: bpy.types.Object,
        gem_size_mm: float = 1.5,
        spacing_mm: float = 0.2,
        create_cutters: bool = True,
    ) -> Set[str]:
        from ..gems import create_gem_mesh, get_or_create_gem_material

        points = _poisson_disk_on_mesh(shirt_obj, gem_size_mm, spacing_mm)
        if not points:
            return {'CANCELLED'}

        placed_objs = []
        gem_mesh = create_gem_mesh(
            cut_key="ROUND",
            name=f"PaveGem_{gem_size_mm:.1f}mm_Mesh",
            size_mm=gem_size_mm,
            context=context,
        )
        mat = get_or_create_gem_material("DIAMOND")

        cutter_mesh = None
        if create_cutters:
            try:
                from ..cutters import create_cutter_mesh
                cutter_mesh = create_cutter_mesh(
                    cut_key="ROUND",
                    name=f"PaveCutter_{gem_size_mm:.1f}mm_Mesh",
                    size_mm=gem_size_mm,
                    context=context,
                )
            except Exception:
                cutter_mesh = None

        for pos, nrm in points:
            obj = bpy.data.objects.new(f"PaveGem_{gem_size_mm:.1f}mm", gem_mesh)
            context.collection.objects.link(obj)

            # ---- Orientación correcta: Z local apunta a lo largo de la normal ----
            # Construir base ortonormal (ONB) con nrm como eje Z
            from mathutils import Matrix
            z = nrm.normalized()
            # Vector de referencia arbitrario no paralelo a z
            ref = Vector((0.0, 0.0, 1.0)) if abs(z.z) < 0.9 else Vector((0.0, 1.0, 0.0))
            x = ref.cross(z).normalized()   # eje X tangente
            y = z.cross(x).normalized()     # eje Y bitangente (right-hand)

            # Columnas de la matriz de rotación = ejes locales en world space
            rot = Matrix((
                (x.x, y.x, z.x, 0.0),
                (x.y, y.y, z.y, 0.0),
                (x.z, y.z, z.z, 0.0),
                (0.0, 0.0, 0.0, 1.0),
            ))
            obj.matrix_world = Matrix.Translation(pos) @ rot

            obj["j3d_type"]    = "GEM"
            obj["j3d_gem_cut"] = "ROUND"
            obj["j3d_gem_stone"] = "DIAMOND"
            obj["j3d_gem_size"] = gem_size_mm
            obj["j3d_pave_shirt"] = shirt_obj.name

            if not obj.data.materials:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat

            placed_objs.append(obj)

            # Emparejar con cortador booleano (asiento y canal de luz)
            if create_cutters and cutter_mesh:
                cutter_obj = bpy.data.objects.new(f"PaveCutter_{gem_size_mm:.1f}mm", cutter_mesh)
                context.collection.objects.link(cutter_obj)
                cutter_obj.matrix_world = obj.matrix_world.copy()
                cutter_obj["j3d_type"] = "CUTTER"
                cutter_obj["j3d_source_gem"] = obj.name
                cutter_obj["j3d_pave_shirt"] = shirt_obj.name
                cutter_obj.display_type = 'WIRE'
                placed_objs.append(cutter_obj)

        # Parent all gems & cutters to the shirt for clean hierarchy
        for o in placed_objs:
            o.parent = shirt_obj

        return {'FINISHED'}


# ── Operators — los 3 botones ─────────────────────────────────────────────────

class J3DComm_OT_pave_enter_zone(Operator):
    """Entra al modo de selección de zona pavé (Face Select o Weight Paint)."""
    bl_idname = "j3d_community.pave_enter_zone"
    bl_label   = "Pintado / Selección"
    bl_description = (
        "Face Select: selecciona caras en Edit Mode para definir la zona pavé.\n"
        "Weight Paint: pinta la zona con rojo (peso ≥ 0.5 = activo)"
    )
    bl_options = {'REGISTER', 'UNDO'}

    zone_mode: EnumProperty(
        name="Modo de zona",
        items=ZONE_MODE_ITEMS,
        default="FACE_SELECT",
    )

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def execute(self, context):
        obj = context.active_object

        if self.zone_mode == "FACE_SELECT":
            bpy.ops.object.mode_set(mode='EDIT')
            context.tool_settings.mesh_select_mode = (False, False, True)  # face
            self.report({'INFO'}, "Edit Mode — selecciona las caras de la zona pavé.")

        elif self.zone_mode == "WEIGHT_PAINT":
            # Ensure vertex group exists
            if VGROUP_NAME not in obj.vertex_groups:
                obj.vertex_groups.new(name=VGROUP_NAME)
            # Set active group
            obj.vertex_groups.active_index = obj.vertex_groups[VGROUP_NAME].index
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            self.report({'INFO'}, f"Weight Paint — pinta la zona '{VGROUP_NAME}' (rojo = activo).")

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=280)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "zone_mode", expand=True)


class J3DComm_OT_pave_create_shirt(Operator):
    """Genera la malla camisa desde la zona seleccionada o pintada."""
    bl_idname = "j3d_community.pave_create_shirt"
    bl_label   = "Crear Camisa"
    bl_description = (
        "Extrae las caras de la zona pavé y genera una malla camisa\n"
        "flotante offset sobre la superficie del objeto activo"
    )
    bl_options = {'REGISTER', 'UNDO'}

    zone_mode: EnumProperty(
        name="Modo de zona",
        items=ZONE_MODE_ITEMS,
        default="FACE_SELECT",
    )

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and context.mode == 'OBJECT'
        )

    def execute(self, context):
        source = context.active_object
        strategy = FaceShirtStrategy()
        shirt = strategy.create_shirt(context, source, self.zone_mode)

        if shirt is None:
            zone_hint = (
                "en Edit Mode selecciona caras"
                if self.zone_mode == "FACE_SELECT"
                else f"pinta el grupo '{VGROUP_NAME}' antes de crear la camisa"
            )
            self.report({'WARNING'}, f"Sin zona válida — {zone_hint}.")
            return {'CANCELLED'}

        # Select shirt and deselect all others
        for o in context.selected_objects:
            o.select_set(False)
        shirt.select_set(True)
        context.view_layer.objects.active = shirt

        self.report({'INFO'}, f"Camisa '{shirt.name}' creada ({self.zone_mode}).")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=280)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "zone_mode", expand=True)


class J3DComm_OT_pave_distribute(Operator):
    """Distribuye gemas sobre la malla camisa con Poisson Disk + BVH."""
    bl_idname = "j3d_community.pave_distribute"
    bl_label   = "Crear Distribución"
    bl_description = (
        "Distribuye gemas sobre la malla camisa activa usando\n"
        "Poisson Disk Sampling 3D y proyección BVH de normales"
    )
    bl_options = {'REGISTER', 'UNDO'}

    gem_size_mm: FloatProperty(
        name="Tamaño gema (mm)",
        default=1.5,
        min=0.3,
        max=10.0,
        step=10,
        precision=2,
    )
    spacing_mm: FloatProperty(
        name="Separación (mm)",
        description="Gap mínimo entre girdles",
        default=0.2,
        min=0.05,
        max=5.0,
        step=5,
        precision=2,
    )
    seed: IntProperty(
        name="Semilla",
        description="Semilla de aleatoriedad — cambia para variar la distribución",
        default=42,
        min=0,
        max=9999,
    )
    create_cutters: BoolProperty(
        name="Crear Cortadores (Asientos)",
        description="Genera cortadores booleanos (asiento + taladro) alineados con cada micro-gema",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
            and (
                obj.get("j3d_type") == "PAVE_SHIRT"
                or obj.get("j3d_type") == "MESH"  # allow any mesh for testing
            )
        )

    def execute(self, context):
        shirt = context.active_object
        random.seed(self.seed)
        strategy = FaceShirtStrategy()
        result = strategy.create_distribution(
            context,
            shirt,
            self.gem_size_mm,
            self.spacing_mm,
            create_cutters=self.create_cutters,
        )
        if 'FINISHED' in result:
            count = sum(
                1 for o in context.scene.objects
                if o.parent == shirt and o.get("j3d_type") == "GEM"
            )
            self.report({'INFO'}, f"{count} gemas distribuidas en '{shirt.name}'.")
        else:
            self.report({'WARNING'}, "Sin puntos válidos — revisa la malla camisa.")
        return result

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "gem_size_mm")
        col.prop(self, "spacing_mm")
        layout.separator()
        layout.prop(self, "seed")
        layout.prop(self, "create_cutters")


# ── Registration ───────────────────────────────────────────────────────────────

classes = (
    J3DComm_OT_pave_enter_zone,
    J3DComm_OT_pave_create_shirt,
    J3DComm_OT_pave_distribute,
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            bpy.utils.unregister_class(cls)
            bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
