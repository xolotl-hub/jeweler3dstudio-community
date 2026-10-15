"""
Jeweler 3D Studio - V-Cutters: V-Wedge Operators

Longitudinal and transversal V-cutters for stone setting.
"""

import bpy
import bmesh
from bpy.props import FloatProperty, BoolProperty
from bpy.types import Operator, Context

from ..units import mm_to_bu
from ._geometry import _build_v_wedge_bm
from ._utils import (
    _sort_chain,
    _mat_between_gems,
    _mat4,
    _gem_up,
    _merge_bm_into,
    _finalize_cutter_obj,
    _apply_boolean_if_allowed,
    _avg_gem_size,
)


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
    cap_ends:   BoolProperty(name="Rematar extremos", default=True,                                  # type: ignore
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
