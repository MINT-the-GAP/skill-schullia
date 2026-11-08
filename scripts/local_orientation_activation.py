#!/usr/bin/env python3
"""Transactional activation and rollback for the ignored local overlay."""

from __future__ import annotations

import argparse
import copy
import ctypes
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time
from typing import Callable, Sequence

import local_orientation_config as config
import local_orientation_index as local_index
from local_orientation_metadata import canonical_json, decode_json


ROOT = Path(__file__).resolve().parents[1]
TRANSACTION_VERSION = 1
TRANSACTION_FILENAME = "activation-transaction.json"
CONFIG_BACKUP_FILENAME = "activation-config.backup"
STAGED_CONFIG_FILENAME = "activation-config.stage.json"
INDEX_BACKUP_FILENAME = "activation-index.backup"
MANIFEST_TEMP_FILENAME = "activation-transaction.tmp"
CONFIG_TEMP_FILENAME = "activation-config.tmp"
INDEX_TEMP_FILENAME = "activation-index.tmp"
MAX_CONFIG_BYTES = 1_000_000
MAX_MANIFEST_BYTES = 64 * 1024
MAX_INDEX_BYTES = 64 * 1024 * 1024

SUCCESS_REASONS = frozenset({
    "activation_staged", "activation_index_attested",
    "activation_committed", "activation_rolled_back",
    "activation_finalized",
})
FAILURE_REASONS = frozenset({
    "activation_arguments_invalid", "activation_confirmation_required",
    "activation_platform_unsupported", "activation_configuration_missing",
    "activation_configuration_boundary", "activation_configuration_invalid",
    "activation_configuration_not_disabled", "activation_configuration_changed",
    "activation_stage_invalid", "activation_transaction_exists",
    "activation_transaction_missing", "activation_transaction_invalid",
    "activation_orphaned_state", "activation_build_lock_present",
    "activation_index_missing", "activation_index_invalid",
    "activation_index_changed", "activation_phase_invalid",
    "activation_permissions_unavailable",
    "activation_cleanup_failed", "activation_boundary_rejected",
    "activation_operational_error",
})
STATES = frozenset({
    "staged", "index_attested", "committed", "rolled_back", "finalized",
    "excluded", "error",
})
HEX64 = re.compile(r"^[a-f0-9]{64}$")


class ActivationFault(RuntimeError):
    """A detached failure whose surface is a closed reason code only."""

    def __init__(self, code: str):
        self.code = code if code in FAILURE_REASONS else "activation_operational_error"
        super().__init__(self.code)


@dataclass(frozen=True)
class ActivationResult:
    status: str
    reason_code: str

    def __post_init__(self) -> None:
        if (self.status not in STATES
                or self.reason_code not in SUCCESS_REASONS | FAILURE_REASONS
                or (self.reason_code in SUCCESS_REASONS) != (
                    self.status not in {"excluded", "error"})):
            raise ValueError("activation_result_invalid")

    @property
    def succeeded(self) -> bool:
        return self.reason_code in SUCCESS_REASONS

    def safe_dict(self) -> dict[str, str]:
        return {"status": self.status, "reason_code": self.reason_code}

    def __repr__(self) -> str:
        return "ActivationResult(<closed-status>)"


@dataclass(frozen=True, repr=False)
class _OperationLease:
    descriptor: int
    identity: tuple[int, int]


@dataclass(frozen=True, repr=False)
class _DaclSnapshot:
    owner: bytes
    group: bytes
    acl: bytes
    protected: bool

    def __repr__(self) -> str:
        return "_DaclSnapshot(<closed>)"


class _AclHeader(ctypes.Structure):
    _fields_ = [
        ("revision", ctypes.c_ubyte),
        ("reserved_1", ctypes.c_ubyte),
        ("size", ctypes.c_ushort),
        ("ace_count", ctypes.c_ushort),
        ("reserved_2", ctypes.c_ushort),
    ]


def staged_config_path(repo_root: Path = ROOT) -> Path:
    """Return the fixed ignored staged-config location for trusted callers."""
    return Path(repo_root).absolute() / config.STATE_DIRECTORY / STAGED_CONFIG_FILENAME


def _require_confirmation(confirmed: object) -> None:
    if confirmed is not True:
        raise ActivationFault("activation_confirmation_required")


def _require_windows() -> None:
    if os.name != "nt":
        raise ActivationFault("activation_platform_unsupported")


def _exists(path: Path) -> bool:
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False
    except OSError:
        raise ActivationFault("activation_boundary_rejected") from None


def _acquire_operation_lease(
        guard: local_index._StateGuard) -> _OperationLease:
    """Own the shared build lock without ever adopting an existing lock."""
    guard.verify()
    if _exists(guard.lock):
        raise ActivationFault("activation_build_lock_present")
    try:
        descriptor, identity = local_index._create_bound_file(
            guard.lock, guard
        )
    except FileExistsError:
        raise ActivationFault("activation_build_lock_present") from None
    except Exception:
        if _exists(guard.lock):
            raise ActivationFault("activation_build_lock_present") from None
        raise ActivationFault("activation_boundary_rejected") from None
    return _OperationLease(descriptor, identity)


def _release_operation_lease(
        guard: local_index._StateGuard, lease: _OperationLease) -> None:
    """Delete only the lock created and still owned by this operation."""
    failed = False
    try:
        local_index._verify_bound_file(
            guard.lock, lease.descriptor, lease.identity, guard
        )
        local_index._windows_delete_descriptor(
            lease.descriptor, lease.identity
        )
    except Exception:
        failed = True
    finally:
        try:
            os.close(lease.descriptor)
        except OSError:
            failed = True
    try:
        guard.verify()
        if _exists(guard.lock):
            failed = True
    except Exception:
        failed = True
    if failed:
        raise ActivationFault("activation_cleanup_failed")


