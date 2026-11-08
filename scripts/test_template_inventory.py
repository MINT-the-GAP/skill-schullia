#!/usr/bin/env python3
"""Regression tests for read-only template inventory and review drift."""
from __future__ import annotations

import io
import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from template_inventory import (
    inspect_readme,
    inventory,
    is_template,
    main,
    select_inventory,
    stored_path,
)


ROOT = Path(__file__).resolve().parents[1]


class InventoryTests(unittest.TestCase):
    def test_syntax_contract_covers_current_template_catalog(self):
        catalog = json.loads(
            (ROOT / 'references' / 'template-catalog.json').read_text(encoding='utf-8')
        )
        contract = json.loads(
            (ROOT / 'references' / 'syntax-contract.json').read_text(encoding='utf-8')
        )
        catalog_by_id = {item['source_id']: item for item in catalog['templates']}
        contract_by_id = {item['source_id']: item for item in contract['templates']}
        self.assertEqual(len(catalog_by_id), 24)
        self.assertEqual(set(contract_by_id), set(catalog_by_id))

        rule_ids = {
            item['id'] for group in ('general_rules', 'template_rules')
            for item in contract[group]
        }
        for source_id, item in contract_by_id.items():
            self.assertEqual(item['reference'], catalog_by_id[source_id]['reference'])
            self.assertTrue((ROOT / 'references' / item['reference']).is_file())
            self.assertTrue(item['browser_rules'])
            self.assertLessEqual(set(item['rules']), rule_ids)

    def test_syntax_contract_rules_are_auditable(self):
        contract = json.loads(
            (ROOT / 'references' / 'syntax-contract.json').read_text(encoding='utf-8')
        )
        allowed = set(contract['verification_levels'])
        rules = contract['general_rules'] + contract['template_rules']
        self.assertEqual(len({item['id'] for item in rules}), len(rules))
        for item in rules:
            self.assertIn(item['verification'], allowed)
            self.assertTrue(item['source'])
            self.assertIn('anchor', item)
            self.assertIn('attachment', item)
            self.assertIn('imports', item)
            if item['verification'] == 'static':
                self.assertTrue(item['validator_code'])
        for item in contract['general_rules']:
            self.assertTrue(item['valid'])
            self.assertTrue(item['invalid'])

    def selection_fixture(self):
        rows = [
            {
                'source_id': 'ghrepo:mint-the-gap/lia-current',
                'repo': 'lia-current',
                'review_status': 'current',
                'reference': 'current.md',
                'header_declarations': [],
            },
            {
                'source_id': 'ghrepo:mint-the-gap/lia-stale',
                'repo': 'lia-stale',
                'review_status': 'revision_changed',
                'reference': 'stale.md',
                'header_declarations': [],
            },
        ]
        issues = ['ghrepo:mint-the-gap/lia-stale: revision_changed']
        return rows, issues

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

    def test_source_selection_ignores_unrelated_review_issues(self):
        rows, issues = self.selection_fixture()
        selected, selected_issues = select_inventory(rows, issues, 'lia-current')
        self.assertEqual([row['repo'] for row in selected], ['lia-current'])
        self.assertEqual(selected_issues, [])

    def test_source_selection_preserves_global_issues(self):
        rows, issues = self.selection_fixture()
        issues.append('Duplicate source_id in template catalog')
        _, selected_issues = select_inventory(rows, issues, 'lia-current')
        self.assertEqual(selected_issues, ['Duplicate source_id in template catalog'])

    def run_mocked_main(self, arguments):
        rows, issues = self.selection_fixture()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch('template_inventory.inventory', return_value=(rows, issues)),
            patch('template_inventory.read_json', return_value={'templates': []}),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = main(arguments)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_check_for_current_selected_source_succeeds(self):
        status, output, _ = self.run_mocked_main(
            ['--source', 'lia-current', '--check'],
        )
        self.assertEqual(status, 0)
        self.assertIn('review issues: 0', output)
        self.assertNotIn('lia-stale', output)

    def test_check_for_stale_selected_source_fails(self):
        status, output, _ = self.run_mocked_main(
            ['--source', 'lia-stale', '--check'],
        )
        self.assertEqual(status, 1)
        self.assertIn('REVIEW ghrepo:mint-the-gap/lia-stale', output)

    def test_unfiltered_check_still_fails(self):
        status, output, _ = self.run_mocked_main(['--check'])
        self.assertEqual(status, 1)
        self.assertIn('lia-stale', output)

    def test_json_output_contains_only_selected_issues(self):
        status, output, _ = self.run_mocked_main(
            ['--source', 'lia-current', '--json', '--check'],
        )
        payload = json.loads(output)
        self.assertEqual(status, 0)
        self.assertEqual([row['repo'] for row in payload['templates']], ['lia-current'])
        self.assertEqual(payload['issues'], [])

    def test_unknown_source_returns_two(self):
        status, _, error = self.run_mocked_main(
            ['--source', 'does-not-exist', '--check'],
        )
        self.assertEqual(status, 2)
        self.assertIn('No template matches', error)


if __name__ == "__main__":
    unittest.main()
