# Ibagué — route geometry, boarding-stop and variant worklist

**Updated:** 20 November 2026. **Status:** research / open tasks. No task in this list authorizes automatic replacement of production GTFS `stops.txt`, `stop_times.txt`, `trips.txt` or `shapes.txt`.

This is the **single cross-route worklist** for the 14 itinerary changes effective 19 October 2026, **plus route 35's rural Cay extension**. Source: [municipal modification notice](https://www.ibague.gov.co/portal/noticias/23334-este-lunes-cambiaran-los-recorridos-de-14-rutas-de-busetas-en-ibague-conozca-sus), 14 official October posters, the [official 2026 branch regulation](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf), and [route/variant evidence](variant_route_validation_sources_2026_11_20.md). **15 route cases; 14 are October itinerary changes; route 35 is extra branch work.**

"Add" in a task means **add only after the official physical location is confirmed and after checking that no appropriate `stop_id` already exists**. A route change does not prove a new physical stop exists. Avoid creating duplicate stops or deleting shared stops when only their route association changes.

## Route-by-route queue

| Priority | Route | Stop / geometry action | Official poster | Status |
| --- | --- | --- | --- | --- |
| High | 1 | **Arboleda del Campestre / La Samaria** — Check new outbound/inbound termini, official boarding stops and ordered stops along Pedro Tafur and airport road | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-1-scaled.png) | Open |
| Medium | 2 | **Calle 69 / Jordán 9 / Calle 64** — Match new stops on Jordán 9 diversion; preserve unchanged Ambalá/Carrera Quinta visits | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-2-scaled.png) | Open |
| High | 7 (source 4/7) | **Carrera Primera / Carrera Segunda / centro** — Resolve source 4/7 versus official 7 and independent route 4; compare stop order of R5/R6 before any reassignment | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-7-scaled.png) | Open |
| High | 8 | **Calle 100 / Mercacentro / Nueva Castilla / Santa Bárbara** — Check R9/R11 IDA and R10/R12 VUELTA; R11 direction_id mismatch; verify short turns and Calle 100 stops before frequency split | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-8-scaled.png) | Open |
| High | 9 | **Santa Cruz** — Identify terminal/turnaround and new boarding stops toward Santa Cruz in both relevant directions | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-9-scaled.png) | Open |
| High | 15 | **Santa Cruz / Panóptico / Calle 10 / Carrera Cuarta** — Validate removal of Santa Cruz visits and updated turn via Calle 10; do not delete shared stop records from stops.txt | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-15-scaled.png) | Open |
| Medium | 19 | **Arboleda del Campestre / Avenida Pedro Tafur** — Check road connection and stop order along revised connector in both directions | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-19-scaled.png) | Open |
| Medium | 21 | **Piscinas Olímpicas / Versalles** — Check stop calls following revised Carrera Quinta to Piscinas Olímpicas and Versalles alignment | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-21-scaled.png) | Open |
| High | 28 | **Parque Caiké entrance / opposite roadside** — Find precise park-bound and return-side boarding positions, verify stop IDs, insert in R37/R38 stop_times only with supported times | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-28-scaled.png) | Open |
| High | 29 | **Calambeo / Carmen de Bulira** — Explain R39 5 stops versus R40 44; check whether terminal shift changes stop sequence without deleting Calambeo from official map | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-29-scaled.png) | Open |
| Medium | 37 | **Calle 15 / Calle 16 / Carrera Quinta / Carrera Primera** — Check Calle 15 return and remove obsolete Calle 16 visits from correct pattern only after map review | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-37-scaled.png) | Open |
| Medium | 40 | **Calle 17 / Calle 42 / Carrera Quinta / Versalles** — Audit two changed road sections and associated boarding stops; preserve unaffected corridor | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-40-scaled.png) | Open |
| High | 48 | **Villa Restrepo / Iguaima / Juntas; Avenida Guabinal** — Verify Juntas terminal and directional stops plus rural sequence, source R53 17 / R54 85 incompleteness, and Guabinal/Clínica Sharon city diversion; conditional one-in-three rule | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-48-scaled.png) | In review |
| Medium | 50 | **La Tobogán / Calle 42 / Avenida Guabinal** — Map affected return pattern and street-side stops; keep outward route unchanged | [Source](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-50-scaled.png) | Open |
| High | 35 | **El Libertador / vereda Cay** — Locate verified branch junction, Cay terminal and directional ordered stops; R45 37 and R46 34 do not prove dedicated Cay trips; one-in-three rule is not a stop list | [Source](https://transmusical.gov.co/wp-content/uploads/2026/06/Ruta-35-scaled.jpg) | Open |

## Work packages in order

### A — Physical boarding stops / possible missing route portions (high)

- [ ] **28 Caiké:** establish park entrance stop and opposite-side return boarding stop; verify both directions and reuse existing IDs if correctly located. Already detailed in [stop remediation plan](stop_remediation_plan.md#open-task--gtfs-route-28-add-caiké-entrance-boarding-stops-priority-high).
- [ ] **48 Juntas:** verify actual physical Juntas departure stop, Iguaima and Villa Restrepo stop sequence and direction. Secondary ordered stops are *candidates*, not official stop IDs. Resolve 17 versus 85 source stop visits. Check urban Avenida Guabinal deviation **separately**. Respect conditional feeder operation before activating special service.
- [ ] **35 Cay:** seek official stop inventory or route agency confirmation for branch junction, turn-around and ordered stop sequence; OSM Cay `bus_station` is only a candidate and unrelated VDA. CAY service must not be imported as line 35.
- [ ] **1 / 9:** new Arboleda/La Samaria and Santa Cruz terminal/extension segments; audit physical stop additions in each direction before modifying `stop_times`.

### B — Direction and old-pattern reconciliation (high)

- [ ] **8:** map `R9/R11` east-to-west IDA and `R10/R12` west-to-east VUELTA; inspect conflicting `R11.direction_id`, mixed route-37 terminal labels, western short turns, and October Calle 100/Mercacentro detour. Prove any actual short-turn trips before allocating legal headways.
- [ ] **7 / upstream 4/7:** compare two old patterns and official new 7 against separately advertised 4; decide current route IDs and stop lists without silently splitting or removing service.
- [ ] **29:** resolve source `R39` (5 stops) versus `R40` (44); check Calambeo versus Carmen de Bulira terminal and real stop positions.
- [ ] **15:** stop serving Santa Cruz per official Oct change; remove only **route-pattern stop visits** that are shown to be obsolete, not shared physical `stops.txt` rows.

### C — Smaller official October road changes (medium)

- [ ] **2, 19, 21, 37, 40, 50:** validate each documented changed road section against official maps and GraphHopper `bus` routing; determine direction-specific stop calls or changed boarding side. Route 50 changes *return* only. Route 37's return uses Calle 15.
- [ ] For every case, do not reroute unchanged roads or silently alter untouched stop visits.

## Definition of done for each route

1. Official route evidence (and applicable date) recorded; real branch vs ordinary route change decided.
2. Correct direction and ordered stop IDs reviewed; physical stop coordinates and boarding side independently confirmed where changed.
3. Original shared stops preserved; add or remove a stop visit only when supported. Never create a timetable from a drawn line alone.
4. Where necessary, reroute the changed segments with **existing** organization GraphHopper `bus` profile and *reviewed official waypoints* (not only old source stops).
5. Check GTFS stop order, stop-to-shape distances, shape continuity and right-side service; rerun MobilityData validator after approved generator changes.
6. Do not duplicate legal headways across branches: conditional every-third dispatch to Juntas or Cay remains a **subset of total route service**. Route 28's extra weekend trip times are not yet proven.
7. Preserve a QA provenance record for each accepted or rejected change and honor upstream GTFS redistribution constraints.

## Separate inventory (not the October route geometry worklist)

- **Route 39** and separately advertised **route 4**: determine whether they are new standalone services in the 2026 route inventory, with source geometry and operating evidence.
- **Four feeder routes:** Chucuní, Llanos del Combeima, San Bernardo, Los Túneles have official posters with specific departures; model only with supported direction and timing, not as automatic extensions of these 15 cases.
- **78 unnamed existing stops** and duplicate physical candidate `stop_code=287`: [general stop remediation plan](stop_remediation_plan.md) remains applicable.

Machine-readable status: [route_geometry_stop_worklist.csv](route_geometry_stop_worklist.csv). Each case starts **Open**, not completed.

## Route 48 research QA — underway

The [dedicated Juntas road, stop and directional QA](route48_juntas_qa_2026_11_20.md) checks the 17-vs-85 source pattern gap and GraphHopper branch corridor. The follow-up workflow audits narrow OSM/Overpass stop candidates. **Status: in review, not route-validated; no GTFS data changed.**
