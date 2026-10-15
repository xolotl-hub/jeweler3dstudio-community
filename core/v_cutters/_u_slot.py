"""
Jeweler 3D Studio - V-Cutters: U-Cutter Operator

Slot en U transversal centrado en cada gema seleccionada.
"""

import math
import bpy
import bmesh
from mathutils import Matrix
from bpy.props import FloatProperty
from bpy.types import Operator, Context

from ..units import mm_to_bu
from ._geometry import _build_u_slot_bm
from ._utils import (
    _sort_chain,
    _mat_at_gem_in_chain,
    _merge_bm_into,
    _finalize_cutter_obj,
    _apply_boolean_if_allowed,
    _avg_gem_size,
)


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
