"""Extract one PDF, display characters per page, and preserve lines and bookmarks."""
from __future__ import annotations

import argparse 
import csv

from lab_common import add_pdf_argument, doc_dir, file_digest, require_pymupdf, resolve_pdf, source_label, write_json, write_jsonl


def extract_document(path, pymupdf) -> dict:
    with pymupdf.open(path) as pdf:
        if pdf.needs_pass:
            raise SystemExit("This PDF is password protected. Use a classroom PDF that opens without a password.")
        outline = []
        for index, entry in enumerate(pdf.get_toc(simple=False), 1):
            level, title, page_number = entry[:3]
            details = entry[3] if len(entry) > 3 else {}
            point = details.get("to")
            outline.append({
                "outline_index": index, "level": level, "title": title,
                "pdf_page": page_number,
                "destination_y": round(float(point.y), 3) if point is not None else None,
            })
        pages = []
        flags = pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES
        for number, page in enumerate(pdf, 1):
            layout = page.get_text("dict", flags=flags, sort=True)
            lines = []
            for block in layout["blocks"]:
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    text = "".join(span["text"] for span in spans).rstrip()
                    if not text.strip():
                        continue
                    lines.append({
                        "line_id": f"p{number:04d}-l{len(lines)+1:04d}",
                        "pdf_page": number, "text": text,
                        "bbox": [round(float(v), 3) for v in line["bbox"]],
                        "font_size": round(max((float(span["size"]) for span in spans), default=0), 2),
                        "bold": any(int(span.get("flags", 0)) & 16 for span in spans),
                    })
            # Use the same line representation for counts, sections and provenance.
            text = "\n".join(line["text"] for line in lines)
            pages.append({
                "pdf_page": number, "page_label": page.get_label() or str(number),
                "char_count": len(text.strip()), "text": text, "lines": lines,
                "image_count": len(page.get_image_info()),
                "status": "text_extracted" if text.strip() else "no_extractable_text_review",
            })
        return {
            "schema_version": 1, "document_id": file_digest(path),
            "source_file": path.name, "source_path": source_label(path),
            "page_count": len(pdf), "outline": outline, "pages": pages,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_pdf_argument(parser)
    args = parser.parse_args()
    source = resolve_pdf(args.pdf)
    destination = doc_dir(args.pdf)
    pymupdf = require_pymupdf()
    try:
        document = extract_document(source, pymupdf)
    except (RuntimeError, ValueError) as exc:
        raise SystemExit(f"Cannot extract this PDF: {exc}") from exc
    write_json(destination / "document.json", document)
    write_jsonl(destination / "pages.jsonl", document["pages"])
    with (destination / "page-stats.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["pdf_page", "printed_label", "characters", "text_lines", "images", "status"])
        for page in document["pages"]:
            writer.writerow([page["pdf_page"], page["page_label"], page["char_count"], len(page["lines"]), page["image_count"], page["status"]])
    with (destination / "lines.txt").open("w", encoding="utf-8", newline="\n") as file:
        for page in document["pages"]:
            file.write(f"\n=== PDF page {page['pdf_page']} / printed label {page['page_label']} ===\n")
            for line in page["lines"]:
                file.write(f"[{line['line_id']}] [{line['font_size']}pt] {line['text']}\n")
    no_text = [page["pdf_page"] for page in document["pages"] if not page["text"].strip()]
    for page in document["pages"]:
        print(f"PDF page {page['pdf_page']:>4}: {page['char_count']:>6} characters; {len(page['lines']):>3} lines; images={page['image_count']}")
    print("Pages:", document["page_count"])
    print("Bookmarks:", len(document["outline"]))
    print("No extractable text - review visually:", no_text)
    print("Artifacts:", destination)
    print("Counts are Unicode code points in text.strip(), including internal spaces/newlines; not tokens.")
    print("A zero count does not prove that a page is blank or needs OCR.")


if __name__ == "__main__":
    main()
