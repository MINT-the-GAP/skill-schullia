#!/usr/bin/env python3
"""Read-only Git leak gate for the optional local orientation overlay.

The gate checks index blobs, tracked working-tree files, and untracked
non-ignored candidates. It never walks ignored local source trees and never
prints matched values or private filenames.

Exit codes: 0 clean, 1 potential leak, 2 operational error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent.parent
RESERVED_PREFIX = ".schullia-local"
FORBIDDEN_SOURCE_SUFFIXES = {".tex", ".ltx", ".sty", ".cls", ".bib"}
LOCAL_ARTIFACT_SUFFIXES = {
    ".cache", ".db", ".jsonl", ".log", ".manifest", ".sqlite", ".sqlite3"
}
LOCAL_MARKERS = {
    "local-orientation", "local_orientation", "schullia-local", "schullia_local"
}
PUBLIC_LOCAL_JSON_PATHS = frozenset({
    'references/local-orientation-near-copy-policy.json',
    "references/local-orientation-feature-taxonomy.json",
})

# The token boundary prevents URL schemes such as https:// from being
# mistaken for Windows drive paths.
WINDOWS_PATH = re.compile(r"(?<![A-Za-z0-9+.-])[A-Za-z]:[\\/](?![\\/])")
UNC_PATH = re.compile(
    r"(?<![\\])\\\\(?![\\])"
    r"[A-Za-z0-9][A-Za-z0-9._$-]{0,254}"
    r"[\\/](?![\\/])"
    r"[A-Za-z0-9][A-Za-z0-9._$ -]{0,254}"
)
HOME_PATH = re.compile(
    r"(?<![A-Za-z0-9._-])/(?:private/)?"
    r"(?:(?:Users|home)/[^/\s\x00]+|root)(?:/|$)",
    re.IGNORECASE,
)
WSL_HOME_PATH = re.compile(
    r"(?<![A-Za-z0-9._-])/[m]nt/[A-Za-z]/[U]sers/[^/\s\x00]+(?:/|$)",
    re.IGNORECASE,
)
POSIX_LOCAL_PATH = re.compile(
    r"(?<![A-Za-z0-9._~:/-])/(?:[s]rv|[o]pt|[v]ar|[V]olumes|[m]edia|[m]nt)"
    r"/[^/\s\x00]+(?:/|$)",
    re.IGNORECASE,
)
FILE_URI = re.compile(
    r"file:/+(?:[A-Za-z]:/|(?:private/)?(?:Users|home)/|root(?:/|$)|"
    r"(?:[s]rv|[o]pt|[v]ar|[V]olumes|[m]edia|[m]nt)/)",
    re.IGNORECASE,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class GateError(RuntimeError):
    """Sanitized operational failure."""


@dataclass(frozen=True)
class GateReport:
    findings: Mapping[str, int]

    @property
    def clean(self) -> bool:
        return not self.findings

    def as_dict(self) -> dict[str, object]:
        return {
            "status": "clean" if self.clean else "potential_leak",
            "findings": dict(sorted(self.findings.items())),
            "total": sum(self.findings.values()),
        }


@dataclass(frozen=True)
class IndexEntry:
    mode: str
    object_id: str
    path: str


def _git(repo: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise GateError("git_unavailable") from exc
    if result.returncode:
        raise GateError("git_command_failed")
    return result.stdout


def _decode_path(value: bytes) -> str:
    return value.decode("utf-8", errors="surrogateescape")


def _index_entries(raw: bytes) -> list[IndexEntry]:
    output = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, encoded_path = record.split(b"\t", 1)
            mode, object_id, _stage = metadata.decode("ascii").split(" ", 2)
        except (ValueError, UnicodeDecodeError) as exc:
            raise GateError("git_index_unreadable") from exc
        output.append(IndexEntry(mode, object_id, _decode_path(encoded_path)))
    return output


def _nul_paths(raw: bytes) -> list[str]:
    return [_decode_path(item) for item in raw.split(b"\0") if item]


def _relative(value: str) -> PurePosixPath | None:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts:
        return None
    if any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path


def _path_findings(value: str) -> set[str]:
    path = _relative(value)
    if path is None:
        return {"unsafe_git_path"}
    findings = set()
    folded_parts = tuple(part.casefold() for part in path.parts)
    folded = "/".join(folded_parts)
    suffix = PurePosixPath(path.name).suffix.casefold()
    if folded_parts[0] == RESERVED_PREFIX:
        findings.add("reserved_local_path")
    if suffix in FORBIDDEN_SOURCE_SUFFIXES:
        findings.add("private_source_extension")
    if suffix in LOCAL_ARTIFACT_SUFFIXES and any(mark in folded for mark in LOCAL_MARKERS):
        findings.add("local_runtime_artifact")
    if (
        suffix == ".json"
        and not path.name.casefold().endswith(".schema.json")
        and folded not in PUBLIC_LOCAL_JSON_PATHS
        and any(mark in folded for mark in LOCAL_MARKERS)
    ):
        findings.add("local_configuration_artifact")
    return findings


def _reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _link(path: Path) -> bool:
    try:
        if path.is_symlink() or _reparse(path):
            return True
        isjunction = getattr(os.path, "isjunction", None)
        return bool(isjunction and isjunction(path))
    except OSError:
        return True


def _link_parent(repo: Path, relative: PurePosixPath) -> bool:
    current = repo
    for part in relative.parts[:-1]:
        current = current / part
        if _link(current):
            return True
    return False


def _config_needles(
    repo: Path, config: Path | None, environ: Mapping[str, str] | None
) -> list[str]:
    try:
        from local_orientation_config import private_config_needles  # type: ignore
        loader = private_config_needles
    except (ImportError, AttributeError):
        try:
            from local_orientation_config import private_root_needles  # type: ignore
            loader = private_root_needles
        except (ImportError, AttributeError):
            return []
    try:
        values = loader(repo, config, environ)
    except Exception:
        return []
    return [value for value in values if isinstance(value, str) and len(value) >= 4]


def _needles(values: Iterable[str]) -> tuple[tuple[str, ...], tuple[bytes, ...]]:
    text_values: set[str] = set()
    byte_values: set[bytes] = set()
    for value in values:
        stripped = value.strip().rstrip("/\\")
        if len(stripped) < 4:
            continue
        slash = stripped.replace("\\", "/")
        backslash = stripped.replace("/", "\\")
        for candidate in {
            stripped,
            slash,
            backslash,
            backslash.replace("\\", "\\\\"),
        }:
            folded = candidate.casefold()
            text_values.add(folded)
            for encoding in ("utf-8", "utf-16-le", "utf-16-be"):
                byte_values.add(candidate.encode(encoding, errors="ignore"))
                byte_values.add(folded.encode(encoding, errors="ignore"))
    return tuple(sorted(text_values)), tuple(sorted(byte_values))


def _textual(data: bytes) -> bool:
    sample = data[:8192]
    if not sample:
        return True
    if b"\0" in sample:
        return False
    controls = sum(byte < 9 or 13 < byte < 32 for byte in sample)
    return controls / len(sample) < 0.05


def _contains_absolute_private_path(text: str) -> bool:
    separator_decoded = re.sub(
        r"\\u002f", "/", text, flags=re.IGNORECASE
    )
    separator_decoded = re.sub(
        r"\\u005c", lambda _match: "\\", separator_decoded,
        flags=re.IGNORECASE,
    )
    candidates = set()
    for value in (text, separator_decoded):
        collapsed_backslashes = value.replace("\\\\", "\\")
        candidates.update({
            value,
            collapsed_backslashes,
            value.replace("\\/", "/"),
            collapsed_backslashes.replace("\\/", "/"),
        })
    return any(
        WINDOWS_PATH.search(candidate)
        or UNC_PATH.search(candidate)
        or HOME_PATH.search(candidate)
        or WSL_HOME_PATH.search(candidate)
        or POSIX_LOCAL_PATH.search(candidate)
        or FILE_URI.search(candidate)
        for candidate in candidates
    )


def _content_findings(
    data: bytes, text_needles: Sequence[str], byte_needles: Sequence[bytes]
) -> set[str]:
    findings = set()
    lowered = data.lower()
    if any(needle and (needle in data or needle.lower() in lowered) for needle in byte_needles):
        findings.add("configured_private_value")
    path_views = [data.decode("utf-8", errors="ignore")]
    if b"\x00" in data:
        path_views.extend((
            data.decode("utf-16-le", errors="ignore"),
            data.decode("utf-16-be", errors="ignore"),
        ))
    if any(_contains_absolute_private_path(value) for value in path_views):
        findings.add("absolute_private_path")
    if not _textual(data):
        return findings
    text = data.decode("utf-8-sig", errors="replace")
    folded = text.casefold()
    if any(needle in folded for needle in text_needles):
        findings.add("configured_private_value")
    if _contains_absolute_private_path(text):
        findings.add("absolute_private_path")
    return findings


def _link_findings(relative: PurePosixPath, target: bytes) -> set[str]:
    findings = set()
    text = target.decode("utf-8", errors="surrogateescape")
    if _contains_absolute_private_path(text) or text.startswith("/"):
        findings.add("external_link_target")
    parts = PurePosixPath(text.replace("\\", "/")).parts
    if RESERVED_PREFIX in {part.casefold() for part in parts}:
        findings.add("local_link_target")
    depth = len(relative.parent.parts)
    for part in parts:
        if part == "..":
            depth -= 1
        elif part not in {"", "."}:
            depth += 1
        if depth < 0:
            findings.add("external_link_target")
            break
    return findings


def _worktree_data(repo: Path, value: str) -> tuple[bytes | None, set[str]]:
    relative = _relative(value)
    if relative is None:
        return None, {"unsafe_git_path"}
    if _link_parent(repo, relative):
        return None, {"link_boundary"}
    path = repo.joinpath(*relative.parts)
    try:
        if path.is_symlink() or _reparse(path):
            target = os.fsencode(os.readlink(path))
            return target, _link_findings(relative, target)
        if path.is_file():
            return path.read_bytes(), set()
        return None, set()
    except OSError:
        return None, {"unreadable_candidate"}


def scan_repository(
    repo_root: Path,
    *,
    explicit_config: Path | None = None,
    environ: Mapping[str, str] | None = None,
    private_needles: Iterable[str] | None = None,
) -> GateReport:
    """Inspect Git candidates without mutating Git or the filesystem."""
    repo = repo_root.resolve()
    top = Path(
        _git(repo, "rev-parse", "--show-toplevel").decode("utf-8", errors="replace").strip()
    ).resolve()
    if top != repo:
        raise GateError("repository_root_mismatch")

    values = list(private_needles) if private_needles is not None else _config_needles(
        repo, explicit_config, environ
    )
    text_needles, byte_needles = _needles(values)
    findings: Counter[str] = Counter()

    cache: dict[str, bytes] = {}
    for entry in _index_entries(_git(repo, "ls-files", "-z", "--stage")):
        findings.update(_path_findings(entry.path))
        if entry.mode == "160000":
            continue
        data = cache.get(entry.object_id)
        if data is None:
            data = _git(repo, "cat-file", "blob", entry.object_id)
            cache[entry.object_id] = data
        findings.update(_content_findings(data, text_needles, byte_needles))
        if entry.mode == "120000":
            relative = _relative(entry.path)
            if relative is not None:
                findings.update(_link_findings(relative, data))

    tracked = _nul_paths(_git(repo, "ls-files", "-z"))
    untracked = _nul_paths(_git(repo, "ls-files", "-z", "--others", "--exclude-standard"))
    for value in tracked + untracked:
        findings.update(_path_findings(value))
        data, extra = _worktree_data(repo, value)
        findings.update(extra)
        if data is not None:
            findings.update(_content_findings(data, text_needles, byte_needles))

    return GateReport(dict(findings))


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, _message):
        raise GateError("arguments_invalid")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args(argv)


def _print(report: GateReport, as_json: bool) -> None:
    payload = report.as_dict()
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    elif report.clean:
        print("OK local_orientation_leak_gate clean")
    else:
        print(f"ERROR local_orientation_leak_gate potential_leak total={payload['total']}")
        for category, count in sorted(report.findings.items()):
            print(f"ERROR {category} count={count}")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        report = scan_repository(
            args.repo_root, explicit_config=args.config, environ=os.environ
        )
    except GateError as exc:
        payload = {"status": "error", "error_code": str(exc)}
        if "args" in locals() and args.as_json:
            print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        else:
            print(f"ERROR local_orientation_leak_gate {exc}", file=sys.stderr)
        return 2
    except Exception:
        payload = {"status": "error", "error_code": "unexpected_gate_error"}
        if args.as_json:
            print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        else:
            print("ERROR local_orientation_leak_gate unexpected_gate_error", file=sys.stderr)
        return 2
    _print(report, args.as_json)
    return 0 if report.clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
