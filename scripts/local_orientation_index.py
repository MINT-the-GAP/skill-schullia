#!/usr/bin/env python3
"""Explicit, bounded local metadata builds and read-only freshness validation.

SQLite is used only in memory. Its serialized bytes cross a descriptor-bound
filesystem boundary; SQLite never opens a source, state pathname, or sidecar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import sqlite3
import stat
import time
from typing import Mapping
import uuid

import local_orientation_candidates as selector
import local_orientation_config as config
import local_orientation_includes as includes
import local_orientation_tex as tex
from local_orientation_metadata import (
    MetadataFault, canonical_json, decode_json, validate_metadata,
    MAX_DOCUMENT_JSON_BYTES,
)


ROOT = Path(__file__).resolve().parents[1]
INDEX_VERSION = 2
INDEX_FILENAME = "orientation.sqlite"
LOCK_FILENAME = "build.lock"
GRAPH_WARNINGS = frozenset({
    "include_reference_unsupported", "include_target_not_allowlisted",
    "include_cycle",
})


class IndexFault(RuntimeError):
    def __init__(self, code: str, state: str = config.STATE_EXCLUDED):
        self.code, self.state = code, state
        super().__init__(code)


@dataclass(frozen=True)
class IndexLimits:
    max_documents: int = 512
    max_file_bytes: int = 4 * 1024 * 1024
    max_total_bytes: int = 32 * 1024 * 1024
    max_index_bytes: int = 64 * 1024 * 1024
    max_edges: int = 2048
    max_depth: int = 32
    max_seconds: float = 30.0

    def __post_init__(self):
        for name, maximum in {
            "max_documents": 512, "max_file_bytes": 4 * 1024 * 1024,
            "max_total_bytes": 32 * 1024 * 1024,
            "max_index_bytes": 64 * 1024 * 1024, "max_edges": 2048,
            "max_depth": 32,
        }.items():
            value = getattr(self, name)
            if type(value) is not int or not 0 < value <= maximum:
                raise ValueError("index_limits_invalid")
        if (type(self.max_seconds) not in {int, float}
                or not 0 < self.max_seconds <= 30
                or self.max_file_bytes > self.max_total_bytes):
            raise ValueError("index_limits_invalid")


@dataclass(frozen=True)
class BuildResult:
    availability_state: str = config.STATE_AVAILABLE
    reason_code: str = "index_built"
    index_ready: bool = True

    def safe_dict(self) -> dict[str, object]:
        return {
            "availability_state": self.availability_state,
            "reason_code": self.reason_code,
            "index_ready": self.index_ready,
            "local_search_performed": False,
            "orientation_profile_prepared": False,
            "local_orientation_used": False,
        }


@dataclass(frozen=True, repr=False)
class IndexSnapshot:
    documents: tuple[dict[str, object], ...] = field(repr=False)
    edges: tuple[tuple[str, str, str], ...] = field(repr=False)
    warning_codes: tuple[str, ...] = field(repr=False)
    index_ready: bool = True

    def __repr__(self):
        return "IndexSnapshot(<local-only>)"


def _check_time(deadline):
    if time.monotonic() > deadline:
        raise IndexFault("index_time_limit")


def _identity(metadata, *, regular=False):
    if int(metadata.st_dev) == 0 or int(metadata.st_ino) == 0:
        raise IndexFault("state_identity_unavailable")
    if regular and (not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1):
        raise IndexFault("state_file_invalid")
    return (int(metadata.st_dev), int(metadata.st_ino))


def _file_signature(metadata):
    _identity(metadata, regular=True)
    return (_identity(metadata), metadata.st_size, metadata.st_mtime_ns,
            metadata.st_nlink)


def _directory_stamp(path):
    metadata = path.lstat()
    if selector._entry_link(path, metadata) or not stat.S_ISDIR(metadata.st_mode):
        raise IndexFault("state_directory_invalid")
    return _identity(metadata)


def _directory_chain(path):
    absolute = path.absolute()
    parts = absolute.parts
    if not parts:
        raise IndexFault("state_directory_invalid")
    current = Path(parts[0])
    result = [(current, _directory_stamp(current))]
    for part in parts[1:]:
        current = current / part
        result.append((current, _directory_stamp(current)))
    return tuple(result)


def _verify_chain(chain):
    for path, expected in chain:
        if _directory_stamp(path) != expected:
            raise IndexFault("state_directory_changed")


def _windows_relative_handle(parent_handle, name, *, access, disposition,
                             directory=False):
    """Native relative open: never re-resolve a mutable state parent pathname."""
    import ctypes
    from ctypes import wintypes
    class UnicodeString(ctypes.Structure):
        _fields_ = [("length", wintypes.USHORT), ("maximum", wintypes.USHORT),
                    ("buffer", wintypes.LPWSTR)]
    class ObjectAttributes(ctypes.Structure):
        _fields_ = [("length", wintypes.ULONG), ("root", wintypes.HANDLE),
                    ("name", ctypes.POINTER(UnicodeString)),
                    ("attributes", wintypes.ULONG), ("security", wintypes.LPVOID),
                    ("qos", wintypes.LPVOID)]
    class IOStatus(ctypes.Structure):
        _fields_ = [("status", ctypes.c_void_p), ("information", ctypes.c_size_t)]
    if not name or any(character in name for character in "/\\:") or name in {".", ".."}:
        raise IndexFault("state_boundary_escape")
    buffer = ctypes.create_unicode_buffer(name)
    unicode = UnicodeString(len(name.encode("utf-16-le")),
                            len(name.encode("utf-16-le")) + 2,
                            ctypes.cast(buffer, wintypes.LPWSTR))
    attributes = ObjectAttributes()
    attributes.length, attributes.root = ctypes.sizeof(attributes), parent_handle
    attributes.name = ctypes.pointer(unicode)
    attributes.attributes = 0x40 | 0x1000  # CASE_INSENSITIVE | DONT_REPARSE
    ios, handle = IOStatus(), wintypes.HANDLE()
    native = ctypes.WinDLL("ntdll", use_last_error=True)
    native.NtCreateFile.argtypes = (
        ctypes.POINTER(wintypes.HANDLE), wintypes.ULONG,
        ctypes.POINTER(ObjectAttributes), ctypes.POINTER(IOStatus),
        wintypes.LPVOID, wintypes.ULONG, wintypes.ULONG, wintypes.ULONG,
        wintypes.ULONG, wintypes.LPVOID, wintypes.ULONG,
    )
    native.NtCreateFile.restype = ctypes.c_long
    options = 0x00200000 | 0x20 | (1 if directory else 0x40)
    status = native.NtCreateFile(ctypes.byref(handle), access | 0x100000,
                                 ctypes.byref(attributes), ctypes.byref(ios), None,
                                 0x80, 0x3, disposition, options, None, 0)
    if status < 0:
        if status & 0xffffffff == 0xC0000035:
            raise FileExistsError()
        raise IndexFault("state_relative_open_failed")
    return handle.value


class _DirectoryLease:
    """Pin a directory before creating any descendant.

    Windows leases deny DELETE sharing, preventing parent rename. All child
    operations use RootDirectory/DONT_REPARSE against in-place reparse changes.
    POSIX operations additionally use the held dir_fd and
    O_NOFOLLOW instead of resolving a mutable absolute parent pathname.
    """

    def __init__(self, path, parent=None):
        self.handle = None
        self.descriptor = None
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.CreateFileW.argtypes = (
                wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
            )
            kernel.CreateFileW.restype = wintypes.HANDLE
            kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
            kernel.CloseHandle.restype = wintypes.BOOL
            # FILE_LIST_DIRECTORY|READ_ATTRIBUTES makes Windows enforce delete
            # sharing. Native relative opens handle in-place reparse changes.
            # OPEN_EXISTING, BACKUP_SEMANTICS|OPEN_REPARSE_POINT.
            if parent is None:
                handle = kernel.CreateFileW(str(path), 0x81, 0x3, None, 3,
                                            0x02000000 | 0x00200000, None)
                if handle == ctypes.c_void_p(-1).value:
                    raise IndexFault("state_directory_lease_unavailable")
            else:
                handle = _windows_relative_handle(
                    parent.handle, path.name, access=0x81, disposition=1,
                    directory=True)
            self.handle, self.kernel = handle, kernel
        else:
            if not (hasattr(os, "O_NOFOLLOW") and os.open in os.supports_dir_fd):
                raise IndexFault("state_directory_lease_unavailable")
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            if parent is None:
                self.descriptor = os.open(path, flags)
            else:
                self.descriptor = os.open(path.name, flags, dir_fd=parent.descriptor)

    def close(self):
        if self.handle is not None:
            self.kernel.CloseHandle(self.handle)
            self.handle = None
        if self.descriptor is not None:
            os.close(self.descriptor)
            self.descriptor = None


class _StateGuard:
    def __init__(self, repo_root: Path, *, create: bool):
        self.leases = []
        # POSIX dir_fd binds parents, but the stdlib cannot atomically bind an
        # unlink/rename to the expected leaf inode. Do not silently weaken the
        # mutation guarantee on unsupported platforms.
        if create and os.name != "nt":
            raise IndexFault("state_platform_unsupported", config.STATE_UNREACHABLE)
        self.repo = Path(repo_root).absolute()
        self.chain = _directory_chain(self.repo)
        self.state = self.repo / config.STATE_DIRECTORY
        try:
            for path, expected in self.chain:
                parent = self.leases[-1] if self.leases else None
                self.leases.append(_DirectoryLease(path, parent))
                if _directory_stamp(path) != expected:
                    raise IndexFault("state_directory_changed")
            # The local zone must be ignored even with an external configuration,
            # before any directory is created.
            if (config._git(self.repo, "check-ignore", "-q", "--",
                            config.STATE_DIRECTORY + "/" + INDEX_FILENAME).returncode != 0
                    or config._git(self.repo, "ls-files", "--",
                                   config.LOCAL_ZONE).stdout.strip()):
                raise IndexFault("state_repository_boundary")
            for part in (self.repo / config.LOCAL_ZONE, self.state):
                self.verify()
                if not part.exists():
                    if not create:
                        raise IndexFault("index_missing", config.STATE_UNREACHABLE)
                    if os.name == "nt":
                        handle = _windows_relative_handle(
                            self.leases[-1].handle, part.name, access=0x81,
                            disposition=2, directory=True)
                        self.leases[-1].kernel.CloseHandle(handle)
                    else:
                        os.mkdir(part.name, mode=0o700,
                                 dir_fd=self.leases[-1].descriptor)
                expected = _directory_stamp(part)
                self.leases.append(_DirectoryLease(part, self.leases[-1]))
                self.chain += ((part, expected),)
                self.verify()
            self.index = self.state / INDEX_FILENAME
            self.lock = self.state / LOCK_FILENAME
        except BaseException:
            self.close()
            raise

    def verify(self):
        _verify_chain(self.chain)

    def close(self):
        for lease in reversed(self.leases):
            lease.close()
        self.leases.clear()

    def __del__(self):
        self.close()

    def open_new(self, path):
        self.verify()
        if path.parent != self.state:
            raise IndexFault("state_boundary_escape")
        if os.name == "nt":
            return self.open_windows_child(path, create=True)
        return os.open(path.name, _open_flags(writable=True), 0o600,
                       dir_fd=self.leases[-1].descriptor)

    def open_windows_child(self, path, *, create=False, deleting=False):
        import msvcrt
        if path.parent != self.state:
            raise IndexFault("state_boundary_escape")
        access = 0x40000000 | 0x10000 | 0x80 if create else 0x10000 | 0x80 if deleting else 0x80000000
        handle = _windows_relative_handle(
            self.leases[-1].handle, path.name, access=access,
            disposition=2 if create else 1)
        return msvcrt.open_osfhandle(
            handle, (os.O_WRONLY if create else os.O_RDONLY)
            | getattr(os, "O_BINARY", 0))

    def open_existing(self, path):
        self.verify()
        if path.parent != self.state:
            raise IndexFault("state_boundary_escape")
        if os.name == "nt":
            return self.open_windows_child(path)
        return os.open(path.name, _open_flags(),
                       dir_fd=self.leases[-1].descriptor)

    def unlink_bound(self, path, expected_identity):
        self.verify()
        if os.name == "nt":
            descriptor = self.open_windows_child(path, deleting=True)
            try:
                _verify_bound_file(path, descriptor, expected_identity, self)
                _windows_delete_descriptor(descriptor, expected_identity)
            finally:
                os.close(descriptor)
        else:
            os.unlink(path.name, dir_fd=self.leases[-1].descriptor)

    def replace_bound(self, temporary, expected_identity):
        self.verify()
        if os.name == "nt":
            _rename_windows_bound(temporary, self, expected_identity)
        else:
            descriptor = self.leases[-1].descriptor
            os.replace(temporary.name, self.index.name,
                       src_dir_fd=descriptor, dst_dir_fd=descriptor)

    def existing_index_signature(self):
        self.verify()
        if not self.index.exists():
            if self.index.is_symlink():
                raise IndexFault("state_file_invalid")
            return None
        metadata = self.index.lstat()
        if selector._entry_link(self.index, metadata):
            raise IndexFault("state_file_invalid")
        return _file_signature(metadata)


def _rename_windows_bound(temporary, guard, expected):
    """Rename a child relative to the leased directory without reopening it.

    MoveFileEx would request a second writable parent handle and conflict with
    our read-only directory lease. NtSetInformationFile consumes the already
    leased RootDirectory handle, so the lease stays in force throughout.
    """
    import ctypes
    from ctypes import wintypes
    lease = guard.leases[-1]
    descriptor = guard.open_windows_child(temporary, deleting=True)
    try:
        import msvcrt
        handle = msvcrt.get_osfhandle(descriptor)
        _verify_bound_file(temporary, descriptor, expected, guard)
        name = INDEX_FILENAME
        class IOStatus(ctypes.Structure):
            _fields_ = [("status", ctypes.c_void_p), ("information", ctypes.c_size_t)]
        class RenameInfo(ctypes.Structure):
            _fields_ = [
                ("replace", wintypes.BOOLEAN), ("root", wintypes.HANDLE),
                ("length", wintypes.ULONG), ("name", wintypes.WCHAR * len(name)),
            ]
        info = RenameInfo()
        info.replace, info.root = 1, lease.handle
        info.length = len(name.encode("utf-16-le"))
        info.name = name
        ios = IOStatus()
        native = ctypes.WinDLL("ntdll", use_last_error=True)
        native.NtSetInformationFile.argtypes = (
            wintypes.HANDLE, ctypes.POINTER(IOStatus), wintypes.LPVOID,
            wintypes.ULONG, ctypes.c_int,
        )
        native.NtSetInformationFile.restype = ctypes.c_long
        length = RenameInfo.name.offset + info.length
        status = native.NtSetInformationFile(handle, ctypes.byref(ios),
                                             ctypes.byref(info), length, 10)
        if status < 0:
            raise IndexFault("index_publish_failed", config.STATE_UNREACHABLE)
    finally:
        os.close(descriptor)


def _windows_delete_descriptor(descriptor, expected_identity):
    import ctypes
    import msvcrt
    from ctypes import wintypes
    if _identity(os.fstat(descriptor), regular=True) != expected_identity:
        raise IndexFault("state_file_changed")
    class IOStatus(ctypes.Structure):
        _fields_ = [("status", ctypes.c_void_p), ("information", ctypes.c_size_t)]
    ios, disposition = IOStatus(), wintypes.BOOLEAN(1)
    native = ctypes.WinDLL("ntdll", use_last_error=True)
    native.NtSetInformationFile.argtypes = (
        wintypes.HANDLE, ctypes.POINTER(IOStatus), wintypes.LPVOID,
        wintypes.ULONG, ctypes.c_int,
    )
    native.NtSetInformationFile.restype = ctypes.c_long
    status = native.NtSetInformationFile(
        msvcrt.get_osfhandle(descriptor), ctypes.byref(ios),
        ctypes.byref(disposition), ctypes.sizeof(disposition), 13)
    if status < 0:
        raise IndexFault("state_delete_failed")


def _open_flags(writable=False):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL if writable else os.O_RDONLY
    return flags | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_BINARY", 0)


def _read_blob(path, maximum, deadline, verify, *, missing_code="index_missing",
               opener=None):
    verify()
    try:
        before = path.lstat()
    except FileNotFoundError:
        raise IndexFault(missing_code, config.STATE_UNREACHABLE) from None
    if selector._entry_link(path, before):
        raise IndexFault("state_file_invalid")
    signature = _file_signature(before)
    if not 0 <= before.st_size <= maximum:
        raise IndexFault("index_size_limit")
    descriptor = os.open(path, _open_flags()) if opener is None else opener(path)
    try:
        if _file_signature(os.fstat(descriptor)) != signature:
            raise IndexFault("state_file_changed")
        verify()
        chunks, remaining = [], maximum + 1
        while remaining:
            _check_time(deadline)
            chunk = os.read(descriptor, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        if len(data) > maximum:
            raise IndexFault("index_size_limit")
        if _file_signature(os.fstat(descriptor)) != signature:
            raise IndexFault("state_file_changed")
    finally:
        os.close(descriptor)
    verify()
    after = path.lstat()
    if (selector._entry_link(path, after)
            or _file_signature(after) != signature or len(data) != before.st_size):
        raise IndexFault("state_file_changed")
    return data, signature


def _configuration(repo_root, explicit_config, environ, deadline):
    repo = Path(repo_root).absolute()
    chain = _directory_chain(repo)
    path, _origin = config.discover_config(repo, explicit_config, environ)
    if path is None:
        raise IndexFault("configuration_absent", config.STATE_NOT_CONFIGURED)
    path = path.absolute()
    if not path.exists():
        raise IndexFault("configuration_unreachable", config.STATE_UNREACHABLE)
    config_chain = _directory_chain(path.parent)
    verify = lambda: (_verify_chain(chain), _verify_chain(config_chain))
    data, signature = _read_blob(path, 1_000_000, deadline, verify,
                                 missing_code="configuration_unreachable")
    # Duplicate JSON fields must not mean one thing to a fingerprint and
    # another to the pre-existing configuration validator.
    value = decode_json(data.decode("utf-8-sig"))
    result, sources = config.load_validated_sources(
        repo, explicit_config=path, environ={} if environ is None else environ)
    after, after_signature = _read_blob(path, 1_000_000, deadline, verify,
                                       missing_code="configuration_unreachable")
    if data != after or signature != after_signature:
        raise IndexFault("configuration_changed")
    if result.availability_state != config.STATE_AVAILABLE:
        raise IndexFault(result.reason_code, result.availability_state)
    fingerprint = hashlib.sha256(canonical_json({
        "configuration": value,
        "configuration_identity": signature,
    }).encode("utf-8")).hexdigest()
    return tuple(sources), fingerprint


def _versions_fingerprint():
    public_paths = (
        ROOT / "references" / "local-orientation-config.schema.json",
        ROOT / "references" / "local-orientation-metadata.schema.json",
        ROOT / "references" / "local-orientation-feature-taxonomy.json",
        ROOT / "references" / "operator-taxonomy.json",
        ROOT / "scripts" / "local_orientation_features.py",
        ROOT / "scripts" / "local_orientation_tex.py",
        ROOT / "scripts" / "local_orientation_candidates.py",
        ROOT / "scripts" / "local_orientation_includes.py",
        ROOT / "scripts" / "local_orientation_metadata.py",
        ROOT / "scripts" / "local_orientation_index.py",
    )
    digest = hashlib.sha256()
    for path in public_paths:
        digest.update(path.name.encode("ascii"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    digest.update(str(INDEX_VERSION).encode("ascii"))
    digest.update(str(tex.PARSER_VERSION).encode("ascii"))
    return digest.hexdigest()


def _analyze(sources, limits, deadline):
    _check_time(deadline)
    remaining = max(0.000001, deadline - time.monotonic())
    graph = includes.analyze_sources(
        sources,
        limits=includes.IncludeLimits(
            max_nodes=limits.max_documents, max_edges=limits.max_edges,
            max_depth=limits.max_depth, max_total_bytes=limits.max_total_bytes,
            max_seconds=min(limits.max_seconds, remaining)),
        parser_limits=tex.ParserLimits(max_bytes=limits.max_file_bytes),
        discovery_limits=selector.DiscoveryLimits(
            max_candidates=limits.max_documents,
            max_entries=10_000, max_directories=2048,
            max_file_bytes=limits.max_file_bytes,
            max_total_bytes=limits.max_total_bytes),
    )
    total = 0
    for document in graph.documents:
        _check_time(deadline)
        validate_metadata(document, deadline=deadline)
        total += len(canonical_json(document).encode("utf-8"))
        if total > limits.max_index_bytes // 2:
            raise IndexFault("index_size_limit")
    if len(graph.candidates) != len(graph.documents):
        raise IndexFault("index_graph_invalid")
    return graph


def _candidate_identities(graph):
    return tuple((str(candidate.device), str(candidate.inode), candidate.link_count)
                 for candidate in graph.candidates)


def _manifest(fingerprint, versions, graph):
    return {
        "index_version": INDEX_VERSION,
        "configuration_fingerprint": fingerprint,
        "versions_fingerprint": versions,
        "warning_codes": list(graph.warning_codes),
    }


_DDL = {
    "manifest": "CREATE TABLE manifest (ordinal INTEGER PRIMARY KEY, payload TEXT NOT NULL)",
    "documents": "CREATE TABLE documents (ordinal INTEGER PRIMARY KEY, payload TEXT NOT NULL)",
    "identities": "CREATE TABLE identities (ordinal INTEGER PRIMARY KEY, device TEXT NOT NULL, inode TEXT NOT NULL, links INTEGER NOT NULL)",
    "edges": "CREATE TABLE edges (ordinal INTEGER PRIMARY KEY, source_id TEXT NOT NULL, parent_id TEXT NOT NULL, child_id TEXT NOT NULL)",
}


def _require_serialization():
    if not (hasattr(sqlite3.Connection, "serialize")
            and hasattr(sqlite3.Connection, "deserialize")):
        raise IndexFault("sqlite_serialization_unavailable", config.STATE_UNREACHABLE)


def _sqlite_memory(deadline):
    _require_serialization()
    connection = sqlite3.connect(":memory:")
    connection.enable_load_extension(False)
    connection.execute("PRAGMA trusted_schema=OFF")
    connection.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
    if hasattr(connection, "setlimit"):
        for name, value in (
            ("SQLITE_LIMIT_LENGTH", MAX_DOCUMENT_JSON_BYTES + 65536),
            ("SQLITE_LIMIT_SQL_LENGTH", 65536), ("SQLITE_LIMIT_COLUMN", 16),
            ("SQLITE_LIMIT_EXPR_DEPTH", 64), ("SQLITE_LIMIT_ATTACHED", 0),
            ("SQLITE_LIMIT_COMPOUND_SELECT", 8), ("SQLITE_LIMIT_VARIABLE_NUMBER", 16),
        ):
            connection.setlimit(getattr(sqlite3, name), value)
    return connection


def _serialize_graph(graph, fingerprint, versions, limits, deadline):
    connection = _sqlite_memory(deadline)
    try:
        for ddl in _DDL.values():
            connection.execute(ddl)
        connection.execute("INSERT INTO manifest VALUES (?,?)",
                           (1, canonical_json(_manifest(fingerprint, versions, graph))))
        connection.executemany("INSERT INTO documents VALUES (?,?)",
                               ((number, canonical_json(document))
                                for number, document in enumerate(graph.documents, 1)))
        connection.executemany("INSERT INTO identities VALUES (?,?,?,?)",
                               ((number, *identity) for number, identity
                                in enumerate(_candidate_identities(graph), 1)))
        connection.executemany("INSERT INTO edges VALUES (?,?,?,?)",
                               ((number, *edge) for number, edge
                                in enumerate(graph.edges, 1)))
        connection.commit()
        data = connection.serialize()
        if len(data) > limits.max_index_bytes:
            raise IndexFault("index_size_limit")
        return data
    finally:
        connection.close()


def _validate_sqlite_header(data):
    if len(data) < 100 or data[:16] != b"SQLite format 3\0":
        raise IndexFault("index_corrupt")
    page_size = int.from_bytes(data[16:18], "big")
    page_size = 65536 if page_size == 1 else page_size
    if (page_size < 512 or page_size > 65536 or page_size & (page_size - 1)
            or len(data) % page_size or data[18:20] != b"\1\1"
            or int.from_bytes(data[28:32], "big") != len(data) // page_size):
        raise IndexFault("index_corrupt")


def _load_blob(data, limits, deadline):
    _validate_sqlite_header(data)
    connection = _sqlite_memory(deadline)
    try:
        connection.deserialize(data)
        connection.execute("PRAGMA trusted_schema=OFF")
        connection.execute("PRAGMA query_only=ON")
        connection.set_authorizer(lambda action, _a, _b, _db, _trigger:
                                  sqlite3.SQLITE_OK if action in {
                                      sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ,
                                      sqlite3.SQLITE_FUNCTION,
                                  } else sqlite3.SQLITE_DENY)
        schema = connection.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY name").fetchall()
        expected = [("table", name, name, ddl)
                    for name, ddl in sorted(_DDL.items())]
        if schema != expected:
            raise IndexFault("index_schema_invalid")
        manifests = connection.execute("SELECT ordinal,payload FROM manifest LIMIT 2").fetchall()
        if len(manifests) != 1 or manifests[0][0] != 1:
            raise IndexFault("index_manifest_invalid")
        manifest = decode_json(manifests[0][1])
        if (type(manifest) is not dict or set(manifest) != {
                "index_version", "configuration_fingerprint",
                "versions_fingerprint", "warning_codes"}
                or type(manifest["index_version"]) is not int
                or manifest["index_version"] != INDEX_VERSION):
            raise IndexFault("index_version_unsupported")
        for key in ("configuration_fingerprint", "versions_fingerprint"):
            value = manifest[key]
            if type(value) is not str or len(value) != 64 or any(c not in "abcdef0123456789" for c in value):
                raise IndexFault("index_manifest_invalid")
        warnings = manifest["warning_codes"]
        if (type(warnings) is not list or any(type(item) is not str or item not in GRAPH_WARNINGS for item in warnings)
                or warnings != sorted(set(warnings))):
            raise IndexFault("index_manifest_invalid")
        rows = connection.execute("SELECT ordinal,payload FROM documents ORDER BY ordinal LIMIT ?",
                                  (limits.max_documents + 1,)).fetchall()
        if len(rows) > limits.max_documents:
            raise IndexFault("index_document_limit")
        documents = []
        for ordinal, (stored_number, payload) in enumerate(rows, 1):
            _check_time(deadline)
            if stored_number != ordinal or type(payload) is not str or len(payload.encode("utf-8")) > MAX_DOCUMENT_JSON_BYTES:
                raise IndexFault("index_metadata_invalid")
            document = decode_json(payload)
            validate_metadata(document, deadline=deadline)
            documents.append(document)
        identities = connection.execute(
            "SELECT ordinal,device,inode,links FROM identities ORDER BY ordinal LIMIT ?",
            (limits.max_documents + 1,)).fetchall()
        if len(identities) != len(documents):
            raise IndexFault("index_identity_invalid")
        for ordinal, row in enumerate(identities, 1):
            if (row[0] != ordinal or type(row[3]) is not int or row[3] != 1
                    or any(type(item) is not str or not item.isascii() or not item.isdigit()
                           or not 0 < int(item) < 2**128 for item in row[1:3])):
                raise IndexFault("index_identity_invalid")
        edge_rows = connection.execute(
            "SELECT ordinal,source_id,parent_id,child_id FROM edges ORDER BY ordinal LIMIT ?",
            (limits.max_edges + 1,)).fetchall()
        if len(edge_rows) > limits.max_edges:
            raise IndexFault("index_edge_limit")
        keys = {(doc["source_id"], doc["document_id"]) for doc in documents}
        edges = []
        for ordinal, row in enumerate(edge_rows, 1):
            if (row[0] != ordinal or (row[1], row[2]) not in keys
                    or (row[1], row[3]) not in keys):
                raise IndexFault("index_graph_invalid")
            edges.append(tuple(row[1:]))
        if edges != sorted(set(edges)):
            raise IndexFault("index_graph_invalid")
        if len(keys) != len(documents):
            raise IndexFault("index_metadata_invalid")
        return (manifest, tuple(documents), tuple(tuple(row[1:]) for row in identities),
                tuple(edges))
    finally:
        connection.close()


def _verify_bound_file(path, descriptor, identity, guard):
    guard.verify()
    opened, named = os.fstat(descriptor), path.lstat()
    if (selector._entry_link(path, named)
            or _identity(opened, regular=True) != identity
            or _identity(named, regular=True) != identity):
        raise IndexFault("state_file_changed")


def _create_bound_file(path, guard):
    guard.verify()
    descriptor = guard.open_new(path)
    try:
        identity = _identity(os.fstat(descriptor), regular=True)
        _verify_bound_file(path, descriptor, identity, guard)
        return descriptor, identity
    except Exception:
        os.close(descriptor)
        raise


def _safe_unlink(path, identity, guard):
    """Never follow a replaced directory or delete an attacker's replacement."""
    try:
        guard.verify()
        metadata = path.lstat()
        if (not selector._entry_link(path, metadata)
                and _identity(metadata, regular=True) == identity):
            guard.unlink_bound(path, identity)
    except Exception:
        # A suspicious replacement is left for explicit operator inspection.
        return


