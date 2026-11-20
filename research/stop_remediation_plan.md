# Targeted stop remediation plan — 19 November 2026

## Established data

Pinned upstream 22 May 2026 GTFS: **1,153 stop points**, 3,925 stop_times, no stop_id references missing. The existing [stop identifiers audit](stop_sources_audit.md) found **974 numbered stops**, **101 synthetic terminals**, **78 unnamed placeholders**, and duplicated candidate physical number **287** (2.26 km apart).

A new targeted review generates a route+direction inventory for each of the 78 unnamed stops and finds the nearest *numbered* source stop. **Do not automatically match based on proximity**.

Locally checked output on pinned ZIP: **2 unnamed points at <=30 m**, **11 at >30 to 75 m**, **65 at >75 m** from their nearest numbered source stop. Only **5 of 78** are within 50 m. A same-route/direction candidate is within 50 m for **3**. Therefore most unnamed stops cannot simply inherit a neighboring source name.

Run with:

```sh
python scripts/prepare_stop_remediation.py --download --output-dir build/stop_review
# Or:
python scripts/prepare_stop_remediation.py --zip gtfs_ibague.zip
```

GitHub Action [Prepare GTFS stop remediation review](../.github/workflows/stop-remediation.yml) produces `unnamed_stops_review.csv`, `duplicate_code_287.json` and `summary.json` as CI artifacts. Source SHA-256 is enforced and no feed edits are performed.

## Getting the authoritative inventory

Official contact confirmed at [TransMusical](https://transmusical.gov.co/contacto-y-canales-de-atencion/): `ventanillaunica@transmusical.gov.co`. The site confirms the installation of **1,150 paraderos tipo banderín** and the 2025 construction contract 037 is cited in contemporaneous reports.

[Spanish ready-to-send official information request](../requests/solicitud_inventario_paraderos_2026-11-19.md) specifies coordinates, paradero numbers, route+direction assignments, status, GIS/GTFS licensing and as-built plans. **No contact has been made yet.** Do not mark as sent until a send confirmation or case number exists.

No official full public inventory has been discovered through [SETP's paraderos page](https://transmusical.gov.co/paraderos/) or the existing public ArcGIS observatory catalog [research](stop_sources_audit.md). The search result is negative, not a proof that no inventory exists.

## When the actual inventory is provided

1. Preserve source files and capture original URI, publication date, download time, and license.
2. Validate CRS and stop point coordinates. Normalize official sign IDs as strings and keep both code and type.
3. Match by official code **and** spatial proximity, never code alone; handle code 287 collision manually.
4. Check direction-specific authorized routes, station side, and status before editing stop_times.
5. Manually review 78 placeholders; use `stop_code` after confirmed matches but **never silently rewrite `stop_id`**.
6. Recheck 2026 changed route stop sequences before public GTFS publication.
7. MobilityData validator and publication permission are independent prerequisites.

The original University's source archive is not redistributed in this repository pending licensing clarification. CSV derived from it remains as ephemeral private CI artifact rather than committing coordinates in Git.


## Open task — GTFS route 28: add Caiké entrance boarding stops (priority: high)

**Status: TODO — not yet added to `stops.txt` or `stop_times.txt`.** Route 28 was officially modified effective 19 October 2026 to serve Parque Recreacional Caiké directly, and the park instructions describe the return boarding location on the opposite side of the roadway.

- [ ] Identify and verify the physical boarding location **at the Parque Caiké entrance** for the outbound/park-bound direction using the official TransMusical route-28 map, park guidance and OSM roadside geometry; do **not** use the park polygon centroid as a stop.
- [ ] Identify and verify the **opposite-side return boarding stop** independently; check traffic direction and whether each location already matches an existing official/source stop before assigning new IDs.
- [ ] Add the confirmed stop(s) to `stops.txt` (or reuse existing `stop_id` where legitimately matched), with source URL, coordinate and direction provenance.
- [ ] Insert the stops at the correct `stop_sequence` in relevant route-28 `stop_times.txt` templates (source patterns `TRIP_R37`/`TRIP_R38`), preserving remaining stop order and recalculating relative times **only from supported evidence**; no fabricated running times.
- [ ] Verify both directions and route shape alignment against the October map with GraphHopper `bus` profile and official via points; rerun MobilityData validator and review stops-to-shapes / ordering notices.
- [ ] Record decisions and the accepted stop IDs in the route-28 review/override register prior to enabling publication.

**Reason:** prior stop-first geometry candidates approach the park area but the pinned source GTFS lacks identified boarding positions at the entrance. Geometry proximity to a park reference point does not prove an official GTFS stop. **Do not automatically promote candidate locations to published stops.**

Sources: [official route 28 poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-28-scaled.png), [Alcaldía itinerary changes](https://www.ibague.gov.co/portal/noticias/23334-este-lunes-cambiaran-los-recorridos-de-14-rutas-de-busetas-en-ibague-conozca-sus), and [Parque Caiké FAQ](https://caike.com.co/preguntas-frecuentes/).

## Cross-route worklist for all changed routes

Route 28 is **one** of the pending stop/geometry reviews. The [consolidated route geometry, boarding-stop and variant worklist](route_geometry_stop_worklist.md) covers **all 14 official October modified routes plus route 35 Cay**, with priority, action type and source links; the [CSV](route_geometry_stop_worklist.csv) tracks each case's status. Physical stops are added only after location, travel direction, boarding side and source stop-ID matching are verified.
