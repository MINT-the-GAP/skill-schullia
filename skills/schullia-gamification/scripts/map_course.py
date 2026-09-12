#!/usr/bin/env python3
"""Read-only structural mapper for LiaScript gamification placement.

The mapper never renders or executes course content. It treats synchronized
course data as untrusted text and emits source positions and structural
evidence only.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import urlsplit, urlunsplit
from typing import Any, Sequence


BACKTICK = chr(96)
ContainerContext = tuple[str, int, int, list[dict[str, Any]], int]
DEFAULT_CATALOG = (
    Path(__file__).resolve().parents[1] / "references" / "placement-catalog.json"
)

DEFAULT_CANDIDATE_CLASSES = [
    "start_bootstrap",
    "start_post_tool_block",
    "h2_whole_slide",
    "h2_prefix_or_suffix",
    "dynflex_whole_section",
    "standalone_quiz",
    "solution_reward_tail",
    "flow_text_clue",
    "local_template_target",
    "global_surface_target",
    "lootif_spawn_range",
    "container_visibility_option",
    "collectible_concealment_option",
    "hidden_macro_inside_reveal",
    "optional_secret_or_portal",
    "garden_before_reflection",
    "reflection_optional",
    "submission_or_freeze",
]

DEFAULT_BLOCK_PAIRS = [
    {"kind": "earth", "open": ["Erdhaufen"], "close": ["EndeErdhaufen"]},
    {
        "kind": "plant",
        "open": ["Pflanze", "Blume"],
        "close": ["EndePflanze", "EndeBlume"],
    },
]
DEFAULT_INLINE_MACROS = ["Erdhaufen.inline", "Pflanze.inline", "Blume.inline"]
DEFAULT_LAYER_TOKENS = [
    "erde",
    "pflanze",
    "erde-unsichtbar",
    "erde-zauberstaub",
    "pflanze-unsichtbar",
    "pflanze-zauberstaub",
]
DEFAULT_LAYER_CARRIERS = [
    "Energiekiste",
    "Energietruhe",
    "Schatztruhe",
    "Diamanttruhe",
    "Diamantentruhe",
    "Schluessel",
    "Puzzleteil",
    "Lupe",
    "Schaufel",
    "Giesskanne",
]

COMMONMARK_TYPE6_HTML_TAGS = frozenset(
    {
        "address", "article", "aside", "base", "basefont", "blockquote",
        "body", "caption", "center", "col", "colgroup", "dd", "details",
        "dialog", "dir", "div", "dl", "dt", "fieldset", "figcaption",
        "figure", "footer", "form", "frame", "frameset", "h1", "h2",
        "h3", "h4", "h5", "h6", "head", "header", "hr", "html",
        "iframe", "legend", "li", "link", "main", "menu", "menuitem",
        "nav", "noframes", "ol", "optgroup", "option", "p", "param",
        "search", "section", "summary", "table", "tbody", "td", "tfoot",
        "th", "thead", "title", "tr", "track", "ul",
    }
)

COMMONMARK_TYPE1_CLOSER = re.compile(
    r"</(?:pre|script|style|textarea)>", re.IGNORECASE
)
COMMONMARK_TYPE1_TAGS = frozenset(
    {"pre", "script", "style", "textarea"}
)


def _list_marker_can_interrupt(marker: str, content: str) -> bool:
    """Apply the CommonMark paragraph-interruption rule to one list item."""

    return bool(content.strip(" \t")) and (
        not marker[0].isdigit() or int(marker[:-1]) == 1
    )


def _list_markers_same_type(first: str, second: str) -> bool:
    """Compare CommonMark list type, ignoring an ordered start number."""

    first_ordered = first[0].isdigit()
    second_ordered = second[0].isdigit()
    if first_ordered or second_ordered:
        return first_ordered and second_ordered and first[-1] == second[-1]
    return first == second


def _is_setext_underline(value: str) -> bool:
    """Return whether a line is a one-or-more-character Setext underline."""

    return re.fullmatch(r" {0,3}(?:=+|-+)[ \t]*", value) is not None


def _is_thematic_break(value: str) -> bool:
    """Recognize three or more matching CommonMark break markers."""

    indentation = re.match(r" {0,3}", value)
    assert indentation is not None
    content = value[indentation.end() :]
    if not content or content[0] not in "-*_":
        return False
    marker = content[0]
    compact = content.replace(" ", "").replace("\t", "")
    return len(compact) >= 3 and all(char == marker for char in compact)


def _is_ascii_punctuation(character: str) -> bool:
    """Return CommonMark's ASCII-punctuation character class."""

    if len(character) != 1:
        return False
    codepoint = ord(character)
    return (
        0x21 <= codepoint <= 0x2F
        or 0x3A <= codepoint <= 0x40
        or 0x5B <= codepoint <= 0x60
        or 0x7B <= codepoint <= 0x7E
    )


def _logical_line_ending_end(value: str, cursor: int) -> int | None:
    """Return the end of one LF, CR or CRLF line ending."""

    if cursor >= len(value) or value[cursor] not in "\r\n":
        return None
    if value.startswith("\r\n", cursor):
        return cursor + 2
    return cursor + 1


def _spaces_tabs_end(value: str, cursor: int) -> int:
    while cursor < len(value) and value[cursor] in " \t":
        cursor += 1
    return cursor


def _link_reference_title_end(value: str, cursor: int) -> int | None:
    """Return the end of one CommonMark link title, including delimiters."""

    if cursor >= len(value) or value[cursor] not in (chr(34), chr(39), "("):
        return None
    opener = value[cursor]
    closer = ")" if opener == "(" else opener
    cursor += 1
    while cursor < len(value):
        character = value[cursor]
        if (
            character == chr(92)
            and cursor + 1 < len(value)
            and _is_ascii_punctuation(value[cursor + 1])
        ):
            cursor += 2
            continue
        if character == closer:
            return cursor + 1
        if opener == "(" and character == "(":
            return None
        line_end = _logical_line_ending_end(value, cursor)
        if line_end is not None:
            next_end = line_end
            while next_end < len(value) and value[next_end] not in "\r\n":
                next_end += 1
            if not value[line_end:next_end].strip(" \t"):
                return None
            cursor = line_end
            continue
        cursor += 1
    return None


def _link_reference_destination_end(value: str, cursor: int) -> int | None:
    """Return the end of one exact CommonMark link destination."""

    if cursor >= len(value):
        return None
    if value[cursor] == "<":
        cursor += 1
        while cursor < len(value):
            character = value[cursor]
            if (
                character == chr(92)
                and cursor + 1 < len(value)
                and _is_ascii_punctuation(value[cursor + 1])
            ):
                cursor += 2
                continue
            if character in "\r\n<":
                return None
            if character == ">":
                return cursor + 1
            cursor += 1
        return None

    destination_start = cursor
    parentheses = 0
    while cursor < len(value):
        character = value[cursor]
        codepoint = ord(character)
        if character == " " or codepoint < 0x20 or codepoint == 0x7F:
            break
        if (
            character == chr(92)
            and cursor + 1 < len(value)
            and _is_ascii_punctuation(value[cursor + 1])
        ):
            cursor += 2
            continue
        if character == "(":
            parentheses += 1
        elif character == ")":
            if parentheses == 0:
                return None
            parentheses -= 1
        cursor += 1
    if cursor == destination_start or parentheses:
        return None
    return cursor


def _link_reference_definition_end(value: str) -> int | None:
    """Return the end of a leading CommonMark link reference definition.

    value is the accumulated logical paragraph text. The returned end is
    before the line ending following the definition, so callers can retain any
    subsequent paragraph text. Backslash escapes apply only to ASCII
    punctuation and the 999-character label limit counts source characters.
    """

    cursor = 0
    while cursor < min(3, len(value)) and value[cursor] == " ":
        cursor += 1
    if cursor >= len(value) or value[cursor] != "[":
        return None

    label_start = cursor + 1
    cursor = label_start
    label_has_nonspace = False
    while cursor < len(value):
        character = value[cursor]
        if (
            character == chr(92)
            and cursor + 1 < len(value)
            and _is_ascii_punctuation(value[cursor + 1])
        ):
            label_has_nonspace = label_has_nonspace or (
                value[cursor + 1] not in " \t\r\n"
            )
            cursor += 2
            continue
        if character == "[":
            return None
        if character == "]":
            break
        label_has_nonspace = label_has_nonspace or (
            character not in " \t\r\n"
        )
        cursor += 1
        if cursor - label_start > 999:
            return None
    if (
        cursor >= len(value)
        or cursor - label_start > 999
        or not label_has_nonspace
        or cursor + 1 >= len(value)
        or value[cursor + 1] != ":"
    ):
        return None

    cursor = _spaces_tabs_end(value, cursor + 2)
    line_end = _logical_line_ending_end(value, cursor)
    if line_end is not None:
        cursor = _spaces_tabs_end(value, line_end)
    destination_end = _link_reference_destination_end(value, cursor)
    if destination_end is None:
        return None

    cursor = _spaces_tabs_end(value, destination_end)
    destination_line_end = cursor
    line_end = _logical_line_ending_end(value, cursor)
    if line_end is not None:
        title_cursor = _spaces_tabs_end(value, line_end)
        if (
            title_cursor < len(value)
            and value[title_cursor] in (chr(34), chr(39), "(")
        ):
            title_end = _link_reference_title_end(value, title_cursor)
            if title_end is not None:
                trailing_end = _spaces_tabs_end(value, title_end)
                if (
                    trailing_end == len(value)
                    or _logical_line_ending_end(value, trailing_end)
                    is not None
                ):
                    return trailing_end
        return destination_line_end

    if cursor == len(value):
        return cursor
    if cursor == destination_end:
        return None
    title_end = _link_reference_title_end(value, cursor)
    if title_end is None:
        return None
    trailing_end = _spaces_tabs_end(value, title_end)
    if (
        trailing_end != len(value)
        and _logical_line_ending_end(value, trailing_end) is None
    ):
        return None
    return trailing_end


def _is_link_reference_definition(value: str) -> bool:
    """Recognize one complete CommonMark link reference definition."""

    end = _link_reference_definition_end(value)
    return end is not None and end == len(value)


def _liascript_fence_decorators(info: str) -> bool:
    """Recognize macro-only decorators after an optional language token.

    LiaScript permits backtick-quoted macro arguments on a fence opener.
    Limit that extension to complete macro calls so ordinary CommonMark info
    strings containing backticks do not accidentally become code fences.
    """

    prefix = re.match(r"[ \t]*(?:[^\s@`]+[ \t]+)?(?=@)", info)
    if prefix is None:
        return False
    cursor = prefix.end()
    while cursor < len(info):
        parsed = _parse_macro_at(info, cursor, len(info))
        if parsed is None:
            return False
        _, macro_end, _ = parsed
        next_cursor = _spaces_tabs_end(info, macro_end)
        if next_cursor == len(info):
            return True
        if next_cursor == macro_end:
            return False
        cursor = next_cursor
    return False


def _fence_opener_match(value: str) -> re.Match[str] | None:
    """Return a CommonMark opener or LiaScript macro-decorated opener."""

    match = re.match(
        r"^ {0,3}(" + re.escape(BACKTICK) + r"{3,}|~{3,})(.*)$",
        value,
    )
    if match is None:
        return None
    if (
        match.group(1)[0] == BACKTICK
        and BACKTICK in match.group(2)
        and not _liascript_fence_decorators(match.group(2))
    ):
        return None
    return match


def _source_column(text: str, cursor: int) -> int:
    """Return the CommonMark visual column at one source boundary."""

    return len(text[:cursor].expandtabs(4))


def _consume_prefix_columns(
    text: str,
    cursor: int,
    virtual_indent: int,
    limit: int,
) -> tuple[int, int, int]:
    """Consume at most ``limit`` visual whitespace columns.

    A tab is one source character but can straddle a container boundary.  The
    unconsumed columns of such a tab are returned as ``virtual_indent`` so the
    following quote/list component or leaf block still sees them.
    """

    consumed = 0
    if virtual_indent:
        take = min(virtual_indent, limit)
        virtual_indent -= take
        consumed += take
    while consumed < limit and cursor < len(text):
        character = text[cursor]
        if character == " ":
            width = 1
        elif character == "\t":
            width = 4 - (_source_column(text, cursor) % 4)
        else:
            break
        take = min(width, limit - consumed)
        cursor += 1
        consumed += take
        virtual_indent += width - take
        if width > take:
            break
    return cursor, virtual_indent, consumed


def _fold(value: str) -> str:
    value = value.casefold().replace("ß", "ss")
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )


def _normalize_url(value: str) -> str:
    value = value.strip()
    try:
        parts = urlsplit(value)
    except ValueError:
        return value
    if not parts.scheme or not parts.netloc:
        return value
    return urlunsplit(
        (
            parts.scheme.casefold(),
            parts.netloc.casefold(),
            parts.path,
            parts.query,
            parts.fragment,
        )
    )


class SourceMap:
    """Coordinate conversion for one immutable decoded source string."""

    def __init__(self, raw_bytes: bytes, path: Path | None = None) -> None:
        self.raw_bytes = raw_bytes
        self.path = path
        if raw_bytes.startswith(b"\xef\xbb\xbf"):
            self.bom_bytes = 3
            self.text = raw_bytes[3:].decode("utf-8")
        else:
            self.bom_bytes = 0
            self.text = raw_bytes.decode("utf-8")
        # CommonMark replaces NUL before parsing.  Keep the immutable decoded
        # source for raw spans/byte coordinates and expose a same-length
        # lexical shadow for every recognizer.
        self.lex_text = self.text.replace("\x00", "\ufffd")
        self.nul_offsets = [
            index for index, char in enumerate(self.text) if char == "\x00"
        ]

        byte_offsets = [self.bom_bytes]
        current = self.bom_bytes
        for char in self.text:
            current += len(char.encode("utf-8"))
            byte_offsets.append(current)
        self.byte_offsets = byte_offsets

        self.line_starts = [0]
        for match in re.finditer("\n", self.text):
            self.line_starts.append(match.end())

        self.lines: list[dict[str, Any]] = []
        for index, start in enumerate(self.line_starts):
            end_with_eol = (
                self.line_starts[index + 1]
                if index + 1 < len(self.line_starts)
                else len(self.text)
            )
            end = end_with_eol
            while end > start and self.text[end - 1] in "\r\n":
                end -= 1
            self.lines.append(
                {
                    "number": index + 1,
                    "start": start,
                    "end": end,
                    "end_with_eol": end_with_eol,
                    "text": self.lex_text[start:end],
                }
            )

    def point(self, char_offset: int) -> dict[str, int]:
        char_offset = max(0, min(char_offset, len(self.text)))
        line_index = bisect_right(self.line_starts, char_offset) - 1
        line_index = max(0, min(line_index, len(self.line_starts) - 1))
        return {
            "char": char_offset,
            "byte": self.byte_offsets[char_offset],
            "line": line_index + 1,
            "column": char_offset - self.line_starts[line_index] + 1,
        }

    def span(
        self, start: int, end: int, *, include_raw: bool = False
    ) -> dict[str, Any]:
        start_point = self.point(start)
        end_point = self.point(end)
        result: dict[str, Any] = {
            "char_start": start,
            "char_end": end,
            "byte_start": start_point["byte"],
            "byte_end": end_point["byte"],
            "line_start": start_point["line"],
            "column_start": start_point["column"],
            "line_end": end_point["line"],
            "column_end": end_point["column"],
        }
        if include_raw:
            result["raw"] = self.text[start:end]
        return result

    def line_for_offset(self, char_offset: int) -> dict[str, Any]:
        line_index = bisect_right(self.line_starts, char_offset) - 1
        return self.lines[max(0, min(line_index, len(self.lines) - 1))]


