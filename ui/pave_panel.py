"""
Jeweler 3D Studio — Panel UI: Pavé Face Shirt
Panel lateral en la N-panel (Properties sidebar) con el flujo de 3 pasos
para la técnica Camisa de Cara.
"""

import bpy
from bpy.types import Panel


class J3DComm_PT_pave_face_shirt(Panel):
    """Panel principal del flujo Pavé — Camisa de Cara."""
    bl_label       = "💎 Pavé — Camisa de Cara"
    bl_idname      = "J3DComm_PT_pave_face_shirt"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jeweler 3D Community"
    bl_order       = 30

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # ── Paso 1 — Seleccionar / Pintar zona ────────────────────────────────
        box1 = layout.box()
        row = box1.row()
        row.label(text="1. Definir Zona", icon='FACESEL')
        col = box1.column(align=True)
        col.operator(
            "j3d_community.pave_enter_zone",
            text="Selección de Caras",
            icon='EDITMODE_HLT',
        ).zone_mode = "FACE_SELECT"
        col.operator(
            "j3d_community.pave_enter_zone",
            text="Pintar Zona",
            icon='VPAINT_HLT',
        ).zone_mode = "WEIGHT_PAINT"

        # Hint contextual
        if obj and obj.type == 'MESH':
            if context.mode == 'EDIT_MESH':
                box1.label(text="Selecciona caras → Object Mode", icon='INFO')
            elif context.mode == 'WEIGHT_PAINT':
                box1.label(text="Pinta la zona → Object Mode", icon='INFO')

        layout.separator(factor=0.5)

        # ── Paso 2 — Crear Camisa ─────────────────────────────────────────────
        box2 = layout.box()
        box2.label(text="2. Crear Camisa", icon='MOD_SOLIDIFY')

        can_shirt = (
            obj is not None
            and obj.type == 'MESH'
            and context.mode == 'OBJECT'
        )
        col2 = box2.column()
        col2.enabled = can_shirt
        col2.operator("j3d_community.pave_create_shirt", text="Crear Camisa", icon='OUTLINER_OB_MESH')

        if obj and obj.get("j3d_type") == "PAVE_SHIRT":
            box2.label(text=f"Camisa activa: {obj.name}", icon='CHECKMARK')

        layout.separator(factor=0.5)

        # ── Paso 3 — Crear Distribución ───────────────────────────────────────
        box3 = layout.box()
        box3.label(text="3. Crear Distribución", icon='PARTICLES')

        is_shirt = obj is not None and (
            obj.get("j3d_type") == "PAVE_SHIRT"
            or obj.type == 'MESH'  # allow any mesh for quick testing
        )
        col3 = box3.column()
        col3.enabled = is_shirt and context.mode == 'OBJECT'
        col3.operator(
            "j3d_community.pave_distribute",
            text="Crear Distribución",
            icon='SHADERFX',
        )


classes = (J3DComm_PT_pave_face_shirt,)


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