def _close_operation(
        guard: local_index._StateGuard,
        lease: _OperationLease | None,
) -> None:
    try:
        if lease is not None:
            _release_operation_lease(guard, lease)
    finally:
        guard.close()


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _signature_record(signature) -> dict[str, object]:
    identity, size, modified_ns, links = signature
    return {
        "device": str(identity[0]), "inode": str(identity[1]),
        "size": int(size), "modified_ns": int(modified_ns),
        "links": int(links),
    }


def _signature_value(record: object):
    if (type(record) is not dict
            or set(record) != {"device", "inode", "size", "modified_ns", "links"}
            or type(record["device"]) is not str
            or type(record["inode"]) is not str
            or not record["device"].isdigit() or not record["inode"].isdigit()
            or type(record["size"]) is not int
            or type(record["modified_ns"]) is not int
            or type(record["links"]) is not int
            or not 0 < int(record["device"]) < 2**128
            or not 0 < int(record["inode"]) < 2**128
            or record["size"] < 0 or record["modified_ns"] < 0
            or record["links"] != 1):
        raise ActivationFault("activation_transaction_invalid")
    return ((int(record["device"]), int(record["inode"])),
            record["size"], record["modified_ns"], record["links"])


def _mode(path: Path) -> int:
    try:
        metadata = path.lstat()
        local_index._file_signature(metadata)
        return stat.S_IMODE(metadata.st_mode)
    except Exception:
        raise ActivationFault("activation_boundary_rejected") from None


def _lease_for(guard: local_index._StateGuard, parent: Path):
    target = parent.absolute()
    for (path, _identity), lease in zip(guard.chain, guard.leases):
        if path.absolute() == target:
            return lease
    raise ActivationFault("activation_boundary_rejected")


def _open_child(guard: local_index._StateGuard, path: Path, *, create=False,
                deleting=False) -> int:
    """Open a fixed child relative to a leased directory without reparsing."""
    try:
        guard.verify()
        lease = _lease_for(guard, path.parent)
        import msvcrt
        if create:
            access, disposition, flags = 0x40010080, 2, os.O_WRONLY
        elif deleting:
            access, disposition, flags = 0x00030080, 1, os.O_RDONLY
        else:
            access, disposition, flags = 0x80000000, 1, os.O_RDONLY
        handle = local_index._windows_relative_handle(
            lease.handle, path.name, access=access, disposition=disposition,
        )
        return msvcrt.open_osfhandle(
            handle, flags | getattr(os, "O_BINARY", 0)
        )
    except FileExistsError:
        raise
    except ActivationFault:
        raise
    except Exception:
        raise ActivationFault("activation_boundary_rejected") from None


def _open_security_child(
        guard: local_index._StateGuard, path: Path, access: int) -> int:
    """Open one fixed child for handle-bound security-descriptor access."""
    try:
        guard.verify()
        lease = _lease_for(guard, path.parent)
        import msvcrt
        handle = local_index._windows_relative_handle(
            lease.handle, path.name, access=access | 0x80, disposition=1,
        )
        return msvcrt.open_osfhandle(
            handle, os.O_RDONLY | getattr(os, "O_BINARY", 0)
        )
    except ActivationFault:
        raise
    except Exception:
        raise ActivationFault("activation_permissions_unavailable") from None


def _read_windows_dacl(descriptor: int) -> _DaclSnapshot:
    """Read a DACL from an already identity-bound file handle."""
    import msvcrt
    from ctypes import wintypes

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    pointer = ctypes.c_void_p
    advapi.GetSecurityInfo.argtypes = (
        wintypes.HANDLE, ctypes.c_int, wintypes.DWORD,
        ctypes.POINTER(pointer), ctypes.POINTER(pointer),
        ctypes.POINTER(pointer), ctypes.POINTER(pointer),
        ctypes.POINTER(pointer),
    )
    advapi.GetSecurityInfo.restype = wintypes.DWORD
    advapi.GetSecurityDescriptorControl.argtypes = (
        pointer, ctypes.POINTER(wintypes.WORD),
        ctypes.POINTER(wintypes.DWORD),
    )
    advapi.GetSecurityDescriptorControl.restype = wintypes.BOOL
    advapi.GetLengthSid.argtypes = (pointer,)
    advapi.GetLengthSid.restype = wintypes.DWORD
    kernel.LocalFree.argtypes = (pointer,)
    kernel.LocalFree.restype = pointer

    owner, group = pointer(), pointer()
    dacl, security_descriptor = pointer(), pointer()
    result = advapi.GetSecurityInfo(
        wintypes.HANDLE(msvcrt.get_osfhandle(descriptor)),
        1, 0x00000001 | 0x00000002 | 0x00000004,
        ctypes.byref(owner), ctypes.byref(group), ctypes.byref(dacl), None,
        ctypes.byref(security_descriptor),
    )
    if result != 0 or not security_descriptor.value:
        raise ActivationFault("activation_permissions_unavailable")
    try:
        if not owner.value or not group.value or not dacl.value:
            raise ActivationFault("activation_permissions_unavailable")
        owner_size = int(advapi.GetLengthSid(owner))
        group_size = int(advapi.GetLengthSid(group))
        if not 8 <= owner_size <= 1024 or not 8 <= group_size <= 1024:
            raise ActivationFault("activation_permissions_unavailable")
        control, revision = wintypes.WORD(), wintypes.DWORD()
        if not advapi.GetSecurityDescriptorControl(
                security_descriptor, ctypes.byref(control),
                ctypes.byref(revision)):
            raise ActivationFault("activation_permissions_unavailable")
        header = ctypes.cast(
            dacl, ctypes.POINTER(_AclHeader)
        ).contents
        size = int(header.size)
        if not ctypes.sizeof(_AclHeader) <= size <= 0xFFFF:
            raise ActivationFault("activation_permissions_unavailable")
        return _DaclSnapshot(
            ctypes.string_at(owner, owner_size),
            ctypes.string_at(group, group_size),
            ctypes.string_at(dacl, size),
            bool(int(control.value) & 0x1000),
        )
    finally:
        kernel.LocalFree(security_descriptor)


