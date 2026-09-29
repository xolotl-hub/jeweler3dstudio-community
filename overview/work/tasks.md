# Tarea Activa (`overview/work/tasks.md`)
 
> Espacio de trabajo activo para la tarea en ejecución. Escribir aquí antes de modificar código.

## 🎯 Tarea Activa: w62 — Auditoría Integral de Deuda Técnica y Mejoras

- **ID:** `w62`
- **Descripción:** Escaneo y auditoría exhaustiva del 100% de la base de código del proyecto contra las nuevas directrices de Blender Extensions (`blender_review_guidelines_checkpoints.md`), patrones RNA/álgebra lineal, modularidad (<250L) y consistencia en pipelines multi-tier.
- **Hipótesis:** Existen oportunidades de refactor en módulos monolíticos residuales (`cutters.py`, `gems.py`, `ring.py`), posibles faltantes en tooltips/RNA annotations o shims innecesarios, y enriquecimiento de pendientes con tareas de alto valor.

## 🏷️ Clasificación

- [ ] **Problema (Bug):** Comportamiento inesperado o fallo funcional.
- [x] **Mejora (Feature):** Nueva capacidad o refactor de valor.
- [x] **Deuda / Refactor:** Limpieza de código o estructuración técnica.

## 🛣️ Rutas de Trabajo y Posibles Soluciones

1. **Escaneo de Límite de Líneas (<250L):** Identificar archivos que superen 250L y planificar su modularización atómica.
2. **Auditoría de Normativa Blender Extensions (Checkpoints):**
   - Verificar simetría `register()` / `unregister()` en todos los submódulos.
   - Auditar `description` en todos los `bpy.props` y `bpy.types.Operator`.
   - Verificar polling `@classmethod poll` en todos los operadores.
   - Validar uso del `PropertyGroup` unificado (`scene.j3d`) en todos los métodos `draw()`.
   - Verificar que no existan shims o llamadas deprecadas (`bl_info`, imports residuales).
3. **Auditoría de Scripts y Pipelines:**
   - Comprobar herramientas en `tools/` y tests en `tests/`.
4. **Actualización de Registros:**
   - Sincronizar `overview/work/deuda_tecnica.md`, `overview/work/pendientes.md`, `overview/work.md`, `overview/work_review.md` y `overview/session.md`.

