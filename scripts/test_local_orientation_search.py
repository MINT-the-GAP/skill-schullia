#!/usr/bin/env python3
"""Dependency-free, temporary synthetic tests for local search and federation."""
from __future__ import annotations

import contextlib
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
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import local_orientation_config as config
import local_orientation_index as index
import local_orientation_tex as tex
import search_local_orientation as local
import search_with_local_orientation as federation


SENTINEL = "SYNTHETIC_PRIVATE_SENTINEL"


def metadata(locator="allowed/one.tex", *, subject=("mathematics",), grades=(7,),
             operator="Berechne", solved=True, modified=1):
    body = (r"\begin{aufgabe}" + operator + " den Wert. " + SENTINEL +
            (r"\begin{loesung}Eine synthetische Loesung.\end{loesung}" if solved else "") +
            r"\end{aufgabe}")
    source = config.ValidatedSource(
        "synthetic-source", Path(tempfile.gettempdir()) / "synthetic-not-opened",
        ("allowed",), (), (".tex",), subject, grades, ("synthetic-group",),
        ("worksheet",), "exclude")
    result = tex.parse_tex_text(body, source_id=source.source_id,
                                relative_locator=locator, source=source,
                                modified_ns=modified).as_dict()
    return result


def fake_snapshot(documents, edges=()):
    return SimpleNamespace(documents=tuple(documents), edges=tuple(edges), index_ready=True)


def make_repository(base):
    repo, source = base / "repo", base / "source"
    repo.mkdir()
    source.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (repo / ".gitignore").write_text(".schullia-local/\n", encoding="utf-8")
    (source / "allowed").mkdir()
    (source / "allowed" / "one.tex").write_text(
        r"\begin{aufgabe}Berechne den Wert. " + SENTINEL +
        r"\begin{loesung}Nur synthetisch.\end{loesung}\end{aufgabe}", encoding="utf-8")
    value = {
        "schema_version": 1, "enabled": True, "usage_context": "orientation-only",
        "state_directory": ".schullia-local/state",
        "sources": [{
            "id": "synthetic-source", "root": str(source), "include": ["allowed"],
            "exclude": [], "allowed_extensions": [".tex"], "subjects": ["mathematics"],
            "grades": [7], "learner_groups": ["synthetic-group"],
            "document_types": ["worksheet"], "archive_policy": "exclude",
            "risk_policy": {key: False for key in config.RISK_KEYS},
        }],
    }
    config_path = base / "synthetic-config.json"
    config_path.write_text(json.dumps(value), encoding="utf-8")
    return repo, source, config_path, value


def make_public_corpus(base):
    corpus = base / "public-corpus"
    corpus.mkdir()
    connection = sqlite3.connect(corpus / "index.sqlite")
    connection.executescript("""
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
        INSERT INTO meta VALUES('fts_available','0');
        CREATE TABLE search_items(item_id TEXT,item_type TEXT,source_id TEXT,
                                  path TEXT,title TEXT,body TEXT,metadata TEXT);
        CREATE TABLE documents(document_id TEXT,source_id TEXT,path TEXT,title TEXT,
          document_kind TEXT,usage_context TEXT,revision_sha TEXT,content_state TEXT,
          local_relpath TEXT,raw_url TEXT,web_url TEXT,header_json TEXT,
          headings_json TEXT,parse_warnings_json TEXT);
        CREATE TABLE sources(source_id TEXT,collection TEXT,state TEXT,owner TEXT,
                             repo TEXT,configured_ref TEXT);
    """)
    connection.execute("INSERT INTO sources VALUES(?,?,?,?,?,?)",
                       ("public-source", "public", "current", "example", "courses", "main"))
    connection.execute("INSERT INTO documents VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
        "public-document", "public-source", "one.md", "Public synthetic course",
        "course", "task-content", "a" * 40, "current", "sources/one.md",
        "https://example.invalid/raw/one.md", "https://example.invalid/one.md",
        "{}", "[]", "[]"))
    connection.execute("INSERT INTO search_items VALUES(?,?,?,?,?,?,?)", (
        "public-document", "document", "public-source", "one.md",
        "Public synthetic course", "A public synthetic example", "{}"))
    connection.commit()
    connection.close()
    return corpus


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


