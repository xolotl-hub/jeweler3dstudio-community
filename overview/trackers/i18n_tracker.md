# 📋 Tracker de Internacionalización — `i18n_tracker.md`

> **Ruta canónica**: `overview/trackers/i18n_tracker.md`
> **Generado por**: `i18n-agent-skill` (`$i18n`)
> **Ecosistema**: Blender 4.2+ Extension (`bpy.app.translations`)
> **Estrategia**: Fallback Progresivo (`bpy.app.translations` EN Base → ES / FR / ZH)
> **Política de Compilación**: Zero-Breakage — Validar registro de addon y operadores en Blender headless.

---

## 📌 Fase 1: UI Keys & Menús Globales (Blender UI)
*Extracción y registro de cadenas en paneles N-Panel, Menús Shift+A y diálogos modal.*

- [x] **UI-01**: Crear módulo central de traducciones `ui/i18n.py` con diccionario canónico para `bpy.app.translations`.
- [x] **UI-02**: Mapear cadenas y labels de Menús Shift+A (`ui/menus.py`).
- [x] **UI-03**: Mapear títulos, labels y botones de los 6 paneles y 13 subpaneles (`ui/panels.py`).
- [x] **UI-04**: Mapear mensajes de reporte (`self.report({'INFO'}, ...)`), descripciones de operadores y tooltips.
- [x] ✅ **Validación Fase 1**: Registro limpio en `bpy.app.translations.register()` y test headless Blender PASS.

---

## 📌 Fase 2: Model & Metadata Fallback Engine
*Estandarización de nombres de cortes (17 cuts), perfiles de metal y materiales en inglés base con diccionario ES.*

- [ ] **MOD-01**: Estandarizar `RING_PROFILE_ITEMS` en `core/ring.py` (Base EN + traducción ES).
- [ ] **MOD-02**: Estandarizar `CUT_DEFS` y nombres de gemas en `core/gem_data.py` / `core/gems.py`.
- [ ] **MOD-03**: Estandarizar nombres de zonas y parámetros en `core/cutters.py`.
- [ ] **MOD-04**: Estandarizar metales preciosos y densidades en `core/metrics.py`.
- [ ] ✅ **Validación Fase 2**: Ejecución de operadores con nombres traducidos sin romper `j3d_type` ni props internas.

---

## 📌 Fase 3: Migración Progresiva de Idiomas Adicionales
*Ampliación a otros idiomas clave del mercado de joyería 3D (Francés, Chino, etc.).*

- [ ] **LANG-01**: Soporte completo Español (`es`).
- [ ] **LANG-02**: Soporte Francés (`fr_FR`).
- [ ] **LANG-03**: Soporte Chino Simplificado (`zh_HANS`).
- [ ] ✅ **Validación Fase 3**: Verificación de cobertura y paridad de llaves.

---

## 🛡️ Checklist Global de Zero-Breakage

- [ ] Pruebas headless de Blender (`scratch/test_menus.py` y registro) pasando en verde antes de cerrar bloque.
- [ ] Las claves de propiedades internas (`obj["j3d_type"]`, enum keys como `"MEDIA_CANA"`, `"ROUND"`) permanecen inmutables.
- [ ] ZIP empaquetado y verificado en `dist/`.
