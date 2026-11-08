#!/usr/bin/env python3
"""Ephemeral multi-document guidance with a closed public-safe projection."""
from __future__ import annotations

import json
from pathlib import Path
import time
from types import MappingProxyType
from typing import Mapping, Sequence

from local_orientation_config import (
    ROOT, STATE_AVAILABLE, STATE_EXCLUDED, STATE_NOT_CONFIGURED,
    STATE_UNREACHABLE,
)
from local_orientation_metadata import (
    MetadataFault, _validate as _validate_schema, decode_json, validate_metadata,
)
from search_local_orientation import (
    LocalHit, LocalSearchResult, SafeArgumentParser, SearchFault, SearchLimits,
    SUPPORTED_FILTERS, filters_from_args,
)

GUIDANCE_VERSION = 1
MIN_DIVERSE_DOCUMENTS = 3
MAX_GUIDANCE_HITS = 16
MAX_OUTPUT_CHARS = 12000
SCHEMA_PATH = ROOT / "references" / "local-orientation-guidance.schema.json"

STATES = frozenset({
    STATE_AVAILABLE, STATE_EXCLUDED, STATE_NOT_CONFIGURED, STATE_UNREACHABLE,
})
REASON_CODES = frozenset({
    "guidance_ready", "guidance_applied", "guidance_not_requested",
    "guidance_local_unavailable", "guidance_search_not_performed",
    "guidance_no_candidates", "guidance_diversity_required",
    "guidance_no_shared_features", "guidance_metadata_invalid",
    "guidance_operational_error",
})
COUNTERCHECKS = frozenset({
    "public_evidence", "subject_review", "technical_validation",
    "no_private_content_used",
})
FILTER_DIMENSIONS = frozenset(SUPPORTED_FILTERS)


class GuidanceFault(ValueError):
    def __init__(self, code: str = "guidance_operational_error"):
        self.code = code if code in REASON_CODES else "guidance_operational_error"
        super().__init__(self.code)


def _taxonomy():
    try:
        from local_orientation_features import FEATURE_DIMENSIONS, FEATURE_IDS
        dimensions = tuple(FEATURE_DIMENSIONS)
        if (not dimensions or len(dimensions) != len(set(dimensions))
                or not isinstance(FEATURE_IDS, Mapping)
                or set(FEATURE_IDS) != set(dimensions)
                or any(type(item) is not str for item in dimensions)
                or any(type(FEATURE_IDS[key]) not in {set, frozenset}
                       or not FEATURE_IDS[key]
                       or any(type(item) is not str for item in FEATURE_IDS[key])
                       for key in dimensions)):
            raise GuidanceFault()
        return dimensions, FEATURE_IDS
    except GuidanceFault:
        raise
    except Exception:
        raise GuidanceFault() from None


def _empty_features():
    dimensions, _ids = _taxonomy()
    return {dimension: () for dimension in dimensions}


def _normalize_filters(value):
    if value is None:
        return ()
    keys = value.keys() if isinstance(value, Mapping) else value
    try:
        selected = tuple(keys)
    except Exception:
        raise GuidanceFault() from None
    if (len(selected) > len(FILTER_DIMENSIONS)
            or any(type(item) is not str or item not in FILTER_DIMENSIONS
                   for item in selected)):
        raise GuidanceFault()
    return tuple(sorted(set(selected)))


def _feature_tokens(features):
    return frozenset(
        f"{dimension}:{feature_id}"
        for dimension, values in features.items() for feature_id in values
    )


