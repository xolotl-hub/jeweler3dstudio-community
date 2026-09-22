# Tracker: Iconos de Gemas — 3 Estilos × 17 Cortes
> `overview/trackers/gem_icons_tracker.md`
> Generación de 51 iconos SVG + PNG (17 cortes × 3 estilos visuales)
> Orden de producción obligatorio: `marquise` → `round` → `asscher`.

---

## ?? Estilos definidos

| ID | Nombre | Concepto | Paleta | Estado |
|---|---|---|---|---|
| `marquise` | Art Déco Dorado | Línea dorada fina sobre negro, geometría angular deco | `#C9A84C` sobre `#0A0A0A` | 🟡 En progreso |
| `round` | Luxury Blueprint | Facetado técnico exacto sobre navy profundo, líneas blancas finas | `#DDE4F5` sobre `#0D1B3E` | ?? En progreso |
| `asscher` | Geometría Sagrada | Círculos y polígonos concéntricos dorados sobre negro | `#D4AF6A` sobre `#111111` | ?? Pendiente |

---

## ?? Progreso por corte

| # | Corte | marquise | round | asscher | Notas |
|---|---|---|---|---|---|
| 01 | ROUND | ✅ listo | ?? WIP | ? vacío | Round Marquise activo en `assets/gems/png/round.png`; topología de `core/gems.py` |
| 02 | OVAL | ? vacío | ? vacío | ? vacío | |
| 03 | CUSHION | ? vacío | ? vacío | ? vacío | |
| 04 | PEAR | ? vacío | ? vacío | ? vacío | |
| 05 | MARQUISE | ? vacío | ? vacío | ? vacío | |
| 06 | PRINCESS | ? vacío | ? vacío | ? vacío | |
| 07 | BAGUETTE | ? vacío | ? vacío | ? vacío | |
| 08 | SQUARE | ? vacío | ? vacío | ? vacío | |
| 09 | EMERALD | ? vacío | ? vacío | ? vacío | |
| 10 | ASSCHER | ? vacío | ? vacío | ? vacío | |
| 11 | RADIANT | ? vacío | ? vacío | ? vacío | |
| 12 | FLANDERS | ? vacío | ? vacío | ? vacío | |
| 13 | OCTAGON | ? vacío | ? vacío | ? vacío | |
| 14 | HEART | ? vacío | ? vacío | ? vacío | |
| 15 | TRILLION | ? vacío | ? vacío | ? vacío | |
| 16 | TRILLIANT | ? vacío | ? vacío | ? vacío | |
| 17 | TRIANGLE | ? vacío | ? vacío | ? vacío | |

**Leyenda:** ? listo · ?? WIP · ? vacío (PNG placeholder transparente)

---

## ?? Estructura de archivos

```
assets/gems/
+-- png/                   <- Estilo ACTIVO (el que usa el addon)
¦   +-- round.png
¦   +-- ...
+-- styles/
¦   +-- marquise/          <- Art Déco dorado (17 SVG + 17 PNG)
¦   ¦   +-- round.png
¦   ¦   +-- ...
¦   +-- round/             <- Luxury Blueprint (17 SVG + 17 PNG)
¦   ¦   +-- round.png      <- en construcción
¦   ¦   +-- ...
¦   +-- asscher/           <- Geometría Sagrada (17 SVG + 17 PNG)
¦       +-- ...
+-- svg/
    +-- styles/
        +-- marquise/
        +-- round/
        +-- asscher/
```

---

## ?? Sesión activa

- **Fecha inicio:** 2026-09-08
- **Entregado:** `marquise/round.svg` + `marquise/round.png`, activado en `assets/gems/png/round.png`.
- **Ajuste de visor:** preview Round en escala 10; SVG final 433×256, fondo horizontal; fila del visor al 75% de alto.
- **Ajuste de selector:** `template_icon_view` sustituido por menú compacto; evitar doble render de Round.
- **Siguiente:** `oval.png` en estilo `marquise`; luego continuar los demás cortes.
- **Referencia para round:** JewelCraft dark/round.png — vista superior del Round Brilliant
  - Tabla octagonal interior
  - 8 star facets (triángulos)
  - 8 kite/bezzel facets (cuadriláteros)
  - 16 upper-girdle halves (triángulos pequeños en el borde)
- **Script:** `tools/generate_gem_icons_v2.py` (multi-estilo)

---

## ?? Decisiones de diseño

- Referencias base preservadas (no sobrescribir):
  - `style_marquise_art_deco_gold.png` — estilo fuente activo; aplicar a `round`, `oval` y cortes sucesivos.
  - `style_round_luxury_blueprint.png` — referencia secundaria.
  - `style_asscher_sacred_geometry.png` — referencia terciaria.
- El selector de estilo activo es un **pendiente UI** (ver `pendientes.md` p9)
- Por ahora el addon carga desde `assets/gems/png/`
- Al implementar p9, el addon leerá desde `assets/gems/styles/{estilo_activo}/`
