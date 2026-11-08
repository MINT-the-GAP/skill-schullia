#!/usr/bin/env python3
"""Bounded structured local search; the console projection contains no hits."""
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Sequence

from local_orientation_config import ROOT, STATE_AVAILABLE, STATE_EXCLUDED, STATE_NOT_CONFIGURED, STATE_UNREACHABLE
from local_orientation_metadata import MetadataFault, validate_metadata

OPERATORS = frozenset({
    "angeben", "auffuellen", "auswaehlen", "begr\u00fcnden", "berechnen",
    "beschreiben", "bestimmen", "beurteilen", "bewerten", "darstellen",
    "entscheiden", "ergaenzen", "erklaeren", "ermitteln", "erstellen",
    "formulieren", "interpretieren", "konstruieren", "loesen", "markieren",
    "nennen", "pruefen", "skizzieren", "untersuchen", "vergleichen",
    "zeigen", "zeichnen", "zuordnen",
})
STATES = frozenset({STATE_AVAILABLE, STATE_EXCLUDED, STATE_NOT_CONFIGURED, STATE_UNREACHABLE})
SUPPORTED_FILTERS = frozenset({
    "subject", "grade", "learner_group", "document_type", "operator",
    "solution_presence", "solution_assignment", "response_shape", "suitability",
    "has_warnings", "min_subtasks", "min_tasks", "max_tasks", "modified_after_ns",
    "topic_id", "task_family", "learning_action", "response_form", "solution_form",
    "number_profile", "context_profile", "representation", "complexity_band",
})
FEATURE_FILTER_MAP = {
    "topic_id": "topic_ids",
    "task_family": "task_families",
    "learning_action": "learning_actions",
    "response_form": "response_forms",
    "solution_form": "solution_forms",
    "number_profile": "number_profiles",
    "context_profile": "context_profiles",
    "representation": "representations",
    "complexity_band": "complexity_bands",
}
UNSUPPORTED_FILTERS = frozenset({"query", "topic", "archive_status"})
_SEARCH_FAILURE_REASONS = frozenset({
    "arguments_invalid", "feature_taxonomy_invalid",
    "search_filter_invalid", "search_filter_unknown",
    "search_filter_unsupported", "search_filters_invalid",
    "search_limits_invalid", "search_metadata_invalid",
    "search_operational_error", "search_result_limit_invalid",
    "search_scan_limit", "search_time_limit",
})
_PRESERVED_INDEX_REASONS = MappingProxyType({
    "configuration_absent": STATE_NOT_CONFIGURED,
    "configuration_disabled": STATE_NOT_CONFIGURED,
    "configuration_unreachable": STATE_UNREACHABLE,
    "index_missing": STATE_UNREACHABLE,
    "index_stale": STATE_EXCLUDED,
    "index_version_unsupported": STATE_EXCLUDED,
    "index_configuration_changed": STATE_EXCLUDED,
})
_LOCAL_SEARCH_RESULT_RULES = MappingProxyType({
    "search_complete": (STATE_AVAILABLE, True, True),
    "local_not_requested": (STATE_NOT_CONFIGURED, False, False),
    "configuration_not_active": (STATE_NOT_CONFIGURED, False, False),
    "index_unreachable": (STATE_UNREACHABLE, False, False),
    "index_excluded": (STATE_EXCLUDED, False, False),
    **{
        code: (state, False, False)
        for code, state in _PRESERVED_INDEX_REASONS.items()
    },
    **{
        code: (STATE_EXCLUDED, False, False)
        for code in _SEARCH_FAILURE_REASONS
    },
})


