#!/usr/bin/env python3
"""OSM/GraphHopper road candidates for the 14 changed Ibagué routes.

Research only: stop-first routing is NOT proof of an October 2026 route.
Never changes GTFS production files or implicitly approves road geometry.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/omtu-unibague/gtfs-ibague/55be037eaeaa7031eb095af53929e4ef2caaba9a/gtfs_ibague.zip"
SOURCE_SHA = "7cf772c89dec4ac1a0f97e709c9db519ad8d146caaf2121fe624c149ed29c050"
ROUTES = ("1", "2", "7", "8", "9", "15", "19", "21", "28", "29", "37", "40", "48", "50")
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/143.0.0.0 Safari/537.36",
           "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.9",
           "Cache-Control": "no-cache"}


def csv_in(raw: bytes):
    return list(csv.DictReader(io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8-sig", newline="")))


def source_tables(payload: bytes):
    actual = hashlib.sha256(payload).hexdigest()
    if actual != SOURCE_SHA:
        raise ValueError("Pinned original GTFS checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names = {Path(n).name: n for n in z.namelist() if n.endswith(".txt")}
        required = {"routes.txt", "trips.txt", "stops.txt", "stop_times.txt", "shapes.txt"}
        if required - set(names):
            raise ValueError("Pinned original GTFS missing required files")
        return {name: csv_in(z.read(names[name])) for name in required}


def label(name):
    return re.sub(r"^RUTA\s+", "", name.strip(), flags=re.IGNORECASE).strip()


def selected_labels(arg):
    names = list(ROUTES) if arg.lower() == "all" else [x.strip() for x in arg.split(",") if x.strip()]
    if not names or len(names) != len(set(names)) or set(names) - set(ROUTES):
        raise ValueError("Only the 14 October 2026 route labels can be selected")
    return set(names)


def valid_xy(point):
    if not isinstance(point, (list, tuple)) or len(point) < 2:
        return False
    try:
        lon, lat = float(point[0]), float(point[1])
    except (ValueError, TypeError):
        return False
    return math.isfinite(lon) and math.isfinite(lat) and -75.8 < lon < -74.75 and 3.75 < lat < 4.75


def meters(a, b):
    lon1, lat1 = map(math.radians, a[:2])
    lon2, lat2 = map(math.radians, b[:2])
    dv, du = lon2 - lon1, lat2 - lat1
    h = math.sin(du/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dv/2)**2
    return 12742000 * math.asin(min(1, math.sqrt(h)))


def manifest(tables, names, max_patterns=None):
    routes = {r["route_id"]: ("7" if label(r["route_short_name"]) == "4/7" else label(r["route_short_name"]))
              for r in tables["routes.txt"]}
    source_trips = sorted((t for t in tables["trips.txt"] if routes[t["route_id"]] in names),
                          key=lambda t: (int(routes[t["route_id"]].split("/")[0]) if routes[t["route_id"]].split("/")[0].isdigit() else 999, t["trip_id"]))
    if max_patterns is not None:
        source_trips = source_trips[:max_patterns]
    by_trip = collections.defaultdict(list)
    for t in tables["stop_times.txt"]:
        by_trip[t["trip_id"]].append(t)
    stops = {s["stop_id"]: s for s in tables["stops.txt"]}
    selected = []
    for trip in source_trips:
        visits = sorted(by_trip[trip["trip_id"]], key=lambda x: int(x["stop_sequence"]))
        points = []
        for v in visits:
            stop = stops.get(v["stop_id"])
            if stop is None:
                raise ValueError("Source trip references unknown stop")
            xy = [float(stop["stop_lon"]), float(stop["stop_lat"])]
            if not valid_xy(xy):
                raise ValueError("Stop coordinates outside Ibagué research boundary")
            points.append({"stop_id": v["stop_id"], "stop_name": stop["stop_name"],
                           "stop_sequence": int(v["stop_sequence"]), "point_lon_lat": xy})
        if len(points) < 2:
            raise ValueError("Trip pattern lacks two stops")
        selected.append({"route": routes[trip["route_id"]], "route_id": trip["route_id"],
                         "source_trip_id": trip["trip_id"], "source_shape_id": trip["shape_id"],
                         "source_direction_id": trip.get("direction_id", ""),
                         "source_headsign": trip.get("trip_headsign", ""),
                         "stop_visits": points,
                         "reviewed_official_vias": [],
                         "official_map_reviewed": False,
                         "status": "STOP_ONLY_RESEARCH_INPUT_NOT_OFFICIAL_ITINERARY"})
    if not selected:
        raise ValueError("None of the selected routes occur in pinned source")
    return {"project": "Ibagué post-2026-10-19 changed routes", "source_sha256": SOURCE_SHA,
            "osm_router": "self-hosted GraphHopper bus", "publication_ready": False,
            "notice": "Stop-only routing may omit legally required detours; insert verified map vias per direction",
            "patterns": selected}


def insert_reviewed_vias(pattern):
    """Insert only documented approved via points after named stop sequences."""
    vias = collections.defaultdict(list)
    sequences = {x["stop_sequence"] for x in pattern["stop_visits"]}
    for row in pattern.get("reviewed_official_vias", []):
        position = int(row["after_stop_sequence"])
        point = row["point_lon_lat"]
        if (position not in sequences or not valid_xy(point) or
            row.get("approved") is not True or not str(row.get("official_source_url", "")).startswith("https://")):
            raise ValueError("Via point not approved or missing official source reference")
        vias[position].append([float(point[0]), float(point[1])])
    points = []
    for stop in pattern["stop_visits"]:
        points.append(stop["point_lon_lat"])
        points.extend(vias[stop["stop_sequence"]])
    dedup = []
    for point in points:
        if not dedup or meters(point, dedup[-1]) > 2.0:
            dedup.append(point)
    if len(dedup) < 2:
        raise ValueError("Fewer than two distinct consecutive routing points")
    return dedup


def normalize_endpoint(url):
    u = urllib.parse.urlsplit(url)
    if u.scheme not in ("https", "http") or not u.netloc or u.username or u.password:
        raise ValueError("Invalid GRAPHHOPPER_URL")
    base = u.path.rstrip("/")
    if base.endswith("/route") or base.endswith("/info"):
        base = base.rsplit("/", 1)[0]
    return urllib.parse.urlunsplit((u.scheme, u.netloc, base, "", ""))


class GraphHopper:
    def __init__(self, url, profile="bus", timeout=50):
        self.url = normalize_endpoint(url)
        self.profile = profile
        self.timeout = timeout
        self.headers = dict(HEADERS)
        cid = os.getenv("CF_ACCESS_CLIENT_ID")
        csecret = os.getenv("CF_ACCESS_CLIENT_SECRET")
        if bool(cid) != bool(csecret):
            raise ValueError("Both Cloudflare Access credentials must be present together")
        if cid and csecret:
            self.headers.update({"CF-Access-Client-Id": cid, "CF-Access-Client-Secret": csecret})

    def request(self, path, payload=None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = self.headers | ({"Content-Type": "application/json"} if body else {})
        request = urllib.request.Request(self.url + path, data=body, headers=headers,
                                         method="POST" if body else "GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as res:
                result = json.load(res)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"GraphHopper HTTP {exc.code}; private endpoint hidden") from None
        except (urllib.error.URLError, TimeoutError, ValueError):
            raise RuntimeError("GraphHopper request failed or returned non-JSON; private endpoint hidden") from None
        if not isinstance(result, dict):
            raise RuntimeError("Unexpected GraphHopper JSON payload")
        return result

    def check_bus_profile(self):
        details = self.request("/info")
        active = {p.get("name") for p in details.get("profiles", []) if isinstance(p, dict)}
        if self.profile not in active:
            raise RuntimeError("GraphHopper does not advertise requested routing profile")
        return {"profile": self.profile, "osm_data_date": details.get("data_date", "unknown")}

    def route(self, points):
        reply = self.request("/route", {"profile": self.profile, "points": points,
                                         "points_encoded": False, "instructions": False,
                                         "calc_points": True})
        paths = reply.get("paths")
        if not isinstance(paths, list) or not paths:
            raise RuntimeError("GraphHopper returned no paths")
        best = paths[0]
        geom = best.get("points", {})
        coords = geom.get("coordinates", []) if isinstance(geom, dict) else []
        if len(coords) < 2 or not all(valid_xy(v) for v in coords):
            raise RuntimeError("GraphHopper returned unusable geometry")
        return {"coordinates": [[float(a), float(b)] for a, b, *rest in coords],
                "distance_m": float(best.get("distance", 0))}


def snapped_distance(point, line):
    """Approximate perpendicular distance in meters on a small Ibagué-area WGS84 line."""
    lat_ref = math.radians(point[1])
    sx = 111195 * math.cos(lat_ref)
    sy = 111195
    px, py = point[0] * sx, point[1] * sy
    smallest = float("inf")
    for a, b in zip(line, line[1:]):
        ax, ay = a[0] * sx, a[1] * sy
        bx, by = b[0] * sx, b[1] * sy
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((px - ax)*dx + (py - ay)*dy)/(dx*dx + dy*dy))) if dx*dx + dy*dy > 0 else 0
        smallest = min(smallest, math.hypot(px - (ax + t*dx), py - (ay + t*dy)))
    return smallest


def route_pattern(pattern, gh, chunk_size=12):
    points = insert_reviewed_vias(pattern)
    geom = []
    queries = 0
    total_m = 0.0
    for begin in range(0, len(points)-1, chunk_size-1):
        chunk = points[begin:begin+chunk_size]
        if len(chunk) < 2:
            continue
        result = gh.route(chunk)
        candidate = result["coordinates"]
        if geom and meters(geom[-1], candidate[0]) > 100:
            raise RuntimeError("GraphHopper route chunks have a >100m geometry discontinuity")
        geom.extend(candidate[1:] if geom and meters(geom[-1], candidate[0]) < 10 else candidate)
        queries += 1
        total_m += result["distance_m"]
    if len(geom) < 2 or not all(valid_xy(v) for v in geom):
        raise RuntimeError("No usable GraphHopper road candidate")
    distances = [snapped_distance(row["point_lon_lat"], geom) for row in pattern["stop_visits"]]
    return {"geometry": geom, "distance_m": round(total_m, 1), "queries": queries,
            "stop_count": len(distances), "stops_over_50m": sum(d > 50 for d in distances),
            "stops_over_100m": sum(d > 100 for d in distances),
            "max_stop_distance_m": round(max(distances), 1),
            "review_status": "ROAD_CANDIDATE_ONLY_OFFICIAL_ITINERARY_UNVERIFIED"}


def create_outputs(data, gh, output, max_patterns=None):
    output.mkdir(parents=True, exist_ok=True)
    meta = gh.check_bus_profile()
    features, reports, gtfs_lines = [], [], []
    for idx, pat in enumerate(data["patterns"]):
        if max_patterns is not None and idx >= max_patterns:
            break
        key = pat["source_trip_id"]
        try:
            r = route_pattern(pat, gh)
            status = r.pop("review_status")
            coords = r.pop("geometry")
            shape_id = "GH_REVIEW_" + re.sub(r"[^A-Za-z0-9_]", "_", key)
            feature = {"type": "Feature", "properties": {"route": pat["route"],
                    "source_trip_id": key, "candidate_shape_id": shape_id,
                    "status": status, "official_map_reviewed": bool(pat["official_map_reviewed"]),
                    "reviewed_vias": len(pat.get("reviewed_official_vias", []))},
                    "geometry": {"type": "LineString", "coordinates": coords}}
            features.append(feature)
            for n, (lon, lat) in enumerate(coords, 1):
                gtfs_lines.append({"shape_id": shape_id, "shape_pt_lat": lat,
                                   "shape_pt_lon": lon, "shape_pt_sequence": n})
            reports.append({"route": pat["route"], "source_trip_id": key,
                            "source_shape_id": pat["source_shape_id"], "candidate_shape_id": shape_id,
                            "status": status, **r})
        except RuntimeError as exc:
            # Mask GraphHopper URLs/credentials; do not hide data-quality failures.
            reports.append({"route": pat["route"], "source_trip_id": key,
                            "status": "ROUTING_FAILED", "failure": str(exc)})
    geo = {"type": "FeatureCollection", "metadata": {**meta,
           "published": False, "official_itinerary_verified": False,
           "shape_id_replacements_committed": 0, "source_sha256": SOURCE_SHA,
           "osm_routing_note": "GraphHopper routing follows its imported OSM road graph, not legal route geometry"},
           "features": features}
    (output/"candidate_road_shapes_RESEARCH_ONLY.geojson").write_text(json.dumps(geo, ensure_ascii=False) + "\n", encoding="utf-8")
    (output/"pattern_route_qa.json").write_text(json.dumps(reports, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (output/"candidate_shapes_NOT_GTFS.txt").open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=("shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"))
        writer.writeheader()
        writer.writerows(gtfs_lines)
    summary = {"selected_source_patterns": len(reports), "successful_graphhopper_candidates": len(features),
               "failed_patterns": sum(r["status"] == "ROUTING_FAILED" for r in reports),
               "requires_official_map_review": True, "input_source_sha256": SOURCE_SHA,
               "source_gtfs_unchanged": True, "generator_unchanged": True}
    (output/"summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if not features:
        raise RuntimeError("GraphHopper returned zero usable road candidates")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--download", action="store_true")
    src.add_argument("--zip", type=Path)
    parser.add_argument("--routes", default="8,37,50", help="Comma-separated official labels, or all")
    parser.add_argument("--max-patterns", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path("build/ibague-graphhopper"))
    parser.add_argument("--manifest", type=Path, help="Manually edited manifest with evidenced official waypoints")
    parser.add_argument("--route", action="store_true", help="Route stop-based preview; never promotes to final GTFS")
    args = parser.parse_args()
    if not 1 <= args.max_patterns <= 30:
        raise ValueError("max-patterns must be between 1 and 30")
    if args.download:
        req = urllib.request.Request(SOURCE_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=90) as res:
            payload = res.read()
    else:
        payload = args.zip.read_bytes()
    tables = source_tables(payload)
    expected = selected_labels(args.routes)
    if args.manifest:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        if data.get("source_sha256") != SOURCE_SHA or any(p["route"] not in expected for p in data["patterns"]):
            raise ValueError("Invalid reviewed manifest provenance or selected routes")
        original = manifest(tables, expected)
        known = {(p["route"], p["source_trip_id"]) for p in original["patterns"]}
        if any((p["route"], p["source_trip_id"]) not in known for p in data["patterns"]):
            raise ValueError("Unrecognized source pattern in reviewed manifest")
        # Prevent changing original stop order and position inside a reviewed manifest.
        bykey = {(p["route"], p["source_trip_id"]): p for p in original["patterns"]}
        for p in data["patterns"]:
            if p["stop_visits"] != bykey[(p["route"], p["source_trip_id"])]["stop_visits"]:
                raise ValueError("Original source stop positions/order altered in reviewed manifest")
    else:
        data = manifest(tables, expected, args.max_patterns)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/"route_waypoint_review_manifest.json").write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(f"Prepared {len(data['patterns'])} ordered source trip patterns for official map waypoint review")
    if args.route:
        url = os.getenv("GRAPHHOPPER_URL", "")
        if not url:
            raise RuntimeError("GRAPHHOPPER_URL organization variable is required")
        outcome = create_outputs(data, GraphHopper(url, profile=os.getenv("GRAPHHOPPER_PROFILE", "bus")),
                                 args.output, args.max_patterns)
        print(json.dumps(outcome, indent=2))
    else:
        print("No GraphHopper request made; research manifest prepared for review")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
