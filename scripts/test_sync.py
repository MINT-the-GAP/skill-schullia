#!/usr/bin/env python3
"""Dependency-free regression tests for source synchronization decisions."""

from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile

import sync_sources as sync
import update_knowledge as update

ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_freshness_requires_matching_configuration() -> None:
    with tempfile.TemporaryDirectory() as directory:
        corpus = Path(directory)
        configuration = {"schema_version": 1, "files": [{"id": "one"}]}
        digest = sync.config_sha256(configuration)
        write_json(corpus / "state.json", {"config_sha256": digest})
        write_json(
            corpus / "sync-report.json",
            {
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "failures": [],
            },
        )

        assert sync.last_run_is_fresh(corpus, 24, digest)
        assert not sync.last_run_is_fresh(corpus, 24, "changed-configuration")


def test_index_freshness_uses_content_hashes() -> None:
    with tempfile.TemporaryDirectory() as directory:
        corpus = Path(directory)
        write_json(corpus / "sources.json", [])
        (corpus / "files.jsonl").write_text("", encoding="utf-8")
        expected = update.expected_index_metadata(corpus)
        assert expected is not None
        with closing(sqlite3.connect(corpus / "index.sqlite")) as connection:
            connection.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
            connection.executemany(
                "INSERT INTO meta VALUES (?,?)", expected.items()
            )
            connection.commit()

        assert update.index_is_current(corpus)
        (corpus / "files.jsonl").write_text("{}\n", encoding="utf-8")
        assert not update.index_is_current(corpus)


