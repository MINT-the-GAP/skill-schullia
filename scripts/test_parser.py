#!/usr/bin/env python3
"""Small dependency-free regression tests for the LiaScript index parser."""

from __future__ import annotations

from pathlib import Path
import sys

import build_index as parser

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def test_header() -> None:
    text = """<!--
version: 0.0.1
import: https://example.test/one.md
import: https://example.test/two.md
link: https://example.test/
      style.css
tags: Trigonometrie, leicht, Angeben
comment: Kurze Beschreibung.
         Zweite eingerückte Zeile.
author: Ada; Grace
repository: https://example.test/course
icon: icon.svg
font: Noto Sans
dark: true
classroom: false
sharing: false
translateWithGoogle: false
-->
# Titel
"""
    header, end, warnings = parser.extract_header(text)
    assert end > 0 and not warnings
    assert header["imports"] == ["https://example.test/one.md", "https://example.test/two.md"]
    assert header["links"] == ["https://example.test/style.css"]
    assert header["tags"] == ["Trigonometrie", "leicht", "Angeben"]
    assert header["authors"] == ["Ada; Grace"]
    assert header["scalars"]["comment"] == "Kurze Beschreibung.\nZweite eingerückte Zeile."
    assert header["scalars"]["repository"] == "https://example.test/course"
    assert header["scalars"]["translatewithgoogle"] == "false"


def test_codex_frontmatter_is_not_a_liascript_header() -> None:
    text = """---
name: example-skill
description: Kein LiaScript-Dokumentkopf.
---
# Anweisung
"""
    header, end, warnings = parser.extract_header(text)
    assert header == {} and end == 0 and not warnings


def test_quizzes_and_operator_mismatch() -> None:
    definitions, aliases = parser.load_taxonomy(parser.DEFAULT_TAXONOMY)
    live = """# Aufgabe
**Fülle** die Lücken **aus**.
[[ 12 ]] und [[___]] und [[(rot)|blau]]
@canvas

## Auswahl
**Wähle** die richtige Antwort **aus**.
- [(X)] richtig
- [( )] falsch
- [[X]] Aussage A
- [[ ]] Aussage B
[->[(Antwort)|Beschriftung]]
"""
    document_id = "fixture"
    headings = parser.extract_headings(live)
    quizzes = parser.extract_quizzes(live, document_id, "task-content")
    macros = parser.extract_macros(live, document_id, "task-content", 0)
    declared = parser.declared_operators(["Angeben"], aliases)
    tasks, occurrences, warnings = parser.extract_tasks(
        live, document_id, headings, quizzes, macros, definitions, declared,
        ["Angeben"], "task-content",
    )
    types = {quiz["quiz_type"] for quiz in quizzes}
    assert {"text_input", "text_input_placeholder", "inline_selection", "single_choice", "multiple_choice", "drag_drop"}.issubset(types)
    assert len(tasks) == 2
    assert tasks[0]["operator_declared"] == ["angeben"]
    assert tasks[0]["operator_detected"] == ["auffuellen"]
    assert tasks[1]["operator_detected"] == ["auswaehlen"]
    assert any(warning.startswith("operator_mismatch") for warning in warnings)
    assert any(occurrence["operator_id"] == "auffuellen" for occurrence in occurrences)
    assert any(macro["name"] == "canvas" for macro in macros)


def test_header_zone_is_not_live() -> None:
    text = """<!--
@Demo
[[!]]
@end
-->
# Dokumentation
Kein Livequiz.
"""
    _, header_end, _ = parser.extract_header(text)
    body = "".join("\n" if char == "\n" else " " for char in text[:header_end]) + text[header_end:]
    assert not parser.extract_quizzes(body, "fixture", "task-content")
    macros = parser.extract_macros(text, "fixture", "task-content", header_end)
    assert macros and all(macro["usage_context"] == "definition" for macro in macros)


def main() -> int:
    test_header()
    test_codex_frontmatter_is_not_a_liascript_header()
    test_quizzes_and_operator_mismatch()
    test_header_zone_is_not_live()
    print("Parser tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
