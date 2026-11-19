# Official operating hours audit — 19 November 2026

## Scope

Every regular route poster listed at [SETP TransMusical — Rutas](https://transmusical.gov.co/rutas/) was viewed (32 individual route names), and the four `alimentador` posters were inspected separately.

- `official_service_hours.csv`: **32** route-specific TransMusical operating windows, including routes **4** and **39** not present as standalone routes in the original GTFS, and the newer poster for **7** replacing the old combined **4/7** identification.
- `official_feeders.csv`: four additional special/feeder services. They advertise individual departures or direction-specific times, so they cannot safely be represented with ordinary route-wide operating windows.
- Images are **linked to their official source URLs**, not redistributed in this repository.
- Poster folders `2026/05`, `2026/06`, `2026/10` indicate upload path; they do **not** independently establish a legally effective date.

## Important limitations

1. `Horario de servicio` on each poster is a route-wide service window. It is not guaranteed to be the first or last departure at each terminus, and cannot be compared as if it were a per-direction `frequencies.txt` entry without a tolerance and separate itinerary evidence.
2. Posters do **not** include a full dispatch frequency table or `headway_secs`. The 16 routes without GTFS frequencies still lack **official, exact headways**.
3. Some posters describe Monday–Saturday and Sunday/holiday windows; the original `calendar.txt` only models Monday–Friday. This is a material coverage omission. Do not create Saturday/holiday trips until validated trip patterns and appropriate headways have been assigned.
4. For route **9**, the end time on Sunday/holidays is too small for reliable transcription from the accessible poster rendition. It is **deliberately blank**, rather than guessed.
5. Route **35** states 1 in 3 buses serve **vereda Cay**; route **48** states 1 in 3 serve **Juntas**. This does not automatically map to GTFS `trip_id` patterns.
6. Route **4** is listed separately on the TransMusical site in addition to **7**, while the upstream GTFS uses `RUTA 4/7`. Model this as an unresolved route-inventory issue, **not** a silent renaming or arbitrary extra route.

## Key official vs upstream frequency-window mismatches to review

The existing GTFS `frequencies.txt` uses headways for 14 routes and leaves 16 without. Comparing earliest `frequencies.txt` start and latest end to official **route-level** Mon–Sat windows highlights (not proofs of GTFS error):

- Route **1**: first modeled frequency 05:20 vs official start 05:30 (10 min earlier)
- Route **2**: 05:20 vs 05:30 (10 min earlier)
- Route **8**: 05:20 vs 05:30 (10 min earlier)
- Route **9**: 05:10 vs 05:30 (20 min earlier), and 21:00 modeled end vs official 20:30
- Route **18**: 04:30 vs 05:00 (30 min earlier)
- Route **20**: modeled end 21:00 vs official 20:30 (30 min later)
- Route **21**: modeled end 21:00 vs official 20:30 (30 min later)

All these comparisons require direction-specific validation. Trips beginning outside an advertised route-level window are warnings for inspection, not an instruction to mechanically truncate a feed.

## Next operations

1. Use `official_service_hours.csv` as the **sole primary source for advertised operating windows**. Secondary sources such as Moovit must not override these.
2. Reconcile route **4**, **7**, **39** and the four feeder services with the route inventory.
3. Obtain primary-source frequency regulations and/or technical dispatch annex to resolve missing `headway_secs` before generating a release.
4. Validate the modified 2026-10 route shapes and stop sequences, then create service calendars for Saturdays, Sundays and Colombian public holidays.