def test_lia_loot_reference_contract() -> None:
    options_path = ROOT / "references" / "lia-loot-options.json"
    options = json.loads(options_path.read_text(encoding="utf-8"))

    assert options["schema_version"] == 2
    assert set(options["macros"]) == {
        "Highscore",
        "Ressourcen",
        "achievements",
        "lootif",
        "Endelootif",
        "Schatztruhe",
        "Diamanttruhe",
        "Energiekiste",
        "Schluessel",
        "Lupe",
        "Schaufel",
        "Giesskanne",
        "Erdhaufen",
        "EndeErdhaufen",
        "Pflanze",
        "EndePflanze",
        "Unsichtbar",
        "Zauberstaub",
        "Portal",
        "Einwegportal",
        "Einbahnportal",
        "Schloss",
        "Geheimfolie",
    }
    assert set(options["macros"]["Endelootif"]["aliases"]) == {
        "EndeLootif", "endlootif", "EndLootIf",
    }
    assert options["macros"]["Pflanze"]["aliases"] == ["Blume"]
    assert options["macros"]["EndePflanze"]["aliases"] == ["EndeBlume"]
    assert set(options["public_macro_names_including_aliases"]) == {
        "Highscore",
        "Ressourcen",
        "achievements",
        "Achievements",
        "Erfolge",
        "lootif",
        "Endelootif",
        "EndeLootif",
        "endlootif",
        "EndLootIf",
        "Schatztruhe",
        "Diamanttruhe",
        "Energiekiste",
        "Schluessel",
        "Lupe",
        "Schaufel",
        "Giesskanne",
        "Erdhaufen",
        "EndeErdhaufen",
        "Pflanze",
        "Blume",
        "EndePflanze",
        "EndeBlume",
        "Portal",
        "Einwegportal",
        "Einbahnportal",
        "Unsichtbar",
        "Zauberstaub",
        "Schloss",
        "Geheimfolie",
    }
    assert {
        "LootIfStart_",
        "LootIfEnd_",
        "LootWerkzeug_",
        "LootRevealStart_",
        "LootRevealEnd_",
    }.issubset(options["emission_policy"]["internal_macros_forbidden"])
    assert set(options["key_colors"]) == {
        "rot", "blau", "gruen", "gelb", "lila", "orange",
    }
    assert set(options["key_color_aliases"]) == {
        "red", "blue", "green", "yellow", "purple", "orange",
    }
    assert set(options["surface_targets"]) == {
        "toc", "menu", "classroom", "info", "translator", "mode",
    }
    assert set(options["surface_target_aliases"]) == set(
        options["surface_targets"]
    )
    assert set(options["lock_target_aliases"]) == {
        "toc",
        "mode",
        "menu",
        "translator",
        "classroom",
        "info",
        "seitenwechsel",
        "check",
        "resolve",
        "hint",
        "portal",
    }
    assert {item["id"] for item in options["template_targets"]} == {
        "dynflex",
        "timer",
        "boardmode",
        "marker",
        "markerquiz",
        "annotation",
        "canvasocr",
        "kachel",
        "mathpath",
        "llm",
        "coordinate",
        "freeze",
    }
    assert all("accepted_aliases" in item for item in options["template_targets"])
    assert options["portal_modes"]["two_way"]["canonical"] == "hinundher"
    assert options["portal_modes"]["one_way"]["canonical"] == "einweg"
    shared = options["shared_collectible_options"]
    assert set(shared["applies_to"]) == {
        "Schatztruhe",
        "Diamanttruhe",
        "Energiekiste",
        "Schluessel",
        "Lupe",
        "Schaufel",
        "Giesskanne",
        "Erdhaufen",
        "Pflanze",
    }
    assert set(shared["does_not_apply_to"]) == {
        "Portal",
        "Einwegportal",
        "Einbahnportal",
        "Schloss",
        "Unsichtbar",
        "Zauberstaub",
    }
    environment = shared["environment"]
    assert environment["same_axis"] == "OR"
    assert environment["different_axes"] == "AND"
    assert environment["live_reevaluation_before_collection"] is True
    assert set(environment["theme"]["canonical"]) == {
        "theme=rot", "theme=gelb", "theme=tuerkis", "theme=blau",
    }
    assert set(environment["variant"]["canonical"]) == {
        "farbmodus=dunkel", "farbmodus=hell",
    }
    assert environment["annotations"]["canonical"] == "annotationen=aus"
    assert shared["direct_layers"]["order"] == (
        "left_to_right_outer_to_inner_then_item"
    )
    assert set(shared["direct_layers"]["canonical_kinds"]) == {
        "erde", "pflanze",
    }

    conditional = options["conditional_spawn"]
    assert conditional["canonical_action"] == "spawn"
    assert set(conditional["comparators"]) == {">", ">=", "=", "<=", "<"}
    assert set(conditional["trigger_families"]) == {
        "previous_quiz",
        "current_slide_quizzes",
        "solved_quizzes",
        "resources",
        "opened_chests",
        "lock_target",
        "secret_slide",
        "magnifier",
        "marker",
    }
    assert conditional["valid_closed_range_in_full_catalog_before_spawn"] is True
    assert (
        conditional["valid_closed_range_in_active_source_declarations_before_spawn"]
        is False
    )
    assert options["range_rules"]["nesting"] == "LIFO"
    assert options["range_rules"]["cross_slide_pairing"] is False

    assert {item["id"] for item in options["fixed_achievements"]} == {
        "all-quizzes-solved",
        "perfect-highscore",
        "all-treasure-chests-opened",
        "all-diamond-chests-opened",
        "all-energy-chests-opened",
        "all-invisible-objects-found",
        "all-magic-dust-objects-found",
        "all-soil-dug",
        "all-plants-bloomed",
        "all-locks-opened",
        "secret-slide-found",
    }
    assert options["achievement_catalog"]["zero_total_does_not_unlock"] is True
    assert (
        options["achievement_catalog"][
            "valid_closed_lootif_ranges_count_before_spawn"
        ]
        is True
    )
    variation = options["variation_contract"]
    assert variation["minimum_changed_dimensions_from_nearest_prior"] == 3
    assert variation["minimum_changed_core_dimensions_from_nearest_prior"] == 1
    assert variation["identical_fingerprint_forbidden"] is True
    assert set(variation["immediate_predecessor_must_change_one_of"]) == {
        "primary_mechanic", "path_topology",
    }
    assert {
        "VAR-FINGERPRINT-ALL-HISTORY",
        "VAR-NO-IDENTICAL-FINGERPRINT",
        "VAR-NO-LOCK-DEFAULT",
        "VAR-STRUCTURAL-DIFFERENCE",
    }.issubset(options["variation_contract_ids"])
    assert {
        "SOLV-ONE-COMPLETE-WITNESS",
        "SOLV-PREFIX-RESOURCES",
        "SOLV-PREFIX-KEYS",
        "SOLV-NO-SELF-LOCK",
        "SOLV-SINGLETON-TOOLS",
        "SOLV-TOOLS-BEFORE-LAYERS",
        "SOLV-CONDITIONAL-TRIGGERS",
        "SOLV-ENVIRONMENT-STATE",
        "SOLV-FULL-CATALOG",
        "SOLV-FINAL-CHECK",
    }.issubset(options["solvability_contract_ids"])

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = skill.split("---", 2)[1]
    frontmatter_keys = {
        line.split(":", 1)[0].strip()
        for line in frontmatter.splitlines()
        if ":" in line
    }
    assert frontmatter_keys == {"name", "description"}
    assert "### Kurs mit lia-loot gamifizieren" in skill
    assert "(references/lia-loot.md)" in skill
    assert "(references/lia-loot-options.json)" in skill

    sources = json.loads(
        (ROOT / "references" / "sources.json").read_text(encoding="utf-8")
    )
    fallback = sources["organizations"][0]["fallback_repositories"]
    assert {"name": "lia-loot", "default_branch": "main"} in fallback

    corpus_sources = ROOT / "corpus" / "sources.json"
    if not corpus_sources.exists():
        return
    records = json.loads(corpus_sources.read_text(encoding="utf-8"))
    matches = [
        record
        for record in records
        if record.get("source_id") == options["source"]["source_id"]
    ]
    if not matches:
        return
    assert len(matches) == 1
    assert matches[0]["revision_sha"] == options["source"]["reviewed_revision"]

    readmes = list(
        (ROOT / "corpus" / "sources").glob(
            "ghrepo-mint-the-gap-lia-loot-*/files/README.md"
        )
    )
    assert len(readmes) == 1
    digest = hashlib.sha256(readmes[0].read_bytes()).hexdigest()
    assert digest == options["source"]["readme_sha256"]


def main() -> int:
    test_freshness_requires_matching_configuration()
    test_index_freshness_uses_content_hashes()
    test_lia_loot_reference_contract()
    print("Sync tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
