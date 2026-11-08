#!/usr/bin/env python3
"""Dependency-free synthetic tests for abstract local orientation guidance."""
from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import local_orientation_config as config
import local_orientation_guidance as guidance
import search_local_orientation as search
from test_local_orientation_search import SENTINEL, metadata


def document(number, *, family=None, same_digest=False):
    value = metadata(f"allowed/guidance-{number}.tex")
    value["local_provenance"]["integrity_sha256"] = (
        "1" * 64 if same_digest else f"{number + 1:064x}"
    )
    value["classification"]["learner_groups"] = [SENTINEL]
    return value, family or ("synthetic-family", str(number))


def result(documents):
    hits = tuple(
        search.LocalHit(value, (), ("synthetic",), family)
        for value, family in documents
    )
    return search.LocalSearchResult(
        hits, availability_state=config.STATE_AVAILABLE,
        reason_code="search_complete", index_ready=True,
        local_search_performed=True,
    )


class GuidanceTests(unittest.TestCase):
    def test_single_and_duplicate_documents_do_not_prepare_profile(self):
        single = guidance.prepare_orientation_guidance(result([document(1)]))
        self.assertFalse(single.orientation_profile_prepared)
        self.assertEqual(single.reason_code, "guidance_diversity_required")
        duplicates = guidance.prepare_orientation_guidance(result([
            document(1, family=("one",), same_digest=True),
            document(2, family=("two",), same_digest=True),
            document(3, family=("three",), same_digest=True),
        ]))
        self.assertFalse(duplicates.orientation_profile_prepared)
        self.assertEqual(duplicates.reason_code, "guidance_diversity_required")

    def test_three_hashes_in_one_include_family_do_not_prepare_profile(self):
        same_family = ("connected",)
        local_result = result([
            document(1, family=same_family),
            document(2, family=same_family),
            document(3, family=same_family),
        ])
        for number, hit in enumerate(local_result.hits):
            with self.assertRaises(AttributeError):
                hit.family_key = ("forged-family", str(number))
            detached = hit.metadata
            detached["local_provenance"]["integrity_sha256"] = f"{number + 9:064x}"
        with self.assertRaises(AttributeError):
            local_result.hits = ()
        prepared = guidance.prepare_orientation_guidance(local_result)
        self.assertFalse(prepared.orientation_profile_prepared)
        self.assertEqual(prepared.reason_code, "guidance_diversity_required")

        duplicates = result([
            document(1, family=("one",), same_digest=True),
            document(2, family=("two",), same_digest=True),
            document(3, family=("three",), same_digest=True),
        ])
        for number, hit in enumerate(duplicates.hits):
            detached = hit.metadata
            detached["local_provenance"]["integrity_sha256"] = f"{number + 20:064x}"
        self.assertEqual(
            guidance.prepare_orientation_guidance(duplicates).reason_code,
            "guidance_diversity_required",
        )

    def test_shared_features_are_deterministic_and_private_values_stay_hidden(self):
        documents = [document(1), document(2), document(3)]
        first = guidance.prepare_orientation_guidance(
            result(documents), requested_filter_dimensions={"subject": "mathematics",
                                                            "task_family": "calculation",
                                                            "learner_group": SENTINEL})
        second = guidance.prepare_orientation_guidance(result(list(reversed(documents))),
                                                        requested_filter_dimensions=(
                                                            "task_family", "learner_group",
                                                            "subject"))
        self.assertTrue(first.orientation_profile_prepared, first.reason_code)
        self.assertFalse(first.local_orientation_used)
        self.assertEqual(first.as_dict(), second.as_dict())
        payload = first.as_dict()
        self.assertEqual(payload["filter_dimensions"],
                         ["learner_group", "subject", "task_family"])
        self.assertIn("calculation", payload["features"]["task_families"])
        serialized = json.dumps(payload, sort_keys=True) + repr(first)
        for secret in (SENTINEL, "guidance-1.tex", "synthetic-source",
                       documents[0][0]["document_id"],
                       documents[0][0]["local_provenance"]["integrity_sha256"]):
            self.assertNotIn(secret, serialized)
        for forbidden in ("hit_count", "source_count", "document_count",
                          "support_count", "frequency", "relative_locator",
                          "integrity_sha256"):
            self.assertNotIn(forbidden, serialized.casefold())
        with self.assertRaises(TypeError):
            json.dumps(first)

    def test_feature_needs_support_from_three_families_and_hashes(self):
        documents = [document(1), document(2), document(3)]
        modified = copy.deepcopy(documents[2][0])
        modified["features"]["task_families"] = []
        documents[2] = (modified, documents[2][1])
        prepared = guidance.prepare_orientation_guidance(result(documents))
        self.assertTrue(prepared.orientation_profile_prepared)
        self.assertNotIn("calculation", prepared.as_dict()["features"]["task_families"])
        self.assertTrue(any(prepared.as_dict()["features"].values()))

    def test_unknown_review_and_invalid_metadata_are_not_used(self):
        documents = [document(1), document(2), document(3)]
        for status in ("unknown", "ambiguous", "review_required"):
            changed = []
            for value, family in documents:
                item = copy.deepcopy(value)
                item["features"]["status"] = status
                if status == "unknown":
                    for dimension in guidance._taxonomy()[0]:
                        item["features"][dimension] = []
                if status == "ambiguous":
                    item["classification"]["subjects"] = [
                        "mathematics", "physics",
                    ]
                    item["features"]["topic_ids"] = [
                        {
                            "id": "algebra-equations",
                            "basis": "body_pattern",
                            "confidence": "medium",
                        },
                        {
                            "id": "electricity",
                            "basis": "body_pattern",
                            "confidence": "medium",
                        },
                    ]
                if status == "review_required":
                    item["risk_codes"] = ["shell_escape"]
                    item["suitability"] = "review_required"
                    item["technical"]["parse_status"] = "parsed_with_warnings"
                changed.append((item, family))
            outcome = guidance.prepare_orientation_guidance(result(changed))
            self.assertFalse(outcome.orientation_profile_prepared)
        broken = copy.deepcopy(documents[0][0])
        broken["features"]["task_families"][0]["id"] = SENTINEL
        with self.assertRaises(search.SearchFault) as caught:
            result([(broken, documents[0][1]), documents[1], documents[2]])
        self.assertEqual(str(caught.exception), "search_metadata_invalid")
        self.assertNotIn(SENTINEL, str(caught.exception))

    def test_application_requires_subset_all_checks_and_non_leak(self):
        with self.assertRaises(guidance.GuidanceFault):
            guidance.OrientationGuidance(
                availability_state=config.STATE_AVAILABLE,
                reason_code="guidance_applied",
            )
        prepared = guidance.prepare_orientation_guidance(
            result([document(1), document(2), document(3)]))
        selected = sorted(prepared.feature_ids)[0]
        for applied, checks, non_leak in (
            ((), guidance.COUNTERCHECKS, True),
            ((selected,), {"public_evidence"}, True),
            ((selected,), guidance.COUNTERCHECKS, False),
            ((SENTINEL,), guidance.COUNTERCHECKS, True),
        ):
            with self.assertRaises(guidance.GuidanceFault) as caught:
                guidance.record_guidance_application(
                    prepared, applied_feature_ids=applied,
                    completed_counterchecks=checks,
                    non_leak_confirmed=non_leak)
            self.assertEqual(str(caught.exception), "guidance_operational_error")
            self.assertNotIn(SENTINEL, str(caught.exception))
        used = guidance.record_guidance_application(
            prepared, applied_feature_ids=(selected,),
            completed_counterchecks=guidance.COUNTERCHECKS,
            non_leak_confirmed=True)
        payload = used.as_dict()
        self.assertTrue(payload["local_orientation_used"])
        self.assertEqual(payload["reason_code"], "guidance_applied")
        self.assertEqual(payload["applied_feature_ids"], [selected])
        with self.assertRaises(TypeError):
            prepared._features["topic_ids"] = ("energy",)
        with self.assertRaises(AttributeError):
            prepared._features = {"topic_ids": ("energy",)}
        with self.assertRaises(AttributeError):
            prepared._used = True
        self.assertFalse(prepared.local_orientation_used)

    def test_unavailable_empty_and_public_scope_are_distinct(self):
        unavailable = search.LocalSearchResult(
            availability_state=config.STATE_NOT_CONFIGURED,
            reason_code="configuration_disabled")
        brief = guidance.prepare_orientation_guidance(unavailable)
        self.assertEqual(brief.reason_code, "guidance_local_unavailable")
        empty = search.LocalSearchResult(
            availability_state=config.STATE_AVAILABLE,
            reason_code="search_complete", index_ready=True,
            local_search_performed=True)
        self.assertEqual(guidance.prepare_orientation_guidance(empty).reason_code,
                         "guidance_no_candidates")
        with patch.dict(sys.modules, {"search_with_local_orientation": None}):
            for scope in ("public", [], {}, None):
                public = guidance.search_orientation_guidance(
                    Path(tempfile.gettempdir()), scope=scope)
                self.assertEqual(public.reason_code, "guidance_not_requested")
                self.assertFalse(public.local_search_performed)

    def test_cli_argument_errors_are_sanitized(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = guidance.main(["--scope", SENTINEL])
        self.assertEqual(code, 1)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["reason_code"], "guidance_operational_error")
        self.assertNotIn(SENTINEL, out.getvalue() + err.getvalue())


if __name__ == "__main__":
    unittest.main()
