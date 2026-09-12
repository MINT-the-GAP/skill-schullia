#!/usr/bin/env python3
"""Dependency-free regressions for source-pinned weekly course profiles."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import profile_weekly_courses as profiler

OPTIONS = profiler.read_json(profiler.OPTIONS_PATH)
REVISION = "a" * 40
HEADER = """<!--
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-loot/main/README.md
-->
"""
COURSE = HEADER + """# Start
@Ressourcen(0, 0, 50)
@Highscore(1000, 5, 10, 20, 2)
@achievements
@Schaufel

## Aufgabe 1
Berechne 1 + 1.
[[2]]

@Schatztruhe(2; anker)

@Pflanze
@Energiekiste(3)
@EndePflanze

## Erholungsgarten
@Erdhaufen.inline(@Diamanttruhe)

## Selbsteinschätzung
Wie sicher bist du?
[[ sicher | unsicher ]]

## Abgabe
"""


def entry_for(path: str, text: str) -> dict:
    return {
        "path": path, "stored": True, "source_id": profiler.SOURCE_ID,
        "revision_sha": REVISION,
        "web_url": f"https://github.com/MINT-the-GAP/Wochenaufgabe/blob/{REVISION}/{path}",
        "content_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def make_snapshot(root: Path, files: dict[str, str]) -> Path:
    corpus = root / "corpus"
    source = corpus / "sources" / "arbitrary-directory-no-fixed-hash"
    source.mkdir(parents=True)
    (source / "source.json").write_text(json.dumps({
        "source_id": profiler.SOURCE_ID, "revision_sha": REVISION,
        "web_url": "https://github.com/MINT-the-GAP/Wochenaufgabe",
    }), encoding="utf-8")
    entries = []
    for path, text in files.items():
        target = source / "files" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
        entries.append(entry_for(path, text))
    (source / "manifest.jsonl").write_text("\n".join(json.dumps(entry) for entry in entries), encoding="utf-8")
    return corpus


class ProfileTests(unittest.TestCase):
    def profile(self, text: str = COURSE, path: str = "9/Mathematik/Lia9_27.md"):
        return profiler.profile_course(text.encode("utf-8"), entry_for(path, text), OPTIONS)

    def test_whole_course_order_phases_and_nested_placement(self):
        result = self.profile()
        self.assertEqual(result["grade"], 9)
        self.assertEqual(result["week"], 27)
        self.assertEqual(result["learning_slide_count"], 1)
        self.assertEqual(result["native_task_quiz_count"], 1)
        self.assertEqual(result["slides"][1]["family_sequence"], ["reward", "plant", "reward"])
        self.assertEqual(result["phase_counts"]["garden"], {"earth": 1, "reward": 1})
        self.assertEqual(result["macro_counts"]["EndePflanze"], 1)
        self.assertEqual(result["family_counts"]["plant"], 1)
        nested = next(e for e in result["slides"][2]["events"] if e["macro"] == "Diamanttruhe")
        self.assertIn("nested_macro", nested["placement"])
        reward = next(e for e in result["slides"][1]["events"] if e["macro"] == "Energiekiste")
        self.assertIn("inside_plant", reward["placement"])
        self.assertEqual(result["configurations"][0]["argument_source"], "0, 0, 50")
        self.assertEqual(result["content_sha256"], hashlib.sha256(COURSE.encode("utf-8")).hexdigest())
        self.assertIn(REVISION, result["web_url"])

    def test_lexical_candidates_remain_separate_from_parsed_instances(self):
        text = COURSE + "\n`@Schloss(check, red)`\n<!-- @Schloss(check, red) -->\n"
        result = self.profile(text)
        self.assertNotIn("Schloss", result["macro_counts"])
        self.assertEqual(result["lexical_inventory"]["public_macro_text_counts"]["Schloss"], 2)
        self.assertEqual(result["structure_status"], "no_mapper_diagnostic")

    def test_import_header_definition_comment_and_code_are_not_body_loot(self):
        text = """<!--
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-loot/main/README.md
@myMacro: @Schatztruhe
-->
# Start
`@Schatztruhe`
<!-- @Schatztruhe -->
```text
@Schatztruhe
```
## Aufgabe
Berechne.
[[2]]
"""
        self.assertIsNone(self.profile(text))

    def test_placeholder_with_configuration_and_reflection_is_excluded(self):
        text = HEADER + "# Start\n@Ressourcen(0,0,50)\n## Aufgabe 1: Aufgabenplatzhalter\n## Selbsteinschätzung\nWie sicher?\n[[ gut | schlecht ]]\n"
        self.assertIsNone(self.profile(text))

    def test_alias_is_canonicalized_without_counting_internal_calls(self):
        text = HEADER + "# Start\n@Erfolge\n@Energietruhe(3)\n@LootTruhe_(1)\n## Aufgabe\nBerechne.\n[[2]]\n"
        result = self.profile(text)
        self.assertEqual(result["macro_counts"], {"Energiekiste": 1, "achievements": 1})
        self.assertEqual(result["slides"][0]["events"][0]["authored_name"], "Erfolge")

    def test_imported_task_instance_qualifies_without_native_quiz(self):
        text = HEADER.replace("-->\n", "import: https://raw.githubusercontent.com/MINT-the-GAP/lia-orthography/main/README.md\n-->\n")
        text += '# Start\n@achievements\n## Aufgabe\n@orthography(``, `Feler`, `Fehler`)\n'
        result = self.profile(text)
        self.assertIsNotNone(result)
        self.assertGreater(result["imported_task_instance_count"], 0)

    def test_discovery_is_dynamic_and_special_course_requires_explicit_inclusion(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = make_snapshot(Path(directory), {
                "9/Mathematik/Lia9_27.md": COURSE,
                "12/Chemie/Lia12_108.md": COURSE,
                "5/Lia5_SK.md": COURSE,
                "README.md": COURSE,
                "5/Deutsch/Lia5_41.md": HEADER + "# Empty\n",
            })
            profile = profiler.build_profiles(corpus, course_paths=["9/Mathematik/Lia9_27.md"])
            self.assertEqual(profile["selection"]["profiled_count"], 2)
            self.assertEqual(len(profile["courses"]), 1)
            self.assertEqual({x["path"] for x in profile["selection"]["other_gamified_paths"]}, {"5/Lia5_SK.md"})
            included = profiler.build_profiles(corpus, include_paths=["5/Lia5_SK.md"])
            self.assertEqual(included["selection"]["profiled_count"], 3)
            special = next(x for x in included["courses"] if x["path"] == "5/Lia5_SK.md")
            self.assertEqual(special["course_kind"], "additional_reviewed_course")
            self.assertIsNone(special["subject"])
            self.assertEqual(included["selection"]["included_paths"], ["5/Lia5_SK.md"])

    def test_manifest_hash_mismatch_fails_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = make_snapshot(Path(directory), {"9/Mathematik/Lia9_27.md": COURSE})
            path = next((corpus / "sources").glob("*/files/9/Mathematik/Lia9_27.md"))
            changed = COURSE + "\nChanged\n"
            path.write_text(changed, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from manifest"):
                profiler.build_profiles(corpus)
            self.assertEqual(path.read_text(encoding="utf-8"), changed)

    def test_manifest_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = make_snapshot(Path(directory), {"9/Mathematik/Lia9_27.md": COURSE})
            manifest = next((corpus / "sources").glob("*/manifest.jsonl"))
            manifest.write_text(json.dumps(entry_for("9/../../outside.md", COURSE)), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unsafe manifest path"):
                profiler.build_profiles(corpus)

    def test_snapshot_partial_acceptance_and_content_changes(self):
        accepted = {
            "schema_version": 1, "source": {"source_id": profiler.SOURCE_ID, "revision_sha": REVISION},
            "selection": {"profiled_courses": [{"path": "a", "content_sha256": "1"}, {"path": "b", "content_sha256": "2"}]},
            "courses": [{"path": "a", "content_sha256": "1"}],
        }
        current = deepcopy(accepted)
        current["source"]["revision_sha"] = "b" * 40
        comparison = profiler.compare_snapshot(current, accepted)
        self.assertTrue(comparison["matches"])
        self.assertTrue(comparison["source_revision_changed"])
        self.assertEqual(comparison["known_unaccepted"], ["b"])
        current["selection"]["profiled_courses"][0]["content_sha256"] = "changed"
        current["selection"]["profiled_courses"].append({"path": "c", "content_sha256": "3"})
        comparison = profiler.compare_snapshot(current, accepted)
        self.assertFalse(comparison["matches"])
        self.assertEqual(comparison["changed"], ["a"])
        self.assertEqual(comparison["added"], ["c"])
        current["selection"]["profiled_courses"] = []
        self.assertEqual(profiler.compare_snapshot(current, accepted)["removed"], ["a"])

    def test_new_special_course_requires_review_and_missing_include_is_reportable(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = make_snapshot(Path(directory), {"9/Mathematik/Lia9_27.md": COURSE})
            accepted = profiler.build_profiles(corpus)
            current = deepcopy(accepted)
            current["selection"]["other_gamified_paths"] = [{"path": "5/Lia5_SK.md"}]
            difference = profiler.compare_snapshot(current, accepted)
            self.assertFalse(difference["matches"])
            self.assertEqual(difference["new_review_candidates"], ["5/Lia5_SK.md"])
            accepted["courses"].append({"path": "5/Lia5_SK.md", "content_sha256": "old"})
            current = profiler.build_profiles(corpus, include_paths=["5/Lia5_SK.md"], strict_includes=False)
            self.assertEqual(profiler.compare_snapshot(current, accepted)["removed"], ["5/Lia5_SK.md"])

    def test_check_reuses_only_verified_unchanged_profiles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unchanged = "9/Mathematik/Lia9_27.md"
            changed = "9/Mathematik/Lia9_28.md"
            added = "10/Physik/Lia10_01.md"
            special = "7/Physik/Experiment.md"
            corpus = make_snapshot(root, {unchanged: COURSE, changed: COURSE})
            accepted = profiler.build_profiles(corpus)
            snapshot = root / "accepted.json"
            snapshot.write_text(json.dumps(accepted), encoding="utf-8")
            with patch.object(profiler.map_course, "map_source", wraps=profiler.map_course.map_source) as mapper:
                with redirect_stdout(io.StringIO()):
                    status = profiler.main(["--corpus-root", str(corpus), "--check", str(snapshot)])
                self.assertEqual(status, 0)
                self.assertEqual(mapper.call_count, 0)
            source = next((corpus / "sources").iterdir())
            contents = {unchanged: COURSE, changed: COURSE + "\n@Schatztruhe(4)\n", added: COURSE, special: COURSE}
            for path, text in contents.items():
                target = source / "files" / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(text.encode("utf-8"))
            (source / "manifest.jsonl").write_text("\n".join(json.dumps(entry_for(path, text))
                                                          for path, text in contents.items()), encoding="utf-8")
            output = io.StringIO()
            with patch.object(profiler.map_course, "map_source", wraps=profiler.map_course.map_source) as mapper:
                with redirect_stdout(output):
                    status = profiler.main(["--corpus-root", str(corpus), "--check", str(snapshot), "--json"])
                self.assertEqual(status, 1)
                self.assertEqual(mapper.call_count, 3)
            result = json.loads(output.getvalue())
            self.assertEqual(result["changed"], [changed])
            self.assertEqual(result["added"], [added])
            self.assertEqual(result["new_review_candidates"], [special])
            # An unchanged manifest hash cannot hide changed bytes on disk.
            (source / "files" / unchanged).write_bytes((COURSE + "tampered").encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "differs from manifest"):
                profiler.build_profiles(corpus, check_snapshot=accepted)

    def test_cli_check_reports_deleted_include_and_new_subject_special_course(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            regular = "9/Mathematik/Lia9_27.md"
            special = "5/Lia5_SK.md"
            added = "7/Physik/Experiment.md"
            corpus = make_snapshot(root, {regular: COURSE, special: COURSE})
            accepted = profiler.build_profiles(corpus, include_paths=[special])
            # Compact snapshots need only provenance, selection and accepted hashes.
            accepted["courses"] = [{"path": item["path"], "content_sha256": item["content_sha256"]}
                                   for item in accepted["courses"]]
            snapshot = root / "accepted.json"
            snapshot.write_text(json.dumps(accepted), encoding="utf-8")
            source = next((corpus / "sources").iterdir())
            (source / "files" / special).unlink()
            new_file = source / "files" / added
            new_file.parent.mkdir(parents=True)
            new_file.write_bytes(COURSE.encode("utf-8"))
            (source / "manifest.jsonl").write_text("\n".join(json.dumps(entry_for(path, COURSE))
                                                          for path in [regular, added]), encoding="utf-8")
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                status = profiler.main(["--corpus-root", str(corpus), "--check", str(snapshot), "--json"])
            self.assertEqual(status, 1, errors.getvalue())
            self.assertEqual(errors.getvalue(), "")
            result = json.loads(output.getvalue())
            self.assertEqual(result["removed"], [special])
            self.assertEqual(result["new_review_candidates"], [added])
            self.assertFalse(result["matches"])

    def test_check_is_read_only_and_reuses_snapshot_special_courses(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = make_snapshot(root, {"9/Mathematik/Lia9_27.md": COURSE, "5/Lia5_SK.md": COURSE})
            accepted = profiler.build_profiles(corpus, include_paths=["5/Lia5_SK.md"])
            snapshot = root / "accepted.json"
            snapshot.write_text(json.dumps(accepted), encoding="utf-8")
            before = snapshot.read_bytes()
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(io.StringIO()):
                status = profiler.main(["--corpus-root", str(corpus), "--check", str(snapshot), "--json"])
            self.assertEqual(status, 0)
            self.assertTrue(json.loads(output.getvalue())["matches"])
            self.assertEqual(snapshot.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
