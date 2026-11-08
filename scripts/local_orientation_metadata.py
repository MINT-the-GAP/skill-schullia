#!/usr/bin/env python3
"""Dependency-free validation of the canonical local-only metadata schema."""

from __future__ import annotations

import json
from pathlib import Path
import re
import time
from typing import Any

import local_orientation_features as features

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "references" / "local-orientation-metadata.schema.json"
MAX_DOCUMENT_JSON_BYTES = 4 * 1024 * 1024
MAX_VALIDATION_NODES = 500_000


class MetadataFault(ValueError):
    def __init__(self, code: str = "metadata_invalid"):
        self.code = code
        super().__init__(code)


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise MetadataFault()
        result[key] = value
    return result


def decode_json(value: str | bytes) -> Any:
    """Strict JSON: no duplicate object keys or nonfinite numbers."""
    try:
        return json.loads(value, object_pairs_hook=_unique_pairs,
                          parse_constant=lambda _value: (_ for _ in ()).throw(MetadataFault()))
    except Exception:
        pass
    raise MetadataFault() from None


def _validate(value, node, schema, budget, deadline):
    budget[0] += 1
    if budget[0] > MAX_VALIDATION_NODES or time.monotonic() > deadline:
        raise MetadataFault("metadata_limit_exceeded")
    if "$ref" in node:
        reference = node["$ref"]
        if not isinstance(reference, str) or not reference.startswith("#/$defs/"):
            raise MetadataFault()
        return _validate(value, schema["$defs"][reference[8:]], schema, budget, deadline)
    if "const" in node and (type(value) is not type(node["const"]) or value != node["const"]):
        raise MetadataFault()
    if "enum" in node and not any(type(value) is type(item) and value == item for item in node["enum"]):
        raise MetadataFault()
    kind = node.get("type")
    if kind == "object":
        if type(value) is not dict:
            raise MetadataFault()
        properties = node.get("properties", {})
        if not set(node.get("required", ())).issubset(value):
            raise MetadataFault()
        if node.get("additionalProperties") is False and not set(value).issubset(properties):
            raise MetadataFault()
        for key, item in value.items():
            if key not in properties:
                raise MetadataFault()
            _validate(item, properties[key], schema, budget, deadline)
    elif kind == "array":
        if type(value) is not list or not node.get("minItems", 0) <= len(value) <= node.get("maxItems", MAX_VALIDATION_NODES):
            raise MetadataFault()
        if node.get("uniqueItems"):
            serial = [canonical_json(item) for item in value]
            if len(serial) != len(set(serial)):
                raise MetadataFault()
        for item in value:
            _validate(item, node["items"], schema, budget, deadline)
    elif kind == "string":
        if type(value) is not str or not node.get("minLength", 0) <= len(value) <= node.get("maxLength", MAX_DOCUMENT_JSON_BYTES):
            raise MetadataFault()
        if "pattern" in node and re.fullmatch(node["pattern"], value) is None:
            raise MetadataFault()
    elif kind == "integer":
        if type(value) is not int or not node.get("minimum", -1) <= value <= node.get("maximum", 2**63 - 1):
            raise MetadataFault()


def _relationships(value):
    structure = value["structure"]
    tasks, solutions = value["tasks"], value["solutions"]
    line_count = value["technical"]["line_count"]
    if (structure["heading_count"] != sum(structure["heading_counts"].values())
            or structure["task_count"] != len(tasks)
            or structure["solution_count"] != len(solutions)):
        raise MetadataFault()
    for collection, label in ((tasks, "task"), (solutions, "solution")):
        previous = 0
        for ordinal, entry in enumerate(collection, 1):
            span = entry["line_span"]
            if (entry["ordinal"] != ordinal
                    or entry[f"{label}_id"] != f"{label}-{ordinal:06d}"
                    or not previous <= span["start"] <= span["end"] <= line_count):
                raise MetadataFault()
            previous = span["start"]
    assignments = {task["task_id"]: [] for task in tasks}
    for solution in solutions:
        target = solution.get("task_id")
        if target is None:
            if solution["assignment_status"] != "unassigned":
                raise MetadataFault()
        else:
            if target not in assignments or solution["assignment_status"] != "assigned":
                raise MetadataFault()
            assignments[target].append(solution)
    for task in tasks:
        linked = assignments[task["task_id"]]
        expected = "absent" if not linked else "present" if len(linked) == 1 else "ambiguous"
        assignment = "unassigned" if not linked else "assigned" if len(linked) == 1 else "ambiguous"
        shape = linked[0]["kind"] if len(linked) == 1 else "unknown"
        if (task["solution_presence"] != expected or task["solution_assignment"] != assignment
                or task["solution_shape"] != shape
                or task["response_shape"] != ("multi-part" if task["subtask_count"] else "unknown")
                or task["subtask_count"] > structure["item_count"]):
            raise MetadataFault()
        operators = task["operator_candidates"]
        if len({item["operator_id"] for item in operators}) != len(operators):
            raise MetadataFault()
        if any(not task["line_span"]["start"] <= item["line"] <= task["line_span"]["end"] for item in operators):
            raise MetadataFault()
    flagged = bool(value["warning_codes"] or value["risk_codes"])
    try:
        features.validate_feature_payload(
            value["features"],
            classification=value["classification"],
            flagged=flagged,
        )
    except features.FeatureFault:
        raise MetadataFault() from None
    if (value["technical"]["parse_status"] != ("parsed_with_warnings" if flagged else "parsed")
            or value["suitability"] != ("review_required" if flagged else "structure_only")):
        raise MetadataFault()


def validate_metadata(value: object, *, deadline: float | None = None) -> None:
    """Validate all schema fields and document-local relationship invariants."""
    failure = None
    try:
        encoded = canonical_json(value).encode("utf-8")
        if len(encoded) > MAX_DOCUMENT_JSON_BYTES:
            raise MetadataFault("metadata_limit_exceeded")
        schema = decode_json(SCHEMA_PATH.read_text(encoding="utf-8"))
        _validate(value, schema, schema, [0], deadline or time.monotonic() + 10)
        _relationships(value)
        return
    except MetadataFault as error:
        failure = error.code
    except Exception:
        failure = "metadata_invalid"
    raise MetadataFault(failure) from None
