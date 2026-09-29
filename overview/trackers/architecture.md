# Arquitectura — Jeweler 3D Studio
> Última actualización: 2026-09-22 · Cobertura: 100 %

---

## Diagrama general (capas)

```mermaid
graph TD
    BL["Blender 4.2+ Runtime"]

    subgraph ADDON["Addon jeweler3dstudio (root)"]
        INIT["__init__.py\nEntry point · register/unregister"]
        MANIFEST["blender_manifest.toml\nid · version · tags · license"]
    end

    subgraph CORE["core/ — Lógica de negocio (Operators + datos)"]
        C_INIT["core/__init__.py\nOrquesta: units · ring · gems · cutters"]
        C_UNITS["core/units.py\nConversión mm↔in · tallas US"]
        C_RING["core/ring.py\nOperator: J3D_OT_size_ring\nItems: US_SIZE, GEOMETRY_TYPE, ORIENTATION, RING_PROFILE"]
        C_GEMS["core/gems.py\nOperator: J3D_OT_add_gem\nCatálogo: GEM_MESH_DATA (17 cortes)\nEnums: STONE_ITEMS · get_cut_enum_items\nPresets: CUT_COMMERCIAL_SIZES / GLOBAL_COMMERCIAL_SIZES"]
        C_CUTTERS["core/cutters.py\nOperators: J3D_OT_add_seat_cutter\nJ3D_OT_add_v_cutter"]
        C_PRONGS["core/prongs.py ⚠️ desconectado"]
        C_PAVE["core/pave.py ⚠️ desconectado"]
        C_METRICS["core/metrics.py ⚠️ desconectado"]
    end

    subgraph GEM_DATA["core/gem_data/ — Geometría por familia"]
        GD_INIT["gem_data/__init__.py"]
        GD_FANCY["_fancy.py · 54 KB\n(Oval · Pear · Heart · Marquise · Baguette · ...)"]
        GD_ROUND["_round.py · 10 KB\n(Round Brilliant)"]
        GD_OCTAGON["_octagon.py · 4 KB\n(Asscher · Cushion · Radiant · Princess)"]
        GD_STEPPED["_stepped.py · 9 KB\n(Emerald · Square Emerald · Baguette step)"]
        GD_TRILLION["_trillion.py · 12 KB\n(Trillion · Shield · Kite · ...)"]
    end

    subgraph UI["ui/ — Presentación (Panels)"]
        UI_INIT["ui/__init__.py"]
        UI_I18N["ui/i18n.py\nInternacionalización ES/EN"]
        UI_MENUS["ui/menus.py\nMenús contextuales 3D View"]
        UI_GIZMOS["ui/gizmos.py\nGizmos viewport (stub activo)"]
        UI_DIALOGS["ui/dialogs.py\nDialogs / popups"]

        subgraph PANELS["ui/panels/"]
            P_INIT["panels/__init__.py\nRegistra clases + scene_props"]
            P_SCENE["scene_props.py\nJ3D_SceneSettings (PropertyGroup)\nbpy.types.Scene.j3d\n─ Ring: us_size · geometry_type · ring_* (8 props)\n─ Gems: gem_cut · gem_stone · gem_size_preset · gem_size\n─ Swap: swap_cut · swap_stone · swap_size\n─ Cutters: cutter_segments · cutter_crease"]
            P_RING["ring.py\nVIEW3D_PT_j3d_ring_size\nVIEW3D_PT_j3d_sub_size\nVIEW3D_PT_j3d_sub_profile"]
            P_GEMS["gems.py\nVIEW3D_PT_j3d_gems\nVIEW3D_PT_j3d_sub_gem_visor"]
            P_GEMMAP["gem_map.py\nVIEW3D_PT_j3d_sub_gem_map\nVIEW3D_PT_j3d_sub_gem_swap"]
            P_CUTTERS["cutters.py\nVIEW3D_PT_j3d_cutters\nVIEW3D_PT_j3d_sub_cutter_seat\nVIEW3D_PT_j3d_sub_cutter_v"]
            P_STUBS["stubs.py\nSettings · Prongs · Bezel · Pave\nBaskets · Gallery · Supports\nMetrics · Weights · Quotation\n(Stubs — pendientes implementar)"]
        end
    end

    subgraph ASSETS["assets/ — Recursos estáticos"]
        A_GEMS["gems/\n├ png/ (iconos producción)\n├ dark/ ← excluido del ZIP\n├ light/ ← excluido del ZIP\n├ svg/ ← excluido del ZIP\n├ references/ ← excluido del ZIP\n└ gems.blend ← excluido del ZIP"]
        A_NG["node_groups/ (geometría de nodos)"]
    end

    subgraph TOOLS["tools/ — Herramientas de desarrollo (no se empacan)"]
        T_ICONS["generate_gem_icons.py\ngenerate_all_marquise_icons.py\ngen_round_blueprint.py\ngenerate_oval_marquise_icon.py\ngenerate_round_marquise_icon.py"]
        T_SPLIT["split_gem_data.py"]
        T_TPL["templates/\nLICENSE_commercial.txt\nLICENSE_community.txt\nREADME_community.md"]

        subgraph PACKZIP["tools/pack_zip/ — Pipeline multi-tier"]
            PK_COMMON["pack_common.py\nUtilidades: copy_base_files · transform_manifest · zip_directory\nFiltros: EXCLUDE_DIRS · EXCLUDE_ASSET_PREFIXES"]
            PK_TIERS["pack_tiers.py\nRouter de tiers"]
            PK_ALL["pack_all.py\nOrquesta los 3 tiers"]
            PK_EXT["pack_extension.py\n(Pro / fuente)"]
            PK_COMM["pack_community.py\nTransform namespace → jeweler3dstudio_community\nbpy.ops.j3d.* → bpy.ops.j3d_community.*"]
            PK_STD["pack_standard.py\nTransform namespace → jeweler3dstudio_standard\nbpy.ops.j3d.* → bpy.ops.j3d_standard.*"]
            PK_PRO["pack_pro.py"]
        end
    end

    subgraph DIST["dist/ — Artefactos de distribución"]
        D_PRO["jeweler3dstudio-0.1.0.zip"]
        D_COMM["jeweler3dstudio_community-0.1.0.zip"]
        D_STD["jeweler3dstudio_standard-0.1.0.zip"]
        D_UNPK["unpacked/\n├ jeweler3dstudio/\n├ jeweler3dstudio_community/\n└ jeweler3dstudio_standard/"]
        D_PUB["publish/ (placeholder)"]
    end

    subgraph TESTS["tests/"]
        T_HEAD["run_tests_headless.py\n(unittest · mock bpy/bmesh)\nTests: sintaxis · integridad cortes · paquetes dist"]
    end

    BL --> INIT
    INIT --> CORE
    INIT --> UI
    INIT --> ASSETS
    C_INIT --> C_UNITS & C_RING & C_GEMS & C_CUTTERS
    C_GEMS --> GEM_DATA
    UI_INIT --> PANELS
    P_INIT --> P_SCENE
    P_SCENE --> C_RING
    P_SCENE --> C_GEMS
    TOOLS --> DIST
    PK_COMMON --> PK_COMM & PK_STD & PK_EXT & PK_PRO
    PK_ALL --> PACKZIP
    TESTS --> DIST
```

