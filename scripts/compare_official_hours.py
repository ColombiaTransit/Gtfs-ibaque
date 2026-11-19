#!/usr/bin/env python3
"""Compare official advertised route service spans with upstream GTFS frequency rows.

IMPORTANT: A route-wide poster span is not necessarily a first/last departure from
a specific terminus. Discrepancies are research flags, NEVER automated fixes.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

UPSTREAM_REV = "55be037eaeaa7031eb095af53929e4ef2caaba9a"
URL = f"https://raw.githubusercontent.com/omtu-unibague/gtfs-ibague/{UPSTREAM_REV}/gtfs_ibague.zip"
SHA256 = "7cf772c89dec4ac1a0f97e709c9db519ad8d146caaf2121fe624c149ed29c050"

def minutes(time):
    hh, mm, *_ = [int(x) for x in time.split(":")]
    return hh * 60 + mm

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--zip", type=Path)
    source.add_argument("--download", action="store_true")
    parser.add_argument("--official-hours", type=Path, default=Path("research/official_service_hours.csv"))
    parser.add_argument("--output", type=Path, default=Path("build/official_hours_comparison.json"))
    args = parser.parse_args()

    if args.download:
        request = urllib.request.Request(URL, headers={"User-Agent": "ColombiaTransit-ibague-audit/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
    else:
        data = args.zip.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != SHA256:
        raise ValueError(f"Upstream checksum mismatch {sha}")

    with zipfile.ZipFile(io.BytesIO(data)) as z:
        def rows(name):
            return list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig")))
        routes, trips, freq = rows("routes.txt"), rows("trips.txt"), rows("frequencies.txt")

    official = {r["route"]: r for r in csv.DictReader(args.official_hours.open(encoding="utf-8-sig", newline=""))}
    route_names = {r["route_id"]: r["route_short_name"].removeprefix("RUTA ").strip() for r in routes}
    # The old combined route 4/7 is represented by the newer officially posted route 7.
    by_trip = {t["trip_id"]: t for t in trips}
    by_route = collections.defaultdict(list)
    for f in freq:
        trip = by_trip[f["trip_id"]]
        n = route_names[trip["route_id"]]
        n = "7" if n == "4/7" else n
        by_route[n].append(f)

    records = []
    warnings = []
    present = set()
    for route in routes:
        upstream_name = route_names[route["route_id"]]
        n = "7" if upstream_name == "4/7" else upstream_name
        present.add(n)
        poster = official.get(n)
        if poster is None:
            raise ValueError(f"Missing official route poster entry for route {upstream_name}")
        route_freq = by_route.get(n, [])
        if route_freq:
            minstart = min(minutes(row["start_time"]) for row in route_freq)
            maxend = max(minutes(row["end_time"]) for row in route_freq)
        else:
            minstart = maxend = None
        official_start = minutes(poster["mon_sat_start"])
        official_end = minutes(poster["mon_sat_end"])
        flags = []
        if not route_freq:
            flags.append("frequency_missing")
        else:
            if minstart < official_start:
                flags.append("gtfs_frequency_begins_before_official_route_window")
            if maxend > official_end:
                flags.append("gtfs_frequency_ends_after_official_route_window")
            if minstart > official_start:
                flags.append("gtfs_first_frequency_later_than_official_start")
            if maxend < official_end:
                flags.append("gtfs_last_frequency_earlier_than_official_end")
        if poster["sunday_holiday_end"] == "":
            flags.append("official_sunday_end_unverified")
        record = {
            "upstream_route_name": upstream_name,
            "official_route_name": n,
            "official_poster_url": poster["official_poster_url"],
            "official_mon_sat": [poster["mon_sat_start"], poster["mon_sat_end"]],
            "official_sunday_holiday": [poster["sunday_holiday_start"], poster["sunday_holiday_end"]],
            "frequency_row_count": len(route_freq),
            "earliest_frequency_start": f"{minstart // 60:02d}:{minstart % 60:02d}" if minstart is not None else None,
            "latest_frequency_end": f"{maxend // 60:02d}:{maxend % 60:02d}" if maxend is not None else None,
            "flags": flags
        }
        records.append(record)
        if any(f in flags for f in ("gtfs_frequency_begins_before_official_route_window", "gtfs_frequency_ends_after_official_route_window")):
            warnings.append({"route": n, "flags": flags})

    official_extra = sorted(set(official) - present, key=int)
    result = {
        "source_archive_sha256": sha,
        "official_poster_count_regular_routes": len(official),
        "original_gtfs_route_count": len(routes),
        "official_extra_routes_not_in_upstream": official_extra,
        "officially_published_feeder_routes_are_tracked_separately": True,
        "routes_missing_frequencies": sum(not bool(by_route.get("7" if name == "4/7" else name)) for name in route_names.values()),
        "routes_with_gtfs_frequency_outside_official_advertised_span": warnings,
        "records": records,
        "important_note": "Route-wide published hours are not equivalent to each direction's first and last trip; flags require investigation and must not trigger automatic GTFS edits."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Official regular routes: {len(official)} | GTFS: {len(routes)} | extra: {official_extra}")
    print(f"Missing frequency routes: {result['routes_missing_frequencies']}")
    print(f"Outside advertised span: {', '.join(r['route'] for r in warnings)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
