#!/usr/bin/env python3
"""Pure fail-soft routing decision for optional local authoring guidance."""
from __future__ import annotations

import argparse
import json
from typing import Sequence

ELIGIBLE_SUBJECTS = frozenset({"mathematics", "physics"})
ELIGIBLE_ACTIONS = frozenset({
    "create_task", "substantial_revision", "compose_course",
})
PUBLIC_ONLY_ACTIONS = frozenset({
    "explain_syntax", "classify_operator", "gamification_only",
})
USER_SCOPES = frozenset({"auto", "public_only", "local", "both"})
REASON_CODES = frozenset({
    "routing_local_eligible", "routing_user_public_only",
    "routing_browser_public_only", "routing_capability_unavailable",
    "routing_subject_not_eligible", "routing_action_public_only",
    "routing_request_invalid",
})


class RoutingFault(ValueError):
    def __init__(self):
        super().__init__("routing_request_invalid")


class RoutingDecision:
    __slots__ = (
        "eligible", "scope", "reason_code", "read_routing_reference", "_sealed",
    )

    def __init__(self, eligible=False, scope="public",
                 reason_code="routing_request_invalid",
                 read_routing_reference=False):
        if (type(eligible) is not bool or type(scope) is not str
                or scope not in {"public", "local", "both"}
                or type(reason_code) is not str or reason_code not in REASON_CODES
                or type(read_routing_reference) is not bool
                or read_routing_reference != eligible
                or eligible != (scope in {"local", "both"})
                or eligible != (reason_code == "routing_local_eligible")):
            raise RoutingFault()
        object.__setattr__(self, "eligible", eligible)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "reason_code", reason_code)
        object.__setattr__(
            self, "read_routing_reference", read_routing_reference
        )
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("routing_decision_immutable")
        object.__setattr__(self, name, value)

    def __repr__(self):
        return "RoutingDecision(<public-safe>)"

    def as_dict(self):
        return {
            "eligible": self.eligible,
            "scope": self.scope,
            "reason_code": self.reason_code,
            "read_routing_reference": self.read_routing_reference,
        }


def decide_orientation_route(*, subject, authoring_action,
                             browser_or_url_only, filesystem_available,
                             python_available, user_scope="auto"):
    """Decide eligibility without importing config, search, index or build code."""
    try:
        if (type(subject) is not str or type(authoring_action) is not str
                or type(browser_or_url_only) is not bool
                or type(filesystem_available) is not bool
                or type(python_available) is not bool
                or type(user_scope) is not str or user_scope not in USER_SCOPES):
            raise RoutingFault()
        if user_scope == "public_only":
            return RoutingDecision(reason_code="routing_user_public_only")
        if browser_or_url_only:
            return RoutingDecision(reason_code="routing_browser_public_only")
        if not filesystem_available or not python_available:
            return RoutingDecision(reason_code="routing_capability_unavailable")
        if authoring_action in PUBLIC_ONLY_ACTIONS:
            return RoutingDecision(reason_code="routing_action_public_only")
        if authoring_action not in ELIGIBLE_ACTIONS:
            raise RoutingFault()
        if subject not in ELIGIBLE_SUBJECTS:
            return RoutingDecision(reason_code="routing_subject_not_eligible")
        scope = user_scope if user_scope in {"local", "both"} else "local"
        return RoutingDecision(True, scope, "routing_local_eligible", True)
    except RoutingFault:
        return RoutingDecision(reason_code="routing_request_invalid")
    except Exception:
        return RoutingDecision(reason_code="routing_request_invalid")


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise RoutingFault()


def parse_args(argv: Sequence[str] | None = None):
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--action", required=True, dest="authoring_action")
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--no-filesystem", action="store_true")
    parser.add_argument("--no-python", action="store_true")
    parser.add_argument("--user-scope", default="auto")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None):
    try:
        args = parse_args(argv)
        result = decide_orientation_route(
            subject=args.subject, authoring_action=args.authoring_action,
            browser_or_url_only=args.browser,
            filesystem_available=not args.no_filesystem,
            python_available=not args.no_python,
            user_scope=args.user_scope,
        )
    except Exception:
        result = RoutingDecision(reason_code="routing_request_invalid")
    print(json.dumps(result.as_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.reason_code != "routing_request_invalid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
