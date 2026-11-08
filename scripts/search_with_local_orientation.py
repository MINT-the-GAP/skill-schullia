#!/usr/bin/env python3
"""Explicit public/local federation with distinct provenance and output surfaces."""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import stat
import time
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Sequence
from urllib.parse import quote

from search_local_orientation import (
    ROOT, STATE_NOT_CONFIGURED, LocalSearchResult, SafeArgumentParser, SearchFault,
    SearchLimits, filters_from_args, search_local_orientation,
)

_PUBLIC_REASON_RULES = MappingProxyType({
    "public_search_complete": True,
    "public_output_limited": True,
    "public_not_requested": False,
    "public_index_missing": False,
    "public_query_invalid": False,
    "public_filter_invalid": False,
    "public_index_boundary_invalid": False,
    "public_search_time_limit": False,
    "public_search_operational_error": False,
    "scope_invalid": False,
    "search_limits_invalid": False,
    "arguments_invalid": False,
    "federation_operational_error": False,
})


def _freeze_public_value(value):
    if type(value) is dict:
        return MappingProxyType({
            key: _freeze_public_value(item) for key, item in value.items()
        })
    if type(value) in (list, tuple):
        return tuple(_freeze_public_value(item) for item in value)
    if value is None or type(value) in (str, int, float, bool):
        return value
    raise SearchFault("federated_result_invalid")


def _thaw_public_value(value):
    if isinstance(value, Mapping):
        return {key: _thaw_public_value(item) for key, item in value.items()}
    if type(value) is tuple:
        return [_thaw_public_value(item) for item in value]
    return value


class FederatedSearchResult:
    __slots__ = (
        "scope", "_public_results", "public_reason_code",
        "public_search_performed", "local", "_sealed",
    )

    def __init__(self, scope, public_results=(), public_reason_code="public_not_requested",
                 public_search_performed=False, local=None):
        result_values = tuple(public_results)
        expected_performed = _PUBLIC_REASON_RULES.get(public_reason_code)
        local_value = local or LocalSearchResult(
            availability_state=STATE_NOT_CONFIGURED,
            reason_code="local_not_requested",
        )
        if (scope not in {"public", "local", "both"}
                or expected_performed is None
                or type(public_search_performed) is not bool
                or public_search_performed is not expected_performed
                or (not public_search_performed and result_values)
                or not isinstance(local_value, LocalSearchResult)):
            raise SearchFault("federated_result_invalid")
        object.__setattr__(self, "scope", scope)
        object.__setattr__(
            self, "_public_results",
            tuple(_freeze_public_value(item) for item in result_values),
        )
        object.__setattr__(self, "public_reason_code", public_reason_code)
        object.__setattr__(
            self, "public_search_performed", public_search_performed
        )
        object.__setattr__(
            self, "local", local_value,
        )
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("federated_search_result_immutable")
        object.__setattr__(self, name, value)

    def __repr__(self):
        return "FederatedSearchResult(<separate-result-groups>)"

    @property
    def public_results(self):
        return tuple(
            _thaw_public_value(item) for item in self._public_results
        )

    def as_dict(self):
        return {
            "scope": self.scope,
            "public": {"reason_code": self.public_reason_code,
                       "public_search_performed": self.public_search_performed,
                       "results": list(self.public_results)},
            "local": self.local.as_dict(),
        }


def _link_like(path: Path) -> bool:
    try:
        metadata = path.lstat()
        attributes = getattr(metadata, "st_file_attributes", 0)
        junction = getattr(os.path, "isjunction", None)
        return bool(
            path.is_symlink()
            or attributes
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
            or (junction and junction(path))
        )
    except FileNotFoundError:
        raise
    except OSError:
        raise SearchFault("public_index_boundary_invalid") from None


def _inside(path: Path, root: Path) -> bool:
    try:
        candidate = os.path.normcase(os.path.abspath(os.fspath(path)))
        parent = os.path.normcase(os.path.abspath(os.fspath(root)))
        return os.path.commonpath((candidate, parent)) == parent
    except (OSError, ValueError):
        return False