def _publish(data, guard, original_signature, lock_descriptor,
             lock_identity, deadline):
    temporary = guard.state / ("build-" + uuid.uuid4().hex + ".tmp")
    descriptor, identity = _create_bound_file(temporary, guard)
    published = False
    try:
        view = memoryview(data)
        position = 0
        while position < len(view):
            _check_time(deadline)
            _verify_bound_file(temporary, descriptor, identity, guard)
            written = os.write(descriptor, view[position:position + 65536])
            if not written:
                raise IndexFault("index_write_failed", config.STATE_UNREACHABLE)
            position += written
        os.fsync(descriptor)
        _verify_bound_file(temporary, descriptor, identity, guard)
        _verify_bound_file(guard.lock, lock_descriptor, lock_identity, guard)
        if guard.existing_index_signature() != original_signature:
            raise IndexFault("state_file_changed")
        _check_time(deadline)
        os.close(descriptor)
        descriptor = None
        guard.verify()
        if _identity(temporary.lstat(), regular=True) != identity:
            raise IndexFault("state_file_changed")
        guard.replace_bound(temporary, identity)
        published = True
        guard.verify()
        if _identity(guard.index.lstat(), regular=True) != identity:
            raise IndexFault("state_file_changed")
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if not published:
            _safe_unlink(temporary, identity, guard)


