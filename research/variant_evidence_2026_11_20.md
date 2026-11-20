# Ibagué route variants — source-evidence check (20 November 2026)

**Status:** evidence classified, NOT a verified route-variant timetable. No changes to `scripts/build_gtfs.py`, `trips.txt`, `frequencies.txt`, or `shapes.txt` are approved here.

## Route 8 — four source trip patterns are NOT three confirmed variants of direction 1

Primary technical input: pinned May 2026 Universidad de Ibagué GTFS, source SHA-256 `7cf772c89dec4ac1a0f97e709c9db519ad8d146caaf2121fe624c149ed29c050`. Its ordered stop lists were preserved in [GH research run 44701165571](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44701165571) artifact `route_waypoint_review_manifest.json`. This is a source-structure finding, not an assertion of 2026 actual bus operations.

| Source trip | Original direction_id | Stops | Candidate common-direction family |
| --- | --- | ---: | --- |
| `TRIP_R9` | 0 | 70 | A |
| `TRIP_R11` | 1 | 60 | A (direction_id conflicts) |
| `TRIP_R10` | 1 | 77 | B |
| `TRIP_R12` | 1 | 75 | B |

- R9/R11 share **49 exact stop_id values**, all **49 in identical relative visit order** (0 inversions of 1,176 possible pairs).
- R10/R12 share **61 exact stop_id values**, all **61 in identical relative visit order** (0 inversions of 1,830 possible pairs).
- The two provisional families **share zero exact stop IDs** (R9 vs R10/R12; R11 vs R10/R12).
- R11 is marked `direction_id=1` despite sharing 49 ordered stops with R9, marked `direction_id=0`. Thus the original direction metadata cannot safely be used to classify the trip without further verification.
- These results suggest **two geographic directional families, each with two partially overlapping or truncated patterns**. They do **not** establish that there are two simultaneously operated route variants in each direction; a source stop sequence can include archival, partial, and terminal records.
- Current generator `build_gtfs.py` interleaves **three** direction-1 source patterns with an equal 1/3 share. This is explicitly **provisional and unsupported by these findings**. Do not make the 1/3 allocation a confirmed operational fact.
- Need: compare all four ordered stop paths and endpoints against the [official October 2026 route 8 map](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-8-scaled.png), especially the shift from Calle 108 to Calle 100, then determine whether R11/R12 are short-turns, historical fragments, actual different routing, or duplicated segments. Correct direction grouping before using variant-specific headways.

## Route 35 — Cay extension

- Official [TransMusical route 35 poster](https://transmusical.gov.co/wp-content/uploads/2026/06/Ruta-35-scaled.jpg): **one in three vehicles** reaches vereda Cay. Normal 2026 route frequency and operating windows already recorded in `research/official_resolution_005549_frequencies.csv` and `research/official_service_hours.csv`.
- Original pinned GTFS has **two** route-35 source patterns, not a documented normal/Cay pair; do **not** infer the branch from two directions.
- Branch policy can be captured as a **rule** now, but not as a verified GTFS variant trip until the divergence junction, branch-specific ordered stops and exact day-type scope have been sourced. Keep source route frequency as **combined**, not duplicated.

## Route 48 — Juntas extension

- [Official Resolución 005549 (9 October 2026), pp. 7–8](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf) establishes **every third departure to Juntas Monday–Saturday**, **all Sunday/holiday departures to Juntas**, conditional on the separate feeder entering operation; also records departures **05:00 and 05:40 from Juntas**.
- Original pinned GTFS has two source patterns, `TRIP_R53` (17 stop visits, direction 0) and `TRIP_R54` (85, direction 1), **not** proof of a normal-versus-Juntas pair. The asymmetric stop counts require source completeness review.
- The rule can be recorded, but a definitive Juntas GTFS variant needs branch geometry/stop order, interpretation of the conditional feeder clause, and assignment of the two specified departures. Do not assume 1/3 of full legal frequency on each direction independently.

## Route 28 — Caiké

- [TransMusical October route 28 map](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-28-scaled.png) and [Parque Caiké operator's arrival instructions](https://caike.com.co/preguntas-frecuentes/) say route 28 now reaches the park gate; return boarding is on the **opposite side of the main road**.
- An older, separately branded Caiké feeder must **not** be conflated with route 28's revised alignment. Published legal text also refers to **additional weekend/holiday departures** from the Caiké area, but the project has not verified their exact clock times.
- Source has only two patterns (one per nominal direction). Whether the new direct park service is the **standard post-October alignment** or a separate operating variant is not yet proven; do **not** invent a frequency share or timed trips.

## Decision gate

- **Enough to store as source-backed branching policies:** 35 and 48, with validity/source and confidence fields, and a tentative 8 two-family structure.
- **Not enough to enable automatic distinct trip patterns:** all four route cases (8, 28, 35, 48), pending current map-constrained road geometry, stop order and verified dispatch allocation.
- Existing GraphHopper trial produced road-following candidates for all 14 changed routes, but used original stop sequences and **zero official October map via-waypoints**. It does not resolve the operational branch identities.
- Keep all findings separate from generator activation until accepted.
