# Tarea Activa (`overview/work/tasks.md`)
 
> Espacio de trabajo activo para la tarea en ejecución. Escribir aquí antes de modificar código.

## 🎯 Tarea Activa: w55 — Commit y Push por Defecto en pack_community.py

- **ID:** w55
- **Descripción:** Configurar `tools/pack_zip/pack_community.py` para que al ejecutarse realice automáticamente el ciclo completo (generar ZIP + commit y push a `jeweler3dstudio-community`) sin requerir flags adicionales, agregando `--no-publish` para saltar el push si se desea.
- **Hipótesis:** El script dedicado de Community debe publicar por defecto.

## 🏷️ Clasificación

- [ ] **Problema (Bug):** Comportamiento inesperado o fallo funcional.
- [x] **Mejora (Feature):** Nueva capacidad o refactor de valor.
- [ ] **Deuda / Refactor:** Limpieza de código o estructuración técnica.

## 🛣️ Rutas de Trabajo y Posibles Soluciones

1. Modificar `main()` en `tools/pack_zip/pack_community.py`:
   - Publicar automáticamente a menos que se use `--no-publish`.
2. Probar la ejecución directa de `python3 tools/pack_zip/pack_community.py` y verificar commit y push.







