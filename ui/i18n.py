"""
Jeweler 3D Studio - Internationalization & Translation Module (i18n)
Registers UI translations for Blender 4.2+ via bpy.app.translations.
Supports:
  - Spanish ('es_ES', 'es')
  - French ('fr_FR')
  - English (Default/fallback)
"""

from typing import Dict, Tuple
import bpy

# Translation Catalog: { lang_code: { (msgctxt, msgid): msgstr } }
TRANSLATIONS_DICT: Dict[str, Dict[Tuple[str, str], str]] = {
    "es_ES": {
        # --- UI Panels & Categories ---
        ("*", "Jeweler 3D"): "Jeweler 3D",
        ("*", "Ring & Size"): "Anillo y Talla",
        ("*", "Create Reference Size"): "Crear Talla de Referencia",
        ("*", "3D Profile Ring Shank"): "Aro con Perfil 3D",
        ("*", "Gems & Cuts"): "Gemas y Cortes",
        ("*", "Add Gem"): "Añadir Gema",
        ("*", "Gem Map (Inventory)"): "Mapa de Gemas (Inventario)",
        ("*", "Calculate Gem Map"): "Calcular Mapa de Gemas",
        ("*", "Select Gems"): "Seleccionar Gemas",
        ("*", "Select All"): "Sel. Todas",
        ("*", "Swap Gems"): "Intercambiar Gemas",
        ("*", "Boolean Cutters"): "Cortadores Booleanos",
        ("*", "Add Cutter to Gem"): "Añadir Cortador a Gema",
        ("*", "Reset Cutter Defaults"): "Restablecer Cortador",
        ("*", "Settings (Prongs & Bezel)"): "Engastes (Garras y Bisel)",
        ("*", "Baskets & Galleries"): "Canastas y Galerías",
        ("*", "Metrics & Costs"): "Métricas y Costos",
        ("*", "Calculate Metal Weight"): "Calcular Peso de Metal",
        ("*", "Technical Sheet"): "Ficha Técnica",
        
        # --- Menus (Shift + A) ---
        ("*", "Rings & Sizes"): "Anillos & Tallas",
        ("*", "Ring Size (Curve)"): "Talla de Anillo (Curva)",
        ("*", "Ring Size (Cylinder)"): "Talla de Anillo (Cilindro)",
        ("*", "Ring Shank (Profile)"): "Aro de Anillo (Perfil)",
        ("*", "Gems"): "Gemas",

        # --- Operators & Redo Panel ---
        ("*", "Create Ring Size"): "Crear Talla de Anillo",
        ("*", "Create Ring with Profile"): "Crear Aro con Perfil",
        ("*", "Geometry Type"): "Tipo de Geometría",
        ("*", "Orientation"): "Orientación",
        ("*", "US Ring Size"): "Talla US",
        ("*", "Talla US"): "Talla US",
        ("*", "Alignment"): "Alineación",
        ("*", "Location"): "Ubicación",
        ("*", "Rotation"): "Rotación",
        ("*", "Width (mm)"): "Ancho (mm)",
        ("*", "Thickness (mm)"): "Grosor (mm)",
        ("*", "Radial Segments"): "Divisiones Radiales",
        ("*", "Profile Resolution"): "Resolución de Perfil",
        ("*", "Edge Crease"): "Pliegue de Arista (Crease)",
        ("*", "Subdivision"): "Subdivisión",

        # --- Ring Profiles ---
        ("*", "Half Round"): "Media Caña",
        ("*", "Flat"): "Plano",
        ("*", "Comfort Fit"): "Confort",
        ("*", "Knife Edge"): "Filo",
        ("*", "Euro Shank"): "Aro Europeo",
        ("*", "Beveled"): "Biseado",
        ("*", "Concave"): "Cóncavo",

        # --- Orientations ---
        ("*", "Top (XY)"): "Superior (XY)",
        ("*", "Front (XZ)"): "Frontal (XZ)",
        ("*", "Side (YZ)"): "Lateral (YZ)",

        # --- Gem Cuts ---
        ("*", "Round Brilliant"): "Brillante Redondo",
        ("*", "Princess"): "Princesa",
        ("*", "Emerald"): "Esmeralda",
        ("*", "Marquise"): "Marquesa",
        ("*", "Pear"): "Pera",
        ("*", "Cushion"): "Cojín",
        ("*", "Radiant"): "Radiante",
        ("*", "Heart"): "Corazón",
        ("*", "Trillion"): "Trillón",
        ("*", "Trilliant"): "Trillante",
        ("*", "Triangle"): "Triángulo",
        ("*", "Flanders"): "Flandes",
        ("*", "Square"): "Cuadrado",

        # --- Cutters 5-Zone ---
        ("*", "Top Extension"): "Extensión Superior",
        ("*", "Table Height"): "Altura de Tabla",
        ("*", "Crown Cone"): "Cono de Corona",
        ("*", "Girdle Band"): "Banda de Filetín",
        ("*", "Pavilion Seat"): "Asiento de Pabellón",
        ("*", "Drill Hole"): "Perforación Inferior",
        ("*", "Live Cutter Parameters"): "Parámetros de Cortador en Vivo",
    },
    "fr_FR": {
        # --- UI Panels & Categories (French) ---
        ("*", "Jeweler 3D"): "Jeweler 3D",
        ("*", "Ring & Size"): "Bague et Taille",
        ("*", "Create Reference Size"): "Créer Taille de Référence",
        ("*", "3D Profile Ring Shank"): "Corps de Bague Profil 3D",
        ("*", "Gems & Cuts"): "Pierres et Tailles",
        ("*", "Add Gem"): "Ajouter une Pierre",
        ("*", "Gem Map (Inventory)"): "Carte des Pierres (Inventaire)",
        ("*", "Boolean Cutters"): "Percés et Découpeurs",
        ("*", "Ring Size (Curve)"): "Taille de Bague (Courbe)",
        ("*", "Ring Size (Cylinder)"): "Taille de Bague (Cylindre)",
        ("*", "Ring Shank (Profile)"): "Corps de Bague (Profil)",
        ("*", "Round Brilliant"): "Brillant Rond",
    }
}

# Add alias for 'es' locale
TRANSLATIONS_DICT["es"] = TRANSLATIONS_DICT["es_ES"]


def register():
    """Registra catalogo de traducciones en Blender"""
    try:
        bpy.app.translations.register(__name__, TRANSLATIONS_DICT)
    except Exception as e:
        print(f"[Jeweler 3D i18n] Warning during register: {e}")


def unregister():
    """Elimina catalogo de traducciones al desactivar extension"""
    try:
        bpy.app.translations.unregister(__name__)
    except Exception as e:
        print(f"[Jeweler 3D i18n] Warning during unregister: {e}")
