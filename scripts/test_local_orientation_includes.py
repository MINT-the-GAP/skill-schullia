#!/usr/bin/env python3
"""Dependency-free include-graph regressions using temporary synthetic data."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
import hashlib
import io
import os
from pathlib import Path
import socket
import subprocess
import tempfile
from unittest.mock import patch

import local_orientation_candidates as selector
import local_orientation_includes as includes
import local_orientation_tex as tex
from test_local_orientation_tex import (
    assert_metadata_matches_schema, create_directory_link,
    exception_surface, validated_source, write_tex,
)


TASK = r"\begin{aufgabe}Nenne eine Zahl.\end{aufgabe}"
SECRET = "synthetic-private-source-sentinel"


def fault(codes, action):
    if isinstance(codes, str):
        codes = {codes}
    try:
        action()
    except includes.IncludeFault as error:
        assert error.code in codes, (error.code, codes)
        assert SECRET not in exception_surface(error)
        assert error.__cause__ is None
        assert error.__context__ is None
        return
    raise AssertionError("expected sanitized include fault")


def fixture(root: Path):
    source = root / SECRET
    source.mkdir()
    return source, validated_source(source, exclude=("allowed/excluded",))


def by_locator(graph):
    return {document["local_provenance"]["relative_locator"]: document
            for document in graph.documents}


def test_literal_edges_dedup_and_document_boundaries():
    with tempfile.TemporaryDirectory() as directory:
        source, capability = fixture(Path(directory))
        write_tex(source / "allowed/main.tex", TASK + "\n"
                  + r"\input{child}\include{child.tex}\subfile{sub/leaf}")
        write_tex(source / "allowed/child.tex", TASK)
        write_tex(source / "allowed/sub/leaf.tex", r"\begin{loesung}7\end{loesung}")
        graph = includes.analyze_sources((capability,))
        assert len(graph.documents) == 3
        assert len(graph.edges) == 2
        assert not graph.warning_codes
        docs = by_locator(graph)
        assert docs["allowed/main.tex"]["structure"]["task_count"] == 1
        assert docs["allowed/main.tex"]["tasks"][0]["solution_presence"] == "absent"
        assert docs["allowed/sub/leaf.tex"]["solutions"][0]["assignment_status"] == "unassigned"
        for document in graph.documents:
            assert_metadata_matches_schema(document)
        assert SECRET not in repr(graph)
        assert "main.tex" not in repr(graph)
        assert repr(graph) == "IncludeGraph(<local-only>)"


def test_excludes_and_unsupported_references_never_open_targets():
    with tempfile.TemporaryDirectory() as directory:
        source, capability = fixture(Path(directory))
        write_tex(source / "allowed/main.tex", TASK + "\n" + "\n".join([
            r"\input{excluded/secret}", r"\input{missing}",
            r"\input{../outside}", r"\input{/absolute}",
            r"\input{" + "C" + ":/private}", r"\input{file:///private}",
            r"\input{" + chr(92) * 2 + "server/share}", r"\input{private:stream}",
            r"\input{|secret}", r"\input{\dynamic}",
            r"\input{artifact.sty}", r"\input{bad#1}",
            r"\input{bad$1}", r"\input{bad name}", r"\input unbraced",
            r"\includegraphics{excluded/secret}",
        ]))
        write_tex(source / "allowed/excluded/secret.tex", SECRET)
        write_tex(source / "outside.tex", SECRET)
        seen = []
        original = selector.read_candidate_bytes
        def read(candidate, maximum):
            seen.append(candidate.relative_locator)
            return original(candidate, maximum)
        with patch.object(selector, "read_candidate_bytes", side_effect=read):
            graph = includes.analyze_sources((capability,))
        assert seen == ["allowed/main.tex"]
        assert not graph.edges
        assert set(graph.warning_codes) == {
            "include_reference_unsupported", "include_target_not_allowlisted"
        }


def test_canonical_lexer_masks_decoys_and_normalizes_comments():
    with tempfile.TemporaryDirectory() as directory:
        source, capability = fixture(Path(directory))
        text = r"""% \input{decoy}
