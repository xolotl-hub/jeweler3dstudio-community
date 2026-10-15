"""
Jeweler 3D Studio - V-Cutters: Transform & Chain Utilities

Helpers for gem orientation, chain sorting, BMesh merging,
object finalization, and boolean application.
"""

from typing import List
import bpy
import bmesh
from mathutils import Vector, Matrix


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
