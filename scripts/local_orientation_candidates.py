#!/usr/bin/env python3
"""Safely select TeX candidates from an already validated local source.

This is a library, not a CLI. It never prints paths, follows links, or persists
content. Discovery reads each bounded candidate only to create a process-local
keyed content authenticator that is never serialized or exposed. Rules are
relative POSIX paths:
``*``, ``?`` and character classes match within one segment, while a segment
equal to ``**`` matches zero or more segments. A directory match includes its
descendants. Matching is case-sensitive; case-fold collisions are rejected.
"""

from __future__ import annotations

import fnmatch
import hashlib
import hmac
import os
import secrets
import stat
import weakref
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from local_orientation_config import ValidatedSource


@dataclass(frozen=True)
class DiscoveryLimits:
    max_depth: int = 32
    max_directories: int = 10_000
    max_entries: int = 100_000
    max_candidates: int = 20_000
    max_file_bytes: int = 8 * 1024 * 1024
    max_total_bytes: int = 512 * 1024 * 1024

    def __post_init__(self) -> None:
        values = (
            self.max_depth,
            self.max_directories,
            self.max_entries,
            self.max_candidates,
            self.max_file_bytes,
            self.max_total_bytes,
        )
        if any(type(value) is not int or value <= 0 for value in values):
            raise ValueError("discovery_limits_invalid")
        if self.max_file_bytes > self.max_total_bytes:
            raise ValueError("discovery_limits_invalid")


