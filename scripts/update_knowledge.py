#!/usr/bin/env python3
"""Synchronize all configured sources and rebuild the SchulLia index."""

from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

from build_index import PARSER_VERSION


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-age-hours", type=float, default=0)
    parser.add_argument("--metadata-only-binary", action="store_true")
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_index_metadata(corpus: Path) -> dict[str, str] | None:
    paths = {
        "corpus_sources_sha256": corpus / "sources.json",
        "corpus_files_sha256": corpus / "files.jsonl",
        "taxonomy_sha256": SKILL_DIR / "references" / "operator-taxonomy.json",
        "source_config_sha256": SKILL_DIR / "references" / "sources.json",
    }
    if any(not path.exists() for path in paths.values()):
        return None
    return {
        "parser_version": PARSER_VERSION,
        **{key: file_sha256(path) for key, path in paths.items()},
    }


def index_is_current(corpus: Path) -> bool:
    index_path = corpus / "index.sqlite"
    expected = expected_index_metadata(corpus)
    if not index_path.exists() or expected is None:
        return False
    try:
        with closing(sqlite3.connect(index_path)) as connection:
            actual = dict(connection.execute("SELECT key,value FROM meta"))
    except (sqlite3.Error, OSError):
        return False
    return all(actual.get(key) == value for key, value in expected.items())


def main() -> int:
    args = parse_args()
    sync_command = [sys.executable, str(SCRIPT_DIR / "sync_sources.py")]
    if args.force:
        sync_command.append("--force")
    if args.max_age_hours:
        sync_command.extend(["--max-age-hours", str(args.max_age_hours)])
    if args.metadata_only_binary:
        sync_command.append("--metadata-only-binary")
    sync_result = subprocess.run(sync_command, check=False)
    if sync_result.returncode not in {0, 2}:
        return sync_result.returncode
    corpus = SCRIPT_DIR.parent / "corpus"
    report_path = corpus / "sync-report.json"
    report = {}
    if report_path.exists():
        with report_path.open("r", encoding="utf-8-sig") as handle:
            report = json.load(handle)
    if not report.get("changed") and index_is_current(corpus):
        print("Index remains current; rebuild skipped")
        return sync_result.returncode
    build_result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "build_index.py")], check=False
    )
    if build_result.returncode:
        return build_result.returncode
    return sync_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
