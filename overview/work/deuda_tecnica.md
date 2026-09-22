# Deuda Técnica (`overview/work/deuda_tecnica.md`)

> Errores, refactors pendientes o problemas no resueltos a nivel de código, ordenados por prioridad de impacto.

## 🔴 Prioridad Alta (Impacto Crítico / Bloqueante)

| ID | Ubicación / Componente | Descripción de la Deuda | Impacto |
|---|---|---|---|
| d9 | `core/prongs.py` (104L) | Módulo stub no funcional — requiere implementar garras paramétricas procedurales (redondas, V/chevron, talón) para engastes. | Módulo incompleto / UI bloqueada. |
| d10 | `core/pave.py` (72L) | Módulo stub no funcional — requiere implementar distribución de micro-gemas y micro-garras sobre curvas/superficies. | Módulo incompleto / UI bloqueada. |

## 🟡 Prioridad Media (Impacto Moderado / Mantenibilidad)

| ID | Ubicación / Componente | Descripción de la Deuda | Impacto |
|---|---|---|---|
| d8 | `core/cutters.py` (822L) | Módulo supera límite de 250L — separar motor geométrico BMesh (`cutters_core.py`), generadores de siluetas 2D y operadores/UI de edición en vivo. | Mantenibilidad / Escalabilidad. |
| d5 | `core/gems.py` (746L) | Módulo supera límite de 250L — separar motor geométrico y cálculo volumétrico de operadores de inserción y previews. | Mantenibilidad. |
| d7 | `core/ring.py` (588L) | Módulo supera límite de 250L — separar generador de tallas/curvas de perfiles de metal y operadores. | Mantenibilidad. |
| d2 | `ui/panels.py` (556L) | Archivo supera límite de 250L — candidato a refactor dividiendo por subpaneles temáticos en `ui/`. | Mantenibilidad. |

## 🟢 Prioridad Baja (Mejora Menor / Estilo)

| ID | Ubicación / Componente | Descripción de la Deuda | Impacto |
|---|---|---|---|
| d6 | `tools/generate_gem_icons.py` (497L) | Script de generación supera 250L — modularizar por estilo/corte. | Dev tooling. |
| d4 | `overview/work.md` | Filas de historial con líneas vacías entre entradas — inconsistencia de formato. | Visual / menor. |

---

## ✅ Completados (Historial)

| ID | Ubicación / Componente | Descripción de la Deuda | Solución Aplicada | Agente | Fecha |
|---|---|---|---|---|---|
| d1 | `core/gems.py` / `J3D_OT_add_gem` | Geometría del diamante incompleta: solo pabellón (cono primitivo). | `create_round_brilliant_mesh()` procedural 57 facetas (corona + filetín + pabellón). | Gemini 3.7 Flash (Medium) | 2026-09-08 |
| d3 | `core/gems.py` | Funciones `create_gem_mesh`, `GEM_TYPES`, `CUT_ITEMS`, `GEM_TYPE_ITEMS` no usadas. | Eliminadas en refactor; reemplazadas por `CUT_DEFS` + `create_round_brilliant_mesh`. | Composer | 2026-09-08 |
| - | `ui/panels.py` | `icon='GEM'` no existe en Blender 5.2 — causaba crash silencioso en draw() ocultando botón. | Cambiado a `icon='MESH_ICOSPHERE'`. | Claude Sonnet 4.6 (Thinking) | 2026-09-01 |
| - | `core/ring.py` | `spline.points.add()` en spline BEZIER lanzaba RuntimeError. | Cambiado a `spline.bezier_points.add()`. | Gemini 3.6 Flash (Medium) | 2026-09-01 |
