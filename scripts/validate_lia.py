#!/usr/bin/env python3
'''Static quality gate for generated SchulLia/LiaScript authoring output.'''

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    line: int
    message: str


@dataclass(frozen=True)
class AssessmentUnit:
    task_number: int | None
    label: str | None
    line: int
    text: str
    inherited_instruction: str = ''


HEADER_RE = re.compile(r'\A<!--\s*\n(?P<body>.*?)\n-->', re.DOTALL)
META_RE = re.compile(r'^\s*(?P<key>[\w-]+)\s*:\s*(?P<value>.*?)\s*$', re.MULTILINE)
HEADING_RE = re.compile(r'^(#{1,6})[ \t]+\S')
HEADING_WITHOUT_SPACE_RE = re.compile(r'^#{1,6}(?!#)\S')
CHAINED_HEADING_RE = re.compile(r'^#{1,6}[ \t]+\S.*?[ \t]+#{1,6}[ \t]+\S')
RESOURCE_RE = re.compile(r'^\s*(?P<key>import|script|link)\s*:', re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r'\{\{[^{}]+\}\}|\b(?:TODO|TBD|PLATZHALTER)\b', re.IGNORECASE)
ALGEBRITE_RE = re.compile(r'@Algebrite\.(?P<macro>check(?:_expression|2|_margin)?|equals)\((?P<args>[^\n]*)\)')
UNIT_RE = re.compile(
    r'(?<![\w])(?:km/h|kmh|m/s\^?2|m/s²|m/s|cm\^?2|cm²|m\^?2|m²|mm|cm|km|kg|mg|g|ml|mL|l|L|h|min|s|°C|K|J|W|N|Pa|V|A|Ω|mol)(?![\w])'
)
QUANTITY_RE = re.compile(
    r'(?:\d+(?:[.,]\d+)?|\.\d+)\s*(?:km/h|kmh|m/s\^?2|m/s²|m/s|cm\^?2|cm²|m\^?2|m²|mm|cm|km|kg|mg|g|ml|mL|l|L|h|min|s|°C|K|J|W|N|Pa|V|A|Ω|mol)(?![\w])'
)
PROVIDER_MARKERS = {
    'abcjs': ('liatemplates/abcjs', '/abcjs/'),
    'board_mode': ('lia-board-mode',),
    'annotation': ('lia-annotation',),
    'avr8js': ('liatemplates/avr8js', '/avr8js/'),
    'dynflex': ('lia-dynflex',),
    'electro': ('lia-electro',),
    'freeze': ('liascript-template-freeze', 'lia-freeze-v2'),
    'globalquiz': ('lia-globalquiz',),
    'mathpath': ('lia-mathpath',),
    'navigation': ('lia-navigation',),
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
    'mathe': ('lia-mathe',),
    'speech': ('speech-recognition-quiz',),
    'timer': ('lia-timer',),
    'loot': ('lia-loot',),
}
HEADER_METADATA_KEYS = {
    'attribute', 'author', 'classroom', 'comment', 'dark', 'date', 'edit',
    'email', 'font', 'formula', 'icon', 'import', 'language', 'link', 'logo',
    'mode', 'narrator', 'persistent', 'repository', 'script', 'sharing',
    'tags', 'translatewithgoogle', 'translation', 'version',
}
ROOT = Path(__file__).resolve().parents[1]
OPERATOR_TAXONOMY = json.loads(
    (ROOT / 'references' / 'operator-taxonomy.json').read_text(encoding='utf-8')
)
OPERATOR_PATTERNS = {
    item['id']: tuple(re.compile(pattern, re.IGNORECASE) for pattern in item['prompt_patterns'])
    for item in OPERATOR_TAXONOMY['operators']
}
PART_LABEL_RE = re.compile(r'(?m)^[ \t]*\*\*(?P<label>[A-Za-z]|\d+)\)\*\*[ \t]*')
SOLUTION_BLOCK_RE = re.compile(
    r'(?ms)^\*{8,}[ \t]*\r?\n(?P<body>.*?)^\*{8,}[ \t]*$'
)
DYNAMIC_TASK_RE = re.compile(
    r'\bMath\.random\s*\(|\bcrypto\.getRandomValues\s*\(|\bLIASCRIPT\s*:',
    re.IGNORECASE,
)
SHARED_SCOPE_RE = re.compile(
    r'\b(?:jeweils|alle|folgende(?:n|r|s)?|Teilaufgaben|Aufgaben|Eingaben|Werte)\b',
    re.IGNORECASE,
)
PROCESS_OPERATORS = {'berechnen', 'ermitteln', 'bestimmen', 'loesen'}
REASONING_OPERATORS = {'begründen', 'erklaeren', 'zeigen'}
ANALYSIS_OPERATORS = {'vergleichen', 'interpretieren', 'untersuchen'}
JUDGMENT_OPERATORS = {'beurteilen', 'bewerten', 'entscheiden'}
VISUAL_OPERATORS = {'beschreiben', 'darstellen', 'skizzieren', 'zeichnen', 'konstruieren'}
OPEN_OPERATORS = {'formulieren', 'erstellen'}


def add(issues: list[Issue], severity: str, code: str, line: int, message: str) -> None:
    issues.append(Issue(severity, code, max(line, 1), message))


def line_of(text: str, offset: int) -> int:
    return text.count('\n', 0, max(offset, 0)) + 1


