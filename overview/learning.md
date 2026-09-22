# Registro de Aprendizajes y Reglas (`overview/learning.md`)

Este archivo consolida las reglas, aprendizajes y propuestas de mejora identificadas durante el desarrollo, estructurado según la especificación canónica de `.agents`.

## 📌 Propuestas de mejora

- **[rules]** `git init` es un prerrequisito obligatorio antes de ejecutar `git submodule add` en repositorios recién creados.
- **[rules]** La carga secuencial de `core/__init__.py` debe usar `hasattr(mod, "register")` / `hasattr(mod, "unregister")` para no fallar en módulos helper sin clases `bpy`.
- **[rules]** Durante `$boot`, la detección de `.skill/` debe actualizar `overview/commands_project.md` de forma determinista entre los delimitadores `<!-- SKILLS_START -->` y `<!-- SKILLS_END -->`.
- **[rules]** Durante `$boot`, `overview/README.md` debe transformarse desde la plantilla para describir la gobernanza viva del proyecto cliente, en lugar de copiar literalmente el texto instructivo de inicialización de `.agents/templates/README.md`.
- **[rules]** **Validación Headless en Tiempo de Ejecución**: Ejecutar validación agnóstica mediante el intérprete o CLI disponible en el sistema del host antes del cierre, verificando la compatibilidad real del entorno sin asumir versiones estáticas.
- **[python-blender-addon-agent-skill]** **Acceso Defensivo a Capas y Atributos de Geometría**: Nunca acceder a capas de malla asumiendo una versión estática de API. Usar introspección segura y fallback resiliente (`getattr`, `.get()` con fallback a `.new()`) para soportar cambios en el sistema de atributos del motor.
- **[python-blender-addon-agent-skill]** **Comparación Explícita y Tolerancia Numérica**: Tratar los objetos de álgebra lineal (vectores, matrices, ángulos de Euler) como tipos no primitivos. Comparar siempre mediante coerción explícita (`tuple(...)`) o umbral de tolerancia (`abs(x) < 1e-5`), evitando operadores de igualdad directa que dependen de la implementación interna de bindings C/C++.
- **[python-blender-addon-agent-skill]** **Desacoplamiento entre Generación Geométrica y Transformación de Escena**: Mantener los generadores de malla en coordenadas locales puras y delegar la orientación/posición a transformaciones espaciales explícitas en la escena, evitando anclar rotaciones fijas en los algoritmos de topología.
- **[rules]** **Patrón de Re-construcción Paramétrica Reactiva (Live State Rebuild)**: Desacoplar los generadores procedurales de los operadores de inserción almacenando parámetros en metadatos del objeto. Esto permite la edición en caliente (*in-place rebuild*) desde cualquier vista o panel de propiedades preservando transformaciones de escena y jerarquías sin destructividad.
- **[rules]** **Control de Nitidez No Destructiva (Edge Crease vs Densidad de Malla)**: Para geometrías procedurales destinadas a operaciones booleanas o de ensamble, utilizar pesos de arista paramétricos (*Edge Crease*) en vez de aumentar la densidad de subdivisiones estáticas, garantizando bajo coste computacional y precisión de aristas vivas.
- **[rules]** **Distribución Elástica de Columnas en Contenedores de Ancho Restringido**: En interfaces tabulares compactas, proteger el espacio de las columnas numéricas críticas y unidades fijas, forzando a que las columnas de texto descriptivo absorban la compresión elástica para evitar truncamientos numéricos.
- **[rules]** **Parametrización por Cotas Relativas al Origen Local**: En piezas de múltiples zonas o secciones, definir las alturas y radios de cada nivel respecto al plano neutro local (Z=0), permitiendo la calibración milimétrica independiente y evitando la propagación de errores acumulativos en la cadena dimensional.
- **[python-blender-addon-agent-skill]** Exigir `@classmethod poll()` en todo `bpy.types.Operator`, incluyendo operadores de diálogo modal o exportadores I/O.

---

## 📜 Histórico de mejoras aplicadas

### python-agent-rules
- **Gestión Rigurosa de Unidades Físicas**: Al realizar conversiones de escala entre sistemas de unidades (ej. milímetros a metros `mm / 1000.0`), verificar el vector de dimensión resultante y nombrar variables de dimensión explícitamente (`inner_dia_mm`, `radius_m`).
- **Arquitectura Modular y Desacoplada**: Mantener estrictamente separada la UI de los algoritmos y operadores core (`core/*.py` vs `ui/*.py`). Registrar y limpiar propiedades globales de manera determinista.

### python-blender-addon-agent-rules
- **Primitivos Nativos de Blender**: Preferir el uso de operadores nativos (`bpy.ops.curve.primitive_bezier_circle_add`, `bpy.ops.mesh.primitive_cylinder_add`) sobre construcciones manuales con BMesh.
- **Escalado de Objetos y `transform_apply`**: Instanciar primitivos con radio base 1.0, aplicar escala real en metros mediante `obj.scale = (r_m, r_m, z_m)` y congelar transformaciones inmediatamente ejecutando `bpy.ops.object.transform_apply(scale=True)`.
- **Ventana de Re-Ajuste (Redo Panel)**: Configurar siempre `bl_options = {'REGISTER', 'UNDO'}` en clases `bpy.types.Operator`.
- **Control de Ruido Visual en Subpaneles**: Configurar `bl_options = {'DEFAULT_CLOSED'}` en subpaneles (`bl_parent_id`).
- **Context Safety en UI**: Evitar asignar `col.operator_context` directamente en elementos de `UILayout`.
- **Manifiesto y Empaquetado**: Sustituir `bl_info` en `__init__.py` por `blender_manifest.toml` en Blender 4.2+. Estructura plana al empaquetar la extensión en `.zip`.

### 📌 Histórico de aprendizajes generales
- `git init` es un prerrequisito obligatorio antes de ejecutar `git submodule add` en repositorios recién creados.
- La carga secuencial de `core/__init__.py` debe usar `hasattr(mod, "register")` / `hasattr(mod, "unregister")` para no fallar en módulos helper sin clases `bpy`.
- Exigir `@classmethod poll()` en todo `bpy.types.Operator`, incluyendo operadores de diálogo modal o exportadores I/O.
