"""Verify the complete PDF pipeline on pdf1.pdf, pdf2.pdf and pdf3.pdf.

Run inside the lab .venv. Uses existing human-reviewed boundaries, or explicit
reference plans supplied with --review-dir. Never approves an unknown PDF.
"""
from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from lab_common import doc_dir, load_json, load_jsonl, write_json


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_output(directory):
    document=load_json(directory/"document.json")
    sections=load_jsonl(directory/"sections.jsonl")
    chunks=load_jsonl(directory/"chunks.jsonl")
    source={line["line_id"]:line for page in document["pages"] for line in page["lines"]}
    counts=Counter(span["line_id"] for section in sections for span in section["source_spans"])
    if counts!=Counter({line_id:1 for line_id in source}):
        raise ValueError("Section line coverage differs from extraction.")
    if not sections or not chunks:
        raise ValueError("No sections/chunks created.")
    for section in sections:
        for span in section["source_spans"]:
            if section["text"][span["start_char"]:span["end_char"]]!=source[span["line_id"]]["text"]:
                raise ValueError("Section source span does not match original line text.")
        covered=0
        for chunk in [item for item in chunks if item["section_id"]==section["section_id"]]:
            start,end=chunk["section_start_char"],chunk["section_end_char"]
            if start>covered or end<=start or end-start>900:
                raise ValueError("Chunk coverage or maximum size failed.")
            if chunk["text"]!=section["text"][start:end] or chunk["heading_path"]!=section["heading_path"]:
                raise ValueError("Chunk text/path differs from section.")
            pages=[]
            for span in chunk["source_spans"]:
                original=source[span["line_id"]]
                fragment=chunk["text"][span["start_char"]:span["end_char"]]
                if fragment!=original["text"][span["line_start_char"]:span["line_end_char"]]:
                    raise ValueError("Chunk provenance text mismatch.")
                if span["pdf_page"]!=original["pdf_page"]:
                    raise ValueError("Chunk provenance page mismatch.")
                pages.append(span["pdf_page"])
            if sorted(set(pages))!=chunk["source_pages"]:
                raise ValueError("Source pages do not match chunk spans.")
            covered=max(covered,end)
        if covered!=len(section["text"]):
            raise ValueError("Not all section characters have a chunk.")
    return {
        "source_file":document["source_file"],"source_sha256":document["document_id"],
        "pages":document["page_count"],"bookmarks":len(document["outline"]),
        "no_extractable_text_pages":[page["pdf_page"] for page in document["pages"] if page["char_count"]==0],
        "extracted_lines":len(source),"sections":len(sections),"chunks":len(chunks),
        "sections_sha256":digest(directory/"sections.jsonl"),"chunks_sha256":digest(directory/"chunks.jsonl"),
        "all_lines_once":True,"all_section_characters_covered":True,"source_spans_verified":True,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-dir",type=Path,help="Directory with already reviewed pdf1.json/pdf2.json/pdf3.json for these exact file hashes")
    parser.add_argument("--report",type=Path,default=ROOT/"validation/current/report.json")
    args=parser.parse_args()
    import pymupdf
    report={"os":platform.system(),"release":platform.release(),"architecture":platform.machine(),
            "python":platform.python_version(),"pymupdf":pymupdf.__version__,"documents":[],"passed":False}
    started=time.monotonic()
    args.report.parent.mkdir(parents=True,exist_ok=True)
    try:
        for number in (1,2,3):
            argument=f"data/pdfs/pdf{number}.pdf"
            directory=doc_dir(argument)
            log=[]
            for script in ("03_extract_pdf.py","04_plan_sections.py"):
                result=subprocess.run([sys.executable,str(ROOT/"scripts"/script),"--pdf",argument],cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
                log.append(result.stdout+result.stderr)
                if result.returncode:
                    raise RuntimeError(f"{script} failed for pdf{number}: {result.stderr}")
            proposed=load_json(directory/"boundaries.proposed.json")
            if args.review_dir:
                reference=args.review_dir/f"pdf{number}.json"
                if not reference.is_file():
                    raise ValueError(f"Missing reference review: {reference}")
                # Builder checks both document hash and review state before using it.
                shutil.copy2(reference,directory/"boundaries.json")
            for script in ("05_build_sections.py","06_chunk_sections.py","07_preview.py"):
                result=subprocess.run([sys.executable,str(ROOT/"scripts"/script),"--pdf",argument],cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
                log.append(result.stdout+result.stderr)
                if result.returncode:
                    raise RuntimeError(f"{script} failed for pdf{number}: {result.stderr}")
            (args.report.parent/f"pdf{number}.log").write_text("\n".join(log),encoding="utf-8")
            checked=check_output(directory)
            checked["unresolved_before_human_review"]=sum(b["status"]=="unresolved" for b in proposed["boundaries"])
            checked["skipped_after_review"]=sum(b["status"]=="skip" for b in load_json(directory/"boundaries.json")["boundaries"])
            report["documents"].append(checked)
            print(f"pdf{number}: {checked['pages']} pages -> {checked['sections']} sections -> {checked['chunks']} chunks; PASS")
        report["passed"]=True
    except (OSError,ValueError,RuntimeError) as exc:
        report["error"]=str(exc)
        raise SystemExit(str(exc)) from exc
    finally:
        report["seconds"]=round(time.monotonic()-started,3)
        write_json(args.report,report)
        print("Report:",args.report)


if __name__=="__main__":
    main()
