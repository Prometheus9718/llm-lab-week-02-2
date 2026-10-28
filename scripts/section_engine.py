"""Pure-Python section planning and construction for the PDF workshop.

The extractor supplies original text lines.  This module matches headings using
normalized copies, then slices the ORIGINAL lines at reviewed boundaries.  A
bookmark page alone is never enough to silently assign a whole page to a title.
"""

from collections import Counter, defaultdict
from itertools import groupby
import re
import unicodedata


def normalize(text):
    """Normalize a copy for matching; never use this copy as section text."""
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "")
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = text.replace("'", "").replace("_", " ")
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.casefold().split())


def title_variants(text):
    """Also allow 'Chapter 4. Title' to match a separately typeset 'Title'."""
    normalized = normalize(text)
    variants = {normalized} if normalized else set()
    without_prefix = re.sub(
        r"^(?:chapter|part|appendix)\s+(?:\d+|[ivxlcdm]+|[a-z])(?:\s+|$)",
        "",
        normalized,
    ).strip()
    if without_prefix:
        variants.add(without_prefix)
    # Some books use a descriptive bookmark "Appendix: Title" while the page
    # typesets only "Title", without an appendix letter/number.
    if normalized.startswith("appendix "):
        variants.add(normalized.removeprefix("appendix ").strip())
    return variants


def flatten_lines(document):
    """Return document-order lines and reject ambiguous source identifiers."""
    flattened = []
    seen = set()
    previous_page = 0
    for page in document.get("pages", []):
        page_number = page["pdf_page"]
        if not isinstance(page_number, int) or page_number <= previous_page:
            raise ValueError("document.json pages must have increasing PDF page numbers.")
        previous_page = page_number
        for line in page.get("lines", []):
            line_id = line.get("line_id")
            if not isinstance(line_id, str) or not line_id or line_id in seen:
                raise ValueError("Every extracted line needs a unique, nonempty line_id.")
            if line.get("pdf_page") != page_number:
                raise ValueError(f"Page mismatch for extracted line {line_id}.")
            if not isinstance(line.get("text"), str) or not line["text"].strip():
                raise ValueError(f"Extracted line {line_id} has no text.")
            seen.add(line_id)
            flattened.append({**line, "_index": len(flattened)})
    return flattened


def estimate_body_font(lines):
    """Choose a character-weighted modal font size, rather than a line mean."""
    weights = Counter()
    for line in lines:
        size = float(line.get("font_size", 0) or 0)
        if size > 0:
            weights[round(size, 1)] += max(1, len(line["text"].strip()))
    return weights.most_common(1)[0][0] if weights else 0.0


def _heading_matches(page_lines, title, body_font, destination_y=None):
    """Find exact normalized title windows, preserving wrapped-heading starts."""
    variants = title_variants(title)
    matches = []
    for start in range(len(page_lines)):
        for length in range(1, 5):
            window = page_lines[start:start + length]
            if len(window) != length:
                break
            joined = " ".join(line["text"].strip() for line in window)
            if not variants.intersection(title_variants(joined)):
                continue
            first, last = window[0], window[-1]
            size = max(float(line.get("font_size", 0) or 0) for line in window)
            bold = any(line.get("bold", False) for line in window)
            # A default bookmark often targets the page top, where a running
            # header repeats the section title. Prefer heading typography;
            # use bookmark proximity only as a small tie-breaker.
            score = (size - body_font) / max(body_font, 1.0) * 8 + int(bold)
            bbox = first.get("bbox", [0, 0, 0, 0])
            if isinstance(destination_y, (int, float)):
                score -= min(abs(float(bbox[1]) - destination_y) / 1000, 0.25)
            matches.append({
                "pdf_page": first["pdf_page"],
                "line_id": first["line_id"],
                "end_line_id": last["line_id"],
                "line_text": joined,
                "_start": first["_index"],
                "_end": last["_index"],
                "_score": score,
            })

    # A chapter label + title and the title alone can both match.  Treat
    # overlapping matches as one heading and keep the earliest original line.
    merged = []
    for match in sorted(matches, key=lambda item: (item["_start"], item["_end"])):
        if merged and match["_start"] <= merged[-1]["_end"]:
            previous = merged[-1]
            previous["_score"] = max(previous["_score"], match["_score"])
            previous["_end"] = max(previous["_end"], match["_end"])
        else:
            merged.append(dict(match))
    return sorted(merged, key=lambda item: (-item["_score"], item["_start"]))


def _public_match(match):
    return {key: value for key, value in match.items() if not key.startswith("_")}


