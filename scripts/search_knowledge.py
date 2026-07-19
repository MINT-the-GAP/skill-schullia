#!/usr/bin/env python3
"""Search and inspect the local SchulLia knowledge index."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CORPUS = SKILL_DIR / "corpus"
VALID_TYPES = {"document", "task", "quiz", "macro", "operator"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def parse_json(value: str | None, default: Any) -> Any:
    return json.loads(value) if value else default


def fts_query(value: str) -> str:
    tokens = re.findall(r"[^\W_]+", value, flags=re.UNICODE)
    return " AND ".join('"' + token.replace('"', '""') + '"' for token in tokens)


def open_index(corpus: Path) -> sqlite3.Connection:
    index = corpus / "index.sqlite"
    if not index.exists():
        raise FileNotFoundError(index)
    connection = sqlite3.connect(str(index))
    connection.execute("PRAGMA query_only = ON")
    connection.row_factory = sqlite3.Row
    return connection


def table_counts(connection: sqlite3.Connection) -> dict[str, int]:
    return {
        table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        for table in ("sources", "documents", "tasks", "quizzes", "macros", "operators", "operator_occurrences")
    }


def command_status(args: argparse.Namespace) -> int:
    corpus = args.corpus.resolve()
    report = load_json(corpus / "sync-report.json", {})
    state = load_json(corpus / "state.json", {})
    result: dict[str, Any] = {
        "corpus": str(corpus),
        "index_exists": (corpus / "index.sqlite").exists(),
        "last_sync": report.get("finished_at"),
        "sync_warnings": report.get("warnings", []),
        "sync_failures": report.get("failures", []),
        "source_states": {},
        "counts": {},
    }
    for source_state in state.get("sources", {}).values():
        key = source_state.get("state", "unknown")
        result["source_states"][key] = result["source_states"].get(key, 0) + 1
    if result["index_exists"]:
        with open_index(corpus) as connection:
            result["counts"] = table_counts(connection)
            result["fts_available"] = connection.execute(
                "SELECT value FROM meta WHERE key='fts_available'"
            ).fetchone()[0] == "1"
            result["parser_version"] = connection.execute(
                "SELECT value FROM meta WHERE key='parser_version'"
            ).fetchone()[0]
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Corpus: {result['corpus']}")
        print(f"Last sync: {result['last_sync'] or 'never'}")
        print("Sources: " + (", ".join(f"{key}={value}" for key, value in sorted(result["source_states"].items())) or "none"))
        print("Index: " + (", ".join(f"{key}={value}" for key, value in result["counts"].items()) or "missing"))
        if result["sync_failures"]:
            print(f"Warning: {len(result['sync_failures'])} source sync failure(s)")
            for failure in result["sync_failures"][:5]:
                print(f"  {failure.get('source_id')}: {failure.get('error')}")
        if result["sync_warnings"]:
            print(f"Notice: {len(result['sync_warnings'])} synchronization warning(s)")
            for warning in result["sync_warnings"][:5]:
                print(f"  {warning.get('source_id')}: {warning.get('warning')}")
    return 0 if result["index_exists"] else 3


def document_for_item(connection: sqlite3.Connection, item_type: str, item_id: str) -> sqlite3.Row | None:
    if item_type == "document":
        return connection.execute("SELECT * FROM documents WHERE document_id=?", (item_id,)).fetchone()
    table_and_key = {
        "task": ("tasks", "task_id"),
        "quiz": ("quizzes", "quiz_id"),
        "macro": ("macros", "macro_id"),
    }.get(item_type)
    if not table_and_key:
        return None
    table, key = table_and_key
    row = connection.execute(f"SELECT document_id FROM {table} WHERE {key}=?", (item_id,)).fetchone()
    if not row:
        return None
    return connection.execute("SELECT * FROM documents WHERE document_id=?", (row[0],)).fetchone()


def hydrate(connection: sqlite3.Connection, item_type: str, item_id: str) -> dict[str, Any] | None:
    if item_type == "document":
        row = connection.execute(
            "SELECT document_id,source_id,path,title,document_kind,usage_context,revision_sha,"
            "content_state,local_relpath,raw_url,web_url,header_json,headings_json,parse_warnings_json "
            "FROM documents WHERE document_id=?", (item_id,)
        ).fetchone()
        if not row:
            return None
        result = dict(row)
        result["header"] = parse_json(result.pop("header_json"), {})
        result["headings"] = parse_json(result.pop("headings_json"), [])
        result["parse_warnings"] = parse_json(result.pop("parse_warnings_json"), [])
        return result
    if item_type == "task":
        row = connection.execute("SELECT * FROM tasks WHERE task_id=?", (item_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        for key in ("operator_declared_json", "operator_detected_json", "operators_json", "quiz_types_json", "macros_json", "tags_json"):
            result[key.removesuffix("_json")] = parse_json(result.pop(key), [])
        return result
    if item_type == "quiz":
        row = connection.execute("SELECT * FROM quizzes WHERE quiz_id=?", (item_id,)).fetchone()
        return dict(row) if row else None
    if item_type == "macro":
        row = connection.execute("SELECT * FROM macros WHERE macro_id=?", (item_id,)).fetchone()
        return dict(row) if row else None
    if item_type == "operator":
        operator_id = item_id.removeprefix("operator:")
        row = connection.execute(
            "SELECT o.operator_id,o.lemma,o.aliases_json,o.defined,COUNT(x.occurrence_id) AS occurrences "
            "FROM operators o LEFT JOIN operator_occurrences x ON x.operator_id=o.operator_id "
            "WHERE o.operator_id=? GROUP BY o.operator_id,o.lemma,o.aliases_json,o.defined",
            (operator_id,),
        ).fetchone()
        if not row:
            return None
        result = dict(row)
        result["aliases"] = parse_json(result.pop("aliases_json"), [])
        result["defined"] = bool(result["defined"])
        return result
    return None


def provenance(connection: sqlite3.Connection, item_type: str, item_id: str) -> dict[str, Any] | None:
    document = document_for_item(connection, item_type, item_id)
    if not document:
        return None
    source = connection.execute("SELECT * FROM sources WHERE source_id=?", (document["source_id"],)).fetchone()
    if not source:
        return None
    return {
        "source_id": source["source_id"],
        "collection": source["collection"],
        "state": source["state"],
        "owner": source["owner"],
        "repo": source["repo"],
        "configured_ref": source["configured_ref"],
        "resolved_revision": document["revision_sha"],
        "path": document["path"],
        "raw_url": document["raw_url"],
        "web_url": document["web_url"],
    }


def passes_structured_filters(details: dict[str, Any] | None, args: argparse.Namespace) -> bool:
    if not details:
        return False
    if args.usage_context and details.get("usage_context") not in args.usage_context:
        return False
    if args.operator:
        values = details.get("operator_declared", []) + details.get("operator_detected", [])
        if details.get("operator_id"):
            values.append(details["operator_id"])
        if args.operator.casefold() not in {str(value).casefold() for value in values}:
            return False
    if args.quiz_type:
        values = details.get("quiz_types", [])
        if details.get("quiz_type"):
            values.append(details["quiz_type"])
        if args.quiz_type.casefold() not in {str(value).casefold() for value in values}:
            return False
    return True


def search_rows(connection: sqlite3.Connection, args: argparse.Namespace) -> list[sqlite3.Row]:
    types = args.type or sorted(VALID_TYPES)
    for item_type in types:
        if item_type not in VALID_TYPES:
            raise ValueError(f"Unknown item type: {item_type}")
    fts_available = connection.execute(
        "SELECT value FROM meta WHERE key='fts_available'"
    ).fetchone()[0] == "1"
    query = fts_query(args.query or "")
    parameters: list[Any] = []
    where: list[str] = []
    if args.query and fts_available and not args.literal and query:
        table = "search_fts"
        where.append("search_fts MATCH ?")
        parameters.append(query)
        score = "bm25(search_fts) AS score"
        snippet = "snippet(search_fts,5,'[',']',' … ',32) AS snippet"
    else:
        table = "search_items"
        score = "0.0 AS score"
        snippet = "substr(body,1,1200) AS snippet"
        if args.query:
            where.append("(title LIKE ? OR body LIKE ? OR metadata LIKE ?)")
            like = f"%{args.query}%"
            parameters.extend([like, like, like])
    placeholders = ",".join("?" for _ in types)
    where.append(f"item_type IN ({placeholders})")
    parameters.extend(types)
    if args.source:
        where.append("source_id LIKE ?")
        parameters.append(f"%{args.source}%")
    if args.path:
        where.append("path LIKE ?")
        parameters.append(f"%{args.path}%")
    sql = (
        f"SELECT item_id,item_type,source_id,path,title,{snippet},{score} FROM {table} "
        f"WHERE {' AND '.join(where)} ORDER BY score,item_type,title LIMIT ?"
    )
    parameters.append(min(max(args.limit * 20, 100), 2000))
    return list(connection.execute(sql, parameters))


def command_search(args: argparse.Namespace) -> int:
    corpus = args.corpus.resolve()
    try:
        connection = open_index(corpus)
    except FileNotFoundError:
        print("Knowledge index is missing. Run sync_sources.py and build_index.py.", file=sys.stderr)
        return 3
    with connection:
        try:
            candidates = search_rows(connection, args)
        except (sqlite3.OperationalError, ValueError) as exc:
            print(f"Search error: {exc}", file=sys.stderr)
            return 1
        results: list[dict[str, Any]] = []
        for row in candidates:
            details = hydrate(connection, row["item_type"], row["item_id"])
            if not passes_structured_filters(details, args):
                continue
            item = {
                "item_id": row["item_id"],
                "item_type": row["item_type"],
                "source_id": row["source_id"],
                "path": row["path"],
                "title": row["title"],
                "snippet": re.sub(r"\s+", " ", row["snippet"] or "").strip(),
                "details": details,
                "provenance": provenance(connection, row["item_type"], row["item_id"]),
            }
            results.append(item)
            if len(results) >= args.limit:
                break
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if not results:
        print("No matches.")
        return 0
    used = 0
    for number, result in enumerate(results, 1):
        provenance_value = result["provenance"] or {}
        lines = ""
        details = result["details"] or {}
        if details.get("start_line"):
            lines = f":{details['start_line']}-{details.get('end_line', details['start_line'])}"
        header = f"{number}. [{result['item_type']}] {result['title']}"
        location = f"   {result.get('source_id') or '-'}  {result.get('path') or '-'}{lines}"
        snippet = f"   {result['snippet']}"
        url = f"   {provenance_value.get('web_url') or ''}" if provenance_value else ""
        block = "\n".join(part for part in (header, location, snippet, url) if part)
        if used + len(block) > args.max_chars:
            print("... output truncated by --max-chars")
            break
        print(block)
        used += len(block)
    return 0


def command_show(args: argparse.Namespace) -> int:
    corpus = args.corpus.resolve()
    try:
        connection = open_index(corpus)
    except FileNotFoundError:
        print("Knowledge index is missing.", file=sys.stderr)
        return 3
    with connection:
        item_type = args.type
        if not item_type:
            row = connection.execute("SELECT item_type FROM search_items WHERE item_id=?", (args.item_id,)).fetchone()
            if not row:
                print("Item not found.", file=sys.stderr)
                return 1
            item_type = row[0]
        details = hydrate(connection, item_type, args.item_id)
        if not details:
            print("Item not found.", file=sys.stderr)
            return 1
        result = {
            "item_id": args.item_id,
            "item_type": item_type,
            "details": details,
            "provenance": provenance(connection, item_type, args.item_id),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show corpus freshness and counts")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=command_status)

    search = subparsers.add_parser("search", help="Search documents, tasks, quizzes, macros, and operators")
    search.add_argument("query", nargs="?", default="")
    search.add_argument("--type", action="append", choices=sorted(VALID_TYPES))
    search.add_argument("--source")
    search.add_argument("--path")
    search.add_argument("--operator")
    search.add_argument("--quiz-type")
    search.add_argument("--usage-context", action="append")
    search.add_argument("--literal", action="store_true")
    search.add_argument("--limit", type=int, default=8)
    search.add_argument("--max-chars", type=int, default=12000)
    search.add_argument("--json", action="store_true")
    search.set_defaults(func=command_search)

    show = subparsers.add_parser("show", help="Show one indexed item with provenance")
    show.add_argument("item_id")
    show.add_argument("--type", choices=sorted(VALID_TYPES))
    show.set_defaults(func=command_show)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if hasattr(args, "limit"):
        args.limit = min(max(args.limit, 1), 50)
        args.max_chars = min(max(args.max_chars, 1000), 100000)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