class _RelaxedDataParser:
    """Tiny parser for the historical unquoted catalog snapshot."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def parse(self) -> Any:
        value = self._value()
        self._space()
        if self.pos != len(self.text):
            raise ValueError(f"unexpected catalog content at character {self.pos}")
        return value

    def _space(self) -> None:
        while self.pos < len(self.text):
            if self.text[self.pos].isspace():
                self.pos += 1
                continue
            if self.text.startswith("//", self.pos):
                newline = self.text.find("\n", self.pos)
                self.pos = len(self.text) if newline < 0 else newline + 1
                continue
            break

    def _value(self) -> Any:
        self._space()
        if self.pos >= len(self.text):
            raise ValueError("unexpected end of catalog")
        char = self.text[self.pos]
        if char == "{":
            return self._object()
        if char == "[":
            return self._array()
        if char in (chr(34), chr(39)):
            return self._string()
        token = self._bare()
        folded = token.casefold()
        if folded == "true":
            return True
        if folded == "false":
            return False
        if folded == "null":
            return None
        if re.fullmatch(r"-?(?:0|[1-9]\d*)", token):
            return int(token)
        if re.fullmatch(r"-?(?:0|[1-9]\d*)\.\d+", token):
            return float(token)
        return token

    def _object(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        self.pos += 1
        while True:
            self._space()
            if self.pos < len(self.text) and self.text[self.pos] == "}":
                self.pos += 1
                return result
            if self.pos >= len(self.text):
                raise ValueError("unterminated catalog object")
            key = (
                self._string()
                if self.text[self.pos] in (chr(34), chr(39))
                else self._bare()
            )
            self._space()
            if self.pos >= len(self.text) or self.text[self.pos] != ":":
                raise ValueError(f"missing colon after catalog key {key!r}")
            self.pos += 1
            result[str(key)] = self._value()
            self._space()
            if self.pos < len(self.text) and self.text[self.pos] == ",":
                self.pos += 1
                continue
            if self.pos < len(self.text) and self.text[self.pos] == "}":
                self.pos += 1
                return result
            raise ValueError(f"missing comma in catalog object at {self.pos}")

    def _array(self) -> list[Any]:
        result: list[Any] = []
        self.pos += 1
        while True:
            self._space()
            if self.pos < len(self.text) and self.text[self.pos] == "]":
                self.pos += 1
                return result
            if self.pos >= len(self.text):
                raise ValueError("unterminated catalog array")
            result.append(self._value())
            self._space()
            if self.pos < len(self.text) and self.text[self.pos] == ",":
                self.pos += 1
                continue
            if self.pos < len(self.text) and self.text[self.pos] == "]":
                self.pos += 1
                return result
            raise ValueError(f"missing comma in catalog array at {self.pos}")

    def _string(self) -> str:
        quote = self.text[self.pos]
        self.pos += 1
        chars: list[str] = []
        while self.pos < len(self.text):
            char = self.text[self.pos]
            self.pos += 1
            if char == quote:
                return "".join(chars)
            if char == chr(92) and self.pos < len(self.text):
                escaped = self.text[self.pos]
                self.pos += 1
                translations = {
                    "n": "\n",
                    "r": "\r",
                    "t": "\t",
                    chr(92): chr(92),
                    chr(34): chr(34),
                    chr(39): chr(39),
                }
                chars.append(translations.get(escaped, escaped))
            else:
                chars.append(char)
        raise ValueError("unterminated catalog string")

    def _bare(self) -> str:
        self._space()
        start = self.pos
        while self.pos < len(self.text):
            if self.text[self.pos].isspace() or self.text[self.pos] in "{}[]:,":
                break
            self.pos += 1
        if self.pos == start:
            raise ValueError(f"expected catalog token at {self.pos}")
        return self.text[start:self.pos]


def load_catalog(path: Path | str = DEFAULT_CATALOG) -> dict[str, Any]:
    catalog_path = Path(path)
    text = catalog_path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = _RelaxedDataParser(text).parse()
    if not isinstance(data, dict):
        raise ValueError("placement catalog root must be an object")
    return data


def _contains(interval: dict[str, Any], position: int, *, strict: bool = False) -> bool:
    span = interval["span"]
    if strict:
        return span["char_start"] < position < span["char_end"]
    return span["char_start"] <= position < span["char_end"]


def _covered(
    position: int,
    intervals: Sequence[dict[str, Any]],
    kinds: set[str] | None = None,
) -> bool:
    return any(
        (kinds is None or item.get("kind") in kinds) and _contains(item, position)
        for item in intervals
    )


def _overlaps(
    start: int, end: int, intervals: Sequence[dict[str, Any]]
) -> bool:
    return any(
        start < item["span"]["char_end"] and item["span"]["char_start"] < end
        for item in intervals
    )


def _header(sm: SourceMap) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    match = re.match(r"^[ \t]*<!--", sm.lex_text)
    if not match:
        return None, []
    close_start = sm.lex_text.find("-->", match.end())
    if close_start < 0:
        return None, [{"code": "unterminated_main_header", "line": 1}]
    end = close_start + 3
    header: dict[str, Any] = {
        "span": sm.span(match.start(), end),
        "directives": [],
        "imports": [],
    }
    directive_re = re.compile(r"^[ \t]*([A-Za-z][\w-]*):[ \t]*(.*)$")
    for line in sm.lines:
        if line["start"] >= end:
            break
        line_match = directive_re.match(line["text"])
        if not line_match:
            continue
        key, value = line_match.groups()
        value_start = line["start"] + line_match.start(2)
        value_end = line["start"] + line_match.end(2)
        directive = {
            "key": key,
            "key_normalized": key.casefold(),
            "value": value,
            "span": sm.span(line["start"], line["end"], include_raw=True),
            "value_span": sm.span(value_start, value_end),
            "order": len(header["directives"]),
        }
        header["directives"].append(directive)
        if key.casefold() == "import":
            url = value.strip()
            header["imports"].append(
                {
                    "url": url,
                    "normalized_url": _normalize_url(url),
                    "order": len(header["imports"]),
                    "span": directive["span"],
                }
            )

    loot_indexes = [
        item["order"]
        for item in header["imports"]
        if "lia-loot" in item["normalized_url"].casefold()
    ]
    loot_index = loot_indexes[0] if loot_indexes else None
    for item in header["imports"]:
        if loot_index is None:
            item["relative_to_loot"] = "loot_absent"
        elif item["order"] < loot_index:
            item["relative_to_loot"] = "before"
        elif item["order"] > loot_index:
            item["relative_to_loot"] = "after"
        else:
            item["relative_to_loot"] = "self"
    header["loot_import_orders"] = loot_indexes

    imports = header["imports"]
    slots: list[dict[str, Any]] = []
    for rank in range(len(imports) + 1):
        if not imports:
            position = close_start
        elif rank < len(imports):
            position = imports[rank]["span"]["char_start"]
        else:
            previous_line = sm.line_for_offset(
                imports[-1]["span"]["char_start"]
            )
            position = previous_line["end_with_eol"]
        previous = imports[rank - 1] if rank else None
        following = imports[rank] if rank < len(imports) else None
        position_kind = (
            "before_first"
            if rank == 0
            else "after_last"
            if rank == len(imports)
            else "between"
        )
        slots.append(
            {
                "kind": "import_slot",
                "slot_index": rank,
                "rank": rank,
                "position_kind": position_kind,
                "span": sm.span(position, position),
                "insertion_line": sm.point(position)["line"],
                "before_import_order": (
                    following["order"] if following is not None else None
                ),
                "after_import_order": (
                    previous["order"] if previous is not None else None
                ),
                "adjacent_imports": {
                    "previous": (
                        {
                            "order": previous["order"],
                            "url": previous["url"],
                        }
                        if previous is not None
                        else None
                    ),
                    "next": (
                        {
                            "order": following["order"],
                            "url": following["url"],
                        }
                        if following is not None
                        else None
                    ),
                },
            }
        )
    header["import_slots"] = slots
    return header, []


def _find_fences(
    sm: SourceMap,
    header_end: int,
    container_contexts: dict[int, ContainerContext] | None = None,
    excluded: Sequence[dict[str, Any]] = (),
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fences: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    active: dict[str, Any] | None = None
    def finish_unclosed(end: int) -> None:
        nonlocal active
        assert active is not None
        fence = {
            key: value
            for key, value in active.items()
            if key
            not in {
                "start",
                "container_end",
                "components",
            }
        }
        fence["close_line"] = None
        fence["closed"] = False
        fence["span"] = sm.span(active["start"], end)
        fences.append(fence)
        diagnostics.append(
            {"code": "unterminated_fence", "line": active["open_line"]}
        )
        active = None

    for line in sm.lines:
        if line["end_with_eol"] <= header_end:
            continue
        if (
            active is not None
            and line["start"] >= active["container_end"]
        ):
            finish_unclosed(active["container_end"])
        if active is None:
            context = (
                container_contexts.get(line["number"])
                if container_contexts is not None
                else None
            )
            if context is None:
                (
                    view,
                    view_offset,
                    quote_depth,
                    components,
                    virtual_indent,
                ) = _raw_html_container_parts(line["text"])
            else:
                (
                    view,
                    view_offset,
                    quote_depth,
                    components,
                    virtual_indent,
                ) = context
            list_indent = sum(
                int(component["content_indent"])
                for component in components
                if component["kind"] == "list"
            )
            normalized_view = " " * virtual_indent + view
            match = _fence_opener_match(normalized_view)
            if not match:
                continue
            candidate_start = (
                line["start"]
                + view_offset
                + match.start(1)
                - virtual_indent
            )
            if _covered(candidate_start, excluded):
                continue
            marker = match.group(1)
            active = {
                "kind": "fence",
                "marker": marker[0],
                "length": len(marker),
                "info": match.group(2).strip(),
                "start": line["start"],
                "open_line": line["number"],
                "info_start": (
                    line["start"]
                    + view_offset
                    + match.start(2)
                    - virtual_indent
                ),
                "open_end": line["end"],
                "blockquote_depth": quote_depth,
                "list_indent": list_indent,
                "components": [dict(component) for component in components],
            }
            active["container_end"] = _raw_html_container_end(
                sm,
                line,
                view_offset,
                quote_depth,
                active["components"],
            )
            continue
        matched, view_offset, virtual_indent = _consume_raw_html_container(
            line["text"], active["components"]
        )
        if matched != len(active["components"]):
            continue
        view = " " * virtual_indent + line["text"][view_offset:]
        close_pattern = (
            r"^ {0,3}"
            + re.escape(active["marker"])
            + "{"
            + str(active["length"])
            + r",}[ \t]*$"
        )
        close_match = re.match(close_pattern, view)
        if close_match:
            active["end"] = line["end_with_eol"]
            active["close_line"] = line["number"]
            active["closed"] = True
            fence = {
                key: value
                for key, value in active.items()
                if key
                not in {
                    "start",
                    "end",
                    "container_end",
                    "components",
                }
            }
            fence["span"] = sm.span(active["start"], active["end"])
            fences.append(fence)
            active = None
    if active is not None:
        finish_unclosed(min(len(sm.text), active["container_end"]))
    return fences, diagnostics


def _find_indented_code(
    sm: SourceMap,
    header_end: int,
    excluded: Sequence[dict[str, Any]] = (),
    container_contexts: dict[int, ContainerContext] | None = None,
) -> list[dict[str, Any]]:
    ranges: list[dict[str, Any]] = []
    active_first: dict[str, Any] | None = None
    active_last: dict[str, Any] | None = None
    active_container_signature: tuple[tuple[Any, ...], ...] | None = None
    paragraph_open = False
    paragraph_container_signature: tuple[tuple[Any, ...], ...] | None = None
    html_blank_block_end: int | None = None
    if container_contexts is None:
        container_contexts = _raw_html_container_contexts(
            sm, header_end, excluded
        )

    def indentation(
        value: str, initial_column: int
    ) -> tuple[int, int]:
        """Return leading indentation columns/chars at CommonMark tab stops."""

        column = initial_column
        cursor = 0
        while cursor < len(value):
            character = value[cursor]
            if character == " ":
                column += 1
            elif character == "\t":
                column += 4 - (column % 4)
            else:
                break
            cursor += 1
        return column - initial_column, cursor

    def type6_html_start(
        value: str, initial_column: int, virtual_indent: int
    ) -> bool:
        columns, cursor = indentation(value, initial_column)
        columns += virtual_indent
        if columns > 3:
            return False
        content = value[cursor:]
        match = re.match(
            r"</?([A-Za-z][A-Za-z0-9-]*)(?=[ \t]|/?>|$)",
            content,
        )
        return bool(
            match
            and match.group(1).casefold() in COMMONMARK_TYPE6_HTML_TAGS
        )

    def type7_html_start(
        value: str,
        initial_column: int,
        virtual_indent: int,
        paragraph_is_open: bool,
    ) -> bool:
        columns, cursor = indentation(value, initial_column)
        columns += virtual_indent
        return bool(
            columns <= 3
            and not paragraph_is_open
            and _is_complete_html_tag_line(value[cursor:])
        )

    def starts_nonparagraph_block(
        value: str,
        initial_column: int,
        virtual_indent: int,
        paragraph_is_open: bool,
    ) -> bool:
        columns, cursor = indentation(value, initial_column)
        columns += virtual_indent
        if columns > 3:
            return False
        content = value[cursor:]
        if type6_html_start(value, initial_column, virtual_indent):
            return True
        if paragraph_is_open and _is_setext_underline(content):
            return True
        if _fence_opener_match(content) is not None:
            return True
        if _is_thematic_break(content):
            return True
        if (
            not paragraph_is_open
            and _is_link_reference_definition(content)
        ):
            return True
        return bool(
            re.match(
                r"^(?:"
                r"#{1,6}(?:[ \t]+|$)"
                r"|<(?i:pre|script|style|textarea)(?=[ \t>]|$)"
                r"|<!--|<\?|<!\[CDATA\[|<![A-Za-z]"
                r"|\|"
                r")",
                content,
                flags=re.UNICODE,
            )
        )

    def flush() -> None:
        nonlocal active_first, active_last, active_container_signature
        if active_first is None or active_last is None:
            return
        ranges.append(
            {
                "kind": "indented_code",
                "open_line": active_first["number"],
                "close_line": active_last["number"],
                "span": sm.span(
                    active_first["start"], active_last["end_with_eol"]
                ),
            }
        )
        active_first = None
        active_last = None
        active_container_signature = None

    for line in sm.lines:
        if line["end_with_eol"] <= header_end:
            continue
        line_owners = [
            item for item in excluded if _contains(item, line["start"])
        ]
        if line_owners:
            flush()
            if any(
                item.get("block_start") is not False
                for item in line_owners
            ):
                paragraph_open = False
                paragraph_container_signature = None
            continue
        (
            view,
            offset,
            quote_depth,
            container_components,
            virtual_indent,
        ) = container_contexts[line["number"]]
        container_signature = _container_component_signature(
            container_components
        )
        if (
            paragraph_open
            and paragraph_container_signature != container_signature
        ):
            paragraph_open = False
            paragraph_container_signature = None

        if html_blank_block_end is not None:
            if line["start"] >= html_blank_block_end:
                html_blank_block_end = None
            elif view.strip(" \t"):
                flush()
                paragraph_open = False
                paragraph_container_signature = None
                continue
            else:
                html_blank_block_end = None

        if not view.strip(" \t"):
            if (
                active_first is not None
                and container_signature != active_container_signature
            ):
                flush()
            paragraph_open = False
            paragraph_container_signature = None
            continue

        initial_column = len(line["text"][:offset].expandtabs(4))
        authored_code_columns, _ = indentation(view, initial_column)
        code_columns = virtual_indent + authored_code_columns
        block_view = view
        block_initial_column = initial_column
        block_virtual_indent = virtual_indent

        if code_columns < 4:
            flush()
            is_type6_html = type6_html_start(
                block_view, block_initial_column, block_virtual_indent
            )
            is_type7_html = type7_html_start(
                block_view,
                block_initial_column,
                block_virtual_indent,
                paragraph_open,
            )
            is_blank_html = is_type6_html or is_type7_html
            if is_blank_html:
                html_blank_block_end = _raw_html_container_end(
                    sm,
                    line,
                    offset,
                    quote_depth,
                    container_components,
                )
            if is_blank_html or starts_nonparagraph_block(
                block_view,
                block_initial_column,
                block_virtual_indent,
                paragraph_open,
            ):
                paragraph_open = False
                paragraph_container_signature = None
            elif block_view.strip(" \t"):
                if not paragraph_open:
                    paragraph_open = True
                    paragraph_container_signature = container_signature
            continue
        if (
            active_first is not None
            and container_signature != active_container_signature
        ):
            flush()
        if active_first is None and paragraph_open:
            continue
        if active_first is None:
            active_first = line
            active_container_signature = container_signature
            paragraph_open = False
            paragraph_container_signature = None
        active_last = line
    flush()
    return ranges


def _find_inline_code(
    sm: SourceMap,
    excluded: Sequence[dict[str, Any]],
    header_end: int,
    container_contexts: dict[int, ContainerContext] | None = None,
) -> list[dict[str, Any]]:
    """Find CommonMark code spans, including spans crossing line endings.

    An opening delimiter is a maximal, unescaped run of backticks.  An equally
    long run closes it even when preceded by a backslash, because backslash
    escapes are not processed inside CommonMark code spans.  Soft line breaks
    inside one paragraph are supported, but a code span never consumes a
    following CommonMark/LiaScript block.  Fenced/indented code is supplied in
    ``excluded``.
    """

    result: list[dict[str, Any]] = []
    text = sm.lex_text
    finite_owner_kinds = {"html_tag", "html_autolink"}
    blocking_excluded = [
        item for item in excluded
        if item["kind"] not in finite_owner_kinds
    ]

    def list_interrupts(line_text: str) -> bool:
        candidate = _first_list_interrupt_candidate(line_text)
        return bool(
            candidate
            and _list_marker_can_interrupt(candidate[0], candidate[1])
        )

    def starts_block(line_text: str, virtual_indent: int = 0) -> bool:
        normalized = " " * virtual_indent + line_text
        if not normalized.strip():
            return True
        if _is_setext_underline(normalized):
            return True
        if _raw_html_state_start(normalized) is not None:
            return True
        if list_interrupts(normalized):
            return True
        if _fence_opener_match(normalized) is not None:
            return True
        if _is_thematic_break(normalized):
            return True
        return bool(
            re.match(
                r"^(?:"
                r" {0,3}#{1,6}(?:[ \t]+|$)"
                r"| {0,3}>"
                r"| {0,3}\|"
                r")",
                normalized,
                flags=re.UNICODE,
            )
        )

    def context_for(
        line: dict[str, Any],
    ) -> ContainerContext:
        if container_contexts is not None:
            context = container_contexts.get(line["number"])
            if context is not None:
                return context
        return _raw_html_container_parts(line["text"])

    def component_signature(
        components: Sequence[dict[str, Any]],
    ) -> tuple[tuple[Any, ...], ...]:
        return tuple(
            (
                component["kind"],
                component.get("marker"),
                component.get("content_indent"),
            )
            for component in components
        )

    def explicit_list_interrupts(
        line_text: str, active_components: Sequence[dict[str, Any]]
    ) -> bool:
        # Consume any repeated/indented prefixes of the current container,
        # then parse an arbitrary ordered suffix (list -> quote -> list ...).
        # A physical list marker in that suffix starts new structure only if
        # it may interrupt the running paragraph (bullet, or ordered start 1).
        matched, cursor, virtual_indent = _consume_raw_html_container(
            line_text, active_components
        )
        candidate = _first_list_interrupt_candidate(
            line_text, cursor, virtual_indent
        )
        _, _, _, explicit, _ = _raw_html_container_parts(
            line_text, cursor, virtual_indent
        )
        list_components = [
            component
            for component in explicit
            if component["kind"] == "list"
        ]
        if not list_components:
            return False
        assert candidate is not None
        marker, content, _ = candidate
        if matched < len(active_components):
            return True
        return _list_marker_can_interrupt(marker, content)

    def paragraph_limit(position: int) -> int:
        line = sm.line_for_offset(position)
        line_index = line["number"] - 1
        content, _, _, components, virtual_indent = context_for(line)
        if starts_block(content, virtual_indent):
            return line["end_with_eol"]
        opening_signature = component_signature(components)
        limit = line["end_with_eol"]
        for following in sm.lines[line_index + 1 :]:
            if _covered(following["start"], blocking_excluded):
                return following["start"]
            if explicit_list_interrupts(
                following["text"], components
            ):
                return following["start"]
            (
                following_content,
                _,
                _,
                following_components,
                following_virtual_indent,
            ) = context_for(following)
            if component_signature(following_components) != opening_signature:
                return following["start"]
            if starts_block(
                following_content, following_virtual_indent
            ):
                return following["start"]
            limit = following["end_with_eol"]
        return limit

    index = header_end
    while index < len(text):
        containing = next(
            (item for item in excluded if _contains(item, index)), None
        )
        if containing is not None:
            index = containing["span"]["char_end"]
            continue
        if text[index] != BACKTICK or not _unescaped(text, index):
            index += 1
            continue
        run_end = index + 1
        while run_end < len(text) and text[run_end] == BACKTICK:
            run_end += 1
        delimiter_length = run_end - index
        search_limit = paragraph_limit(index)
        cursor = run_end
        close_end: int | None = None
        while cursor < search_limit:
            containing = next(
                (
                    item for item in blocking_excluded
                    if _contains(item, cursor)
                ),
                None,
            )
            if containing is not None:
                cursor = containing["span"]["char_end"]
                continue
            candidate = text.find(BACKTICK, cursor, search_limit)
            if candidate < 0:
                break
            if _covered(candidate, blocking_excluded):
                cursor = candidate + 1
                continue
            candidate_end = candidate + 1
            while (
                candidate_end < len(text)
                and text[candidate_end] == BACKTICK
            ):
                candidate_end += 1
            if candidate_end - candidate == delimiter_length:
                close_end = candidate_end
                break
            cursor = candidate_end
        if close_end is None:
            index = run_end
            continue
        result.append(
            {
                "kind": "inline_code",
                "span": sm.span(index, close_end),
                "delimiter_length": delimiter_length,
            }
        )
        index = close_end
    return result


def _raw_html_container_parts(
    text: str,
    start_cursor: int = 0,
    start_virtual_indent: int = 0,
    *,
    allow_lists: bool = True,
    stop_after_first_list: bool = False,
) -> ContainerContext:
    cursor = start_cursor
    virtual_indent = start_virtual_indent
    quote_depth = 0
    components: list[dict[str, Any]] = []
    list_marker = re.compile(r"(?:[-+*]|\d{1,9}[.)])")
    while cursor < len(text):
        level_start = cursor
        level_virtual_indent = virtual_indent
        probe, probe_virtual_indent, _ = _consume_prefix_columns(
            text, cursor, virtual_indent, 3
        )

        if (
            probe_virtual_indent == 0
            and probe < len(text)
            and text[probe] == ">"
        ):
            quote_depth += 1
            components.append({"kind": "quote"})
            cursor = probe + 1
            virtual_indent = 0
            if cursor < len(text) and text[cursor] in " \t":
                cursor, virtual_indent, _ = _consume_prefix_columns(
                    text, cursor, virtual_indent, 1
                )
            continue

        if _is_thematic_break(text[level_start:]) and not level_virtual_indent:
            cursor = level_start
            virtual_indent = level_virtual_indent
            break

        if not allow_lists or probe_virtual_indent:
            cursor = level_start
            virtual_indent = level_virtual_indent
            break
        marker = list_marker.match(text, probe)
        if marker is None:
            cursor = level_start
            virtual_indent = level_virtual_indent
            break
        padding_start = marker.end()
        if not text[padding_start:].strip(" \t"):
            # CommonMark permits a blank first item line, with or without
            # authored trailing spaces/tabs.  Its following blocks always use
            # W+1 columns; the blank-line whitespace does not increase that
            # indent (bullet ``-`` => 2, ordered ``1.`` => 3).
            start_column = _source_column(text, level_start) - level_virtual_indent
            marker_end_column = _source_column(text, padding_start)
            cursor = len(text)
            virtual_indent = 0
            components.append(
                {
                    "kind": "list",
                    "content_indent": (
                        marker_end_column - start_column + 1
                    ),
                    "marker": marker.group(0),
                    "marker_offset": marker.start(),
                }
            )
            if stop_after_first_list:
                break
            continue
        if text[padding_start] not in " \t":
            cursor = level_start
            virtual_indent = level_virtual_indent
            break
        padding_end = padding_start
        while padding_end < len(text) and text[padding_end] in " \t":
            padding_end += 1
        before_width = _source_column(text, padding_start)
        after_width = _source_column(text, padding_end)
        padding_width = after_width - before_width
        # CommonMark list padding is one to four columns.  With wider
        # padding, only the first whitespace character belongs to the marker;
        # the remainder stays as content indentation (usually code).
        if padding_width <= 4:
            cursor = padding_end
            virtual_indent = 0
        else:
            cursor, virtual_indent, _ = _consume_prefix_columns(
                text, padding_start, 0, 1
            )
        start_column = _source_column(text, level_start) - level_virtual_indent
        end_column = _source_column(text, cursor) - virtual_indent
        components.append(
            {
                "kind": "list",
                "content_indent": end_column - start_column,
                "marker": marker.group(0),
                "marker_offset": marker.start(),
            }
        )
        if stop_after_first_list:
            break
    return text[cursor:], cursor, quote_depth, components, virtual_indent


def _first_list_interrupt_candidate(
    text: str,
    start_cursor: int = 0,
    start_virtual_indent: int = 0,
) -> tuple[str, str, int] | None:
    view, _, _, components, virtual_indent = _raw_html_container_parts(
        text,
        start_cursor,
        start_virtual_indent,
        stop_after_first_list=True,
    )
    component = next(
        (item for item in components if item["kind"] == "list"), None
    )
    if component is None:
        return None
    return (
        str(component["marker"]),
        " " * virtual_indent + view,
        int(component["marker_offset"]),
    )


def _consume_raw_html_container(
    text: str,
    components: Sequence[dict[str, Any]],
    start_cursor: int = 0,
    start_virtual_indent: int = 0,
) -> tuple[int, int, int]:
    """Consume as many established container prefixes as this line carries."""

    cursor = start_cursor
    virtual_indent = start_virtual_indent
    for component_index, component in enumerate(components):
        component_start = cursor
        component_virtual_indent = virtual_indent
        if component["kind"] == "quote":
            probe, probe_virtual_indent, _ = _consume_prefix_columns(
                text, cursor, virtual_indent, 3
            )
            if (
                probe_virtual_indent
                or probe >= len(text)
                or text[probe] != ">"
            ):
                return (
                    component_index,
                    component_start,
                    component_virtual_indent,
                )
            cursor = probe + 1
            virtual_indent = 0
            if cursor < len(text) and text[cursor] in " \t":
                cursor, virtual_indent, _ = _consume_prefix_columns(
                    text, cursor, virtual_indent, 1
                )
            continue

        required = int(component["content_indent"])
        cursor, virtual_indent, consumed = _consume_prefix_columns(
            text, cursor, virtual_indent, required
        )
        if consumed < required:
            return (
                component_index,
                component_start,
                component_virtual_indent,
            )
    return len(components), cursor, virtual_indent


def _raw_html_state_start(value: str) -> dict[str, Any] | None:
    """Describe an HTML block opener used by the container-state prepass."""

    indentation = re.match(r" {0,3}", value)
    assert indentation is not None
    cursor = indentation.end()
    content = value[cursor:]
    type_one = re.match(
        r"<(?P<tag>pre|script|style|textarea)(?=[ \t>]|$)",
        content,
        flags=re.IGNORECASE,
    )
    if type_one is not None:
        return {
            "kind": "type_one",
            "closer": COMMONMARK_TYPE1_CLOSER,
            "search_start": cursor + type_one.end(),
        }
    if content.startswith("<!--"):
        if content.startswith("<!-->") or content.startswith("<!--->"):
            return {"kind": "finite", "closed": True}
        return {
            "kind": "finite",
            "closer": "-->",
            "search_start": cursor + len("<!--"),
        }
    if content.startswith("<?"):
        return {
            "kind": "finite",
            "closer": "?>",
            "search_start": cursor + len("<?"),
        }
    if content.startswith("<![CDATA["):
        return {
            "kind": "finite",
            "closer": "]]>",
            "search_start": cursor + len("<![CDATA["),
        }
    if re.match(r"<![A-Za-z]", content):
        return {
            "kind": "finite",
            "closer": ">",
            "search_start": cursor + len("<!A"),
        }
    type_six = re.match(
        r"</?([A-Za-z][A-Za-z0-9-]*)(?=[ \t]|/?>|$)", content
    )
    if (
        type_six is not None
        and type_six.group(1).casefold() in COMMONMARK_TYPE6_HTML_TAGS
    ):
        return {"kind": "type_six", "end_on_blank": True}
    return None


def _raw_html_state_closed(state: dict[str, Any], value: str) -> bool:
    if state.get("closed") is True:
        return True
    closer = state.get("closer")
    if closer is None:
        return False
    start = int(state.get("search_start", 0))
    if isinstance(closer, str):
        return value.find(closer, start) >= 0
    return closer.search(value, start) is not None


def _is_complete_html_tag_line(value: str) -> bool:
    """Recognize one complete CommonMark HTML tag plus trailing spaces/tabs."""

    candidate = value.rstrip(" \t")
    if not candidate.startswith("<"):
        return False
    probe = SourceMap(candidate.encode("utf-8"))
    tokens, _ = _scan_html_tags(probe, ())
    return bool(
        len(tokens) == 1
        and tokens[0]["kind"] == "html_tag"
        and (
            tokens[0]["closing"]
            or tokens[0]["tag"] not in COMMONMARK_TYPE1_TAGS
        )
        and tokens[0]["span"]["char_start"] == 0
        and tokens[0]["span"]["char_end"] == len(candidate)
    )


def _raw_html_type_seven_state(
    value: str, paragraph_is_open: bool
) -> dict[str, Any] | None:
    """Return a blank-line HTML-block state for a standalone complete tag."""

    if paragraph_is_open:
        return None
    indentation = re.match(r" {0,3}", value)
    assert indentation is not None
    if not _is_complete_html_tag_line(value[indentation.end() :]):
        return None
    return {"kind": "type_seven", "end_on_blank": True}


def _raw_html_other_block_start(
    value: str, paragraph_is_open: bool = False
) -> bool:
    """Return whether normalized content cannot be a lazy paragraph line."""

    indentation = re.match(r" {0,3}", value)
    assert indentation is not None
    content = value[indentation.end() :]
    if paragraph_is_open and _is_setext_underline(content):
        return True
    if _raw_html_type_seven_state(value, paragraph_is_open) is not None:
        return True
    if _fence_opener_match(content) is not None:
        return True
    if _is_thematic_break(content):
        return True
    if not paragraph_is_open and _is_link_reference_definition(content):
        return True
    return bool(
        re.match(
            r"^(?:"
            r"#{1,6}(?:[ \t]+|$)"
            r"|\|"
            r")",
            content,
            flags=re.UNICODE,
        )
    )


def _raw_html_container_contexts(
    sm: SourceMap,
    header_end: int,
    code_blocks: Sequence[dict[str, Any]] = (),
) -> dict[int, ContainerContext]:
    """Resolve explicit and implicit list/quote prefixes for every body line."""

    contexts: dict[int, ContainerContext] = {}
    active_components: list[dict[str, Any]] = []
    paragraph_open = False
    active_html: dict[str, Any] | None = None
    active_code: dict[str, Any] | None = None
    code_openers = {
        int(item.get("open_line", item["span"]["line_start"])): item
        for item in code_blocks
        if item.get("open_line", item["span"]["line_start"]) is not None
        and item.get("block_start") is not False
    }

    for line in sm.lines:
        if line["end_with_eol"] <= header_end:
            continue
        text = line["text"]
        if (
            active_code is not None
            and line["start"] >= int(active_code["end"])
        ):
            active_code = None
        matched, cursor, virtual_indent = _consume_raw_html_container(
            text, active_components
        )

        if active_code is not None:
            inside = matched == len(active_components)
            if (
                not inside
                and not text[cursor:].strip(" \t")
                and not any(
                    component["kind"] == "quote"
                    for component in active_components[matched:]
                )
            ):
                inside = True
            if inside:
                contexts[line["number"]] = (
                    text[cursor:],
                    cursor,
                    sum(
                        component["kind"] == "quote"
                        for component in active_components
                    ),
                    [dict(component) for component in active_components],
                    virtual_indent,
                )
                if line["end_with_eol"] >= int(active_code["end"]):
                    active_code = None
                paragraph_open = False
                continue
            active_code = None
            active_components = active_components[:matched]
            paragraph_open = False

        if active_html is not None:
            inside = matched == len(active_components)
            if (
                not inside
                and not text[cursor:].strip(" \t")
                and not any(
                    component["kind"] == "quote"
                    for component in active_components[matched:]
                )
            ):
                inside = True
            if inside:
                view = text[cursor:]
                contexts[line["number"]] = (
                    view,
                    cursor,
                    sum(
                        component["kind"] == "quote"
                        for component in active_components
                    ),
                    [dict(component) for component in active_components],
                    virtual_indent,
                )
                if active_html.get("end_on_blank") and not view.strip(
                    " \t"
                ):
                    active_html = None
                elif _raw_html_state_closed(active_html, view):
                    active_html = None
                else:
                    active_html["search_start"] = 0
                paragraph_open = False
                continue
            active_html = None
            active_components = active_components[:matched]
            paragraph_open = False

        matched, cursor, virtual_indent = _consume_raw_html_container(
            text, active_components
        )
        base_components = active_components[:matched]
        remainder = text[cursor:]
        (
            _,
            explicit_end,
            _,
            explicit_components,
            explicit_virtual_indent,
        ) = _raw_html_container_parts(text, cursor, virtual_indent)
        for component in explicit_components:
            if component["kind"] == "list":
                component["item_start_line"] = line["number"]
                component["item_start_char"] = (
                    line["start"] + int(component["marker_offset"])
                )
        if (
            paragraph_open
            and explicit_components
            and explicit_components[0]["kind"] == "list"
        ):
            first_marker = str(explicit_components[0]["marker"])
            candidate = _first_list_interrupt_candidate(
                text, cursor, virtual_indent
            )
            assert candidate is not None
            container_closed = matched < len(active_components)
            same_type_sibling = bool(
                matched < len(active_components)
                and active_components[matched]["kind"] == "list"
                and _list_markers_same_type(
                    str(active_components[matched]["marker"]),
                    first_marker,
                )
            )
            list_can_interrupt = container_closed or same_type_sibling or (
                _list_marker_can_interrupt(
                    first_marker, candidate[1]
                )
            )
            if not list_can_interrupt:
                explicit_end = cursor
                explicit_components = []

        lazy = False
        if matched == len(active_components):
            line_components = [
                *base_components,
                *explicit_components,
            ]
            content_offset = explicit_end
            content_virtual_indent = explicit_virtual_indent
        elif not remainder.strip(" \t"):
            missing = active_components[matched:]
            if any(component["kind"] == "quote" for component in missing):
                first_quote = next(
                    index
                    for index, component in enumerate(missing)
                    if component["kind"] == "quote"
                )
                line_components = [
                    *base_components,
                    *missing[:first_quote],
                ]
                content_offset = cursor
                content_virtual_indent = virtual_indent
            else:
                line_components = list(active_components)
                content_offset = cursor
                content_virtual_indent = virtual_indent
        elif explicit_components:
            line_components = [
                *base_components,
                *explicit_components,
            ]
            content_offset = explicit_end
            content_virtual_indent = explicit_virtual_indent
        elif paragraph_open and not (
            _raw_html_state_start(" " * virtual_indent + remainder)
            or _raw_html_other_block_start(
                " " * virtual_indent + remainder,
                paragraph_is_open=True,
            )
        ):
            line_components = list(active_components)
            content_offset = cursor
            content_virtual_indent = virtual_indent
            lazy = True
        else:
            line_components = list(base_components)
            content_offset = cursor
            content_virtual_indent = virtual_indent

        view = text[content_offset:]
        contexts[line["number"]] = (
            view,
            content_offset,
            sum(
                component["kind"] == "quote"
                for component in line_components
            ),
            [dict(component) for component in line_components],
            content_virtual_indent,
        )
        active_components = line_components
        if explicit_components:
            # A real new quote/list container interrupts the paragraph that
            # was active in its parent.  Repeated prefixes of the current
            # container were consumed above and do not reach this branch.
            paragraph_open = False

        code_opener = code_openers.get(line["number"])
        if code_opener is not None:
            paragraph_open = False
            active_html = None
            code_end = int(code_opener["span"]["char_end"])
            if code_end > line["end_with_eol"]:
                active_code = {
                    "end": code_end,
                }
            continue

        if not view.strip(" \t"):
            paragraph_open = False
            continue
        normalized_view = " " * content_virtual_indent + view
        html_state = _raw_html_state_start(normalized_view)
        if html_state is not None and "search_start" in html_state:
            html_state["search_start"] = max(
                0, int(html_state["search_start"]) - content_virtual_indent
            )
        if html_state is None:
            html_state = _raw_html_type_seven_state(
                normalized_view, paragraph_open
            )
        if html_state is not None:
            paragraph_open = False
            if not _raw_html_state_closed(html_state, view):
                html_state["search_start"] = 0
                active_html = html_state
            continue
        if lazy:
            paragraph_open = True
        elif _raw_html_other_block_start(
            normalized_view, paragraph_is_open=paragraph_open
        ):
            paragraph_open = False
        else:
            paragraph_open = True
    return contexts


def _raw_html_container_view(text: str) -> ContainerContext:
    """Return the complete explicit container context for one source line."""

    return _raw_html_container_parts(text)


def _raw_html_container_end(
    sm: SourceMap,
    opening_line: dict[str, Any],
    view_offset: int,
    quote_depth: int,
    components: Sequence[dict[str, Any]] | None = None,
) -> int:
    """Return the exclusive end of the opener's parent container block."""

    if components is None:
        (
            _,
            parsed_offset,
            parsed_quote_depth,
            parsed_components,
            _,
        ) = (
            _raw_html_container_parts(opening_line["text"])
        )
        if parsed_offset != view_offset or parsed_quote_depth != quote_depth:
            return len(sm.text)
        components = parsed_components
    if not components:
        return len(sm.text)

    has_quote = any(
        component["kind"] == "quote" for component in components
    )
    for line in sm.lines[opening_line["number"] :]:
        if not has_quote and not line["text"].strip(" \t"):
            continue
        matched, cursor, _ = _consume_raw_html_container(
            line["text"], components
        )
        if matched < len(components):
            remaining = components[matched:]
            blank_list_continuation = (
                not line["text"][cursor:].strip(" \t")
                and not any(
                    item["kind"] == "quote" for item in remaining
                )
            )
            if blank_list_continuation:
                continue
            return line["start"]
    return len(sm.text)


def _container_component_signature(
    components: Sequence[dict[str, Any]],
) -> tuple[tuple[Any, ...], ...]:
    """Describe one concrete container path, including list-item identity."""

    return tuple(
        (
            item["kind"],
            item.get("marker"),
            item.get("content_indent"),
            item.get("item_start_char"),
        )
        for item in components
    )


def _inline_paragraph_end(
    sm: SourceMap,
    start: int,
    container_contexts: dict[int, ContainerContext],
) -> int:
    """Return the exclusive source end of the opener's inline leaf block."""

    opening_line = sm.line_for_offset(start)
    opening_context = container_contexts.get(
        opening_line["number"],
        _raw_html_container_view(opening_line["text"]),
    )
    opening_view, _, _, opening_components, opening_virtual_indent = (
        opening_context
    )
    opening_normalized = " " * opening_virtual_indent + opening_view
    opening_signature = _container_component_signature(opening_components)
    opening_html_state = _raw_html_state_start(opening_normalized)
    if (
        opening_html_state is not None
        and opening_html_state.get("end_on_blank")
    ):
        for following in sm.lines[opening_line["number"] :]:
            context = container_contexts.get(
                following["number"],
                _raw_html_container_view(following["text"]),
            )
            view, _, _, components, virtual_indent = context
            if (
                _container_component_signature(components)
                != opening_signature
            ):
                return following["start"]
            if not (" " * virtual_indent + view).strip(" \t"):
                return following["start"]
        return len(sm.text)
    if re.match(r" {0,3}#{1,6}(?:[ \t]+|$)", opening_normalized):
        return opening_line["end"]

    for following in sm.lines[opening_line["number"] :]:
        context = container_contexts.get(
            following["number"],
            _raw_html_container_view(following["text"]),
        )
        view, _, _, components, virtual_indent = context
        if _container_component_signature(components) != opening_signature:
            return following["start"]
        normalized = " " * virtual_indent + view
        if not normalized.strip(" \t"):
            return following["start"]
        if (
            _raw_html_state_start(normalized) is not None
            or _raw_html_other_block_start(
                normalized, paragraph_is_open=True
            )
        ):
            return following["start"]
        list_candidate = _first_list_interrupt_candidate(normalized)
        if list_candidate and _list_marker_can_interrupt(
            list_candidate[0], list_candidate[1]
        ):
            return following["start"]
    return len(sm.text)