def _font_boundaries(lines, body_font):
    """Suggest headings for a no-bookmark document; all need human review."""
    repeated = Counter(normalize(line["text"]) for line in lines)
    candidates = []
    for line in lines:
        text = line["text"].strip()
        size = float(line.get("font_size", 0) or 0)
        if not body_font or size < body_font * 1.18 or len(text) > 140:
            continue
        if len(text) < 3 or not any(character.isalpha() for character in text):
            continue
        # Running titles often repeat.  Omit them from suggestions only;
        # their source text still remains in the final section body.
        if repeated[normalize(text)] > 2:
            continue
        candidates.append(line)

    font_levels = sorted({round(float(line["font_size"]), 1) for line in candidates}, reverse=True)
    boundaries = []
    for line in candidates:
        level = min(font_levels.index(round(float(line["font_size"]), 1)) + 1, 4)
        boundaries.append({
            "level": level,
            "title": line["text"].strip(),
            "pdf_page": line["pdf_page"],
            "line_id": line["line_id"],
            "method": "font_heuristic",
            "status": "accepted",
            "note": "A font-size suggestion, not a verified semantic heading. Review before building.",
        })
    return boundaries


def plan_sections(document):
    """Create an unreviewed plan; uncertain bookmarks remain unresolved."""
    lines = flatten_lines(document)
    by_page = defaultdict(list)
    for line in lines:
        by_page[line["pdf_page"]].append(line)
    body_font = estimate_body_font(lines)
    outline = document.get("outline", [])
    boundaries = []
    warnings = []
    previous_anchor = -1

    if outline:
        mode = "bookmarks"
        for item in outline:
            target_page = item.get("pdf_page", -1)
            matches = _heading_matches(
                by_page.get(target_page, []), item["title"], body_font,
                item.get("destination_y"),
            )
            eligible = [match for match in matches if match["_start"] >= previous_anchor]
            chosen = eligible[0] if eligible else None
            ambiguous = bool(chosen and len(eligible) > 1
                             and chosen["_score"] - eligible[1]["_score"] < 0.5)
            boundary = {
                "outline_index": item.get("outline_index"),
                "level": item["level"],
                "title": item["title"],
                "pdf_page": target_page,
                "line_id": None,
                "method": "unresolved",
                "status": "unresolved",
                "note": "Choose a valid source line, or skip with an explanatory note.",
            }
            if chosen and not ambiguous:
                boundary.update({
                    "pdf_page": chosen["pdf_page"],
                    "line_id": chosen["line_id"],
                    "method": "title_match",
                    "status": "accepted",
                    "note": "Matched normalized title text on the bookmark's destination page.",
                })
                previous_anchor = chosen["_start"]
            else:
                suggestions = list(matches)
                if isinstance(target_page, int) and target_page > 0:
                    for nearby in (target_page - 1, target_page + 1):
                        suggestions.extend(_heading_matches(
                            by_page.get(nearby, []), item["title"], body_font,
                        ))
                # Nearby-page matches are review suggestions, never silent corrections.
                boundary["suggestions"] = [_public_match(match) for match in suggestions[:6]]
                if ambiguous:
                    boundary["note"] = "Several matching positions: choose the actual heading line."
                elif matches:
                    boundary["note"] = "A match precedes an earlier accepted heading; review bookmark order."
            boundaries.append(boundary)
    else:
        boundaries = _font_boundaries(lines, body_font)
        mode = "font_candidates" if boundaries else "manual"
        warnings.append("No PDF bookmarks found. Font-size candidates require visual review.")
        if not boundaries:
            warnings.append("No heading candidates found. Add manual boundaries, or keep one Document section.")

    if not lines:
        warnings.append("No extractable text lines. Inspect the PDF; scans may need OCR in a later lesson.")
    return {
        "schema_version": 1,
        "document_id": document["document_id"],
        "source_file": document["source_file"],
        "reviewed": False,
        "mode": mode,
        "body_font_size": body_font,
        "boundaries": boundaries,
        "warnings": warnings,
        "review_instructions": [
            "Review boundaries.json in VS Code alongside lines.txt and the PDF.",
            "An accepted boundary must have a valid line_id and its matching pdf_page.",
            "For a non-heading bookmark, use status skip and explain why in note.",
            "Keep boundaries in document order; same-line entries must form a parent-child chain.",
            "Set reviewed to true only after reviewing. This is a human review gate.",
            "Skipping a boundary never deletes its source text.",
        ],
    }


