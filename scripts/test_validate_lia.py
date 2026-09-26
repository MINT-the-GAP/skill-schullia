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


class ValidateLiaTests(unittest.TestCase):
    def codes(self, text: str, reference: str | None = None) -> set[str]:
        return {issue.code for issue in validate(text, 'weekly', reference)}

    def test_valid_weekly_course(self) -> None:
        self.assertEqual(validate(VALID_WEEKLY, 'weekly'), [])

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

    def test_task_profile_rejects_unstructured_fragment(self) -> None:
        issues = validate('Berechne.\n\n[[ 2 ]]\n', 'task')
        self.assertIn('task.structure', {issue.code for issue in issues})

    def test_task_profile_rejects_second_main_header(self) -> None:
        fragment = VALID_WEEKLY.split('## Letzte Station:', 1)[0]
        issues = validate(fragment, 'task')
        self.assertIn('task.header', {issue.code for issue in issues})

    def test_double_blank_before_adetails_is_rejected(self) -> None:
        text = VALID_WEEKLY.replace('\n\n@ADetails', '\n\n\n@ADetails')
        self.assertIn('spacing.adetails', self.codes(text))


if __name__ == '__main__':
    unittest.main()
