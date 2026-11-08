#!/usr/bin/env python3
"""Bounded static TeX structure parser for local orientation metadata.

This module is not a TeX engine. It never expands macros, follows input or
include targets, starts subprocesses, accesses the network, or writes source
material. Production parsing accepts only selector-attested candidates.
"""

from __future__ import annotations

import bisect
import copy
import hashlib
import itertools
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Iterable, Mapping, Sequence

import local_orientation_features as features


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OPERATOR_TAXONOMY = ROOT / "references" / "operator-taxonomy.json"
PARSER_VERSION = 2

TASK_ENVIRONMENTS = frozenset({"aufgabe", "exercise", "problem", "question", "task"})
SOLUTION_ENVIRONMENTS = frozenset({"loesung", "lösung", "solution", "answer", "antwort"})
LIST_ENVIRONMENTS = frozenset({"enumerate", "itemize"})
TASK_COMMANDS = TASK_ENVIRONMENTS
SOLUTION_COMMANDS = SOLUTION_ENVIRONMENTS
HEADING_LEVELS = ("section", "subsection", "subsubsection", "paragraph")

WARNING_CODES = frozenset({
    "legacy_encoding", "unclosed_verbatim", "unbalanced_braces",
    "unbalanced_brackets", "unbalanced_environment",
    "malformed_macro_definition", "malformed_task_block",
    "malformed_solution_block", "ambiguous_solution_assignment",
    "warning_limit_reached",
})
RISK_CODES = frozenset({
    "shell_escape", "file_io", "lua_execution", "dynamic_tex",
    "macro_definition", "external_program", "external_resource",
    "pipe_input", "absolute_reference", "reference_traversal",
    "dynamic_reference", "malformed_reference", "risk_limit_reached",
})
REFERENCE_KINDS = (
    "literal_relative", "absolute", "traversal", "dynamic", "pipe", "malformed"
)

COMMAND_RE = re.compile(r"\\(?:[A-Za-z@]+|.)", re.UNICODE)
ENVIRONMENT_RE = re.compile(
    r"\\(begin|end)\s*\{\s*([A-Za-z@*\u00c0-\u024f]+)\s*\}", re.IGNORECASE
)
HEADING_RE = re.compile(
    r"\\(section|subsection|subsubsection|paragraph)\*?\s*", re.IGNORECASE
)
ITEM_RE = re.compile(r"\\item(?:\s*\[[^\]\r\n]{0,512}\])?", re.IGNORECASE)
REFERENCE_RE = re.compile(r"\\(input|include|subfile)\b", re.IGNORECASE)