def _write_windows_dacl(
        descriptor: int, snapshot: _DaclSnapshot) -> None:
    """Apply and then verify one closed in-memory DACL snapshot."""
    import msvcrt
    from ctypes import wintypes

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    advapi.SetSecurityInfo.argtypes = (
        wintypes.HANDLE, ctypes.c_int, wintypes.DWORD,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p,
    )
    advapi.SetSecurityInfo.restype = wintypes.DWORD
    acl = ctypes.create_string_buffer(snapshot.acl, len(snapshot.acl))
    information = (
        0x00000004
        | (0x80000000 if snapshot.protected else 0x20000000)
    )
    result = advapi.SetSecurityInfo(
        wintypes.HANDLE(msvcrt.get_osfhandle(descriptor)),
        1, information, None, None,
        ctypes.cast(acl, ctypes.c_void_p), None,
    )
    if result != 0 or _read_windows_dacl(descriptor) != snapshot:
        raise ActivationFault("activation_permissions_unavailable")


def _copy_windows_dacl(
        guard: local_index._StateGuard,
        source: Path,
        source_identity,
        target: Path,
        target_identity,
) -> _DaclSnapshot:
    source_descriptor = target_descriptor = None
    try:
        source_descriptor = _open_security_child(
            guard, source, 0x00020000
        )
        target_descriptor = _open_security_child(
            guard, target, 0x00020000 | 0x00040000
        )
        local_index._verify_bound_file(
            source, source_descriptor, source_identity, guard
        )
        local_index._verify_bound_file(
            target, target_descriptor, target_identity, guard
        )
        snapshot = _read_windows_dacl(source_descriptor)
        _write_windows_dacl(target_descriptor, snapshot)
        if _read_windows_dacl(source_descriptor) != snapshot:
            raise ActivationFault("activation_permissions_unavailable")
        local_index._verify_bound_file(
            source, source_descriptor, source_identity, guard
        )
        local_index._verify_bound_file(
            target, target_descriptor, target_identity, guard
        )
        return snapshot
    except ActivationFault:
        raise
    except Exception:
        raise ActivationFault("activation_permissions_unavailable") from None
    finally:
        if target_descriptor is not None:
            os.close(target_descriptor)
        if source_descriptor is not None:
            os.close(source_descriptor)


def _verify_windows_dacl(
        guard: local_index._StateGuard, path: Path, identity,
        expected: _DaclSnapshot) -> None:
    descriptor = None
    try:
        descriptor = _open_security_child(
            guard, path, 0x00020000
        )
        local_index._verify_bound_file(path, descriptor, identity, guard)
        if _read_windows_dacl(descriptor) != expected:
            raise ActivationFault("activation_permissions_unavailable")
        local_index._verify_bound_file(path, descriptor, identity, guard)
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _read_file(guard: local_index._StateGuard, path: Path, maximum: int,
               *, missing_code: str):
    try:
        return local_index._read_blob(
            path, maximum, time.monotonic() + 30.0, guard.verify,
            missing_code=missing_code,
            opener=lambda value: _open_child(guard, value),
        )
    except local_index.IndexFault as error:
        if error.code == missing_code:
            raise ActivationFault(missing_code) from None
        raise ActivationFault("activation_boundary_rejected") from None
    except ActivationFault:
        raise
    except Exception:
        raise ActivationFault("activation_boundary_rejected") from None


def _write_all(descriptor: int, data: bytes) -> None:
    view, offset = memoryview(data), 0
    while offset < len(view):
        written = os.write(descriptor, view[offset:offset + 65536])
        if not written:
            raise OSError("short_write")
        offset += written


def _create_file(guard: local_index._StateGuard, path: Path, data: bytes,
                 mode: int):
    descriptor = None
    identity = None
    try:
        descriptor = _open_child(guard, path, create=True)
        identity = local_index._identity(os.fstat(descriptor), regular=True)
        _write_all(descriptor, data)
        os.fsync(descriptor)
        try:
            os.fchmod(descriptor, mode)
        except (AttributeError, OSError):
            os.chmod(path, mode)
        os.fsync(descriptor)
        local_index._verify_bound_file(path, descriptor, identity, guard)
        signature = local_index._file_signature(os.fstat(descriptor))
        if signature[1] != len(data):
            raise ActivationFault("activation_boundary_rejected")
        return identity, signature
    except FileExistsError:
        raise ActivationFault("activation_orphaned_state") from None
    except ActivationFault:
        if descriptor is not None and identity is not None:
            try:
                local_index._windows_delete_descriptor(descriptor, identity)
            except Exception:
                pass
        raise
    except Exception:
        if descriptor is not None and identity is not None:
            try:
                local_index._windows_delete_descriptor(descriptor, identity)
            except Exception:
                pass
        raise ActivationFault("activation_operational_error") from None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _verify_file(guard, path, expected_signature, expected_hash,
                 maximum, missing_code):
    data, signature = _read_file(
        guard, path, maximum, missing_code=missing_code
    )
    if signature != expected_signature or _hash(data) != expected_hash:
        raise ActivationFault("activation_transaction_invalid")
    return data