def normalize_line_endings(text: str, issues: list[Issue]) -> str:
    '''Normalize for parsing while retaining a diagnostic for mixed endings.'''
    endings = re.findall(r'\r\n|\r|\n', text)
    if len(set(endings)) > 1:
        first = endings[0]
        offset = 0
        for ending in endings:
            position = text.find(ending, offset)
            if ending != first:
                add(
                    issues,
                    'error',
                    'line-ending.mixed',
                    line_of(text, position),
                    'LF, CRLF und einzelne CR-Zeilenenden dürfen nicht gemischt werden.',
                )
                break
            offset = position + len(ending)
    return text.replace('\r\n', '\n').replace('\r', '\n')


def fence_diagnostics(text: str, issues: list[Issue]) -> None:
    '''Check LiaScript's documented backtick-fence form and exact closure.'''
    active: tuple[str, int, int] | None = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if not marker:
            continue
        run, tail = marker.groups()
        char = run[0]
        if active is None:
            if char == '~':
                add(
                    issues,
                    'error',
                    'fence.marker',
                    number,
                    'LiaScript-Codeblöcke verwenden Backticks; Tilden-Fences sind nicht belegt.',
                )
            active = (char, len(run), number)
            continue
        open_char, open_length, _ = active
        if tail.strip() or char != open_char:
            continue
        if len(run) < open_length:
            continue
        if len(run) != open_length:
            add(
                issues,
                'error',
                'fence.length',
                number,
                'Öffnende und schließende Code-Fence müssen dieselbe Markerzahl verwenden.',
            )
        active = None
    if active is not None:
        _, _, start_line = active
        add(
            issues,
            'error',
            'fence.unclosed',
            start_line,
            'Code-Fence ist nicht geschlossen.',
        )


def table_cells(line: str) -> list[str] | None:
    '''Return cells for a pipe table row without treating escaped pipes as cuts.'''
    if '|' not in line:
        return None
    cells = re.split(r'(?<!\\)\|', line.strip())
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return [cell.strip() for cell in cells]


def is_table_separator(cells: list[str] | None) -> bool:
    return bool(cells) and all(re.fullmatch(r':?-{3,}:?', cell) for cell in cells)


def is_response_line(line: str) -> bool:
    return bool(re.search(r'\[\[(?!\?\]\])[^\n]*\]\]', line))


def is_quiz_start(line: str) -> bool:
    stripped = line.strip()
    return bool(
        is_response_line(line)
        or re.match(r'^`{3,}text\s+@LLMQuiz(?:\.question)?\(', stripped)
        or stripped.startswith((
            '@BerechneOCR', '@Kachelfolge', '@KachelfolgeN',
            '@TextmarkerQuiz', '@orthography', '@orthographytext',
            '@diktat', '@PentominoQuiz', '@PentominoDockQuiz',
            '@KoordQuiz', '@GeometrieQuiz', '@CoordinateQuiz',
            '@GeometryQuiz', '@KonstruktionQuiz', '@ConstructionQuiz',
            '@UmfangQuiz', '@AreaQuiz',
        ))
    )


def is_quiz_tail(line: str) -> bool:
    stripped = line.strip()
    return bool(
        is_response_line(line)
        or stripped.startswith('[[?]]')
        or re.fullmatch(r'\*{8,}', stripped)
        or stripped == '</div>'
        or stripped.startswith((
            '@Algebrite.', '@BerechneOCR', '@KachelgruppenCheck',
            '@Kachelfolge', '@KachelfolgeN', '@TextmarkerQuiz',
            '@SpeechRecognition', '@orthography', '@orthographytext',
            '@diktat', '@PentominoQuiz', '@PentominoDockQuiz',
            '@KoordQuiz', '@GeometrieQuiz', '@CoordinateQuiz',
            '@GeometryQuiz', '@KonstruktionQuiz', '@ConstructionQuiz',
            '@UmfangQuiz', '@AreaQuiz', '@ResetterRekonstruktion',
            '@ResetterReconstruction',
        ))
    )


def german_key(value: str) -> str:
    translated = value.translate(str.maketrans({
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue',
    }))
    normalized = unicodedata.normalize('NFKD', translated)
    return ''.join(char for char in normalized if not unicodedata.combining(char)).casefold()


OPERATOR_ID_BY_KEY: dict[str, str] = {}
for operator_item in OPERATOR_TAXONOMY['operators']:
    operator_id = operator_item['id']
    for operator_name in (operator_id, operator_item['lemma'], *operator_item['aliases']):
        OPERATOR_ID_BY_KEY[german_key(operator_name)] = operator_id


def instruction_text(text: str) -> str:
    without_comments = re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)
    lines: list[str] = []
    for _, line in authored_lines(without_comments):
        stripped = line.strip()
        if not stripped:
            continue
        if HEADING_RE.match(line) or stripped.startswith(('@', '[[', '```')):
            continue
        if re.search(r'\[\[[^\n]*\]\]', line):
            line = line.split('[[', 1)[0]
        lines.append(line)
    visible = ' '.join(lines)
    visible = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', visible)
    visible = re.sub(r'[*_`]', '', visible)
    return re.sub(r'\s+', ' ', visible).strip()


def instruction_region(text: str) -> str:
    boundaries: list[int] = []
    quiz_match = re.search(r'\[\[[^\n]*\]\]', text)
    if quiz_match:
        boundaries.append(quiz_match.start())
    for macro in (
        '@BerechneOCR', '@LLMQuiz', '@TextmarkerQuiz', '@Kachelfolge',
        '@orthography', '@orthographytext', '@diktat', '@PentominoQuiz',
        '@KoordQuiz', '@GeometrieQuiz', '@CoordinateQuiz', '@GeometryQuiz',
        '@KonstruktionQuiz', '@ConstructionQuiz', '@UmfangQuiz', '@AreaQuiz',
    ):
        position = text.find(macro)
        if position >= 0:
            boundaries.append(position)
    return text[:min(boundaries)] if boundaries else text


