#!/usr/bin/env python3
"""Create read-only route-aware review tables for unnamed Ibagué GTFS stops.

Pinned upstream ZIP is fetched and SHA-256 verified. Does NOT change stop_id,
stop_times.txt or any source coordinates; nearest points are manual leads only.
"""
import argparse,collections,csv,hashlib,io,json,math,urllib.request,zipfile
from pathlib import Path

REV="55be037eaeaa7031eb095af53929e4ef2caaba9a"
URL=f"https://raw.githubusercontent.com/omtu-unibague/gtfs-ibague/{REV}/gtfs_ibague.zip"
SHA256="7cf772c89dec4ac1a0f97e709c9db519ad8d146caaf2121fe624c149ed29c050"

def meters(a,b):
    lat1,lon1,lat2,lon2=map(math.radians,[float(a["stop_lat"]),float(a["stop_lon"]),float(b["stop_lat"]),float(b["stop_lon"])])
    v=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return round(12742000*math.asin(min(1,math.sqrt(v))),1)

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--zip",type=Path)
    g.add_argument("--download",action="store_true")
    p.add_argument("--output-dir",type=Path,default=Path("build/stop_review"))
    a=p.parse_args()
    if a.download:
        request=urllib.request.Request(URL,headers={"User-Agent":"ColombiaTransit-GTFS-StopReview/1.0"})
        with urllib.request.urlopen(request,timeout=60) as r:payload=r.read()
    else:payload=a.zip.read_bytes()
    sha=hashlib.sha256(payload).hexdigest()
    if sha!=SHA256:raise RuntimeError("Upstream SHA-256 mismatch "+sha)
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        def table(name):return list(csv.DictReader(io.TextIOWrapper(z.open(name),encoding="utf-8-sig",newline="")))
        stops=table("stops.txt");times=table("stop_times.txt")
        trips=table("trips.txt");routes=table("routes.txt")
    by_trip={t["trip_id"]:t for t in trips}
    route_names={r["route_id"]:r["route_short_name"] for r in routes}
    uses=collections.defaultdict(set)
    for t in times:
        trip=by_trip[t["trip_id"]]
        uses[t["stop_id"]].add((route_names[trip["route_id"]],trip.get("direction_id","?")))
    unnamed=[s for s in stops if "marcador de local" in s["stop_name"].lower()]
    numbered=[s for s in stops if "marcador de local" not in s["stop_name"].lower() and not s["stop_name"].lower().startswith("terminal")]
    rows=[]
    for stop in unnamed:
        candidates=sorted([(meters(stop,n),n) for n in numbered],key=lambda x:x[0])
        dist,near=candidates[0]
        overlap=next(((d,n) for d,n in candidates if uses[stop["stop_id"]] & uses[n["stop_id"]]),(None,None))
        classif="potential_same_site_unverified" if dist<=30 else ("nearby_requires_review" if dist<=75 else "no_close_numbered_stop")
        rows.append({
            "source_stop_id":stop["stop_id"],"lat":stop["stop_lat"],"lon":stop["stop_lon"],
            "route_directions":";".join(sorted(f"{r}/{d}" for r,d in uses[stop["stop_id"]])),
            "closest_numbered_stop_id":near["stop_id"],"closest_numbered_name":near["stop_name"],
            "closest_distance_m":dist,
            "closest_same_route_stop_id":overlap[1]["stop_id"] if overlap[1] else "",
            "closest_same_route_stop_name":overlap[1]["stop_name"] if overlap[1] else "",
            "closest_same_route_distance_m":overlap[0] if overlap[0] is not None else "",
            "review_class":classif,"official_stop_code":"","confirmed_name":"","verification_url":"",
            "status":"awaiting_official_stop_inventory",
            "note":"DO NOT auto merge or rename; nearest stop may be across road or different platform"
        })
    pth=a.output_dir;pth.mkdir(parents=True,exist_ok=True)
    with (pth/"unnamed_stops_review.csv").open("w",encoding="utf-8",newline="") as stream:
        out=csv.DictWriter(stream,fieldnames=list(rows[0]));out.writeheader();out.writerows(rows)
    duplicate=[s for s in stops if s["stop_id"] in ("306","590")]
    dup={"suspected_sign_number":"287","records":duplicate,
         "route_directions":{s["stop_id"]:sorted(f"{r}/{d}" for r,d in uses[s["stop_id"]]) for s in duplicate},
         "distance_m":meters(*duplicate) if len(duplicate)==2 else None,
         "decision":"not_identical; do_not_merge_without_official_inventory"}
    (pth/"duplicate_code_287.json").write_text(json.dumps(dup,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    counts=collections.Counter(r["review_class"] for r in rows)
    summ={"source_sha256":sha,"total_stops":len(stops),"total_stop_times":len(times),"unnamed":len(rows),
          "classes":dict(counts),
          "closest_numbered_within_50m":sum(float(r["closest_distance_m"])<=50 for r in rows),
          "same_route_direction_within_50m":sum(r["closest_same_route_distance_m"]!="" and float(r["closest_same_route_distance_m"])<=50 for r in rows),
          "duplicate_287_distance_m":dup["distance_m"],
          "warning":"No GTFS source edited; derived georeferenced review table is for QA only pending upstream redistribution permissions."}
    (pth/"summary.json").write_text(json.dumps(summ,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summ,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