def tree_signature(root):
    return {path.relative_to(root).as_posix(): (
        path.stat().st_size, path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest())
        for path in root.rglob("*") if path.is_file()}


class LocalSearchTests(unittest.TestCase):
    def search(self, documents, filters=None, edges=(), **kwargs):
        with patch.object(index, "load_valid_index",
                          return_value=fake_snapshot(documents, edges)):
            return local.search_local_orientation(Path(tempfile.gettempdir()),
                                                  filters=filters, environ={}, **kwargs)

    def test_operator_filter_ids_match_canonical_metadata_schema(self):
        schema_path = Path(__file__).resolve().parents[1] / "references" / "local-orientation-metadata.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(local.OPERATORS, frozenset(schema["$defs"]["operator_id"]["enum"]))

    def test_real_synthetic_build_search_and_revocation(self):
        with tempfile.TemporaryDirectory(prefix="schullia-search-") as temporary:
            base = Path(temporary)
            repo, source, config_path, value = make_repository(base)
            original_source = tree_signature(source)
            index.build_local_index(repo, explicit_config=config_path, environ={})
            original_repo = tree_signature(repo)
            with patch.object(socket, "create_connection", side_effect=AssertionError("network forbidden")), \
                 patch.object(index, "build_local_index", side_effect=AssertionError("implicit build")):
                result = local.search_local_orientation(
                    repo, explicit_config=config_path, environ={},
                    filters={"subject": "mathematics", "grade": 7, "operator": "berechnen"})
            self.assertTrue(result.local_search_performed, result.reason_code)
            self.assertEqual(len(result.hits), 1)
            self.assertFalse(result.local_orientation_used)
            self.assertEqual(tree_signature(repo), original_repo)
            self.assertEqual(tree_signature(source), original_source)
            output = json.dumps(result.as_dict()) + repr(result) + repr(result.hits)
            for secret in (str(source), "one.tex", "synthetic-group", SENTINEL,
                           result.hits[0].metadata["document_id"]):
                self.assertNotIn(secret, output)
            with self.assertRaises(TypeError):
                json.dumps(result)
            with self.assertRaises(TypeError):
                json.dumps(result.hits[0])
            value["enabled"] = False
            config_path.write_text(json.dumps(value), encoding="utf-8")
            result = local.search_local_orientation(repo, explicit_config=config_path, environ={})
            self.assertFalse(result.local_search_performed)
            self.assertFalse(result.index_ready)
            self.assertEqual(result.availability_state, config.STATE_NOT_CONFIGURED)

    def test_exact_classification_before_recency_and_stable_order(self):
        exact = metadata("allowed/exact.tex", modified=1)
        broad = metadata("allowed/broad.tex", subject=("mathematics", "physics"), grades=(7, 8), modified=999999)
        filters = {"subject": "mathematics", "grade": 7, "operator": "berechnen"}
        result = self.search([broad, exact], filters)
        reversed_result = self.search([exact, broad], filters)
        self.assertEqual(result.hits[0].metadata["document_id"], exact["document_id"])
        self.assertEqual([hit.rank for hit in result.hits], [hit.rank for hit in reversed_result.hits])
        self.assertIn("technical_mtime_only", result.hits[0].ranking_basis)

    def test_solution_then_risks_then_feature_confidence_before_recency(self):
        solved = metadata("allowed/solved.tex", solved=True, modified=1)
        unsolved = metadata("allowed/unsolved.tex", solved=False, modified=9999)
        risky = metadata("allowed/risky.tex", solved=True, modified=999999)
        for item in solved["features"]["task_families"]:
            item["confidence"] = "medium"
        for document in (unsolved, risky):
            for item in document["features"]["task_families"]:
                item["confidence"] = "high"
        risky["risk_codes"] = ["shell_escape"]
        risky["suitability"] = "review_required"
        risky["technical"]["parse_status"] = "parsed_with_warnings"
        risky["features"]["status"] = "review_required"
        result = self.search(
            [risky, unsolved, solved],
            {"operator": "berechnen", "task_family": "calculation"},
        )
        self.assertEqual([hit.metadata["document_id"] for hit in result.hits],
                         [solved["document_id"], risky["document_id"],
                          unsolved["document_id"]])

    def test_filters_and_no_cross_task_operator_solution_match(self):
        doc = metadata(solved=False)
        second_document = metadata(operator="Nenne", solved=True)
        second = second_document["tasks"][0]
        second["task_id"] = "task-000002"
        second["ordinal"] = 2
        second_solution = second_document["solutions"][0]
        second_solution["task_id"] = "task-000002"
        doc["tasks"].append(second)
        doc["solutions"].append(second_solution)
        doc["structure"]["task_count"] = 2
        doc["structure"]["solution_count"] = 1
        self.assertEqual(len(self.search([doc], {
            "operator": "berechnen", "solution_presence": "present"}).hits), 0)
        for filters in ({"subject": "physics"}, {"grade": 8}, {"learner_group": "other"},
                        {"document_type": "other"}, {"min_tasks": 3}, {"max_tasks": 1},
                        {"has_warnings": True}, {"modified_after_ns": 2}):
            result = self.search([doc], filters)
            self.assertTrue(result.local_search_performed, filters)
            self.assertEqual(result.hits, (), filters)
        result = self.search([doc], {"learner_group": "synthetic-group", "min_tasks": 2})
        self.assertEqual(len(result.hits), 1)

    def test_unsupported_invalid_unknown_and_sql_injection(self):
        with patch.object(index, "load_valid_index", side_effect=AssertionError("must not load")):
            for key in ("query", "topic", "archive_status"):
                result = local.search_local_orientation(filters={key: SENTINEL}, environ={})
                self.assertEqual(result.reason_code, "search_filter_unsupported")
                self.assertNotIn(SENTINEL, json.dumps(result.as_dict()))
            self.assertEqual(local.search_local_orientation(
                filters={SENTINEL: "value"}).reason_code, "search_filter_unknown")
            for filters in ({"grade": True}, {"operator": "' OR 1=1 --"},
                            {"subject": []}, {"min_tasks": 4, "max_tasks": 2}):
                self.assertEqual(local.search_local_orientation(
                    filters=filters).reason_code, "search_filter_invalid")
        result = self.search([metadata()], {"learner_group": "' OR 1=1 --"})
        self.assertTrue(result.local_search_performed)
        self.assertEqual(result.hits, ())

    def test_closed_feature_filter_and_include_family(self):
        document = metadata()
        feature = document["features"]["task_families"][0]["id"]
        result = self.search([document], {"task_family": feature})
        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result.hits[0].family_key,
                         (document["source_id"], document["document_id"]))
        self.assertIn("feature_filter_match", result.hits[0].ranking_basis)
        rejected = local.search_local_orientation(
            filters={"task_family": SENTINEL}, environ={})
        self.assertEqual(rejected.reason_code, "search_filter_invalid")
        self.assertNotIn(SENTINEL, json.dumps(rejected.as_dict()))

    def test_include_components_are_internal_family_keys(self):
        documents = [metadata(f"allowed/family-{number}.tex")
                     for number in range(1, 4)]
        for number, document in enumerate(documents, 1):
            document["document_id"] = f"doc-{number:032x}"
        source = documents[0]["source_id"]
        edge = (source, documents[0]["document_id"], documents[1]["document_id"])
        result = self.search(documents, edges=(edge,))
        self.assertEqual(result.hits[0].family_key, result.hits[1].family_key)
        self.assertNotEqual(result.hits[0].family_key, result.hits[2].family_key)
        self.assertNotIn(str(result.hits[0].family_key), repr(result.hits[0]))

    def test_limits_and_exception_projection(self):
        docs = [metadata("allowed/" + str(number) + ".tex") for number in range(20)]
        self.assertEqual(len(self.search(docs).hits), 8)
        self.assertEqual(len(self.search(docs, limit=16).hits), 16)
        self.assertEqual(self.search(docs, limit=17).reason_code, "search_result_limit_invalid")
        self.assertEqual(self.search(docs, limits=local.SearchLimits(max_documents=2)).reason_code,
                         "search_scan_limit")
        self.assertEqual(self.search(docs, limits=local.SearchLimits(max_tasks=2)).reason_code,
                         "search_scan_limit")
        with self.assertRaises(local.SearchFault):
            local.SearchLimits(max_output_chars=10)
        with patch.object(index, "load_valid_index", side_effect=OSError(SENTINEL)):
            result = local.search_local_orientation(environ={})
        self.assertEqual(result.reason_code, "search_operational_error")
        self.assertNotIn(SENTINEL, json.dumps(result.as_dict()))
        with patch.object(index, "load_valid_index",
                          side_effect=index.IndexFault("index_missing", config.STATE_UNREACHABLE)):
            result = local.search_local_orientation(environ={})
        self.assertEqual(result.reason_code, "index_missing")
        self.assertFalse(result.local_search_performed)

    def test_cli_never_prints_private_values_or_argparse_inputs(self):
        for args in (["--grade", SENTINEL], ["--unknown-" + SENTINEL],
                     ["--topic", SENTINEL], ["--operator", SENTINEL]):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = local.main(args)
            payload = json.loads(out.getvalue())
            self.assertEqual(code, 1)
            self.assertFalse(payload["local_search_performed"])
            self.assertNotIn(SENTINEL, out.getvalue() + err.getvalue())
        with patch.object(index, "load_valid_index", return_value=fake_snapshot([metadata()])), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(local.main(["--operator", "berechnen"]), 0)
        self.assertLessEqual(len(out.getvalue()), 1024)
        self.assertNotIn("one.tex", out.getvalue())