def detected_operator_ids(text: str) -> set[str]:
    prompt = instruction_text(instruction_region(text))
    return {
        operator_id
        for operator_id, patterns in OPERATOR_PATTERNS.items()
        if any(pattern.search(prompt) for pattern in patterns)
    }


def declared_operator_ids(text: str) -> tuple[set[str], list[str]]:
    declared: set[str] = set()
    unknown: list[str] = []
    for value in re.findall(r'\boperator\s*=\s*([\wäöüÄÖÜß-]+)', text, re.IGNORECASE):
        operator_id = OPERATOR_ID_BY_KEY.get(german_key(value))
        if operator_id:
            declared.add(operator_id)
        else:
            unknown.append(value)
    for details in re.findall(r'^\s*@ADetails\(([^)]*)\)\s*$', text, re.MULTILINE):
        for value in re.split(r'[;,]', details):
            operator_id = OPERATOR_ID_BY_KEY.get(german_key(value.strip()))
            if operator_id:
                declared.add(operator_id)
    return declared, unknown


def assessment_units(block: str, start_line: int, task_number: int | None) -> list[AssessmentUnit]:
    labels = list(PART_LABEL_RE.finditer(block))
    if not labels:
        return [AssessmentUnit(task_number, None, start_line, block)] if has_quiz(block) else []

    units: list[AssessmentUnit] = []
    prefix = block[:labels[0].start()]
    if has_quiz(prefix):
        units.append(AssessmentUnit(task_number, None, start_line, prefix))
    shared_ids = detected_operator_ids(prefix)
    inherited = prefix if shared_ids and SHARED_SCOPE_RE.search(instruction_text(prefix)) else ''
    for index, label_match in enumerate(labels):
        end = labels[index + 1].start() if index + 1 < len(labels) else len(block)
        part = block[label_match.start():end]
        if not has_quiz(part):
            continue
        units.append(AssessmentUnit(
            task_number,
            label_match.group('label'),
            start_line + block[:label_match.start()].count('\n'),
            part,
            inherited,
        ))
    return units


def assessable_units(text: str, profile: str, header_end: int) -> list[AssessmentUnit]:
    blocks = task_blocks(text)
    if blocks:
        return [
            unit
            for task_number, start_line, block in blocks
            for unit in assessment_units(block, start_line, task_number)
        ]
    if profile != 'course':
        return []
    body = text[header_end:] if header_end else text
    exempt = re.search(
        r'(?m)^#{1,6}\s+(?:Letzte Station:\s*Selbsteinschätzung|Abgabe)\s*$',
        body,
        re.IGNORECASE,
    )
    if exempt:
        body = body[:exempt.start()]
    if not has_quiz(body):
        return []
    return assessment_units(body, line_of(text, header_end), None)


def manual_solutions(text: str) -> list[str]:
    return [match.group('body').strip() for match in SOLUTION_BLOCK_RE.finditer(text)]


