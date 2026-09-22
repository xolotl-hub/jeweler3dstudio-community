# Tarea Activa (`overview/work/tasks.md`)
 
> Espacio de trabajo activo para la tarea en ejecución. Escribir aquí antes de modificar código.

## 🎯 Tarea Activa: w56 — Incorporar website y Metadatos en blender_manifest.toml

- **ID:** w56
- **Descripción:** Agregar `website` y metadatos canónicos a `blender_manifest.toml` y en la función `transform_manifest` de `tools/pack_zip/pack_common.py`.
- **Hipótesis:** Metadatos requeridos para aprobación en extensions.blender.org.

## 🏷️ Clasificación

- [ ] **Problema (Bug):** Comportamiento inesperado o fallo funcional.
- [x] **Mejora (Feature):** Nueva capacidad o refactor de valor.
- [ ] **Deuda / Refactor:** Limpieza de código o estructuración técnica.

## 🛣️ Rutas de Trabajo y Posibles Soluciones

1. Actualizar `blender_manifest.toml` en raíz con `website = "https://github.com/xolotl-hub/jeweler-3d-studio"`.
2. Actualizar `transform_manifest` en `tools/pack_zip/pack_common.py` inyectando `website` para cada tier (`jeweler3dstudio-community`, etc.).
3. Ejecutar `python3 tools/pack_zip/pack_community.py` para sincronizar y publicar a GitHub.