class OrientationGuidance:
    __slots__ = (
        "_availability_state", "_reason_code", "_filter_dimensions", "_features",
        "_local_search_performed", "_profile_prepared", "_used",
        "_applied_feature_ids", "_counterchecks", "_non_leak_confirmed",
        "_sealed",
    )

    def __init__(self, *, availability_state=STATE_EXCLUDED,
                 reason_code="guidance_operational_error", filter_dimensions=(),
                 features=None, local_search_performed=False,
                 orientation_profile_prepared=False, local_orientation_used=False,
                 applied_feature_ids=(), completed_counterchecks=(),
                 non_leak_confirmed=False):
        try:
            source = _empty_features() if features is None else features
            dimensions, _ids = _taxonomy()
            feature_snapshot = MappingProxyType({
                dimension: tuple(source.get(dimension, ())) for dimension in dimensions
            })
            object.__setattr__(self, "_availability_state", availability_state)
            object.__setattr__(self, "_reason_code", reason_code)
            object.__setattr__(
                self, "_filter_dimensions", tuple(filter_dimensions)
            )
            object.__setattr__(self, "_features", feature_snapshot)
            object.__setattr__(
                self, "_local_search_performed", local_search_performed
            )
            object.__setattr__(
                self, "_profile_prepared", orientation_profile_prepared
            )
            object.__setattr__(self, "_used", local_orientation_used)
            object.__setattr__(
                self, "_applied_feature_ids", tuple(applied_feature_ids)
            )
            object.__setattr__(
                self, "_counterchecks", tuple(completed_counterchecks)
            )
            object.__setattr__(
                self, "_non_leak_confirmed", non_leak_confirmed
            )
            _validate_projection(self._projection())
            object.__setattr__(self, "_sealed", True)
        except GuidanceFault:
            raise GuidanceFault() from None
        except Exception:
            raise GuidanceFault() from None

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("orientation_guidance_immutable")
        object.__setattr__(self, name, value)

    @property
    def availability_state(self):
        return self._availability_state

    @property
    def reason_code(self):
        return self._reason_code

    @property
    def local_search_performed(self):
        return self._local_search_performed

    @property
    def orientation_profile_prepared(self):
        return self._profile_prepared

    @property
    def local_orientation_used(self):
        return self._used

    @property
    def feature_ids(self):
        return _feature_tokens(self._features)

    def __repr__(self):
        return "OrientationGuidance(<abstract-only>)"

    def _projection(self):
        return {
            "guidance_version": GUIDANCE_VERSION,
            "availability_state": self._availability_state,
            "reason_code": self._reason_code,
            "filter_dimensions": list(self._filter_dimensions),
            "features": {
                dimension: list(values)
                for dimension, values in self._features.items()
            },
            "local_search_performed": self._local_search_performed,
            "orientation_profile_prepared": self._profile_prepared,
            "local_orientation_used": self._used,
            "applied_feature_ids": list(self._applied_feature_ids),
            "completed_counterchecks": list(self._counterchecks),
            "non_leak_confirmed": self._non_leak_confirmed,
            "usage_context": "orientation-only",
        }

    def as_dict(self):
        value = self._projection()
        _validate_projection(value)
        return value


def _validate_projection(value):
    try:
        schema = decode_json(SCHEMA_PATH.read_text(encoding="utf-8"))
        _validate_schema(value, schema, schema, [0], time.monotonic() + 2)
        dimensions, allowed_ids = _taxonomy()
        if tuple(value["features"]) != dimensions:
            raise GuidanceFault()
        for dimension, ids in value["features"].items():
            if ids != sorted(set(ids)) or any(item not in allowed_ids[dimension] for item in ids):
                raise GuidanceFault()
        if value["filter_dimensions"] != sorted(set(value["filter_dimensions"])):
            raise GuidanceFault()
        available = _feature_tokens(value["features"])
        applied = value["applied_feature_ids"]
        if applied != sorted(set(applied)) or any(item not in available for item in applied):
            raise GuidanceFault()
        checks = value["completed_counterchecks"]
        if checks != sorted(set(checks)) or any(item not in COUNTERCHECKS for item in checks):
            raise GuidanceFault()
        feature_present = any(value["features"].values())
        if value["orientation_profile_prepared"] != (
                value["local_search_performed"]
                and value["availability_state"] == STATE_AVAILABLE
                and feature_present):
            raise GuidanceFault()
        if value["local_orientation_used"]:
            if (not value["orientation_profile_prepared"] or not applied
                    or set(checks) != COUNTERCHECKS
                    or value["non_leak_confirmed"] is not True
                    or value["reason_code"] != "guidance_applied"):
                raise GuidanceFault()
        elif applied or checks or value["non_leak_confirmed"]:
            raise GuidanceFault()
        if value["reason_code"] not in REASON_CODES or value["availability_state"] not in STATES:
            raise GuidanceFault()
        reason = value["reason_code"]
        inactive = (
            not value["orientation_profile_prepared"]
            and not value["local_orientation_used"]
            and not feature_present
        )
        if reason == "guidance_ready":
            if (value["availability_state"] != STATE_AVAILABLE
                    or not value["local_search_performed"]
                    or not value["orientation_profile_prepared"]
                    or value["local_orientation_used"]):
                raise GuidanceFault()
        elif reason == "guidance_applied":
            if (value["availability_state"] != STATE_AVAILABLE
                    or not value["local_search_performed"]
                    or not value["orientation_profile_prepared"]
                    or not value["local_orientation_used"]):
                raise GuidanceFault()
        elif reason == "guidance_not_requested":
            if (value["availability_state"] != STATE_NOT_CONFIGURED
                    or value["local_search_performed"] or not inactive):
                raise GuidanceFault()
        elif reason == "guidance_local_unavailable":
            if (value["availability_state"] == STATE_AVAILABLE
                    or value["local_search_performed"] or not inactive):
                raise GuidanceFault()
        elif reason == "guidance_search_not_performed":
            if (value["availability_state"] != STATE_AVAILABLE
                    or value["local_search_performed"] or not inactive):
                raise GuidanceFault()
        elif reason in {
            "guidance_no_candidates", "guidance_diversity_required",
            "guidance_no_shared_features", "guidance_metadata_invalid",
        }:
            if (value["availability_state"] != STATE_AVAILABLE
                    or not value["local_search_performed"] or not inactive):
                raise GuidanceFault()
        elif reason == "guidance_operational_error":
            if not inactive:
                raise GuidanceFault()
        else:
            raise GuidanceFault()
    except GuidanceFault:
        raise
    except Exception:
        raise GuidanceFault() from None