---

## Diagrama de flujo de registro (Blender lifecycle)

```mermaid
graph LR
    BL_LOAD["Blender carga addon"] --> INIT_REG["__init__.register()"]
    INIT_REG --> C_REG["core.register()\nunits · ring · gems · cutters"]
    INIT_REG --> UI_REG["ui.register()"]
    INIT_REG --> NG_REG["assets.node_groups.register()"]
    UI_REG --> P_INIT_REG["panels.__init__.register()"]
    P_INIT_REG --> SP_REG["scene_props.register()\n→ J3D_SceneSettings\n→ bpy.types.Scene.j3d"]
    P_INIT_REG --> CLASSES["bpy.utils.register_class()\n× todas las clases de paneles"]
```

---

## Diagrama multi-tier packaging

```mermaid
graph LR
    SRC["Fuente\njeweler3dstudio/"] --> PK_ALL["pack_all.py"]
    PK_ALL --> PK_EXT --> STAGE_PRO["staging/jeweler3dstudio/"]
    PK_ALL --> PK_COMM --> STAGE_COMM["staging/jeweler3dstudio_community/\n+ rename namespace j3d → j3d_community"]
    PK_ALL --> PK_STD --> STAGE_STD["staging/jeweler3dstudio_standard/\n+ rename namespace j3d → j3d_standard"]
    STAGE_PRO --> ZIP_PRO["dist/jeweler3dstudio-0.1.0.zip"]
    STAGE_COMM --> ZIP_COMM["dist/jeweler3dstudio_community-0.1.0.zip"]
    STAGE_STD --> ZIP_STD["dist/jeweler3dstudio_standard-0.1.0.zip"]
```

---

## Componentes por capa

