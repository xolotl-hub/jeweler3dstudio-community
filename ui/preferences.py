"""
Jeweler 3D Studio Community Edition - Addon Preferences
Free & Open Source Edition (GPLv3).
"""

import bpy
from bpy.types import AddonPreferences


class J3DComm_Preferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="💎 Jeweler 3D Studio Community Edition v0.2.0", icon='HEART')
        box.label(text="Versión gratuita y de código abierto (GPLv3). No requiere licencia comercial.")
        box.separator()
        box.label(text="Recursos y soporte:")
        row = box.row(align=True)
        row.operator("wm.url_open", text="Repositorio GitHub", icon='URL').url = "https://github.com/xolotl-hub/jeweler3dstudio-community"
        row.operator("wm.url_open", text="Documentación", icon='HELP').url = "https://github.com/xolotl-hub/jeweler3dstudio-community#readme"


classes = (
    J3DComm_Preferences,
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