def _build_impl(repo_root, explicit_config, environ, limits):
    active = limits or IndexLimits()
    deadline = time.monotonic() + active.max_seconds
    _require_serialization()
    sources, fingerprint = _configuration(
        repo_root, explicit_config, environ, deadline)
    guard = _StateGuard(repo_root, create=True)
    try:
        if guard.lock.exists() or guard.lock.is_symlink():
            metadata = guard.lock.lstat()
            if selector._entry_link(guard.lock, metadata):
                raise IndexFault("state_file_invalid")
            _identity(metadata, regular=True)
            raise IndexFault("index_build_busy", config.STATE_UNREACHABLE)
        lock_descriptor, lock_identity = _create_bound_file(guard.lock, guard)
    except FileExistsError:
        guard.close()
        raise IndexFault("index_build_busy", config.STATE_UNREACHABLE) from None
    except BaseException:
        guard.close()
        raise
    try:
        original = guard.existing_index_signature()
        versions = _versions_fingerprint()
        graph = _analyze(sources, active, deadline)
        data = _serialize_graph(graph, fingerprint, versions, active, deadline)
        _sources, current_fingerprint = _configuration(
            repo_root, explicit_config, environ, deadline)
        if current_fingerprint != fingerprint or _versions_fingerprint() != versions:
            raise IndexFault("configuration_changed")
        for candidate in graph.candidates:
            _check_time(deadline)
            includes._verify_unchanged(candidate)
        _publish(data, guard, original, lock_descriptor, lock_identity, deadline)
        return BuildResult()
    finally:
        os.close(lock_descriptor)
        _safe_unlink(guard.lock, lock_identity, guard)
        guard.close()


