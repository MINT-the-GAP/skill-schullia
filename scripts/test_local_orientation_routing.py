#!/usr/bin/env python3
"""Dependency-free routing matrix for optional local orientation."""
from __future__ import annotations

import contextlib
import io
import json
import unittest

import local_orientation_routing as routing

SENTINEL = "SYNTHETIC_ROUTING_SENTINEL"


def decide(**changes):
    values = {
        "subject": "mathematics",
        "authoring_action": "create_task",
        "browser_or_url_only": False,
        "filesystem_available": True,
        "python_available": True,
        "user_scope": "auto",
    }
    values.update(changes)
    return routing.decide_orientation_route(**values)


class RoutingTests(unittest.TestCase):
    def test_relevant_authoring_routes_use_explicit_local_scope(self):
        for subject in ("mathematics", "physics"):
            for action in ("create_task", "substantial_revision", "compose_course"):
                result = decide(subject=subject, authoring_action=action)
                self.assertTrue(result.eligible, (subject, action))
                self.assertEqual(result.scope, "local")
                self.assertTrue(result.read_routing_reference)
        self.assertEqual(decide(user_scope="both").scope, "both")
        self.assertEqual(decide(user_scope="local").scope, "local")

    def test_browser_opt_out_and_missing_capabilities_short_circuit(self):
        cases = (
            ({"browser_or_url_only": True}, "routing_browser_public_only"),
            ({"user_scope": "public_only"}, "routing_user_public_only"),
            ({"filesystem_available": False}, "routing_capability_unavailable"),
            ({"python_available": False}, "routing_capability_unavailable"),
        )
        for changes, reason in cases:
            result = decide(**changes)
            self.assertFalse(result.eligible)
            self.assertEqual(result.scope, "public")
            self.assertEqual(result.reason_code, reason)
            self.assertFalse(result.read_routing_reference)

    def test_subject_and_action_matrix(self):
        self.assertEqual(decide(subject="chemistry").reason_code,
                         "routing_subject_not_eligible")
        for action in ("explain_syntax", "classify_operator", "gamification_only"):
            result = decide(authoring_action=action)
            self.assertEqual(result.reason_code, "routing_action_public_only")
            self.assertFalse(result.eligible)
        for changes in (
            {"subject": 1}, {"authoring_action": SENTINEL},
            {"browser_or_url_only": 1}, {"filesystem_available": None},
            {"python_available": "yes"}, {"user_scope": SENTINEL},
        ):
            result = decide(**changes)
            self.assertEqual(result.reason_code, "routing_request_invalid")
            self.assertNotIn(SENTINEL, json.dumps(result.as_dict()))

    def test_decider_is_pure_and_projection_is_closed(self):
        result = decide()
        self.assertEqual(set(result.as_dict()), {
            "eligible", "scope", "reason_code", "read_routing_reference",
        })
        self.assertEqual(repr(result), "RoutingDecision(<public-safe>)")
        with self.assertRaises(TypeError):
            json.dumps(result)
        for scope in ([], {}, None):
            with self.assertRaises(routing.RoutingFault):
                routing.RoutingDecision(scope=scope)
        with self.assertRaises(routing.RoutingFault):
            routing.RoutingDecision(
                True, "local", "routing_browser_public_only", True
            )
        with self.assertRaises(AttributeError):
            result.scope = "public"

    def test_cli_never_echoes_invalid_inputs(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = routing.main(["--subject", SENTINEL, "--action", SENTINEL,
                                 "--user-scope", SENTINEL])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out.getvalue())["reason_code"],
                         "routing_request_invalid")
        self.assertNotIn(SENTINEL, out.getvalue() + err.getvalue())


if __name__ == "__main__":
    unittest.main()
