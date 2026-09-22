# Pendientes (`overview/work/pendientes.md`)

> Elementos identificados durante la planificación de arquitectura UI para seguimiento en sesiones futuras.

## 📌 Lista de Pendientes

| ID | Fecha detección | Origen / Contexto | Descripción | Estado |
|---|---|---|---|---|
| p1 | 2026-08-27 | Arquitectura UI | Implementación paramétrica del Panel 1: Anillo y Talla (Tallas US 3-13.5, 8 perfiles con Subsurf y Crease). | `hecho` |
| p2 | 2026-08-27 | Arquitectura UI | Visor Modal 3D de Gemas con previsualización, mallas facetadas (17 cortes estándar), materiales BSDF y estimador ct. | `hecho` |
| p3 | 2026-08-27 | Arquitectura UI | Módulo de Engastes: Garras paramétricas (Prongs), Bisel cerrado (Bezel) y distribución Pavé. | `pendiente` |
| p4 | 2026-08-27 | Arquitectura UI | Módulo de Cortadores Booleanos: Asientos procedurales de 3 zonas con silueta adaptativa a 17 cortes, segmentos configurables y auto-rebuild en swap. | `hecho` |
| p5 | 2026-08-27 | Arquitectura UI | Módulo de Canastas y Galerías: Generador de biseles inferiores y soportes para piedras centrales. | `pendiente` |
| p6 | 2026-08-27 | Visión Administrativa | Cotizador Administrativo ($/g metal + gemas + mano de obra) y Generador de Ficha Técnica (HTML/PDF). | `pendiente` |
| p7 | 2026-08-27 | Visión Administrativa | Verificador de Seguridad para Impresión 3D/Fundición (Grosor mínimo < 0.8mm y compensación de merma %). | `pendiente` |
| p9 | 2026-09-08 | Iconos de Gemas — Estilos | **Selector de estilo visual de iconos:** Botón o EnumProperty (marquise / round / asscher) para elegir qué set de iconos de gemas se muestra en el panel. Ubicación en UI por definir. Al elegir, el addon copia el estilo activo desde `assets/gems/styles/{estilo}/` hacia `assets/gems/png/` o usa una ruta dinámica. Requiere que los 3 estilos estén completos. | `pendiente` |
| p10 | 2026-09-14 | Gemas — Calibres elongados | Cortes Oval, Pear y Marquise son `L x W` (ej. 6x4mm), pero la UI y el operador solo manejan un eje. Requiere segundo campo de dimensión o tabla fija LxW por preset para calcular volumen/ct correcto. | `pendiente` |
| p11 | 2026-09-14 | Gemas — Preset UI | Al cambiar corte (`j3d_gem_cut`), el `j3d_gem_size_preset` puede quedar con key inválido del corte anterior. Solucionado con callback `_on_gem_cut_update` en `scene_props.py`. | `hecho` |
| p12 | 2026-09-14 | Anillos — Aros Cónicos / Graduados | Modulación de ancho/grosor variable a lo largo del recorrido radial (tapered shank / solitario). | `pendiente` |
| p13 | 2026-09-14 | Anillos — Orientación de Creación | Selector de orientación de plano base (Superior XY / Frontal XZ / Lateral YZ) en UI de Talla y Perfil. | `hecho` |
| p14 | 2026-09-19 | Módulo Engastes | **Garras Paramétricas (Prongs):** Generador procedural de garras adaptadas automáticamente a la gema activa (4, 6 u 8 garras; garras en V / chevron para esquinas de cortes princesa, marquesa, pera). Inclinación, altura sobre tabla, diámetro superior/inferior, tipo de punta (redonda, plana, garra/talón), soporte de menú flotante Redo (F9) y N-Panel. | `pendiente` |
| p15 | 2026-09-19 | Módulo Engastes | **Bisel Cerrado Paramétrico (Bezel):** Generador de bisel cerrado y semi-bisel adaptado a los 17 cortes. Grosor de pared, ángulo de socavado (undercut), altura sobre el filetín y pestaña inferior de asiento. | `pendiente` |
| p16 | 2026-09-19 | Módulo Canastas | **Canastas y Galerías Decorativas (Baskets):** Galería de alambre inferior (bridge / under-gallery) con patrones clásicos (arcos, celosía, cruzados), conectando las garras con el aro del anillo para solitarios. | `pendiente` |
| p17 | 2026-09-19 | Módulo Pavé | **Distribución Pavé sobre Curva/Superficie:** Distribución paramétrica de micro-gemas a lo largo del riel o superficie del anillo. Espaciado automático entre gemas (0.1 a 0.3mm), micro-garras (bead prongs) y cortador booleano continuo de canal. | `pendiente` |
| p18 | 2026-09-19 | Cortadores / Booleanos | **Auto-Boolean Inteligente (1-Click):** Botón directo "Aplicar Cortadores al Metal" que ejecuta la diferencia booleana (Exact/Fast) de todos los cortadores asociados a las gemas sobre el aro o engaste activo, ocultando los cortadores automáticamente. | `pendiente` |
| p19 | 2026-09-19 | Cortadores / Booleanos | **Cortador Booleano en V (V-Cutter):** Cortador continuo en canal en V para engaste en carril/canal (channel setting) y ranuras decorativas. | `pendiente` |
| p20 | 2026-09-19 | Verificación & Exportación | **Verificador y Exportador para Impresión 3D / Fundición (Casting Ready):** Verificación de grosor mínimo (< 0.6mm advertencia de fragilidad en fundición a la cera perdida) y exportador STL/3MF escalado con compensación de contracción/merma (ej. +1.5%). | `pendiente` |
| p21 | 2026-09-21 | Internacionalización i18n | **Normalización UI Base Inglés & Tier 1 (ES, IT, FR):** Refactorizar labels base del código fuente a inglés canónico (`ui/panels.py`, `ui/menus.py`, `core/`) y completar catálogos de traducción en `ui/i18n.py` para Español (`es_ES`), Italiano (`it_IT`) y Francés (`fr_FR`). | `hecho` |
| p22 | 2026-09-21 | Internacionalización i18n | **Expansión Multi-idioma Tier 2 (HI, ZH, DE, PT, JA):** Catálogos de traducción para los grandes centros mundiales de manufactura y corte: Hindi (`hi_IN`), Chino Simplificado (`zh_HANS`), Alemán (`de_DE`), Portugués (`pt_BR`) y Japonés (`ja_JP`). | `pendiente` |

- **Estados:** `pendiente`, `en progreso`, `promovido_a_task`, `descartado`, `hecho`.

---

## ✅ Completados (Historial)

| ID | Fecha Resolución | Origen / Contexto | Descripción / Solución | Agente |
|---|---|---|---|---|
| p8 | 2026-09-01 | Bug Escala - Herramienta Talla | Corregida escala mm→BU en `core/ring.py` dividiendo por `unit_scale` (1 BU = 1 mm). Talla US 7 genera 17.32 BU. | Gemini 3.6 Flash (Medium) |

