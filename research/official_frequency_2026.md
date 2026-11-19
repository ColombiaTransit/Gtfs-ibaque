# Official frequencies — Ibagué, October 2026

**Primary legal source:** Resolución No. **005549 of 9 October 2026** from the *Secretaría de Movilidad de Ibagué*: [original municipality PDF](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf).

- Source SHA-256: `fe718cac309bcc34dd75cec28140f9c99cd7f77ad8971b8e1778f56bc3ba41a1` (13 scanned pages).
- The source **revokes Resolución 005459 of 6 October 2026** and **partially replaces Articles 1 and 3 of Resolución 004951 of 15 September 2026**.
- Its **Article 3** publishes **Características del servicio / arquitectura de rutas / etapa de transición SETP / octubre 2026**.
- Data recorded in [`official_resolution_005549_frequencies.csv`](official_resolution_005549_frequencies.csv), **all 30 routes**, with exact day-type and source-page columns.
- Manually verified against rendered original PDF tables, **not accepted blindly from OCR**.

## Frequency schema

- **Días ordinarios:** `FREC HP` (peak), `FREC HV` (valley), `FREC NOC` (night) on PDF **pp. 9–10**.
- **Días sábados:** same three columns, PDF **pp. 10–11**.
- **Días domingos y festivos:** single `FREC` column, PDF **pp. 12–13**.
- All values are headways **in whole minutes**. `FREC NOC=0` for route **29** on weekdays/Saturdays indicates **no night service**; do not turn it into a 0-second GTFS headway.
- The table also specifies route-wide advertised service-hours spans. These **are not inherently direction-specific first and last departure times**.

## The 16 missing-frequency routes — current legal figures

| Route | Mon–Fri HP/HV/NOC | Sat HP/HV/NOC | Sun/holiday |
| --- | --- | --- | --- |
| 22 | 6/6/8 | 7/7/8 | 8 |
| 23 | 6/7/10 | 7/8/10 | 10 |
| 24 | 6/6/10 | 7/7/10 | 8 |
| 28 | 7/8/12 | 8/9/12 | 10 |
| 29 | 25/30/— | 25/30/— | 25 |
| 31 | 8/8/12 | 9/9/12 | 10 |
| 33 | 8/9/12 | 9/10/12 | 10 |
| 35 | 7/7/10 | 8/8/10 | 8 |
| 37 | 6/6/9 | 7/7/9 | 8 |
| 40 | 4/5/7 | 5/6/7 | 7 |
| 43 | 5/5/8 | 6/6/8 | 8 |
| 48 | 9/9/12 | 10/10/12 | 8 |
| 50 | 8/9/12 | 9/10/12 | 10 |
| 53 | 7/7/12 | 8/8/12 | 10 |
| 82 | 5/6/6 | 6/7/6 | 6 |
| 90 | 5/6/10 | 6/7/10 | 9 |

## Critical implementation questions

1. **Clock intervals for HP/HV/NOC.** Detailed investigation and machine-readable provisional mapping: [clock_blocks_audit.md](clock_blocks_audit.md) / [clock_blocks_2022.csv](clock_blocks_2022.csv). 004951/2026 article 4 explicitly preserves applicable 000370/2022 provisions, and 005549/2026 article 4 retains unchanged provisions of 004951. However, check intervening amendments before declaring 2022 cutoff hours legally confirmed for 2026. The 2022 text also has an early-morning demand-dependent exception and a distinct 16:00–18:00 peak for route 28. 

   **Prior note:** Resolución 005549 provides headways per classification but does not define the cutover clock times in its reproduced tables. An earlier 2022 resolution transcription in [CambioIn](https://www.cambioin.com/principal/los-cambios-profundos-que-tendra-el-transporte-urbano-en-ibague) reports peak 06:00–08:30, 11:30–14:30 and 17:00–19:30; valley 08:30–11:30 and 14:30–17:00; night 04:40–06:00 and 19:30–22:00. **That is secondary historical text, not a 2026-verified clock profile.** It also contains an inconsistent printed end time for afternoon valley in one passage. Do not assert these times still govern 2026 without checking later acts or an original attachment.
2. **Official source discrepancy:** TransMusical's current [route posters](https://transmusical.gov.co/rutas/) differ in some service-hour spans from the October 2026 legal table. Both originate from government or SETP organizations; retain both as sources and mark conflicts for investigation (not automatic reconciliation).
3. Route **4/7** is what the *October 2026 legally binding table actually calls it*. The official TransMusical site lists **4** and **7** separately; do not split or rename without resolving which operation and variant each represents.
4. Route **39**, shown on the TransMusical site, does **not** appear in this 30-route regulatory table. Its operational/legal status requires separate confirmation.
5. The act explicitly notes **route 48 Juntas service**: until separate feeder operation starts, every **third departure** of route 48 on Mon–Sat must go to Juntas; Sunday/holidays **all vehicles** go to Juntas. Two morning departures from Juntas **05:00 and 05:40** are specified. Those are variant/service rules, not frequency for the main route. See PDF pp. 7–8.
6. Route 28 has **additional weekend/holiday departures from Parque Recreacional Caiké** (PDF p. 6), without fixed clock times specified there; not yet modeled.
7. The original Universidad de Ibagué GTFS has **30 frequency rows across 14 of these 30 routes**, and 16 routes have none. It has **no weekend service**, despite the official regulation. The released upstream `frequencies.txt` must be rebuilt using these legal data, not overwritten piecemeal.
8. The table gives route-level headways, not proof that all directions use separate full intervals or that every route's `trip_id` maps one-to-one with a timetable. Avoid duplicating jointly served services and check loop variants.
9. **Calendar:** Colombian holidays follow Sunday service per source. Explicit holiday exceptions need `calendar_dates.txt`.
10. All 30 route/period rows are transcribed in CSV. Before feed release, validate the exact cutoff times and geometries, and run the MobilityData GTFS Validator.

## Earlier official 2022 norm citation

Older research gave headway *standards* for eight routes, but these are **superseded for the headway register** by the direct October 2026 source. Retain [`historical_official_frequency_standards.csv`](historical_official_frequency_standards.csv) for provenance; **do not** use 2022 values in 2026 feed generation.

## Data verification and source scope

- The PDF tables were rendered and each of the **30 × 7 = 210 frequency values** was manually read. The original OCR is stored in GitHub Actions [run #44600046626](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44600046626), where PDF source files and OCR excerpts were archived in the `ibague-official-resolutions-2026` artifact.
- Days, times, and frequency spans are exactly the **published scheduled standards**, not demonstrated realized departures on street.
