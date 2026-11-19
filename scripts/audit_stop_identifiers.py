#!/usr/bin/env python3
"""Audit stop identifiers in the pinned original Ibagué GTFS.

Do not rewrite GTFS stop_id: stop_times.txt references these exact keys.
Extract *candidate official paradero ID* from stop_name, preserving original.
No network requests if --zip supplied; --download checks upstream SHA-256.
"""
import argparse, collections, csv, hashlib, io, json, math, re, urllib.request, zipfile
from pathlib import Path

REV="55be037eaeaa7031eb095af53929e4ef2caaba9a"
URL=f"https://raw.githubusercontent.com/omtu-unibague/gtfs-ibague/{REV}/gtfs_ibague.zip"
SHA256="7cf772c89dec4ac1a0f97e709c9db519ad8d146caaf2121fe624c149ed29c050"

def meters(a,b):
    a1,o1,a2,o2=map(math.radians,[float(a["stop_lat"]),float(a["stop_lon"]),float(b["stop_lat"]),float(b["stop_lon"])])
    d1=a2-a1;d2=o2-o1
    k=math.sin(d1/2)**2+math.cos(a1)*math.cos(a2)*math.sin(d2/2)**2
    return round(12742000*math.asin(math.sqrt(k)))

def classify(row):
    name=row["stop_name"].strip()
    if name.lower().startswith("terminal"):return "terminal",None
    if "marcador de local" in name.lower():return "unnamed_placeholder",None
    # Reject arbitrary titles; numbered paradero names from the source include:
    # Id 1150-T3; 287 T3; 1105 Mod; 989-T1&3; etc.
    match=re.match(r"(?i)^\s*(?:id\s*)?-?\s*(\d+)(?:\b|(?=\s*[-T]))",name)
    if match:
        official_id=int(match.group(1))
        return "numbered_stop",official_id
    return "other",None

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--zip",type=Path);g.add_argument("--download",action="store_true")
    p.add_argument("--output",type=Path,default=Path("build/stop_identifiers_audit.json"))
    a=p.parse_args()
    if a.download:
        req=urllib.request.Request(URL,headers={"User-Agent":"ColombiaTransit-Ibague-StopAudit/1.0"})
        with urllib.request.urlopen(req,timeout=60) as r:data=r.read()
    else:data=a.zip.read_bytes()
    sha=hashlib.sha256(data).hexdigest()
    if sha!=SHA256:raise ValueError(f"Pinned upstream checksum mismatch: {sha}")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        stops=list(csv.DictReader(io.TextIOWrapper(z.open("stops.txt"),encoding="utf-8-sig")))
        stop_times=list(csv.DictReader(io.TextIOWrapper(z.open("stop_times.txt"),encoding="utf-8-sig")))
    byofficial=collections.defaultdict(list);counts=collections.Counter();unknown=[];bad_ids=[]
    for s in stops:
        cls,number=classify(s);counts[cls]+=1
        if cls=="numbered_stop":
            if 1<=number<=1150:byofficial[number].append(s)
            else:bad_ids.append({"stop_id":s["stop_id"],"stop_name":s["stop_name"],"parsed_id":number})
        if cls=="other":unknown.append({"stop_id":s["stop_id"],"stop_name":s["stop_name"]})
    dupes=[]
    for number,matches in sorted(byofficial.items()):
        if len(matches)>1:
            dupes.append({"candidate_official_id":number,
                          "records":[{"stop_id":x["stop_id"],"stop_name":x["stop_name"],"lat":x["stop_lat"],"lon":x["stop_lon"]} for x in matches],
                          "pairwise_meters":[meters(x,y) for i,x in enumerate(matches) for y in matches[i+1:]]})
    used={r["stop_id"] for r in stop_times}
    result={
        "source_url":URL,"source_sha256":sha,
        "stop_count":len(stops),"counts":dict(counts),
        "distinct_recognized_official_ids":len(byofficial),
        "unrepresented_numbers_in_1_to_1150":1150-len(byofficial),
        "official_id_duplicates":dupes,
        "numbered_codes_outside_1_to_1150":bad_ids,
        "unparsed_names":unknown,
        "unused_gtfs_stop_ids":sorted(set(s["stop_id"] for s in stops)-used),
        "important_warning":"Candidate physical paradero numbers parsed from stop_name must not replace GTFS stop_id or be merged automatically. 1,150 is publicly reported installed infrastructure, NOT proof of one-to-one correspondence to 1,153 GTFS stops."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GTFS stops",len(stops),"categories",dict(counts))
    print("Candidate official stop IDs",len(byofficial),"duplicate IDs",len(dupes),"out of range",len(bad_ids))
    for x in dupes:print("DUPLICATE",x["candidate_official_id"],"meters",x["pairwise_meters"])
    if unknown:print("Unparsed named stops",unknown[:20])
    return 0 if not bad_ids else 1
if __name__=="__main__":raise SystemExit(main())
