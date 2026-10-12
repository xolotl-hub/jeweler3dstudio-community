"""
Jeweler 3D Studio - Preferences & Gumroad License Management UI
Provides license key activation form and subscription status display in Blender preferences.
"""

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import AddonPreferences, Operator

# Determinación de paquete para extensiones en Blender 4.2+
_ADDON_PACKAGE = __package__.split(".")[0] if "." in __package__ else __package__


class J3DComm_OT_verify_license(Operator):
    """Verifica y activa la clave de licencia de Gumroad"""
    bl_idname = "j3d_community.verify_license"
    bl_label = "Activar Licencia Gumroad"
    bl_description = "Verifica la clave de suscripción contra los servidores de Gumroad"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        prefs = context.preferences.addons.get(__package__, None)
        if not prefs:
            # Buscar en packages alternativos de extensiones
            for name, ext in context.preferences.addons.items():
                if "jeweler3d" in name:
                    prefs = ext
                    break
        if not prefs:
            self.report({'ERROR'}, "No se encontraron las preferencias del addon.")
            return {'CANCELLED'}

        pref_obj = prefs.preferences
        key = pref_obj.license_key.strip()
        if not key:
            self.report({'WARNING'}, "Por favor ingresa una clave de licencia válida.")
            return {'CANCELLED'}

        from ..core.licensing import verify_gumroad_license, PRODUCT_PERMALINKS
        tier = getattr(pref_obj, "current_tier", "essential")
        permalink = PRODUCT_PERMALINKS.get(tier, "jeweler3d-essential")

        self.report({'INFO'}, "Conectando con Gumroad...")
        success, msg, data = verify_gumroad_license(key, permalink)

        if success:
            pref_obj.is_licensed = True
            pref_obj.license_status = f"Activa ({data.get('email', 'Suscripción OK')})"
            pref_obj.license_email = data.get("email", "")
            self.report({'INFO'}, f"✔ {msg}")
        else:
            pref_obj.is_licensed = False
            pref_obj.license_status = f"Error: {msg}"
            self.report({'ERROR'}, f"✗ {msg}")

        return {'FINISHED'}


class J3DComm_OT_deactivate_license(Operator):
    """Desactiva la clave de licencia local"""
    bl_idname = "j3d_community.deactivate_license"
    bl_label = "Desactivar Licencia"
    bl_description = "Borra la clave de licencia local y el token de activación"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        prefs = context.preferences.addons.get(__package__, None)
        if not prefs:
            for name, ext in context.preferences.addons.items():
                if "jeweler3d" in name:
                    prefs = ext
                    break
        if prefs:
            pref_obj = prefs.preferences
            pref_obj.license_key = ""
            pref_obj.is_licensed = False
            pref_obj.license_status = "No activada"
            pref_obj.license_email = ""

            from ..core.licensing import clear_offline_token, PRODUCT_PERMALINKS
            tier = getattr(pref_obj, "current_tier", "essential")
            permalink = PRODUCT_PERMALINKS.get(tier, "jeweler3d-essential")
            clear_offline_token(permalink)

            self.report({'INFO'}, "Licencia desactivada correctamente.")

        return {'FINISHED'}


class J3D_Preferences(AddonPreferences):
    bl_idname = __package__

    current_tier: StringProperty(
        name="Tier",
        default="essential",
    )
    license_key: StringProperty(
        name="Clave de Licencia",
        description="Pega aquí la clave de licencia recibida al comprar en Gumroad",
        default="",
        subtype='PASSWORD',
    )
    is_licensed: BoolProperty(
        name="Licencia Activa",
        default=False,
    )
    license_status: StringProperty(
        name="Estado",
        default="No activada",
    )
    license_email: StringProperty(
        name="Email Registrado",
        default="",
    )

    def draw(self, context):
        layout = self.layout

        # Si el tier es community, no requiere licencia
        if self.current_tier == "community":
            box = layout.box()
            box.label(text="💎 Jeweler 3D Studio Community Edition", icon='HEART')
            box.label(text="Versión gratuita y de código abierto (GPLv3). No requiere licencia.")
            return

        box = layout.box()
        box.label(text="🔑 Activación de Licencia (Gumroad)", icon='LOCKED')

        col = box.column(align=True)
        col.prop(self, "license_key")

        row = box.row(align=True)
        if not self.is_licensed:
            row.operator("j3d_community.verify_license", text="Verificar y Activar Licencia", icon='CHECKMARK')
        else:
            row.operator("j3d_community.deactivate_license", text="Desactivar Licencia", icon='X')

        # Estado visual
        status_box = box.box()
        if self.is_licensed:
            status_box.alert = False
            status_row = status_box.row()
            status_row.label(text=f"✔ Estado: {self.license_status}", icon='CHECKBOX_HLT')
            if self.license_email:
                status_box.label(text=f"Comprador: {self.license_email}", icon='USER')
        else:
            status_box.alert = True
            status_box.label(text=f"⚠ Estado: {self.license_status}", icon='ERROR')
            status_box.label(text="Ingresa tu clave de compra de Gumroad para habilitar el motor nativo.")
            link_row = status_box.row()
            link_row.operator("wm.url_open", text="Comprar Licencia en Gumroad", icon='URL').url = "https://gumroad.com"


classes = (
    J3DComm_OT_verify_license,
    J3DComm_OT_deactivate_license,
    J3D_Preferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
