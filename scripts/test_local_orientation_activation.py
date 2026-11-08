#!/usr/bin/env python3
"""Synthetic transactional activation regressions; no real config is read."""

from __future__ import annotations

import contextlib
import ctypes
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import local_orientation_activation as activation
import local_orientation_config as config
import local_orientation_index as index
from test_local_orientation_security import layout, valid, write_json


SENTINEL = "SYNTHETIC_ACTIVATION_PRIVATE_SENTINEL"


class _SyntheticDaclUnavailable(RuntimeError):
    pass


class _SyntheticAclHeader(ctypes.Structure):
    _fields_ = [
        ("revision", ctypes.c_ubyte),
        ("reserved_1", ctypes.c_ubyte),
        ("size", ctypes.c_ushort),
        ("ace_count", ctypes.c_ushort),
        ("reserved_2", ctypes.c_ushort),
    ]


def _named_dacl(path: Path):
    from ctypes import wintypes

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    pointer = ctypes.c_void_p
    advapi.GetNamedSecurityInfoW.argtypes = (
        wintypes.LPWSTR, ctypes.c_int, wintypes.DWORD,
        ctypes.POINTER(pointer), ctypes.POINTER(pointer),
        ctypes.POINTER(pointer), ctypes.POINTER(pointer),
        ctypes.POINTER(pointer),
    )
    advapi.GetNamedSecurityInfoW.restype = wintypes.DWORD
    advapi.GetSecurityDescriptorControl.argtypes = (
        pointer, ctypes.POINTER(wintypes.WORD),
        ctypes.POINTER(wintypes.DWORD),
    )
    advapi.GetSecurityDescriptorControl.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = (pointer,)
    kernel.LocalFree.restype = pointer
    dacl, descriptor = pointer(), pointer()
    result = advapi.GetNamedSecurityInfoW(
        str(path), 1, 0x00000004, None, None,
        ctypes.byref(dacl), None, ctypes.byref(descriptor),
    )
    if result != 0 or not descriptor.value or not dacl.value:
        raise _SyntheticDaclUnavailable("synthetic_dacl_unavailable")
    try:
        control, revision = wintypes.WORD(), wintypes.DWORD()
        if not advapi.GetSecurityDescriptorControl(
                descriptor, ctypes.byref(control), ctypes.byref(revision)):
            raise _SyntheticDaclUnavailable("synthetic_dacl_unavailable")
        header = ctypes.cast(
            dacl, ctypes.POINTER(_SyntheticAclHeader)
        ).contents
        size = int(header.size)
        if not ctypes.sizeof(_SyntheticAclHeader) <= size <= 0xFFFF:
            raise _SyntheticDaclUnavailable("synthetic_dacl_unavailable")
        return (
            ctypes.string_at(dacl, size),
            bool(int(control.value) & 0x1000),
        )
    finally:
        kernel.LocalFree(descriptor)


def _protect_named_dacl(path: Path):
    from ctypes import wintypes

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    pointer = ctypes.c_void_p
    advapi.GetNamedSecurityInfoW.argtypes = (
        wintypes.LPWSTR, ctypes.c_int, wintypes.DWORD,
        ctypes.POINTER(pointer), ctypes.POINTER(pointer),
        ctypes.POINTER(pointer), ctypes.POINTER(pointer),
        ctypes.POINTER(pointer),
    )
    advapi.GetNamedSecurityInfoW.restype = wintypes.DWORD
    advapi.SetNamedSecurityInfoW.argtypes = (
        wintypes.LPWSTR, ctypes.c_int, wintypes.DWORD,
        pointer, pointer, pointer, pointer,
    )
    advapi.SetNamedSecurityInfoW.restype = wintypes.DWORD
    kernel.LocalFree.argtypes = (pointer,)
    kernel.LocalFree.restype = pointer
    dacl, descriptor = pointer(), pointer()
    result = advapi.GetNamedSecurityInfoW(
        str(path), 1, 0x00000004, None, None,
        ctypes.byref(dacl), None, ctypes.byref(descriptor),
    )
    if result != 0 or not descriptor.value or not dacl.value:
        raise _SyntheticDaclUnavailable("synthetic_dacl_unavailable")
    try:
        result = advapi.SetNamedSecurityInfoW(
            str(path), 1, 0x00000004 | 0x80000000,
            None, None, dacl, None,
        )
        if result != 0:
            raise _SyntheticDaclUnavailable("synthetic_dacl_unavailable")
    finally:
        kernel.LocalFree(descriptor)
    snapshot = _named_dacl(path)
    if not snapshot[1]:
        raise _SyntheticDaclUnavailable("synthetic_dacl_unavailable")
    return snapshot


