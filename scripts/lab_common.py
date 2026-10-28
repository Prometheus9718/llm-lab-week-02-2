"""Shared, OS-independent paths and JSON helpers for the week-one workshop."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


def add_pdf_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--pdf", required=True, help="PDF path, relative to project root or absolute")


def resolve_pdf(pdf_arg: str) -> Path:
    path = Path(pdf_arg).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if not path.is_file():
        raise SystemExit(f"PDF not found: {path}\nCheck --pdf and the files in data/pdfs/.")
    if path.suffix.lower() != ".pdf":
        raise SystemExit(f"Expected a .pdf file: {path.name}")
    return path


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def doc_dir(pdf_arg: str) -> Path:
    path = resolve_pdf(pdf_arg)
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", path.stem).strip("-")[:64] or "document"
    return ROOT / "data" / "extracted" / f"{slug}-{file_digest(path)[:10]}"


def source_label(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise SystemExit(f"Missing: {path}\nRun the preceding workshop step first.")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path.name}, line {exc.lineno}: {exc.msg}") from exc


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"Missing: {path}\nRun the preceding workshop step first.")
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid JSONL: {path.name}, line {number}: {exc}") from exc
    return rows


def require_pymupdf():
    try:
        import pymupdf
    except ImportError as exc:
        raise SystemExit("PyMuPDF is missing. Activate .venv, then run: python -m pip install -r requirements.txt") from exc
    return pymupdf
