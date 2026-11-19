#!/usr/bin/env python3
"""Targeted discovery of Ibagué public transit-stop ArcGIS data.

Read-only queries to ArcGIS Online sharing/search catalog and the public OMTU Hub.
Does not enumerate unrelated nationwide data or download bulk feature layers.
"""
import json, urllib.parse, urllib.request, urllib.error, re
from pathlib import Path
API="https://www.arcgis.com/sharing/rest/search"
SEARCHES=[
 "title:Paraderos AND Ibagué",
 "paraderos AND Ibagué",
 "paradas AND Ibagué",
 "SETP AND Ibagué",
 "transporte público AND Ibagué",
 "unibague AND movilidad",
 "omtu AND Ibagué",
]
CHECK_TERMS=re.compile("ibagu[eé]|tolima|universidad de ibagu[eé]|transmusical|omtu",re.I)
def get_json(url,params=None):
    address=url+("?" + urllib.parse.urlencode(params) if params else "")
    req=urllib.request.Request(address,headers={"User-Agent":"Mozilla/5.0 ColombiaTransit-public-data-audit/1.0","Accept":"application/json,*/*"})
    with urllib.request.urlopen(req,timeout=25) as r:
        return json.loads(r.read(2500000).decode("utf-8")),r.status
def inspect():
    reports=[]; seen={}
    for q in SEARCHES:
        rec={"query":q}
        try:
            data,status=get_json(API,{"f":"json","q":q,"num":"30","start":"1"})
            rec["http_status"]=status;rec["total_hits"]=data.get("total"); rec["api_error"]=data.get("error")
            items=[]
            for item in data.get("results",[]):
                fields=["id","title","type","owner","url","description","snippet","tags","extent","numViews","created","modified","access"]
                d={k:item.get(k) for k in fields if k in item}
                # Only preserve relevant candidates or general search sample, not unrelated ArcGIS noise
                if CHECK_TERMS.search(json.dumps(d,ensure_ascii=False)):
                    items.append(d)
                    seen[item["id"]]=d
            rec["relevant_results"]=items
            print("QUERY",q,"total",data.get("total"),"local_relevant",len(items))
            for d in items[:15]: print("CANDIDATE",d.get("id"),d.get("title"),d.get("type"),"owner",d.get("owner"),"url",d.get("url"))
        except Exception as e:
            rec["error"]=repr(e);print("ERROR",q,repr(e))
        reports.append(rec)
    # look at likely public service layer metadata only
    layers=[]
    for d in list(seen.values())[:30]:
        url=d.get("url") or ""
        if "FeatureServer" not in url and "MapServer" not in url:continue
        try:
            meta,_=get_json(url,{"f":"json"})
            info={"title":d.get("title"),"id":d.get("id"),"url":url,"layers":meta.get("layers"),"name":meta.get("name"),"fullExtent":meta.get("fullExtent"),"error":meta.get("error")}
            layers.append(info)
            print("SERVICE",d.get("title"),"layers",[(x.get("id"),x.get("name")) for x in meta.get("layers",[])])
        except Exception as e:layers.append({"title":d.get("title"),"url":url,"error":repr(e)})
    out={"queries":reports,"unique_relevant_items":len(seen),"service_layer_metadata":layers}
    Path("build").mkdir(exist_ok=True)
    Path("build/ibague_stop_arcgis_discovery.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
if __name__=="__main__":inspect()