def _load_impl(repo_root, explicit_config, environ, limits):
    active = limits or IndexLimits()
    deadline = time.monotonic() + active.max_seconds
    _require_serialization()
    sources, fingerprint = _configuration(
        repo_root, explicit_config, environ, deadline)
    guard = _StateGuard(repo_root, create=False)
    try:
        data, signature = _read_blob(
            guard.index, active.max_index_bytes, deadline, guard.verify,
            opener=guard.open_existing)
        manifest, documents, identities, edges = _load_blob(data, active, deadline)
        versions = _versions_fingerprint()
        if manifest["configuration_fingerprint"] != fingerprint:
            raise IndexFault("index_configuration_changed")
        if manifest["versions_fingerprint"] != versions:
            raise IndexFault("index_version_unsupported")
        graph = _analyze(sources, active, deadline)
        if (documents != graph.documents or identities != _candidate_identities(graph)
                or edges != graph.edges or manifest["warning_codes"] != list(graph.warning_codes)):
            raise IndexFault("index_stale")
        _sources, after_fingerprint = _configuration(
            repo_root, explicit_config, environ, deadline)
        if after_fingerprint != fingerprint or _versions_fingerprint() != versions:
            raise IndexFault("configuration_changed")
        if guard.existing_index_signature() != signature:
            raise IndexFault("state_file_changed")
        _check_time(deadline)
        return IndexSnapshot(documents, edges, tuple(manifest["warning_codes"]))
    finally:
        guard.close()