\newcommand% comment
{\poison}{\input{decoy}\begin{verbatim}}
\def\poison% {decoy}
{\input{decoy}\begin{verbatim}}
\verb|\input{decoy}|
\begin{verb% comment
atim}
\input{decoy}
% \end{verbatim}
\input{decoy}
\end{verb% comment
atim}
\begin{lstlisting}
\input{decoy}
\end{lstlisting}
\begin{minted}{tex}
\input{decoy}
\end{minted}
\\input{decoy}
\input@private{decoy}
\input% comment
{ch% comment
ild}
"""
        write_tex(source / "allowed/main.tex", text + TASK)
        write_tex(source / "allowed/child.tex", TASK)
        write_tex(source / "allowed/decoy.tex", TASK)
        graph = includes.analyze_sources((capability,))
        docs = by_locator(graph)
        assert len(graph.edges) == 1
        assert graph.edges[0][2] == docs["allowed/child.tex"]["document_id"]
        assert docs["allowed/main.tex"]["structure"]["task_count"] == 1


def test_same_source_only_and_duplicate_identity_rejected():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source1, capability1 = fixture(root)
        source2 = root / "second-source"
        source2.mkdir()
        capability2 = replace(validated_source(source2), source_id="second-source")
        write_tex(source1 / "allowed/main.tex", r"\input{child}")
        write_tex(source2 / "allowed/child.tex", TASK)
        graph = includes.analyze_sources((capability1, capability2))
        assert not graph.edges
        assert graph.warning_codes == ("include_target_not_allowlisted",)
        fault("include_sources_duplicate", lambda: includes.analyze_sources(
            (capability1, capability1)))
        # Overlapping source capabilities cannot count the same identity twice.
        fault("include_identity_duplicate", lambda: includes.analyze_sources(
            (capability1, replace(capability1, source_id="same-files"))))


def test_cycles_duplicates_and_depth_limits():
    with tempfile.TemporaryDirectory() as directory:
        source, capability = fixture(Path(directory))
        write_tex(source / "allowed/a.tex", r"\input{a}\input{b}\input{b}")
        write_tex(source / "allowed/b.tex", r"\input{a}")
        graph = includes.analyze_sources((capability,))
        assert len(graph.documents) == 2 and len(graph.edges) == 3
        assert graph.warning_codes == ("include_cycle",)
        write_tex(source / "allowed/a.tex", r"\input{b}")
        write_tex(source / "allowed/b.tex", r"\input{c}")
        write_tex(source / "allowed/c.tex", TASK)
        fault("include_depth_limit", lambda: includes.analyze_sources(
            (capability,), limits=includes.IncludeLimits(max_depth=1)))


def test_hard_resource_budgets_and_deadline():
    for kwargs in ({"max_nodes": 513}, {"max_sources": 33}, {"max_depth": 33},
                   {"max_edges": 2049}, {"max_total_bytes": 32*1024*1024+1},
                   {"max_seconds": 31}, {"max_seconds": float("nan")},
                   {"max_nodes": True}):
        try:
            includes.IncludeLimits(**kwargs)
        except ValueError as error:
            assert str(error) == "include_limits_invalid"
        else:
            raise AssertionError("unbounded include limit accepted")
    with tempfile.TemporaryDirectory() as directory:
        source, capability = fixture(Path(directory))
        write_tex(source / "allowed/a.tex", r"\input{b}\input{b}")
        write_tex(source / "allowed/b.tex", TASK)
        fault({"candidate_limit", "include_node_limit"},
              lambda: includes.analyze_sources((capability,),
                  limits=includes.IncludeLimits(max_nodes=1)))
        fault("include_edge_limit", lambda: includes.analyze_sources(
            (capability,), limits=includes.IncludeLimits(max_edges=1)))
        fault({"candidate_size_limit", "total_size_limit", "include_total_bytes_limit"},
              lambda: includes.analyze_sources((capability,),
                  limits=includes.IncludeLimits(max_total_bytes=8)))
        with patch.object(includes.time, "monotonic", side_effect=[0.0, 31.0]):
            fault("include_time_limit", lambda: includes.analyze_sources((capability,)))


def test_candidate_mutation_and_operational_errors_are_sanitized():
    with tempfile.TemporaryDirectory() as directory:
        source, capability = fixture(Path(directory))
        target = source / "allowed/a.tex"
        write_tex(target, TASK)
        original = selector.read_candidate_bytes
        def mutate(candidate, maximum):
            value = original(candidate, maximum)
            write_tex(target, TASK + " changed")
            return value
        with patch.object(selector, "read_candidate_bytes", side_effect=mutate):
            fault("include_candidate_changed", lambda: includes.analyze_sources((capability,)))
        with patch.object(selector, "read_candidate_bytes",
                          side_effect=OSError(str(target) + SECRET)):
            fault("include_operational_error", lambda: includes.analyze_sources((capability,)))
        with patch.object(includes, "_verify_unchanged",
                          side_effect=PermissionError(str(target) + SECRET)):
            fault("include_operational_error", lambda: includes.analyze_sources((capability,)))


def test_link_boundaries_and_no_writes_network_subprocess():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source, capability = fixture(root)
        target = source / "allowed/a.tex"
        write_tex(target, TASK)
        before = hashlib.sha256(target.read_bytes()).hexdigest()
        original_open = os.open
        def readonly_open(path, flags, *args, **kwargs):
            assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
            return original_open(path, flags, *args, **kwargs)
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(os, "open", side_effect=readonly_open), \
             patch.object(socket, "create_connection", side_effect=AssertionError("network")), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("subprocess")), \
             redirect_stdout(stdout), redirect_stderr(stderr):
            graph = includes.analyze_sources((capability,))
        assert len(graph.documents) == 1
        assert stdout.getvalue() == stderr.getvalue() == ""
        assert hashlib.sha256(target.read_bytes()).hexdigest() == before
        outside = root / "outside"
        outside.mkdir()
        write_tex(outside / "private.tex", SECRET)
        if create_directory_link(source / "allowed/link", outside):
            fault("candidate_link_boundary", lambda: includes.analyze_sources((capability,)))
        else:
            print("SKIP include directory link: platform denied synthetic link creation")


def main():
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print("Local orientation include tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
