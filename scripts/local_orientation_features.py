#!/usr/bin/env python3
"""Closed, bounded feature extraction for already-preprocessed local TeX."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import re
import time
from types import MappingProxyType
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = ROOT / "references" / "local-orientation-feature-taxonomy.json"
TAXONOMY_VERSION = 1
FEATURE_DIMENSIONS = (
    "topic_ids", "task_families", "learning_actions", "response_forms",
    "solution_forms", "reasoning_structures", "number_profiles",
    "quantity_profiles", "context_profiles", "representations",
    "progression_profiles", "complexity_bands",
)
FEATURE_STATUSES = frozenset(
    {"classified", "unknown", "ambiguous", "review_required"}
)
FEATURE_BASES = frozenset(
    {"body_pattern", "operator_derived", "structure_derived"}
)
FEATURE_CONFIDENCES = frozenset({"medium", "high"})
_RULE_KEYS = frozenset(
    {"subjects", "terms", "commands", "operators", "detectors"}
)
_DETECTORS = frozenset({
    "integer", "decimal", "fraction", "percentage", "scientific",
    "symbolic", "unit-bearing", "single-part", "multi-part",
    "solution-none", "solution-assigned", "solution-ambiguous",
    "progression-single", "progression-compact",
    "progression-multi-stage", "progression-mixed-representation",
    "structural-low", "structural-medium", "structural-high",
})
_STRUCTURE_DETECTORS = frozenset({
    "single-part", "multi-part", "solution-none", "solution-assigned",
    "solution-ambiguous", "progression-single", "progression-compact",
    "progression-multi-stage", "progression-mixed-representation",
    "structural-low", "structural-medium", "structural-high",
})


class FeatureFault(ValueError):
    def __init__(self, code: str = "feature_invalid"):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class FeatureLimits:
    max_chars: int = 4 * 1024 * 1024
    max_seconds: float = 5.0

    def __post_init__(self) -> None:
        if (type(self.max_chars) is not int
                or not 1 <= self.max_chars <= 4 * 1024 * 1024
                or type(self.max_seconds) not in (int, float)
                or not 0 < self.max_seconds <= 5):
            raise FeatureFault("feature_limits_invalid")


def _unique_pairs(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise FeatureFault("feature_taxonomy_invalid")
        output[key] = value
    return output


def _clean(value: object, maximum: int = 80) -> bool:
    return (type(value) is str and 1 <= len(value) <= maximum
            and not any(ord(char) < 32 or ord(char) in {
                127, 0x85, 0x2028, 0x2029,
            } for char in value))


def _freeze_taxonomy(value):
    if type(value) is dict:
        return MappingProxyType({
            key: _freeze_taxonomy(item) for key, item in value.items()
        })
    if type(value) is list:
        return tuple(_freeze_taxonomy(item) for item in value)
    return value


@lru_cache(maxsize=1)
def load_taxonomy(path: Path = TAXONOMY_PATH) -> Mapping[str, object]:
    """Load only the canonical public taxonomy and validate every rule."""
    try:
        lexical = Path(path).absolute()
        if lexical != TAXONOMY_PATH.absolute():
            raise FeatureFault("feature_taxonomy_boundary")
        resolved = TAXONOMY_PATH.resolve(strict=True)
        if resolved != lexical.resolve(strict=True):
            raise FeatureFault("feature_taxonomy_boundary")
        raw = resolved.read_bytes()
        if len(raw) > 256 * 1024:
            raise FeatureFault("feature_taxonomy_too_large")
        value = json.loads(
            raw.decode("utf-8-sig"), object_pairs_hook=_unique_pairs,
            parse_constant=lambda _value: (_ for _ in ()).throw(
                FeatureFault("feature_taxonomy_invalid")
            ),
        )
    except FeatureFault:
        raise
    except Exception:
        raise FeatureFault("feature_taxonomy_invalid") from None
    if (type(value) is not dict
            or set(value) != {"taxonomy_version", "dimensions"}
            or value["taxonomy_version"] != TAXONOMY_VERSION
            or type(value["dimensions"]) is not dict
            or tuple(value["dimensions"]) != FEATURE_DIMENSIONS):
        raise FeatureFault("feature_taxonomy_invalid")
    total = 0
    for dimension in FEATURE_DIMENSIONS:
        rules = value["dimensions"][dimension]
        if type(rules) is not dict or not 1 <= len(rules) <= 64:
            raise FeatureFault("feature_taxonomy_invalid")
        for identifier, rule in rules.items():
            total += 1
            if (not _clean(identifier, 64)
                    or re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", identifier) is None
                    or type(rule) is not dict
                    or not set(rule).issubset(_RULE_KEYS)
                    or not rule):
                raise FeatureFault("feature_taxonomy_invalid")
            for key in _RULE_KEYS:
                items = rule.get(key, [])
                if (type(items) is not list or len(items) > 64
                        or len(items) != len(set(items))
                        or any(not _clean(item) for item in items)):
                    raise FeatureFault("feature_taxonomy_invalid")
            if (not set(rule.get("subjects", [])).issubset(
                    {"mathematics", "physics"})
                    or not set(rule.get("detectors", [])).issubset(_DETECTORS)
                    or any(not item.startswith("\\")
                           for item in rule.get("commands", []))
                    or any(re.fullmatch(r"[^\W_][\w-]{0,63}", item,
                                        re.UNICODE) is None
                           for item in rule.get("operators", []))):
                raise FeatureFault("feature_taxonomy_invalid")
    if total > 512:
        raise FeatureFault("feature_taxonomy_invalid")
    return _freeze_taxonomy(value)


FEATURE_IDS = MappingProxyType({
    dimension: frozenset(load_taxonomy()["dimensions"][dimension])
    for dimension in FEATURE_DIMENSIONS
})


def _check_time(deadline: float) -> None:
    if time.monotonic() > deadline:
        raise FeatureFault("feature_time_limit")


def _literal_hits(text: str, terms: Sequence[str], deadline: float) -> int:
    hits = 0
    for term in terms:
        _check_time(deadline)
        if re.search(
            r"(?<!\w)" + re.escape(term.casefold()) + r"(?!\w)",
            text, re.UNICODE,
        ):
            hits += 1
            if hits >= 2:
                break
    return hits


def _text_signals(text: str, deadline: float) -> frozenset[str]:
    checks = (
        ("decimal", r"(?<!\w)\d+[,.]\d+(?!\w)"),
        ("fraction", r"\\(?:frac)\b"),
        ("percentage", r"\\%|(?<!\w)prozent(?!\w)"),
        ("scientific", r"(?:10\s*\^\s*(?:\{|\d)|\\(?:cdot)\s*10\b)"),
        ("symbolic", r"\$[^$\r\n]{0,256}[A-Za-z][^$\r\n]{0,256}\$"),
        ("unit-bearing", r"\\(?:mathrm|unit|si)\b|(?<!\w)(?:meter|sekunde|newton|volt|ampere|joule|watt)(?!\w)"),
        ("integer", r"(?<![\w.,])[-+]?\d+(?![\w.,])"),
    )
    output = set()
    for identifier, pattern in checks:
        _check_time(deadline)
        if re.search(pattern, text, re.IGNORECASE | re.UNICODE):
            output.add(identifier)
    return frozenset(output)


def _structural_signals(
    tasks: Sequence[Mapping[str, object]],
    solutions: Sequence[Mapping[str, object]],
    representation_count: int,
) -> frozenset[str]:
    task_count = len(tasks)
    subtasks = [entry.get("subtask_count", 0) for entry in tasks]
    maximum = max(subtasks, default=0)
    output = set()
    if task_count:
        output.add("multi-part" if maximum else "single-part")
        assignments = [entry.get("solution_assignment") for entry in tasks]
        if not solutions:
            output.add("solution-none")
        elif "ambiguous" in assignments:
            output.add("solution-ambiguous")
        elif "assigned" in assignments:
            output.add("solution-assigned")
    if task_count == 1:
        output.add("progression-single")
    elif 2 <= task_count <= 3:
        output.add("progression-compact")
    elif task_count >= 4:
        output.add("progression-multi-stage")
    if representation_count >= 2:
        output.add("progression-mixed-representation")
    # Structural workload only: never a difficulty or AFB classification.
    if task_count:
        if maximum >= 4 or (task_count >= 6 and maximum >= 2):
            output.add("structural-high")
        elif maximum >= 2 or task_count >= 4 or representation_count >= 2:
            output.add("structural-medium")
        else:
            output.add("structural-low")
    return frozenset(output)


def _candidate(identifier: str, basis: str, confidence: str) -> dict[str, str]:
    return {"id": identifier, "basis": basis, "confidence": confidence}


def _extract_features(
    task_analysis: str,
    *,
    tasks: Sequence[Mapping[str, object]],
    solutions: Sequence[Mapping[str, object]],
    classification: Mapping[str, object],
    warning_codes: Sequence[str],
    risk_codes: Sequence[str],
    limits: FeatureLimits,
) -> dict[str, object]:
    if (type(task_analysis) is not str
            or len(task_analysis) > limits.max_chars
            or type(tasks) not in (list, tuple)
            or type(solutions) not in (list, tuple)
            or type(classification) is not dict):
        raise FeatureFault("feature_input_invalid")
    deadline = time.monotonic() + limits.max_seconds
    taxonomy = load_taxonomy()
    lowered = task_analysis.casefold()
    operators = {
        candidate.get("operator_id")
        for task in tasks
        for candidate in task.get("operator_candidates", ())
        if type(candidate) is dict and type(candidate.get("operator_id")) is str
    }
    configured_subjects = set(classification.get("subjects", ()))
    text_signals = _text_signals(lowered, deadline)
    output: dict[str, object] = {
        "taxonomy_version": TAXONOMY_VERSION,
        "status": "unknown",
    }
    rule_hits: dict[str, list[dict[str, str]]] = {}
    for dimension in FEATURE_DIMENSIONS:
        dimension_hits = []
        for identifier, rule in taxonomy["dimensions"][dimension].items():
            _check_time(deadline)
            subjects = set(rule.get("subjects", ()))
            if subjects and configured_subjects and subjects.isdisjoint(
                    configured_subjects):
                continue
            term_hits = _literal_hits(
                lowered, rule.get("terms", ()), deadline
            )
            command_hits = sum(
                1 for command in rule.get("commands", ())
                if command.casefold() in lowered
            )
            operator_hits = len(
                operators.intersection(rule.get("operators", ()))
            )
            detector_hits = len(text_signals.intersection(
                set(rule.get("detectors", ())) - _STRUCTURE_DETECTORS
            ))
            evidence = term_hits + command_hits + operator_hits + detector_hits
            if not evidence:
                continue
            basis = (
                "body_pattern"
                if term_hits or command_hits or detector_hits
                else "operator_derived"
            )
            dimension_hits.append(_candidate(
                identifier, basis, "high" if evidence >= 2 else "medium"
            ))
        rule_hits[dimension] = dimension_hits

    structural = _structural_signals(
        tasks, solutions, len(rule_hits["representations"])
    )
    for dimension in (
        "response_forms", "solution_forms", "progression_profiles",
        "complexity_bands",
    ):
        for identifier, rule in taxonomy["dimensions"][dimension].items():
            if structural.intersection(rule.get("detectors", ())):
                rule_hits[dimension].append(
                    _candidate(identifier, "structure_derived", "high")
                )

    for dimension in FEATURE_DIMENSIONS:
        deduplicated = {}
        for item in sorted(rule_hits[dimension], key=lambda value: value["id"]):
            previous = deduplicated.get(item["id"])
            if previous is None or (
                previous["confidence"] == "medium"
                and item["confidence"] == "high"
            ):
                deduplicated[item["id"]] = item
        output[dimension] = list(deduplicated.values())

    topic_subjects = set()
    for item in output["topic_ids"]:
        topic_subjects.update(
            taxonomy["dimensions"]["topic_ids"][item["id"]].get(
                "subjects", ()
            )
        )
    any_features = any(output[dimension] for dimension in FEATURE_DIMENSIONS)
    if warning_codes or risk_codes:
        output["status"] = "review_required"
    elif len(topic_subjects) > 1 and len(configured_subjects) != 1:
        output["status"] = "ambiguous"
    elif any_features:
        output["status"] = "classified"
    return output


def extract_features(
    task_analysis: str,
    *,
    tasks: Sequence[Mapping[str, object]],
    solutions: Sequence[Mapping[str, object]],
    classification: Mapping[str, object],
    warning_codes: Sequence[str],
    risk_codes: Sequence[str],
    limits: FeatureLimits | None = None,
) -> dict[str, object]:
    """Return only closed feature IDs; every failure is a fixed error code."""
    try:
        return _extract_features(
            task_analysis, tasks=tasks, solutions=solutions,
            classification=classification, warning_codes=warning_codes,
            risk_codes=risk_codes, limits=limits or FeatureLimits(),
        )
    except FeatureFault:
        raise
    except Exception:
        raise FeatureFault("feature_operational_error") from None


def validate_feature_payload(
    payload: object,
    *,
    classification: Mapping[str, object],
    flagged: bool,
) -> None:
    """Validate closed IDs and the status relationship without source text."""
    try:
        expected = {"taxonomy_version", "status", *FEATURE_DIMENSIONS}
        if (type(payload) is not dict or set(payload) != expected
                or payload["taxonomy_version"] != TAXONOMY_VERSION
                or payload["status"] not in FEATURE_STATUSES):
            raise FeatureFault()
        seen_any = False
        topic_subjects = set()
        taxonomy = load_taxonomy()
        for dimension in FEATURE_DIMENSIONS:
            values = payload[dimension]
            if type(values) is not list or len(values) > 64:
                raise FeatureFault()
            identifiers = []
            for item in values:
                if (type(item) is not dict
                        or set(item) != {"id", "basis", "confidence"}
                        or item["id"] not in FEATURE_IDS[dimension]
                        or item["basis"] not in FEATURE_BASES
                        or item["confidence"] not in FEATURE_CONFIDENCES):
                    raise FeatureFault()
                identifiers.append(item["id"])
            if identifiers != sorted(set(identifiers)):
                raise FeatureFault()
            seen_any = seen_any or bool(values)
            if dimension == "topic_ids":
                for identifier in identifiers:
                    topic_subjects.update(
                        taxonomy["dimensions"][dimension][identifier].get(
                            "subjects", ()
                        )
                    )
        configured = set(classification.get("subjects", ()))
        if flagged:
            expected_status = "review_required"
        elif len(topic_subjects) > 1 and len(configured) != 1:
            expected_status = "ambiguous"
        elif seen_any:
            expected_status = "classified"
        else:
            expected_status = "unknown"
        if payload["status"] != expected_status:
            raise FeatureFault()
    except FeatureFault:
        raise
    except Exception:
        raise FeatureFault("feature_invalid") from None
