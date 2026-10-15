"""
Jeweler 3D Studio - Gems: Geometry & Material Engine

Procedural 3D faceted mesh generation for 17 standard cuts,
carat weight estimation, and realistic Principled BSDF shader builder.
"""

import bpy
import bmesh
from ..units import mm_to_bu
from ..gem_data import GEM_MESH_DATA
from ._constants import GEM_STONES, CUT_VOLUME_FACTORS


def calculate_carats(stone_key: str, cut_key: str, size_mm: float) -> float:
    """Calcula el peso estimado en quilates basado en densidad física, corte y volumen."""
    density = GEM_STONES.get(stone_key, GEM_STONES["DIAMOND"])["density"]
    vol_factor = CUT_VOLUME_FACTORS.get(cut_key, 1.00)
    # Calibración: Diamante Redondo 5.0mm = ~0.50 ct
    base_ct = (size_mm / 5.0) ** 3 * 0.50 * (density / 3.52) * vol_factor
    return max(0.001, round(base_ct, 3))


def get_or_create_gem_material(stone_key: str):
    """Crea o reutiliza un material BSDF realista para la gema seleccionada."""
    mat_name = "J3D_Material_" + stone_key
    mat = bpy.data.materials.get(mat_name)
    if mat is not None:
        return mat

    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

    props = GEM_STONES.get(stone_key, GEM_STONES["DIAMOND"])
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 1.0
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 1.0

    bsdf.inputs['Base Color'].default_value = props["color"]
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['IOR'].default_value = props["ior"]
    return mat


def create_gem_mesh(
    cut_key: str = "ROUND",
    name: str = "Gem_Mesh",
    size_mm: float = 1.0,
    context: object = None,
) -> bpy.types.Mesh:
    """Genera una malla 3D procedural paramétrica para cualquiera de los 17 cortes estándar.
    Escala los vértices normalizados multiplicando por mm_to_bu(size_mm, context).
    """
    scale_bu = mm_to_bu(size_mm, context)
    key_upper = cut_key.upper() if cut_key else "ROUND"
    data = GEM_MESH_DATA.get(key_upper, GEM_MESH_DATA.get("ROUND"))

    bm = bmesh.new()
    verts = [
        bm.verts.new((v[0] * scale_bu, v[1] * scale_bu, v[2] * scale_bu))
        for v in data["verts"]
    ]
    bm.verts.ensure_lookup_table()

    for face_indices in data["faces"]:
        try:
            bm.faces.new([verts[i] for i in face_indices])
        except Exception:
            pass

    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = False

    mesh.update()
    return mesh


def create_round_brilliant_mesh(name: str = "Round_Diamond_Mesh", size_mm: float = 1.0, context: object = None) -> bpy.types.Mesh:
    """Genera una malla 3D de Talla Brillante Redonda."""
    return create_gem_mesh(cut_key="ROUND", name=name, size_mm=size_mm, context=context)
