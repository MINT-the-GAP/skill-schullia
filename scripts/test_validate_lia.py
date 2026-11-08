#!/usr/bin/env python3
'''Regression tests for the SchulLia authoring validator.'''

from __future__ import annotations

import unittest

from validate_lia import validate


VALID_WEEKLY = r'''<!--
author: Testperson
version: 1.0.0
language: de
narrator: Deutsch Female
mode: Presentation

import: https://raw.githubusercontent.com/MINT-the-GAP/lia-board-mode/main/README.md
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-freeze-v2/main/README.md
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-mathpath/refs/heads/master/README.md
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-resetter/main/README.md
import: https://raw.githubusercontent.com/liaTemplates/algebrite/master/README.md

tags: Wochenaufgabe, Mathematik, Klasse 7
comment: Verbindliche Test-Wochenaufgabe.
-->

# Wochenaufgabe 4 Klasse 7 – Mathematik

Bearbeite alle Aufgaben sorgfältig.

## Aufgabe 1: Länge

Berechne die Länge mit Einheit.

<!-- data-hint-button=1 data-solution-button=3 -->
$s=$ [[ 2cm ]]
@Algebrite.check(`2cm`, units=1)
[[?]] Rechne zuerst die Teilstrecken zusammen.
[[?]] @Explain
****************
$s=1\,\mathrm{cm}+1\,\mathrm{cm}=2\,\mathrm{cm}$.
****************

@resetter

@ADetails(2=BE; Größen, Einheiten)

## Letzte Station: Selbsteinschätzung

Wie sicher fühlst du dich?

[[ sicher | teilweise sicher | unsicher ]]

# Abgabe

Kontrolliere deine Antworten.

@Abgabe

@Auswertung(F12;Tab;Time)
'''

VALID_COURSE = VALID_WEEKLY.replace(
    next(line for line in VALID_WEEKLY.splitlines()
         if line.startswith('# Wochenaufgabe ')),
    '# Übung zu Längen',
)

VALID_TASK = r'''## Aufgabe 1: Länge

Berechne die Länge.

[[ 2 ]]
[[?]] Rechne zuerst die Teilstrecken zusammen.
[[?]] @Explain
****************
$s=1+1=2$.
****************

@resetter

@ADetails(2=BE; Größen)
'''


VALID_SIMPLE_COURSE = r'''<!--
author: Testperson
version: 1.0.0
language: de
comment: Kurzer vorhandener Kurs.

import: https://raw.githubusercontent.com/MINT-the-GAP/lia-board-mode/main/README.md

tags: Mathematik, Brueche
-->

# Brueche vergleichen

Wähle den größeren Bruch aus.

[[(1/2)|1/3]]
****************
Der größere Bruch ist $\frac{1}{2}$, weil bei gleichem Zähler der kleinere Nenner den größeren Bruch bezeichnet.
****************
'''


