#!/usr/bin/env python3
"""Synthetic near-copy regressions; no real config, index, or source is read."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import local_orientation_config as config
import local_orientation_near_copy as near


SENTINEL = "SYNTHETIC_PRIVATE_NEAR_COPY_SENTINEL"
PRIVATE_BODY = r"""
\begin{aufgabe}
Ein Fahrradkurier plant eine Fahrt vom Marktplatz zum Schwimmbad.
Die Strecke ist 18 km lang und die Fahrzeit betraegt 45 min.
\begin{enumerate}
\item Berechne die durchschnittliche Geschwindigkeit in km/h.
\item Bestimme die Strecke nach 30 min bei gleicher Geschwindigkeit.
\item Begruende, ob 24 km in 60 min zum gleichen Zusammenhang passen.
\end{enumerate}
\begin{loesung}
Es gilt $v = \frac{18\,\mathrm{km}}{0{,}75\,\mathrm{h}} = 24\,\mathrm{km/h}$.
Nach 30 min werden 12 km zurueckgelegt. Das Zahlenpaar 60 min und 24 km
passt, weil der Quotient aus Strecke und Zeit unveraendert bleibt.
\end{loesung}
\end{aufgabe}
"""


def config_value(source: Path, *, enabled=True):
    return {
        "schema_version": 1,
        "enabled": enabled,
        "usage_context": "orientation-only",
        "state_directory": ".schullia-local/state",
        "sources": [{
            "id": "synthetic-source",
            "root": str(source),
            "include": ["allowed"],
            "exclude": [],
            "allowed_extensions": [".tex"],
            "subjects": ["mathematics"],
            "grades": [7],
            "learner_groups": ["synthetic-group"],
            "document_types": ["worksheet"],
            "archive_policy": "exclude",
            "risk_policy": {key: False for key in config.RISK_KEYS},
        }],
    }


def write_config(path: Path, value) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def layout(base: Path, body=PRIVATE_BODY):
    repo = base / "repo"
    source = base / "private-source"
    repo.mkdir()
    (source / "allowed").mkdir(parents=True)
    (source / "allowed" / "task.tex").write_text(body, encoding="utf-8")
    path = base / "config.json"
    write_config(path, config_value(source))
    return repo, source, path


def course(body: str, title="Kurierfahrt") -> str:
    return (
        "<!--\n"
        "author: Forward-Test\n"
        "language: de\n"
        "narrator: Deutsch Female\n"
        "-->\n\n"
        f"# {title}\n\n"
        "## Aufgabe\n\n"
        + body.strip()
        + "\n"
    )


def copied_course() -> str:
    return course(r"""
Ein Fahrradkurier plant eine Fahrt vom Marktplatz zum Schwimmbad.
Die Strecke ist 18 km lang und die Fahrzeit betraegt 45 min.

1. Berechne die durchschnittliche Geschwindigkeit in km/h.
2. Bestimme die Strecke nach 30 min bei gleicher Geschwindigkeit.
3. Begruende, ob 24 km in 60 min zum gleichen Zusammenhang passen.

### Musterloesung

Es gilt $v = \frac{18\,\mathrm{km}}{0{,}75\,\mathrm{h}} = 24\,\mathrm{km/h}$.
Nach 30 min werden 12 km zurueckgelegt. Das Zahlenpaar 60 min und 24 km
passt, weil der Quotient aus Strecke und Zeit unveraendert bleibt.
""")


def independent_course() -> str:
    return course(r"""
Eine Gaertnerei mischt aus drei Sorten Saatgut eine neue Mischung.
In vier Beeten werden 7, 11, 13 und 17 Pflanzen gezaehlt.

1. Berechne die Gesamtzahl der Pflanzen.
2. Bestimme den Anteil des zweiten Beetes an der Gesamtzahl.
3. Begruende, welche Darstellung fuer den Vergleich geeignet ist.

### Musterloesung

