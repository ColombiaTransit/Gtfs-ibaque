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
