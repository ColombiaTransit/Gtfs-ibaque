#!/usr/bin/env python3
"""Targeted searches of the official Alcaldía de Ibagué public normative index.

Uses exactly the public form fields and endpoint in /portal/js/normatividad.js.
No bulk crawling. Five small searches, results preserved with source URLs.
"""
import html
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ENDPOINT="https://ibague.gov.co/portal/seccion/normatividad/resultado.php"
SEARCHES=["004951","00197","000370","frecuencias de despacho","transporte público colectivo"]

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.href=None
        self.buffer=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="a" and a.get("href"):
            self.href=a["href"];self.buffer=[]
    def handle_data(self,data):
        if self.href is not None:self.buffer.append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self.href is not None:
            self.links.append({"href":self.href,"label":" ".join(" ".join(self.buffer).split())[:180]})
            self.href=None;self.buffer=[]

def search(term):
    fields={
        "lib":"",
        "pagina":"1",
        "palabra":term,
        "pk_id_clase":"",
        "fk_id_dependencia":"",
        "a_documento":"",
        "fechaini":"",
        "fechafin":""
    }
    req=urllib.request.Request(ENDPOINT,data=urllib.parse.urlencode(fields).encode("utf-8"),headers={
        "User-Agent":"ColombiaTransit public-document research (https://github.com/ColombiaTransit/Gtfs-ibaque)",
        "Referer":"https://ibague.gov.co/portal/seccion/normatividad/index.php",
        "Origin":"https://ibague.gov.co",
        "Accept":"text/html, */*",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
    },method="POST")
    with urllib.request.urlopen(req,timeout=35) as r:
        raw=r.read(500000)
        status=r.status
    text=raw.decode("utf-8","replace")
    parser=LinkParser();parser.feed(text)
    # Preserve all visible snippets near likely hits, keeping output compact
    matches=[]
    regex=re.compile(r"(?i)resoluci[oó]n|frecuencia|despacho|movilidad|transporte|004951|00197|000370")
    for m in regex.finditer(text):
        segment=text[max(0,m.start()-160):min(len(text),m.end()+250)]
        segment=html.unescape(re.sub("<[^>]*>"," ",segment))
        segment=" ".join(segment.split())[:350]
        if segment not in matches:matches.append(segment)
        if len(matches)>=12:break
    links=[]
    for x in parser.links:
        url=urllib.parse.urljoin(ENDPOINT,x["href"])
        if url.startswith("https://ibague.gov.co/") or url.startswith("https://www.ibague.gov.co/"):
            if url not in {z["url"] for z in links}: links.append({"url":url,"label":x["label"]})
    return {"term":term,"status":status,"bytes":len(raw),"head":text[:280],"links":links[:80],"matched_snippets":matches}

def main():
    results=[]
    for term in SEARCHES:
        try:
            result=search(term)
        except Exception as e:
            result={"term":term,"error":str(e)[:500]}
        results.append(result)
        print(f"SEARCH {term}: status={result.get('status','error')} bytes={result.get('bytes','-')}")
        print("HEAD",result.get("head","")[:150])
        if result.get("error"):print("ERROR",result["error"])
        for x in result.get("links",[])[:20]:print("LINK",x["label"],x["url"])
        for x in result.get("matched_snippets",[])[:4]:print("TEXT",x[:300])
        time.sleep(.7)
    Path("build").mkdir(exist_ok=True)
    Path("build/municipal_resolution_search.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
