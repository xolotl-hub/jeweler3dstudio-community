# Registro de Aprendizajes y Reglas (`overview/learning.md`)

Este archivo consolida las reglas, aprendizajes y propuestas de mejora identificadas durante el desarrollo y auditorías de código, priorizadas por impacto y aplicabilidad tanto para las reglas globales de `.agents` como para el skill de desarrollo de addons de Blender.

---

## 📌 Propuestas de mejora (Ordenadas por Prioridad)

### 🔴 Alta Prioridad (Requisitos Críticos / Normativa Blender Extensions & Core)

1. **[python-blender-addon-agent-skill] PropertyGroup Unificado Obligatorio (No Stray Scene Props)**:
   - Nunca registrar propiedades sueltas directamente en `bpy.types.Scene` (`Scene.mi_prop = EnumProperty(...)`).
   - Consolidar **todas** las propiedades de escena del addon en un único `bpy.types.PropertyGroup` (ej. `J3D_SceneSettings`) y registrarlo como `bpy.types.Scene.j3d = PointerProperty(type=J3D_SceneSettings)`.
   - Requisito estricto de revisión oficial de `extensions.blender.org` para evitar colisiones y desorden en la UI global.

2. **[python-blender-addon-agent-skill] Requisito de Integridad para Extensiones Oficiales (Zero-Stub Policy)**:
   - Para publicaciones en `extensions.blender.org`, excluir estrictamente operadores stub (`dummy_cube`), botones placeholder o paneles incompletos.
   - Todo paquete público debe contener exclusivamente funciones 100% implementadas, funcionales y verificadas.

3. **[python-blender-addon-agent-skill] Política Anti-Nagware y Publicidad (No In-App Ads/Upsells)**:
   - Cumplir rigurosamente las pautas oficiales prohibiendo banners de compra, promociones cruzadas invasivas ("promo boxes" de BlenderMarket/Gumroad) o nag screens dentro del N-Panel.
   - Toda presencia comercial o enlaces a documentación deben canalizarse exclusivamente mediante los campos estándar del manifiesto (`website`, `documentation`, `tracker` en `blender_manifest.toml`).

4. **[python-blender-addon-agent-skill] Aislamiento Total de Namespaces y `bl_idname` Válidos**:
   - En extensiones y tiers coexistentes, aislar estrictamente `manifest id`, `bl_category`, prefijos de clases, identificadores de operadores `bl_idname` (ej. `j3d.operador`, sin prefijos inventados ajenos) y propiedades en escena (`scene.j3d.*`).
   - Evitar namespaces del sistema (`wm.`) a menos que sean operadores globales de ventana, y garantizar que `bl_idname` sea compatible con el sistema de atajos de teclado de Blender.

5. **[python-blender-addon-agent-skill] Simetría Rigurosa en Registro y Desregistro**:
   - Garantizar un ciclo de vida simétrico e idéntico en `register()` y `unregister()`.
   - Limpiar todas las clases, subpaneles y punteros (`del bpy.types.Scene.j3d`), evitando llamadas cruzadas erróneas y purgando APIs obsoletas no soportadas en Blender 4.2+.

6. **[python-blender-addon-agent-skill] Polling Defensivo Obligatorio (`@classmethod poll`)**:
   - Implementar `@classmethod poll(cls, context)` en todos los operadores `bpy.types.Operator` que dependan de un modo específico (Object Mode vs Edit Mode), selecciones activas o tipos de datos concretos, previniendo crashes o comportamientos anómalos.

7. **[rules] Validación y Suite de Tests Headless en CI/Entorno Local**:
   - Incluir scripts de prueba headless ejecutables vía CLI (`blender --background --python tests/run_suite.py`) que verifiquen registro limpio, ejecución de operadores clave y estabilidad topológica antes de empaquetar o lanzar versiones.

---

### 🟡 Media Prioridad (Calidad de Código, Mantenibilidad y Buenas Prácticas)

8. **[python-blender-addon-agent-skill] Introspección Dinámica de Propiedades (`bl_rna.properties`)**:
   - En funciones de serialización, copia/pega o sincronización de parámetros entre objetos/capas, usar introspección dinámica mediante `rna_type.properties` / `bl_rna.properties` (filtrando `is_readonly` e internas) en lugar de mapeos manuales extensos de código repetitivo ("brute-force manual mapping").

9. **[python-blender-addon-agent-skill] Convención de Acceso a Props de Escena en `draw()`**:
   - En `draw(self, context)`, asignar `j3d = context.scene.j3d` como variable local al inicio del método y consumir `j3d.prop` en todas las llamadas a `layout.prop()` y parámetros de operadores (`op.param = j3d.prop`).

