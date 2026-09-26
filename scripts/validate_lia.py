#!/usr/bin/env python3
'''Static quality gate for generated SchulLia/LiaScript authoring output.'''

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    line: int
    message: str


HEADER_RE = re.compile(r'\A<!--\s*\n(?P<body>.*?)\n-->', re.DOTALL)
META_RE = re.compile(r'^\s*(?P<key>[\w-]+)\s*:\s*(?P<value>.*?)\s*$', re.MULTILINE)
HEADING_RE = re.compile(r'^(#{1,6})\s+\S', re.MULTILINE)
PLACEHOLDER_RE = re.compile(r'\{\{[^{}]+\}\}|\b(?:TODO|TBD|PLATZHALTER)\b', re.IGNORECASE)
ALGEBRITE_RE = re.compile(r'@Algebrite\.(?P<macro>check(?:_expression|2|_margin)?|equals)\((?P<args>[^\n]*)\)')
UNIT_RE = re.compile(
    r'(?<![\w])(?:km/h|kmh|m/s\^?2|m/s²|m/s|cm\^?2|cm²|m\^?2|m²|mm|cm|km|kg|mg|g|ml|mL|l|L|h|min|s|°C|K|J|W|N|Pa|V|A|Ω|mol)(?![\w])'
)
QUANTITY_RE = re.compile(
    r'(?:\d+(?:[.,]\d+)?|\.\d+)\s*(?:km/h|kmh|m/s\^?2|m/s²|m/s|cm\^?2|cm²|m\^?2|m²|mm|cm|km|kg|mg|g|ml|mL|l|L|h|min|s|°C|K|J|W|N|Pa|V|A|Ω|mol)(?![\w])'
)
PROVIDER_MARKERS = {
    'freeze': ('liascript-template-freeze', 'lia-freeze-v2'),
    'mathpath': ('lia-mathpath',),
    'resetter': ('lia-resetter',),
    'algebrite': ('lia-algebrite', '/algebrite/'),
    'canvas_ocr': ('lia-canvas-ocr',),
    'jsxgraph': ('jsxgraph',),
    'coordinate': ('lia-coordinate',),
    'pentomino': ('lia-pentominos',),
    'llm': ('lia-llm',),
    'orthography': ('lia-orthography',),
    'kachel': ('lia-kachel',),
    'marker': ('lia-marker',),
    'timer': ('lia-timer',),
    'loot': ('lia-loot',),
}


def add(issues: list[Issue], severity: str, code: str, line: int, message: str) -> None:
    issues.append(Issue(severity, code, max(line, 1), message))


def line_of(text: str, offset: int) -> int:
    return text.count('\n', 0, max(offset, 0)) + 1


def contains_quantity(value: str) -> bool:
    cleaned = re.sub(r'\\(?:mathrm|text)\{([^{}]+)\}', r'\1', value)
    cleaned = re.sub(r'\\[,;:! ]', '', cleaned)
    return bool(QUANTITY_RE.search(cleaned))


def parse_header(text: str) -> tuple[dict[str, list[str]], list[tuple[str, int]], int]:
    match = HEADER_RE.search(text)
    if not match:
        return {}, [], 0
    metadata: dict[str, list[str]] = {}
    imports: list[tuple[str, int]] = []
    body = match.group('body')
    body_start = match.start('body')
    for item in META_RE.finditer(body):
        key = item.group('key').lower()
        value = item.group('value').strip()
        metadata.setdefault(key, []).append(value)
        if key == 'import':
            imports.append((value, line_of(text, body_start + item.start())))
    return metadata, imports, match.end()