| ID | Capa | Archivo | Estado | Notas |
|---|---|---|---|---|
| a01 | Entry Point | `__init__.py` | ✅ activo | Registro dinámico con reload |
| a02 | Manifest | `blender_manifest.toml` | ✅ activo | v0.1.1 · Blender 4.2+ |
| a03 | Core | `core/units.py` | ✅ activo | Conversión mm/in/tallas |
| a04 | Core | `core/ring.py` | ✅ activo | Operator + enums ring |
| a05 | Core | `core/gems.py` | ✅ activo | Operator + 17 cortes |
| a06 | Core | `core/cutters.py` | ✅ activo | Seat + V cutters |
| a07 | Core | `core/gem_data/_fancy.py` | ✅ activo | Familia fancy (54 KB) |
| a08 | Core | `core/gem_data/_round.py` | ✅ activo | Round Brilliant |
| a09 | Core | `core/gem_data/_octagon.py` | ✅ activo | Asscher/Cushion/Radiant |
| a10 | Core | `core/gem_data/_stepped.py` | ✅ activo | Emerald/Baguette step |
| a11 | Core | `core/gem_data/_trillion.py` | ✅ activo | Trillion/Shield/Kite |
| a12 | Core | `core/prongs.py` | ⚠️ desconectado | Comentado en core/__init__ |
| a13 | Core | `core/pave.py` | ⚠️ desconectado | Comentado en core/__init__ |
| a14 | Core | `core/metrics.py` | ⚠️ desconectado | Comentado en core/__init__ |
| a15 | UI Props | `ui/panels/scene_props.py` | ✅ activo | 20 props en scene.j3d.* |
| a16 | UI Panel | `ui/panels/ring.py` | ✅ activo | 3 paneles N-Panel |
| a17 | UI Panel | `ui/panels/gems.py` | ✅ activo | 2 paneles + icon pcoll |
| a18 | UI Panel | `ui/panels/gem_map.py` | ✅ activo | 2 subpaneles |
| a19 | UI Panel | `ui/panels/cutters.py` | ✅ activo | 3 paneles |
| a20 | UI Panel | `ui/panels/stubs.py` | ⚠️ stubs | 10 paneles placeholder |
| a21 | UI | `ui/i18n.py` | ✅ activo | Traducciones ES/EN |
| a22 | UI | `ui/menus.py` | ✅ activo | Menús contextuales |
| a23 | UI | `ui/gizmos.py` | ⚠️ stub | Gizmos pendientes |
| a24 | UI | `ui/dialogs.py` | ✅ activo | Popups |
| a25 | Assets | `assets/gems/png/` | ✅ activo | Iconos de cortes (PNG) |
| a26 | Assets | `assets/node_groups/` | ✅ activo | Geometría nodos |
| a27 | Dist | `dist/*.zip` (3 tiers) | ✅ generado | Pro · Standard · Community |
| a28 | Tools | `tools/pack_zip/pack_*.py` | ✅ activo | Pipeline multi-tier |
| a29 | Tools | `tools/generate_gem_icons.py` | ✅ activo | Generación de iconos |
| a30 | Tools | `tools/split_gem_data.py` | ✅ activo | Fragmentación gem_data |
| a31 | Tests | `tests/run_tests_headless.py` | ✅ activo | CI headless unittest |

---

## Dependencias externas

| Módulo | Origen | Propósito | Estado |
|---|---|---|---|
| `bpy` | Blender runtime | API principal — tipos, propiedades, ops | ✅ ok |
| `bmesh` | Blender runtime | Manipulación de malla en memoria | ✅ ok |
| `bpy.props` | Blender runtime | Sistema de propiedades declarativas | ✅ ok |
| `mathutils` | Blender runtime | Vectores, matrices, geometría | ✅ ok |
| `zipfile`, `shutil`, `pathlib` | stdlib | Pipeline de empaquetado | ✅ ok |
| `unittest`, `unittest.mock` | stdlib | Suite headless tests | ✅ ok |

---

## Decisiones de arquitectura (ADR)

### 2026-09-22 — PropertyGroup unificado `scene.j3d.*`
- **Contexto:** Las propiedades de escena vivían como atributos sueltos en `bpy.types.Scene`.
- **Decisión:** Consolidar en `J3D_SceneSettings(PropertyGroup)` → `bpy.types.Scene.j3d`.
- **Consecuencias:** Acceso uniforme `context.scene.j3d.*`; simplifica empaquetado multi-tier; elimina colisiones de namespace entre extensiones coexistentes.
- **Agente:** Antigravity · sesión w59

### 2026-09-22 — Regex quirúrgico en transformación multi-tier
- **Contexto:** El regex de reemplazo `j3d → j3d_community` era demasiado amplio y colisionaba con la variable local `j3d = context.scene.j3d`.
- **Decisión:** Ajustar regex a `bpy\.ops\.j3d\.` y strings literales de operadores, nunca reemplazar identificadores Python genéricos.
- **Consecuencias:** Protege variables de acceso a PropertyGroup; evita `NameError` en runtime.
- **Agente:** Antigravity · sesión w61

### 2026-09-22 — Suite headless `tests/run_tests_headless.py`
- **Contexto:** No existe ejecutable de Blender en el entorno CI.
- **Decisión:** Usar `unittest.mock` con jerarquía de módulos ficticios (`bpy`, `bmesh`) para validar sintaxis e integridad estática.
- **Consecuencias:** Detecta regresiones de packaging sin necesitar Blender instalado; metaclass conflicts resueltos con clases dummy distintas.
- **Agente:** Antigravity · sesión w60

---

> **Deuda técnica** → [`overview/work/deuda_tecnica.md`](../work/deuda_tecnica.md)
