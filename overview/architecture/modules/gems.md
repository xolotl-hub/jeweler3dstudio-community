# 💎 Módulo: Gems — Motor de Gemas Paramétricas

> **Archivos:** [`core/gems.py`](file:///home/xolotl/dev/jeweler3dstudio/core/gems.py) (746L) + [`core/gem_data/`](file:///home/xolotl/dev/jeweler3dstudio/core/gem_data/) (subpaquete 5 módulos, ~2600L)
> **Rol:** Generador procedural de gemas 3D, materiales BSDF, estimador de quilates, mapa de inventario e intercambiador.

---

## Diagrama de Componentes

```mermaid
graph LR
    UI["N-Panel\nVisor de Gemas"] -->|"j3d.add_gem"| AddGem

    subgraph Engine["core/gems.py"]
        AddGem["J3D_OT_add_gem\ncut · stone · size · preset"]
        SwapGems["J3D_OT_swap_gems\nswap_cut · stone · size"]
        GemMap["J3D_OT_calculate_gem_map\nInventario escena"]
        CreateMesh["create_gem_mesh()\nEscala verts × mm_to_bu"]
        BSDF["assign_gem_material()\nBSDF · IOR · color"]
        Carats["calculate_carats()\nVolumen × density × factor"]
        Inventory["get_scene_gem_inventory()\nFiltra j3d_type=GEM"]
        CreateMesh --> BSDF
        CreateMesh --> Carats
    end

    subgraph Data["core/gem_data/"]
        RawData["GEM_MESH_DATA\nDict[cut_key → verts + faces]\n17 cortes normalizados\nDividido en _stepped, _fancy, _octagon, _round, _trillion"]
    end

    subgraph Assets["assets/gems/styles/"]
        Icons["17 iconos SVG+PNG\npor estilo (marquise/round/asscher)"]
        Preview["bpy.utils.previews\nget_cut_preview_collection()"]
        Icons --> Preview
    end

    AddGem --> CreateMesh
    AddGem --> BSDF
    SwapGems -->|"rebuild gem + cutter"| CreateMesh
    CreateMesh --> RawData
    UI --> Preview
    GemMap --> Inventory
```

---

## 17 Cortes Estándar

| Familia | Cortes | `GEM_MESH_DATA` Key |
|---|---|---|
| Redondo | ROUND | ✅ |
| Oval / Cojín | OVAL, CUSHION | ✅ |
| Pera | PEAR | ✅ |
| Marquesa | MARQUISE | ✅ |
| Corazón | HEART | ✅ |
| Trillón | TRILLION, TRILLIANT, TRIANGLE | ✅ |
| Rectang. escalonado | EMERALD, ASSCHER, BAGUETTE | ✅ |
| Rectang. brillante | PRINCESS, SQUARE, RADIANT, FLANDERS, OCTAGON | ✅ |

---

## Piedras Preciosas y Propiedades Físicas

| Piedra | IOR | Densidad g/cm³ | Color |
|---|---|---|---|
| DIAMOND | 2.417 | 3.52 | Blanco |
| RUBY | 1.770 | 4.02 | Rojo |
| SAPPHIRE | 1.770 | 4.02 | Azul |
| EMERALD | 1.580 | 2.76 | Verde |
| AQUAMARINE | 1.575 | 2.72 | Celeste |
| AMETHYST | 1.544 | 2.65 | Violeta |
| CUBIC_ZIRCONIA | 2.150 | 5.65 | Cristal |
| MOISSANITE | 2.650 | 3.22 | Cristal |
| MORGANITE | 1.580 | 2.76 | Rosa |
| TANZANITE | 1.695 | 3.35 | Violeta azul |

---

## Custom Properties en `bpy.types.Object` (Gema)

| Prop | Valor | Descripción |
|---|---|---|
| `j3d_type` | `"GEM"` | Identificador de tipo de objeto |
| `j3d_gem_cut` | `str` | Código de corte (ROUND, OVAL…) |
| `j3d_gem_stone` | `str` | Material de piedra |
| `j3d_gem_size` | `float` | Calibre en mm |
| `j3d_carat` | `float` | Quilates estimados |
| `j3d_has_cutter` | `str` | Nombre del cortador asociado (→ `CTR_*`) |

---

## Deuda Técnica

- **Calibres elongados** (Oval, Pear, Marquise) usan solo un eje — falta campo `size_w_mm` para L×W (p10).
- **Preset EnumProperty** no se resetea al cambiar de corte — bug de contexto dinámico en Blender (p11).