def _contains_private_zone_alias(path: Path) -> bool:
    """Recognize Win32 spelling aliases for the private control zone."""
    return any(
        part.rstrip(" .").casefold() == ".schullia-local"
        for part in re.split(r"[\\\\/]+", os.fspath(path))
        if part
    )


def _windows_final_path(path: Path, *, directory: bool) -> str:
    """Return the handle-resolved name, expanding aliases on Windows."""
    if os.name != "nt":
        return os.fspath(path.resolve(strict=True))
    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        create_file = kernel32.CreateFileW
        create_file.argtypes = (
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
            wintypes.HANDLE,
        )
        create_file.restype = wintypes.HANDLE
        get_final = kernel32.GetFinalPathNameByHandleW
        get_final.argtypes = (
            wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD,
        )
        get_final.restype = wintypes.DWORD
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = (wintypes.HANDLE,)
        close_handle.restype = wintypes.BOOL

        flags = 0x02000000 if directory else 0
        handle = create_file(
            os.fspath(path), 0x80, 0x1 | 0x2 | 0x4,
            None, 3, flags, None,
        )
        invalid_handle = ctypes.c_void_p(-1).value
        if handle in (None, invalid_handle):
            raise OSError
        try:
            buffer = ctypes.create_unicode_buffer(32768)
            length = get_final(handle, buffer, len(buffer), 0)
            if not length or length >= len(buffer):
                raise OSError
            return buffer.value
        finally:
            close_handle(handle)
    except (AttributeError, OSError, TypeError, ValueError):
        raise SearchFault("public_index_boundary_invalid") from None


def _reject_private_zone_alias(
    path: Path, *, resolved: Path | None = None, directory: bool
) -> None:
    try:
        canonical = resolved or path.resolve(strict=True)
        names = (
            os.fspath(path),
            os.fspath(canonical),
            _windows_final_path(path, directory=directory),
        )
    except OSError:
        raise SearchFault("public_index_boundary_invalid") from None
    if any(_contains_private_zone_alias(Path(name)) for name in names):
        raise SearchFault("public_index_boundary_invalid")


def _public_index_signature(metadata: os.stat_result):
    if (
        not stat.S_ISREG(metadata.st_mode)
        or int(metadata.st_dev) == 0
        or int(metadata.st_ino) == 0
        or int(metadata.st_nlink) != 1
        or int(metadata.st_size) <= 0
    ):
        raise SearchFault("public_index_boundary_invalid")
    return (
        int(metadata.st_dev),
        int(metadata.st_ino),
        int(metadata.st_nlink),
        int(metadata.st_size),
        int(metadata.st_mtime_ns),
    )


def _validated_public_index(repo_root: Path, corpus: Path):
    repo = Path(repo_root).absolute()
    if not repo.exists():
        raise FileNotFoundError
    if _link_like(repo):
        raise SearchFault("public_index_boundary_invalid")
    try:
        resolved_repo = repo.resolve(strict=True)
    except OSError:
        raise SearchFault("public_index_boundary_invalid") from None
    _reject_private_zone_alias(
        repo, resolved=resolved_repo, directory=True
    )

    selected = Path(corpus)
    if not selected.is_absolute():
        selected = repo / selected
    selected = selected.absolute()
    if not _inside(selected, repo):
        raise SearchFault("public_index_boundary_invalid")
    try:
        relative = selected.relative_to(repo)
    except ValueError:
        raise SearchFault("public_index_boundary_invalid") from None
    current = repo
    for part in relative.parts:
        current /= part
        if not current.exists():
            raise FileNotFoundError
        if _link_like(current):
            raise SearchFault("public_index_boundary_invalid")
    try:
        resolved_corpus = selected.resolve(strict=True)
        metadata = selected.lstat()
    except OSError:
        raise SearchFault("public_index_boundary_invalid") from None
    _reject_private_zone_alias(
        selected, resolved=resolved_corpus, directory=True
    )
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or not _inside(resolved_corpus, resolved_repo)
    ):
        raise SearchFault("public_index_boundary_invalid")

    index = selected / "index.sqlite"
    if not index.exists():
        raise FileNotFoundError
    if _link_like(index):
        raise SearchFault("public_index_boundary_invalid")
    try:
        resolved_index = index.resolve(strict=True)
        signature = _public_index_signature(index.lstat())
    except OSError:
        raise SearchFault("public_index_boundary_invalid") from None
    _reject_private_zone_alias(
        index, resolved=resolved_index, directory=False
    )
    if (
        not _inside(resolved_index, resolved_corpus)
        or os.path.normcase(os.path.abspath(os.fspath(resolved_index)))
        != os.path.normcase(os.path.abspath(os.fspath(index)))
    ):
        raise SearchFault("public_index_boundary_invalid")
    return index, signature


