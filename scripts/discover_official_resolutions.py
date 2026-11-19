#!/usr/bin/env python3
"""Explore the *public* official Ibagué normative index for document-search endpoints.

Research tool only. Does not scrape bulk documents, bypass controls or change any source.
Reports script/form links and limited on-page snippets for targeted follow-up.
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

URLS = [
    "https://ibague.gov.co/portal/seccion/normatividad/index.php",
    "https://transmusical.gov.co/normatividad/",
]
KEYWORDS = ("normativ", "resoluc", "document", "busqueda", "search", "buscar", "api", "ajax", "datatable")
PAT = re.compile(r"normativ|resoluci|documentos|buscar|busqueda|search|endpoint|api/|ajax|fetch", re.I)

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.forms = []
        self.inputs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("src"): self.links.append(a["src"])
        if tag == "form": self.forms.append({k:a.get(k) for k in ("method","action","id")})
        if tag in ("input","select") and len(self.inputs) < 100:
            self.inputs.append({k:a.get(k) for k in ("name","type","id","placeholder") if k in a})

def fetch(url, limit=1500000):
    req=urllib.request.Request(url,headers={"User-Agent":"ColombiaTransit source-research audit (contact via repository); public documents only","Accept":"text/html,application/javascript,text/javascript,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=22) as resp:
            return {"status":resp.status,"url":resp.url,"content_type":resp.headers.get("Content-Type",""),"text":resp.read(limit).decode("utf-8","replace")}
    except Exception as e:
        return {"error":str(e)[:350]}

def snippets(text, pattern, max_count=12):
    out=[]
    for m in pattern.finditer(text):
        start=max(0,m.start()-110);end=min(len(text),m.end()+190)
        sample=re.sub(r"\s+"," ",text[start:end])[:320]
        if sample not in out:out.append(sample)
        if len(out)>=max_count:break
    return out

def main():
    reports=[]
    for url in URLS:
        response=fetch(url)
        report={"target_url":url}
        if "error" in response:
            report["error"]=response["error"]; reports.append(report);continue
        text=response["text"]
        parser=Links();parser.feed(text)
        report.update({"http_status":response["status"],"final_url":response["url"],"html_bytes":len(text),"forms":parser.forms,"inputs":parser.inputs,"candidate_snippets":snippets(text,PAT)})
        scripts=[]
        for src in parser.links:
            absolute=urllib.parse.urljoin(response["url"],src)
            p=urllib.parse.urlparse(absolute)
            if p.hostname not in ("ibague.gov.co","www.ibague.gov.co","transmusical.gov.co"):
                continue
            # limit targeted external JS; avoid downloading the entire WordPress plugin ecosystem
            if len(scripts)>=24:break
            fetched=fetch(absolute,limit=700000)
            script={"url":absolute}
            if "text" in fetched:
                matches=snippets(fetched["text"],PAT,max_count=8)
                script.update({"bytes":len(fetched["text"]),"matches":matches})
            else:
                script["error"]=fetched["error"]
            if script.get("matches") or any(k in absolute.lower() for k in KEYWORDS):
                scripts.append(script)
        report["interesting_scripts"]=scripts
        reports.append(report)
    Path("build").mkdir(exist_ok=True)
    Path("build/municipal_index_discovery.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2)+"\n")
    for item in reports:
        print(f"TARGET {item['target_url']} status={item.get('http_status','error')} html_bytes={item.get('html_bytes',0)}")
        if item.get("error"):print("ERROR",item["error"])
        for f in item.get("forms",[]):print("FORM",str(f)[:350])
        for i in item.get("inputs",[]):print("INPUT",str(i)[:300])
        for s in item.get("interesting_scripts",[]): 
            print("SCRIPT",s["url"],"matches",len(s.get("matches",[])))
            for m in s.get("matches",[])[:4]:print("JS",m[:300])
        for a in item.get("candidate_snippets",[])[:4]:print("HTML",a[:300])

if __name__=="__main__":
    main()
