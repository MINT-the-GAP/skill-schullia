#!/usr/bin/env python3
"""Dependency-free synthetic regressions for local TeX orientation."""

from __future__ import annotations

import copy
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
from typing import Callable, Iterable, Mapping

import local_orientation_candidates as candidates
import local_orientation_config as config
import local_orientation_tex as tex


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "references" / "local-orientation-metadata.schema.json"
TAXONOMY = ROOT / "references" / "operator-taxonomy.json"


def write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def write_tex(path: Path, value: str, encoding: str = "utf-8") -> None:
    write_bytes(path, value.encode(encoding))


def create_directory_link(link: Path, target: Path) -> bool:
    try:
        link.symlink_to(target, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        if os.name != "nt":
            return False
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        cwd=link.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0


def validated_source(
    root: Path,
    *,
    include: tuple[str, ...] = ("allowed",),
    exclude: tuple[str, ...] = ("allowed/archive",),
) -> config.ValidatedSource:
    return config.ValidatedSource(
        source_id="synthetic-source",
        root=root.resolve(),
        include=include,
        exclude=exclude,
        allowed_extensions=(".tex",),
        subjects=("mathematics",),
        grades=(7,),
        learner_groups=(),
        document_types=("worksheet",),
        archive_policy="exclude",
    )


def locator_list(result: candidates.DiscoveryResult) -> list[str]:
    return [candidate.relative_locator for candidate in result.candidates]


def exception_surface(error: BaseException) -> str:
    values: list[str] = []
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        values.extend((str(current), repr(current)))
        current = current.__cause__ or current.__context__
    return "\n".join(values)


def expect_discovery_fault(
    code: str,
    action: Callable[[], object],
    *,
    secrets: Iterable[str] = (),
) -> candidates.DiscoveryFault:
    try:
        action()
    except candidates.DiscoveryFault as error:
        assert error.code == code, (code, error.code)
        surface = exception_surface(error)
        for secret in secrets:
            assert secret not in surface, (code, secret)
        return error
    raise AssertionError(f"expected DiscoveryFault {code}")


def expect_tex_fault(
    code: str,
    action: Callable[[], object],
    *,
    secrets: Iterable[str] = (),
) -> tex.TexParseFault:
    try:
        action()
    except tex.TexParseFault as error:
        assert error.code == code, (code, error.code)
        surface = exception_surface(error)
        for secret in secrets:
            assert secret not in surface, (code, secret)
        return error
    raise AssertionError(f"expected TexParseFault {code}")


def schema_node(schema: Mapping[str, object], reference: str) -> Mapping[str, object]:
    assert reference.startswith("#/$defs/")
    value = schema["$defs"]
    assert isinstance(value, Mapping)
    node = value[reference.removeprefix("#/$defs/")]
    assert isinstance(node, Mapping)
    return node


def validate_schema_value(
    value: object,
    node: Mapping[str, object],
    schema: Mapping[str, object],
) -> None:
    reference = node.get("$ref")
    if isinstance(reference, str):
        validate_schema_value(value, schema_node(schema, reference), schema)
        return
    if "const" in node:
        assert value == node["const"]
    enum = node.get("enum")
    if isinstance(enum, list):
        assert value in enum

    kind = node.get("type")
    if kind == "object":
        assert isinstance(value, Mapping)
        required = node.get("required", [])
        assert isinstance(required, list)
        assert set(required).issubset(value)
        properties = node.get("properties", {})
        assert isinstance(properties, Mapping)
        if node.get("additionalProperties") is False:
            assert set(value).issubset(properties)
        for key, item in value.items():
            child = properties.get(key)
            if isinstance(child, Mapping):
                validate_schema_value(item, child, schema)
    elif kind == "array":
        assert isinstance(value, list)
        minimum = node.get("minItems")
        maximum = node.get("maxItems")
        if isinstance(minimum, int):
            assert len(value) >= minimum
        if isinstance(maximum, int):
            assert len(value) <= maximum
        if node.get("uniqueItems"):
            serial = [json.dumps(item, sort_keys=True) for item in value]
            assert len(serial) == len(set(serial))
        items = node.get("items")
        if isinstance(items, Mapping):
            for item in value:
                validate_schema_value(item, items, schema)
    elif kind == "string":
        assert isinstance(value, str)
        minimum = node.get("minLength")
        maximum = node.get("maxLength")
        if isinstance(minimum, int):
            assert len(value) >= minimum
        if isinstance(maximum, int):
            assert len(value) <= maximum
        pattern = node.get("pattern")
        if isinstance(pattern, str):
            assert re.search(pattern, value)
    elif kind == "integer":
        assert type(value) is int
        minimum = node.get("minimum")
        maximum = node.get("maximum")
        if isinstance(minimum, int):
            assert value >= minimum
        if isinstance(maximum, int):
            assert value <= maximum


def assert_metadata_matches_schema(payload: Mapping[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert isinstance(schema, Mapping)
    validate_schema_value(payload, schema, schema)


def test_candidate_selection_and_privacy() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-source-root"
        selected = root / "allowed"
        write_tex(selected / "b.tex", "B")
        write_tex(selected / "a.tex", "A")
        write_tex(selected / "upper.TEX", "C")
        write_tex(selected / "archive" / "hidden.tex", "HIDDEN")
        write_tex(root / "other" / "outside.tex", "OUTSIDE")
        (selected / "ignored.txt").write_text("ignored", encoding="utf-8")
        before = {
            path.relative_to(root).as_posix(): (
                path.read_bytes(),
                path.stat().st_mtime_ns,
            )
            for path in root.rglob("*")
            if path.is_file()
        }

        source = validated_source(
            root,
            include=("allowed", "allowed/**/*.tex"),
        )
        result = candidates.enumerate_candidates(source)
        assert locator_list(result) == [
            "allowed/a.tex",
            "allowed/b.tex",
            "allowed/upper.TEX",
        ]
        assert result.selected_bytes == 3
        assert str(root) not in repr(result)
        for candidate in result.candidates:
            assert str(root) not in repr(candidate)
            assert candidate.relative_locator not in repr(candidate)
            assert candidates.read_candidate_bytes(candidate, 1024) in {
                b"A", b"B", b"C"
            }

        after = {
            path.relative_to(root).as_posix(): (
                path.read_bytes(),
                path.stat().st_mtime_ns,
            )
            for path in root.rglob("*")
            if path.is_file()
        }
        assert after == before


def test_candidate_rules_limits_and_mutation() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "sentinel-private-root"
        write_tex(root / "allowed" / "one.tex", "one")
        write_tex(root / "allowed" / "two.tex", "two")
        source = validated_source(root)

        expect_discovery_fault(
            "candidate_limit",
            lambda: candidates.enumerate_candidates(
                source, candidates.DiscoveryLimits(max_candidates=1)
            ),
            secrets=(str(root), "one.tex", "two.tex"),
        )
        expect_discovery_fault(
            "entry_limit",
            lambda: candidates.enumerate_candidates(
                source, candidates.DiscoveryLimits(max_entries=1)
            ),
            secrets=(str(root),),
        )
        expect_discovery_fault(
            "candidate_size_limit",
            lambda: candidates.enumerate_candidates(
                source,
                candidates.DiscoveryLimits(
                    max_file_bytes=2,
                    max_total_bytes=4,
                ),
            ),
            secrets=(str(root),),
        )
        expect_discovery_fault(
            "total_size_limit",
            lambda: candidates.enumerate_candidates(
                source,
                candidates.DiscoveryLimits(
                    max_file_bytes=4,
                    max_total_bytes=4,
                ),
            ),
            secrets=(str(root),),
        )
        expect_discovery_fault(
            "directory_limit",
            lambda: candidates.enumerate_candidates(
                source,
                candidates.DiscoveryLimits(max_directories=1),
            ),
            secrets=(str(root),),
        )
        expect_discovery_fault(
            "relative_rule_invalid",
            lambda: candidates.enumerate_candidates(
                validated_source(root, include=("../escape",))
            ),
            secrets=(str(root), "escape"),
        )

        only = candidates.enumerate_candidates(
            validated_source(root, include=("allowed/one.tex",))
        ).candidates[0]
        write_tex(root / "allowed" / "one.tex", "changed-size")
        expect_discovery_fault(
            "candidate_identity_changed",
            lambda: candidates.read_candidate_bytes(only, 1024),
            secrets=(str(root), "one.tex"),
        )

        stable = root / "allowed" / "stable.tex"
        write_tex(stable, "AAAA")
        attested = candidates.enumerate_candidates(
            validated_source(root, include=("allowed/stable.tex",))
        ).candidates[0]
        original = stable.stat()
        write_tex(stable, "BBBB")
        os.utime(
            stable,
            ns=(original.st_atime_ns, original.st_mtime_ns),
        )
        expect_discovery_fault(
            "candidate_identity_changed",
            lambda: candidates.read_candidate_bytes(attested, 1024),
            secrets=(str(root), "stable.tex", "BBBB"),
        )


def test_candidate_unreliable_identity_is_rejected_without_read() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-identity-root"
        target = root / "allowed" / "task.tex"
        write_tex(target, "synthetic")
        source = validated_source(root)
        target_key = os.path.normcase(os.path.abspath(os.fspath(target)))
        original_lstat = candidates.Path.lstat
        original_read = candidates.os.read
        real_metadata = original_lstat(target)
        overrides: dict[str, int] = {}
        read_calls = 0

        class StatView:
            def __init__(self, base: os.stat_result):
                self._base = base

            def __getattr__(self, name: str) -> object:
                if name in overrides:
                    return overrides[name]
                return getattr(self._base, name)

        def mocked_lstat(path: Path, *args: object, **kwargs: object) -> object:
            metadata = original_lstat(path, *args, **kwargs)
            path_key = os.path.normcase(os.path.abspath(os.fspath(path)))
            if path_key == target_key:
                return StatView(metadata)
            return metadata

        def tracked_read(descriptor: int, size: int) -> bytes:
            nonlocal read_calls
            read_calls += 1
            return original_read(descriptor, size)

        nonzero_device = max(1, int(real_metadata.st_dev))
        nonzero_inode = max(1, int(real_metadata.st_ino))
        unreliable_metadata = (
            (
                {"st_dev": 0, "st_ino": 0, "st_nlink": 1},
                "candidate_identity_unavailable",
            ),
            (
                {"st_dev": nonzero_device, "st_ino": 0, "st_nlink": 1},
                "candidate_identity_unavailable",
            ),
            (
                {"st_dev": 0, "st_ino": nonzero_inode, "st_nlink": 1},
                "candidate_identity_unavailable",
            ),
            (
                {
                    "st_dev": nonzero_device,
                    "st_ino": nonzero_inode,
                    "st_nlink": 0,
                },
                "candidate_hardlink_rejected",
            ),
        )
        candidates.Path.lstat = mocked_lstat
        candidates.os.read = tracked_read
        try:
            for identity, expected_code in unreliable_metadata:
                overrides.clear()
                overrides.update(identity)
                error = expect_discovery_fault(
                    expected_code,
                    lambda: candidates.enumerate_candidates(source),
                    secrets=(str(root), "task.tex"),
                )
                assert error.__cause__ is None
                assert error.__context__ is None
                assert read_calls == 0
        finally:
            candidates.os.read = original_read
            candidates.Path.lstat = original_lstat


def test_candidate_same_metadata_identity_exchange_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-exchange-root"
        target = root / "allowed" / "task.tex"
        write_tex(target, "synthetic")
        candidate = candidates.enumerate_candidates(
            validated_source(root)
        ).candidates[0]
        target_key = os.path.normcase(os.path.abspath(os.fspath(target)))
        original_lstat = candidates.Path.lstat
        original_open = candidates.os.open
        original_read = candidates.os.read
        open_calls = 0
        read_calls = 0

        class ExchangedStatView:
            def __init__(self, base: os.stat_result):
                self._base = base

            def __getattr__(self, name: str) -> object:
                replacements = {
                    "st_size": candidate.size_bytes,
                    "st_mtime_ns": candidate.modified_ns,
                    "st_dev": candidate.device,
                    "st_ino": candidate.inode + 1,
                    "st_nlink": candidate.link_count,
                }
                if name in replacements:
                    return replacements[name]
                return getattr(self._base, name)

        def exchanged_lstat(
            path: Path, *args: object, **kwargs: object
        ) -> object:
            metadata = original_lstat(path, *args, **kwargs)
            path_key = os.path.normcase(os.path.abspath(os.fspath(path)))
            if path_key == target_key:
                return ExchangedStatView(metadata)
            return metadata

        def tracked_open(*args: object, **kwargs: object) -> int:
            nonlocal open_calls
            open_calls += 1
            return original_open(*args, **kwargs)

        def tracked_read(descriptor: int, size: int) -> bytes:
            nonlocal read_calls
            read_calls += 1
            return original_read(descriptor, size)

        candidates.Path.lstat = exchanged_lstat
        candidates.os.open = tracked_open
        candidates.os.read = tracked_read
        try:
            error = expect_discovery_fault(
                "candidate_identity_changed",
                lambda: candidates.read_candidate_bytes(candidate, 1024),
                secrets=(str(root), "task.tex"),
            )
        finally:
            candidates.os.read = original_read
            candidates.os.open = original_open
            candidates.Path.lstat = original_lstat
        assert error.__cause__ is None
        assert error.__context__ is None
        assert open_calls == 0
        assert read_calls == 0


def test_candidate_depth_hardlink_and_links() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-root"
        write_tex(root / "deep" / "one" / "two" / "task.tex", "task")
        expect_discovery_fault(
            "traversal_depth_limit",
            lambda: candidates.enumerate_candidates(
                validated_source(root, include=("deep",)),
                candidates.DiscoveryLimits(max_depth=1),
            ),
            secrets=(str(root),),
        )

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-root"
        original = root / "allowed" / "original.tex"
        alias = root / "allowed" / "alias.tex"
        write_tex(original, "hardlink")
        try:
            os.link(original, alias)
        except (OSError, NotImplementedError):
            pass
        else:
            expect_discovery_fault(
                "candidate_hardlink_rejected",
                lambda: candidates.enumerate_candidates(
                    validated_source(root)
                ),
                secrets=(str(root), "original.tex", "alias.tex"),
            )

    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        root = base / "synthetic-root"
        outside = base / "synthetic-outside"
        write_tex(outside / "target.tex", "outside")
        (root / "allowed").mkdir(parents=True)
        link = root / "allowed" / "linked.tex"
        try:
            link.symlink_to(outside / "target.tex")
        except (OSError, NotImplementedError):
            pass
        else:
            expect_discovery_fault(
                "candidate_link_boundary",
                lambda: candidates.enumerate_candidates(
                    validated_source(root)
                ),
                secrets=(str(root), str(outside), "linked.tex"),
            )

    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        real_root = base / "real-root"
        write_tex(real_root / "allowed" / "task.tex", "task")
        linked_root = base / "linked-root"
        if create_directory_link(linked_root, real_root):
            source = replace(
                validated_source(real_root),
                root=linked_root.absolute(),
            )
            expect_discovery_fault(
                "source_root_link_boundary",
                lambda: candidates.enumerate_candidates(source),
                secrets=(str(linked_root), str(real_root)),
            )

    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        root = base / "synthetic-root"
        outside = base / "outside-directory"
        (root / "allowed").mkdir(parents=True)
        write_tex(outside / "hidden.tex", "outside")
        linked = root / "allowed" / "linked-directory"
        if create_directory_link(linked, outside):
            expect_discovery_fault(
                "candidate_link_boundary",
                lambda: candidates.enumerate_candidates(
                    validated_source(
                        root,
                        include=("allowed/**",),
                    )
                ),
                secrets=(str(root), str(outside), "linked-directory"),
            )


def test_candidate_unreadable_diagnostic_is_sanitized() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-private-root"
        write_tex(root / "allowed" / "task.tex", "task")
        original_scandir = candidates.os.scandir

        def denied(_path: object) -> object:
            raise PermissionError(str(root / "private-directory-name"))

        candidates.os.scandir = denied
        try:
            error = expect_discovery_fault(
                "directory_unreadable",
                lambda: candidates.enumerate_candidates(
                    validated_source(root)
                ),
                secrets=(str(root), "private-directory-name"),
            )
        finally:
            candidates.os.scandir = original_scandir
        assert error.__cause__ is None
        assert error.__context__ is None


def test_candidate_operational_boundaries_are_sanitized() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-operational-root"
        write_tex(root / "allowed" / "task.tex", "task")
        source = validated_source(root)

        original_scandir = candidates.os.scandir

        def broken_scandir(_path: object) -> object:
            raise RuntimeError(str(root / "scandir-sentinel"))

        candidates.os.scandir = broken_scandir
        try:
            discovery_error = expect_discovery_fault(
                "discovery_operational_error",
                lambda: candidates.enumerate_candidates(source),
                secrets=(str(root), "scandir-sentinel"),
            )
        finally:
            candidates.os.scandir = original_scandir
        assert discovery_error.__cause__ is None
        assert discovery_error.__context__ is None

        candidate = candidates.enumerate_candidates(source).candidates[0]
        original_read = candidates.os.read

        def broken_read(_descriptor: int, _size: int) -> bytes:
            raise OSError(str(root / "read-sentinel"))

        candidates.os.read = broken_read
        try:
            read_error = expect_discovery_fault(
                "candidate_read_operational_error",
                lambda: candidates.read_candidate_bytes(candidate, 1024),
                secrets=(str(root), "read-sentinel"),
            )
        finally:
            candidates.os.read = original_read
        assert read_error.__cause__ is None
        assert read_error.__context__ is None


def test_candidate_safe_locator_rejects_control_characters() -> None:
    assert candidates._safe_locator(
        ("allowed", "file.tex")
    ) == "allowed/file.tex"
    invalid_code_points = (
        *range(0x20),
        0x7F,
        0x85,
        0x2028,
        0x2029,
    )
    for code_point in invalid_code_points:
        unsafe_part = "synthetic" + chr(code_point) + "file.tex"
        expect_discovery_fault(
            "candidate_locator_invalid",
            lambda value=unsafe_part: candidates._safe_locator(
                ("allowed", value)
            ),
            secrets=(unsafe_part,),
        )


def test_candidate_case_collision_when_supported() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-root"
        first = root / "allowed" / "Case.tex"
        second = root / "allowed" / "case.tex"
        write_tex(first, "first")
        write_tex(second, "second")
        names = {path.name for path in (root / "allowed").iterdir()}
        if {"Case.tex", "case.tex"}.issubset(names):
            expect_discovery_fault(
                "path_case_collision",
                lambda: candidates.enumerate_candidates(
                    validated_source(root)
                ),
                secrets=(str(root), "Case.tex", "case.tex"),
            )


def test_static_parser_structure_privacy_and_references() -> None:
    raw_sentinel = "SYNTHETIC_RAW_CONTENT_SENTINEL"
    child_sentinel = "SYNTHETIC_CHILD_MUST_NOT_BE_OPENED"
    document = r"""
\section*
[synthetic-short]
{SYNTHETIC_RAW_CONTENT_SENTINEL}
% \begin{aufgabe}Berechne hidden.\end{aufgabe}
\newcommand{\fake}{\begin{aufgabe}\write18{hidden}\end{aufgabe}}
\verb|\begin{aufgabe}Berechne verbatim.\end{aufgabe}|
\begin{lstlisting}
\begin{aufgabe}Berechne listing.\end{aufgabe}
\end{lstlisting}
\begin{minted}{python}
print("SYNTHETIC_RAW_CONTENT_SENTINEL")
\end{minted}
\begin{aufgabe}
Berechne den {{synthetischen}} Wert.
\begin{enumerate}
\item Teil eins.
\item Teil zwei mit escaped \% Prozent.
\end{enumerate}
\end{aufgabe}
\begin{loesung}
SYNTHETIC_RAW_CONTENT_SENTINEL
\end{loesung}
\write18{synthetic-command}
\openout1=synthetic-output
\directlua{synthetic-code}
\catcode37=12
\includegraphics{synthetic-image}
\input{child}
\include{../outside}
\subfile{SYNTHETIC_ABSOLUTE_REFERENCE}
\input{\jobname}
\input|"synthetic-command"
"""
    document = document.replace(
        "SYNTHETIC_ABSOLUTE_REFERENCE",
        "".join(["C", ":", "/", "synthetic", "/", "private"]),
    )
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-root"
        main = root / "allowed" / "main.tex"
        child = root / "allowed" / "child.tex"
        write_tex(main, document)
        write_tex(child, child_sentinel)
        source = validated_source(root, include=("allowed/main.tex",))
        candidate = candidates.enumerate_candidates(source).candidates[0]
        before = {
            main: (main.read_bytes(), main.stat().st_mtime_ns),
            child: (child.read_bytes(), child.stat().st_mtime_ns),
        }
        opened: list[Path] = []
        original_open = candidates.os.open

        def guarded_open(path: object, flags: int, *args: object) -> int:
            opened.append(Path(path).resolve())
            return original_open(path, flags, *args)

        candidates.os.open = guarded_open
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                metadata = tex.parse_candidate(
                    candidate,
                    operator_taxonomy_path=TAXONOMY,
                )
        finally:
            candidates.os.open = original_open

        assert opened == [main.resolve()]
        assert stdout.getvalue() == ""
        assert stderr.getvalue() == ""
        after = {
            main: (main.read_bytes(), main.stat().st_mtime_ns),
            child: (child.read_bytes(), child.stat().st_mtime_ns),
        }
        assert after == before

        payload = metadata.as_dict()
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        assert raw_sentinel not in serialized
        assert child_sentinel not in serialized
        assert str(root) not in serialized
        assert "section*" not in serialized
        assert payload["structure"]["heading_count"] == 1
        assert payload["structure"]["task_count"] == 1
        assert payload["structure"]["solution_count"] == 1
        assert payload["structure"]["list_count"] == 1
        assert payload["structure"]["item_count"] == 2
        assert payload["structure"]["macro_definition_count"] == 1
        task = payload["tasks"][0]
        assert task["subtask_count"] == 2
        assert task["solution_presence"] == "present"
        assert any(
            item["operator_id"] == "berechnen"
            for item in task["operator_candidates"]
        )
        assert payload["reference_counts"] == {
            "literal_relative": 1,
            "absolute": 1,
            "traversal": 1,
            "dynamic": 1,
            "pipe": 1,
            "malformed": 0,
        }
        expected_risks = {
            "shell_escape",
            "file_io",
            "lua_execution",
            "dynamic_tex",
            "macro_definition",
            "external_program",
            "external_resource",
            "pipe_input",
            "absolute_reference",
            "reference_traversal",
            "dynamic_reference",
        }
        assert expected_risks.issubset(payload["risk_codes"]), (
            expected_risks - set(payload["risk_codes"]),
            payload["risk_codes"],
        )
        assert_metadata_matches_schema(payload)
        summary = json.dumps(metadata.safe_summary(), sort_keys=True)
        assert str(root) not in summary
        assert "main.tex" not in summary
        assert payload["local_provenance"]["integrity_sha256"] not in summary
        assert str(root) not in repr(metadata)
        assert "main.tex" not in repr(metadata)
        assert repr(metadata) == "LocalOrientationDocumentMetadata(<local-only>)"
        assert not hasattr(tex, "subprocess")


def parse_single_bytes(
    root: Path,
    name: str,
    data: bytes,
    *,
    limits: tex.ParserLimits | None = None,
) -> tex.LocalOrientationDocumentMetadata:
    path = root / "allowed" / name
    write_bytes(path, data)
    source = validated_source(root, include=(f"allowed/{name}",))
    candidate = candidates.enumerate_candidates(source).candidates[0]
    return tex.parse_candidate(
        candidate,
        limits=limits,
        operator_taxonomy_path=TAXONOMY,
    )


def test_parser_encodings_and_binary_rejection() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        bom = parse_single_bytes(
            base / "bom-root",
            "bom.tex",
            b"\xef\xbb\xbf" + "\\begin{aufgabe}Berechne.\\end{aufgabe}".encode(),
        ).as_dict()
        assert bom["technical"]["encoding"] == "utf-8-sig"

        cp_text = (
            "\\usepackage[ansinew]{inputenc}\n"
            "\\begin{aufgabe}Berechne 10 \u20ac.\\end{aufgabe}\n"
        )
        cp = parse_single_bytes(
            base / "cp-root",
            "cp.tex",
            cp_text.encode("cp1252"),
        ).as_dict()
        assert cp["technical"]["encoding"] == "windows-1252"
        assert "legacy_encoding" in cp["warning_codes"]

        latin_text = (
            "\\usepackage[latin1]{inputenc}\n"
            "\\begin{aufgabe}Berechne \u00e4.\\end{aufgabe}\n"
        )
        latin = parse_single_bytes(
            base / "latin-root",
            "latin.tex",
            latin_text.encode("iso-8859-1"),
        ).as_dict()
        assert latin["technical"]["encoding"] == "iso-8859-1"
        assert "legacy_encoding" in latin["warning_codes"]

        invalid_root = base / "invalid-root"
        invalid_path = invalid_root / "allowed" / "invalid.tex"
        invalid_sentinel = "SYNTHETIC_ENCODING_SENTINEL"
        write_bytes(invalid_path, invalid_sentinel.encode() + b"\xff")
        invalid_candidate = candidates.enumerate_candidates(
            validated_source(
                invalid_root,
                include=("allowed/invalid.tex",),
            )
        ).candidates[0]
        expect_tex_fault(
            "encoding_undetermined",
            lambda: tex.parse_candidate(
                invalid_candidate,
                operator_taxonomy_path=TAXONOMY,
            ),
            secrets=(str(invalid_root), "invalid.tex", invalid_sentinel),
        )

        binary_root = base / "binary-root"
        binary_path = binary_root / "allowed" / "binary.tex"
        write_bytes(binary_path, b"synthetic\x00binary")
        binary_candidate = candidates.enumerate_candidates(
            validated_source(
                binary_root,
                include=("allowed/binary.tex",),
            )
        ).candidates[0]
        expect_tex_fault(
            "binary_input_rejected",
            lambda: tex.parse_candidate(
                binary_candidate,
                operator_taxonomy_path=TAXONOMY,
            ),
            secrets=(str(binary_root), "binary.tex"),
        )


def test_parser_limits_malformed_and_unknown_operator() -> None:
    expect_tex_fault(
        "line_limit_exceeded",
        lambda: tex.parse_tex_text(
            "one\ntwo\nthree",
            limits=tex.ParserLimits(max_lines=2),
            operator_taxonomy_path=TAXONOMY,
        ),
    )
    expect_tex_fault(
        "command_limit_exceeded",
        lambda: tex.parse_tex_text(
            "\\section{a}\\section{b}",
            limits=tex.ParserLimits(max_commands=1),
            operator_taxonomy_path=TAXONOMY,
        ),
    )
    expect_tex_fault(
        "nesting_limit_exceeded",
        lambda: tex.parse_tex_text(
            "{{nested}}",
            limits=tex.ParserLimits(max_nesting=1),
            operator_taxonomy_path=TAXONOMY,
        ),
    )
    expect_tex_fault(
        "block_limit_exceeded",
        lambda: tex.parse_tex_text(
            (
                "\\begin{aufgabe}Berechne.\\end{aufgabe}"
                "\\begin{aufgabe}Bestimme.\\end{aufgabe}"
            ),
            limits=tex.ParserLimits(max_blocks=1),
            operator_taxonomy_path=TAXONOMY,
        ),
    )

    malformed = tex.parse_tex_text(
        "\\begin{aufgabe}Neutraler Text mit { offener Klammer.",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert malformed["structure"]["task_count"] == 1
    assert "unbalanced_braces" in malformed["warning_codes"]
    assert "unbalanced_environment" in malformed["warning_codes"]
    assert malformed["tasks"][0]["operator_candidates"] == []

    bounded = tex.parse_tex_text(
        "} ] \\end{aufgabe}",
        limits=tex.ParserLimits(max_warnings=1),
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert bounded["warning_codes"] == ["warning_limit_reached"]
    assert_metadata_matches_schema(bounded)


def test_parser_ambiguous_solution_and_bounded_risks() -> None:
    payload = tex.parse_tex_text(
        (
            "\\begin{aufgabe}Berechne."
            "\\begin{loesung}eins\\end{loesung}"
            "\\begin{answer}zwei\\end{answer}"
            "\\end{aufgabe}"
            "\\input{"
        ),
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert payload["tasks"][0]["solution_presence"] == "ambiguous"
    assert payload["tasks"][0]["solution_assignment"] == "ambiguous"
    assert "ambiguous_solution_assignment" in payload["warning_codes"]
    assert payload["reference_counts"]["malformed"] == 1
    assert "malformed_reference" in payload["risk_codes"]
    assert_metadata_matches_schema(payload)

    bounded = tex.parse_tex_text(
        "\\write18{x}\\directlua{x}\\includegraphics{x}",
        limits=tex.ParserLimits(max_risks=1),
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert bounded["risk_codes"] == ["risk_limit_reached"]
    assert_metadata_matches_schema(bounded)


def object_schema_nodes(value: object) -> Iterable[Mapping[str, object]]:
    if isinstance(value, Mapping):
        if value.get("type") == "object":
            yield value
        for item in value.values():
            yield from object_schema_nodes(item)
    elif isinstance(value, list):
        for item in value:
            yield from object_schema_nodes(item)


def test_metadata_schema_rejects_raw_fields() -> None:
    metadata = tex.parse_tex_text(
        "\\begin{aufgabe}Berechne.\\end{aufgabe}",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert_metadata_matches_schema(metadata)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert isinstance(schema, Mapping)
    for node in object_schema_nodes(schema):
        assert node.get("additionalProperties") is False

    forbidden = (
        "absolute_path",
        "filename",
        "title",
        "text",
        "task_text",
        "solution_text",
        "prompt",
        "snippet",
        "excerpt",
        "content",
        "raw_command",
    )
    for field in forbidden:
        invalid = copy.deepcopy(metadata)
        invalid[field] = "SYNTHETIC_FORBIDDEN_VALUE"
        try:
            assert_metadata_matches_schema(invalid)
        except AssertionError:
            pass
        else:
            raise AssertionError(f"schema accepted forbidden field {field}")

    nested = copy.deepcopy(metadata)
    nested["local_provenance"]["filename"] = "synthetic-private.tex"
    try:
        assert_metadata_matches_schema(nested)
    except AssertionError:
        pass
    else:
        raise AssertionError("schema accepted nested filename")

    task_text = copy.deepcopy(metadata)
    task_text["tasks"][0]["text"] = "SYNTHETIC_RAW_CONTENT"
    try:
        assert_metadata_matches_schema(task_text)
    except AssertionError:
        pass
    else:
        raise AssertionError("schema accepted task text")


def test_no_automatic_config_network_or_subprocess() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "synthetic-root"
        main = root / "allowed" / "main.tex"
        write_tex(
            main,
            "\\begin{aufgabe}Berechne.\\end{aufgabe}",
        )
        candidate = candidates.enumerate_candidates(
            validated_source(root, include=("allowed/main.tex",))
        ).candidates[0]
        before = (main.read_bytes(), main.stat().st_mtime_ns)
        original_discover = config.discover_config
        original_run = subprocess.run
        original_connect = socket.create_connection

        def forbidden(*_args: object, **_kwargs: object) -> object:
            raise AssertionError("forbidden_external_operation")

        config.discover_config = forbidden
        subprocess.run = forbidden
        socket.create_connection = forbidden
        try:
            payload = tex.parse_candidate(
                candidate,
                operator_taxonomy_path=TAXONOMY,
            ).as_dict()
        finally:
            config.discover_config = original_discover
            subprocess.run = original_run
            socket.create_connection = original_connect
        assert payload["structure"]["task_count"] == 1
        assert (main.read_bytes(), main.stat().st_mtime_ns) == before


def test_no_repository_tex_fixture() -> None:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "ls-files",
            "-z",
            "--",
            "*.tex",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == b""


def test_backslash_bomb_finishes_within_bound() -> None:
    command = (
        "import sys; "
        "sys.path.insert(0, 'scripts'); "
        "import local_orientation_tex as tex; "
        "failure = None; "
        "\ntry:\n tex.parse_tex_text(chr(92) * 100000)"
        "\nexcept tex.TexParseFault as error:\n failure = error.code"
        "\nassert failure in (None, 'command_limit_exceeded')"
    )
    started = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-c", command],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=12,
        check=False,
    )
    elapsed = time.monotonic() - started
    assert result.returncode == 0, (result.returncode, result.stderr[:200])
    assert elapsed < 12


def test_commented_and_macro_verbatim_tokens_do_not_mask_real_content() -> None:
    payload = tex.parse_tex_text(
        r"""
% \begin{verbatim}
\newcommand{\poison}{\begin{verbatim}}
\write18{synthetic-command}
\begin{aufgabe}
Berechne den synthetischen Wert.
\end{aufgabe}
""",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert payload["structure"]["task_count"] == 1
    assert payload["structure"]["macro_definition_count"] == 1
    assert "shell_escape" in payload["risk_codes"]
    assert "macro_definition" in payload["risk_codes"]
    assert "unclosed_verbatim" not in payload["warning_codes"]
    operators = payload["tasks"][0]["operator_candidates"]
    assert [item["operator_id"] for item in operators] == ["berechnen"]
    assert_metadata_matches_schema(payload)


def test_commented_macro_definition_does_not_mask_real_content() -> None:
    payload = tex.parse_tex_text(
        r"""
\newcommand% synthetic comment
{\poison}{\begin{verbatim}}
\write18{synthetic-command}
\begin{aufgabe}
Berechne den synthetischen Wert.
\end{aufgabe}
""",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert payload["structure"]["task_count"] == 1
    assert payload["structure"]["macro_definition_count"] == 1
    assert "shell_escape" in payload["risk_codes"]
    assert "macro_definition" in payload["risk_codes"]
    assert "unclosed_verbatim" not in payload["warning_codes"]
    operators = payload["tasks"][0]["operator_candidates"]
    assert [item["operator_id"] for item in operators] == ["berechnen"]
    assert_metadata_matches_schema(payload)


def test_commented_def_decoy_does_not_mask_real_content() -> None:
    payload = tex.parse_tex_text(
        r"""
\def\poison% {decoy}
{\begin{verbatim}}
\write18{synthetic-command}
\begin{aufgabe}
Berechne den synthetischen Wert.
\end{aufgabe}
""",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert payload["structure"]["task_count"] == 1
    assert payload["structure"]["macro_definition_count"] == 1
    assert "shell_escape" in payload["risk_codes"]
    assert "macro_definition" in payload["risk_codes"]
    assert "unclosed_verbatim" not in payload["warning_codes"]
    operators = payload["tasks"][0]["operator_candidates"]
    assert [item["operator_id"] for item in operators] == ["berechnen"]
    assert_metadata_matches_schema(payload)


def test_commented_verbatim_begin_masks_only_its_real_block() -> None:
    payload = tex.parse_tex_text(
        r"""
\begin% synthetic comment
{verbatim}
\begin{aufgabe}
Berechne einen nur vorgetaeuschten Wert.
\end{aufgabe}
\end{verbatim}
\begin{aufgabe}
Nenne einen synthetischen Wert.
\end{aufgabe}
""",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert payload["structure"]["task_count"] == 1
    assert payload["structure"]["verbatim_block_count"] == 1
    operators = payload["tasks"][0]["operator_candidates"]
    assert [item["operator_id"] for item in operators] == ["nennen"]
    assert_metadata_matches_schema(payload)


def test_commented_verbatim_name_masks_only_its_real_block() -> None:
    payload = tex.parse_tex_text(
        r"""
\begin{verb% synthetic comment
atim}
\begin{aufgabe}
Berechne einen nur vorgetaeuschten Wert.
\end{aufgabe}
\end{verbatim}
\begin{aufgabe}
Nenne einen synthetischen Wert.
\end{aufgabe}
""",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert payload["structure"]["task_count"] == 1
    assert payload["structure"]["verbatim_block_count"] == 1
    operators = payload["tasks"][0]["operator_candidates"]
    assert [item["operator_id"] for item in operators] == ["nennen"]
    assert_metadata_matches_schema(payload)


def test_commented_verbatim_end_reveals_following_content() -> None:
    payload = tex.parse_tex_text(
        r"""
\begin{verbatim}
\begin{aufgabe}
Berechne einen nur vorgetaeuschten Wert.
\end{aufgabe}
\end{verb% synthetic comment
atim}
\begin{aufgabe}
Nenne einen synthetischen Wert.
\end{aufgabe}
""",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert payload["structure"]["task_count"] == 1
    assert payload["structure"]["verbatim_block_count"] == 1
    operators = payload["tasks"][0]["operator_candidates"]
    assert [item["operator_id"] for item in operators] == ["nennen"]
    assert_metadata_matches_schema(payload)


def test_heading_list_and_parser_limit_boundaries() -> None:
    excessive_limits = (
        {"max_bytes": 4 * 1024 * 1024 + 1},
        {"max_lines": 100001},
        {"max_commands": 25001},
        {"max_nesting": 129},
        {"max_blocks": 5001},
        {"max_warnings": 257},
        {"max_risks": 129},
    )
    for values in excessive_limits:
        try:
            tex.ParserLimits(**values)
        except ValueError as error:
            assert str(error) == "parser_limits_invalid"
        else:
            raise AssertionError(f"ParserLimits accepted {values}")

    heading_bomb = "\\section{x}" * 3
    expect_tex_fault(
        "heading_limit_exceeded",
        lambda: tex.parse_tex_text(
            heading_bomb,
            limits=tex.ParserLimits(max_blocks=2),
            operator_taxonomy_path=TAXONOMY,
        ),
    )
    list_bomb = "\\begin{enumerate}\\end{enumerate}" * 3
    expect_tex_fault(
        "block_limit_exceeded",
        lambda: tex.parse_tex_text(
            list_bomb,
            limits=tex.ParserLimits(max_blocks=2),
            operator_taxonomy_path=TAXONOMY,
        ),
    )
    valid = tex.parse_tex_text(
        (
            "\\section{x}"
            "\\begin{enumerate}\\item one\\end{enumerate}"
        ),
        limits=tex.ParserLimits(max_blocks=2),
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert valid["structure"]["heading_count"] == 1
    assert valid["structure"]["list_count"] == 1
    assert_metadata_matches_schema(valid)


def test_relative_locator_rejects_local_path_forms() -> None:
    drive = "".join(["C", ":", "/", "synthetic", "/", "file.tex"])
    unc = "".join([
        chr(92), chr(92), "synthetic-server", chr(92), "share",
        chr(92), "file.tex",
    ])
    file_uri = "".join(["file", ":", "/", "/", "/", "synthetic", "/file.tex"])
    ads = "".join(["allowed/name", ":", "stream.tex"])
    backslash = "".join(["allowed", chr(92), "file.tex"])
    traversal = "allowed/../file.tex"
    final_lf = "allowed/file.tex" + chr(0x0A)
    final_next_line = "allowed/file.tex" + chr(0x85)
    final_line_separator = "allowed/file.tex" + chr(0x2028)
    final_paragraph_separator = "allowed/file.tex" + chr(0x2029)
    invalid_locators = (
        drive,
        unc,
        file_uri,
        ads,
        backslash,
        traversal,
        final_lf,
        final_next_line,
        final_line_separator,
        final_paragraph_separator,
    )

    valid_payload = tex.parse_tex_text(
        "neutral synthetic text",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    for locator in invalid_locators:
        expect_tex_fault(
            "metadata_envelope_invalid",
            lambda value=locator: tex.parse_tex_text(
                "neutral synthetic text",
                relative_locator=value,
                operator_taxonomy_path=TAXONOMY,
            ),
            secrets=(locator,),
        )
        invalid_payload = copy.deepcopy(valid_payload)
        invalid_payload["local_provenance"]["relative_locator"] = locator
        try:
            assert_metadata_matches_schema(invalid_payload)
        except AssertionError:
            pass
        else:
            raise AssertionError("schema accepted unsafe relative locator")


def test_nested_solution_content_is_excluded_from_task_features() -> None:
    payload = tex.parse_tex_text(
        r"""
\begin{aufgabe}
Nenne einen synthetischen Wert.
\begin{enumerate}
\item Sichtbare Teilaufgabe.
\end{enumerate}
\begin{loesung}
Berechne einen nur in der Lösung vorkommenden Wert.
\begin{enumerate}
\item Lösungsschritt eins.
\item Lösungsschritt zwei.
\end{enumerate}
\end{loesung}
\end{aufgabe}
""",
        operator_taxonomy_path=TAXONOMY,
    ).as_dict()
    assert payload["structure"]["task_count"] == 1
    assert payload["structure"]["solution_count"] == 1
    assert payload["structure"]["item_count"] == 3
    task = payload["tasks"][0]
    assert task["subtask_count"] == 1
    assert task["solution_presence"] == "present"
    assert [
        item["operator_id"] for item in task["operator_candidates"]
    ] == ["nennen"]
    assert_metadata_matches_schema(payload)


def main() -> int:
    test_candidate_selection_and_privacy()
    test_candidate_rules_limits_and_mutation()
    test_candidate_unreliable_identity_is_rejected_without_read()
    test_candidate_same_metadata_identity_exchange_is_rejected()
    test_candidate_depth_hardlink_and_links()
    test_candidate_unreadable_diagnostic_is_sanitized()
    test_candidate_operational_boundaries_are_sanitized()
    test_candidate_safe_locator_rejects_control_characters()
    test_candidate_case_collision_when_supported()
    test_static_parser_structure_privacy_and_references()
    test_parser_encodings_and_binary_rejection()
    test_parser_limits_malformed_and_unknown_operator()
    test_parser_ambiguous_solution_and_bounded_risks()
    test_metadata_schema_rejects_raw_fields()
    test_no_automatic_config_network_or_subprocess()
    test_no_repository_tex_fixture()
    test_backslash_bomb_finishes_within_bound()
    test_commented_and_macro_verbatim_tokens_do_not_mask_real_content()
    test_commented_macro_definition_does_not_mask_real_content()
    test_commented_def_decoy_does_not_mask_real_content()
    test_commented_verbatim_begin_masks_only_its_real_block()
    test_commented_verbatim_name_masks_only_its_real_block()
    test_commented_verbatim_end_reveals_following_content()
    test_heading_list_and_parser_limit_boundaries()
    test_relative_locator_rejects_local_path_forms()
    test_nested_solution_content_is_excluded_from_task_features()
    print("Local orientation TeX tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
