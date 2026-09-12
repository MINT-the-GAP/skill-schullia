#!/usr/bin/env python3
"""Read-only template discovery, header inventory and review-drift check.

No source code from corpus/ is imported or executed. Header declarations are
discovery evidence, not a whitelist of public APIs or parsed option signatures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MACRO = re.compile(r"^@([A-Za-z_][\w.-]*)(?:[ \t]*(:).*)?$")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+)$")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def is_template(source: dict) -> bool:
    return source.get("collection") == "template-reference" or (
        source.get("owner", "").casefold() == "mint-the-gap"
        and source.get("repo", "").casefold().startswith("lia-")
    )


def stored_path(corpus: Path, value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe corpus path: {value}")
    root = corpus.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path outside corpus: {value}")
    return path


def inspect_readme(text: str) -> dict:
    """Collect declarations outside macro bodies; never infer publicness."""
    lines = text.splitlines()
    declarations = []
    in_block = False
    header_end = 0
    start = len(text) - len(text.lstrip("\ufeff \t\r\n"))
    metadata_keys = {
        "attribute", "author", "classroom", "comment", "dark", "date", "edit",
        "email", "font", "formula", "icon", "import", "language", "link", "logo",
        "mode", "narrator", "persistent", "repository", "script", "sharing",
        "tags", "translatewithgoogle", "translation", "version",
    }
    if text.startswith("<!--", start):
        start_line = text[:start].count("\n")
        header_end = len(lines)
        for index in range(start_line, len(lines)):
            stripped = lines[index].strip()
            if index == start_line:
                stripped = stripped.removeprefix("\ufeff").lstrip()[4:].strip()
            if in_block:
                if stripped == "@end":
                    in_block = False
                continue
            match = MACRO.fullmatch(stripped)
            if match and match[1] != "end":
                declarations.append({"name": match[1], "line": index + 1,
                                     "form": "inline" if match[2] else "block"})
                in_block = not bool(match[2])
                continue
            # Legacy LiaScript definitions omit @, e.g. TextmarkerQuiz: ...
            legacy = re.match(r"^([A-Za-z_][\w.-]*):[ \t]*(.*)$", stripped)
            if legacy and legacy[1].casefold() not in metadata_keys:
                declarations.append({"name": legacy[1], "line": index + 1,
                                     "form": "legacy_inline"})
                continue
            if "-->" in stripped:
                header_end = index + 1
                break
    sections = []
    fence = None
    for number, line in enumerate(lines[header_end:], header_end + 1):
        marker = re.match(r"^\s*(\x60{3,}|~{3,})", line)
        if marker:
            run = marker[1]
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        match = HEADING.match(line)
        if match:
            sections.append({"heading": match[2], "line": number})
    return {"header_declarations": declarations, "documentation_sections": sections,
            "unterminated_macro_block": in_block}


def inventory(corpus: Path, catalog: dict, reference_root: Path) -> tuple[list, list]:
    sources = read_json(corpus / "sources.json")
    files = [json.loads(line) for line in
             (corpus / "files.jsonl").read_text(encoding="utf-8-sig").splitlines()
             if line.strip()]
    reviews = {item["source_id"]: item for item in catalog["templates"]}
    issues = []
    if len(reviews) != len(catalog["templates"]):
        issues.append("Duplicate source_id in template catalog")
    readmes = {(item["source_id"], item["path"].casefold()): item
               for item in files if item.get("stored") and item.get("is_text")}
    output = []
    discovered = set()
    for source in sorted(filter(is_template, sources), key=lambda s: s["source_id"]):
        source_id = source["source_id"]
        discovered.add(source_id)
        review = reviews.get(source_id)
        record = readmes.get((source_id, "readme.md"))
        row = {"source_id": source_id, "repo": source["repo"],
               "revision_sha": source.get("revision_sha"), "state": source.get("state"),
               "reference": review.get("reference") if review else None,
               "review_status": "current"}
        reasons = []
        if not review:
            reasons.append("new_template")
        if source.get("state") != "current":
            reasons.append("source_not_current")
        if not record:
            reasons.append("missing_readme")
        else:
            path = stored_path(corpus, record["local_relpath"])
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            row.update({"local_readme": str(path), "readme_sha256": digest,
                        "web_url": record.get("web_url")})
            if digest != record.get("content_sha256"):
                reasons.append("readme_manifest_hash_mismatch")
            if record.get("revision_sha") != source.get("revision_sha"):
                reasons.append("readme_source_revision_mismatch")
            row.update(inspect_readme(data.decode("utf-8-sig")))
            if row["unterminated_macro_block"]:
                reasons.append("unterminated_macro_block")
            if review and digest != review.get("readme_sha256"):
                reasons.append("readme_changed")
        if review:
            if source.get("revision_sha") != review.get("reviewed_revision"):
                reasons.append("revision_changed")
            reference = stored_path(reference_root, review["reference"])
            if not reference.is_file():
                reasons.append("missing_reference")
        if reasons:
            row["review_status"] = ",".join(reasons)
            issues.append(f"{source_id}: {row['review_status']}")
        output.append(row)
    for missing in sorted(set(reviews) - discovered):
        issues.append(f"{missing}: reviewed_template_missing_from_corpus")
    return output, issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=ROOT / "corpus")
    parser.add_argument("--catalog", type=Path, default=ROOT / "references/template-catalog.json")
    parser.add_argument("--source", help="Case-insensitive repository or source-id substring")
    parser.add_argument("--json", action="store_true", help="Include declarations and section locations")
    parser.add_argument("--check", action="store_true", help="Exit 1 on missing/stale review coverage")
    args = parser.parse_args()
    try:
        rows, issues = inventory(args.corpus, read_json(args.catalog), args.catalog.parent)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Cannot inspect template corpus: {exc}", file=sys.stderr)
        return 2
    selected = [row for row in rows if not args.source or args.source.casefold() in
                (row["source_id"] + " " + row["repo"]).casefold()]
    if args.source and not selected:
        print(f"No template matches: {args.source}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"templates": selected, "issues": issues}, ensure_ascii=False, indent=2))
    else:
        for row in selected:
            count = len(row.get("header_declarations", []))
            print(f"{row['repo']}: {count} header declarations; "
                  f"{row['review_status']}; {row['reference'] or 'no reference'}")
        print(f"Templates: {len(rows)}, review issues: {len(issues)}")
        for issue in issues:
            print(f"REVIEW {issue}")
    return 1 if args.check and issues else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
