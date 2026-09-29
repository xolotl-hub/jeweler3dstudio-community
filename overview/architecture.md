# 🏗️ Arquitectura Viva — Jeweler 3D Studio v0.1.0

> **Índice Raíz Hub & Spoke** — Cobertura 100% exhaustiva del sistema.
> Extensión Blender 4.2+ / 5.x — Joyería CAD paramétrica procedural multi-tier.

---

## 📊 Diagrama de Flujo Maestro y Dependencias

```mermaid
graph TD
    Manifest["📦 blender_manifest.toml\nv0.1.0 · Blender ≥ 4.2"] --> Init["🚀 __init__.py\nDynamic reload + dispatch"]

    subgraph Core["⚙️ core/ — Motor Geométrico CAD"]
        Units["units.py\nmm↔BU (1 BU = 1 mm)"]
        Ring["ring.py\nArcos US 3-13.5\n8 Perfiles + Crease"]
        Gems["gems.py\n17 cortes · BSDF · ct\nLive Map & Select"]
        GemData["gem_data/\n5 familias modularizadas\nTopología normalizada pura"]
        Cutters["cutters.py\n5-Zonas calibradas\nLive Edit (6 Perímetros)"]
        Prongs["prongs.py (stub p14)"]
        Pave["pave.py (stub p17)"]
        Metrics["metrics.py\nDensidad metales preciosos"]
        
        Gems --> GemData
        Gems <--> Cutters
    end

    subgraph UI["🖥️ ui/ — Interfaz N-Panel, Menús e i18n"]
        Panels["panels/\nModularizado en 5 submódulos\n6 Paneles / 13 Subpaneles"]
        Menus["menus.py\nShift+A Add Menu\nCurve / Mesh / Jeweler 3D"]
        I18n["i18n.py\nCanonical EN Base\nCatalogos ES/FR (bpy.app.translations)"]
        Dialogs["dialogs.py\nExportador Ficha Técnica"]
        Gizmos["gizmos.py\nHandles 3D Viewport"]
    end

    subgraph Pipeline["📦 tools/pack_zip/ — Pipeline Multi-Tier"]
        PackPro["pack_pro.py (DEFAULT)\nStudio PRO (17 cortes, 8 perfiles, full)"]
        PackComm["pack_community.py\nCommunity Edition + Auto GitHub Sync"]
        PackStd["pack_standard.py\nStandard Edition"]
        PackAll["pack_all.py\nMaster Orchestrator"]
        PackCommon["pack_common.py\nShared Manifest & Zip Helpers"]
    end

    subgraph Blender["🔷 Blender Runtime Context"]
        B_Scene["bpy.types.Scene properties"]
        B_Obj["bpy.types.Object custom props"]
        B_Mesh["bpy.data.meshes / bmesh"]
        B_Trans["bpy.app.translations"]
    end

    Init --> Core
    Init --> UI
    Panels --> Core
    Menus --> Core
    Panels --> B_Scene
    Cutters --> B_Obj
    I18n --> B_Trans
    Core --> B_Mesh
    Pipeline -->|"Compila"| Dist["dist/*.zip"]
```

---

## 🏛️ Desglose Arquitectónico Modular (100% Cobertura)

```mermaid
graph LR
    subgraph UI_Interaction["Entradas de Usuario"]
        ShiftA["Shift+A Menu"]
        NPanel["N-Panel Viewport"]
        RedoF9["Redo Panel (F9)"]
        LiveTable["Inventario Interactivo"]
    end

    subgraph Processing_Layer["Capa de Procesamiento"]
        RingGen["Ring Shank Generator"]
        GemGen["17-Cut Procedural Mesh"]
        CutterGen["5-Zone Calibrated Cutter"]
        LiveMap["Live Scene Inventory Scanner"]
    end

    subgraph Output_Layer["Objetos y Materiales"]
        MeshRing["Curve / Mesh Ring Objs"]
        MeshGems["Faceted Gem + Glass BSDF"]
        MeshCutters["Boolean Cutter (Wire)"]
        SceneMetrics["Total ct & Dimension Records"]
    end

    ShiftA --> RingGen & GemGen
    NPanel --> RingGen & GemGen & CutterGen & LiveMap
    RedoF9 --> RingGen & GemGen & CutterGen
    LiveTable --> LiveMap

    RingGen --> MeshRing
    GemGen --> MeshGems
    CutterGen --> MeshCutters
    LiveMap --> SceneMetrics
```

---

## 🌐 Arquitectura de Internacionalización (i18n)

```mermaid
graph LR
    CodeBase["UI Base (Canonical English)\npanels.py · menus.py · core/"] --> I18nEngine["ui/i18n.py\nTRANSLATIONS_DICT"]
    
    I18nEngine -->|"En Locale es/es_ES"| DictES["Catálogo Español (80+ llaves)\nAnillos, Cortes, Cotas"]
    I18nEngine -->|"En Locale fr_FR"| DictFR["Catálogo Francés\nBagues, Pierres, Découpeurs"]
    I18nEngine -->|"Default / Other"| FallbackEN["Fallback Directo EN (Zero-Overhead)"]

    DictES & DictFR & FallbackEN --> AppTrans["bpy.app.translations.register()"]
```

---

## 📦 Matriz de Tiers y Aislamiento de Espacios de Nombres

```mermaid
graph TD
    RepoRoot["Source Code (PRO Default)"] --> PackOrchestrator["pack_all.py"]

    PackOrchestrator --> PackComm["pack_community.py"]
    PackOrchestrator --> PackStd["pack_standard.py"]
    PackOrchestrator --> PackPro["pack_pro.py"]

    PackComm -->|"Filtra Stubs + Subpaneles + Prefijo j3d_community"| CommZip["jeweler3dstudio_community-0.1.0.zip\n(GPL-3.0 · Libre)"]
    PackStd -->|"Prefijo j3d_standard"| StdZip["jeweler3dstudio_standard-0.1.0.zip\n(Comercial)"]
    PackPro -->|"Full Features · Prefijo j3d"| ProZip["jeweler3dstudio-0.1.0.zip\n(Comercial PRO)"]

    CommZip -->|"Auto Sync & Push"| GitComm["GitHub: jeweler3dstudio-community\n(Con .agents, .skill/, overview/)"]
```

---

## 🔗 Subdocumentos de Arquitectura

→ [modules/cutters.md](file:///home/xolotl/dev/jeweler3dstudio/overview/architecture/modules/cutters.md) — Detalle del motor de cortadores (5 zonas, live edit, Object props)
→ [modules/gems.md](file:///home/xolotl/dev/jeweler3dstudio/overview/architecture/modules/gems.md) — Motor de gemas (17 cortes, GEM_MESH_DATA, BSDF, mapa de inventario)
→ [modules/ring.md](file:///home/xolotl/dev/jeweler3dstudio/overview/architecture/modules/ring.md) — Motor de aros y tallas
→ [modules/ui.md](file:///home/xolotl/dev/jeweler3dstudio/overview/architecture/modules/ui.md) — Interfaz N-Panel, menús Shift+A y motor i18n
→ [modules/pipeline.md](file:///home/xolotl/dev/jeweler3dstudio/overview/architecture/modules/pipeline.md) — Empaquetado multi-tier y orquestación Git

