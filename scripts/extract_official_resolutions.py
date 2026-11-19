#!/usr/bin/env python3
"""Download and text-extract two official Ibagué 2026 resolutions.

Sources are the Alcaldía's public Gaceta results, not third-party copies.
No OCR unless scan inspection proves it necessary.
"""
import hashlib
import json
import re
import subprocess
import urllib.request
from pathlib import Path

DOCS={
    "004951-2026":"https://ibague.gov.co/portal/admin/archivos/normatividad/2026/70041-RES-20261113170945.pdf",
    "005549-2026":"https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf",
}
TERMS=re.compile(r"(?i)frecuencia|intervalo|despach|horario|ruta(?:s)?|servicio|modific|vigencia|resoluci[oó]n")
def main():
    dest=Path("build/official_resolutions")
    dest.mkdir(parents=True,exist_ok=True)
    reports=[]
    for name,url in DOCS.items():
        report={"name":name,"source_url":url}
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit PublicDocuments/1.0)","Referer":"https://ibague.gov.co/portal/seccion/normatividad/index.php"})
            with urllib.request.urlopen(req,timeout=50) as res:
                binary=res.read(32000000)
                report["http_status"]=res.status
                report["content_type"]=res.headers.get("Content-Type")
            if not binary.startswith(b"%PDF"):
                raise ValueError(f"not a PDF ({binary[:90]!r})")
            pdf=dest/f"{name}.pdf"
            pdf.write_bytes(binary)
            report["pdf_sha256"]=hashlib.sha256(binary).hexdigest()
            report["bytes"]=len(binary)
            info=subprocess.run(["pdfinfo",str(pdf)],capture_output=True,text=True)
            report["pdfinfo"]={line.split(":",1)[0].strip():line.split(":",1)[1].strip() for line in info.stdout.splitlines() if ":" in line}
            txt=dest/f"{name}.txt"
            p=subprocess.run(["pdftotext","-layout",str(pdf),str(txt)],capture_output=True,text=True)
            if p.returncode: raise RuntimeError(p.stderr[:500])
            raw=txt.read_text(encoding="utf-8")
            pages=raw.split("\f")
            report["text_length"]=len(raw)
            report["pages_with_text"]=[len(x.strip()) for x in pages]
            print("DOCUMENT",name,"http",report["http_status"],"bytes",report["bytes"],"pages",report["pdfinfo"].get("Pages"),"text_len",len(raw))
            print("SOURCE",url)
            for idx,page in enumerate(pages):
                if not page.strip():continue
                matches=list(TERMS.finditer(page))
                print("PAGE",idx+1,"length",len(page),"term_matches",len(matches))
                # All text in small pages; relevant snippets in very large pages.
                if len(page)<4500:
                    print("TEXT_BEGIN",name,idx+1,"\n",page[:4500],"\nTEXT_END",name,idx+1)
                else:
                    for m in matches[:12]:
                        nearby=" ".join(page[max(0,m.start()-180):min(len(page),m.end()+250)].split())
                        print("MATCH",name,idx+1,nearby[:470])
            reports.append(report)
        except Exception as e:
            report["error"]=str(e)[:1000]
            print("ERROR",name,repr(e))
            reports.append(report)
    (dest/"metadata.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":main()