class DiscoveryFault(RuntimeError):
    """A failure whose public string contains only a stable code."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True, repr=False, eq=False)
class LocalTexCandidate:
    """A local-only candidate whose representation discloses no locator."""

    source: "ValidatedSource" = field(repr=False)
    path: Path = field(repr=False)
    relative_locator: str = field(repr=False)
    size_bytes: int
    modified_ns: int = field(repr=False)
    device: int = field(repr=False)
    inode: int = field(repr=False)
    link_count: int = field(repr=False)
    content_authenticator: bytes = field(repr=False)

    def __repr__(self) -> str:
        return "LocalTexCandidate(<local-only>)"

    @property
    def source_id(self) -> str:
        return self.source.source_id

    @property
    def absolute_path(self) -> Path:
        return self.path

    @property
    def source_root(self) -> Path:
        return self.source.root


_ATTESTED_CANDIDATES: weakref.WeakSet[LocalTexCandidate] = weakref.WeakSet()
_ATTESTATION_KEY = secrets.token_bytes(32)


@dataclass(frozen=True, repr=False)
class DiscoveryResult:
    candidates: tuple[LocalTexCandidate, ...] = field(repr=False)
    visited_directories: int = field(repr=False)
    visited_entries: int = field(repr=False)
    selected_bytes: int = field(repr=False)

    def __repr__(self) -> str:
        return "DiscoveryResult(<local-only>)"


def _reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except AttributeError:
        return False
    except OSError as exc:
        raise DiscoveryFault("path_metadata_unreadable") from None
    return bool(
        attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _link(path: Path) -> bool:
    try:
        if path.is_symlink() or _reparse(path):
            return True
        isjunction = getattr(os.path, "isjunction", None)
        return bool(isjunction and isjunction(path))
    except DiscoveryFault:
        raise
    except OSError as exc:
        raise DiscoveryFault("path_metadata_unreadable") from None


def _path_chain_has_link(path: Path) -> bool:
    try:
        absolute = path.absolute()
    except OSError as exc:
        raise DiscoveryFault("path_boundary_unresolved") from None
    if not absolute.parts:
        raise DiscoveryFault("path_boundary_unresolved")
    current = Path(absolute.parts[0])
    for part in absolute.parts[1:]:
        current = current / part
        if _link(current):
            return True
    return False


def _inside(path: Path, root: Path) -> bool:
    try:
        candidate = os.path.normcase(os.path.abspath(os.fspath(path)))
        parent = os.path.normcase(os.path.abspath(os.fspath(root)))
        return os.path.commonpath((candidate, parent)) == parent
    except (OSError, ValueError):
        return False


def _entry_link(path: Path, metadata: os.stat_result) -> bool:
    if stat.S_ISLNK(metadata.st_mode):
        return True
    attributes = getattr(metadata, "st_file_attributes", 0)
    if attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
        return True
    isjunction = getattr(os.path, "isjunction", None)
    try:
        return bool(isjunction and isjunction(path))
    except OSError:
        return True


def _rule_parts(rule: str) -> tuple[str, ...]:
    if (
        not isinstance(rule, str)
        or not rule
        or rule != rule.strip()
        or rule in {".", "./"}
        or "\x00" in rule
        or chr(92) in rule
        or ":" in rule
        or PureWindowsPath(rule).is_absolute()
    ):
        raise DiscoveryFault("relative_rule_invalid")
    path = PurePosixPath(rule)
    if path.is_absolute() or not path.parts or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        raise DiscoveryFault("relative_rule_invalid")
    return tuple(path.parts)


def _matches_exact(
    path_parts: tuple[str, ...], rule_parts: tuple[str, ...]
) -> bool:
    @lru_cache(maxsize=None)
    def match(path_index: int, rule_index: int) -> bool:
        if rule_index == len(rule_parts):
            return path_index == len(path_parts)
        pattern = rule_parts[rule_index]
        if pattern == "**":
            return match(path_index, rule_index + 1) or (
                path_index < len(path_parts)
                and match(path_index + 1, rule_index)
            )
        return (
            path_index < len(path_parts)
            and fnmatch.fnmatchcase(path_parts[path_index], pattern)
            and match(path_index + 1, rule_index + 1)
        )

    return match(0, 0)


def _matches_rule_or_ancestor(
    path_parts: tuple[str, ...], rule_parts: tuple[str, ...]
) -> bool:
    return any(
        _matches_exact(path_parts[:length], rule_parts)
        for length in range(1, len(path_parts) + 1)
    )


def _rule_can_reach(
    directory_parts: tuple[str, ...], rule_parts: tuple[str, ...]
) -> bool:
    """Return whether a directory can be or contain a rule match."""

    @lru_cache(maxsize=None)
    def compatible(path_index: int, rule_index: int) -> bool:
        if path_index == len(directory_parts):
            return True
        if rule_index == len(rule_parts):
            return True  # The rule already matched an ancestor directory.
        pattern = rule_parts[rule_index]
        if pattern == "**":
            return compatible(path_index, rule_index + 1) or compatible(
                path_index + 1, rule_index
            )
        return fnmatch.fnmatchcase(
            directory_parts[path_index], pattern
        ) and compatible(path_index + 1, rule_index + 1)

    return compatible(0, 0)


def _safe_locator(parts: tuple[str, ...]) -> str:
    if not parts or any(
        not part
        or part in {".", ".."}
        or any(ord(character) < 32
               or ord(character) in {127, 0x85, 0x2028, 0x2029}
               for character in part)
        or "/" in part
        or chr(92) in part
        or ":" in part
        for part in parts
    ):
        raise DiscoveryFault("candidate_locator_invalid")
    return PurePosixPath(*parts).as_posix()


def _same_candidate(
    candidate: LocalTexCandidate, metadata: os.stat_result
) -> bool:
    return (
        candidate.device != 0
        and candidate.inode != 0
        and candidate.link_count == 1
        and int(metadata.st_dev) != 0
        and int(metadata.st_ino) != 0
        and int(metadata.st_nlink) == 1
        and stat.S_ISREG(metadata.st_mode)
        and int(metadata.st_size) == candidate.size_bytes
        and int(metadata.st_mtime_ns) == candidate.modified_ns
        and int(metadata.st_dev) == candidate.device
        and int(metadata.st_ino) == candidate.inode
        and int(metadata.st_nlink) == candidate.link_count
    )


def _same_metadata(expected: os.stat_result, observed: os.stat_result) -> bool:
    return (
        stat.S_ISREG(expected.st_mode)
        and stat.S_ISREG(observed.st_mode)
        and int(expected.st_dev) != 0
        and int(expected.st_ino) != 0
        and int(expected.st_nlink) == 1
        and int(observed.st_dev) == int(expected.st_dev)
        and int(observed.st_ino) == int(expected.st_ino)
        and int(observed.st_nlink) == 1
        and int(observed.st_size) == int(expected.st_size)
        and int(observed.st_mtime_ns) == int(expected.st_mtime_ns)
    )


def _attest_candidate_content(
    path: Path,
    expected: os.stat_result,
    maximum: int,
) -> bytes:
    """Bind selection to content without exposing a reusable fingerprint."""

    descriptor = None
    flags = os.O_RDONLY
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        opened = os.fstat(descriptor)
        if not _same_metadata(expected, opened):
            raise DiscoveryFault("candidate_identity_changed")
        authenticator = hmac.new(
            _ATTESTATION_KEY, digestmod=hashlib.sha256
        )
        total = 0
        while total <= maximum:
            chunk = os.read(descriptor, min(64 * 1024, maximum + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            if total > maximum:
                raise DiscoveryFault("candidate_size_limit")
            authenticator.update(chunk)
        reread = os.fstat(descriptor)
        if total != int(expected.st_size) or not _same_metadata(
            expected, reread
        ):
            raise DiscoveryFault("candidate_identity_changed")
    except DiscoveryFault:
        raise
    except OSError:
        raise DiscoveryFault("candidate_open_failed") from None
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
    try:
        after = path.lstat()
    except OSError:
        raise DiscoveryFault("candidate_identity_changed") from None
    if not _same_metadata(expected, after):
        raise DiscoveryFault("candidate_identity_changed")
    return authenticator.digest()


def _enumerate_candidates_impl(
    source: "ValidatedSource",
    limits: DiscoveryLimits | None = None,
) -> DiscoveryResult:
    """Enumerate allowlisted regular TeX files from one validated source."""

    selected_limits = DiscoveryLimits() if limits is None else limits
    source_id = getattr(source, "source_id", None)
    root_value = getattr(source, "root", None)
    if not isinstance(source_id, str) or not source_id:
        raise DiscoveryFault("validated_source_invalid")
    try:
        root_path = Path(root_value)
    except (TypeError, ValueError) as exc:
        raise DiscoveryFault("validated_source_invalid") from None
    if not root_path.is_absolute():
        raise DiscoveryFault("validated_source_invalid")
    if _path_chain_has_link(root_path):
        raise DiscoveryFault("source_root_link_boundary")
    try:
        root = root_path.resolve(strict=True)
        root_metadata = root.lstat()
    except OSError as exc:
        raise DiscoveryFault("source_root_unreachable") from None
    if _entry_link(root, root_metadata) or not stat.S_ISDIR(root_metadata.st_mode):
        raise DiscoveryFault("source_root_invalid")

    try:
        include_rules = tuple(_rule_parts(rule) for rule in source.include)
        exclude_rules = tuple(_rule_parts(rule) for rule in source.exclude)
    except (AttributeError, TypeError) as exc:
        raise DiscoveryFault("validated_source_invalid") from None
    if not include_rules:
        raise DiscoveryFault("include_rules_invalid")
    allowed_extensions = tuple(
        value.casefold()
        for value in getattr(source, "allowed_extensions", ())
        if isinstance(value, str)
    )
    if allowed_extensions != (".tex",):
        raise DiscoveryFault("allowed_extensions_invalid")

    def excluded(parts: tuple[str, ...]) -> bool:
        return any(_matches_rule_or_ancestor(parts, rule) for rule in exclude_rules)

    def included(parts: tuple[str, ...]) -> bool:
        return any(_matches_rule_or_ancestor(parts, rule) for rule in include_rules)

    def relevant_directory(parts: tuple[str, ...]) -> bool:
        return any(_rule_can_reach(parts, rule) for rule in include_rules)

    candidates: list[LocalTexCandidate] = []
    selected_bytes = 0
    visited_directories = 0
    visited_entries = 0
    identities: set[tuple[int, int]] = set()
    folded_locators: dict[str, str] = {}
    stack: list[tuple[Path, tuple[str, ...]]] = [(root, ())]

    while stack:
        directory, directory_parts = stack.pop()
        if len(directory_parts) > selected_limits.max_depth:
            raise DiscoveryFault("traversal_depth_limit")
        visited_directories += 1
        if visited_directories > selected_limits.max_directories:
            raise DiscoveryFault("directory_limit")
        try:
            directory_resolved = directory.resolve(strict=True)
        except OSError as exc:
            raise DiscoveryFault("directory_boundary_unresolved") from None
        if _link(directory) or not _inside(directory_resolved, root):
            raise DiscoveryFault("directory_boundary_invalid")
        try:
            with os.scandir(directory) as iterator:
                entries = []
                for entry in iterator:
                    visited_entries += 1
                    if visited_entries > selected_limits.max_entries:
                        raise DiscoveryFault("entry_limit")
                    entries.append(entry)
        except DiscoveryFault:
            raise
        except OSError:
            raise DiscoveryFault("directory_unreadable") from None
        entries.sort(key=lambda item: (item.name.casefold(), item.name))
        child_directories: list[tuple[Path, tuple[str, ...]]] = []

        for entry in entries:
            parts = directory_parts + (entry.name,)
            if excluded(parts):
                continue
            if not (relevant_directory(parts) or included(parts)):
                continue
            locator = _safe_locator(parts)
            folded = locator.casefold()
            previous = folded_locators.get(folded)
            if previous is not None and previous != locator:
                raise DiscoveryFault("path_case_collision")
            folded_locators[folded] = locator

            entry_path = Path(entry.path)
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise DiscoveryFault("candidate_metadata_unreadable") from None
            if _entry_link(entry_path, metadata):
                raise DiscoveryFault("candidate_link_boundary")
            if stat.S_ISDIR(metadata.st_mode):
                if len(parts) > selected_limits.max_depth:
                    raise DiscoveryFault("traversal_depth_limit")
                if relevant_directory(parts):
                    child_directories.append((entry_path, parts))
                continue
            if not stat.S_ISREG(metadata.st_mode) or not included(parts):
                continue
            if entry_path.suffix.casefold() not in allowed_extensions:
                continue
            try:
                resolved = entry_path.resolve(strict=True)
                verified = resolved.lstat()
            except OSError:
                raise DiscoveryFault("candidate_boundary_unresolved") from None
            if not _inside(resolved, root):
                raise DiscoveryFault("candidate_boundary_escape")
            if _entry_link(resolved, verified) or not stat.S_ISREG(verified.st_mode):
                raise DiscoveryFault("candidate_identity_changed")
            _require_stable_identity(verified)
            size = int(verified.st_size)
            if size < 0 or size > selected_limits.max_file_bytes:
                raise DiscoveryFault("candidate_size_limit")
            selected_bytes += size
            if selected_bytes > selected_limits.max_total_bytes:
                raise DiscoveryFault("total_size_limit")
            if len(candidates) + 1 > selected_limits.max_candidates:
                raise DiscoveryFault("candidate_limit")
            device = int(verified.st_dev)
            inode = int(verified.st_ino)
            identity = (device, inode)
            if identity in identities:
                raise DiscoveryFault("candidate_identity_duplicate")
            identities.add(identity)
            authenticator = _attest_candidate_content(
                resolved, verified, selected_limits.max_file_bytes
            )
            candidates.append(
                LocalTexCandidate(
                    source=source,
                    path=resolved,
                    relative_locator=locator,
                    size_bytes=size,
                    modified_ns=int(verified.st_mtime_ns),
                    device=device,
                    inode=inode,
                    link_count=1,
                    content_authenticator=authenticator,
                )
            )

        for child in reversed(child_directories):
            stack.append(child)

    candidates.sort(
        key=lambda item: (item.relative_locator.casefold(), item.relative_locator)
    )
    return DiscoveryResult(
        candidates=tuple(candidates),
        visited_directories=visited_directories,
        visited_entries=visited_entries,
        selected_bytes=selected_bytes,
    )


def _require_stable_identity(metadata: os.stat_result) -> None:
    if int(metadata.st_dev) == 0 or int(metadata.st_ino) == 0:
        raise DiscoveryFault("candidate_identity_unavailable")
    if int(metadata.st_nlink) != 1:
        raise DiscoveryFault("candidate_hardlink_rejected")


def _clean_fault(fault: DiscoveryFault) -> DiscoveryFault:
    """Detach private filesystem exceptions before crossing the public API."""

    fault.__cause__ = None
    fault.__context__ = None
    fault.__traceback__ = None
    fault.__suppress_context__ = True
    return fault


def enumerate_candidates(
    source: "ValidatedSource",
    limits: DiscoveryLimits | None = None,
) -> DiscoveryResult:
    """Enumerate candidates and expose only a detached sanitized fault."""

    fault: DiscoveryFault | None = None
    result: DiscoveryResult | None = None
    try:
        result = _enumerate_candidates_impl(source, limits)
        for candidate in result.candidates:
            _ATTESTED_CANDIDATES.add(candidate)
    except DiscoveryFault as caught:
        fault = caught
    except Exception:
        fault = DiscoveryFault("discovery_operational_error")
    if fault is not None:
        raise _clean_fault(fault)
    if result is None:  # Defensive; the branch is unreachable.
        raise DiscoveryFault("unexpected_discovery_error")
    return result


def _read_candidate_bytes_impl(
    candidate: LocalTexCandidate, max_bytes: int
) -> bytes:
    """Read a selected candidate after no-follow and identity revalidation."""

    if type(max_bytes) is not int or max_bytes <= 0:
        raise DiscoveryFault("read_limit_invalid")
    if candidate.device == 0 or candidate.inode == 0:
        raise DiscoveryFault("candidate_identity_unavailable")
    if candidate.link_count != 1:
        raise DiscoveryFault("candidate_hardlink_rejected")
    if (
        type(candidate.content_authenticator) is not bytes
        or len(candidate.content_authenticator) != hashlib.sha256().digest_size
    ):
        raise DiscoveryFault("candidate_attestation_invalid")
    path = candidate.path
    root = candidate.source.root
    if _path_chain_has_link(path) or _link(path):
        raise DiscoveryFault("candidate_link_boundary")
    try:
        resolved = path.resolve(strict=True)
        before = path.lstat()
    except OSError as exc:
        raise DiscoveryFault("candidate_unreachable") from None
    _require_stable_identity(before)
    if resolved != path or not _inside(resolved, root) or not _same_candidate(
        candidate, before
    ):
        raise DiscoveryFault("candidate_identity_changed")
    if candidate.size_bytes > max_bytes:
        raise DiscoveryFault("candidate_size_limit")

    flags = os.O_RDONLY
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise DiscoveryFault("candidate_open_failed") from None
    try:
        opened = os.fstat(descriptor)
        _require_stable_identity(opened)
        if not _same_candidate(candidate, opened):
            raise DiscoveryFault("candidate_identity_changed")
        chunks: list[bytes] = []
        remaining = max_bytes + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        if len(data) > max_bytes:
            raise DiscoveryFault("candidate_size_limit")
        reread = os.fstat(descriptor)
        _require_stable_identity(reread)
        if not _same_candidate(candidate, reread):
            raise DiscoveryFault("candidate_identity_changed")
    finally:
        os.close(descriptor)
    try:
        after = path.lstat()
    except OSError as exc:
        raise DiscoveryFault("candidate_identity_changed") from None
    _require_stable_identity(after)
    if not _same_candidate(candidate, after) or len(data) != candidate.size_bytes:
        raise DiscoveryFault("candidate_identity_changed")
    observed_authenticator = hmac.new(
        _ATTESTATION_KEY, data, hashlib.sha256
    ).digest()
    if not hmac.compare_digest(
        observed_authenticator, candidate.content_authenticator
    ):
        raise DiscoveryFault("candidate_identity_changed")
    return data


def read_candidate_bytes(candidate: LocalTexCandidate, max_bytes: int) -> bytes:
    """Read a candidate and expose only a detached sanitized fault."""

    fault: DiscoveryFault | None = None
    try:
        if (
            not isinstance(candidate, LocalTexCandidate)
            or candidate not in _ATTESTED_CANDIDATES
        ):
            raise DiscoveryFault("candidate_attestation_invalid")
        return _read_candidate_bytes_impl(candidate, max_bytes)
    except DiscoveryFault as caught:
        fault = caught
    except Exception:
        fault = DiscoveryFault("candidate_read_operational_error")
    if fault is None:  # Defensive; the branch is unreachable.
        raise DiscoveryFault("unexpected_discovery_error")
    raise _clean_fault(fault)