def _result(reason, *, local=None, filters=(), features=None, prepared=False):
    state = local.availability_state if isinstance(local, LocalSearchResult) else STATE_EXCLUDED
    performed = bool(isinstance(local, LocalSearchResult) and local.local_search_performed)
    return OrientationGuidance(
        availability_state=state, reason_code=reason,
        filter_dimensions=filters, features=features,
        local_search_performed=performed,
        orientation_profile_prepared=prepared,
    )


def prepare_orientation_guidance(search_result, *, requested_filter_dimensions=()):
    """Aggregate only closed features supported by independent include families."""
    filters = ()
    local = None
    try:
        filters = _normalize_filters(requested_filter_dimensions)
        candidate = getattr(search_result, "local", search_result)
        if not isinstance(candidate, LocalSearchResult):
            raise GuidanceFault()
        local = candidate
        if local.availability_state != STATE_AVAILABLE:
            return _result("guidance_local_unavailable", local=local, filters=filters)
        if not local.local_search_performed:
            return _result("guidance_search_not_performed", local=local, filters=filters)
        if not local.hits:
            return _result("guidance_no_candidates", local=local, filters=filters)
        if len(local.hits) > MAX_GUIDANCE_HITS:
            raise GuidanceFault()

        dimensions, allowed_ids = _taxonomy()
        unique = {}
        for hit in local.hits:
            if not isinstance(hit, LocalHit):
                return _result("guidance_metadata_invalid", local=local, filters=filters)
            document = hit.metadata
            try:
                validate_metadata(document)
            except MetadataFault:
                return _result("guidance_metadata_invalid", local=local, filters=filters)
            digest = document["local_provenance"]["integrity_sha256"]
            family = hit.family_key
            if not isinstance(family, tuple) or not family:
                return _result("guidance_metadata_invalid", local=local, filters=filters)
            current = unique.get(digest)
            marker = repr(family)
            if current is None or marker < current[0]:
                unique[digest] = (marker, family, document)

        documents = tuple(unique[key][1:] for key in sorted(unique))
        if (len(documents) < MIN_DIVERSE_DOCUMENTS
                or len({item[0] for item in documents}) < MIN_DIVERSE_DOCUMENTS):
            return _result("guidance_diversity_required", local=local, filters=filters)

        support = {
            dimension: {
                feature_id: (set(), set()) for feature_id in allowed_ids[dimension]
            } for dimension in dimensions
        }
        for family, document in documents:
            features = document.get("features")
            if type(features) is not dict or features.get("status") != "classified":
                continue
            digest = document["local_provenance"]["integrity_sha256"]
            if document["suitability"] != "structure_only":
                continue
            for dimension in dimensions:
                for item in features.get(dimension, ()):
                    feature_id = item.get("id") if type(item) is dict else None
                    if (feature_id in allowed_ids[dimension]
                            and item.get("confidence") in {"medium", "high"}):
                        support[dimension][feature_id][0].add(family)
                        support[dimension][feature_id][1].add(digest)

        selected = {
            dimension: tuple(sorted(
                feature_id for feature_id, (families, digests)
                in support[dimension].items()
                if len(families) >= MIN_DIVERSE_DOCUMENTS
                and len(digests) >= MIN_DIVERSE_DOCUMENTS
            )) for dimension in dimensions
        }
        if not any(selected.values()):
            return _result("guidance_no_shared_features", local=local, filters=filters)
        return _result("guidance_ready", local=local, filters=filters,
                       features=selected, prepared=True)
    except GuidanceFault:
        return _result("guidance_operational_error", local=local, filters=filters)
    except Exception:
        return _result("guidance_operational_error", local=local, filters=filters)