def fixture(base: Path):
    repo, source, _external = layout(base)
    document = source / "mathematics" / "grade-7" / "synthetic.tex"
    document.write_text(
        r"\begin{aufgabe}Berechne 2+2. " + SENTINEL
        + r"\end{aufgabe}",
        encoding="utf-8",
    )
    path = repo / config.DEFAULT_CONFIG
    write_json(path, valid(source, False))
    return repo, source, path


def artifacts(repo: Path):
    state = repo / config.STATE_DIRECTORY
    names = {
        activation.TRANSACTION_FILENAME,
        activation.CONFIG_BACKUP_FILENAME,
        activation.STAGED_CONFIG_FILENAME,
        activation.INDEX_BACKUP_FILENAME,
        activation.MANIFEST_TEMP_FILENAME,
        activation.INDEX_TEMP_FILENAME,
    }
    return {name for name in names if (state / name).exists()}


class ActivationTests(unittest.TestCase):
    def test_confirmation_stage_and_byte_exact_rollback(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            before = path.read_bytes()
            result = activation.stage_activation(repo)
            self.assertEqual(result.reason_code, "activation_confirmation_required")
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse((repo / config.STATE_DIRECTORY).exists())

            result = activation.stage_activation(repo, confirmed=True)
            self.assertEqual(result.reason_code, "activation_staged")
            self.assertEqual(path.read_bytes(), before)
            staged = json.loads(
                activation.staged_config_path(repo).read_text(encoding="utf-8")
            )
            original = json.loads(before.decode("utf-8"))
            self.assertFalse(original["enabled"])
            self.assertTrue(staged["enabled"])
            staged["enabled"] = False
            self.assertEqual(staged, original)

            rolled = activation.rollback_activation(repo, confirmed=True)
            self.assertEqual(rolled.reason_code, "activation_rolled_back")
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(artifacts(repo), set())

    def test_full_staged_commit_and_finalize_flow(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            self.assertTrue(
                activation.stage_activation(repo, confirmed=True).succeeded
            )
            index.build_local_index(
                repo, explicit_config=activation.staged_config_path(repo),
                environ={},
            )
            self.assertTrue(activation.attest_index(
                repo, phase="staged", confirmed=True).succeeded)
            committed = activation.commit_activation(repo, confirmed=True)
            self.assertEqual(committed.reason_code, "activation_committed")
            self.assertTrue(json.loads(path.read_text(encoding="utf-8"))["enabled"])
            self.assertTrue(artifacts(repo))

            index.build_local_index(repo, explicit_config=path, environ={})
            self.assertTrue(activation.attest_index(
                repo, phase="final", confirmed=True).succeeded)
            finalized = activation.finalize_activation(repo, confirmed=True)
            self.assertEqual(finalized.reason_code, "activation_finalized")
            self.assertEqual(artifacts(repo), set())
            self.assertTrue(json.loads(path.read_text(encoding="utf-8"))["enabled"])
            index.load_valid_index(repo, explicit_config=path, environ={})

    def test_default_config_is_fixed_and_environment_cannot_redirect(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            redirected = str(Path(tmp) / (SENTINEL + ".json"))
            with patch.dict(
                    os.environ,
                    {config.ENVIRONMENT_VARIABLE: redirected},
                    clear=False):
                staged = activation.stage_activation(repo, confirmed=True)
            self.assertTrue(staged.succeeded, staged.safe_dict())
            self.assertEqual(path, repo / config.DEFAULT_CONFIG)
            self.assertEqual(
                activation.staged_config_path(repo),
                repo / config.STATE_DIRECTORY / activation.STAGED_CONFIG_FILENAME,
            )
            self.assertTrue(activation.rollback_activation(
                repo, confirmed=True).succeeded)

    def test_operation_holds_exclusive_build_lock_lease(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, _path = fixture(Path(tmp))
            observed = []
            original = activation._validate_active_runtime

            def validate_while_locked(repo_root, staged):
                lock = (
                    repo_root / config.STATE_DIRECTORY / index.LOCK_FILENAME
                )
                observed.append(lock.exists())
                with self.assertRaises(index.IndexFault) as caught:
                    index.build_local_index(
                        repo_root, explicit_config=staged, environ={}
                    )
                self.assertEqual(caught.exception.code, "index_build_busy")
                return original(repo_root, staged)

            with patch.object(
                    activation, "_validate_active_runtime",
                    side_effect=validate_while_locked):
                result = activation.stage_activation(repo, confirmed=True)
            self.assertTrue(result.succeeded, result.safe_dict())
            self.assertEqual(observed, [True])
            self.assertFalse(
                (repo / config.STATE_DIRECTORY / index.LOCK_FILENAME).exists()
            )
            self.assertTrue(activation.rollback_activation(
                repo, confirmed=True).succeeded)

    def test_custom_protected_dacl_survives_commit_and_rollback(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            try:
                original_dacl = _protect_named_dacl(path)
            except _SyntheticDaclUnavailable:
                self.skipTest("synthetic_dacl_unavailable")
            self.assertTrue(
                activation.stage_activation(repo, confirmed=True).succeeded
            )
            index.build_local_index(
                repo, explicit_config=activation.staged_config_path(repo),
                environ={},
            )
            self.assertTrue(activation.attest_index(
                repo, phase="staged", confirmed=True).succeeded)
            committed = activation.commit_activation(repo, confirmed=True)
            self.assertTrue(committed.succeeded, committed.safe_dict())
            self.assertTrue(_named_dacl(path) == original_dacl)
            rolled = activation.rollback_activation(repo, confirmed=True)
            self.assertTrue(rolled.succeeded, rolled.safe_dict())
            self.assertTrue(_named_dacl(path) == original_dacl)

    def test_dacl_failure_blocks_publish_without_leaking(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            before = path.read_bytes()
            before_identity = (path.stat().st_dev, path.stat().st_ino)
            self.assertTrue(
                activation.stage_activation(repo, confirmed=True).succeeded
            )
            index.build_local_index(
                repo, explicit_config=activation.staged_config_path(repo),
                environ={},
            )
            self.assertTrue(activation.attest_index(
                repo, phase="staged", confirmed=True).succeeded)
            with patch.object(
                    activation, "_read_windows_dacl",
                    side_effect=OSError(SENTINEL)):
                blocked = activation.commit_activation(repo, confirmed=True)
            self.assertEqual(blocked.reason_code,
                             "activation_permissions_unavailable")
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(
                (path.stat().st_dev, path.stat().st_ino), before_identity
            )
            self.assertNotIn(
                SENTINEL, json.dumps(blocked.safe_dict()) + repr(blocked)
            )
            self.assertTrue(activation.rollback_activation(
                repo, confirmed=True).succeeded)

    def test_dacl_change_before_rename_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            before = path.read_bytes()
            before_identity = (path.stat().st_dev, path.stat().st_ino)
            self.assertTrue(
                activation.stage_activation(repo, confirmed=True).succeeded
            )
            index.build_local_index(
                repo, explicit_config=activation.staged_config_path(repo),
                environ={},
            )
            self.assertTrue(activation.attest_index(
                repo, phase="staged", confirmed=True).succeeded)
            original = activation._read_windows_dacl
            calls = []

            def changed_before_rename(descriptor):
                snapshot = original(descriptor)
                calls.append(True)
                if len(calls) == 5:
                    return activation._DaclSnapshot(
                        snapshot.owner,
                        snapshot.group,
                        snapshot.acl,
                        not snapshot.protected,
                    )
                return snapshot

            with patch.object(
                    activation, "_read_windows_dacl",
                    side_effect=changed_before_rename):
                blocked = activation.commit_activation(repo, confirmed=True)
            self.assertEqual(blocked.reason_code,
                             "activation_permissions_unavailable")
            self.assertGreaterEqual(len(calls), 5)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(
                (path.stat().st_dev, path.stat().st_ino), before_identity
            )
            self.assertTrue(activation.rollback_activation(
                repo, confirmed=True).succeeded)

    def test_rollback_restores_preexisting_index_exactly(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            state = repo / config.STATE_DIRECTORY
            state.mkdir(parents=True)
            baseline = b"SYNTHETIC-BASELINE-INDEX\0" + SENTINEL.encode()
            target = state / index.INDEX_FILENAME
            target.write_bytes(baseline)
            before_config = path.read_bytes()
            self.assertTrue(
                activation.stage_activation(repo, confirmed=True).succeeded
            )
            index.build_local_index(
                repo, explicit_config=activation.staged_config_path(repo),
                environ={},
            )
            self.assertTrue(activation.attest_index(
                repo, phase="staged", confirmed=True).succeeded)
            rolled = activation.rollback_activation(repo, confirmed=True)
            self.assertTrue(rolled.succeeded, rolled.safe_dict())
            self.assertEqual(target.read_bytes(), baseline)
            self.assertEqual(path.read_bytes(), before_config)

    def test_build_lock_mutation_and_write_failure_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            before = path.read_bytes()
            state = repo / config.STATE_DIRECTORY
            state.mkdir(parents=True)
            lock = state / index.LOCK_FILENAME
            lock.write_bytes(b"synthetic-lock")
            blocked = activation.stage_activation(repo, confirmed=True)
            self.assertEqual(blocked.reason_code, "activation_build_lock_present")
            self.assertEqual(lock.read_bytes(), b"synthetic-lock")
            self.assertEqual(path.read_bytes(), before)
            lock.unlink()
            with patch.object(
                    activation, "_write_all", side_effect=OSError(SENTINEL)):
                failed = activation.stage_activation(repo, confirmed=True)
            self.assertEqual(failed.reason_code, "activation_operational_error")
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(artifacts(repo), set())
            self.assertNotIn(SENTINEL, json.dumps(failed.safe_dict()) + repr(failed))

    def test_build_lock_after_stage_blocks_transaction_without_removal(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            before = path.read_bytes()
            self.assertTrue(
                activation.stage_activation(repo, confirmed=True).succeeded
            )
            lock = repo / config.STATE_DIRECTORY / index.LOCK_FILENAME
            lock.write_bytes(b"synthetic-active-build")
            blocked = activation.rollback_activation(repo, confirmed=True)
            self.assertEqual(blocked.reason_code,
                             "activation_build_lock_present")
            self.assertEqual(lock.read_bytes(), b"synthetic-active-build")
            self.assertEqual(path.read_bytes(), before)
            lock.unlink()
            self.assertTrue(activation.rollback_activation(
                repo, confirmed=True).succeeded)

    def test_rollback_rejects_same_byte_leaf_exchanges(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            state = repo / config.STATE_DIRECTORY
            state.mkdir(parents=True)
            index_path = state / index.INDEX_FILENAME
            baseline = b"SYNTHETIC-SAME-BYTE-BASELINE"
            index_path.write_bytes(baseline)
            self.assertTrue(
                activation.stage_activation(repo, confirmed=True).succeeded
            )

            original_config = path.with_name("synthetic-original-config")
            path.replace(original_config)
            path.write_bytes(original_config.read_bytes())
            rejected = activation.rollback_activation(repo, confirmed=True)
            self.assertEqual(rejected.reason_code,
                             "activation_configuration_changed")
            path.unlink()
            original_config.replace(path)

            original_index = state / "synthetic-original-index"
            index_path.replace(original_index)
            index_path.write_bytes(baseline)
            rejected = activation.rollback_activation(repo, confirmed=True)
            self.assertEqual(rejected.reason_code, "activation_index_changed")
            index_path.unlink()
            original_index.replace(index_path)
            self.assertTrue(activation.rollback_activation(
                repo, confirmed=True).succeeded)

    def test_changed_config_and_hardlinks_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="schullia-activation-") as tmp:
            repo, _source, path = fixture(Path(tmp))
            before = path.read_bytes()
            before_metadata = path.stat()
            alias = Path(tmp) / "synthetic-config-alias"
            try:
                os.link(path, alias)
            except (OSError, NotImplementedError):
                pass
            else:
                rejected = activation.stage_activation(repo, confirmed=True)
                self.assertEqual(rejected.reason_code,
                                 "activation_boundary_rejected")
                alias.unlink()
            self.assertEqual(path.read_bytes(), before)

            self.assertTrue(
                activation.stage_activation(repo, confirmed=True).succeeded
            )
            index.build_local_index(
                repo, explicit_config=activation.staged_config_path(repo),
                environ={},
            )
            self.assertTrue(activation.attest_index(
                repo, phase="staged", confirmed=True).succeeded)
            path.write_bytes(before + b" ")
            rejected = activation.commit_activation(repo, confirmed=True)
            self.assertEqual(rejected.reason_code,
                             "activation_configuration_changed")
            path.write_bytes(before)
            os.utime(
                path,
                ns=(before_metadata.st_atime_ns, before_metadata.st_mtime_ns),
            )
            self.assertTrue(activation.rollback_activation(
                repo, confirmed=True).succeeded)

    def test_cli_projection_is_closed_and_sanitized(self):
        with tempfile.TemporaryDirectory(
                prefix="schullia-" + SENTINEL + "-") as tmp:
            repo, _source, _path = fixture(Path(tmp))
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = activation.main([
                    "stage", "--repo-root", str(repo), "--json",
                ])
            self.assertEqual(code, 1)
            payload = json.loads(out.getvalue())
            self.assertEqual(set(payload), {"status", "reason_code"})
            self.assertNotIn(SENTINEL, out.getvalue() + err.getvalue())
            self.assertEqual(repr(activation.stage_activation(repo)),
                             "ActivationResult(<closed-status>)")


def main() -> int:
    if os.name != "nt":
        result = activation.stage_activation(
            Path(tempfile.gettempdir()), confirmed=True
        )
        assert result.reason_code == "activation_platform_unsupported"
        print("PASS POSIX activation fails closed; SKIP Windows transaction tests")
        return 0
    unittest.main(exit=False)
    result = unittest.TestResult()
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    if os.name == "nt":
        unittest.main()
    else:
        raise SystemExit(main())