def known_template_solution(text: str) -> bool:
    for match in re.finditer(r'@BerechneOCR\(\s*`([^`]*)`', text):
        task = match.group(1).strip()
        if re.fullmatch(
            r'\d+(?:[.,]\d+)?\s*(?:\+|-|\*|:|/|\\cdot|\\times)\s*\d+(?:[.,]\d+)?',
            task,
        ):
            return True
    llm = re.search(
        r'```text\s+@LLMQuiz\((?P<options>[^\n]*)\)\s*\r?\n(?P<body>.*?)^```\s*$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    if llm and re.search(r'\bsolution\s*=\s*(?:1|true)\b', llm.group('options'), re.IGNORECASE):
        body = llm.group('body')
        if '<!-- lia-llm:solution -->' in body:
            body = body.split('<!-- lia-llm:solution -->', 1)[1]
        body = re.sub(r'<!--.*?-->', ' ', body, flags=re.DOTALL).strip()
        if body:
            return True
    if re.search(
        r'@orthography(?:text)?\(\s*`[^`]*`\s*,\s*`[^`]*`\s*,\s*`[^`]+`\s*\)',
        text,
        re.DOTALL,
    ):
        return True
    return False


def response_forms(text: str) -> tuple[bool, bool]:
    fields = [
        value
        for value in re.findall(r'\[\[([^\n]*?)\]\]', text)
        if value.strip() not in {'?', '!'}
    ]
    has_choice = any('|' in value or re.search(r'\(\s*[xX ]?\s*\)', value) for value in fields)
    has_open = any('|' not in value and not re.search(r'\(\s*[xX ]?\s*\)', value) for value in fields)
    has_open = has_open or '@LLMQuiz' in text or '@BerechneOCR' in text
    return has_choice, has_open


def solution_is_insufficient(operator_ids: set[str], solution: str) -> bool:
    plain = re.sub(r'<!--.*?-->', ' ', solution, flags=re.DOTALL)
    plain = re.sub(r'\\(?:mathrm|text)\{([^{}]+)\}', r'\1', plain)
    words = re.findall(r'[A-Za-zÄÖÜäöüß]+', plain)
    equation_steps = plain.count('=') >= 1 and bool(
        re.search(r'(?:\+|-|\*|/|:|\\cdot|\\times|\\Rightarrow)', plain)
    )
    reasoning_link = bool(re.search(
        r'\b(?:weil|da|denn|daher|deshalb|dadurch|somit|folglich|während|hingegen|anhand|wenn|also)\b',
        plain,
        re.IGNORECASE,
    ))
    if operator_ids & PROCESS_OPERATORS:
        return not equation_steps and len(words) < 8
    if operator_ids & REASONING_OPERATORS:
        return not equation_steps and (len(words) < 8 or not reasoning_link)
    if operator_ids & (ANALYSIS_OPERATORS | JUDGMENT_OPERATORS):
        return len(words) < 8
    if operator_ids & (VISUAL_OPERATORS | OPEN_OPERATORS):
        return len(words) < 4
    return not plain.strip()


def unit_name(unit: AssessmentUnit) -> str:
    if unit.task_number is None:
        return 'Bewertbare Aufgabe'
    if unit.label is None:
        return f'Aufgabe {unit.task_number}'
    return f'Aufgabe {unit.task_number}, Teil {unit.label})'


def contains_quantity(value: str) -> bool:
    cleaned = re.sub(r'\\(?:mathrm|text)\{([^{}]+)\}', r'\1', value)
    cleaned = re.sub(r'\\[,;:! ]', '', cleaned)
    return bool(QUANTITY_RE.search(cleaned))


def authored_lines(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    fence: tuple[str, int] | None = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if marker:
            run, tail = marker.groups()
            if fence is None:
                fence = (run[0], len(run))
            elif not tail.strip() and run[0] == fence[0] and len(run) >= fence[1]:
                fence = None
            continue
        if fence is None:
            result.append((number, line))
    return result


def mask_fenced_bodies(text: str) -> str:
    '''Blank code-fence bodies while preserving source lines and offsets.'''
    output: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        content = line.rstrip('\r\n')
        ending = line[len(content):]
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', content)
        if fence is None:
            output.append(line)
            if marker:
                run = marker.group(1)
                fence = (run[0], len(run))
            continue
        if marker:
            run, tail = marker.groups()
            if not tail.strip() and run[0] == fence[0] and len(run) >= fence[1]:
                output.append(line)
                fence = None
                continue
        output.append((' ' * len(content)) + ending)
    return ''.join(output)


def header_like_comment_lines(text: str, after_line: int) -> list[int]:
    starts: list[int] = []
    active = False
    start_line = 0
    body: list[str] = []
    for number, line in authored_lines(text):
        if number <= after_line:
            continue
        remainder = line
        while remainder:
            if not active:
                opening = remainder.find('<!--')
                if opening < 0:
                    break
                active = True
                start_line = number
                body = []
                remainder = remainder[opening + 4:]
            closing = remainder.find('-->')
            if closing < 0:
                body.append(remainder)
                break
            body.append(remainder[:closing])
            keys = {match.group('key').casefold()
                    for match in META_RE.finditer('\n'.join(body))}
            if keys & HEADER_METADATA_KEYS:
                starts.append(start_line)
            active = False
            body = []
            remainder = remainder[closing + 3:]
    return starts


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
    return [(number, line) for number, line in authored_lines(text)
            if not RESOURCE_RE.match(line)]


def task_blocks(text: str) -> list[tuple[int, int, str]]:
    pattern = r'^##\s+Aufgabe\s+(\d+)(?:\s*:\s*\S.*)?\s*$'
    matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
    blocks: list[tuple[int, int, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((int(match.group(1)), line_of(text, match.start()), text[match.start():end]))
    return blocks


def has_quiz(block: str) -> bool:
    fields = re.findall(r'\[\[([^\n]*?)\]\]', block)
    if any(value.strip() not in {'?', '!'} for value in fields):
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


def course_shell_parts(text: str) -> tuple[str, str] | None:
    header = HEADER_RE.match(text)
    if not header:
        return None
    headings = [
        line.rstrip()
        for _, line in authored_lines(text)
        if HEADING_RE.match(line)
    ]
    if not headings:
        return None
    return text[:header.end()], '\n'.join(headings)


def validate_solution_fences(text: str, issues: list[Issue]) -> None:
    active: tuple[int, int] | None = None
    for number, line in authored_lines(text):
        match = re.fullmatch(r'\s*(\*{8,})\s*', line)
        if not match:
            continue
        length = len(match.group(1))
        if active is None:
            active = (length, number)
            continue
        open_length, _ = active
        if length != open_length:
            add(
                issues,
                'error',
                'solution.fence-mismatch',
                number,
                'Öffnender und schließender Lösungszaun müssen gleich lang sein.',
            )
        active = None
    if active is not None:
        _, start_line = active
        add(
            issues,
            'error',
            'solution.fence-unclosed',
            start_line,
            'Lösungsbereich ist nicht geschlossen.',
        )


def validate_tables_and_media(text: str, issues: list[Issue]) -> None:
    authored = authored_lines(text)
    for number, line in authored:
        if re.search(r'!\[\s*\]\([^)]*\)', line):
            add(
                issues,
                'error',
                'media.alt-missing',
                number,
                'Bilder benötigen einen nichtleeren Alternativtext.',
            )

    index = 0
    while index < len(authored):
        number, line = authored[index]
        cells = table_cells(line)
        if cells is None:
            index += 1
            continue
        group: list[tuple[int, list[str]]] = [(number, cells)]
        next_index = index + 1
        while next_index < len(authored):
            next_number, next_line = authored[next_index]
            next_cells = table_cells(next_line)
            if next_number != group[-1][0] + 1 or next_cells is None:
                break
            group.append((next_number, next_cells))
            next_index += 1
        separators = [row for row in group if is_table_separator(row[1])]
        if separators:
            expected = len(separators[0][1])
            for row_number, row_cells in group:
                if len(row_cells) != expected:
                    add(
                        issues,
                        'error',
                        'table.column-count',
                        row_number,
                        f'Tabellenzeile hat {len(row_cells)} statt {expected} Spalten.',
                    )
        index = next_index


def validate_header_structure(text: str, issues: list[Issue]) -> None:
    header = HEADER_RE.search(text)
    if not header:
        return
    stack: list[tuple[str, int]] = []
    for offset, line in enumerate(header.group('body').splitlines(), 1):
        number = line_of(text, header.start('body')) + offset - 1
        stripped = line.strip()
        if stripped == '@end':
            if not stack:
                add(issues, 'error', 'macro.block-close', number, '@end besitzt keinen offenen globalen Makroblock.')
            else:
                stack.pop()
            continue
        match = re.fullmatch(r'@([A-Za-z_][\w.-]*)', stripped)
        if match:
            stack.append((match.group(1), number))
    for name, number in stack:
        add(
            issues,
            'error',
            'macro.block-unclosed',
            number,
            f'Globaler Makroblock @{name} ist nicht mit @end geschlossen.',
        )


def validate_loot_blocks(text: str, issues: list[Issue]) -> None:
    opening = {
        'lootif': 'lootif',
        'Erdhaufen': 'earth',
        'Pflanze': 'plant',
        'Blume': 'plant',
        'NebelStart': 'fog',
    }
    closing = {
        'Endelootif': 'lootif', 'EndeLootif': 'lootif',
        'endlootif': 'lootif', 'EndLootIf': 'lootif',
        'EndeErdhaufen': 'earth',
        'EndePflanze': 'plant', 'EndeBlume': 'plant',
        'NebelEnd': 'fog',
    }
    stack: list[tuple[str, str, int]] = []
    for number, line in authored_lines(text):
        stripped = line.strip()
        if HEADING_RE.match(line) and stack:
            for name, _, start_line in stack:
                add(
                    issues,
                    'error',
                    'template.balance.loot',
                    start_line,
                    f'@{name}-Bereich überschreitet eine LiaScript-Foliengrenze.',
                )
            stack.clear()
        open_match = re.fullmatch(r'@(lootif|Erdhaufen|Pflanze|Blume)(?:\([^\n]*\))?|@NebelStart', stripped)
        if open_match and '.inline' not in stripped:
            name = open_match.group(1) or 'NebelStart'
            stack.append((name, opening[name], number))
            continue
        close_match = re.fullmatch(r'@(Endelootif|EndeLootif|endlootif|EndLootIf|EndeErdhaufen|EndePflanze|EndeBlume|NebelEnd)', stripped)
        if not close_match:
            continue
        name = close_match.group(1)
        kind = closing[name]
        if not stack or stack[-1][1] != kind:
            add(
                issues,
                'error',
                'template.balance.loot',
                number,
                f'@{name} schließt keinen passenden obersten Loot-Bereich.',
            )
        else:
            stack.pop()
    for name, _, number in stack:
        add(
            issues,
            'error',
            'template.balance.loot',
            number,
            f'@{name}-Bereich ist nicht geschlossen.',
        )


def validate_template_positions(text: str, issues: list[Issue]) -> None:
    lines = text.splitlines()
    authored_numbers = {number for number, _ in authored_lines(text)}

    def previous_nonblank(index: int) -> tuple[int, str] | None:
        cursor = index - 1
        while cursor >= 0:
            if cursor + 1 not in authored_numbers:
                cursor -= 1
                continue
            if lines[cursor].strip():
                return cursor + 1, lines[cursor]
            cursor -= 1
        return None

    for index, line in enumerate(lines):
        number = index + 1
        if number not in authored_numbers:
            continue
        stripped = line.strip()
        previous = previous_nonblank(index)

        if stripped == '@canvas':
            if previous is None or not is_response_line(previous[1]):
                add(
                    issues,
                    'error',
                    'template.position.canvas',
                    number,
                    '@canvas muss dem zugehörigen Antwortfeld unmittelbar als nächster Inhaltsblock folgen.',
                )

        if stripped.startswith('@KachelgruppenCheck'):
            direct_previous = lines[index - 1] if index else ''
            if index == 0 or not table_cells(direct_previous):
                add(
                    issues,
                    'error',
                    'template.position.kachel-check',
                    number,
                    '@KachelgruppenCheck muss ohne Leerzeile direkt nach der Tabelle stehen.',
                )

        if stripped.startswith('@resetter'):
            if previous is None or not is_quiz_tail(previous[1]):
                add(
                    issues,
                    'error',
                    'template.position.resetter',
                    number,
                    '@resetter ist keinem unmittelbar vorausgehenden unterstützten Quizblock zugeordnet.',
                )

        if stripped.startswith('@Algebrite.'):
            direct_previous = lines[index - 1] if index else ''
            if not is_response_line(direct_previous):
                add(
                    issues,
                    'error',
                    'template.position.algebrite',
                    number,
                    'Algebrite-Validator muss direkt unter dem zugehörigen Antwortfeld stehen.',
                )

        if stripped.startswith('@SpeechRecognition') and stripped != '@SpeechRecognition.support':
            direct_previous = lines[index - 1].strip() if index else ''
            if direct_previous != '[[!]]':
                add(
                    issues,
                    'error',
                    'template.position.speech',
                    number,
                    'SpeechRecognition muss direkt auf das generische Quiz [[!]] folgen.',
                )

        if stripped == '<!-- horizontal-quiz -->':
            next_line = lines[index + 1] if index + 1 < len(lines) else ''
            if not re.match(r'^\s*(?:\[\(|\[\[)', next_line):
                add(
                    issues,
                    'error',
                    'template.position.horizontal-quiz',
                    number,
                    'horizontal-quiz muss ohne Leerzeile direkt vor der Auswahl stehen.',
                )

        if stripped.startswith('<!--') and re.search(r'data-(?:solution|hint)-timer', stripped):
            next_line = lines[index + 1] if index + 1 < len(lines) else ''
            if not is_response_line(next_line):
                add(
                    issues,
                    'error',
                    'template.position.timer',
                    number,
                    'Timerattribute müssen ohne Leerzeile direkt vor dem zugehörigen Quiz stehen.',
                )

        if '@LLMQuiz' in line and not re.match(r'^\s*`{3,}text\s+@LLMQuiz(?:\.question)?\(', line):
            add(
                issues,
                'error',
                'template.position.llm',
                number,
                '@LLMQuiz muss an der öffnenden text-Code-Fence stehen.',
            )

        orthography = re.fullmatch(r'@(orthography|orthographytext)\((.*)\)', stripped)
        if orthography:
            args = split_macro_args(orthography.group(2))
            if len(args) != 3 or any(not re.fullmatch(r'`[^`]*`', arg, re.DOTALL) for arg in args):
                add(
                    issues,
                    'error',
                    'template.arguments.orthography',
                    number,
                    'Orthographie-Makros benötigen genau drei Backtick-Argumente.',
                )

        lock = re.fullmatch(r'@Schloss\(\s*([^,;]+)[,;][^)]*\)', stripped)
        if lock:
            target = german_key(lock.group(1).strip())
            if target == 'portal':
                valid = previous is not None and previous[1].strip().startswith(('@Portal(', '@Einwegportal(', '@Einbahnportal(', '@Schloss('))
            elif target in {'check', 'resolve', 'hint', 'pentominoquiz'}:
                valid = previous is not None and (is_quiz_tail(previous[1]) or previous[1].strip().startswith('@Schloss('))
            else:
                valid = True
            if not valid:
                add(
                    issues,
                    'error',
                    'template.position.loot-lock',
                    number,
                    '@Schloss ist dem zugehörigen Quiz beziehungsweise Portal nicht unmittelbar zugeordnet.',
                )


def validate(text: str, profile: str, reference_text: str | None = None) -> list[Issue]:
    issues: list[Issue] = []
    text = normalize_line_endings(text, issues)
    fence_diagnostics(text, issues)
    metadata, imports, header_end = parse_header(text)
    complete_course = profile in {'course', 'weekly'}
    header_last_line = line_of(text, header_end) if header_end else 0
    authored = authored_lines(text)
    live_text = mask_fenced_bodies(text)
    body_authored = [(number, line) for number, line in authored
                     if number > header_last_line]
    validate_solution_fences(text, issues)
    validate_tables_and_media(text, issues)
    validate_header_structure(text, issues)
    validate_loot_blocks(text, issues)
    validate_template_positions(text, issues)

    if complete_course and re.match(r'\A---[ \t]*(?:\r?\n|$)', text):
        add(issues, 'error', 'header.yaml-frontmatter', 1, 'YAML-Frontmatter ersetzt keinen LiaScript-Hauptheader.')
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

    extra_headers = header_like_comment_lines(text, header_last_line)
    if complete_course:
        for number in extra_headers:
            add(issues, 'error', 'header.multiple', number, 'Es ist nur ein LiaScript-Hauptheader am Dateianfang erlaubt.')
    elif profile == 'task':
        for number in extra_headers:
            add(issues, 'error', 'task.header', number, 'Ein Aufgabenausschnitt darf keinen eigenen LiaScript-Hauptkopf enthalten.')

    for number, line in body_authored:
        match = RESOURCE_RE.match(line)
        if not match:
            continue
        key = match.group('key').lower()
        if profile == 'task':
            add(issues, 'error', 'task.resource', number, f'Ein Aufgabenausschnitt darf keine {key}:-Ressource deklarieren.')
        elif complete_course:
            add(issues, 'error', 'header.resource-outside', number, f'{key}:-Ressourcen gehören in den LiaScript-Hauptheader.')

    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            add(issues, 'error', 'spacing.trailing', number, 'Zeile enthält nachgestellte Leerzeichen.')
        if PLACEHOLDER_RE.search(line):
            add(issues, 'error', 'placeholder', number, 'Nicht ausgefüllter Platzhalter.')
    previous_blank = 0
    for number, line in authored:
        if number <= header_last_line:
            continue
        if not line.strip():
            if previous_blank == number - 1:
                add(
                    issues,
                    'error',
                    'spacing.block-count',
                    number,
                    'Zwischen eigenständigen Blöcken ist genau eine Leerzeile zulässig.',
                )
            previous_blank = number
        else:
            previous_blank = 0
    lines = text.splitlines()
    for number, line in authored:
        if HEADING_WITHOUT_SPACE_RE.match(line):
            add(issues, 'error', 'heading.marker-spacing', number, 'Nach den Überschriftenzeichen muss ein Leerzeichen stehen.')
        if not HEADING_RE.match(line):
            continue
        masked = re.sub(r'`[^`]*`', '', line)
        if CHAINED_HEADING_RE.match(masked):
            add(issues, 'error', 'heading.chained', number, 'Eine Zeile darf nur eine Überschriftenebene eröffnen.')
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
        'abcjs': ('@ABCJS.',),
        'avr8js': ('@AVR8js.',),
        'mathpath': ('@Explain',),
        'freeze': ('@ADetails', '@Abgabe', '@Auswertung', '@Exam'),
        'globalquiz': ('@global(', '@globalforced('),
        'resetter': ('@resetter',),
        'algebrite': ('@Algebrite.',),
        'canvas_ocr': ('@BerechneOCR', '@canvas'),
        'jsxgraph': ('@JSX.',),
        'coordinate': ('@CoordinateSystem', '@Koordinatensystem', '@DGS', '@Punkt', '@Point', '@PlotFunction'),
        'electro': ('@Electro',),
        'pentomino': ('@Pentomino',),
        'llm': ('@LLM',),
        'orthography': ('@orthography', '@diktat', '@linenumbers'),
        'kachel': ('@Kachel',),
        'marker': ('@TextmarkerQuiz', '@markred(', '@markblue(', '@markgreen(', '@markyellow(', '@markpink(', '@markorange(', '@mark('),
        'mathe': ('@Strichliste', '@circleQuiz', '@rectQuiz', '@liaQuiz'),
        'speech': ('@SpeechRecognition',),
        'timer': ('data-solution-timer', 'data-hint-timer'),
        'loot': (
            '@Highscore', '@Ressourcen', '@achievements', '@lootif',
            '@Schatztruhe', '@Schluessel', '@Puzzleteil', '@Portal', '@Schloss',
            '@Taschenlampe', '@Shop', '@Atlaskarte', '@Perk', '@Axt', '@Nebel',
            '@NebelStart', '@NebelEnd', '@Kiste', '@Geschenk', '@Katze', '@Futter',
            '@Reservefolie',
        ),
    }
    if complete_course and provider_index(imports, 'board_mode') is None:
        add(issues, 'error', 'import.complete-core', 1, 'Vollständige Kurse benötigen einen direkten lia-board-mode-Import.')
    if complete_course:
        for provider, macros in required.items():
            if any(macro in live_text for macro in macros) and provider_index(imports, provider) is None:
                add(issues, 'error', 'import.missing', 1, f'Direkter Import für {provider} fehlt.')
        if '@Explain' in live_text and provider_index(imports, 'freeze') is None:
            add(issues, 'error', 'import.explain-freeze', 1, '@Explain benötigt den direkten Freeze-Import für @ADetails.')
    if profile == 'weekly':
        for provider in ('freeze', 'mathpath'):
            if provider_index(imports, provider) is None:
                add(issues, 'error', 'import.weekly-core', 1, f'Wochenaufgabe benötigt den Standardimport {provider}.')

    canvas_used = '@BerechneOCR' in live_text or bool(re.search(r'^\s*@canvas\s*$', live_text, re.MULTILINE))
    coordinate_used = any(macro in live_text for macro in required['coordinate'])
    pentomino_used = any(macro in live_text for macro in required['pentomino'])
    electro_used = any(macro in live_text for macro in required['electro'])
    if complete_course:
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
        if electro_used:
            dependency_rules.extend((
                ('jsxgraph', 'lia-electro benötigt JSXGraph als direkten Import.'),
                ('coordinate', 'lia-electro benötigt lia-coordinate als direkten Import.'),
            ))
        for provider, message in dependency_rules:
            if provider_index(imports, provider) is None:
                add(issues, 'error', 'import.dependency', 1, message)

        order_rules = (
            ('freeze', 'mathpath'),
            ('algebrite', 'canvas_ocr'),
            ('jsxgraph', 'coordinate'),
            ('coordinate', 'pentomino'),
            ('jsxgraph', 'electro'),
            ('coordinate', 'electro'),
        )
        for before, after in order_rules:
            before_index = provider_index(imports, before)
            after_index = provider_index(imports, after)
            if before_index is not None and after_index is not None and before_index > after_index:
                add(issues, 'error', 'import.order', imports[after_index][1], f'Import {before} muss vor {after} stehen.')

    for index, line in enumerate(lines):
        number = index + 1
        stripped = line.strip()
        if stripped.startswith('<!--') and 'data-' in stripped and '-->' in stripped:
            cursor = index + 1
            while cursor < len(lines) and not lines[cursor].strip():
                cursor += 1
            if cursor > index + 1 and cursor < len(lines) and is_quiz_start(lines[cursor]):
                add(
                    issues,
                    'error',
                    'spacing.quiz-comment',
                    index + 2,
                    'Zwischen Quizkommentar und zugehörigem Quiz darf keine Leerzeile stehen.',
                )
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

    for match in ALGEBRITE_RE.finditer(live_text):
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
    for match in outside_unit.finditer(live_text):
        add(issues, 'error', 'units.outside-answer', line_of(text, match.start()), 'Die Einheit steht außerhalb des Antwortfelds und wird deshalb nicht mitgeprüft.')

    units = assessable_units(text, profile, header_end)
    header_operators: set[str] = set()
    if len(units) == 1:
        for tag_value in metadata.get('tags', []):
            for tag in tag_value.split(','):
                operator_id = OPERATOR_ID_BY_KEY.get(german_key(tag.strip()))
                if operator_id:
                    header_operators.add(operator_id)
    for unit in units:
        name = unit_name(unit)
        operator_ids = detected_operator_ids(
            f'{unit.inherited_instruction}\n{unit.text}'
        )
        if not operator_ids:
            add(
                issues,
                'error',
                'operator.missing',
                unit.line,
                f'{name}: sichtbarer Arbeitsauftrag mit Imperativoperator fehlt.',
            )

        declared, unknown_declared = declared_operator_ids(unit.text)
        declared |= header_operators
        if unknown_declared:
            add(
                issues,
                'error',
                'operator.mismatch',
                unit.line,
                f'{name}: unbekannte oder nicht normalisierbare Operatorangabe {unknown_declared[0]!r}.',
            )
        elif declared and operator_ids and declared.isdisjoint(operator_ids):
            add(
                issues,
                'error',
                'operator.mismatch',
                unit.line,
                f'{name}: sichtbarer Operator und Operatorangabe widersprechen sich.',
            )

        has_choice, has_open = response_forms(unit.text)
        choice_only = has_choice and not has_open
        if choice_only and operator_ids & (
            {'berechnen', 'ermitteln', 'loesen'}
            | REASONING_OPERATORS
            | {'skizzieren', 'zeichnen', 'konstruieren'}
        ):
            add(
                issues,
                'error',
                'operator.mismatch',
                unit.line,
                f'{name}: der Operator verlangt eine eigenständige Leistung, das Quiz bietet aber nur eine Auswahl.',
            )

        solutions = manual_solutions(unit.text)
        template_solution = known_template_solution(unit.text)
        if DYNAMIC_TASK_RE.search(unit.text):
            add(
                issues,
                'warning',
                'solution.dynamic-review',
                unit.line,
                f'{name}: dynamische Laufzeitwerte und Lösung müssen manuell aus derselben Datenquelle geprüft werden.',
            )
            continue
        if template_solution and solutions:
            add(
                issues,
                'warning',
                'solution.redundant',
                unit.line,
                f'{name}: belegte Template-Lösung und manueller Lösungsblock sind möglicherweise redundant.',
            )
        if not solutions and not template_solution:
            add(
                issues,
                'error',
                'solution.missing',
                unit.line,
                f'{name}: Musterlösung oder belegte gleichwertige Template-Lösung fehlt.',
            )
        elif solutions:
            combined_solution = '\n'.join(solutions)
            if solution_is_insufficient(operator_ids, combined_solution):
                add(
                    issues,
                    'error',
                    'solution.insufficient',
                    unit.line,
                    f'{name}: die Lösung ist für den sichtbaren Operator statisch erkennbar zu knapp.',
                )

    for task_number, start_line, block in task_blocks(text):
        if has_quiz(block):
            if '@ADetails' not in block:
                add(issues, 'error', 'task.adetails', start_line, f'Aufgabe {task_number}: @ADetails fehlt.')
            if '[[?]] @Explain' not in block:
                add(issues, 'error', 'task.explain', start_line, f'Aufgabe {task_number}: der adaptive Hinweis [[?]] @Explain fehlt.')
            details = re.findall(r'^\s*@ADetails\(([^)]*)\)\s*$', block, re.MULTILINE)
            context = re.sub(
                r'^\s*@ADetails\(.*?\)\s*$',
                '',
                block,
                flags=re.MULTILINE,
            )
            if (
                any(re.search(r'(?:^|[;,])\s*Tutorial\s*(?:,|$)', item, re.IGNORECASE)
                    for item in details)
                and not re.search(
                    r'\b(?:LiaScript|Kursbedienung|Bedienhinweis|Tutorial)\b',
                    context,
                    re.IGNORECASE,
                )
            ):
                add(
                    issues,
                    'error',
                    'explain.generic-topic',
                    start_line,
                    f'Aufgabe {task_number}: „Tutorial“ ist ohne Bedienlernziel kein fachlich passendes Explain-Thema.',
                )
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
        extractor = shell_parts if profile == 'weekly' else (
            course_shell_parts if profile == 'course' else None
        )
        actual_shell = extractor(text) if extractor else None
        reference_shell = extractor(reference_text) if extractor else None
        if actual_shell is None or reference_shell is None:
            add(issues, 'error', 'shell.unavailable', 1, 'Kursrahmen konnte für den Referenzvergleich nicht bestimmt werden.')
        else:
            actual_prefix, actual_suffix = actual_shell
            reference_prefix, reference_suffix = reference_shell
            if actual_prefix.replace('\r\n', '\n') != reference_prefix.replace('\r\n', '\n'):
                add(issues, 'error', 'shell.header-changed', 1, 'Hauptkopf oder Einleitung weicht von der Referenz ab.')
            if actual_suffix.replace('\r\n', '\n') != reference_suffix.replace('\r\n', '\n'):
                if profile == 'weekly':
                    footer_line = line_of(text, text.find(actual_suffix))
                    add(issues, 'error', 'shell.footer-changed', footer_line, 'Selbsteinschätzung oder Footer weicht von der Referenz ab.')
                else:
                    add(issues, 'error', 'shell.structure-changed', 1, 'Überschriftenstruktur weicht von der Referenz ab.')

    return sorted(issues, key=lambda issue: (issue.line, issue.severity, issue.code))


def main() -> int:
    parser = argparse.ArgumentParser(description='Prüft erzeugte SchulLia-/LiaScript-Inhalte.')
    parser.add_argument('path', type=Path, help='Zu prüfende Markdown-Datei')
    parser.add_argument('--profile', choices=('course', 'weekly', 'task'), required=True)
    parser.add_argument('--reference-shell', type=Path, help='Referenz für einen zu bewahrenden Kursrahmen')
    parser.add_argument('--strict', action='store_true', help='Warnungen ebenfalls als Fehlschlag behandeln')
    parser.add_argument('--json', action='store_true', help='Maschinenlesbare Ausgabe')
    args = parser.parse_args()

    text = args.path.read_bytes().decode('utf-8-sig')
    reference_text = None
    if args.reference_shell:
        reference_text = args.reference_shell.read_bytes().decode('utf-8-sig')
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
