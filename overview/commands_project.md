# ⚡ Comandos Disponibles en Este Proyecto

> **Generado automáticamente durante `$boot`.**
> Este archivo es una **copia de referencia** — no editar manualmente.
> Fuente de verdad: `.agents/core/commands.md` y `.skill/[nombre-skill]/core/commands.md`.

---

## 🧠 Comandos del Core (`.agents/`)

| Comando | Acción |
|---|---|
| `$boot` | Bootstrap completo del proyecto |
| `$status` | Mostrar estado actual en resumen |
| `$work [descripción]` | Registrar nueva tarea o bug |
| `$archi` | Actualizar arquitectura viva (diagramas Mermaid) |
| `$learn [texto]` | Registrar aprendizaje general en `overview/learning.md` |
| `$learnagnostico [texto]` | Abstraer a términos genéricos antes de registrar |
| `$close` | Protocolo de cierre de sesión con sincronización de rastreadores |

---

<!-- SKILLS_START -->
## 🎨 Skill: `python-blender-addon-agent-skill` (`.skill/python-blender-addon-agent-skill`)

| Comando | Acción | Descripción |
|---|---|---|
| `$blender` | Bootstrap | Activa la skill de desarrollo de Addons para Blender 4.2+ |
| `$blender:audit` | Auditoría | Diagnóstico de ciclo de vida, manifiesto, UI y context safety |
| `$blender:manifest` | Generación | Emite plantilla oficial de `bl_manifest.toml` |
| `$blender:operator` | Generación | Emite plantilla de `bpy.types.Operator` modal seguro |
| `$blender:panel` | Generación | Emite plantilla de `bpy.types.Panel` (N-Panel) responsivo |

## 🌐 Skill: `i18n-agent-skill` (`.skill/i18n-agent-skill`)

| Comando | Acción | Descripción |
|---|---|---|
| `$i18n` | Bootstrap | Inicializa el contexto operativo de internacionalización |
| `$i18n:audit` | Auditoría | Escanea llaves faltantes, cadenas no traducidas y paridad |
| `$i18n:extract` | Extracción | Extrae cadenas hardcodeadas de UI a archivos de idioma |
| `$i18n:model` | Modelos | Audita modelos de datos: verifica diccionarios y fallback |
| `$i18n:tracker` | Tracker | Genera o actualiza tracker en `overview/trackers/i18n_tracker.md` |
| `$i18n:validate` | Validación | Verifica compilación y pruebas antes de cerrar |
<!-- SKILLS_END -->
