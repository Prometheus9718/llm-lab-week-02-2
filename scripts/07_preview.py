"""Inspect extracted line anchors, sections, and chunks in the terminal or Markdown."""
from __future__ import annotations

import argparse

from lab_common import add_pdf_argument, doc_dir, load_json, load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_pdf_argument(parser)
    parser.add_argument("--page", type=int, help="Show all extracted lines and IDs for one physical PDF page")
    parser.add_argument("--chunks", type=int, default=3, help="Number of short chunk previews to print")
    args = parser.parse_args()
    destination = doc_dir(args.pdf)
    document = load_json(destination / "document.json")
    if args.page is not None:
        if not 1 <= args.page <= document["page_count"]:
            raise SystemExit(f"--page must be between 1 and {document['page_count']}.")
        page = document["pages"][args.page - 1]
        print(f"PDF page {page['pdf_page']} / printed label {page['page_label']}")
        for line in page["lines"]:
            print(f"[{line['line_id']}] {line['text']}")
        if not page["lines"]:
            print("No extractable text. Inspect the PDF visually before deciding whether OCR is needed.")
        return
    sections_path = destination / "sections.jsonl"
    chunks_path = destination / "chunks.jsonl"
    sections = load_jsonl(sections_path) if sections_path.exists() else []
    chunks = load_jsonl(chunks_path) if chunks_path.exists() else []
    print("Source:", document["source_file"])
    print("Pages:", document["page_count"])
    print("Sections:", len(sections), "| Chunks:", len(chunks))
    markdown = ["# PDF section/chunk preview", "", f"Source: {document['source_file']}", "", "## Sections", ""]
    for index, section in enumerate(sections, 1):
        path = " > ".join(section["heading_path"])
        line = f"{index}. {path} — PDF pages {section['pdf_page_start']}-{section['pdf_page_end']}; {len(section['text'])} characters"
        markdown.append(line)
        print(line)
    markdown.extend(["", "## Chunk examples", ""])
    for chunk in chunks[:max(0, args.chunks)]:
        title = " > ".join(chunk["heading_path"])
        header = f"Chunk {chunk['chunk_id']} | {title} | PDF pages {chunk['pdf_page_start']}-{chunk['pdf_page_end']} | {chunk['char_count']} characters"
        print("\n" + header)
        print(repr(chunk["text"][:300]))
        markdown.extend(["### " + header, "", "```text", chunk["text"][:600], "```", ""])
    if not sections:
        print("Next: plan/review boundaries, then build sections.")
    if sections and not chunks:
        print("Next: run 06_chunk_sections.py.")
    output = destination / "preview.md"
    output.write_text("\n".join(markdown) + "\n", encoding="utf-8")
    print("Preview saved:", output)


if __name__ == "__main__":
    main()
