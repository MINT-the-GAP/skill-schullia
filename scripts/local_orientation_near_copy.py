#!/usr/bin/env python3
"""Closed, acceptance-only near-copy gate for optional local orientation.

Private source text is read only through selector-attested candidates. It is
normalized and compared in memory, never returned, logged, or persisted. The
module intentionally has no candidate-file CLI: callers get only a closed
result from a bounded per-acceptance session.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
import json
from pathlib import Path
import re
import time
from types import MappingProxyType
from typing import Mapping, Sequence
import unicodedata

import local_orientation_candidates as selector
import local_orientation_config as config
import local_orientation_includes as includes
import local_orientation_tex as tex
import search_local_orientation as search


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "references" / "local-orientation-near-copy-policy.json"
POLICY_VERSION = 1
STATUSES = frozenset({
    "anti_copy_pass", "anti_copy_risk", "anti_copy_inconclusive",
})
PASS_REASONS = frozenset({"near_copy_no_risk_detected"})
RISK_REASONS = frozenset({
    "near_copy_normalized_risk",
    "near_copy_long_passage_risk",
    "near_copy_paraphrase_risk",
    "near_copy_composition_risk",
})
INCONCLUSIVE_REASONS = frozenset({
    "near_copy_attempt_limit",
    "near_copy_candidate_invalid",
    "near_copy_candidate_too_short",
    "near_copy_filter_invalid",
    "near_copy_no_comparison_basis",
    "near_copy_private_dynamic_construct",
    "near_copy_private_unavailable",
    "near_copy_session_closed",
    "near_copy_time_limit",
    "near_copy_policy_invalid",
    "near_copy_operational_error",
})
REASON_CODES = PASS_REASONS | RISK_REASONS | INCONCLUSIVE_REASONS

_TOKEN_RE = re.compile(r"\d+(?:[.,]\d+)?|[^\W\d_]+", re.UNICODE)
_NUMBER_RE = re.compile(r"(?<!\w)[+-]?\d+(?:[.,]\d+)?(?:\s*\\?%)?")
_MATH_RE = re.compile(
    r"\$[^$\r\n]{1,2048}\$|\\\([^\r\n]{1,2048}\\\)|"
    r"\\\[[\s\S]{1,2048}?\\\]"
)
_HTML_COMMENT_RE = re.compile(r"<!--[\s\S]*?-->")
_TEX_COMMAND_RE = re.compile(r"\\(?:[A-Za-z@]+|.)")
_MARKUP_RE = re.compile(r"[#*_~`>|{}\[\]()]")
_TEX_SLASH = re.escape(chr(92))
_TASK_MARKER_RE = re.compile(
    _TEX_SLASH + r"begin\s*\{\s*(?:aufgabe|exercise|problem|question|task)\s*\}"
    r"|^#{1,6}\s+[^\r\n]*(?:aufgabe|exercise|problem|task)[^\r\n]*$",
    re.IGNORECASE | re.MULTILINE,
)
_SOLUTION_MARKER_RE = re.compile(
    _TEX_SLASH + r"begin\s*\{\s*(?:loesung|losung|solution|answer|antwort)\s*\}"
    r"|^#{1,6}\s+[^\r\n]*(?:musterlosung|musterloesung|"
    r"losung|loesung|solution|answer)[^\r\n]*$",
    re.IGNORECASE | re.MULTILINE,
)
_ITEM_MARKER_RE = re.compile(
    _TEX_SLASH + r"item\b|^[ \t]*(?:[-+*]|\d+[.)]|[a-zA-Z][.)])[ \t]+",
    re.IGNORECASE | re.MULTILINE,
)
_HEADING_MARKER_RE = re.compile(
    _TEX_SLASH + r"(?:section|subsection|subsubsection|paragraph)\*?\b|"
    r"^#{1,6}[ \t]+",
    re.IGNORECASE | re.MULTILINE,
)
_DYNAMIC_RISKS = frozenset({
    "dynamic_tex", "lua_execution", "shell_escape", "file_io",
})


class NearCopyFault(ValueError):
    """A sanitized internal rejection."""

    def __init__(self, code: str = "near_copy_operational_error"):
        self.code = (
            code if code in REASON_CODES else "near_copy_operational_error"
        )
        super().__init__(self.code)


def _unique_pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise NearCopyFault("near_copy_policy_invalid")
        value[key] = item
    return value


def _freeze(value):
    if type(value) is dict:
        return MappingProxyType({
            key: _freeze(item) for key, item in value.items()
        })
    if type(value) is list:
        return tuple(_freeze(item) for item in value)
    return value


def _clean_token(value: object) -> bool:
    return (
        type(value) is str
        and 1 <= len(value) <= 80
        and value == unicodedata.normalize("NFKC", value).casefold()
        and re.fullmatch(r"[^\W_][\w-]*", value, re.UNICODE) is not None
    )


def _fold_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(
        character for character in decomposed
        if not unicodedata.combining(character)
    )


@lru_cache(maxsize=1)
def load_policy(path: Path = POLICY_PATH) -> Mapping[str, object]:
    """Load and strictly validate only the canonical public policy."""
    try:
        lexical = Path(path).absolute()
        if lexical != POLICY_PATH.absolute():
            raise NearCopyFault("near_copy_policy_invalid")
        resolved = POLICY_PATH.resolve(strict=True)
        if resolved != lexical.resolve(strict=True):
            raise NearCopyFault("near_copy_policy_invalid")
        raw = resolved.read_bytes()
        if len(raw) > 128 * 1024:
            raise NearCopyFault("near_copy_policy_invalid")
        value = json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=_unique_pairs,
            parse_constant=lambda _item: (_ for _ in ()).throw(
                NearCopyFault("near_copy_policy_invalid")
            ),
        )
        if type(value) is not dict or set(value) != {
            "policy_version", "max_attempts", "resource_limits", "thresholds",
            "boilerplate_tokens", "stop_tokens", "synonym_groups",
        }:
            raise NearCopyFault("near_copy_policy_invalid")
        if value["policy_version"] != POLICY_VERSION or value["max_attempts"] != 3:
            raise NearCopyFault("near_copy_policy_invalid")
        resources = value["resource_limits"]
        if type(resources) is not dict or set(resources) != {
            "max_candidate_bytes", "max_private_documents",
            "max_total_private_bytes", "max_seconds",
        }:
            raise NearCopyFault("near_copy_policy_invalid")
        resource_maxima = {
            "max_candidate_bytes": 1024 * 1024,
            "max_private_documents": 512,
            "max_total_private_bytes": 32 * 1024 * 1024,
            "max_seconds": 30,
        }
        if any(
            type(resources[key]) is not int
            or not 1 <= resources[key] <= maximum
            for key, maximum in resource_maxima.items()
        ):
            raise NearCopyFault("near_copy_policy_invalid")
        thresholds = value["thresholds"]
        required_thresholds = {
            "min_comparable_content_tokens", "normalized_sequence_tokens",
            "long_sequence_tokens", "long_sequence_ratio",
            "long_shingle_size", "long_shingle_containment",
            "paraphrase_tokens", "paraphrase_ratio",
            "paraphrase_vocabulary_overlap", "composition_min_tokens",
            "composition_min_signals", "composition_vocabulary_overlap",
        }
        if type(thresholds) is not dict or set(thresholds) != required_thresholds:
            raise NearCopyFault("near_copy_policy_invalid")
        integer_thresholds = required_thresholds - {
            "long_sequence_ratio", "long_shingle_containment",
            "paraphrase_ratio", "paraphrase_vocabulary_overlap",
            "composition_vocabulary_overlap",
        }
        if any(
            type(thresholds[key]) is not int or not 1 <= thresholds[key] <= 100
            for key in integer_thresholds
        ):
            raise NearCopyFault("near_copy_policy_invalid")
        if any(
            type(thresholds[key]) not in {int, float}
            or not 0 < thresholds[key] <= 1
            for key in required_thresholds - integer_thresholds
        ):
            raise NearCopyFault("near_copy_policy_invalid")
        for key in ("boilerplate_tokens", "stop_tokens"):
            tokens = value[key]
            if (
                type(tokens) is not list or not tokens
                or len(tokens) != len(set(tokens))
                or any(not _clean_token(item) for item in tokens)
            ):
                raise NearCopyFault("near_copy_policy_invalid")
        groups = value["synonym_groups"]
        if type(groups) is not list or not groups:
            raise NearCopyFault("near_copy_policy_invalid")
        flattened = []
        for group in groups:
            if (
                type(group) is not list or not 2 <= len(group) <= 8
                or len(group) != len(set(group))
                or any(not _clean_token(item) for item in group)
            ):
                raise NearCopyFault("near_copy_policy_invalid")
            flattened.extend(group)
        if len(flattened) != len(set(flattened)):
            raise NearCopyFault("near_copy_policy_invalid")
        return _freeze(value)
    except NearCopyFault:
        raise NearCopyFault("near_copy_policy_invalid") from None
    except Exception:
        raise NearCopyFault("near_copy_policy_invalid") from None


@dataclass(frozen=True)
class NearCopyLimits:
    max_candidate_bytes: int = 1024 * 1024
    max_private_documents: int = 512
    max_total_private_bytes: int = 32 * 1024 * 1024
    max_seconds: float = 30.0

    def __post_init__(self):
        maxima = load_policy()["resource_limits"]
        for key in (
            "max_candidate_bytes", "max_private_documents",
            "max_total_private_bytes",
        ):
            value = getattr(self, key)
            if type(value) is not int or not 1 <= value <= maxima[key]:
                raise NearCopyFault("near_copy_operational_error")
        if (
            type(self.max_seconds) not in {int, float}
            or not 0 < self.max_seconds <= maxima["max_seconds"]
        ):
            raise NearCopyFault("near_copy_operational_error")


class NearCopyResult:
    """Deeply closed public projection; no comparison details are retained."""

    __slots__ = ("_status", "_reason_code", "_performed", "_sealed")

    def __init__(self, status: str, reason_code: str,
                 comparison_performed: bool):
        expected = (
            PASS_REASONS if status == "anti_copy_pass"
            else RISK_REASONS if status == "anti_copy_risk"
            else INCONCLUSIVE_REASONS
            if status == "anti_copy_inconclusive" else frozenset()
        )
        if (
            status not in STATUSES or reason_code not in expected
            or type(comparison_performed) is not bool
            or comparison_performed != (status != "anti_copy_inconclusive")
        ):
            raise NearCopyFault()
        object.__setattr__(self, "_status", status)
        object.__setattr__(self, "_reason_code", reason_code)
        object.__setattr__(self, "_performed", comparison_performed)
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("near_copy_result_immutable")
        object.__setattr__(self, name, value)

    @property
    def status(self):
        return self._status

    @property
    def reason_code(self):
        return self._reason_code

    @property
    def comparison_performed(self):
        return self._performed

    @property
    def release_allowed(self):
        return self._status == "anti_copy_pass"

    def as_dict(self):
        return {
            "status": self.status,
            "reason_code": self.reason_code,
            "comparison_performed": self.comparison_performed,
            "release_allowed": self.release_allowed,
        }

    def __repr__(self):
        return "NearCopyResult(<closed>)"


def _result(status, reason):
    return NearCopyResult(
        status, reason, status != "anti_copy_inconclusive"
    )


@dataclass(frozen=True, repr=False)
class _Profile:
    tokens: tuple[str, ...]
    synonym_tokens: tuple[str, ...]
    vocabulary: frozenset[str]
    numbers: tuple[str, ...]
    equation_shapes: tuple[str, ...]
    operators: tuple[str, ...]
    structure: tuple[int, int, int, int]

    def __repr__(self):
        return "_Profile(<ephemeral>)"


@lru_cache(maxsize=1)
def _policy_views():
    policy = load_policy()
    synonyms = {}
    for group_number, group in enumerate(policy["synonym_groups"]):
        canonical = f"synonym-{group_number}"
        for token in group:
            synonyms[token] = canonical
    excluded = frozenset(
        (*policy["boilerplate_tokens"], *policy["stop_tokens"])
    )
    return MappingProxyType(synonyms), excluded


def _candidate_is_full_document(value: object, maximum: int) -> bool:
    if type(value) is not str or "\x00" in value:
        return False
    try:
        encoded = value.encode("utf-8")
    except UnicodeError:
        return False
    if not 1 <= len(encoded) <= maximum:
        return False
    stripped = value.lstrip("\ufeff \t\r\n")
    if not stripped.startswith("<!--"):
        return False
    end = stripped.find("-->")
    if end < 0 or end > 65536:
        return False
    header = stripped[:end].casefold()
    if "author:" not in header or "language:" not in header:
        return False
    return re.search(r"(?m)^#{1,6}[ \t]+\S", stripped[end + 3:]) is not None


def _equation_shape(value: str) -> str:
    output = []
    for token in re.findall(
        r"\\[A-Za-z@]+|\d+(?:[.,]\d+)?|[A-Za-z\u00c0-\u024f]+|"
        r"==|<=|>=|[=+\-*/^_:]",
        value,
    ):
        if token.startswith("\\"):
            command = token[1:].casefold()
            if command not in {"left", "right", "mathrm", "text"}:
                output.append("c:" + command)
        elif token[0].isdigit():
            output.append("n")
        elif token[0].isalpha():
            output.append("v")
        else:
            output.append(token)
    return " ".join(output)


def _operator_sequence(value: str) -> tuple[str, ...]:
    occurrences = []
    for identifier, pattern in tex._load_operator_patterns(
        tex.DEFAULT_OPERATOR_TAXONOMY
    ):
        for match in pattern.finditer(value):
            occurrences.append((match.start(), identifier))
            if len(occurrences) > 4096:
                raise NearCopyFault("near_copy_operational_error")
    output = []
    for _position, identifier in sorted(occurrences):
        if not output or output[-1] != identifier:
            output.append(identifier)
        if len(output) >= 256:
            break
    return tuple(output)


def _profile(value: str, policy: Mapping[str, object]) -> _Profile:
    if type(value) is not str:
        raise NearCopyFault()
    normalized = _fold_text(value)
    visible = _HTML_COMMENT_RE.sub(" ", normalized)
    synonyms, excluded = _policy_views()
    plain = _TEX_COMMAND_RE.sub(" ", visible)
    plain = _MARKUP_RE.sub(" ", plain)
    raw_tokens = tuple(_TOKEN_RE.findall(plain))
    if len(raw_tokens) > 25000:
        raise NearCopyFault()
    tokens = tuple(token for token in raw_tokens if token not in excluded)
    synonym_tokens = tuple(synonyms.get(token, token) for token in tokens)
    vocabulary = frozenset(
        token for token in synonym_tokens
        if len(token) >= 3 and not token[0].isdigit()
    )
    numbers = tuple(
        match.group(0).replace(" ", "").replace("\\", "").replace(",", ".")
        for match in _NUMBER_RE.finditer(visible)
    )
    equation_shapes = tuple(
        shape for shape in (
            _equation_shape(match.group(0)) for match in _MATH_RE.finditer(visible)
        ) if shape
    )
    structure = (
        len(_TASK_MARKER_RE.findall(visible)),
        len(_SOLUTION_MARKER_RE.findall(visible)),
        len(_ITEM_MARKER_RE.findall(visible)),
        len(_HEADING_MARKER_RE.findall(visible)),
    )
    return _Profile(
        tokens=tokens,
        synonym_tokens=synonym_tokens,
        vocabulary=vocabulary,
        numbers=numbers,
        equation_shapes=equation_shapes,
        operators=_operator_sequence(visible),
        structure=structure,
    )


def _profiles(value: str, policy: Mapping[str, object]) -> tuple[_Profile, ...]:
    """Create a full-document profile plus bounded task/page profiles."""
    minimum = policy["thresholds"]["min_comparable_content_tokens"]
    output = []
    whole = _profile(value, policy)
    if len(whole.tokens) >= minimum:
        output.append(whole)
    split = re.compile(
        r"(?im)^##[ \t]+|"
        + _TEX_SLASH
        + r"begin\s*\{\s*(?:aufgabe|exercise|problem|question|task)\s*\}"
    )
    positions = [match.start() for match in split.finditer(value)]
    positions = positions[:128]
    if positions:
        positions.append(len(value))
        for start, end in zip(positions, positions[1:]):
            item = _profile(value[start:end], policy)
            if (
                len(item.tokens) >= minimum
                and all(item.tokens != previous.tokens for previous in output)
            ):
                output.append(item)
    return tuple(output)


def _sequence_ratio(left: Sequence[str], right: Sequence[str]) -> float:
    return SequenceMatcher(None, left, right, autojunk=True).ratio()


def _shingle_containment(
    left: Sequence[str], right: Sequence[str], size: int
) -> float:
    if len(left) < size or len(right) < size:
        return 0.0
    left_set = {
        tuple(left[index:index + size])
        for index in range(len(left) - size + 1)
    }
    right_set = {
        tuple(right[index:index + size])
        for index in range(len(right) - size + 1)
    }
    shorter = min(len(left_set), len(right_set))
    return len(left_set & right_set) / shorter if shorter else 0.0


def _vocabulary_overlap(left: _Profile, right: _Profile) -> float:
    shorter = min(len(left.vocabulary), len(right.vocabulary))
    return (
        len(left.vocabulary & right.vocabulary) / shorter if shorter else 0.0
    )


def _risk_reason(
    candidate: _Profile,
    private: _Profile,
    policy: Mapping[str, object],
) -> str | None:
    thresholds = policy["thresholds"]
    shorter = min(len(candidate.tokens), len(private.tokens))
    if (
        shorter >= thresholds["normalized_sequence_tokens"]
        and candidate.tokens == private.tokens
    ):
        return "near_copy_normalized_risk"
    if (
        shorter >= thresholds["normalized_sequence_tokens"]
        and candidate.synonym_tokens == private.synonym_tokens
    ):
        return "near_copy_paraphrase_risk"
    ratio = _sequence_ratio(candidate.tokens, private.tokens)
    if shorter >= thresholds["long_sequence_tokens"]:
        if ratio >= thresholds["long_sequence_ratio"]:
            return "near_copy_long_passage_risk"
        if _shingle_containment(
            candidate.tokens, private.tokens,
            thresholds["long_shingle_size"],
        ) >= thresholds["long_shingle_containment"]:
            return "near_copy_long_passage_risk"
    vocabulary_overlap = _vocabulary_overlap(candidate, private)
    if (
        shorter >= thresholds["paraphrase_tokens"]
        and vocabulary_overlap >= thresholds["paraphrase_vocabulary_overlap"]
        and _sequence_ratio(
            candidate.synonym_tokens, private.synonym_tokens
        ) >= thresholds["paraphrase_ratio"]
    ):
        return "near_copy_paraphrase_risk"
    if shorter < thresholds["composition_min_tokens"]:
        return None
    signals = 0
    if len(candidate.numbers) >= 2 and candidate.numbers == private.numbers:
        signals += 1
    if (
        candidate.equation_shapes
        and candidate.equation_shapes == private.equation_shapes
    ):
        signals += 1
    if len(candidate.operators) >= 2 and candidate.operators == private.operators:
        signals += 1
    if (
        sum(candidate.structure[:3]) >= 3
        and candidate.structure == private.structure
    ):
        signals += 1
    if vocabulary_overlap >= thresholds["composition_vocabulary_overlap"]:
        signals += 1
    if _sequence_ratio(
        candidate.synonym_tokens, private.synonym_tokens
    ) >= 0.58:
        signals += 1
    if signals >= thresholds["composition_min_signals"]:
        return "near_copy_composition_risk"
    return None


def _validate_scope(subject: object, filters: object) -> dict[str, object]:
    if subject not in config.SUBJECTS or not isinstance(filters, Mapping):
        raise NearCopyFault("near_copy_filter_invalid")
    try:
        selected = search._validate_filters(dict(filters))
    except Exception:
        raise NearCopyFault("near_copy_filter_invalid") from None
    if selected.get("subject") != subject:
        raise NearCopyFault("near_copy_filter_invalid")
    return selected


def _matches_document(
    document: Mapping[str, object],
    filters: Mapping[str, object],
    deadline: float,
    task_budget: list[int],
) -> bool:
    classification = document["classification"]
    if any(
        key in filters and filters[key] not in classification[field]
        for key, field in (
            ("subject", "subjects"), ("grade", "grades"),
            ("learner_group", "learner_groups"),
            ("document_type", "document_types"),
        )
    ):
        return False
    if (
        "suitability" in filters
        and document["suitability"] != filters["suitability"]
    ):
        return False
    if (
        "has_warnings" in filters
        and bool(document["warning_codes"]) != filters["has_warnings"]
    ):
        return False
    task_count = document["structure"]["task_count"]
    if not (
        filters.get("min_tasks", 0)
        <= task_count
        <= filters.get("max_tasks", 5000)
    ):
        return False
    if (
        document["local_provenance"]["modified_ns"]
        < filters.get("modified_after_ns", 0)
    ):
        return False
    if any(
        filters[key] not in search._document_feature_ids(document, dimension)
        for key, dimension in search.FEATURE_FILTER_MAP.items()
        if key in filters
    ):
        return False
    return bool(search._matching_tasks(
        document, filters, deadline, task_budget
    ))


def _prepare_private_profiles(
    repo_root: Path,
    explicit_config: Path | None,
    environ: Mapping[str, str] | None,
    selected_filters: Mapping[str, object],
    policy: Mapping[str, object],
    limits: NearCopyLimits,
) -> tuple[_Profile, ...]:
    deadline = time.monotonic() + limits.max_seconds
    result, sources = config.load_validated_sources(
        repo_root, explicit_config=explicit_config, environ=environ,
    )
    if result.availability_state != config.STATE_AVAILABLE or not sources:
        raise NearCopyFault("near_copy_private_unavailable")
    remaining = max(0.001, deadline - time.monotonic())
    try:
        graph = includes.analyze_sources(
            sources,
            limits=includes.IncludeLimits(
                max_nodes=limits.max_private_documents,
                max_total_bytes=limits.max_total_private_bytes,
                max_seconds=min(30.0, remaining),
            ),
            parser_limits=tex.ParserLimits(
                max_bytes=min(
                    tex.ParserLimits().max_bytes,
                    limits.max_total_private_bytes,
                )
            ),
            discovery_limits=selector.DiscoveryLimits(
                max_candidates=limits.max_private_documents,
                max_file_bytes=min(
                    selector.DiscoveryLimits().max_file_bytes,
                    limits.max_total_private_bytes,
                ),
                max_total_bytes=limits.max_total_private_bytes,
            ),
        )
    except Exception:
        raise NearCopyFault("near_copy_private_unavailable") from None
    if len(graph.documents) != len(graph.candidates):
        raise NearCopyFault()
    profiles = []
    dynamic = False
    task_budget = [25000]
    for document, candidate in zip(graph.documents, graph.candidates):
        if time.monotonic() > deadline:
            raise NearCopyFault("near_copy_time_limit")
        try:
            matching = _matches_document(
                document, selected_filters, deadline, task_budget
            )
        except Exception:
            raise NearCopyFault() from None
        if not matching:
            continue
        if set(document["risk_codes"]) & _DYNAMIC_RISKS:
            dynamic = True
            continue
        try:
            data = selector.read_candidate_bytes(
                candidate, tex.ParserLimits().max_bytes
            )
            decoded, _encoding, _warnings = tex._decode_tex(
                data, tex.ParserLimits()
            )
            analysis, _v, _m, _w, _r = tex._preprocess_tex(
                decoded, tex.ParserLimits()
            )
            profiles.extend(_profiles(analysis, policy))
            del data, decoded, analysis
        except NearCopyFault:
            raise
        except Exception:
            raise NearCopyFault("near_copy_private_unavailable") from None
        if len(profiles) > limits.max_private_documents * 129:
            raise NearCopyFault()
    if dynamic:
        raise NearCopyFault("near_copy_private_dynamic_construct")
    if not profiles:
        raise NearCopyFault("near_copy_no_comparison_basis")
    return tuple(profiles)


class NearCopySession:
    """Bounded per-E2E session; comparison material dies with the session."""

    __slots__ = (
        "_references", "_fixed_reason", "_policy", "_maximum_bytes",
        "_max_seconds", "_maximum_attempts", "_attempts", "_closed", "_sealed",
    )

    def __init__(
        self,
        references: Sequence[_Profile],
        fixed_reason: str | None,
        policy: Mapping[str, object] | None,
        maximum_bytes: int,
        max_seconds: float,
        maximum_attempts: int = 3,
    ):
        if (
            fixed_reason is not None
            and fixed_reason not in INCONCLUSIVE_REASONS
        ):
            raise NearCopyFault()
        if (
            any(not isinstance(item, _Profile) for item in references)
            or type(maximum_bytes) is not int or maximum_bytes <= 0
            or type(max_seconds) not in {int, float} or max_seconds <= 0
            or maximum_attempts != 3
        ):
            raise NearCopyFault()
        object.__setattr__(self, "_references", list(references))
        object.__setattr__(self, "_fixed_reason", fixed_reason)
        object.__setattr__(self, "_policy", policy)
        object.__setattr__(self, "_maximum_bytes", maximum_bytes)
        object.__setattr__(self, "_max_seconds", max_seconds)
        object.__setattr__(self, "_maximum_attempts", maximum_attempts)
        object.__setattr__(self, "_attempts", 0)
        object.__setattr__(self, "_closed", False)
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("near_copy_session_immutable")
        object.__setattr__(self, name, value)

    def __repr__(self):
        return "NearCopySession(<ephemeral-closed-output>)"

    def __enter__(self):
        return self

    def __exit__(self, _kind, _value, _traceback):
        self.close()
        return False

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def close(self):
        if not self._closed:
            self._references.clear()
            object.__setattr__(self, "_policy", None)
            object.__setattr__(self, "_closed", True)

    def check(self, candidate_text: object) -> NearCopyResult:
        if self._closed:
            return _result(
                "anti_copy_inconclusive", "near_copy_session_closed"
            )
        if self._attempts >= self._maximum_attempts:
            return _result(
                "anti_copy_inconclusive", "near_copy_attempt_limit"
            )
        object.__setattr__(self, "_attempts", self._attempts + 1)
        if not _candidate_is_full_document(
            candidate_text, self._maximum_bytes
        ):
            return _result(
                "anti_copy_inconclusive", "near_copy_candidate_invalid"
            )
        if self._fixed_reason is not None:
            return _result("anti_copy_inconclusive", self._fixed_reason)
        policy = self._policy
        if not isinstance(policy, Mapping) or not self._references:
            return _result(
                "anti_copy_inconclusive", "near_copy_operational_error"
            )
        deadline = time.monotonic() + self._max_seconds
        try:
            candidates = _profiles(candidate_text, policy)
            if not candidates:
                return _result(
                    "anti_copy_inconclusive",
                    "near_copy_candidate_too_short",
                )
            for candidate in candidates:
                for private in self._references:
                    if time.monotonic() > deadline:
                        raise NearCopyFault("near_copy_time_limit")
                    reason = _risk_reason(candidate, private, policy)
                    if reason is not None:
                        return _result("anti_copy_risk", reason)
            return _result(
                "anti_copy_pass", "near_copy_no_risk_detected"
            )
        except NearCopyFault as fault:
            reason = (
                fault.code
                if fault.code in {
                    "near_copy_time_limit", "near_copy_policy_invalid",
                }
                else "near_copy_operational_error"
            )
            return _result("anti_copy_inconclusive", reason)
        except Exception:
            return _result(
                "anti_copy_inconclusive", "near_copy_operational_error"
            )


def _fixed_session(reason: str) -> NearCopySession:
    return NearCopySession((), reason, None, 1024 * 1024, 30.0)


def prepare_acceptance_session(
    repo_root: Path = ROOT,
    *,
    explicit_config: Path | None = None,
    environ: Mapping[str, str] | None = None,
    subject: str,
    filters: Mapping[str, object],
    limits: NearCopyLimits | None = None,
) -> NearCopySession:
    """Prepare one non-oracle acceptance session with at most three checks."""
    try:
        policy = load_policy()
        active = NearCopyLimits() if limits is None else limits
        if not isinstance(active, NearCopyLimits):
            raise NearCopyFault()
        selected = _validate_scope(subject, filters)
        references = _prepare_private_profiles(
            Path(repo_root), explicit_config, environ, selected, policy, active,
        )
        return NearCopySession(
            references, None, policy, active.max_candidate_bytes,
            active.max_seconds, policy["max_attempts"],
        )
    except NearCopyFault as fault:
        reason = (
            fault.code if fault.code in INCONCLUSIVE_REASONS
            else "near_copy_operational_error"
        )
        return _fixed_session(reason)
    except Exception:
        return _fixed_session("near_copy_operational_error")


def main() -> int:
    """Refuse generic CLI use while still emitting only a closed projection."""
    print(json.dumps(
        _result(
            "anti_copy_inconclusive", "near_copy_candidate_invalid"
        ).as_dict(),
        ensure_ascii=True,
        sort_keys=True,
    ))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
