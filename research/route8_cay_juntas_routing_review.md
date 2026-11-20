# Route 8 direction families and OSM candidate branches for routes 35/48

**Research task (20 November 2026):** use actual October 2026 TransMusical directions, 2026 official branch rule, 2026 OSM points, and the original SHA-256-pinned GTFS trip coordinates without changing the public research generator or making assumed departure times.

## Route 8: now evidence for direction, still no variant frequency evidence

Official TransMusical October 2026 [route 8 map](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-8-scaled.png) explicitly states **IDA: Nueva Castilla → Santa Bárbara** and **VUELTA: Santa Bárbara → Nueva Castilla**. Four pinned 2026-05 source patterns run along these east–west geographic axes:

| Source trip | Source `direction_id` | Map direction matched by geographic course | Additional uncertainty |
| --- | --- | --- | --- |
| `TRIP_R9` | `0` | IDA (east → west) | longest westward terminus; October street detail still to be verified |
| `TRIP_R11` | `1` | **IDA** (east → west) | source direction_id conflict; west endpoint approx **1,282 m** before R9's west endpoint |
| `TRIP_R10` | `1` | VUELTA (west → east) | longest westward origin; mixed terminal labels |
| `TRIP_R12` | `1` | VUELTA (west → east) | west origin approx **1,149 m** short of R10's origin |

These findings reproduce 49 and 61 shared exact stop IDs respectively, all in the same visit order within each pair. They now have **two independent lines of evidence**: stop identity/order and the official poster's geographic direction. This strongly indicates that `R11` is mislabeled in the source as direction 1. It **does not prove** that `R11` and `R12` are legitimate actively scheduled shortened workings, or determine their frequencies or first/last dispatches. The October Calle 100 detour remains to be matched with OSM road geometry.

**Do not automatically change the active generator's `direction_id` and 1/3 allocation** until current shortened service is confirmed. However, the source metadata issue is now explicit rather than merely speculative. A reviewer can use the stable audit's `route8_direction_evidence.csv` to document an eventual approved correction.

## Route 35 Cay: candidate reference point from OSM

The [TransMusical official route 35 poster](https://transmusical.gov.co/wp-content/uploads/2026/06/Ruta-35-scaled.jpg) notes that **one in three buses reaches vereda Cay**. The public OSM [node 4339120589](https://www.openstreetmap.org/node/4339120589) is tagged `amenity=bus_station`, named `Vereda Cay`, around **4.47358, -75.25473**. This is a possible target *for a rural road-routing candidate*, not verified as a transit agency stop, official turnaround or branch end.

The pinned source's two trips `TRIP_R45` and `TRIP_R46` are not normal vs Cay variants. Find the endpoint of each trip closest to the Cay OSM point and request a directional GraphHopper **bus-profile** road between them; preserve source patterns. Never fill in missing ``stop_times.txt`` or infer stop positions from the resulting road.

## Route 48 Juntas: current source stops short of rural village

The [official October 2026 route 48 poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-48-scaled.png) notes **one in three buses reaches Juntas**. Resolución 005549 also establishes every third dispatch Mon–Sat, all Sunday/holiday, conditional on separate feeder operation, plus departures **05:00 and 05:40 from Juntas**. The OSM [Juntas village node 703223338](https://www.openstreetmap.org/node/703223338) is around **4.55603, -75.32140**. This is a *place centroid*, **not** a verified stop or terminal.

The University GTFS's `TRIP_R54` starts near **4.52578, -75.31056**, essentially **Villa Restrepo** (OSM village **4.52434, -75.31086**), not Juntas. `TRIP_R53` ends near **4.51307, -75.30389**. Thus the source trips **do not fully demonstrate the additional 2026 Juntas extension**; especially do not treat `R54` as an already verified Juntas origin. To prepare the extension, request GraphHopper bus-road candidates toward OSM Juntas from the nearer source end of each trip and retain `official_branch_stop_sequence_verified=false`.

## Machine-executable investigation

- [`scripts/review_route8_and_branches.py`](../scripts/review_route8_and_branches.py) calculates direction and terminal distances from the **pinned SHA** (not the user's unpinned supplementary feed).
- [CI](../.github/workflows/review-route8-cay-juntas.yml) runs offline tests, builds `route8_direction_evidence.csv` and `branch_variant_manifest.json`, and, when organizational GraphHopper is configured, requests only **4** two-point OSM-road candidate segments in addition to the prior **182 successful route-geometry queries**. It reuses existing infrastructure instead of rerouting 14 routes.
- It uploads temporary research artifacts only: no source GTFS, candidate boarding stops, `shapes.txt` production changes, `trips.txt` or `frequencies.txt` edits.

**Remaining route geometry decisions:** verify the precise Calle 100 route-8 diversion and source stop positions against the October poster. For Cay and Juntas, confirm the actual branch junction, roadway legality, official boarding points, and whether the new branch has a validated return path and stop sequence. Only then permit variant trips and rule-based one-in-three/headway scheduling in the generator.