class FederationTests(unittest.TestCase):
    def test_private_zone_case_alias_and_invalid_scope_fail_closed(self):
        for scope in ([], {}, None):
            result = federation.search_with_local_orientation(scope=scope)
            self.assertEqual(result.public_reason_code, "scope_invalid")
        with patch.object(sqlite3, "connect", side_effect=AssertionError("must not open")):
            result = federation.search_with_local_orientation(
                corpus=Path(tempfile.gettempdir()) / ".SCHULLIA-LOCAL" / "state")
        self.assertEqual(result.public_reason_code, "public_index_boundary_invalid")

    def test_default_public_corpus_junction_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="schullia-boundary-") as temporary:
            base = Path(temporary)
            repo = base / "repo"
            repo.mkdir()
            external = make_public_corpus(base)
            link = repo / "corpus"
            if not create_directory_link(link, external):
                self.skipTest("directory links unavailable")
            result = federation.search_with_local_orientation(
                repo, scope="public", public_query="public"
            )
            self.assertEqual(
                result.public_reason_code, "public_index_boundary_invalid"
            )
            self.assertFalse(result.public_search_performed)
            self.assertEqual(result.public_results, ())

    @unittest.skipUnless(os.name == "nt", "Win32 path-alias regression")
    def test_private_zone_trailing_dot_alias_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="schullia-alias-") as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            private_zone = repo / ".schullia-local"
            private_zone.mkdir()
            make_public_corpus(private_zone)
            alias = repo / ".schullia-local." / "public-corpus"
            with patch.object(
                sqlite3, "connect", side_effect=AssertionError("must not open")
            ):
                result = federation.search_with_local_orientation(
                    repo, corpus=alias, scope="public", public_query="public"
                )
            self.assertEqual(
                result.public_reason_code, "public_index_boundary_invalid"
            )
            self.assertFalse(result.public_search_performed)
            self.assertEqual(result.public_results, ())

    def test_local_result_reason_state_matrix_is_closed(self):
        for values in (
            {
                "availability_state": config.STATE_AVAILABLE,
                "reason_code": "index_missing",
                "index_ready": True,
                "local_search_performed": True,
            },
            {"reason_code": "private_reason_sentinel"},
        ):
            with self.assertRaises(local.SearchFault):
                local.LocalSearchResult(**values)

    def test_public_default_ignores_local_and_preserves_public_provenance(self):
        with tempfile.TemporaryDirectory(prefix="schullia-public-") as temporary:
            base = Path(temporary)
            corpus = make_public_corpus(base)
            before = tree_signature(corpus)
            with patch.object(config, "load_validated_sources", side_effect=AssertionError("private config")), \
                 patch.object(federation, "search_local_orientation", side_effect=AssertionError("local route")), \
                 patch.object(Path, "as_uri", side_effect=AssertionError("URI path forbidden")), \
                 patch.object(socket, "create_connection", side_effect=AssertionError("network")):
                result = federation.search_with_local_orientation(
                    base, corpus=corpus, public_query="public",
                    explicit_config=base / (SENTINEL + ".json"), local_filters={SENTINEL: SENTINEL})
            self.assertTrue(result.public_search_performed, result.public_reason_code)
            self.assertEqual(len(result.public_results), 1)
            self.assertEqual(result.public_results[0]["provenance"]["resolved_revision"], "a" * 40)
            self.assertEqual(result.local.reason_code, "local_not_requested")
            self.assertEqual(tree_signature(corpus), before)
            self.assertNotIn(SENTINEL, json.dumps(result.as_dict()))
            detached = result.public_results[0]
            detached["title"] = "changed"
            self.assertNotEqual(
                result.public_results[0]["title"], "changed"
            )
            with self.assertRaises(AttributeError):
                result.local = local.LocalSearchResult()
            with self.assertRaises(local.SearchFault):
                federation.FederatedSearchResult(
                    "public", ({"title": "before"},),
                    "public_not_requested", False,
                )

    def test_both_keeps_local_hits_internal_and_falls_back_on_error(self):
        with tempfile.TemporaryDirectory(prefix="schullia-both-") as temporary:
            base = Path(temporary)
            corpus = make_public_corpus(base)
            private = local.LocalSearchResult(
                (local.LocalHit(metadata(), (), ()),), availability_state=config.STATE_AVAILABLE,
                reason_code="search_complete", index_ready=True, local_search_performed=True)
            with patch.object(federation, "search_local_orientation", return_value=private):
                result = federation.search_with_local_orientation(
                    base, corpus=corpus, public_query="public", scope="both")
            output = json.dumps(result.as_dict())
            self.assertEqual(len(result.local.hits), 1)
            for secret in (SENTINEL, "one.tex", "synthetic-group"):
                self.assertNotIn(secret, output)
            self.assertTrue(result.public_search_performed)
            self.assertTrue(result.local.local_search_performed)
            with patch.object(federation, "search_local_orientation", side_effect=OSError(SENTINEL)):
                fallback = federation.search_with_local_orientation(base, corpus=corpus, scope="both")
            self.assertTrue(fallback.public_search_performed)
            self.assertFalse(fallback.local.local_search_performed)
            self.assertNotIn(SENTINEL, json.dumps(fallback.as_dict()))

    def test_local_only_and_output_budget(self):
        with patch.object(federation, "_public_search", side_effect=AssertionError("public route")), \
             patch.object(federation, "search_local_orientation", return_value=local.LocalSearchResult(
                 reason_code="configuration_disabled", availability_state=config.STATE_NOT_CONFIGURED)):
            result = federation.search_with_local_orientation(scope="local")
        self.assertFalse(result.public_search_performed)
        self.assertEqual(result.local.availability_state, config.STATE_NOT_CONFIGURED)
        with tempfile.TemporaryDirectory(prefix="schullia-output-") as temporary:
            corpus = make_public_corpus(Path(temporary))
            result = federation.search_with_local_orientation(
                corpus.parent, corpus=corpus,
                limits=local.SearchLimits(max_output_chars=1024))
            self.assertLessEqual(len(json.dumps(result.as_dict(), ensure_ascii=True, sort_keys=True)), 1024)

    def test_public_sql_injection_and_read_errors_are_sanitized(self):
        with tempfile.TemporaryDirectory(prefix="schullia-sql-") as temporary:
            corpus = make_public_corpus(Path(temporary))
            before = tree_signature(corpus)
            result = federation.search_with_local_orientation(
                corpus.parent, corpus=corpus,
                public_query="'; DROP TABLE documents; --")
            self.assertTrue(result.public_search_performed)
            self.assertEqual(tree_signature(corpus), before)
        with patch.object(sqlite3, "connect", side_effect=sqlite3.OperationalError(SENTINEL)):
            with tempfile.TemporaryDirectory() as temporary:
                corpus = make_public_corpus.__globals__["Path"](temporary)
                (corpus / "index.sqlite").write_bytes(b"synthetic")
                result = federation.search_with_local_orientation(
                    corpus.parent, corpus=corpus
                )
        self.assertEqual(result.public_reason_code, "public_search_operational_error")
        self.assertNotIn(SENTINEL, json.dumps(result.as_dict()))

    def test_wrapper_cli_argument_errors_are_sanitized(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(federation.main(["--scope", SENTINEL]), 1)
        self.assertEqual(json.loads(out.getvalue())["public"]["reason_code"], "arguments_invalid")
        self.assertNotIn(SENTINEL, out.getvalue() + err.getvalue())


if __name__ == "__main__":
    unittest.main()
