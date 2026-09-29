# 📦 Módulo: Pipeline — Empaquetado Multi-Tier y Distribución

> **Archivos:** [`tools/pack_zip/pack_all.py`](file:///home/xolotl/dev/jeweler3dstudio/tools/pack_zip/pack_all.py), [`tools/pack_zip/pack_community.py`](file:///home/xolotl/dev/jeweler3dstudio/tools/pack_zip/pack_community.py), [`tools/pack_zip/pack_pro.py`](file:///home/xolotl/dev/jeweler3dstudio/tools/pack_zip/pack_pro.py), [`tools/pack_zip/pack_standard.py`](file:///home/xolotl/dev/jeweler3dstudio/tools/pack_zip/pack_standard.py), [`tools/pack_zip/pack_common.py`](file:///home/xolotl/dev/jeweler3dstudio/tools/pack_zip/pack_common.py)
> **Rol:** Generador de artefactos ZIP y sincronización automatizada de repositorios Git para Blender Extensions y canales comerciales.

---

## Diagrama del Pipeline de Distribución

```mermaid
graph TD
    RepoMaster["Repositorio Maestro (PRO)"] --> PackAll["tools/pack_zip/pack_all.py"]

    subgraph PackAll["Orquestador de Empaquetado"]
        P_Comm["pack_community.py\n• Genera Community ZIP\n• Aísla namespaces a j3d_community\n• Sync git@github.com:...-community"]
        P_Std["pack_standard.py\n• Genera Standard ZIP\n• Aísla namespaces a j3d_standard"]
        P_Pro["pack_pro.py\n• Genera Studio PRO ZIP\n• Namespace nativo j3d"]
    end

    subgraph Outputs["Artefactos en dist/"]
        DistComm["dist/jeweler3dstudio_community-0.1.0.zip\n(Blender Extensions / GPL-3.0)"]
        DistStd["dist/jeweler3dstudio_standard-0.1.0.zip\n(Comercial Standard)"]
        DistPro["dist/jeweler3dstudio-0.1.0.zip\n(Comercial PRO)"]
    end

    subgraph GitSync["Sincronización Git"]
        Submodules[".agents · .skill · overview\n(Inyectados en Community)"]
        GitRepo["GitHub: jeweler3dstudio-community\n(Pushed & Tagged)"]
    end

    P_Comm --> DistComm
    P_Std --> DistStd
    P_Pro --> DistPro

    P_Comm --> Submodules --> GitRepo
```

---

## Especificaciones de Tiers

| Tier | Archivo Zip | Namespace | Destino | Licencia |
|---|---|---|---|---|
| **Community** | `jeweler3dstudio_community-0.1.0.zip` | `j3d_community` | extensions.blender.org | GPL-3.0-or-later |
| **Standard** | `jeweler3dstudio_standard-0.1.0.zip` | `j3d_standard` | Gumroad / BlenderMarket | Comercial |
| **Studio PRO** | `jeweler3dstudio-0.1.0.zip` | `j3d` | Gumroad / BlenderMarket PRO | Comercial |