Insgesamt stehen 48 Pflanzen in den Beeten. Der Anteil des zweiten Beetes
betraegt $\frac{11}{48}$. Ein Saeulendiagramm macht die absoluten
Haeufigkeiten der vier Beete direkt vergleichbar.
""", "Saatgutmischung")


def session(repo: Path, path: Path):
    return near.prepare_acceptance_session(
        repo,
        explicit_config=path,
        environ={},
        subject="mathematics",
        filters={
            "subject": "mathematics",
            "grade": 7,
            "suitability": "structure_only",
        },
    )


class NearCopyTests(unittest.TestCase):
    def test_policy_and_result_projection_are_closed(self):
        policy = near.load_policy()
        self.assertEqual(policy["policy_version"], 1)
        self.assertEqual(policy["max_attempts"], 3)
        with self.assertRaises(TypeError):
            policy["max_attempts"] = 4
        value = near.NearCopyResult(
            "anti_copy_pass", "near_copy_no_risk_detected", True
        )
        self.assertEqual(set(value.as_dict()), {
            "status", "reason_code", "comparison_performed",
            "release_allowed",
        })
        self.assertEqual(repr(value), "NearCopyResult(<closed>)")
        with self.assertRaises(TypeError):
            json.dumps(value)
        for forbidden in (
            "score", "similarity", "count", "path", "filename", "hash",
            "hit", "document", "source", "snippet", "text",
        ):
            self.assertNotIn(forbidden, json.dumps(value.as_dict()).casefold())

    def test_exact_case_whitespace_punctuation_and_markup_are_risk(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo, _source, path = layout(Path(temporary))
            candidates = (
                copied_course(),
                copied_course().upper(),
                copied_course().replace(" ", "   ").replace(".", " ! "),
                copied_course().replace(
                    "1. Berechne", "- **Berechne"
                ).replace(
                    "2. Bestimme", "- _Bestimme"
                ).replace(
                    "3. Begruende", "- Begruende"
                ),
            )
            with session(repo, path) as gate:
                for candidate in candidates[:3]:
                    result = gate.check(candidate)
                    self.assertEqual(result.status, "anti_copy_risk")
                    self.assertTrue(result.comparison_performed)
                    self.assertFalse(result.release_allowed)
            with session(repo, path) as gate:
                result = gate.check(candidates[3])
            self.assertEqual(result.status, "anti_copy_risk")

    def test_cosmetic_rephrasing_and_characteristic_composition_are_risk(self):
        cosmetic = course(r"""
Ein Fahrradkurier bereitet die Fahrt vom Marktplatz zum Schwimmbad vor.
Der Weg ist 18 km lang; fuer ihn sind 45 min vorgesehen.

1. Ermittle die durchschnittliche Geschwindigkeit in km/h.
2. Berechne die Strecke nach 30 min bei unveraendertem Tempo.
3. Erklaere, ob 24 km in 60 min denselben Zusammenhang beschreiben.

### Musterloesung

Es gilt $v = \frac{18\,\mathrm{km}}{0{,}75\,\mathrm{h}} = 24\,\mathrm{km/h}$.
Nach 30 min sind 12 km absolviert. Das Paar 60 min und 24 km passt,
denn der Quotient aus Strecke und Zeit bleibt unveraendert.
""")
        composition = course(r"""
Vom Marktplatz fuehrt eine 18 km lange Route zum Schwimmbad.
Ein Fahrradkurier benoetigt dafuer 45 min.

1. Berechne die durchschnittliche Geschwindigkeit in km/h.
2. Bestimme bei gleicher Geschwindigkeit die Strecke nach 30 min.
3. Begruende den proportionalen Zusammenhang mit 24 km in 60 min.

### Musterloesung

Mit $v = \frac{18\,\mathrm{km}}{0{,}75\,\mathrm{h}} = 24\,\mathrm{km/h}$
folgen fuer 30 min genau 12 km. Auch 60 min und 24 km besitzen denselben
konstanten Quotienten aus Strecke und Zeit.
""")
        with tempfile.TemporaryDirectory() as temporary:
            repo, _source, path = layout(Path(temporary))
            for candidate in (cosmetic, composition):
                with session(repo, path) as gate:
                    result = gate.check(candidate)
                self.assertEqual(
                    result.status, "anti_copy_risk", result.as_dict()
                )

    def test_independent_task_and_public_boilerplate_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo, _source, path = layout(Path(temporary))
            with session(repo, path) as gate:
                result = gate.check(independent_course())
            self.assertEqual(result.status, "anti_copy_pass", result.as_dict())
            self.assertEqual(
                result.reason_code, "near_copy_no_risk_detected"
            )
            self.assertTrue(result.release_allowed)

    def test_short_input_session_close_and_three_attempt_limit(self):
        short = course("Nenne einen Wert.", "Kurz")
        with tempfile.TemporaryDirectory() as temporary:
            repo, _source, path = layout(Path(temporary))
            gate = session(repo, path)
            result = gate.check(short)
            self.assertEqual(result.status, "anti_copy_inconclusive")
            self.assertEqual(
                result.reason_code, "near_copy_candidate_too_short"
            )
            gate.close()
            self.assertEqual(
                gate.check(independent_course()).reason_code,
                "near_copy_session_closed",
            )
            with session(repo, path) as bounded:
                for _ in range(3):
                    self.assertEqual(
                        bounded.check(independent_course()).status,
                        "anti_copy_pass",
                    )
                fourth = bounded.check(independent_course())
            self.assertEqual(fourth.status, "anti_copy_inconclusive")
            self.assertEqual(
                fourth.reason_code, "near_copy_attempt_limit"
            )

    def test_dynamic_tex_is_inconclusive_and_decoys_are_not_evidence(self):
        dynamic = (
            r"\csname syntheticDynamicName\endcsname" + PRIVATE_BODY
        )
        decoys = r"""