def _verify_public_index(index: Path, expected) -> None:
    if _link_like(index):
        raise SearchFault("public_index_boundary_invalid")
    _reject_private_zone_alias(index, directory=False)
    try:
        observed = _public_index_signature(index.lstat())
    except OSError:
        raise SearchFault("public_index_boundary_invalid") from None
    if observed != expected:
        raise SearchFault("public_index_boundary_invalid")


def _readonly_public_connection(index: Path) -> sqlite3.Connection:
    value = quote(index.absolute().as_posix(), safe="/:")
    if value.startswith("//"):
        uris = (
            "file://///" + value.lstrip("/") + "?mode=ro&immutable=1",
            "file://localhost/" + value + "?mode=ro&immutable=1",
            "file:" + value.replace("//", "////", 1)
            + "?mode=ro&immutable=1",
        )
    else:
        uris = ("file:" + value + "?mode=ro&immutable=1",)
    for uri in uris:
        try:
            connection = sqlite3.connect(uri, uri=True)
            connection.row_factory = sqlite3.Row
            return connection
        except sqlite3.Error:
            continue
    raise SearchFault("public_search_operational_error")


def _public_search(repo_root, corpus, query, *, limit, item_types, operator,
                   max_chars):
    """Reuse public query/hydration code over a strictly read-only connection."""
    connection = None
    try:
        import search_knowledge as public
        if not isinstance(query, str) or len(query) > 512:
            raise SearchFault("public_query_invalid")
        types = list(item_types) if item_types is not None else None
        if types is not None and (not 1 <= len(types) <= len(public.VALID_TYPES)
                                  or any(item not in public.VALID_TYPES for item in types)):
            raise SearchFault("public_filter_invalid")
        if operator is not None and (not isinstance(operator, str) or len(operator) > 80):
            raise SearchFault("public_filter_invalid")
        path = Path(corpus)
        if _contains_private_zone_alias(path):
            raise SearchFault("public_index_boundary_invalid")
        index, signature = _validated_public_index(repo_root, path)
        deadline = time.monotonic() + 10.0
        connection = _readonly_public_connection(index)
        _verify_public_index(index, signature)
        connection.execute("PRAGMA query_only=ON")
        connection.execute("PRAGMA trusted_schema=OFF")
        connection.enable_load_extension(False)
        connection.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        args = argparse.Namespace(query=query, type=types, source=None, path=None,
                                  operator=operator, quiz_type=None, usage_context=None,
                                  literal=False, limit=limit)
        rows = public.search_rows(connection, args)
        result, used = [], 0
        reason = "public_search_complete"
        for row in rows:
            if time.monotonic() > deadline:
                raise SearchFault("public_search_time_limit")
            details = public.hydrate(connection, row["item_type"], row["item_id"])
            if not public.passes_structured_filters(details, args):
                continue
            item = {
                "item_id": row["item_id"], "item_type": row["item_type"],
                "source_id": row["source_id"], "path": row["path"], "title": row["title"],
                "snippet": re.sub(r"\s+", " ", row["snippet"] or "").strip(),
                "details": details,
                "provenance": public.provenance(connection, row["item_type"], row["item_id"]),
            }
            encoded = json.dumps(item, ensure_ascii=True, sort_keys=True)
            if used + len(encoded) > max_chars:
                reason = "public_output_limited"
                break
            result.append(item)
            used += len(encoded)
            if len(result) >= limit:
                break
        _verify_public_index(index, signature)
        return tuple(result), reason, True
    except FileNotFoundError:
        return (), "public_index_missing", False
    except SearchFault as fault:
        return (), fault.code, False
    except Exception:
        return (), "public_search_operational_error", False
    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass


