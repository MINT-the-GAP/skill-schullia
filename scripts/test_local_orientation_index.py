#!/usr/bin/env python3
"""Synthetic persistence, freshness and privacy regressions; no real sources."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import tempfile
import threading
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

import local_orientation_config as config
import local_orientation_index as index
import local_orientation_metadata as metadata
import local_orientation_tex as tex
from test_local_orientation_security import (
    layout, valid, write_json, create_directory_link,
)


SENTINEL = "PRIVATE_SOURCE_SENTINEL_DO_NOT_EXPORT"


def fixture(base):
    repo, source, config_path = layout(base)
    allowed = source / "mathematics" / "grade-7"
    (allowed / "a.tex").write_text(
        "\\begin{aufgabe}\nNenne " + SENTINEL + ".\n\\end{aufgabe}\n"
        "\\input{b}\n", encoding="utf-8")
    (allowed / "b.tex").write_text(
        "\\begin{aufgabe}Berechne 2+2.\\end{aufgabe}\n"
        "\\begin{loesung}4\\end{loesung}\n", encoding="utf-8")
    write_json(config_path, valid(source))
    return repo, source, config_path


def digest_sources(source):
    return {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in source.rglob("*.tex")}


def build(repo, config_path, **kwargs):
    return index.build_local_index(repo, explicit_config=config_path, environ={}, **kwargs)


def load(repo, config_path, **kwargs):
    return index.load_valid_index(repo, explicit_config=config_path, environ={}, **kwargs)


def expect_fault(action, codes, secrets=()):
    if isinstance(codes, str):
        codes = {codes}
    try:
        action()
    except index.IndexFault as error:
        assert error.code in codes, (error.code, codes)
        assert error.__cause__ is None and error.__context__ is None
        surface = str(error) + repr(error)
        for secret in (SENTINEL, *secrets):
            assert secret not in surface
        return error
    raise AssertionError("expected sanitized IndexFault")


def index_path(repo):
    return repo / config.STATE_DIRECTORY / index.INDEX_FILENAME


def mutate_database(path, action):
    connection = sqlite3.connect(":memory:")
    try:
        connection.deserialize(path.read_bytes())
        action(connection)
        connection.commit()
        path.write_bytes(connection.serialize())
    finally:
        connection.close()


def test_build_load_readonly_and_privacy():
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        before = digest_sources(source)
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = build(repo, config_path)
            snapshot = load(repo, config_path)
        assert not stdout.getvalue() and not stderr.getvalue()
        assert len(snapshot.documents) == 2 and len(snapshot.edges) == 1
        assert snapshot.index_ready
        payload = json.dumps(result.safe_dict())
        assert result.safe_dict()["orientation_profile_prepared"] is False
        for secret in (str(source), str(config_path), SENTINEL, "source-one", "a.tex"):
            assert secret not in payload + repr(snapshot)
        assert "count" not in payload
        raw = index_path(repo).read_bytes()
        assert SENTINEL.encode() not in raw and str(source).encode() not in raw
        before_state = {p.name: (p.read_bytes(), p.stat().st_mtime_ns)
                        for p in index_path(repo).parent.iterdir()}
        load(repo, config_path)
        after_state = {p.name: (p.read_bytes(), p.stat().st_mtime_ns)
                       for p in index_path(repo).parent.iterdir()}
        assert before_state == after_state
        assert before == digest_sources(source)
        assert set(before_state) == {index.INDEX_FILENAME}


def test_source_mutation_deletion_and_inventory_addition():
    for mode in ("same-mtime", "deletion", "addition"):
        with tempfile.TemporaryDirectory() as temporary:
            repo, source, config_path = fixture(Path(temporary))
            build(repo, config_path)
            target = source / "mathematics" / "grade-7" / "b.tex"
            original = target.stat()
            if mode == "same-mtime":
                value = target.read_bytes().replace(b"2+2", b"3+3")
                target.write_bytes(value)
                os.utime(target, ns=(original.st_atime_ns, original.st_mtime_ns))
            elif mode == "deletion":
                target.unlink()
            else:
                (target.parent / "c.tex").write_text("Synthetic extra", encoding="utf-8")
            expect_fault(lambda: load(repo, config_path), "index_stale",
                         (str(source), target.name))


def test_configuration_revocation_and_disabled_no_traversal():
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        build(repo, config_path)
        disabled = valid(source, False)
        write_json(config_path, disabled)
        with patch.object(index.includes, "analyze_sources", side_effect=AssertionError("must not traverse")):
            fault = expect_fault(lambda: load(repo, config_path), "configuration_disabled")
            assert fault.state == config.STATE_NOT_CONFIGURED
        changed = valid(source)
        changed["sources"][0]["exclude"].append("mathematics/grade-7/b.tex")
        write_json(config_path, changed)
        expect_fault(lambda: load(repo, config_path), "index_configuration_changed")
        write_json(config_path, valid(source))
        expect_fault(lambda: load(repo, config_path), "index_configuration_changed")
        build(repo, config_path)
        assert len(load(repo, config_path).documents) == 2


def test_missing_corrupt_schema_and_version():
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        expect_fault(lambda: load(repo, config_path), "index_missing")
        build(repo, config_path)
        path = index_path(repo)
        original = path.read_bytes()
        path.write_bytes(b"not sqlite " + SENTINEL.encode())
        expect_fault(lambda: load(repo, config_path), "index_corrupt")
        path.write_bytes(original)
        mutate_database(path, lambda db: db.execute("CREATE TABLE unwanted (x)"))
        expect_fault(lambda: load(repo, config_path), "index_schema_invalid")
        path.write_bytes(original)
        def change_manifest(db):
            value = json.loads(db.execute("SELECT payload FROM manifest").fetchone()[0])
            value["index_version"] = 999
            db.execute("UPDATE manifest SET payload=?", (json.dumps(value),))
        mutate_database(path, change_manifest)
        expect_fault(lambda: load(repo, config_path), "index_version_unsupported")
        path.write_bytes(original)
        def inject_raw(db):
            value = json.loads(db.execute("SELECT payload FROM documents WHERE ordinal=1").fetchone()[0])
            value["snippet"] = SENTINEL
            db.execute("UPDATE documents SET payload=? WHERE ordinal=1", (json.dumps(value),))
        mutate_database(path, inject_raw)
        expect_fault(lambda: load(repo, config_path), "metadata_invalid")
        path.write_bytes(original)
        def change_structural_count(db):
            value = json.loads(db.execute("SELECT payload FROM documents WHERE ordinal=1").fetchone()[0])
            value["structure"]["task_count"] += 1
            db.execute("UPDATE documents SET payload=? WHERE ordinal=1", (json.dumps(value),))
        mutate_database(path, change_structural_count)
        expect_fault(lambda: load(repo, config_path), "metadata_invalid")
        path.write_bytes(original)
        def schema_valid_tamper(db):
            value = json.loads(db.execute("SELECT payload FROM documents WHERE ordinal=1").fetchone()[0])
            value["classification"]["grades"] = [9]
            db.execute("UPDATE documents SET payload=? WHERE ordinal=1", (json.dumps(value),))
        mutate_database(path, schema_valid_tamper)
        expect_fault(lambda: load(repo, config_path), "index_stale")


def test_feature_taxonomy_fingerprint_invalidates_an_old_index():
    with tempfile.TemporaryDirectory() as temporary:
        repo, _source, config_path = fixture(Path(temporary))
        build(repo, config_path)
        with patch.object(index, "_versions_fingerprint", return_value="0" * 64):
            expect_fault(
                lambda: load(repo, config_path), "index_version_unsupported"
            )


def test_build_abort_preserves_prior_and_sanitizes_faults():
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        build(repo, config_path)
        original = index_path(repo).read_bytes()
        for fault_target in ("_serialize_graph", "_publish"):
            with patch.object(index, fault_target, side_effect=OSError(str(source) + SENTINEL)):
                expect_fault(lambda: build(repo, config_path), "index_operational_error",
                             (str(source),))
            assert index_path(repo).read_bytes() == original
            assert not (index_path(repo).parent / index.LOCK_FILENAME).exists()
        with patch.object(index.sqlite3, "connect", side_effect=sqlite3.DatabaseError(str(source))):
            expect_fault(lambda: load(repo, config_path), "index_operational_error", (str(source),))


def test_actual_write_failure_preserves_prior():
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        build(repo, config_path)
        original = index_path(repo).read_bytes()
        with patch.object(index.os, "write", side_effect=OSError(str(source) + SENTINEL)):
            expect_fault(lambda: build(repo, config_path), "index_operational_error", (str(source),))
        assert index_path(repo).read_bytes() == original
        assert set(p.name for p in index_path(repo).parent.iterdir()) == {index.INDEX_FILENAME}


def test_build_lock_parallel_and_readers():
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        build(repo, config_path)
        started, release = threading.Event(), threading.Event()
        original_analyze = index._analyze
        errors = []
        def blocked(*args):
            if threading.current_thread().name == "synthetic-builder":
                started.set()
                if not release.wait(10):
                    raise RuntimeError("synthetic timeout")
            return original_analyze(*args)
        def worker():
            try:
                build(repo, config_path)
            except BaseException as error:
                errors.append(error)
        with patch.object(index, "_analyze", side_effect=blocked):
            thread = threading.Thread(target=worker, name="synthetic-builder")
            thread.start()
            try:
                assert started.wait(10)
                expect_fault(lambda: build(repo, config_path), "index_build_busy")
                assert len(load(repo, config_path).documents) == 2
            finally:
                release.set()
                thread.join(15)
        assert not thread.is_alive() and not errors


def test_links_hardlinks_and_state_replacement():
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, config_path = fixture(base)
        zone = repo / config.LOCAL_ZONE
        outside = base / "outside"
        outside.mkdir()
        if create_directory_link(zone, outside):
            expect_fault(lambda: build(repo, config_path), {
                "local_zone_link_boundary", "state_directory_invalid"})
            zone.unlink() if zone.is_symlink() else os.rmdir(zone)
            assert not list(outside.iterdir())
        else:
            print("SKIP state-directory link creation unavailable")
        build(repo, config_path)
        path = index_path(repo)
        linked = base / "hardlink-copy"
        try:
            os.link(path, linked)
        except (OSError, NotImplementedError):
            print("SKIP hardlink creation unavailable")
        else:
            expect_fault(lambda: load(repo, config_path), "state_file_invalid")
            linked.unlink()
        original = path.read_bytes()
        real_replace = index.os.replace
        def replace_with_attacker_file(source_path, target_path):
            path.write_bytes(b"attacker index")
            return real_replace(source_path, target_path)
        # A pre-publication mutation is rejected before replacement.
        original_signature = index._StateGuard(repo, create=False).existing_index_signature()
        guard = index._StateGuard(repo, create=False)
        lock_fd, lock_id = index._create_bound_file(guard.lock, guard)
        try:
            path.write_bytes(b"attacker index")
            expect_fault(lambda: index._sanitized(
                index._publish, original, guard, original_signature,
                lock_fd, lock_id, index.time.monotonic() + 5),
                "state_file_changed")
        finally:
            os.close(lock_fd)
            index._safe_unlink(guard.lock, lock_id, guard)
            guard.close()


def test_parent_lease_blocks_state_swap_before_creation():
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, config_path = fixture(base)
        build(repo, config_path)
        guard = index._StateGuard(repo, create=False)
        old_state = guard.state.with_name("state-old")
        real_open = index._windows_relative_handle if os.name == "nt" else index.os.open
        swap_attempted = []
        def swap_before_open(*args, **kwargs):
            name = args[1] if os.name == "nt" else args[0]
            if Path(name).name == index.LOCK_FILENAME:
                swap_attempted.append(True)
                try:
                    guard.state.rename(old_state)
                except OSError:
                    pass  # Windows directory lease denies the rename.
                else:
                    assert os.name != "nt", "Windows lease failed"
                    assert create_directory_link(guard.state, source)
            return real_open(*args, **kwargs)
        try:
            target, attribute = (index, "_windows_relative_handle") if os.name == "nt" else (index.os, "open")
            with patch.object(target, attribute, side_effect=swap_before_open):
                try:
                    descriptor, identity = index._create_bound_file(guard.lock, guard)
                except index.IndexFault:
                    pass
                else:
                    os.close(descriptor)
                    index._safe_unlink(guard.lock, identity, guard)
            assert swap_attempted
            assert not (source / index.LOCK_FILENAME).exists()
        finally:
            guard.close()
            if old_state.exists():
                if guard.state.exists() or guard.state.is_symlink():
                    guard.state.unlink() if guard.state.is_symlink() else os.rmdir(guard.state)
                old_state.rename(guard.state)


def test_cleanup_preserves_a_replaced_leaf():
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, config_path = fixture(base)
        guard = index._StateGuard(repo, create=True)
        descriptor, identity = index._create_bound_file(guard.lock, guard)
        os.close(descriptor)
        replacement = b"synthetic-replacement-must-survive"
        renamed = guard.state / "original-lock"
        original_open = guard.open_windows_child
        def swap_before_open(path, **kwargs):
            if kwargs.get("deleting") and path == guard.lock:
                guard.lock.rename(renamed)
                guard.lock.write_bytes(replacement)
            return original_open(path, **kwargs)
        try:
            with patch.object(guard, "open_windows_child", side_effect=swap_before_open):
                index._safe_unlink(guard.lock, identity, guard)
            assert guard.lock.read_bytes() == replacement
            assert renamed.exists()
        finally:
            guard.close()


def test_publish_rejects_replaced_temporary_leaf_before_rename():
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        build(repo, config_path)
        original_index = index_path(repo).read_bytes()
        original_replace = index._StateGuard.replace_bound
        def swap_before_rename(guard, temporary_path, expected_identity):
            old = temporary_path.with_suffix(".saved")
            temporary_path.rename(old)
            temporary_path.write_bytes(b"foreign-temp-must-not-be-published")
            return original_replace(guard, temporary_path, expected_identity)
        with patch.object(index._StateGuard, "replace_bound", new=swap_before_rename):
            expect_fault(lambda: build(repo, config_path), "state_file_changed")
        assert index_path(repo).read_bytes() == original_index


def test_inplace_reparse_before_native_create_is_fail_closed():
    if os.name != "nt":
        print("SKIP Windows FSCTL reparse regression on non-Windows platform")
        return
    import ctypes
    import struct
    from ctypes import wintypes
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        guard = index._StateGuard(repo, create=True)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateFileW.argtypes = (
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        )
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel.DeviceIoControl.argtypes = (
            wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
            wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
            wintypes.LPVOID,
        )
        kernel.DeviceIoControl.restype = wintypes.BOOL
        handle = kernel.CreateFileW(str(guard.state), 0x40000000, 0x7, None, 3,
                                    0x02200000, None)
        if handle == ctypes.c_void_p(-1).value:
            guard.close()
            raise AssertionError("synthetic reparse writer unavailable")
        changed = []
        original_native = index._windows_relative_handle
        substitute = (chr(92) + "??" + chr(92) + str(source)).encode("utf-16-le")
        printed = str(source).encode("utf-16-le")
        payload = struct.pack("<HHHH", 0, len(substitute), len(substitute) + 2,
                              len(printed)) + substitute + b"\0\0" + printed + b"\0\0"
        raw = struct.pack("<IHH", 0xA0000003, len(payload), 0) + payload
        def native_after_reparse(parent, name, **kwargs):
            if name == index.LOCK_FILENAME:
                returned = wintypes.DWORD()
                buffer = ctypes.create_string_buffer(raw)
                assert kernel.DeviceIoControl(
                    handle, 0x900A4, buffer, len(raw), None, 0,
                    ctypes.byref(returned), None)
                changed.append(True)
            return original_native(parent, name, **kwargs)
        before = digest_sources(source)
        try:
            with patch.object(index, "_windows_relative_handle", side_effect=native_after_reparse):
                expect_fault(lambda: index._sanitized(
                    index._create_bound_file, guard.lock, guard),
                    "state_relative_open_failed", (str(source),))
            assert changed
            assert not (source / index.LOCK_FILENAME).exists()
            assert before == digest_sources(source)
        finally:
            if changed:
                delete = ctypes.create_string_buffer(struct.pack("<IHH", 0xA0000003, 0, 0))
                returned = wintypes.DWORD()
                assert kernel.DeviceIoControl(
                    handle, 0x900AC, delete, 8, None, 0,
                    ctypes.byref(returned), None)
            kernel.CloseHandle(handle)
            guard.close()


def test_source_state_and_config_identity_fail_closed():
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        build(repo, config_path)
        with patch.object(index, "_identity", side_effect=index.IndexFault("state_identity_unavailable")):
            expect_fault(lambda: load(repo, config_path), "state_identity_unavailable")
        raw = config_path.read_bytes()
        original_read = index._read_blob
        count = 0
        def changed_configuration(*args, **kwargs):
            nonlocal count
            result = original_read(*args, **kwargs)
            if args[0] == config_path:
                count += 1
                if count == 1:
                    config_path.write_bytes(raw + b" ")
            return result
        with patch.object(index, "_read_blob", side_effect=changed_configuration):
            expect_fault(lambda: load(repo, config_path), "configuration_changed")


def test_limits_schema_types_relations_and_no_execution():
    bad_limits = (
        {"max_documents": 513}, {"max_seconds": 31}, {"max_edges": True},
        {"max_file_bytes": 5 * 1024 * 1024}, {"max_index_bytes": 0},
    )
    for values in bad_limits:
        try:
            index.IndexLimits(**values)
        except ValueError:
            pass
        else:
            raise AssertionError("unbounded limits accepted")
    payload = tex.parse_tex_text(
        "\\begin{aufgabe}Nenne etwas.\\end{aufgabe}").as_dict()
    metadata.validate_metadata(payload)
    alterations = []
    value = copy.deepcopy(payload)
    value["schema_version"] = True
    alterations.append(value)
    value = copy.deepcopy(payload)
    value["tasks"][0]["line_span"]["end"] = 999
    alterations.append(value)
    value = copy.deepcopy(payload)
    value["tasks"][0]["solution_presence"] = "present"
    alterations.append(value)
    value = copy.deepcopy(payload)
    value["local_provenance"]["relative_locator"] = "a.tex\n"
    alterations.append(value)
    for value in alterations:
        try:
            metadata.validate_metadata(value)
        except metadata.MetadataFault:
            pass
        else:
            raise AssertionError("invalid metadata accepted")
    with tempfile.TemporaryDirectory() as temporary:
        repo, source, config_path = fixture(Path(temporary))
        real_run = subprocess.run
        def git_only(command, *args, **kwargs):
            if command[0] != "git":
                raise AssertionError("unexpected process")
            return real_run(command, *args, **kwargs)
        with patch.object(subprocess, "run", side_effect=git_only), \
                patch.object(socket, "socket", side_effect=AssertionError("network forbidden")):
            build(repo, config_path)
            load(repo, config_path)
        expect_fault(lambda: build(repo, config_path, limits=index.IndexLimits(max_documents=1)),
                     {"candidate_limit", "include_node_limit"})
        expect_fault(lambda: load(repo, config_path, limits=index.IndexLimits(max_index_bytes=100)),
                     "index_size_limit")


def main():
    if os.name != "nt":
        with tempfile.TemporaryDirectory() as temporary:
            repo, source, config_path = fixture(Path(temporary))
            expect_fault(lambda: build(repo, config_path), "state_platform_unsupported")
        print("PASS POSIX build fails closed; SKIP Windows native persistence tests")
        return 0
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print("Local orientation index tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
