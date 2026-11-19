#!/usr/bin/env python3
"""Fetch and extract public municipal resolution PDFs using PyMuPDF.
No OCR unless the returned documents actually require it.
"""
import hashlib
import json
import re
import urllib.request
from pathlib import Path
import fitz

DOCS={
  "004951-2026":"https://ibague.gov.co/portal/admin/archivos/normatividad/2026/70041-RES-20261113170945.pdf",
  "005549-2026":"https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf"
}
TERM=re.compile(r"(?i)frecuencia|intervalo|despach|horario|ruta(?:s)?|modific|resoluci[oó]n")
def main():
    dest=Path("build/official_resolutions")
    dest.mkdir(parents=True,exist_ok=True)
    results=[]
    for name,url in DOCS.items():
        d={"document":name,"url":url}
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit official-document research/1.0)","Referer":"https://ibague.gov.co/portal/seccion/normatividad/index.php"})
            with urllib.request.urlopen(req,timeout=60) as r:
                data=r.read(40000000)
                d["http_status"]=r.status
                d["content_type"]=r.headers.get("Content-Type","")
            if not data.startswith(b"%PDF"):raise ValueError(f"Not a PDF: {data[:50]!r}")
            (dest/(name+".pdf")).write_bytes(data)
            d["sha256"]=hashlib.sha256(data).hexdigest()
            doc=fitz.open(stream=data,filetype="pdf")
            d["pages"]=len(doc)
            extracted=[]
            for i,page in enumerate(doc):
                page_text=page.get_text(sort=True)
                extracted.append(page_text)
                count=len(page_text.strip())
                print("PAGE",name,i+1,"text_length",count)
                if count:
                    if len(page_text)<8000:
                        print("PAGE_TEXT_BEGIN",name,i+1,"\n",page_text,"\nPAGE_TEXT_END",name,i+1)
                    else:
                        for m in list(TERM.finditer(page_text))[:20]:
                            print("PAGE_MATCH",name,i+1," ".join(page_text[max(0,m.start()-150):m.end()+300].split())[:480])
            full="\n\n".join(f"===== PAGE {i+1} =====\n{t}" for i,t in enumerate(extracted))
            (dest/(name+".txt")).write_text(full,encoding="utf-8")
            d["text_len"]=len(full)
            d["blank_pages"]=[i+1 for i,t in enumerate(extracted) if len(t.strip())<40]
            d["needs_visual_or_ocr"]=bool(d["blank_pages"])
            print("DOCUMENT",name,"pages",len(doc),"bytes",len(data),"blank_pages",d["blank_pages"],"text_len",d["text_len"])
        except Exception as e:
            print("ERROR",name,repr(e))
            d["error"]=repr(e)
        results.append(d)
    (dest/"metadata.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
