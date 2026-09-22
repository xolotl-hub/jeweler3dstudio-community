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
        ("*", "Size Reference"): "Talla",
        ("*", "Metal Profile / Shank"): "Perfil del Metal",
        ("*", "Create Reference Size"): "Crear Talla de Referencia",
        ("*", "3D Profile Ring Shank"): "Aro con Perfil 3D",
        ("*", "Gems & Cuts"): "Gemas y Cortes",
        ("*", "Gems"): "Gemas",
        ("*", "Add Gem"): "Añadir Gema",
        ("*", "Add 3D Gem"): "Añadir Gema 3D",
        ("*", "Gem Map (Inventory)"): "Mapa de Gemas (Inventario)",
        ("*", "Calculate / Review Gems"): "Calcular / Revisar Gemas",
        ("*", "Calculate Gem Map"): "Calcular Mapa de Gemas",
        ("*", "Select Gems"): "Seleccionar Gemas",
        ("*", "Select All"): "Sel. Todas",
        ("*", "Swap Gems"): "Intercambiar Gemas",
        ("*", "New Cut"): "Nuevo Corte",
        ("*", "New Stone"): "Nueva Piedra",
        ("*", "New Size (mm)"): "Nuevo Calibre (mm)",
        ("*", "No gems in active scene"): "Sin gemas en la escena",
        ("*", "Cut (Stone)"): "Corte (Piedra)",
        ("*", "Size"): "Calibre",
        ("*", "Weight/ea"): "Peso/u",
        ("*", "Qty"): "Cant.",
        ("*", "Cutters"): "Cortadores",
        ("*", "Boolean Cutters"): "Cortadores Booleanos",
        ("*", "Seat & Hole Cutter"): "Asiento y Perforación",
        ("*", "Generate Cutter:"): "Generar Cortador:",
        ("*", "Add Cutter to Gem"): "Añadir Cortador a Gema",
        ("*", "Add Cutter"): "Añadir Cortador",
        ("*", "Reset Cutter Defaults"): "Restablecer Cortador",
        ("*", "V-Cutter"): "Cortador en V",
        ("*", "Settings (Prongs & Bezel)"): "Engastes (Garras y Bisel)",
        ("*", "Prongs"): "Garras (Prongs)",
        ("*", "Bezel"): "Bisel (Bezel)",
        ("*", "Pavé"): "Pavé",
        ("*", "Baskets & Galleries"): "Canastas y Galerías",
        ("*", "Standard Gallery"): "Galería Estándar",
        ("*", "Under Gallery Supports"): "Soportes",
        ("*", "Metrics & Costs"): "Métricas y Costos",
        ("*", "Metrics & Quoting"): "Métricas y Cotizador",
        ("*", "Weights & Metals"): "Pesos y Metales",
        ("*", "Quoting & Technical Sheet"): "Cotizador & Ficha Técnica",
        ("*", "Calculate Metal Weight"): "Calcular Peso de Metal",
        ("*", "Technical Sheet"): "Ficha Técnica",
        
        # --- Menus (Shift + A) ---
        ("*", "Rings & Sizes"): "Anillos & Tallas",
        ("*", "Ring Size (Curve)"): "Talla de Anillo (Curva)",
        ("*", "Ring Size (Cylinder)"): "Talla de Anillo (Cilindro)",
        ("*", "Ring Shank (Profile)"): "Aro de Anillo (Perfil)",

        # --- Operators & Redo Panel ---
        ("*", "Create Ring Size"): "Crear Talla de Anillo",
        ("*", "Create Ring Shank"): "Crear Aro con Perfil",
        ("*", "Create Ring with Profile"): "Crear Aro con Perfil",
        ("*", "Geometry Type"): "Tipo de Geometría",
        ("*", "Orientation"): "Orientación",
        ("*", "US Size"): "Talla US",
        ("*", "US Ring Size"): "Talla US",
        ("*", "Talla US"): "Talla US",
        ("*", "Alignment"): "Alineación",
        ("*", "Location"): "Ubicación",
        ("*", "Rotation"): "Rotación",
        ("*", "Width"): "Ancho",
        ("*", "Width (mm)"): "Ancho (mm)",
        ("*", "Thickness"): "Grosor",
        ("*", "Thickness (mm)"): "Grosor (mm)",
        ("*", "Radial Segments"): "Divisiones Radiales",
        ("*", "Profile Resolution"): "Resolución de Perfil",
        ("*", "Edge Crease"): "Pliegue de Aristas (Crease)",
        ("*", "Subdivision Surface"): "Subdivision Surface",
        ("*", "Subdivision"): "Subdivisión",
        ("*", "Subsurf Level"): "Nivel Subsurf",
        ("*", "Levels"): "Nivel",
        ("*", "Cut"): "Corte",
        ("*", "Stone"): "Piedra",
        ("*", "Commercial Size"): "Calibre Comercial",
        ("*", "Size / ct"): "Calibre / ct",
        ("*", "Size (mm)"): "Tamaño (mm)",
        ("*", "Cutter Segments"): "Segmentos Cortador",
        ("*", "Cutter Crease"): "Crease Cortador",
        ("*", "Segments"): "Segmentos",
        ("*", "Crease"): "Crease",
        ("*", "Crease (Shift+E)"): "Crease (Shift+E)",
        ("*", "Cylinder Depth (mm)"): "Grosor Anillo (mm)",

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
        ("*", "Octagon"): "Octágono",
        ("*", "Baguette"): "Baguette",
        ("*", "Asscher"): "Asscher",

        # --- Gem Stones ---
        ("*", "Diamond"): "Diamante",
        ("*", "Ruby"): "Rubí",
        ("*", "Sapphire"): "Zafiro",
        ("*", "Aquamarine"): "Aquamarina",
        ("*", "Amethyst"): "Amatista",
        ("*", "Cubic Zirconia"): "Circonia",
        ("*", "Moissanite"): "Moissanita",
        ("*", "Morganite"): "Morganita",
        ("*", "Tanzanite"): "Tanzanita",

        # --- Cutters 5-Zone ---
        ("*", "Horizontal Diameters (Radius & Z):"): "Perímetros Horizontales (Radio y Z):",
        ("*", "1. Top Extension"): "1. Cima Superior (Extensión)",
        ("*", "2. Table / Crown"): "2. Tabla / Corona",
        ("*", "3. Upper Girdle"): "3. Filetín Superior",
        ("*", "4. Lower Girdle"): "4. Filetín Inferior",
        ("*", "5. Pavilion Seat"): "5. Asiento (Pabellón)",
        ("*", "6. Drill Hole Bottom"): "6. Perforación Inferior",
        ("*", "Top Extension"): "Extensión Superior",
        ("*", "Table Height"): "Altura de Tabla",
        ("*", "Crown Cone"): "Cono de Corona",
        ("*", "Girdle Band"): "Banda de Filetín",
        ("*", "Pavilion Seat"): "Asiento de Pabellón",
        ("*", "Drill Hole"): "Perforación Inferior",
        ("*", "Radius (mm)"): "Radio (mm)",
        ("*", "Top Radius"): "Radio Cima",
        ("*", "Top Z"): "Z Cima",
        ("*", "Table Radius"): "Radio Tabla",
        ("*", "Table Z"): "Z Tabla",
        ("*", "Upper Girdle Radius"): "Radio Filetín Sup.",
        ("*", "Upper Girdle Z"): "Z Filetín Sup.",
        ("*", "Lower Girdle Radius"): "Radio Filetín Inf.",
        ("*", "Lower Girdle Z"): "Z Filetín Inf.",
        ("*", "Seat Radius"): "Radio Asiento",
        ("*", "Seat Z"): "Z Asiento",
        ("*", "Hole Radius"): "Radio Perforación",
        ("*", "Hole Z"): "Z Perforación",
    },
    "fr_FR": {
        # --- UI Panels & Categories (French) ---
        ("*", "Jeweler 3D"): "Jeweler 3D",
        ("*", "Ring & Size"): "Bague et Taille",
        ("*", "Size Reference"): "Taille",
        ("*", "Metal Profile / Shank"): "Corps de Bague (Profil)",
        ("*", "Create Reference Size"): "Créer Taille de Référence",
        ("*", "3D Profile Ring Shank"): "Corps de Bague Profil 3D",
        ("*", "Gems & Cuts"): "Pierres et Tailles",
        ("*", "Gems"): "Pierres",
        ("*", "Add Gem"): "Ajouter une Pierre",
        ("*", "Add 3D Gem"): "Ajouter Pierre 3D",
        ("*", "Gem Map (Inventory)"): "Carte des Pierres (Inventaire)",
        ("*", "Calculate / Review Gems"): "Calculer / Examiner Pierres",
        ("*", "Boolean Cutters"): "Percés et Découpeurs",
        ("*", "Cutters"): "Découpeurs",
        ("*", "Ring Size (Curve)"): "Taille de Bague (Courbe)",
        ("*", "Ring Size (Cylinder)"): "Taille de Bague (Cylindre)",
        ("*", "Ring Shank (Profile)"): "Corps de Bague (Profil)",
        ("*", "Round Brilliant"): "Brillant Rond",
        ("*", "Diamond"): "Diamant",
        ("*", "Ruby"): "Rubis",
        ("*", "Sapphire"): "Saphir",
        ("*", "Emerald"): "Émeraude",
        ("*", "Top (XY)"): "Dessus (XY)",
        ("*", "Front (XZ)"): "Face (XZ)",
        ("*", "Side (YZ)"): "Profil (YZ)",
        ("*", "Half Round"): "Demi-Jonc",
        ("*", "Flat"): "Ruban Plat",
        ("*", "Comfort Fit"): "Confort",
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
