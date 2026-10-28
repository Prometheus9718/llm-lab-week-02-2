"""Build sections from reviewed line anchors while preserving every source line.

Edit boundaries.json after running 04_plan_sections.py. Accepted anchors must be
in document order. Mark non-heading bookmarks as skip with an explanatory note.
Set reviewed to true before running this script.
"""

import argparse

from lab_common import add_pdf_argument, doc_dir, load_json, write_json, write_jsonl
from section_engine import build_sections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_pdf_argument(parser)
    args = parser.parse_args()
    output_dir = doc_dir(args.pdf)
    document_path = output_dir / "document.json"
    boundaries_path = output_dir / "boundaries.json"
    if not document_path.exists():
        raise SystemExit("Error: document.json is missing. Run 03_extract_pdf.py first.")
    if not boundaries_path.exists():
        raise SystemExit("Error: boundaries.json is missing. Run 04_plan_sections.py first.")
    try:
        document = load_json(document_path)
        plan = load_json(boundaries_path)
        sections, report = build_sections(document, plan)
        sections_path = output_dir / "sections.jsonl"
        write_jsonl(sections_path, sections)
        write_json(output_dir / "sections-report.json", report)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"Error: {error}") from None
    print(f"Sections: {len(sections)}")
    print(f"Accepted boundaries: {report['accepted_boundaries']}; skipped: {report['skipped_boundaries']}")
    print(f"Line coverage: {report['assigned_lines']}/{report['input_lines']} (every source line exactly once)")
    print(f"Original line characters retained: {report['assigned_line_characters']}")
    print(f"Output: {sections_path}")


if __name__ == "__main__":
    main()