def _rename_bound(guard: local_index._StateGuard, source: Path, target: Path,
                  expected_identity,
                  expected_permissions: _DaclSnapshot | None = None) -> None:
    """Rename an attested child relative to one held directory lease."""
    if source.parent != target.parent:
        raise ActivationFault("activation_boundary_rejected")
    descriptor = _open_child(guard, source, deleting=True)
    try:
        import msvcrt
        from ctypes import wintypes
        handle = msvcrt.get_osfhandle(descriptor)
        local_index._verify_bound_file(source, descriptor, expected_identity, guard)
        if (expected_permissions is not None
                and _read_windows_dacl(descriptor) != expected_permissions):
            raise ActivationFault("activation_permissions_unavailable")
        name = target.name

        class IOStatus(ctypes.Structure):
            _fields_ = [("status", ctypes.c_void_p),
                        ("information", ctypes.c_size_t)]

        class RenameInfo(ctypes.Structure):
            _fields_ = [
                ("replace", wintypes.BOOLEAN), ("root", wintypes.HANDLE),
                ("length", wintypes.ULONG),
                ("name", wintypes.WCHAR * len(name)),
            ]

        lease = _lease_for(guard, target.parent)
        info, ios = RenameInfo(), IOStatus()
        info.replace, info.root = 1, lease.handle
        info.length, info.name = len(name.encode("utf-16-le")), name
        native = ctypes.WinDLL("ntdll", use_last_error=True)
        native.NtSetInformationFile.argtypes = (
            wintypes.HANDLE, ctypes.POINTER(IOStatus), ctypes.c_void_p,
            wintypes.ULONG, ctypes.c_int,
        )
        native.NtSetInformationFile.restype = ctypes.c_long
        status = native.NtSetInformationFile(
            handle, ctypes.byref(ios), ctypes.byref(info),
            RenameInfo.name.offset + info.length, 10,
        )
        if status < 0:
            raise ActivationFault("activation_boundary_rejected")
        local_index._verify_bound_file(
            target, descriptor, expected_identity, guard
        )
        if (expected_permissions is not None
                and _read_windows_dacl(descriptor) != expected_permissions):
            raise ActivationFault("activation_permissions_unavailable")
    finally:
        os.close(descriptor)


def _delete_bound(guard, path, expected_identity) -> None:
    descriptor = _open_child(guard, path, deleting=True)
    try:
        local_index._verify_bound_file(path, descriptor, expected_identity, guard)
        local_index._windows_delete_descriptor(descriptor, expected_identity)
    except ActivationFault:
        raise
    except Exception:
        raise ActivationFault("activation_cleanup_failed") from None
    finally:
        os.close(descriptor)


def _safe_cleanup_created(guard, created) -> None:
    for path, identity in reversed(created):
        try:
            if _exists(path):
                _delete_bound(guard, path, identity)
        except Exception:
            pass


def _atomic_replace(guard, target, temporary, data, mode,
                    expected_target_signature, maximum,
                    changed_code="activation_configuration_changed"):
    if _exists(temporary):
        raise ActivationFault("activation_orphaned_state")
    identity, _temporary_signature = _create_file(
        guard, temporary, data, mode
    )
    published = False
    try:
        permissions = None
        if expected_target_signature is None:
            if _exists(target):
                raise ActivationFault(changed_code)
        else:
            _current, signature = _read_file(
                guard, target, maximum, missing_code=changed_code
            )
            if signature != expected_target_signature:
                raise ActivationFault(changed_code)
            permissions = _copy_windows_dacl(
                guard, target, expected_target_signature[0],
                temporary, identity,
            )
            _verify_windows_dacl(
                guard, target, expected_target_signature[0], permissions
            )
        _rename_bound(
            guard, temporary, target, identity, permissions
        )
        published = True
        value, signature = _read_file(
            guard, target, maximum, missing_code=changed_code
        )
        if value != data or signature[0] != identity:
            raise ActivationFault(changed_code)
        if permissions is not None:
            _verify_windows_dacl(
                guard, target, identity, permissions
            )
        return signature
    finally:
        if not published:
            _safe_cleanup_created(guard, [(temporary, identity)])


def _decode_config(raw: bytes) -> dict[str, object]:
    try:
        value = decode_json(raw.decode("utf-8-sig"))
        return copy.deepcopy(dict(config._validate_top_level(value)))
    except Exception:
        raise ActivationFault("activation_configuration_invalid") from None


def _activated_bytes(original: dict[str, object]) -> bytes:
    value = copy.deepcopy(original)
    value["enabled"] = True
    try:
        return (canonical_json(value) + "\n").encode("utf-8")
    except Exception:
        raise ActivationFault("activation_configuration_invalid") from None


def _only_enabled_changed(original, activated) -> bool:
    expected = copy.deepcopy(original)
    expected["enabled"] = True
    return activated == expected


