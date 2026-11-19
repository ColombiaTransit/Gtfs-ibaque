# Ibagué GTFS — ColombiaTransit

Reproducible research and GTFS preparation for public transport in **Ibagué, Tolima, Colombia**.

## Project status

**Research / source-audit stage — not yet a published updated GTFS feed.**

The upstream feed published by the Observatorio de Movilidad y Transporte at Universidad de Ibagué is the starting point. Its original archive remains unchanged. A pinned upstream revision and SHA-256 checksum are recorded in [`sources/upstream.json`](sources/upstream.json).

**Source:** [omtu-unibague/gtfs-ibague](https://github.com/omtu-unibague/gtfs-ibague)  
**Official route posters:** [SETP TransMusical](https://transmusical.gov.co/rutas/)

## Upstream feed inventory (22 May 2026 snapshot)

| Metric | Observed |
| --- | ---: |
| Routes | 30 |
| Trips / patterns | 62 |
| Stops | 1,153 |
| Stop times | 3,925 |
| Shape points | 16,115 |
| Shapes | 62 |
| Frequency rows | 30 |
| Trips without frequencies | 32 across 16 routes |
| Default service calendar | Monday–Friday only |

Declared service dates are 2024-01-01 through 2030-12-31. They do **not** demonstrate that the source remains operationally current.

## Official 2026 legal headway table

The primary frequency source is **Resolución 005549 (9 October 2026), article 3, pages 9–13**. All 30 routes are manually transcribed into [`research/official_resolution_005549_frequencies.csv`](research/official_resolution_005549_frequencies.csv): weekdays and Saturdays each have peak/valley/night headways, while Sundays/holidays have one headway.

- [Full legal-source frequency analysis](research/official_frequency_2026.md)
- [2026 source discovery, legal supersession and outstanding period boundaries](research/official_frequency_investigation.md)

**16/16 originally missing frequency routes now have official legal headways.** The GTFS source ZIP has **not** yet been modified; exact hours for HP/HV/NOC, service-day and trip-direction mapping, updated shapes and validator remain pending. Third-party Moovit frequency estimates are excluded.

## Official operating-hours audit (19 November 2026)

All **36** route posters from [TransMusical's official list](https://transmusical.gov.co/rutas/) were inspected: **32 regular route posters**, plus **4 feeder services** with different direction-specific or individual departure patterns.

- [Official regular route service hours, with direct links to every image](research/official_service_hours.csv).
- [Special feeder service posters](research/official_feeders.csv).
- [Analysis, limitations and currently identified discrepancies](research/official_hours_audit.md).
- [Route coverage and modifications](research/routes.csv).
- [Frequency candidates — secondary, NOT official](research/frequency_candidates.csv).
- [Other research findings](research/findings.md).

The GTFS currently lacks all Saturday, Sunday and holiday calendars, and 16 routes have no `frequencies.txt` entries. Route 39 and separately advertised route 4 are not standalone entries in the source; source route 4/7 corresponds at least in part to the later posted route 7. The official route posters contain **service spans, not complete headways**; the exact headways are instead transcribed from the legally published October 2026 tables.

## Clock periods (HP / HV / NOC)

The provisional 2022 clock profile is recorded with citations, day-type scope, conflicts and route-28 / pre-06:00 exceptions:

- [Clock-block research and legal continuity](research/clock_blocks_audit.md)
- [Machine-readable provisional clock blocks](research/clock_blocks_2022.csv)

The original 2022 regulation was reproduced by a news source and its unmodified provisions are expressly carried forward by article 4 of the original 004951/2026 scanned municipality PDF. However, the intervening 2024 and March 2026 changes have not been fully inspected. **No assumption is silently promoted to a final GTFS service rule.**

## Reproduce audits

Python 3.11+ using standard library only:

```sh
python scripts/audit_source.py --zip gtfs_ibague.zip --output build/audit.json
python scripts/compare_official_hours.py --zip gtfs_ibague.zip --output build/official_hours_comparison.json
# Or fetch the SHA-256-verified pinned upstream copy directly:
python scripts/audit_source.py --download
python scripts/compare_official_hours.py --download
```

The **Audit pinned upstream GTFS** GitHub Actions workflow runs both checks and uploads JSON reports.

## Data integrity policy

1. Preserve the upstream archive unchanged and attribute Universidad de Ibagué / SETP; do not silently rewrite it.
2. Record modifications with source URLs, effective dates and verification status.
3. Do not convert third-party headway ranges into exact GTFS headways without a documented assumption and status flag.
4. An official route-wide service window is not necessarily the first/last departure in every direction. Differences are research flags, not direct instructions to rewrite the GTFS.
5. Verify route shapes affected by the **19 October 2026** change before release.
6. Confirm timetable and branch conditions for four advertised feeder services, routes 4, 7 and 39.
7. Add Colombian public holiday calendars and run the MobilityData GTFS Validator before feed publication.
8. Confirm redistribution permission first: the source repository has no explicit license.

No revised GTFS feed has been generated or published yet.