class TexParseFault(ValueError):
    """A rejection whose string form never contains source data."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)

    def __repr__(self) -> str:
        return f"TexParseFault(code={self.code!r})"


@dataclass(frozen=True)
class ParserLimits:
    max_bytes: int = 4 * 1024 * 1024
    max_lines: int = 100_000
    max_commands: int = 25_000
    max_nesting: int = 128
    max_blocks: int = 5_000
    max_warnings: int = 256
    max_risks: int = 128

    def __post_init__(self) -> None:
        schema_maxima = {
            "max_bytes": 4 * 1024 * 1024,
            "max_lines": 100_000,
            "max_commands": 25_000,
            "max_nesting": 128,
            "max_blocks": 5_000,
            "max_warnings": 256,
            "max_risks": 128,
        }
        if any(
            type(getattr(self, name)) is not int
            or getattr(self, name) <= 0
            or getattr(self, name) > maximum
            for name, maximum in schema_maxima.items()
        ):
            raise ValueError("parser_limits_invalid")


@dataclass(frozen=True, repr=False)
class LocalOrientationDocumentMetadata:
    """Local-only data; repr is closed and safe_summary remains internal."""

    _payload: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        return copy.deepcopy(dict(self._payload))

    def safe_summary(self) -> dict[str, object]:
        structure = self._payload.get("structure", {})
        technical = self._payload.get("technical", {})
        return {
            "usage_context": "orientation-only",
            "parse_status": technical.get("parse_status", "unknown")
            if isinstance(technical, Mapping) else "unknown",
            "task_count": structure.get("task_count", 0)
            if isinstance(structure, Mapping) else 0,
            "solution_count": structure.get("solution_count", 0)
            if isinstance(structure, Mapping) else 0,
            "warning_count": len(self._payload.get("warning_codes", ())),
            "risk_count": len(self._payload.get("risk_codes", ())),
        }

    def __repr__(self) -> str:
        return "LocalOrientationDocumentMetadata(<local-only>)"


@dataclass(frozen=True)
class _Block:
    name: str
    shape: str
    start: int
    end: int


def _mask(chars: list[str], start: int, end: int) -> None:
    for index in range(max(0, start), min(len(chars), end)):
        if chars[index] not in "\r\n":
            chars[index] = " "


def _skip_space(text: str, position: int) -> int:
    while position < len(text) and text[position].isspace():
        position += 1
    return position


def _skip_tex_space(text: str, position: int) -> int:
    """Skip TeX whitespace, including comments that consume their newline."""
    while position < len(text):
        position = _skip_space(text, position)
        if position >= len(text) or text[position] != "%":
            return position
        line_end = text.find("\n", position + 1)
        if line_end < 0:
            return len(text)
        position = line_end + 1
    return position


def _consume_group(
    text: str, position: int, opener: str, closer: str, maximum: int
) -> int | None:
    if position >= len(text) or text[position] != opener:
        return None
    depth = 0
    backslash_run = 0
    index = position
    while index < len(text):
        character = text[index]
        if character == chr(92):
            backslash_run += 1
            index += 1
            continue
        escaped = bool(backslash_run % 2)
        backslash_run = 0
        if escaped:
            index += 1
            continue
        if character == "%":
            line_end = text.find("\n", index + 1)
            if line_end < 0:
                return None
            index = line_end + 1
            continue
        if character == opener:
            depth += 1
            if depth > maximum:
                raise TexParseFault("nesting_limit_exceeded")
        elif character == closer:
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _find_group_start(text: str, position: int, maximum_scan: int) -> int | None:
    limit = min(len(text), position + maximum_scan)
    backslash_run = 0
    index = position
    while index < limit:
        character = text[index]
        if character == chr(92):
            backslash_run += 1
            index += 1
            continue
        escaped = bool(backslash_run % 2)
        backslash_run = 0
        if escaped:
            index += 1
            continue
        if character == "%":
            line_end = text.find("\n", index + 1, limit)
            if line_end < 0:
                return None
            index = line_end + 1
            continue
        if character == "{":
            return index
        index += 1
    return None


def _strip_comments(text: str) -> str:
    chars = list(text)
    position = 0
    while position < len(text):
        if text[position] == "%":
            end = text.find("\n", position)
            end = len(text) if end < 0 else end
            _mask(chars, position, end)
            position = end
            continue
        if text[position] != chr(92):
            position += 1
            continue
        run_start = position
        while position < len(text) and text[position] == chr(92):
            position += 1
        if position >= len(text) or text[position] != "%":
            continue
        if (position - run_start) % 2:
            position += 1
            continue
        end = text.find("\n", position)
        end = len(text) if end < 0 else end
        _mask(chars, position, end)
        position = end
    return "".join(chars)


def _elide_tex_comments(text: str) -> str:
    """Remove TeX comments and their consumed line ending from a token."""
    output: list[str] = []
    position = 0
    while position < len(text):
        if text[position] == "%":
            line_end = text.find("\n", position + 1)
            position = len(text) if line_end < 0 else line_end + 1
            continue
        if text[position] != chr(92):
            output.append(text[position])
            position += 1
            continue
        run_start = position
        while position < len(text) and text[position] == chr(92):
            position += 1
        output.append(text[run_start:position])
        if position >= len(text) or text[position] != "%":
            continue
        if (position - run_start) % 2:
            output.append("%")
            position += 1
            continue
        line_end = text.find("\n", position + 1)
        position = len(text) if line_end < 0 else line_end + 1
    return "".join(output)


def _macro_definition_end(
    text: str,
    command: str,
    command_end: int,
    limits: ParserLimits,
) -> tuple[int, bool]:
    cursor = _skip_tex_space(text, command_end)
    if cursor < len(text) and text[cursor] == "*":
        cursor = _skip_tex_space(text, cursor + 1)
    end: int | None = None
    if command in {"newcommand", "renewcommand", "providecommand"}:
        if cursor < len(text) and text[cursor] == "{":
            grouped = _consume_group(text, cursor, "{", "}", limits.max_nesting)
            cursor = grouped if grouped is not None else -1
        else:
            name = re.match(r"\\[A-Za-z@]+", text[cursor:])
            cursor = cursor + len(name.group(0)) if name else -1
        if cursor >= 0:
            cursor = _skip_tex_space(text, cursor)
            for _ in range(2):
                if cursor >= len(text) or text[cursor] != "[":
                    break
                grouped = _consume_group(
                    text, cursor, "[", "]", limits.max_nesting
                )
                if grouped is None:
                    cursor = -1
                    break
                cursor = _skip_tex_space(text, grouped)
            if cursor >= 0 and cursor < len(text) and text[cursor] == "{":
                end = _consume_group(text, cursor, "{", "}", limits.max_nesting)
    else:
        body = _find_group_start(text, cursor, 2048)
        if body is not None:
            end = _consume_group(text, body, "{", "}", limits.max_nesting)
    if end is not None:
        return end, False
    line_end = text.find("\n", command_end)
    return (len(text) if line_end < 0 else line_end), True


def _environment_name(
    text: str,
    command_end: int,
    limits: ParserLimits,
) -> tuple[str, int] | None:
    cursor = _skip_tex_space(text, command_end)
    if cursor >= len(text) or text[cursor] != "{":
        return None
    end = _consume_group(text, cursor, "{", "}", limits.max_nesting)
    if end is None:
        return None
    environment = _elide_tex_comments(
        text[cursor + 1:end - 1]
    ).strip().casefold()
    return environment, end


def _verbatim_begin(
    text: str,
    command_end: int,
    limits: ParserLimits,
) -> tuple[str, int] | None:
    parsed = _environment_name(text, command_end, limits)
    if parsed is None:
        return None
    environment, end = parsed
    if environment not in {"verbatim", "verbatim*", "lstlisting", "minted"}:
        return None
    return environment, end


def _verbatim_end(
    text: str,
    position: int,
    environment: str,
    limits: ParserLimits,
) -> int | None:
    newline = text.find("\n", position)
    if newline < 0:
        return None
    line_start = newline + 1
    while line_start <= len(text):
        cursor = line_start
        while cursor < len(text) and text[cursor] in " \t":
            cursor += 1
        command_end = cursor + 4
        if (command_end <= len(text)
                and text[cursor:cursor + 1] == chr(92)
                and text[cursor + 1:command_end].casefold() == "end"
                and (command_end == len(text)
                     or not (text[command_end].isascii()
                             and (text[command_end].isalpha()
                                  or text[command_end] == "@")))):
            parsed = _environment_name(text, command_end, limits)
            if parsed is not None and parsed[0] == environment:
                group_end = parsed[1]
                tail = group_end
                while tail < len(text) and text[tail] in " \t":
                    tail += 1
                if (tail == len(text) or text[tail] == "\n"
                        or (text[tail] == "\r"
                            and (tail + 1 == len(text)
                                 or text[tail + 1] == "\n"))):
                    return group_end
        newline = text.find("\n", line_start)
        if newline < 0:
            return None
        line_start = newline + 1
    return None


def _preprocess_tex(
    text: str, limits: ParserLimits
) -> tuple[str, int, int, list[str], list[str]]:
    """Mask comments, macro definitions and verbatim regions in one pass."""
    chars = list(text)
    position = 0
    verbatim_count = 0
    macro_count = 0
    warnings: list[str] = []
    risks: list[str] = []
    macro_commands = {
        "newcommand", "renewcommand", "providecommand",
        "def", "edef", "gdef", "xdef",
    }

    while position < len(text):
        if text[position] == "%":
            end = text.find("\n", position)
            end = len(text) if end < 0 else end
            _mask(chars, position, end)
            position = end
            continue
        if text[position] != chr(92):
            position += 1
            continue

        run_start = position
        while position < len(text) and text[position] == chr(92):
            position += 1
        if position >= len(text):
            break
        run_length = position - run_start
        if text[position] == "%":
            if run_length % 2:
                position += 1
            else:
                end = text.find("\n", position)
                end = len(text) if end < 0 else end
                _mask(chars, position, end)
                position = end
            continue
        if not run_length % 2:
            continue
        command_start = position - 1
        first = text[position]
        if not (first.isascii() and (first.isalpha() or first == "@")):
            position += 1
            continue
        command_end = position + 1
        while command_end < len(text):
            character = text[command_end]
            if not (character.isascii() and (character.isalpha() or character == "@")):
                break
            command_end += 1
        command = text[position:command_end].casefold()

        if command in macro_commands:
            end, malformed = _macro_definition_end(
                text, command, command_end, limits
            )
            macro_span = _strip_comments(text[command_start:end])
            risks.extend(_dangerous_risks(macro_span))
            risks.append("macro_definition")
            _mask(chars, command_start, end)
            macro_count += 1
            if macro_count > limits.max_blocks:
                raise TexParseFault("block_limit_exceeded")
            if malformed:
                warnings.append("malformed_macro_definition")
            position = max(end, command_end)
            continue

        if command == "verb":
            delimiter_at = command_end
            if delimiter_at < len(text) and text[delimiter_at] == "*":
                delimiter_at += 1
            if delimiter_at >= len(text) or text[delimiter_at].isspace():
                position = command_end
                continue
            delimiter = text[delimiter_at]
            line_end = text.find("\n", delimiter_at + 1)
            found = text.find(delimiter, delimiter_at + 1)
            if found < 0 or (line_end >= 0 and found > line_end):
                end = len(text) if line_end < 0 else line_end
                warnings.append("unclosed_verbatim")
            else:
                end = found + 1
            _mask(chars, command_start, end)
            verbatim_count += 1
            if verbatim_count > limits.max_blocks:
                raise TexParseFault("block_limit_exceeded")
            position = max(end, command_end)
            continue

        if command == "begin":
            begin = _verbatim_begin(text, command_end, limits)
            if begin is not None:
                environment, begin_end = begin
                end = _verbatim_end(
                    text, begin_end, environment, limits
                )
                if end is None:
                    end = len(text)
                    warnings.append("unclosed_verbatim")
                _mask(chars, command_start, end)
                verbatim_count += 1
                if verbatim_count > limits.max_blocks:
                    raise TexParseFault("block_limit_exceeded")
                if environment == "minted":
                    risks.append("external_program")
                position = end
                continue
        position = command_end

    return "".join(chars), verbatim_count, macro_count, warnings, risks


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    offsets.extend(index + 1 for index, character in enumerate(text) if character == "\n")
    return offsets


def _line_number(offsets: Sequence[int], position: int) -> int:
    return bisect.bisect_right(offsets, max(0, position))


def _check_nesting(text: str, limits: ParserLimits) -> list[str]:
    brace_depth = bracket_depth = 0
    warnings: list[str] = []
    backslash_run = 0
    for character in text:
        if character == chr(92):
            backslash_run += 1
            continue
        escaped = bool(backslash_run % 2)
        backslash_run = 0
        if escaped:
            continue
        if character == "{":
            brace_depth += 1
        elif character == "}":
            brace_depth -= 1
            if brace_depth < 0:
                warnings.append("unbalanced_braces")
                brace_depth = 0
        elif character == "[":
            bracket_depth += 1
        elif character == "]":
            bracket_depth -= 1
            if bracket_depth < 0:
                warnings.append("unbalanced_brackets")
                bracket_depth = 0
        if max(brace_depth, bracket_depth) > limits.max_nesting:
            raise TexParseFault("nesting_limit_exceeded")
    if brace_depth:
        warnings.append("unbalanced_braces")
    if bracket_depth:
        warnings.append("unbalanced_brackets")
    return warnings


def _environment_blocks(
    text: str, limits: ParserLimits
) -> tuple[list[_Block], list[_Block], int, list[str]]:
    stack: list[tuple[str, int]] = []
    tasks: list[_Block] = []
    solutions: list[_Block] = []
    list_count = 0
    warnings: list[str] = []
    events = list(itertools.islice(
        ENVIRONMENT_RE.finditer(text), limits.max_commands + 1
    ))
    if len(events) > limits.max_commands:
        raise TexParseFault("command_limit_exceeded")
    for event in events:
        action = event.group(1).casefold()
        name = event.group(2).casefold()
        if action == "begin":
            stack.append((name, event.start()))
            if len(stack) > limits.max_nesting:
                raise TexParseFault("nesting_limit_exceeded")
            if name in LIST_ENVIRONMENTS:
                list_count += 1
                if list_count > limits.max_blocks:
                    raise TexParseFault("block_limit_exceeded")
            continue
        if not stack or stack[-1][0] != name:
            warnings.append("unbalanced_environment")
            match_at = next((index for index in range(len(stack) - 1, -1, -1)
                             if stack[index][0] == name), None)
            if match_at is None:
                continue
            _name, start = stack.pop(match_at)
        else:
            _name, start = stack.pop()
        block = _Block(name, "environment", start, event.end())
        if name in TASK_ENVIRONMENTS:
            tasks.append(block)
        elif name in SOLUTION_ENVIRONMENTS:
            solutions.append(block)
    for name, start in stack:
        warnings.append("unbalanced_environment")
        if name in TASK_ENVIRONMENTS:
            tasks.append(_Block(name, "environment", start, len(text)))
            warnings.append("malformed_task_block")
        elif name in SOLUTION_ENVIRONMENTS:
            solutions.append(_Block(name, "environment", start, len(text)))
            warnings.append("malformed_solution_block")
    if len(tasks) + len(solutions) > limits.max_blocks:
        raise TexParseFault("block_limit_exceeded")
    return (sorted(tasks, key=lambda block: block.start),
            sorted(solutions, key=lambda block: block.start),
            list_count, warnings)


def _command_blocks(
    text: str, names: Iterable[str], kind: str, limits: ParserLimits
) -> tuple[list[_Block], list[str]]:
    alternatives = "|".join(sorted((re.escape(name) for name in names),
                                   key=len, reverse=True))
    pattern = re.compile(r"\\(" + alternatives + r")\b", re.IGNORECASE)
    blocks: list[_Block] = []
    warnings: list[str] = []
    for match in pattern.finditer(text):
        cursor = _skip_space(text, match.end())
        if cursor < len(text) and text[cursor] == "*":
            cursor = _skip_space(text, cursor + 1)
        if cursor < len(text) and text[cursor] == "[":
            cursor = _consume_group(text, cursor, "[", "]", limits.max_nesting) or -1
            if cursor >= 0:
                cursor = _skip_space(text, cursor)
        if cursor < 0 or cursor >= len(text) or text[cursor] != "{":
            continue
        end = _consume_group(text, cursor, "{", "}", limits.max_nesting)
        if end is None:
            warnings.append("malformed_task_block" if kind == "task"
                            else "malformed_solution_block")
            end = len(text)
        blocks.append(_Block(match.group(1).casefold(), "command", match.start(), end))
        if len(blocks) > limits.max_blocks:
            raise TexParseFault("block_limit_exceeded")
    return blocks, warnings


def _deduplicate_blocks(blocks: Iterable[_Block]) -> list[_Block]:
    result: list[_Block] = []
    seen: set[tuple[int, int, str]] = set()
    for block in sorted(blocks, key=lambda item: (item.start, -item.end, item.shape)):
        key = (block.start, block.end, block.shape)
        if key in seen:
            continue
        if block.shape == "command" and any(
            parent.shape == "environment" and parent.start <= block.start
            and block.end <= parent.end for parent in result
        ):
            continue
        seen.add(key)
        result.append(block)
    return result


def _mask_blocks(text: str, blocks: Iterable[_Block]) -> str:
    chars = list(text)
    masked_until = 0
    for block in sorted(blocks, key=lambda item: (item.start, item.end)):
        start = max(masked_until, block.start)
        end = min(len(text), block.end)
        if start < end:
            _mask(chars, start, end)
        masked_until = max(masked_until, end)
    return "".join(chars)


def _load_operator_patterns(path: Path) -> list[tuple[str, re.Pattern[str]]]:
    try:
        lexical = Path(path).absolute()
        expected_lexical = DEFAULT_OPERATOR_TAXONOMY.absolute()
    except OSError as exc:
        raise TexParseFault("operator_taxonomy_invalid") from exc
    if lexical != expected_lexical:
        raise TexParseFault("operator_taxonomy_boundary")
    try:
        expected_resolved = DEFAULT_OPERATOR_TAXONOMY.resolve(strict=True)
    except OSError as exc:
        raise TexParseFault("operator_taxonomy_invalid") from exc
    try:
        raw = expected_resolved.read_bytes()
        if len(raw) > 1_000_000:
            raise TexParseFault("operator_taxonomy_too_large")
        value = json.loads(raw.decode("utf-8-sig"))
    except TexParseFault:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TexParseFault("operator_taxonomy_invalid") from exc
    if not isinstance(value, dict) or not isinstance(value.get("operators"), list):
        raise TexParseFault("operator_taxonomy_invalid")
    output: list[tuple[str, re.Pattern[str]]] = []
    for operator in value["operators"]:
        if not isinstance(operator, dict):
            raise TexParseFault("operator_taxonomy_invalid")
        identifier = operator.get("id")
        patterns = operator.get("prompt_patterns")
        if (not isinstance(identifier, str)
                or not re.fullmatch(r"[^\W_][\w-]{0,63}", identifier, re.UNICODE)
                or not isinstance(patterns, list)
                or any(not isinstance(pattern, str) or len(pattern) > 1024
                       for pattern in patterns)):
            raise TexParseFault("operator_taxonomy_invalid")
        for pattern in patterns:
            try:
                output.append((identifier, re.compile(
                    pattern, re.IGNORECASE | re.UNICODE
                )))
            except re.error as exc:
                raise TexParseFault("operator_taxonomy_invalid") from exc
    if len(output) > 512:
        raise TexParseFault("operator_taxonomy_invalid")
    return output


def _operator_candidates(
    text: str,
    block: _Block,
    offsets: Sequence[int],
    patterns: Sequence[tuple[str, re.Pattern[str]]],
) -> list[dict[str, object]]:
    region = text[block.start:min(block.end, block.start + 8192)]
    matches: dict[str, tuple[int, int]] = {}
    for identifier, pattern in patterns:
        found = pattern.search(region)
        if found is None:
            continue
        absolute = block.start + found.start()
        previous = matches.get(identifier)
        if previous is None or absolute < previous[0]:
            matches[identifier] = (absolute, _line_number(offsets, absolute))
    return [{
        "operator_id": identifier,
        "basis": "body_pattern",
        "confidence": "medium",
        "line": line,
        "conflict_status": "none",
    } for identifier, (_position, line) in sorted(
        matches.items(), key=lambda item: (item[1][0], item[0])
    )]


def _bounded_codes(codes: Iterable[str], maximum: int, limit_code: str) -> list[str]:
    unique = sorted(set(codes))
    if len(unique) <= maximum:
        return unique
    return unique[:max(0, maximum - 1)] + [limit_code]


def _reference_value(text: str, match: re.Match[str], limits: ParserLimits) -> str | None:
    cursor = _skip_space(text, match.end())
    if cursor < len(text) and text[cursor] == "{":
        end = _consume_group(text, cursor, "{", "}", limits.max_nesting)
        return text[cursor + 1:end - 1].strip() if end is not None else None
    if cursor < len(text):
        token = re.match(r"[^\s%]+", text[cursor:])
        return token.group(0).strip() if token else None
    return None


def _classify_references(text: str, limits: ParserLimits) -> tuple[dict[str, int], list[str]]:
    counts = {kind: 0 for kind in REFERENCE_KINDS}
    risks: list[str] = []
    references = list(itertools.islice(
        REFERENCE_RE.finditer(text), limits.max_commands + 1
    ))
    if len(references) > limits.max_commands:
        raise TexParseFault("command_limit_exceeded")
    for match in references:
        value = _reference_value(text, match, limits)
        if not value:
            counts["malformed"] += 1
            risks.append("malformed_reference")
            continue
        stripped = value.strip(chr(34) + chr(39))
        if stripped.startswith("|"):
            counts["pipe"] += 1
            risks.append("pipe_input")
        elif (stripped.casefold().startswith("file:")
              or stripped.startswith("/") or stripped.startswith(chr(92) * 2)
              or PureWindowsPath(stripped).is_absolute()):
            counts["absolute"] += 1
            risks.append("absolute_reference")
        elif any(part == ".." for part in PurePosixPath(
                stripped.replace(chr(92), "/")).parts):
            counts["traversal"] += 1
            risks.append("reference_traversal")
        elif any(token in stripped for token in (chr(92), "#", "$", "{", "}")):
            counts["dynamic"] += 1
            risks.append("dynamic_reference")
        else:
            counts["literal_relative"] += 1
    return counts, risks


def _dangerous_risks(text: str) -> list[str]:
    prefix = re.escape(chr(92))
    checks = (
        (prefix + r"write\s*18\b|" + prefix + r"immediate\s*"
         + prefix + r"write\s*18\b|" + prefix + r"ShellEscape\b",
         "shell_escape"),
        (prefix + r"(?:openin|openout|read|write)(?![A-Za-z@])", "file_io"),
        (prefix + r"(?:directlua|luaexec)(?![A-Za-z@])", "lua_execution"),
        (prefix + r"(?:catcode|csname)(?![A-Za-z@])", "dynamic_tex"),
        (prefix + r"(?:def|edef|gdef|xdef|newcommand|renewcommand|providecommand)"
         + r"(?![A-Za-z@])",
         "macro_definition"),
        (prefix + r"(?:tikzexternalize|write18|ShellEscape)\b", "external_program"),
        (prefix + r"(?:includegraphics|bibliography|addbibresource)\b",
         "external_resource"),
    )
    return [code for pattern, code in checks if re.search(pattern, text, re.IGNORECASE)]


def _decode_tex(data: bytes, limits: ParserLimits) -> tuple[str, str, list[str]]:
    if len(data) > limits.max_bytes:
        raise TexParseFault("file_size_limit_exceeded")
    if b"\x00" in data:
        raise TexParseFault("binary_input_rejected")
    sample = data[:8192]
    if sample:
        controls = sum(byte < 9 or 13 < byte < 32 for byte in sample)
        if controls / len(sample) >= 0.05:
            raise TexParseFault("binary_input_rejected")
    if data.startswith(b"\xef\xbb\xbf"):
        try:
            return data.decode("utf-8-sig"), "utf-8-sig", []
        except UnicodeDecodeError as exc:
            raise TexParseFault("encoding_invalid") from exc
    try:
        return data.decode("utf-8"), "utf-8", []
    except UnicodeDecodeError:
        header = data[:8192].lower()
        byte_prefix = re.escape(bytes((92,)))
        cp1252 = re.search(
            byte_prefix
            + rb"usepackage\s*\[\s*(?:ansinew|cp1252)\s*\]\s*\{\s*inputenc\s*\}",
            header,
        )
        latin1 = re.search(
            byte_prefix
            + rb"usepackage\s*\[\s*(?:latin1|iso-8859-1)\s*\]\s*\{\s*inputenc\s*\}",
            header,
        )
        encoding = "cp1252" if cp1252 else "iso-8859-1" if latin1 else None
        if encoding is None:
            raise TexParseFault("encoding_undetermined")
        try:
            decoded = data.decode(encoding)
        except UnicodeDecodeError as exc:
            raise TexParseFault("encoding_invalid") from exc
        public_name = "windows-1252" if encoding == "cp1252" else "iso-8859-1"
        return decoded, public_name, ["legacy_encoding"]


def _classification(source: object | None) -> dict[str, object]:
    def values(name: str) -> list[object]:
        value = getattr(source, name, ()) if source is not None else ()
        return list(value) if isinstance(value, (tuple, list)) else []

    archive = getattr(source, "archive_policy", "exclude") if source else "exclude"
    if archive not in {"exclude", "deprioritize"}:
        archive = "exclude"
    subjects = values("subjects")
    grades = values("grades")
    learner_groups = values("learner_groups")
    document_types = values("document_types")
    if (len(subjects) > 2 or len(grades) > 9
            or len(learner_groups) > 32 or len(document_types) > 32):
        raise TexParseFault("classification_limit_exceeded")
    if (not set(subjects).issubset({"mathematics", "physics"})
            or any(type(value) is not int or not 5 <= value <= 13 for value in grades)
            or any(not isinstance(value, str) or not 1 <= len(value) <= 80
                   for value in learner_groups)
            or any(not isinstance(value, str)
                   or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value)
                   for value in document_types)
            or any(len(values) != len(set(values)) for values in (
                subjects, grades, learner_groups, document_types
            ))):
        raise TexParseFault("classification_invalid")
    return {
        "subjects": subjects,
        "grades": grades,
        "learner_groups": learner_groups,
        "document_types": document_types,
        "archive_policy": archive,
        "basis": "configured",
    }


def _validate_metadata_envelope(
    source_id: str,
    document_id: str,
    relative_locator: str,
    size_bytes: int,
    modified_ns: int,
    integrity_sha256: str,
    encoding: str,
    limits: ParserLimits,
) -> None:
    path = PurePosixPath(relative_locator)
    windows_path = PureWindowsPath(relative_locator)
    if (not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", source_id)
            or not re.fullmatch(r"doc-[a-f0-9]{32}", document_id)
            or not relative_locator or len(relative_locator) > 1024
            or path.is_absolute() or windows_path.is_absolute()
            or any(ord(character) < 32
                   or ord(character) in {127, 0x85, 0x2028, 0x2029}
                   for character in relative_locator)
            or ":" in relative_locator
            or chr(92) in relative_locator
            or any(part in {"", ".", ".."} for part in path.parts)
            or type(size_bytes) is not int or not 0 <= size_bytes <= limits.max_bytes
            or type(modified_ns) is not int or modified_ns < 0
            or not re.fullmatch(r"[a-f0-9]{64}", integrity_sha256)
            or encoding not in {"utf-8", "utf-8-sig", "windows-1252", "iso-8859-1"}):
        raise TexParseFault("metadata_envelope_invalid")


def _parse_decoded(
    text: str,
    *,
    source_id: str,
    document_id: str,
    relative_locator: str,
    size_bytes: int,
    modified_ns: int,
    integrity_sha256: str,
    encoding: str,
    source: object | None,
    initial_warnings: Iterable[str],
    limits: ParserLimits,
    operator_patterns: Sequence[tuple[str, re.Pattern[str]]],
) -> LocalOrientationDocumentMetadata:
    _validate_metadata_envelope(
        source_id, document_id, relative_locator, size_bytes, modified_ns,
        integrity_sha256, encoding, limits,
    )
    line_count = text.count("\n") + 1
    if line_count > limits.max_lines:
        raise TexParseFault("line_limit_exceeded")

    analysis, verbatim_count, macro_count, warnings, risks = _preprocess_tex(
        text, limits
    )
    warnings.extend(initial_warnings)
    risks.extend(_dangerous_risks(analysis))
    warnings.extend(_check_nesting(analysis, limits))
    command_count = sum(1 for _ in itertools.islice(
        COMMAND_RE.finditer(analysis), limits.max_commands + 1
    ))
    if command_count > limits.max_commands:
        raise TexParseFault("command_limit_exceeded")

    env_tasks, env_solutions, list_count, env_warnings = _environment_blocks(
        analysis, limits
    )
    warnings.extend(env_warnings)
    command_tasks, task_warnings = _command_blocks(
        analysis, TASK_COMMANDS, "task", limits
    )
    command_solutions, solution_warnings = _command_blocks(
        analysis, SOLUTION_COMMANDS, "solution", limits
    )
    warnings.extend(task_warnings)
    warnings.extend(solution_warnings)
    tasks = _deduplicate_blocks((*env_tasks, *command_tasks))
    solutions = _deduplicate_blocks((*env_solutions, *command_solutions))
    if len(tasks) + len(solutions) > limits.max_blocks:
        raise TexParseFault("block_limit_exceeded")

    offsets = _line_offsets(text)
    task_analysis = _mask_blocks(analysis, solutions)
    items = list(itertools.islice(
        ITEM_RE.finditer(analysis), limits.max_commands + 1
    ))
    if len(items) > limits.max_commands:
        raise TexParseFault("command_limit_exceeded")
    task_items = list(itertools.islice(
        ITEM_RE.finditer(task_analysis), limits.max_commands + 1
    ))
    if len(task_items) > limits.max_commands:
        raise TexParseFault("command_limit_exceeded")
    headings = {level: 0 for level in HEADING_LEVELS}
    heading_count = 0
    for heading in HEADING_RE.finditer(analysis):
        level = heading.group(1).casefold()
        headings[level] += 1
        heading_count += 1
        if (headings[level] > limits.max_blocks
                or heading_count > min(20_000, 4 * limits.max_blocks)):
            raise TexParseFault("heading_limit_exceeded")

    task_payloads: list[dict[str, object]] = []
    for ordinal, block in enumerate(tasks, 1):
        subtask_count = sum(
            block.start <= item.start() < block.end for item in task_items
        )
        task_payloads.append({
            "task_id": f"task-{ordinal:06d}",
            "ordinal": ordinal,
            "kind": block.shape,
            "line_span": {
                "start": _line_number(offsets, block.start),
                "end": _line_number(offsets, max(block.start, block.end - 1)),
            },
            "subtask_count": subtask_count,
            "operator_candidates": _operator_candidates(
                task_analysis, block, offsets, operator_patterns
            ),
            "response_shape": "multi-part" if subtask_count else "unknown",
            "solution_presence": "absent",
            "solution_shape": "unknown",
            "solution_assignment": "unassigned",
        })

    solution_payloads: list[dict[str, object]] = []
    assigned: dict[int, list[int]] = {index: [] for index in range(len(tasks))}
    for ordinal, block in enumerate(solutions, 1):
        contained = [index for index, task in enumerate(tasks)
                     if task.start <= block.start and block.end <= task.end]
        if len(contained) == 1:
            task_index: int | None = contained[0]
        else:
            preceding = [index for index, task in enumerate(tasks)
                         if task.end <= block.start and not assigned[index]]
            task_index = (max(preceding, key=lambda index: tasks[index].end)
                          if preceding else None)
        payload: dict[str, object] = {
            "solution_id": f"solution-{ordinal:06d}",
            "ordinal": ordinal,
            "kind": block.shape,
            "line_span": {
                "start": _line_number(offsets, block.start),
                "end": _line_number(offsets, max(block.start, block.end - 1)),
            },
            "assignment_status": "assigned" if task_index is not None else "unassigned",
        }
        if task_index is not None:
            assigned[task_index].append(ordinal - 1)
            payload["task_id"] = f"task-{task_index + 1:06d}"
        solution_payloads.append(payload)

    for task_index, solution_indexes in assigned.items():
        if len(solution_indexes) == 1:
            solution = solutions[solution_indexes[0]]
            task_payloads[task_index]["solution_presence"] = "present"
            task_payloads[task_index]["solution_shape"] = solution.shape
            task_payloads[task_index]["solution_assignment"] = "assigned"
        elif len(solution_indexes) > 1:
            task_payloads[task_index]["solution_presence"] = "ambiguous"
            task_payloads[task_index]["solution_assignment"] = "ambiguous"
            warnings.append("ambiguous_solution_assignment")

    reference_counts, reference_risks = _classify_references(analysis, limits)
    risks.extend(reference_risks)
    warning_codes = _bounded_codes(
        warnings, limits.max_warnings, "warning_limit_reached"
    )
    risk_codes = _bounded_codes(risks, limits.max_risks, "risk_limit_reached")
    if any(code not in WARNING_CODES for code in warning_codes):
        raise TexParseFault("internal_warning_code_invalid")
    if any(code not in RISK_CODES for code in risk_codes):
        raise TexParseFault("internal_risk_code_invalid")

    classification = _classification(source)
    try:
        feature_payload = features.extract_features(
            task_analysis,
            tasks=task_payloads,
            solutions=solution_payloads,
            classification=classification,
            warning_codes=warning_codes,
            risk_codes=risk_codes,
        )
    except features.FeatureFault as fault:
        raise TexParseFault(fault.code) from None

    payload: dict[str, object] = {
        "schema_version": 2,
        "parser_version": PARSER_VERSION,
        "usage_context": "orientation-only",
        "source_id": source_id,
        "document_id": document_id,
        "local_provenance": {
            "relative_locator": relative_locator,
            "size_bytes": size_bytes,
            "modified_ns": modified_ns,
            "integrity_sha256": integrity_sha256,
        },
        "classification": classification,
        "features": feature_payload,
        "technical": {
            "encoding": encoding,
            "parse_status": "parsed_with_warnings"
            if warning_codes or risk_codes else "parsed",
            "line_count": line_count,
            "command_count": command_count,
        },
        "suitability": "review_required"
        if warning_codes or risk_codes else "structure_only",
        "structure": {
            "heading_counts": headings,
            "heading_count": heading_count,
            "task_count": len(tasks),
            "solution_count": len(solutions),
            "list_count": list_count,
            "item_count": len(items),
            "verbatim_block_count": verbatim_count,
            "macro_definition_count": macro_count,
        },
        "tasks": task_payloads,
        "solutions": solution_payloads,
        "reference_counts": reference_counts,
        "warning_codes": warning_codes,
        "risk_codes": risk_codes,
    }
    return LocalOrientationDocumentMetadata(payload)


def _parse_tex_text_impl(
    text: str,
    *,
    source_id: str = "synthetic-source",
    document_id: str = "doc-00000000000000000000000000000000",
    relative_locator: str = "synthetic/document.tex",
    encoding: str = "utf-8",
    modified_ns: int = 0,
    source: object | None = None,
    limits: ParserLimits | None = None,
    operator_taxonomy_path: Path = DEFAULT_OPERATOR_TAXONOMY,
) -> LocalOrientationDocumentMetadata:
    """Parse already decoded synthetic text without touching source paths."""
    active_limits = limits or ParserLimits()
    if not isinstance(text, str):
        raise TexParseFault("text_input_invalid")
    encoded = text.encode("utf-8")
    if len(encoded) > active_limits.max_bytes:
        raise TexParseFault("file_size_limit_exceeded")
    return _parse_decoded(
        text,
        source_id=source_id,
        document_id=document_id,
        relative_locator=relative_locator,
        size_bytes=len(encoded),
        modified_ns=modified_ns,
        integrity_sha256=hashlib.sha256(encoded).hexdigest(),
        encoding=encoding,
        source=source,
        initial_warnings=(),
        limits=active_limits,
        operator_patterns=_load_operator_patterns(operator_taxonomy_path),
    )


def _sanitized_call(function):
    failure: str | None = None
    try:
        return function()
    except TexParseFault as exc:
        failure = exc.code
    except Exception:
        failure = "parser_operational_error"
    raise TexParseFault(failure or "parser_operational_error")


def parse_tex_text(
    text: str,
    *,
    source_id: str = "synthetic-source",
    document_id: str = "doc-00000000000000000000000000000000",
    relative_locator: str = "synthetic/document.tex",
    encoding: str = "utf-8",
    modified_ns: int = 0,
    source: object | None = None,
    limits: ParserLimits | None = None,
    operator_taxonomy_path: Path = DEFAULT_OPERATOR_TAXONOMY,
) -> LocalOrientationDocumentMetadata:
    """Parse decoded synthetic text and sanitize every public failure."""
    return _sanitized_call(lambda: _parse_tex_text_impl(
        text, source_id=source_id, document_id=document_id,
        relative_locator=relative_locator, encoding=encoding,
        modified_ns=modified_ns, source=source, limits=limits,
        operator_taxonomy_path=operator_taxonomy_path,
    ))


def parse_candidate(
    candidate: object,
    *,
    limits: ParserLimits | None = None,
    operator_taxonomy_path: Path = DEFAULT_OPERATOR_TAXONOMY,
) -> LocalOrientationDocumentMetadata:
    """Parse one attested candidate and sanitize every public failure."""
    return _sanitized_call(lambda: _parse_candidate_impl(
        candidate, limits=limits,
        operator_taxonomy_path=operator_taxonomy_path,
    ))


def _parse_candidate_impl(
    candidate: object,
    *,
    limits: ParserLimits | None = None,
    operator_taxonomy_path: Path = DEFAULT_OPERATOR_TAXONOMY,
) -> LocalOrientationDocumentMetadata:
    """Revalidate and statically parse one selector-attested candidate."""
    active_limits = limits or ParserLimits()
    try:
        from local_orientation_candidates import (  # type: ignore
            LocalTexCandidate,
            read_candidate_bytes,
        )
    except (ImportError, AttributeError) as exc:
        raise TexParseFault("candidate_selector_unavailable") from exc
    if not isinstance(candidate, LocalTexCandidate):
        raise TexParseFault("candidate_attestation_invalid")
    try:
        data = read_candidate_bytes(candidate, active_limits.max_bytes)
    except Exception:
        raise TexParseFault("candidate_read_rejected") from None
    if not isinstance(data, bytes):
        raise TexParseFault("candidate_read_invalid")
    text, encoding, decode_warnings = _decode_tex(data, active_limits)
    try:
        source = candidate.source
        source_id = str(source.source_id)
        relative_locator = str(candidate.relative_locator)
        modified_ns = int(candidate.modified_ns)
    except (AttributeError, TypeError, ValueError) as exc:
        raise TexParseFault("candidate_attestation_invalid") from exc
    document_id = "doc-" + hashlib.sha256(
        (source_id + "\0" + relative_locator).encode("utf-8")
    ).hexdigest()[:32]
    return _parse_decoded(
        text,
        source_id=source_id,
        document_id=document_id,
        relative_locator=relative_locator,
        size_bytes=len(data),
        modified_ns=modified_ns,
        integrity_sha256=hashlib.sha256(data).hexdigest(),
        encoding=encoding,
        source=source,
        initial_warnings=decode_warnings,
        limits=active_limits,
        operator_patterns=_load_operator_patterns(operator_taxonomy_path),
    )