def _validate_active_runtime(repo: Path, staged: Path) -> None:
    try:
        result, sources = config.load_validated_sources(
            repo, explicit_config=staged, environ={}
        )
        if (result.availability_state != config.STATE_AVAILABLE
                or result.reason_code != "configuration_valid" or not sources):
            raise ActivationFault("activation_stage_invalid")
    except ActivationFault:
        raise
    except Exception:
        raise ActivationFault("activation_stage_invalid") from None


def _manifest_paths(guard) -> dict[str, Path]:
    return {
        "manifest": guard.state / TRANSACTION_FILENAME,
        "config_backup": guard.state / CONFIG_BACKUP_FILENAME,
        "stage": guard.state / STAGED_CONFIG_FILENAME,
        "index_backup": guard.state / INDEX_BACKUP_FILENAME,
        "manifest_temp": guard.state / MANIFEST_TEMP_FILENAME,
        "index_temp": guard.state / INDEX_TEMP_FILENAME,
        "config_temp": guard.repo / config.LOCAL_ZONE / CONFIG_TEMP_FILENAME,
        "config": guard.repo / config.DEFAULT_CONFIG,
    }


def _valid_hash(value: object) -> bool:
    return type(value) is str and HEX64.fullmatch(value) is not None


def _validate_manifest(value: object) -> dict[str, object]:
    try:
        if (type(value) is not dict
                or set(value) != {"transaction_version", "phase", "config", "index"}
                or value["transaction_version"] != TRANSACTION_VERSION
                or value["phase"] not in {"staged", "committed"}):
            raise ActivationFault("activation_transaction_invalid")
        cfg, idx = value["config"], value["index"]
        if (type(cfg) is not dict or set(cfg) != {
                "original_hash", "original_signature", "mode",
                "backup_hash", "backup_signature", "stage_hash",
                "stage_signature", "committed_signature"}):
            raise ActivationFault("activation_transaction_invalid")
        for key in ("original_hash", "backup_hash", "stage_hash"):
            if not _valid_hash(cfg[key]):
                raise ActivationFault("activation_transaction_invalid")
        for key in ("original_signature", "backup_signature", "stage_signature"):
            _signature_value(cfg[key])
        if (type(cfg["mode"]) is not int or not 0 <= cfg["mode"] <= 0o777
                or (cfg["committed_signature"] is not None
                    and not isinstance(cfg["committed_signature"], dict))):
            raise ActivationFault("activation_transaction_invalid")
        if cfg["committed_signature"] is not None:
            _signature_value(cfg["committed_signature"])
        if ((value["phase"] == "committed")
                != (cfg["committed_signature"] is not None)):
            raise ActivationFault("activation_transaction_invalid")
        if (type(idx) is not dict or set(idx) != {
                "baseline_present", "baseline_hash", "baseline_signature",
                "backup_hash", "backup_signature", "attested_hash",
                "attested_signature", "attested_phase"}):
            raise ActivationFault("activation_transaction_invalid")
        if type(idx["baseline_present"]) is not bool:
            raise ActivationFault("activation_transaction_invalid")
        baseline_values = (
            idx["baseline_hash"], idx["baseline_signature"],
            idx["backup_hash"], idx["backup_signature"],
        )
        if idx["baseline_present"]:
            if (not _valid_hash(idx["baseline_hash"])
                    or not _valid_hash(idx["backup_hash"])):
                raise ActivationFault("activation_transaction_invalid")
            _signature_value(idx["baseline_signature"])
            _signature_value(idx["backup_signature"])
        elif any(item is not None for item in baseline_values):
            raise ActivationFault("activation_transaction_invalid")
        if idx["attested_phase"] not in {"none", "staged", "final"}:
            raise ActivationFault("activation_transaction_invalid")
        if idx["attested_phase"] == "none":
            if idx["attested_hash"] is not None or idx["attested_signature"] is not None:
                raise ActivationFault("activation_transaction_invalid")
        else:
            if not _valid_hash(idx["attested_hash"]):
                raise ActivationFault("activation_transaction_invalid")
            _signature_value(idx["attested_signature"])
        if idx["attested_phase"] == "final" and value["phase"] != "committed":
            raise ActivationFault("activation_transaction_invalid")
        return copy.deepcopy(value)
    except ActivationFault:
        raise
    except Exception:
        raise ActivationFault("activation_transaction_invalid") from None


def _load_manifest(guard, paths):
    if not _exists(paths["manifest"]):
        raise ActivationFault("activation_transaction_missing")
    raw, signature = _read_file(
        guard, paths["manifest"], MAX_MANIFEST_BYTES,
        missing_code="activation_transaction_missing",
    )
    try:
        value = decode_json(raw.decode("utf-8"))
    except Exception:
        raise ActivationFault("activation_transaction_invalid") from None
    return _validate_manifest(value), signature


def _manifest_bytes(value) -> bytes:
    _validate_manifest(value)
    raw = (canonical_json(value) + "\n").encode("ascii")
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ActivationFault("activation_transaction_invalid")
    return raw


def _create_manifest(guard, path, value, created) -> None:
    identity, _signature = _create_file(
        guard, path, _manifest_bytes(value), 0o600
    )
    created.append((path, identity))


def _replace_manifest(guard, paths, value, current_signature):
    return _atomic_replace(
        guard, paths["manifest"], paths["manifest_temp"],
        _manifest_bytes(value), 0o600, current_signature,
        MAX_MANIFEST_BYTES, "activation_transaction_invalid",
    )


