# Ibagué GraphHopper OSM road candidate pilot — 20 November 2026

**Successful action:** [run #44700800994](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44700800994).

The pilot used the SHA-256 pinned source GTFS (May 2026) and the ColombiaTransit **GraphHopper bus** server on its imported OSM road network. It routed all original stops in order. **No 19 October official via points were supplied yet**; these are road-following research candidates, not validated or replacement GTFS shapes.

| Route | Source pattern | OSM GraphHopper candidate length (km) | Stop visits | Stops farther than 50 m | Max stop-to-candidate offset |
| --- | --- | ---: | ---: | ---: | ---: |
| 8 | `TRIP_R10` | 15.87 | 77 | 0 | 12.4 m |
| 8 | `TRIP_R11` | 15.19 | 60 | 0 | 17.1 m |
| 8 | `TRIP_R12` | 14.80 | 75 | 0 | 12.4 m |
| 8 | `TRIP_R9` | 16.49 | 70 | 0 | 17.1 m |
| 37 | `TRIP_R47` | 13.71 | 56 | 0 | 17.1 m |
| 37 | `TRIP_R48` | 16.61 | 74 | 0 | 11.1 m |
| 50 | `TRIP_R55` | 13.06 | 59 | 0 | 17.3 m |
| 50 | `TRIP_R56` | 13.36 | 57 | 0 | 11.4 m |

**8/8** patterns routed successfully; **0/8** routing failures; **0** stop visits farther than 50 m from the candidate line. There were 51 GraphHopper requests, chunked across the 8 patterns.

**Not yet verified:**
- Route 8's official change from Calle 108 to Calle 100. A stop-only shortest-path result can still follow the old street.
- Route 37 return direction's Calle 15 vs Calle 16.
- Route 50's changed *return direction only* via La Tobogán, Calle 42 and Guabinal.
- The routing server OSM import date was not independently certified as containing the relevant October 2026 street edits.
- Exact source stop sequence fitness after itinerary changes and direction assignment.

Keep the old source shapes in the research GTFS until the required official via-points and affected direction(s) are reviewed. The workflow stores a temporary research artifact with GeoJSON, stop manifest, per-pattern QA and provisional `candidate_shapes_NOT_GTFS.txt`, **not** a public release or generator override.