def _validated_boundaries(document, plan, lines):
    if plan.get("document_id") != document.get("document_id"):
        raise ValueError("boundaries.json belongs to a different PDF. Run the planner for this file.")
    if plan.get("reviewed") is not True:
        raise ValueError("Review boundaries.json, resolve its entries, then set reviewed to true.")
    positions = {line["line_id"]: line for line in lines}
    accepted = []
    skipped = 0
    previous_index = -1
    previous_level = 0
    entries = plan.get("boundaries", [])
    if not isinstance(entries, list):
        raise ValueError("boundaries must be a JSON list.")
    unresolved = [entry for entry in entries if entry.get("status") == "unresolved"]
    if unresolved:
        examples = "; ".join(str(entry.get("title", "?")) for entry in unresolved[:3])
        raise ValueError(
            f"{len(unresolved)} unresolved boundaries: {examples}. "
            "Assign a valid line and status accepted, or status skip with a note."
        )
    for number, entry in enumerate(entries, start=1):
        status = entry.get("status")
        if status == "skip":
            if not isinstance(entry.get("note"), str) or not entry["note"].strip():
                raise ValueError(f"Skipped boundary {number} needs a nonempty explanatory note.")
            skipped += 1
            continue
        if status != "accepted":
            raise ValueError(f"Boundary {number}: status must be accepted, unresolved, or skip.")
        title = entry.get("title")
        level = entry.get("level")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Boundary {number} needs a nonempty title.")
        if not isinstance(level, int) or isinstance(level, bool) or level < 1:
            raise ValueError(f"Boundary {number} needs a positive integer level.")
        line_id = entry.get("line_id")
        if line_id not in positions:
            raise ValueError(f"Boundary {number}: unknown line_id {line_id!r}; inspect lines.txt.")
        source_line = positions[line_id]
        if entry.get("pdf_page") != source_line["pdf_page"]:
            raise ValueError(f"Boundary {number}: pdf_page disagrees with line {line_id}.")
        index = source_line["_index"]
        if index < previous_index:
            raise ValueError(f"Boundary {number} is out of document order; correct or reorder boundaries.json.")
        if index == previous_index and level <= previous_level:
            raise ValueError(
                f"Boundary {number} shares a line with a sibling/ancestor. "
                "Same-line boundaries must form a parent-child chain; correct or skip the duplicate."
            )
        previous_index, previous_level = index, level
        accepted.append({**entry, "_index": index})
    return accepted, skipped


def build_sections(document, plan):
    """Slice reviewed headings without duplicating or dropping source lines."""
    lines = flatten_lines(document)
    accepted, skipped = _validated_boundaries(document, plan, lines)
    if not lines:
        raise ValueError("No extractable text lines; inspect the PDF before section building.")

    sections = []
    covered = []
    covered_characters = 0
    stack = []

    def emit(start, end, path, level, title):
        nonlocal covered_characters
        selected = lines[start:end]
        if not selected:
            return
        spans = []
        text_parts = []
        offset = 0
        for source_line in selected:
            text = source_line["text"]
            spans.append({
                "pdf_page": source_line["pdf_page"],
                "line_id": source_line["line_id"],
                "start_char": offset,
                "end_char": offset + len(text),
            })
            covered.append(source_line["line_id"])
            covered_characters += len(text)
            text_parts.append(text)
            offset += len(text) + 1  # The separator is a newline in section text.
        sections.append({
            "section_id": f"{document['document_id'][:12]}-s{len(sections) + 1:04d}",
            "document_id": document["document_id"],
            "source_file": document["source_file"],
            "heading_path": list(path),
            "level": level,
            "title": title,
            "text": "\n".join(text_parts),
            "source_spans": spans,
            "pdf_page_start": selected[0]["pdf_page"],
            "pdf_page_end": selected[-1]["pdf_page"],
        })

    groups = [(index, list(group)) for index, group in groupby(accepted, key=lambda item: item["_index"])]
    if not groups:
        emit(0, len(lines), ["Document"], 0, "Document")
    else:
        if groups[0][0] > 0:
            emit(0, groups[0][0], ["Front matter"], 0, "Front matter")
        for group_number, (start, boundaries) in enumerate(groups):
            for boundary in boundaries:
                level = boundary["level"]
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, boundary["title"].strip()))
            end = groups[group_number + 1][0] if group_number + 1 < len(groups) else len(lines)
            emit(start, end, [title for _, title in stack], stack[-1][0], stack[-1][1])

    line_counts = Counter(covered)
    expected_ids = {line["line_id"] for line in lines}
    missing = sorted(expected_ids - set(covered))
    duplicates = sorted(line_id for line_id, count in line_counts.items() if count > 1)
    if missing or duplicates or len(covered) != len(lines):
        raise ValueError("Internal coverage failure: a source line was dropped or assigned more than once.")
    input_characters = sum(len(line["text"]) for line in lines)
    if input_characters != covered_characters:
        raise ValueError("Internal coverage failure: original line characters were changed.")
    report = {
        "schema_version": 1,
        "document_id": document["document_id"],
        "source_file": document["source_file"],
        "mode": plan.get("mode", "manual"),
        "sections": len(sections),
        "accepted_boundaries": len(accepted),
        "skipped_boundaries": skipped,
        "same_line_parent_child_groups": sum(len(group) > 1 for _, group in groups),
        "input_lines": len(lines),
        "assigned_lines": len(covered),
        "unique_assigned_lines": len(line_counts),
        "input_line_characters": input_characters,
        "assigned_line_characters": covered_characters,
        "missing_line_ids": missing,
        "duplicate_line_ids": duplicates,
        "all_lines_assigned_once": True,
        "note": "Line characters are preserved exactly; section text joins source lines with newlines.",
    }
    return sections, report