def _configuration_preflight(guard, paths, manifest):
    cfg = manifest["config"]
    backup = _verify_file(
        guard, paths["config_backup"],
        _signature_value(cfg["backup_signature"]), cfg["backup_hash"],
        MAX_CONFIG_BYTES, "activation_transaction_invalid",
    )
    stage = _verify_file(
        guard, paths["stage"], _signature_value(cfg["stage_signature"]),
        cfg["stage_hash"], MAX_CONFIG_BYTES,
        "activation_transaction_invalid",
    )
    original_value, stage_value = _decode_config(backup), _decode_config(stage)
    if original_value.get("enabled") is not False or not _only_enabled_changed(
            original_value, stage_value):
        raise ActivationFault("activation_transaction_invalid")
    return backup, stage, original_value, stage_value


def _stage_impl(repo_root: Path, confirmed: bool) -> ActivationResult:
    _require_confirmation(confirmed)
    _require_windows()
    repo = Path(repo_root).absolute()
    guard = local_index._StateGuard(repo, create=True)
    created = []
    lease = None
    try:
        lease = _acquire_operation_lease(guard)
        paths = _manifest_paths(guard)
        artifacts = (
            paths["manifest"], paths["config_backup"], paths["stage"],
            paths["index_backup"], paths["manifest_temp"],
            paths["index_temp"], paths["config_temp"],
        )
        if _exists(paths["manifest"]):
            raise ActivationFault("activation_transaction_exists")
        if any(_exists(path) for path in artifacts[1:]):
            raise ActivationFault("activation_orphaned_state")
        if not _exists(paths["config"]):
            raise ActivationFault("activation_configuration_missing")
        raw, original_signature = _read_file(
            guard, paths["config"], MAX_CONFIG_BYTES,
            missing_code="activation_configuration_missing",
        )
        original = _decode_config(raw)
        if original.get("enabled") is not False:
            raise ActivationFault("activation_configuration_not_disabled")
        mode = _mode(paths["config"])
        backup_identity, backup_signature = _create_file(
            guard, paths["config_backup"], raw, 0o600
        )
        created.append((paths["config_backup"], backup_identity))

        baseline_present = _exists(guard.index)
        baseline_hash = baseline_signature = None
        backup_index_hash = backup_index_signature = None
        if baseline_present:
            baseline, baseline_signature_value = _read_file(
                guard, guard.index, MAX_INDEX_BYTES,
                missing_code="activation_index_missing",
            )
            baseline_hash = _hash(baseline)
            baseline_signature = _signature_record(baseline_signature_value)
            index_identity, index_backup_signature_value = _create_file(
                guard, paths["index_backup"], baseline, 0o600
            )
            created.append((paths["index_backup"], index_identity))
            backup_index_hash = _hash(baseline)
            backup_index_signature = _signature_record(
                index_backup_signature_value
            )

        active = _activated_bytes(original)
        stage_identity, stage_signature = _create_file(
            guard, paths["stage"], active, mode
        )
        created.append((paths["stage"], stage_identity))
        _validate_active_runtime(repo, paths["stage"])
        manifest = {
            "transaction_version": TRANSACTION_VERSION,
            "phase": "staged",
            "config": {
                "original_hash": _hash(raw),
                "original_signature": _signature_record(original_signature),
                "mode": mode, "backup_hash": _hash(raw),
                "backup_signature": _signature_record(backup_signature),
                "stage_hash": _hash(active),
                "stage_signature": _signature_record(stage_signature),
                "committed_signature": None,
            },
            "index": {
                "baseline_present": baseline_present,
                "baseline_hash": baseline_hash,
                "baseline_signature": baseline_signature,
                "backup_hash": backup_index_hash,
                "backup_signature": backup_index_signature,
                "attested_hash": None, "attested_signature": None,
                "attested_phase": "none",
            },
        }
        _create_manifest(guard, paths["manifest"], manifest, created)
        created.clear()
        return ActivationResult("staged", "activation_staged")
    except Exception:
        _safe_cleanup_created(guard, created)
        raise
    finally:
        _close_operation(guard, lease)


def _attest_index_impl(repo_root: Path, phase: str,
                       confirmed: bool) -> ActivationResult:
    _require_confirmation(confirmed)
    _require_windows()
    if phase not in {"staged", "final"}:
        raise ActivationFault("activation_phase_invalid")
    repo = Path(repo_root).absolute()
    guard = local_index._StateGuard(repo, create=False)
    lease = None
    try:
        lease = _acquire_operation_lease(guard)
        paths = _manifest_paths(guard)
        manifest, manifest_signature = _load_manifest(guard, paths)
        expected_phase = "staged" if phase == "staged" else "committed"
        if manifest["phase"] != expected_phase:
            raise ActivationFault("activation_phase_invalid")
        backup, stage, _original, _activated = _configuration_preflight(
            guard, paths, manifest
        )
        current, current_signature = _read_file(
            guard, paths["config"], MAX_CONFIG_BYTES,
            missing_code="activation_configuration_missing",
        )
        cfg = manifest["config"]
        if phase == "staged":
            if (current != backup
                    or current_signature != _signature_value(
                        cfg["original_signature"])):
                raise ActivationFault("activation_configuration_changed")
            validation_config = paths["stage"]
        else:
            if (current != stage
                    or current_signature != _signature_value(
                        cfg["committed_signature"])):
                raise ActivationFault("activation_configuration_changed")
            validation_config = paths["config"]
        try:
            local_index.load_valid_index(
                repo, explicit_config=validation_config, environ={}
            )
        except Exception:
            raise ActivationFault("activation_index_invalid") from None
        raw_index, signature = _read_file(
            guard, guard.index, MAX_INDEX_BYTES,
            missing_code="activation_index_missing",
        )
        manifest["index"]["attested_hash"] = _hash(raw_index)
        manifest["index"]["attested_signature"] = _signature_record(signature)
        manifest["index"]["attested_phase"] = phase
        _replace_manifest(guard, paths, manifest, manifest_signature)
        return ActivationResult("index_attested", "activation_index_attested")
    finally:
        _close_operation(guard, lease)


