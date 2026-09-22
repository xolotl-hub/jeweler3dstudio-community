# Deuda Técnica (`overview/work/deuda_tecnica.md`)

> Errores, refactors pendientes o problemas no resueltos a nivel de código, ordenados por prioridad de impacto.

## 🔴 Prioridad Alta (Impacto Crítico / Bloqueante o Bugs Latentes)

| ID | Ubicación / Componente | Descripción de la Deuda | Impacto |
|---|---|---|---|
| d9 | `core/prongs.py` (104L) | Módulo stub no funcional — requiere implementar garras paramétricas procedurales (redondas, V/chevron, talón) para engastes (`p14`). | Módulo incompleto / UI bloqueada. |
| d10 | `core/pave.py` (90L) | Módulo stub no funcional — requiere implementar distribución de micro-gemas y micro-garras sobre curvas/superficies (`p17`). | Módulo incompleto / UI bloqueada. |

## 🟡 Prioridad Media (Impacto Moderado / Mantenibilidad & Monolitos)

| ID | Ubicación / Componente | Descripción de la Deuda | Impacto |
|---|---|---|---|
| d8 | `core/cutters.py` (822L) | Módulo supera límite de 250L — separar motor geométrico BMesh (`cutters_core.py`), generadores de siluetas 2D y operadores/UI de edición en vivo. Bandera global `_UPDATING_CUTTER` no es context/thread-safe. | Mantenibilidad / Robustez. |
| d5 | `core/gems.py` (746L) | Módulo supera límite de 250L — separar motor geométrico y cálculo volumétrico de operadores de inserción, swap y previews. | Mantenibilidad. |
| d7 | `core/ring.py` (588L) | Módulo supera límite de 250L — separar generador de tallas/curvas de perfiles de metal y operadores. | Mantenibilidad. |
| d14 | `core/gems.py` / `ui/panels/` | Calibres elongados (Oval, Pear, Marquise, Baguette) operan con un solo eje; falta soporte `L x W` (`p10`). | Precisión física y volumétrica. |
| d15 | `core/gems.py` | Presets de calibres (`j3d_gem_size_preset`) conservan clave al cambiar de corte si no se resetea dinámicamente (`p11`). | Glitch en N-Panel. |

## 🟢 Prioridad Baja (Mejora Menor / Estilo & Tooling)

| ID | Ubicación / Componente | Descripción de la Deuda | Impacto |
|---|---|---|---|
| d6 | `tools/generate_gem_icons.py` (497L) | Script de generación supera 250L — modularizar por estilo/corte. | Dev tooling. |
| d16 | `core/metrics.py` (84L) / `ui/dialogs.py` (98L) | Módulos desconectados del registro oficial — conectar a UI cuando se habilite panel de Ficha Técnica (`p6`). | Integración. |
| d4 | `overview/work.md` | Filas de historial con líneas vacías entre entradas — inconsistencia de formato. | Visual / menor. |

---

## ✅ Completados (Historial)

| ID | Ubicación / Componente | Descripción de la Deuda | Solución Aplicada | Agente | Fecha |
|---|---|---|---|---|---|
| d2 | `ui/panels.py` (753L) | Monolito de UI N-Panel superaba ampliamente 250L. | Modularizado en subpaquete `ui/panels/` con submódulos temáticos (`ring.py`, `gems.py`, `gem_map.py`, `cutters.py`, `stubs.py`, `__init__.py`), todos estrictamente < 250L. Simplificado pipeline de exclusión en `pack_community.py`. | Gemini 3.7 Flash (Medium) | 2026-09-22 |
| d13 | `core/gem_data.py` (2589L) | Monolito de mallas normalizadas de 17 cortes. | Modularizado en subpaquete `core/gem_data/` (5 familias de corte: `_stepped`, `_fancy`, `_octagon`, `_round`, `_trillion` + `__init__.py` con reexport de `GEM_MESH_DATA`). Mantiene retrocompatibilidad 100%. | Gemini 3.7 Flash (Medium) | 2026-09-22 |
| d11 | `ui/gizmos.py` | `target_set_prop("matrix", ...)` inválido en Blender 4.2+ y función `unregister()` duplicada. | Eliminada llamada no soportada y unificado `unregister()` a bloque simétrico limpio. Resuelve `flag-w22`. | Gemini 3.7 Flash (Medium) | 2026-09-21 |
| d12 | `core/prongs.py` | Función `unregister()` duplicada y llamada errónea a `register_class` dentro del desregistro. | Unificado `unregister()` y eliminada llamada residual de registro. | Gemini 3.7 Flash (Medium) | 2026-09-21 |
| d1 | `core/gems.py` / `J3D_OT_add_gem` | Geometría del diamante incompleta: solo pabellón (cono primitivo). | `create_round_brilliant_mesh()` procedural 57 facetas (corona + filetín + pabellón). | Gemini 3.7 Flash (Medium) | 2026-09-08 |
| d3 | `core/gems.py` | Funciones `create_gem_mesh`, `GEM_TYPES`, `CUT_ITEMS`, `GEM_TYPE_ITEMS` no usadas. | Eliminadas en refactor; reemplazadas por `CUT_DEFS` + `create_round_brilliant_mesh`. | Composer | 2026-09-08 |
| - | `ui/panels/` | `icon='GEM'` no existe en Blender 5.2 — causaba crash silencioso en draw() ocultando botón. | Cambiado a `icon='MESH_ICOSPHERE'`. | Claude Sonnet 4.6 (Thinking) | 2026-09-01 |
| - | `core/ring.py` | `spline.points.add()` en spline BEZIER lanzaba RuntimeError. | Cambiado a `spline.bezier_points.add()`. | Gemini 3.6 Flash (Medium) | 2026-09-01 |


