#!/usr/bin/env python3
"""Inspect additional OFFICIAL Ibagué municipal/SETP archives for two named acts.
No document enumeration. Preserve URL, status and relevant link context.
"""
import json,re,urllib.request,urllib.parse,html
from html.parser import HTMLParser
from pathlib import Path

TARGETS={
"legacy_gaceta":"https://ibague.gov.co/portal/seccion/contenido/contenido.php?cnt=10&subcnt=71&subtype=1&type=2",
"setp_norms":"https://transmusical.gov.co/normatividad/",
"setp_search_00197":"https://transmusical.gov.co/?s=00197",
"setp_search_1595":"https://transmusical.gov.co/?s=1595",
"setp_wp_search_00197":"https://transmusical.gov.co/wp-json/wp/v2/search?search=00197&per_page=20",
"setp_wp_search_1595":"https://transmusical.gov.co/wp-json/wp/v2/search?search=1595&per_page=20",
}
PAT=re.compile(r"00197|(?<!\d)197(?!\d)|1595|001595|30\s+de\s+abril\s+de\s+2024|27\s+de\s+marzo\s+de\s+2026|frecuen|resolucion|resoluci[oó]n|movilidad",re.I)
class Link(HTMLParser):
    def __init__(self):super().__init__();self.a=None;self.parts=[];self.anchors=[]
    def handle_starttag(self,t,attrs):
        d=dict(attrs)
        if t=="a" and d.get("href"):self.a=d["href"];self.parts=[]
    def handle_data(self,data):
        if self.a is not None:self.parts.append(data)
    def handle_endtag(self,t):
        if t=="a" and self.a is not None:
            self.anchors.append({"href":self.a,"text":" ".join(" ".join(self.parts).split())[:260]});self.a=None;self.parts=[]
def run():
    results=[]
    for k,url in TARGETS.items():
        result={"key":k,"url":url}
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit/1.0 research)","Accept":"text/html,application/json,*/*"})
            with urllib.request.urlopen(req,timeout=24) as resp:
                data=resp.read(12000000); result["http_status"]=resp.status;result["content_type"]=resp.headers.get("Content-Type","");result["final_url"]=resp.url
            text=data.decode("utf-8","replace")
            result["length"]=len(text)
            if k == "legacy_gaceta":
                exact = {}
                for key, pat in {
                    "00197":r"(?<!\\d)0*197(?!\\d)",
                    "1595":r"(?<!\\d)0*1595(?!\\d)",
                    "30_april_2024":r"30\\s+de\\s+abril\\s+de\\s+2024",
                    "27_march_2026":r"27\\s+de\\s+marzo\\s+de\\s+2026",
                }.items():
                    found = list(re.finditer(pat, text, re.I))
                    exact[key] = {"count":len(found),"contexts":[]}
                    for m in found[:16]:
                        context = html.unescape(re.sub(r"\\s+"," ",text[max(0,m.start()-400):m.end()+450]))
                        exact[key]["contexts"].append(context[:930])
                        print("EXACT", key, context[:850])
                result["exact_hits"] = exact
            if "application/json" in result["content_type"]:
                result["json_head"]=text[:3500]
            parser=Link();parser.feed(text)
            hits=[]
            for i,m in enumerate(PAT.finditer(text)):
                if len(hits)>=45:break
                portion=re.sub(r"\s+"," ",html.unescape(re.sub("<[^>]+>"," ",text[max(0,m.start()-160):m.end()+210])))
                if portion not in hits:hits.append(portion[:380])
            result["keyword_context"]=hits
            anchor_hits=[]
            for a in parser.anchors:
                absurl=urllib.parse.urljoin(result["final_url"],a["href"])
                if PAT.search(a["text"]+" "+a["href"]) or ".pdf" in absurl.lower() or "/normativ" in absurl.lower():
                    anchor_hits.append({"url":absurl,"text":a["text"]})
            result["links"]=anchor_hits[:75]
            print("TARGET",k,"status",result["http_status"],"len",result["length"],"links",len(result["links"]))
            for x in result["links"][:28]:print("LINK",k,x["text"][:80],x["url"][:250])
            for x in result["keyword_context"][:12]:print("SNIP",k,x[:300])
        except Exception as e:result["error"]=repr(e);print("ERROR",k,repr(e))
        results.append(result)
    out=Path("build/clock_amendments_archive_discovery.json");out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
if __name__=="__main__":run()
