# Route 48 — Juntas branch and stop validation (20 November 2026)

**Stage:** source geometry / stop QA. The October 2026 official timetable rule is known, but neither the exact official boarding point at Juntas nor a fully current two-direction trip pattern has been proven. **Do not yet add new GTFS trips, stops or shapes.**

## Primary evidence

- [TransMusical October 2026 route 48 poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-48-scaled.png) shows the *ordinary* Tierra Firme ↔ Villa Restrepo itinerary and notes an extension to **Juntas on one in three vehicles**; it does not separately draw Juntas beyond Villa Restrepo.
- [Alcaldía Ibagué, 18 October 2026](https://www.ibague.gov.co/portal/noticias/23334-este-lunes-cambiaran-los-recorridos-de-14-rutas-de-busetas-en-ibague-conozca-sus): updated city route on **Calle 115 → Avenida Guabinal via Clínica Sharon → Calle 67**, avoiding the former Carrera Quinta/Éxito bridge trajectory, effective **19 October 2026**.
- [Resolución 005549, 9 October 2026, pages 7–8](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf): while the separate feeder is not operating, **every third dispatch to Juntas Monday–Saturday**; **all dispatches to Juntas on Sunday/Colombian holidays**; **05:00** and **05:40** departures explicitly recorded *from Juntas*. Conditional status of separate feeder needs review prior to final operation model. The 9/9/12 (weekday HP/HV/NOC), 10/10/12 (Saturday), 8 (Sunday/holiday) minute headways are **total route headways, not separate headways for two full routes**.
- [Moovit route 48 to Tierra Firme](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-48-Ibagu%C3%A9-4506-957721-86260811-1) and [to Juntas](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-48-Ibagu%C3%A9-4506-957721-86260811-0): **secondary**, with listed Juntas/Iguaima/Villa Restrepo/Pastales/Puerto Perú/Llanitos/Tres Esquinas stops. Published stop labels are not authoritative coordinates, and parts of older city itinerary may be out of date.

## Pinned-source GTFS review (May 2026, source SHA checked in previous Actions)

| Trip | Source direction | Stop visits | What the recorded pattern actually covers |
| --- | --- | ---: | --- |
| `TRIP_R53` | 0, to rural sector | **17** | Begins at a stop around 4.44370, -75.23725, **not Tierra Firme**, and ends at source stop **1198** (4.51307, -75.30389), before the Villa Restrepo village reference |
| `TRIP_R54` | 1, to Tierra Firme | **85** | Starts at source stop **1258** (4.52578, -75.31056), around Villa Restrepo, **not Juntas**, and finishes at source stop 1320 in Tierra Firme |

This is an **asymmetric or incomplete source pattern**, not evidence of a 17-stop express trip or a verified rural branch. Do not generate new short-turn trips by assuming every source template is a full current scheduled direction.

## Road QA from the previously generated GraphHopper candidates

Existing results reused from [full route audit](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44701165571) and [Cay/Juntas branch audit](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44711047487), **without re-running either 182 requests or the rural branch requests**.

| Direction | Prior source road candidate | Rural branch candidate | Join gap |
| --- | ---: | ---: | ---: |
| R53 toward Juntas | **13.36 km** | **5.98 km** | **4.9 m** |
| R54 from Juntas | **26.40 km** | **4.16 km** | **0.1 m** |

The candidate branch roads pass **Villa Restrepo → Iguaima → Juntas** for R53, and **Juntas → Iguaima → Villa Restrepo** for R54. All *sampled* points on the shorter branch road are within **55 m** of the opposite-direction candidate in the first QA trial. This verifies **road corridor consistency**, not actual bus directions or legal routing. Reference places are not licensed passenger stop IDs.

The rural route remains incomplete because R53's old trip misses the eastern city origin, R54 omits Juntas, and the precise city update on Avenida Guabinal has **no approved official via anchors**.

## Narrow stop inventory step

New research-only [audit script](../scripts/audit_route48_juntas.py) and [GitHub workflow](../.github/workflows/audit-route48-juntas.yml) reuse existing Actions artifacts, check ordered geographic witnesses, and optionally query the *organization Overpass* for `highway=bus_stop`, `public_transport=platform/stop_position`, and `amenity=bus_station` in a small bounding box around Villa Restrepo and Juntas. Results are classified as OSM candidate objects only. An empty / unavailable OSM response does **not** prove no stops exist. No source-derived stop coordinates are committed to GitHub; QA is uploaded as temporary artifacts.

**To close route 48:** determine official stop/terminal at Juntas (including the opposite side), verify the intermediate directional stop list and update R53 with missing city visits; compare Avenida Guabinal revision with the October official map and reroute only its affected segment. Confirm the feeder condition, then implement a single combined corridor headway with 1-of-3 Juntas dispatches Mon–Sat / all on Sunday-holidays and the special 05:00/05:40 Juntas-origin departures, without producing invented stop-to-stop run times.
