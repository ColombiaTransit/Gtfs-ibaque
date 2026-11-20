#!/usr/bin/env python3
"""Non-destructive audit of ambiguous Ibagué GTFS trip patterns.

No corrections are invented. No generated/public trips, shapes or stops change.
The report is compact metadata derived from the SHA256-pinned source.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import io
import itertools
import json
import math
import re
import urllib.request
from pathlib import Path

from route_changed_shapes_graphhopper import (SOURCE_SHA, SOURCE_URL, HEADERS,
                                               label, source_tables)

TARGET = ("8", "28", "35", "48", "4/7", "29")


def shared_order(a: list[str], b: list[str]) -> dict:
    """Compare exact stop IDs, not near-road estimates or name similarities."""
    ai = {v: i for i, v in enumerate(a)}
    bi = {v: i for i, v in enumerate(b)}
    common = [v for v in a if v in bi]
    order = [bi[x] for x in common]
    # O(n log n) inversion count; enough for small GTFS source but explicit.
    inversions = sum(order[i] > order[j] for i in range(len(order)) for j in range(i + 1, len(order)))
    return {"shared_stop_ids": len(set(common)), "shared_in_identical_order": inversions == 0,
            "inversions": inversions, "fraction_of_shorter": round(len(set(common)) / min(len(a), len(b)), 4),
            "fraction_of_longer": round(len(set(common)) / max(len(a), len(b)), 4)}


def route_family_pairs(patterns: list[dict], pairwise: list[dict]) -> list[dict]:
    """Find suggestive overlap families; never certify active variant operations."""
    if len(patterns) != 4:
        return []
    idx = {p["source_trip_id"]: p for p in patterns}
    scores = {frozenset((r["a"], r["b"])): r for r in pairwise}
    ids = sorted(idx)
    matchings = [((ids[0], ids[1]), (ids[2], ids[3])),
                 ((ids[0], ids[2]), (ids[1], ids[3])),
                 ((ids[0], ids[3]), (ids[1], ids[2]))]
    candidates = []
    for pairs in matchings:
        current = [scores[frozenset(pair)] for pair in pairs]
        candidates.append((sum(x["shared_stop_ids"] for x in current), pairs, current))
    score, pairs, rows = max(candidates, key=lambda x: x[0])
    if any(r["fraction_of_shorter"] < 0.60 or not r["shared_in_identical_order"] for r in rows):
        return []
    return [{"pattern_ids": sorted(pair), "shared_stop_ids": r["shared_stop_ids"],
             "fraction_of_shorter": r["fraction_of_shorter"],
             "original_direction_ids": {x: idx[x]["direction_id"] for x in pair},
             "direction_id_mismatch": len({idx[x]["direction_id"] for x in pair}) != 1,
             "classification": "SOURCE_STOP_OVERLAP_FAMILY_NOT_CONFIRMED_VARIANT"}
            for pair, r in zip(pairs, rows)]


def audited(source: dict) -> dict:
    route_label = {r["route_id"]: label(r["route_short_name"]) for r in source["routes.txt"]}
    missing = set(TARGET) - set(route_label.values())
    if missing:
        raise ValueError(f"Missing expected upstream routes {sorted(missing)}")
    trips = collections.defaultdict(list)
    for t in source["trips.txt"]:
        route = route_label.get(t["route_id"])
        if route in TARGET:
            trips[route].append(t)
    visits = collections.defaultdict(list)
    for r in source["stop_times.txt"]:
        visits[r["trip_id"]].append(r)
    stops = {s["stop_id"]: s for s in source["stops.txt"]}
    reports = {}
    for rt in TARGET:
        ps, comparisons = [], []
        for t in sorted(trips[rt], key=lambda x: x["trip_id"]):
            vv = sorted(visits[t["trip_id"]], key=lambda x: int(x["stop_sequence"]))
            if not vv:
                raise ValueError("Source trip with no stops: " + t["trip_id"])
            ss = [v["stop_id"] for v in vv]
            other = []
            for v in vv:
                name = stops[v["stop_id"]]["stop_name"]
                for m in re.finditer(r"\bruta\s+(\d+)\b", name, re.IGNORECASE):
                    if m.group(1) not in (rt,):
                        other.append({"stop_id": v["stop_id"], "stop_name": name,
                                      "mentions_route": m.group(1)})
            ps.append({"source_trip_id": t["trip_id"], "source_route_id": t["route_id"],
                       "source_shape_id": t["shape_id"], "direction_id": t.get("direction_id", ""),
                       "stop_count": len(ss), "unique_stop_ids": len(set(ss)),
                       "first_stop_id": ss[0], "first_stop_name": stops[ss[0]]["stop_name"],
                       "last_stop_id": ss[-1], "last_stop_name": stops[ss[-1]]["stop_name"],
                       "foreign_route_terminal_names": other,
                       "_ids": ss})
        for a, b in itertools.combinations(ps, 2):
            c = shared_order(a["_ids"], b["_ids"])
            comparisons.append({"a": a["source_trip_id"], "b": b["source_trip_id"], **c})
        families = route_family_pairs(ps, comparisons) if rt == "8" else []
        mismatches = [x for x in families if x["direction_id_mismatch"]]
        for p in ps: p.pop("_ids")
        reports[rt] = {"source_patterns": len(ps), "patterns": ps,
                       "pairwise_exact_stop_overlap": comparisons,
                       "candidate_stop_families": families,
                       "original_direction_metadata_conflicts": len(mismatches),
                       "source_variants_verified": False,
                       "separate_branch_stop_sequence_verified": False}
        if rt == "8":
            reports[rt]["risk"] = "UNVERIFIED_THREE_WAY_EQUAL_SPLIT_DIRECTION_1"
        elif rt == "35":
            reports[rt]["risk"] = "CAY_ONE_IN_THREE_BRANCH_NOT_IDENTIFIED_IN_SOURCE_TRIPS"
        elif rt == "48":
            reports[rt]["risk"] = "JUNTAS_CONDITIONAL_BRANCH_NOT_IDENTIFIED_IN_SOURCE_TRIPS"
        elif rt == "28":
            reports[rt]["risk"] = "CAIKE_WEEKEND_ADDITIONAL_DEPARTURES_NOT_EXPLICIT"
        elif rt == "4/7":
            reports[rt]["risk"] = "COMBINED_ROUTE_NOT_RECONCILED_WITH_SEPARATE_4_AND_7"
        else:
            reports[rt]["risk"] = "TERMINAL_RELOCATION_NEEDS_DIRECTION_CHECK"
    return {"source_sha256": SOURCE_SHA,
            "scope": "SOURCE_PATTERN_AUDIT_ONLY_NO_OPERATIONAL_VARIANTS_APPROVED",
            "route_8_three_way_split_confirmed": False,
            "trips_changed": 0, "shapes_changed": 0, "stop_times_changed": 0,
            "route_analysis": reports}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    io_group = p.add_mutually_exclusive_group(required=True)
    io_group.add_argument("--download", action="store_true")
    io_group.add_argument("--zip", type=Path)
    p.add_argument("--output", type=Path, default=Path("build/ibague-variant-audit/source_variant_report.json"))
    args = p.parse_args()
    if args.download:
        with urllib.request.urlopen(urllib.request.Request(SOURCE_URL, headers=HEADERS), timeout=90) as r:
            payload = r.read()
    else:
        payload = args.zip.read_bytes()
    report = audited(source_tables(payload))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for route, row in report["route_analysis"].items():
        print(f"Route {route}: {row['source_patterns']} patterns; direction-mismatched stop families={row['original_direction_metadata_conflicts']}; {row['risk']}")
    print("Research report:", args.output)


if __name__ == "__main__":
    main()