def _find_link_reference_definitions(
    sm: SourceMap,
    excluded: Sequence[dict[str, Any]],
    header_end: int,
    container_contexts: dict[int, ContainerContext],
) -> list[dict[str, Any]]:
    """Protect leading CommonMark definitions removed from paragraph output."""

    result: list[dict[str, Any]] = []
    paragraph_open = False
    active_html: dict[str, Any] | None = None
    previous_signature: tuple[tuple[Any, ...], ...] | None = None
    line_index = 0
    while line_index < len(sm.lines):
        line = sm.lines[line_index]
        line_index += 1
        if line["end_with_eol"] <= header_end:
            continue
        context = container_contexts.get(
            line["number"],
            _raw_html_container_view(line["text"]),
        )
        view, view_offset, _, components, virtual_indent = context
        signature = _container_component_signature(components)
        if previous_signature is not None and signature != previous_signature:
            paragraph_open = False
        previous_signature = signature

        content_start = line["start"] + view_offset
        owners = [
            item
            for item in excluded
            if _contains(item, content_start)
            or _contains(item, line["start"])
        ]
        if owners:
            if any(item.get("block_start") is not False for item in owners):
                paragraph_open = False
                active_html = None
            continue

        normalized = " " * virtual_indent + view
        if active_html is not None:
            if active_html.get("end_on_blank") and not normalized.strip(
                " \t"
            ):
                active_html = None
            elif _raw_html_state_closed(active_html, normalized):
                active_html = None
            else:
                active_html["search_start"] = 0
            paragraph_open = False
            continue
        if not normalized.strip(" \t"):
            paragraph_open = False
            continue
        html_state = _raw_html_state_start(normalized)
        if html_state is None:
            html_state = _raw_html_type_seven_state(
                normalized, paragraph_open
            )
        if html_state is not None:
            paragraph_open = False
            if not _raw_html_state_closed(html_state, normalized):
                html_state["search_start"] = 0
                active_html = html_state
            continue

        if not paragraph_open:
            indentation = re.match(r" {0,3}", normalized)
            assert indentation is not None
            if (
                indentation.end() < len(normalized)
                and normalized[indentation.end()] == "["
            ):
                source_start = (
                    line["start"]
                    + view_offset
                    + indentation.end()
                    - virtual_indent
                )
                paragraph_end = _inline_paragraph_end(
                    sm, source_start, container_contexts
                )
                logical_lines: list[str] = []
                physical_lines: list[dict[str, Any]] = []
                for candidate in sm.lines[line["number"] - 1 :]:
                    if candidate["start"] >= paragraph_end:
                        break
                    candidate_context = container_contexts.get(
                        candidate["number"],
                        _raw_html_container_view(candidate["text"]),
                    )
                    candidate_view = candidate_context[0]
                    candidate_virtual_indent = candidate_context[4]
                    logical_lines.append(
                        " " * candidate_virtual_indent + candidate_view
                    )
                    physical_lines.append(candidate)
                logical = "\n".join(logical_lines)
                definition_end = _link_reference_definition_end(logical)
                if definition_end is not None:
                    consumed_lines = (
                        logical[:definition_end].count("\n") + 1
                    )
                    last_line = physical_lines[consumed_lines - 1]
                    result.append(
                        {
                            "kind": "link_reference_definition",
                            "block_start": True,
                            "span": sm.span(
                                source_start, last_line["end_with_eol"]
                            ),
                        }
                    )
                    line_index = last_line["number"]
                    last_context = container_contexts.get(
                        last_line["number"],
                        _raw_html_container_view(last_line["text"]),
                    )
                    previous_signature = _container_component_signature(
                        last_context[3]
                    )
                    paragraph_open = False
                    continue

        if (
            _raw_html_state_start(normalized) is not None
            or _raw_html_other_block_start(
                normalized, paragraph_is_open=paragraph_open
            )
        ):
            paragraph_open = False
        else:
            paragraph_open = True
    return result


