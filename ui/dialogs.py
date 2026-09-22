"""
Jeweler 3D Studio - UI Dialogs Module
Provides modal popups and technical report exporters for production.
"""

import os
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from ..core.metrics import calculate_mesh_weight, calculate_mesh_volume_cm3, get_metal_density


class J3DComm_OT_export_report(Operator):
    """Exporta un reporte técnico de producción en formato de texto / JSON"""
    bl_idname = "j3d_community.export_report"
    bl_label = "Exportar Reporte Técnico"
    bl_description = "Genera una ficha técnica con pesos de metal y conteo de gemas"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(
        name="Ruta de Archivo",
        subtype='FILE_PATH'
    ) # type: ignore

    include_gems: BoolProperty(
        name="Incluir Conteo de Gemas",
        default=True
    ) # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Solo ejecutable en Object Mode."""
        return context.mode == 'OBJECT'

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        if not self.filepath:
            self.filepath = os.path.join(bpy.path.abspath("//"), "Jeweler_3D_Report.txt")

        scene = context.scene
        metal_key = getattr(scene, "j3d_community_metal_type", "GOLD_18K_YELLOW")
        active_obj = context.active_object

        lines = [
            "=" * 50,
            "     JEWELER 3D STUDIO - REPORTES DE PRODUCCIÓN",
            "=" * 50,
            f"Metal Seleccionado: {metal_key}",
            f"Densidad: {get_metal_density(metal_key):.2f} g/cm³",
        ]

        if active_obj and active_obj.type == 'MESH':
            vol_cm3 = calculate_mesh_volume_cm3(active_obj)
            weight_g = calculate_mesh_weight(active_obj, metal_key)
            lines.extend([
                f"Objeto Evaluado: {active_obj.name}",
                f"Volumen Neto Malla: {vol_cm3:.4f} cm³",
                f"Peso Estimado Metal: {weight_g:.2f} g",
            ])
        else:
            lines.append("No hay ninguna pieza/malla activa elegible seleccionada.")

        lines.append("=" * 50)

        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        self.report({'INFO'}, f"Ficha técnica exportada en: {self.filepath}")
        return {'FINISHED'}


classes = (
    J3DComm_OT_export_report,
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            try:
                bpy.utils.unregister_class(cls)
                bpy.utils.register_class(cls)
            except Exception:
                pass


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
