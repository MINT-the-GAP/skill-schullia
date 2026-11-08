#!/usr/bin/env python3
"""Closed end-to-end acceptance gate for one generated LiaScript candidate."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import time
from types import MappingProxyType
from typing import Mapping, Sequence

import check_local_orientation_leaks as leaks
import local_orientation_config as config
import local_orientation_features as features
import local_orientation_guidance as guidance
from local_orientation_metadata import _validate as _validate_schema, decode_json
import search_local_orientation as local_search
import validate_lia


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "references" / "local-orientation-acceptance.schema.json"
ACCEPTANCE_VERSION = 1
MAX_CANDIDATE_BYTES = 4 * 1024 * 1024
MAX_APPLIED_FEATURES = 16
CASES = MappingProxyType({
    "L1": ("mathematics", "course", 7),
    "L3": ("physics", "course", 8),
})
SCOPES = frozenset({"public_only", "both"})
REVIEW_STATUSES = frozenset({
    "bestanden", "Warnung", "fehlgeschlagen", "blockiert", "unbelegt",
})
ANTI_COPY_STATUSES = frozenset({
    "anti_copy_pass", "anti_copy_risk", "anti_copy_inconclusive",
})
ACCEPTANCE_FILTERS = frozenset({
    "subject", "grade", "operator", "min_subtasks", "min_tasks", "max_tasks",
    "topic_id", "task_family", "learning_action", "response_form",
    "solution_form", "number_profile", "context_profile", "representation",
    "complexity_band",
})
COUNTERCHECKS = tuple(sorted(guidance.COUNTERCHECKS))
BOOLEAN_FIELDS = frozenset({
    "local_search_performed", "orientation_profile_prepared",
    "local_orientation_used", "sources_unchanged", "non_leak_confirmed",
    "no_private_content_output", "no_private_content_versioned",
})


class AcceptanceFault(ValueError):
    """Sanitized failure with no candidate, path, filter value or source data."""

    def __init__(self, code: str = "acceptance_operational_error"):
        self.code = code
        super().__init__(code)


def _freeze(value):
    if type(value) is dict:
        return MappingProxyType({
            key: _freeze(item) for key, item in value.items()
        })
    if type(value) is list:
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value):
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if type(value) is tuple:
        return [_thaw(item) for item in value]
    return value


class AcceptanceWitness:
    """Deep-immutable public projection; never a persisted run record."""

    __slots__ = ("_payload", "_sealed")

    def __init__(self, payload: Mapping[str, object]):
        try:
            snapshot = dict(payload)
            _validate_witness(snapshot)
            object.__setattr__(self, "_payload", _freeze(snapshot))
            object.__setattr__(self, "_sealed", True)
        except AcceptanceFault:
            raise AcceptanceFault() from None
        except Exception:
            raise AcceptanceFault() from None

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("acceptance_witness_immutable")
        object.__setattr__(self, name, value)

    def as_dict(self) -> dict[str, object]:
        value = _thaw(self._payload)
        _validate_witness(value)
        return value

    @property
    def release_allowed(self) -> bool:
        return self._payload["release_status"] == "freigegeben"

    def __repr__(self) -> str:
        return "AcceptanceWitness(<sanitized>)"


def _validate_witness(value: object) -> None:
    try:
        schema = decode_json(SCHEMA_PATH.read_text(encoding="utf-8"))
        _validate_schema(value, schema, schema, [0], time.monotonic() + 2)
        if type(value) is not dict:
            raise AcceptanceFault()
        if any(type(value[key]) is not bool for key in BOOLEAN_FIELDS):
            raise AcceptanceFault()
        for key in (
            "filter_dimensions", "applied_feature_ids",
            "completed_counterchecks",
        ):
            if value[key] != sorted(set(value[key])):
                raise AcceptanceFault()
        if value["subject"] != CASES[value["case_id"]][0]:
            raise AcceptanceFault()
        released = value["release_status"] == "freigegeben"
        pass_reason = value["reason_code"] in {
            "acceptance_pass", "acceptance_public_only_pass",
        }
        if released != pass_reason:
            raise AcceptanceFault()
        if released:
            if (value["anti_copy_status"] != "anti_copy_pass"
                    or value["technical_validator_status"] != "bestanden"
                    or value["subject_review_status"] != "bestanden"
                    or value["evaluator_status"] != "bestanden"
                    or not value["sources_unchanged"]
                    or not value["non_leak_confirmed"]
                    or not value["no_private_content_output"]
                    or not value["no_private_content_versioned"]
                    or tuple(value["completed_counterchecks"]) != COUNTERCHECKS):
                raise AcceptanceFault()
        elif value["local_orientation_used"] or value["applied_feature_ids"]:
            raise AcceptanceFault()
        if value["scope"] == "public_only":
            if (value["availability_state"] != config.STATE_NOT_CONFIGURED
                    or value["local_search_performed"]
                    or value["orientation_profile_prepared"]
                    or value["local_orientation_used"]
                    or value["applied_feature_ids"]):
                raise AcceptanceFault()
            if released and value["reason_code"] != "acceptance_public_only_pass":
                raise AcceptanceFault()
        elif value["scope"] == "both":
            if released and (
                value["availability_state"] != config.STATE_AVAILABLE
                or not value["local_search_performed"]
                or not value["orientation_profile_prepared"]
                or not value["local_orientation_used"]
                or not value["applied_feature_ids"]
                or value["reason_code"] != "acceptance_pass"
            ):
                raise AcceptanceFault()
        else:
            raise AcceptanceFault()
    except AcceptanceFault:
        raise
    except Exception:
        raise AcceptanceFault() from None


def _reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except AttributeError:
        return False
    except OSError:
        return True
    return bool(
        attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _link(path: Path) -> bool:
    try:
        if path.is_symlink() or _reparse(path):
            return True
        junction = getattr(os.path, "isjunction", None)
        return bool(junction and junction(path))
    except OSError:
        return True


def _path_chain_has_link(path: Path) -> bool:
    try:
        absolute = path.absolute()
    except OSError:
        return True
    if not absolute.parts:
        return True
    current = Path(absolute.parts[0])
    for part in absolute.parts[1:]:
        current /= part
        if _link(current):
            return True
    return False


def _file_signature(metadata: os.stat_result):
    if (not stat.S_ISREG(metadata.st_mode) or int(metadata.st_nlink) != 1
            or int(metadata.st_dev) == 0 or int(metadata.st_ino) == 0):
        raise AcceptanceFault("acceptance_input_invalid")
    return (
        int(metadata.st_dev), int(metadata.st_ino), int(metadata.st_nlink),
        int(metadata.st_size), int(metadata.st_mtime_ns),
    )


def _decode_candidate(data: bytes) -> str:
    if len(data) > MAX_CANDIDATE_BYTES or b"\x00" in data:
        raise AcceptanceFault("acceptance_input_invalid")
    try:
        text = data.decode("utf-8-sig")
    except (UnicodeError, AttributeError):
        raise AcceptanceFault("acceptance_input_invalid") from None
    if len(text.encode("utf-8")) > MAX_CANDIDATE_BYTES:
        raise AcceptanceFault("acceptance_input_invalid")
    return text


def _read_candidate_path(path: Path) -> str:
    descriptor = None
    try:
        candidate = Path(path)
        if (candidate.suffix.casefold() not in {".md", ".markdown"}
                or ".schullia-local" in {
                    part.casefold() for part in candidate.parts
                }
                or _path_chain_has_link(candidate) or _link(candidate)):
            raise AcceptanceFault("acceptance_input_invalid")
        before = candidate.lstat()
        signature = _file_signature(before)
        if not 0 <= before.st_size <= MAX_CANDIDATE_BYTES:
            raise AcceptanceFault("acceptance_input_invalid")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        flags |= getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(candidate, flags)
        if _file_signature(os.fstat(descriptor)) != signature:
            raise AcceptanceFault("acceptance_input_invalid")
        chunks: list[bytes] = []
        remaining = MAX_CANDIDATE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        if len(data) > MAX_CANDIDATE_BYTES:
            raise AcceptanceFault("acceptance_input_invalid")
        if _file_signature(os.fstat(descriptor)) != signature:
            raise AcceptanceFault("acceptance_input_invalid")
        after = candidate.lstat()
        if _link(candidate) or _file_signature(after) != signature:
            raise AcceptanceFault("acceptance_input_invalid")
        return _decode_candidate(data)
    except AcceptanceFault:
        raise
    except Exception:
        raise AcceptanceFault("acceptance_input_invalid") from None
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def _candidate_text(*, candidate_text: str | None,
                    candidate_path: Path | None) -> str:
    if (candidate_text is None) == (candidate_path is None):
        raise AcceptanceFault("acceptance_input_invalid")
    if candidate_text is not None:
        if type(candidate_text) is not str:
            raise AcceptanceFault("acceptance_input_invalid")
        return _decode_candidate(candidate_text.encode("utf-8"))
    return _read_candidate_path(candidate_path)


def _validated_filters(value: Mapping[str, object], subject: str,
                       grade: int) -> dict[str, object]:
    try:
        if (type(value) is not dict
                or not 2 <= len(value) <= len(ACCEPTANCE_FILTERS)
                or not set(value).issubset(ACCEPTANCE_FILTERS)
                or value.get("subject") != subject
                or value.get("grade") != grade):
            raise AcceptanceFault("acceptance_input_invalid")
        selected = local_search._validate_filters(dict(value))
        if set(selected) != set(value):
            raise AcceptanceFault("acceptance_input_invalid")
        return selected
    except AcceptanceFault:
        raise
    except Exception:
        raise AcceptanceFault("acceptance_input_invalid") from None


def _validated_applied(value: Sequence[str], *,
                       required: bool) -> tuple[str, ...]:
    try:
        items = tuple(value)
        if (type(value) not in {list, tuple}
                or len(items) > MAX_APPLIED_FEATURES
                or len(items) != len(set(items))
                or (required and not items) or (not required and items)):
            raise AcceptanceFault("acceptance_input_invalid")
        allowed = {
            f"{dimension}:{identifier}"
            for dimension, identifiers in features.FEATURE_IDS.items()
            for identifier in identifiers
        }
        if any(type(item) is not str or item not in allowed for item in items):
            raise AcceptanceFault("acceptance_input_invalid")
        return tuple(sorted(items))
    except AcceptanceFault:
        raise
    except Exception:
        raise AcceptanceFault("acceptance_input_invalid") from None


def _literal_hit(text: str, term: str) -> bool:
    return re.search(
        r"(?<!\w)" + re.escape(term.casefold()) + r"(?!\w)",
        text.casefold(),
        re.UNICODE,
    ) is not None


def _text_detectors(text: str) -> set[str]:
    checks = (
        ("decimal", r"(?<!\w)\d+[,.]\d+(?!\w)"),
        ("fraction", r"\\(?:frac)\b"),
        ("percentage", r"\\%|(?<!\w)prozent(?!\w)"),
        ("scientific", r"(?:10\s*\^\s*(?:\{|\d)|\\(?:cdot)\s*10\b)"),
        ("symbolic", r"\$[^$\r\n]{0,256}[A-Za-z][^$\r\n]{0,256}\$"),
        (
            "unit-bearing",
            r"\\(?:mathrm|unit|si)\b|(?<!\w)"
            r"(?:meter|sekunde|newton|volt|ampere|joule|watt)(?!\w)",
        ),
        ("integer", r"(?<![\w.,])[-+]?\d+(?![\w.,])"),
    )
    return {
        identifier for identifier, pattern in checks
        if re.search(pattern, text, re.IGNORECASE | re.UNICODE)
    }


def _rule_literal_hit(text: str, rule: Mapping[str, object],
                      operators: set[str]) -> bool:
    return bool(
        any(_literal_hit(text, term) for term in rule.get("terms", ()))
        or any(
            command.casefold() in text.casefold()
            for command in rule.get("commands", ())
        )
        or operators.intersection(rule.get("operators", ()))
    )


def _structural_detectors(text: str, representation_count: int) -> set[str]:
    _metadata, _imports, header_end = validate_lia.parse_header(text)
    body = text[header_end:] if header_end else text
    blocks = validate_lia.task_blocks(text)
    task_count = len(blocks) if blocks else int(validate_lia.has_quiz(body))
    subtask_counts = [
        len(validate_lia.PART_LABEL_RE.findall(block))
        for _number, _line, block in blocks
    ]
    if not blocks and task_count:
        subtask_counts = [len(validate_lia.PART_LABEL_RE.findall(body))]
    maximum = max(subtask_counts, default=0)
    output: set[str] = set()
    if task_count:
        output.add("multi-part" if maximum else "single-part")
        has_solution = bool(
            validate_lia.manual_solutions(text)
            or validate_lia.known_template_solution(text)
        )
        output.add("solution-assigned" if has_solution else "solution-none")
    if task_count == 1:
        output.add("progression-single")
    elif 2 <= task_count <= 3:
        output.add("progression-compact")
    elif task_count >= 4:
        output.add("progression-multi-stage")
    if representation_count >= 2:
        output.add("progression-mixed-representation")
    if task_count:
        if maximum >= 4 or (task_count >= 6 and maximum >= 2):
            output.add("structural-high")
        elif maximum >= 2 or task_count >= 4 or representation_count >= 2:
            output.add("structural-medium")
        else:
            output.add("structural-low")
    return output


def _observed_feature_ids(text: str, *, subject: str) -> frozenset[str]:
    taxonomy = features.load_taxonomy()
    operators = validate_lia.detected_operator_ids(text)
    text_signals = _text_detectors(text)
    representation_count = sum(
        _rule_literal_hit(text, rule, operators)
        for rule in taxonomy["dimensions"]["representations"].values()
    )
    structural = _structural_detectors(text, representation_count)
    observed = set()
    for dimension, rules in taxonomy["dimensions"].items():
        for identifier, rule in rules.items():
            subjects = set(rule.get("subjects", ()))
            if subjects and subject not in subjects:
                continue
            detectors = set(rule.get("detectors", ()))
            if (_rule_literal_hit(text, rule, operators)
                    or detectors.intersection(text_signals | structural)):
                observed.add(f"{dimension}:{identifier}")
    return frozenset(observed)


def _perform_anti_copy(
    repo_root: Path,
    *,
    explicit_config: Path | None,
    environ: Mapping[str, str] | None,
    subject: str,
    filters: Mapping[str, object],
    candidate_text: str,
) -> str:
    try:
        import local_orientation_near_copy as near_copy
        session = near_copy.prepare_acceptance_session(
            repo_root,
            explicit_config=explicit_config,
            environ=environ,
            subject=subject,
            filters=filters,
        )
        try:
            result = session.check(candidate_text)
        finally:
            session.close()
        if not isinstance(result, near_copy.NearCopyResult):
            raise AcceptanceFault("acceptance_anti_copy_blocked")
        status = result.status
        if (status not in ANTI_COPY_STATUSES
                or type(result.reason_code) is not str
                or type(result.comparison_performed) is not bool
                or type(result.release_allowed) is not bool
                or result.release_allowed != (status == "anti_copy_pass")
                or not result.comparison_performed):
            raise AcceptanceFault("acceptance_anti_copy_blocked")
        return status
    except AcceptanceFault:
        raise
    except Exception:
        raise AcceptanceFault("acceptance_anti_copy_blocked") from None


def _leak_clean(
    repo_root: Path,
    *,
    explicit_config: Path | None,
    environ: Mapping[str, str] | None,
) -> bool:
    try:
        report = leaks.scan_repository(
            repo_root,
            explicit_config=explicit_config,
            environ=environ,
        )
        return isinstance(report, leaks.GateReport) and report.clean
    except Exception:
        return False


def _payload(
    *,
    case_id: str,
    scope: str,
    subject: str,
    reason_code: str,
    availability_state: str,
    filters: Mapping[str, object],
    technical_status: str,
    subject_review_status: str,
    evaluator_status: str,
    anti_copy_status: str = "anti_copy_inconclusive",
    local_search_performed: bool = False,
    profile_prepared: bool = False,
    used: bool = False,
    applied: Sequence[str] = (),
    counterchecks: Sequence[str] = (),
    sources_unchanged: bool = False,
    non_leak_confirmed: bool = False,
    no_private_content_output: bool = False,
    no_private_content_versioned: bool = False,
    released: bool = False,
) -> AcceptanceWitness:
    return AcceptanceWitness({
        "acceptance_version": ACCEPTANCE_VERSION,
        "usage_context": "orientation-only",
        "case_id": case_id,
        "scope": scope,
        "subject": subject,
        "availability_state": availability_state,
        "release_status": (
            "freigegeben" if released else "nicht_freigegeben"
        ),
        "reason_code": reason_code,
        "filter_dimensions": sorted(filters),
        "local_search_performed": local_search_performed,
        "orientation_profile_prepared": profile_prepared,
        "local_orientation_used": used,
        "applied_feature_ids": sorted(applied) if used else [],
        "completed_counterchecks": sorted(counterchecks),
        "anti_copy_status": anti_copy_status,
        "technical_validator_status": technical_status,
        "subject_review_status": subject_review_status,
        "evaluator_status": evaluator_status,
        "sources_unchanged": sources_unchanged,
        "non_leak_confirmed": non_leak_confirmed,
        "no_private_content_output": no_private_content_output,
        "no_private_content_versioned": no_private_content_versioned,
    })


def run_acceptance(
    repo_root: Path = ROOT,
    *,
    candidate_text: str | None = None,
    candidate_path: Path | None = None,
    case_id: str,
    scope: str,
    filters: Mapping[str, object],
    applied_feature_ids: Sequence[str] = (),
    public_evidence_status: str,
    subject_review_status: str,
    evaluator_status: str,
    sources_unchanged: bool,
    no_private_content_used: bool,
    no_private_content_output: bool,
    no_private_content_versioned: bool,
    explicit_config: Path | None = None,
    environ: Mapping[str, str] | None = None,
    guidance_limit: int = 8,
) -> AcceptanceWitness:
    """Run all machine gates; every in-scope failure is a closed witness."""
    if case_id not in CASES or scope not in SCOPES:
        raise AcceptanceFault("acceptance_input_invalid")
    subject, profile, grade = CASES[case_id]
    if any(status not in REVIEW_STATUSES for status in (
            public_evidence_status, subject_review_status, evaluator_status)):
        raise AcceptanceFault("acceptance_input_invalid")
    if any(type(value) is not bool for value in (
            sources_unchanged, no_private_content_used,
            no_private_content_output, no_private_content_versioned)):
        raise AcceptanceFault("acceptance_input_invalid")
    if (type(guidance_limit) is not int
            or not 1 <= guidance_limit <= guidance.MAX_GUIDANCE_HITS):
        raise AcceptanceFault("acceptance_input_invalid")
    selected = _validated_filters(filters, subject, grade)
    applied = _validated_applied(
        applied_feature_ids, required=scope == "both",
    )
    text = _candidate_text(
        candidate_text=candidate_text, candidate_path=candidate_path,
    )
    technical_status = (
        "bestanden" if not validate_lia.validate(text, profile)
        else "fehlgeschlagen"
    )
    common = dict(
        case_id=case_id,
        scope=scope,
        subject=subject,
        filters=selected,
        technical_status=technical_status,
        subject_review_status=subject_review_status,
        evaluator_status=evaluator_status,
        sources_unchanged=sources_unchanged,
        no_private_content_output=no_private_content_output,
        no_private_content_versioned=no_private_content_versioned,
    )
    initial_state = (
        config.STATE_NOT_CONFIGURED
        if scope == "public_only" else config.STATE_EXCLUDED
    )
    if technical_status != "bestanden":
        return _payload(
            reason_code="acceptance_technical_validation_failed",
            availability_state=initial_state,
            **common,
        )
    if public_evidence_status != "bestanden":
        return _payload(
            reason_code="acceptance_public_evidence_failed",
            availability_state=initial_state,
            **common,
        )
    if subject_review_status != "bestanden":
        return _payload(
            reason_code="acceptance_subject_review_failed",
            availability_state=initial_state,
            **common,
        )
    if evaluator_status != "bestanden":
        return _payload(
            reason_code="acceptance_evaluator_failed",
            availability_state=initial_state,
            **common,
        )
    if not (no_private_content_used and no_private_content_output
            and no_private_content_versioned):
        return _payload(
            reason_code="acceptance_private_content_boundary",
            availability_state=initial_state,
            **common,
        )
    if not sources_unchanged:
        return _payload(
            reason_code="acceptance_sources_changed",
            availability_state=initial_state,
            **common,
        )

    prepared = None
    availability = config.STATE_NOT_CONFIGURED
    searched = profile_prepared = False
    if scope == "both":
        try:
            prepared = guidance.search_orientation_guidance(
                repo_root,
                scope="both",
                explicit_config=explicit_config,
                environ=environ,
                local_filters=selected,
                limit=guidance_limit,
            )
            availability = prepared.availability_state
            searched = prepared.local_search_performed
            profile_prepared = prepared.orientation_profile_prepared
        except Exception:
            prepared = None
        if (not isinstance(prepared, guidance.OrientationGuidance)
                or availability != config.STATE_AVAILABLE
                or not searched or not profile_prepared):
            return _payload(
                reason_code="acceptance_guidance_unavailable",
                availability_state=availability,
                local_search_performed=searched,
                profile_prepared=profile_prepared,
                **common,
            )
        observed = _observed_feature_ids(text, subject=subject)
        if (any(item not in prepared.feature_ids for item in applied)
                or any(item not in observed for item in applied)):
            return _payload(
                reason_code="acceptance_feature_unverified",
                availability_state=availability,
                local_search_performed=True,
                profile_prepared=True,
                **common,
            )

    try:
        anti_copy_status = _perform_anti_copy(
            repo_root,
            explicit_config=explicit_config,
            environ=environ,
            subject=subject,
            filters=selected,
            candidate_text=text,
        )
    except AcceptanceFault:
        anti_copy_status = "anti_copy_inconclusive"
    if anti_copy_status != "anti_copy_pass":
        return _payload(
            reason_code="acceptance_anti_copy_blocked",
            availability_state=availability,
            anti_copy_status=anti_copy_status,
            local_search_performed=searched,
            profile_prepared=profile_prepared,
            **common,
        )

    if not _leak_clean(
        repo_root,
        explicit_config=explicit_config,
        environ=environ,
    ):
        return _payload(
            reason_code="acceptance_leak_blocked",
            availability_state=availability,
            anti_copy_status=anti_copy_status,
            local_search_performed=searched,
            profile_prepared=profile_prepared,
            **common,
        )

    if scope == "public_only":
        return _payload(
            reason_code="acceptance_public_only_pass",
            availability_state=config.STATE_NOT_CONFIGURED,
            anti_copy_status=anti_copy_status,
            counterchecks=COUNTERCHECKS,
            non_leak_confirmed=True,
            released=True,
            **common,
        )

    try:
        recorded = guidance.record_guidance_application(
            prepared,
            applied_feature_ids=applied,
            completed_counterchecks=COUNTERCHECKS,
            non_leak_confirmed=True,
        )
        if (not isinstance(recorded, guidance.OrientationGuidance)
                or not recorded.local_orientation_used):
            raise AcceptanceFault("acceptance_application_rejected")
        projection = recorded.as_dict()
        if (projection["applied_feature_ids"] != list(applied)
                or projection["completed_counterchecks"] != list(COUNTERCHECKS)
                or projection["non_leak_confirmed"] is not True):
            raise AcceptanceFault("acceptance_application_rejected")
    except Exception:
        return _payload(
            reason_code="acceptance_application_rejected",
            availability_state=availability,
            anti_copy_status=anti_copy_status,
            local_search_performed=True,
            profile_prepared=True,
            non_leak_confirmed=True,
            **common,
        )

    return _payload(
        reason_code="acceptance_pass",
        availability_state=availability,
        anti_copy_status=anti_copy_status,
        local_search_performed=True,
        profile_prepared=True,
        used=True,
        applied=applied,
        counterchecks=COUNTERCHECKS,
        non_leak_confirmed=True,
        released=True,
        **common,
    )


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, _message):
        raise AcceptanceFault("acceptance_input_invalid")


def _parser() -> SafeArgumentParser:
    parser = SafeArgumentParser(
        description=(
            "Run the closed L1/L3 LiaScript acceptance gate. "
            "Output never contains paths or candidate content."
        ),
    )
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--case", choices=sorted(CASES), required=True)
    parser.add_argument("--scope", choices=sorted(SCOPES), required=True)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument(
        "--applied-feature-id", action="append", default=[],
    )
    parser.add_argument(
        "--public-evidence-status",
        choices=sorted(REVIEW_STATUSES),
        default="unbelegt",
    )
    parser.add_argument(
        "--subject-review-status",
        choices=sorted(REVIEW_STATUSES),
        default="unbelegt",
    )
    parser.add_argument(
        "--evaluator-status",
        choices=sorted(REVIEW_STATUSES),
        default="unbelegt",
    )
    parser.add_argument("--sources-unchanged", action="store_true")
    parser.add_argument("--no-private-content-used", action="store_true")
    parser.add_argument("--no-private-content-output", action="store_true")
    parser.add_argument("--no-private-content-versioned", action="store_true")
    for name in (
        "operator", "topic_id", "task_family", "learning_action",
        "response_form", "solution_form", "number_profile",
        "context_profile", "representation", "complexity_band",
    ):
        parser.add_argument("--" + name.replace("_", "-"))
    parser.add_argument("--min-subtasks", type=int)
    parser.add_argument("--min-tasks", type=int)
    parser.add_argument("--max-tasks", type=int)
    return parser


def _cli_filters(arguments: argparse.Namespace) -> dict[str, object]:
    subject, _profile, grade = CASES[arguments.case]
    selected: dict[str, object] = {
        "subject": subject,
        "grade": grade,
    }
    for name in (
        "operator", "topic_id", "task_family", "learning_action",
        "response_form", "solution_form", "number_profile",
        "context_profile", "representation", "complexity_band",
        "min_subtasks", "min_tasks", "max_tasks",
    ):
        value = getattr(arguments, name)
        if value is not None:
            selected[name] = value
    return selected


def main(argv: Sequence[str] | None = None) -> int:
    try:
        arguments = _parser().parse_args(argv)
        witness = run_acceptance(
            arguments.repo_root,
            candidate_path=arguments.candidate,
            case_id=arguments.case,
            scope=arguments.scope,
            filters=_cli_filters(arguments),
            applied_feature_ids=arguments.applied_feature_id,
            public_evidence_status=arguments.public_evidence_status,
            subject_review_status=arguments.subject_review_status,
            evaluator_status=arguments.evaluator_status,
            sources_unchanged=arguments.sources_unchanged,
            no_private_content_used=arguments.no_private_content_used,
            no_private_content_output=arguments.no_private_content_output,
            no_private_content_versioned=(
                arguments.no_private_content_versioned
            ),
            environ=os.environ,
        )
        print(json.dumps(
            witness.as_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ))
        return 0 if witness.release_allowed else 1
    except Exception:
        print(json.dumps(
            {
                "release_status": "nicht_freigegeben",
                "reason_code": "acceptance_input_invalid",
            },
            sort_keys=True,
            separators=(",", ":"),
        ))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