def split_macro_args(raw: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in raw:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in ('`', chr(39), chr(34)):
            quote = char
            current.append(char)
        elif char in '([{':
            depth += 1
            current.append(char)
        elif char in ')]}':
            depth = max(0, depth - 1)
            current.append(char)
        elif char == ',' and depth == 0:
            args.append(''.join(current).strip())
            current = []
        else:
            current.append(char)
    args.append(''.join(current).strip())
    return args


def provider_index(imports: list[tuple[str, int]], provider: str) -> int | None:
    markers = PROVIDER_MARKERS[provider]
    for index, (url, _) in enumerate(imports):
        if any(marker in url.lower() for marker in markers):
            return index
    return None


def visible_lines(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence and not line.lstrip().startswith('import:'):
            result.append((number, line))
    return result


def task_blocks(text: str) -> list[tuple[int, int, str]]:
    pattern = r'^##\s+Aufgabe\s+(\d+)(?:\s*:\s*\S.*)?\s*$'
    matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
    blocks: list[tuple[int, int, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((int(match.group(1)), line_of(text, match.start()), text[match.start():end]))
    return blocks


def has_quiz(block: str) -> bool:
    if re.search(r'\[\[(?:\s*\([^\n]*\)\s*)?(?:X|x|\s|\d|[?!])[^\n]*\]\]', block):
        return True
    quiz_macros = (
        '@BerechneOCR', '@LLMQuiz', '@TextmarkerQuiz', '@Kachelfolge',
        '@orthography', '@diktat', '@PentominoQuiz', '@PentominoDockQuiz',
        '@KoordQuiz', '@GeometrieQuiz', '@CoordinateQuiz', '@GeometryQuiz',
        '@KonstruktionQuiz', '@ConstructionQuiz', '@UmfangQuiz', '@AreaQuiz',
    )
    return any(macro in block for macro in quiz_macros)


def shell_parts(text: str) -> tuple[str, str] | None:
    first = re.search(r'^##\s+Aufgabe\s+\d+(?:\s*:\s*\S.*)?\s*$', text, re.MULTILINE | re.IGNORECASE)
    footer = re.search(r'^#\s+Abgabe\s*$', text, re.MULTILINE | re.IGNORECASE)
    if not first or not footer or footer.start() <= first.start():
        return None
    return text[:first.start()], text[footer.start():]


def validate(text: str, profile: str, reference_text: str | None = None) -> list[Issue]:
    issues: list[Issue] = []
    metadata, imports, header_end = parse_header(text)
    complete_course = profile in {'course', 'weekly'}

    if complete_course and not header_end:
        add(issues, 'error', 'header.missing', 1, 'Der LiaScript-Hauptheader muss am Dateianfang stehen.')
    if complete_course and header_end:
        for field in ('author', 'version', 'language', 'comment', 'tags'):
            values = metadata.get(field, [])
            if not values or not any(value.strip() for value in values):
                add(issues, 'error', 'header.field', 1, f'Headerfeld {field}: fehlt oder ist leer.')
            if len(values) > 1:
                add(issues, 'error', 'header.duplicate', 1, f'Headerfeld {field}: ist mehrfach vorhanden.')
            if any(PLACEHOLDER_RE.search(value) for value in values):
                add(issues, 'error', 'header.placeholder', 1, f'Headerfeld {field}: enthält einen Platzhalter.')
        after_header = text[header_end:]
        if not re.match(r'\n\n#\s+\S', after_header):
            add(issues, 'error', 'spacing.header-title', line_of(text, header_end), 'Zwischen Hauptheader und H1 muss genau eine Leerzeile stehen.')

    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            add(issues, 'error', 'spacing.trailing', number, 'Zeile enthält nachgestellte Leerzeichen.')
        if PLACEHOLDER_RE.search(line):
            add(issues, 'error', 'placeholder', number, 'Nicht ausgefüllter Platzhalter.')
    for match in re.finditer(r'\n{4,}', text):
        add(issues, 'error', 'spacing.excess', line_of(text, match.start()), 'Mehr als zwei aufeinanderfolgende Leerzeilen.')
    lines = text.splitlines()
    for match in HEADING_RE.finditer(text):
        number = line_of(text, match.start())
        index = number - 1
        before_ok = index == 0 or (not lines[index - 1].strip() and (index < 2 or lines[index - 2].strip()))
        after_ok = index + 1 < len(lines) and not lines[index + 1].strip() and (index + 2 >= len(lines) or lines[index + 2].strip())
        if not before_ok:
            add(issues, 'error', 'spacing.before-heading', number, 'Vor einer Überschrift muss genau eine Leerzeile stehen.')
        if not after_ok:
            add(issues, 'error', 'spacing.after-heading', number, 'Nach einer Überschrift muss genau eine Leerzeile stehen.')

    urls = [url for url, _ in imports]
    for url in sorted(set(urls)):
        if urls.count(url) > 1:
            line = next(number for candidate, number in imports if candidate == url)
            add(issues, 'error', 'import.duplicate', line, f'Import ist doppelt vorhanden: {url}')
    for provider, markers in PROVIDER_MARKERS.items():
        matches = [(url, number) for url, number in imports if any(marker in url.lower() for marker in markers)]
        if len(matches) > 1:
            add(issues, 'error', 'import.provider-duplicate', matches[1][1], f'Template {provider} ist über mehrere direkte Imports eingebunden.')

    required: dict[str, tuple[str, ...]] = {
        'mathpath': ('@Explain',),
        'freeze': ('@ADetails', '@Abgabe', '@Auswertung', '@Exam'),
        'resetter': ('@resetter',),
        'algebrite': ('@Algebrite.',),
        'canvas_ocr': ('@BerechneOCR', '@canvas'),
        'coordinate': ('@CoordinateSystem', '@Koordinatensystem', '@DGS', '@Punkt', '@Point', '@PlotFunction'),
        'pentomino': ('@Pentomino',),
        'llm': ('@LLM',),
        'orthography': ('@orthography', '@diktat', '@linenumbers'),
        'kachel': ('@Kachel',),
        'marker': ('@TextmarkerQuiz', '@markred(', '@markblue(', '@markgreen(', '@markyellow(', '@markpink(', '@markorange(', '@mark('),
        'timer': ('data-solution-timer', 'data-hint-timer'),
    }
    for provider, macros in required.items():
        if any(macro in text for macro in macros) and provider_index(imports, provider) is None:
            add(issues, 'error', 'import.missing', 1, f'Direkter Import für {provider} fehlt.')
    if '@Explain' in text and provider_index(imports, 'freeze') is None:
        add(issues, 'error', 'import.explain-freeze', 1, '@Explain benötigt den direkten Freeze-Import für @ADetails.')
    if profile == 'weekly':
        for provider in ('freeze', 'mathpath'):
            if provider_index(imports, provider) is None:
                add(issues, 'error', 'import.weekly-core', 1, f'Wochenaufgabe benötigt den Standardimport {provider}.')

    canvas_used = '@BerechneOCR' in text or bool(re.search(r'^\s*@canvas\s*$', text, re.MULTILINE))
    coordinate_used = any(macro in text for macro in required['coordinate'])
    pentomino_used = any(macro in text for macro in required['pentomino'])
    dependency_rules = []
    if canvas_used:
        dependency_rules.append(('algebrite', 'lia-canvas-ocr benötigt Algebrite als direkten vorherigen Import.'))
    if coordinate_used:
        dependency_rules.append(('jsxgraph', 'lia-coordinate benötigt JSXGraph als direkten vorherigen Import.'))
    if pentomino_used:
        dependency_rules.extend((
            ('jsxgraph', 'lia-pentominos benötigt JSXGraph als direkten Import.'),
            ('coordinate', 'lia-pentominos benötigt lia-coordinate als direkten Import.'),
        ))
    for provider, message in dependency_rules:
        if provider_index(imports, provider) is None:
            add(issues, 'error', 'import.dependency', 1, message)

    order_rules = (
        ('freeze', 'mathpath'),
        ('algebrite', 'canvas_ocr'),
        ('jsxgraph', 'coordinate'),
        ('coordinate', 'pentomino'),
    )
    for before, after in order_rules:
        before_index = provider_index(imports, before)
        after_index = provider_index(imports, after)
        if before_index is not None and after_index is not None and before_index > after_index:
            add(issues, 'error', 'import.order', imports[after_index][1], f'Import {before} muss vor {after} stehen.')

    for index, line in enumerate(lines):
        number = index + 1
        if line.strip().startswith('[[?]]') and index > 0 and not lines[index - 1].strip():
            add(issues, 'error', 'spacing.quiz-hint', number, 'Zwischen Quizblock und Hinweis darf keine Leerzeile stehen.')
        if '@Explain' in line:
            if not re.search(r'^\s*\[\[\?\]\]\s+@Explain\s*$', line):
                add(issues, 'error', 'hint.explain-syntax', number, '@Explain muss als eigener Hinweis [[?]] @Explain stehen.')
        if line.strip().startswith('@resetter'):
            before_blank = index > 0 and not lines[index - 1].strip() and (index < 2 or lines[index - 2].strip())
            after_blank = index + 1 < len(lines) and not lines[index + 1].strip() and (index + 2 >= len(lines) or lines[index + 2].strip())
            if not before_blank or not after_blank:
                add(issues, 'error', 'spacing.resetter', number, '@resetter braucht davor und danach genau eine Leerzeile.')
        if line.strip().startswith('@ADetails'):
            before_blank = index > 0 and not lines[index - 1].strip() and (index < 2 or lines[index - 2].strip())
            if not before_blank:
                add(issues, 'error', 'spacing.adetails', number, 'Vor @ADetails muss genau eine Leerzeile stehen.')
        if line.strip().startswith('@Algebrite.') and index > 0 and not lines[index - 1].strip():
            add(issues, 'error', 'spacing.validator', number, 'Zwischen Antwortfeld und Algebrite-Prüfung darf keine Leerzeile stehen.')

    for match in ALGEBRITE_RE.finditer(text):
        number = line_of(text, match.start())
        macro = match.group('macro')
        args = split_macro_args(match.group('args'))
        expected = args[0] if args else ''
        complex_term = any(char in expected for char in '();')
        if complex_term and not (expected.startswith('`') and expected.endswith('`')):
            add(issues, 'error', 'algebrite.backticks', number, 'Terme mit Klammern oder Semikolon müssen im ersten Algebrite-Argument in Backticks stehen.')
        has_units = contains_quantity(expected)
        options = ','.join(args[1:]).replace(' ', '').lower()
        if has_units and macro in {'check', 'check_expression'} and 'units=1' not in options:
            add(issues, 'error', 'algebrite.units-disabled', number, f'@Algebrite.{macro} prüft Einheiten nur mit units=1.')
        if has_units and macro in {'check2', 'check_margin'} and 'units=0' in options:
            add(issues, 'error', 'algebrite.units-disabled', number, f'@Algebrite.{macro} darf bei einer Einheitenerwartung nicht units=0 setzen.')

    outside_unit = re.compile(r'\[\[[^\]\n]*\]\]\s*(' + UNIT_RE.pattern + r')')
    for match in outside_unit.finditer(text):
        add(issues, 'error', 'units.outside-answer', line_of(text, match.start()), 'Die Einheit steht außerhalb des Antwortfelds und wird deshalb nicht mitgeprüft.')

    for task_number, start_line, block in task_blocks(text):
        if has_quiz(block):
            if '@ADetails' not in block:
                add(issues, 'error', 'task.adetails', start_line, f'Aufgabe {task_number}: @ADetails fehlt.')
            if '[[?]] @Explain' not in block:
                add(issues, 'error', 'task.explain', start_line, f'Aufgabe {task_number}: der adaptive Hinweis [[?]] @Explain fehlt.')
            if '@resetter' not in block and '@BerechneOCR' not in block:
                add(issues, 'warning', 'task.resetter', start_line, f'Aufgabe {task_number}: @resetter fehlt.')
        unit_required = bool(re.search(
            r'\b(?:mit|inklusive|einschließlich)\s+(?:der\s+)?Einheit\b|\bgib[^.\n]{0,80}\bEinheit\b',
            block,
            re.IGNORECASE,
        ))
        if unit_required and has_quiz(block) and '@BerechneOCR' not in block:
            answer_fields = re.findall(r'\[\[([^\]\n]*)\]\]', block)
            if not any(contains_quantity(field) for field in answer_fields):
                add(issues, 'error', 'units.answer-missing', start_line, f'Aufgabe {task_number}: verlangte Einheit fehlt im Antwortfeld.')
            algebrite_calls = list(ALGEBRITE_RE.finditer(block))
            if algebrite_calls:
                expected_values = [split_macro_args(call.group('args'))[0] for call in algebrite_calls]
                if not any(contains_quantity(value) for value in expected_values):
                    add(issues, 'error', 'units.validator-missing', start_line, f'Aufgabe {task_number}: verlangte Einheit fehlt im Validator-Sollwert.')
            solutions = re.findall(r'^\*{8,}\s*$\n(.*?)^\*{8,}\s*$', block, re.MULTILINE | re.DOTALL)
            if solutions and not any(contains_quantity(solution) for solution in solutions):
                add(issues, 'error', 'units.solution-missing', start_line, f'Aufgabe {task_number}: verlangte Einheit fehlt in der Musterrechnung.')

    terminology = (
        (r'\bStundenkilometer\b', 'km/h statt „Stundenkilometer“ verwenden.'),
        (r'\bkmh\b', 'Die Einheit wird km/h geschrieben.'),
        (r'\b[xy]-Achse\b', 'Waagerechte und senkrechte kartesische Achse als Abszissenachse bzw. Ordinatenachse bezeichnen.'),
        (r'\bFormel\s+umstellen\b', 'Präzisieren: eine Gleichung nach einer Variablen umstellen.'),
        (r'\bEnergie(?:verbrauch|erzeugung|verlust)\b', 'Energie wird umgesetzt, übertragen oder entwertet; Leistung wird erzeugt bzw. verbraucht.'),
        (r'\bGewicht\b(?!skraft)', 'Bei der physikalischen Kraft ist „Gewichtskraft“ der präzise Begriff.'),
    )
    for number, line in visible_lines(text):
        for pattern, message in terminology:
            if re.search(pattern, line, re.IGNORECASE):
                add(issues, 'warning', 'terminology', number, message)

    if profile == 'weekly':
        if not re.search(r'^#\s+Wochenaufgabe\s+.+\s+Klasse\s+.+\s+[–-]\s+.+$', text, re.MULTILINE):
            add(issues, 'error', 'weekly.title', 1, 'H1 muss dem Muster „Wochenaufgabe … Klasse … – Fach“ folgen.')
        if not any(value.lower() == 'presentation' for value in metadata.get('mode', [])):
            add(issues, 'error', 'weekly.mode', 1, 'Wochenaufgaben verwenden mode: Presentation.')
        if not any('wochenaufgabe' in value.lower() for value in metadata.get('tags', [])):
            add(issues, 'error', 'weekly.tags', 1, 'Im Header-Tagfeld fehlt Wochenaufgabe.')
        blocks = task_blocks(text)
        numbers = [number for number, _, _ in blocks]
        if not numbers:
            add(issues, 'error', 'weekly.tasks', 1, 'Es fehlen H2-Aufgabenblöcke „## Aufgabe N“.')
        elif numbers != list(range(1, len(numbers) + 1)):
            add(issues, 'error', 'weekly.sequence', blocks[0][1], 'Aufgabennummern müssen bei 1 beginnen und lückenlos fortlaufen.')
        self_assessment = re.search(r'^##\s+Letzte Station:\s*Selbsteinschätzung\s*$', text, re.MULTILINE)
        submission = re.search(r'^#\s+Abgabe\s*$', text, re.MULTILINE)
        abgabe = re.search(r'^@Abgabe\s*$', text, re.MULTILINE)
        auswertung = re.search(r'^@Auswertung\(F12;Tab;Time\)\s*$', text, re.MULTILINE)
        if not self_assessment:
            add(issues, 'error', 'weekly.self-assessment', 1, 'Abschnitt „Letzte Station: Selbsteinschätzung“ fehlt.')
        if not submission or not abgabe or not auswertung:
            add(issues, 'error', 'weekly.footer', 1, 'Footer muss # Abgabe, @Abgabe und @Auswertung(F12;Tab;Time) enthalten.')
        elif not (submission.start() < abgabe.start() < auswertung.start()):
            add(issues, 'error', 'weekly.footer-order', line_of(text, submission.start()), 'Abgabe-Footer steht nicht in der verbindlichen Reihenfolge.')
        if self_assessment and submission and self_assessment.start() > submission.start():
            add(issues, 'error', 'weekly.footer-order', line_of(text, submission.start()), 'Die Selbsteinschätzung muss vor dem Abgabe-Footer stehen.')
        if auswertung and text[auswertung.end():].strip():
            add(issues, 'error', 'weekly.footer-tail', line_of(text, auswertung.end()), 'Nach @Auswertung darf kein weiterer Inhalt folgen.')

    if profile == 'task':
        if header_end:
            add(issues, 'error', 'task.header', 1, 'Ein Aufgabenausschnitt darf keinen eigenen LiaScript-Hauptkopf enthalten.')
        if not task_blocks(text):
            add(issues, 'error', 'task.structure', 1, 'Aufgabenausschnitt benötigt mindestens eine Überschrift „## Aufgabe N: Titel“.')

    if reference_text is not None:
        actual_shell = shell_parts(text)
        reference_shell = shell_parts(reference_text)
        if actual_shell is None or reference_shell is None:
            add(issues, 'error', 'shell.unavailable', 1, 'Kursrahmen konnte für den Referenzvergleich nicht bestimmt werden.')
        else:
            actual_prefix, actual_suffix = actual_shell
            reference_prefix, reference_suffix = reference_shell
            if actual_prefix.replace('\r\n', '\n') != reference_prefix.replace('\r\n', '\n'):
                add(issues, 'error', 'shell.header-changed', 1, 'Hauptkopf oder Einleitung weicht von der Referenz ab.')
            if actual_suffix.replace('\r\n', '\n') != reference_suffix.replace('\r\n', '\n'):
                footer_line = line_of(text, text.find(actual_suffix))
                add(issues, 'error', 'shell.footer-changed', footer_line, 'Selbsteinschätzung oder Footer weicht von der Referenz ab.')

    return sorted(issues, key=lambda issue: (issue.line, issue.severity, issue.code))


def main() -> int:
    parser = argparse.ArgumentParser(description='Prüft erzeugte SchulLia-/LiaScript-Inhalte.')
    parser.add_argument('path', type=Path, help='Zu prüfende Markdown-Datei')
    parser.add_argument('--profile', choices=('course', 'weekly', 'task'), required=True)
    parser.add_argument('--reference-shell', type=Path, help='Referenz für unveränderten Wochenaufgabenrahmen')
    parser.add_argument('--strict', action='store_true', help='Warnungen ebenfalls als Fehlschlag behandeln')
    parser.add_argument('--json', action='store_true', help='Maschinenlesbare Ausgabe')
    args = parser.parse_args()

    text = args.path.read_text(encoding='utf-8-sig')
    reference_text = None
    if args.reference_shell:
        reference_text = args.reference_shell.read_text(encoding='utf-8-sig')
    issues = validate(text, args.profile, reference_text)

    if args.json:
        print(json.dumps([asdict(issue) for issue in issues], ensure_ascii=False, indent=2))
    elif issues:
        for issue in issues:
            print(f'{args.path}:{issue.line}: {issue.severity.upper()} {issue.code}: {issue.message}')
        errors = sum(issue.severity == 'error' for issue in issues)
        warnings = sum(issue.severity == 'warning' for issue in issues)
        print(f'{errors} Fehler, {warnings} Warnungen')
    else:
        print(f'{args.path}: OK ({args.profile})')

    failed = any(issue.severity == 'error' or (args.strict and issue.severity == 'warning') for issue in issues)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