class SearchFault(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _project_index_reason(code, state):
    expected = _PRESERVED_INDEX_REASONS.get(code)
    if expected == state:
        return code
    if state == STATE_NOT_CONFIGURED:
        return "configuration_not_active"
    if state == STATE_UNREACHABLE:
        return "index_unreachable"
    return "index_excluded"


@dataclass(frozen=True)
class SearchLimits:
    max_results: int = 16
    max_documents: int = 512
    max_tasks: int = 25000
    max_seconds: float = 30.0
    max_output_chars: int = 12000

    def __post_init__(self) -> None:
        for value, maximum in ((self.max_results, 16), (self.max_documents, 512),
                               (self.max_tasks, 25000), (self.max_output_chars, 12000)):
            if type(value) is not int or not 1 <= value <= maximum:
                raise SearchFault("search_limits_invalid")
        if self.max_output_chars < 1024:
            raise SearchFault("search_limits_invalid")
        if type(self.max_seconds) not in (int, float) or not 0 < self.max_seconds <= 30:
            raise SearchFault("search_limits_invalid")


def _freeze_local_value(value):
    if type(value) is dict:
        return MappingProxyType({
            key: _freeze_local_value(item) for key, item in value.items()
        })
    if type(value) in (list, tuple):
        return tuple(_freeze_local_value(item) for item in value)
    if value is None or type(value) in (str, int, bool, float):
        return value
    raise SearchFault("search_metadata_invalid")


def _thaw_local_value(value):
    if isinstance(value, Mapping):
        return {key: _thaw_local_value(item) for key, item in value.items()}
    if type(value) is tuple:
        return [_thaw_local_value(item) for item in value]
    return value


class LocalHit:
    """Deep-immutable local snapshot without a generic serialization path."""
    __slots__ = (
        "_metadata", "_rank", "_ranking_basis", "_family_key", "_sealed",
    )

    def __init__(self, metadata, rank, ranking_basis, family_key=None):
        try:
            validate_metadata(metadata)
            rank_value = tuple(rank)
            basis_value = tuple(ranking_basis)
            family_value = family_key if family_key is not None else (
                metadata.get("source_id"), metadata.get("document_id"))
            if (type(family_value) is not tuple or not family_value
                    or any(type(item) is not str or not 1 <= len(item) <= 160
                           for item in family_value)
                    or any(type(item) not in (int, str) for item in rank_value)
                    or any(type(item) is not str for item in basis_value)):
                raise SearchFault("search_metadata_invalid")
            object.__setattr__(self, "_metadata", _freeze_local_value(metadata))
            object.__setattr__(self, "_rank", rank_value)
            object.__setattr__(self, "_ranking_basis", basis_value)
            object.__setattr__(self, "_family_key", tuple(family_value))
            object.__setattr__(self, "_sealed", True)
        except (MetadataFault, SearchFault):
            raise SearchFault("search_metadata_invalid") from None
        except Exception:
            raise SearchFault("search_metadata_invalid") from None

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("local_hit_immutable")
        object.__setattr__(self, name, value)

    @property
    def metadata(self):
        return _thaw_local_value(self._metadata)

    @property
    def rank(self):
        return self._rank

    @property
    def ranking_basis(self):
        return self._ranking_basis

    @property
    def family_key(self):
        return self._family_key

    @property
    def usage_context(self):
        return "orientation-only"

    def __repr__(self):
        return "LocalHit(<local-only>)"


class LocalSearchResult:
    __slots__ = (
        "_hits", "_availability_state", "_reason_code", "_index_ready",
        "_local_search_performed", "_sealed",
    )

    def __init__(self, hits=(), *, availability_state=STATE_EXCLUDED,
                 reason_code="search_operational_error", index_ready=False,
                 local_search_performed=False):
        try:
            hit_values = tuple(hits)
            rule = _LOCAL_SEARCH_RESULT_RULES.get(reason_code)
            if (any(not isinstance(hit, LocalHit) for hit in hit_values)
                    or rule is None
                    or type(index_ready) is not bool
                    or type(local_search_performed) is not bool
                    or (availability_state, index_ready,
                        local_search_performed) != rule
                    or (not local_search_performed and hit_values)):
                raise SearchFault("search_result_invalid")
            object.__setattr__(self, "_hits", hit_values)
            object.__setattr__(self, "_availability_state", availability_state)
            object.__setattr__(self, "_reason_code", reason_code)
            object.__setattr__(self, "_index_ready", index_ready)
            object.__setattr__(
                self, "_local_search_performed", local_search_performed
            )
            object.__setattr__(self, "_sealed", True)
        except SearchFault:
            raise
        except Exception:
            raise SearchFault("search_result_invalid") from None

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("local_search_result_immutable")
        object.__setattr__(self, name, value)

    @property
    def hits(self):
        return self._hits

    @property
    def availability_state(self):
        return self._availability_state

    @property
    def reason_code(self):
        return self._reason_code

    @property
    def index_ready(self):
        return self._index_ready

    @property
    def local_search_performed(self):
        return self._local_search_performed

    @property
    def local_orientation_used(self):
        return False

    def __repr__(self):
        return "LocalSearchResult(<local-only>)"

    def as_dict(self):
        return {
            "availability_state": self.availability_state,
            "reason_code": self.reason_code,
            "index_ready": self.index_ready,
            "local_search_performed": self.local_search_performed,
            "orientation_profile_prepared": False,
            "local_orientation_used": False,
            "usage_context": "orientation-only",
        }


def _feature_ids():
    try:
        from local_orientation_features import FEATURE_IDS
        expected = set(FEATURE_FILTER_MAP.values())
        if (not isinstance(FEATURE_IDS, Mapping) or not expected.issubset(FEATURE_IDS)
                or any(type(FEATURE_IDS[key]) not in {set, frozenset}
                       or not FEATURE_IDS[key]
                       or any(type(item) is not str for item in FEATURE_IDS[key])
                       for key in expected)):
            raise SearchFault("feature_taxonomy_invalid")
        return FEATURE_IDS
    except SearchFault:
        raise
    except Exception:
        raise SearchFault("feature_taxonomy_invalid") from None


def _document_feature_ids(document, dimension):
    values = document.get("features", {}).get(dimension, ())
    return frozenset(item["id"] for item in values
                     if type(item) is dict and type(item.get("id")) is str)


def _include_families(documents, edges):
    """Return opaque connected-component keys for the local include graph."""
    keys = {(item["source_id"], item["document_id"]) for item in documents}
    parent = {key: key for key in keys}

    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    def union(left, right):
        left, right = find(left), find(right)
        if left != right:
            parent[max(left, right)] = min(left, right)

    for source_id, parent_id, child_id in edges:
        left, right = (source_id, parent_id), (source_id, child_id)
        if left in keys and right in keys:
            union(left, right)
    return {key: find(key) for key in keys}


def _validate_filters(filters):
    if filters is None:
        return {}
    if not isinstance(filters, dict) or any(not isinstance(key, str) for key in filters):
        raise SearchFault("search_filters_invalid")
    if set(filters) & UNSUPPORTED_FILTERS:
        raise SearchFault("search_filter_unsupported")
    if set(filters) - SUPPORTED_FILTERS:
        raise SearchFault("search_filter_unknown")
    result = dict(filters)
    feature_ids = _feature_ids() if set(result) & set(FEATURE_FILTER_MAP) else {}
    enums = {
        "subject": {"mathematics", "physics"}, "operator": OPERATORS,
        "solution_presence": {"absent", "present", "ambiguous"},
        "solution_assignment": {"assigned", "unassigned", "ambiguous"},
        "response_shape": {"unknown", "multi-part"},
        "suitability": {"structure_only", "review_required"},
    }
    for key, values in enums.items():
        if key in result and (not isinstance(result[key], str) or result[key] not in values):
            raise SearchFault("search_filter_invalid")
    for key, dimension in FEATURE_FILTER_MAP.items():
        if key in result and (type(result[key]) is not str
                              or result[key] not in feature_ids[dimension]):
            raise SearchFault("search_filter_invalid")
    for key in ("learner_group", "document_type"):
        if key in result:
            value = result[key]
            if (not isinstance(value, str) or not 1 <= len(value) <= 80
                    or any(ord(c) < 32 or ord(c) in {127, 133, 8232, 8233} for c in value)):
                raise SearchFault("search_filter_invalid")
    for key, (minimum, maximum) in {
        "grade": (5, 13), "min_subtasks": (0, 25000), "min_tasks": (0, 5000),
        "max_tasks": (0, 5000), "modified_after_ns": (0, 2**63 - 1),
    }.items():
        if key in result and (type(result[key]) is not int or not minimum <= result[key] <= maximum):
            raise SearchFault("search_filter_invalid")
    if "has_warnings" in result and type(result["has_warnings"]) is not bool:
        raise SearchFault("search_filter_invalid")
    if result.get("min_tasks", 0) > result.get("max_tasks", 5000):
        raise SearchFault("search_filter_invalid")
    return result


def _matching_tasks(document, filters, deadline, task_budget):
    matches = []
    for task in document["tasks"]:
        task_budget[0] -= 1
        if task_budget[0] < 0:
            raise SearchFault("search_scan_limit")
        if time.monotonic() > deadline:
            raise SearchFault("search_time_limit")
        if "operator" in filters and not any(
                item["operator_id"] == filters["operator"] for item in task["operator_candidates"]):
            continue
        if any(key in filters and task[key] != filters[key]
               for key in ("solution_presence", "solution_assignment", "response_shape")):
            continue
        if task["subtask_count"] < filters.get("min_subtasks", 0):
            continue
        matches.append(task)
    return matches


def _rank(document, tasks, filters):
    classification = document["classification"]
    exact_subject = int("subject" in filters and len(classification["subjects"]) == 1)
    exact_grade = int("grade" in filters and len(classification["grades"]) == 1)
    precise_operator = int("operator" in filters and any(
        len(task["operator_candidates"]) == 1
        and task["operator_candidates"][0]["conflict_status"] == "none" for task in tasks))
    solution_quality = max((2 if task["solution_assignment"] == "assigned" else
                            0 if task["solution_assignment"] == "ambiguous" else 1
                            for task in tasks), default=0)
    confidence = {"high": 2, "medium": 1}
    feature_precision = sum(max((confidence.get(item.get("confidence"), 0)
                                 for item in document.get("features", {}).get(dimension, ())
                                 if item.get("id") == filters.get(key)), default=0)
                            for key, dimension in FEATURE_FILTER_MAP.items() if key in filters)
    rank = (-exact_subject, -exact_grade, -precise_operator, -solution_quality,
            -int(document["suitability"] == "structure_only"),
            len(document["risk_codes"]), len(document["warning_codes"]),
            -feature_precision,
            -document["local_provenance"]["modified_ns"], document["source_id"], document["document_id"])
    basis = ("configured_subject_grade", "operator_precision",
             "solution_assignment", "suitability_risks", "parser_warnings",
             "feature_filter_match", "technical_mtime_only",
             "stable_local_identity")
    return rank, basis


def search_local_orientation(repo_root: Path = ROOT, *, explicit_config: Path | None = None,
                             environ: Mapping[str, str] | None = None, filters=None,
                             limit=8, limits: SearchLimits | None = None) -> LocalSearchResult:
    """Freshly validate then search; no writes, rebuilds, raw text or public hits."""
    try:
        bounds = limits or SearchLimits()
        if not isinstance(bounds, SearchLimits):
            raise SearchFault("search_limits_invalid")
        if type(limit) is not int or not 1 <= limit <= bounds.max_results:
            raise SearchFault("search_result_limit_invalid")
        selected = _validate_filters(filters)
        deadline = time.monotonic() + bounds.max_seconds
        from local_orientation_index import IndexFault, IndexLimits, load_valid_index
        try:
            snapshot = load_valid_index(
                repo_root, explicit_config=explicit_config, environ=environ,
                limits=IndexLimits(max_documents=bounds.max_documents, max_seconds=bounds.max_seconds))
        except IndexFault as fault:
            state = fault.state if fault.state in STATES else STATE_EXCLUDED
            code = _project_index_reason(fault.code, state)
            return LocalSearchResult(
                availability_state=state, reason_code=code
            )
        if time.monotonic() > deadline:
            raise SearchFault("search_time_limit")
        if len(snapshot.documents) > bounds.max_documents:
            raise SearchFault("search_scan_limit")
        families = _include_families(snapshot.documents, snapshot.edges)
        task_budget, hits = [bounds.max_tasks], []
        for document in snapshot.documents:
            if time.monotonic() > deadline:
                raise SearchFault("search_time_limit")
            try:
                validate_metadata(document, deadline=deadline)
            except MetadataFault:
                raise SearchFault("search_metadata_invalid") from None
            classification = document["classification"]
            if any(key in selected and selected[key] not in classification[field]
                   for key, field in (("subject", "subjects"), ("grade", "grades"),
                                      ("learner_group", "learner_groups"), ("document_type", "document_types"))):
                continue
            if "suitability" in selected and document["suitability"] != selected["suitability"]:
                continue
            if "has_warnings" in selected and bool(document["warning_codes"]) != selected["has_warnings"]:
                continue
            if not selected.get("min_tasks", 0) <= document["structure"]["task_count"] <= selected.get("max_tasks", 5000):
                continue
            if document["local_provenance"]["modified_ns"] < selected.get("modified_after_ns", 0):
                continue
            if any(selected[key] not in _document_feature_ids(document, dimension)
                   for key, dimension in FEATURE_FILTER_MAP.items() if key in selected):
                continue
            tasks = _matching_tasks(document, selected, deadline, task_budget)
            if tasks:
                rank, basis = _rank(document, tasks, selected)
                key = (document["source_id"], document["document_id"])
                hits.append(LocalHit(document, rank, basis, families[key]))
        hits.sort(key=lambda hit: hit.rank)
        return LocalSearchResult(tuple(hits[:limit]), availability_state=STATE_AVAILABLE,
                                 reason_code="search_complete", index_ready=True, local_search_performed=True)
    except SearchFault as fault:
        return LocalSearchResult(reason_code=fault.code)
    except Exception:
        return LocalSearchResult(reason_code="search_operational_error")


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise SearchFault("arguments_invalid")


def parse_args(argv: Sequence[str] | None = None):
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path)
    for key in ("subject", "learner-group", "document-type", "operator", "solution-presence",
                "solution-assignment", "response-shape", "suitability", "topic", "query", "archive-status",
                "topic-id", "task-family", "learning-action", "response-form", "solution-form",
                "number-profile", "context-profile", "representation", "complexity-band"):
        parser.add_argument("--" + key)
    for key in ("grade", "min-subtasks", "min-tasks", "max-tasks", "modified-after-ns"):
        parser.add_argument("--" + key, type=int)
    parser.add_argument("--has-warnings", choices=("yes", "no"))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def filters_from_args(args):
    filters = {key: getattr(args, key) for key in SUPPORTED_FILTERS | UNSUPPORTED_FILTERS
               if hasattr(args, key) and getattr(args, key) is not None}
    if "has_warnings" in filters:
        filters["has_warnings"] = filters["has_warnings"] == "yes"
    return filters


def main(argv: Sequence[str] | None = None):
    try:
        args = parse_args(argv)
        result = search_local_orientation(args.repo_root, explicit_config=args.config,
                                          filters=filters_from_args(args), limit=args.limit)
    except SearchFault:
        result = LocalSearchResult(reason_code="arguments_invalid")
    except Exception:
        result = LocalSearchResult(reason_code="search_operational_error")
    print(json.dumps(result.as_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.local_search_performed or result.availability_state == STATE_NOT_CONFIGURED else 1


if __name__ == "__main__":
    raise SystemExit(main())
