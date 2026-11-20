# Ibagué GTFS generator v1 — research preview, NOT publication

This first generator creates a **reproducible local GTFS preview** from the SHA-256 pinned 22 May 2026 Universidad de Ibagué ZIP. It is **not a verified current-day transport schedule** and **must not be published or redistributed** until source rights and operational assumptions are resolved.

## Inputs and provenance

- Pinned upstream archive: `sources/upstream.json` (unmodified ZIP and checksum). The archive is downloaded only when the generator runs; it is not committed here.
- Route headways: `research/official_resolution_005549_frequencies.csv`, manually verified against *Resolución 005549*, 9 October 2026, article 3, pp. 9–13; all 30 existing routes and 210 weekday/Saturday/Sunday period values.
- Service windows: **2026 regulation service spans**, with disagreements against the separately audited TransMusical posters left as review findings. Service spans are route-wide, not proven first/last dispatch per direction.
- HP/HV/NOC clock limits: historical 2022 bands only, **provisional** because amendments in 2024 and March 2026 could not be directly checked. See `research/clock_amendment_final_review.md`.
- Weekend and Colombian holiday calendar: the `python-holidays` Colombia holiday list. A holiday on Monday–Saturday changes that date to Sunday-type service using `calendar_dates.txt`.
- Stop improvements: optional, explicit `--approved-stop-overrides` CSV, with columns `stop_id,stop_name,source_url,approved` and `approved=yes`. Only original unnamed placeholders can be renamed. **No candidate from the user-supplied November ZIP is automatically accepted**; the 16 strong and 17 secondary matches remain QA leads, pending side-of-road/direction checks.

## Behavior and preservation

- Preserves **all 30 original routes**, source `route_id` and `stop_id`, stop locations, the source shapes and the original stop order. Does **not** invent October 2026 modified geometry or add route 39/4/feeder services.
- Builds three GTFS template services: `CT_WK`, `CT_SA`, `CT_SU`; generates trips and `frequencies.txt` from existing validated stop-time differences, without guessing missing or non-monotonic template travel times. Unusable patterns are **excluded and reported**, not silently repaired.
- Reconstructs provisional workday and Saturday frequency clock bands (05:xx starts clipped to legal route hours), and one constant period on Sunday/Colombian holidays. Route 29 `FREC NOC=0` is **no service**, never a zero-second headway.
- Uses direction grouping by source `direction_id`; if absent, falls back to `trip_headsign`, explicitly a provisional assumption. Multiple patterns within a direction are interleaved with **equal provisional allocation**, so a single legal headway does not multiply across variants. Those groups are listed in the report for review.
- Route 28 has the historical 16:00–18:00 peak exception; **18:00–19:30 on workdays and Saturdays is deliberately unmodeled** rather than being invented. The Sunday service remains full legal span.
- Normalizes template stop times to offsets from the first source arrival; does not invent travel times. Removes `shape_dist_traveled` from `stop_times.txt` because the source shapes do not consistently provide matching distances; retains the source shapes unchanged.
- Omits stale `feed_info` validity metadata. The generator produces `ibague_generator_report.json` containing all unresolved assumptions and excluded templates.

## Run locally

Install Python 3.11+ and a supported version of the official holiday library:

```bash
python -m pip install 'holidays>=0.50,<1.0'
python -m unittest discover -s tests -p 'test_build_gtfs.py' -v
python scripts/validate_official_frequencies.py
python scripts/build_gtfs.py --download --start-date 20261120 --days 90 \
  --output build/ibague-research-preview.zip \
  --report build/ibague_generator_report.json
```

The source ZIP may instead be supplied locally via `--zip path/to/gtfs_ibague.zip`, **only if its SHA-256 exactly matches the pinned source**. The recently supplied, alternative `gtfs-ibague.zip` is a *supplementary stop-name source*, **not** a replacement upstream ZIP.

Optional manual stop name corrections (none committed/approved yet):

```csv
stop_id,stop_name,source_url,approved
123,Example verified stop name,https://official.example/source,yes
```

```bash
python scripts/build_gtfs.py --download --start-date 20261120 \
  --approved-stop-overrides path/to/verified_stops.csv
```

## CI and release gate

`.github/workflows/build-preview.yml` runs unit tests, validates the legal headway register, generates the preview on a GitHub runner, and executes MobilityData GTFS Validator v8.0.1. It uploads **only QA reports**, not the source-derived ZIP, because the pinned upstream repository carries no explicit reuse/redistribution license. The generated ZIP lives temporarily on the runner and is not published in a release.

**Release blockers** (remain explicit even if the GTFS validator reports zero errors):

1. Explicit redistribution rights/permission for the upstream archive and transformed data.
2. Confirm time-of-day cutovers HP/HV/NOC or publicly label a provisional interpretation.
3. Verify post-19 October 2026 routes 1, 2, 7, 8, 9, 15, 19, 21, 28, 29, 37, 40, 48 and 50; confirm stop sequences and route branches.
4. Decide route 4/7 versus independently advertised 4 and 7; determine route 39 and four feeder routes.
5. Resolve route 28 evening and routes 35/48 branch dispatch allocation; independently review direction/variant interleaving.
6. Manually vet any of the 78 placeholder stop-name fixes before applying them.

Do not infer timetable correctness from a successful build or validator run.
