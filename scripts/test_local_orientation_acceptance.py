#!/usr/bin/env python3
"""Synthetic tests for the closed local-orientation acceptance gate."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import local_orientation_acceptance as acceptance
import local_orientation_config as config
import local_orientation_features as features
import local_orientation_guidance as guidance
import validate_lia


CANDIDATE = r"""<!--
author: Synthetic Test
version: 1.0.0
language: de
narrator: Deutsch Female
comment: Synthetischer Abnahmekurs.

import: https://raw.githubusercontent.com/MINT-the-GAP/lia-board-mode/main/README.md

tags: Mathematik, Klasse 7, Rechnen
-->

# Proportionaler Zusammenhang

Berechne den Wert. Begründe deinen Rechenweg.

[[12]]

**********
Aus $3 \cdot 4 = 12$ folgt der gesuchte Wert.
**********
"""

FEATURE_ID = "task_families:calculation"
PRIVATE_SENTINEL = "PRIVATE-TEX-SENTINEL-88137"


def prepared_guidance(feature_id: str = FEATURE_ID):
    feature_map = {
        dimension: () for dimension in features.FEATURE_DIMENSIONS
    }
    dimension, identifier = feature_id.split(":", 1)
    feature_map[dimension] = (identifier,)
    return guidance.OrientationGuidance(
        availability_state=config.STATE_AVAILABLE,
        reason_code="guidance_ready",
        filter_dimensions=("grade", "subject", "task_family"),
        features=feature_map,
        local_search_performed=True,
        orientation_profile_prepared=True,
    )


class AcceptanceTests(unittest.TestCase):
    def kwargs(self, *, scope="both"):
        return {
            "candidate_text": CANDIDATE,
            "case_id": "L1",
            "scope": scope,
            "filters": {
                "subject": "mathematics",
                "grade": 7,
                **(
                    {"task_family": "calculation"}
                    if scope == "both" else {}
                ),
            },
            "applied_feature_ids": (
                [FEATURE_ID] if scope == "both" else []
            ),
            "public_evidence_status": "bestanden",
            "subject_review_status": "bestanden",
            "evaluator_status": "bestanden",
            "sources_unchanged": True,
            "no_private_content_used": True,
            "no_private_content_output": True,
            "no_private_content_versioned": True,
            "environ": {},
        }

    def run_patched(self, *, scope="both", anti="anti_copy_pass",
                    leak=True, prepared=None, **changes):
        values = self.kwargs(scope=scope)
        values.update(changes)
        brief = prepared if prepared is not None else prepared_guidance()
        with (
            patch.object(
                acceptance.guidance,
                "search_orientation_guidance",
                return_value=brief,
            ) as search,
            patch.object(
                acceptance,
                "_perform_anti_copy",
                return_value=anti,
            ) as anti_copy,
            patch.object(
                acceptance,
                "_leak_clean",
                return_value=leak,
            ) as leak_gate,
        ):
            witness = acceptance.run_acceptance(**values)
        return witness, search, anti_copy, leak_gate

    def test_synthetic_candidate_is_strictly_valid(self):
        self.assertEqual(validate_lia.validate(CANDIDATE, "course"), [])
        self.assertIn(
            FEATURE_ID,
            acceptance._observed_feature_ids(
                CANDIDATE, subject="mathematics",
            ),
        )

    def test_both_release_records_only_after_every_gate(self):
        original = guidance.record_guidance_application
        with patch.object(
            guidance,
            "record_guidance_application",
            wraps=original,
        ) as record:
            witness, search, anti_copy, leak_gate = self.run_patched()
        data = witness.as_dict()
        self.assertTrue(witness.release_allowed)
        self.assertEqual(data["reason_code"], "acceptance_pass")
        self.assertEqual(data["availability_state"], config.STATE_AVAILABLE)
        self.assertTrue(data["local_search_performed"])
        self.assertTrue(data["orientation_profile_prepared"])
        self.assertTrue(data["local_orientation_used"])
        self.assertEqual(data["applied_feature_ids"], [FEATURE_ID])
        self.assertEqual(
            data["completed_counterchecks"],
            sorted(guidance.COUNTERCHECKS),
        )
        self.assertEqual(data["anti_copy_status"], "anti_copy_pass")
        self.assertTrue(data["non_leak_confirmed"])
        self.assertEqual(search.call_count, 1)
        self.assertEqual(anti_copy.call_count, 1)
        self.assertEqual(leak_gate.call_count, 1)
        self.assertEqual(record.call_count, 1)
        self.assertEqual(
            record.call_args.kwargs["completed_counterchecks"],
            tuple(sorted(guidance.COUNTERCHECKS)),
        )

    def test_public_only_release_never_prepares_or_records_guidance(self):
        with (
            patch.object(
                guidance,
                "search_orientation_guidance",
                side_effect=AssertionError("must_not_search"),
            ) as search,
            patch.object(
                guidance,
                "record_guidance_application",
                side_effect=AssertionError("must_not_record"),
            ) as record,
            patch.object(
                acceptance, "_perform_anti_copy",
                return_value="anti_copy_pass",
            ),
            patch.object(acceptance, "_leak_clean", return_value=True),
        ):
            witness = acceptance.run_acceptance(
                **self.kwargs(scope="public_only"),
            )
        data = witness.as_dict()
        self.assertTrue(witness.release_allowed)
        self.assertEqual(
            data["reason_code"], "acceptance_public_only_pass",
        )
        self.assertEqual(
            data["availability_state"], config.STATE_NOT_CONFIGURED,
        )
        self.assertFalse(data["local_search_performed"])
        self.assertFalse(data["orientation_profile_prepared"])
        self.assertFalse(data["local_orientation_used"])
        self.assertEqual(data["applied_feature_ids"], [])
        search.assert_not_called()
        record.assert_not_called()

    def test_strict_validator_blocks_before_private_gates(self):
        invalid = self.kwargs()
        invalid["candidate_text"] = "not a LiaScript course"
        with (
            patch.object(
                acceptance.guidance, "search_orientation_guidance",
            ) as search,
            patch.object(acceptance, "_perform_anti_copy") as anti_copy,
            patch.object(acceptance, "_leak_clean") as leak_gate,
            patch.object(
                guidance, "record_guidance_application",
            ) as record,
        ):
            witness = acceptance.run_acceptance(**invalid)
        self.assertEqual(
            witness.as_dict()["reason_code"],
            "acceptance_technical_validation_failed",
        )
        search.assert_not_called()
        anti_copy.assert_not_called()
        leak_gate.assert_not_called()
        record.assert_not_called()

    def test_review_and_private_boundary_fail_closed(self):
        cases = (
            (
                {"public_evidence_status": "Warnung"},
                "acceptance_public_evidence_failed",
            ),
            (
                {"subject_review_status": "unbelegt"},
                "acceptance_subject_review_failed",
            ),
            (
                {"evaluator_status": "blockiert"},
                "acceptance_evaluator_failed",
            ),
            (
                {"no_private_content_used": False},
                "acceptance_private_content_boundary",
            ),
            (
                {"no_private_content_output": False},
                "acceptance_private_content_boundary",
            ),
            (
                {"no_private_content_versioned": False},
                "acceptance_private_content_boundary",
            ),
            (
                {"sources_unchanged": False},
                "acceptance_sources_changed",
            ),
        )
        for changes, reason in cases:
            with self.subTest(reason=reason, changes=changes):
                values = self.kwargs()
                values.update(changes)
                with patch.object(
                    acceptance.guidance, "search_orientation_guidance",
                ) as search:
                    witness = acceptance.run_acceptance(**values)
                self.assertFalse(witness.release_allowed)
                self.assertEqual(witness.as_dict()["reason_code"], reason)
                search.assert_not_called()

    def test_guidance_and_feature_proof_fail_closed(self):
        unavailable = guidance.OrientationGuidance(
            availability_state=config.STATE_UNREACHABLE,
            reason_code="guidance_local_unavailable",
        )
        witness, _search, anti_copy, leak_gate = self.run_patched(
            prepared=unavailable,
        )
        self.assertEqual(
            witness.as_dict()["reason_code"],
            "acceptance_guidance_unavailable",
        )
        anti_copy.assert_not_called()
        leak_gate.assert_not_called()

        values = self.kwargs()
        values["candidate_text"] = CANDIDATE.replace(
            "Berechne den Wert.", "Notiere den Wert.",
        )
        witness, _search, anti_copy, leak_gate = self.run_patched(
            **values,
        )
        self.assertEqual(
            witness.as_dict()["reason_code"],
            "acceptance_feature_unverified",
        )
        anti_copy.assert_not_called()
        leak_gate.assert_not_called()

    def test_anti_copy_and_leak_gate_block_recording(self):
        for anti in ("anti_copy_risk", "anti_copy_inconclusive"):
            with self.subTest(anti=anti), patch.object(
                guidance, "record_guidance_application",
            ) as record:
                witness, _search, _anti, leak_gate = self.run_patched(
                    anti=anti,
                )
                data = witness.as_dict()
                self.assertEqual(
                    data["reason_code"], "acceptance_anti_copy_blocked",
                )
                self.assertEqual(data["anti_copy_status"], anti)
                leak_gate.assert_not_called()
                record.assert_not_called()
        with patch.object(
            guidance, "record_guidance_application",
        ) as record:
            witness, *_ = self.run_patched(leak=False)
        self.assertEqual(
            witness.as_dict()["reason_code"], "acceptance_leak_blocked",
        )
        record.assert_not_called()

    def test_record_failure_is_not_a_release(self):
        with patch.object(
            guidance,
            "record_guidance_application",
            side_effect=guidance.GuidanceFault(),
        ):
            witness, *_ = self.run_patched()
        self.assertFalse(witness.release_allowed)
        self.assertEqual(
            witness.as_dict()["reason_code"],
            "acceptance_application_rejected",
        )
        self.assertFalse(witness.as_dict()["local_orientation_used"])

    def test_witness_is_closed_immutable_and_contains_no_sentinel(self):
        witness, *_ = self.run_patched(scope="public_only")
        with self.assertRaises(AttributeError):
            witness.extra = PRIVATE_SENTINEL
        encoded = json.dumps(witness.as_dict(), sort_keys=True)
        self.assertNotIn(PRIVATE_SENTINEL, encoded)
        self.assertNotIn(PRIVATE_SENTINEL, repr(witness))
        tampered = witness.as_dict()
        tampered["private_path"] = PRIVATE_SENTINEL
        with self.assertRaises(acceptance.AcceptanceFault):
            acceptance.AcceptanceWitness(tampered)

    def test_candidate_path_is_bounded_markdown_without_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            markdown = root / "candidate.md"
            markdown.write_bytes(CANDIDATE.encode("utf-8"))
            self.assertEqual(
                acceptance._read_candidate_path(markdown), CANDIDATE,
            )
            tex = root / "candidate.tex"
            tex.write_bytes(PRIVATE_SENTINEL.encode("utf-8"))
            with self.assertRaises(acceptance.AcceptanceFault):
                acceptance._read_candidate_path(tex)
            hardlink = root / "linked.md"
            try:
                os.link(markdown, hardlink)
            except OSError:
                return
            with self.assertRaises(acceptance.AcceptanceFault):
                acceptance._read_candidate_path(markdown)
            with self.assertRaises(acceptance.AcceptanceFault):
                acceptance._read_candidate_path(hardlink)

    def test_near_copy_adapter_accepts_only_a_real_pass(self):
        class Result:
            def __init__(self, status, comparison=True):
                self.status = status
                self.reason_code = "synthetic_reason"
                self.comparison_performed = comparison
                self.release_allowed = status == "anti_copy_pass"

        class Session:
            def __init__(self, result):
                self.result = result
                self.checks = 0
                self.closed = False

            def check(self, text):
                self.checks += 1
                self.seen = text
                return self.result

            def close(self):
                self.closed = True

        for status in (
            "anti_copy_pass", "anti_copy_risk", "anti_copy_inconclusive",
        ):
            result = Result(status)
            session = Session(result)
            fake = SimpleNamespace(
                NearCopyResult=Result,
                prepare_acceptance_session=lambda *_a, **_k: session,
            )
            with patch.dict(
                sys.modules, {"local_orientation_near_copy": fake},
            ):
                observed = acceptance._perform_anti_copy(
                    acceptance.ROOT,
                    explicit_config=None,
                    environ={},
                    subject="mathematics",
                    filters={"subject": "mathematics", "grade": 7},
                    candidate_text=CANDIDATE,
                )
            self.assertEqual(observed, status)
            self.assertEqual(session.checks, 1)
            self.assertTrue(session.closed)

        session = Session(Result("anti_copy_pass", comparison=False))
        fake = SimpleNamespace(
            NearCopyResult=Result,
            prepare_acceptance_session=lambda *_a, **_k: session,
        )
        with (
            patch.dict(
                sys.modules, {"local_orientation_near_copy": fake},
            ),
            self.assertRaises(acceptance.AcceptanceFault),
        ):
            acceptance._perform_anti_copy(
                acceptance.ROOT,
                explicit_config=None,
                environ={},
                subject="mathematics",
                filters={"subject": "mathematics", "grade": 7},
                candidate_text=CANDIDATE,
            )
        self.assertTrue(session.closed)

    def test_cli_error_is_sanitized(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = acceptance.main([
                "--unknown-" + PRIVATE_SENTINEL,
            ])
        self.assertEqual(code, 2)
        payload = json.loads(output.getvalue())
        self.assertEqual(
            payload,
            {
                "reason_code": "acceptance_input_invalid",
                "release_status": "nicht_freigegeben",
            },
        )
        self.assertNotIn(PRIVATE_SENTINEL, output.getvalue())


if __name__ == "__main__":
    unittest.main()