% SYNTHETIC_PRIVATE_NEAR_COPY_SENTINEL exact copied passage
\newcommand{\decoy}{SYNTHETIC_PRIVATE_NEAR_COPY_SENTINEL copied passage}
\begin{verbatim}
SYNTHETIC_PRIVATE_NEAR_COPY_SENTINEL copied passage
\end{verbatim}
""" + PRIVATE_BODY
        with tempfile.TemporaryDirectory() as temporary:
            repo, _source, path = layout(Path(temporary), dynamic)
            gate = near.prepare_acceptance_session(
                repo, explicit_config=path, environ={},
                subject="mathematics",
                filters={"subject": "mathematics", "grade": 7},
            )
            result = gate.check(independent_course())
            gate.close()
            self.assertEqual(result.status, "anti_copy_inconclusive")
            self.assertEqual(
                result.reason_code, "near_copy_private_dynamic_construct"
            )

        with tempfile.TemporaryDirectory() as temporary:
            repo, _source, path = layout(Path(temporary), decoys)
            gate = near.prepare_acceptance_session(
                repo, explicit_config=path, environ={},
                subject="mathematics",
                filters={"subject": "mathematics", "grade": 7},
            )
            candidate = independent_course().replace(
                "Saatgutmischung", SENTINEL
            )
            result = gate.check(candidate)
            gate.close()
            self.assertEqual(result.status, "anti_copy_pass", result.as_dict())

    def test_unknown_macro_does_not_hide_a_copy(self):
        value = PRIVATE_BODY.replace(
            "Ein Fahrradkurier",
            r"\syntheticUnknownMacro{Ein Fahrradkurier}",
        )
        with tempfile.TemporaryDirectory() as temporary:
            repo, _source, path = layout(Path(temporary), value)
            with session(repo, path) as gate:
                result = gate.check(copied_course())
            self.assertEqual(result.status, "anti_copy_risk", result.as_dict())

    def test_invalid_scope_config_and_operational_failures_are_sanitized(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo, source, path = layout(base)
            invalid = config_value(source)
            invalid["private_argument_sentinel"] = SENTINEL
            write_config(path, invalid)
            gate = session(repo, path)
            result = gate.check(independent_course())
            surface = json.dumps(result.as_dict()) + repr(gate)
            gate.close()
            self.assertEqual(result.status, "anti_copy_inconclusive")
            self.assertNotIn(SENTINEL, surface)
            self.assertNotIn(str(source), surface)

            gate = near.prepare_acceptance_session(
                repo, explicit_config=path, environ={},
                subject="physics",
                filters={"subject": "mathematics", "grade": 7},
            )
            result = gate.check(independent_course())
            self.assertEqual(result.reason_code, "near_copy_filter_invalid")
            gate.close()

    def test_hardlink_and_identity_failures_are_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo, source, path = layout(base)
            original = source / "allowed" / "task.tex"
            alias = source / "allowed" / "alias.tex"
            try:
                os.link(original, alias)
            except (OSError, NotImplementedError):
                print("SKIP near-copy hardlink creation unavailable")
            else:
                gate = session(repo, path)
                result = gate.check(independent_course())
                gate.close()
                self.assertEqual(result.status, "anti_copy_inconclusive")
                self.assertFalse(result.comparison_performed)

        with tempfile.TemporaryDirectory() as temporary:
            repo, source, path = layout(Path(temporary))
            with patch.object(
                near.selector, "read_candidate_bytes",
                side_effect=OSError(str(source) + SENTINEL),
            ):
                gate = session(repo, path)
            result = gate.check(independent_course())
            surface = json.dumps(result.as_dict()) + repr(gate)
            gate.close()
            self.assertEqual(result.status, "anti_copy_inconclusive")
            self.assertNotIn(SENTINEL, surface)
            self.assertNotIn(str(source), surface)

    def test_no_network_writes_or_generic_oracle_cli(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo, source, path = layout(Path(temporary))
            before = {
                item.relative_to(source).as_posix(): item.read_bytes()
                for item in source.rglob("*") if item.is_file()
            }
            with patch.object(
                socket, "create_connection",
                side_effect=AssertionError("network forbidden"),
            ), patch.object(
                subprocess, "Popen",
                side_effect=AssertionError("subprocess forbidden"),
            ):
                gate = session(repo, path)
                result = gate.check(independent_course())
                gate.close()
            after = {
                item.relative_to(source).as_posix(): item.read_bytes()
                for item in source.rglob("*") if item.is_file()
            }
            self.assertEqual(result.status, "anti_copy_pass")
            self.assertEqual(before, after)

        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = near.main()
        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "anti_copy_inconclusive")
        self.assertFalse(payload["release_allowed"])
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