def record_guidance_application(guidance, *, applied_feature_ids,
                                completed_counterchecks, non_leak_confirmed):
    """Record an explicit caller attestation; real behavioral proof is external."""
    try:
        if not isinstance(guidance, OrientationGuidance) or not guidance.orientation_profile_prepared:
            raise GuidanceFault()
        applied = tuple(sorted(set(applied_feature_ids)))
        checks = tuple(sorted(set(completed_counterchecks)))
        if (not applied or any(type(item) is not str or item not in guidance.feature_ids
                               for item in applied)
                or set(checks) != COUNTERCHECKS
                or non_leak_confirmed is not True):
            raise GuidanceFault()
        return OrientationGuidance(
            availability_state=guidance._availability_state,
            reason_code="guidance_applied",
            filter_dimensions=guidance._filter_dimensions,
            features=guidance._features,
            local_search_performed=True,
            orientation_profile_prepared=True,
            local_orientation_used=True,
            applied_feature_ids=applied,
            completed_counterchecks=checks,
            non_leak_confirmed=True,
        )
    except GuidanceFault:
        raise GuidanceFault() from None
    except Exception:
        raise GuidanceFault() from None


def search_orientation_guidance(repo_root: Path = ROOT, *, scope,
                                explicit_config: Path | None = None,
                                environ: Mapping[str, str] | None = None,
                                local_filters=None, limit=8,
                                limits: SearchLimits | None = None):
    """Run an explicitly scoped search and prepare an ephemeral safe brief."""
    if not isinstance(scope, str) or scope not in {"local", "both"}:
        return OrientationGuidance(
            availability_state=STATE_NOT_CONFIGURED,
            reason_code="guidance_not_requested",
        )
    try:
        from search_with_local_orientation import search_with_local_orientation
        result = search_with_local_orientation(
            repo_root, scope=scope, explicit_config=explicit_config,
            environ=environ, local_filters=local_filters, limit=limit,
            limits=limits,
        )
        return prepare_orientation_guidance(
            result, requested_filter_dimensions=local_filters or ())
    except Exception:
        return OrientationGuidance(reason_code="guidance_operational_error")


def parse_args(argv: Sequence[str] | None = None):
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("local", "both"), required=True)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path)
    for key in (
        "subject", "learner-group", "document-type", "operator",
        "solution-presence", "solution-assignment", "response-shape",
        "suitability", "topic-id", "task-family", "learning-action",
        "response-form", "solution-form", "number-profile", "context-profile",
        "representation", "complexity-band",
    ):
        parser.add_argument("--" + key, dest=key.replace("-", "_"))
    for key in ("grade", "min-subtasks", "min-tasks", "max-tasks", "modified-after-ns"):
        parser.add_argument("--" + key, type=int, dest=key.replace("-", "_"))
    parser.add_argument("--has-warnings", choices=("yes", "no"), dest="has_warnings")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None):
    try:
        args = parse_args(argv)
        guidance = search_orientation_guidance(
            args.repo_root, scope=args.scope, explicit_config=args.config,
            local_filters=filters_from_args(args), limit=args.limit)
    except (GuidanceFault, SearchFault):
        guidance = OrientationGuidance(reason_code="guidance_operational_error")
    except Exception:
        guidance = OrientationGuidance(reason_code="guidance_operational_error")
    output = json.dumps(guidance.as_dict(), ensure_ascii=True, sort_keys=True)
    if len(output) > MAX_OUTPUT_CHARS:
        guidance = OrientationGuidance(reason_code="guidance_operational_error")
        output = json.dumps(guidance.as_dict(), ensure_ascii=True, sort_keys=True)
    print(output)
    return 0 if (guidance.orientation_profile_prepared
                 or guidance.availability_state == STATE_NOT_CONFIGURED) else 1


if __name__ == "__main__":
    raise SystemExit(main())