10. **[python-blender-addon-agent-skill] Acceso Defensivo a Capas y Atributos de Geometría**:
    - Nunca acceder a capas de malla asumiendo una versión estática de API. Usar introspección segura y fallback resiliente (`getattr`, `.get()` con fallback a `.new()`) para soportar cambios en el sistema de atributos del motor.

11. **[python-blender-addon-agent-skill] Comparación Explícita y Tolerancia Numérica**:
    - Tratar objetos de álgebra lineal (vectores, matrices, ángulos de Euler) como tipos no primitivos. Comparar siempre mediante coerción explícita (`tuple(...)`) o umbral de tolerancia (`abs(x) < 1e-5`), evitando operadores de igualdad directa que dependen de bindings C/C++.

12. **[python-blender-addon-agent-skill] Desacoplamiento entre Generación Geométrica y Transformación de Escena**:
    - Mantener los generadores de malla en coordenadas locales puras (Z=0 / origen neutro) y delegar la orientación/posición a transformaciones espaciales explícitas en la escena.

13. **[rules] Patrón de Re-construcción Paramétrica Reactiva (Live State Rebuild)**:
    - Desacoplar generadores procedurales de operadores de inserción almacenando parámetros en metadatos del objeto, permitiendo edición en caliente (*in-place rebuild*) desde cualquier panel preservando jerarquías y modificadores.

14. **[rules] Carga Secuencial y Descubrimiento Modular Defensivo**:
    - La carga secuencial de módulos en `core/__init__.py` o `ui/__init__.py` debe usar `hasattr(mod, "register")` / `hasattr(mod, "unregister")` para no fallar en módulos de utilidades o algoritmos puros sin clases `bpy`.

---

### 🟢 Baja Prioridad (Estilo, Ergonomía de UI y Optimización)

15. **[rules] Control de Nitidez No Destructiva (Edge Crease vs Densidad de Malla)**:
    - Para geometrías procedurales destinadas a operaciones booleanas o de ensamble, utilizar pesos de arista paramétricos (*Edge Crease*) en vez de aumentar la densidad de subdivisiones estáticas.

16. **[rules] Distribución Elástica de Columnas en Contenedores de Ancho Restringido**:
    - En interfaces tabulares compactas, proteger el espacio de las columnas numéricas críticas y unidades fijas, forzando a que las columnas descriptivas absorban la compresión elástica.

17. **[rules] Parametrización por Cotas Relativas al Origen Local**:
    - Definir alturas y radios respecto al plano neutro local (Z=0), permitiendo calibración milimétrica independiente y evitando acumulación de tolerancias.

18. **[rules] Empaquetado Multi-Tier por Exclusión Modular de Archivos**:
    - En pipelines de compilación con múltiples ediciones (Community vs PRO), modularizar capacidades en submódulos atómicos y filtrar mediante exclusión de archivos (`unlink()`) en el staging de empaquetado.

19. **[rules] Inicialización Determinista de Submódulos Git**:
    - `git init` es un prerrequisito obligatorio antes de ejecutar `git submodule add` en repositorios recién creados.

20. **[rules] Gobernanza Dinámica en `$boot`**:
    - Durante `$boot`, transformar `overview/README.md` desde la plantilla para describir la gobernanza viva del proyecto cliente, y actualizar `overview/commands_project.md` de forma determinista entre los delimitadores `<!-- SKILLS_START -->` y `<!-- SKILLS_END -->`.

---

## 📜 Histórico de mejoras aplicadas

### python-agent-rules
- **Gestión Rigurosa de Unidades Físicas**: Conversiones de escala explícitas (milímetros a metros `mm / 1000.0`) y nombramiento descriptivo de variables (`inner_dia_mm`, `radius_m`).
- **Arquitectura Modular y Desacoplada**: UI estrictamente separada de los algoritmos y operadores core (`core/*.py` vs `ui/*.py`).
- **Prerrequisito Git Submodules**: Ejecución obligatoria de `git init` previo a vincular submódulos.

### python-blender-addon-agent-rules
- **Primitivos Nativos de Blender**: Preferir operadores nativos (`primitive_bezier_circle_add`, `primitive_cylinder_add`) sobre construcciones manuales BMesh complejas cuando aplique.
- **Escalado y `transform_apply`**: Instanciar primitivos con radio base 1.0, aplicar escala en metros y congelar inmediatamente con `bpy.ops.object.transform_apply(scale=True)`.
- **Ventana de Re-Ajuste (Redo Panel)**: Configurar `bl_options = {'REGISTER', 'UNDO'}` en clases `bpy.types.Operator`.
- **Control de Ruido Visual en Subpaneles**: Configurar `bl_options = {'DEFAULT_CLOSED'}` en subpaneles (`bl_parent_id`).
- **Context Safety en UI**: Evitar asignar `col.operator_context` directamente en elementos de `UILayout`.
- **Manifiesto Blender 4.2+**: Uso de `blender_manifest.toml` con estructura plana de empaquetado `.zip`.
