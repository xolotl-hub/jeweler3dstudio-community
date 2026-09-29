# Registro de Aprendizajes y Reglas (`overview/learning.md`)

Este archivo consolida las reglas, aprendizajes y propuestas de mejora identificadas durante el desarrollo y auditorías de código, priorizadas por impacto y aplicabilidad tanto para las reglas globales de `.agents` como para el skill de desarrollo de addons de Blender.

---

## 📌 Propuestas de mejora (Ordenadas por Prioridad)

*(Sin propuestas pendientes — todas las mejoras candidatas fueron auditadas y promovidas a los submódulos oficiales `.agents` y `.skill/python-blender-addon-agent-skill`)*

---

## 📜 Histórico de mejoras aplicadas

### python-agent-rules
- **[2026-09-22] Scaffold Incremental y Gobernanza Dinámica en $boot**: Creación determinista de archivos/carpetas faltantes desde `templates/` y delimitadores `<!-- SKILLS_START -->` / `<!-- SKILLS_END -->`.
- **[2026-09-22] Inicialización Determinista de Submódulos Git**: Protocolo de verificación e inicialización previa con `git submodule status`.
- **[2026-09-22] Carga Secuencial y Descubrimiento Modular Defensivo**: Validación con `hasattr(mod, "register")` en inicializadores de paquetes.
- **[2026-09-22] Suite de Tests Headless Automatizada**: Protocolo de validación por CLI en entornos CI y local.
- **Gestión Rigurosa de Unidades Físicas**: Conversiones de escala explícitas (milímetros a metros `mm / 1000.0`) y nombramiento descriptivo de variables (`inner_dia_mm`, `radius_m`).
- **Arquitectura Modular y Desacoplada**: UI estrictamente separada de los algoritmos y operadores core (`core/*.py` vs `ui/*.py`).
- **Prerrequisito Git Submodules**: Ejecución obligatoria de `git init` previo a vincular submódulos.

### python-blender-addon-agent-skill
- **[2026-09-22] PropertyGroup Unificado Obligatorio (No Stray Scene Props)**: Consolidación de todas las propiedades de escena en un único `PropertyGroup` (`Scene.j3d = PointerProperty(type=...)`).
- **[2026-09-22] Requisito de Integridad para Extensiones Oficiales (Zero-Stub Policy)**: Prohibición estricta de operadores stub, botones dummy o paneles incompletos.
- **[2026-09-22] Política Anti-Nagware y Cero Publicidad (No In-App Ads/Upsells)**: Prohibición de banners comerciales y cajas de promoción dentro del N-Panel; canalización exclusiva vía manifiesto.
- **[2026-09-22] Aislamiento Total de Namespaces y `bl_idname` Válidos**: Aislamiento estricto de identificadores de operadores, prefijos de clases y compatibilidad con Keymaps.
- **[2026-09-22] Simetría Rigurosa en Registro y Desregistro**: Limpieza simétrica de clases, handlers y eliminación del puntero `del bpy.types.Scene.<addon>`.
- **[2026-09-22] Polling Defensivo Obligatorio (`@classmethod poll`)**: Verificación de contexto en todos los operadores `bpy.types.Operator`.
- **[2026-09-22] Introspección Dinámica de Propiedades (`bl_rna.properties`)**: Patrón RNA de copia y serialización sin mapeos manuales rígidos.
- **[2026-09-22] Convención de Acceso a Props de Escena en `draw()`**: Asignación local de `props = context.scene.<addon>` para consumo directo en layout y paso de parámetros.
- **[2026-09-22] Acceso Defensivo a Capas y Atributos de Geometría**: Uso de `mesh.attributes` con `.get()` y fallback seguro `.new()`.
- **[2026-09-22] Comparación Explícita y Tolerancia Numérica en Álgebra Lineal**: Reglas de comparación por umbral `1e-5` y coerción a tuplas hashables.
- **[2026-09-22] Desacoplamiento entre Generación Geométrica y Transformación de Escena**: Generadores de malla en espacio local neutro Z=0 y asignación espacial en escena.
- **[2026-09-22] Patrón de Re-construcción Paramétrica Reactiva (Live State Rebuild)**: Preservación de modificadores y metadatos en edición en vivo.
- **[2026-09-22] Control de Nitidez No Destructiva (Edge Crease vs Densidad de Malla)**: Uso de pesos paramétricos de arista en lugar de sobre-subdivisión.
- **[2026-09-22] Distribución Elástica de Columnas en UI de Ancho Restringido**: Protección de anchos fijos numéricos en interfaces tabulares.
- **[2026-09-22] Parametrización por Cotas Relativas al Origen Local**: Definición de dimensiones relativas a Z=0 para evitar acumulación de tolerancias.
- **[2026-09-22] Empaquetado Multi-Tier por Exclusión Modular de Archivos**: Staging atómico de paquetes por exclusión de archivos.
- **Primitivos Nativos de Blender**: Preferir operadores nativos (`primitive_bezier_circle_add`, `primitive_cylinder_add`) sobre construcciones manuales BMesh complejas cuando aplique.
- **Escalado y `transform_apply`**: Instanciar primitivos con radio base 1.0, aplicar escala en metros y congelar inmediatamente con `bpy.ops.object.transform_apply(scale=True)`.
- **Ventana de Re-Ajuste (Redo Panel)**: Configurar `bl_options = {'REGISTER', 'UNDO'}` en clases `bpy.types.Operator`.
- **Control de Ruido Visual en Subpaneles**: Configurar `bl_options = {'DEFAULT_CLOSED'}` en subpaneles (`bl_parent_id`).
- **Context Safety en UI**: Evitar asignar `col.operator_context` directamente en elementos de `UILayout`.
- **Manifiesto Blender 4.2+**: Uso de `blender_manifest.toml` con estructura plana de empaquetado `.zip`.