def search_with_local_orientation(repo_root: Path = ROOT, *, scope="public",
                                  corpus: Path | None = None, public_query="",
                                  public_types=None, public_operator=None,
                                  explicit_config: Path | None = None,
                                  environ: Mapping[str, str] | None = None,
                                  local_filters=None, limit=8,
                                  limits: SearchLimits | None = None):
    """Public is the default; private configuration is touched only for local/both."""
    if not isinstance(scope, str) or scope not in {"public", "local", "both"}:
        return FederatedSearchResult("public", public_reason_code="scope_invalid")
    try:
        bounds = limits or SearchLimits()
        if not isinstance(bounds, SearchLimits) or type(limit) is not int or not 1 <= limit <= bounds.max_results:
            raise SearchFault("search_result_limit_invalid")
    except Exception:
        return FederatedSearchResult(scope, public_reason_code="search_limits_invalid")
    results, reason, performed = (), "public_not_requested", False
    if scope in {"public", "both"}:
        try:
            results, reason, performed = _public_search(
                repo_root,
                Path(repo_root) / "corpus" if corpus is None else corpus,
                public_query, limit=limit, item_types=public_types,
                operator=public_operator, max_chars=max(1, bounds.max_output_chars - 1200))
        except Exception:
            results, reason, performed = (), "public_search_operational_error", False
    local = None
    if scope in {"local", "both"}:
        try:
            local = search_local_orientation(
                repo_root, explicit_config=explicit_config, environ=environ,
                filters=local_filters, limit=limit, limits=bounds)
        except Exception:
            # No local exception can prevent delivery of public results.
            local = LocalSearchResult(reason_code="search_operational_error")
    result = FederatedSearchResult(scope, results, reason, performed, local)
    # Hard total output cap includes the wrapper and console-safe local projection.
    if len(json.dumps(result.as_dict(), ensure_ascii=True, sort_keys=True)) > bounds.max_output_chars:
        return FederatedSearchResult(
            scope, (), "public_output_limited", performed, local
        )
    return result


def parse_args(argv: Sequence[str] | None = None):
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument("public_query", nargs="?", default="")
    parser.add_argument("--scope", choices=("public", "local", "both"), default="public")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--type", action="append", dest="public_types")
    parser.add_argument("--operator", dest="public_operator")
    for key in ("subject", "learner-group", "document-type", "operator", "solution-presence",
                "solution-assignment", "response-shape", "suitability", "topic", "query", "archive-status",
                "topic-id", "task-family", "learning-action", "response-form", "solution-form",
                "number-profile", "context-profile", "representation", "complexity-band"):
        parser.add_argument("--local-" + key, dest=key.replace("-", "_"))
    for key in ("grade", "min-subtasks", "min-tasks", "max-tasks", "modified-after-ns"):
        parser.add_argument("--local-" + key, type=int, dest=key.replace("-", "_"))
    parser.add_argument("--local-has-warnings", choices=("yes", "no"), dest="has_warnings")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None):
    try:
        args = parse_args(argv)
        result = search_with_local_orientation(
            args.repo_root, scope=args.scope, corpus=args.corpus, public_query=args.public_query,
            public_types=args.public_types, public_operator=args.public_operator,
            explicit_config=args.config, local_filters=filters_from_args(args), limit=args.limit)
    except SearchFault:
        result = FederatedSearchResult("public", public_reason_code="arguments_invalid")
    except Exception:
        result = FederatedSearchResult("public", public_reason_code="federation_operational_error")
    print(json.dumps(result.as_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.public_search_performed or result.local.local_search_performed else 1


if __name__ == "__main__":
    raise SystemExit(main())
