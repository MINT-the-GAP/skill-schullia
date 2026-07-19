#!/usr/bin/env python3
"""Build a deterministic SQLite/JSONL index from the synchronized SchulLia corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CORPUS = SKILL_DIR / "corpus"
DEFAULT_TAXONOMY = SKILL_DIR / "references" / "operator-taxonomy.json"
PARSER_VERSION = "3"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HEADER_KEYS = {
    "attribute", "author", "classroom", "comment", "dark", "date", "edit",
    "email", "font", "formula", "icon", "import", "language", "link", "logo",
    "mode", "narrator", "onload", "persistent", "repository", "script",
    "sharing", "style", "tags", "translatewithgoogle", "translation", "version",
}
MULTI_HEADER_KEYS = {
    "attribute", "author", "formula", "import", "link", "script", "translation",
}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"(?ms)^\s*(```|~~~).*?^\s*\1\s*$")
SCRIPT_RE = re.compile(r"(?is)<script\b[^>]*>.*?</script\s*>")
STYLE_RE = re.compile(r"(?is)<style\b[^>]*>.*?</style\s*>")
ONLOAD_RE = re.compile(r"(?ms)^\s*@onload\b.*?^\s*@end\b")
HTML_COMMENT_RE = re.compile(r"(?s)<!--.*?-->")
INLINE_QUIZ_RE = re.compile(r"\[\[(.*?)\]\]")
RADIO_RE = re.compile(r"\[\(\s*([Xx ])\s*\)\]")
MULTIPLE_RE = re.compile(r"\[\[\s*([Xx ])\s*\]\]")
DRAG_RE = re.compile(r"\[->\[")
MACRO_RE = re.compile(
    r"(?<![\w@])@([A-Za-z_][\w.-]*)(?=\s*(?:\(|\[|`|$))",
    re.MULTILINE,
)
BOLD_WORD_RE = re.compile(r"^\s*(?:[-*+]\s+)?(?:__\$?[^_]+__\s*)?\*\*([A-ZÄÖÜ][A-Za-zÄÖÜäöüß-]+)\*\*")
MARKDOWN_RE = re.compile(r"[*_`~]+")
HTML_TAG_RE = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class OperatorDefinition:
    operator_id: str
    lemma: str
    aliases: tuple[str, ...]
    patterns: tuple[re.Pattern[str], ...]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def stable_id(*parts: Any) -> str:
    payload = "\0".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def json_compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_jsonl_atomic(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        for record in records:
            handle.write(json_compact(record))
            handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def decode_text(data: bytes) -> tuple[str | None, str | None]:
    encodings = ["utf-8-sig"]
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        encodings.insert(0, "utf-16")
    encodings.append("cp1252")
    for encoding in encodings:
        try:
            return data.decode(encoding).replace("\r\n", "\n").replace("\r", "\n"), encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None, None


def mask_match(text: str, match: re.Match[str]) -> str:
    value = match.group(0)
    return "".join("\n" if character == "\n" else " " for character in value)


def mask_regex(text: str, pattern: re.Pattern[str]) -> str:
    return pattern.sub(lambda match: mask_match(text, match), text)


def strip_markup(value: str) -> str:
    value = HTML_TAG_RE.sub(" ", value)
    value = MARKDOWN_RE.sub("", value)
    value = re.sub(r"\\$", "", value)
    return re.sub(r"\s+", " ", value).strip()


def extract_header(text: str) -> tuple[dict[str, Any], int, list[str]]:
    warnings: list[str] = []
    start = len(text) - len(text.lstrip("\ufeff \t\n"))
    if not text.startswith("<!--", start):
        return {}, 0, warnings
    end = text.find("-->", start + 4)
    if end < 0:
        warnings.append("unterminated_header_comment")
        return {}, 0, warnings
    raw = text[start + 4:end]
    scalars: dict[str, str] = {}
    lists: dict[str, list[str]] = {key: [] for key in MULTI_HEADER_KEYS}
    macro_definitions: list[str] = []
    last_key: str | None = None
    for raw_line in raw.splitlines():
        line = raw_line.rstrip()
        macro_match = re.match(r"^\s*@([A-Za-z_][\w.-]*)\b", line)
        if macro_match:
            macro_definitions.append(macro_match.group(1))
        match = re.match(r"^\s*([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if match:
            key = match.group(1).casefold()
            value = match.group(2)
            last_key = key if key in HEADER_KEYS else None
            if key in MULTI_HEADER_KEYS:
                if value:
                    lists[key].append(value)
            elif key in HEADER_KEYS:
                if key in scalars:
                    warnings.append(f"duplicate_header_key:{key}")
                scalars[key] = value
            elif (match.group(1).endswith("Quiz") or any(character.isupper() for character in match.group(1)[1:])) and not value:
                macro_definitions.append(match.group(1))
            continue
        continuation = line.strip()
        if continuation and raw_line[:1].isspace() and last_key:
            if last_key in MULTI_HEADER_KEYS and lists.get(last_key):
                separator = ""
                if not (
                    lists[last_key][-1].startswith(("http://", "https://"))
                    and not re.search(r"[{}();]", continuation)
                ):
                    separator = "\n"
                lists[last_key][-1] += separator + continuation
                continue
            if last_key in scalars:
                scalars[last_key] += "\n" + continuation
                continue
        last_key = None
    header: dict[str, Any] = {
        "raw": raw,
        "scalars": scalars,
        "macro_definitions": sorted(set(macro_definitions)),
    }
    for key, values in lists.items():
        if values:
            header[key + "s"] = values
    tags_raw = scalars.get("tags", "")
    header["tags"] = [item.strip() for item in tags_raw.split(",") if item.strip()]
    return header, end + 3, warnings


def load_taxonomy(path: Path) -> tuple[list[OperatorDefinition], dict[str, OperatorDefinition]]:
    document = load_json(path)
    definitions: list[OperatorDefinition] = []
    aliases: dict[str, OperatorDefinition] = {}
    for entry in document["operators"]:
        try:
            patterns = tuple(re.compile(pattern, re.IGNORECASE) for pattern in entry["prompt_patterns"])
        except re.error as exc:
            raise ValueError(f"Invalid operator pattern for {entry['id']}: {exc}") from exc
        definition = OperatorDefinition(
            operator_id=entry["id"],
            lemma=entry["lemma"],
            aliases=tuple(entry.get("aliases", [])),
            patterns=patterns,
        )
        definitions.append(definition)
        for value in (definition.operator_id, definition.lemma, *definition.aliases):
            aliases[value.casefold()] = definition
    return definitions, aliases


def detected_operators(text: str, definitions: list[OperatorDefinition]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    occupied: set[tuple[str, int, int]] = set()
    for definition in definitions:
        for pattern in definition.patterns:
            for match in pattern.finditer(text):
                key = (definition.operator_id, match.start(), match.end())
                if key in occupied:
                    continue
                occupied.add(key)
                results.append({
                    "operator_id": definition.operator_id,
                    "lemma": definition.lemma,
                    "surface": match.group(0),
                    "method": "body_pattern",
                    "confidence": 0.9,
                    "start": match.start(),
                    "end": match.end(),
                })
    results.sort(key=lambda item: (item["start"], item["operator_id"]))
    return results


def declared_operators(tags: list[str], aliases: dict[str, OperatorDefinition]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for tag in tags:
        definition = aliases.get(tag.casefold())
        if definition:
            found.append({
                "operator_id": definition.operator_id,
                "lemma": definition.lemma,
                "surface": tag,
                "method": "metadata_tag",
                "confidence": 1.0,
            })
    return found


def line_offsets(text: str) -> list[int]:
    offsets = [0]
    for match in re.finditer("\n", text):
        offsets.append(match.end())
    return offsets


def offset_to_line(offsets: list[int], offset: int) -> int:
    import bisect
    return bisect.bisect_right(offsets, offset)


def extract_headings(live_text: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for line_number, line in enumerate(live_text.splitlines(), 1):
        match = HEADING_RE.match(line)
        if match:
            headings.append({
                "level": len(match.group(1)),
                "text": strip_markup(match.group(2)),
                "line": line_number,
            })
    return headings


def title_from_headings(headings: list[dict[str, Any]], path: str) -> str:
    for heading in headings:
        if heading["level"] == 1:
            return heading["text"]
    return Path(path).stem


def quiz_type_for_match(content: str, line: str) -> str:
    stripped = content.strip()
    if stripped == "!":
        return "generic_script"
    if stripped == "?":
        return "hint"
    if stripped in {"X", "x", ""} and re.match(r"^\s*(?:[-*+]\s+)?\[\[", line):
        return "multiple_choice"
    if "|" in content:
        return "inline_selection"
    if re.fullmatch(r"_+(?:\s+_+)*", stripped):
        return "text_input_placeholder"
    return "text_input"


def extract_quizzes(live_text: str, document_id: str, usage_context: str) -> list[dict[str, Any]]:
    quizzes: list[dict[str, Any]] = []
    offsets = line_offsets(live_text)
    ordinal = 0
    for line_number, line in enumerate(live_text.splitlines(), 1):
        matrix_line = line.lstrip().startswith("|")
        for match in RADIO_RE.finditer(line):
            ordinal += 1
            quiz_type = "matrix" if matrix_line else "single_choice"
            quizzes.append({
                "quiz_id": stable_id(document_id, "quiz", line_number, match.start(), ordinal),
                "document_id": document_id,
                "ordinal": ordinal,
                "start_line": line_number,
                "end_line": line_number,
                "start_char": offsets[line_number - 1] + match.start(),
                "end_char": offsets[line_number - 1] + match.end(),
                "syntax": "radio",
                "quiz_type": quiz_type,
                "usage_context": usage_context,
                "raw_text": match.group(0),
            })
        for match in INLINE_QUIZ_RE.finditer(line):
            if RADIO_RE.fullmatch(match.group(0)):
                continue
            ordinal += 1
            quiz_type = quiz_type_for_match(match.group(1), line)
            if matrix_line and quiz_type in {"multiple_choice", "inline_selection", "text_input"}:
                quiz_type = "matrix"
            quizzes.append({
                "quiz_id": stable_id(document_id, "quiz", line_number, match.start(), ordinal),
                "document_id": document_id,
                "ordinal": ordinal,
                "start_line": line_number,
                "end_line": line_number,
                "start_char": offsets[line_number - 1] + match.start(),
                "end_char": offsets[line_number - 1] + match.end(),
                "syntax": "double_bracket",
                "quiz_type": quiz_type,
                "usage_context": usage_context,
                "raw_text": match.group(0),
            })
        for match in DRAG_RE.finditer(line):
            ordinal += 1
            quizzes.append({
                "quiz_id": stable_id(document_id, "quiz", line_number, match.start(), ordinal),
                "document_id": document_id,
                "ordinal": ordinal,
                "start_line": line_number,
                "end_line": line_number,
                "start_char": offsets[line_number - 1] + match.start(),
                "end_char": offsets[line_number - 1] + match.end(),
                "syntax": "drag_marker",
                "quiz_type": "drag_drop",
                "usage_context": usage_context,
                "raw_text": line[match.start(): min(len(line), match.start() + 240)],
            })
    return quizzes


def extract_macros(text: str, document_id: str, usage_context: str, header_end: int) -> list[dict[str, Any]]:
    macros: list[dict[str, Any]] = []
    offsets = line_offsets(text)
    seen: set[tuple[int, int, str]] = set()
    for match in MACRO_RE.finditer(text):
        name = match.group(1)
        if name.casefold() in {"end", "input", "output", "onload", "style"}:
            continue
        line_number = offset_to_line(offsets, match.start())
        context = "definition" if match.start() < header_end else usage_context
        key = (line_number, match.start(), name)
        if key in seen:
            continue
        seen.add(key)
        macros.append({
            "macro_id": stable_id(document_id, "macro", match.start(), name),
            "document_id": document_id,
            "name": name,
            "start_line": line_number,
            "start_char": match.start(),
            "usage_context": context,
            "raw_text": match.group(0),
        })
    return macros


def heading_for_line(headings: list[dict[str, Any]], line_number: int) -> str | None:
    stack: list[dict[str, Any]] = []
    for heading in headings:
        if heading["line"] > line_number:
            break
        while stack and stack[-1]["level"] >= heading["level"]:
            stack.pop()
        stack.append(heading)
    return " > ".join(item["text"] for item in stack) if stack else None


def extract_tasks(
    live_text: str,
    document_id: str,
    headings: list[dict[str, Any]],
    quizzes: list[dict[str, Any]],
    macros: list[dict[str, Any]],
    definitions: list[OperatorDefinition],
    declared: list[dict[str, Any]],
    tags: list[str],
    usage_context: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    lines = live_text.splitlines()
    candidates: list[dict[str, Any]] = []
    warnings: list[str] = []
    for line_number, line in enumerate(lines, 1):
        plain = strip_markup(line)
        if not plain or len(plain) > 700:
            continue
        detected = detected_operators(plain, definitions)
        bold = BOLD_WORD_RE.match(line)
        if not detected and bold:
            detected = [{
                "operator_id": bold.group(1).casefold(),
                "lemma": bold.group(1).casefold(),
                "surface": bold.group(1),
                "method": "bold_imperative_candidate",
                "confidence": 0.45,
                "start": 0,
                "end": len(bold.group(1)),
            }]
        if detected:
            candidates.append({"line": line_number, "prompt": plain, "operators": detected})

    tasks: list[dict[str, Any]] = []
    occurrences: list[dict[str, Any]] = []
    heading_lines = {heading["line"] for heading in headings}
    for ordinal, candidate in enumerate(candidates, 1):
        start_line = candidate["line"]
        next_candidate = candidates[ordinal]["line"] if ordinal < len(candidates) else len(lines) + 1
        end_line = min(next_candidate - 1, start_line + 199, len(lines))
        for possible_end in range(start_line + 1, min(end_line, len(lines)) + 1):
            if possible_end in heading_lines:
                end_line = possible_end - 1
                break
        task_quizzes = [q for q in quizzes if start_line <= q["start_line"] <= end_line]
        task_macros = [m for m in macros if start_line <= m["start_line"] <= end_line and m["usage_context"] != "definition"]
        quiz_types = sorted({item["quiz_type"] for item in task_quizzes})
        if not quiz_types:
            task_type = "open_response"
        elif len(quiz_types) == 1:
            task_type = quiz_types[0]
        else:
            task_type = "mixed"
        detected_ids = [item["operator_id"] for item in candidate["operators"]]
        declared_ids = [item["operator_id"] for item in declared]
        if declared_ids and detected_ids and not set(declared_ids).intersection(detected_ids):
            warnings.append(f"operator_mismatch:line={start_line}:declared={','.join(declared_ids)}:body={','.join(detected_ids)}")
        combined: list[dict[str, Any]] = []
        for item in declared:
            combined.append({**item, "role": "declared"})
        for item in candidate["operators"]:
            combined.append({**item, "role": "detected"})
        raw_text = "\n".join(lines[start_line - 1:end_line]).strip()
        task_id = stable_id(document_id, "task", start_line, candidate["prompt"])
        task = {
            "task_id": task_id,
            "document_id": document_id,
            "ordinal": ordinal,
            "start_line": start_line,
            "end_line": end_line,
            "heading": heading_for_line(headings, start_line),
            "prompt": candidate["prompt"],
            "operator_declared": declared_ids,
            "operator_detected": detected_ids,
            "operators": combined,
            "operator_basis": "declared_and_body" if declared and candidate["operators"] else ("declared" if declared else "body"),
            "operator_confidence": max((item["confidence"] for item in combined), default=0.0),
            "task_type": task_type,
            "quiz_types": quiz_types,
            "macros": sorted({item["name"] for item in task_macros}),
            "tags": tags,
            "usage_context": usage_context,
            "raw_text": raw_text,
        }
        tasks.append(task)
        for quiz in task_quizzes:
            quiz["task_id"] = task_id
        for occurrence_ordinal, item in enumerate(combined, 1):
            occurrence_id = stable_id(
                task_id,
                item["method"],
                item["operator_id"],
                item.get("surface"),
                item.get("start"),
                item.get("end"),
                occurrence_ordinal,
            )
            occurrences.append({
                "occurrence_id": occurrence_id,
                "operator_id": item["operator_id"],
                "document_id": document_id,
                "task_id": task_id,
                "start_line": start_line,
                "end_line": start_line,
                "surface": item.get("surface"),
                "detection_method": item["method"],
                "confidence": item["confidence"],
                "usage_context": usage_context,
                "raw_text": candidate["prompt"],
            })
    return tasks, occurrences, warnings


def create_schema(connection: sqlite3.Connection) -> bool:
    connection.executescript(
        """
        PRAGMA journal_mode = OFF;
        PRAGMA synchronous = OFF;
        PRAGMA temp_store = MEMORY;
        PRAGMA foreign_keys = ON;
        PRAGMA user_version = 1;
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE sources (
          source_id TEXT PRIMARY KEY,
          collection TEXT NOT NULL,
          source_kind TEXT NOT NULL,
          owner TEXT NOT NULL,
          repo TEXT NOT NULL,
          configured_ref TEXT,
          path TEXT,
          revision_sha TEXT NOT NULL,
          state TEXT NOT NULL,
          usage_context TEXT NOT NULL,
          web_url TEXT,
          raw_url TEXT,
          license_spdx TEXT,
          synced_at TEXT,
          metadata_json TEXT NOT NULL
        );
        CREATE TABLE documents (
          document_id TEXT PRIMARY KEY,
          source_id TEXT NOT NULL REFERENCES sources(source_id),
          path TEXT NOT NULL,
          title TEXT NOT NULL,
          document_kind TEXT NOT NULL,
          usage_context TEXT NOT NULL,
          revision_sha TEXT NOT NULL,
          git_blob_sha1 TEXT,
          content_sha256 TEXT,
          normalized_sha256 TEXT,
          size_bytes INTEGER NOT NULL,
          line_count INTEGER,
          encoding TEXT,
          content_state TEXT NOT NULL,
          local_relpath TEXT,
          raw_url TEXT,
          web_url TEXT,
          header_json TEXT NOT NULL,
          headings_json TEXT NOT NULL,
          parse_warnings_json TEXT NOT NULL,
          text TEXT,
          UNIQUE(source_id, path)
        );
        CREATE TABLE tasks (
          task_id TEXT PRIMARY KEY,
          document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
          ordinal INTEGER NOT NULL,
          start_line INTEGER NOT NULL,
          end_line INTEGER NOT NULL,
          heading TEXT,
          prompt TEXT NOT NULL,
          operator_declared_json TEXT NOT NULL,
          operator_detected_json TEXT NOT NULL,
          operators_json TEXT NOT NULL,
          operator_basis TEXT NOT NULL,
          operator_confidence REAL NOT NULL,
          task_type TEXT NOT NULL,
          quiz_types_json TEXT NOT NULL,
          macros_json TEXT NOT NULL,
          tags_json TEXT NOT NULL,
          usage_context TEXT NOT NULL,
          raw_text TEXT NOT NULL
        );
        CREATE TABLE quizzes (
          quiz_id TEXT PRIMARY KEY,
          document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
          task_id TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
          ordinal INTEGER NOT NULL,
          start_line INTEGER NOT NULL,
          end_line INTEGER NOT NULL,
          start_char INTEGER NOT NULL,
          end_char INTEGER NOT NULL,
          syntax TEXT NOT NULL,
          quiz_type TEXT NOT NULL,
          usage_context TEXT NOT NULL,
          raw_text TEXT NOT NULL
        );
        CREATE TABLE macros (
          macro_id TEXT PRIMARY KEY,
          document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
          name TEXT NOT NULL,
          start_line INTEGER NOT NULL,
          start_char INTEGER NOT NULL,
          usage_context TEXT NOT NULL,
          raw_text TEXT NOT NULL
        );
        CREATE TABLE operators (
          operator_id TEXT PRIMARY KEY,
          lemma TEXT NOT NULL,
          aliases_json TEXT NOT NULL,
          defined INTEGER NOT NULL
        );
        CREATE TABLE operator_occurrences (
          occurrence_id TEXT PRIMARY KEY,
          operator_id TEXT NOT NULL,
          document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
          task_id TEXT REFERENCES tasks(task_id) ON DELETE CASCADE,
          start_line INTEGER NOT NULL,
          end_line INTEGER NOT NULL,
          surface TEXT,
          detection_method TEXT NOT NULL,
          confidence REAL NOT NULL,
          usage_context TEXT NOT NULL,
          raw_text TEXT NOT NULL
        );
        CREATE TABLE search_items (
          item_id TEXT PRIMARY KEY,
          item_type TEXT NOT NULL,
          source_id TEXT,
          path TEXT,
          title TEXT NOT NULL,
          body TEXT NOT NULL,
          metadata TEXT NOT NULL
        );
        CREATE INDEX idx_documents_source_path ON documents(source_id, path);
        CREATE INDEX idx_tasks_type ON tasks(task_type);
        CREATE INDEX idx_quizzes_type ON quizzes(quiz_type);
        CREATE INDEX idx_macros_name ON macros(name);
        CREATE INDEX idx_occurrences_operator ON operator_occurrences(operator_id);
        """
    )
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE search_fts USING fts5("
            "item_id UNINDEXED, item_type UNINDEXED, source_id UNINDEXED, path UNINDEXED, "
            "title, body, metadata, tokenize='unicode61 remove_diacritics 2')"
        )
        return True
    except sqlite3.OperationalError:
        return False


def add_search_item(
    connection: sqlite3.Connection,
    fts_available: bool,
    item_id: str,
    item_type: str,
    source_id: str | None,
    path: str | None,
    title: str,
    body: str,
    metadata: str,
) -> None:
    values = (item_id, item_type, source_id, path, title, body, metadata)
    connection.execute("INSERT INTO search_items VALUES (?,?,?,?,?,?,?)", values)
    if fts_available:
        connection.execute("INSERT INTO search_fts VALUES (?,?,?,?,?,?,?)", values)


def provenance(document: dict[str, Any], source: dict[str, Any], lines: tuple[int, int] | None = None) -> dict[str, Any]:
    result = {
        "source_id": source["source_id"],
        "collection": source["collection"],
        "owner": source["owner"],
        "repo": source["repo"],
        "configured_ref": source.get("configured_ref"),
        "resolved_revision": document["revision_sha"],
        "path": document["path"],
        "git_blob_sha1": document.get("git_blob_sha1"),
        "content_sha256": document.get("content_sha256"),
        "raw_url": document.get("raw_url"),
        "web_url": document.get("web_url"),
        "extractor_version": PARSER_VERSION,
    }
    if lines:
        result["lines"] = {"start": lines[0], "end": lines[1]}
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--max-file-bytes", type=int, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    corpus = args.corpus.resolve()
    sources_path = corpus / "sources.json"
    files_path = corpus / "files.jsonl"
    if not sources_path.exists() or not files_path.exists():
        print("No synchronized corpus found. Run sync_sources.py first.", file=sys.stderr)
        return 3
    sources = {item["source_id"]: item for item in load_json(sources_path)}
    definitions, aliases = load_taxonomy(args.taxonomy)
    config = load_json(SKILL_DIR / "references" / "sources.json")
    max_file_bytes = args.max_file_bytes or int(config["limits"]["max_index_file_bytes"])

    temporary_index = corpus / "index.sqlite.tmp"
    final_index = corpus / "index.sqlite"
    temporary_index.unlink(missing_ok=True)
    connection = sqlite3.connect(temporary_index)
    connection.row_factory = sqlite3.Row
    fts_available = create_schema(connection)
    connection.execute("INSERT INTO meta VALUES (?,?)", ("parser_version", PARSER_VERSION))
    connection.execute("INSERT INTO meta VALUES (?,?)", ("fts_available", "1" if fts_available else "0"))
    connection.execute(
        "INSERT INTO meta VALUES (?,?)",
        ("corpus_sources_sha256", file_sha256(sources_path)),
    )
    connection.execute(
        "INSERT INTO meta VALUES (?,?)",
        ("corpus_files_sha256", file_sha256(files_path)),
    )
    connection.execute(
        "INSERT INTO meta VALUES (?,?)",
        ("taxonomy_sha256", file_sha256(args.taxonomy)),
    )
    connection.execute(
        "INSERT INTO meta VALUES (?,?)",
        (
            "source_config_sha256",
            file_sha256(SKILL_DIR / "references" / "sources.json"),
        ),
    )

    for source in sorted(sources.values(), key=lambda item: item["source_id"]):
        connection.execute(
            "INSERT INTO sources VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                source["source_id"], source["collection"], source["source_kind"],
                source["owner"], source["repo"], source.get("configured_ref"),
                source.get("path"), source["revision_sha"], source.get("state", "current"),
                source.get("usage_context", "task-content"), source.get("web_url"),
                source.get("raw_url"), source.get("license_spdx"), source.get("synced_at"),
                json_compact(source),
            ),
        )

    task_exports: list[dict[str, Any]] = []
    quiz_exports: list[dict[str, Any]] = []
    macro_exports: list[dict[str, Any]] = []
    operator_exports: list[dict[str, Any]] = []
    indexed_documents = 0
    skipped_documents = 0

    for definition in definitions:
        connection.execute(
            "INSERT INTO operators VALUES (?,?,?,1)",
            (definition.operator_id, definition.lemma, json_compact(definition.aliases)),
        )

    for file_record in read_jsonl(files_path):
        source = sources.get(file_record["source_id"])
        if not source:
            continue
        document_id = stable_id(file_record["source_id"], file_record["path"])
        usage_context = source.get("usage_context", "task-content")
        content_state = file_record.get("content_state", "unknown")
        local_relpath = file_record.get("local_relpath")
        text: str | None = None
        encoding: str | None = None
        header: dict[str, Any] = {}
        headings: list[dict[str, Any]] = []
        warnings: list[str] = []
        tasks: list[dict[str, Any]] = []
        quizzes: list[dict[str, Any]] = []
        macros: list[dict[str, Any]] = []
        occurrences: list[dict[str, Any]] = []
        normalized_sha256: str | None = None
        title = Path(file_record["path"]).stem
        document_kind = "binary"

        if not file_record.get("is_text"):
            content_state = "binary"
            skipped_documents += 1
        elif not file_record.get("stored") or not local_relpath:
            content_state = "not_stored"
            skipped_documents += 1
        elif int(file_record.get("size_bytes", 0)) > max_file_bytes:
            content_state = "too_large"
            skipped_documents += 1
        else:
            absolute_path = corpus / Path(local_relpath)
            try:
                data = absolute_path.read_bytes()
            except OSError as exc:
                content_state = "read_error"
                warnings.append(f"read_error:{exc}")
            else:
                text, encoding = decode_text(data)
                if text is None:
                    content_state = "decode_error"
                    warnings.append("decode_error")
                else:
                    content_state = "indexed"
                    normalized_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
                    header, header_end, header_warnings = extract_header(text)
                    warnings.extend(header_warnings)
                    body = text
                    if header_end:
                        body = "".join("\n" if char == "\n" else " " for char in text[:header_end]) + text[header_end:]
                    live_text = mask_regex(body, FENCE_RE)
                    live_text = mask_regex(live_text, SCRIPT_RE)
                    live_text = mask_regex(live_text, STYLE_RE)
                    live_text = mask_regex(live_text, ONLOAD_RE)
                    live_text = mask_regex(live_text, HTML_COMMENT_RE)
                    headings = extract_headings(live_text)
                    title = title_from_headings(headings, file_record["path"])
                    quizzes = extract_quizzes(live_text, document_id, usage_context)
                    macros = extract_macros(text, document_id, usage_context, header_end)
                    tags = header.get("tags", [])
                    declared = declared_operators(tags, aliases)
                    tasks, occurrences, task_warnings = extract_tasks(
                        live_text, document_id, headings, quizzes, macros, definitions,
                        declared, tags, usage_context,
                    )
                    warnings.extend(task_warnings)
                    if "Math.random" in text or "crypto.getRandomValues" in text:
                        warnings.append("contains_dynamic_random_generation")
                    document_kind = "liascript" if header_end or quizzes or macros else "text"
                    if PurePosixPath(file_record["path"]).suffix.casefold() not in {
                        ".md", ".markdown", ".mdown", ".mkd"
                    }:
                        header = {}
                        headings = []
                        tasks = []
                        quizzes = []
                        macros = []
                        occurrences = []
                        document_kind = "text"
                    indexed_documents += 1

        document = {
            "document_id": document_id,
            "source_id": file_record["source_id"],
            "path": file_record["path"],
            "title": title,
            "document_kind": document_kind,
            "usage_context": usage_context,
            "revision_sha": file_record["revision_sha"],
            "git_blob_sha1": file_record.get("git_blob_sha1"),
            "content_sha256": file_record.get("content_sha256"),
            "normalized_sha256": normalized_sha256,
            "size_bytes": int(file_record.get("size_bytes", 0)),
            "line_count": file_record.get("line_count"),
            "encoding": encoding,
            "content_state": content_state,
            "local_relpath": local_relpath,
            "raw_url": file_record.get("raw_url"),
            "web_url": file_record.get("web_url"),
            "header": header,
            "headings": headings,
            "parse_warnings": sorted(set(warnings)),
            "text": text,
        }
        connection.execute(
            "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                document_id, document["source_id"], document["path"], title, document_kind,
                usage_context, document["revision_sha"], document["git_blob_sha1"],
                document["content_sha256"], normalized_sha256, document["size_bytes"],
                document["line_count"], encoding, content_state, local_relpath,
                document["raw_url"], document["web_url"], json_compact(header),
                json_compact(headings), json_compact(document["parse_warnings"]), text,
            ),
        )
        if text is not None:
            metadata_text = " ".join(header.get("tags", [])) + " " + json_compact(header.get("scalars", {}))
            add_search_item(
                connection, fts_available, document_id, "document", document["source_id"],
                document["path"], title, text, metadata_text,
            )

        for task in tasks:
            connection.execute(
                "INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    task["task_id"], document_id, task["ordinal"], task["start_line"],
                    task["end_line"], task["heading"], task["prompt"],
                    json_compact(task["operator_declared"]), json_compact(task["operator_detected"]),
                    json_compact(task["operators"]), task["operator_basis"],
                    task["operator_confidence"], task["task_type"],
                    json_compact(task["quiz_types"]), json_compact(task["macros"]),
                    json_compact(task["tags"]), task["usage_context"], task["raw_text"],
                ),
            )
            add_search_item(
                connection, fts_available, task["task_id"], "task", document["source_id"],
                document["path"], task["heading"] or title, task["prompt"] + "\n" + task["raw_text"],
                " ".join(task["operator_declared"] + task["operator_detected"] + task["quiz_types"] + task["macros"] + task["tags"]),
            )
            task_exports.append({
                **{key: value for key, value in task.items() if key != "raw_text"},
                "raw_text": task["raw_text"],
                "_provenance": provenance(document, source, (task["start_line"], task["end_line"])),
            })

        for quiz in quizzes:
            connection.execute(
                "INSERT INTO quizzes VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    quiz["quiz_id"], document_id, quiz.get("task_id"), quiz["ordinal"],
                    quiz["start_line"], quiz["end_line"], quiz["start_char"], quiz["end_char"],
                    quiz["syntax"], quiz["quiz_type"], quiz["usage_context"], quiz["raw_text"],
                ),
            )
            add_search_item(
                connection, fts_available, quiz["quiz_id"], "quiz", document["source_id"],
                document["path"], quiz["quiz_type"], quiz["raw_text"], quiz["syntax"],
            )
            quiz_exports.append({
                **quiz,
                "_provenance": provenance(document, source, (quiz["start_line"], quiz["end_line"])),
            })

        for macro in macros:
            connection.execute(
                "INSERT INTO macros VALUES (?,?,?,?,?,?,?)",
                (
                    macro["macro_id"], document_id, macro["name"], macro["start_line"],
                    macro["start_char"], macro["usage_context"], macro["raw_text"],
                ),
            )
            add_search_item(
                connection, fts_available, macro["macro_id"], "macro", document["source_id"],
                document["path"], macro["name"], macro["raw_text"], macro["usage_context"],
            )
            macro_exports.append({
                **macro,
                "_provenance": provenance(document, source, (macro["start_line"], macro["start_line"])),
            })

        for occurrence in occurrences:
            if connection.execute(
                "SELECT 1 FROM operators WHERE operator_id=?", (occurrence["operator_id"],)
            ).fetchone() is None:
                connection.execute(
                    "INSERT INTO operators VALUES (?,?,?,0)",
                    (occurrence["operator_id"], occurrence["operator_id"], "[]"),
                )
            connection.execute(
                "INSERT INTO operator_occurrences VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    occurrence["occurrence_id"], occurrence["operator_id"], document_id,
                    occurrence["task_id"], occurrence["start_line"], occurrence["end_line"],
                    occurrence["surface"], occurrence["detection_method"], occurrence["confidence"],
                    occurrence["usage_context"], occurrence["raw_text"],
                ),
            )

    for row in connection.execute(
        "SELECT o.operator_id,o.lemma,o.aliases_json,o.defined,COUNT(x.occurrence_id) AS occurrences "
        "FROM operators o LEFT JOIN operator_occurrences x ON x.operator_id=o.operator_id "
        "GROUP BY o.operator_id,o.lemma,o.aliases_json,o.defined ORDER BY o.operator_id"
    ):
        item = {
            "operator_id": row[0],
            "lemma": row[1],
            "aliases": json.loads(row[2]),
            "defined": bool(row[3]),
            "occurrences": row[4],
        }
        operator_exports.append(item)
        add_search_item(
            connection, fts_available, "operator:" + row[0], "operator", None, None,
            row[1], " ".join([row[0], row[1], *item["aliases"]]), f"occurrences={row[4]}",
        )

    connection.execute("INSERT INTO meta VALUES (?,?)", ("indexed_documents", str(indexed_documents)))
    connection.execute("INSERT INTO meta VALUES (?,?)", ("skipped_documents", str(skipped_documents)))
    connection.commit()
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    connection.close()
    if integrity != "ok":
        temporary_index.unlink(missing_ok=True)
        print(f"SQLite integrity check failed: {integrity}", file=sys.stderr)
        return 1
    os.replace(temporary_index, final_index)

    write_jsonl_atomic(corpus / "tasks.jsonl", sorted(task_exports, key=lambda item: item["task_id"]))
    write_jsonl_atomic(corpus / "quizzes.jsonl", sorted(quiz_exports, key=lambda item: item["quiz_id"]))
    write_jsonl_atomic(corpus / "macros.jsonl", sorted(macro_exports, key=lambda item: item["macro_id"]))
    write_jsonl_atomic(corpus / "operators.jsonl", operator_exports)
    print(
        f"Index built: {indexed_documents} text documents, {len(task_exports)} tasks, "
        f"{len(quiz_exports)} quizzes, {len(macro_exports)} macro references, "
        f"FTS={'yes' if fts_available else 'no'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
