"""Split reviewed sections into bounded, overlapping chunks with page/line provenance."""
from __future__ import annotations

import argparse
import hashlib

from lab_common import add_pdf_argument, doc_dir, load_jsonl, write_json, write_jsonl


def character_windows(text: str, maximum: int, overlap: int):
    """Prefer paragraph/line/word endings; preserve the exact original substring."""
    start = 0
    while start < len(text):
        end = min(start + maximum, len(text))
        if end < len(text):
            lower = start + maximum // 2
            for delimiter in ("\n\n", "\n", " "):
                position = text.rfind(delimiter, lower, end)
                if position >= lower:
                    end = position + len(delimiter)
                    break
        yield start, end
        if end == len(text):
            break
        start = max(start + 1, end - overlap)


def make_chunks(sections: list[dict], maximum: int, overlap: int) -> tuple[list[dict], dict]:
    if maximum < 2 or overlap < 0 or overlap >= maximum // 2:
        raise SystemExit("Use --max-chars >= 2 and 0 <= --overlap-chars < half of max-chars.")
    chunks = []
    covered_characters = 0
    for section in sections:
        text = section["text"]
        covered_until = 0
        for index, (start, end) in enumerate(character_windows(text, maximum, overlap), 1):
            if start > covered_until or end <= start or end - start > maximum:
                raise SystemExit("Chunk coverage validation failed; no output written.")
            covered_until = max(covered_until, end)
            spans = []
            for span in section["source_spans"]:
                left = max(start, span["start_char"])
                right = min(end, span["end_char"])
                if left < right:
                    spans.append({
                        "pdf_page": span["pdf_page"], "line_id": span["line_id"],
                        "start_char": left - start, "end_char": right - start,
                        "line_start_char": left - span["start_char"],
                        "line_end_char": right - span["start_char"],
                    })
            pages = sorted({span["pdf_page"] for span in spans})
            if not pages:
                raise SystemExit("Chunk has no source lines; inspect section offsets.")
            identity = f"{section['document_id']}:{section['section_id']}:{start}:{end}"
            chunks.append({
                "chunk_id": hashlib.sha256(identity.encode()).hexdigest()[:24],
                "document_id": section["document_id"], "source_file": section["source_file"],
                "section_id": section["section_id"], "chunk_index_in_section": index,
                "heading_path": section["heading_path"], "text": text[start:end],
                "char_count": end - start, "section_start_char": start, "section_end_char": end,
                "pdf_page_start": min(pages), "pdf_page_end": max(pages),
                "source_pages": pages, "source_spans": spans,
            })
        if covered_until != len(text):
            raise SystemExit(f"Incomplete coverage: {section['section_id']}")
        covered_characters += covered_until
    report = {
        "sections": len(sections), "chunks": len(chunks),
        "max_chars": maximum, "overlap_chars": overlap,
        "section_characters": sum(len(item["text"]) for item in sections),
        "covered_characters": covered_characters,
        "coverage_complete": True,
        "note": "Character limits are not model token limits. No PDF chunks were embedded in this workshop.",
    }
    return chunks, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_pdf_argument(parser)
    parser.add_argument("--max-chars", type=int, default=900)
    parser.add_argument("--overlap-chars", type=int, default=100)
    args = parser.parse_args()
    destination = doc_dir(args.pdf)
    sections = load_jsonl(destination / "sections.jsonl")
    if not sections:
        raise SystemExit("No sections. Complete the heading review and section-building step first.")
    chunks, report = make_chunks(sections, args.max_chars, args.overlap_chars)
    write_jsonl(destination / "chunks.jsonl", chunks)
    write_json(destination / "chunks-report.json", report)
    print("Sections:", len(sections))
    print("Chunks:", len(chunks))
    print("Characters covered:", report["covered_characters"])
    print("Coverage complete:", report["coverage_complete"])
    print("Saved:", destination / "chunks.jsonl")
    print("No chunks cross section boundaries. Overlap occurs inside a section only.")


if __name__ == "__main__":
    main()
