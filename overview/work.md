# Trabajo: índice maestro y backlog canónico

> **Backlog canónico único.** Concentra los IDs de `tarea`, `bug` y `deuda`. El detalle se distribuye en `overview/work/tasks.md` (tarea activa), `overview/work/pendientes.md` (seguimiento) y `overview/work/deuda_tecnica.md` (deuda ordenada por prioridad Alta/Media/Baja).

| ID | Tipo | Estado | Resumen | Archivo de Detalle |
|---|---|---|---|---|
| $archi | tarea / doc | hecho | Arquitectura 100 % documentada con 3 diagramas Mermaid y 31 componentes. | — |
| — | — | — | Backlog limpio sin tareas bloqueantes activas | — |


Tipos: `tarea`, `bug`, `deuda`. Estados: `pendiente`, `en progreso`, `bloqueado`, `hecho`, `no verificado`.

---

## ✅ Completados (Historial)

<!-- Mover aquí tareas, bugs o deudas completadas conservando su ID -->

| ID | Tipo | Resuelto por (Agente) | Causa Raíz / Resumen Solución | Fecha |
|---|---|---|---|---|
| w61 | bug | Gemini 3.7 Flash (Medium) | Corregido regex agresivo en `tools/pack_zip/pack_community.py` y `pack_standard.py`: `re.sub(r'\bj3d\.')` convertía erróneamente la variable local `j3d.gem_cut` en `j3d_community.gem_cut`, disparando `NameError`. Restringido el reemplazo exclusivamente a identificadores de operadores en strings y llamadas `bpy.ops.j3d.`. Añadido test automatizado en `tests/run_tests_headless.py` (6/6 tests passing OK) y regenerados los 3 tiers ZIP. | 2026-09-22 |
| w60 | tarea / calidad | Gemini 3.7 Flash (Medium) | Blindaje multi-tier y cumplimiento Blender Extensions: 1) Corregido registro de `scene_props` en generación de `ui/panels/__init__.py` en `pack_community.py`, 2) Purgado stub residual `dummy_cube` de `core/gems.py`, `ui/panels/cutters.py` y `ui/panels/stubs.py`, 3) Sincronizada lectura de `scene.j3d` en operadores y callbacks dinámicos de `cutters.py` y `gems.py`, 4) Implementado reseteo automático de preset comercial al cambiar corte (`_on_gem_cut_update`), 5) Creada suite de pruebas headless automatizada `tests/run_tests_headless.py` con 5/5 tests passing (`OK`), 6) Regenerados y validados los 3 paquetes ZIP en `dist/`. | 2026-09-22 |
| d2 | deuda / refactor | Gemini 3.7 Flash (Medium) | Modularizado `ui/panels.py` (753L) en subpaquete `ui/panels/` (`ring.py`, `gems.py`, `gem_map.py`, `cutters.py`, `stubs.py`, `__init__.py`), todos estrictamente < 250L. Simplificado pipeline de Community en `tools/pack_zip/pack_community.py`. Regenerados y validados los 3 tiers ZIP. | 2026-09-22 |
| d13 | deuda / refactor | Gemini 3.7 Flash (Medium) | Modularizado `core/gem_data.py` (2589L) en subpaquete `core/gem_data/` con 5 módulos organizados por familias de corte (`_stepped.py`, `_fancy.py`, `_octagon.py`, `_round.py`, `_trillion.py`) y `__init__.py` con reexport de `GEM_MESH_DATA`. Validación de 17 mallas de corte intactas y regeneración de los 3 tiers ZIP. | 2026-09-22 |
| d11 | bug / deuda | Gemini 3.7 Flash (Medium) | Eliminada llamada no soportada `target_set_prop("matrix", ...)` en `ui/gizmos.py` y unificado `unregister()` redundante. Resuelto `flag-w22` y `d12` (limpieza de `core/prongs.py`). | 2026-09-21 |
| w59 | tarea | Gemini 3.7 Flash (Medium) | Auditoría integral de deuda técnica: escaneo completo de 100% de archivos del proyecto, clasificación priorizada Alta/Media/Baja en `overview/work/deuda_tecnica.md`. | 2026-09-21 |
| w58 | mejora | Gemini 3.7 Flash (Medium) | Normalización UI Base a Inglés Canónico (`ui/panels.py`, `ui/menus.py`, `core/ring.py`, `core/gems.py`, `core/cutters.py`) para cumplimiento de Blender Extensions. Actualizado catálogo de traducciones i18n (`ui/i18n.py`) con llaves en inglés y soporte `es_ES`/`fr_FR`. Reconstruido y publicado Community ZIP (771.0 KB). | 2026-09-21 |
| w57 | bug | Gemini 3.7 Flash (Medium) | Fix: Gemas en Community caían a ROUND porque GEM_MESH_DATA estaba filtrado a 3 cortes. Eliminados filtros en `pack_community.py`; Community ahora tiene los 17 cortes completos igual que PRO. | 2026-09-21 |
| w56 | mejora | Gemini 3.7 Flash (Medium) | Añadido campo `website` oficial en `blender_manifest.toml` y en la generación paramétrica de manifiestos en `tools/pack_zip/pack_common.py`. Sincronizado y publicado en GitHub Community. | 2026-09-21 |
| w55 | mejora | Gemini 3.7 Flash (Medium) | Habilitada la publicación automática (build + commit + push) por defecto al ejecutar `tools/pack_zip/pack_community.py`, agregando flag `--no-publish` para omitir el push. Verificado commit y push con actualización de LICENSE_community.txt y README_community.md. | 2026-09-21 |
| w54 | tarea | Gemini 3.7 Flash (Medium) | Modularizado `tools/pack_zip/` en scripts independientes por tier (`pack_pro.py` [default], `pack_community.py`, `pack_standard.py`, `pack_all.py`, `pack_common.py`), estableciendo Jeweler 3D Studio PRO como el tier default y prioritario en el flujo de desarrollo. | 2026-09-21 |
| w53 | mejora | Gemini 3.7 Flash (Medium) | Integrado ecosistema de gobernanza completo (`.gitmodules`, submódulos `.agents`, `.skill/` y carpeta `overview/`) en el pipeline de publicación automática `publish_community` en `tools/pack_zip/pack_tiers.py` para demostrar capacidades de `*-agent-rules` en el repo público. | 2026-09-21 |
| w52 | mejora | Gemini 3.7 Flash (Medium) | Omitidos subpaneles 'Mapa de Gemas' e 'Intercambiar Gemas' de la edición Community en `tools/pack_zip/pack_tiers.py`. El panel 'Gemas' de Community ahora contiene exclusivamente 'Añadir Gema' (con 3 cortes base y promo box de Studio PRO). | 2026-09-21 |
| w51 | mejora | Gemini 3.7 Flash (Medium) | Filtrados paneles y eliminados stubs inactivos (Engastes, Cortadores, Canastas y Métricas/Cotizador) de la edición Community en `tools/pack_zip/pack_tiers.py`. N-Panel en Community despliega exclusivamente Anillo y Gemas. Corregido lookahead regex para prefijos de operadores. | 2026-09-21 |
| w50 | bug | Gemini 3.7 Flash (Medium) | Corregido cálculo de `ROOT_DIR` con `find_project_root()` en `tools/pack_zip/pack_tiers.py` para localizar `blender_manifest.toml` y el código fuente desde cualquier subdirectorio. Generados paquetes válidos en `dist/` (~765 KB cada uno). | 2026-09-21 |
| w49 | mejora | Gemini 3.7 Flash (Medium) | Creado `tools/pack_tiers.py` para generación automática de las 3 ediciones (Community, Standard, Studio PRO) con aislamiento de IDs de manifiesto (`jeweler3dstudio_community`, `jeweler3dstudio_standard`, `jeweler3dstudio`), prefijos de operadores (`j3d_lite`, `j3d_std`, `j3d`), categorías N-Panel y filtrado de features para coexistencia sin colisión en Blender 4.2+. | 2026-09-21 |
| w48 | mejora | Gemini 3.7 Flash (Medium) | Creado `README.md` principal en la raíz del repositorio con documentación detallada del addon, características, 17 cortes, cortadores de 5 zonas, guía de instalación para Blender 4.2+, arquitectura modular y roadmap. | 2026-09-21 |
| w47 | mejora | Gemini 3.7 Flash (Medium) | Reordenada la tabla del Mapa de Gemas (`ui/panels.py`): 1) Cabecera de columnas superior, 2) Filas de gemas existentes con sombreado y selector, 3) Pie de tabla inferior con totales y botón 'Sel. Todas'. ZIP empaquetado. | 2026-09-21 |
| w46 | mejora | Gemini 3.7 Flash (Medium) | Resaltado visual bidireccional en la tabla del Mapa de Gemas (`ui/panels.py`): detecta la gema activa seleccionada en el Viewport 3D y resalta su fila con una caja destacada (`box.box()`), botón `emboss=True` e icono `RADIOBUT_ON`. ZIP empaquetado. | 2026-09-21 |
| w45 | mejora | Gemini 3.7 Flash (Medium) | Selector interactivo de gemas directo por fila en tabla del Mapa de Gemas (`j3d.select_gems`) con soporte de selección por lote (corte/piedra/calibre) y botón global de selección en cabecera. ZIP empaquetado. | 2026-09-21 |
| w44 | tarea | Gemini 3.7 Flash (Medium) | Fase 1 i18n completada: creado `ui/i18n.py` con catálogo de 67 términos en `es_ES`/`fr_FR`, registrado en `bpy.app.translations` y conectado en `ui/__init__.py`. Validado en Blender 5.2 headless y ZIP empaquetado. | 2026-09-21 |
| w43 | mejora | Gemini 3.7 Flash (Medium) | Integración de operadores en menú Shift+A (Add Menu): Curve > Talla de Anillo (Curva), Mesh > Talla de Anillo (Cilindro) y Aro con Perfil, y submenú dedicado Jeweler 3D con acceso al Redo Panel (F9). Creado `ui/menus.py` y actualizado ZIP. | 2026-09-21 |
| w42 | mejora | Gemini 3.7 Flash (Medium) | Edición en vivo de cortadores seleccionados con control de Crease paramétrico (0.0-1.0), segmentos y edición individual de radio y Z para los 6 perímetros. | 2026-09-19 |
| w41 | mejora | Gemini 3.7 Flash (Medium) | Cortador Booleano de 5 zonas calibrado milimétricamente con STL de referencia (extensión superior cilíndrica, corona, girdle, pabellón y perforación). | 2026-09-19 |
| w40 | mejora | Gemini 3.7 Flash (Medium) | Factor de split en tabla de Mapa de Gemas (0.45/0.38/0.60) y empaquetado ZIP corregido. | 2026-09-19 |
| w39 | mejora | Gemini 3.7 Flash (Medium) | Protegido ancho de columnas numéricas (Calibre ~22.4%, Peso/u ~25.0%, Cant. ~16.6%) en `ui/panels.py` para que nunca se trunquen a puntos suspensivos (`...`) en paneles N estrechos, dejando que Corte absorba la compresión. ZIP empaquetado. | 2026-09-19 |
| w38 | mejora | Gemini 3.7 Flash (Medium) | Ajustadas proporciones elásticas en tabla 4 columnas del Mapa de Gemas (`ui/panels.py`). ZIP empaquetado. | 2026-09-19 |
| w37 | bug | Gemini 3.7 Flash (Medium) | Eliminada restricción `if key != "ROUND"` en `get_cut_preview_collection()` y `get_cut_enum_items()` de `core/gems.py` y `ui/panels.py`. Ahora los 17 iconos se cargan y muestran en el desplegable y recuadro de previsualización del addon. ZIP re-empaquetado. | 2026-09-19 |
| w36 | tarea | Gemini 3.7 Flash (Medium) | Generado set completo de los 17 iconos de gemas en SVG y PNG en `assets/gems/styles/marquise/` con el pipeline Art Déco oro/negro (`#0A0A0A`, `#C9A84C`, `#806722`), doble filetín y facetas proyectadas desde `core/gem_data.py` con Inkscape CLI. Creado `tools/generate_all_marquise_icons.py`. | 2026-09-19 |
| w35 | tarea | Gemini 3.7 Flash (Medium) | Generado icono `oval.svg` y renderizado `oval.png` en `assets/gems/styles/marquise/` con proporciones de corona de 33 facetas en estilo Art Déco oro/negro (`#0A0A0A`, `#C9A84C`, `#806722`). Creado script `tools/generate_oval_marquise_icon.py`. | 2026-09-19 |
| w34 | mejora | Gemini 3.7 Flash (Medium) | Tabla 4 cols en Mapa de Gemas, lectura dimensional en vivo, Intercambiador de Gemas (`j3d.swap_gems`) y módulo `core/cutters.py` procedural (3 zonas con adaptabilidad a 17 cortes y auto-rebuild). ZIP empaquetado. | 2026-09-19 |
| w33 | mejora | Gemini 3.7 Flash (Medium) | Renombrado "Visor de Gemas" a "Añadir Gema", implementado operador `j3d.calculate_gem_map` e interfaz de cálculo y tabla de inventario en "Mapa de Gemas". ZIP empaquetado. | 2026-09-19 |
| w32 | mejora | Gemini 3.7 Flash (Medium) | Integradas mallas normalizadas de los 17 cortes estándar en `core/gem_data.py` (Python puro, 0 binarios) y conectado generador paramétrico `create_gem_mesh` en `core/gems.py`. Resuelto `p2`. | 2026-09-19 |
| w31 | mejora | Gemini 3.7 Flash (Medium) | Ajustados valores por defecto al abrir addon y operador: Ancho=3.00mm, Grosor=1.50mm, Radiales=16, Perfil=2. ZIP empaquetado. | 2026-09-18 |
| w30 | tarea | Gemini 3.7 Flash (Medium) | Selector de orientación de plano (Superior XY, Frontal XZ, Lateral YZ) en Talla (Curva/Cilindro) y Perfil del Metal (Aro 3D). Resuelto `p13`. ZIP empaquetado. | 2026-09-14 |
| w29 | mejora | Gemini 3.7 Flash (Medium) | Modificador Subsurf automático + Edge Crease (`crease_edge` = 0.8) en esquinas vivas del perfil. Selectores de segmentos radiales y resolución de perfil en UI. ZIP empaquetado. | 2026-09-14 |
| w28 | tarea | Gemini 3.7 Flash (Medium) | 8 perfiles paramétricos de metal (Media Caña, Plano, Confort, Oval, Filo, Aro Europeo, Biseado, Cóncavo) con sweep BMesh y diámetro interior = Talla US real. Selector UI y ZIP empaquetado. | 2026-09-14 |
| w27 | tarea | Claude Sonnet 4.6 (Thinking) | 17 cortes x tabla completa de calibres comerciales GIA/ISO con ct estimados por densidad+factor volumétrico. Default=1.0mm (ROUND). ZIP reempaquetado. | 2026-09-14 |
| w26 | tarea | Gemini 3.7 Flash (Medium) | Desplegable de calibres y quilates comerciales estándar (19 calibres 1.0mm-10.0mm GIA) con fallback condicional a `CUSTOM`. | 2026-09-14 |
| w25 | tarea | Gemini 3.7 Flash (Medium) | Normalizadas conversiones mm/BU (`mm_to_bu`), creado `core/units.py`, simplificada UI fijando estándar `1 BU = 1 mm`. | 2026-09-14 |
| w24 | tarea | OpenAI GPT-5 | Generado Round Brilliant Art Déco desde proporciones de tabla, estrella y filetín de `core/gems.py`; SVG y PNG activados. | 2026-09-08 |
| w23 | tarea | Gemini 3.7 Flash (Medium) | Generados 17 iconos vectoriales de lujo (SVG + PNG 256x256 dark/light), backup en `assets_historial/`, y conectado `template_icon_view` con `bpy.utils.previews`. | 2026-09-08 |
| w22 | bug | Gemini 3.7 Flash (Medium) | Eliminada llamada a propiedad inexistente `target_set_prop("matrix", ...)` en `ui/gizmos.py` y asignado `matrix_basis` en `refresh()`. | 2026-09-08 |
| w21 | tarea | Claude Sonnet 4.6 (Thinking) | Reemplazado `j3d.dummy_cube` por `j3d.add_gem` en `ui/panels.py` (Visor de Gemas). Botón ahora genera Diamante 3D facetado de 5mm. | 2026-09-01 |
| w20 | tarea | Gemini 3.6 Flash (Medium) | Ajustado `J3D_OT_dummy_cube` (`core/gems.py`) a tamaño de 5 mm en la escala de joyería (1 BU = 1 mm). | 2026-09-01 |
| w19 | bug | Gemini 3.6 Flash (Medium) | Restaurado `J3D_OT_dummy_cube` en `core/gems.py` devolviendo los botones a los subpaneles UI. | 2026-09-01 |
| w18 | tarea | Gemini 3.6 Flash (Medium) | Operador `J3D_OT_add_gem` (`j3d.add_gem`) en `core/gems.py`: Diamante Redondo 5mm (0.52ct) por defecto, 7 cortes, materiales BSDF e integración en Visor de Gemas (`ui/panels.py`). | 2026-09-01 |
| w17 | bug | Gemini 3.6 Flash (Medium) | Cambiado `spline.points.add(3)` por `spline.bezier_points.add(3)` en `core/ring.py`. Resuelto RuntimeError. | 2026-09-01 |
| w16 | bug | Gemini 3.6 Flash (Medium) | Refactor en `core/ring.py` con `object_data_add(context, obdata, operator=self)` y generadores nativos BMesh/Curve. Corregida alineación View. | 2026-09-01 |
| w15 | bug | Gemini 3.6 Flash (Medium) | Eliminada división por 1000 en `core/ring.py` e implementada escala 1 BU = 1 mm adaptable a `unit_scale`. Talla US 7 mide 17.32 BU. Resuelto `p8`. | 2026-09-01 |
| w14 | tarea | Gemini 3.6 Flash (Medium) | Script `pack_extension.py` en raíz que empaqueta únicamente la extensión de Blender en `dist/jeweler3dstudio-0.1.0.zip` (50 archivos, 444 KB), omitiendo entornos de dev. | 2026-09-01 |
| w13 | tarea | Gemini 3.6 Flash (Medium) | Integración de `AddObjectHelper` en `J3D_OT_create_ring_size` (`core/ring.py`) agregando `align`, `location` y `rotation` al Redo Panel en curvas y cilindros. | 2026-09-01 |
| w1 | tarea | Gemini 3.6 Flash (Medium) | Auditoría completa de extensión Blender 4.2+ (Manifiesto, UI context safety, registro modular). Corregido `core/__init__.py`. | 2026-08-26 |
| w2 | tarea | Gemini 3.6 Flash (Medium) | Generador paramétrico procedural de mallas 3D para gemas en `core/gems.py` con facetas reales (6 cortes), materiales BSDF y estimador de quilates. | 2026-08-27 |
| w3 | tarea | Gemini 3.6 Flash (Medium) | Visor modal interactivo de gemas, presets de tamaño rápido (1.0 a 6.5mm) y operador de edición `j3d.edit_gem`. | 2026-08-27 |
| w4 | tarea | Gemini 3.6 Flash (Medium) | Refactorización de UI a sub-paneles nativos de Blender (`bl_parent_id`), resolviendo el anidamiento visual de cajas. | 2026-08-27 |
| w5 | tarea | Gemini 3.6 Flash (Medium) | Visor modal emergente con `template_icon_view`, iconos PNG de cortes, recuadro de previsualización grande y botones OK/Cancel. | 2026-08-27 |
| w6 | tarea | Gemini 3.6 Flash (Medium) | Estructura de paneles independientes de nivel superior en la pestaña Jeweler 3D (idéntico a Jewelcraft). | 2026-08-27 |
| w7 | tarea | Gemini 3.6 Flash (Medium) | Simplificación de UI a 1 botón funcional ultra-simple por sección (Anillo, Gema, Cortador, Métricas). | 2026-08-27 |
| w8 | tarea | Gemini 3.6 Flash (Medium) | Eliminación del panel `VIEW3D_PT_j3d_gems` ("Gemas y Engastes") de `ui/panels.py`. | 2026-08-27 |
| w9 | tarea | Gemini 3.6 Flash (Medium) | Estructura limpia de 6 paneles y subpaneles con operador base `j3d.dummy_cube` para construcción progresiva. | 2026-08-27 |
| w10 | tarea | Gemini 3.6 Flash (Medium) | Arquitectura completa de 6 paneles y 13 sub-paneles en `ui/panels.py` + Registro del backlog `p1`-`p7` en `pendientes.md`. | 2026-08-27 |
| w11 | tarea | Gemini 3.6 Flash (Medium) | Configuración de `bl_options = {'DEFAULT_CLOSED'}` en sub-paneles excepto Visor de Gemas. | 2026-08-27 |
| w12 | tarea | Gemini 3.6 Flash (Medium) | Herramienta Talla implementada en `core/ring.py` (Tallas US 3.0-13.5 con medias tallas, default US 7.0, selector doble Curva/Cilindro y panel emergente de ajuste). | 2026-08-27 |

---

## 📋 Historial de Intentos

### [w27] Calibres y Quilates Comerciales Dinámicos por Corte

| Fecha | Agente | Intento | Resultado |
|---|---|---|---|
| 2026-09-14 | Gemini 3.7 Flash (Medium) | Implementación de calibres específicos para los 17 cortes x piedra, default a 1.0mm y factores volumétricos | en progreso |