def _sanitized(function, *args):
    code, state = "index_operational_error", config.STATE_EXCLUDED
    try:
        return function(*args)
    except IndexFault as error:
        code, state = error.code, error.state
    except config.ConfigFault as error:
        code, state = error.code, error.state
    except (includes.IncludeFault, selector.DiscoveryFault, tex.TexParseFault,
            MetadataFault) as error:
        code = error.code
    except (OSError, sqlite3.Error):
        code, state = "index_operational_error", config.STATE_UNREACHABLE
    except Exception:
        pass
    # Raise outside the handler: the exception's private chain is never kept.
    raise IndexFault(code, state)


def build_local_index(
    repo_root: Path = ROOT, explicit_config: Path | None = None,
    environ: Mapping[str, str] | None = None, limits: IndexLimits | None = None,
) -> BuildResult:
    """Explicit full rebuild, with no implicit source selection or activation."""
    return _sanitized(_build_impl, repo_root, explicit_config, environ, limits)


def load_valid_index(
    repo_root: Path = ROOT, explicit_config: Path | None = None,
    environ: Mapping[str, str] | None = None, limits: IndexLimits | None = None,
) -> IndexSnapshot:
    """Read-only load with complete bounded config/source/schema revalidation."""
    return _sanitized(_load_impl, repo_root, explicit_config, environ, limits)
