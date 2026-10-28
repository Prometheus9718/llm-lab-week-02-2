"""Propose editable section anchors from extracted PDF bookmarks or fonts.

Run 03_extract_pdf.py first. Review the resulting boundaries.json alongside
lines.txt and the original PDF; this script never overwrites an existing review.
"""

import argparse
from collections import Counter

from lab_common import add_pdf_argument, doc_dir, load_json, write_json
from section_engine import plan_sections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_pdf_argument(parser)
    args = parser.parse_args()
    output_dir = doc_dir(args.pdf)
    document_path = output_dir / "document.json"
    if not document_path.exists():
        raise SystemExit("Error: document.json is missing. Run 03_extract_pdf.py for this PDF first.")
    try:
        document = load_json(document_path)
        plan = plan_sections(document)
        proposed_path = output_dir / "boundaries.proposed.json"
        review_path = output_dir / "boundaries.json"
        write_json(proposed_path, plan)
        created_review = not review_path.exists()
        if created_review:
            write_json(review_path, plan)
        counts = Counter(boundary["status"] for boundary in plan["boundaries"])
        report = {
            "document_id": plan["document_id"],
            "source_file": plan["source_file"],
            "mode": plan["mode"],
            "body_font_size": plan["body_font_size"],
            "boundaries": len(plan["boundaries"]),
            "status_counts": dict(counts),
            "warnings": plan["warnings"],
            "review_created": created_review,
        }
        write_json(output_dir / "section-plan-report.json", report)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"Error: {error}") from None
    print(f"Mode: {plan['mode']}; estimated body font: {plan['body_font_size']:.1f} pt")
    print(f"Boundaries: {len(plan['boundaries'])}; accepted: {counts['accepted']}; unresolved: {counts['unresolved']}")
    print(f"Proposed plan: {proposed_path}")
    print(f"Review file: {review_path}")
    if not created_review:
        print("Existing boundaries.json kept. Compare it with the new proposed plan if needed.")
    for warning in plan["warnings"]:
        print(f"Warning: {warning}")
    print("Review boundaries.json, resolve or skip uncertain entries, then set reviewed to true.")


if __name__ == "__main__":
    main()