def _commit_impl(repo_root: Path, confirmed: bool) -> ActivationResult:
    _require_confirmation(confirmed)
    _require_windows()
    repo = Path(repo_root).absolute()
    guard = local_index._StateGuard(repo, create=False)
    lease = None
    try:
        lease = _acquire_operation_lease(guard)
        paths = _manifest_paths(guard)
        manifest, manifest_signature = _load_manifest(guard, paths)
        if (manifest["phase"] != "staged"
                or manifest["index"]["attested_phase"] != "staged"):
            raise ActivationFault("activation_phase_invalid")
        backup, stage, _original, _activated = _configuration_preflight(
            guard, paths, manifest
        )
        cfg, idx = manifest["config"], manifest["index"]
        current, current_signature = _read_file(
            guard, paths["config"], MAX_CONFIG_BYTES,
            missing_code="activation_configuration_missing",
        )
        if (current != backup or _hash(current) != cfg["original_hash"]
                or current_signature != _signature_value(
                    cfg["original_signature"])):
            raise ActivationFault("activation_configuration_changed")
        current_index, current_index_signature = _read_file(
            guard, guard.index, MAX_INDEX_BYTES,
            missing_code="activation_index_missing",
        )
        if (current_index_signature != _signature_value(
                idx["attested_signature"])
                or _hash(current_index) != idx["attested_hash"]):
            raise ActivationFault("activation_index_changed")
        _validate_active_runtime(repo, paths["stage"])
        committed_signature = _atomic_replace(
            guard, paths["config"], paths["config_temp"], stage,
            cfg["mode"], current_signature, MAX_CONFIG_BYTES,
        )
        manifest["phase"] = "committed"
        manifest["config"]["committed_signature"] = _signature_record(
            committed_signature
        )
        _replace_manifest(guard, paths, manifest, manifest_signature)
        return ActivationResult("committed", "activation_committed")
    finally:
        _close_operation(guard, lease)


def _preflight_index_rollback(guard, paths, manifest):
    idx = manifest["index"]
    baseline = None
    if idx["baseline_present"]:
        baseline = _verify_file(
            guard, paths["index_backup"],
            _signature_value(idx["backup_signature"]), idx["backup_hash"],
            MAX_INDEX_BYTES, "activation_transaction_invalid",
        )
    if not _exists(guard.index):
        return baseline, None, None, "missing"
    current, signature = _read_file(
        guard, guard.index, MAX_INDEX_BYTES,
        missing_code="activation_index_missing",
    )
    digest = _hash(current)
    if (idx["baseline_present"]
            and digest == idx["baseline_hash"]
            and signature == _signature_value(idx["baseline_signature"])):
        return baseline, current, signature, "baseline"
    if (idx["attested_phase"] != "none"
            and digest == idx["attested_hash"]
            and signature == _signature_value(idx["attested_signature"])):
        return baseline, current, signature, "attested"
    raise ActivationFault("activation_index_changed")


def _cleanup_transaction(guard, paths, manifest, manifest_signature) -> None:
    cfg, idx = manifest["config"], manifest["index"]
    entries = [
        (paths["stage"], _signature_value(cfg["stage_signature"])[0]),
    ]
    if idx["baseline_present"]:
        entries.append((paths["index_backup"],
                        _signature_value(idx["backup_signature"])[0]))
    entries.extend([
        (paths["config_backup"],
         _signature_value(cfg["backup_signature"])[0]),
        (paths["manifest"], manifest_signature[0]),
    ])
    for path, identity in entries:
        if not _exists(path):
            raise ActivationFault("activation_cleanup_failed")
        _delete_bound(guard, path, identity)


def _rollback_impl(repo_root: Path, confirmed: bool) -> ActivationResult:
    _require_confirmation(confirmed)
    _require_windows()
    repo = Path(repo_root).absolute()
    guard = local_index._StateGuard(repo, create=False)
    lease = None
    try:
        lease = _acquire_operation_lease(guard)
        paths = _manifest_paths(guard)
        manifest, manifest_signature = _load_manifest(guard, paths)
        backup, stage, _original, _activated = _configuration_preflight(
            guard, paths, manifest
        )
        cfg = manifest["config"]
        current, current_signature = _read_file(
            guard, paths["config"], MAX_CONFIG_BYTES,
            missing_code="activation_configuration_missing",
        )
        if (current == backup
                and current_signature == _signature_value(
                    cfg["original_signature"])):
            config_action = "unchanged"
        elif (current == stage and manifest["phase"] == "committed"
                and current_signature == _signature_value(
                    cfg["committed_signature"])):
            config_action = "restore"
        elif current == stage and manifest["phase"] == "staged":
            # Recovery after the config publish but before the manifest publish.
            config_action = "restore"
        else:
            raise ActivationFault("activation_configuration_changed")
        baseline, _current_index, index_signature, index_state = (
            _preflight_index_rollback(guard, paths, manifest)
        )
        expected_config_signature = current_signature
        if config_action == "restore":
            expected_config_signature = _atomic_replace(
                guard, paths["config"], paths["config_temp"], backup,
                cfg["mode"], current_signature, MAX_CONFIG_BYTES,
            )
        expected_index_signature = index_signature
        if manifest["index"]["baseline_present"]:
            if index_state != "baseline":
                expected = index_signature if index_state == "attested" else None
                expected_index_signature = _atomic_replace(
                    guard, guard.index, paths["index_temp"], baseline,
                    0o600, expected, MAX_INDEX_BYTES,
                    "activation_index_changed",
                )
        elif index_state == "attested":
            _delete_bound(guard, guard.index, index_signature[0])

        restored, restored_signature = _read_file(
            guard, paths["config"], MAX_CONFIG_BYTES,
            missing_code="activation_configuration_missing",
        )
        if (restored != backup
                or restored_signature != expected_config_signature):
            raise ActivationFault("activation_configuration_changed")
        if manifest["index"]["baseline_present"]:
            restored_index, restored_index_signature = _read_file(
                guard, guard.index, MAX_INDEX_BYTES,
                missing_code="activation_index_missing",
            )
            if (_hash(restored_index) != manifest["index"]["baseline_hash"]
                    or restored_index_signature != expected_index_signature):
                raise ActivationFault("activation_index_changed")
        elif _exists(guard.index):
            raise ActivationFault("activation_index_changed")
        _cleanup_transaction(guard, paths, manifest, manifest_signature)
        return ActivationResult("rolled_back", "activation_rolled_back")
    finally:
        _close_operation(guard, lease)


