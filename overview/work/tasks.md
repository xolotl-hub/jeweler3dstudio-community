# Tarea Activa (`overview/work/tasks.md`)
 
> Espacio de trabajo activo para la tarea en ejecución. Escribir aquí antes de modificar código.

## 🎯 Tarea Activa: w58 — Normalización UI Base Inglés (Requisito Blender Extensions)

- **ID:** w58
- **Descripción:** Normalizar todos los labels, descripciones de operadores, menús Shift+A, propiedades y paneles de la UI al inglés canónico base, y actualizar catálogo i18n (`ui/i18n.py`) para soporte de traducción automático vía `bpy.app.translations`.
- **Hipótesis:** Requisito obligatorio para extensions.blender.org.

## 🏷️ Clasificación

- [ ] **Problema (Bug):** Comportamiento inesperado o fallo funcional.
- [x] **Mejora (Feature):** Nueva capacidad o refactor de valor.
- [ ] **Deuda / Refactor:** Limpieza de código o estructuración técnica.

## 🛣️ Rutas de Trabajo y Posibles Soluciones

1. Refactorizar `core/ring.py`, `core/gems.py`, `core/cutters.py`, `ui/menus.py` y `ui/panels.py` con cadenas canónicas en inglés.
2. Sincronizar catálogo `ui/i18n.py` con llaves en inglés y traducciones completas en español (`es_ES`/`es`) y francés (`fr_FR`).
3. Empaquetar y verificar compilación de Community y Pro (`tools/pack_zip/pack_community.py`).









