#!/usr/bin/env python3
"""Validate manually transcribed official Ibagué 2026 legal headways.

Data are from Resolución 005549, Art. 3, pp. 9–13. Reports discrepancies
against TransMusical posters; never silently fixes them.
"""
import argparse
import csv
import json
import re
from pathlib import Path

EXPECTED_MISSING={"22","23","24","28","29","31","33","35","37","40","43","48","50","53","82","90"}
PERIOD_COLUMNS=("weekday_peak_hp_min","weekday_valley_hv_min","weekday_night_noc_min","saturday_peak_hp_min","saturday_valley_hv_min","saturday_night_noc_min","sunday_holiday_min")
SCHEDULES=(("weekday_service_hours","mon_sat_start","mon_sat_end"),("sunday_holiday_service_hours","sunday_holiday_start","sunday_holiday_end"))
SRC="https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf"
SHA="fe718cac309bcc34dd75cec28140f9c99cd7f77ad8971b8e1778f56bc3ba41a1"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as stream:return list(csv.DictReader(stream))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--official",type=Path,default=Path("research/official_resolution_005549_frequencies.csv"))
    parser.add_argument("--posters",type=Path,default=Path("research/official_service_hours.csv"))
    parser.add_argument("--routes",type=Path,default=Path("research/routes.csv"))
    parser.add_argument("--output",type=Path,default=Path("build/official_frequencies_validation.json"))
    args=parser.parse_args()
    rows,poster_rows,upstream=read(args.official),read(args.posters),read(args.routes)
    expected={x["route_label"] for x in upstream if x["upstream_route_id"]}
    found={x["route"] for x in rows}
    errors=[]
    if len(rows)!=len(expected):errors.append(f"Expected {len(expected)} legal rows, got {len(rows)}")
    if len(rows)!=len(found):errors.append("Duplicate legal route row")
    if expected!=found:errors.append(f"Legal route identifiers mismatch: missing={sorted(expected-found)}, extra={sorted(found-expected)}")
    if EXPECTED_MISSING-not found:errors.append(f"Originally missing routes are not covered: {sorted(EXPECTED_MISSING-found)}")
    n=0
    for row in rows:
        route=row["route"]
        for col in PERIOD_COLUMNS:
            try: headway=int(row[col])
            except ValueError:
                errors.append(f"{route} invalid {col}={row[col]}")
                continue
            n+=1
            if headway==0 and not (route=="29" and col in ("weekday_night_noc_min","saturday_night_noc_min")):
                errors.append(f"{route} unexpected zero for {col}")
            if not 0<=headway<=60:errors.append(f"{route} invalid headway {col}={headway}")
        for col,*_ in SCHEDULES:
            if not re.fullmatch(r"\d\d:\d\d-\d\d:\d\d",row[col]):errors.append(f"{route}: invalid span {col}={row[col]}")
        if row["source_url"]!=SRC or row["source_sha256"]!=SHA:errors.append(f"{route}: wrong source provenance")
    posters={r["route"]:r for r in poster_rows}
    conflicts=[]
    for row in rows:
        route=row["route"]
        poster=posters.get("7" if route=="4/7" else route)
        if poster is None:
            errors.append(f"Missing poster for {route}");continue
        for official_key,poster_start_key,poster_end_key in SCHEDULES:
            official_start,official_end=row[official_key].split("-")
            for key,ref,cur in (("start",poster[poster_start_key],official_start),("end",poster[poster_end_key],official_end)):
                if ref and ref!=cur:conflicts.append({"route":route,"day_type":official_key,"field":key,"regulation":cur,"poster":ref,"poster_url":poster["official_poster_url"]})
    report={"primary_source":SRC,"primary_source_sha256":SHA,"route_count":len(rows),"transcribed_frequency_cells":n,"zero_night_frequency_routes":["29"],"originally_missing_routes_with_new_official_frequency":len(EXPECTED_MISSING&found),"official_poster_hours_conflicts":conflicts,"conflict_count":len(conflicts),"errors":errors,"warning":"Poster and legal service spans are both official; do not auto-reconcile. Period clock cutoffs remain unverified and no GTFS feed has been regenerated."}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Legal routes: {len(rows)} | official headways: {n} | previously missing routes covered: {len(EXPECTED_MISSING&found)}")
    print(f"Discrepancies with official route posters: {len(conflicts)} field-level differences")
    print(f"Validation errors: {len(errors)}")
    for e in errors:print("ERROR:",e)
    return 1 if errors else 0
if __name__=="__main__":raise SystemExit(main())