def _finalize_impl(repo_root: Path, confirmed: bool) -> ActivationResult:
    _require_confirmation(confirmed)
    _require_windows()
    repo = Path(repo_root).absolute()
    guard = local_index._StateGuard(repo, create=False)
    lease = None
    try:
        lease = _acquire_operation_lease(guard)
        paths = _manifest_paths(guard)
        manifest, manifest_signature = _load_manifest(guard, paths)
        if (manifest["phase"] != "committed"
                or manifest["index"]["attested_phase"] != "final"):
            raise ActivationFault("activation_phase_invalid")
        _backup, stage, _original, _activated = _configuration_preflight(
            guard, paths, manifest
        )
        current, current_signature = _read_file(
            guard, paths["config"], MAX_CONFIG_BYTES,
            missing_code="activation_configuration_missing",
        )
        if (current != stage
                or current_signature != _signature_value(
                    manifest["config"]["committed_signature"])):
            raise ActivationFault("activation_configuration_changed")
        idx = manifest["index"]
        raw_index, signature = _read_file(
            guard, guard.index, MAX_INDEX_BYTES,
            missing_code="activation_index_missing",
        )
        if (signature != _signature_value(idx["attested_signature"])
                or _hash(raw_index) != idx["attested_hash"]):
            raise ActivationFault("activation_index_changed")
        _validate_active_runtime(repo, paths["config"])
        try:
            local_index.load_valid_index(
                repo, explicit_config=paths["config"], environ={}
            )
        except Exception:
            raise ActivationFault("activation_index_invalid") from None
        _cleanup_transaction(guard, paths, manifest, manifest_signature)
        return ActivationResult("finalized", "activation_finalized")
    finally:
        _close_operation(guard, lease)


def _safe_call(function: Callable[..., ActivationResult], *args) -> ActivationResult:
    try:
        return function(*args)
    except ActivationFault as error:
        code = error.code
    except local_index.IndexFault as error:
        code = (
            "activation_platform_unsupported"
            if error.code == "state_platform_unsupported"
            else "activation_boundary_rejected"
        )
    except Exception:
        code = "activation_operational_error"
    return ActivationResult(
        "error" if code == "activation_operational_error" else "excluded",
        code,
    )


def stage_activation(repo_root: Path = ROOT, *, confirmed=False) -> ActivationResult:
    return _safe_call(_stage_impl, repo_root, confirmed)


def attest_index(repo_root: Path = ROOT, *, phase: str,
                 confirmed=False) -> ActivationResult:
    return _safe_call(_attest_index_impl, repo_root, phase, confirmed)


def commit_activation(repo_root: Path = ROOT, *, confirmed=False) -> ActivationResult:
    return _safe_call(_commit_impl, repo_root, confirmed)


def rollback_activation(repo_root: Path = ROOT, *, confirmed=False) -> ActivationResult:
    return _safe_call(_rollback_impl, repo_root, confirmed)


def finalize_activation(repo_root: Path = ROOT, *, confirmed=False) -> ActivationResult:
    return _safe_call(_finalize_impl, repo_root, confirmed)


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, _message):
        raise ActivationFault("activation_arguments_invalid")


def parse_args(argv: Sequence[str] | None = None):
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=("stage", "attest-index", "commit", "rollback", "finalize"),
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--phase", choices=("staged", "final"))
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        if args.action == "stage":
            result = stage_activation(args.repo_root, confirmed=args.confirm)
        elif args.action == "attest-index":
            if args.phase is None:
                raise ActivationFault("activation_arguments_invalid")
            result = attest_index(
                args.repo_root, phase=args.phase, confirmed=args.confirm
            )
        elif args.action == "commit":
            result = commit_activation(args.repo_root, confirmed=args.confirm)
        elif args.action == "rollback":
            result = rollback_activation(args.repo_root, confirmed=args.confirm)
        else:
            result = finalize_activation(args.repo_root, confirmed=args.confirm)
    except ActivationFault as error:
        result = ActivationResult("excluded", error.code)
    except Exception:
        result = ActivationResult("error", "activation_operational_error")
    print(json.dumps(result.safe_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.succeeded else (2 if result.status == "error" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
