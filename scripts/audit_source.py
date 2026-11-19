#!/usr/bin/env python3
"""Audit the pinned Universidad de Ibagué GTFS without modifying it."""
import argparse
import collections
import csv
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

UPSTREAM_COMMIT = "55be037eaeaa7031eb095af53929e4ef2caaba9a"
SOURCE_URL = f"https://raw.githubusercontent.com/omtu-unibague/gtfs-ibague/{UPSTREAM_COMMIT}/gtfs_ibague.zip"
EXPECTED_SHA256 = "7cf772c89dec4ac1a0f97e709c9db519ad8d146caaf2121fe624c149ed29c050"
REQUIRED = ("agency.txt", "routes.txt", "trips.txt", "stops.txt", "stop_times.txt", "shapes.txt", "calendar.txt", "frequencies.txt")

def read_table(archive, filename):
    if filename not in archive.namelist():
        return []
    with archive.open(filename) as stream:
        reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
        return list(reader)

def audit(payload):
    sha256 = hashlib.sha256(payload).hexdigest()
    if sha256 != EXPECTED_SHA256:
        raise ValueError(f"Source SHA-256 mismatch: {sha256} != {EXPECTED_SHA256}")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        files = sorted(archive.namelist())
        missing_files = sorted(set(REQUIRED) - set(files))
        if missing_files:
            raise ValueError(f"Required GTFS files missing: {missing_files}")
        tables = {filename: read_table(archive, filename) for filename in files if filename.endswith(".txt")}

    routes = tables["routes.txt"]
    trips = tables["trips.txt"]
    stops = tables["stops.txt"]
    stop_times = tables["stop_times.txt"]
    shapes = tables["shapes.txt"]
    frequencies = tables["frequencies.txt"]
    route_ids = {row["route_id"] for row in routes}
    trip_ids = {row["trip_id"] for row in trips}
    stop_ids = {row["stop_id"] for row in stops}
    shape_ids = {row["shape_id"] for row in shapes}
    service_ids = {row["service_id"] for row in tables["calendar.txt"]}
    service_ids |= {row["service_id"] for row in tables.get("calendar_dates.txt", [])}
    frequencies_by_trip = collections.Counter(row["trip_id"] for row in frequencies)
    trips_by_route = collections.defaultdict(list)
    for row in trips:
        trips_by_route[row["route_id"]].append(row["trip_id"])
    gaps = []
    for route in routes:
        tids = trips_by_route[route["route_id"]]
        missing = [tid for tid in tids if not frequencies_by_trip[tid]]
        if missing:
            gaps.append({"route_id": route["route_id"], "short_name": route["route_short_name"], "missing_trip_ids": missing})

    unknown_refs = {
        "trips_missing_route": sorted({row["route_id"] for row in trips} - route_ids),
        "trips_missing_service": sorted({row["service_id"] for row in trips} - service_ids),
        "trips_missing_shape": sorted({row["shape_id"] for row in trips} - shape_ids),
        "stop_times_missing_trip": sorted({row["trip_id"] for row in stop_times} - trip_ids),
        "stop_times_missing_stop": sorted({row["stop_id"] for row in stop_times} - stop_ids),
        "frequencies_missing_trip": sorted({row["trip_id"] for row in frequencies} - trip_ids)
    }
    return {
        "upstream_url": SOURCE_URL,
        "upstream_sha256": sha256,
        "counts": {k: len(v) for k, v in sorted(tables.items())},
        "distinct_shape_ids": len(shape_ids),
        "routes_missing_frequencies": gaps,
        "trips_missing_frequencies": sum(len(v["missing_trip_ids"]) for v in gaps),
        "unreferenced_stops": len(stop_ids - {row["stop_id"] for row in stop_times}),
        "placeholder_stop_names": sum("Marcador De Local Sem Titulo" in row["stop_name"] for row in stops),
        "calendar": tables["calendar.txt"],
        "feed_info": tables.get("feed_info.txt", []),
        "unknown_references": unknown_refs
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--zip", type=Path, help="Path to upstream GTFS ZIP")
    source.add_argument("--download", action="store_true", help="Fetch pinned upstream GTFS ZIP")
    parser.add_argument("--output", type=Path, default=Path("build/audit.json"))
    args = parser.parse_args()
    if args.download:
        request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "ColombiaTransit-GTFS-Audit/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read()
    else:
        payload = args.zip.read_bytes()
    report = audit(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Source audit saved to {args.output}")
    print(f"Routes: {report['counts'].get('routes.txt')} | trips: {report['counts'].get('trips.txt')} | missing frequency trips: {report['trips_missing_frequencies']}")
    if any(report["unknown_references"].values()):
        print("ERROR: Found broken GTFS references", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
