#!/usr/bin/env python3
"""Bounded local-only TeX include graphs; never execute or fetch source code.

Only selector-attested files in the same source may be connected.  The graph
contains per-document parser metadata and opaque local edges, not expanded TeX.
Raw reference arguments are transient and never leave this implementation.
"""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass, field, replace
from pathlib import PurePosixPath, PureWindowsPath
from typing import Sequence

import local_orientation_candidates as selector
import local_orientation_tex as tex
from local_orientation_config import ValidatedSource


@dataclass(frozen=True)
class IncludeLimits:
    max_sources: int = 32
    max_nodes: int = 512
    max_edges: int = 2048
    max_depth: int = 32
    max_total_bytes: int = 32 * 1024 * 1024
    max_seconds: float = 30.0

    def __post_init__(self) -> None:
        maxima = {"max_sources": 32, "max_nodes": 512, "max_edges": 2048,
                  "max_depth": 32, "max_total_bytes": 32 * 1024 * 1024}
        if any(type(getattr(self, key)) is not int
               or not 0 < getattr(self, key) <= maximum
               for key, maximum in maxima.items()):
            raise ValueError("include_limits_invalid")
        if (type(self.max_seconds) not in {int, float}
                or not 0 < self.max_seconds <= 30):
            raise ValueError("include_limits_invalid")


class IncludeFault(RuntimeError):
    """Sanitized graph rejection without a source-data exception chain."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, repr=False)
class IncludeGraph:
    """Local-only graph; its members must never be generically serialized."""

    documents: tuple[dict[str, object], ...] = field(repr=False)
    candidates: tuple[selector.LocalTexCandidate, ...] = field(repr=False)
    edges: tuple[tuple[str, str, str], ...] = field(repr=False)
    warning_codes: tuple[str, ...] = field(repr=False)

    def __repr__(self) -> str:
        return "IncludeGraph(<local-only>)"


def _deadline_check(deadline: float) -> None:
    if time.monotonic() > deadline:
        raise IncludeFault("include_time_limit")


def _reference_arguments(
    original: str, analysis: str, limits: tex.ParserLimits
):
    """Use the parser's masked token stream and original grouped arguments.

    Reading the original argument is necessary because a TeX comment consumes
    its newline even inside a filename.  Command visibility still comes only
    from the canonical macro/verbatim/comment preprocessing.
    """
    references = 0
    for match in tex.REFERENCE_RE.finditer(analysis):
        before = match.start() - 1
        slash_count = 0
        while before >= 0 and analysis[before] == chr(92):
            slash_count += 1
            before -= 1
        if slash_count % 2:
            continue  # e.g. a printed \\input rather than an input command.
        if (match.end() < len(analysis)
                and analysis[match.end()] == "@"):
            continue
        references += 1
        if references > limits.max_commands:
            raise IncludeFault("include_reference_limit")
        cursor = tex._skip_tex_space(original, match.end())
        if cursor >= len(original) or original[cursor] != "{":
            yield None
            continue
        end = tex._consume_group(
            original, cursor, "{", "}", limits.max_nesting
        )
        if end is None:
            yield None
            continue
        yield tex._elide_tex_comments(original[cursor + 1:end - 1]).strip()


def _target_locator(parent_locator: str, value: str | None) -> str | None:
    """Return a literal .tex locator, without probing any target path."""
    if not value or len(value) > 1024:
        return None
    if (value.startswith(("/", "|")) or PureWindowsPath(value).is_absolute()
            or any(character.isspace() or ord(character) < 32
                   or ord(character) in {127, 0x85, 0x2028, 0x2029}
                   for character in value)
            or any(character in value for character in "\\:#${}|%~^&\"'")):
        return None
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    target = PurePosixPath(value)
    if target.suffix:
        if target.suffix.casefold() != ".tex":
            return None
    else:
        target = target.with_suffix(".tex")
    locator = (PurePosixPath(parent_locator).parent / target).as_posix()
    if len(locator) > 1024:
        return None
    return locator


def _verify_unchanged(candidate: selector.LocalTexCandidate) -> None:
    """Reject visible changes after a graph's only content read."""
    if selector._path_chain_has_link(candidate.path):
        raise IncludeFault("include_candidate_changed")
    metadata = candidate.path.lstat()
    if (selector._entry_link(candidate.path, metadata)
            or not selector._same_candidate(candidate, metadata)):
        raise IncludeFault("include_candidate_changed")


def _check_graph_depth(
    keys: Sequence[str], adjacency: dict[str, set[str]], maximum: int,
    deadline: float,
) -> bool:
    """Bounded DFS; cycles are retained as local edges but never expanded."""
    color: dict[str, int] = {}
    height: dict[str, int] = {}
    cycle = False
    for key in keys:
        if color.get(key) == 2:
            continue
        stack: list[tuple[str, object]] = [(key, iter(sorted(adjacency[key])))]
        color[key] = 1
        height[key] = 0
        while stack:
            _deadline_check(deadline)
            current, children = stack[-1]
            try:
                child = next(children)
            except StopIteration:
                color[current] = 2
                stack.pop()
                if stack:
                    parent = stack[-1][0]
                    height[parent] = max(height[parent], height[current] + 1)
                    if height[parent] > maximum:
                        raise IncludeFault("include_depth_limit")
                continue
            if color.get(child) == 1:
                cycle = True
                continue
            if color.get(child) == 2:
                height[current] = max(height[current], height[child] + 1)
                if height[current] > maximum:
                    raise IncludeFault("include_depth_limit")
                continue
            if len(stack) > maximum:
                raise IncludeFault("include_depth_limit")
            color[child] = 1
            height[child] = 0
            stack.append((child, iter(sorted(adjacency[child]))))
    return cycle


