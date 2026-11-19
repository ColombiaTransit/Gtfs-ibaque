# Ibagué GTFS — ColombiaTransit

Reproducible research and GTFS preparation for public transport in **Ibagué, Tolima, Colombia**.

## Project status

**Research / source-audit stage — not yet a published updated GTFS feed.**

The upstream feed published by the Observatorio de Movilidad y Transporte at Universidad de Ibagué is the starting point. Its original archive remains unchanged. A pinned upstream revision and SHA-256 checksum are recorded in [`sources/upstream.json`](sources/upstream.json).

**Source:** [omtu-unibague/gtfs-ibague](https://github.com/omtu-unibague/gtfs-ibague)  
**Transport authority / route information:** [SETP TransMusical](https://transmusical.gov.co/rutas/)

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

The upstream feed declares service dates 2024-01-01 through 2030-12-31, but this **does not demonstrate that its service patterns are current**.

## Research registers

- [Route inventory and change flags](research/routes.csv): route-by-route audit status.
- [Frequency candidates](research/frequency_candidates.csv): *unverified planning leads*, not approved GTFS headways.
- [Source findings and open questions](research/findings.md): official changes, route 39, service-day limitations and required checks.

## Reproduce the source audit

Python 3.11+ with **standard library only**:

```sh
python scripts/audit_source.py --zip gtfs_ibague.zip --output build/audit.json
# Or download the pinned upstream copy:
python scripts/audit_source.py --download --output build/audit.json
```

Run the **Audit pinned upstream GTFS** GitHub Actions workflow to download the pinned ZIP, verify SHA-256, and publish an audit JSON artifact.

## Data integrity policy

1. Preserve the original upstream ZIP byte-for-byte and attribute Universidad de Ibagué / SETP. Do not silently rewrite the source.
2. Record all changes separately with source URLs, effective dates, and verification status.
3. Do not convert frequency ranges into exact GTFS `headway_secs` without a documented assumption and a distinct status flag.
4. Do not infer weekend or holiday service merely from an advertised timetable when it cannot be mapped to each trip pattern.
5. Validate route geometry affected by changes effective **19 October 2026** before publication.
6. Add Colombian public holidays and the MobilityData GTFS Validator during the feed-generation phase.
7. Confirm reuse rights before redistributing the upstream archive or publishing a derived feed; the upstream repository currently does not specify a license.

This repository intentionally does **not** claim that the missing frequencies or modified shapes have been fixed.