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

    assert options["schema_version"] == 3
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
        "Puzzleteil",
        "Puzzletor",
        "Lupe",
        "Schaufel",
        "Giesskanne",
        "Erdhaufen",
        "EndeErdhaufen",
        "Erdhaufen.inline",
        "Pflanze",
        "EndePflanze",
        "Pflanze.inline",
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
    assert options["macros"]["Pflanze.inline"]["aliases"] == ["Blume.inline"]
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
        "Puzzleteil",
        "Puzzletor",
        "Lupe",
        "Schaufel",
        "Giesskanne",
        "Erdhaufen",
        "EndeErdhaufen",
        "Erdhaufen.inline",
        "Pflanze",
        "Blume",
        "EndePflanze",
        "EndeBlume",
        "Pflanze.inline",
        "Blume.inline",
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
        "LootRevealInline_",
        "LootRevealEnd_",
        "LootPuzzleteil_",
        "LootPuzzletor_",
    }.issubset(options["emission_policy"]["internal_macros_forbidden"])
    assert set(options["key_colors"]) == {
        "rot", "blau", "gruen", "gelb", "lila", "orange",
        "magenta", "weiss", "schwarz", "tuerkis", "grau", "braun",
    }
    assert set(options["key_color_aliases"]) == {
        "red", "blue", "green", "yellow", "purple", "orange",
        "magenta", "white", "black", "turquoise", "gray", "brown",
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
        "pentominoquiz",
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
        "Puzzleteil",
        "Lupe",
        "Schaufel",
        "Giesskanne",
        "Erdhaufen",
        "Pflanze",
    }
    assert set(shared["does_not_apply_to"]) == {
        "Puzzletor",
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
    assert "Puzzleteil" in shared["direct_layers"]["applies_to"]

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
        "puzzle_gate",
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
        "all-puzzle-gates-opened",
        "secret-slide-found",
    }
    assert options["achievement_catalog"]["zero_total_does_not_unlock"] is True
    assert (
        options["achievement_catalog"][
            "valid_closed_lootif_ranges_count_before_spawn"
        ]
        is True
    )
    assert options["macros"]["achievements"]["fixed_achievement_count"] == 12
    assert (
        options["achievement_catalog"][
            "valid_puzzle_gates_count_and_require_exact_opening"
        ]
        is True
    )

    emission = options["emission_policy"]
    assert emission["gamification_macro_source"] == "public_lia_loot_only"
    assert emission["canonical_spellings_only"] is True
    assert emission["foreign_template_macros_for_new_gamification"] is False
    assert set(emission["internal_macros_forbidden"]).isdisjoint(
        options["public_macro_names_including_aliases"]
    )

    course_workflow = options["course_generation_workflow"]
    assert course_workflow["applies_to"] == "new_complete_course"
    base_grounding = course_workflow["grounding"]
    assert base_grounding["required_before_generation"] is True
    assert base_grounding["minimum_comparable_complete_courses"] >= 3
    assert base_grounding["use_all_when_fewer_available"] is True
    assert base_grounding["minimum_real_task_examples"] >= 3
    assert base_grounding["cover_each_central_task_family"] is True
    assert {
        "outline",
        "learning_progression",
        "task_density",
        "difficulty_progression",
        "hints",
        "feedback",
    }.issubset(base_grounding["comparison_dimensions"])
    assert {
        "documentation", "definition", "test_fixture",
    }.issubset(base_grounding["excluded_contexts"])

    staging = course_workflow["staging"]
    assert staging["base_course_first"] is True
    assert staging["base_course_must_be_pedagogically_complete"] is True
    assert staging["base_course_has_no_new_gamification"] is True
    assert staging["lia_loot_import_forbidden_in_base_course"] is True
    assert staging["lia_loot_macros_forbidden_in_base_course"] is True
    assert staging["other_new_gamification_forbidden_in_base_course"] is True
    assert (
        staging["upfront_gamification_request_does_not_skip_base_stage"]
        is True
    )
    assert staging["full_gamification_intake_before_opt_in"] is False
    assert staging["final_handoff_opt_in_question_required"] is True
    assert staging["opt_in_question_position"] == "last_sentence"
    assert staging["opt_in_question"] == (
        "Möchtest du den fertigen Kurs jetzt mit lia-loot gamifizieren?"
    )
    assert staging["run_gamification_route_only_after_yes"] is True
    assert staging["negative_answer_keeps_base_course_unchanged"] is True
    assert staging["task_snippets_do_not_trigger_opt_in"] is True
    assert (
        staging["existing_course_explicit_gamification_can_start_intake"]
        is True
    )

    intake = options["gamification_intake"]
    topics = {item["id"]: item for item in intake["topics"]}
    assert set(topics) == {
        "achievements",
        "highscore",
        "resources",
        "hidden_content",
        "buried_content",
        "plants",
        "puzzle_gates",
        "portals",
        "keys",
        "secret_slides",
        "trigger_events",
    }
    assert intake["ask_only_if_unspecified"] is True
    assert intake["ask_followups_only_for_remaining_gaps"] is True
    assert intake["design_waits_until_complete"] is True
    assert all(item["ask_quantity"] for item in topics.values())
    qualitative = intake["qualitative_quantities"]
    assert qualitative["accepted"] is True
    assert qualitative["resolve_before_design"] is True
    assert qualitative["require_exact_number_reprompt"] is False
    assert set(qualitative["fallback_by_relevant_learning_slides"]) == {
        "low", "medium", "high",
    }
    assert topics["achievements"]["cardinality"] == "disabled_or_all_fixed"
    assert (
        topics["highscore"]["cardinality"]
        == "disabled_or_single_configuration"
    )
    assert {
        "resource_types",
        "initial_amounts",
        "reward_find_counts",
        "reward_amounts",
    }.issubset(topics["resources"]["required_details"])
    assert topics["puzzle_gates"]["public_macros"] == [
        "Puzzleteil", "Puzzletor",
    ]
    assert topics["trigger_events"]["public_macros"] == [
        "lootif", "Endelootif",
    ]
    assert set(topics["trigger_events"]["user_aliases"]) == {
        "TriggerEvents", "TiggerEvents",
    }

    difficulty = intake["difficulty"]
    assert {
        "item_concealment", "resources", "highscore",
    }.issubset(difficulty)
    assert {
        "anchor",
        "delay",
        "surface_or_submenu",
        "slide_binding",
        "concealment_layers",
    }.issubset(difficulty["item_concealment"]["factors"])
    assert {
        "initial_amounts",
        "reward_amounts",
        "fixed_costs",
        "recovery_reserve",
    }.issubset(difficulty["resources"]["factors"])
    assert {
        "failed_check_penalty",
        "hint_penalty",
        "grace_minutes",
        "per_minute_penalty",
    }.issubset(difficulty["highscore"]["factors"])

    grounding = options["existing_course_grounding"]
    assert grounding["required_before_design"] is True
    assert grounding["minimum_real_course_examples"] >= 3
    assert {
        "target_project", "current_conversation", "local_corpus",
    }.issubset(grounding["sources"])
    assert {
        "documentation", "definition", "test_fixture",
    }.issubset(grounding["excluded_contexts"])

    puzzle = options["puzzle_rules"]
    assert puzzle["maximum_slots_per_gate"] == 16
    assert puzzle["maximum_gates_per_color"] == 1
    assert puzzle["all_pieces_must_precede_own_gate"] is True
    assert set(puzzle["navigation_gate_blocks"]) == {
        "next",
        "toc",
        "direct_slide_hash",
        "browser_history",
        "portal",
    }
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
        "SOLV-PUZZLE-PIECES-BEFORE-GATE",
        "SOLV-PUZZLE-MATRIX-COMPLETE",
        "SOLV-PUZZLE-NAVIGATION-BOUNDARY",
        "SOLV-NO-SELF-LOCK",
        "SOLV-SINGLETON-TOOLS",
        "SOLV-TOOLS-BEFORE-LAYERS",
        "SOLV-CONDITIONAL-TRIGGERS",
        "SOLV-ENVIRONMENT-STATE",
        "SOLV-FULL-CATALOG",
        "SOLV-FINAL-CHECK",
    }.issubset(options["solvability_contract_ids"])

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    normalized_skill = " ".join(skill.split())
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
    assert "ausschließlich die dokumentierten öffentlichen" in skill
    assert "TriggerEvents beziehungsweise TiggerEvents" in skill
    assert "Puzzletoren" in skill
    assert "Schwierigkeitsgrad für drei unabhängige Achsen" in skill
    assert "mindestens drei" in skill
    assert "jede zentrale geplante Aufgabenfamilie" in normalized_skill
    assert "ungegamifizierten Basiskurs" in normalized_skill
    assert "Gamification-Route nicht parallel" in normalized_skill
    assert (
        "als letzten Satz mit genau einer Opt-in-Frage"
        in normalized_skill
    )
    assert (
        "Möchtest du den fertigen Kurs jetzt mit lia-loot gamifizieren?"
        in normalized_skill
    )

    loot_reference = (
        ROOT / "references" / "lia-loot.md"
    ).read_text(encoding="utf-8")
    normalized_reference = " ".join(loot_reference.split())
    assert (
        "## Zweistufige Erzeugung eines neuen Kurses"
        in normalized_reference
    )
    assert "ohne vorher den vollständigen" in normalized_reference
    assert "Gamification-Klärungsdialog zu führen" in normalized_reference

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
