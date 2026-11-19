# Ibagué source investigation — 2026-11-19

## Verified from the supplied GTFS ZIP

- Published as `v1.0_20260522` by Observatorio de Movilidad y Transporte / Universidad de Ibagué / SETP.
- 30 routes, 62 trip patterns, 1,153 stops, 3,925 stop times, 62 shapes (16,115 points).
- `frequencies.txt` has 30 rows and covers 30/62 trip patterns. Missing for routes **22, 23, 24, 28, 29, 31, 33, 35, 37, 40, 43, 48, 50, 53, 82, 90** (32 trip patterns).
- `calendar.txt` contains one weekday-only service, Monday–Friday; no Saturday/Sunday and no `calendar_dates.txt`. Declared validity through 2030 must not be treated as verified current service.
- 78 stops have the placeholder name `Marcador De Local Sem Titulo`. Further stop-name cleanup needed.
- The supplied ZIP passed a basic referential integrity audit. This is **not** a MobilityData GTFS Validator result.

## Verified from official publications

- [Alcaldía de Ibagué, 18 October 2026](https://www.ibague.gov.co/portal/noticias/23334-este-lunes-cambiaran-los-recorridos-de-14-rutas-de-busetas-en-ibague-conozca-sus): geometry/itinerary changes effective **19 October 2026** to routes **1, 2, 7, 8, 9, 15, 19, 21, 28, 29, 37, 40, 48, 50**. Assess the geometry and stop order for those routes before release; only changed portions should be rebuilt.
- The same publication says old **route 4/7** is operated under **route 7**.
- [SETP TransMusical's public route list](https://transmusical.gov.co/rutas/) includes **route 39**, absent from the upstream archive. The public site also displays other named/numbered route entries; do not automatically treat every listing as covered by the upstream archive.

## Candidate / unverified information

- `research/frequency_candidates.csv` captures preliminary Moovit weekday windows and headway ranges gathered in earlier research. They represent **one selected direction**, are **not independently revalidated here**, and are *not exact headways*.
- TransMusical route posters may contain weekday, weekend and holiday operating hours. Read individual source images and link each to its route and effective date before entering a calendar override.
- Possible distinct service branches for routes **35** (Cay) and **48** (Juntas) require confirmation against specific official posters and GTFS shapes.
- [Article about Resolución 00197 of 30 April 2024](https://caracol.com.co/2024/05/03/conozca-los-cambios-en-el-recorrido-de-algunas-rutas-de-bus-en-ibague/) identifies frequency/service-window regulation. **Full original resolution and technical annex not yet obtained**; do not treat the article as a route-level timetable.

## Follow-up work

1. Locate original Resolución 00197/2024 and its technical annex; check if later acts supersede it.
2. Compare affected 2026 routes against up-to-date official route maps before changing shapes.
3. Verify each frequency window **per direction and service day** using primary source data; convert headway bands to GTFS only with an explicit documented assumption.
4. Verify weekend/holiday service and make service calendars match actual applicable trips.
5. Confirm route 39 operational details and whether it belongs in the published feed.
6. Clean placeholder stop names using official stop inventories; do not silently rename stops from guesswork.
7. Establish license/redistribution permission, build a derived generator, run the official MobilityData GTFS Validator, then publish a versioned feed.

## Source provenance

The original archive is pinned to upstream commit `55be037eaeaa7031eb095af53929e4ef2caaba9a` with a SHA-256 checksum; see `sources/upstream.json`. The source ZIP itself is not copied into this repository while its redistribution terms are unclear.
