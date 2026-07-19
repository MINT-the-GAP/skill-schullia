#!/usr/bin/env python3
"""Validate synchronized SchulLia snapshots, provenance, hashes, and SQLite integrity."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CORPUS = SKILL_DIR / "corpus"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def load_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--deep", action="store_true", help="Rehash every stored file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    corpus = args.corpus.resolve()
    required = ["sources.json", "files.jsonl", "index.sqlite", "sync-report.json"]
    missing = [name for name in required if not (corpus / name).exists()]
    if missing:
        print("Missing corpus artifacts: " + ", ".join(missing), file=sys.stderr)
        return 3

    errors: list[str] = []
    warnings: list[str] = []
    sources = load_json(corpus / "sources.json")
    source_ids = [source["source_id"] for source in sources]
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate source_id in sources.json")
    configured = load_json(SKILL_DIR / "references" / "sources.json")
    configured_files = {item["id"] for item in configured.get("files", [])}
    absent_fixed = sorted(configured_files.difference(source_ids))
    if absent_fixed:
        errors.append("missing configured fixed sources: " + ", ".join(absent_fixed))

    file_count = 0
    for record in read_jsonl(corpus / "files.jsonl"):
        file_count += 1
        if record.get("source_id") not in source_ids:
            errors.append(f"file references unknown source: {record.get('source_id')}:{record.get('path')}")
        path = record.get("path", "")
        if not path or path.startswith(("/", "\\")) or ".." in Path(path).parts:
            errors.append(f"unsafe manifest path: {path}")
        if record.get("stored"):
            local = corpus / Path(record["local_relpath"])
            if not local.exists():
                errors.append(f"stored file is missing: {record['local_relpath']}")
            elif args.deep:
                data = local.read_bytes()
                if hashlib.sha256(data).hexdigest() != record.get("content_sha256"):
                    errors.append(f"SHA-256 mismatch: {record['local_relpath']}")
                if git_blob_sha1(data) != record.get("git_blob_sha1"):
                    errors.append(f"Git blob SHA mismatch: {record['local_relpath']}")
        if record.get("lfs_pointer"):
            warnings.append(f"Git LFS pointer without object bytes: {record['source_id']}:{path}")

    connection = sqlite3.connect(str(corpus / "index.sqlite"))
    connection.execute("PRAGMA query_only = ON")
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            errors.append(f"SQLite integrity: {integrity}")
        indexed_sources = connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        indexed_documents = connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        broken_tasks = connection.execute(
            "SELECT COUNT(*) FROM tasks t LEFT JOIN documents d ON d.document_id=t.document_id "
            "WHERE d.document_id IS NULL OR t.start_line<1 OR t.end_line<t.start_line"
        ).fetchone()[0]
        broken_quizzes = connection.execute(
            "SELECT COUNT(*) FROM quizzes q LEFT JOIN documents d ON d.document_id=q.document_id "
            "WHERE d.document_id IS NULL OR q.start_line<1 OR q.end_line<q.start_line"
        ).fetchone()[0]
        if broken_tasks:
            errors.append(f"invalid task records: {broken_tasks}")
        if broken_quizzes:
            errors.append(f"invalid quiz records: {broken_quizzes}")
        if indexed_sources != len(sources):
            errors.append(f"source count mismatch: index={indexed_sources}, manifest={len(sources)}")
        if indexed_documents != file_count:
            errors.append(f"document count mismatch: index={indexed_documents}, manifest={file_count}")
    finally:
        connection.close()

    for warning in warnings[:20]:
        print("WARNING " + warning)
    if len(warnings) > 20:
        print(f"WARNING ... and {len(warnings) - 20} more")
    if errors:
        for error in errors:
            print("ERROR " + error, file=sys.stderr)
        return 1
    print(
        f"Corpus valid: {len(sources)} sources, {file_count} files, "
        f"deep_hashes={'yes' if args.deep else 'no'}, warnings={len(warnings)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
