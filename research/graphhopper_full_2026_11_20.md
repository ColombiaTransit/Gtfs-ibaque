# Ibagué — all fourteen changed routes via OSM GraphHopper (20 November 2026)

**Status:** first complete road-following *research candidate* generation successful. **No source GTFS, generator shape or public release changed.**

- [GitHub Actions run #44701165571](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44701165571) — self-hosted GraphHopper, `bus` profile, OSM road graph.
- The original GTFS was downloaded from the pinned May 2026 SHA-256-verified university archive. Route `4/7` was mapped to official label `7` for the geometry audit **only**.
- **30 of 30** source patterns routed successfully across **14** routes; no GraphHopper request failures.
- **0 stop visits** farther than 50 m from their provisional OSM road candidates; maximum **36.2 m** (route 29).
- **Important:** good stop proximity **does not establish an accurate October 2026 route**. The first pass uses the source stop sequence and has **zero official October 2026 via anchors**. GH may select the old or shortest streets instead of a newly required bus detour.

| Route | Patterns | Stop visits | Maximum stop offset | GH requests |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 131 | 14.1 m | 13 |
| 2 | 2 | 128 | 17.1 m | 13 |
| 7 | 2 | 102 | 27.3 m | 10 |
| 8 | 4 | 282 | 17.1 m | 27 |
| 9 | 2 | 158 | 25.0 m | 15 |
| 15 | 2 | 158 | 14.1 m | 15 |
| 19 | 2 | 160 | 17.1 m | 16 |
| 21 | 2 | 130 | 23.5 m | 12 |
| 28 | 2 | 86 | 12.4 m | 8 |
| 29 | 2 | 49 | 36.2 m | 5 |
| 37 | 2 | 130 | 17.1 m | 12 |
| 40 | 2 | 145 | 12.7 m | 14 |
| 48 | 2 | 102 | 19.8 m | 10 |
| 50 | 2 | 116 | 17.3 m | 12 |

**Immediate review targets:** route 8 through Calle 100 (rather than Calle 108); route 37 inbound via Calle 15; route 50 return through La Tobogán / Calle 42; route 1 Arboleda extension; route 15 no Santa Cruz; route 7 remapping of the former 4/7; route 48 urban diversion and Juntas branch. All other official modifications are recorded separately in [`route_changes_2026_10_19.csv`](route_changes_2026_10_19.csv).

The research artifact from this run contains `candidate_road_shapes_RESEARCH_ONLY.geojson`, `candidate_shapes_NOT_GTFS.txt`, `pattern_route_qa.json`, and `route_waypoint_review_manifest.json`. It is temporary, not an approved downloadable GTFS feed. Candidate shapes must be checked against the officially published new itinerary and explicit via points per affected direction before promotion.

The road geometry reflects the GraphHopper server's imported OSM snapshot, which is not an authoritative legal bus-route map. Source attribution © OpenStreetMap contributors (ODbL); the pinned original GTFS redistribution license remains unresolved.

Machine-readable overview: [`graphhopper_full_2026_11_20_summary.csv`](graphhopper_full_2026_11_20_summary.csv).