class ValidateLiaTests(unittest.TestCase):
    def codes(self, text: str, reference: str | None = None) -> set[str]:
        return {issue.code for issue in validate(text, 'weekly', reference)}

    def profile_codes(self, text: str, profile: str) -> set[str]:
        return {issue.code for issue in validate(text, profile)}

    def issue_for(self, text: str, profile: str, code: str):
        matches = [issue for issue in validate(text, profile) if issue.code == code]
        self.assertEqual(len(matches), 1, (code, validate(text, profile)))
        return matches[0]

    def test_two_blank_lines_between_blocks_are_rejected(self) -> None:
        text = '''## Aufgabe 1: Abstand

Berechne den Abstand.


[[ 2 ]]
[[?]] Addiere die Teilstrecken.
********
$1+1=2$.
********

@resetter

@ADetails(1=BE; Abstand)
'''
        issue = self.issue_for(text, 'task', 'spacing.block-count')
        self.assertEqual(issue.line, 5)
        valid = text.replace('\n\n\n[[ 2 ]]', '\n\n[[ 2 ]]')
        self.assertNotIn('spacing.block-count', self.profile_codes(valid, 'task'))

    def test_blank_between_quiz_comment_and_quiz_is_rejected(self) -> None:
        text = '''## Aufgabe 1: Auswahl

Wähle die richtige Antwort aus.

<!-- data-solution-button=2 -->

[[(X) richtig | ( ) falsch]]
********
Richtig ist „richtig“.
********
'''
        issue = self.issue_for(text, 'task', 'spacing.quiz-comment')
        self.assertEqual(issue.line, 6)
        valid = text.replace('-->\n\n[[', '-->\n[[')
        self.assertNotIn('spacing.quiz-comment', self.profile_codes(valid, 'task'))

    def test_unclosed_code_fence_is_rejected(self) -> None:
        text = '## Aufgabe 1: Code\n\n```javascript\nconst value = 1\n'
        issue = self.issue_for(text, 'task', 'fence.unclosed')
        self.assertEqual(issue.line, 3)
        valid = text + '```\n'
        self.assertNotIn('fence.unclosed', self.profile_codes(valid, 'task'))

    def test_tilde_fence_is_rejected(self) -> None:
        text = '## Aufgabe 1: Code\n\n~~~javascript\nconst value = 1\n~~~\n'
        issue = self.issue_for(text, 'task', 'fence.marker')
        self.assertEqual(issue.line, 3)
        valid = text.replace('~~~', '```')
        self.assertNotIn('fence.marker', self.profile_codes(valid, 'task'))

    def test_empty_image_alt_is_rejected(self) -> None:
        text = '## Aufgabe 1: Bild\n\n![](bild.png)\n'
        issue = self.issue_for(text, 'task', 'media.alt-missing')
        self.assertEqual(issue.line, 3)
        valid = text.replace('![]', '![Skizze eines Rechtecks]')
        self.assertNotIn('media.alt-missing', self.profile_codes(valid, 'task'))

    def test_unequal_solution_fences_are_rejected(self) -> None:
        text = '''## Aufgabe 1: Summe

Berechne die Summe.

[[ 2 ]]
********
$1+1=2$.
*********
'''
        issue = self.issue_for(text, 'task', 'solution.fence-mismatch')
        self.assertEqual(issue.line, 8)
        valid = text.replace('*********\n', '********\n')
        self.assertNotIn('solution.fence-mismatch', self.profile_codes(valid, 'task'))

    def test_canvas_must_belong_to_preceding_answer(self) -> None:
        text = '''## Aufgabe 1: Eingabe

Berechne die Summe.

[[ 2 ]]

Ein fremder Absatz.

@canvas
'''
        issue = self.issue_for(text, 'task', 'template.position.canvas')
        self.assertEqual(issue.line, 9)
        valid = text.replace('\n\nEin fremder Absatz.\n', '')
        self.assertNotIn('template.position.canvas', self.profile_codes(valid, 'task'))

    def test_kachel_check_must_follow_table_without_blank(self) -> None:
        text = '''## Aufgabe 1: Gruppen

Ordne die Begriffe zu.

| A | B |
|---|---|
| eins | zwei |

@KachelgruppenCheck(test)
'''
        issue = self.issue_for(text, 'task', 'template.position.kachel-check')
        self.assertEqual(issue.line, 9)
        valid = text.replace('| eins | zwei |\n\n@', '| eins | zwei |\n@')
        self.assertNotIn('template.position.kachel-check', self.profile_codes(valid, 'task'))

    def test_resetter_after_unrelated_paragraph_is_rejected(self) -> None:
        text = '''## Aufgabe 1: Summe

Berechne die Summe.

[[ 2 ]]

Ein fremder Absatz.

@resetter

@ADetails(1=BE; Addition)
'''
        issue = self.issue_for(text, 'task', 'template.position.resetter')
        self.assertEqual(issue.line, 9)
        valid = text.replace('\n\nEin fremder Absatz.\n', '')
        self.assertNotIn('template.position.resetter', self.profile_codes(valid, 'task'))

    def test_inconsistent_table_column_count_is_rejected(self) -> None:
        text = '''## Aufgabe 1: Tabelle

Nenne den passenden Wert.

| A | B |
|---|---|
| eins | zwei | drei |
'''
        issue = self.issue_for(text, 'task', 'table.column-count')
        self.assertEqual(issue.line, 7)
        valid = text.replace('| eins | zwei | drei |', '| eins | zwei |')
        self.assertNotIn('table.column-count', self.profile_codes(valid, 'task'))

    def test_valid_weekly_course(self) -> None:
        self.assertEqual(validate(VALID_WEEKLY, 'weekly'), [])

    def test_valid_single_task_course(self) -> None:
        self.assertEqual(validate(VALID_COURSE, 'course'), [])

    def test_valid_headerless_task_fragment(self) -> None:
        self.assertEqual(validate(VALID_TASK, 'task'), [])

    def test_missing_explain_is_rejected(self) -> None:
        text = VALID_WEEKLY.replace('[[?]] @Explain\n', '')
        self.assertIn('task.explain', self.codes(text))

    def test_complex_algebrite_term_needs_backticks(self) -> None:
        text = VALID_WEEKLY.replace('@Algebrite.check(`2cm`, units=1)', '@Algebrite.check(-(K/2))')
        self.assertIn('algebrite.backticks', self.codes(text))

    def test_unit_outside_answer_field_is_rejected(self) -> None:
        text = VALID_WEEKLY.replace('$s=$ [[ 2cm ]]', '$s=$ [[ 2 ]] cm')
        self.assertIn('units.outside-answer', self.codes(text))

    def test_units_must_be_enabled_for_check(self) -> None:
        text = VALID_WEEKLY.replace('@Algebrite.check(`2cm`, units=1)', '@Algebrite.check(`2cm`)')
        self.assertIn('algebrite.units-disabled', self.codes(text))

    def test_required_unit_must_be_in_validator(self) -> None:
        text = VALID_WEEKLY.replace('@Algebrite.check(`2cm`, units=1)', '@Algebrite.check(`2`, units=1)')
        self.assertIn('units.validator-missing', self.codes(text))

    def test_required_unit_must_be_in_solution(self) -> None:
        text = VALID_WEEKLY.replace(r'\mathrm{cm}', '')
        self.assertIn('units.solution-missing', self.codes(text))

    def test_reference_shell_detects_intro_change(self) -> None:
        text = VALID_WEEKLY.replace('Bearbeite alle Aufgaben sorgfältig.', 'Andere Einleitung.')
        self.assertIn('shell.header-changed', self.codes(text, VALID_WEEKLY))

    def test_course_reference_shell_allows_body_change(self) -> None:
        text = VALID_SIMPLE_COURSE.replace(
            'Wähle den größeren Bruch aus.',
            'Prüfe beide Brüche und wähle den größeren aus.',
        )
        self.assertEqual(validate(text, 'course', VALID_SIMPLE_COURSE), [])

    def test_course_reference_shell_detects_header_change(self) -> None:
        text = VALID_SIMPLE_COURSE.replace(
            'comment: Kurzer vorhandener Kurs.',
            'comment: Geaenderter Kurs.',
        )
        codes = {
            issue.code for issue in validate(
                text,
                'course',
                VALID_SIMPLE_COURSE,
            )
        }
        self.assertIn('shell.header-changed', codes)

    def test_course_reference_shell_detects_heading_change(self) -> None:
        text = VALID_SIMPLE_COURSE.replace(
            '# Brueche vergleichen',
            '# Andere Ueberschrift',
        )
        codes = {
            issue.code for issue in validate(
                text,
                'course',
                VALID_SIMPLE_COURSE,
            )
        }
        self.assertIn('shell.structure-changed', codes)

    def test_generic_tutorial_is_not_a_subject_explain_topic(self) -> None:
        details = next(
            line for line in VALID_WEEKLY.splitlines()
            if line.startswith('@ADetails(2=BE; ')
        )
        text = VALID_WEEKLY.replace(
            details,
            '@ADetails(2=BE; Energieumwandlung, Tutorial)',
        )
        self.assertIn('explain.generic-topic', self.codes(text))

    def test_task_profile_rejects_unstructured_fragment(self) -> None:
        issues = validate('Berechne.\n\n[[ 2 ]]\n', 'task')
        self.assertIn('task.structure', {issue.code for issue in issues})

    def test_task_profile_rejects_second_main_header(self) -> None:
        fragment = VALID_WEEKLY.split('## Letzte Station:', 1)[0]
        issues = validate(fragment, 'task')
        self.assertIn('task.header', {issue.code for issue in issues})

    def test_complete_profiles_require_board_mode(self) -> None:
        board = 'import: https://raw.githubusercontent.com/MINT-the-GAP/lia-board-mode/main/README.md\n'
        for profile, source in (('course', VALID_COURSE), ('weekly', VALID_WEEKLY)):
            with self.subTest(profile=profile):
                self.assertIn(
                    'import.complete-core',
                    self.profile_codes(source.replace(board, ''), profile),
                )

    def test_exact_duplicate_import_is_rejected(self) -> None:
        board = 'import: https://raw.githubusercontent.com/MINT-the-GAP/lia-board-mode/main/README.md\n'
        text = VALID_COURSE.replace(board, board + board)
        self.assertIn('import.duplicate', self.profile_codes(text, 'course'))

    def test_provider_duplicate_board_import_is_rejected(self) -> None:
        board = 'import: https://raw.githubusercontent.com/MINT-the-GAP/lia-board-mode/main/README.md\n'
        commit = 'import: https://raw.githubusercontent.com/MINT-the-GAP/lia-board-mode/012f1565c41a0411f63f35b9ddf8db1ecab44847/README.md\n'
        text = VALID_COURSE.replace(board, board + commit)
        self.assertIn('import.provider-duplicate', self.profile_codes(text, 'course'))

    def test_provider_duplicate_freeze_and_mathpath_variants_are_rejected(self) -> None:
        cases = (
            (
                'lia-freeze-v2/main/README.md\n',
                'lia-freeze-v2/main/README.md\n'
                'import: https://raw.githubusercontent.com/liascript-templates/liascript-template-freeze/main/README.md\n',
            ),
            (
                'lia-mathpath/refs/heads/master/README.md\n',
                'lia-mathpath/refs/heads/master/README.md\n'
                'import: https://raw.githubusercontent.com/MINT-the-GAP/lia-mathpath/main/README.md\n',
            ),
        )
        for old, new in cases:
            with self.subTest(provider=old):
                text = VALID_COURSE.replace(old, new)
                self.assertIn('import.provider-duplicate', self.profile_codes(text, 'course'))

    def test_task_rejects_resource_declarations(self) -> None:
        for key in ('import', 'script', 'link'):
            with self.subTest(key=key):
                text = VALID_TASK + f'\n{key}: https://example.invalid/resource\n'
                self.assertIn('task.resource', self.profile_codes(text, 'task'))

    def test_complete_course_rejects_resource_outside_header(self) -> None:
        text = VALID_COURSE + '\nscript: https://example.invalid/resource.js\n'
        self.assertIn('header.resource-outside', self.profile_codes(text, 'course'))

    def test_second_header_like_comment_is_rejected(self) -> None:
        text = VALID_COURSE + '\n<!--\nauthor: Zweite Person\nversion: 2.0.0\n-->\n'
        self.assertIn('header.multiple', self.profile_codes(text, 'course'))

    def test_local_liascript_comments_are_allowed(self) -> None:
        comments = (
            '<!-- normaler lokaler Kommentar -->\n'
            '<!-- data-hint-button=1 data-solution-button=3 -->\n'
            '<!-- style: compact -->\n'
            '<!-- params: local -->\n'
            '<!-- lia-llm: context -->'
        )
        text = VALID_COURSE.replace(
            '<!-- data-hint-button=1 data-solution-button=3 -->',
            comments,
        )
        self.assertNotIn('header.multiple', self.profile_codes(text, 'course'))

    def test_yaml_frontmatter_is_not_a_main_header(self) -> None:
        text = '---\nauthor: Testperson\nversion: 1.0.0\n---\n\n# Kurs\n'
        codes = self.profile_codes(text, 'course')
        self.assertIn('header.yaml-frontmatter', codes)
        self.assertIn('header.missing', codes)

    def test_chained_heading_markers_are_rejected(self) -> None:
        text = VALID_COURSE.replace('# Übung zu Längen', '# Aufgabe 1 ## Teil a)')
        self.assertIn('heading.chained', self.profile_codes(text, 'course'))

    def test_heading_marker_requires_space(self) -> None:
        text = VALID_COURSE.replace('## Aufgabe 1: Länge', '##Aufgabe 1: Länge')
        self.assertIn('heading.marker-spacing', self.profile_codes(text, 'course'))

    def test_h3_heading_is_allowed(self) -> None:
        text = VALID_COURSE + '\n### Vertiefung\n\nEin kleiner Abschnitt.\n'
        self.assertEqual(validate(text, 'course'), [])

    def test_heading_examples_in_code_fences_are_ignored(self) -> None:
        example = (
            '\n```markdown\n'
            '#Aufgabe ohne Leerzeichen\n'
            '# Aufgabe 1 ## Teil a)\n'
            'import: https://example.invalid/example\n'
            '```\n'
        )
        codes = self.profile_codes(VALID_COURSE + example, 'course')
        self.assertNotIn('heading.marker-spacing', codes)
        self.assertNotIn('heading.chained', codes)
        self.assertNotIn('header.resource-outside', codes)

    def test_template_examples_in_code_fences_are_ignored(self) -> None:
        example = (
            '\n````markdown\n'
            '[[ 2 ]]\n\n@canvas\n'
            '@Algebrite.check(`2`)\n'
            '@KachelgruppenCheck(example)\n'
            '![](example.png)\n'
            '| A | B |\n|---|---|\n| eins | zwei | drei |\n'
            '````\n'
        )
        codes = self.profile_codes(VALID_SIMPLE_COURSE + example, 'course')
        self.assertNotIn('import.missing', codes)
        self.assertNotIn('import.dependency', codes)
        self.assertNotIn('template.position.canvas', codes)
        self.assertNotIn('template.position.kachel-check', codes)
        self.assertNotIn('media.alt-missing', codes)
        self.assertNotIn('table.column-count', codes)

    def test_lia_mathe_macro_requires_direct_import(self) -> None:
        text = VALID_SIMPLE_COURSE + '\n@Strichliste(7)\n'
        self.assertIn('import.missing', self.profile_codes(text, 'course'))

    def test_new_lia_loot_macro_requires_direct_import(self) -> None:
        text = VALID_SIMPLE_COURSE + '\n@Reservefolie(2)\n'
        self.assertIn('import.missing', self.profile_codes(text, 'course'))

    def test_lia_electro_requires_direct_dependencies(self) -> None:
        electro_import = (
            'import: https://raw.githubusercontent.com/MINT-the-GAP/'
            'lia-electro/main/README.md\n'
        )
        text = VALID_SIMPLE_COURSE.replace(
            'tags: Mathematik, Brueche',
            electro_import + '\ntags: Mathematik, Brueche',
        ) + '\n@ElectroOn(example)\n'
        issues = [
            issue for issue in validate(text, 'course')
            if issue.code == 'import.dependency'
        ]
        self.assertEqual(len(issues), 2)
        self.assertTrue(any('JSXGraph' in issue.message for issue in issues))
        self.assertTrue(any('lia-coordinate' in issue.message for issue in issues))

    def test_missing_required_header_field_is_rejected(self) -> None:
        text = VALID_COURSE.replace('comment: Verbindliche Test-Wochenaufgabe.\n', '')
        self.assertIn('header.field', self.profile_codes(text, 'course'))

    def test_wrong_blank_count_after_header_is_rejected(self) -> None:
        text = VALID_COURSE.replace('-->\n\n# Übung', '-->\n# Übung')
        self.assertIn('spacing.header-title', self.profile_codes(text, 'course'))

    def test_double_blank_before_adetails_is_rejected(self) -> None:
        text = VALID_WEEKLY.replace('\n\n@ADetails', '\n\n\n@ADetails')
        self.assertIn('spacing.adetails', self.codes(text))

    def test_assessable_task_without_operator_is_rejected(self) -> None:
        text = VALID_TASK.replace(
            'Berechne die Länge.',
            'Die Länge ist gesucht.',
        )
        self.assertIn('operator.missing', self.profile_codes(text, 'task'))

    def test_simple_imperative_operator_is_accepted(self) -> None:
        self.assertNotIn('operator.missing', self.profile_codes(VALID_TASK, 'task'))

    def test_separable_operator_is_detected_across_instruction(self) -> None:
        text = VALID_TASK.replace(
            'Berechne die Länge.',
            'Gib die gesuchte Länge in Zentimetern an.',
        )
        self.assertNotIn('operator.missing', self.profile_codes(text, 'task'))

    def test_short_parts_with_individual_operators_are_accepted(self) -> None:
        text = r'''## Aufgabe 1: Drei Teilaufgaben

**a)** Nenne die Anzahl der Ecken eines Quadrats.

[[ 4 ]]
[[?]] Zähle die Eckpunkte.
****************
Ein Quadrat hat vier Ecken.
****************

**b)** Berechne $3+5$.

[[ 8 ]]
[[?]] Addiere beide Summanden.
****************
$3+5=8$.
****************

**c)** Begründe, warum $8$ eine gerade Zahl ist.

[[___]]
[[?]] Verwende die Teilbarkeit durch zwei.
[[?]] @Explain
****************
Weil $8=2\cdot4$ gilt, ist 8 ohne Rest durch zwei teilbar und daher gerade.
****************

@resetter

@ADetails(3=BE; Grundrechenarten)
'''
        codes = self.profile_codes(text, 'task')
        self.assertNotIn('operator.missing', codes)
        self.assertNotIn('solution.insufficient', codes)

    def test_shared_scoped_operator_can_cover_multiple_inputs(self) -> None:
        text = r'''## Aufgabe 1: Summen

Berechne jeweils die Summe.

$2+3=$ [[ 5 ]]

$4+5=$ [[ 9 ]]

$6+7=$ [[ 13 ]]
[[?]] Addiere jeweils beide Summanden.
[[?]] @Explain
****************
$2+3=5$, $4+5=9$ und $6+7=13$.
****************

@resetter

@ADetails(3=BE; Grundrechenarten)
'''
        self.assertNotIn('operator.missing', self.profile_codes(text, 'task'))

    def test_heading_or_bold_noun_is_not_an_operator(self) -> None:
        text = VALID_TASK.replace(
            'Berechne die Länge.',
            '**Berechnung:** Die Länge ist gesucht.',
        )
        self.assertIn('operator.missing', self.profile_codes(text, 'task'))

    def test_calculation_with_working_and_unit_is_accepted(self) -> None:
        text = VALID_TASK.replace(
            'Berechne die Länge.',
            'Berechne die Länge mit Einheit.',
        ).replace(
            '[[ 2 ]]',
            '[[ 2cm ]]',
        ).replace(
            '$s=1+1=2$.',
            r'$s=1\,\mathrm{cm}+1\,\mathrm{cm}=2\,\mathrm{cm}$. Die Länge beträgt $2\,\mathrm{cm}$.',
        )
        codes = self.profile_codes(text, 'task')
        self.assertNotIn('solution.insufficient', codes)
        self.assertNotIn('units.solution-missing', codes)

    def test_calculation_with_end_value_only_is_rejected(self) -> None:
        text = VALID_TASK.replace('$s=1+1=2$.', '$2$.')
        self.assertIn('solution.insufficient', self.profile_codes(text, 'task'))

    def test_reasoning_without_model_reason_is_rejected(self) -> None:
        text = VALID_TASK.replace(
            'Berechne die Länge.',
            'Begründe, warum die Länge 2 beträgt.',
        ).replace('$s=1+1=2$.', 'Die Aussage ist richtig.')
        self.assertIn('solution.insufficient', self.profile_codes(text, 'task'))

    def test_complete_model_reason_is_accepted(self) -> None:
        text = VALID_TASK.replace(
            'Berechne die Länge.',
            'Begründe, warum die Länge 2 beträgt.',
        ).replace(
            '$s=1+1=2$.',
            'Weil beide Teilstrecken jeweils eine Längeneinheit messen, beträgt ihre Summe zwei Längeneinheiten.',
        )
        self.assertNotIn('solution.insufficient', self.profile_codes(text, 'task'))

    def test_selection_with_answer_and_feedback_is_accepted(self) -> None:
        text = VALID_TASK.replace(
            'Berechne die Länge.',
            'Wähle die größere Zahl aus.',
        ).replace(
            '[[ 2 ]]',
            '[[(X) 12 | ( ) 10]]',
        ).replace(
            '$s=1+1=2$.',
            '12 ist richtig, weil 12 größer als 10 ist.',
        )
        codes = self.profile_codes(text, 'task')
        self.assertNotIn('operator.mismatch', codes)
        self.assertNotIn('solution.missing', codes)

    def test_known_template_solution_does_not_need_duplicate_block(self) -> None:
        text = r'''## Aufgabe 1: Rechenweg

Berechne $12+8$ mit vollständigem Rechenweg.

@BerechneOCR(`12+8`,`zeilenrueckmeldung=1`)
[[?]] Zerlege 12 in 10 und 2.
[[?]] @Explain

@ADetails(2=BE; Grundrechenarten)
'''
        codes = self.profile_codes(text, 'task')
        self.assertNotIn('solution.missing', codes)
        self.assertNotIn('solution.redundant', codes)

    def test_dynamic_task_does_not_demand_invented_static_solution(self) -> None:
        text = r'''## Aufgabe 1: Zufallszahl

Berechne die Summe der beiden angezeigten Zufallszahlen.

```javascript
const a = Math.floor(Math.random() * 10)
```

[[ 0 ]]
[[?]] Addiere die beiden angezeigten Zahlen.
[[?]] @Explain

@resetter

@ADetails(1=BE; Grundrechenarten)
'''
        codes = self.profile_codes(text, 'task')
        self.assertIn('solution.dynamic-review', codes)
        self.assertNotIn('solution.missing', codes)
        self.assertNotIn('solution.insufficient', codes)

    def test_self_assessment_and_submission_do_not_need_operators(self) -> None:
        codes = self.codes(VALID_WEEKLY)
        self.assertNotIn('operator.missing', codes)

    def test_reasoning_operator_with_choice_only_quiz_is_rejected(self) -> None:
        text = VALID_TASK.replace(
            'Berechne die Länge.',
            'Begründe, warum die Aussage stimmt.',
        ).replace(
            '[[ 2 ]]',
            '[[(X) richtig | ( ) falsch]]',
        ).replace(
            '$s=1+1=2$.',
            'Weil zwei Teilstrecken der Länge 1 zusammen die Länge 2 ergeben, stimmt die Aussage.',
        )
        self.assertIn('operator.mismatch', self.profile_codes(text, 'task'))

    def test_missing_solution_is_rejected(self) -> None:
        text = VALID_TASK.replace(
            '****************\n$s=1+1=2$.\n****************\n',
            '',
        )
        self.assertIn('solution.missing', self.profile_codes(text, 'task'))

    def test_visible_operator_must_match_explicit_operator_setting(self) -> None:
        text = VALID_TASK.replace(
            '[[ 2 ]]',
            '[[ 2 ]]\n```text @LLMQuiz(0.66;solution=1;operator=erklaeren,`Berechne die Länge.`)\nDie Länge beträgt zwei Einheiten.\n```',
        )
        self.assertIn('operator.mismatch', self.profile_codes(text, 'task'))


if __name__ == '__main__':
    unittest.main()
