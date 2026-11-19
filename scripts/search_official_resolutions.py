#!/usr/bin/env python3
"""Search the official municipal Gaceta using its actual multipart HTML form.

The site publishes a free public search. Fetch form first to preserve cookies and
hidden fields, then use the same FormData encoding as its JavaScript client.
Only five targeted terms; never enumerate the entire database.
"""
import html
import http.cookiejar
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT="https://ibague.gov.co/portal/seccion/normatividad/"
INDEX=ROOT+"index.php"
ENDPOINT=ROOT+"resultado.php"
SEARCHES=[("197","2024"),("370","2022"),("005459","2026"),("5459","2026"),("frecuencias","2024"),("frecuencias","2026")]

class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside=False;self.hidden={};self.fields=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="form" and a.get("id")=="nmFormulario": self.inside=True
        if self.inside and tag in ("input","select"):
            if a.get("name"):
                self.fields.append((a["name"],a.get("value","")))
                if a.get("type")=="hidden":self.hidden[a["name"]]=a.get("value","")
    def handle_endtag(self,tag):
        if tag=="form":self.inside=False

def post_multipart(opener,form,word,year):
    import secrets
    boundary="----colombiatransit-"+secrets.token_hex(8)
    values={k:v for k,v in form.fields}
    values.update({"palabra":word,"pagina":"1","a_documento":year})
    data=b"".join((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode("utf8") for k,v in values.items())
    data+=f"--{boundary}--\r\n".encode()
    req=urllib.request.Request(ENDPOINT,data=data,method="POST",headers={
        "User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit OfficialDocumentResearch/1.0)",
        "Referer":INDEX,
        "Origin":"https://ibague.gov.co",
        "Accept":"*/*",
        "Content-Type":f"multipart/form-data; boundary={boundary}",
    })
    try:
        with opener.open(req,timeout=30) as r:
            content=r.read(600000)
            return r.status,content.decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code,e.read(20000).decode("utf-8","replace")

def extract(text):
    links=[]
    for href,label in re.findall(r"<a\s+[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",text,flags=re.I|re.S):
        stripped=" ".join(html.unescape(re.sub("<[^>]+>"," ",label)).split())
        full=urllib.parse.urljoin(ROOT,html.unescape(href))
        if full not in [x["url"] for x in links]:
            links.append({"label":stripped[:220],"url":full})
    plain=" ".join(html.unescape(re.sub("<[^>]+>"," ",text)).split())
    return links[:60],plain[:1800]

def main():
    cj=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    with opener.open(urllib.request.Request(INDEX,headers={"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit OfficialDocumentResearch/1.0)"}),timeout=30) as r:
        body=r.read().decode("utf-8","replace")
    form=FormParser();form.feed(body)
    print("OFFICIAL_FORM_FIELDS",form.fields)
    print("COOKIE_COUNT",len(cj))
    results=[]
    for word, year in SEARCHES:
        status,text=post_multipart(opener,form,word,year)
        links,plain=extract(text)
        d={"search":word,"year":year,"status":status,"text_prefix":plain,"links":links}
        results.append(d)
        print("SEARCH",word,"YEAR",year,"status",status,"length",len(text),"links",len(links))
        print("TEXT",plain[:800])
        for x in links[:20]:
            print("LINK",x["label"],x["url"])
        time.sleep(.5)
    Path("build").mkdir(exist_ok=True)
    Path("build/municipal_resolution_search.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
