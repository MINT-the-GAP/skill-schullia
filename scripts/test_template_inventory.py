#!/usr/bin/env python3
"""Regression tests for read-only template inventory and review drift."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from template_inventory import inspect_readme, inventory, is_template, stored_path


class InventoryTests(unittest.TestCase):
    def test_discovery_scope(self):
        self.assertTrue(is_template({"collection": "template-reference"}))
        self.assertTrue(is_template({"owner": "MINT-the-GAP", "repo": "lia-new"}))
        self.assertFalse(is_template({"owner": "MINT-the-GAP", "repo": "Wochenaufgabe"}))
        self.assertFalse(is_template({"owner": "LiaScript", "repo": "docs"}))

    def test_header_bodies_and_fenced_examples_are_not_declarations(self):
        text = (
            "<!--\n@public: @Internal_(@0)\n@Block\n"
            "<script>\n@body_call\n</script>\n@end\n"
            "@style\nbody { color: red }\n@end\n-->\n"
            "# API\n\x60\x60\x60markdown\n# Example only\n"
            "@not_a_definition\n\x60\x60\x60\n## Options\n"
        )
        found = inspect_readme(text)
        self.assertEqual([(item["name"], item["line"]) for item in found["header_declarations"]],
                         [("public", 2), ("Block", 3), ("style", 8)])
        self.assertEqual([item["heading"] for item in found["documentation_sections"]],
                         ["API", "Options"])
        self.assertFalse(found["unterminated_macro_block"])

    def test_nested_comments_in_macro_and_legacy_definitions(self):
        text = ("<!--\nauthor: Known Author\nimport: dependency\n"
                "@lines\n<script>\n<!-- class=example -->\n"
                "</script>\n@end\nTextmarkerQuiz: <span>quiz</span>\n"
                "markred: <span>@0</span>\n@after: ok\n-->\n# Actual API\n")
        found = inspect_readme(text)
        self.assertEqual([item["name"] for item in found["header_declarations"]],
                         ["lines", "TextmarkerQuiz", "markred", "after"])
        self.assertEqual(found["documentation_sections"],
                         [{"heading": "Actual API", "line": 13}])
        self.assertFalse(found["unterminated_macro_block"])

    def test_unterminated_block_is_reported(self):
        self.assertTrue(inspect_readme("<!--\n@Broken\ntext\n-->\n# API")[
            "unterminated_macro_block"])

    def test_paths_cannot_escape_corpus(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                stored_path(Path(temp), "../outside.md")
            with self.assertRaises(ValueError):
                stored_path(Path(temp), str(Path(temp).resolve() / "absolute.md"))

    def fixture(self, root):
        corpus = root / "corpus"
        refs = root / "references"
        corpus.mkdir()
        refs.mkdir()
        (refs / "detail.md").write_text("Reviewed API\n", encoding="utf-8")
        data = b"<!--\n@Quiz: content\n-->\n# Options\n"
        (corpus / "README.md").write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        source = {"source_id": "ghrepo:mint-the-gap/lia-example",
                  "repo": "lia-example", "owner": "MINT-the-GAP",
                  "revision_sha": "a" * 40, "state": "current"}
        record = {"source_id": source["source_id"], "path": "README.md",
                  "local_relpath": "README.md", "stored": True, "is_text": True,
                  "revision_sha": source["revision_sha"], "content_sha256": digest}
        catalog = {"templates": [{"source_id": source["source_id"],
                                 "reviewed_revision": source["revision_sha"],
                                 "readme_sha256": digest, "reference": "detail.md"}]}
        (corpus / "sources.json").write_text(json.dumps([source]), encoding="utf-8")
        (corpus / "files.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
        return corpus, refs, source, record, catalog

    def test_current_inventory_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, refs, _, _, catalog = self.fixture(Path(temp))
            before = {p: p.read_bytes() for p in corpus.iterdir()}
            rows, issues = inventory(corpus, catalog, refs)
            self.assertEqual(issues, [])
            self.assertEqual(rows[0]["header_declarations"][0]["name"], "Quiz")
            self.assertEqual(before, {p: p.read_bytes() for p in corpus.iterdir()})

    def test_revision_change_without_readme_change_still_requires_review(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, refs, source, record, catalog = self.fixture(Path(temp))
            source["revision_sha"] = record["revision_sha"] = "b" * 40
            (corpus / "sources.json").write_text(json.dumps([source]), encoding="utf-8")
            (corpus / "files.jsonl").write_text(json.dumps(record), encoding="utf-8")
            rows, issues = inventory(corpus, catalog, refs)
            self.assertEqual(rows[0]["review_status"], "revision_changed")
            self.assertEqual(len(issues), 1)

    def test_new_template_and_removed_source_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, refs, _, _, catalog = self.fixture(Path(temp))
            _, issues = inventory(corpus, {"templates": []}, refs)
            self.assertIn("new_template", issues[0])
            (corpus / "sources.json").write_text("[]", encoding="utf-8")
            _, issues = inventory(corpus, catalog, refs)
            self.assertIn("reviewed_template_missing_from_corpus", issues[0])

    def test_tampered_readme_and_missing_reference_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, refs, _, _, catalog = self.fixture(Path(temp))
            (corpus / "README.md").write_text("changed\n", encoding="utf-8")
            catalog["templates"][0]["reference"] = "absent.md"
            rows, _ = inventory(corpus, catalog, refs)
            self.assertIn("readme_manifest_hash_mismatch", rows[0]["review_status"])
            self.assertIn("readme_changed", rows[0]["review_status"])
            self.assertIn("missing_reference", rows[0]["review_status"])


if __name__ == "__main__":
    unittest.main()
