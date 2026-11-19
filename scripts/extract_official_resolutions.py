#!/usr/bin/env python3
"""Download and OCR official 2026 Ibagué regulations if text extraction fails.

OCR is used *only* for pages lacking extractable text. Original files are
preserved byte-for-byte in CI artifacts. Spanish Tesseract is used once per
scanned page; manual verification is still required for unclear numbers.
"""
import hashlib
import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path
import fitz

DOCS={
 "004951-2026":"https://ibague.gov.co/portal/admin/archivos/normatividad/2026/70041-RES-20261113170945.pdf",
 "005549-2026":"https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf"
}
TERM=re.compile(r"(?i)frecuencia|intervalo|despach|horario|ruta(?:s)?|modific|resoluci[oó]n|pico|valle|tabla|parque automotor")
def main():
    dest=Path("build/official_resolutions");dest.mkdir(parents=True,exist_ok=True)
    results=[]
    for name,url in DOCS.items():
        result={"document":name,"url":url}
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"Mozilla/5.0 (compatible; ColombiaTransit public document research/1.0)",
                "Referer":"https://ibague.gov.co/portal/seccion/normatividad/index.php"
            })
            with urllib.request.urlopen(req,timeout=60) as resp:pdf=resp.read(40000000)
            if not pdf.startswith(b"%PDF"):raise ValueError(f"Not PDF {pdf[:60]!r}")
            (dest/(name+".pdf")).write_bytes(pdf)
            result["sha256"]=hashlib.sha256(pdf).hexdigest()
            result["bytes"]=len(pdf)
            doc=fitz.open(stream=pdf,filetype="pdf")
            result["pages"]=len(doc)
            texts=[];ocr_pages=[]; failures=[]
            for i,page in enumerate(doc):
                raw=page.get_text(sort=True)
                if len(raw.strip())<40:
                    ocr_pages.append(i+1)
                    with tempfile.TemporaryDirectory() as d:
                        path=Path(d)/f"page-{i+1}.png"
                        page.get_pixmap(matrix=fitz.Matrix(2.4,2.4),alpha=False).save(str(path))
                        proc=subprocess.run(["tesseract",str(path),"stdout","-l","spa","--psm","3"],text=True,capture_output=True,timeout=100)
                        if proc.returncode:
                            failures.append({"page":i+1,"stderr":proc.stderr[:300]})
                        else:
                            raw=proc.stdout
                texts.append(raw)
                n=len(raw.strip())
                matches=list(TERM.finditer(raw))
                print("PAGE",name,i+1,"characters",n,"search_matches",len(matches),flush=True)
                # Store full text in the artifact; logs contain article/table clues.
                for m in matches[:14]:
                    excerpt=" ".join(raw[max(0,m.start()-170):min(len(raw),m.end()+350)].split())[:600]
                    print("MATCH",name,i+1,excerpt,flush=True)
                if not matches:print("PAGE_PREFIX",name,i+1," ".join(raw.split())[:300],flush=True)
            text="\n\n".join(f"===== PAGE {i+1} =====\n{t}" for i,t in enumerate(texts))
            (dest/(name+".txt")).write_text(text,encoding="utf-8")
            result.update({"ocr_pages":ocr_pages,"ocr_failures":failures,"text_length":len(text),"page_text_lengths":[len(x) for x in texts]})
            print("DOCUMENT",name,"pages",len(doc),"OCR",len(ocr_pages),"text_length",len(text),"failures",len(failures),flush=True)
        except Exception as e:
            result["error"]=repr(e); print("ERROR",name,repr(e),flush=True)
        results.append(result)
    (dest/"metadata.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
