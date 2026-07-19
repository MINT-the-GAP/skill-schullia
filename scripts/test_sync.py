#!/usr/bin/env python3
"""Dependency-free regression tests for source synchronization decisions."""

from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import tempfile

import sync_sources as sync
import update_knowledge as update


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_freshness_requires_matching_configuration() -> None:
    with tempfile.TemporaryDirectory() as directory:
        corpus = Path(directory)
        configuration = {"schema_version": 1, "files": [{"id": "one"}]}
        digest = sync.config_sha256(configuration)
        write_json(corpus / "state.json", {"config_sha256": digest})
        write_json(
            corpus / "sync-report.json",
            {
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "failures": [],
            },
        )

        assert sync.last_run_is_fresh(corpus, 24, digest)
        assert not sync.last_run_is_fresh(corpus, 24, "changed-configuration")


def test_index_freshness_uses_content_hashes() -> None:
    with tempfile.TemporaryDirectory() as directory:
        corpus = Path(directory)
        write_json(corpus / "sources.json", [])
        (corpus / "files.jsonl").write_text("", encoding="utf-8")
        expected = update.expected_index_metadata(corpus)
        assert expected is not None
        with closing(sqlite3.connect(corpus / "index.sqlite")) as connection:
            connection.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
            connection.executemany(
                "INSERT INTO meta VALUES (?,?)", expected.items()
            )
            connection.commit()

        assert update.index_is_current(corpus)
        (corpus / "files.jsonl").write_text("{}\n", encoding="utf-8")
        assert not update.index_is_current(corpus)


def main() -> int:
    test_freshness_requires_matching_configuration()
    test_index_freshness_uses_content_hashes()
    print("Sync tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