def _analyze_sources_impl(
    sources: Sequence[ValidatedSource], *, limits: IncludeLimits | None,
    parser_limits: tex.ParserLimits | None,
    discovery_limits: selector.DiscoveryLimits | None,
) -> IncludeGraph:
    active = limits or IncludeLimits()
    parsing = parser_limits or tex.ParserLimits()
    if (not isinstance(sources, (tuple, list))
            or len(sources) > active.max_sources
            or any(not isinstance(source, ValidatedSource) for source in sources)):
        raise IncludeFault("include_sources_invalid")
    if len({source.source_id for source in sources}) != len(sources):
        raise IncludeFault("include_sources_duplicate")
    deadline = time.monotonic() + active.max_seconds
    discovery = discovery_limits or selector.DiscoveryLimits()
    discovery = replace(
        discovery,
        max_depth=min(discovery.max_depth, 32),
        max_directories=min(discovery.max_directories, 10_000),
        max_entries=min(discovery.max_entries, 100_000),
        max_candidates=min(discovery.max_candidates, active.max_nodes),
        max_file_bytes=min(discovery.max_file_bytes, parsing.max_bytes,
                           active.max_total_bytes),
        max_total_bytes=min(discovery.max_total_bytes, active.max_total_bytes),
    )
    candidates: list[selector.LocalTexCandidate] = []
    total_bytes = 0
    identities: set[tuple[int, int]] = set()
    for source in sorted(sources, key=lambda item: item.source_id):
        _deadline_check(deadline)
        found = selector.enumerate_candidates(source, discovery)
        _deadline_check(deadline)
        for candidate in found.candidates:
            total_bytes += candidate.size_bytes
            if total_bytes > active.max_total_bytes:
                raise IncludeFault("include_total_bytes_limit")
            if len(candidates) >= active.max_nodes:
                raise IncludeFault("include_node_limit")
            identity = (candidate.device, candidate.inode)
            if identity in identities:
                raise IncludeFault("include_identity_duplicate")
            identities.add(identity)
            candidates.append(candidate)

    documents: list[dict[str, object]] = []
    target_map = {(candidate.source_id, candidate.relative_locator): candidate
                  for candidate in candidates}
    document_ids = {
        (candidate.source_id, candidate.relative_locator): "doc-" + hashlib.sha256(
            (candidate.source_id + "\0" + candidate.relative_locator).encode("utf-8")
        ).hexdigest()[:32]
        for candidate in candidates
    }
    operator_patterns = tex._load_operator_patterns(tex.DEFAULT_OPERATOR_TAXONOMY)
    edges: set[tuple[str, str, str]] = set()
    warnings: set[str] = set()
    references = 0
    read_bytes = 0
    for candidate in candidates:
        _deadline_check(deadline)
        data = selector.read_candidate_bytes(candidate, parsing.max_bytes)
        read_bytes += len(data)
        if read_bytes > active.max_total_bytes:
            raise IncludeFault("include_total_bytes_limit")
        text, encoding, decode_warnings = tex._decode_tex(data, parsing)
        document_id = document_ids[(candidate.source_id, candidate.relative_locator)]
        metadata = tex._parse_decoded(
            text, source_id=candidate.source_id, document_id=document_id,
            relative_locator=candidate.relative_locator, size_bytes=len(data),
            modified_ns=candidate.modified_ns,
            integrity_sha256=hashlib.sha256(data).hexdigest(), encoding=encoding,
            source=candidate.source, initial_warnings=decode_warnings,
            limits=parsing, operator_patterns=operator_patterns,
        )
        documents.append(metadata.as_dict())
        analysis, _v, _m, _w, _r = tex._preprocess_tex(text, parsing)
        for value in _reference_arguments(text, analysis, parsing):
            references += 1
            if references > active.max_edges:
                raise IncludeFault("include_edge_limit")
            _deadline_check(deadline)
            locator = _target_locator(candidate.relative_locator, value)
            if locator is None:
                warnings.add("include_reference_unsupported")
                continue
            key = (candidate.source_id, locator)
            if key not in target_map:
                warnings.add("include_target_not_allowlisted")
                continue
            edges.add((candidate.source_id, document_id, document_ids[key]))
        del data, text, analysis
        _deadline_check(deadline)

    adjacency: dict[str, set[str]] = {
        value: set() for value in document_ids.values()
    }
    for _source_id, parent, child in edges:
        adjacency[parent].add(child)
    if _check_graph_depth(
            tuple(sorted(adjacency)), adjacency, active.max_depth, deadline):
        warnings.add("include_cycle")
    for candidate in candidates:
        _deadline_check(deadline)
        _verify_unchanged(candidate)
    return IncludeGraph(tuple(documents), tuple(candidates), tuple(sorted(edges)),
                        tuple(sorted(warnings)))


def analyze_sources(
    sources: Sequence[ValidatedSource], *, limits: IncludeLimits | None = None,
    parser_limits: tex.ParserLimits | None = None,
    discovery_limits: selector.DiscoveryLimits | None = None,
) -> IncludeGraph:
    """Analyze only active validated sources and detach all private failures."""
    code: str | None = None
    try:
        return _analyze_sources_impl(
            sources, limits=limits, parser_limits=parser_limits,
            discovery_limits=discovery_limits,
        )
    except IncludeFault as failure:
        code = failure.code
    except selector.DiscoveryFault as failure:
        code = failure.code
    except tex.TexParseFault as failure:
        code = failure.code
    except Exception:
        code = "include_operational_error"
    raise IncludeFault(code or "include_operational_error")
