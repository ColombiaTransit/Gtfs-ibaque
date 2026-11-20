#!/usr/bin/env python3
"""Route 48 Juntas: compare existing GraphHopper research shapes, not a GTFS build.

Input geometries are the two prior *unapproved* research artifacts. Only route 48
is inspected. OSM refs are geographic witnesses, not authorized boarding stops.
No directions, frequencies, stop IDs or schedules are edited or inferred.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from shapely.geometry import LineString, Point
from shapely.ops import transform
from pyproj import Transformer

SOURCE_TRIPS = ("TRIP_R53", "TRIP_R54")
TO_METERS = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True).transform
# Locations are geographic references, NOT verified boarding locations.
REFERENCES = [
    ("Villa Restrepo village", -75.31086, 4.52434, "OSM_PLACE_REFERENCE_NOT_STOP"),
    ("Iguaima location", -75.31834, 4.54913, "GEOGRAPHIC_REFERENCE_NOT_STOP"),
    ("Juntas village", -75.32140, 4.55603, "OSM_PLACE_REFERENCE_NOT_STOP"),
    ("Puerto Peru bridge", -75.29410, 4.50302, "GEOGRAPHIC_REFERENCE_NOT_STOP"),
    ("Pastales village", -75.27691, 4.50935, "GEOGRAPHIC_REFERENCE_NOT_STOP"),
]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def line_of(feature):
    geom = feature.get("geometry", {})
    if geom.get("type") != "LineString" or len(geom.get("coordinates", [])) < 2:
        raise ValueError("Expected a valid line geometry")
    return transform(TO_METERS, LineString(geom["coordinates"]))


def find_route48(features, kind):
    selected = {}
    for feat in features:
        p = feat.get("properties", {})
        if p.get("route") != "48":
            continue
        trip = p.get("source_trip_id")
        if trip not in SOURCE_TRIPS or trip in selected:
            raise ValueError(f"Unexpected or duplicate route 48 {kind} pattern")
        selected[trip] = feat
    if set(selected) != set(SOURCE_TRIPS):
        raise ValueError(f"Missing expected route 48 {kind} patterns")
    return selected


def landmark_rows(segments):
    rows = []
    for trip, line in segments.items():
        for name, lon, lat, category in REFERENCES:
            point = transform(TO_METERS, Point(lon, lat))
            rows.append({"source_trip_id": trip, "reference_name": name,
                         "reference_class": category,
                         "distance_to_branch_road_m": round(line.distance(point), 1),
                         "projected_branch_distance_m": round(line.project(point), 1),
                         "osm_or_source_point_is_authorized_gtfs_stop": "no"})
    return rows


def verify_landmark_order(rows):
    lookup = {(r["source_trip_id"], r["reference_name"]): r for r in rows}
    expected = {
        "TRIP_R53": ("Villa Restrepo village", "Iguaima location", "Juntas village"),
        "TRIP_R54": ("Juntas village", "Iguaima location", "Villa Restrepo village"),
    }
    for trip, names in expected.items():
        ss = [lookup[trip, x]["projected_branch_distance_m"] for x in names]
        if not all(a < b for a, b in zip(ss, ss[1:])):
            raise ValueError(f"Incorrect ordered Juntas road corridor: {trip}")
    return expected


def sample_overlap(a, b, every_m=45, tolerance_m=55):
    # Direction-independent fraction of the shorter extension alongside the other.
    short, other = (a, b) if a.length <= b.length else (b, a)
    count = max(2, math.ceil(short.length / every_m))
    samples = [short.interpolate(short.length * i / count) for i in range(count + 1)]
    fraction = sum(other.distance(p) <= tolerance_m for p in samples) / len(samples)
    return round(fraction, 3)


def extract_osm_features(data):
    if not isinstance(data.get("elements"), list):
        raise ValueError("Invalid OSM export")
    rows=[]
    for e in data["elements"]:
        tags = e.get("tags", {})
        if not isinstance(tags, dict):
            continue
        loc = e if e.get("type") == "node" else e.get("center", {})
        lon,lat=loc.get("lon"),loc.get("lat")
        if lon is None or lat is None:
            continue
        if not(-75.5<float(lon)<-75.1 and 4.35<float(lat)<4.65):
            continue
        rows.append({"osm_id": f"{e['type']}/{e['id']}",
                     "name": tags.get("name", ""), "ref": tags.get("ref", ""),
                     "lat": float(lat), "lon": float(lon),
                     "highway":tags.get("highway", ""),
                     "public_transport":tags.get("public_transport", ""),
                     "amenity":tags.get("amenity", ""),
                     "route_48_operator_confirmed": "no"})
    return rows


def overpass_query():
    # Very small Juntas / Villa Restrepo segment; does not query citywide OSM.
    bbox="4.502,-75.341,4.563,-75.295"
    return ('[out:json][timeout:90];('
            f'node["highway"="bus_stop"]({bbox});'
            f'node["public_transport"~"^(platform|stop_position)$"]({bbox});'
            f'node["amenity"="bus_station"]({bbox});'
            f'way["public_transport"="platform"]({bbox});'
            ');out body center;')


def fetch_overpass():
    base=os.environ.get("API_OVERPASS", "").strip()
    if not base:
        return None,"not_configured"
    url=base.rstrip("/")
    if not url.endswith("/interpreter"):
        url += "/interpreter"
    parts=urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        return None,"invalid_endpoint"
    headers={"Content-Type":"application/x-www-form-urlencoded",
             "Accept":"application/json", "User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit-Route48QA/1.0)"}
    ident=os.getenv("CF_ACCESS_CLIENT_ID", "")
    secret=os.getenv("CF_ACCESS_CLIENT_SECRET", "")
    if bool(ident)!=bool(secret):
        return None,"incomplete_cloudflare_service_token"
    if ident:
        headers.update({"CF-Access-Client-Id":ident,"CF-Access-Client-Secret":secret})
    body=urllib.parse.urlencode({"data":overpass_query()}).encode()
    req=urllib.request.Request(url,method="POST",headers=headers,data=body)
    try:
        with urllib.request.urlopen(req,timeout=110) as resp:
            data=json.load(resp)
    except urllib.error.HTTPError as exc:
        return None,"HTTP_"+str(exc.code)
    except (urllib.error.URLError,TimeoutError,ValueError):
        return None,"network_or_invalid_response"
    if not isinstance(data,dict) or "remark" in data:
        return None,"overpass_error_or_remark"
    return data,"ok"


def write_csv(path,rows,fields):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def audit(base, branches, manifest, osm=None):
    old=find_route48(base.get("features",[]),"existing")
    extra=find_route48(branches.get("features",[]),"branch")
    indexed={p["source_trip_id"]:p for p in manifest.get("patterns",[]) if p.get("route")=="48"}
    if set(indexed)!=set(SOURCE_TRIPS):
        raise ValueError("Missing original route 48 stop manifest")
    oldlines={t:line_of(v) for t,v in old.items()}
    extensions={t:line_of(v) for t,v in extra.items()}
    rows=landmark_rows(extensions)
    order=verify_landmark_order(rows)
    summary=[]
    for trip in SOURCE_TRIPS:
        visits=indexed[trip]["stop_visits"]
        source_id=indexed[trip]["source_direction_id"]
        if source_id != ("0" if trip=="TRIP_R53" else "1"):
            raise ValueError("Unexpected route 48 source direction")
        extension_side="append" if trip=="TRIP_R53" else "prepend"
        srcendpoint=visits[-1] if extension_side=="append" else visits[0]
        endxy=extra[trip]["geometry"]["coordinates"][0 if extension_side=="append" else -1]
        gap=transform(TO_METERS,Point(*srcendpoint["point_lon_lat"])).distance(transform(TO_METERS,Point(*endxy)))
        # Failed endpoint alignment means we cannot even form a coherent candidate line.
        if gap>100:
            raise ValueError("GraphHopper rural extension does not join source endpoint")
        summary.append({"source_trip_id":trip,"source_direction_id":source_id,
                        "original_stop_visits":len(visits),"original_road_length_m":round(oldlines[trip].length,1),
                        "candidate_extension_length_m":round(extensions[trip].length,1),
                        "join_point_error_m":round(gap,1),"extension_relation":extension_side,
                        "source_first_stop_id":visits[0]["stop_id"],"source_last_stop_id":visits[-1]["stop_id"],
                        "source_full_end_to_end_confirmed":"no",
                        "branch_official_boarding_stop_confirmed":"no",
                        "urban_october_reroute_verified":"no", "gtfs_activated":"no"})
    osm_rows=[]
    if osm is not None:
        for p in extract_osm_features(osm):
            pt=transform(TO_METERS,Point(p["lon"],p["lat"]))
            distances=[extensions[t].distance(pt) for t in SOURCE_TRIPS]
            p.update({"nearest_branch_road_m":round(min(distances),1),
                      "on_candidate_branch_75m": "yes" if min(distances)<=75 else "no",
                      "boarding_stop_verified_by_agency":"no"})
            osm_rows.append(p)
        osm_rows.sort(key=lambda p:(p["nearest_branch_road_m"],p["osm_id"]))
    result={"status":"RESEARCH_ONLY_NOT_APPROVED",
            "source":"pinned_2026_may_gtfs_plus_prior_graphhopper_actions",
            "branch_reference_places_not_stops":True,
            "juntas_road_order_landmarks":order,
            "all_road_order_checks_passed":True,
            "shared_opposite_direction_road_fraction_55m":sample_overlap(*extensions.values()),
            "source_patterns":summary,
            "osm_query_status":"provided" if osm is not None else "unavailable",
            "osm_stop_candidates_count":len(osm_rows),
            "osm_candidate_points_within_75m":sum(p["on_candidate_branch_75m"]=="yes" for p in osm_rows),
            "agency_verified_new_boarding_stops":0,
            "official_via_waypoints_applied":0,
            "trips_txt_changed":False,"stops_txt_changed":False,"stop_times_txt_changed":False,
            "shapes_txt_changed":False,"frequencies_txt_changed":False,
            "release_ready":False}
    return rows,summary,osm_rows,result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base",type=Path,required=True)
    p.add_argument("--branch",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--osm",type=Path)
    p.add_argument("--try-overpass",action="store_true")
    p.add_argument("--out",type=Path,default=Path("build/route48-juntas"))
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    osm=None
    status="not_requested"
    if a.osm:
        osm=read_json(a.osm)
        status="local_export"
    elif a.try_overpass:
        osm,status=fetch_overpass()
    landmarks,patterns,osmrows,result=audit(read_json(a.base),read_json(a.branch),read_json(a.manifest),osm)
    result["osm_query_status"]=status
    write_csv(a.out/"landmark_road_alignment.csv",landmarks,list(landmarks[0]))
    write_csv(a.out/"source_pattern_gaps.csv",patterns,list(patterns[0]))
    fields=["osm_id","name","ref","lat","lon","highway","public_transport","amenity",
            "route_48_operator_confirmed","nearest_branch_road_m","on_candidate_branch_75m",
            "boarding_stop_verified_by_agency"]
    write_csv(a.out/"osm_stop_candidates_REVIEW_ONLY.csv",osmrows,fields)
    (a.out/"summary.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