def _find_raw_html_blocks(
    sm: SourceMap,
    excluded: Sequence[dict[str, Any]],
    header_end: int,
    container_contexts: dict[int, ContainerContext],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Protect complete CommonMark type-1 raw HTML elements."""

    result: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    opener = re.compile(
        r" {0,3}<(?P<tag>pre|script|style|textarea)(?=[ \t]|>|$)",
        re.IGNORECASE,
    )
    for line in sm.lines:
        if line["end_with_eol"] <= header_end:
            continue
        (
            view,
            view_offset,
            quote_depth,
            components,
            virtual_indent,
        ) = container_contexts.get(
            line["number"],
            _raw_html_container_view(line["text"]),
        )
        normalized_view = " " * virtual_indent + view
        match = opener.match(normalized_view)
        if match is None:
            continue
        start = (
            line["start"]
            + view_offset
            + match.start("tag")
            - 1
            - virtual_indent
        )
        if _covered(start, excluded) or not _unescaped(sm.lex_text, start):
            continue
        tag = match.group("tag").casefold()
        closer = COMMONMARK_TYPE1_CLOSER
        search_start = (
            line["start"]
            + view_offset
            + match.end()
            - virtual_indent
        )
        container_end = _raw_html_container_end(
            sm, line, view_offset, quote_depth, components
        )
        close_match = closer.search(sm.lex_text, search_start, container_end)
        end = (
            sm.line_for_offset(close_match.end() - 1)["end_with_eol"]
            if close_match is not None
            else container_end
        )
        result.append(
            {
                "kind": "raw_html",
                "tag": tag,
                "block_start": True,
                "closed": close_match is not None,
                "span": sm.span(start, end),
            }
        )
        if close_match is None:
            diagnostics.append(
                {
                    "code": "unterminated_raw_html",
                    "tag": tag,
                    "line": line["number"],
                }
            )
            continue
    return result, diagnostics


def _find_html_markup(
    sm: SourceMap,
    excluded: Sequence[dict[str, Any]],
    header_end: int,
    container_contexts: dict[int, ContainerContext],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Protect delimiter-based CommonMark raw HTML in source order.

    Complete comments, processing instructions, declarations and CDATA
    sections are inline raw HTML wherever they occur.  An unterminated form is
    protected conservatively through EOF only when its opener starts a
    container-normalized CommonMark block.
    """

    result: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    cursor = header_end
    opener = re.compile(r"<!--|<\?|<!\[CDATA\[|<![A-Za-z]")

    def block_context(
        start: int,
    ) -> tuple[bool, int, int, dict[str, Any]]:
        line = sm.line_for_offset(start)
        (
            view,
            view_offset,
            quote_depth,
            _,
            virtual_indent,
        ) = container_contexts.get(
            line["number"],
            _raw_html_container_view(line["text"]),
        )
        normalized_view = " " * virtual_indent + view
        indentation = re.match(r" {0,3}", normalized_view)
        assert indentation is not None
        normalized_start = (
            line["start"]
            + view_offset
            + indentation.end()
            - virtual_indent
        )
        return normalized_start == start, quote_depth, view_offset, line

    def in_container_prefix(position: int, quote_depth: int) -> bool:
        if quote_depth == 0:
            return False
        line = sm.line_for_offset(position)
        (
            _,
            view_offset,
            line_quote_depth,
            _,
            _,
        ) = container_contexts.get(
            line["number"],
            _raw_html_container_view(line["text"]),
        )
        return (
            line_quote_depth >= quote_depth
            and position < line["start"] + view_offset
        )

    while True:
        match = opener.search(sm.lex_text, cursor)
        if match is None:
            break
        start = match.start()
        if _covered(start, excluded):
            containing = next(
                item for item in excluded if _contains(item, start)
            )
            cursor = containing["span"]["char_end"]
            continue
        marker = match.group(0)
        if not _unescaped(sm.lex_text, start):
            cursor = start + 1
            continue
        short_comment_end: int | None = None
        if marker == "<!--":
            kind = "html_comment"
            form = "comment"
            terminator = "-->"
            if sm.lex_text.startswith("<!-->", start):
                short_comment_end = start + len("<!-->")
            elif sm.lex_text.startswith("<!--->", start):
                short_comment_end = start + len("<!--->")
        elif marker == "<?":
            kind = "html_processing_instruction"
            form = "processing_instruction"
            terminator = "?>"
        elif marker == "<![CDATA[":
            kind = "html_cdata"
            form = "cdata"
            terminator = "]]>"
        else:
            kind = "html_declaration"
            form = "declaration"
            terminator = ">"

        (
            block_start,
            quote_depth,
            container_view_offset,
            container_line,
        ) = block_context(start)
        container_end = (
            _raw_html_container_end(
                sm,
                container_line,
                container_view_offset,
                quote_depth,
                container_contexts.get(
                    container_line["number"], ("", 0, 0, [], 0)
                )[3],
            )
            if block_start
            else _inline_paragraph_end(sm, start, container_contexts)
        )
        end_marker = (
            short_comment_end - len(terminator)
            if short_comment_end is not None
            else sm.lex_text.find(terminator, match.end(), container_end)
        )
        while (
            end_marker >= 0
            and block_start
            and in_container_prefix(end_marker, quote_depth)
        ):
            end_marker = sm.lex_text.find(
                terminator,
                end_marker + len(terminator),
                container_end,
            )
        if end_marker >= 0:
            terminator_end = (
                short_comment_end
                if short_comment_end is not None
                else end_marker + len(terminator)
            )
            end = (
                sm.line_for_offset(terminator_end - 1)["end_with_eol"]
                if block_start
                else terminator_end
            )
            result.append(
                {
                    "kind": kind,
                    "span": sm.span(start, end),
                    "block_start": block_start,
                    "closed": True,
                }
            )
            # Keep enumerating overlapping candidates.  Source-order
            # ownership is resolved jointly with Type-1 spans afterwards.
            cursor = start + 1
            continue

        # An inline-looking opener without a terminator in this paragraph is
        # plain text.  Only a genuine block start owns the remaining block.
        if not block_start:
            cursor = start + 1
            continue
        result.append(
            {
                "kind": kind,
                "span": sm.span(start, container_end),
                "block_start": block_start,
                "closed": False,
            }
        )
        diagnostics.append(
            {
                "code": (
                    "unterminated_html_comment"
                    if form == "comment"
                    else "unterminated_html_" + form
                ),
                "line": sm.point(start)["line"],
            }
        )
        cursor = start + 1
    return result, diagnostics


def _select_outermost_html_spans(
    candidates: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Resolve independently lexed HTML forms by source-order ownership."""

    selected: list[dict[str, Any]] = []
    ordered = sorted(
        candidates,
        key=lambda item: (
            item["span"]["char_start"],
            -item["span"]["char_end"],
        ),
    )
    for candidate in ordered:
        start = candidate["span"]["char_start"]
        if any(_contains(owner, start) for owner in selected):
            continue
        selected.append(candidate)
    return selected


def _unterminated_html_diagnostics(
    spans: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    codes = {
        "html_comment": "unterminated_html_comment",
        "html_processing_instruction": (
            "unterminated_html_processing_instruction"
        ),
        "html_declaration": "unterminated_html_declaration",
        "html_cdata": "unterminated_html_cdata",
    }
    diagnostics: list[dict[str, Any]] = []
    for item in spans:
        if item.get("closed") is not False:
            continue
        kind = item["kind"]
        if kind == "raw_html":
            diagnostics.append(
                {
                    "code": "unterminated_raw_html",
                    "tag": item["tag"],
                    "line": item["span"]["line_start"],
                }
            )
            continue
        diagnostics.append(
            {
                "code": codes[kind],
                "line": item["span"]["line_start"],
            }
        )
    return diagnostics


def _unescaped(text: str, index: int) -> bool:
    backslashes = 0
    index -= 1
    while index >= 0 and text[index] == chr(92):
        backslashes += 1
        index -= 1
    return backslashes % 2 == 0


def _find_math(
    sm: SourceMap, excluded: Sequence[dict[str, Any]], header_end: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    result: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    finite_owner_kinds = {"html_tag", "html_autolink"}
    blocking_excluded = [
        item for item in excluded
        if item["kind"] not in finite_owner_kinds
    ]
    display_start: int | None = None
    cursor = header_end
    while cursor < len(sm.lex_text):
        active_excluded = (
            excluded if display_start is None else blocking_excluded
        )
        if _covered(cursor, active_excluded):
            containing = next(
                item for item in active_excluded if _contains(item, cursor)
            )
            cursor = containing["span"]["char_end"]
            continue
        if sm.lex_text.startswith("$$", cursor) and _unescaped(
            sm.lex_text, cursor
        ):
            if display_start is None:
                display_start = cursor
            else:
                end = cursor + 2
                result.append(
                    {
                        "kind": "display_math",
                        "span": sm.span(display_start, end),
                        "closed": True,
                    }
                )
                display_start = None
            cursor += 2
            continue
        if display_start is None and sm.lex_text[cursor] == "$" and _unescaped(
            sm.lex_text, cursor
        ):
            line = sm.line_for_offset(cursor)
            close = cursor + 1
            while close < line["end"]:
                if (
                    sm.lex_text[close] == "$"
                    and not sm.lex_text.startswith("$$", close)
                    and _unescaped(sm.lex_text, close)
                    and not _covered(close, blocking_excluded)
                ):
                    result.append(
                        {
                            "kind": "inline_math",
                            "span": sm.span(cursor, close + 1),
                            "closed": True,
                        }
                    )
                    cursor = close + 1
                    break
                close += 1
            else:
                cursor += 1
            continue
        cursor += 1
    if display_start is not None:
        result.append(
            {
                "kind": "display_math",
                "span": sm.span(display_start, len(sm.text)),
                "closed": False,
            }
        )
        diagnostics.append(
            {
                "code": "unterminated_display_math",
                "line": sm.point(display_start)["line"],
            }
        )
    return result, diagnostics


def _find_headings(
    sm: SourceMap, excluded: Sequence[dict[str, Any]], header_end: int
) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    pattern = re.compile(r"^[ \t]{0,3}(#{1,6})[ \t]+(.+?)[ \t]*$")
    for line in sm.lines:
        if line["end_with_eol"] <= header_end or _covered(line["start"], excluded):
            continue
        match = pattern.match(line["text"])
        if not match:
            continue
        raw_title = match.group(2)
        normalized_title = re.sub(r"[ \t]+#+[ \t]*$", "", raw_title).strip()
        headings.append(
            {
                "id": len(headings),
                "level": len(match.group(1)),
                "title": normalized_title,
                "title_folded": _fold(normalized_title),
                "span": sm.span(line["start"], line["end"], include_raw=True),
                "line_end_with_eol": line["end_with_eol"],
            }
        )
    for index, heading in enumerate(headings):
        start = heading["span"]["char_start"]
        end = (
            headings[index + 1]["span"]["char_start"]
            if index + 1 < len(headings)
            else len(sm.text)
        )
        title = heading["title_folded"]
        if "erholungsgarten" in title:
            role = "garden"
        elif "selbsteinschatzung" in title:
            role = "reflection"
        elif title.strip().startswith("abgabe"):
            role = "submission"
        elif index == 0:
            role = "start"
        elif any(token in title for token in ("depot", "geheim", "portal")):
            role = "optional_secret"
        elif heading["level"] == 2:
            role = "task_or_station"
        else:
            role = "section"
        heading["role"] = role
        heading["slide_span"] = sm.span(start, end)
        heading["slide_end_line"] = sm.point(end)["line"]
    return headings


def _slide_id_at(headings: Sequence[dict[str, Any]], position: int) -> int | None:
    if not headings:
        return None
    starts = [item["span"]["char_start"] for item in headings]
    index = bisect_right(starts, position) - 1
    return index if index >= 0 else None


def _legacy_html_classes_overescaped(attributes: str) -> tuple[list[str], str | None]:
    match = re.search(
        r"\\bclass\\s*=\\s*(?:\"([^\"]*)\"|'([^']*)'|([^\\s>]+))",
        attributes,
        flags=re.IGNORECASE,
    )
    if not match:
        return [], None
    value = next(group for group in match.groups() if group is not None)
    style = "quoted" if match.group(1) is not None or match.group(2) is not None else "unquoted"
    return value.split(), style


def _html_classes(attributes: str) -> tuple[list[str], str | None]:
    """Parse quoted and unquoted class attributes without normalizing case."""
    match = re.search(
        r"""\bclass\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""",
        attributes,
        flags=re.IGNORECASE,
    )
    if not match:
        return [], None
    value = next(group for group in match.groups() if group is not None)
    style = (
        "quoted"
        if match.group(1) is not None or match.group(2) is not None
        else "unquoted"
    )
    return value.split(), style


def _scan_html_tags(
    sm: SourceMap,
    excluded: Sequence[dict[str, Any]],
    container_contexts: dict[int, ContainerContext] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Lex CommonMark HTML tags and autolinks."""

    tokens: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    text = sm.lex_text
    cursor = 0
    tag_name_re = re.compile(r"[A-Za-z][A-Za-z0-9-]*")
    attribute_name_re = re.compile(r"[A-Za-z_:][A-Za-z0-9_.:-]*")
    uri_autolink_re = re.compile(
        r"<[A-Za-z][A-Za-z0-9+.-]{1,31}:[^<>\x00-\x20\x7f]*>"
    )
    email_autolink_re = re.compile(
        r"<[A-Za-z0-9.!#\x24%&\x27*+/=?^_\x60{|}~-]+@"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*>"
    )
    invalid_spacing = " \t\n\r\f\v"
    # Form feed and vertical tab are not CommonMark whitespace/line endings
    # for an unquoted attribute value, so they remain valid value characters.
    invalid_unquoted = set(" \t\n\r")
    invalid_unquoted.update({chr(34), chr(39), "=", "<", ">", chr(96)})

    def html_whitespace(
        index: int, limit: int
    ) -> tuple[int, bool, bool]:
        """Consume spaces/tabs and at most one logical line ending."""

        start = index
        line_endings = 0
        while index < limit:
            if text[index] in " \t":
                index += 1
                continue
            if text[index] not in "\r\n":
                break
            line_endings += 1
            if line_endings > 1:
                return index, index > start, False
            if text.startswith("\r\n", index):
                index += 2
            else:
                index += 1
        if index == limit and index < len(text) and text[index] in "\r\n":
            return index, index > start, False
        return index, index > start, True

    def reject(start: int, reason: str, tag: str | None = None) -> None:
        item: dict[str, Any] = {
            "code": "invalid_html_tag_candidate",
            "reason": reason,
            "line": sm.point(start)["line"],
        }
        if tag:
            item["tag"] = tag.casefold()
        diagnostics.append(item)
    while cursor < len(text):
        start = text.find("<", cursor)
        if start < 0:
            break
        if _covered(start, excluded):
            containing = next(
                item for item in excluded if _contains(item, start)
            )
            cursor = containing["span"]["char_end"]
            continue
        if not _unescaped(text, start):
            cursor = start + 1
            continue
        limit = (
            _inline_paragraph_end(sm, start, container_contexts)
            if container_contexts is not None
            else len(text)
        )

        autolink_match = uri_autolink_re.match(text, start, limit)
        autolink_kind = "uri"
        if autolink_match is None:
            autolink_match = email_autolink_re.match(text, start, limit)
            autolink_kind = "email"
        if autolink_match is not None:
            end = autolink_match.end()
            tokens.append(
                {
                    "kind": "autolink",
                    "autolink_kind": autolink_kind,
                    "span": sm.span(start, end, include_raw=True),
                }
            )
            cursor = end
            continue

        index = start + 1
        closing = index < limit and text[index] == "/"
        if closing:
            index += 1
        name_match = tag_name_re.match(text, index, limit)
        if name_match is None:
            candidate = index
            while (
                candidate < limit
                and text[candidate] in invalid_spacing
            ):
                candidate += 1
            if candidate < limit and text[candidate].isalpha():
                reject(start, "invalid_tag_name_or_spacing")
            cursor = start + 1
            continue
        tag = name_match.group(0).casefold()
        name_end = name_match.end()
        index = name_end
        if closing:
            index, _, valid_spacing = html_whitespace(index, limit)
            if not valid_spacing:
                reject(start, "too_many_close_tag_line_endings", tag)
                cursor = start + 1
                continue
            if index >= limit or text[index] != ">":
                reject(start, "invalid_close_tag", tag)
                cursor = start + 1
                continue
            end = index + 1
            tokens.append(
                {
                    "kind": "html_tag",
                    "tag": tag,
                    "closing": True,
                    "attributes": text[name_end:index],
                    "self_closing": False,
                    "closed": True,
                    "malformed": False,
                    "span": sm.span(start, end, include_raw=True),
                }
            )
            cursor = end
            continue

        self_closing = False
        invalid_reason: str | None = None
        attributes_end: int | None = None
        while True:
            index, had_separator, valid_spacing = html_whitespace(
                index, limit
            )
            if not valid_spacing:
                invalid_reason = "too_many_attribute_separator_line_endings"
                break
            if index >= limit:
                invalid_reason = "unclosed_open_tag"
                break
            if text[index] == ">":
                attributes_end = index
                end = index + 1
                break
            if text.startswith("/>", index):
                self_closing = True
                attributes_end = index
                end = index + 2
                break
            if not had_separator:
                invalid_reason = "missing_attribute_separator"
                break

            attribute_match = attribute_name_re.match(text, index, limit)
            if attribute_match is None:
                invalid_reason = "invalid_attribute_name"
                break
            index = attribute_match.end()
            after_name = index
            index, _, valid_spacing = html_whitespace(index, limit)
            if not valid_spacing:
                invalid_reason = "too_many_pre_equals_line_endings"
                break
            if index >= limit:
                invalid_reason = "unclosed_open_tag"
                break
            if text[index] != "=":
                index = after_name
                continue

            index += 1
            index, _, valid_spacing = html_whitespace(index, limit)
            if not valid_spacing:
                invalid_reason = "too_many_post_equals_line_endings"
                break
            if index >= limit:
                invalid_reason = "missing_attribute_value"
                break
            quote = text[index] if text[index] in (chr(34), chr(39)) else None
            if quote is not None:
                close_quote = text.find(quote, index + 1, limit)
                if close_quote < 0:
                    invalid_reason = "unclosed_attribute_value"
                    break
                index = close_quote + 1
                continue
            value_start = index
            while index < limit and text[index] not in invalid_unquoted:
                index += 1
            if index == value_start:
                invalid_reason = "missing_or_invalid_attribute_value"
                break

        if invalid_reason is not None or attributes_end is None:
            reject(start, invalid_reason or "invalid_open_tag", tag)
            cursor = start + 1
            continue
        attributes = text[name_end:attributes_end]
        tokens.append(
            {
                "kind": "html_tag",
                "tag": tag,
                "closing": False,
                "attributes": attributes,
                "self_closing": self_closing,
                "closed": True,
                "malformed": False,
                "span": sm.span(start, end, include_raw=True),
            }
        )
        cursor = end
    return tokens, diagnostics


def _html_token_protection(
    tokens: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Project finite CommonMark HTML/autolink tokens into protected spans."""

    return [
        {
            "kind": (
                "html_autolink"
                if item.get("kind") == "autolink"
                else "html_tag"
            ),
            "span": dict(item["span"]),
        }
        for item in tokens
    ]


def _find_html(
    sm: SourceMap,
    excluded: Sequence[dict[str, Any]],
    headings: Sequence[dict[str, Any]],
    tokens: Sequence[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if tokens is None:
        tokens, lexer_diagnostics = _scan_html_tags(sm, excluded)
    else:
        lexer_diagnostics = []
    void_tags = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }
    stack: list[dict[str, Any]] = []
    ranges: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = list(lexer_diagnostics)
    open_count: Counter[str] = Counter()
    close_count: Counter[str] = Counter()
    quote_count: Counter[str] = Counter()
    for token in tokens:
        if token.get("kind") != "html_tag":
            continue
        closing = bool(token["closing"])
        tag = str(token["tag"])
        tag_span = token["span"]
        attributes = str(token["attributes"])
        if not closing:
            classes, class_style = _html_classes(attributes)
            if tag in void_tags or token["self_closing"]:
                open_count[tag] += 1
                close_count[tag] += 1
                item = {
                    "id": len(ranges) + len(stack),
                    "tag": tag,
                    "classes": classes,
                    "class_style": class_style,
                    "open_span": tag_span,
                    "close_span": tag_span,
                    "span": tag_span,
                    "depth": len(stack) + 1,
                    "parent_id": stack[-1]["id"] if stack else None,
                    "slide_id": _slide_id_at(
                        headings, tag_span["char_start"]
                    ),
                    "lifo_invalid": False,
                    "top_level": not stack,
                    "balanced": bool(token["closed"]),
                    "closed": bool(token["closed"]),
                    "container": False,
                    "void": tag in void_tags,
                    "self_closing": bool(token["self_closing"]),
                }
                ranges.append(item)
                if class_style:
                    quote_count[f"{tag}:{class_style}"] += 1
                continue
            item = {
                "id": len(ranges) + len(stack),
                "tag": tag,
                "classes": classes,
                "class_style": class_style,
                "open_span": tag_span,
                "depth": len(stack) + 1,
                "parent_id": stack[-1]["id"] if stack else None,
                "slide_id": _slide_id_at(
                    headings, tag_span["char_start"]
                ),
                "lifo_invalid": False,
                "container": True,
            }
            stack.append(item)
            open_count[tag] += 1
            if class_style:
                quote_count[f"{tag}:{class_style}"] += 1
            continue

        close_count[tag] += 1
        matching_index = next(
            (index for index in range(len(stack) - 1, -1, -1) if stack[index]["tag"] == tag),
            None,
        )
        if matching_index is None:
            diagnostics.append(
                {
                    "code": "unmatched_html_close",
                    "tag": tag,
                    "line": tag_span["line_start"],
                }
            )
            continue
        if matching_index != len(stack) - 1:
            for crossed in stack[matching_index:]:
                crossed["lifo_invalid"] = True
            diagnostics.append(
                {
                    "code": "html_lifo_mismatch",
                    "tag": tag,
                    "line": tag_span["line_start"],
                }
            )
        item = stack.pop(matching_index)
        item["close_span"] = tag_span
        item["span"] = sm.span(
            item["open_span"]["char_start"], item["close_span"]["char_end"]
        )
        item["top_level"] = item["depth"] == 1
        item["balanced"] = not item["lifo_invalid"]
        item["closed"] = True
        ranges.append(item)

    for item in stack:
        diagnostics.append(
            {
                "code": "unclosed_html",
                "tag": item["tag"],
                "line": item["open_span"]["line_start"],
            }
        )
        item["close_span"] = sm.span(len(sm.text), len(sm.text))
        item["span"] = sm.span(
            item["open_span"]["char_start"], len(sm.text)
        )
        item["top_level"] = item["depth"] == 1
        item["balanced"] = False
        item["closed"] = False
        ranges.append(item)
    ranges.sort(key=lambda item: item["open_span"]["char_start"])
    for new_id, item in enumerate(ranges):
        item["id"] = new_id
    summary = {
        "open": dict(open_count),
        "close": dict(close_count),
        "class_attribute_style": dict(quote_count),
        "balanced": not any(
            item["code"].startswith(("unclosed_html", "unmatched_html", "html_lifo"))
            for item in diagnostics
        ),
    }
    return ranges, diagnostics, summary


def _find_feedback_ranges(
    sm: SourceMap, headings: Sequence[dict[str, Any]], excluded: Sequence[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ranges: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    open_by_slide: dict[int | None, dict[str, Any]] = {}
    for line in sm.lines:
        if _covered(line["start"], excluded) or not re.fullmatch(
            r"\*{3,}[ \t]*", line["text"]
        ):
            continue
        slide_id = _slide_id_at(headings, line["start"])
        opened = open_by_slide.pop(slide_id, None)
        if opened is None:
            open_by_slide[slide_id] = line
            continue
        ranges.append(
            {
                "kind": "feedback",
                "slide_id": slide_id,
                "open_span": sm.span(opened["start"], opened["end"], include_raw=True),
                "close_span": sm.span(line["start"], line["end"], include_raw=True),
                "span": sm.span(opened["start"], line["end_with_eol"]),
            }
        )
    for slide_id, line in open_by_slide.items():
        diagnostics.append(
            {
                "code": "unpaired_feedback_delimiter",
                "slide_id": slide_id,
                "line": line["number"],
            }
        )
    return ranges, diagnostics


def _find_table_ranges(
    sm: SourceMap, excluded: Sequence[dict[str, Any]], headings: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    active: list[dict[str, Any]] = []
    for line in sm.lines + [
        {
            "number": len(sm.lines) + 1,
            "start": len(sm.text),
            "end": len(sm.text),
            "end_with_eol": len(sm.text),
            "text": "",
        }
    ]:
        table_line = (
            not _covered(line["start"], excluded)
            and bool(re.match(r"^[ \t]*\|.*\|[ \t]*$", line["text"]))
        )
        if table_line:
            active.append(line)
            continue
        if len(active) >= 2:
            result.append(
                {
                    "kind": "table_or_matrix",
                    "slide_id": _slide_id_at(headings, active[0]["start"]),
                    "span": sm.span(active[0]["start"], active[-1]["end_with_eol"]),
                }
            )
        active = []
    return result


def _find_native_quiz_ranges(
    sm: SourceMap,
    excluded: Sequence[dict[str, Any]],
    headings: Sequence[dict[str, Any]],
    table_ranges: Sequence[dict[str, Any]],
    macros: Sequence[dict[str, Any]],
    feedback_ranges: Sequence[dict[str, Any]],
    container_contexts: dict[int, ContainerContext] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Inventory typed LiaScript quiz syntax and its complete source blocks.

    Quiz markup can occur at line start, inline, in list rows, or in tables.
    Matrix-like text inside macro arguments and all protected lexer regions is
    deliberately excluded.  Table/list blocks are kept whole; a native hint
    may extend the preceding quiz across blank or macro-only helper lines.
    """

    double_square = re.compile(r"\[\[(?:(?!\]\]).)*\]\]")
    drag = re.compile(r"\[->\[(?:(?!\]\]).)*\]\]")
    choice = re.compile(
        r"\[(?=[^\]\r\n]*\(\s*[Xx ]?\s*\))[^\]\r\n]*\]"
    )
    macro_spans = [
        item for item in macros if item.get("usage_context") == "body"
    ]
    diagnostics: list[dict[str, Any]] = []
    tokens_by_line: dict[int, list[dict[str, Any]]] = {}

    for line in sm.lines:
        candidates: list[tuple[int, int, str]] = []
        for match in double_square.finditer(line["text"]):
            candidates.append((match.start(), match.end(), "double_square"))
        for match in drag.finditer(line["text"]):
            candidates.append((match.start(), match.end(), "drag_marker"))
        for match in choice.finditer(line["text"]):
            if any(
                start <= match.start() and match.end() <= end
                for start, end, _ in candidates
            ):
                continue
            candidates.append((match.start(), match.end(), "choice"))
        for relative_start, relative_end, syntax_kind in sorted(candidates):
            start = line["start"] + relative_start
            end = line["start"] + relative_end
            if _covered(start, excluded):
                continue
            if any(
                item["span"]["char_start"] <= start
                and end <= item["span"]["char_end"]
                for item in macro_spans
            ):
                continue
            raw = sm.text[start:end]
            tokens_by_line.setdefault(line["number"], []).append(
                {
                    "kind": syntax_kind,
                    "role": (
                        "hint"
                        if syntax_kind == "double_square"
                        and re.match(r"\[\[\s*\?", raw)
                        else "answer"
                    ),
                    "span": sm.span(start, end, include_raw=True),
                }
            )

    ranges: list[dict[str, Any]] = []
    consumed_lines: set[int] = set()

    def forms_for(lines: Sequence[dict[str, Any]], container: str) -> list[str]:
        forms = {container}
        for line in lines:
            stripped = line["text"].lstrip()
            if re.match(r"(?:[-+*]|\d+[.)])[ \t]+", stripped):
                forms.add("list")
            if "$" in line["text"]:
                forms.add("math_inline")
            first_token = tokens_by_line[line["number"]][0]["span"]
            if first_token["column_start"] > len(line["text"]) - len(stripped) + 1:
                forms.add("inline")
            else:
                forms.add("line_start")
        return sorted(forms)

    def append_range(
        lines: Sequence[dict[str, Any]],
        *,
        container: str,
        span: dict[str, Any] | None = None,
    ) -> None:
        syntax = [
            token
            for line in lines
            for token in tokens_by_line.get(line["number"], [])
        ]
        if not syntax:
            return
        block_span = span or sm.span(
            lines[0]["start"], lines[-1]["end_with_eol"]
        )
        ranges.append(
            {
                "id": len(ranges),
                "kind": "native_quiz",
                "container_kind": container,
                "forms": forms_for(lines, container),
                "slide_id": _slide_id_at(
                    headings, block_span["char_start"]
                ),
                "span": block_span,
                "syntax_spans": syntax,
                "syntax_count": len(syntax),
                "syntax_line_count": len(lines),
                "line_count": (
                    block_span["line_end"] - block_span["line_start"] + 1
                ),
                "complete": True,
            }
        )
        consumed_lines.update(line["number"] for line in lines)

    for table in table_ranges:
        lines = [
            line
            for line in sm.lines
            if table["span"]["char_start"] <= line["start"]
            and line["end_with_eol"] <= table["span"]["char_end"]
            and line["number"] in tokens_by_line
        ]
        append_range(lines, container="table", span=table["span"])

    token_lines = [
        line
        for line in sm.lines
        if line["number"] in tokens_by_line
        and line["number"] not in consumed_lines
    ]
    groups: list[list[dict[str, Any]]] = []
    for line in token_lines:
        if not groups:
            groups.append([line])
            continue
        previous = groups[-1][-1]
        same_slide = _slide_id_at(headings, previous["start"]) == _slide_id_at(
            headings, line["start"]
        )
        previous_list = _line_flags(
            sm, previous["start"], container_contexts
        )["inside_list"]
        current_list = _line_flags(
            sm, line["start"], container_contexts
        )["inside_list"]
        if same_slide and line["number"] == previous["number"] + 1 and (
            previous_list == current_list
        ):
            groups[-1].append(line)
        else:
            groups.append([line])

    for group in groups:
        first = group[0]
        container = (
            "list"
            if _line_flags(
                sm, first["start"], container_contexts
            )["inside_list"]
            else "line"
        )
        append_range(group, container=container)

    # Attach a hint-only range to the closest preceding answer range if only
    # blank or macro-only helper lines lie between them.
    hint_only = [
        item
        for item in ranges
        if all(
            token["role"] == "hint" for token in item["syntax_spans"]
        )
    ]
    attached_hint_ids: set[int] = set()
    for hint in hint_only:
        predecessors = [
            item
            for item in ranges
            if item is not hint
            and item["slide_id"] == hint["slide_id"]
            and item["span"]["char_end"] <= hint["span"]["char_start"]
            and any(
                token["role"] == "answer"
                for token in item["syntax_spans"]
            )
        ]
        if not predecessors:
            macro_predecessors = [
                macro for macro in macros
                if macro.get("usage_context") == "body"
                and "quiz" in macro.get("name_folded", "")
                and macro.get("slide_id") == hint["slide_id"]
                and macro["span"]["char_end"] <= hint["span"]["char_start"]
                and not sm.lex_text[
                    macro["span"]["char_end"] : hint["span"]["char_start"]
                ].strip()
            ]
            if macro_predecessors:
                predecessor = max(
                    macro_predecessors,
                    key=lambda item: item["span"]["char_end"],
                )
                hint["associated_macro_quiz_id"] = predecessor["id"]
                hint["container_kind"] = "macro_quiz_hint"
                hint["forms"] = sorted(
                    set(hint["forms"]) | {"macro_quiz"}
                )
                attached_hint_ids.add(id(hint))
            continue
        previous = max(
            predecessors, key=lambda item: item["span"]["char_end"]
        )
        between = sm.lex_text[
            previous["span"]["char_end"] : hint["span"]["char_start"]
        ]
        helper_only = True
        for raw_line in between.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if not re.fullmatch(r"@[A-Za-zÀ-ÖØ-öø-ÿ][\w.-]*(?:\([^\r\n]*\))?", stripped):
                helper_only = False
                break
        if not helper_only:
            continue
        previous["span"] = sm.span(
            previous["span"]["char_start"], hint["span"]["char_end"]
        )
        previous["syntax_spans"].extend(hint["syntax_spans"])
        previous["syntax_count"] = len(previous["syntax_spans"])
        previous["syntax_line_count"] += hint["syntax_line_count"]
        previous["line_count"] = (
            previous["span"]["line_end"]
            - previous["span"]["line_start"]
            + 1
        )
        previous["forms"] = sorted(
            set(previous["forms"]) | set(hint["forms"])
        )
        attached_hint_ids.add(id(hint))
        ranges.remove(hint)

    for hint in hint_only:
        if id(hint) in attached_hint_ids:
            continue
        if hint in ranges:
            ranges.remove(hint)
        diagnostics.append(
            {
                "code": "orphan_hint",
                "kind": "native_quiz",
                "line": hint["span"]["line_start"],
                "span": hint["span"],
            }
        )

    # A safe native-quiz carrier includes its typed timer metadata, the
    # immediately associated question prompt, all hint syntax, and the full
    # LiaScript feedback/solution pair.  This keeps reward insertion and
    # wrapping away from the interior of a logical quiz.
    comment_ranges = [
        item for item in excluded if item.get("kind") == "html_comment"
    ]
    for quiz in ranges:
        original_start = quiz["span"]["char_start"]
        original_end = quiz["span"]["char_end"]
        slide_id = quiz["slide_id"]
        feedback_candidates = [
            item for item in feedback_ranges
            if item["slide_id"] == slide_id
            and item["open_span"]["char_start"] >= original_end
            and item["open_span"]["line_start"]
            <= quiz["span"]["line_end"] + 3
            and not any(
                other is not quiz
                and original_end <= other["span"]["char_start"]
                < item["open_span"]["char_start"]
                for other in ranges
            )
        ]
        feedback = (
            min(
                feedback_candidates,
                key=lambda item: item["open_span"]["char_start"],
            )
            if feedback_candidates
            else None
        )
        complete_end = (
            feedback["span"]["char_end"] if feedback else original_end
        )

        metadata = [
            item for item in comment_ranges
            if item.get("closed") is not False
            and item["span"]["char_end"] <= original_start
            and sm.lex_text[
                item["span"]["char_end"] : original_start
            ].strip()
            == ""
            and item["span"]["line_end"] >= quiz["span"]["line_start"] - 8
        ]
        complete_start = original_start
        metadata_item = (
            max(metadata, key=lambda item: item["span"]["char_end"])
            if metadata
            else None
        )
        if metadata_item is not None:
            complete_start = metadata_item["span"]["char_start"]

        first_line_number = sm.point(complete_start)["line"]
        first_syntax = min(
            quiz["syntax_spans"], key=lambda item: item["span"]["char_start"]
        )["span"]
        syntax_is_inline = first_syntax["column_start"] > 1
        if metadata_item is not None or not syntax_is_inline:
            index = first_line_number - 2
            blanks = 0
            while index >= 0 and not sm.lines[index]["text"].strip() and blanks < 2:
                blanks += 1
                index -= 1
            prompt_lines: list[dict[str, Any]] = []
            while index >= 0 and len(prompt_lines) < 4:
                line = sm.lines[index]
                stripped = line["text"].strip()
                if not stripped:
                    break
                if re.match(r"^(?:#{1,6}\s|@|<|\*{3,}|---$|\|)", stripped):
                    break
                if _slide_id_at(headings, line["start"]) != slide_id:
                    break
                prompt_lines.append(line)
                index -= 1
            if prompt_lines:
                complete_start = prompt_lines[-1]["start"]

        quiz["span"] = sm.span(complete_start, complete_end)
        quiz["question_or_metadata_span"] = sm.span(
            complete_start, original_start
        )
        quiz["feedback_range_id"] = feedback.get("id") if feedback else None
        quiz["complete_components"] = {
            "question_or_metadata": complete_start < original_start,
            "typed_syntax": True,
            "hint": any(
                token["role"] == "hint" for token in quiz["syntax_spans"]
            ),
            "feedback_solution": feedback is not None,
        }
        quiz["line_count"] = (
            quiz["span"]["line_end"] - quiz["span"]["line_start"] + 1
        )

    ranges.sort(key=lambda item: item["span"]["char_start"])
    for identifier, item in enumerate(ranges):
        item["id"] = identifier
    return ranges, diagnostics


def _html_depth_at(ranges: Sequence[dict[str, Any]], position: int) -> int:
    return sum(
        item["open_span"]["char_end"]
        <= position
        < item["close_span"]["char_end"]
        for item in ranges
    )


def _range_depth_at(ranges: Sequence[dict[str, Any]], position: int) -> int:
    return sum(_contains(item, position, strict=True) for item in ranges)


def _line_flags(
    sm: SourceMap,
    position: int,
    container_contexts: dict[int, ContainerContext] | None = None,
) -> dict[str, bool]:
    line = sm.line_for_offset(position)
    text = line["text"]

    if container_contexts is not None:
        context = container_contexts.get(line["number"])
        if context is not None:
            components = context[3]
            return {
                "inside_list": any(
                    item["kind"] == "list" for item in components
                ),
                "inside_blockquote": any(
                    item["kind"] == "quote" for item in components
                ),
            }

    def indentation(value: str) -> int:
        prefix = re.match(r"^[ \t]*", value).group(0)
        return len(prefix.expandtabs(4))

    direct_list = re.match(
        r"^([ \t]*)(?:[-+*]|\d{1,9}[.)])(?:[ \t]+|$)", text
    )
    inside_list = direct_list is not None
    if not inside_list and text.strip():
        minimum_indent = indentation(text)
        line_index = line["number"] - 1
        for previous in reversed(sm.lines[:line_index]):
            previous_text = previous["text"]
            if not previous_text.strip():
                continue
            marker = re.match(
                r"^([ \t]*)(?:[-+*]|\d{1,9}[.)])(?:[ \t]+|$)",
                previous_text,
            )
            if marker is not None:
                marker_end = len(marker.group(0).expandtabs(4))
                if marker.end() == len(previous_text) and not re.search(
                    r"[ \t]$", previous_text
                ):
                    marker_end += 1
                if minimum_indent >= marker_end:
                    inside_list = True
                    break
            minimum_indent = min(minimum_indent, indentation(previous_text))
            if minimum_indent == 0:
                break
    return {
        "inside_list": inside_list,
        "inside_blockquote": bool(re.match(r"^[ \t]*>", text)),
    }


def _context_at(
    sm: SourceMap,
    position: int,
    *,
    header: dict[str, Any] | None,
    fences: Sequence[dict[str, Any]],
    inline_code: Sequence[dict[str, Any]],
    comments: Sequence[dict[str, Any]],
    math_spans: Sequence[dict[str, Any]],
    tables: Sequence[dict[str, Any]],
    quiz_ranges: Sequence[dict[str, Any]],
    html_ranges: Sequence[dict[str, Any]],
    feedback_ranges: Sequence[dict[str, Any]],
    headings: Sequence[dict[str, Any]],
    container_contexts: dict[int, ContainerContext] | None = None,
) -> dict[str, Any]:
    flags = _line_flags(sm, position, container_contexts)
    flags.update(
        {
            "slide_id": _slide_id_at(headings, position),
            "inside_header": bool(header and _contains(header, position)),
            "inside_fence": bool(_range_depth_at(fences, position)),
            "inside_inline_code": _covered(position, inline_code),
            "inside_html_comment": _covered(position, comments),
            "inside_math": _covered(position, math_spans),
            "inside_table_or_quiz": bool(
                _range_depth_at(tables, position)
                or _range_depth_at(quiz_ranges, position)
            ),
            "html_depth": _html_depth_at(html_ranges, position),
            "feedback_depth": _range_depth_at(feedback_ranges, position),
        }
    )
    return flags


def _split_macro_arguments(value: str) -> list[str]:
    if not value.strip():
        return []
    parts: list[str] = []
    start = 0
    round_depth = square_depth = curly_depth = 0
    quote: str | None = None
    tick_length = 0
    index = 0
    while index < len(value):
        char = value[index]
        if tick_length:
            marker = BACKTICK * tick_length
            if value.startswith(marker, index):
                tick_length = 0
                index += len(marker)
            else:
                index += 1
            continue
        if quote:
            if char == quote and _unescaped(value, index):
                quote = None
            index += 1
            continue
        if char == BACKTICK:
            run_end = index + 1
            while run_end < len(value) and value[run_end] == BACKTICK:
                run_end += 1
            tick_length = run_end - index
            index = run_end
            continue
        if char in (chr(34), chr(39)):
            quote = char
        elif char == "(":
            round_depth += 1
        elif char == ")":
            round_depth = max(0, round_depth - 1)
        elif char == "[":
            square_depth += 1
        elif char == "]":
            square_depth = max(0, square_depth - 1)
        elif char == "{":
            curly_depth += 1
        elif char == "}":
            curly_depth = max(0, curly_depth - 1)
        elif (
            char == ";"
            and round_depth == 0
            and square_depth == 0
            and curly_depth == 0
        ):
            parts.append(value[start:index].strip())
            start = index + 1
        index += 1
    parts.append(value[start:].strip())
    return parts


def _top_level_argument_parts(
    value: str, separators: set[str]
) -> list[dict[str, Any]]:
    """Split authored macro arguments and preserve exact trimmed offsets."""

    boundaries: list[tuple[int, int, str | None]] = []
    start = 0
    separator_before: str | None = None
    round_depth = square_depth = curly_depth = 0
    quote: str | None = None
    tick_length = 0
    index = 0
    while index < len(value):
        char = value[index]
        if tick_length:
            marker = BACKTICK * tick_length
            if value.startswith(marker, index):
                tick_length = 0
                index += len(marker)
            else:
                index += 1
            continue
        if quote:
            if char == quote and _unescaped(value, index):
                quote = None
            index += 1
            continue
        if char == BACKTICK:
            run_end = index + 1
            while run_end < len(value) and value[run_end] == BACKTICK:
                run_end += 1
            tick_length = run_end - index
            index = run_end
            continue
        if char in (chr(34), chr(39)):
            quote = char
        elif char == "(":
            round_depth += 1
        elif char == ")":
            round_depth = max(0, round_depth - 1)
        elif char == "[":
            square_depth += 1
        elif char == "]":
            square_depth = max(0, square_depth - 1)
        elif char == "{":
            curly_depth += 1
        elif char == "}":
            curly_depth = max(0, curly_depth - 1)
        elif (
            char in separators
            and round_depth == 0
            and square_depth == 0
            and curly_depth == 0
        ):
            boundaries.append((start, index, separator_before))
            start = index + 1
            separator_before = char
        index += 1
    boundaries.append((start, len(value), separator_before))

    result: list[dict[str, Any]] = []
    for raw_start, raw_end, preceding in boundaries:
        trimmed_start = raw_start
        trimmed_end = raw_end
        while trimmed_start < trimmed_end and value[trimmed_start].isspace():
            trimmed_start += 1
        while trimmed_end > trimmed_start and value[trimmed_end - 1].isspace():
            trimmed_end -= 1
        result.append(
            {
                "text": value[trimmed_start:trimmed_end],
                "start": trimmed_start,
                "end": trimmed_end,
                "raw_start": raw_start,
                "raw_end": raw_end,
                "separator_before": preceding,
            }
        )
    return result


def _parse_macro_at(text: str, start: int, limit: int) -> tuple[str, int, str | None] | None:
    match = re.match(r"@([^\W\d_][\w.-]*)", text[start:limit], flags=re.UNICODE)
    if not match:
        return None
    name = match.group(1)
    name_end = start + match.end()
    cursor = name_end
    while cursor < limit and text[cursor] in " \t":
        cursor += 1
    if cursor >= limit or text[cursor] != "(":
        return name, name_end, None

    open_position = cursor
    depth = 0
    quote: str | None = None
    tick_length = 0
    cursor = open_position
    while cursor < limit:
        char = text[cursor]
        if tick_length:
            marker = BACKTICK * tick_length
            if text.startswith(marker, cursor):
                tick_length = 0
                cursor += len(marker)
            else:
                cursor += 1
            continue
        if quote:
            if char == quote and _unescaped(text, cursor):
                quote = None
            cursor += 1
            continue
        if char == BACKTICK:
            run_end = cursor + 1
            while run_end < limit and text[run_end] == BACKTICK:
                run_end += 1
            tick_length = run_end - cursor
            cursor = run_end
            continue
        if char in (chr(34), chr(39)):
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return name, cursor + 1, text[open_position + 1 : cursor]
        cursor += 1
    return name, name_end, None


def _macro_records_in_range(
    sm: SourceMap,
    start: int,
    end: int,
    excluded: Sequence[dict[str, Any]],
    usage_context: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    cursor = start
    while cursor < end:
        found = sm.lex_text.find("@", cursor, end)
        if found < 0:
            break
        cursor = found + 1
        if _covered(found, excluded):
            continue
        if found > 0 and (
            sm.lex_text[found - 1].isalnum()
            or sm.lex_text[found - 1] in "._"
        ):
            continue
        parsed = _parse_macro_at(sm.lex_text, found, end)
        if parsed is None:
            continue
        name, macro_end, argument_source = parsed
        line = sm.line_for_offset(found)
        raw = sm.text[found:macro_end]
        records.append(
            {
                "name": name,
                "name_folded": _fold(name),
                "form": "inline_wrapper" if name.casefold().endswith(".inline") else "macro",
                "argument_source": argument_source,
                "arguments": (
                    _split_macro_arguments(argument_source)
                    if argument_source is not None
                    else []
                ),
                "span": sm.span(found, macro_end, include_raw=True),
                "standalone_line": line["text"].strip() == raw.strip(),
                "usage_context": usage_context,
            }
        )
    return records


def _find_macros(
    sm: SourceMap,
    protected: Sequence[dict[str, Any]],
    fences: Sequence[dict[str, Any]],
    header_end: int,
    context_arguments: dict[str, Any],
) -> list[dict[str, Any]]:
    records = _macro_records_in_range(
        sm, header_end, len(sm.text), protected, "body"
    )
    for fence in fences:
        info_start = fence.get("info_start")
        open_end = fence.get("open_end")
        if info_start is None or open_end is None:
            continue
        records.extend(
            _macro_records_in_range(
                sm, info_start, open_end, [], "fence_decorator"
            )
        )

    records.sort(
        key=lambda item: (
            item["span"]["char_start"],
            -item["span"]["char_end"],
        )
    )
    for identifier, item in enumerate(records):
        item["id"] = identifier

    for item in records:
        start = item["span"]["char_start"]
        end = item["span"]["char_end"]
        containers = [
            candidate
            for candidate in records
            if candidate["id"] != item["id"]
            and candidate["span"]["char_start"] < start
            and end <= candidate["span"]["char_end"]
        ]
        parent = (
            min(
                containers,
                key=lambda candidate: (
                    candidate["span"]["char_end"]
                    - candidate["span"]["char_start"]
                ),
            )
            if containers
            else None
        )
        item["parent_id"] = parent["id"] if parent else None
        item["children"] = []

    by_id = {item["id"]: item for item in records}
    for item in records:
        parent_id = item["parent_id"]
        if parent_id is not None:
            by_id[parent_id]["children"].append(item["id"])

    def depth(item: dict[str, Any]) -> int:
        value = 0
        parent_id = item["parent_id"]
        while parent_id is not None:
            value += 1
            parent_id = by_id[parent_id]["parent_id"]
        return value

    for item in records:
        item["macro_depth"] = depth(item)
        item.update(
            _context_at(
                sm,
                item["span"]["char_start"],
                **context_arguments,
            )
        )
        if item["usage_context"] == "fence_decorator":
            item["inside_fence"] = True
    return records


def _catalog_environment(catalog: dict[str, Any]) -> dict[str, Any]:
    environment = catalog.get("environment")
    return environment if isinstance(environment, dict) else {}


def _name_map(values: Sequence[str]) -> dict[str, str]:
    return {_fold(value): value for value in values}


def _pair_environment_blocks(
    sm: SourceMap,
    macros: Sequence[dict[str, Any]],
    catalog: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    environment = _catalog_environment(catalog)
    pair_specs = environment.get("block_pairs") or DEFAULT_BLOCK_PAIRS
    open_lookup: dict[str, str] = {}
    close_lookup: dict[str, str] = {}
    for spec in pair_specs:
        for name in spec.get("open", []):
            open_lookup[_fold(name)] = str(spec["kind"])
        for name in spec.get("close", []):
            close_lookup[_fold(name)] = str(spec["kind"])

    stack: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    def marker_reasons(macro: dict[str, Any]) -> tuple[bool, list[str]]:
        if macro["standalone_line"]:
            marker_only = True
        else:
            line = sm.line_for_offset(macro["span"]["char_start"])
            raw = macro["span"]["raw"].strip()
            marker_only = (
                (macro["inside_list"] or macro["inside_blockquote"])
                and line["text"].rstrip().endswith(raw)
            )
        reasons: list[str] = []
        if not macro["standalone_line"]:
            reasons.append("marker_not_standalone")
        if macro["inside_list"]:
            reasons.append("marker_in_list")
        if macro["inside_blockquote"]:
            reasons.append("marker_in_blockquote")
        if macro["html_depth"]:
            reasons.append("marker_inside_html")
        return marker_only, reasons

    for macro in macros:
        if macro["usage_context"] != "body" or macro["parent_id"] is not None:
            continue
        name = macro["name_folded"]
        if name not in open_lookup and name not in close_lookup:
            continue
        marker_only, structural_reasons = marker_reasons(macro)
        if not marker_only:
            diagnostics.append(
                {
                    "code": "environment_marker_not_standalone",
                    "line": macro["span"]["line_start"],
                    "macro": macro["name"],
                }
            )
            continue
        if structural_reasons:
            diagnostics.append(
                {
                    "code": "environment_invalid_marker",
                    "line": macro["span"]["line_start"],
                    "macro": macro["name"],
                    "exclusion_reasons": structural_reasons,
                }
            )
        if name in open_lookup:
            stack.append(
                {
                    "kind": open_lookup[name],
                    "macro": macro,
                    "exclusion_reasons": structural_reasons,
                    "lifo_invalid": False,
                }
            )
            continue
        kind = close_lookup[name]
        if not stack:
            diagnostics.append(
                {
                    "code": "environment_close_without_open",
                    "kind": kind,
                    "line": macro["span"]["line_start"],
                }
            )
            continue
        frame = stack[-1]
        open_kind = frame["kind"]
        opener = frame["macro"]
        if open_kind != kind:
            for open_frame in stack:
                open_frame["lifo_invalid"] = True
            diagnostics.append(
                {
                    "code": "environment_lifo_mismatch",
                    "expected": open_kind,
                    "actual": kind,
                    "line": macro["span"]["line_start"],
                }
            )
            continue
        stack.pop()
        reasons = list(frame["exclusion_reasons"])
        reasons.extend(structural_reasons)
        if frame["lifo_invalid"]:
            reasons.append("lifo_mismatch")
        if opener["slide_id"] != macro["slide_id"]:
            reasons.append("crosses_slide")
        if opener["html_depth"] != macro["html_depth"]:
            reasons.append("different_html_depth")
        if opener["html_depth"] or macro["html_depth"]:
            reasons.append("marker_inside_html")
        reasons = sorted(set(reasons))
        if reasons:
            diagnostics.append(
                {
                    "code": "environment_invalid_pair",
                    "kind": kind,
                    "line": opener["span"]["line_start"],
                    "close_line": macro["span"]["line_start"],
                    "exclusion_reasons": reasons,
                }
            )
        payload = [
            item["id"]
            for item in macros
            if opener["span"]["char_end"]
            <= item["span"]["char_start"]
            < macro["span"]["char_start"]
        ]
        pairs.append(
            {
                "id": len(pairs),
                "kind": kind,
                "open_macro_id": opener["id"],
                "close_macro_id": macro["id"],
                "open_span": opener["span"],
                "close_span": macro["span"],
                "span": sm.span(
                    opener["span"]["char_start"], macro["span"]["char_end"]
                ),
                "slide_id": opener["slide_id"],
                "structural_depth": len(stack),
                "payload_macro_ids": payload,
                "valid": not reasons,
                "exclusion_reasons": reasons,
            }
        )
    for frame in stack:
        kind = frame["kind"]
        opener = frame["macro"]
        diagnostics.append(
            {
                "code": "environment_open_without_close",
                "kind": kind,
                "line": opener["span"]["line_start"],
            }
        )
    return pairs, diagnostics


def _pair_lootif_ranges(
    sm: SourceMap,
    macros: Sequence[dict[str, Any]],
    quiz_ranges: Sequence[dict[str, Any]],
    headings: Sequence[dict[str, Any]],
    header: dict[str, Any] | None,
    environment_pairs: Sequence[dict[str, Any]],
    providers: dict[str, Any],
    protected: Sequence[dict[str, Any]],
    html_ranges: Sequence[dict[str, Any]],
    catalog: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    specs = _catalog_environment(catalog).get("conditional_ranges", [])
    spec = next(
        (
            item
            for item in specs
            if _fold(str(item.get("kind", ""))) == "lootif"
        ),
        None,
    )
    if spec is None:
        return [], []
    open_names = {str(value) for value in spec.get("open", ["lootif"])}
    close_names = {
        str(value) for value in spec.get(
            "close", ["Endelootif", "EndeLootif", "endlootif", "EndLootIf"]
        )
    }
    open_folded = {_fold(value) for value in open_names}
    close_folded = {_fold(value) for value in close_names}
    trigger_index = int(spec.get("trigger_argument_index", 0))
    action_index = int(spec.get("action_argument_index", 1))
    required_action = _fold(str(spec.get("required_action", "spawn")))
    families = spec.get("trigger_families", {})
    stack: list[dict[str, Any]] = []
    ranges: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    dash_re = re.compile(r"[_\u2010-\u2015\u2212]")
    max_safe = Decimal("9007199254740991")

    def normalized(value: str) -> str:
        value = dash_re.sub("-", _fold(value.strip()))
        return re.sub(r"\s+", " ", value)

    def fixed_key(value: str) -> str:
        return re.sub(r"[\s-]+", "-", normalized(value)).strip("-")

    def aliases(config: dict[str, Any]) -> set[str]:
        values = [config.get("canonical", ""), *config.get("aliases", [])]
        return {fixed_key(str(value)) for value in values if str(value).strip()}

    def alias_map(config: dict[str, Any], field: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for canonical, values in config.get(field, {}).items():
            result[normalized(str(canonical))] = str(canonical)
            for value in values:
                result[normalized(str(value))] = str(canonical)
        return result

    def parse_number(raw: str, *, integer: bool) -> Decimal | None:
        if not re.fullmatch(r"\d+(?:[.,]\d+)?", raw.strip()):
            return None
        try:
            value = Decimal(raw.strip().replace(",", "."))
        except InvalidOperation:
            return None
        if value < 0 or value > max_safe:
            return None
        if integer and value != value.to_integral_value():
            return None
        return value

    comparator_aliases = {
        ">": ">", ">=": ">=", "=>": ">=", "=": "=", "==": "=",
        "<=": "<=", "=<": "<=", "<": "<", "grosser": ">",
        "grosser oder gleich": ">=", "mindestens": ">=", "gleich": "=",
        "hochstens": "<=", "kleiner": "<", "kleiner oder gleich": "<=",
    }
    comparator_pattern = "|".join(
        re.escape(value)
        for value in sorted(comparator_aliases, key=len, reverse=True)
    )

    solved_labels = {
        normalized(str(value))
        for value in families.get("solved_quizzes", {}).get("labels", [])
    }
    resource_labels = alias_map(families.get("resources", {}), "labels")
    chest_labels = alias_map(families.get("opened_chests", {}), "labels")
    puzzle_colors = alias_map(families.get("puzzle_gate", {}), "colors")
    marker_colors = alias_map(families.get("marker", {}), "colors")
    lock_targets = alias_map(families.get("lock_target", {}), "targets")
    provider_target_by_id = {
        str(item.get("canonical_target", item.get("target"))): item
        for item in [
            *providers.get("targets", []),
            *providers.get("native_targets", []),
        ]
    }

    def parse_trigger(trigger: str) -> tuple[dict[str, Any] | None, str | None]:
        text = normalized(trigger)
        key = fixed_key(trigger)
        if not text or "@" in text:
            return None, "empty_or_placeholder_trigger"
        if key in aliases(families.get("previous_quiz", {})):
            return {"family": "previous_quiz"}, None
        if key in aliases(families.get("current_slide_quizzes", {})):
            return {"family": "current_slide_quizzes"}, None
        if key in aliases(families.get("secret_slide", {})):
            return {"family": "secret_slide"}, None
        if key in aliases(families.get("magnifier", {})):
            return {"family": "magnifier"}, None

        match = re.fullmatch(r"puzzletor\s*[:=]\s*([^\s:]+)", text)
        if match:
            color = puzzle_colors.get(normalized(match.group(1)))
            if color is None:
                return None, "unknown_puzzle_color"
            return {"family": "puzzle_gate", "color": color}, None
        match = re.fullmatch(r"([^\s]+)\s+puzzletor\s+(?:geoffnet|geoeffnet)", text)
        if match:
            token = normalized(match.group(1))
            color = puzzle_colors.get(token)
            if color is None:
                for suffix in ("es", "en", "er", "e"):
                    if token.endswith(suffix):
                        color = puzzle_colors.get(token[: -len(suffix)])
                        if color is not None:
                            break
            if color is None:
                return None, "unknown_puzzle_color"
            return {"family": "puzzle_gate", "color": color}, None

        match = re.fullmatch(r"(?:markiert|marked)\s*[:=]\s*([^:\s]+)(?:\s*:\s*(.*))?", text)
        if match:
            color = marker_colors.get(normalized(match.group(1)))
            word = re.sub(r"\s+", " ", (match.group(2) or "").strip())
            if color is None:
                return None, "unknown_marker_color"
            if match.group(2) is not None and not word:
                return None, "empty_marker_word"
            return {"family": "marker", "color": color, "word": word or None}, None
        match = re.fullmatch(
            r"(?:ein\s+)?wort(?:\s+(.+?))?\s+wurde\s+mit\s+(?:der\s+farbe\s+)?([^\s]+)\s+markiert",
            text,
        )
        if not match:
            match = re.fullmatch(
                r"wort\s+(.+?)\s+mit\s+(?:der\s+farbe\s+)?([^\s]+)\s+markiert",
                text,
            )
        if match:
            color = marker_colors.get(normalized(match.group(2)))
            if color is None:
                return None, "unknown_marker_color"
            word = (match.group(1) or "").strip().strip(chr(34) + chr(39))
            return {"family": "marker", "color": color, "word": word or None}, None

        match = re.fullmatch(
            r"mindestens\s+(\d+(?:[.,]\d+)?)\s+(?:bewertbare\s+)?aufgaben(?:\s+(?:gelost|geloest))?",
            text,
        )
        if match:
            value = parse_number(match.group(1), integer=True)
            if value is None:
                return None, "invalid_quiz_threshold"
            return {"family": "solved_quizzes", "comparator": ">=", "value": str(value)}, None

        match = re.fullmatch(
            r"(\d+(?:[.,]\d+)?)\s+(.+?)\s+(?:geoffnet|geoeffnet|eingesammelt)",
            text,
        )
        if match:
            value = parse_number(match.group(1), integer=True)
            chest_type = chest_labels.get(normalized(match.group(2)))
            if value is None or chest_type is None:
                return None, "invalid_chest_trigger"
            return {"family": "opened_chests", "chest_type": chest_type, "comparator": ">=", "value": str(value)}, None

        match = re.fullmatch(
            r"(?:schloss|lock)\s*:\s*([^\s:]+)|(?:schloss|lock)\s+([^\s:]+)\s+(?:geoffnet|geoeffnet|entsperrt)",
            text,
        )
        if match:
            raw_target = match.group(1) or match.group(2)
            target = lock_targets.get(normalized(raw_target))
            if target is None:
                return None, "unknown_lock_target"
            return {"family": "lock_target", "target": target}, None

        match = re.fullmatch(
            rf"(.+?)\s*({comparator_pattern})\s*(\d+(?:[.,]\d+)?)",
            text,
        )
        if not match:
            return None, "unknown_trigger_syntax"
        label = normalized(match.group(1))
        comparator = comparator_aliases[normalized(match.group(2))]
        if label in solved_labels:
            family = "solved_quizzes"
            value = parse_number(match.group(3), integer=True)
            extra: dict[str, Any] = {}
        elif label in resource_labels:
            family = "resources"
            value = parse_number(match.group(3), integer=False)
            extra = {"resource": resource_labels[label]}
        elif label in chest_labels:
            family = "opened_chests"
            value = parse_number(match.group(3), integer=True)
            extra = {"chest_type": chest_labels[label]}
        else:
            return None, "unknown_comparison_label"
        if value is None:
            return None, "invalid_comparison_value"
        return {
            "family": family,
            "comparator": comparator,
            "value": str(value),
            **extra,
        }, None

    def compare(actual: Decimal, operator: str, expected: Decimal) -> bool:
        return {
            ">": actual > expected,
            ">=": actual >= expected,
            "=": actual == expected,
            "<=": actual <= expected,
            "<": actual < expected,
        }[operator]

    def simple_arguments(macro: dict[str, Any]) -> list[str]:
        source = macro.get("argument_source")
        if source is None:
            return []
        return [part.strip() for part in re.split(r"[;,]", source)]

    def semicolon_arguments(macro: dict[str, Any]) -> list[str]:
        source = macro.get("argument_source")
        if source is None:
            return []
        return [
            part["text"]
            for part in _top_level_argument_parts(source, {";"})
        ]

    def counter_state_reachable(
        maximum: int, operator: str, expected: Decimal
    ) -> bool:
        """Whether a monotone integer counter can satisfy the comparison."""

        return any(
            compare(Decimal(value), operator, expected)
            for value in range(maximum + 1)
        )

    def puzzle_matrix(value: str) -> list[list[int]] | None:
        compact = re.sub(r"\s+", "", value)
        if not re.fullmatch(
            r"\[\[(?:\d+)(?:;\d+)*\](?:;\[(?:\d+)(?:;\d+)*\])*\]",
            compact,
        ):
            return None
        rows = [
            [int(cell) for cell in row.split(";")]
            for row in re.findall(r"\[([^\[\]]+)\]", compact[1:-1])
        ]
        if (
            not rows
            or any(len(row) != len(rows[0]) for row in rows)
            or sum(len(row) for row in rows) > 16
        ):
            return None
        flattened = [cell for row in rows for cell in row]
        if sorted(flattened) != list(range(1, len(flattened) + 1)):
            return None
        return rows

    def inside_range(
        position: int, ranges_to_check: Sequence[dict[str, Any]]
    ) -> bool:
        return any(
            item["span"]["char_start"] < position < item["span"]["char_end"]
            for item in ranges_to_check
        )

    def visible_text_outside(start: int, end: int) -> str:
        excluded_spans = [
            (item["span"]["char_start"], item["span"]["char_end"])
            for item in protected
        ]
        excluded_spans.extend(
            (item["span"]["char_start"], item["span"]["char_end"])
            for item in macros
        )
        excluded_spans.extend(
            (span["char_start"], span["char_end"])
            for item in html_ranges
            for span in (item["open_span"], item["close_span"])
        )
        excluded_spans.append((start, end))
        merged: list[list[int]] = []
        for left, right in sorted(excluded_spans):
            if right <= left:
                continue
            if merged and left <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], right)
            else:
                merged.append([left, right])
        chunks: list[str] = []
        cursor = 0
        for left, right in merged:
            if cursor < left:
                chunks.append(sm.lex_text[cursor:left])
            cursor = max(cursor, right)
        if cursor < len(sm.lex_text):
            chunks.append(sm.lex_text[cursor:])
        return normalized("\n".join(chunks))

    def relation(item: dict[str, Any], start: int, end: int) -> str:
        span = item["span"]
        return "before" if span["char_end"] <= start else "after"

    def macro_evidence(item: dict[str, Any], start: int, end: int, **extra: Any) -> dict[str, Any]:
        return {
            "kind": "macro", "macro_id": item["id"],
            "relation": relation(item, start, end), "proof_basis": "source", **extra,
        }

    def quiz_evidence(item: dict[str, Any], start: int, end: int) -> dict[str, Any]:
        return {
            "kind": "native_quiz", "quiz_id": item["id"],
            "relation": relation(item, start, end), "proof_basis": "source",
        }

    def evaluate_trigger(
        parsed: dict[str, Any], opener: dict[str, Any], closer: dict[str, Any]
    ) -> tuple[str, list[dict[str, Any]]]:
        start = opener["span"]["char_start"]
        end = closer["span"]["char_end"]
        external_macros = [
            item for item in macros
            if item["usage_context"] == "body"
            and not (start <= item["span"]["char_start"] < end)
        ]
        external_quizzes = [
            item for item in quiz_ranges
            if item["span"]["char_end"] <= start or item["span"]["char_start"] >= end
        ]
        family = parsed["family"]
        matches: list[dict[str, Any]] = []
        if family == "previous_quiz":
            candidates = [item for item in external_quizzes if item["span"]["char_end"] <= start]
            matches = [quiz_evidence(max(candidates, key=lambda item: item["span"]["char_end"]), start, end)] if candidates else []
        elif family == "current_slide_quizzes":
            candidates = [item for item in external_quizzes if item["slide_id"] == opener["slide_id"]]
            matches = [quiz_evidence(item, start, end) for item in candidates]
        elif family == "solved_quizzes":
            expected = Decimal(parsed["value"])
            candidates = list(external_quizzes)
            if counter_state_reachable(
                len(candidates), parsed["comparator"], expected
            ):
                matches = [quiz_evidence(item, start, end) for item in candidates]
                if not candidates:
                    matches = [{"kind": "zero_threshold", "relation": "course", "proof_basis": "source"}]
        elif family == "magnifier":
            candidates = [item for item in external_macros if item["name"] == "Lupe"]
            matches = [macro_evidence(item, start, end) for item in candidates]
        elif family == "secret_slide":
            candidates = [item for item in external_macros if item["name"] == "Geheimfolie"]
            matches = [macro_evidence(item, start, end) for item in candidates]
        elif family == "resources":
            resource_index = {"gold": 0, "diamonds": 1, "energy": 2}[parsed["resource"]]
            expected = Decimal(parsed["value"])
            for item in external_macros:
                if item["name"] != "Ressourcen":
                    continue
                values = simple_arguments(item)
                if resource_index >= len(values):
                    continue
                actual = parse_number(values[resource_index], integer=False)
                if actual is not None and compare(actual, parsed["comparator"], expected):
                    matches.append(macro_evidence(item, start, end, actual=str(actual)))
        elif family == "opened_chests":
            expected = Decimal(parsed["value"])
            configured_index = {"gold": 0, "diamonds": 1, "energy": 2}[parsed["chest_type"]]
            configured = any(
                item["name"] == "Ressourcen" and len(simple_arguments(item)) > configured_index
                for item in external_macros
            )
            names = {
                _fold(value)
                for value in families.get("opened_chests", {}).get("macros", {}).get(parsed["chest_type"], [])
            }
            candidates = [item for item in external_macros if item["name_folded"] in names]
            if configured and counter_state_reachable(
                len(candidates), parsed["comparator"], expected
            ):
                matches = [macro_evidence(item, start, end) for item in candidates]
                if not candidates:
                    matches = [{"kind": "configured_chest_counter", "relation": "course", "proof_basis": "source"}]
        elif family == "lock_target":
            target = parsed["target"]
            candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
            keys = [item for item in external_macros if item["name"] == "Schluessel"]
            for item in external_macros:
                if item["name"] != "Schloss":
                    continue
                args = simple_arguments(item)
                if not args or lock_targets.get(normalized(args[0])) != target:
                    continue
                color = normalized(args[1]) if len(args) > 1 else ""
                if not any(simple_arguments(key) and normalized(simple_arguments(key)[0]) == color for key in keys):
                    continue
                contract = provider_target_by_id.get(target)
                contract_evidence: dict[str, Any] | None = None
                if contract is not None:
                    purpose = contract.get("purpose_states", {}).get("lock")
                    eligible = bool(
                        purpose.get("eligible")
                        if purpose is not None
                        else contract.get("eligible")
                    )
                    instances = list(contract.get("instances", []))
                    if purpose is not None:
                        allowed_ids = set(
                            purpose.get("evidence_instance_ids", [])
                        )
                        instances = [
                            instance for instance in instances
                            if instance.get("id") in allowed_ids
                        ]
                    if contract.get("scope") != "global":
                        instances = [
                            instance for instance in instances
                            if (
                                instance["span"]["char_end"] <= start
                                or instance["span"]["char_start"] >= end
                            )
                            and instance.get("slide_id") == opener.get("slide_id")
                        ]
                        eligible = eligible and bool(instances)
                    if eligible:
                        contract_evidence = {
                            "kind": "provider_target",
                            "provider": contract.get("provider"),
                            "target": target,
                            "instance_ids": [
                                instance["id"] for instance in instances
                            ],
                            "required_state": (
                                purpose.get("required_state")
                                if purpose is not None
                                else contract.get("required_state")
                            ),
                            "relation": (
                                relation(instances[0], start, end)
                                if instances else "global"
                            ),
                            "proof_basis": "source",
                        }
                elif target in {"check", "resolve", "hint"}:
                    local_quizzes = [
                        quiz for quiz in external_quizzes
                        if quiz.get("slide_id") == opener.get("slide_id")
                    ]
                    if local_quizzes:
                        contract_evidence = {
                            "kind": "native_quiz_surface",
                            "target": target,
                            "quiz_ids": [quiz["id"] for quiz in local_quizzes],
                            "relation": relation(
                                local_quizzes[0], start, end
                            ),
                            "proof_basis": "source",
                        }
                elif target == "seitenwechsel":
                    page_headings = [
                        heading for heading in headings
                        if heading.get("level") == 2
                    ]
                    if len(page_headings) >= 2:
                        contract_evidence = {
                            "kind": "native_navigation_surface",
                            "target": target,
                            "heading_ids": [
                                heading["id"] for heading in page_headings
                            ],
                            "relation": "course",
                            "proof_basis": "source",
                        }
                elif target == "pentominoquiz":
                    pentomino_imports = [
                        imported
                        for imported in ((header or {}).get("imports", []))
                        if imported.get("provider") == "lia-pentominos"
                    ]
                    pentomino_names = {
                        _fold(value)
                        for value in families.get("lock_target", {})
                        .get("targets", {}).get("pentominoquiz", [])
                    }
                    components = [
                        candidate for candidate in external_macros
                        if candidate["name_folded"] in pentomino_names
                        and candidate["parent_id"] is None
                        and candidate.get("slide_id") == opener.get("slide_id")
                    ]
                    if pentomino_imports and components:
                        contract_evidence = {
                            "kind": "imported_pentomino_surface",
                            "target": target,
                            "import_orders": [
                                imported["order"]
                                for imported in pentomino_imports
                            ],
                            "macro_ids": [
                                component["id"] for component in components
                            ],
                            "relation": relation(
                                components[0], start, end
                            ),
                            "proof_basis": "source",
                        }
                elif target == "portal":
                    portals = [
                        candidate for candidate in external_macros
                        if candidate["name"] in {
                            "Portal", "Einwegportal", "Einbahnportal"
                        }
                        and candidate["parent_id"] is None
                    ]
                    if portals:
                        contract_evidence = {
                            "kind": "portal_surface",
                            "macro_ids": [candidate["id"] for candidate in portals],
                            "relation": "course",
                            "proof_basis": "source",
                        }
                if contract_evidence is not None:
                    candidates.append((item, contract_evidence))
            matches = [
                macro_evidence(item, start, end, target=target)
                | {"target_contract": contract_evidence}
                for item, contract_evidence in candidates
            ]
        elif family == "puzzle_gate":
            requested_color = parsed["color"]
            all_body_macros = [
                item for item in macros
                if item.get("usage_context") == "body"
            ]
            same_color_gates: list[tuple[dict[str, Any], list[list[int]] | None]] = []
            for item in all_body_macros:
                if item["name"] != "Puzzletor":
                    continue
                args = semicolon_arguments(item)
                if (
                    not args
                    or puzzle_colors.get(normalized(args[0])) != requested_color
                ):
                    continue
                valid_anchor = (
                    len(args) == 2
                    or (len(args) == 3 and args[2] == "anker")
                )
                same_color_gates.append(
                    (
                        item,
                        puzzle_matrix(args[1])
                        if valid_anchor and len(args) >= 2
                        else None,
                    )
                )
            if len(same_color_gates) == 1:
                gate, matrix = same_color_gates[0]
                gate_position = gate["span"]["char_start"]
                gate_is_external = (
                    matrix is not None
                    and not (
                        start <= gate["span"]["char_start"] < end
                    )
                    and gate["parent_id"] is None
                    and gate["standalone_line"]
                    and not inside_range(gate_position, environment_pairs)
                    and not inside_range(gate_position, ranges)
                    and not any(
                        frame["macro"]["span"]["char_start"]
                        < gate_position
                        for frame in stack
                    )
                )
                if gate_is_external and matrix is not None:
                    required_numbers = {
                        cell for row in matrix for cell in row
                    }
                    numbered_pieces: list[tuple[dict[str, Any], int]] = []
                    invalid_piece = False
                    environment_config = _catalog_environment(catalog)
                    concealment_config = environment_config.get(
                        "item_concealment", {}
                    )
                    item_mode_tokens = {
                        _fold(str(value))
                        for value in concealment_config.get(
                            "canonical_options",
                            ["unsichtbar", "zauberstaub"],
                        )
                    } | {
                        _fold(str(value))
                        for value in concealment_config.get(
                            "scan_aliases", {}
                        )
                    }
                    for piece in all_body_macros:
                        if piece["name"] != "Puzzleteil":
                            continue
                        args = semicolon_arguments(piece)
                        if not args:
                            continue
                        color = puzzle_colors.get(normalized(args[0]))
                        if color != requested_color:
                            continue
                        extras = args[2:]
                        concealment_count = sum(
                            _fold(extra) in item_mode_tokens
                            for extra in extras
                        )
                        shared_option_kinds = [
                            _shared_collectible_option_kind(extra)
                            for extra in extras
                        ]
                        valid_extras = all(
                            _fold(extra) in item_mode_tokens
                            or _normalize_layer_token(
                                extra, environment_config
                            ) is not None
                            or option_kind is not None
                            for extra, option_kind in zip(
                                extras, shared_option_kinds
                            )
                        )
                        if (
                            len(args) < 2
                            or not re.fullmatch(r"\d+", args[1])
                            or not (1 <= int(args[1]) <= 16)
                            or not valid_extras
                            or concealment_count > 1
                            or shared_option_kinds.count("duration") > 1
                        ):
                            invalid_piece = True
                            continue
                        numbered_pieces.append((piece, int(args[1])))
                    numbers = [number for _, number in numbered_pieces]
                    if (
                        not invalid_piece
                        and len(numbers) == len(set(numbers))
                        and set(numbers) == required_numbers
                        and all(
                            not (
                                start
                                <= piece["span"]["char_start"]
                                < end
                            )
                            for piece, _ in numbered_pieces
                        )
                        and all(
                            piece["span"]["char_start"] < gate_position
                            for piece, _ in numbered_pieces
                        )
                    ):
                        matches = [
                            macro_evidence(
                                gate, start, end,
                                color=requested_color,
                                matrix=matrix,
                            ),
                            *[
                                macro_evidence(
                                    piece, start, end,
                                    color=requested_color,
                                    piece_number=number,
                                )
                                for piece, number in numbered_pieces
                            ],
                        ]
        elif family == "marker":
            direct_imports = [
                item for item in ((header or {}).get("imports", []))
                if item.get("provider") == families.get("marker", {}).get("requires_direct_import", "lia-marker")
            ]
            word = parsed.get("word")
            outside_text = visible_text_outside(start, end)
            if direct_imports and (not word or normalized(word) in outside_text):
                matches = [{
                    "kind": "import", "import_order": item["order"],
                    "relation": "header", "proof_basis": "source",
                    "color": parsed["color"], "word": word,
                } for item in direct_imports]
        return ("proven" if matches else "unproven"), matches

    for macro in macros:
        if macro["usage_context"] != "body" or macro["parent_id"] is not None:
            continue
        name = macro["name"]
        if name not in open_names | close_names and _fold(name) in open_folded | close_folded:
            diagnostics.append({
                "code": "lootif_invalid_macro_case",
                "line": macro["span"]["line_start"],
                "macro": name,
            })
            continue
        if name in open_names:
            reasons: list[str] = []
            if not macro["standalone_line"]:
                reasons.append("marker_not_standalone")
            if macro["inside_list"]:
                reasons.append("marker_in_list")
            if macro["inside_blockquote"]:
                reasons.append("marker_in_blockquote")
            if macro["html_depth"]:
                reasons.append("marker_inside_html")
            arguments = macro["arguments"]
            trigger = (
                arguments[trigger_index]
                if trigger_index < len(arguments)
                else ""
            )
            action = (
                arguments[action_index]
                if action_index < len(arguments)
                else ""
            )
            if len(arguments) != 2 or not trigger:
                reasons.append("invalid_arguments")
            if _fold(action) != required_action:
                reasons.append("invalid_action")
            stack.append(
                {
                    "macro": macro,
                    "trigger": trigger,
                    "action": action,
                    "exclusion_reasons": reasons,
                }
            )
            continue
        if name not in close_names:
            continue
        if not stack:
            diagnostics.append(
                {
                    "code": "lootif_close_without_open",
                    "line": macro["span"]["line_start"],
                }
            )
            continue
        frame = stack.pop()
        opener = frame["macro"]
        reasons = list(frame["exclusion_reasons"])
        if not macro["standalone_line"]:
            reasons.append("marker_not_standalone")
        if macro["inside_list"]:
            reasons.append("marker_in_list")
        if macro["inside_blockquote"]:
            reasons.append("marker_in_blockquote")
        if opener["slide_id"] != macro["slide_id"]:
            reasons.append("crosses_slide")
        if opener["html_depth"] != macro["html_depth"]:
            reasons.append("different_html_depth")
        if opener["html_depth"] or macro["html_depth"]:
            reasons.append("marker_inside_html")
        parsed_trigger, trigger_error = parse_trigger(frame["trigger"])
        if parsed_trigger is None:
            trigger_status = "invalid"
            trigger_evidence: list[dict[str, Any]] = []
            reasons.append("invalid_trigger")
        else:
            trigger_status, trigger_evidence = evaluate_trigger(
                parsed_trigger, opener, macro
            )
            if trigger_status != "proven":
                reasons.append("external_trigger_unproven")
        reasons = sorted(set(reasons))
        ranges.append(
            {
                "id": len(ranges),
                "kind": "lootif",
                "open_macro_id": opener["id"],
                "close_macro_id": macro["id"],
                "open_span": opener["span"],
                "close_span": macro["span"],
                "span": sm.span(
                    opener["span"]["char_start"],
                    macro["span"]["char_end"],
                ),
                "slide_id": opener["slide_id"],
                "trigger": frame["trigger"],
                "action": frame["action"],
                "trigger_parse_status": "valid" if parsed_trigger else "invalid",
                "trigger_parse_error": trigger_error,
                "parsed_trigger": parsed_trigger,
                "external_trigger_status": trigger_status,
                "external_trigger_evidence": trigger_evidence,
                "evidence_basis": "source",
                "valid": not reasons,
                "exclusion_reasons": reasons,
            }
        )
    for frame in stack:
        diagnostics.append(
            {
                "code": "lootif_open_without_close",
                "line": frame["macro"]["span"]["line_start"],
            }
        )
    return ranges, diagnostics


def _validate_cross_family_ranges(
    environment_pairs: Sequence[dict[str, Any]],
    lootif_ranges: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Fail closed when environment and conditional intervals cross."""

    diagnostics: list[dict[str, Any]] = []
    items = [
        ("environment", item) for item in environment_pairs
    ] + [("lootif", item) for item in lootif_ranges]
    for index, (left_family, left) in enumerate(items):
        left_start = left["span"]["char_start"]
        left_end = left["span"]["char_end"]
        for right_family, right in items[index + 1 :]:
            if left_family == right_family:
                continue
            right_start = right["span"]["char_start"]
            right_end = right["span"]["char_end"]
            crossed = (
                left_start < right_start < left_end < right_end
                or right_start < left_start < right_end < left_end
            )
            if not crossed:
                continue
            for item in (left, right):
                item["valid"] = False
                item["exclusion_reasons"] = sorted(
                    set(item.get("exclusion_reasons", []))
                    | {"cross_family_lifo_mismatch"}
                )
            diagnostics.append({
                "code": "environment_conditional_lifo_mismatch",
                "environment_pair_id": left["id"] if left_family == "environment" else right["id"],
                "lootif_range_id": left["id"] if left_family == "lootif" else right["id"],
            })
    return diagnostics


def _normalize_layer_token(
    token: str, environment: dict[str, Any]
) -> dict[str, Any] | None:
    folded = _fold(token.strip())
    if not folded:
        return None
    kind_token, separator, suffix_token = folded.partition("-")
    kind_aliases = {
        _fold(key): str(value)
        for key, value in (
            environment.get("direct_layer_scan_kind_aliases")
            or {"erde": "earth", "pflanze": "plant"}
        ).items()
    }
    suffix_aliases = {
        _fold(key): str(value)
        for key, value in (
            environment.get("direct_layer_scan_suffix_aliases")
            or {"unsichtbar": "solid", "zauberstaub": "dust"}
        ).items()
    }
    kind = kind_aliases.get(kind_token)
    if kind not in {"earth", "plant"}:
        return None
    concealment: str | None = None
    if separator:
        concealment = suffix_aliases.get(suffix_token)
        if concealment not in {"solid", "dust"}:
            return None
    canonical_kind = "erde" if kind == "earth" else "pflanze"
    if concealment == "solid":
        canonical = canonical_kind + "-unsichtbar"
    elif concealment == "dust":
        canonical = canonical_kind + "-zauberstaub"
    else:
        canonical = canonical_kind
    return {
        "raw_token": token.strip(),
        "kind": kind,
        "concealment": concealment,
        "canonical_token": canonical,
        "is_scan_alias": folded != canonical,
    }


def _shared_collectible_option_kind(token: str) -> str | None:
    """Classify documented non-layer options used by collectible macros."""

    value = _fold(token.strip())
    if value in {
        "anker", "nur auf folie", "nur-auf-folie", "folie",
        "only on slide", "only-on-slide", "slide only", "slide-only",
    }:
        return "anchor"
    if re.fullmatch(
        r"(?:(?:nach|erst nach)\s*=?\s*)?"
        r"\d+(?:[.,]\d+)?\s*"
        r"(?:s|sek|sekunde|sekunden|m|min|minute|minuten)",
        value,
    ):
        return "duration"
    if re.fullmatch(
        r"(?:theme|farbtheme)[\s:=_-]+"
        r"(?:rot|red|gelb|yellow|standard|default|tuerkis|turkis|turquoise|blau|blue)",
        value,
    ):
        return "theme"
    if value in {"darkmode", "dark-mode", "dark mode", "lightmode", "light-mode", "light mode"}:
        return "variant"
    if re.fullmatch(
        r"(?:farbmodus|variant)[\s:=_-]+"
        r"(?:dunkel|dunkelmodus|dark|darkmode|dark-mode|dark mode|"
        r"hell|hellmodus|light|lightmode|light-mode|light mode)",
        value,
    ):
        return "variant"
    if value in {
        "annotation-aus", "annotation-hidden", "annotations-aus",
        "annotations-hidden", "ohne annotation", "ohne annotationen",
        "ohne-annotation", "ohne-annotationen", "without annotations",
        "without-annotations",
    }:
        return "annotations"
    if re.fullmatch(
        r"(?:annotation|annotationen)[\s:=_-]+"
        r"(?:aus|false|hidden|off|versteckt)",
        value,
    ):
        return "annotations"
    return None


def _environment_summary(
    sm: SourceMap,
    macros: Sequence[dict[str, Any]],
    pairs: Sequence[dict[str, Any]],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    environment = _catalog_environment(catalog)
    inline_names = {
        _fold(value)
        for value in (environment.get("inline_macros") or DEFAULT_INLINE_MACROS)
    }
    carriers = {
        _fold(value)
        for value in (
            environment.get("direct_layer_carriers") or DEFAULT_LAYER_CARRIERS
        )
    }
    forbidden = {
        _fold(value)
        for value in environment.get("forbidden_direct_layer_carriers", [])
    }
    direct_target_policy = environment.get("direct_layer_target_policy", {})
    foreign_layer_targets = {
        _fold(str(target))
        for provider in catalog.get("template_providers", [])
        for target in provider.get("targets", [])
    }
    for provider in catalog.get("template_providers", []):
        for alias, canonical in provider.get("target_aliases", {}).items():
            foreign_layer_targets.update(
                {_fold(str(alias)), _fold(str(canonical))}
            )
    foreign_target_carriers = {
        _fold(str(value))
        for value in direct_target_policy.get(
            "foreign_template_target_carriers",
            [
                "Schatztruhe", "Diamanttruhe", "Diamantentruhe",
                "Energiekiste", "Energietruhe",
            ],
        )
    }
    concealment_config = environment.get("item_concealment", {})
    canonical_item_modes = [
        str(value)
        for value in concealment_config.get(
            "canonical_options", ["unsichtbar", "zauberstaub"]
        )
    ]
    item_mode_aliases = {
        _fold(str(key)): str(value)
        for key, value in concealment_config.get(
            "scan_aliases",
            {
                "unsichtbar": "unsichtbar",
                "solid": "unsichtbar",
                "verdeckt": "unsichtbar",
                "zauberstaub": "zauberstaub",
                "dust": "zauberstaub",
            },
        ).items()
    }
    reveal_config = environment.get("reveal_visibility", {})

    def argument_coordinates(
        macro: dict[str, Any]
    ) -> tuple[int, int] | None:
        source = macro.get("argument_source")
        raw = macro["span"].get("raw", "")
        opening = raw.find("(")
        if source is None or opening < 0 or not raw.endswith(")"):
            return None
        return macro["span"]["char_start"] + opening + 1, macro["span"]["char_end"] - 1

    def item_edit_variants(
        macro: dict[str, Any], mode_parts: Sequence[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        coordinates = argument_coordinates(macro)
        if len(mode_parts) > 1:
            return []
        result: list[dict[str, Any]] = []
        if mode_parts and coordinates is not None:
            base, _ = coordinates
            part = mode_parts[0]
            replace_span = sm.span(
                base + part["start"], base + part["end"], include_raw=True
            )
            for mode in canonical_item_modes:
                result.append(
                    {
                        "mode": mode,
                        "operation": "replace_argument",
                        "replace_span": replace_span,
                        "text": mode,
                    }
                )
            return result
        if coordinates is not None:
            _, close_position = coordinates
            separator = (
                ""
                if not (macro.get("argument_source") or "").strip()
                else "; "
            )
            for mode in canonical_item_modes:
                result.append(
                    {
                        "mode": mode,
                        "operation": "insert_argument",
                        "anchor": sm.span(close_position, close_position),
                        "separator": separator,
                        "text": separator + mode,
                    }
                )
            return result
        for mode in canonical_item_modes:
            result.append(
                {
                    "mode": mode,
                    "operation": "rewrite_macro",
                    "replace_span": macro["span"],
                    "text": f"@{macro['name']}({mode})",
                }
            )
        return result

    def reveal_edit_variants(
        macro: dict[str, Any], *, inline: bool
    ) -> list[dict[str, Any]]:
        coordinates = argument_coordinates(macro)
        if coordinates is None:
            return item_edit_variants(macro, [])
        base, close_position = coordinates
        source = macro.get("argument_source") or ""
        parts = _top_level_argument_parts(
            source, {",", ";"} if inline else {";"}
        )
        option_parts = parts[1:] if inline else parts
        mode_parts = [
            part
            for part in option_parts
            if _fold(part["text"]) in item_mode_aliases
        ]
        if len(mode_parts) > 1:
            return []
        if mode_parts:
            part = mode_parts[0]
            replace_span = sm.span(
                base + part["start"], base + part["end"], include_raw=True
            )
            return [
                {
                    "mode": mode,
                    "operation": "replace_argument",
                    "replace_span": replace_span,
                    "text": mode,
                }
                for mode in canonical_item_modes
            ]
        if inline:
            has_options = any(
                part["separator_before"] == "," for part in parts[1:]
            )
            separator = (
                str(reveal_config.get("inline_option_separator", "; "))
                if has_options
                else str(reveal_config.get("inline_payload_separator", ", "))
            )
        else:
            separator = (
                ""
                if not source.strip()
                else str(reveal_config.get("block_option_separator", "; "))
            )
        return [
            {
                "mode": mode,
                "operation": "insert_argument",
                "anchor": sm.span(close_position, close_position),
                "separator": separator,
                "text": separator + mode,
            }
            for mode in canonical_item_modes
        ]

    inline_reveals: list[dict[str, Any]] = []
    direct_layers: list[dict[str, Any]] = []
    item_concealments: list[dict[str, Any]] = []
    macro_by_id = {item["id"]: item for item in macros}
    for macro in macros:
        if macro["name_folded"] in inline_names:
            base = macro["name"].split(".", 1)[0]
            visibility_edits = reveal_edit_variants(macro, inline=True)
            inline_reveals.append(
                {
                    "macro_id": macro["id"],
                    "kind": "earth" if _fold(base) == "erdhaufen" else "plant",
                    "payload_macro_ids": list(macro["children"]),
                    "span": macro["span"],
                    "slide_id": macro["slide_id"],
                    "visibility_edit_variants": visibility_edits,
                    "visibility_syntax_valid": bool(visibility_edits),
                }
            )
        if (
            macro["usage_context"] == "body"
            and macro["name_folded"] in carriers
        ):
            source = macro.get("argument_source")
            parts = (
                _top_level_argument_parts(source, {";"})
                if source is not None
                else []
            )
            mode_parts = [
                part
                for part in parts
                if _fold(part["text"]) in item_mode_aliases
            ]
            current_modes = [
                item_mode_aliases[_fold(part["text"])]
                for part in mode_parts
            ]
            structurally_eligible = not (
                macro["name_folded"] == "puzzleteil"
                and source is None
            )
            concealment_valid = (
                structurally_eligible and len(mode_parts) <= 1
            )
            item_concealments.append(
                {
                    "id": len(item_concealments),
                    "macro_id": macro["id"],
                    "carrier": macro["name"],
                    "span": macro["span"],
                    "slide_id": macro["slide_id"],
                    "current_concealment": (
                        current_modes[0] if len(current_modes) == 1 else None
                    ),
                    "observed_mode_tokens": [
                        part["text"] for part in mode_parts
                    ],
                    "concealment_valid": concealment_valid,
                    "structurally_eligible": structurally_eligible,
                    "exclusion_reasons": (
                        ["bare_puzzleteil_requires_color_and_number"]
                        if not structurally_eligible
                        else ["duplicate_or_conflicting_item_concealment"]
                        if len(mode_parts) > 1
                        else []
                    ),
                    "edit_variants": (
                        item_edit_variants(macro, mode_parts)
                        if concealment_valid
                        else []
                    ),
                }
            )
        layer_arguments: list[tuple[int, str]] = []
        layer_scannable = (
            macro["name_folded"] in carriers
            or macro["name_folded"] in forbidden
        )
        if layer_scannable:
            if macro["name_folded"] == "puzzleteil":
                first_option = 2
            elif macro["name_folded"] == "schluessel":
                # Key color and target are optional and author-order agnostic;
                # only tokens that normalize as a layer are layer options.
                first_option = 0
            else:
                first_option = 0
            layer_arguments = list(
                enumerate(macro["arguments"][first_option:], first_option)
            )
        for argument_order, argument in layer_arguments:
            layer = _normalize_layer_token(argument, environment)
            if layer is None:
                continue
            carrier_allowed = macro["name_folded"] in carriers
            observed_foreign_targets = sorted(
                {
                    value
                    for value in macro["arguments"]
                    if _fold(value) in foreign_layer_targets
                }
            )
            target_compatible = (
                not observed_foreign_targets
                or macro["name_folded"] in foreign_target_carriers
            )
            layer.update(
                {
                    "macro_id": macro["id"],
                    "carrier": macro["name"],
                    "argument_order": argument_order,
                    "slide_id": macro["slide_id"],
                    "valid_carrier": carrier_allowed and target_compatible,
                    "carrier_allowed": carrier_allowed,
                    "target_compatible": target_compatible,
                    "foreign_template_targets": observed_foreign_targets,
                    "exclusion_reasons": (
                        []
                        if carrier_allowed and target_compatible
                        else ["unsupported_direct_layer_carrier"]
                        if not carrier_allowed
                        else ["foreign_template_target_requires_chest_carrier"]
                    ),
                    "forbidden_carrier": macro["name_folded"] in forbidden,
                    "span": macro["span"],
                }
            )
            direct_layers.append(layer)

    tool_events: list[dict[str, Any]] = []
    for tool in environment.get("tools", []):
        names = {_fold(value) for value in tool.get("macros", [])}
        for macro in macros:
            if macro["name_folded"] in names:
                tool_events.append(
                    {
                        "tool": tool.get("id"),
                        "macro_id": macro["id"],
                        "name": macro["name"],
                        "span": macro["span"],
                        "slide_id": macro["slide_id"],
                        "required_before": tool.get("required_before", []),
                    }
                )
    tool_events.sort(key=lambda item: item["span"]["char_start"])
    for order, item in enumerate(tool_events):
        item["order"] = order

    for pair in pairs:
        opener = macro_by_id[pair["open_macro_id"]]
        pair["visibility_edit_variants"] = reveal_edit_variants(
            opener, inline=False
        )
        pair["visibility_syntax_valid"] = bool(
            pair["visibility_edit_variants"]
        )

    counts = Counter()
    counts["earth_inline"] = sum(
        item["kind"] == "earth" for item in inline_reveals
    )
    counts["plant_inline"] = sum(
        item["kind"] == "plant" for item in inline_reveals
    )
    counts["earth_blocks"] = sum(item["kind"] == "earth" for item in pairs)
    counts["plant_blocks"] = sum(item["kind"] == "plant" for item in pairs)
    counts["earth_direct_layers"] = sum(
        item["kind"] == "earth" for item in direct_layers
    )
    counts["plant_direct_layers"] = sum(
        item["kind"] == "plant" for item in direct_layers
    )
    counts["item_concealment_carriers"] = len(item_concealments)
    counts["item_concealed"] = sum(
        item["current_concealment"] is not None
        for item in item_concealments
    )
    return {
        "counts": dict(counts),
        "block_pairs": list(pairs),
        "inline_reveals": inline_reveals,
        "direct_layers": direct_layers,
        "item_concealments": item_concealments,
        "tool_events": tool_events,
        "invalid_direct_layers": [
            item for item in direct_layers if not item["valid_carrier"]
        ],
        "invalid_item_concealments": [
            item
            for item in item_concealments
            if not item["concealment_valid"]
        ],
        "nested_payloads": {
            str(item["macro_id"]): [
                macro_by_id[child]["name"] for child in item["payload_macro_ids"]
            ]
            for item in inline_reveals
        },
    }


def _provider_for_url(url: str, catalog: dict[str, Any]) -> str | None:
    path = urlsplit(url).path or url
    segments = {
        value.casefold()
        for value in re.split(r"[/\\]+", path)
        if value
    }

    def matches(pattern: Any) -> bool:
        value = str(pattern).strip().casefold()
        return bool(value) and value in segments

    entries = list(catalog.get("template_providers", [])) + list(
        catalog.get("non_target_imports", [])
    )
    for entry in entries:
        if any(matches(pattern) for pattern in entry.get("import_patterns", [])):
            return str(entry.get("provider"))
    if "lia-loot" in segments:
        return "lia-loot"
    return None


def _annotate_imports(header: dict[str, Any] | None, catalog: dict[str, Any]) -> None:
    if not header:
        return
    for item in header["imports"]:
        item["provider"] = _provider_for_url(item["normalized_url"], catalog)
        item["is_loot"] = item["provider"] == "lia-loot"

    # Header lexing cannot establish provider identity.  Recompute every
    # loot-relative field only after exact path-segment provider matching so
    # names such as ``not-lia-loot`` never become false imports.
    loot_orders = [
        item["order"] for item in header["imports"] if item["is_loot"]
    ]
    loot_order = loot_orders[0] if loot_orders else None
    header["loot_import_orders"] = loot_orders
    for item in header["imports"]:
        if loot_order is None:
            item["relative_to_loot"] = "loot_absent"
        elif item["order"] < loot_order:
            item["relative_to_loot"] = "before"
        elif item["order"] > loot_order:
            item["relative_to_loot"] = "after"
        else:
            item["relative_to_loot"] = "self"

    policy = catalog.get("import_policy", {})
    tested = {
        _fold(value) for value in policy.get("both_orders_browser_tested_with_loot", [])
    }
    for slot in header["import_slots"]:
        rank = slot["rank"]
        for side in ("previous", "next"):
            adjacent = slot["adjacent_imports"][side]
            if adjacent is not None:
                item = header["imports"][adjacent["order"]]
                adjacent["provider"] = (
                    item.get("provider") or item["normalized_url"]
                )
        if loot_order is None:
            status = "unproven"
            crossed: list[str] = []
            pair_evidence: list[dict[str, Any]] = []
        elif rank == loot_order:
            status = "course_observed"
            crossed = []
            pair_evidence = [
                {
                    "import_order": loot_order,
                    "provider": "lia-loot",
                    "observed_relation": "self",
                    "proposed_relation": "observed_slot",
                    "evidence_status": "course_observed",
                }
            ]
        else:
            low, high = sorted((rank, loot_order))
            crossed_items = [
                item
                for item in header["imports"][low:high]
                if not item.get("is_loot")
            ]
            crossed = [
                item.get("provider") or item["normalized_url"] for item in crossed_items
            ]
            pair_evidence = []
            for item in crossed_items:
                provider = item.get("provider") or item["normalized_url"]
                pair_evidence.append(
                    {
                        "import_order": item["order"],
                        "provider": provider,
                        "observed_relation": (
                            "before_loot"
                            if item["order"] < loot_order
                            else "after_loot"
                        ),
                        "proposed_relation": (
                            "before_loot"
                            if item["order"] < rank
                            else "after_loot"
                        ),
                        "evidence_status": (
                            "browser_tested"
                            if _fold(item.get("provider") or "") in tested
                            else "unproven"
                        ),
                    }
                )
            if crossed_items and all(
                _fold(item.get("provider") or "") in tested for item in crossed_items
            ):
                status = "browser_tested"
            else:
                status = "unproven"
        slot["compatibility_status"] = status
        slot["crossed_providers_from_observed_loot_position"] = crossed
        slot["loot_order_evidence"] = pair_evidence


def _pattern_occurrences(
    sm: SourceMap,
    pattern: str,
    *,
    excluded: Sequence[dict[str, Any]],
    macros: Sequence[dict[str, Any]],
    html_ranges: Sequence[dict[str, Any]],
    headings: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    folded_pattern = _fold(pattern)
    occurrences: list[dict[str, Any]] = []
    seen: set[tuple[int, int, str]] = set()

    for macro in macros:
        if folded_pattern not in macro["name_folded"]:
            continue
        if (
            folded_pattern == "explain"
            and macro["arguments"]
            and _fold(macro["arguments"][0]) == "tutorial"
        ):
            continue
        key = (
            macro["span"]["char_start"],
            macro["span"]["char_end"],
            "macro",
        )
        if key not in seen:
            seen.add(key)
            occurrences.append(
                {
                    "pattern": pattern,
                    "kind": "macro",
                    "macro_id": macro["id"],
                    "span": macro["span"],
                    "slide_id": macro["slide_id"],
                    "fence_decorator": macro["usage_context"] == "fence_decorator",
                }
            )

    for html_range in html_ranges:
        if not any(folded_pattern in _fold(value) for value in html_range["classes"]):
            continue
        span = html_range["open_span"]
        key = (span["char_start"], span["char_end"], "html")
        if key not in seen:
            seen.add(key)
            occurrences.append(
                {
                    "pattern": pattern,
                    "kind": "html",
                    "html_id": html_range["id"],
                    "span": span,
                    "slide_id": html_range["slide_id"],
                }
            )

    regex = re.compile(re.escape(pattern), flags=re.IGNORECASE)
    for match in regex.finditer(sm.lex_text):
        if _covered(match.start(), excluded):
            continue
        key = (match.start(), match.end(), "text")
        if key in seen:
            continue
        seen.add(key)
        occurrences.append(
            {
                "pattern": pattern,
                "kind": "text",
                "span": sm.span(match.start(), match.end(), include_raw=True),
                "slide_id": _slide_id_at(headings, match.start()),
            }
        )
    occurrences.sort(key=lambda item: item["span"]["char_start"])
    return occurrences


def _semantic_provider_instances(
    sm: SourceMap,
    target: str,
    *,
    block_policy: str | None,
    typed_patterns: Sequence[dict[str, Any]],
    protected: Sequence[dict[str, Any]],
    comments: Sequence[dict[str, Any]],
    macros: Sequence[dict[str, Any]],
    html_ranges: Sequence[dict[str, Any]],
    quiz_ranges: Sequence[dict[str, Any]],
    headings: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return typed authored instances; never infer them from prose."""

    instances: list[dict[str, Any]] = []
    seen: set[tuple[str, int, int]] = set()

    def patterns(kind: str) -> list[dict[str, Any]]:
        return [
            item
            for item in typed_patterns
            if str(item.get("kind", "")) == kind
        ]

    def containing(
        ranges: Sequence[dict[str, Any]], position: int
    ) -> dict[str, Any] | None:
        matches = [
            item
            for item in ranges
            if item["span"]["char_start"]
            <= position
            < item["span"]["char_end"]
        ]
        return (
            min(
                matches,
                key=lambda item: (
                    item["span"]["char_end"]
                    - item["span"]["char_start"]
                ),
            )
            if matches
            else None
        )

    def line_span(position: int) -> dict[str, Any]:
        line = sm.line_for_offset(position)
        return sm.span(line["start"], line["end_with_eol"])

    def macro_block(
        macro: dict[str, Any],
        *,
        preferred_html_class: str | None = None,
        require_quiz: bool = False,
    ) -> tuple[dict[str, Any] | None, str | None]:
        position = macro["span"]["char_start"]
        if macro["usage_context"] == "fence_decorator":
            fence = containing(
                [
                    item
                    for item in protected
                    if item.get("kind") == "fence"
                ],
                position,
            )
            if fence is not None:
                return fence["span"], "fence"
        if preferred_html_class is not None:
            wrappers = [
                item
                for item in html_ranges
                if any(
                    _fold(value) == _fold(preferred_html_class)
                    for value in item["classes"]
                )
            ]
            wrapper = containing(wrappers, position)
            if wrapper is not None:
                return wrapper["span"], "html"
        quiz = containing(quiz_ranges, position)
        if quiz is not None:
            return quiz["span"], "native_quiz"
        if require_quiz:
            return None, None
        return line_span(position), "macro_line"

    def add(
        kind: str,
        span: dict[str, Any],
        block_span: dict[str, Any],
        block_kind: str,
        **evidence: Any,
    ) -> None:
        key = (kind, span["char_start"], span["char_end"])
        if key in seen:
            return
        seen.add(key)
        instances.append(
            {
                "pattern": target,
                "kind": kind,
                "span": span,
                "slide_id": _slide_id_at(
                    headings, span["char_start"]
                ),
                "block_span": block_span,
                "block_kind": block_kind,
                "block_complete": (
                    block_span["char_start"] < block_span["char_end"]
                ),
                "block_policy": block_policy,
                **evidence,
            }
        )

    if target == "dynflex":
        html_specs = patterns("html_class") or [
            {"id": "section_class_dynflex", "tag": "section", "value": "dynFlex"}
        ]
        for html_range in html_ranges:
            matched = next(
                (
                    spec
                    for spec in html_specs
                    if html_range.get("balanced")
                    and (
                        not spec.get("tag")
                        or html_range["tag"]
                        == str(spec["tag"]).casefold()
                    )
                    and any(
                        _fold(value) == _fold(str(spec.get("value", "")))
                        for value in html_range["classes"]
                    )
                ),
                None,
            )
            if matched is not None:
                add(
                    "html",
                    html_range["open_span"],
                    html_range["span"],
                    "html",
                    html_id=html_range["id"],
                    typed_pattern_id=matched.get("id"),
                )

    elif target == "markerquiz":
        html_specs = patterns("html_class") or [
            {"id": "markerquiz_html_class", "value": "markerquiz"}
        ]
        wrappers = [
            item
            for item in html_ranges
            if item.get("balanced")
            and any(
                (
                    not spec.get("tag")
                    or item["tag"] == str(spec["tag"]).casefold()
                )
                and any(
                    _fold(value) == _fold(str(spec.get("value", "")))
                    for value in item["classes"]
                )
                for spec in html_specs
            )
        ]
        for wrapper in wrappers:
            matched = next(
                spec
                for spec in html_specs
                if (
                    not spec.get("tag")
                    or wrapper["tag"] == str(spec["tag"]).casefold()
                )
                and any(
                    _fold(value) == _fold(str(spec.get("value", "")))
                    for value in wrapper["classes"]
                )
            )
            add(
                "html",
                wrapper["open_span"],
                wrapper["span"],
                "html",
                html_id=wrapper["id"],
                typed_pattern_id=matched.get("id"),
            )
        macro_specs = patterns("macro_name") or [
            {"id": "textmarkerquiz_macro", "value": "TextmarkerQuiz"}
        ]
        for macro in macros:
            matched = next(
                (
                    spec
                    for spec in macro_specs
                    if macro["name_folded"]
                    == _fold(str(spec.get("value", "")))
                ),
                None,
            )
            if matched is None:
                continue
            if containing(wrappers, macro["span"]["char_start"]) is not None:
                continue
            block_span, block_kind = macro_block(
                macro, preferred_html_class="markerquiz"
            )
            if block_span is not None and block_kind is not None:
                add(
                    "macro",
                    macro["span"],
                    block_span,
                    block_kind,
                    macro_id=macro["id"],
                    macro_name=macro["name"],
                    typed_pattern_id=matched.get("id"),
                )

    elif target == "timer":
        timer_specs = [
            *patterns("html_comment_attribute"),
            *patterns("macro_argument_attribute"),
        ]
        timer_attribute = str(
            (timer_specs or [{"name": "data-solution-timer"}])[0].get(
                "name", "data-solution-timer"
            )
        )
        timer_key = re.compile(
            r"\b" + re.escape(timer_attribute) + r"\s*=",
            flags=re.IGNORECASE,
        )
        timer_start = re.compile(
            r"\bdata-solution-timer-start\s*=\s*[^A-Za-z]*(oncheck|onclick)",
            flags=re.IGNORECASE,
        )
        for comment in comments:
            start = comment["span"]["char_start"]
            raw = sm.lex_text[start : comment["span"]["char_end"]]
            match = timer_key.search(raw)
            if match is None:
                continue
            slide_id = _slide_id_at(headings, start)
            following = [
                quiz
                for quiz in quiz_ranges
                if quiz["slide_id"] == slide_id
                and (
                    quiz["span"]["char_start"]
                    <= comment["span"]["char_start"]
                    < quiz["span"]["char_end"]
                    or quiz["span"]["char_start"]
                    >= comment["span"]["char_end"]
                )
            ]
            if not following:
                continue
            quiz = min(
                following,
                key=lambda item: (
                    0
                    if item["span"]["char_start"]
                    <= comment["span"]["char_start"]
                    < item["span"]["char_end"]
                    else 1,
                    item["span"]["char_start"],
                ),
            )
            start_match = timer_start.search(raw)
            span = sm.span(
                start + match.start(),
                start + match.end(),
                include_raw=True,
            )
            add(
                "typed_metadata",
                span,
                quiz["span"],
                "native_quiz",
                metadata_container_span=comment["span"],
                typed_pattern_id=(
                    patterns("html_comment_attribute")[0].get("id")
                    if patterns("html_comment_attribute")
                    else None
                ),
                timer_start=(
                    start_match.group(1).casefold()
                    if start_match is not None
                    else None
                ),
            )
        for macro in macros:
            argument_source = macro.get("argument_source") or ""
            match = timer_key.search(argument_source)
            if match is None:
                continue
            block_span, block_kind = macro_block(macro)
            if block_span is None or block_kind is None:
                continue
            start_match = timer_start.search(argument_source)
            add(
                "macro_metadata",
                macro["span"],
                block_span,
                block_kind,
                macro_id=macro["id"],
                macro_name=macro["name"],
                typed_pattern_id=(
                    patterns("macro_argument_attribute")[0].get("id")
                    if patterns("macro_argument_attribute")
                    else None
                ),
                timer_start=(
                    start_match.group(1).casefold()
                    if start_match is not None
                    else None
                ),
            )

    else:
        macro_specs = [
            *patterns("macro_name"),
            *patterns("macro_name_prefix"),
        ]
        if target == "kachel":
            standalone_names = {"kachelfolge", "kachelfolgen"}
            group_name = "kachelgruppen"
            check_name = "kachelgruppencheck"
            macro_specs = [
                spec
                for spec in macro_specs
                if _fold(str(spec.get("value", "")))
                in standalone_names
            ]

        for macro in macros:
            name = macro["name_folded"]
            matched = next(
                (
                    spec
                    for spec in macro_specs
                    if (
                        spec.get("kind") == "macro_name"
                        and name == _fold(str(spec.get("value", "")))
                    )
                    or (
                        spec.get("kind") == "macro_name_prefix"
                        and name.startswith(
                            _fold(str(spec.get("value", "")))
                        )
                    )
                ),
                None,
            )
            if matched is None:
                continue
            forbidden_first = matched.get("forbidden_first_argument")
            if (
                forbidden_first is not None
                and macro["arguments"]
                and _fold(macro["arguments"][0])
                == _fold(str(forbidden_first))
            ):
                continue
            block_span, block_kind = macro_block(
                macro,
                require_quiz=bool(matched.get("requires_native_quiz")),
            )
            if block_span is None or block_kind is None:
                continue
            add(
                "macro",
                macro["span"],
                block_span,
                block_kind,
                macro_id=macro["id"],
                macro_name=macro["name"],
                typed_pattern_id=matched.get("id"),
            )
        if target == "kachel":
            group_macros = [
                item
                for item in macros
                if item["name_folded"] == group_name
            ]
            check_macros = [
                item
                for item in macros
                if item["name_folded"] == check_name
            ]
            handled_tables: set[tuple[int, int]] = set()
            for group in group_macros:
                line_number = group["span"]["line_start"]
                first = line_number - 1
                last = line_number - 1
                while first > 0 and re.match(
                    r"^[ \t]*\|.*\|[ \t]*$",
                    sm.lines[first - 1]["text"],
                ):
                    first -= 1
                while last + 1 < len(sm.lines) and re.match(
                    r"^[ \t]*\|.*\|[ \t]*$",
                    sm.lines[last + 1]["text"],
                ):
                    last += 1
                table_key = (first, last)
                if table_key in handled_tables:
                    continue
                handled_tables.add(table_key)
                groups = [
                    item
                    for item in group_macros
                    if first + 1
                    <= item["span"]["line_start"]
                    <= last + 1
                ]
                checks = [
                    item
                    for item in check_macros
                    if item["span"]["line_start"] == last + 2
                    and item["standalone_line"]
                ]
                if not groups or len(checks) != 1:
                    continue
                check = checks[0]
                block_span = sm.span(
                    sm.lines[first]["start"],
                    sm.line_for_offset(check["span"]["char_start"])[
                        "end_with_eol"
                    ],
                )
                spec = next(
                    item
                    for item in patterns("macro_name")
                    if _fold(str(item.get("value", ""))) == group_name
                )
                add(
                    "macro_group",
                    sm.span(
                        groups[0]["span"]["char_start"],
                        check["span"]["char_end"],
                    ),
                    block_span,
                    "kachel_table_group",
                    macro_ids=[item["id"] for item in groups],
                    check_macro_id=check["id"],
                    macro_name="KachelgruppeN+KachelgruppenCheck",
                    typed_pattern_id=spec.get("id"),
                )

            for html_range in html_ranges:
                matched = next(
                    (
                        spec
                        for spec in patterns("html_class")
                        if html_range.get("balanced")
                        and (
                            not spec.get("tag")
                            or html_range["tag"]
                            == str(spec["tag"]).casefold()
                        )
                        and any(
                            _fold(value)
                            == _fold(str(spec.get("value", "")))
                            for value in html_range["classes"]
                        )
                    ),
                    None,
                )
                if matched is not None:
                    add(
                        "html",
                        html_range["open_span"],
                        html_range["span"],
                        "html",
                        html_id=html_range["id"],
                        typed_pattern_id=matched.get("id"),
                    )
        if target == "canvasocr":
            for html_range in html_ranges:
                matched = next(
                    (
                        spec
                        for spec in patterns("html_class")
                        if html_range.get("balanced")
                        and (
                            not spec.get("tag")
                            or html_range["tag"]
                            == str(spec["tag"]).casefold()
                        )
                        and any(
                            _fold(value)
                            == _fold(str(spec.get("value", "")))
                            for value in html_range["classes"]
                        )
                    ),
                    None,
                )
                if matched is None:
                    continue
                add(
                    "html",
                    html_range["open_span"],
                    html_range["span"],
                    "html",
                    html_id=html_range["id"],
                    typed_pattern_id=matched.get("id"),
                )
        if target == "llm":
            metadata_specs = patterns("html_comment_attribute_prefix")
            closed_fences = [
                item
                for item in protected
                if item.get("kind") == "fence" and item.get("closed")
            ]
            for comment in comments:
                comment_start = comment["span"]["char_start"]
                raw = sm.lex_text[
                    comment_start : comment["span"]["char_end"]
                ]
                matched_spec = None
                matched_attr = None
                for spec in metadata_specs:
                    matched_attr = re.search(
                        r"\b("
                        + re.escape(str(spec.get("prefix", "data-llm")))
                        + r"[A-Za-z0-9_-]*)\s*=",
                        raw,
                        flags=re.IGNORECASE,
                    )
                    if matched_attr is not None:
                        matched_spec = spec
                        break
                if matched_spec is None or matched_attr is None:
                    continue
                slide_id = _slide_id_at(headings, comment_start)
                following_quizzes = [
                    item
                    for item in quiz_ranges
                    if item["slide_id"] == slide_id
                    and (
                        item["span"]["char_start"]
                        <= comment_start
                        < item["span"]["char_end"]
                        or item["span"]["char_start"]
                        >= comment["span"]["char_end"]
                    )
                ]
                following_fences = [
                    item
                    for item in closed_fences
                    if _slide_id_at(headings, item["span"]["char_start"])
                    == slide_id
                    and item["span"]["char_start"]
                    >= comment["span"]["char_end"]
                ]
                quiz = (
                    min(
                        following_quizzes,
                        key=lambda item: item["span"]["char_start"],
                    )
                    if following_quizzes
                    else None
                )
                fence = (
                    min(
                        following_fences,
                        key=lambda item: item["span"]["char_start"],
                    )
                    if following_fences
                    else None
                )
                if quiz is None and fence is None:
                    continue
                if quiz is not None and fence is not None:
                    quiz_start = quiz["span"]["char_start"]
                    quiz_end = quiz["span"]["char_end"]
                    fence_start = fence["span"]["char_start"]
                    fence_end = fence["span"]["char_end"]
                    if quiz_start <= fence_end and fence_start <= quiz_end:
                        block_span = sm.span(
                            min(quiz_start, fence_start),
                            max(quiz_end, fence_end),
                        )
                        block_kind = "native_quiz_with_fence"
                    elif fence_start < quiz_start:
                        block_span = fence["span"]
                        block_kind = "fence"
                        quiz = None
                    else:
                        block_span = quiz["span"]
                        block_kind = "native_quiz"
                        fence = None
                elif quiz is not None:
                    block_span = quiz["span"]
                    block_kind = "native_quiz"
                else:
                    block_span = fence["span"]
                    block_kind = "fence"
                supporting_span = sm.span(
                    comment_start + matched_attr.start(),
                    comment_start + matched_attr.end(),
                    include_raw=True,
                )
                existing = next(
                    (
                        item
                        for item in instances
                        if fence is not None
                        and item["block_span"]["char_start"]
                        == fence["span"]["char_start"]
                        and item["block_span"]["char_end"]
                        == fence["span"]["char_end"]
                    ),
                    None,
                )
                if existing is not None:
                    existing["block_span"] = block_span
                    existing["block_kind"] = block_kind
                    existing.setdefault("supporting_syntax", []).append(
                        {
                            "typed_pattern_id": matched_spec.get("id"),
                            "span": supporting_span,
                        }
                    )
                else:
                    add(
                        "typed_metadata",
                        supporting_span,
                        block_span,
                        block_kind,
                        metadata_container_span=comment["span"],
                        typed_pattern_id=matched_spec.get("id"),
                    )

            for html_range in html_ranges:
                if not html_range.get("balanced"):
                    continue
                raw = html_range["open_span"].get("raw", "")
                for spec in patterns("html_attribute_prefix"):
                    match = re.search(
                        r"\b("
                        + re.escape(str(spec.get("prefix", "data-llm")))
                        + r"[A-Za-z0-9_-]*)\s*=",
                        raw,
                        flags=re.IGNORECASE,
                    )
                    if match is None:
                        continue
                    start = html_range["open_span"]["char_start"] + match.start()
                    add(
                        "html_metadata",
                        sm.span(
                            start,
                            start + len(match.group(0)),
                            include_raw=True,
                        ),
                        html_range["span"],
                        "html",
                        html_id=html_range["id"],
                        typed_pattern_id=spec.get("id"),
                    )
                    break
        if target == "coordinate":
            for spec in patterns("fenced_call"):
                callee_parts = [
                    re.escape(part)
                    for part in str(spec.get("callee", "")).split(".")
                ]
                call_re = re.compile(
                    r"\b" + r"\s*\.\s*".join(callee_parts) + r"\s*\(",
                    flags=re.IGNORECASE,
                )
                required = [
                    str(value)
                    for value in spec.get("required_fence_decorators", [])
                ]
                for fence in protected:
                    if fence.get("kind") != "fence" or not fence.get("closed"):
                        continue
                    info = str(fence.get("info", ""))
                    if required and not any(
                        re.search(
                            r"@" + re.escape(value) + r"(?=$|[\s(])",
                            info,
                            flags=re.IGNORECASE,
                        )
                        for value in required
                    ):
                        continue
                    raw = sm.lex_text[
                        fence["span"]["char_start"] : fence["span"]["char_end"]
                    ]
                    match = call_re.search(raw)
                    if match is None:
                        continue
                    start = fence["span"]["char_start"] + match.start()
                    add(
                        "fenced_call",
                        sm.span(
                            start,
                            start + len(match.group(0)),
                            include_raw=True,
                        ),
                        fence["span"],
                        "fence",
                        typed_pattern_id=spec.get("id"),
                        fence_open_line=fence.get("open_line"),
                    )

            coordinate_slides = {
                item["slide_id"] for item in instances
            }
            for html_range in html_ranges:
                if not html_range.get("balanced"):
                    continue
                raw = html_range["open_span"].get("raw", "")
                id_match = re.search(
                    r"\bid\s*=\s*([^\s>]+)",
                    raw,
                    flags=re.IGNORECASE,
                )
                html_id = (
                    id_match.group(1).strip(chr(34) + chr(39))
                    if id_match is not None
                    else ""
                )
                matched = next(
                    (
                        spec
                        for spec in [
                            *patterns("html_class"),
                            *patterns("html_id"),
                        ]
                        if (
                            spec.get("kind") == "html_class"
                            and any(
                                _fold(value)
                                == _fold(str(spec.get("value", "")))
                                for value in html_range["classes"]
                            )
                        )
                        or (
                            spec.get("kind") == "html_id"
                            and _fold(html_id)
                            == _fold(str(spec.get("value", "")))
                        )
                    ),
                    None,
                )
                if matched is None:
                    continue
                slide_id = _slide_id_at(
                    headings, html_range["span"]["char_start"]
                )
                if slide_id not in coordinate_slides:
                    continue
                add(
                    "html",
                    html_range["open_span"],
                    html_range["span"],
                    "html",
                    html_id=html_range["id"],
                    typed_pattern_id=matched.get("id"),
                    supporting_only=True,
                )

    instances.sort(key=lambda item: item["span"]["char_start"])
    for identifier, instance in enumerate(instances):
        instance["id"] = identifier
    return instances


def _provider_targets(
    sm: SourceMap,
    catalog: dict[str, Any],
    header: dict[str, Any] | None,
    excluded: Sequence[dict[str, Any]],
    comments: Sequence[dict[str, Any]],
    macros: Sequence[dict[str, Any]],
    html_ranges: Sequence[dict[str, Any]],
    quiz_ranges: Sequence[dict[str, Any]],
    headings: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    imports = header["imports"] if header else []
    imported_providers = {
        item.get("provider") for item in imports if item.get("provider")
    }
    targets: list[dict[str, Any]] = []
    aliases: dict[str, str] = {}
    for provider in catalog.get("template_providers", []):
        provider_name = str(provider.get("provider"))
        direct_import = provider_name in imported_providers
        aliases.update(
            {
                str(alias): str(canonical)
                for alias, canonical in provider.get("target_aliases", {}).items()
            }
        )
        for target in provider.get("targets", []):
            target = str(target)
            target_spec = provider.get("target_specs", {}).get(target, {})
            scope = target_spec.get("scope", provider.get("scope"))
            patterns = target_spec.get(
                "instance_patterns", provider.get("instance_patterns", [])
            )
            required_state = target_spec.get(
                "required_state", provider.get("required_state")
            )
            block_policy = target_spec.get(
                "block_policy", provider.get("block_policy")
            )
            instances = _semantic_provider_instances(
                sm,
                target,
                block_policy=block_policy,
                typed_patterns=target_spec.get(
                    "typed_instance_patterns",
                    provider.get("typed_instance_patterns", []),
                ),
                protected=excluded,
                comments=comments,
                macros=macros,
                html_ranges=html_ranges,
                quiz_ranges=quiz_ranges,
                headings=headings,
            )
            for instance in instances:
                instance["required_state"] = required_state

            hard_required = [
                str(value) for value in provider.get("hard_required_imports", [])
            ]
            missing_hard = [
                value
                for value in hard_required
                if not any(value.casefold() in item["normalized_url"].casefold() for item in imports)
            ]
            observed_companions = [
                {
                    "pattern": str(value),
                    "present": any(
                        str(value).casefold() in item["normalized_url"].casefold()
                        for item in imports
                    ),
                }
                for value in provider.get("observed_companion_imports", [])
            ]

            reasons: list[str] = []
            if not direct_import:
                reasons.append("direct_import_missing")
            if missing_hard:
                reasons.append("hard_required_import_missing")
            if scope != "global" and not instances:
                reasons.append("source_instance_missing")
            eligible = not reasons
            source_contract_status = "proven" if eligible else "disproven"
            state_status = "runtime_required" if eligible else "disproven"

            purpose_states: dict[str, dict[str, Any]] = {}
            for purpose, purpose_state in provider.get(
                "purpose_states", {}
            ).items():
                purpose_instances = list(instances)
                if target == "timer" and purpose == "lock":
                    purpose_instances = [
                        item
                        for item in instances
                        if item.get("timer_start") == "onclick"
                    ]
                elif target == "freeze" and purpose == "lock":
                    purpose_instances = [
                        item
                        for item in instances
                        if _fold(str(item.get("macro_name", "")))
                        in {"abgabe", "adetails"}
                    ]
                purpose_reasons = [
                    reason
                    for reason in reasons
                    if reason != "source_instance_missing"
                ]
                if not purpose_instances:
                    purpose_reasons.append(
                        "purpose_source_instance_missing"
                    )
                purpose_eligible = not purpose_reasons
                purpose_states[str(purpose)] = {
                    "required_state": purpose_state,
                    "source_contract_status": (
                        "proven" if purpose_eligible else "disproven"
                    ),
                    "state_status": (
                        "runtime_required"
                        if purpose_eligible
                        else "disproven"
                    ),
                    "eligible": purpose_eligible,
                    "evidence_instance_ids": [
                        item["id"] for item in purpose_instances
                    ],
                    "exclusion_reasons": purpose_reasons,
                }

            selected_by_slide: list[dict[str, Any]] = []
            for slide_id in sorted(
                {
                    item["slide_id"]
                    for item in instances
                    if item["slide_id"] is not None
                }
            ):
                first = next(
                    item
                    for item in instances
                    if item["slide_id"] == slide_id
                )
                selected_by_slide.append(
                    {
                        "slide_id": slide_id,
                        "instance_id": first["id"],
                    }
                )
            targets.append(
                {
                    "provider": provider_name,
                    "target": target,
                    "canonical_target": target,
                    "scope": scope,
                    "direct_import": direct_import,
                    "hard_required_imports": hard_required,
                    "missing_hard_required_imports": missing_hard,
                    "observed_companion_imports": observed_companions,
                    "instances": instances,
                    "selected_instance": instances[0] if instances else None,
                    "selected_instances_by_slide": selected_by_slide,
                    "required_state": required_state,
                    "source_contract_status": source_contract_status,
                    "state_status": state_status,
                    "eligible": eligible,
                    "block_policy": block_policy,
                    "purpose_states": purpose_states,
                    "exclusion_reasons": reasons,
                }
            )

    expected_count = catalog.get("reviewed_source", {}).get(
        "canonical_target_count"
    )
    native_targets = [
        {
            "provider": "native-liascript",
            "target": str(item["id"]),
            "canonical_target": str(item["id"]),
            "scope": str(item.get("scope", "global")),
            "direct_import": True,
            "instances": [],
            "selected_instance": None,
            "required_state": item.get("required_state"),
            "source_contract_status": "proven",
            "state_status": "runtime_required",
            "eligible": True,
            "block_policy": "no_local_block_for_global_surface",
            "purpose_states": {},
            "exclusion_reasons": [],
        }
        for item in catalog.get("native_targets", [])
    ]
    return {
        "catalog_target_count": expected_count,
        "mapped_target_count": len(targets),
        "target_aliases": aliases,
        "targets": targets,
        "native_targets": native_targets,
        "count_matches_catalog": expected_count == len(targets),
    }


def _integer_matrix(value: str) -> list[list[int]]:
    rows = re.findall(r"\[([^\[\]]+)\]", value)
    result: list[list[int]] = []
    for row in rows:
        numbers = [int(number) for number in re.findall(r"-?\d+", row)]
        if numbers:
            result.append(numbers)
    return result


def _reward_name(name: str) -> str | None:
    folded = _fold(name)
    if folded in {"energiekiste", "energietruhe"}:
        return "Energiekiste"
    if folded == "schatztruhe":
        return "Schatztruhe"
    if folded in {"diamanttruhe", "diamantentruhe"}:
        return "Diamanttruhe"
    return None


def _garden_fingerprints(
    sm: SourceMap,
    headings: Sequence[dict[str, Any]],
    macros: Sequence[dict[str, Any]],
    environment: dict[str, Any],
) -> list[dict[str, Any]]:
    macro_by_id = {item["id"]: item for item in macros}
    gardens: list[dict[str, Any]] = []
    for heading in headings:
        if heading["role"] != "garden":
            continue
        slide_id = heading["id"]
        slide_macros = [
            item
            for item in macros
            if item["slide_id"] == slide_id and item["usage_context"] == "body"
        ]
        inline_by_id = {
            item["macro_id"]: item
            for item in environment["inline_reveals"]
            if item["slide_id"] == slide_id
        }
        tools = [
            item["name"]
            for item in environment["tool_events"]
            if item["slide_id"] == slide_id
            and item["tool"] in {"shovel", "watering_can"}
        ]

        tutorial: list[dict[str, Any]] = []
        pieces: list[dict[str, Any]] = []
        for macro_id, reveal in sorted(
            inline_by_id.items(),
            key=lambda pair: macro_by_id[pair[0]]["span"]["char_start"],
        ):
            children = [macro_by_id[identifier] for identifier in reveal["payload_macro_ids"]]
            reward_children = [
                _reward_name(child["name"]) for child in children
                if _reward_name(child["name"]) is not None
            ]
            if reward_children:
                tutorial.append(
                    {
                        "kind": reveal["kind"],
                        "payload": reward_children,
                    }
                )
            for child in children:
                if child["name_folded"] != "puzzleteil":
                    continue
                number_match = re.search(
                    r"\d+", child["arguments"][-1] if child["arguments"] else ""
                )
                pieces.append(
                    {
                        "wrapper": reveal["kind"],
                        "color": child["arguments"][0].strip() if child["arguments"] else None,
                        "number": int(number_match.group()) if number_match else None,
                    }
                )

        gate_macro = next(
            (item for item in slide_macros if item["name_folded"] == "puzzletor"),
            None,
        )
        gate = None
        if gate_macro:
            gate = {
                "color": gate_macro["arguments"][0].strip()
                if gate_macro["arguments"]
                else None,
                "matrix": _integer_matrix(gate_macro["arguments"][1])
                if len(gate_macro["arguments"]) > 1
                else [],
                "mode": gate_macro["arguments"][2].strip()
                if len(gate_macro["arguments"]) > 2
                else None,
            }

        block_pairs = [
            item
            for item in environment["block_pairs"]
            if item["slide_id"] == slide_id
            and (
                gate_macro is None
                or item["open_span"]["char_start"] > gate_macro["span"]["char_start"]
            )
        ]
        block_pairs.sort(key=lambda item: item["open_span"]["char_start"])
        post_gate: list[dict[str, Any]] = []
        for pair in block_pairs:
            rewards = Counter()
            for macro_id in pair["payload_macro_ids"]:
                reward = _reward_name(macro_by_id[macro_id]["name"])
                if reward:
                    rewards[reward] += 1
            post_gate.append(
                {
                    "kind": pair["kind"],
                    "rewards": dict(sorted(rewards.items())),
                }
            )

        canonical = {
            "tools": tools,
            "tutorial": tutorial,
            "pieces": pieces,
            "gate": gate,
            "post_gate": post_gate,
        }
        canonical_json = json.dumps(
            canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        if block_pairs:
            fingerprint_end = max(
                item["close_span"]["char_end"] for item in block_pairs
            )
        elif slide_macros:
            fingerprint_end = max(
                item["span"]["char_end"] for item in slide_macros
            )
        else:
            fingerprint_end = heading["span"]["char_end"]
        fingerprint_start = heading["span"]["char_start"]
        normalized_raw = (
            sm.text[fingerprint_start:fingerprint_end]
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )
        reveal_counts = Counter()
        for item in inline_by_id.values():
            reveal_counts[item["kind"]] += 1
        for item in environment["block_pairs"]:
            if item["slide_id"] == slide_id:
                reveal_counts[item["kind"]] += 1
        reward_totals = Counter()
        for macro in slide_macros:
            reward = _reward_name(macro["name"])
            if reward:
                reward_totals[reward] += 1
        gardens.append(
            {
                "slide_id": slide_id,
                "heading": heading["title"],
                "page_span": heading["slide_span"],
                "fingerprint_span": sm.span(fingerprint_start, fingerprint_end),
                "raw_normalized_character_count": len(normalized_raw),
                "raw_normalized_sha256": hashlib.sha256(
                    normalized_raw.encode("utf-8")
                ).hexdigest(),
                "structural": canonical,
                "structural_sha256": hashlib.sha256(
                    canonical_json.encode("utf-8")
                ).hexdigest(),
                "reveal_instance_counts": dict(reveal_counts),
                "reward_counts": dict(reward_totals),
                "tool_order": tools,
            }
        )
    return gardens


def _anchor_context_reasons(context: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for flag, reason in (
        ("inside_header", "inside_header"),
        ("inside_fence", "inside_fence"),
        ("inside_inline_code", "inside_inline_code"),
        ("inside_html_comment", "inside_html_comment"),
        ("inside_math", "inside_math"),
        ("inside_table_or_quiz", "inside_table_or_quiz"),
        ("inside_list", "inside_list"),
        ("inside_blockquote", "inside_blockquote"),
    ):
        if context.get(flag):
            reasons.append(reason)
    if context.get("html_depth", 0):
        reasons.append("inside_html")
    if context.get("feedback_depth", 0):
        reasons.append("inside_feedback")
    return reasons


def _make_anchor(
    sm: SourceMap,
    candidate_class: str,
    position: int,
    context_arguments: dict[str, Any],
    *,
    slide_id: int | None = None,
    role: str | None = None,
    action: str | None = None,
    close_position: int | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = _context_at(sm, position, **context_arguments)
    if slide_id is not None:
        context["slide_id"] = slide_id
    reasons = _anchor_context_reasons(context)
    result: dict[str, Any] = {
        "candidate_class": candidate_class,
        "anchor": sm.span(position, position),
        "slide_id": context["slide_id"],
        "context": context,
        "valid_block_boundary": not reasons,
        "exclusion_reasons": reasons,
    }
    if role:
        result["role"] = role
    if action:
        result["action"] = action
    if close_position is not None:
        close_context = _context_at(sm, close_position, **context_arguments)
        close_reasons = _anchor_context_reasons(close_context)
        result["close_anchor"] = sm.span(close_position, close_position)
        result["close_context"] = close_context
        result["valid_block_boundary"] = not reasons and not close_reasons
        result["exclusion_reasons"] = sorted(set(reasons + close_reasons))
    if evidence:
        result["evidence"] = evidence
    return result


def _candidate_anchors(
    sm: SourceMap,
    catalog: dict[str, Any],
    headings: Sequence[dict[str, Any]],
    html_ranges: Sequence[dict[str, Any]],
    feedback_ranges: Sequence[dict[str, Any]],
    quiz_ranges: Sequence[dict[str, Any]],
    lootif_ranges: Sequence[dict[str, Any]],
    macros: Sequence[dict[str, Any]],
    environment: dict[str, Any],
    providers: dict[str, Any],
    gardens: Sequence[dict[str, Any]],
    context_arguments: dict[str, Any],
) -> dict[str, Any]:
    specs = {
        str(item["id"]): item for item in catalog.get("candidate_classes", [])
    }
    if not specs:
        specs = {
            identifier: {"id": identifier, "forms": []}
            for identifier in DEFAULT_CANDIDATE_CLASSES
        }
    buckets: dict[str, list[dict[str, Any]]] = {
        identifier: [] for identifier in specs
    }

    def add(identifier: str, anchor: dict[str, Any]) -> None:
        if identifier not in buckets:
            buckets[identifier] = []
        anchor["allowed_forms"] = list(specs.get(identifier, {}).get("forms", []))
        anchor["requires"] = list(specs.get(identifier, {}).get("requires", []))
        anchor["id"] = f"{identifier}:{len(buckets[identifier])}"
        buckets[identifier].append(anchor)

    if headings:
        start = headings[0]
        start_position = start["line_end_with_eol"]
        add(
            "start_bootstrap",
            _make_anchor(
                sm, "start_bootstrap", start_position, context_arguments,
                slide_id=start["id"], role="after_start_heading",
            ),
        )
        start_tools = [
            item for item in environment["tool_events"] if item["slide_id"] == start["id"]
        ]
        post_tool_position = (
            sm.line_for_offset(start_tools[-1]["span"]["char_end"])["end_with_eol"]
            if start_tools else start_position
        )
        add(
            "start_post_tool_block",
            _make_anchor(
                sm, "start_post_tool_block", post_tool_position, context_arguments,
                slide_id=start["id"], role="after_last_start_tool",
            ),
        )

    for heading in headings:
        if heading["level"] != 2:
            continue
        open_position = heading["line_end_with_eol"]
        close_position = heading["slide_span"]["char_end"]
        add(
            "h2_whole_slide",
            _make_anchor(
                sm, "h2_whole_slide", open_position, context_arguments,
                slide_id=heading["id"], role=heading["role"],
                close_position=close_position,
                evidence={"heading": heading["title"]},
            ),
        )
        for role, position in (("prefix", open_position), ("suffix", close_position)):
            add(
                "h2_prefix_or_suffix",
                _make_anchor(
                    sm, "h2_prefix_or_suffix", position, context_arguments,
                    slide_id=heading["id"], role=role,
                    evidence={"heading": heading["title"]},
                ),
            )

    for html_range in html_ranges:
        if (
            html_range["tag"] == "section"
            and html_range["top_level"]
            and any(_fold(value) == "dynflex" for value in html_range["classes"])
        ):
            add(
                "dynflex_whole_section",
                _make_anchor(
                    sm,
                    "dynflex_whole_section",
                    html_range["open_span"]["char_start"],
                    context_arguments,
                    slide_id=html_range["slide_id"],
                    role="wrap_from_outside",
                    close_position=html_range["close_span"]["char_end"],
                    evidence={"html_id": html_range["id"]},
                ),
            )

    for quiz in quiz_ranges:
        quiz_html_hosts = [
            item
            for item in html_ranges
            if item["open_span"]["char_end"] <= quiz["span"]["char_start"]
            and quiz["span"]["char_end"] <= item["close_span"]["char_start"]
        ]
        quiz_anchor = _make_anchor(
            sm,
            "standalone_quiz",
            quiz["span"]["char_start"],
            context_arguments,
            slide_id=quiz["slide_id"],
            role="wrap_native_quiz",
            close_position=quiz["span"]["char_end"],
            evidence={
                "instance_kind": "native_quiz",
                "quiz_id": quiz["id"],
                "container_kind": quiz["container_kind"],
                "balanced_html_host_ids": [
                    item["id"] for item in quiz_html_hosts
                ],
            },
        )
        allowed_reasons: set[str] = set()
        if quiz["container_kind"] == "list":
            allowed_reasons.add("inside_list")
        if any(
            item["span"]["char_start"] == quiz["span"]["char_start"]
            for item in context_arguments["comments"]
        ):
            allowed_reasons.add("inside_html_comment")
        quiz_anchor["specialized_boundary"] = "complete_native_quiz"
        quiz_anchor["exclusion_reasons"] = [
            reason
            for reason in quiz_anchor["exclusion_reasons"]
            if reason not in allowed_reasons
        ]
        quiz_anchor["valid_block_boundary"] = not quiz_anchor[
            "exclusion_reasons"
        ]
        add(
            "standalone_quiz",
            quiz_anchor,
        )

    quiz_names = {
        "orthography",
        "diktat",
        "textmarkerquiz",
        "llmquiz",
        "kachel",
    }
    for macro in macros:
        folded = macro["name_folded"]
        if "quiz" in folded or folded in quiz_names:
            if any(
                quiz["span"]["char_start"]
                <= macro["span"]["char_start"]
                < quiz["span"]["char_end"]
                for quiz in quiz_ranges
            ):
                continue
            line = sm.line_for_offset(macro["span"]["char_start"])
            add(
                "standalone_quiz",
                _make_anchor(
                    sm, "standalone_quiz", line["start"], context_arguments,
                    slide_id=macro["slide_id"], role="before_quiz",
                    close_position=line["end_with_eol"],
                    evidence={"macro_id": macro["id"], "macro": macro["name"]},
                ),
            )

    for feedback in feedback_ranges:
        host_html_ranges = [
            item
            for item in html_ranges
            if item["open_span"]["char_end"]
            <= feedback["span"]["char_start"]
            and feedback["span"]["char_end"]
            <= item["close_span"]["char_start"]
        ]
        tail = _make_anchor(
            sm,
            "solution_reward_tail",
            feedback["close_span"]["char_start"],
            context_arguments,
            slide_id=feedback["slide_id"],
            role="before_feedback_close",
            evidence={
                "feedback_open_line": feedback["open_span"]["line_start"],
                "feedback_close_line": feedback["close_span"]["line_start"],
                "balanced_html_host_ids": [
                    item["id"] for item in host_html_ranges
                ],
            },
        )
        # This class intentionally inserts the reward as the final payload item
        # of a feedback block. It is therefore the one safe specialized
        # boundary for which feedback_depth == 1 is expected.
        tail["specialized_boundary"] = "solution_tail_inside_feedback"
        allowed_reasons = {"inside_feedback"}
        native_quiz_hosts = [
            item
            for item in quiz_ranges
            if item["span"]["char_start"]
            <= feedback["span"]["char_start"]
            and feedback["span"]["char_end"]
            <= item["span"]["char_end"]
        ]
        if native_quiz_hosts:
            allowed_reasons.add("inside_table_or_quiz")
            tail["evidence"]["native_quiz_host_ids"] = [
                item["id"] for item in native_quiz_hosts
            ]
        if (
            tail["context"]["html_depth"]
            and len(host_html_ranges) == tail["context"]["html_depth"]
        ):
            allowed_reasons.add("inside_html")
        tail["exclusion_reasons"] = [
            reason
            for reason in tail["exclusion_reasons"]
            if reason not in allowed_reasons
        ]
        tail["valid_block_boundary"] = not tail["exclusion_reasons"]
        add(
            "solution_reward_tail",
            tail,
        )

    generic_block_boundaries: list[dict[str, Any]] = []
    for index, line in enumerate(sm.lines):
        current = line["text"].strip()
        previous_blank = index == 0 or not sm.lines[index - 1]["text"].strip()
        next_blank = index + 1 >= len(sm.lines) or not sm.lines[index + 1]["text"].strip()
        context = _context_at(sm, line["start"], **context_arguments)
        if (not current or previous_blank or next_blank) and not _anchor_context_reasons(context):
            if context["slide_id"] is not None:
                generic_block_boundaries.append(
                    {
                        "id": f"block_boundary:{len(generic_block_boundaries)}",
                        "anchor": sm.span(line["start"], line["start"]),
                        "slide_id": context["slide_id"],
                        "context": context,
                    }
                )
        if (
            current
            and any(char.isalpha() for char in current)
            and not re.match(r"^[#<>@|*\[\]{}]", current)
            and not _anchor_context_reasons(context)
        ):
            add(
                "flow_text_clue",
                _make_anchor(
                    sm, "flow_text_clue", line["end"], context_arguments,
                    slide_id=context["slide_id"], role="line_end_inline",
                    evidence={"line": line["number"]},
                ),
            )

    for target in providers["targets"]:
        if not target["eligible"]:
            continue
        if target["scope"] == "global":
            if headings:
                add(
                    "global_surface_target",
                    _make_anchor(
                        sm,
                        "global_surface_target",
                        headings[0]["line_end_with_eol"],
                        context_arguments,
                        slide_id=headings[0]["id"],
                        role="global_target_declaration",
                        evidence={
                            "provider": target["provider"],
                            "target": target["target"],
                            "state_status": target["state_status"],
                            "target_eligible": target["eligible"],
                            "block_policy": target["block_policy"],
                        },
                    ),
                )
        else:
            for instance in target["instances"]:
                block_span = instance["block_span"]
                add(
                    "local_template_target",
                    _make_anchor(
                        sm,
                        "local_template_target",
                        block_span["char_start"],
                        context_arguments,
                        slide_id=instance["slide_id"],
                        role="wrap_complete_instance",
                        close_position=block_span["char_end"],
                        evidence={
                            "provider": target["provider"],
                            "target": target["target"],
                            "instance_kind": instance["kind"],
                            "block_kind": instance["block_kind"],
                            "block_policy": target["block_policy"],
                            "state_status": target["state_status"],
                            "target_eligible": target["eligible"],
                        },
                    ),
                )

    for target in providers["native_targets"]:
        if not headings or not target["eligible"]:
            continue
        add(
            "global_surface_target",
            _make_anchor(
                sm,
                "global_surface_target",
                headings[0]["line_end_with_eol"],
                context_arguments,
                slide_id=headings[0]["id"],
                role="native_global_target_declaration",
                evidence={
                    "provider": target["provider"],
                    "target": target["target"],
                    "state_status": target["state_status"],
                    "target_eligible": target["eligible"],
                    "block_policy": target["block_policy"],
                },
            ),
        )

    for lootif_range in lootif_ranges:
        if not lootif_range["valid"]:
            continue
        add(
            "lootif_spawn_range",
            _make_anchor(
                sm,
                "lootif_spawn_range",
                lootif_range["span"]["char_start"],
                context_arguments,
                slide_id=lootif_range["slide_id"],
                role="wrap_complete_reachable_spawn",
                close_position=lootif_range["span"]["char_end"],
                evidence={
                    "lootif_range_id": lootif_range["id"],
                    "trigger": lootif_range["trigger"],
                    "external_trigger_status": lootif_range[
                        "external_trigger_status"
                    ],
                },
            ),
        )

    macro_by_id = {item["id"]: item for item in macros}

    def concealment_witness(
        position: int, *, reveal_kind: str | None = None
    ) -> dict[str, Any]:
        tool_events = environment["tool_events"]
        magnifiers = [item for item in tool_events if item["tool"] == "magnifier"]
        required_tool = (
            "shovel" if reveal_kind == "earth"
            else "watering_can" if reveal_kind == "plant"
            else None
        )
        matching_tools = [
            item for item in tool_events if item["tool"] == required_tool
        ] if required_tool else []
        if not magnifiers:
            status = "missing_magnifier"
        elif required_tool and not matching_tools:
            status = f"missing_{required_tool}"
        else:
            status = "human_review_required"
        prefix = [
            item for item in [*magnifiers, *matching_tools]
            if item["span"]["char_end"] <= position
        ]
        return {
            "witness_status": status,
            "discoverability_review_status": (
                "human_review_required_under_content_policy"
            ),
            "automation_eligible": False,
            "source_prefix_evidence": [
                {"tool": item["tool"], "macro_id": item["macro_id"]}
                for item in prefix
            ],
            "course_witness_evidence": [
                {"tool": item["tool"], "macro_id": item["macro_id"]}
                for item in [*magnifiers, *matching_tools]
            ],
        }

    def edit_position(variants: Sequence[dict[str, Any]], fallback: int) -> int:
        if not variants:
            return fallback
        variant = variants[0]
        if "anchor" in variant:
            return variant["anchor"]["char_start"]
        return variant["replace_span"]["char_start"]

    for pair in environment["block_pairs"]:
        if not pair["valid"]:
            continue
        variants = pair.get("visibility_edit_variants", [])
        position = edit_position(variants, pair["open_span"]["char_start"])
        anchor = _make_anchor(
            sm,
            "container_visibility_option",
            position,
            context_arguments,
            slide_id=pair["slide_id"],
            role="edit_block_reveal_options",
            evidence={
                "environment_pair_id": pair["id"],
                "kind": pair["kind"],
                "reveal_form": "block",
            },
        )
        anchor["edit_variants"] = variants
        anchor["syntax_eligible"] = pair.get(
            "visibility_syntax_valid", False
        )
        anchor.update(concealment_witness(position, reveal_kind=pair["kind"]))
        add("container_visibility_option", anchor)
    for reveal in environment["inline_reveals"]:
        variants = reveal.get("visibility_edit_variants", [])
        position = edit_position(variants, reveal["span"]["char_start"])
        anchor = _make_anchor(
            sm,
            "container_visibility_option",
            position,
            context_arguments,
            slide_id=reveal["slide_id"],
            role="edit_inline_reveal_options",
            evidence={
                "inline_reveal_macro_id": reveal["macro_id"],
                "kind": reveal["kind"],
                "reveal_form": "inline",
            },
        )
        anchor["edit_variants"] = variants
        anchor["syntax_eligible"] = reveal.get(
            "visibility_syntax_valid", False
        )
        anchor.update(
            concealment_witness(position, reveal_kind=reveal["kind"])
        )
        add("container_visibility_option", anchor)

    for item in environment["item_concealments"]:
        variants = item["edit_variants"]
        position = edit_position(variants, item["span"]["char_start"])
        anchor = _make_anchor(
            sm,
            "collectible_concealment_option",
            position,
            context_arguments,
            slide_id=item["slide_id"],
            role="edit_collectible_item_option",
            evidence={
                "item_concealment_id": item["id"],
                "macro_id": item["macro_id"],
                "carrier": item["carrier"],
            },
        )
        anchor["edit_variants"] = variants
        anchor["current_concealment"] = item["current_concealment"]
        anchor["syntax_eligible"] = item["concealment_valid"]
        anchor.update(concealment_witness(position))
        add("collectible_concealment_option", anchor)

    def wrapper_edits(child: dict[str, Any]) -> list[dict[str, Any]]:
        if child["name_folded"] in {"unsichtbar", "zauberstaub"}:
            name_span = sm.span(
                child["span"]["char_start"] + 1,
                child["span"]["char_start"] + 1 + len(child["name"]),
                include_raw=True,
            )
            return [
                {
                    "mode": mode,
                    "operation": "replace_wrapper_name",
                    "replace_span": name_span,
                    "text": wrapper,
                }
                for mode, wrapper in (
                    ("unsichtbar", "Unsichtbar"),
                    ("zauberstaub", "Zauberstaub"),
                )
            ]
        return [
            {
                "mode": mode,
                "operation": "wrap_exact_payload",
                "prefix_anchor": sm.span(
                    child["span"]["char_start"],
                    child["span"]["char_start"],
                ),
                "prefix_text": f"@{wrapper}(",
                "suffix_anchor": sm.span(
                    child["span"]["char_end"],
                    child["span"]["char_end"],
                ),
                "suffix_text": ")",
            }
            for mode, wrapper in (
                ("unsichtbar", "Unsichtbar"),
                ("zauberstaub", "Zauberstaub"),
            )
        ]

    hidden_sources: list[tuple[str, int, str, int]] = []
    environment_catalog = _catalog_environment(catalog)
    structural_reveal_names = {
        _fold(str(name))
        for spec in environment_catalog.get("block_pairs", [])
        for name in [*spec.get("open", []), *spec.get("close", [])]
    } | {
        _fold(str(name))
        for spec in environment_catalog.get("conditional_ranges", [])
        for name in [*spec.get("open", []), *spec.get("close", [])]
    } | {
        _fold(str(name))
        for name in environment_catalog.get("inline_macros", [])
    }
    for pair in environment["block_pairs"]:
        if pair["valid"]:
            hidden_sources.extend(
                ("block", pair["id"], pair["kind"], child_id)
                for child_id in pair["payload_macro_ids"]
            )
    for reveal in environment["inline_reveals"]:
        hidden_sources.extend(
            ("inline", reveal["macro_id"], reveal["kind"], child_id)
            for child_id in reveal["payload_macro_ids"]
        )
    for reveal_form, reveal_id, reveal_kind, child_id in hidden_sources:
        child = macro_by_id[child_id]
        if child["name_folded"] in structural_reveal_names:
            continue
        variants = wrapper_edits(child)
        anchor = _make_anchor(
            sm,
            "hidden_macro_inside_reveal",
            child["span"]["char_start"],
            context_arguments,
            slide_id=child["slide_id"],
            role="wrap_exact_reveal_payload_macro",
            close_position=child["span"]["char_end"],
            evidence={
                "reveal_form": reveal_form,
                "reveal_id": reveal_id,
                "reveal_kind": reveal_kind,
                "child_macro_id": child_id,
            },
        )
        anchor["edit_variants"] = variants
        anchor["current_wrapper"] = (
            child["name_folded"]
            if child["name_folded"] in {"unsichtbar", "zauberstaub"}
            else None
        )
        anchor["syntax_eligible"] = True
        anchor.update(
            concealment_witness(
                child["span"]["char_start"], reveal_kind=reveal_kind
            )
        )
        add("hidden_macro_inside_reveal", anchor)

    secret_slide_ids = {
        item["id"] for item in headings if item["role"] == "optional_secret"
    }
    portal_macros = [
        item
        for item in macros
        if item["name_folded"] in {
            "portal", "einwegportal", "einbahnportal"
        }
        and item["parent_id"] is None
        and item["usage_context"] == "body"
    ]
    for heading in headings:
        if heading["id"] in secret_slide_ids:
            add(
                "optional_secret_or_portal",
                _make_anchor(
                    sm,
                    "optional_secret_or_portal",
                    heading["line_end_with_eol"],
                    context_arguments,
                    slide_id=heading["id"],
                    role="optional_secret_slide",
                    evidence={"heading": heading["title"]},
                ),
            )
    for macro in portal_macros:
        add(
            "optional_secret_or_portal",
            _make_anchor(
                sm,
                "optional_secret_or_portal",
                macro["span"]["char_end"],
                context_arguments,
                slide_id=macro["slide_id"],
                role="lia_loot_portal_topology",
                evidence={"macro_id": macro["id"], "macro": macro["name"]},
            ),
        )

    garden_by_slide = {item["slide_id"]: item for item in gardens}
    for heading in headings:
        if heading["role"] == "reflection":
            previous = headings[heading["id"] - 1] if heading["id"] else None
            existing = (
                garden_by_slide.get(previous["id"]) if previous is not None else None
            )
            if existing:
                position = existing["fingerprint_span"]["char_start"]
                action = "vary_existing"
                evidence = {
                    "existing_garden_sha256": existing["raw_normalized_sha256"]
                }
            else:
                position = heading["span"]["char_start"]
                action = "insert_before_reflection"
                evidence = {"next_heading": heading["title"]}
            add(
                "garden_before_reflection",
                _make_anchor(
                    sm,
                    "garden_before_reflection",
                    position,
                    context_arguments,
                    slide_id=previous["id"] if previous else heading["id"],
                    role="before_reflection",
                    action=action,
                    evidence=evidence,
                ),
            )
            add(
                "reflection_optional",
                _make_anchor(
                    sm,
                    "reflection_optional",
                    heading["line_end_with_eol"],
                    context_arguments,
                    slide_id=heading["id"],
                    role="reflection_prefix",
                    evidence={"heading": heading["title"]},
                ),
            )
        elif heading["role"] == "submission":
            add(
                "submission_or_freeze",
                _make_anchor(
                    sm,
                    "submission_or_freeze",
                    heading["line_end_with_eol"],
                    context_arguments,
                    slide_id=heading["id"],
                    role="submission_prefix",
                    evidence={"heading": heading["title"]},
                ),
            )

    ordered_classes = [
        {
            "id": identifier,
            "forms": list(specs[identifier].get("forms", [])),
            "requires": list(specs[identifier].get("requires", [])),
            "conceptual_group": specs[identifier].get(
                "conceptual_group"
            ),
            "anchor_count": len(buckets.get(identifier, [])),
            "anchors": buckets.get(identifier, []),
        }
        for identifier in specs
    ]
    return {
        "catalog_class_count": len(specs),
        "classes": ordered_classes,
        "anchors": [
            anchor
            for identifier in specs
            for anchor in buckets.get(identifier, [])
        ],
        "safe_block_boundaries": generic_block_boundaries,
    }


def map_source(
    raw_bytes: bytes,
    *,
    source_path: Path | str | None = None,
    catalog: dict[str, Any] | None = None,
    catalog_path: Path | str = DEFAULT_CATALOG,
) -> dict[str, Any]:
    """Map immutable LiaScript bytes without executing or modifying them."""

    sm = SourceMap(raw_bytes, Path(source_path) if source_path else None)
    if catalog is None:
        catalog = load_catalog(catalog_path)

    diagnostics: list[dict[str, Any]] = []
    if sm.nul_offsets:
        diagnostics.append(
            {
                "code": "nul_replaced_for_commonmark",
                "count": len(sm.nul_offsets),
                "replacement": "U+FFFD",
                "positions": [sm.point(offset) for offset in sm.nul_offsets],
            }
        )
    header, found = _header(sm)
    diagnostics.extend(found)
    header_end = header["span"]["char_end"] if header else 0
    _annotate_imports(header, catalog)

    owner_seed: list[dict[str, Any]] = []
    fences: list[dict[str, Any]] = []
    fence_diagnostics: list[dict[str, Any]] = []
    provisional_indented: list[dict[str, Any]] = []
    link_reference_definitions: list[dict[str, Any]] = []
    container_contexts: dict[int, ContainerContext] = {}
    protected_owners: list[dict[str, Any]] = []
    html_protected: list[dict[str, Any]] = []
    math_spans: list[dict[str, Any]] = []
    for _ in range(6):
        pre_fence_contexts = _raw_html_container_contexts(
            sm, header_end, [*owner_seed, *link_reference_definitions]
        )
        provisional_fences, _ = _find_fences(
            sm,
            header_end,
            pre_fence_contexts,
            [*owner_seed, *link_reference_definitions],
        )
        fence_contexts = _raw_html_container_contexts(
            sm,
            header_end,
            [
                *owner_seed,
                *link_reference_definitions,
                *provisional_fences,
            ],
        )
        fences, fence_diagnostics = _find_fences(
            sm,
            header_end,
            fence_contexts,
            [*owner_seed, *link_reference_definitions],
        )
        fence_contexts = _raw_html_container_contexts(
            sm,
            header_end,
            [*owner_seed, *link_reference_definitions, *fences],
        )
        provisional_indented = _find_indented_code(
            sm,
            header_end,
            [*fences, *owner_seed, *link_reference_definitions],
            fence_contexts,
        )
        container_contexts = _raw_html_container_contexts(
            sm,
            header_end,
            [
                *owner_seed,
                *link_reference_definitions,
                *fences,
                *provisional_indented,
            ],
        )
        provisional_indented = _find_indented_code(
            sm,
            header_end,
            [*fences, *owner_seed, *link_reference_definitions],
            container_contexts,
        )
        container_contexts = _raw_html_container_contexts(
            sm,
            header_end,
            [
                *owner_seed,
                *link_reference_definitions,
                *fences,
                *provisional_indented,
            ],
        )
        next_link_reference_definitions = _find_link_reference_definitions(
            sm,
            [*fences, *provisional_indented, *owner_seed],
            header_end,
            container_contexts,
        )
        provisional_code = [
            *fences,
            *provisional_indented,
            *next_link_reference_definitions,
        ]
        provisional_html_tokens, _ = _scan_html_tags(
            sm,
            [*provisional_code, *owner_seed],
            container_contexts,
        )
        provisional_finite_html = _html_token_protection(
            provisional_html_tokens
        )
        provisional_inline = _find_inline_code(
            sm,
            [
                *provisional_code,
                *owner_seed,
                *provisional_finite_html,
            ],
            header_end,
            container_contexts,
        )
        raw_html_candidates, _ = _find_raw_html_blocks(
            sm,
            [*provisional_code, *provisional_inline],
            header_end,
            container_contexts,
        )
        html_markup_candidates, _ = _find_html_markup(
            sm,
            [*provisional_code, *provisional_inline],
            header_end,
            container_contexts,
        )
        math_candidates, _ = _find_math(
            sm,
            [
                *provisional_code,
                *provisional_inline,
                *provisional_finite_html,
            ],
            header_end,
        )
        next_owners = _select_outermost_html_spans(
            [
                *raw_html_candidates,
                *html_markup_candidates,
                *math_candidates,
            ]
        )
        seed_signature = tuple(
            (
                item["kind"],
                item["span"]["char_start"],
                item["span"]["char_end"],
            )
            for item in owner_seed
        )
        next_signature = tuple(
            (
                item["kind"],
                item["span"]["char_start"],
                item["span"]["char_end"],
            )
            for item in next_owners
        )
        link_reference_signature = tuple(
            (
                item["span"]["char_start"],
                item["span"]["char_end"],
            )
            for item in link_reference_definitions
        )
        next_link_reference_signature = tuple(
            (
                item["span"]["char_start"],
                item["span"]["char_end"],
            )
            for item in next_link_reference_definitions
        )
        protected_owners = next_owners
        link_reference_definitions = next_link_reference_definitions
        if (
            next_signature == seed_signature
            and next_link_reference_signature == link_reference_signature
        ):
            break
        owner_seed = next_owners
    html_protected = [
        item
        for item in protected_owners
        if item["kind"] not in {"display_math", "inline_math"}
    ]
    math_spans = [
        item
        for item in protected_owners
        if item["kind"] in {"display_math", "inline_math"}
    ]
    diagnostics.extend(fence_diagnostics)
    diagnostics.extend(_unterminated_html_diagnostics(html_protected))
    diagnostics.extend(
        {
            "code": "unterminated_display_math",
            "line": item["span"]["line_start"],
        }
        for item in math_spans
        if item["kind"] == "display_math" and item.get("closed") is False
    )
    raw_html = [
        item for item in html_protected if item["kind"] == "raw_html"
    ]
    html_markup = [
        item for item in html_protected if item["kind"] != "raw_html"
    ]
    indented_code = _find_indented_code(
        sm,
        header_end,
        [*fences, *protected_owners, *link_reference_definitions],
        container_contexts,
    )
    code_blocks = [*fences, *indented_code]
    finite_html_tokens, _ = _scan_html_tags(
        sm,
        [
            *code_blocks,
            *protected_owners,
            *link_reference_definitions,
        ],
        container_contexts,
    )
    finite_html_protected = _html_token_protection(finite_html_tokens)
    inline_code = _find_inline_code(
        sm,
        [
            *code_blocks,
            *protected_owners,
            *link_reference_definitions,
            *finite_html_protected,
        ],
        header_end,
        container_contexts,
    )
    comments = [
        item for item in html_markup if item["kind"] == "html_comment"
    ]
    header_protected = (
        [{"kind": "header", "span": dict(header["span"])}] if header else []
    )
    protected = [
        *header_protected,
        *link_reference_definitions,
        *code_blocks,
        *inline_code,
        *raw_html,
        *html_markup,
        *math_spans,
    ]
    protected.sort(key=lambda item: item["span"]["char_start"])
    html_structure_excluded = list(protected)
    html_tokens, found = _scan_html_tags(
        sm, html_structure_excluded, container_contexts
    )
    diagnostics.extend(found)
    html_tag_protected = _html_token_protection(html_tokens)
    protected.extend(html_tag_protected)
    protected.sort(key=lambda item: item["span"]["char_start"])
    headings = _find_headings(sm, protected, header_end)
    html_ranges, found, html_summary = _find_html(
        sm, html_structure_excluded, headings, html_tokens
    )
    diagnostics.extend(found)
    macro_protected = protected
    feedback_ranges, found = _find_feedback_ranges(sm, headings, protected)
    diagnostics.extend(found)
    table_ranges = _find_table_ranges(sm, protected, headings)
    preliminary_context = {
        "header": header,
        "fences": code_blocks,
        "inline_code": inline_code,
        "comments": comments,
        "math_spans": math_spans,
        "tables": table_ranges,
        "quiz_ranges": [],
        "html_ranges": html_ranges,
        "feedback_ranges": feedback_ranges,
        "headings": headings,
        "container_contexts": container_contexts,
    }
    preliminary_macros = _find_macros(
        sm,
        macro_protected,
        fences,
        header_end,
        preliminary_context,
    )
    quiz_ranges, found = _find_native_quiz_ranges(
        sm,
        protected,
        headings,
        table_ranges,
        preliminary_macros,
        feedback_ranges,
        container_contexts,
    )
    diagnostics.extend(found)

    context_arguments = {
        **preliminary_context,
        "quiz_ranges": quiz_ranges,
    }
    macros = _find_macros(
        sm,
        macro_protected,
        fences,
        header_end,
        context_arguments,
    )
    providers = _provider_targets(
        sm, catalog, header, protected, comments, macros,
        html_ranges, quiz_ranges, headings,
    )
    environment_pairs, found = _pair_environment_blocks(sm, macros, catalog)
    diagnostics.extend(found)
    lootif_ranges, found = _pair_lootif_ranges(
        sm, macros, quiz_ranges, headings, header,
        environment_pairs, providers, protected, html_ranges, catalog
    )
    diagnostics.extend(found)
    diagnostics.extend(
        _validate_cross_family_ranges(environment_pairs, lootif_ranges)
    )
    environment = _environment_summary(
        sm, macros, environment_pairs, catalog
    )
    gardens = _garden_fingerprints(sm, headings, macros, environment)
    candidates = _candidate_anchors(
        sm,
        catalog,
        headings,
        html_ranges,
        feedback_ranges,
        quiz_ranges,
        lootif_ranges,
        macros,
        environment,
        providers,
        gardens,
        context_arguments,
    )

    if not header:
        diagnostics.append({"code": "main_header_missing", "line": 1})
    else:
        loot_count = len(header["loot_import_orders"])
        if loot_count == 0:
            diagnostics.append({"code": "lia_loot_import_missing"})
        elif loot_count > 1:
            diagnostics.append(
                {"code": "duplicate_lia_loot_import", "count": loot_count}
            )
    if not providers["count_matches_catalog"]:
        diagnostics.append(
            {
                "code": "provider_target_count_mismatch",
                "expected": providers["catalog_target_count"],
                "actual": providers["mapped_target_count"],
            }
        )
    for layer in environment["invalid_direct_layers"]:
        diagnostics.append(
            {
                "code": "direct_layer_on_unsupported_carrier",
                "macro_id": layer["macro_id"],
                "carrier": layer["carrier"],
                "line": layer["span"]["line_start"],
            }
        )

    if b"\r\n" in raw_bytes and raw_bytes.replace(b"\r\n", b"").find(b"\n") >= 0:
        newline_style = "mixed"
    elif b"\r\n" in raw_bytes:
        newline_style = "crlf"
    elif b"\n" in raw_bytes:
        newline_style = "lf"
    else:
        newline_style = "none"

    return {
        "schema_version": "1.0.0",
        "source": {
            "path": str(source_path) if source_path is not None else None,
            "sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "byte_count": len(raw_bytes),
            "character_count": len(sm.text),
            "line_count": len(sm.lines),
            "newline_style": newline_style,
            "encoding": "utf-8",
            "bom_bytes": sm.bom_bytes,
            "read_only": True,
        },
        "catalog": {
            "schema_version": catalog.get("schema_version"),
            "reviewed_source": catalog.get("reviewed_source"),
        },
        "header": header,
        "imports": header["imports"] if header else [],
        "import_slots": header["import_slots"] if header else [],
        "headings": headings,
        "slides": [
            {
                "id": item["id"],
                "level": item["level"],
                "title": item["title"],
                "title_folded": item["title_folded"],
                "role": item["role"],
                "heading_span": item["span"],
                "span": item["slide_span"],
            }
            for item in headings
        ],
        "protected_spans": sorted(
            [*protected, *quiz_ranges],
            key=lambda item: item["span"]["char_start"],
        ),
        "html_ranges": html_ranges,
        "html_summary": html_summary,
        "block_ranges": {
            "feedback": feedback_ranges,
            "tables": table_ranges,
            "native_quiz": quiz_ranges,
            "environment": environment_pairs,
            "lootif": lootif_ranges,
        },
        "macros": macros,
        "environment": environment,
        "provider_targets": providers,
        "candidates": candidates,
        "gardens": gardens,
        "garden_fingerprint": gardens[0] if len(gardens) == 1 else None,
        "diagnostics": diagnostics,
    }


def map_text(
    text: str,
    *,
    source_path: Path | str | None = None,
    catalog: dict[str, Any] | None = None,
    catalog_path: Path | str = DEFAULT_CATALOG,
) -> dict[str, Any]:
    return map_source(
        text.encode("utf-8"),
        source_path=source_path,
        catalog=catalog,
        catalog_path=catalog_path,
    )


def map_course(
    path: Path | str,
    *,
    catalog_path: Path | str = DEFAULT_CATALOG,
) -> dict[str, Any]:
    course_path = Path(path)
    raw_bytes = course_path.read_bytes()
    return map_source(
        raw_bytes,
        source_path=course_path,
        catalog_path=catalog_path,
    )


def _arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Map LiaScript placement positions without modifying the course."
    )
    parser.add_argument("course", type=Path, help="UTF-8 LiaScript Markdown file")
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG,
        help="placement-catalog.json path",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="indent the emitted JSON",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _arguments(argv)
    try:
        result = map_course(args.course, catalog_path=args.catalog)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"map_course: {error}", file=sys.stderr)
        return 2
    json.dump(
        result,
        sys.stdout,
        ensure_ascii=False,
        indent=2 if args.pretty else None,
        separators=None if args.pretty else (",", ":"),
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
