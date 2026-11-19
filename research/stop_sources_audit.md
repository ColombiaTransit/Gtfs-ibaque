# Ibagué bus-stop source investigation — 19 November 2026

## Most useful existing source: Universidad de Ibagué GTFS

The pinned original `gtfs_ibague.zip` at [omtu-unibague/gtfs-ibague](https://github.com/omtu-unibague/gtfs-ibague) already includes a georeferenced stop inventory with **1,153 unique GTFS stop_id values**, all linked from `stop_times.txt`.

Re-examining the actual `stops.txt` reveals:

| GTFS name pattern | Count |
| --- | ---: |
| Numbered candidates for official paraderos (e.g. `Id 1150-T3`, `287 T3`, `1105 Mod`) | **974** |
| Synthetic `Terminal Inicio/Fin` stops | **101** |
| `Marcador De Local Sem Titulo` placeholders | **78** |
| **Total** | **1,153** |

The **974 numbered stops contain 973 distinct candidate numbers**, all within **1–1150**. Number **287** appears twice at points about **2,260 meters apart** (source GTFS `stop_id=306`, named `287-T3`, and `stop_id=590`, named `287 T3`). This is a specific source conflict; do not merge. The 1–1150 ID range is strikingly consistent with the publicly reported **1,150 TransMusical stops**, but **a numerical correspondence does not establish 1:1 identity or a full match**.

**Important schema rule:** `stop_id` is the GTFS primary key and is referenced by `stop_times.txt`. The numbered identifier is currently encoded in `stop_name`; do **not** replace the primary key or merge stops automatically. Preserve codes separately in a proposed `stop_code` or provenance register after verification.

### Official evidence: physical stop numbers, route-specific signboards

- [SETP/TransMusical official stop information page](https://transmusical.gov.co/paraderos/): types 1, 2, 3, but currently no public full list of coordinates or route associations.
- [Public SETP October 2025 deployment report](https://www.ecosdelcombeima.com/ibague/nota-174448-tome-nota-asi-deben-usarse-los-nuevos-paraderos-del-setp-en-ibague): **1,150 designated stop signs**, each providing route references and local landmarks. Crucially **not all routes serve every stop they pass**.
- Example [physical stop sign ID 1032 at Carrera 5 / Calle 44](https://commons.wikimedia.org/wiki/File:Paraderos_de_transporte_p%C3%BAblico_en_Ibagu%C3%A9.svg): shows route numbers **1, 17, 21, 40, 50** and an explanatory stop schema. Use as a specimen showing which fields could exist; do not substitute one sign for a citywide stop–route inventory.
- [Alcaldía report on 2026 Carrera Quinta pilot](https://ibague.gov.co/portal/noticias/21719-alcaldia-de-ibague-inicia-el-plan-piloto-de-paraderos-de-buses-en-la-carrera-qui): confirms a corridor-specific adoption exercise; temporary pilot stop rules do not automatically generalize to the entire network.

### Route mapping already visible through Google Maps

SETP explicitly announced the availability of route and stop discovery in Google Maps in **July 2026**: [news quoting SETP manager](https://ondasdeibague.com/noticias/ibague/68501-paraderos-y-rutas-de-buses-de-ibague-ya-estan-disponibles-en-google-maps). This is evidence of published passenger-facing stop–route data, **not proof of an accessible official public API or a new downloadable GTFS**. Respect applicable license and API rules.

### ArcGIS / university observatory — negative catalog check

The [Observatorio de Movilidad y Transporte (Universidad de Ibagué)](https://observatorio-de-movilidad-y-transporte-unibague-unibague.hub.arcgis.com/) has ArcGIS Online content under owner `omtu_unibague` (55 public search results at time of audit), and additional `2220181026_unibague` content (24 items). Targeted search and complete owner-page inspection on [GitHub Actions run 44608431355](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44608431355) identified **no published dedicated stop-feature service** in these accounts. Published Feature Services concern road accidents and mobility measurements, not an official list of stop points. This does **not** rule out unpublished, unindexed or municipality-hosted geodata.

A reproducible public ArcGIS catalog query script is in [`scripts/discover_ibague_stop_gis.py`](../scripts/discover_ibague_stop_gis.py). Its report is stored as a GitHub Actions artifact.

### Supplemental source — OpenStreetMap

OSM `highway=bus_stop` / `public_transport=platform` and names can help check stop positions or supply human-readable location descriptions; they are **not** automatically official authorizations to stop, and public OSM stop IDs should not be mapped to local `paradero_id` without positional verification. Data coverage has not yet been measured. Keep OSM as a fallback, not a replacement for the existing georeferenced GTFS.

## Next bounded actions

1. Keep the source `stop_id`, coordinates and stop times unchanged until differences are verified.
2. Generate a machine-readable QA report from the pinned source ZIP, including the **78 placeholder names**, **101 synthetic terminal locations** and duplicate code **287**, using [`scripts/audit_stop_identifiers.py`](../scripts/audit_stop_identifiers.py).
3. Treat the physical paradero number as `stop_code` *only after exact matching / uniqueness checks*. Duplicate code 287 needs manual investigation.
4. Compare existing GTFS stop positions to the locally authoritative *SETP list* of approximately 1,150 installed paraderos if a GIS inventory can be obtained. Ask SETP/Secretaría de Movilidad for `id_paradero`, coordinates, street reference, `rutas_que_paran`, stop type and installation/activation status.
5. For the **78 unnamed entries**, use manually checked OpenStreetMap street names or geocoded cross-streets as provisional descriptions, never as confirmed official stop names.
6. Revalidate directions and stopping positions for the modified **October 2026** routes before editing `stop_times.txt` or the stop–route links.

**Status:** The existing stop coordinate inventory is strong. A public, independently downloadable official `paraderos ↔ rutas` cross-reference or geodata layer was **not** verified. Do not undertake wholesale stop reconstruction.
