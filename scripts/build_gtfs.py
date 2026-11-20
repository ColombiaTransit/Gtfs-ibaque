#!/usr/bin/env python3
"""Build a RESEARCH-ONLY Ibagué GTFS preview from the pinned 2026 upstream.

Uses the verified October 2026 headways and explicitly provisional 2022 clock
bands. Never publishes, redistributes, geocodes, guesses missing trip times or
silently rewrites route geometry/stops. See research/generator_v1.md.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

SOURCE_SHA256 = "7cf772c89dec4ac1a0f97e709c9db519ad8d146caaf2121fe624c149ed29c050"
SOURCE_URL = "https://raw.githubusercontent.com/omtu-unibague/gtfs-ibague/55be037eaeaa7031eb095af53929e4ef2caaba9a/gtfs_ibague.zip"
REQUIRED = {"agency.txt", "routes.txt", "stops.txt", "shapes.txt", "trips.txt", "stop_times.txt"}
DAY_TYPES = ("WK", "SA", "SU")
PERIODS = (("04:40", "06:00", "NOC"), ("06:00", "08:30", "HP"),
           ("08:30", "11:30", "HV"), ("11:30", "14:30", "HP"),
           ("14:30", "17:00", "HV"), ("17:00", "19:30", "HP"),
           ("19:30", "22:00", "NOC"))
HEADWAY_KEYS = {
    "WK": {"HP": "weekday_peak_hp_min", "HV": "weekday_valley_hv_min", "NOC": "weekday_night_noc_min"},
    "SA": {"HP": "saturday_peak_hp_min", "HV": "saturday_valley_hv_min", "NOC": "saturday_night_noc_min"},
    "SU": {"FLAT": "sunday_holiday_min"},
}
HOURS_KEYS = {"WK": "weekday_service_hours", "SA": "saturday_service_hours", "SU": "sunday_holiday_service_hours"}
MODIFIED_ROUTES = {"1", "2", "7", "8", "9", "15", "19", "21", "28", "29", "37", "40", "48", "50"}


def read_csv_file(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_gtfs(payload: bytes) -> dict[str, list[dict[str, str]]]:
    sha = hashlib.sha256(payload).hexdigest()
    if sha != SOURCE_SHA256:
        raise ValueError(f"Pinned upstream SHA-256 mismatch: {sha}")
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names = {Path(n).name: n for n in z.namelist() if n.endswith('.txt')}
        if missing := REQUIRED - names.keys():
            raise ValueError(f"Missing source tables: {sorted(missing)}")
        output = {}
        for name, zipname in names.items():
            with z.open(zipname) as f:
                output[name] = list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")))
        return output


def hm(raw: str) -> int:
    fields = raw.split(":")
    if len(fields) not in (2, 3) or any(not f.isdigit() for f in fields):
        raise ValueError(f"Invalid time: {raw}")
    hour, minute = int(fields[0]), int(fields[1])
    sec = int(fields[2]) if len(fields) == 3 else 0
    if minute > 59 or sec > 59 or hour > 47:
        raise ValueError(f"Invalid time: {raw}")
    return hour * 3600 + minute * 60 + sec


def fmt(sec: int) -> str:
    if sec < 0:
        raise ValueError("Negative time offset")
    return f"{sec // 3600:02d}:{(sec // 60) % 60:02d}:{sec % 60:02d}"


def label(route: dict[str, str]) -> str:
    return re.sub(r"^RUTA\s+", "", route["route_short_name"].strip(), flags=re.I).strip()


def clock_segments(route: str, day: str, window: str) -> list[tuple[int, int, str]]:
    start, end = map(hm, window.split("-"))
    if start >= end:
        raise ValueError(f"Bad official service span {route}/{day}: {window}")
    if day == "SU":
        return [(start, end, "FLAT")]
    blocks = PERIODS
    if route == "28":
        # This is a documented historical peak exception; 18:00-19:30 is
        # UNRESOLVED and intentionally not generated instead of guessing.
        blocks = (("04:40", "06:00", "NOC"), ("06:00", "08:30", "HP"),
                  ("08:30", "11:30", "HV"), ("11:30", "14:30", "HP"),
                  ("14:30", "16:00", "HV"), ("16:00", "18:00", "HP"),
                  ("19:30", "22:00", "NOC"))
    return [(max(start, hm(a)), min(end, hm(b)), p) for a, b, p in blocks
            if max(start, hm(a)) < min(end, hm(b))]


def template_offsets(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], str | None]:
    """Normalize existing observed stop offsets; NEVER infer missing times."""
    rows = sorted(rows, key=lambda r: int(r["stop_sequence"]))
    if len(rows) < 2:
        return [], "fewer_than_two_stop_times"
    first = rows[0]["arrival_time"] or rows[0]["departure_time"]
    last = rows[-1]["arrival_time"] or rows[-1]["departure_time"]
    if not first or not last:
        return [], "missing_start_or_end_time"
    try:
        origin = hm(first)
        out = []
        prev = 0
        for row in rows:
            arrival = row.get("arrival_time", "")
            departure = row.get("departure_time", "")
            if not arrival or not departure:
                return [], "missing_stop_time"
            arr = hm(arrival) - origin
            dep = hm(departure) - origin
            if arr < prev or dep < arr:
                return [], "nonmonotonic_existing_stop_time"
            newrow = dict(row)
            newrow["arrival_time"] = fmt(arr)
            newrow["departure_time"] = fmt(dep)
            # The original feed has shape distance in stop_times but lacks
            # consistently matching shape_dist_traveled on shape vertices.
            newrow.pop("shape_dist_traveled", None)
            out.append(newrow)
            prev = dep
        return out, None
    except (ValueError, KeyError) as e:
        return [], f"invalid_existing_stop_time:{e}"


def service_calendar(start: dt.date, days: int, holidays: set[dt.date]) -> tuple[list[dict], list[dict]]:
    end = start + dt.timedelta(days=days - 1)
    base = []
    for day, weekly in (("WK", [1, 1, 1, 1, 1, 0, 0]),
                        ("SA", [0, 0, 0, 0, 0, 1, 0]),
                        ("SU", [0, 0, 0, 0, 0, 0, 1])):
        base.append({"service_id": f"CT_{day}",
                     **dict(zip(("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"), map(str, weekly))),
                     "start_date": start.strftime("%Y%m%d"), "end_date": end.strftime("%Y%m%d")})
    exceptions = []
    for holiday in sorted(holidays):
        if not start <= holiday <= end or holiday.weekday() == 6:
            continue
        old = "SA" if holiday.weekday() == 5 else "WK"
        exceptions.append({"service_id": f"CT_{old}", "date": holiday.strftime("%Y%m%d"), "exception_type": "2"})
        exceptions.append({"service_id": "CT_SU", "date": holiday.strftime("%Y%m%d"), "exception_type": "1"})
    return base, exceptions


def get_colombia_holidays(start: dt.date, days: int) -> set[dt.date]:
    try:
        import holidays as holidays_module  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install python-holidays: pip install 'holidays>=0.50,<1'") from exc
    end = start + dt.timedelta(days=days - 1)
    return set(holidays_module.country_holidays("CO", years=range(start.year, end.year + 1)).keys())


def approved_stop_names(stops: list[dict], overrides: Path | None) -> list[dict]:
    """Apply only explicitly approved names with cited verification provenance."""
    if overrides is None:
        return []
    by_id = {r["stop_id"]: r for r in stops}
    applied = []
    for entry in read_csv_file(overrides):
        sid, newname = entry.get("stop_id", ""), entry.get("stop_name", "").strip()
        if entry.get("approved", "").strip().lower() != "yes" or not entry.get("source_url", "").strip():
            raise ValueError(f"Unapproved/unattributed stop override for {sid}")
        if sid not in by_id or not newname:
            raise ValueError(f"Invalid stop override for {sid}")
        old = by_id[sid]["stop_name"]
        if "marcador de local" not in old.lower():
            raise ValueError(f"Override can only rename original placeholder {sid}")
        if sid in applied:
            raise ValueError(f"Duplicate stop override {sid}")
        by_id[sid]["stop_name"] = newname
        applied.append(sid)
    return applied


def csv_bytes(rows: list[dict], fields: list[str] | None = None) -> bytes:
    if not rows:
        return b""
    fields = fields or list(rows[0])
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def build(source: dict[str, list[dict]], legal: list[dict], start: dt.date, days: int,
          holidays: set[dt.date], stop_overrides: Path | None = None) -> tuple[dict[str, bytes], dict]:
    if not 1 <= days <= 366:
        raise ValueError("days must be 1..366")
    original_routes, original_trips = source["routes.txt"], source["trips.txt"]
    legal_by_label = {r["route"]: r for r in legal}
    if len(legal_by_label) != len(legal):
        raise ValueError("Duplicate legal frequency route")
    source_labels = {label(r) for r in original_routes}
    if source_labels != set(legal_by_label):
        raise ValueError(f"Source/legal route mismatch: source_only={source_labels - set(legal_by_label)}, legal_only={set(legal_by_label) - source_labels}")
    stops = [dict(s) for s in source["stops.txt"]]
    applied = approved_stop_names(stops, stop_overrides)
    base_calendar, exceptions = service_calendar(start, days, holidays)
    stop_times_by_trip: dict[str, list[dict]] = collections.defaultdict(list)
    for row in source["stop_times.txt"]:
        stop_times_by_trip[row["trip_id"]].append(row)
    by_route_dir: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for trip in original_trips:
        direction = trip.get("direction_id", "").strip()
        if not direction:
            # Using trip_headsign as a stable group is a provisional fallback,
            # not evidence of a direction_id in the source.
            direction = "headsign:" + trip.get("trip_headsign", "").strip()
        if direction == "headsign:":
            raise ValueError(f"Cannot classify trip direction {trip['trip_id']}")
        by_route_dir[(trip["route_id"], direction)].append(trip)
    routes = {r["route_id"]: r for r in original_routes}
    out_trips, out_times, out_freq = [], [], []
    excluded = []
    generated = collections.Counter()
    pattern_split = []
    uncovered = []
    for (route_id, direction), templates in sorted(by_route_dir.items()):
        route_label = label(routes[route_id])
        legal_row = legal_by_label[route_label]
        # Count ALL source patterns in a direction; dropping invalid patterns
        # must NOT increase the other variants' service frequency implicitly.
        total = len(templates)
        if total > 1:
            pattern_split.append({"route": route_label, "direction": direction,
                                  "patterns": total, "allocation": "provisional_equal_split"})
        templates.sort(key=lambda t: t["trip_id"])
        for index, template in enumerate(templates):
            original_id = template["trip_id"]
            normalized, reason = template_offsets(stop_times_by_trip.get(original_id, []))
            if reason:
                excluded.append({"route": route_label, "source_trip_id": original_id, "reason": reason})
                continue
            for day in DAY_TYPES:
                periods = clock_segments(route_label, day, legal_row[HOURS_KEYS[day]])
                generated_periods = []
                for a, b, period in periods:
                    headway_min = int(legal_row[HEADWAY_KEYS[day][period]])
                    if headway_min == 0:
                        # Legally zero night service on route 29.
                        continue
                    if headway_min < 0 or headway_min > 60:
                        raise ValueError(f"Invalid legal headway {route_label}/{day}/{period}={headway_min}")
                    # Interleave direction variants; never copy the route-wide
                    # headway to multiple variants at the same departure time.
                    interval = 60 * headway_min * total
                    segment_start = a + index * 60 * headway_min
                    if segment_start >= b:
                        continue
                    generated_periods.append({"trip_id": f"CT_{day}_{original_id}", "start_time": fmt(segment_start),
                                              "end_time": fmt(b), "headway_secs": str(interval), "exact_times": "0"})
                if not generated_periods:
                    uncovered.append({"route": route_label, "source_trip_id": original_id, "day_type": day,
                                      "reason": "no_positive_headway_period"})
                    continue
                tid = f"CT_{day}_{original_id}"
                trip = {k: v for k, v in template.items() if k not in ("service_id", "block_id", "trip_id")}
                trip.update({"trip_id": tid, "service_id": f"CT_{day}"})
                out_trips.append(trip)
                for row in normalized:
                    newrow = dict(row)
                    newrow["trip_id"] = tid
                    out_times.append(newrow)
                out_freq.extend(generated_periods)
                generated[route_label] += len(generated_periods)
    if not out_trips:
        raise ValueError("All source trip patterns were excluded")
    # Keep exact source shapes and stop identities: post-19 Oct 2026 route changes
    # are an explicit publication blocker, NOT synthesized here.
    tables = {
        "agency.txt": csv_bytes(source["agency.txt"]),
        "routes.txt": csv_bytes(original_routes),
        "stops.txt": csv_bytes(stops),
        "shapes.txt": csv_bytes(source["shapes.txt"]),
        "trips.txt": csv_bytes(out_trips),
        "stop_times.txt": csv_bytes(out_times),
        "frequencies.txt": csv_bytes(out_freq, ["trip_id", "start_time", "end_time", "headway_secs", "exact_times"]),
        "calendar.txt": csv_bytes(base_calendar),
        "calendar_dates.txt": csv_bytes(exceptions, ["service_id", "date", "exception_type"]),
        "feed_info.txt": csv_bytes([{
            "feed_publisher_name": "ColombiaTransit (unpublished research preview)",
            "feed_publisher_url": "https://github.com/ColombiaTransit/Gtfs-ibaque",
            "feed_lang": "es", "feed_start_date": start.strftime("%Y%m%d"),
            "feed_end_date": (start + dt.timedelta(days=days - 1)).strftime("%Y%m%d"),
            "feed_version": "research-preview-" + start.strftime("%Y%m%d"),
        }]),
    }
    # A well-formed, nonempty calendar_dates header even when no exceptions fall in range.
    if not exceptions:
        tables["calendar_dates.txt"] = b"service_id,date,exception_type\n"
    # Strip optional stale feed_info entries from upstream rather than preserving
    # their inaccurate claim of validity to 2030.
    report = {
        "publication_ready": False, "status": "RESEARCH_PREVIEW_ONLY", "source_sha256": SOURCE_SHA256,
        "legal_source": legal[0]["source_url"], "start_date": start.strftime("%Y%m%d"),
        "end_date": (start + dt.timedelta(days=days - 1)).strftime("%Y%m%d"),
        "source_routes": len(original_routes), "source_trip_patterns": len(original_trips),
        "output_template_trips": len(out_trips), "output_frequency_rows": len(out_freq),
        "covered_routes": len(generated), "headway_periods_by_route": dict(sorted(generated.items())),
        "source_stops": len(stops), "renamed_stops_with_approval": applied,
        "remaining_unnamed_stops": sum("marcador de local" in s["stop_name"].lower() for s in stops),
        "holiday_override_dates": len({e["date"] for e in exceptions}),
        "excluded_patterns": excluded, "uncovered_pattern_day": uncovered,
        "provisional_equal_variant_splits": pattern_split,
        "route_28_unmodeled_evening_minutes": "18:00-19:30 weekdays/Saturdays (clipped to route window)",
        "publication_blockers": [
            "No explicit reuse/redistribution license for upstream GTFS",
            "Historical 2022 HP/HV/NOC boundaries used provisionally (2024 and 2026 amendments unavailable)",
            "Unverified post-2026-10-19 geometry and stop patterns on modified routes",
            "Unresolved separate route 4/7 versus route 4 and route 7, plus route 39 and four feeders",
            "Route 28 18:00-19:30 status and routes 35/48 branch allocations unresolved",
            "Trip pattern interleaving when multiple variants in a direction is provisional",
        ],
    }
    return tables, report


def write_zip(path: Path, tables: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(tables):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, tables[name])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--zip", type=Path, help="Locally held pinned upstream ZIP")
    source.add_argument("--download", action="store_true", help="Fetch SHA-256 pinned original ZIP")
    parser.add_argument("--start-date", required=True, help="YYYYMMDD; research preview period starts here")
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--legal", type=Path, default=Path("research/official_resolution_005549_frequencies.csv"))
    parser.add_argument("--approved-stop-overrides", type=Path)
    parser.add_argument("--output", type=Path, default=Path("build/ibague-research-preview.zip"))
    parser.add_argument("--report", type=Path, default=Path("build/ibague_generator_report.json"))
    args = parser.parse_args()
    start = dt.datetime.strptime(args.start_date, "%Y%m%d").date()
    if args.download:
        req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "ColombiaTransit-Ibague-Research-Generator/1.0"})
        with urllib.request.urlopen(req, timeout=90) as response:
            payload = response.read()
    else:
        payload = args.zip.read_bytes()
    source_tables = read_gtfs(payload)
    official = read_csv_file(args.legal)
    dates = get_colombia_holidays(start, args.days)
    tables, report = build(source_tables, official, start, args.days, dates, args.approved_stop_overrides)
    write_zip(args.output, tables)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"RESEARCH ONLY: {len(tables)} GTFS tables -> {args.output}; {report['output_frequency_rows']} frequencies across {report['covered_routes']} routes")
    print(f"Report: {args.report} | publication_ready=false (license, geometry, clock assumptions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
