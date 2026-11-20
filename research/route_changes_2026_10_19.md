# Ibagué: fourteen geometry amendments effective 19 October 2026

**Status (20 November 2026): primary source and map inventory complete; no route shape is verified or replaced.**

Sources: the [municipal announcement]( https://www.ibague.gov.co/portal/noticias/23334-este-lunes-cambiaran-los-recorridos-de-14-rutas-de-busetas-en-ibague-conozca-sus ) (18 October 2026), the [official SETP route-posters](https://transmusical.gov.co/rutas/) (October 2026 image paths), pinned May 2026 Universidad de Ibagué GTFS, and an independently supplied supplementary Moovit-derived GTFS with service calendar starting 13 November 2026.

## Inventory

| Route | Pinned upstream route_id | Patterns | Verified official itinerary change | Official new map |
| --- | ---: | ---: | --- | --- |
| 1 | 1 | 2 | Extends via Pedro Tafur and airport road to Arboleda del Campestre; enters La Samaria via Clínica Virrey Solís and Makro | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-1-scaled.png) |
| 2 | 8 | 2 | From Avenida Ambalá turn at Calle 69 roundabout near Universidad de Ibagué into Jordán 9 and via Calle 64 to Carrera Quinta/Multicentro | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-2-scaled.png) |
| 7 | 20 | 2 | Former combined 4/7 renamed route 7; changes streets around Carreras Primera and Segunda in central Ibagué | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-7-scaled.png) |
| 8 | 27 | 4 | At Nueva Castilla/Topacio use Calle 100 passing Mercacentro instead of Calle 108 | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-8-scaled.png) |
| 9 | 29 | 2 | Extend former Santa Bárbara route leg to Barrio Santa Cruz | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-9-scaled.png) |
| 15 | 4 | 2 | Stop serving Santa Cruz; at Panóptico take Calle 10 toward Carrera Cuarta | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-15-scaled.png) |
| 19 | 7 | 2 | Direct connection from Arboleda del Campestre toward Avenida Pedro Tafur | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-19-scaled.png) |
| 21 | 10 | 2 | From Carrera Quinta continue toward Piscinas Olímpicas, then Versalles | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-21-scaled.png) |
| 28 | 14 | 2 | Service extended/diverted directly into Parque Recreacional Caiké; additional weekend/holiday departure conditions are not fully transcribed | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-28-scaled.png) |
| 29 | 15 | 2 | Municipal announcement describes terminal shift toward Carmen de Bulira; official poster still depicts endpoints at both Calambeo and Carmen de Bulira | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-29-scaled.png) |
| 37 | 19 | 2 | Remove Calle 16 segment between Carrera Quinta and Primera; inbound return uses Calle 15 | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-37-scaled.png) |
| 40 | 21 | 2 | No longer reaches Calle 17; instead of Avenida Ferrocarril from Calle 42 take Carrera Quinta toward Versalles | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-40-scaled.png) |
| 48 | 23 | 2 | From Calle 115 use Avenida Guabinal by Clínica Sharon toward Calle 67 instead of Carrera Quinta/Éxito bridge | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-48-scaled.png) |
| 50 | 24 | 2 | Outbound ascent unchanged; return via La Tobogán and Calle 42 to Avenida Guabinal | [Poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-50-scaled.png) |

**Coverage:** 14 official route labels / 30 pinned upstream patterns; route 8 uniquely has four patterns; the other thirteen routes each have two.

## Supplementary GTFS cross-check

The supplementary ZIP has a November 13, 2026 calendar beginning date, but that is NOT proof of post-October geometry. It lists route 4 and not route 7. It still titles route 1 `Delicias - Belén`, route 9 `Nueva Castilla - Villa Adriana`, and route 15 `Protecho - Santa Cruz`. These clash with new destinations/removed service in the official October posters. Route 1's candidate shape bounding box (lat 4.4285–4.4630, lon -75.2461 to -75.1901) does not reach Arboleda del Campestre, while the same candidate dataset maps Arboleda-serving routes 4/19 much farther southeast (near lat 4.39, lon -75.14); treat the alternative route 1 shape as stale. All candidate shapes remain **unverified** pending shape-by-shape review.

**Route 29 nuance:** the government press release describes a terminal change, but the October poster shows both Calambeo and Carmen de Bulira as route extremities. Do not delete Calambeo stops solely on that wording.

**Conflicting secondary report:** some news reports list route 53 among changed services (15 rather than 14); the municipality's 18 October statement and the corresponding fourteen October 'Nuevo Trayecto' posters are the controlling inventory. Put route 53 in a separate follow-up if an official change notice is found.

## Next geometrical audit (do not repeat frequency and fares research)

1. Extract the pinned source route, trip, shape and ordered stop sequence for these 30 patterns, including the four route-8 patterns.
2. For each official October poster, use its 'actualización en el trayecto' inset and reference-point sequence; map only the changed road segments, preserving unaffected shape and stop IDs.
3. For route 7, reconcile '4/7' → '7' route identity and the separately posted '4' without deleting valid service. Do not infer from the Moovit candidate route 4.
4. For 28/48 and 29, isolate branch or terminal variants; verify the direction affected (especially 37 and 50). Do not fabricate stop_times.
5. If no machine-readable new geometry exists, obtain OSM road segments and route them between officially evidenced waypoints; keep a geometry QA flag until the alignment and stop order are checked.
6. Run MobilityData validation and compare shape-to-stop distances **after** actual replacement. The research-only preview generator should retain old shapes until explicitly accepted.

Machine-readable list: [`route_changes_2026_10_19.csv`](route_changes_2026_10_19.csv).
