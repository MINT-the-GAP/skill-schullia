#!/usr/bin/env python3
"""Dependency-free unit and corpus regressions for map_course.py."""

from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MAPPER_PATH = (
    ROOT / "skills" / "schullia-gamification" / "scripts" / "map_course.py"
)
CATALOG_PATH = (
    ROOT
    / "skills"
    / "schullia-gamification"
    / "references"
    / "placement-catalog.json"
)
COURSE_ROOT = (
    ROOT
    / "corpus"
    / "sources"
    / "ghrepo-mint-the-gap-wochenaufgabe-66366d21e5"
    / "files"
)
FIXTURE_TREE_ROOT = COURSE_ROOT.parent

SPEC = importlib.util.spec_from_file_location("schullia_map_course", MAPPER_PATH)
assert SPEC and SPEC.loader
mapper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mapper)


FIXTURES: dict[str, dict[str, Any]] = {
    "D5_01": {
        "rel": "5/Deutsch/Lia5_01.md",
        "header": 41,
        "mode": 32,
        "imports": [8,9,10,11,12,13,14,15,16,17,19,21,22,24,26,27,28,29],
        "headings": [43,110,232,632,664,710,919,968,988],
        "html": ((2,0),(31,0),(0,0)),
        "reflection": 968,
    },
    "D5_02": {
        "rel": "5/Deutsch/Lia5_02.md",
        "header": 39,
        "mode": 32,
        "imports": [8,9,10,11,12,13,14,15,16,17,19,21,22,24,26,27,28,29],
        "headings": [41,100,158,333,587,623,671,840,856],
        "html": ((5,0),(34,0),(12,0)),
        "reflection": 840,
    },
    "D5_03": {
        "rel": "5/Deutsch/Lia5_03.md",
        "header": 39,
        "mode": 32,
        "imports": [7,8,9,10,11,12,13,14,15,16,18,20,21,23,25,26,27,28],
        "headings": [41,122,154,267,375,490,522,606,647,695,711],
        "html": ((1,3),(2,20),(0,6)),
        "reflection": 695,
        "fences": [(185,187),(199,201),(213,215),(227,229),(241,243),(255,257)],
        "garden": (647,689),
        "pairs": [(673,675),(677,679),(681,683),(687,689)],
    },
    "M5_01": {
        "rel": "5/Mathematik/Lia5_01.md",
        "header": 41,
        "mode": 6,
        "imports": [9,10,11,12,13,14,15,16,17,18,20,22,23,25,27,28,29,31],
        "headings": [43,123,220,376,512,618,725,823,845],
        "html": ((5,0),(16,0),(0,0)),
        "reflection": 823,
    },
    "M5_02": {
        "rel": "5/Mathematik/Lia5_02.md",
        "header": 39,
        "mode": 6,
        "imports": [10,11,12,13,14,15,16,17,18,19,20,22,24,25,27,29,30,32],
        "headings": [42,115,368,543,667,763,867,925,944],
        "html": ((3,4),(11,18),(0,0)),
        "reflection": 925,
    },
    "M5_03": {
        "rel": "5/Mathematik/Lia5_03.md",
        "header": 41,
        "mode": 6,
        "imports": [8,9,10,11,12,13,14,15,16,17,18,20,22,23,25,27,28,30,32],
        "headings": [43,141,345,439,667,895,1148,1250,1298,1319],
        "html": ((8,0),(46,0),(0,0)),
        "reflection": 1298,
        "garden": (1250,1292),
        "pairs": [(1276,1278),(1280,1282),(1284,1286),(1290,1292)],
    },
}

FIXTURES.update(
    {
        "D6_01": {
            "rel": "6/Deutsch/Lia6_01.md",
            "header": 39,
            "mode": 32,
            "imports": [8,9,10,11,12,13,14,15,16,17,19,21,22,24,26,27,28,29],
            "headings": [41,112,184,230,382,596,630,652,674],
            "html": ((2,0),(22,0),(12,0)),
            "reflection": 652,
        },
        "D6_02": {
            "rel": "6/Deutsch/Lia6_02.md",
            "header": 37,
            "mode": 30,
            "imports": [7,8,9,10,11,12,13,14,15,16,18,20,21,23,25,26,27,28],
            "headings": [39,103,287,476,569,750,917,1005,1021],
            "html": ((7,0),(52,0),(10,0)),
            "reflection": 1005,
        },
        "D6_03": {
            "rel": "6/Deutsch/Lia6_03.md",
            "header": 39,
            "mode": 32,
            "imports": [8,9,10,11,12,13,14,15,16,17,19,21,22,24,26,27,28,29],
            "headings": [41,111,233,382,559,578,761,904,950,966],
            "html": ((5,0),(48,0),(0,0)),
            "reflection": 950,
            "fences": [(582,615)],
            "garden": (904,946),
            "pairs": [(930,932),(934,936),(938,940),(944,946)],
        },
        "M6_01": {
            "rel": "6/Mathematik/Lia6_01.md",
            "header": 39,
            "mode": 6,
            "imports": [9,10,11,12,13,14,15,16,17,18,20,22,23,25,26,27,29],
            "headings": [41,125,337,561,635,763,1011,1087,1105],
            "html": ((6,0),(48,0),(0,0)),
            "reflection": 1087,
        },
        "M6_02": {
            "rel": "6/Mathematik/Lia6_02.md",
            "header": 41,
            "mode": 6,
            "imports": [9,10,11,12,13,14,15,16,17,18,20,22,23,25,27,28,29,31],
            "headings": [43,123,234,422,580,664,950,1049,1067],
            "html": ((6,0),(30,0),(0,0)),
            "reflection": 1049,
        },
        "M6_03": {
            "rel": "6/Mathematik/Lia6_03.md",
            "header": 41,
            "mode": 6,
            "imports": [9,10,11,12,13,14,15,16,17,18,20,22,23,25,27,28,29,31],
            "headings": [43,127,364,693,869,1192,1426,1622,1669,1687],
            "html": ((6,0),(43,0),(0,0)),
            "reflection": 1669,
            "garden": (1622,1664),
            "pairs": [(1648,1650),(1652,1654),(1656,1658),(1662,1664)],
        },
    }
)

CONCEALMENT_EXPECTED = {
    "D5_01": (70, 17, 0, 0),
    "D5_02": (58, 11, 0, 0),
    "D5_03": (89, 7, 10, 34),
    "M5_01": (47, 11, 0, 0),
    "M5_02": (51, 11, 0, 0),
    "M5_03": (94, 1, 10, 34),
    "D6_01": (37, 1, 0, 0),
    "D6_02": (69, 2, 0, 0),
    "D6_03": (94, 2, 10, 34),
    "M6_01": (7, 0, 0, 0),
    "M6_02": (7, 0, 0, 0),
    "M6_03": (43, 0, 10, 34),
}

GARDEN_SHA256 = "ab77a4dee31950aff71b338d29a4cfc51afdbcb1e03f269711d598a3731176de"
TARGETS = {
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
EXPECTED_CANDIDATES = (
    ("start_bootstrap", ("inline", "direct_layer", "tool_pickup"), (), None),
    ("start_post_tool_block", ("block",), ("tools_visible_before_open_marker",), None),
    ("h2_whole_slide", ("block",), (), None),
    ("h2_prefix_or_suffix", ("block",), ("top_level_balanced_boundaries",), None),
    ("dynflex_whole_section", ("block", "target_chest"), (), None),
    ("standalone_quiz", ("block", "adjacent_direct_layered_item"), (), None),
    ("solution_reward_tail", ("block", "inline", "direct_layer"), (), None),
    (
        "flow_text_clue",
        ("inline",),
        ("puzzle_gate_clue_or_secret_slide_access_clue",),
        None,
    ),
    ("local_template_target", ("target_chest", "block"), (), None),
    ("global_surface_target", ("target_chest", "native_surface_key"), (), None),
    ("lootif_spawn_range", ("block",), ("reachable_external_trigger",), None),
    (
        "container_visibility_option",
        ("container_option",),
        ("earlier_magnifier_and_text_neutral_discoverability",),
        "concealment",
    ),
    (
        "collectible_concealment_option",
        ("collectible_option",),
        ("earlier_magnifier_and_text_neutral_discoverability",),
        "concealment",
    ),
    (
        "hidden_macro_inside_reveal",
        ("nested_content",),
        ("earlier_magnifier_and_text_neutral_discoverability",),
        "concealment",
    ),
    (
        "optional_secret_or_portal",
        ("block", "inline", "adjacent_direct_layered_item"),
        ("return_path_or_explicit_one_way", "stateful_portal_graph_witness"),
        None,
    ),
    ("garden_before_reflection", ("block", "inline", "direct_layer"), (), None),
    (
        "reflection_optional",
        ("block", "inline", "direct_layer", "adjacent_direct_layered_item"),
        (),
        None,
    ),
    (
        "submission_or_freeze",
        ("block", "target_chest"),
        ("complete_mandatory_witness",),
        None,
    ),
)
CANDIDATE_IDS = frozenset(item[0] for item in EXPECTED_CANDIDATES)
GLOBAL_PROVIDER_TARGETS = {"boardmode", "marker", "annotation"}
NATIVE_TARGETS = {"toc", "menu", "classroom", "info", "translator", "mode"}


def _class_counts(result: dict[str, Any], tag: str, class_name: str) -> tuple[int, int]:
    quoted = unquoted = 0
    for item in result["html_ranges"]:
        if item["tag"] != tag or class_name not in item["classes"]:
            continue
        if item["class_style"] == "quoted":
            quoted += 1
        elif item["class_style"] == "unquoted":
            unquoted += 1
    return quoted, unquoted


def _candidate(result: dict[str, Any], identifier: str) -> dict[str, Any]:
    return next(
        item for item in result["candidates"]["classes"] if item["id"] == identifier
    )


def _target(result: dict[str, Any], identifier: str) -> dict[str, Any]:
    return next(
        item
        for item in result["provider_targets"]["targets"]
        if item["target"] == identifier
    )


def _tree_snapshot(root: Path) -> tuple[tuple[Any, ...], ...]:
    snapshot: list[tuple[Any, ...]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        stat = path.stat()
        if path.is_file():
            raw = path.read_bytes()
            snapshot.append(
                (
                    "file",
                    relative,
                    stat.st_size,
                    stat.st_mtime_ns,
                    hashlib.sha256(raw).hexdigest(),
                )
            )
        elif path.is_dir():
            snapshot.append(("directory", relative))
        else:
            snapshot.append(("other", relative, stat.st_size, stat.st_mtime_ns))
    return tuple(snapshot)


def _assert_byte_span(raw: bytes, text: str, span: dict[str, Any]) -> None:
    bom = 3 if raw.startswith(b"\xef\xbb\xbf") else 0
    expected_start = bom + len(text[: span["char_start"]].encode("utf-8"))
    expected_end = bom + len(text[: span["char_end"]].encode("utf-8"))
    assert span["byte_start"] == expected_start
    assert span["byte_end"] == expected_end


def _all_spans(value: Any):
    if isinstance(value, dict):
        if {
            "char_start",
            "char_end",
            "byte_start",
            "byte_end",
        } <= value.keys():
            yield value
        for child in value.values():
            yield from _all_spans(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _all_spans(child)


def _synthetic_course(imports: list[str], body: str) -> str:
    import_lines = "\n".join(
        f"import: https://example.test/{name}/main/README.md"
        for name in imports
    )
    return (
        "<!--\n"
        "version: 1.0.0\n"
        f"{import_lines}\n"
        "-->\n"
        "# Testkurs\n"
        f"{body}"
    )


def test_catalog_contract() -> None:
    catalog = mapper.load_catalog(CATALOG_PATH)
    assert catalog["schema_version"] == "1.1.0"
    targets = [
        target
        for provider in catalog["template_providers"]
        for target in provider["targets"]
    ]
    assert len(targets) == len(set(targets)) == 12
    assert set(targets) == TARGETS
    assert catalog["reviewed_source"]["canonical_target_count"] == 12
    assert catalog["import_policy"]["enumerate_all_n_plus_one_slots"] is True
    assert set(catalog["import_policy"]["slot_evidence_states"]) == {
        "course_observed",
        "browser_tested",
        "unproven",
    }
    root_options = json.loads(
        (ROOT / "references" / "lia-loot-options.json").read_text(
            encoding="utf-8"
        )
    )
    canonical_template_targets = {
        item["id"] for item in root_options["template_targets"]
    }
    lock_targets = catalog["environment"]["conditional_ranges"][0][
        "trigger_families"
    ]["lock_target"]["targets"]
    assert canonical_template_targets <= set(lock_targets)
    assert {"boardmode", "marker", "annotation"} <= set(lock_targets)
    assert not {
        "boardmodefontbutton", "textmarkerbutton", "annotationsbar"
    } & set(lock_targets)
    marker = next(
        item for item in catalog["template_providers"] if item["provider"] == "lia-marker"
    )
    assert marker["target_specs"]["marker"]["scope"] == "global"
    assert marker["target_specs"]["markerquiz"]["scope"] == "slide"
    coordinate = next(
        item
        for item in catalog["template_providers"]
        if item["provider"] == "lia-coordinate"
    )
    assert coordinate["hard_required_imports"] == []
    assert coordinate["observed_companion_imports"] == ["jsxgraph"]
    candidate_contract = tuple(
        (
            item["id"],
            tuple(item.get("forms", [])),
            tuple(item.get("requires", [])),
            item.get("conceptual_group"),
        )
        for item in catalog["candidate_classes"]
    )
    assert candidate_contract == EXPECTED_CANDIDATES
    assert len(candidate_contract) == 18
    content_policy = catalog["content_policy"]
    assert content_policy["existing_learner_facing_text"] == (
        "preserve_word_for_word"
    )
    assert content_policy["existing_task_order"] == "preserve_relative_order"
    assert set(content_policy["allowed_added_text_purposes"]) == {
        "puzzle_gate_clue", "secret_slide_access_clue",
    }
    assert content_policy["text_delta_outside_allowed_purposes"] == 0
    puzzle_placement = catalog["puzzle_piece_placement"]
    compatibility = puzzle_placement["candidate_compatibility"]
    assert set(compatibility) == CANDIDATE_IDS
    assert puzzle_placement["fixed_default_piece_count"] is None
    assert puzzle_placement["surface_target_allowed"] is False
    assert compatibility["global_surface_target"]["status"] == (
        "unsupported_direct_target"
    )
    assert compatibility["flow_text_clue"]["status"] == "clue_only"
    assert catalog["combination_clue_policy"]["must_derive_unique_permutation"] is True
    portal_policy = catalog["portal_route_policy"]
    assert portal_policy["public_author_macros"] == [
        "Portal", "Einwegportal", "Einbahnportal",
    ]
    assert portal_policy["portalzurueck_is_author_macro"] is False
    assert portal_policy["portal_only_requires_competing_edges_closed"] is True
    assert portal_policy["added_portal_or_key_explanatory_prose"] == "forbidden"


def test_synthetic_lexer_and_macro_tree() -> None:
    bt = chr(96)
    source = (
        "<!--\n"
        "version: 1.0.0\n"
        "mode: Presentation\n"
        "import: https://example.test/lia-loot/main/README.md\n"
        "tags: test\n"
        "import: https://example.test/lia-pentominos/main/README.md\n"
        "-->\n"
        "# Übung\n"
        f"Text Ä {bt}<!-- @Pflanze -->{bt}\n"
        "<!-- @Pflanze -->\n"
        "$$\n@Pflanze\n$$\n"
        f"{bt * 3}text @LLMQuiz(1; solution=1)\n"
        "## falsche Überschrift\n"
        "@Erdhaufen\n"
        f"{bt * 3}\n"
        "## Aufgabe\n"
        "<section class=dynFlex>\n"
        '<div class="flex-child">\n'
        "@Erdhaufen.inline(@Puzzleteil(tuerkis; 1))\n"
        "</div>\n"
        "</section>\n"
        "@Erdhaufen\n"
        "@Pflanze\n"
        "@Schatztruhe(1; blume-verdeckt; soil-dust)\n"
        "@EndePflanze\n"
        "@EndeErdhaufen\n"
        "@Puzzletor(tuerkis; [[3;1];[4;2]]; anker)\n"
    )
    result = mapper.map_text(source, source_path="synthetic.md")
    assert [item["span"]["line_start"] for item in result["imports"]] == [4, 6]
    assert result["imports"][0]["relative_to_loot"] == "self"
    assert result["imports"][1]["relative_to_loot"] == "after"
    assert len(result["import_slots"]) == len(result["imports"]) + 1
    assert [item["span"]["line_start"] for item in result["headings"]] == [8, 18]
    assert [(item["open_line"], item["close_line"]) for item in result["protected_spans"] if item["kind"] == "fence"] == [(14, 17)]
    assert len([item for item in result["protected_spans"] if item["kind"] == "html_comment"]) == 1
    names = [item["name"] for item in result["macros"]]
    assert names.count("Pflanze") == 1
    decorator = next(
        item for item in result["macros"] if item["name"] == "LLMQuiz"
    )
    assert decorator["usage_context"] == "fence_decorator"
    assert decorator["inside_fence"] is True
    outer = next(item for item in result["macros"] if item["name"] == "Erdhaufen.inline")
    child = next(item for item in result["macros"] if item["name"] == "Puzzleteil")
    assert child["parent_id"] == outer["id"]
    assert outer["span"]["byte_start"] > outer["span"]["char_start"]
    raw = source[outer["span"]["char_start"]:outer["span"]["char_end"]]
    assert raw == outer["span"]["raw"]
    assert len(result["environment"]["block_pairs"]) == 2
    assert all(item["valid"] for item in result["environment"]["block_pairs"])
    layers = result["environment"]["direct_layers"]
    assert [item["canonical_token"] for item in layers] == [
        "pflanze-unsichtbar",
        "erde-zauberstaub",
    ]
    gate = next(item for item in result["macros"] if item["name"] == "Puzzletor")
    assert gate["arguments"] == ["tuerkis", "[[3;1];[4;2]]", "anker"]
    assert _class_counts(result, "section", "dynFlex") == (0, 1)
    assert _class_counts(result, "div", "flex-child") == (1, 0)


def test_every_import_rank_and_n_plus_one_slots() -> None:
    other_imports = [
        "https://example.test/lia-DynFlex/main/README.md",
        "https://example.test/lia-navigation/main/README.md",
        "https://example.test/lia-freeze-v2/main/README.md",
    ]
    loot = "https://example.test/lia-loot/main/README.md"
    for rank in range(len(other_imports) + 1):
        values = list(other_imports)
        values.insert(rank, loot)
        header = "\n".join(f"import: {value}" for value in values)
        result = mapper.map_text(
            f"<!--\nversion: 1.0.0\n{header}\n-->\n# Kurs\n"
        )
        assert result["header"]["loot_import_orders"] == [rank]
        imports = result["imports"]
        slots = result["import_slots"]
        assert len(slots) == len(values) + 1
        assert [item["slot_index"] for item in slots] == list(
            range(len(values) + 1)
        )
        assert [item["rank"] for item in slots] == list(
            range(len(values) + 1)
        )
        assert [item["position_kind"] for item in slots] == [
            "before_first",
            *(["between"] * (len(values) - 1)),
            "after_last",
        ]
        for slot_index, slot in enumerate(slots):
            previous = slot["adjacent_imports"]["previous"]
            following = slot["adjacent_imports"]["next"]
            assert slot["after_import_order"] == (
                slot_index - 1 if slot_index else None
            )
            assert slot["before_import_order"] == (
                slot_index if slot_index < len(values) else None
            )
            assert previous is None or previous["order"] == slot_index - 1
            assert following is None or following["order"] == slot_index
            assert slot["span"]["char_start"] == slot["span"]["char_end"]
            if slot_index < len(imports):
                assert (
                    slot["span"]["char_start"]
                    == imports[slot_index]["span"]["char_start"]
                )
            else:
                assert (
                    slot["span"]["char_start"]
                    > imports[-1]["span"]["char_end"]
                )
            for evidence in slot["loot_order_evidence"]:
                assert evidence["evidence_status"] in {
                    "course_observed",
                    "browser_tested",
                    "unproven",
                }
                assert evidence["provider"]
        assert slots[rank]["compatibility_status"] == "course_observed"
        assert slots[rank]["loot_order_evidence"] == [
            {
                "import_order": rank,
                "provider": "lia-loot",
                "observed_relation": "self",
                "proposed_relation": "observed_slot",
                "evidence_status": "course_observed",
            }
        ]
        for slot in slots:
            if slot["slot_index"] == rank:
                continue
            expected_crossed = slot[
                "crossed_providers_from_observed_loot_position"
            ]
            assert [
                item["provider"] for item in slot["loot_order_evidence"]
            ] == expected_crossed
            assert slot["compatibility_status"] == (
                "browser_tested"
                if expected_crossed
                and set(expected_crossed) <= {
                    "lia-navigation",
                    "lia-freeze-v2",
                }
                else "unproven"
            )

    gapped_source = (
        "<!--\n"
        "version: 1.0.0\n"
        "import: https://example.test/lia-DynFlex/main/README.md\n"
        "author: Test\n"
        "import: https://example.test/lia-loot/main/README.md\n"
        "mode: Presentation\n"
        "import: https://example.test/lia-freeze-v2/main/README.md\n"
        "-->\n"
        "# Kurs\n"
    )
    result = mapper.map_text(gapped_source, source_path="gapped-header.md")
    imports = result["imports"]
    slots = result["import_slots"]
    assert [item["span"]["line_start"] for item in imports] == [3, 5, 7]
    assert [item["slot_index"] for item in slots] == [0, 1, 2, 3]
    assert [item["position_kind"] for item in slots] == [
        "before_first",
        "between",
        "between",
        "after_last",
    ]
    assert [item["insertion_line"] for item in slots] == [3, 5, 7, 8]
    assert [item["span"]["column_start"] for item in slots] == [1, 1, 1, 1]
    assert [item["span"]["char_start"] for item in slots] == [
        imports[0]["span"]["char_start"],
        imports[1]["span"]["char_start"],
        imports[2]["span"]["char_start"],
        gapped_source.index("-->"),
    ]
    assert [
        (
            item["after_import_order"],
            item["before_import_order"],
        )
        for item in slots
    ] == [(None, 0), (0, 1), (1, 2), (2, None)]
    assert [
        (
            item["adjacent_imports"]["previous"]["order"]
            if item["adjacent_imports"]["previous"]
            else None,
            item["adjacent_imports"]["next"]["order"]
            if item["adjacent_imports"]["next"]
            else None,
        )
        for item in slots
    ] == [(None, 0), (0, 1), (1, 2), (2, None)]
    assert slots[0]["loot_order_evidence"] == [
        {
            "import_order": 0,
            "provider": "lia-DynFlex",
            "observed_relation": "before_loot",
            "proposed_relation": "after_loot",
            "evidence_status": "unproven",
        }
    ]
    assert slots[1]["loot_order_evidence"][0]["evidence_status"] == (
        "course_observed"
    )
    assert slots[2]["loot_order_evidence"] == []
    assert slots[3]["loot_order_evidence"] == [
        {
            "import_order": 2,
            "provider": "lia-freeze-v2",
            "observed_relation": "after_loot",
            "proposed_relation": "before_loot",
            "evidence_status": "browser_tested",
        }
    ]


def test_provider_semantics_and_candidate_contracts() -> None:
    imports = [
        "lia-DynFlex",
        "lia-timer",
        "lia-board-mode",
        "lia-marker",
        "lia-annotation",
        "lia-canvas-ocr",
        "lia-kachel",
        "lia-mathpath",
        "lia-llm",
        "lia-coordinate",
        "lia-freeze-v2",
        "lia-loot",
    ]
    source = _synthetic_course(
        imports,
        (
            "## Station\n"
            '<section class="dynFlex">\n'
            "DynFlex-Inhalt\n"
            "</section>\n\n"
            '<!-- data-solution-timer="30s" '
            'data-solution-timer-start="onclick" -->\n'
            "[[Antwort]]\n"
            "[[?]] @Explain\n\n"
            "<div class=markerquiz>\n"
            "@TextmarkerQuiz\n"
            "</div>\n\n"
            "@canvas\n"
            "@Kachelfolge(`[->[(A)|B]]`)\n"
            "@LLMQuiz(1; solution=1)\n"
            "@CoordinateSystem(id=test)\n"
            "@Abgabe\n"
            "@Auswertung(F12;Tab;Time)\n\n"
            "***\n"
            "Lösung\n"
            "***\n"
        ),
    )
    result = mapper.map_text(source, source_path="all-targets.md")
    targets = {
        item["target"]: item
        for item in result["provider_targets"]["targets"]
    }
    assert set(targets) == TARGETS
    assert {
        target for target, item in targets.items() if item["scope"] == "global"
    } == GLOBAL_PROVIDER_TARGETS
    for target, item in targets.items():
        assert item["direct_import"] is True
        assert item["block_policy"]
        assert item["required_state"]
        assert item["eligible"] is True, (target, item)
        assert item["state_status"] == "runtime_required"
        if target in GLOBAL_PROVIDER_TARGETS:
            assert item["instances"] == []
            assert item["source_contract_status"] == "proven"
            continue
        assert item["source_contract_status"] == "proven"
        assert item["instances"], target
        for instance in item["instances"]:
            assert instance["kind"] != "text"
            assert instance["block_complete"] is True
            assert (
                instance["block_span"]["char_start"]
                < instance["block_span"]["char_end"]
            )
            assert instance["block_policy"] == item["block_policy"]

    timer = targets["timer"]
    assert timer["purpose_states"]["chest"]["eligible"] is True
    assert timer["purpose_states"]["lock"]["eligible"] is True
    assert (
        timer["purpose_states"]["lock"]["state_status"]
        == "runtime_required"
    )
    freeze = targets["freeze"]
    assert freeze["purpose_states"]["chest"]["eligible"] is True
    assert freeze["purpose_states"]["lock"]["eligible"] is True

    native = result["provider_targets"]["native_targets"]
    assert {item["target"] for item in native} == NATIVE_TARGETS
    assert all(item["eligible"] for item in native)
    assert all(item["state_status"] == "runtime_required" for item in native)

    classes = {
        item["id"]: item for item in result["candidates"]["classes"]
    }
    assert set(classes) == CANDIDATE_IDS
    candidate_contract = tuple(
        (
            item["id"],
            tuple(item["forms"]),
            tuple(item["requires"]),
            item["conceptual_group"],
        )
        for item in result["candidates"]["classes"]
    )
    assert candidate_contract == EXPECTED_CANDIDATES

    local_anchors = classes["local_template_target"]["anchors"]
    assert local_anchors
    assert {
        item["evidence"]["target"] for item in local_anchors
    } == TARGETS - GLOBAL_PROVIDER_TARGETS
    for anchor in local_anchors:
        evidence = anchor["evidence"]
        assert evidence["target_eligible"] is True
        assert evidence["block_policy"]
        assert evidence["state_status"] == "runtime_required"
        assert "close_anchor" in anchor
        assert (
            anchor["anchor"]["char_start"]
            < anchor["close_anchor"]["char_start"]
        )
        target = targets[evidence["target"]]
        assert any(
            anchor["anchor"]["char_start"]
            == instance["block_span"]["char_start"]
            and anchor["close_anchor"]["char_start"]
            == instance["block_span"]["char_end"]
            for instance in target["instances"]
        )

    global_anchors = classes["global_surface_target"]["anchors"]
    assert {
        item["evidence"]["target"]
        for item in global_anchors
        if item["evidence"]["provider"] == "native-liascript"
    } == NATIVE_TARGETS
    assert {
        item["evidence"]["target"]
        for item in global_anchors
        if item["evidence"]["provider"] != "native-liascript"
    } == GLOBAL_PROVIDER_TARGETS
    first_surface = result["headings"][0]["line_end_with_eol"]
    assert all(
        item["role"] in {
            "global_target_declaration",
            "native_global_target_declaration",
        }
        and item["anchor"]["char_start"] == first_surface
        and item["anchor"]["char_end"] == first_surface
        and item["evidence"]["target_eligible"] is True
        and item["evidence"]["state_status"] == "runtime_required"
        and item["valid_block_boundary"] is True
        for item in global_anchors
    )

    native_quizzes = result["block_ranges"]["native_quiz"]
    assert native_quizzes
    assert any(
        item["evidence"].get("instance_kind") == "native_quiz"
        for item in classes["standalone_quiz"]["anchors"]
    )
    native_quiz_anchor = next(
        item
        for item in classes["standalone_quiz"]["anchors"]
        if item["evidence"].get("instance_kind") == "native_quiz"
    )
    native_quiz = native_quizzes[native_quiz_anchor["evidence"]["quiz_id"]]
    assert (
        native_quiz_anchor["anchor"]["char_start"]
        == native_quiz["span"]["char_start"]
    )
    assert native_quiz_anchor["context"]["inside_table_or_quiz"] is False
    assert native_quiz_anchor["valid_block_boundary"] is True
    feedback = result["block_ranges"]["feedback"][0]
    tail = classes["solution_reward_tail"]["anchors"][0]
    assert tail["anchor"]["char_start"] == feedback["close_span"]["char_start"]
    assert tail["role"] == "before_feedback_close"
    assert tail["specialized_boundary"] == "solution_tail_inside_feedback"
    assert tail["context"]["feedback_depth"] == 1
    assert "inside_feedback" not in tail["exclusion_reasons"]
    assert tail["valid_block_boundary"] is True

    dynflex = next(
        item
        for item in result["html_ranges"]
        if "dynFlex" in item["classes"]
    )
    assert dynflex["close_span"]["char_start"] not in {
        item["anchor"]["char_start"]
        for item in result["candidates"]["safe_block_boundaries"]
    }


def test_provider_false_positives_fail_closed() -> None:
    imports = [
        "lia-DynFlex",
        "lia-timer",
        "lia-marker",
        "lia-canvas-ocr",
        "lia-kachel",
        "lia-mathpath",
        "lia-llm",
        "lia-coordinate",
        "lia-freeze-v2",
        "lia-loot",
    ]
    source = _synthetic_course(
        imports,
        (
            "## Nur Wörter\n"
            "dynflex timer markerquiz canvas Kachel LLMQuiz "
            "CoordinateSystem Abgabe\n"
            "@Schloss(dynflex; rot)\n"
            "> <h2> @Explain(Tutorial) </h2>\n"
        ),
    )
    result = mapper.map_text(source, source_path="false-positives.md")
    for target in TARGETS - GLOBAL_PROVIDER_TARGETS:
        item = _target(result, target)
        assert item["instances"] == [], target
        assert item["source_contract_status"] == "disproven"
        assert item["state_status"] == "disproven"
        assert item["eligible"] is False
    assert _candidate(result, "local_template_target")["anchors"] == []

    exact_kachel = mapper.map_text(
        _synthetic_course(
            ["lia-kachel", "lia-loot"],
            (
                "## Exakte Syntax\n"
                "Das Wort Kachel steht nur in Prosa.\n"
                "@Schloss(kachel; rot)\n"
                "@Kachelfolge(`[->[(A)|B]]`)\n"
            ),
        ),
        source_path="exact-kachel.md",
    )
    target = _target(exact_kachel, "kachel")
    assert len(target["instances"]) == 1
    instance = target["instances"][0]
    assert instance["macro_name"] == "Kachelfolge"
    assert instance["kind"] == "macro"
    anchors = [
        item
        for item in _candidate(exact_kachel, "local_template_target")[
            "anchors"
        ]
        if item["evidence"]["target"] == "kachel"
    ]
    assert len(anchors) == 1
    assert anchors[0]["anchor"]["char_start"] == instance["block_span"][
        "char_start"
    ]
    assert anchors[0]["close_anchor"]["char_start"] == instance[
        "block_span"
    ]["char_end"]


def test_invalid_environment_and_lootif_ranges() -> None:
    catalog = mapper.load_catalog(CATALOG_PATH)
    conditional = catalog["environment"]["conditional_ranges"][0]
    assert conditional["kind"] == "lootif"
    assert conditional["open"] == ["lootif"]
    assert conditional["close"] == [
        "Endelootif", "EndeLootif", "endlootif", "EndLootIf"
    ]
    assert conditional["required_action"] == "spawn"
    assert conditional["trigger_argument_index"] == 0
    assert conditional["action_argument_index"] == 1
    assert conditional["evidence_scope"] == "course_outside_own_range"
    assert conditional["proof_basis"] == "source"
    assert set(conditional["trigger_families"]) == {
        "previous_quiz", "current_slide_quizzes", "solved_quizzes",
        "resources", "opened_chests", "lock_target", "puzzle_gate",
        "secret_slide", "magnifier", "marker",
    }

    invalid_sources = {
        "missing": "## A\n@Erdhaufen\nInhalt\n",
        "wrong_end": "## A\n@Erdhaufen\n@EndePflanze\n",
        "crossed": (
            "## A\n@Erdhaufen\n@Pflanze\n"
            "@EndeErdhaufen\n@EndePflanze\n"
        ),
        "slide": "## A\n@Erdhaufen\n## B\n@EndeErdhaufen\n",
        "html": (
            "## A\n<section class=dynFlex>\n"
            "@Erdhaufen\nInhalt\n@EndeErdhaufen\n</section>\n"
        ),
        "list": "## A\n- @Erdhaufen\n  Inhalt\n- @EndeErdhaufen\n",
        "blockquote": (
            "## A\n> @Pflanze\n> Inhalt\n> @EndePflanze\n"
        ),
        "html_siblings": (
            "## A\n"
            "<section class=dynFlex>\n"
            "@Erdhaufen\nA\n@EndeErdhaufen\n"
            "</section>\n"
            '<div class="flex-child">\n'
            "@Pflanze\nB\n@EndePflanze\n"
            "</div>\n"
            "<div class=markerquiz>\n"
            "@Erdhaufen\nC\n@EndeErdhaufen\n"
            "</div>\n"
        ),
    }
    for identifier, body in invalid_sources.items():
        result = mapper.map_text(
            _synthetic_course(["lia-loot"], body),
            source_path=f"invalid-{identifier}.md",
        )
        assert not any(
            item["valid"] for item in result["environment"]["block_pairs"]
        ), identifier
        assert any(
            item["code"].startswith("environment_")
            for item in result["diagnostics"]
        ), identifier
        if identifier in {
            "crossed",
            "slide",
            "html",
            "list",
            "blockquote",
            "html_siblings",
        }:
            assert result["environment"]["block_pairs"], identifier
    nested_html = mapper.map_text(
        _synthetic_course(["lia-loot"], invalid_sources["html_siblings"])
    )
    assert len(nested_html["environment"]["block_pairs"]) == 3
    assert all(
        "marker_inside_html" in item["exclusion_reasons"]
        for item in nested_html["environment"]["block_pairs"]
    )
    quoted = mapper.map_text(
        _synthetic_course(["lia-loot"], invalid_sources["blockquote"])
    )
    assert len(quoted["environment"]["block_pairs"]) == 1
    assert "marker_in_blockquote" in quoted["environment"][
        "block_pairs"
    ][0]["exclusion_reasons"]

    valid_lootif = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## A\n"
                "@Lupe\n"
                "@lootif(Lupe gefunden; spawn)\n"
                "@Schatztruhe\n"
                "@EndLootIf\n"
            ),
        )
    )
    ranges = valid_lootif["block_ranges"]["lootif"]
    assert len(ranges) == 1
    assert ranges[0]["valid"] is True
    assert ranges[0]["external_trigger_status"] == "proven"
    lootif_anchors = _candidate(valid_lootif, "lootif_spawn_range")["anchors"]
    assert len(lootif_anchors) == 1
    assert (
        lootif_anchors[0]["anchor"]["char_start"]
        == ranges[0]["span"]["char_start"]
    )
    assert (
        lootif_anchors[0]["close_anchor"]["char_start"]
        == ranges[0]["span"]["char_end"]
    )

    invalid_lootif = {
        "missing_close": (
            "## A\n@Lupe\n@lootif(Lupe gefunden; spawn)\nInhalt\n"
        ),
        "wrong_action": (
            "## A\n@Lupe\n@lootif(Lupe gefunden; show)\n@Endelootif\n"
        ),
        "self_trigger": (
            "## A\n@lootif(Lupe gefunden; spawn)\n@Lupe\n@Endelootif\n"
        ),
        "cross_slide": (
            "## A\n@Lupe\n@lootif(Lupe gefunden; spawn)\n"
            "## B\n@Endelootif\n"
        ),
        "list": (
            "## A\n@Lupe\n- @lootif(Lupe gefunden; spawn)\n"
            "  Inhalt\n- @Endelootif\n"
        ),
        "blockquote": (
            "## A\n@Lupe\n> @lootif(Lupe gefunden; spawn)\n"
            "> Inhalt\n> @Endelootif\n"
        ),
        "html": (
            "## A\n@Lupe\n<div>\n@lootif(Lupe gefunden; spawn)\n"
            "Inhalt\n@Endelootif\n</div>\n"
        ),
        "not_standalone": (
            "## A\n@Lupe\nText @lootif(Lupe gefunden; spawn)\n"
            "Inhalt\nText @Endelootif\n"
        ),
        "empty_trigger": (
            "## A\n@Lupe\n@lootif(; spawn)\n@Endelootif\n"
        ),
        "one_field": (
            "## A\n@Lupe\n@lootif(Lupe gefunden)\n@Endelootif\n"
        ),
        "three_fields": (
            "## A\n@Lupe\n@lootif(Lupe gefunden; spawn; extra)\n"
            "@Endelootif\n"
        ),
        "comma_fields": (
            "## A\n@Lupe\n@lootif(Lupe gefunden, spawn)\n"
            "@Endelootif\n"
        ),
    }
    for identifier, body in invalid_lootif.items():
        result = mapper.map_text(
            _synthetic_course(["lia-loot"], body),
            source_path=f"invalid-lootif-{identifier}.md",
        )
        assert _candidate(result, "lootif_spawn_range")["anchors"] == []
        assert not any(
            item["valid"] for item in result["block_ranges"]["lootif"]
        )


def test_fence_negative_cases() -> None:
    bt = chr(96)
    source = (
        "<!--\n"
        "version: 1.0.0\n"
        "-->\n"
        "# Kurs\n"
        f"{bt * 3}\n"
        "@Pflanze\n"
        f"    {bt * 3}\n"
        "## keine Folie\n"
        "@EndePflanze\n"
        f"{bt * 3}\n"
        "## echte Folie\n"
    )
    result = mapper.map_text(source, source_path="fence-indent.md")
    assert [
        (item["open_line"], item["close_line"])
        for item in result["protected_spans"]
        if item["kind"] == "fence"
    ] == [(5, 10)]
    assert [item["span"]["line_start"] for item in result["headings"]] == [
        4,
        11,
    ]
    assert result["macros"] == []
    assert not any(
        item["code"] == "unterminated_fence"
        for item in result["diagnostics"]
    )

    invalid_info = (
        "<!--\n"
        "version: 1.0.0\n"
        "-->\n"
        "# Kurs\n"
        f"{bt * 3} bad{bt}info\n"
        "@Pflanze\n"
    )
    result = mapper.map_text(invalid_info, source_path="fence-info.md")
    assert not any(
        item["kind"] == "fence" for item in result["protected_spans"]
    )
    assert [item["name"] for item in result["macros"]] == ["Pflanze"]

    tabbed = (
        "<!--\nversion: 1.0.0\n-->\n# Kurs\n"
        f"\t{bt * 3}text\n"
        "@Pflanze\n"
        f"\t{bt * 3}\n"
        "    @Erdhaufen\n"
        "## Folie\n"
    )
    result = mapper.map_text(tabbed, source_path="fence-tab.md")
    assert not any(
        item["kind"] == "fence" for item in result["protected_spans"]
    )
    assert [item["name"] for item in result["macros"]] == [
        "Pflanze",
        "Erdhaufen",
    ]
    indented = [
        item for item in result["protected_spans"]
        if item["kind"] == "indented_code"
    ]
    assert {
        (item["span"]["line_start"], item["span"]["line_end"])
        for item in indented
    } == {(5, 6)}

    unclosed_fence_containers = {
        "list": (
            f"- item\n  {bt * 3}\n  @LLMQuiz(700)\n"
            "  [[hidden list fence]]\n"
            "Outside @LLMQuiz(701)\n[[visible 701]]\n",
            "Outside ",
        ),
        "quote": (
            f"> {bt * 3}\n> @LLMQuiz(702)\n"
            "> [[hidden quote fence]]\n"
            "Outside @LLMQuiz(703)\n[[visible 703]]\n",
            "Outside ",
        ),
        "quote-list": (
            f"> - item\n>\n>   {bt * 3}\n"
            ">   @LLMQuiz(704)\n"
            ">   [[hidden quote list fence]]\n"
            "> Outside @LLMQuiz(705)\n> [[visible 705]]\n",
            "> Outside ",
        ),
        "list-quote": (
            f"- > {bt * 3}\n  > @LLMQuiz(706)\n"
            "  > [[hidden list quote fence]]\n"
            "  Outside @LLMQuiz(707)\n  [[visible 707]]\n",
            "  Outside ",
        ),
        "nested-list": (
            f"- outer\n  - inner\n    {bt * 3}\n"
            "    @LLMQuiz(708)\n"
            "    [[hidden nested list fence]]\n"
            "  Outside @LLMQuiz(709)\n  [[visible 709]]\n",
            "  Outside ",
        ),
        "list-blank": (
            f"- item\n  {bt * 3}\n\n"
            "  @LLMQuiz(710)\n  [[hidden after blank fence]]\n"
            "Outside @LLMQuiz(711)\n[[visible 711]]\n",
            "Outside ",
        ),
    }
    for label, (body, outside_marker) in unclosed_fence_containers.items():
        course = _synthetic_course(["lia-llm", "lia-loot"], "## A\n" + body)
        result = mapper.map_text(
            course,
            source_path=f"unclosed-fence-container-{label}.md",
        )
        fences = [
            item
            for item in result["protected_spans"]
            if item["kind"] == "fence"
        ]
        assert len(fences) == 1, label
        assert fences[0]["closed"] is False, label
        assert fences[0]["close_line"] is None, label
        assert fences[0]["span"]["char_end"] == course.index(
            outside_marker, fences[0]["span"]["char_start"]
        ), label
        assert len(
            [
                item
                for item in result["macros"]
                if item["name"] == "LLMQuiz"
            ]
        ) == 1, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert any(
            item["code"] == "unterminated_fence"
            for item in result["diagnostics"]
        ), label

    root_unclosed_fence = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\n{bt * 3}\n@LLMQuiz(712)\n"
                "[[hidden root fence]]\n"
                "Outside @LLMQuiz(713)\n[[still hidden root fence]]\n"
            ),
        ),
        source_path="unclosed-root-fence.md",
    )
    root_fence = next(
        item
        for item in root_unclosed_fence["protected_spans"]
        if item["kind"] == "fence"
    )
    assert root_fence["closed"] is False
    assert root_fence["span"]["char_end"] == root_unclosed_fence[
        "source"
    ]["character_count"]
    assert root_unclosed_fence["macros"] == []
    assert root_unclosed_fence["block_ranges"]["native_quiz"] == []

    for index, fake_line in enumerate(
        ("<script>", "<?fake", "<![CDATA[", "- fake", "> - fake")
    ):
        course = _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\n- item\n  {bt * 3}\n"
                f"  {fake_line}\n  {bt * 3}\n"
                "  - nested\n\n    <?course\n"
                f"    @LLMQuiz({720 + index * 3})\n"
                f"  Outside @LLMQuiz({721 + index * 3})\n"
                "  [[visible outer after fake fence marker]]\n"
                f"Outside root @LLMQuiz({722 + index * 3})\n"
                "[[visible root after fake fence marker]]\n"
            ),
        )
        result = mapper.map_text(
            course,
            source_path=f"fence-fake-container-marker-{index}.md",
        )
        fences = [
            item
            for item in result["protected_spans"]
            if item["kind"] == "fence"
        ]
        assert len(fences) == 1 and fences[0]["closed"] is True, fake_line
        pi = next(
            item
            for item in result["protected_spans"]
            if item["kind"] == "html_processing_instruction"
        )
        assert pi["closed"] is False, fake_line
        assert pi["span"]["char_end"] == course.index(
            "  Outside ", pi["span"]["char_start"]
        ), fake_line
        assert len(
            [
                item
                for item in result["macros"]
                if item["name"] == "LLMQuiz"
            ]
        ) == 2, fake_line
        assert len(result["block_ranges"]["native_quiz"]) == 2, fake_line

    html_families = [
        ("raw_html", "<script>", "</script>", "type-one"),
        (
            "html_processing_instruction",
            "<?outer",
            "?>",
            "processing-instruction",
        ),
        ("html_comment", "<!-- open", "-->", "comment"),
        ("html_cdata", "<![CDATA[", "]]>", "cdata"),
        ("html_declaration", "<!DOCTYPE", ">", "declaration"),
    ]
    for index, (html_kind, opener, closer, label) in enumerate(html_families):
        hidden_number = 750 + index * 2
        visible_number = hidden_number + 1
        course = _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\n{opener}\n{bt * 3}\n"
                f"@LLMQuiz({hidden_number})\n{closer}\n"
                f"@LLMQuiz({visible_number})\n"
                f"[[visible after HTML-owned fake fence {label}]]\n"
            ),
        )
        result = mapper.map_text(
            course,
            source_path=f"html-owned-fake-fence-{label}.md",
        )
        assert not any(
            item["kind"] == "fence" for item in result["protected_spans"]
        ), label
        html = next(
            item
            for item in result["protected_spans"]
            if item["kind"] == html_kind
        )
        assert html["closed"] is True, label
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({visible_number})"}, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert not any(
            item["code"] == "unterminated_fence"
            for item in result["diagnostics"]
        ), label

        unclosed_course = _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\n{opener}\n{bt * 3}\n"
                f"@LLMQuiz({780 + index})\n"
                f"[[hidden in unclosed HTML-owned fake fence {label}]]\n"
            ),
        )
        unclosed = mapper.map_text(
            unclosed_course,
            source_path=f"unclosed-html-owned-fake-fence-{label}.md",
        )
        assert not any(
            item["kind"] == "fence"
            for item in unclosed["protected_spans"]
        ), label
        html = next(
            item
            for item in unclosed["protected_spans"]
            if item["kind"] == html_kind
        )
        assert html["closed"] is False, label
        assert html["span"]["char_end"] == len(unclosed_course), label
        assert unclosed["macros"] == [], label
        assert unclosed["block_ranges"]["native_quiz"] == [], label

    real_after_fake = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            f"## A\n<script>\n{bt * 3}\n</script>\n"
            f"{bt * 3}\n@LLMQuiz(790)\n{bt * 3}\n"
            "@LLMQuiz(791)\n[[visible after real later fence]]\n"
        ),
    )
    real_after = mapper.map_text(
        real_after_fake,
        source_path="real-fence-after-html-owned-fake.md",
    )
    assert [
        item["kind"]
        for item in real_after["protected_spans"]
        if item["kind"] in {"raw_html", "fence"}
    ] == ["raw_html", "fence"]
    assert {
        item["span"]["raw"]
        for item in real_after["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(791)"}
    assert len(real_after["block_ranges"]["native_quiz"]) == 1

    for index, (html_kind, opener, closer, label) in enumerate(html_families):
        code_first = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    f"## A\n    {opener}\n"
                    f"    @LLMQuiz({800 + index})\n"
                    f"    {closer}\n"
                    f"@LLMQuiz({810 + index})\n"
                    f"[[visible after indented-code-owned {label}]]\n"
                ),
            ),
            source_path=f"indented-code-owned-fake-html-{label}.md",
        )
        assert len(
            [
                item
                for item in code_first["protected_spans"]
                if item["kind"] == "indented_code"
            ]
        ) == 1, label
        assert not any(
            item["kind"] == html_kind
            for item in code_first["protected_spans"]
        ), label
        assert len(
            [
                item
                for item in code_first["macros"]
                if item["name"] == "LLMQuiz"
            ]
        ) == 1, label
        assert len(code_first["block_ranges"]["native_quiz"]) == 1, label

    owner_direction_cases = {
        "math-before-fence": (
            "$$\n"
            f"{bt * 3}\n@LLMQuiz(820)\n"
            "$$\n@LLMQuiz(821)\n[[visible 821]]\n",
            "display_math",
        ),
        "fence-before-math": (
            f"{bt * 3}\n$$\n@LLMQuiz(822)\n"
            f"{bt * 3}\n@LLMQuiz(823)\n[[visible 823]]\n",
            "fence",
        ),
        "html-before-math": (
            "<script>\n$$\n@LLMQuiz(824)\n</script>\n"
            "@LLMQuiz(825)\n[[visible 825]]\n",
            "raw_html",
        ),
        "math-before-html": (
            "$$\n<script>\n@LLMQuiz(826)\n$$\n"
            "@LLMQuiz(827)\n[[visible 827]]\n",
            "display_math",
        ),
    }
    for label, (body, owner_kind) in owner_direction_cases.items():
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"], "## A\n" + body
            ),
            source_path=f"owner-direction-{label}.md",
        )
        owners = [
            item
            for item in result["protected_spans"]
            if item["kind"] in {"display_math", "fence", "raw_html"}
        ]
        assert len(owners) == 1, label
        assert owners[0]["kind"] == owner_kind, label
        assert owners[0]["closed"] is True, label
        assert len(
            [
                item
                for item in result["macros"]
                if item["name"] == "LLMQuiz"
            ]
        ) == 1, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label

    unclosed_math_owner = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n$$\n"
                f"{bt * 3}\n@LLMQuiz(830)\n"
                "[[hidden unclosed math-owned fake fence]]\n"
            ),
        ),
        source_path="unclosed-math-owned-fake-fence.md",
    )
    math_owner = next(
        item
        for item in unclosed_math_owner["protected_spans"]
        if item["kind"] == "display_math"
    )
    assert math_owner["closed"] is False
    assert math_owner["span"]["char_end"] == unclosed_math_owner[
        "source"
    ]["character_count"]
    assert not any(
        item["kind"] == "fence"
        for item in unclosed_math_owner["protected_spans"]
    )
    assert unclosed_math_owner["macros"] == []
    assert unclosed_math_owner["block_ranges"]["native_quiz"] == []
    assert any(
        item["code"] == "unterminated_display_math"
        for item in unclosed_math_owner["diagnostics"]
    )
    assert not any(
        item["code"] == "unterminated_fence"
        for item in unclosed_math_owner["diagnostics"]
    )

    math_before_indented = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n$$\n\n    @LLMQuiz(831)\n"
                "    [[hidden blank math indented]]\n$$\n"
                "@LLMQuiz(832)\n[[visible 832]]\n"
            ),
        ),
        source_path="math-owned-fake-indented.md",
    )
    assert len(
        [
            item
            for item in math_before_indented["protected_spans"]
            if item["kind"] == "display_math"
        ]
    ) == 1
    assert not any(
        item["kind"] == "indented_code"
        for item in math_before_indented["protected_spans"]
    )
    assert len(
        [
            item
            for item in math_before_indented["macros"]
            if item["name"] == "LLMQuiz"
        ]
    ) == 1

    math_before_inline_code = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\n$$\n{bt}@LLMQuiz(835){bt}\n$$\n"
                "@LLMQuiz(836)\n[[visible 836]]\n"
            ),
        ),
        source_path="math-owned-fake-inline-code.md",
    )
    assert len(
        [
            item
            for item in math_before_inline_code["protected_spans"]
            if item["kind"] == "display_math"
        ]
    ) == 1
    assert not any(
        item["kind"] == "inline_code"
        for item in math_before_inline_code["protected_spans"]
    )
    assert len(
        [
            item
            for item in math_before_inline_code["macros"]
            if item["name"] == "LLMQuiz"
        ]
    ) == 1

    indented_before_math = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n    $$\n    @LLMQuiz(833)\n    $$\n"
                "@LLMQuiz(834)\n[[visible 834]]\n"
            ),
        ),
        source_path="indented-owned-fake-math.md",
    )
    assert len(
        [
            item
            for item in indented_before_math["protected_spans"]
            if item["kind"] == "indented_code"
        ]
    ) == 1
    assert not any(
        item["kind"] == "display_math"
        for item in indented_before_math["protected_spans"]
    )
    assert len(
        [
            item
            for item in indented_before_math["macros"]
            if item["name"] == "LLMQuiz"
        ]
    ) == 1


def test_indented_code_tabstops_containers_and_continuations() -> None:
    positive_prefixes = (
        "\t",
        " \t",
        "  \t",
        "   \t",
        "    ",
        "     ",
        " \t  ",
    )
    for index, prefix in enumerate(positive_prefixes, start=1):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Code\n"
                    f"{prefix}@LLMQuiz({index})\n"
                    f"{prefix}[[hidden {index}]]\n"
                ),
            ),
            source_path=f"indented-tabstop-positive-{index}.md",
        )
        indented = [
            item
            for item in result["protected_spans"]
            if item["kind"] == "indented_code"
        ]
        assert len(indented) == 1, (prefix, indented)
        assert "LLMQuiz" not in {
            item["name"] for item in result["macros"]
        }, prefix
        assert result["block_ranges"]["native_quiz"] == [], prefix
        assert _target(result, "llm")["instances"] == [], prefix

    for width in range(4):
        prefix = " " * width
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Visible\n"
                    f"{prefix}@LLMQuiz({100 + width})\n"
                    f"{prefix}[[visible {width}]]\n"
                ),
            ),
            source_path=f"indented-space-negative-{width}.md",
        )
        assert not any(
            item["kind"] == "indented_code"
            for item in result["protected_spans"]
        ), width
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({100 + width})"}, width
        assert result["block_ranges"]["native_quiz"], width

    continued_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## Continued\n"
            " \t@LLMQuiz(201)\n"
            "\n"
            "  \t[[hidden continued]]\n"
            "Boundary\n"
            "   \t@LLMQuiz(202)\n"
            "Visible boundary\n"
            "@LLMQuiz(299)\n"
            "[[visible after code]]\n"
        ),
    )
    continued = mapper.map_text(
        continued_source,
        source_path="indented-blank-continuation.md",
    )
    continued_spans = [
        item
        for item in continued["protected_spans"]
        if item["kind"] == "indented_code"
    ]
    assert len(continued_spans) == 1
    first_span = continued_spans[0]["span"]
    first_raw = continued_source[
        first_span["char_start"] : first_span["char_end"]
    ]
    assert "@LLMQuiz(201)\n\n" in first_raw
    assert "[[hidden continued]]" in first_raw
    assert "Boundary" not in first_raw
    assert {
        item["span"]["raw"]
        for item in continued["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(202)", "@LLMQuiz(299)"}
    assert len(continued["block_ranges"]["native_quiz"]) == 1

    container_prefixes = {
        "quote_spaces": ">     ",
        "quote_tabstop": ">   \t",
        "list_spaces": "-     ",
        "list_tabstop": "-    \t",
        "nested": "> -     ",
    }
    for index, (label, prefix) in enumerate(
        container_prefixes.items(), start=1
    ):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Container\n"
                    f"{prefix}@LLMQuiz({300 + index})\n"
                    f"{prefix}[[hidden {label}]]\n"
                ),
            ),
            source_path=f"indented-container-{label}.md",
        )
        assert any(
            item["kind"] == "indented_code"
            for item in result["protected_spans"]
        ), label
        assert "LLMQuiz" not in {
            item["name"] for item in result["macros"]
        }, label
        assert result["block_ranges"]["native_quiz"] == [], label

    quote_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## Quote continuation\n"
            ">     @LLMQuiz(350)\n"
            ">\n"
            ">     [[hidden quote continuation]]\n"
        ),
    )
    quote_blank = mapper.map_text(
        quote_source,
        source_path="indented-quote-blank-continuation.md",
    )
    quote_spans = [
        item
        for item in quote_blank["protected_spans"]
        if item["kind"] == "indented_code"
    ]
    assert len(quote_spans) == 1
    quote_span = quote_spans[0]["span"]
    assert ">\n>     [[hidden quote continuation]]" in (
        quote_source[quote_span["char_start"] : quote_span["char_end"]]
    )
    assert quote_blank["macros"] == []
    assert quote_blank["block_ranges"]["native_quiz"] == []

    list_paragraph_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## List paragraph continuation\n"
            "- Item\n"
            "      @LLMQuiz(360)\n"
            "      [[visible list continuation]]\n"
        ),
    )
    list_continuation = mapper.map_text(
        list_paragraph_source,
        source_path="indented-list-paragraph-continuation.md",
    )
    assert not any(
        item["kind"] == "indented_code"
        for item in list_continuation["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in list_continuation["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(360)"}
    assert list_continuation["block_ranges"]["native_quiz"]

    list_code = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## List code\n"
                "- Item\n"
                "\n"
                "      @LLMQuiz(361)\n"
                "      [[hidden list code]]\n"
            ),
        ),
        source_path="indented-list-code.md",
    )
    assert any(
        item["kind"] == "indented_code"
        for item in list_code["protected_spans"]
    )
    assert list_code["macros"] == []
    assert list_code["block_ranges"]["native_quiz"] == []

    list_precedence = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## List precedence\n"
                "  - Item\n"
                "\n"
                "    @LLMQuiz(362)\n"
                "    [[visible list paragraph]]\n"
                "\n"
                "        @LLMQuiz(363)\n"
                "        [[hidden list code]]\n"
            ),
        ),
        source_path="indented-list-precedence.md",
    )
    assert {
        item["span"]["raw"]
        for item in list_precedence["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(362)"}
    assert len(
        [
            item
            for item in list_precedence["protected_spans"]
            if item["kind"] == "indented_code"
        ]
    ) == 1

    quote_paragraph = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Quote paragraph\n"
                "> Running paragraph\n"
                ">     @LLMQuiz(370)\n"
                ">     [[visible quote continuation]]\n"
                ">\n"
                ">     @LLMQuiz(371)\n"
                ">     [[hidden quote code]]\n"
            ),
        ),
        source_path="indented-quote-paragraph.md",
    )
    assert {
        item["span"]["raw"]
        for item in quote_paragraph["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(370)"}
    assert len(
        [
            item
            for item in quote_paragraph["protected_spans"]
            if item["kind"] == "indented_code"
        ]
    ) == 1

    container_near_misses = {
        "quote_three": ">    ",
        "quote_short_tab": "> \t",
        "list_padding": "-    ",
    }
    for index, (label, prefix) in enumerate(
        container_near_misses.items(), start=1
    ):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                f"## Container control\n{prefix}@LLMQuiz({400 + index})\n",
            ),
            source_path=f"indented-container-control-{label}.md",
        )
        assert not any(
            item["kind"] == "indented_code"
            for item in result["protected_spans"]
        ), label
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({400 + index})"}, label

    ordered_two_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## Ordered interruption\n"
            "Running paragraph\n"
            "2.     @LLMQuiz(501)\n"
            "       [[visible ordered continuation]]\n"
        ),
    )
    ordered_two = mapper.map_text(
        ordered_two_source,
        source_path="indented-ordered-two-paragraph.md",
    )
    assert not any(
        item["kind"] == "indented_code"
        for item in ordered_two["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in ordered_two["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(501)"}
    assert ordered_two["block_ranges"]["native_quiz"]

    ordered_controls = {
        "one-interrupts": (
            "Running paragraph\n"
            "1.     @LLMQuiz(502)\n"
            "       [[hidden ordered one]]\n"
        ),
        "two-after-blank": (
            "Running paragraph\n\n"
            "2.     @LLMQuiz(503)\n"
            "       [[hidden ordered two after blank]]\n"
        ),
        "unordered-interrupts": (
            "Running paragraph\n"
            "-     @LLMQuiz(504)\n"
            "      [[hidden unordered]]\n"
        ),
        "nested-under-unordered": (
            "Running paragraph\n"
            "- 2.     @LLMQuiz(505)\n"
            "         [[hidden nested ordered]]\n"
        ),
        "nested-under-new-blockquote": (
            "Running paragraph\n"
            "> 2.     @LLMQuiz(507)\n"
            ">        [[hidden quote ordered]]\n"
        ),
    }
    for label, body in ordered_controls.items():
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                "## Ordered control\n" + body,
            ),
            source_path=f"indented-ordered-control-{label}.md",
        )
        assert any(
            item["kind"] == "indented_code"
            for item in result["protected_spans"]
        ), label
        assert "LLMQuiz" not in {
            item["name"] for item in result["macros"]
        }, label
        assert result["block_ranges"]["native_quiz"] == [], label

    empty_list_interrupt = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Empty list control\n"
                "Running paragraph\n"
                "+     \n"
                "    @LLMQuiz(506)\n"
            ),
        ),
        source_path="indented-empty-list-no-interrupt.md",
    )
    assert not any(
        item["kind"] == "indented_code"
        for item in empty_list_interrupt["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in empty_list_interrupt["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(506)"}

    # The indented-code scanner must consume the same stateful container view
    # as the other block scanners.  Re-parsing these physical prefixes
    # statelessly turns the continuation tab of the outer list into four false
    # code columns after the nested quote marker.
    nested_tab_visible = {
        "linkref": (
            "-\t>\t[x]: /u\n"
            "\t>\t@LLMQuiz(601) [[visible 601]]\n",
            True,
            True,
        ),
        "paragraph": (
            "-\t>\tfoo\n"
            "\t>\t@LLMQuiz(602) [[visible 602]]\n",
            True,
            True,
        ),
        "paragraph-one-extra-column": (
            "-\t>\tfoo\n"
            "\t>\t @LLMQuiz(603) [[visible 603]]\n",
            True,
            True,
        ),
        "blank-new-quote": (
            "-\t>\tfoo\n"
            "\n"
            "\t>\t@LLMQuiz(604) [[visible 604]]\n",
            True,
            True,
        ),
        "list-only": (
            "-\t[x]: /u\n"
            "\t@LLMQuiz(605) [[visible 605]]\n",
            True,
            False,
        ),
        "quote-only": (
            ">\t[x]: /u\n"
            ">\t@LLMQuiz(606) [[visible 606]]\n",
            False,
            True,
        ),
        "deep-list-quote-list": (
            "-\t>\t-\t[x]: /u\n"
            "\t>\t\t@LLMQuiz(607) [[visible 607]]\n",
            True,
            True,
        ),
    }
    for label, (body, inside_list, inside_quote) in (
        nested_tab_visible.items()
    ):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                "## Stateful container view\n" + body,
            ),
            source_path=f"indented-stateful-visible-{label}.md",
        )
        assert not any(
            item["kind"] == "indented_code"
            for item in result["protected_spans"]
        ), label
        macros = [
            item for item in result["macros"] if item["name"] == "LLMQuiz"
        ]
        assert len(macros) == 1, (label, macros)
        assert macros[0]["inside_list"] is inside_list, label
        assert macros[0]["inside_blockquote"] is inside_quote, label
        assert result["block_ranges"]["native_quiz"], label

    root_after_container = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Container exit\n"
                "-\t>\tfoo\n"
                "\n"
                "@LLMQuiz(608) [[root visible]]\n"
            ),
        ),
        source_path="indented-stateful-root-exit.md",
    )
    root_macro = next(
        item
        for item in root_after_container["macros"]
        if item["name"] == "LLMQuiz"
    )
    assert root_macro["inside_list"] is False
    assert root_macro["inside_blockquote"] is False

    nested_tab_code = {
        "nested-threshold": (
            "-\t>\tfoo\n"
            "\t>\t\n"
            "\t>\t  @LLMQuiz(611) [[hidden 611]]\n"
        ),
        "nested-after-blank": (
            "-\t>\tfoo\n"
            "\n"
            "\t>\t  @LLMQuiz(612) [[hidden 612]]\n"
        ),
        "list-only": (
            "-\tfoo\n"
            "\n"
            "\t\t@LLMQuiz(613) [[hidden 613]]\n"
        ),
        "quote-only": (
            ">\tfoo\n"
            ">\t\n"
            ">\t  @LLMQuiz(614) [[hidden 614]]\n"
        ),
        "root": "\t@LLMQuiz(615) [[hidden 615]]\n",
    }
    for label, body in nested_tab_code.items():
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                "## Exact code threshold\n" + body,
            ),
            source_path=f"indented-stateful-code-{label}.md",
        )
        code = [
            item
            for item in result["protected_spans"]
            if item["kind"] == "indented_code"
        ]
        assert len(code) == 1, (label, code)
        assert not any(
            item["name"] == "LLMQuiz" for item in result["macros"]
        ), label
        assert result["block_ranges"]["native_quiz"] == [], label

    context_seed = (
        "-\t>\t[x]: /u\n"
        "\t>\t@LLMQuiz(621)\n"
    )
    context_map = mapper.SourceMap(context_seed.encode("utf-8"))
    contexts = mapper._raw_html_container_contexts(context_map, 0, ())
    assert [
        (
            contexts[number][0],
            contexts[number][1],
            contexts[number][2],
            contexts[number][4],
            mapper._container_component_signature(contexts[number][3]),
        )
        for number in (1, 2)
    ] == [
        (
            "[x]: /u",
            4,
            1,
            2,
            (
                ("list", "-", 4, 0),
                ("quote", None, None, None),
            ),
        ),
        (
            "@LLMQuiz(621)",
            3,
            1,
            2,
            (
                ("list", "-", 4, 0),
                ("quote", None, None, None),
            ),
        ),
    ]
    assert mapper._find_indented_code(
        context_map, 0, (), contexts
    ) == []

    blank_seed = (
        "-\t>\tfoo\n"
        "\n"
        "\t>\t@LLMQuiz(622)\n"
    )
    blank_map = mapper.SourceMap(blank_seed.encode("utf-8"))
    blank_contexts = mapper._raw_html_container_contexts(blank_map, 0, ())
    assert [
        (
            blank_contexts[number][0],
            blank_contexts[number][4],
            [
                component["kind"]
                for component in blank_contexts[number][3]
            ],
        )
        for number in (1, 2, 3)
    ] == [
        ("foo", 2, ["list", "quote"]),
        ("", 0, ["list"]),
        ("@LLMQuiz(622)", 2, ["list", "quote"]),
    ]


def test_container_tab_residual_columns() -> None:
    def mapped(label: str, body: str) -> dict[str, Any]:
        return mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], "## Tabs\n" + body),
            source_path=f"container-tab-residual-{label}.md",
        )

    # Quote markers consume one visual column of following whitespace.  List
    # markers instead apply CommonMark's W+N rule: all N columns when N<=4,
    # otherwise W+1 with the residual columns left in item content.  The
    # public concealment threshold happens to be the same in this matrix.
    for kind, marker in (("quote", ">"), ("bullet", "-")):
        for authored_spaces in range(4):
            quiz_id = 600 + authored_spaces
            prefix = marker + "\t" + " " * authored_spaces
            result = mapped(
                f"{kind}-{authored_spaces}",
                f"{prefix}@LLMQuiz({quiz_id})\n",
            )
            hidden = authored_spaces >= 2
            indented = [
                item
                for item in result["protected_spans"]
                if item["kind"] == "indented_code"
            ]
            assert bool(indented) is hidden, (kind, authored_spaces)
            assert (
                f"@LLMQuiz({quiz_id})" in {
                    item["span"]["raw"]
                    for item in result["macros"]
                    if item["name"] == "LLMQuiz"
                }
            ) is not hidden, (kind, authored_spaces)

            native = mapped(
                f"{kind}-native-{authored_spaces}",
                f"{prefix}[[answer {authored_spaces}]]\n",
            )
            assert bool(native["block_ranges"]["native_quiz"]) is not hidden, (
                kind,
                authored_spaces,
            )

    exact_padding = (
        ("bullet-tab", "-\tfoo", "foo", 2, "-", 4, 0),
        ("bullet-tab-space", "-\t foo", "foo", 3, "-", 5, 0),
        (
            "bullet-tab-two-spaces",
            "-\t  foo",
            "  foo",
            2,
            "-",
            2,
            2,
        ),
        ("bullet-double-tab", "-\t\tfoo", "\tfoo", 2, "-", 2, 2),
        ("ordered-tab", "1.\tfoo", "foo", 3, "1.", 4, 0),
        (
            "ordered-tab-two-spaces",
            "1.\t  foo",
            "foo",
            5,
            "1.",
            6,
            0,
        ),
        (
            "ordered-tab-three-spaces",
            "1.\t   foo",
            "   foo",
            3,
            "1.",
            3,
            1,
        ),
        ("wide-tab", "123.\tfoo", "foo", 5, "123.", 8, 0),
        (
            "wide-tab-space",
            "123.\t foo",
            " foo",
            5,
            "123.",
            5,
            3,
        ),
        (
            "max-marker-tab",
            "123456789.\tfoo",
            "foo",
            11,
            "123456789.",
            12,
            0,
        ),
    )
    for (
        label,
        line,
        expected_view,
        expected_offset,
        marker,
        expected_indent,
        expected_virtual,
    ) in exact_padding:
        view, offset, _, components, virtual_indent = (
            mapper._raw_html_container_parts(line)
        )
        assert view == expected_view, label
        assert offset == expected_offset, label
        assert virtual_indent == expected_virtual, label
        assert components[-1]["marker"] == marker, label
        assert components[-1]["marker_offset"] == 0, label
        assert components[-1]["content_indent"] == expected_indent, label

    continuation_matrix = (
        ("bullet-four", "-\tfoo", "\tX", 1, "   X", 0),
        ("ordered-four", "1.\tfoo", "\tX", 1, "   X", 0),
        ("wide-eight", "123.\tfoo", "\t\tX", 1, "\tX", 0),
        (
            "max-twelve",
            "123456789.\tfoo",
            "\t\t\tX",
            1,
            "\t\tX",
            0,
        ),
    )
    for (
        label,
        opener,
        matching,
        expected_match,
        short,
        expected_short_match,
    ) in continuation_matrix:
        components = mapper._raw_html_container_parts(opener)[3]
        matched, _, _ = mapper._consume_raw_html_container(
            matching, components
        )
        assert matched == expected_match, label
        matched, _, _ = mapper._consume_raw_html_container(short, components)
        assert matched == expected_short_match, label

    ordered_cases = (
        ("one-control", "1.\t  ", False),
        ("one-code", "1.\t   ", True),
        ("wide-control", "123.\t", False),
        ("wide-code", "123.\t ", True),
    )
    for index, (label, prefix, hidden) in enumerate(ordered_cases):
        quiz_id = 620 + index
        result = mapped(label, f"{prefix}@LLMQuiz({quiz_id})\n")
        assert any(
            item["kind"] == "indented_code"
            for item in result["protected_spans"]
        ) is hidden, label
        assert (
            f"@LLMQuiz({quiz_id})" in {
                item["span"]["raw"]
                for item in result["macros"]
                if item["name"] == "LLMQuiz"
            }
        ) is not hidden, label

    nested_cases = (
        ("quote-list", "> -\t    "),
        ("list-quote", "- >\t    "),
        ("double-tab-quote", ">\t\t"),
        ("double-tab-list", "-\t\t"),
    )
    for index, (label, prefix) in enumerate(nested_cases):
        result = mapped(label, f"{prefix}@LLMQuiz({640 + index})\n")
        assert any(
            item["kind"] == "indented_code"
            for item in result["protected_spans"]
        ), label
        assert "LLMQuiz" not in {
            item["name"] for item in result["macros"]
        }, label

    for label, line, marker, expected_indent, expected_virtual in (
        ("bullet", "-\t\tcode", "-", 2, 2),
        ("ordered-one", "1.\t\tcode", "1.", 3, 1),
        ("ordered-wide", "123.\t\tcode", "123.", 5, 3),
    ):
        view, _, _, components, virtual_indent = (
            mapper._raw_html_container_parts(line)
        )
        assert view == "\tcode", label
        assert virtual_indent == expected_virtual, label
        assert components[-1]["kind"] == "list", label
        assert components[-1]["content_indent"] == expected_indent, label
        assert components[-1]["marker"] == marker, label
        assert components[-1]["marker_offset"] == 0, label

        continuation = " " * expected_indent
        environment = mapped(
            f"{label}-environment",
            (
                line
                + "\n"
                + continuation
                + "@Erdhaufen\n"
                + continuation
                + "X\n"
                + continuation
                + "@EndeErdhaufen\n"
            ),
        )
        pair = environment["environment"]["block_pairs"][0]
        assert pair["valid"] is False, label
        assert "marker_in_list" in pair["exclusion_reasons"], label

        native = mapped(
            f"{label}-native",
            line + "\n" + continuation + "[[answer]]\n",
        )
        assert native["block_ranges"]["native_quiz"][0][
            "container_kind"
        ] == "list", label


def test_link_reference_paragraph_and_container_state() -> None:
    valid = (
        "[bar]: /baz",
        r"[a\[b\]]: <https://example.test/a b>",
        '[title]: /target "A title"',
        "[balanced]: /target(and-more)",
        "[multiline]:\n/target",
        "[title-next]: /target\n  'A title'",
        "[\nmultiline label\n]: /target",
        "[nbsp]: /a\u00a0b",
        "[" + (r"\*" * 499) + "a]: /target",
    )
    invalid = (
        "[[bar]: /baz",
        "[   ]: /baz",
        "[bar]: <unterminated",
        "[bar]: /unbalanced(",
        "[bar]: /baz trailing",
        r"[bar]: /a\ b",
        "[bar]: /a\x01b",
        "[" + (r"\*" * 500) + "]: /target",
    )
    assert all(mapper._is_link_reference_definition(item) for item in valid)
    assert not any(
        mapper._is_link_reference_definition(item) for item in invalid
    )
    assert mapper._is_link_reference_definition("[bar]:") is False

    running = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Running paragraph\n"
                "Paragraph\n"
                "[bar]: /baz\n"
                "    @LLMQuiz(700)\n"
                "    [[visible answer]]\n"
            ),
        ),
        source_path="link-reference-cannot-interrupt-paragraph.md",
    )
    assert not any(
        item["kind"] == "indented_code"
        for item in running["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in running["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(700)"}
    assert len(running["block_ranges"]["native_quiz"]) == 1

    after_blank = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Closed paragraph\n"
                "Paragraph\n\n"
                "[bar]: /baz\n"
                "    @LLMQuiz(701)\n"
                "    [[hidden answer]]\n"
            ),
        ),
        source_path="link-reference-after-blank-block.md",
    )
    assert any(
        item["kind"] == "indented_code"
        for item in after_blank["protected_spans"]
    )
    assert "LLMQuiz" not in {
        item["name"] for item in after_blank["macros"]
    }
    assert after_blank["block_ranges"]["native_quiz"] == []

    protected_definitions = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Invisible definitions\n"
                "[llm]: /@LLMQuiz(702)\n"
                "[native]: <[[hidden reference quiz]]>\n"
                "[earth]: /@Erdhaufen\n"
                "[title]: /url \"@Pflanze [[hidden title quiz]]\"\n"
                "@LLMQuiz(703)\n"
                "[[visible answer]]\n"
                "@Erdhaufen\nX\n@EndeErdhaufen\n"
            ),
        ),
        source_path="link-reference-definitions-are-protected.md",
    )
    definitions = [
        item
        for item in protected_definitions["protected_spans"]
        if item["kind"] == "link_reference_definition"
    ]
    assert len(definitions) == 4
    assert {
        item["span"]["raw"]
        for item in protected_definitions["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(703)"}
    assert {
        item["name"]
        for item in protected_definitions["macros"]
        if item["name"] in {
            "Erdhaufen",
            "EndeErdhaufen",
            "Pflanze",
        }
    } == {"Erdhaufen", "EndeErdhaufen"}
    assert len(protected_definitions["block_ranges"]["native_quiz"]) == 1
    assert protected_definitions["environment"]["block_pairs"][0][
        "valid"
    ] is True

    exact_multiline = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Multiline definition\n"
                "[foo]:\n"
                "/url\n"
                "    @LLMQuiz(704)\n"
                "    [[hidden answer]]\n"
            ),
        ),
        source_path="link-reference-multiline-destination.md",
    )
    assert len(
        [
            item
            for item in exact_multiline["protected_spans"]
            if item["kind"] == "link_reference_definition"
        ]
    ) == 1
    assert any(
        item["kind"] == "indented_code"
        for item in exact_multiline["protected_spans"]
    )
    assert "LLMQuiz" not in {
        item["name"] for item in exact_multiline["macros"]
    }
    assert exact_multiline["block_ranges"]["native_quiz"] == []

    escape_and_nbsp = (
        ("literal-space", r"[foo]: /a\ b", 705, False),
        ("nbsp", "[foo]: /a\u00a0b", 706, True),
        (
            "label-999",
            "[" + (r"\*" * 499) + "a]: /url",
            707,
            True,
        ),
        (
            "label-1000",
            "[" + (r"\*" * 500) + "]: /url",
            708,
            False,
        ),
    )
    for label, definition, quiz_id, valid_definition in escape_and_nbsp:
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Exact reference grammar\n"
                    + definition
                    + "\n"
                    + f"    @LLMQuiz({quiz_id})\n"
                    + "    [[answer]]\n"
                ),
            ),
            source_path=f"link-reference-exact-{label}.md",
        )
        assert bool(
            [
                item
                for item in result["protected_spans"]
                if item["kind"] == "link_reference_definition"
            ]
        ) is valid_definition, label
        assert bool(
            [
                item
                for item in result["protected_spans"]
                if item["kind"] == "indented_code"
            ]
        ) is valid_definition, label
        assert (
            f"@LLMQuiz({quiz_id})" in {
                item["span"]["raw"]
                for item in result["macros"]
                if item["name"] == "LLMQuiz"
            }
        ) is not valid_definition, label

    title_fallback = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Next-line title fallback\n"
                "[foo]: /url\n"
                "  \"@LLMQuiz(709)\" junk\n"
                "@LLMQuiz(710)\n"
            ),
        ),
        source_path="link-reference-next-line-title-garbage.md",
    )
    assert len(
        [
            item
            for item in title_fallback["protected_spans"]
            if item["kind"] == "link_reference_definition"
        ]
    ) == 1
    assert {
        item["span"]["raw"]
        for item in title_fallback["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(709)", "@LLMQuiz(710)"}

    html_block_controls = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Raw HTML block controls\n"
                "<div>\n"
                "[foo]: /@LLMQuiz(711)\n"
                "</div>\n\n"
                "<span>\n"
                "[bar]: /@LLMQuiz(712)\n"
                "</span>\n\n"
            ),
        ),
        source_path="link-reference-not-inside-type-six-seven-html.md",
    )
    assert not any(
        item["kind"] == "link_reference_definition"
        for item in html_block_controls["protected_spans"]
    )
    # LiaScript-specific contract: generic Type-6/7 HTML controls block
    # state, but does not blanket-conceal inner LiaScript macros.
    assert {
        item["span"]["raw"]
        for item in html_block_controls["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(711)", "@LLMQuiz(712)"}

    for index, candidate in enumerate(invalid):
        quiz_id = 710 + index
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Invalid reference\n\n"
                    + candidate
                    + "\n"
                    + f"    @LLMQuiz({quiz_id})\n"
                ),
            ),
            source_path=f"invalid-link-reference-{index}.md",
        )
        assert not any(
            item["kind"] == "indented_code"
            for item in result["protected_spans"]
        ), candidate
        assert f"@LLMQuiz({quiz_id})" in {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        }, candidate

    containers = (
        ("list", "- Paragraph\n", {"marker_in_list"}),
        ("quote", "> Paragraph\n", {"marker_in_blockquote"}),
        (
            "nested",
            "- > Paragraph\n",
            {"marker_in_list", "marker_in_blockquote"},
        ),
    )
    for label, opening, expected_reasons in containers:
        body = (
            "## Lazy reference\n"
            + opening
            + "[bar]: /baz\n"
            + "@Erdhaufen\nX\n@EndeErdhaufen\n"
        )
        result = mapper.map_text(
            _synthetic_course(["lia-loot"], body),
            source_path=f"lazy-link-reference-{label}.md",
        )
        pair = result["environment"]["block_pairs"][0]
        assert pair["valid"] is False, label
        assert expected_reasons.issubset(pair["exclusion_reasons"]), label
        markers = [
            item
            for item in result["macros"]
            if item["name"] in {"Erdhaufen", "EndeErdhaufen"}
        ]
        assert len(markers) == 2
        assert all(
            item["inside_list"]
            for item in markers
        ) is ("marker_in_list" in expected_reasons), label
        assert all(
            item["inside_blockquote"]
            for item in markers
        ) is ("marker_in_blockquote" in expected_reasons), label

        native = mapper.map_text(
            _synthetic_course(
                ["lia-loot"],
                "## Lazy native\n" + opening + "[bar]: /baz\n[[answer]]\n",
            ),
            source_path=f"lazy-link-reference-native-{label}.md",
        )
        expected_container = (
            "list" if "marker_in_list" in expected_reasons else "line"
        )
        assert native["block_ranges"]["native_quiz"][0][
            "container_kind"
        ] == expected_container, label

    exited = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## Container exit\n"
                "- Paragraph\n\n"
                "[bar]: /baz\n"
                "@Erdhaufen\nX\n@EndeErdhaufen\n"
            ),
        ),
        source_path="link-reference-after-list-exit.md",
    )
    assert exited["environment"]["block_pairs"][0]["valid"] is True


def test_list_switch_and_outer_interrupt_contexts() -> None:
    bt = chr(96)
    switch_cases = (
        ("ordered-to-bullet", "1. foo\n*\n", "  "),
        ("bullet-to-ordered", "- foo\n1.\n", "   "),
        ("bullet-to-ordered-two", "- foo\n2.\n", "   "),
        ("delimiter-switch", "1. foo\n2)\n", "   "),
    )
    for label, opening, continuation in switch_cases:
        result = mapper.map_text(
            _synthetic_course(
                ["lia-loot"],
                (
                    "## List type switch\n"
                    + opening
                    + continuation
                    + "@Erdhaufen\n"
                    + continuation
                    + "X\n"
                    + continuation
                    + "@EndeErdhaufen\n"
                ),
            ),
            source_path=f"list-type-switch-{label}.md",
        )
        pair = result["environment"]["block_pairs"][0]
        assert pair["valid"] is False, label
        assert "marker_in_list" in pair["exclusion_reasons"], label
        markers = [
            item
            for item in result["macros"]
            if item["name"] in {"Erdhaufen", "EndeErdhaufen"}
        ]
        assert len(markers) == 2 and all(
            item["inside_list"] for item in markers
        ), label

    quoted_switch = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## Quoted list type switch\n"
                "> 1. foo\n"
                "> *\n"
                ">   @Erdhaufen\n"
                ">   X\n"
                ">   @EndeErdhaufen\n"
            ),
        ),
        source_path="quoted-list-type-switch.md",
    )
    pair = quoted_switch["environment"]["block_pairs"][0]
    assert pair["valid"] is False
    assert {
        "marker_in_list",
        "marker_in_blockquote",
    }.issubset(pair["exclusion_reasons"])

    # LiaScript-specific contract: generic Type-6/7 HTML changes paragraph and
    # container state but does not hide its following LiaScript source.  Only
    # Type-1 and special markup owners suppress macros/quizzes wholesale.
    type_seven_after_switch = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Type seven after list switch\n"
                "1. foo\n"
                "*\n"
                "  <span>\n"
                "  @LLMQuiz(750)\n"
                "  [[visible answer]]\n"
            ),
        ),
        source_path="list-switch-type-seven-visible-liascript.md",
    )
    assert {
        item["span"]["raw"]
        for item in type_seven_after_switch["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(750)"}
    quiz = type_seven_after_switch["block_ranges"]["native_quiz"][0]
    assert quiz["container_kind"] == "list"

    recursive = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## Outer item content\n"
                "Paragraph\n"
                "- -\n"
                "  @Erdhaufen\n"
                "  X\n"
                "  @EndeErdhaufen\n"
            ),
        ),
        source_path="outer-list-item-nonblank-inner-empty.md",
    )
    pair = recursive["environment"]["block_pairs"][0]
    assert pair["valid"] is False
    assert pair["exclusion_reasons"] == ["marker_in_list"]
    candidate = mapper._first_list_interrupt_candidate("- -")
    assert candidate == ("-", "-", 0)

    inline_boundary = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Outer item inline boundary\n"
                + "Paragraph "
                + bt
                + "open\n"
                + "- -\n"
                + "  @LLMQuiz(751)\n"
                + "  [[visible answer]] "
                + bt
                + "\n"
            ),
        ),
        source_path="outer-list-item-inline-code-boundary.md",
    )
    assert not any(
        item["kind"] == "inline_code"
        for item in inline_boundary["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in inline_boundary["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(751)"}
    assert inline_boundary["block_ranges"]["native_quiz"]

    for label, marker in (
        ("outer-empty", "-"),
        ("ordered-two", "2. -"),
    ):
        control = mapper.map_text(
            _synthetic_course(
                ["lia-loot"],
                (
                    "## Noninterrupting outer item\n"
                    "Paragraph\n"
                    + marker
                    + "\n"
                    + "  @Erdhaufen\n"
                    + "  X\n"
                    + "  @EndeErdhaufen\n"
                ),
            ),
            source_path=f"outer-list-noninterrupt-{label}.md",
        )
        assert control["environment"]["block_pairs"][0]["valid"] is True, label


def test_multiline_inline_markup_paragraph_and_container_state() -> None:
    families = (
        ("comment", "<!-- open", "continued -->", "html_comment"),
        ("pi", "<?open", "continued ?>", "html_processing_instruction"),
        ("declaration", "<!A open", "continued >", "html_declaration"),
        ("cdata", "<![CDATA[open", "continued]]>", "html_cdata"),
    )
    for index, (label, opener, closer, kind) in enumerate(families):
        quiz_id = 800 + index
        running = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Inline owner paragraph\n"
                    + "Paragraph "
                    + opener
                    + "\n"
                    + closer
                    + "\n"
                    + f"    @LLMQuiz({quiz_id})\n"
                    + "    [[visible answer]]\n"
                ),
            ),
            source_path=f"inline-{label}-keeps-paragraph-open.md",
        )
        owners = [
            item
            for item in running["protected_spans"]
            if item["kind"] == kind
        ]
        assert len(owners) == 1 and owners[0]["block_start"] is False, label
        assert not any(
            item["kind"] == "indented_code"
            for item in running["protected_spans"]
        ), label
        assert f"@LLMQuiz({quiz_id})" in {
            item["span"]["raw"]
            for item in running["macros"]
            if item["name"] == "LLMQuiz"
        }, label
        assert running["block_ranges"]["native_quiz"], label

        internal_id = 820 + index
        outside_id = 830 + index
        inside = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Inline owner contents\n"
                    + "Paragraph "
                    + opener
                    + "\n"
                    + f"@LLMQuiz({internal_id}) [[hidden]]\n"
                    + closer
                    + "\n"
                    + f"@LLMQuiz({outside_id})\n"
                    + "[[visible]]\n"
                ),
            ),
            source_path=f"inline-{label}-softbreak-owner.md",
        )
        assert {
            item["span"]["raw"]
            for item in inside["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({outside_id})"}, label
        assert len(inside["block_ranges"]["native_quiz"]) == 1, label

    containers = (
        ("list", "- Paragraph ", {"marker_in_list"}),
        ("quote", "> Paragraph ", {"marker_in_blockquote"}),
        (
            "nested",
            "- > Paragraph ",
            {"marker_in_list", "marker_in_blockquote"},
        ),
    )
    for family_index, (family, opener, closer, kind) in enumerate(families):
        for container, prefix, expected_reasons in containers:
            result = mapper.map_text(
                _synthetic_course(
                    ["lia-loot"],
                    (
                        "## Inline owner lazy container\n"
                        + prefix
                        + opener
                        + "\n"
                        + closer
                        + "\n"
                        + "@Erdhaufen\nX\n@EndeErdhaufen\n"
                    ),
                ),
                source_path=(
                    f"inline-{family}-lazy-container-{container}.md"
                ),
            )
            owners = [
                item
                for item in result["protected_spans"]
                if item["kind"] == kind
            ]
            assert len(owners) == 1 and owners[0]["block_start"] is False
            pair = result["environment"]["block_pairs"][0]
            assert pair["valid"] is False, (family, container)
            assert expected_reasons.issubset(
                pair["exclusion_reasons"]
            ), (family, container)

    boundary_starts = (
        ("blank", "Paragraph {opener}\n\nBoundary\n"),
        ("heading", "Paragraph {opener}\n## Boundary\n"),
        ("list", "Paragraph {opener}\n- Boundary\n"),
        ("container-exit", "> Paragraph {opener}\n- Boundary\n"),
    )
    for family_index, (family, opener, closer, kind) in enumerate(families):
        for boundary_index, (boundary, pattern) in enumerate(boundary_starts):
            quiz_id = 850 + family_index * 10 + boundary_index
            body = (
                "## Inline paragraph boundary\n"
                + pattern.format(opener=opener)
                + f"@LLMQuiz({quiz_id})\n"
                + "[[visible after boundary]]\n"
                + closer
                + "\n"
            )
            result = mapper.map_text(
                _synthetic_course(["lia-llm", "lia-loot"], body),
                source_path=f"inline-{family}-boundary-{boundary}.md",
            )
            assert not any(
                item["kind"] == kind
                for item in result["protected_spans"]
            ), (family, boundary)
            assert f"@LLMQuiz({quiz_id})" in {
                item["span"]["raw"]
                for item in result["macros"]
                if item["name"] == "LLMQuiz"
            }, (family, boundary)
            assert result["block_ranges"]["native_quiz"], (
                family,
                boundary,
            )

    identity_source = mapper.SourceMap(
        (
            "- Paragraph\n"
            "  continuation\n"
            "- sibling\n"
            "  continuation\n"
        ).encode("utf-8")
    )
    identity_contexts = mapper._raw_html_container_contexts(
        identity_source, 0
    )
    assert [
        identity_contexts[line][3][-1]["item_start_line"]
        for line in range(1, 5)
    ] == [1, 1, 3, 3]

    for family_index, (family, opener, closer, kind) in enumerate(families):
        hidden_id = 890 + family_index * 2
        visible_id = hidden_id + 1
        same_item = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Same list item inline owner\n"
                    + "- Paragraph "
                    + opener
                    + "\n"
                    + f"  @LLMQuiz({hidden_id}) [[hidden]]\n"
                    + "  "
                    + closer
                    + "\n"
                    + f"  @LLMQuiz({visible_id})\n"
                    + "  [[visible]]\n"
                ),
            ),
            source_path=f"inline-{family}-same-list-item.md",
        )
        owners = [
            item
            for item in same_item["protected_spans"]
            if item["kind"] == kind
        ]
        assert len(owners) == 1 and owners[0]["block_start"] is False
        assert {
            item["span"]["raw"]
            for item in same_item["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({visible_id})"}, family
        assert len(same_item["block_ranges"]["native_quiz"]) == 1

        for marker_label, marker, continuation in (
            ("bullet", "-", "  "),
            ("same-number-ordered", "1.", "   "),
        ):
            quiz_id = 900 + family_index * 10 + len(marker)
            sibling = mapper.map_text(
                _synthetic_course(
                    ["lia-llm", "lia-loot"],
                    (
                        "## List sibling inline boundary\n"
                        + marker
                        + " Paragraph "
                        + opener
                        + "\n"
                        + marker
                        + f" @LLMQuiz({quiz_id}) "
                        + closer
                        + "\n"
                        + continuation
                        + "[[visible sibling answer]]\n"
                    ),
                ),
                source_path=(
                    f"inline-{family}-sibling-{marker_label}.md"
                ),
            )
            assert not any(
                item["kind"] == kind
                for item in sibling["protected_spans"]
            ), (family, marker_label)
            macros = [
                item
                for item in sibling["macros"]
                if item["name"] == "LLMQuiz"
            ]
            assert [item["span"]["raw"] for item in macros] == [
                f"@LLMQuiz({quiz_id})"
            ], (family, marker_label)
            assert macros[0]["inside_list"] is True
            assert len(sibling["block_ranges"]["native_quiz"]) == 1
            assert sibling["block_ranges"]["native_quiz"][0][
                "container_kind"
            ] == "list"


def test_finite_html_tag_paragraph_boundaries() -> None:
    positive = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## HTML tag softbreak\n"
                "Paragraph <span title=\"open\n"
                "@LLMQuiz(930) [[hidden]]\">\n"
                "@LLMQuiz(931)\n"
                "[[visible]]\n"
            ),
        ),
        source_path="finite-html-tag-same-paragraph.md",
    )
    tags = [
        item
        for item in positive["protected_spans"]
        if item["kind"] == "html_tag"
    ]
    assert len(tags) == 1
    assert tags[0]["span"]["line_start"] < tags[0]["span"]["line_end"]
    assert {
        item["span"]["raw"]
        for item in positive["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(931)"}
    assert len(positive["block_ranges"]["native_quiz"]) == 1

    boundaries = (
        (
            "blank",
            (
                "Paragraph <span title=\"open\n\n"
                "@LLMQuiz({quiz})\n"
                "[[visible]]\n"
                "\">\n"
            ),
            False,
        ),
        (
            "heading",
            (
                "Paragraph <span title=\"open\n"
                "## Boundary\n"
                "@LLMQuiz({quiz})\n"
                "[[visible]]\n"
                "\">\n"
            ),
            False,
        ),
        (
            "same-list-sibling",
            (
                "- Paragraph <span title=\"open\n"
                "- @LLMQuiz({quiz})\n"
                "  [[visible]]\n"
                "  \">\n"
            ),
            True,
        ),
        (
            "container-exit",
            (
                "> Paragraph <span title=\"open\n"
                "- Boundary\n"
                "  @LLMQuiz({quiz})\n"
                "  [[visible]]\n"
                "  \">\n"
            ),
            True,
        ),
        (
            "atx-heading-leaf",
            (
                "## Heading <span title=\"open\n"
                "@LLMQuiz({quiz})\n"
                "[[visible]]\n"
                "\">\n"
            ),
            False,
        ),
    )
    for index, (label, pattern, inside_list) in enumerate(boundaries):
        quiz_id = 940 + index
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                "## HTML tag boundary\n" + pattern.format(quiz=quiz_id),
            ),
            source_path=f"finite-html-tag-boundary-{label}.md",
        )
        assert not any(
            item["kind"] == "html_tag"
            and item["span"]["raw"].startswith("<span")
            for item in result["protected_spans"]
        ), label
        macros = [
            item
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        ]
        assert [item["span"]["raw"] for item in macros] == [
            f"@LLMQuiz({quiz_id})"
        ], label
        assert macros[0]["inside_list"] is inside_list, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert (
            result["block_ranges"]["native_quiz"][0]["container_kind"]
            == ("list" if inside_list else "line")
        ), label


def test_lootif_trigger_matrix_and_cross_family_lifo() -> None:
    def one(
        trigger: str,
        *,
        before: str = "",
        after: str = "",
        payload: str = "Inhalt\n",
        imports: list[str] | None = None,
        closer: str = "Endelootif",
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        result = mapper.map_text(
            _synthetic_course(
                imports or ["lia-loot"],
                "## A\n"
                + before
                + f"@lootif({trigger}; spawn)\n"
                + payload
                + f"@{closer}\n"
                + after,
            ),
            source_path="lootif-trigger.md",
        )
        assert len(result["block_ranges"]["lootif"]) == 1, trigger
        return result, result["block_ranges"]["lootif"][0]

    for trigger in (
        "Lupe gefunden",
        "LUPE   GEFUNDEN",
        "lupe_gefunden",
        "lupe–gefunden",
        "magnifier-found",
    ):
        _, item = one(trigger, before="@Lupe\n")
        assert item["trigger_parse_status"] == "valid", trigger
        assert item["external_trigger_status"] == "proven", trigger
        assert item["valid"] is True, trigger
        assert item["evidence_basis"] == "source"
        assert all(
            evidence["proof_basis"] == "source"
            for evidence in item["external_trigger_evidence"]
        )

    _, after = one("Lupe gefunden", after="@Lupe\n")
    assert after["valid"] is True
    assert {item["relation"] for item in after["external_trigger_evidence"]} == {
        "after"
    }
    _, self_only = one("Lupe gefunden", payload="@Lupe\n")
    assert self_only["trigger_parse_status"] == "valid"
    assert self_only["external_trigger_status"] == "unproven"
    assert self_only["valid"] is False

    proven_cases = [
        ("Vorherige Aufgabe gelöst", "Frage [[1]]\n", "", ["lia-loot"]),
        ("previous_task_solved", "Frage [[1]]\n", "", ["lia-loot"]),
        ("Alle Aufgaben der aktuellen Folie gelöst", "", "Frage [[1]]\n", ["lia-loot"]),
        ("bewertbare Aufgaben >= 1", "Frage [[1]]\n", "", ["lia-loot"]),
        ("mindestens 1 bewertbare Aufgaben gelöst", "Frage [[1]]\n", "", ["lia-loot"]),
        ("Energie >= 50", "@Ressourcen(0,0,60)\n", "", ["lia-loot"]),
        ("Schatztruhen >= 1", "@Ressourcen(0,0,1)\n@Schatztruhe\n", "", ["lia-loot"]),
        ("1 Schatztruhe geöffnet", "@Ressourcen(0,0,1)\n@Schatztruhe\n", "", ["lia-loot"]),
        ("Schloss: check", "Frage [[1]]\n@Schluessel(rot)\n@Schloss(check, rot)\n", "", ["lia-loot"]),
        ("Puzzletor: rot", "@Puzzleteil(rot; 1)\n@Puzzletor(rot; [[1]])\n", "", ["lia-loot"]),
        ("Geheime Folie besucht", "@Geheimfolie\n", "", ["lia-loot"]),
        ("markiert: rot", "", "", ["lia-marker", "lia-loot"]),
        ("markiert: rot: Energie", "Energie\n", "", ["lia-marker", "lia-loot"]),
    ]
    for trigger, before, after_text, imports in proven_cases:
        _, item = one(trigger, before=before, after=after_text, imports=imports)
        assert item["trigger_parse_status"] == "valid", trigger
        assert item["external_trigger_status"] == "proven", (
            trigger,
            item,
        )
        assert item["valid"] is True, trigger

    invalid_triggers = [
        "Puzzletor: pink",
        "Schatztruhen banane 9",
        "markiert: violett",
        "markiert: rot:",
        "Energie >= -1",
        "Aufgaben >= 1.5",
        "Gold >= 1e3",
        "Gold >= 9007199254740992",
    ]
    for trigger in invalid_triggers:
        _, item = one(
            trigger,
            before=(
                "@Ressourcen(9,9,9)\n@Schatztruhe\n"
                "@Puzzleteil(blau; 1)\n@Puzzletor(blau; [[1]])\n"
            ),
            imports=["lia-marker", "lia-loot"],
        )
        assert item["trigger_parse_status"] == "invalid", trigger
        assert item["external_trigger_status"] == "invalid", trigger
        assert item["valid"] is False, trigger

    _, mismatch = one(
        "Puzzletor: rot",
        before="@Puzzleteil(blau; 1)\n@Puzzletor(blau; [[1]])\n",
    )
    assert mismatch["trigger_parse_status"] == "valid"
    assert mismatch["external_trigger_status"] == "unproven"
    assert mismatch["valid"] is False
    _, missing_piece = one(
        "Puzzletor: rot",
        before="@Puzzleteil(rot; 1)\n@Puzzletor(rot; [[2;1]])\n",
    )
    assert missing_piece["trigger_parse_status"] == "valid"
    assert missing_piece["external_trigger_status"] == "unproven"
    _, too_many = one(
        "Schatztruhen >= 2",
        before="@Ressourcen(0,0,1)\n@Schatztruhe\n",
    )
    assert too_many["trigger_parse_status"] == "valid"
    assert too_many["external_trigger_status"] == "unproven"

    comparison_cases = {
        "Gold > 4", "Gold >= 5", "Gold = 5", "Gold <= 5", "Gold < 6",
        "Gold => 5", "Gold == 5", "Gold =< 5", "Gold größer 4",
        "Gold größer oder gleich 5", "Gold mindestens 5", "Gold gleich 5",
        "Gold höchstens 5", "Gold kleiner 6", "Gold kleiner oder gleich 5",
    }
    for trigger in comparison_cases:
        _, item = one(trigger, before="@Ressourcen(5,0,0)\n")
        assert item["trigger_parse_status"] == "valid", trigger
        assert item["external_trigger_status"] == "proven", trigger
    _, decimal_resource = one(
        "Gold = 1,5", before="@Ressourcen(1.5,0,0)\n"
    )
    assert decimal_resource["valid"] is True
    _, max_safe = one(
        "Gold = 9007199254740991",
        before="@Ressourcen(9007199254740991,0,0)\n",
    )
    assert max_safe["valid"] is True

    for closer in ("Endelootif", "EndeLootif", "endlootif", "EndLootIf"):
        _, item = one("Lupe gefunden", before="@Lupe\n", closer=closer)
        assert item["valid"] is True, closer
    wrong_case = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            "## A\n@Lupe\n@lootif(Lupe gefunden; spawn)\nX\n@ENDLOOTIF\n",
        )
    )
    assert wrong_case["block_ranges"]["lootif"] == []
    assert any(
        item["code"] == "lootif_invalid_macro_case"
        for item in wrong_case["diagnostics"]
    )

    crossed_sources = [
        (
            "@Lupe\n@Erdhaufen\n@lootif(Lupe gefunden; spawn)\n"
            "X\n@EndeErdhaufen\n@Endelootif\n"
        ),
        (
            "@Lupe\n@lootif(Lupe gefunden; spawn)\n@Pflanze\n"
            "X\n@Endelootif\n@EndePflanze\n"
        ),
    ]
    for body in crossed_sources:
        result = mapper.map_text(_synthetic_course(["lia-loot"], "## A\n" + body))
        assert len(result["environment"]["block_pairs"]) == 1
        assert len(result["block_ranges"]["lootif"]) == 1
        assert result["environment"]["block_pairs"][0]["valid"] is False
        assert result["block_ranges"]["lootif"][0]["valid"] is False
        assert "cross_family_lifo_mismatch" in result["environment"]["block_pairs"][0]["exclusion_reasons"]
        assert "cross_family_lifo_mismatch" in result["block_ranges"]["lootif"][0]["exclusion_reasons"]


def test_trigger_witness_hardening() -> None:
    def trigger_result(
        trigger: str,
        *,
        before: str = "",
        payload: str = "X\n",
        after: str = "",
        imports: list[str] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        result = mapper.map_text(
            _synthetic_course(
                imports or ["lia-loot"],
                (
                    "## A\n" + before
                    + f"@lootif({trigger}; spawn)\n"
                    + payload + "@Endelootif\n" + after
                ),
            ),
            source_path="trigger-hardening.md",
        )
        assert len(result["block_ranges"]["lootif"]) == 1
        return result, result["block_ranges"]["lootif"][0]

    valid_puzzle = (
        "@Puzzleteil(rot; 1)\n@Puzzleteil(rot; 2)\n"
        "@Puzzleteil(rot; 3)\n@Puzzleteil(rot; 4)\n"
        "@Puzzletor(rot; [[3;1];[4;2]])\n"
    )
    _, puzzle = trigger_result("Puzzletor: rot", before=valid_puzzle)
    assert puzzle["external_trigger_status"] == "proven"
    assert puzzle["valid"] is True
    assert len(puzzle["external_trigger_evidence"]) == 5
    _, puzzle_after = trigger_result(
        "Puzzletor: rot", after=valid_puzzle
    )
    assert puzzle_after["external_trigger_status"] == "proven"
    assert {
        evidence["relation"]
        for evidence in puzzle_after["external_trigger_evidence"]
    } == {"after"}
    _, anchored_puzzle = trigger_result(
        "Puzzletor: rot",
        before=(
            "@Puzzleteil(rot; 1; erde; unsichtbar)\n"
            "@Puzzletor(rot; [[1]]; anker)\n"
        ),
    )
    assert anchored_puzzle["external_trigger_status"] == "proven"
    _, shared_options_puzzle = trigger_result(
        "Puzzletor: rot",
        before=(
            "@Puzzleteil(rot; 1; anker; 12s; theme=rot; "
            "farbmodus=dunkel; annotationen=aus; erde; pflanze; "
            "erde-unsichtbar; unsichtbar)\n"
            "@Puzzletor(rot; [[1]])\n"
        ),
    )
    assert shared_options_puzzle["external_trigger_status"] == "proven"
    for piece_count, matrix in (
        (3, "[[3;1;2]]"),
        (6, "[[6;1;5];[2;4;3]]"),
        (16, "[[16;1;15;2];[14;3;13;4];[12;5;11;6];[10;7;9;8]]"),
    ):
        parts = "".join(
            f"@Puzzleteil(rot; {number})\n"
            for number in range(1, piece_count + 1)
        )
        _, variable_puzzle = trigger_result(
            "Puzzletor: rot",
            before=parts + f"@Puzzletor(rot; {matrix})\n",
        )
        assert variable_puzzle["external_trigger_status"] == "proven"

    invalid_puzzles = {
        "piece_color_mismatch": (
            "@Puzzleteil(blau; 1)\n@Puzzletor(rot; [[1]])\n"
        ),
        "piece_gap": (
            "@Puzzleteil(rot; 1)\n@Puzzleteil(rot; 3)\n"
            "@Puzzletor(rot; [[1;2;3]])\n"
        ),
        "piece_duplicate": (
            "@Puzzleteil(rot; 1)\n@Puzzleteil(rot; 1)\n"
            "@Puzzletor(rot; [[1]])\n"
        ),
        "invalid_matrix": (
            "@Puzzleteil(rot; 1)\n@Puzzletor(rot; [[1;1]])\n"
        ),
        "duplicate_gate": (
            "@Puzzleteil(rot; 1)\n@Puzzletor(rot; [[1]])\n"
            "@Puzzletor(rot; [[1]])\n"
        ),
        "invalid_gate_anchor": (
            "@Puzzleteil(rot; 1)\n"
            "@Puzzletor(rot; [[1]]; anchor)\n"
        ),
        "invalid_piece_extra": (
            "@Puzzleteil(rot; 1; banane)\n"
            "@Puzzletor(rot; [[1]])\n"
        ),
        "duplicate_duration": (
            "@Puzzleteil(rot; 1; 1s; 2s)\n"
            "@Puzzletor(rot; [[1]])\n"
        ),
        "piece_after_own_gate": (
            "@Puzzletor(rot; [[1]])\n@Puzzleteil(rot; 1)\n"
        ),
        "gate_inside_reveal": (
            "@Puzzleteil(rot; 1)\n@Erdhaufen\n"
            "@Puzzletor(rot; [[1]])\n@EndeErdhaufen\n"
        ),
    }
    for label, before in invalid_puzzles.items():
        _, item = trigger_result("Puzzletor: rot", before=before)
        assert item["trigger_parse_status"] == "valid", label
        assert item["external_trigger_status"] == "unproven", label
        assert item["valid"] is False, label
    _, self_puzzle = trigger_result(
        "Puzzletor: rot",
        payload="@Puzzleteil(rot; 1)\n@Puzzletor(rot; [[1]])\n",
    )
    assert self_puzzle["external_trigger_status"] == "unproven"
    _, self_duplicate_gate = trigger_result(
        "Puzzletor: rot",
        before="@Puzzleteil(rot; 1)\n@Puzzletor(rot; [[1]])\n",
        payload="@Puzzletor(rot; [[1]])\n",
    )
    assert self_duplicate_gate["external_trigger_status"] == "unproven"
    _, self_duplicate_piece = trigger_result(
        "Puzzletor: rot",
        before="@Puzzleteil(rot; 1)\n@Puzzletor(rot; [[1]])\n",
        payload="@Puzzleteil(rot; 1)\n",
    )
    assert self_duplicate_piece["external_trigger_status"] == "unproven"

    timer_body = (
        '<!-- data-solution-timer="30s" '
        'data-solution-timer-start="onclick" -->\n'
        "[[Antwort]]\n@Schluessel(rot)\n@Schloss(timer; rot)\n"
    )
    _, no_import = trigger_result("Schloss: timer", before=timer_body)
    assert no_import["external_trigger_status"] == "unproven"
    _, no_instance = trigger_result(
        "Schloss: timer",
        before="@Schluessel(rot)\n@Schloss(timer; rot)\n",
        imports=["lia-timer", "lia-loot"],
    )
    assert no_instance["external_trigger_status"] == "unproven"
    _, wrong_state = trigger_result(
        "Schloss: timer",
        before=(
            '<!-- data-solution-timer="30s" '
            'data-solution-timer-start="oncheck" -->\n'
            "[[Antwort]]\n@Schluessel(rot)\n@Schloss(timer; rot)\n"
        ),
        imports=["lia-timer", "lia-loot"],
    )
    assert wrong_state["external_trigger_status"] == "unproven"
    _, valid_lock = trigger_result(
        "Schloss: timer",
        before=timer_body,
        imports=["lia-timer", "lia-loot"],
    )
    assert valid_lock["external_trigger_status"] == "proven"
    assert valid_lock["valid"] is True
    target_evidence = valid_lock["external_trigger_evidence"][0][
        "target_contract"
    ]
    assert target_evidence["provider"] == "lia-timer"
    assert target_evidence["instance_ids"]
    _, valid_lock_after = trigger_result(
        "Schloss: timer",
        after=timer_body,
        imports=["lia-timer", "lia-loot"],
    )
    assert valid_lock_after["external_trigger_status"] == "proven"
    assert valid_lock_after["external_trigger_evidence"][0][
        "relation"
    ] == "after"

    _, page_missing = trigger_result(
        "Schloss: seitenwechsel",
        before="@Schluessel(rot)\n@Schloss(seitenwechsel; rot)\n",
    )
    assert page_missing["external_trigger_status"] == "unproven"
    _, page_navigation = trigger_result(
        "Schloss: seitenwechsel",
        before="@Schluessel(rot)\n@Schloss(seitenwechsel; rot)\n",
        after="## B\nZweite Folie\n",
    )
    assert page_navigation["external_trigger_status"] == "proven"

    pentomino_surface = (
        "@PentominoQuiz(1)\n@Schluessel(rot)\n"
        "@Schloss(pentominoquiz; rot)\n"
    )
    _, pentomino_missing_import = trigger_result(
        "Schloss: pentominoquiz", before=pentomino_surface
    )
    assert pentomino_missing_import["external_trigger_status"] == "unproven"
    _, pentomino_missing_instance = trigger_result(
        "Schloss: pentominoquiz",
        before="@Schluessel(rot)\n@Schloss(pentominoquiz; rot)\n",
        imports=["lia-pentominos", "lia-loot"],
    )
    assert pentomino_missing_instance["external_trigger_status"] == "unproven"
    _, pentomino_before = trigger_result(
        "Schloss: pentominoquiz",
        before=pentomino_surface,
        imports=["lia-pentominos", "lia-loot"],
    )
    assert pentomino_before["external_trigger_status"] == "proven"
    _, pentomino_after = trigger_result(
        "Schloss: pentominoquiz",
        after=pentomino_surface,
        imports=["lia-pentominos", "lia-loot"],
    )
    assert pentomino_after["external_trigger_status"] == "proven"

    protected_words = (
        "<!-- Geheimwort -->\n"
        "$Geheimwort$\n"
        "`Geheimwort`\n"
        "```text\nGeheimwort\n```\n"
        "@Schatztruhe(Geheimwort)\n"
        "<script>Geheimwort</script>\n"
    )
    _, protected_marker = trigger_result(
        "markiert: rot: Geheimwort",
        before=protected_words,
        imports=["lia-marker", "lia-loot"],
    )
    assert protected_marker["external_trigger_status"] == "unproven"
    header_only = mapper.map_text(
        (
            "<!--\nversion: 1.0.0\ncomment: Geheimwort\n"
            "import: https://example.test/lia-marker/main/README.md\n"
            "import: https://example.test/lia-loot/main/README.md\n-->\n"
            "# Testkurs\n## A\n"
            "@lootif(markiert: rot: Geheimwort; spawn)\n"
            "X\n@Endelootif\n"
        ),
        source_path="marker-header-only.md",
    )
    assert header_only["block_ranges"]["lootif"][0][
        "external_trigger_status"
    ] == "unproven"
    _, visible_marker = trigger_result(
        "markiert: rot: Geheimwort",
        before="Hier steht das Geheimwort sichtbar.\n",
        imports=["lia-marker", "lia-loot"],
    )
    assert visible_marker["external_trigger_status"] == "proven"

    two_quizzes = "Frage A [[1]]\n\nFrage B [[2]]\n"
    for expression in (
        "bewertbare Aufgaben = 1",
        "bewertbare Aufgaben = 2",
        "bewertbare Aufgaben < 1",
        "bewertbare Aufgaben <= 0",
    ):
        _, item = trigger_result(expression, before=two_quizzes)
        assert item["external_trigger_status"] == "proven", expression
    for expression in (
        "bewertbare Aufgaben > 2",
        "bewertbare Aufgaben = 3",
        "bewertbare Aufgaben < 0",
    ):
        _, item = trigger_result(expression, before=two_quizzes)
        assert item["external_trigger_status"] == "unproven", expression

    two_chests = (
        "@Ressourcen(0,0,1)\n@Schatztruhe\n@Schatztruhe\n"
    )
    for expression in (
        "Schatztruhen = 1", "Schatztruhen = 2",
        "Schatztruhen < 1", "Schatztruhen <= 0",
    ):
        _, item = trigger_result(expression, before=two_chests)
        assert item["external_trigger_status"] == "proven", expression
    for expression in ("Schatztruhen > 2", "Schatztruhen = 3"):
        _, item = trigger_result(expression, before=two_chests)
        assert item["external_trigger_status"] == "unproven", expression


def test_concealment_inventory_edits_and_remap() -> None:
    source = _synthetic_course(
        ["lia-loot"],
        (
            "## A\n@Lupe\n@Schaufel\n@Giesskanne\n"
            "@Schatztruhe\n"
            "@Schatztruhe(erde)\n"
            "@Energiekiste(erde-unsichtbar)\n"
            "@Diamanttruhe(zauberstaub)\n"
            "@Lupe(solid)\n"
            "@Schaufel(unsichtbar; dust)\n"
            "@Puzzleteil\n"
            "@Erdhaufen.inline(@Schatztruhe)\n"
            "@Pflanze.inline(@Energiekiste, clue)\n"
            "@Erdhaufen\n"
            "@Schatztruhe\n"
            "@Unsichtbar(@Diamanttruhe)\n"
            "@EndeErdhaufen\n"
        ),
    )
    result = mapper.map_text(source, source_path="concealment.md")
    items = result["environment"]["item_concealments"]

    bare = next(
        item
        for item in items
        if item["carrier"] == "Schatztruhe"
        and item["span"]["line_start"] == 10
    )
    assert {edit["operation"] for edit in bare["edit_variants"]} == {
        "rewrite_macro"
    }
    assert {
        edit["text"] for edit in bare["edit_variants"]
    } == {"@Schatztruhe(unsichtbar)", "@Schatztruhe(zauberstaub)"}

    argumented = next(
        item
        for item in items
        if item["carrier"] == "Schatztruhe"
        and item["span"]["line_start"] == 11
    )
    assert all(
        edit["operation"] == "insert_argument"
        and edit["anchor"]["char_start"]
        == argumented["span"]["char_end"] - 1
        and edit["separator"] == "; "
        for edit in argumented["edit_variants"]
    )
    layer_only = next(
        item for item in items if item["carrier"] == "Energiekiste"
        and item["span"]["line_start"] == 12
    )
    assert layer_only["current_concealment"] is None
    existing = next(
        item for item in items if item["carrier"] == "Diamanttruhe"
        and item["span"]["line_start"] == 13
    )
    assert existing["current_concealment"] == "zauberstaub"
    assert all(
        edit["operation"] == "replace_argument"
        and edit["replace_span"]["raw"] == "zauberstaub"
        for edit in existing["edit_variants"]
    )
    alias = next(
        item for item in items if item["carrier"] == "Lupe"
        and item["span"]["line_start"] == 14
    )
    assert alias["current_concealment"] == "unsichtbar"
    duplicate = next(
        item for item in items if item["carrier"] == "Schaufel"
        and item["span"]["line_start"] == 15
    )
    assert duplicate["concealment_valid"] is False
    assert duplicate["edit_variants"] == []
    bare_piece = next(
        item for item in items if item["carrier"] == "Puzzleteil"
        and item["span"]["line_start"] == 16
    )
    assert bare_piece["structurally_eligible"] is False
    assert bare_piece["edit_variants"] == []

    visibility = _candidate(result, "container_visibility_option")["anchors"]
    assert len(visibility) == 3
    inline = [
        item for item in visibility
        if item["evidence"]["reveal_form"] == "inline"
    ]
    assert len(inline) == 2
    assert inline[0]["edit_variants"][0]["text"] == ", unsichtbar"
    assert inline[1]["edit_variants"][0]["text"] == "; unsichtbar"
    hidden = _candidate(result, "hidden_macro_inside_reveal")["anchors"]
    assert hidden
    assert all(
        item["edit_variants"] and item["automation_eligible"] is False
        for item in hidden
    )
    wrapper = next(
        item for item in hidden if item["current_wrapper"] == "unsichtbar"
    )
    assert {
        edit["operation"] for edit in wrapper["edit_variants"]
    } == {"replace_wrapper_name"}

    def apply_edit(text: str, edit: dict[str, Any]) -> str:
        if edit["operation"] in {"rewrite_macro", "replace_argument"}:
            span = edit["replace_span"]
            return text[: span["char_start"]] + edit["text"] + text[span["char_end"] :]
        if edit["operation"] == "insert_argument":
            position = edit["anchor"]["char_start"]
            return text[:position] + edit["text"] + text[position:]
        assert edit["operation"] == "wrap_exact_payload"
        start = edit["prefix_anchor"]["char_start"]
        end = edit["suffix_anchor"]["char_start"]
        return (
            text[:start]
            + edit["prefix_text"]
            + text[start:end]
            + edit["suffix_text"]
            + text[end:]
        )

    rewritten = apply_edit(
        source,
        next(edit for edit in bare["edit_variants"] if edit["mode"] == "unsichtbar"),
    )
    remapped = mapper.map_text(rewritten)
    assert any(
        item["carrier"] == "Schatztruhe"
        and item["span"]["line_start"] == 10
        and item["current_concealment"] == "unsichtbar"
        for item in remapped["environment"]["item_concealments"]
    )
    inserted = apply_edit(
        source,
        next(edit for edit in argumented["edit_variants"] if edit["mode"] == "zauberstaub"),
    )
    remapped = mapper.map_text(inserted)
    assert any(
        item["carrier"] == "Schatztruhe"
        and item["span"]["line_start"] == 11
        and item["current_concealment"] == "zauberstaub"
        for item in remapped["environment"]["item_concealments"]
    )

    crlf_text = _synthetic_course(
        ["lia-loot"], "## Ä\r\n@Schatztruhe(erde)\r\n"
    ).replace("\n", "\r\n").replace("\r\r\n", "\r\n")
    raw = b"\xef\xbb\xbf" + crlf_text.encode("utf-8")
    crlf = mapper.map_source(raw, source_path="concealment-crlf.md")
    candidate = _candidate(
        crlf, "collectible_concealment_option"
    )["anchors"][0]
    for span in _all_spans(candidate["edit_variants"]):
        _assert_byte_span(raw, crlf_text, span)


def test_bom_crlf_and_all_position_domains() -> None:
    bt = chr(96)
    text = (
        "<!--\r\n"
        "version: 1.0.0\r\n"
        "import: https://example.test/lia-DynFlex/main/README.md\r\n"
        "import: https://example.test/lia-loot/main/README.md\r\n"
        "-->\r\n"
        "# Übung\r\n"
        "## Äpfel\r\n"
        f"{bt * 3}text @LLMQuiz(1)\r\n"
        "@Pflanze\r\n"
        f"{bt * 3}\r\n"
        '<section class="dynFlex">\r\n'
        "Inhalt\r\n"
        "</section>\r\n"
    )
    raw = b"\xef\xbb\xbf" + text.encode("utf-8")
    result = mapper.map_source(raw, source_path="bom-crlf.md")
    assert result["source"]["newline_style"] == "crlf"
    assert result["source"]["bom_bytes"] == 3
    assert result["source"]["byte_count"] == len(raw)
    assert result["source"]["character_count"] == len(text)
    decorator = next(
        item for item in result["macros"] if item["name"] == "LLMQuiz"
    )
    assert decorator["usage_context"] == "fence_decorator"
    assert "Pflanze" not in {item["name"] for item in result["macros"]}
    spans = [
        result["imports"][0]["span"],
        next(
            item["span"]
            for item in result["protected_spans"]
            if item["kind"] == "fence"
        ),
        result["headings"][0]["span"],
        _candidate(result, "h2_whole_slide")["anchors"][0]["anchor"],
        _candidate(result, "dynflex_whole_section")["anchors"][0][
            "close_anchor"
        ],
    ]
    for span in spans:
        _assert_byte_span(raw, text, span)
    all_spans = list(_all_spans(result))
    assert len(all_spans) > 20
    for span in all_spans:
        assert 0 <= span["char_start"] <= span["char_end"] <= len(text)
        assert 3 <= span["byte_start"] <= span["byte_end"] <= len(raw)
        _assert_byte_span(raw, text, span)
        assert raw[span["byte_start"] : span["byte_end"]].decode(
            "utf-8"
        ) == text[span["char_start"] : span["char_end"]]
        if "raw" in span:
            assert span["raw"] == text[
                span["char_start"] : span["char_end"]
            ]
    assert result["header"]["span"]["char_start"] == 0
    assert result["header"]["span"]["byte_start"] == 3
    assert result["imports"][0]["span"]["byte_start"] > (
        result["imports"][0]["span"]["char_start"]
    )


def test_nul_commonmark_shadow_and_original_offsets() -> None:
    body = (
        "## NUL\n"
        "Ã„ <http://example.test/\x00@LLMQuiz(990)[[hidden-uri]]>\n"
        '<input title="\x00@LLMQuiz(992)" data-v="[[hidden tag]]">\n'
        "@LLMQuiz(alpha\x00omega)\n"
        "@LLMQuiz(visible)\n"
        "[[visible answer]]\n"
    )
    text = _synthetic_course(["lia-llm", "lia-loot"], body).replace(
        "\n", "\r\n"
    )
    raw = b"\xef\xbb\xbf" + text.encode("utf-8")
    result = mapper.map_source(raw, source_path="nul-shadow-bom-crlf.md")

    diagnostic = next(
        item
        for item in result["diagnostics"]
        if item["code"] == "nul_replaced_for_commonmark"
    )
    nul_offsets = [index for index, char in enumerate(text) if char == "\x00"]
    assert diagnostic["count"] == len(nul_offsets) == 3
    assert diagnostic["replacement"] == "U+FFFD"
    assert [item["char"] for item in diagnostic["positions"]] == nul_offsets
    for point in diagnostic["positions"]:
        assert point["byte"] >= 3
        assert raw[point["byte"]] == 0

    autolink = next(
        item
        for item in result["protected_spans"]
        if item["kind"] == "html_autolink"
    )
    html_tag = next(
        item
        for item in result["protected_spans"]
        if item["kind"] == "html_tag" and "input" in item["span"]["raw"]
    )
    for owner in (autolink, html_tag):
        span = owner["span"]
        assert "\x00" in span["raw"]
        assert span["raw"] == text[span["char_start"] : span["char_end"]]
        assert raw[span["byte_start"] : span["byte_end"]].decode(
            "utf-8"
        ) == span["raw"]

    macros = {
        item["span"]["raw"]: item
        for item in result["macros"]
        if item["name"] == "LLMQuiz"
    }
    assert set(macros) == {
        "@LLMQuiz(alpha\x00omega)",
        "@LLMQuiz(visible)",
    }
    nul_macro = macros["@LLMQuiz(alpha\x00omega)"]
    assert nul_macro["argument_source"] == "alpha\ufffdomega"
    assert nul_macro["arguments"] == ["alpha\ufffdomega"]
    assert len(result["block_ranges"]["native_quiz"]) == 1
    assert result["block_ranges"]["native_quiz"][0]["syntax_spans"][0][
        "span"
    ]["raw"] == "[[visible answer]]"
    assert result["source"]["bom_bytes"] == 3
    assert result["source"]["newline_style"] == "crlf"
    assert result["source"]["character_count"] == len(text)
    assert result["source"]["byte_count"] == len(raw)


def test_native_quiz_drag_and_protected_near_misses() -> None:
    bt = chr(96)
    source = _synthetic_course(
        ["lia-kachel", "lia-loot"],
        (
            "## A\n"
            "Ordne [->[(A)|B]]\n"
            "\n"
            "    [[indented code]]\n"
            f"{bt * 3}text\n"
            "[[fence body]]\n"
            f"{bt * 3}\n"
            "@Kachelfolge(`[->[(A)|B]]`)\n"
        ),
    )
    result = mapper.map_text(source, source_path="native-drag.md")
    quizzes = result["block_ranges"]["native_quiz"]
    assert len(quizzes) == 1
    assert quizzes[0]["syntax_count"] == 1
    assert quizzes[0]["syntax_spans"][0]["kind"] == "drag_marker"
    assert quizzes[0]["syntax_spans"][0]["span"]["raw"] == "[->[(A)|B]]"
    assert quizzes[0]["complete"] is True
    assert all(
        "indented code" not in item["span"].get("raw", "")
        and "fence body" not in item["span"].get("raw", "")
        for quiz in quizzes
        for item in quiz["syntax_spans"]
    )
    assert len(_target(result, "kachel")["instances"]) == 1
    quiz_span = quizzes[0]["span"]
    assert not any(
        quiz_span["char_start"] < boundary["anchor"]["char_start"] < quiz_span["char_end"]
        for boundary in result["candidates"]["safe_block_boundaries"]
    )


def test_typed_provider_alternatives_and_near_misses() -> None:
    canvas = mapper.map_text(
        _synthetic_course(
            ["lia-canvas-ocr", "lia-loot"],
            "## A\n<canvas class=lia-draw>Zeichne</canvas>\n",
        )
    )
    canvas_instances = _target(canvas, "canvasocr")["instances"]
    assert len(canvas_instances) == 1
    assert canvas_instances[0]["kind"] == "html"
    assert canvas_instances[0]["block_kind"] == "html"
    assert (
        canvas_instances[0]["block_span"]["char_start"]
        < canvas_instances[0]["block_span"]["char_end"]
    )

    llm = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n<!-- data-llm-textarea=true -->\n[[Antwort]]\n"
                "<div data-llm-model=test>KI</div>\n"
            ),
        )
    )
    llm_instances = _target(llm, "llm")["instances"]
    assert {item["kind"] for item in llm_instances} == {
        "typed_metadata", "html_metadata"
    }
    assert all(
        item["block_span"]["char_start"] < item["block_span"]["char_end"]
        for item in llm_instances
    )

    bt = chr(96)
    coordinate = mapper.map_text(
        _synthetic_course(
            ["lia-coordinate", "lia-loot"],
            (
                "## A\n"
                f"{bt * 3}javascript @JSX.Graph\n"
                "const p = board.create('point', [1, 2]);\n"
                f"{bt * 3}\n"
                "<div id=jxgbox></div>\n"
                "@ErzeugePunkt(test)\n"
            ),
        )
    )
    coordinate_instances = _target(coordinate, "coordinate")["instances"]
    assert {item["kind"] for item in coordinate_instances} >= {
        "fenced_call", "macro"
    }
    assert any(item.get("supporting_only") for item in coordinate_instances)

    coordinate_near_misses = [
        "## A\n<div id=jxgbox></div>\n",
        "## A\nboard.create('point', [1,2])\n",
        (
            "## A\n"
            f"{bt * 3}javascript\nboard.create('point', [1,2]);\n{bt * 3}\n"
        ),
        "## A\n@Schloss(board.create; rot)\n",
    ]
    for body in coordinate_near_misses:
        result = mapper.map_text(
            _synthetic_course(["lia-coordinate", "lia-loot"], body)
        )
        assert _target(result, "coordinate")["instances"] == [], body

    kachel = mapper.map_text(
        _synthetic_course(
            ["lia-kachel", "lia-loot"],
            (
                "## A\n"
                "@Kachelfolge(foo)\n"
                "@KachelfolgeN(foo)\n"
                "| A | B |\n|---|---|\n"
                "| @KachelgruppeN(foo) | x |\n"
                "@KachelgruppenCheck(foo)\n"
                "<div class=Kachel>sichtbar</div>\n"
            ),
        )
    )
    kachel_instances = _target(kachel, "kachel")["instances"]
    assert len(kachel_instances) == 4
    assert sum(
        item["block_kind"] == "kachel_table_group"
        for item in kachel_instances
    ) == 1
    group = next(
        item for item in kachel_instances
        if item["block_kind"] == "kachel_table_group"
    )
    assert len(group["macro_ids"]) == 1
    assert group["check_macro_id"] is not None

    for body in (
        "## A\n@Kachel(foo)\n",
        "## A\n@KachelUnsinn(foo)\n",
        "## A\n| @KachelgruppeN(foo) | x |\n",
        "## A\n@KachelgruppenCheck(foo)\n",
        "## A\n<span class=Kachel>nur Attribut</span>\n",
    ):
        result = mapper.map_text(
            _synthetic_course(["lia-kachel", "lia-loot"], body)
        )
        assert _target(result, "kachel")["instances"] == [], body

    prose = mapper.map_text(
        _synthetic_course(
            ["lia-canvas-ocr", "lia-llm", "lia-loot"],
            (
                "## A\nlia-draw und data-llm stehen nur in Prosa.\n"
                "@Schloss(lia-draw; data-llm)\n"
            ),
        )
    )
    assert _target(prose, "canvasocr")["instances"] == []
    assert _target(prose, "llm")["instances"] == []

    substring_import = mapper.map_text(
        _synthetic_course(
            ["not-lia-timer-backup", "lia-loot"],
            "## A\n<!-- data-solution-timer=30s -->\n[[A]]\n",
        )
    )
    assert _target(substring_import, "timer")["direct_import"] is False
    assert _target(substring_import, "timer")["eligible"] is False

    crossed_html = mapper.map_text(
        _synthetic_course(
            ["lia-DynFlex", "lia-loot"],
            (
                "## A\n<article><section class=dynFlex>\n"
                "Inhalt\n</article></section>\n"
            ),
        )
    )
    assert crossed_html["html_summary"]["balanced"] is False
    assert _target(crossed_html, "dynflex")["instances"] == []


def test_protected_and_boundary_hardening() -> None:
    bt = chr(96)
    for width in (1, 2):
        code_span = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## A\nText " + bt * width + "code\n"
                    "@LLMQuiz(1)\n[[fake]]\n"
                    + bt * width + " Ende\n"
                ),
            ),
            source_path=f"multiline-code-{width}.md",
        )
        inline = [
            item for item in code_span["protected_spans"]
            if item["kind"] == "inline_code"
        ]
        assert len(inline) == 1, width
        assert inline[0]["span"]["line_start"] < inline[0]["span"]["line_end"]
        assert "LLMQuiz" not in {item["name"] for item in code_span["macros"]}
        assert code_span["block_ranges"]["native_quiz"] == []
        assert _target(code_span, "llm")["instances"] == []

    container_softbreaks = {
        "list": "## A\n- Text `code\n  @LLMQuiz(1)`\n",
        "blockquote": "## A\n> Text `code\n> @LLMQuiz(1)`\n",
        "lazy_list": (
            "## A\n- Text `code\n@LLMQuiz(1) [[fake]] `\n"
        ),
        "lazy_blockquote": (
            "## A\n> Text `code\n@LLMQuiz(1) [[fake]] `\n"
        ),
        "lazy_multilevel_blockquote": (
            "## A\n>> Text `code\n> @LLMQuiz(1) [[fake]]\n"
            "@LLMQuiz(2) [[fake2]] `\n"
        ),
    }
    for label, body in container_softbreaks.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"code-container-{label}.md",
        )
        inline = [
            item for item in result["protected_spans"]
            if item["kind"] == "inline_code"
        ]
        assert len(inline) == 1, label
        assert inline[0]["span"]["line_start"] < inline[0]["span"]["line_end"]
        assert "LLMQuiz" not in {item["name"] for item in result["macros"]}, label
        assert result["block_ranges"]["native_quiz"] == [], label
        assert _target(result, "llm")["instances"] == [], label

    container_boundaries = {
        "new_list_item": (
            "## A\n- Text `offen\n- @LLMQuiz(1) `\n"
        ),
        "list_blankline": (
            "## A\n- Text `offen\n\n  @LLMQuiz(1) `\n"
        ),
        "list_heading": (
            "## A\n- Text `offen\n  ## B\n  @LLMQuiz(1) `\n"
        ),
        "blockquote_to_heading": (
            "## A\n> Text `offen\n## B\n@LLMQuiz(1) `\n"
        ),
        "blockquote_to_list": (
            "## A\n> Text `offen\n- @LLMQuiz(1) `\n"
        ),
        "nested_blockquote": (
            "## A\n> Text `offen\n>> @LLMQuiz(1) `\n"
        ),
        "blockquote_blankline": (
            "## A\n> Text `offen\n>\n> @LLMQuiz(1) `\n"
        ),
    }
    for label, body in container_boundaries.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"code-container-boundary-{label}.md",
        )
        assert not any(
            item["kind"] == "inline_code"
            for item in result["protected_spans"]
        ), label
        assert "LLMQuiz" in {item["name"] for item in result["macros"]}, label
        assert _target(result, "llm")["instances"], label

    boundary_cases = {
        "blankline": (
            "## A\nText `offen\n\n@LLMQuiz(1) `\n"
        ),
        "heading": (
            "## A\nText `offen\n## B\n@LLMQuiz(1) `\n"
        ),
        "list": (
            "## A\nText `offen\n- @LLMQuiz(1) `\n"
        ),
        "blockquote": (
            "## A\nText `offen\n> @LLMQuiz(1) `\n"
        ),
    }
    for label, body in boundary_cases.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"code-boundary-{label}.md",
        )
        assert not any(
            item["kind"] == "inline_code"
            for item in result["protected_spans"]
        ), label
        assert "LLMQuiz" in {item["name"] for item in result["macros"]}, label
        assert _target(result, "llm")["instances"], label
        if label == "heading":
            assert [item["title"] for item in result["headings"]] == [
                "Testkurs", "A", "B",
            ]

    paragraph_softbreak_nonboundaries = {
        "ordered_two": (
            "## A\nParagraph `code\n"
            "2. @LLMQuiz(991) [[hidden]] `\n"
        ),
        "ordered_ten_digit_one": (
            "## A\nParagraph `code\n"
            "0000000001. @LLMQuiz(992) [[hidden]] `\n"
        ),
        "type_seven_html": (
            "## A\nParagraph `code\n"
            "<span>@LLMQuiz(993)</span> [[hidden]] `\n"
        ),
        "list_nested_ordered_two": (
            "## A\n- Paragraph `code\n"
            "  2. @LLMQuiz(994) [[hidden]] `\n"
        ),
        "quote_ordered_two": (
            "## A\n> Paragraph `code\n"
            "> 2. @LLMQuiz(995) [[hidden]] `\n"
        ),
        "list_to_list": (
            "## A\n- - Paragraph `code\n"
            "    @LLMQuiz(1003) [[hidden]] `\n"
        ),
        "list_to_quote": (
            "## A\n- > Paragraph `code\n"
            "  > @LLMQuiz(1004) [[hidden]] `\n"
        ),
        "quote_to_list": (
            "## A\n> - Paragraph `code\n"
            ">   @LLMQuiz(1005) [[hidden]] `\n"
        ),
        "deep_mixed_explicit": (
            "## A\n> - > - Paragraph `code\n"
            ">   >   @LLMQuiz(1006) [[hidden]] `\n"
        ),
        "deep_mixed_lazy": (
            "## A\n> - > - Paragraph `code\n"
            "@LLMQuiz(1007) [[hidden]] `\n"
        ),
    }
    for label, body in paragraph_softbreak_nonboundaries.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"code-paragraph-softbreak-{label}.md",
        )
        inline = [
            item for item in result["protected_spans"]
            if item["kind"] == "inline_code"
        ]
        assert len(inline) == 1, label
        assert inline[0]["span"]["line_start"] < inline[0]["span"]["line_end"], label
        assert "LLMQuiz" not in {
            item["name"] for item in result["macros"]
        }, label
        assert result["block_ranges"]["native_quiz"] == [], label
        assert _target(result, "llm")["instances"] == [], label

    paragraph_interrupt_boundaries = {
        "ordered_one": (
            "## A\nParagraph `code\n"
            "1. @LLMQuiz(996) [[visible]] `\n"
        ),
        "ordered_nine_digit_one": (
            "## A\nParagraph `code\n"
            "000000001. @LLMQuiz(997) [[visible]] `\n"
        ),
        "blankline": (
            "## A\nParagraph `code\n\n"
            "@LLMQuiz(998) [[visible]] `\n"
        ),
        "bullet": (
            "## A\nParagraph `code\n"
            "- @LLMQuiz(999) [[visible]] `\n"
        ),
        "quote": (
            "## A\nParagraph `code\n"
            "> @LLMQuiz(1000) [[visible]] `\n"
        ),
        "list_nested_ordered_one": (
            "## A\n- Paragraph `code\n"
            "  1. @LLMQuiz(1001) [[visible]] `\n"
        ),
        "type_six_html": (
            "## A\nParagraph `code\n<div></div>\n\n"
            "@LLMQuiz(1002) [[visible]] `\n"
        ),
        "nested_inner_item": (
            "## A\n- - Paragraph `code\n"
            "    - @LLMQuiz(1008) [[visible]] `\n"
        ),
        "mixed_outer_item": (
            "## A\n- > Paragraph `code\n"
            "- @LLMQuiz(1009) [[visible]] `\n"
        ),
        "mixed_deeper_quote": (
            "## A\n- > Paragraph `code\n"
            "  >> @LLMQuiz(1010) [[visible]] `\n"
        ),
        "mixed_container_exit": (
            "## A\n- > Paragraph `code\n## B\n"
            "@LLMQuiz(1011) [[visible]] `\n"
        ),
    }
    for label, body in paragraph_interrupt_boundaries.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"code-paragraph-boundary-{label}.md",
        )
        assert not any(
            item["kind"] == "inline_code"
            for item in result["protected_spans"]
        ), label
        assert "LLMQuiz" in {
            item["name"] for item in result["macros"]
        }, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert _target(result, "llm")["instances"], label

    for index, underline in enumerate(
        ("=", "==", "===", "-", "--", "---"), start=1320
    ):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## A\nParagraph `code\n"
                    f"{underline}\n"
                    f"@LLMQuiz({index}) [[visible]] `\n"
                ),
            ),
            source_path=f"code-setext-boundary-{index}.md",
        )
        assert not any(
            item["kind"] == "inline_code"
            for item in result["protected_spans"]
        ), underline
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({index})"}, underline
        assert len(result["block_ranges"]["native_quiz"]) == 1, underline

    setext_container_boundaries = {
        "quote_single": (
            "## A\n> Paragraph `code\n> =\n"
            "@LLMQuiz(1330) [[visible]] `\n"
        ),
        "list_double": (
            "## A\n- Paragraph `code\n  ==\n"
            "@LLMQuiz(1331) [[visible]] `\n"
        ),
    }
    for label, body in setext_container_boundaries.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"code-setext-container-{label}.md",
        )
        assert not any(
            item["kind"] == "inline_code"
            for item in result["protected_spans"]
        ), label
        assert "LLMQuiz" in {
            item["name"] for item in result["macros"]
        }, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label

    for index, near_miss in enumerate(
        ("= x", "-x", "=-", "    ="), start=1340
    ):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## A\nParagraph `code\n"
                    f"{near_miss}\n"
                    f"@LLMQuiz({index}) [[hidden]] `\n"
                ),
            ),
            source_path=f"code-setext-near-miss-{index}.md",
        )
        inline = [
            item for item in result["protected_spans"]
            if item["kind"] == "inline_code"
        ]
        assert len(inline) == 1, near_miss
        assert "LLMQuiz" not in {
            item["name"] for item in result["macros"]
        }, near_miss
        assert result["block_ranges"]["native_quiz"] == [], near_miss

    for index, underline in enumerate(
        ("=", "==", "===", "-", "--", "---"), start=1350
    ):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## A\nParagraph\n"
                    f"{underline}\n"
                    f"    @LLMQuiz({index})\n"
                    "    [[hidden]]\n"
                ),
            ),
            source_path=f"indented-after-setext-{index}.md",
        )
        assert len(
            [
                item for item in result["protected_spans"]
                if item["kind"] == "indented_code"
            ]
        ) == 1, underline
        assert result["macros"] == [], underline
        assert result["block_ranges"]["native_quiz"] == [], underline

    setext_container_indented = {
        "quote": (
            "## A\n> Paragraph\n> =\n"
            ">     @LLMQuiz(1360)\n>     [[hidden]]\n"
        ),
        "list": (
            "## A\n- Paragraph\n  ==\n"
            "      @LLMQuiz(1361)\n      [[hidden]]\n"
        ),
    }
    for label, body in setext_container_indented.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"indented-after-setext-container-{label}.md",
        )
        assert len(
            [
                item for item in result["protected_spans"]
                if item["kind"] == "indented_code"
            ]
        ) == 1, label
        assert result["macros"] == [], label
        assert result["block_ranges"]["native_quiz"] == [], label

    setext_near_miss_indented = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\nParagraph\n= x\n"
                "    @LLMQuiz(1362)\n    [[visible]]\n"
            ),
        ),
        source_path="indented-after-setext-near-miss.md",
    )
    assert not any(
        item["kind"] == "indented_code"
        for item in setext_near_miss_indented["protected_spans"]
    )
    assert "LLMQuiz" in {
        item["name"] for item in setext_near_miss_indented["macros"]
    }
    assert len(setext_near_miss_indented["block_ranges"]["native_quiz"]) == 1

    escaped = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            "## A\nText \\` @LLMQuiz(1) \\`\n",
        ),
        source_path="escaped-backticks.md",
    )
    assert not any(
        item["kind"] == "inline_code"
        for item in escaped["protected_spans"]
    )
    assert "LLMQuiz" in {item["name"] for item in escaped["macros"]}
    even_source = _synthetic_course(
        ["lia-loot"], "## A\nText \\\\`code`\n"
    )
    even_escape = mapper.map_text(
        even_source,
        source_path="even-escaped-backtick.md",
    )
    even_spans = [
        item for item in even_escape["protected_spans"]
        if item["kind"] == "inline_code"
    ]
    assert len(even_spans) == 1
    even_span = even_spans[0]["span"]
    assert even_source[
        even_span["char_start"] : even_span["char_end"]
    ] == "`code`"

    finite_tag_before_backtick_cases = {
        "root_single": (
            "## A\n<span data-x=" + chr(34) + bt + chr(34) + ">\n"
            "@LLMQuiz(1370) [[visible]] " + bt + "\n"
        ),
        "root_paired": (
            "## A\n<span data-x=" + chr(34) + bt + chr(34) + "></span>\n"
            "@LLMQuiz(1371) [[visible]] " + bt + "\n"
        ),
        "quote_paired": (
            "## A\n> <span data-x=" + chr(34) + bt + chr(34) + "></span>\n"
            "@LLMQuiz(1372) [[visible]] " + bt + "\n"
        ),
        "list_paired": (
            "## A\n- <span data-x=" + chr(34) + bt + chr(34) + "></span>\n"
            "@LLMQuiz(1373) [[visible]] " + bt + "\n"
        ),
        "paragraph_inline": (
            "## A\nText <span data-x=" + chr(34) + bt + chr(34) + "></span>\n"
            "@LLMQuiz(1374) [[visible]] " + bt + "\n"
        ),
    }
    for label, body in finite_tag_before_backtick_cases.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"html-tag-before-backtick-{label}.md",
        )
        assert not any(
            item["kind"] == "inline_code"
            for item in result["protected_spans"]
        ), label
        assert "LLMQuiz" in {
            item["name"] for item in result["macros"]
        }, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert any(
            item["kind"] == "html_tag"
            for item in result["protected_spans"]
        ), label

    finite_autolink_before_backtick_cases = {
        "uri": (
            "## A\n<http://example.test/" + bt + ">\n"
            "@LLMQuiz(1375) [[visible]] " + bt + "\n"
        ),
        "email": (
            "## A\n<foo" + bt + "bar@example.org>\n"
            "@LLMQuiz(1376) [[visible]] " + bt + "\n"
        ),
        "even_escaped_uri": (
            "## A\n" + chr(92) * 2 + "<http://example.test/" + bt + ">\n"
            "@LLMQuiz(1377) [[visible]] " + bt + "\n"
        ),
    }
    for label, body in finite_autolink_before_backtick_cases.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"autolink-before-backtick-{label}.md",
        )
        assert not any(
            item["kind"] == "inline_code"
            for item in result["protected_spans"]
        ), label
        assert "LLMQuiz" in {
            item["name"] for item in result["macros"]
        }, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert any(
            item["kind"] == "html_autolink"
            for item in result["protected_spans"]
        ), label

    even_escaped_type7 = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n" + chr(92) * 2 + "<span data-x="
                + chr(34) + bt + chr(34) + "></span>\n"
                "@LLMQuiz(1378) [[visible]] " + bt + "\n"
            ),
        ),
        source_path="even-escaped-type7-before-backtick.md",
    )
    assert not any(
        item["kind"] == "inline_code"
        for item in even_escaped_type7["protected_spans"]
    )
    assert "LLMQuiz" in {
        item["name"] for item in even_escaped_type7["macros"]
    }
    assert len(even_escaped_type7["block_ranges"]["native_quiz"]) == 1
    assert any(
        item["kind"] == "html_tag"
        for item in even_escaped_type7["protected_spans"]
    )

    odd_escaped_finite_cases = {
        "type7": (
            "## A\n" + chr(92) + "<span data-x="
            + chr(34) + bt + chr(34) + "></span>\n"
            "@LLMQuiz(1380) [[hidden]] " + bt + "\n"
        ),
        "autolink": (
            "## A\n" + chr(92) + "<http://example.test/" + bt + ">\n"
            "@LLMQuiz(1381) [[hidden]] " + bt + "\n"
        ),
    }
    for label, body in odd_escaped_finite_cases.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"odd-escaped-finite-{label}.md",
        )
        inline = [
            item for item in result["protected_spans"]
            if item["kind"] == "inline_code"
        ]
        assert len(inline) == 1, label
        assert "LLMQuiz" not in {
            item["name"] for item in result["macros"]
        }, label
        assert result["block_ranges"]["native_quiz"] == [], label
        assert not any(
            item["kind"] in {"html_tag", "html_autolink"}
            for item in result["protected_spans"]
        ), label

    code_before_finite_cases = {
        "type7_without_backtick": (
            "## A\nParagraph `code\n<span data-x="
            + chr(34) + "value" + chr(34) + "></span> "
            "@LLMQuiz(1390) [[hidden]] `\n"
        ),
        "autolink": (
            "## A\nParagraph `code\n"
            "<http://example.test/path> "
            "@LLMQuiz(1391) [[hidden]] `\n"
        ),
    }
    for label, body in code_before_finite_cases.items():
        result = mapper.map_text(
            _synthetic_course(["lia-llm", "lia-loot"], body),
            source_path=f"backtick-before-finite-{label}.md",
        )
        inline = [
            item for item in result["protected_spans"]
            if item["kind"] == "inline_code"
        ]
        assert len(inline) == 1, label
        assert inline[0]["span"]["line_start"] < inline[0]["span"]["line_end"], label
        assert "LLMQuiz" not in {
            item["name"] for item in result["macros"]
        }, label
        assert result["block_ranges"]["native_quiz"] == [], label
        assert not any(
            item["kind"] in {"html_tag", "html_autolink"}
            for item in result["protected_spans"]
        ), label

    code_closes_inside_finite_lookalike_cases = {
        "type7": (
            "## A\nParagraph `code\n<span data-x="
            + chr(34) + bt + chr(34) + "></span> "
            "@LLMQuiz(1392) [[visible]] `\n"
        ),
        "autolink": (
            "## A\nParagraph `code\n"
            "<http://example.test/`> "
            "@LLMQuiz(1393) [[visible]] `\n"
        ),
    }
    for label, body in code_closes_inside_finite_lookalike_cases.items():
        source = _synthetic_course(["lia-llm", "lia-loot"], body)
        result = mapper.map_text(
            source,
            source_path=f"code-closes-inside-finite-lookalike-{label}.md",
        )
        inline = [
            item for item in result["protected_spans"]
            if item["kind"] == "inline_code"
        ]
        assert len(inline) == 1, label
        macro = next(
            item for item in result["macros"]
            if item["name"] == "LLMQuiz"
        )
        assert inline[0]["span"]["char_end"] < macro["span"]["char_start"], label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert _target(result, "llm")["instances"], label

    raw_html = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n<pre>@LLMQuiz(1)\n[[pre fake]]</pre>\n"
                "<script>@LLMQuiz(2)\n[[script fake]]</script>\n"
                "<style>@LLMQuiz(3)\n[[style fake]]</style>\n"
                '<TeXtArEa\n rows="2">@LLMQuiz(4)\n'
                "[[textarea fake]]</TEXTAREA>\n"
            ),
        ),
        source_path="raw-html-protected.md",
    )
    raw_blocks = [
        item for item in raw_html["protected_spans"]
        if item["kind"] == "raw_html"
    ]
    assert {item["tag"] for item in raw_blocks} == {
        "pre", "script", "style", "textarea",
    }
    assert raw_html["macros"] == []
    assert raw_html["block_ranges"]["native_quiz"] == []
    assert _target(raw_html, "llm")["instances"] == []

    block_closer_line_cases = (
        ("raw_html", "<script>", "</script>", "type-one"),
        (
            "html_processing_instruction", "<?course", "?>",
            "processing-instruction",
        ),
        ("html_comment", "<!--", "-->", "comment"),
        ("html_declaration", "<!ELEMENT", ">", "declaration"),
        ("html_cdata", "<![CDATA[", "]]>", "cdata"),
    )
    for index, (kind, opener, closer, label) in enumerate(
        block_closer_line_cases, start=1010
    ):
        source = _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\n{opener}\ninside\n"
                f"{closer} @LLMQuiz({index}) [[hidden]]\n"
                f"@LLMQuiz({index + 100})\n[[visible]]\n"
            ),
        )
        result = mapper.map_text(
            source,
            source_path=f"raw-html-block-closer-line-{label}.md",
        )
        spans = [
            item for item in result["protected_spans"]
            if item["kind"] == kind
        ]
        assert len(spans) == 1, label
        assert spans[0]["block_start"] is True, label
        assert spans[0]["closed"] is True, label
        assert spans[0]["span"]["char_end"] == source.index(
            f"@LLMQuiz({index + 100})"
        ), label
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({index + 100})"}, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert len(_target(result, "llm")["instances"]) == 1, label

    inline_special_exact_cases = (
        (
            "html_processing_instruction",
            "<?course @LLMQuiz(1110) ?>",
            "processing-instruction",
        ),
        (
            "html_comment", "<!-- @LLMQuiz(1111) -->", "comment",
        ),
        (
            "html_declaration", "<!A@LLMQuiz(1112)>",
            "single-letter-declaration",
        ),
        (
            "html_declaration", "<!ABC123 @LLMQuiz(1113)>",
            "declaration-contents",
        ),
        (
            "html_cdata", "<![CDATA[@LLMQuiz(1114)]]>", "cdata",
        ),
    )
    for index, (kind, markup, label) in enumerate(
        inline_special_exact_cases, start=1210
    ):
        source = _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\nText {markup} @LLMQuiz({index})\n"
                "[[visible]]\n"
            ),
        )
        result = mapper.map_text(
            source,
            source_path=f"raw-html-inline-exact-{label}.md",
        )
        spans = [
            item for item in result["protected_spans"]
            if item["kind"] == kind
        ]
        assert len(spans) == 1, label
        assert spans[0]["block_start"] is False, label
        assert spans[0]["closed"] is True, label
        span = spans[0]["span"]
        assert source[span["char_start"] : span["char_end"]] == markup, label
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({index})"}, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert len(_target(result, "llm")["instances"]) == 1, label

    raw_type_one_closed_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\n<script\n"
            "@LLMQuiz(40)\n[[hidden script quiz]]\n</script>\n"
            "@LLMQuiz(41)\n"
        ),
    )
    raw_type_one_closed = mapper.map_text(
        raw_type_one_closed_source,
        source_path="raw-html-type-one-incomplete-opener.md",
    )
    closed_type_one_spans = [
        item for item in raw_type_one_closed["protected_spans"]
        if item["kind"] == "raw_html"
    ]
    assert len(closed_type_one_spans) == 1
    assert closed_type_one_spans[0]["tag"] == "script"
    assert closed_type_one_spans[0]["closed"] is True
    assert {
        item["span"]["raw"]
        for item in raw_type_one_closed["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(41)"}
    assert raw_type_one_closed["block_ranges"]["native_quiz"] == []
    assert len(_target(raw_type_one_closed, "llm")["instances"]) == 1

    raw_type_one_unclosed_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        "## A\n<textarea\n@LLMQuiz(42)\n[[hidden textarea quiz]]\n",
    )
    raw_type_one_unclosed = mapper.map_text(
        raw_type_one_unclosed_source,
        source_path="raw-html-type-one-unclosed-opener.md",
    )
    unclosed_type_one_spans = [
        item for item in raw_type_one_unclosed["protected_spans"]
        if item["kind"] == "raw_html"
    ]
    assert len(unclosed_type_one_spans) == 1
    assert unclosed_type_one_spans[0]["tag"] == "textarea"
    assert unclosed_type_one_spans[0]["closed"] is False
    assert unclosed_type_one_spans[0]["span"]["char_end"] == len(
        raw_type_one_unclosed_source
    )
    assert raw_type_one_unclosed["macros"] == []
    assert raw_type_one_unclosed["block_ranges"]["native_quiz"] == []
    assert any(
        item["code"] == "unterminated_raw_html"
        and item["tag"] == "textarea"
        for item in raw_type_one_unclosed["diagnostics"]
    )

    raw_type_one_containers = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n> <pre\n> @LLMQuiz(43)\n> </pre>\n"
                "- <style\tdata-kind=quiz\n  @LLMQuiz(44)\n  </style>\n"
                "- > <textarea\n  > @LLMQuiz(45)\n  > </textarea>\n"
                "@LLMQuiz(46)\n"
            ),
        ),
        source_path="raw-html-type-one-containers.md",
    )
    container_raw_spans = [
        item for item in raw_type_one_containers["protected_spans"]
        if item["kind"] == "raw_html"
    ]
    assert [item["tag"] for item in container_raw_spans] == [
        "pre", "style", "textarea",
    ]
    assert all(item["closed"] is True for item in container_raw_spans)
    assert {
        item["span"]["raw"]
        for item in raw_type_one_containers["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(46)"}
    assert raw_type_one_containers["block_ranges"]["native_quiz"] == []

    raw_type_one_false_starts = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\nText <script>@LLMQuiz(47)</script>\n"
                "\\<style>@LLMQuiz(48)</style>\n"
            ),
        ),
        source_path="raw-html-type-one-false-starts.md",
    )
    assert not any(
        item["kind"] == "raw_html"
        for item in raw_type_one_false_starts["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in raw_type_one_false_starts["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(47)", "@LLMQuiz(48)"}

    special_markup_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\nText <?course\n"
            "continued <!-- nested-looking delimiter -->\n"
            "@LLMQuiz(60)\n[[hidden pi quiz]]\n?> Ende\n"
            "Text <!ELEMENT br\n"
            "@LLMQuiz(61)\n[[hidden declaration quiz]]\ncontinued > Ende\n"
            "Text <![CDATA[\n"
            "@LLMQuiz(62)\n[[hidden cdata quiz]]\n]]> Ende\n"
            "@LLMQuiz(63)\nSichtbar [[ok]]\n"
        ),
    )
    special_markup = mapper.map_text(
        special_markup_source,
        source_path="commonmark-special-html-closed.md",
    )
    special_markup_spans = [
        item for item in special_markup["protected_spans"]
        if item["kind"] in {
            "html_processing_instruction",
            "html_declaration",
            "html_cdata",
        }
    ]
    assert [item["kind"] for item in special_markup_spans] == [
        "html_processing_instruction",
        "html_declaration",
        "html_cdata",
    ]
    assert all(item["closed"] is True for item in special_markup_spans)
    assert not any(
        item["kind"] == "html_comment"
        for item in special_markup["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in special_markup["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(63)"}
    assert len(special_markup["block_ranges"]["native_quiz"]) == 1
    assert len(_target(special_markup, "llm")["instances"]) == 1

    unclosed_special_cases = [
        (
            "html_processing_instruction",
            "unterminated_html_processing_instruction",
            "## A\n<?course\n@LLMQuiz(64)\n[[hidden pi quiz]]\n",
        ),
        (
            "html_declaration",
            "unterminated_html_declaration",
            "## A\n> <!DOCTYPE\n> @LLMQuiz(65)\n> [[hidden declaration quiz]]\n",
        ),
        (
            "html_cdata",
            "unterminated_html_cdata",
            "## A\n- <![CDATA[\n  @LLMQuiz(66)\n  [[hidden cdata quiz]]\n",
        ),
    ]
    for html_kind, diagnostic_code, body in unclosed_special_cases:
        source = _synthetic_course(["lia-llm", "lia-loot"], body)
        result = mapper.map_text(
            source, source_path=f"commonmark-{html_kind}-unclosed.md"
        )
        spans = [
            item for item in result["protected_spans"]
            if item["kind"] == html_kind
        ]
        assert len(spans) == 1, html_kind
        assert spans[0]["closed"] is False, html_kind
        assert spans[0]["span"]["char_end"] == len(source), html_kind
        assert result["macros"] == [], html_kind
        assert result["block_ranges"]["native_quiz"] == [], html_kind
        assert any(
            item["code"] == diagnostic_code
            for item in result["diagnostics"]
        ), html_kind

    container_exit_cases = [
        (
            "quote-type-one",
            "raw_html",
            "unterminated_raw_html",
            (
                "## A\n> <script>\n"
                "> @LLMQuiz(510)\n> [[hidden quote type one]]\n"
                "Outside @LLMQuiz(511)\n[[visible 511]]\n"
            ),
            "@LLMQuiz(511)",
        ),
        (
            "list-processing-instruction",
            "html_processing_instruction",
            "unterminated_html_processing_instruction",
            (
                "## A\n- <?course\n"
                "  @LLMQuiz(512)\n  [[hidden list pi]]\n"
                "Outside @LLMQuiz(513)\n[[visible 513]]\n"
            ),
            "@LLMQuiz(513)",
        ),
        (
            "quote-declaration",
            "html_declaration",
            "unterminated_html_declaration",
            (
                "## A\n> <!DOCTYPE\n"
                "> @LLMQuiz(514)\n> [[hidden quote declaration]]\n"
                "Outside @LLMQuiz(515)\n[[visible 515]]\n"
            ),
            "@LLMQuiz(515)",
        ),
        (
            "nested-cdata",
            "html_cdata",
            "unterminated_html_cdata",
            (
                "## A\n> - <![CDATA[\n"
                ">   @LLMQuiz(516)\n"
                ">   [[hidden nested cdata]]\n"
                "Outside @LLMQuiz(517)\n[[visible 517]]\n"
            ),
            "@LLMQuiz(517)",
        ),
        (
            "list-comment",
            "html_comment",
            "unterminated_html_comment",
            (
                "## A\n- <!-- open\n"
                "  @LLMQuiz(518)\n  [[hidden list comment]]\n"
                "Outside @LLMQuiz(519)\n[[visible 519]]\n"
            ),
            "@LLMQuiz(519)",
        ),
        (
            "list-blank-type-one",
            "raw_html",
            "unterminated_raw_html",
            (
                "## A\n- <style>\n\n"
                "  @LLMQuiz(520)\n  [[hidden after list blank]]\n"
                "Outside @LLMQuiz(521)\n[[visible 521]]\n"
            ),
            "@LLMQuiz(521)",
        ),
        (
            "reverse-nested-type-one",
            "raw_html",
            "unterminated_raw_html",
            (
                "## A\n- > <pre>\n"
                "  > @LLMQuiz(522)\n"
                "  > [[hidden reverse nested type one]]\n"
                "Outside @LLMQuiz(523)\n[[visible 523]]\n"
            ),
            "@LLMQuiz(523)",
        ),
        (
            "implicit-list-type-one",
            "raw_html",
            "unterminated_raw_html",
            (
                "## A\n- item\n\n  <script>\n"
                "  @LLMQuiz(550)\n  [[hidden implicit type one]]\n"
                "Outside @LLMQuiz(551)\n[[visible 551]]\n"
            ),
            "@LLMQuiz(551)",
        ),
        (
            "implicit-quote-list-pi",
            "html_processing_instruction",
            "unterminated_html_processing_instruction",
            (
                "## A\n> - item\n>\n>   <?course\n"
                ">   @LLMQuiz(552)\n"
                ">   [[hidden implicit quote list pi]]\n"
                "Outside @LLMQuiz(553)\n[[visible 553]]\n"
            ),
            "@LLMQuiz(553)",
        ),
        (
            "implicit-list-quote-comment",
            "html_comment",
            "unterminated_html_comment",
            (
                "## A\n- > item\n  > <!-- open\n"
                "  > @LLMQuiz(554)\n"
                "  > [[hidden implicit list quote comment]]\n"
                "Outside @LLMQuiz(555)\n[[visible 555]]\n"
            ),
            "@LLMQuiz(555)",
        ),
        (
            "implicit-nested-list-cdata",
            "html_cdata",
            "unterminated_html_cdata",
            (
                "## A\n- outer\n  - inner\n\n    <![CDATA[\n"
                "    @LLMQuiz(556)\n"
                "    [[hidden implicit nested cdata]]\n"
                "Outside @LLMQuiz(557)\n[[visible 557]]\n"
            ),
            "@LLMQuiz(557)",
        ),
        (
            "implicit-list-tab-declaration",
            "html_declaration",
            "unterminated_html_declaration",
            (
                "## A\n- item\n\t<!DOCTYPE\n"
                "\t@LLMQuiz(558)\n\t[[hidden tab declaration]]\n"
                "Outside @LLMQuiz(559)\n[[visible 559]]\n"
            ),
            "@LLMQuiz(559)",
        ),
    ]
    for label, html_kind, diagnostic_code, body, visible_macro in (
        container_exit_cases
    ):
        source = _synthetic_course(["lia-llm", "lia-loot"], body)
        result = mapper.map_text(
            source,
            source_path=f"commonmark-container-exit-{label}.md",
        )
        spans = [
            item
            for item in result["protected_spans"]
            if item["kind"] == html_kind
        ]
        assert len(spans) == 1, label
        assert spans[0]["closed"] is False, label
        outside = source.index("Outside ")
        assert spans[0]["span"]["char_end"] == outside, label
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {visible_macro}, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label
        assert any(
            item["code"] == diagnostic_code
            for item in result["diagnostics"]
        ), label

    implicit_closed_cases = [
        (
            "raw_html",
            "<script>",
            "</script>",
            "type one",
        ),
        (
            "html_processing_instruction",
            "<?course",
            "?>",
            "processing instruction",
        ),
        (
            "html_comment",
            "<!-- open",
            "-->",
            "comment",
        ),
        (
            "html_cdata",
            "<![CDATA[",
            "]]>",
            "cdata",
        ),
        (
            "html_declaration",
            "<!DOCTYPE",
            ">",
            "declaration",
        ),
    ]
    for index, (html_kind, opener, closer, label) in enumerate(
        implicit_closed_cases
    ):
        hidden_number = 560 + index * 2
        visible_number = hidden_number + 1
        source = _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n- item\n\n"
                f"  {opener}\n"
                f"  @LLMQuiz({hidden_number})\n"
                f"  [[hidden implicit closed {label}]]\n"
                f"  {closer}\n"
                f"  @LLMQuiz({visible_number})\n"
                f"  [[visible implicit closed {label}]]\n"
            ),
        )
        result = mapper.map_text(
            source,
            source_path=f"commonmark-implicit-list-closed-{label}.md",
        )
        spans = [
            item
            for item in result["protected_spans"]
            if item["kind"] == html_kind
        ]
        assert len(spans) == 1, label
        assert spans[0]["closed"] is True, label
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({visible_number})"}, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label

    for index, (html_kind, opener, closer, label) in enumerate(
        implicit_closed_cases
    ):
        hidden_number = 590 + index * 2
        visible_number = hidden_number + 1
        source = _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n> - item\n"
                f">   {opener}\n"
                f">   {closer}\n"
                ">\n"
                f">   {opener}\n"
                f">   @LLMQuiz({hidden_number})\n"
                f">   [[hidden after blank {label}]]\n"
                f"> Outside @LLMQuiz({visible_number})\n"
                f"> [[visible outside list {label}]]\n"
            ),
        )
        result = mapper.map_text(
            source,
            source_path=(
                f"commonmark-quote-list-blank-between-{label}.md"
            ),
        )
        spans = [
            item
            for item in result["protected_spans"]
            if item["kind"] == html_kind
        ]
        assert len(spans) == 2, label
        assert [item["closed"] for item in spans] == [True, False], label
        assert spans[1]["span"]["char_end"] == source.index(
            "> Outside"
        ), label
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({visible_number})"}, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label

    non_interrupting_ordered_html = [
        (
            "raw_html",
            "<script>",
            "ordered two type one",
            "2. text",
        ),
        (
            "html_processing_instruction",
            "<?course",
            "ordered two processing instruction",
            "2. text",
        ),
        (
            "html_comment",
            "<!-- open",
            "empty bullet comment",
            "-     ",
        ),
    ]
    for index, (html_kind, opener, label, paragraph_line) in enumerate(
        non_interrupting_ordered_html
    ):
        source = _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\nRunning paragraph\n{paragraph_line}\n"
                f"   {opener}\n"
                f"   @LLMQuiz({610 + index * 2})\n"
                f"Outside @LLMQuiz({611 + index * 2})\n"
                f"[[hidden root {label}]]\n"
            ),
        )
        result = mapper.map_text(
            source,
            source_path=f"commonmark-{label.replace(' ', '-')}.md",
        )
        span = next(
            item
            for item in result["protected_spans"]
            if item["kind"] == html_kind
        )
        assert span["closed"] is False, label
        assert span["span"]["char_end"] == len(source), label
        assert result["macros"] == [], label
        assert result["block_ranges"]["native_quiz"] == [], label

    interrupting_list_html = {
        "ordered-one": (
            "Running paragraph\n1. text\n   <script>\n"
            "   @LLMQuiz(620)\n"
            "Outside @LLMQuiz(621)\n[[visible 621]]\n"
        ),
        "ordered-two-after-blank": (
            "Running paragraph\n\n2. text\n   <script>\n"
            "   @LLMQuiz(622)\n"
            "Outside @LLMQuiz(623)\n[[visible 623]]\n"
        ),
        "unordered": (
            "Running paragraph\n- text\n  <script>\n"
            "  @LLMQuiz(624)\n"
            "Outside @LLMQuiz(625)\n[[visible 625]]\n"
        ),
        "ordered-two-under-new-quote": (
            "Running paragraph\n> 2. text\n>    <script>\n"
            ">    @LLMQuiz(626)\n"
            "> Outside @LLMQuiz(627)\n> [[visible 627]]\n"
        ),
        "ordered-two-under-unordered": (
            "Running paragraph\n- 2. text\n     <script>\n"
            "     @LLMQuiz(628)\n"
            "Outside @LLMQuiz(629)\n[[visible 629]]\n"
        ),
    }
    for label, body in interrupting_list_html.items():
        source = _synthetic_course(
            ["lia-llm", "lia-loot"], "## A\n" + body
        )
        result = mapper.map_text(
            source,
            source_path=f"commonmark-list-interrupt-{label}.md",
        )
        span = next(
            item
            for item in result["protected_spans"]
            if item["kind"] == "raw_html"
        )
        assert span["closed"] is False, label
        outside_marker = (
            "> Outside "
            if label == "ordered-two-under-new-quote"
            else "Outside "
        )
        assert span["span"]["char_end"] == source.index(
            outside_marker, span["span"]["char_start"]
        ), label
        assert len(
            [
                item
                for item in result["macros"]
                if item["name"] == "LLMQuiz"
            ]
        ) == 1, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label

    lazy_ordered_context_cases = {
        "list": (
            "- paragraph\n  2. lazy continuation\n"
            "  <script>\n  @LLMQuiz(640)\n"
            "Outside @LLMQuiz(641)\n[[visible 641]]\n"
        ),
        "quote-list": (
            "> - paragraph\n>   2. lazy quote/list continuation\n"
            ">   <script>\n>   @LLMQuiz(642)\n"
            "> Outside @LLMQuiz(643)\n> [[visible 643]]\n"
        ),
    }
    for label, body in lazy_ordered_context_cases.items():
        source = _synthetic_course(
            ["lia-llm", "lia-loot"], "## A\n" + body
        )
        result = mapper.map_text(
            source,
            source_path=f"commonmark-lazy-ordered-two-{label}.md",
        )
        span = next(
            item
            for item in result["protected_spans"]
            if item["kind"] == "raw_html"
        )
        outside_marker = "> Outside " if label == "quote-list" else "Outside "
        assert span["closed"] is False, label
        assert span["span"]["char_end"] == source.index(
            outside_marker, span["span"]["char_start"]
        ), label
        assert len(
            [
                item
                for item in result["macros"]
                if item["name"] == "LLMQuiz"
            ]
        ) == 1, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label

    thematic_root_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\nRunning paragraph\n- - -\n"
            "  <script>\n  @LLMQuiz(630)\n"
            "Outside @LLMQuiz(631)\n[[hidden root thematic]]\n"
        ),
    )
    thematic_root = mapper.map_text(
        thematic_root_source,
        source_path="commonmark-thematic-root-before-html.md",
    )
    thematic_root_span = next(
        item
        for item in thematic_root["protected_spans"]
        if item["kind"] == "raw_html"
    )
    assert thematic_root_span["closed"] is False
    assert thematic_root_span["span"]["char_end"] == len(
        thematic_root_source
    )
    assert thematic_root["macros"] == []
    assert thematic_root["block_ranges"]["native_quiz"] == []

    thematic_container_cases = {
        "quote": (
            "Running paragraph\n> * * *\n>  <script>\n"
            ">  @LLMQuiz(632)\n"
            "> Outside @LLMQuiz(633)\n> [[hidden quote thematic]]\n"
            "Root @LLMQuiz(634)\n[[visible 634]]\n"
        ),
        "list": (
            "Running paragraph\n- item\n  _ _ _\n  <script>\n"
            "  @LLMQuiz(635)\n"
            "  Outside @LLMQuiz(636)\n  [[hidden list thematic]]\n"
            "Root @LLMQuiz(637)\n[[visible 637]]\n"
        ),
    }
    for label, body in thematic_container_cases.items():
        source = _synthetic_course(
            ["lia-llm", "lia-loot"], "## A\n" + body
        )
        result = mapper.map_text(
            source,
            source_path=f"commonmark-thematic-{label}-before-html.md",
        )
        span = next(
            item
            for item in result["protected_spans"]
            if item["kind"] == "raw_html"
        )
        assert span["closed"] is False, label
        assert span["span"]["char_end"] == source.index(
            "Root ", span["span"]["char_start"]
        ), label
        assert len(
            [
                item
                for item in result["macros"]
                if item["name"] == "LLMQuiz"
            ]
        ) == 1, label
        assert len(result["block_ranges"]["native_quiz"]) == 1, label

    closer_after_quote_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\n> <?course\n> @LLMQuiz(530)\n"
            "?> Outside @LLMQuiz(531)\n[[visible 531]]\n"
        ),
    )
    closer_after_quote = mapper.map_text(
        closer_after_quote_source,
        source_path="commonmark-closer-after-quote-exit.md",
    )
    quote_pi = next(
        item
        for item in closer_after_quote["protected_spans"]
        if item["kind"] == "html_processing_instruction"
    )
    assert quote_pi["closed"] is False
    assert quote_pi["span"]["char_end"] == closer_after_quote_source.index(
        "?> Outside"
    )
    assert {
        item["span"]["raw"]
        for item in closer_after_quote["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(531)"}
    assert len(closer_after_quote["block_ranges"]["native_quiz"]) == 1

    lazy_inline_comment = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n> Text <!-- @LLMQuiz(540)\n"
                "lazy @LLMQuiz(541) --> @LLMQuiz(542)\n"
                "[[visible after lazy comment]]\n"
            ),
        ),
        source_path="commonmark-inline-comment-lazy-quote.md",
    )
    lazy_comments = [
        item
        for item in lazy_inline_comment["protected_spans"]
        if item["kind"] == "html_comment"
    ]
    assert len(lazy_comments) == 1
    assert lazy_comments[0]["closed"] is True
    assert {
        item["span"]["raw"]
        for item in lazy_inline_comment["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(542)"}
    assert len(lazy_inline_comment["block_ranges"]["native_quiz"]) == 1

    root_unclosed_comment_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        "## A\n<!-- root open\n@LLMQuiz(550)\n[[hidden root comment]]\n",
    )
    root_unclosed_comment = mapper.map_text(
        root_unclosed_comment_source,
        source_path="commonmark-root-comment-unclosed.md",
    )
    root_comment = next(
        item
        for item in root_unclosed_comment["protected_spans"]
        if item["kind"] == "html_comment"
    )
    assert root_comment["closed"] is False
    assert root_comment["span"]["char_end"] == len(
        root_unclosed_comment_source
    )
    assert root_unclosed_comment["macros"] == []
    assert root_unclosed_comment["block_ranges"]["native_quiz"] == []

    html_block_followers = {
        "processing-instruction": (
            "<?course\nraw html\n?>\n"
            "    @LLMQuiz(560)\n    [[hidden after pi]]\n"
        ),
        "comment": (
            "<!-- open\nraw html\n-->\n"
            "    @LLMQuiz(561)\n    [[hidden after comment]]\n"
        ),
        "cdata": (
            "<![CDATA[\nraw html\n]]>\n"
            "    @LLMQuiz(562)\n    [[hidden after cdata]]\n"
        ),
        "declaration": (
            "<!DOCTYPE\nraw html\n>\n"
            "    @LLMQuiz(563)\n    [[hidden after declaration]]\n"
        ),
        "type-one": (
            "<script>\nraw html\n</script>\n"
            "    @LLMQuiz(564)\n    [[hidden after type one]]\n"
        ),
        "fence": (
            f"{bt * 3}text\nraw fence\n{bt * 3}\n"
            "    @LLMQuiz(565)\n    [[hidden after fence]]\n"
        ),
        "heading": (
            "### Block heading\n"
            "    @LLMQuiz(566)\n    [[hidden after heading]]\n"
        ),
    }
    for label, body in html_block_followers.items():
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                "## Block follower\n" + body,
            ),
            source_path=f"indented-after-{label}.md",
        )
        indented = [
            item
            for item in result["protected_spans"]
            if item["kind"] == "indented_code"
        ]
        assert len(indented) == 1, label
        assert "LLMQuiz" not in {
            item["name"] for item in result["macros"]
        }, label
        assert result["block_ranges"]["native_quiz"] == [], label

    type_six_inside = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Type six\nRunning paragraph\n<div>\nraw html\n"
                "    @LLMQuiz(570)\n    [[not indented code in type six]]\n"
                "\n@LLMQuiz(571)\n"
            ),
        ),
        source_path="commonmark-type-six-content.md",
    )
    assert not any(
        item["kind"] == "indented_code"
        for item in type_six_inside["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in type_six_inside["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(570)", "@LLMQuiz(571)"}

    type_six_then_code = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Type six then code\n<div>\nraw html\n\n"
                "    @LLMQuiz(572)\n    [[hidden after type six]]\n"
            ),
        ),
        source_path="commonmark-type-six-then-code.md",
    )
    assert len(
        [
            item
            for item in type_six_then_code["protected_spans"]
            if item["kind"] == "indented_code"
        ]
    ) == 1
    assert type_six_then_code["macros"] == []
    assert type_six_then_code["block_ranges"]["native_quiz"] == []

    implicit_list_type_six_exit = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Implicit list type six\n- item\n\n"
                "  <div>\n  raw html\n"
                "### Outside boundary\n"
                "    @LLMQuiz(573)\n"
                "    [[hidden after implicit list type six]]\n"
            ),
        ),
        source_path="commonmark-implicit-list-type-six-exit.md",
    )
    assert len(
        [
            item
            for item in implicit_list_type_six_exit["protected_spans"]
            if item["kind"] == "indented_code"
        ]
    ) == 1
    assert implicit_list_type_six_exit["macros"] == []
    assert (
        implicit_list_type_six_exit["block_ranges"]["native_quiz"] == []
    )

    type_seven_paragraph = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Type seven paragraph\nRunning paragraph\n<a></a>\n"
                "    @LLMQuiz(580)\n"
                "    [[visible type seven continuation]]\n"
            ),
        ),
        source_path="commonmark-type-seven-paragraph.md",
    )
    assert not any(
        item["kind"] == "indented_code"
        for item in type_seven_paragraph["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in type_seven_paragraph["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(580)"}
    assert type_seven_paragraph["block_ranges"]["native_quiz"]

    type_seven_then_code = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Type seven block\n<a></a>\n\n"
                "    @LLMQuiz(581)\n"
                "    [[hidden after type seven blank]]\n"
            ),
        ),
        source_path="commonmark-type-seven-then-code.md",
    )
    assert len(
        [
            item
            for item in type_seven_then_code["protected_spans"]
            if item["kind"] == "indented_code"
        ]
    ) == 1
    assert type_seven_then_code["macros"] == []
    assert type_seven_then_code["block_ranges"]["native_quiz"] == []

    unclosed_inline_special = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            "## A\nText <?course @LLMQuiz(67)\n",
        ),
        source_path="commonmark-special-html-unclosed-inline.md",
    )
    assert not any(
        item["kind"] == "html_processing_instruction"
        for item in unclosed_inline_special["protected_spans"]
    )
    assert {
        item["span"]["raw"]
        for item in unclosed_inline_special["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(67)"}

    special_markup_near_misses = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\nText <!element @LLMQuiz(68)>\n"
                "Text <![cdata[@LLMQuiz(69)]]>\n"
                "Text < ?course @LLMQuiz(70) ?>\n"
                "Text \\<?course @LLMQuiz(71) ?>\n"
                "Text \\\\<?course @LLMQuiz(72) ?>\n"
            ),
        ),
        source_path="commonmark-special-html-near-misses.md",
    )
    assert {
        item["span"]["raw"]
        for item in special_markup_near_misses["macros"]
        if item["name"] == "LLMQuiz"
    } == {
        "@LLMQuiz(69)", "@LLMQuiz(70)", "@LLMQuiz(71)",
    }
    near_miss_special_spans = [
        item for item in special_markup_near_misses["protected_spans"]
        if item["kind"] in {
            "html_processing_instruction",
            "html_declaration",
            "html_cdata",
        }
    ]
    assert {
        item["kind"] for item in near_miss_special_spans
    } == {"html_declaration", "html_processing_instruction"}
    assert len(_target(special_markup_near_misses, "llm")["instances"]) == 3

    markup_owns_type_one_cases = [
        (
            "html_processing_instruction",
            "<?course",
            "?>",
            "<script>",
        ),
        ("html_cdata", "<![CDATA[", "]]>", "<textarea>"),
        ("html_comment", "<!--", "-->", "<pre>"),
        ("html_declaration", "<!ELEMENT", ">", "<style"),
    ]
    for index, (
        markup_kind, markup_open, markup_close, type_one_open
    ) in enumerate(markup_owns_type_one_cases, start=80):
        source = _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\n{markup_open}\n{type_one_open}\n"
                f"@LLMQuiz({index})\n[[hidden nested quiz]]\n"
                f"{markup_close}\n@LLMQuiz({index + 100})\n"
                "Sichtbar [[ok]]\n"
            ),
        )
        result = mapper.map_text(
            source,
            source_path=f"markup-owns-{markup_kind}.md",
        )
        assert len(
            [
                item for item in result["protected_spans"]
                if item["kind"] == markup_kind
            ]
        ) == 1, markup_kind
        assert not any(
            item["kind"] == "raw_html"
            for item in result["protected_spans"]
        ), markup_kind
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({index + 100})"}, markup_kind
        assert len(result["block_ranges"]["native_quiz"]) == 1, markup_kind
        assert not any(
            item["code"] == "unterminated_raw_html"
            for item in result["diagnostics"]
        ), markup_kind

    type_one_owns_markup_cases = [
        (
            "script",
            "<?course @LLMQuiz(90) ?>",
            "html_processing_instruction",
        ),
        (
            "pre",
            "<!ELEMENT @LLMQuiz(91)>",
            "html_declaration",
        ),
        (
            "style",
            "<![CDATA[@LLMQuiz(92)]]>",
            "html_cdata",
        ),
        (
            "textarea",
            "<!-- @LLMQuiz(93) -->",
            "html_comment",
        ),
    ]
    for index, (
        raw_tag, markup_text, markup_kind
    ) in enumerate(type_one_owns_markup_cases, start=190):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    f"## A\n<{raw_tag}>\n{markup_text}\n"
                    f"[[hidden raw quiz]]\n</{raw_tag}>\n"
                    f"@LLMQuiz({index})\nSichtbar [[ok]]\n"
                ),
            ),
            source_path=f"type-one-owns-{markup_kind}.md",
        )
        raw_spans = [
            item for item in result["protected_spans"]
            if item["kind"] == "raw_html"
        ]
        assert len(raw_spans) == 1, markup_kind
        assert raw_spans[0]["tag"] == raw_tag, markup_kind
        assert not any(
            item["kind"] == markup_kind
            for item in result["protected_spans"]
        ), markup_kind
        assert {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        } == {f"@LLMQuiz({index})"}, markup_kind
        assert len(result["block_ranges"]["native_quiz"]) == 1, markup_kind

    markup_then_real_type_one = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n<?outer\n<script>\n?>\n"
                "<style>\n@LLMQuiz(200)\n[[hidden style quiz]]\n"
                "</style>\n@LLMQuiz(201)\nSichtbar [[ok]]\n"
            ),
        ),
        source_path="markup-then-real-type-one.md",
    )
    assert [
        item["kind"]
        for item in markup_then_real_type_one["protected_spans"]
        if item["kind"] in {
            "html_processing_instruction", "raw_html",
        }
    ] == ["html_processing_instruction", "raw_html"]
    assert {
        item["span"]["raw"]
        for item in markup_then_real_type_one["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(201)"}
    assert len(markup_then_real_type_one["block_ranges"]["native_quiz"]) == 1
    assert not any(
        item["code"] == "unterminated_raw_html"
        for item in markup_then_real_type_one["diagnostics"]
    )

    type_one_then_real_markup = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n<script>\n<?inner-unclosed\n</script>\n"
                "<?real @LLMQuiz(202) ?>\n"
                "@LLMQuiz(203)\nSichtbar [[ok]]\n"
            ),
        ),
        source_path="type-one-then-real-markup.md",
    )
    assert [
        item["kind"]
        for item in type_one_then_real_markup["protected_spans"]
        if item["kind"] in {
            "raw_html", "html_processing_instruction",
        }
    ] == ["raw_html", "html_processing_instruction"]
    assert {
        item["span"]["raw"]
        for item in type_one_then_real_markup["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(203)"}
    assert len(type_one_then_real_markup["block_ranges"]["native_quiz"]) == 1
    assert not any(
        item["code"] == "unterminated_html_processing_instruction"
        for item in type_one_then_real_markup["diagnostics"]
    )

    short_comment_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\nText <!--> @LLMQuiz(210)\n"
            "> <!---> @LLMQuiz(211)\n"
            "- <!--> @LLMQuiz(212)\n"
            "\\<!-- @LLMQuiz(213) -->\n"
            "\\\\<!-- @LLMQuiz(214) -->\n"
            "@LLMQuiz(215)\nSichtbar [[ok]]\n"
        ),
    )
    short_comments = mapper.map_text(
        short_comment_source,
        source_path="commonmark-short-comments.md",
    )
    short_comment_spans = [
        item for item in short_comments["protected_spans"]
        if item["kind"] == "html_comment"
    ]
    assert len(short_comment_spans) == 4
    assert all(item["closed"] is True for item in short_comment_spans)
    assert {
        item["span"]["raw"]
        for item in short_comments["macros"]
        if item["name"] == "LLMQuiz"
    } == {
        "@LLMQuiz(210)", "@LLMQuiz(213)", "@LLMQuiz(215)",
    }
    assert len(short_comments["block_ranges"]["native_quiz"]) == 1
    assert len(_target(short_comments, "llm")["instances"]) == 3

    unclosed_comment_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        "## A\n> <!-- unclosed\n> @LLMQuiz(216)\n> [[hidden quiz]]\n",
    )
    unclosed_comment = mapper.map_text(
        unclosed_comment_source,
        source_path="commonmark-comment-unclosed.md",
    )
    unclosed_comment_spans = [
        item for item in unclosed_comment["protected_spans"]
        if item["kind"] == "html_comment"
    ]
    assert len(unclosed_comment_spans) == 1
    assert unclosed_comment_spans[0]["closed"] is False
    assert unclosed_comment_spans[0]["span"]["char_end"] == len(
        unclosed_comment_source
    )
    assert unclosed_comment["macros"] == []
    assert unclosed_comment["block_ranges"]["native_quiz"] == []
    assert any(
        item["code"] == "unterminated_html_comment"
        for item in unclosed_comment["diagnostics"]
    )

    escaped_unclosed_comments = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## A\n\\<!-- @LLMQuiz(217)\n"
                "\\\\<!-- @LLMQuiz(218)\n"
            ),
        ),
        source_path="commonmark-comment-unclosed-escape-parity.md",
    )
    assert {
        item["span"]["raw"]
        for item in escaped_unclosed_comments["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(217)", "@LLMQuiz(218)"}
    escaped_unclosed_spans = [
        item for item in escaped_unclosed_comments["protected_spans"]
        if item["kind"] == "html_comment"
    ]
    assert escaped_unclosed_spans == []
    assert not any(
        item["code"] == "unterminated_html_comment"
        for item in escaped_unclosed_comments["diagnostics"]
    )

    backslash = chr(92)
    quoted_tag_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            '## A\n<input title="x > @LLMQuiz(1)">\n'
            "<img alt='x > [[fake]] < &quot; y'>\n"
            '<div\n title="x >\n## not-heading @LLMQuiz(2) <">'
            "text</div>\n"
            f'<input title="x {backslash}" > @LLMQuiz(3)">\n'
            f'<input title="x {backslash} path > @LLMQuiz(6)">\n'
            '<input title="&quot; > @LLMQuiz(4) &lt;">\n'
            "<widget title='x > @LLMQuiz(5)' />\n"
            "@Lupe\n"
        ),
    )
    quoted_tags = mapper.map_text(
        quoted_tag_source, source_path="quoted-html-tags.md"
    )
    llm_macros = [
        item for item in quoted_tags["macros"]
        if item["name"] == "LLMQuiz"
    ]
    assert len(llm_macros) == 1
    assert "@LLMQuiz(3)" in llm_macros[0]["span"]["raw"]
    assert quoted_tags["block_ranges"]["native_quiz"] == []
    assert len(_target(quoted_tags, "llm")["instances"]) == 1
    assert [item["title"] for item in quoted_tags["headings"]] == [
        "Testkurs", "A",
    ]
    lupe = next(item for item in quoted_tags["macros"] if item["name"] == "Lupe")
    assert lupe["html_depth"] == 0
    void_or_self = [
        item for item in quoted_tags["html_ranges"]
        if item.get("container") is False
    ]
    assert {item["tag"] for item in void_or_self} == {
        "input", "img", "widget",
    }
    assert all(
        item["span"]["char_start"] == item["open_span"]["char_start"]
        and item["span"]["char_end"] == item["open_span"]["char_end"]
        for item in void_or_self
    )
    div = next(
        item for item in quoted_tags["html_ranges"]
        if item["tag"] == "div"
    )
    assert "@LLMQuiz(2)" in div["open_span"]["raw"]
    html_tag_spans = [
        item for item in quoted_tags["protected_spans"]
        if item["kind"] == "html_tag"
    ]
    assert html_tag_spans
    assert any(
        "[[fake]]" in item["span"].get("raw", "")
        for item in html_tag_spans
    )

    malformed_tag_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        "## A\n<input title=x < @LLMQuiz(8)>\n@Lupe\n",
    )
    malformed_tag = mapper.map_text(
        malformed_tag_source, source_path="malformed-html-tag.md"
    )
    assert "LLMQuiz" in {
        item["name"] for item in malformed_tag["macros"]
    }
    assert any(
        item["code"] == "invalid_html_tag_candidate"
        for item in malformed_tag["diagnostics"]
    )
    unclosed_tag_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            '## A\n<input title="x > @LLMQuiz(9)\n'
            "[[unclosed attribute]]\n## hidden\n"
        ),
    )
    unclosed_tag = mapper.map_text(
        unclosed_tag_source, source_path="unclosed-html-tag.md"
    )
    assert "LLMQuiz" in {
        item["name"] for item in unclosed_tag["macros"]
    }
    assert len(unclosed_tag["block_ranges"]["native_quiz"]) == 1
    assert [item["title"] for item in unclosed_tag["headings"]] == [
        "Testkurs", "A", "hidden",
    ]
    unclosed_spans = [
        item for item in unclosed_tag["protected_spans"]
        if item["kind"] == "html_tag"
    ]
    assert unclosed_spans == []
    assert any(
        item["code"] == "invalid_html_tag_candidate"
        and item["reason"] == "unclosed_attribute_value"
        for item in unclosed_tag["diagnostics"]
    )

    invalid_grammar_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            '## A\n< input title="x > @LLMQuiz(10)">\n'
            '<x:y title="@LLMQuiz(11)">\n'
            '<x_y title="@LLMQuiz(12)">\n'
            '<input title=x=y @LLMQuiz(13)>\n'
            '<input title="x"foo="@LLMQuiz(14)">\n'
            '<input ??? @LLMQuiz(15)>\n'
            '< /div @LLMQuiz(16)>\n'
            '</x:y @LLMQuiz(17)>\n'
            '</div foo @LLMQuiz(18)>\n'
        ),
    )
    invalid_grammar = mapper.map_text(
        invalid_grammar_source, source_path="invalid-html-grammar.md"
    )
    invalid_llm_raws = {
        item["span"]["raw"]
        for item in invalid_grammar["macros"]
        if item["name"] == "LLMQuiz"
    }
    assert invalid_llm_raws == {
        "@LLMQuiz(10)", "@LLMQuiz(11)", "@LLMQuiz(12)",
        "@LLMQuiz(13)", "@LLMQuiz(14)", "@LLMQuiz(15)",
        "@LLMQuiz(16)", "@LLMQuiz(17)", "@LLMQuiz(18)",
    }
    assert not any(
        item["kind"] == "html_tag"
        for item in invalid_grammar["protected_spans"]
    )
    assert sum(
        item["code"] == "invalid_html_tag_candidate"
        for item in invalid_grammar["diagnostics"]
    ) >= 8

    valid_html_whitespace_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\n<input\n title\n = @LLMQuiz(300)>\n"
            "<input\r\n title=@LLMQuiz(301)>\r\n"
            "<input\r title=@LLMQuiz(302)>\r"
            "<widget title=@LLMQuiz(303)\n/>\n"
            "<div\n class=box>Text</div\r\n>\n"
            "@LLMQuiz(304)\n"
        ),
    )
    valid_html_whitespace = mapper.map_text(
        valid_html_whitespace_source,
        source_path="commonmark-valid-html-whitespace.md",
    )
    assert {
        item["span"]["raw"]
        for item in valid_html_whitespace["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(304)"}
    valid_void_or_self = [
        item for item in valid_html_whitespace["html_ranges"]
        if item.get("container") is False
    ]
    assert [item["tag"] for item in valid_void_or_self] == [
        "input", "input", "input", "widget",
    ]
    assert valid_void_or_self[-1]["self_closing"] is True
    valid_div = next(
        item for item in valid_html_whitespace["html_ranges"]
        if item["tag"] == "div"
    )
    assert valid_div["closed"] is True
    assert valid_div["balanced"] is True
    assert not any(
        item["code"] == "invalid_html_tag_candidate"
        for item in valid_html_whitespace["diagnostics"]
    )

    invalid_html_whitespace_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\n<input\n\n title=@LLMQuiz(310)>\n"
            "<input\f title=@LLMQuiz(311)>\n"
            "<input\v title=@LLMQuiz(312)>\n"
            "<input title\n\n=@LLMQuiz(313)>\n"
            "<input title=\n\n@LLMQuiz(314)>\n"
            "<input title=x\n\n data=@LLMQuiz(315)/>\n"
            "<div>Text</div\n\n>\n"
            "@LLMQuiz(316)\n"
        ),
    )
    invalid_html_whitespace = mapper.map_text(
        invalid_html_whitespace_source,
        source_path="commonmark-invalid-html-whitespace.md",
    )
    assert {
        item["span"]["raw"]
        for item in invalid_html_whitespace["macros"]
        if item["name"] == "LLMQuiz"
    } == {
        "@LLMQuiz(310)", "@LLMQuiz(311)", "@LLMQuiz(312)",
        "@LLMQuiz(313)", "@LLMQuiz(314)", "@LLMQuiz(315)",
        "@LLMQuiz(316)",
    }
    invalid_whitespace_reasons = {
        item.get("reason")
        for item in invalid_html_whitespace["diagnostics"]
        if item["code"] == "invalid_html_tag_candidate"
    }
    assert {
        "too_many_attribute_separator_line_endings",
        "missing_attribute_separator",
        "too_many_pre_equals_line_endings",
        "too_many_post_equals_line_endings",
        "too_many_close_tag_line_endings",
    } <= invalid_whitespace_reasons
    invalid_div = next(
        item for item in invalid_html_whitespace["html_ranges"]
        if item["tag"] == "div"
    )
    assert invalid_div["closed"] is False
    assert invalid_div["balanced"] is False

    autolink_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\n<https://example.org/a>\n"
            "<teacher@example.org>\n"
            "<https://example.org/@LLMQuiz(99)>\n"
            "@Erdhaufen\nFund\n@EndeErdhaufen\n"
            "Frage [[1]]\n@LLMQuiz(1)\n"
        ),
    )
    autolinks = mapper.map_text(
        autolink_source, source_path="commonmark-autolinks.md"
    )
    protected_autolinks = [
        item for item in autolinks["protected_spans"]
        if item["kind"] == "html_autolink"
    ]
    assert len(protected_autolinks) == 3
    autolink_llm = [
        item for item in autolinks["macros"]
        if item["name"] == "LLMQuiz"
    ]
    assert len(autolink_llm) == 1
    assert autolink_llm[0]["span"]["raw"] == "@LLMQuiz(1)"
    assert len(autolinks["block_ranges"]["native_quiz"]) == 1
    assert len(autolinks["environment"]["block_pairs"]) == 1
    assert autolinks["environment"]["block_pairs"][0]["valid"] is True
    assert not any(
        item["code"] == "unclosed_html"
        and item.get("tag") in {"https", "teacher"}
        for item in autolinks["diagnostics"]
    )

    escaped_angle_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\n\\<input title=@LLMQuiz(50)>\n"
            "\\<https://example.org/@LLMQuiz(51)>\n"
            "\\\\<input title=@LLMQuiz(52)>\n"
            "\\\\<https://example.org/@LLMQuiz(53)>\n"
        ),
    )
    escaped_angles = mapper.map_text(
        escaped_angle_source,
        source_path="escaped-html-tags-and-autolinks.md",
    )
    assert {
        item["span"]["raw"]
        for item in escaped_angles["macros"]
        if item["name"] == "LLMQuiz"
    } == {"@LLMQuiz(50)", "@LLMQuiz(51)"}
    escaped_angle_protected = [
        item for item in escaped_angles["protected_spans"]
        if item["kind"] in {"html_tag", "html_autolink"}
    ]
    assert len(
        [item for item in escaped_angle_protected if item["kind"] == "html_tag"]
    ) == 1
    assert len(
        [
            item for item in escaped_angle_protected
            if item["kind"] == "html_autolink"
        ]
    ) == 1
    assert any(
        "@LLMQuiz(52)" in item["span"]["raw"]
        for item in escaped_angle_protected
    )
    assert any(
        "@LLMQuiz(53)" in item["span"]["raw"]
        for item in escaped_angle_protected
    )
    assert len(_target(escaped_angles, "llm")["instances"]) == 2

    unclosed_textarea_source = _synthetic_course(
        ["lia-llm", "lia-loot"],
        (
            "## A\n<textarea class=answer>\n"
            "@LLMQuiz(5)\n[[unclosed fake]]\n## not-a-slide\n"
        ),
    )
    unclosed_textarea = mapper.map_text(
        unclosed_textarea_source,
        source_path="raw-html-unclosed-textarea.md",
    )
    raw_textareas = [
        item for item in unclosed_textarea["protected_spans"]
        if item["kind"] == "raw_html" and item["tag"] == "textarea"
    ]
    assert len(raw_textareas) == 1
    assert raw_textareas[0]["closed"] is False
    assert raw_textareas[0]["span"]["char_end"] == len(
        unclosed_textarea_source
    )
    assert unclosed_textarea["macros"] == []
    assert unclosed_textarea["block_ranges"]["native_quiz"] == []
    assert _target(unclosed_textarea, "llm")["instances"] == []
    assert any(
        item["code"] == "unterminated_raw_html"
        and item["tag"] == "textarea"
        for item in unclosed_textarea["diagnostics"]
    )

    list_continuation = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## A\n- Eintrag\n  @Erdhaufen\n"
                "  X\n  @EndeErdhaufen\n"
            ),
        ),
        source_path="list-continuation.md",
    )
    pair = list_continuation["environment"]["block_pairs"][0]
    assert pair["valid"] is False
    assert "marker_in_list" in pair["exclusion_reasons"]
    markers = {
        item["name"]: item
        for item in list_continuation["macros"]
        if item["name"] in {"Erdhaufen", "EndeErdhaufen"}
    }
    assert all(item["inside_list"] for item in markers.values())

    empty_item_cases = {
        "bullet": (
            "## A\n-\n  @Erdhaufen\n"
            "  X\n  @EndeErdhaufen\n"
        ),
        "ordered_one": (
            "## A\n1.\n   @Erdhaufen\n"
            "   X\n   @EndeErdhaufen\n"
        ),
        "ordered_two_block_start": (
            "## A\n2.\n   @Erdhaufen\n"
            "   X\n   @EndeErdhaufen\n"
        ),
    }
    for label, body in empty_item_cases.items():
        result = mapper.map_text(
            _synthetic_course(["lia-loot"], body),
            source_path=f"empty-list-item-{label}.md",
        )
        pair = result["environment"]["block_pairs"][0]
        assert pair["valid"] is False, label
        assert pair["exclusion_reasons"] == ["marker_in_list"], label
        markers = {
            item["name"]: item
            for item in result["macros"]
            if item["name"] in {"Erdhaufen", "EndeErdhaufen"}
        }
        assert len(markers) == 2, label
        assert all(item["inside_list"] for item in markers.values()), label

    empty_item_nonlist_controls = {
        "setext": (
            "## A\nParagraph\n-\n"
            "  @Erdhaufen\n  X\n  @EndeErdhaufen\n"
        ),
        "thematic": (
            "## A\n---\n"
            "  @Erdhaufen\n  X\n  @EndeErdhaufen\n"
        ),
        "escaped_marker": (
            "## A\n\\-\n"
            "  @Erdhaufen\n  X\n  @EndeErdhaufen\n"
        ),
        "ordered_two_no_interruption": (
            "## A\nParagraph\n2.\n"
            "   @Erdhaufen\n   X\n   @EndeErdhaufen\n"
        ),
        "dedent": (
            "## A\n-\n  item\n\n"
            "@Erdhaufen\nX\n@EndeErdhaufen\n"
        ),
    }
    for label, body in empty_item_nonlist_controls.items():
        result = mapper.map_text(
            _synthetic_course(["lia-loot"], body),
            source_path=f"empty-list-item-control-{label}.md",
        )
        pair = result["environment"]["block_pairs"][0]
        assert pair["valid"] is True, label
        assert pair["exclusion_reasons"] == [], label
        markers = [
            item for item in result["macros"]
            if item["name"] in {"Erdhaufen", "EndeErdhaufen"}
        ]
        assert len(markers) == 2, label
        assert not any(item["inside_list"] for item in markers), label

    for label, marker, indent in (
        ("bullet", "-", "  "),
        ("ordered", "1.", "   "),
    ):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-loot"],
                f"## A\n{marker}\n{indent}[[answer]]\n",
            ),
            source_path=f"native-quiz-empty-list-item-{label}.md",
        )
        quizzes = result["block_ranges"]["native_quiz"]
        assert len(quizzes) == 1, label
        assert quizzes[0]["container_kind"] == "list", label
        assert "list" in quizzes[0]["forms"], label

    orphan = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## A\n[[?nur Hinweis]]\n"
                "@lootif(bewertbare Aufgaben >= 1; spawn)\n"
                "X\n@Endelootif\n"
            ),
        ),
        source_path="orphan-hint.md",
    )
    assert orphan["block_ranges"]["native_quiz"] == []
    assert any(item["code"] == "orphan_hint" for item in orphan["diagnostics"])
    assert orphan["block_ranges"]["lootif"][0][
        "external_trigger_status"
    ] == "unproven"
    assert _candidate(orphan, "standalone_quiz")["anchors"] == []

    current_slide_orphan = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## A\n@lootif(Alle Aufgaben der aktuellen Folie gelöst; spawn)\n"
                "X\n@Endelootif\n[[?später Hinweis]]\n"
            ),
        ),
    )
    assert current_slide_orphan["block_ranges"]["lootif"][0][
        "external_trigger_status"
    ] == "unproven"

    inline_payloads = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## A\n@Erdhaufen.inline(erde)\n"
                "@Pflanze.inline(pflanze)\n@Schatztruhe(erde)\n"
            ),
        ),
        source_path="inline-payload-layer.md",
    )
    layers = inline_payloads["environment"]["direct_layers"]
    assert len(layers) == 1
    assert layers[0]["carrier"] == "Schatztruhe"
    assert layers[0]["canonical_token"] == "erde"
    assert not any(
        item["code"] == "direct_layer_on_unsupported_carrier"
        for item in inline_payloads["diagnostics"]
    )


def test_freeze_audit_fail_closed_regressions() -> None:
    not_loot = mapper.map_text(
        _synthetic_course(["not-lia-loot"], "## A\nText\n")
    )
    assert not_loot["imports"][0]["provider"] is None
    assert not_loot["imports"][0]["is_loot"] is False
    assert not_loot["imports"][0]["relative_to_loot"] == "loot_absent"
    assert not_loot["header"]["loot_import_orders"] == []
    assert any(
        item["code"] == "lia_loot_import_missing"
        for item in not_loot["diagnostics"]
    )

    for tag in ("p", "dl", "school-card"):
        html = mapper.map_text(
            _synthetic_course(
                ["lia-loot"],
                (
                    f"## A\n<{tag}>\n@Erdhaufen\n"
                    f"Inhalt\n@EndeErdhaufen\n</{tag}>\n"
                ),
            )
        )
        pair = html["environment"]["block_pairs"][0]
        assert pair["valid"] is False, tag
        assert "marker_inside_html" in pair["exclusion_reasons"], tag
        assert not any(
            anchor["evidence"].get("environment_pair_id") == pair["id"]
            for anchor in _candidate(
                html, "container_visibility_option"
            )["anchors"]
        )

    quiz_html = mapper.map_text(
        _synthetic_course(
            ["lia-loot"], "## A\n<div>\nFrage [[Antwort]]\n</div>\n"
        )
    )
    quiz = quiz_html["block_ranges"]["native_quiz"][0]
    quiz_anchor = next(
        item
        for item in _candidate(quiz_html, "standalone_quiz")["anchors"]
        if item["evidence"].get("quiz_id") == quiz["id"]
    )
    assert quiz_anchor["valid_block_boundary"] is False
    assert "inside_html" in quiz_anchor["exclusion_reasons"]

    nested = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## A\n@Erdhaufen\n@Pflanze\n@Schatztruhe\n"
                "@EndePflanze\n@EndeErdhaufen\n"
            ),
        )
    )
    structural = {
        "erdhaufen", "endeerdhaufen", "pflanze", "endepflanze",
        "blume", "endeblume", "lootif", "endelootif",
    }
    hidden = _candidate(nested, "hidden_macro_inside_reveal")["anchors"]
    assert hidden
    assert all(
        nested["macros"][item["evidence"]["child_macro_id"]][
            "name_folded"
        ] not in structural
        for item in hidden
    )
    assert {
        nested["macros"][item["evidence"]["child_macro_id"]]["name"]
        for item in hidden
    } == {"Schatztruhe"}

    nested_portal = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            "## A\n@Erdhaufen.inline(@Portal(1))\n",
        )
    )
    portal = next(
        item for item in nested_portal["macros"] if item["name"] == "Portal"
    )
    assert portal["parent_id"] is not None
    assert _candidate(
        nested_portal, "optional_secret_or_portal"
    )["anchors"] == []

    public_portal_aliases = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            "## A\n@Einbahnportal(2)\n@PortalZurueck(1)\n## B\n",
        )
    )
    portal_anchors = _candidate(
        public_portal_aliases, "optional_secret_or_portal"
    )["anchors"]
    assert [item["evidence"]["macro"] for item in portal_anchors] == [
        "Einbahnportal",
    ]

    bt = chr(96)
    quoted_fence = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\n> {bt * 3}text\n"
                "> @LLMQuiz(1)\n> [[fake]]\n"
                f"> {bt * 4}\n"
            ),
        )
    )
    list_fence = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                f"## A\n- {bt * 3}text\n"
                "  @LLMQuiz(1)\n  [[fake]]\n"
                f"  {bt * 4}\n"
            ),
        )
    )
    for result in (quoted_fence, list_fence):
        fences = [
            item for item in result["protected_spans"]
            if item["kind"] == "fence"
        ]
        assert len(fences) == 1
        assert fences[0]["closed"] is True
        assert "LLMQuiz" not in {item["name"] for item in result["macros"]}
        assert result["block_ranges"]["native_quiz"] == []
        assert _target(result, "llm")["instances"] == []
        assert _target(result, "llm")["eligible"] is False

    layers = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## A\n@Schluessel(toc; erde)\n"
                "@Schluessel(timer; erde)\n"
                "@Schluessel(erde)\n"
                "@Schatztruhe(timer; erde)\n"
            ),
        )
    )["environment"]["direct_layers"]
    native_key = next(
        item for item in layers if item["span"]["line_start"] == 7
    )
    foreign_key = next(
        item for item in layers if item["span"]["line_start"] == 8
    )
    foreign_chest = next(
        item for item in layers if item["span"]["line_start"] == 10
    )
    layer_only_key = next(
        item for item in layers if item["span"]["line_start"] == 9
    )
    assert native_key["valid_carrier"] is True
    assert native_key["target_compatible"] is True
    assert foreign_key["valid_carrier"] is False
    assert foreign_key["foreign_template_targets"] == ["timer"]
    assert "foreign_template_target_requires_chest_carrier" in foreign_key[
        "exclusion_reasons"
    ]
    assert foreign_chest["valid_carrier"] is True
    assert foreign_chest["foreign_template_targets"] == ["timer"]
    assert layer_only_key["valid_carrier"] is True
    assert layer_only_key["canonical_token"] == "erde"

    forbidden_layers = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## A\n@Portal(erde)\n"
                "@Einbahnportal(erde)\n"
                "@Schloss(check; rot; erde)\n"
                "@Puzzletor(rot; [[1]]; erde)\n"
                "@Foo(erde)\n"
            ),
        ),
        source_path="forbidden-layers.md",
    )
    invalid = forbidden_layers["environment"]["invalid_direct_layers"]
    assert {item["carrier"] for item in invalid} == {
        "Portal", "Einbahnportal", "Schloss", "Puzzletor",
    }
    assert all(item["valid_carrier"] is False for item in invalid)
    assert "Foo" not in {
        item["carrier"]
        for item in forbidden_layers["environment"]["direct_layers"]
    }
    assert sum(
        item["code"] == "direct_layer_on_unsupported_carrier"
        for item in forbidden_layers["diagnostics"]
    ) == 4


def test_twelve_course_regressions() -> dict[str, dict[str, Any]]:
    catalog = mapper.load_catalog(CATALOG_PATH)
    catalog_candidate_ids = [
        item["id"] for item in catalog["candidate_classes"]
    ]
    results: dict[str, dict[str, Any]] = {}
    garden_structural_hashes: set[str] = set()
    fixture_tree_before = _tree_snapshot(FIXTURE_TREE_ROOT)
    fixture_paths = {item[1] for item in fixture_tree_before}
    assert {
        "source.json",
        "manifest.jsonl",
        "files/repo_inventory.json",
    } <= fixture_paths
    assert not any(
        path.endswith((".map.json", ".mapping.json", ".mapper.json"))
        for path in fixture_paths
    )

    for identifier, expected in FIXTURES.items():
        path = COURSE_ROOT / expected["rel"]
        assert path.is_file(), path
        before_bytes = path.read_bytes()
        before = (
            hashlib.sha256(before_bytes).hexdigest(),
            len(before_bytes),
            path.stat().st_mtime_ns,
        )
        result = mapper.map_course(path, catalog_path=CATALOG_PATH)
        after_bytes = path.read_bytes()
        after = (
            hashlib.sha256(after_bytes).hexdigest(),
            len(after_bytes),
            path.stat().st_mtime_ns,
        )
        assert before == after, f"{identifier}: mapper changed source"
        assert result["source"]["read_only"] is True
        assert result["source"]["sha256"] == before[0]

        assert result["header"]["span"]["line_end"] == expected["header"]
        mode = next(
            item
            for item in result["header"]["directives"]
            if item["key_normalized"] == "mode"
        )
        assert mode["span"]["line_start"] == expected["mode"]
        assert [item["span"]["line_start"] for item in result["imports"]] == expected["imports"]
        assert len(result["import_slots"]) == len(result["imports"]) + 1
        assert [item["span"]["line_start"] for item in result["headings"]] == expected["headings"]
        assert result["html_summary"]["balanced"] is True
        section, flex, marker = expected["html"]
        assert _class_counts(result, "section", "dynFlex") == section
        assert _class_counts(result, "div", "flex-child") == flex
        assert _class_counts(result, "div", "markerquiz") == marker
        assert [(item["open_line"], item["close_line"]) for item in result["protected_spans"] if item["kind"] == "fence"] == expected.get("fences", [])

        assert result["provider_targets"]["mapped_target_count"] == 12
        assert result["provider_targets"]["count_matches_catalog"] is True
        targets = {
            item["target"]: item
            for item in result["provider_targets"]["targets"]
        }
        assert set(targets) == TARGETS
        assert all(item["direct_import"] for item in targets.values())
        for target in GLOBAL_PROVIDER_TARGETS:
            assert targets[target]["scope"] == "global"
            assert targets[target]["instances"] == []
            assert targets[target]["source_contract_status"] == "proven"
            assert targets[target]["state_status"] == "runtime_required"
            assert targets[target]["eligible"] is True
        for target in TARGETS - GLOBAL_PROVIDER_TARGETS:
            item = targets[target]
            assert item["scope"] == "slide"
            if item["instances"]:
                assert item["source_contract_status"] == "proven"
                assert item["state_status"] == "runtime_required"
                assert item["eligible"] is True
                assert all(
                    instance["kind"] != "text"
                    and instance["block_complete"] is True
                    and instance["block_span"]["char_start"]
                    < instance["block_span"]["char_end"]
                    for instance in item["instances"]
                ), (identifier, target, item["instances"])
            else:
                assert item["source_contract_status"] == "disproven"
                assert item["state_status"] == "disproven"
                assert item["eligible"] is False
        assert [
            item["id"] for item in result["candidates"]["classes"]
        ] == [item[0] for item in EXPECTED_CANDIDATES]
        assert set(catalog_candidate_ids) == CANDIDATE_IDS
        assert len(catalog_candidate_ids) == 18
        assert result["candidates"]["catalog_class_count"] == len(catalog_candidate_ids)
        assert result["candidates"]["safe_block_boundaries"]
        carriers, concealed, visibility, hidden = CONCEALMENT_EXPECTED[
            identifier
        ]
        assert len(result["environment"]["item_concealments"]) == carriers
        assert result["environment"]["counts"][
            "item_concealment_carriers"
        ] == carriers
        assert result["environment"]["counts"]["item_concealed"] == concealed
        assert _candidate(
            result, "collectible_concealment_option"
        )["anchor_count"] == carriers
        assert _candidate(
            result, "container_visibility_option"
        )["anchor_count"] == visibility
        assert _candidate(
            result, "hidden_macro_inside_reveal"
        )["anchor_count"] == hidden
        if visibility:
            assert all(
                anchor["edit_variants"]
                and anchor["discoverability_review_status"]
                == "human_review_required_under_content_policy"
                for anchor in _candidate(
                    result, "container_visibility_option"
                )["anchors"]
            )
        if identifier == "M6_03":
            assert {
                anchor["witness_status"]
                for anchor in _candidate(
                    result, "container_visibility_option"
                )["anchors"]
            } == {"missing_magnifier"}

        text = before_bytes.decode("utf-8")
        for macro in result["macros"]:
            span = macro["span"]
            assert text[span["char_start"]:span["char_end"]] == span["raw"]
            assert (
                before_bytes[span["byte_start"]:span["byte_end"]].decode("utf-8")
                == span["raw"]
            )

        garden_class = _candidate(result, "garden_before_reflection")
        assert garden_class["anchor_count"] == 1
        garden_anchor = garden_class["anchors"][0]
        if "garden" not in expected:
            assert all(
                result["environment"]["counts"].get(key, 0) == 0
                for key in (
                    "earth_inline", "plant_inline", "earth_blocks",
                    "plant_blocks", "earth_direct_layers",
                    "plant_direct_layers",
                )
            )
            assert result["gardens"] == []
            assert garden_anchor["action"] == "insert_before_reflection"
            assert garden_anchor["anchor"]["line_start"] == expected["reflection"]
        else:
            garden = result["garden_fingerprint"]
            assert garden is not None
            assert (
                garden["fingerprint_span"]["line_start"],
                garden["fingerprint_span"]["line_end"],
            ) == expected["garden"]
            assert garden["raw_normalized_character_count"] == 1493
            assert garden["raw_normalized_sha256"] == GARDEN_SHA256
            assert garden["reveal_instance_counts"] == {"earth": 5, "plant": 5}
            assert garden["reward_counts"] == {
                "Energiekiste": 18,
                "Schatztruhe": 8,
                "Diamanttruhe": 4,
            }
            assert garden["tool_order"] == ["Schaufel", "Giesskanne"]
            assert [
                (item["open_span"]["line_start"], item["close_span"]["line_start"])
                for item in result["environment"]["block_pairs"]
                if item["slide_id"] == garden["slide_id"]
            ] == expected["pairs"]
            assert all(
                item["valid"]
                for item in result["environment"]["block_pairs"]
                if item["slide_id"] == garden["slide_id"]
            )
            assert garden_anchor["action"] == "vary_existing"
            garden_structural_hashes.add(garden["structural_sha256"])
        results[identifier] = result

    assert len(garden_structural_hashes) == 1
    fixture_tree_after = _tree_snapshot(FIXTURE_TREE_ROOT)
    assert fixture_tree_after == fixture_tree_before
    return results


def test_corpus_edge_cases(results: dict[str, dict[str, Any]]) -> None:
    d5_02 = results["D5_02"]
    energy = next(
        item
        for item in d5_02["macros"]
        if item["name"] == "Energiekiste" and item["span"]["line_start"] == 350
    )
    assert energy["html_depth"] == 2
    assert energy["feedback_depth"] == 1
    solution_tail = next(
        item
        for item in _candidate(d5_02, "solution_reward_tail")["anchors"]
        if item["anchor"]["line_start"] == 351
    )
    assert solution_tail["role"] == "before_feedback_close"
    assert solution_tail["context"]["feedback_depth"] == 1
    assert solution_tail["context"]["html_depth"] == 2
    assert solution_tail["valid_block_boundary"] is True
    assert solution_tail["specialized_boundary"] == (
        "solution_tail_inside_feedback"
    )

    def quiz_at(result: dict[str, Any], syntax_line: int) -> dict[str, Any]:
        return next(
            quiz
            for quiz in result["block_ranges"]["native_quiz"]
            if any(
                token["span"]["line_start"] == syntax_line
                for token in quiz["syntax_spans"]
            )
        )

    d5_01 = results["D5_01"]
    assert len(d5_01["block_ranges"]["native_quiz"]) == 44
    for syntax_line, expected_span, form, expected_valid in (
        (305, (304, 311), "inline", False),
        (675, (667, 695), "table", True),
        (722, (721, 728), "inline", False),
    ):
        quiz = quiz_at(d5_01, syntax_line)
        assert (
            quiz["span"]["line_start"], quiz["span"]["line_end"]
        ) == expected_span
        assert form in quiz["forms"] or quiz["container_kind"] == form
        assert quiz["complete_components"]["question_or_metadata"] is True
        assert quiz["complete_components"]["feedback_solution"] is True
        anchor = next(
            item
            for item in _candidate(d5_01, "standalone_quiz")["anchors"]
            if item["evidence"].get("quiz_id") == quiz["id"]
        )
        assert anchor["anchor"]["char_start"] == quiz["span"]["char_start"]
        assert anchor["close_anchor"]["char_start"] == quiz["span"]["char_end"]
        assert anchor["context"]["inside_table_or_quiz"] is False
        assert anchor["close_context"]["inside_table_or_quiz"] is False
        assert anchor["valid_block_boundary"] is expected_valid, (
            syntax_line, anchor["context"], anchor["exclusion_reasons"]
        )
        if not expected_valid:
            assert "inside_html" in anchor["exclusion_reasons"]

    d6_list = quiz_at(results["D6_01"], 149)
    assert len(results["D6_01"]["block_ranges"]["native_quiz"]) == 6
    assert (d6_list["span"]["line_start"], d6_list["span"]["line_end"]) == (
        138, 181
    )
    assert d6_list["container_kind"] == "list"
    assert d6_list["syntax_count"] == 10
    assert d6_list["complete_components"]["hint"] is True
    assert d6_list["complete_components"]["feedback_solution"] is True

    m6_math = quiz_at(results["M6_01"], 154)
    assert len(results["M6_01"]["block_ranges"]["native_quiz"]) == 45
    assert (m6_math["span"]["line_start"], m6_math["span"]["line_end"]) == (
        147, 160
    )
    assert "math_inline" in m6_math["forms"]
    assert m6_math["syntax_count"] == 2
    assert m6_math["complete_components"]["hint"] is True
    assert m6_math["complete_components"]["feedback_solution"] is True

    d6_03 = results["D6_03"]
    orthography = next(
        item
        for item in d6_03["macros"]
        if item["name"] == "orthography" and item["span"]["line_start"] == 243
    )
    assert "<!--" in orthography["span"]["raw"]
    comment_ranges = [
        item["span"]
        for item in d6_03["protected_spans"]
        if item["kind"] == "html_comment"
    ]
    assert not any(
        span["char_start"] <= orthography["span"]["char_start"]
        and orthography["span"]["char_end"] <= span["char_end"]
        for span in comment_ranges
    )

    d6_01 = results["D6_01"]
    assert _target(d6_01, "timer")["instances"]
    assert _target(d6_01, "timer")["eligible"] is True
    assert _target(d6_01, "mathpath")["instances"] == []
    assert _target(d6_01, "mathpath")["eligible"] is False

    m6_03 = results["M6_03"]
    outers = [
        item
        for item in m6_03["macros"]
        if item["name"].endswith(".inline")
        and item["span"]["line_start"] == 1629
    ]
    nested = [
        item
        for item in m6_03["macros"]
        if item["name"] == "Puzzleteil"
        and item["span"]["line_start"] == 1629
    ]
    assert len(outers) == 4
    assert len(nested) == 4
    assert {item["parent_id"] for item in nested} == {
        item["id"] for item in outers
    }
    gate = next(
        item
        for item in m6_03["macros"]
        if item["name"] == "Puzzletor" and item["span"]["line_start"] == 1645
    )
    assert gate["arguments"] == ["tuerkis", "[[3;1];[4;2]]", "anker"]

    m5_03 = results["M5_03"]
    assert m5_03["header"]["loot_import_orders"] == [17]
    pentomino = next(
        item for item in m5_03["imports"] if "pentomino" in item["normalized_url"].lower()
    )
    assert m5_03["imports"].index(pentomino) == 18
    assert pentomino["span"]["line_start"] == 32
    assert pentomino["relative_to_loot"] == "after"

    m6_01 = results["M6_01"]
    assert len(m6_01["imports"]) == 17
    assert m6_01["header"]["loot_import_orders"] == [16]
    assert "resetter" not in {
        item["target"] for item in m6_01["provider_targets"]["targets"]
    }
    assert _target(m6_01, "kachel")["instances"] == []
    assert _target(m6_01, "kachel")["eligible"] is False
    assert _target(m6_01, "mathpath")["instances"] == []
    assert _target(m6_01, "mathpath")["eligible"] is False

    for identifier in ("D5_01", "M5_01"):
        path = COURSE_ROOT / FIXTURES[identifier]["rel"]
        source = path.read_text(encoding="utf-8")
        baseline = results[identifier]
        resources = next(
            item for item in baseline["macros"]
            if item["name"] == "Ressourcen"
        )
        assert resources["argument_source"] is not None
        assert resources["argument_source"].count(",") == 2
        augmented = mapper.map_text(
            source
            + "\n## Trigger-Regression\n"
            + "@lootif(Energie >= 50; spawn)\n"
            + "Energiebeleg\n@Endelootif\n"
        )
        trigger = augmented["block_ranges"]["lootif"][-1]
        assert trigger["parsed_trigger"]["family"] == "resources"
        assert trigger["external_trigger_status"] == "proven"
        assert trigger["valid"] is True


def test_final_commonmark_owner_and_html_block_regressions() -> None:
    bt = chr(96)
    bs = chr(92)
    dq = chr(34)

    def llm_raw(result: dict[str, Any]) -> set[str]:
        return {
            item["span"]["raw"]
            for item in result["macros"]
            if item["name"] == "LLMQuiz"
        }

    def spans(result: dict[str, Any], *kinds: str) -> list[dict[str, Any]]:
        return [
            item
            for item in result["protected_spans"]
            if item["kind"] in set(kinds)
        ]

    for slash_count, quiz_id in ((1, 1500), (2, 1501)):
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Code closer\nParagraph "
                    + bt
                    + "code"
                    + bs * slash_count
                    + bt
                    + f"\n@LLMQuiz({quiz_id}) [[visible]] "
                    + bt
                    + "\n"
                ),
            ),
            source_path=f"code-close-backslash-{slash_count}.md",
        )
        assert len(spans(result, "inline_code")) == 1, slash_count
        assert f"@LLMQuiz({quiz_id})" in llm_raw(result), slash_count
        assert result["block_ranges"]["native_quiz"], slash_count

    literal_closers = (
        ("script", "style"),
        ("pre", "textarea"),
        ("style", "script"),
        ("textarea", "pre"),
    )
    for offset, (opener, closer) in enumerate(literal_closers):
        quiz_id = 1510 + offset
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    f"## Type one\n<{opener}>\nraw\n"
                    f"</{closer}> trailing protected\n"
                    f"@LLMQuiz({quiz_id})\n[[visible]]\n"
                ),
            ),
            source_path=f"type-one-{opener}-closed-by-{closer}.md",
        )
        raw = spans(result, "raw_html")
        assert len(raw) == 1 and raw[0]["closed"] is True, (opener, closer)
        assert f"@LLMQuiz({quiz_id})" in llm_raw(result), (opener, closer)
        assert result["block_ranges"]["native_quiz"], (opener, closer)

    mixed_case_type_one = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Mixed case type one\n<SCRIPT>\nraw\n</TeXtArEa>\n"
                "@LLMQuiz(1514)\n[[visible]]\n"
            ),
        ),
        source_path="type-one-mixed-case-literal-closer.md",
    )
    assert spans(mixed_case_type_one, "raw_html")[0]["closed"] is True
    assert "@LLMQuiz(1514)" in llm_raw(mixed_case_type_one)

    for offset, invalid_closer in enumerate(
        ("</script >", "</script\t>", "</script\n>")
    ):
        quiz_id = 1515 + offset
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Type one invalid closer\n<script>\nraw\n"
                    + invalid_closer
                    + f"\n@LLMQuiz({quiz_id})\n[[hidden]]\n"
                ),
            ),
            source_path=f"type-one-invalid-closer-{offset}.md",
        )
        raw = spans(result, "raw_html")
        assert len(raw) == 1 and raw[0]["closed"] is False, invalid_closer
        assert f"@LLMQuiz({quiz_id})" not in llm_raw(result), invalid_closer
        assert result["block_ranges"]["native_quiz"] == [], invalid_closer

    lowercase_declaration = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Lowercase declaration\n<!doctype html\n"
                "@LLMQuiz(1520)\n> trailing protected\n"
                "@LLMQuiz(1521)\n[[visible]]\n"
            ),
        ),
        source_path="lowercase-declaration-block.md",
    )
    declarations = spans(lowercase_declaration, "html_declaration")
    assert len(declarations) == 1 and declarations[0]["closed"] is True
    assert llm_raw(lowercase_declaration) == {"@LLMQuiz(1521)"}
    assert lowercase_declaration["block_ranges"]["native_quiz"]

    quoted_declaration = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Quoted declaration\n> <!doctype html\n"
                "> @LLMQuiz(1522)\n> >\n"
                "@LLMQuiz(1523)\n[[visible]]\n"
            ),
        ),
        source_path="lowercase-declaration-quote.md",
    )
    assert llm_raw(quoted_declaration) == {"@LLMQuiz(1523)"}

    inline_declaration = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Inline declarations\n"
                "Text <!doctype @LLMQuiz(1524)>\n"
                "Text <!ELEMENT @LLMQuiz(1525)>\n"
                "Text <!1doctype @LLMQuiz(1526)>\n"
                "Text " + bs + "<!doctype @LLMQuiz(1527)>\n"
            ),
        ),
        source_path="declaration-case-and-near-miss.md",
    )
    assert llm_raw(inline_declaration) == {
        "@LLMQuiz(1526)",
        "@LLMQuiz(1527)",
    }
    assert len(spans(inline_declaration, "html_declaration")) == 2

    finite_factories = (
        (
            "type7",
            lambda delimiter: (
                "<span data-x=" + dq + delimiter + dq + "></span>"
            ),
            "html_tag",
        ),
        (
            "uri",
            lambda delimiter: "<http://example.test/" + delimiter + ">",
            "html_autolink",
        ),
        (
            "email",
            lambda delimiter: "<foo" + delimiter + "bar@example.org>",
            "html_autolink",
        ),
    )
    quiz_id = 1600
    for label, factory, owner_kind in finite_factories:
        for delimiter, math_kind in (("$", "inline_math"), ("$$", "display_math")):
            finite = factory(delimiter)
            if delimiter == "$":
                body = (
                    "## Finite before inline math\n"
                    + finite
                    + f" @LLMQuiz({quiz_id}) [[visible]] $\n"
                )
            else:
                body = (
                    "## Finite before display math\n"
                    + finite
                    + f"\n@LLMQuiz({quiz_id}) [[visible]]\n$$\n"
                )
            result = mapper.map_text(
                _synthetic_course(["lia-llm", "lia-loot"], body),
                source_path=f"finite-{label}-before-{math_kind}.md",
            )
            owners = [
                item
                for item in spans(result, owner_kind)
                if delimiter in item["span"].get("raw", "")
            ]
            assert owners, (label, delimiter)
            owner_span = owners[0]["span"]
            assert not any(
                owner_span["char_start"]
                <= item["span"]["char_start"]
                < owner_span["char_end"]
                for item in spans(result, "inline_math", "display_math")
            ), (label, delimiter)
            assert f"@LLMQuiz({quiz_id})" in llm_raw(result), (label, delimiter)
            assert result["block_ranges"]["native_quiz"], (label, delimiter)
            quiz_id += 1

            finite = factory(delimiter)
            if delimiter == "$":
                body = (
                    "## Inline math before finite\n$lead "
                    + finite
                    + f" tail @LLMQuiz({quiz_id}) [[visible]]\n"
                )
            else:
                body = (
                    "## Display math before finite\n$$\n"
                    + finite
                    + f"\n@LLMQuiz({quiz_id}) [[visible]]\n"
                )
            result = mapper.map_text(
                _synthetic_course(["lia-llm", "lia-loot"], body),
                source_path=f"{math_kind}-before-finite-{label}.md",
            )
            owned_math = spans(result, math_kind)
            assert len(owned_math) == 1 and owned_math[0]["closed"] is True, (
                label,
                delimiter,
            )
            assert f"@LLMQuiz({quiz_id})" in llm_raw(result), (label, delimiter)
            assert result["block_ranges"]["native_quiz"], (label, delimiter)
            quiz_id += 1

    # Use a void open tag for the open-tag form so HTML element nesting does
    # not intentionally extend beyond the CommonMark block/container exit.
    standalone_tags = ("<input>", "</span>", "<span />")
    for container_label, prefix, reason, flag in (
        ("quote", "> ", "marker_in_blockquote", "inside_blockquote"),
        ("list", "- ", "marker_in_list", "inside_list"),
    ):
        for tag_index, tag in enumerate(standalone_tags):
            result = mapper.map_text(
                _synthetic_course(
                    ["lia-loot"],
                    (
                        "## Type seven container exit\n"
                        + prefix
                        + tag
                        + "\t  \n"
                        + "@Erdhaufen\nX\n@EndeErdhaufen\n"
                    ),
                ),
                source_path=(
                    f"type-seven-{container_label}-exit-{tag_index}.md"
                ),
            )
            pair = result["environment"]["block_pairs"][0]
            assert pair["valid"] is True, (container_label, tag)
            markers = [
                item
                for item in result["macros"]
                if item["name"] in {"Erdhaufen", "EndeErdhaufen"}
            ]
            assert len(markers) == 2, (container_label, tag)
            assert not any(item[flag] for item in markers), (container_label, tag)

        trailing = mapper.map_text(
            _synthetic_course(
                ["lia-loot"],
                (
                    "## Type seven trailing text\n"
                    + prefix
                    + "<span /> trailing text\n"
                    + "@Erdhaufen\nX\n@EndeErdhaufen\n"
                ),
            ),
            source_path=f"type-seven-{container_label}-trailing-text.md",
        )
        pair = trailing["environment"]["block_pairs"][0]
        assert pair["valid"] is False, container_label
        assert reason in pair["exclusion_reasons"], container_label

        running = mapper.map_text(
            _synthetic_course(
                ["lia-loot"],
                (
                    "## Type seven running paragraph\n"
                    + prefix
                    + "Paragraph\n"
                    + "<span />\n"
                    + "@Erdhaufen\nX\n@EndeErdhaufen\n"
                ),
            ),
            source_path=f"type-seven-{container_label}-paragraph.md",
        )
        pair = running["environment"]["block_pairs"][0]
        assert pair["valid"] is False, container_label
        assert reason in pair["exclusion_reasons"], container_label

        for tag in (
            "<script/>",
            "<pre/>",
            "<style/>",
            "<textarea/>",
        ):
            reserved = mapper.map_text(
                _synthetic_course(
                    ["lia-loot"],
                    (
                        "## Reserved type-one name\n"
                        + prefix
                        + tag
                        + "\n@Erdhaufen\nX\n@EndeErdhaufen\n"
                    ),
                ),
                source_path=(
                    f"type-seven-reserved-{container_label}-"
                    + tag.strip("</>")
                    + ".md"
                ),
            )
            pair = reserved["environment"]["block_pairs"][0]
            assert pair["valid"] is False, (container_label, tag)
            assert reason in pair["exclusion_reasons"], (
                container_label,
                tag,
            )

        for tag in ("</script>", "</pre>", "</style>", "</textarea>"):
            closing_type_seven = mapper.map_text(
                _synthetic_course(
                    ["lia-loot"],
                    (
                        "## Reserved-name closing Type seven\n"
                        + prefix
                        + tag
                        + "\n@Erdhaufen\nX\n@EndeErdhaufen\n"
                    ),
                ),
                source_path=(
                    f"type-seven-closing-{container_label}-"
                    + tag.strip("</>")
                    + ".md"
                ),
            )
            pair = closing_type_seven["environment"]["block_pairs"][0]
            assert pair["valid"] is True, (container_label, tag)

        for tag in ("<script>", "<script />"):
            type_one = mapper.map_text(
                _synthetic_course(
                    ["lia-loot"],
                    (
                        "## Actual type one\n"
                        + prefix
                        + tag
                        + "\n@Erdhaufen\nX\n@EndeErdhaufen\n"
                    ),
                ),
                source_path=f"actual-type-one-{container_label}.md",
            )
            pair = type_one["environment"]["block_pairs"][0]
            assert pair["valid"] is True, (container_label, tag)

        new_container = mapper.map_text(
            _synthetic_course(
                ["lia-loot"],
                (
                    "## Parent paragraph to container\nRoot paragraph\n"
                    + prefix
                    + "<span />\n"
                    + "@Erdhaufen\nX\n@EndeErdhaufen\n"
                ),
            ),
            source_path=f"type-seven-new-{container_label}.md",
        )
        pair = new_container["environment"]["block_pairs"][0]
        assert pair["valid"] is True, container_label

        same_container_body = (
            "> Paragraph\n> <span />\n"
            if container_label == "quote"
            else "- Paragraph\n  <span />\n"
        )
        same_container = mapper.map_text(
            _synthetic_course(
                ["lia-loot"],
                (
                    "## Same container paragraph\n"
                    + same_container_body
                    + "@Erdhaufen\nX\n@EndeErdhaufen\n"
                ),
            ),
            source_path=f"type-seven-same-{container_label}.md",
        )
        pair = same_container["environment"]["block_pairs"][0]
        assert pair["valid"] is False, container_label
        assert reason in pair["exclusion_reasons"], container_label

    for tag_index, tag in enumerate(standalone_tags):
        root_type_seven = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Root type seven state\n"
                    + tag
                    + f"\n    @LLMQuiz({1700 + tag_index})\n"
                    + "    [[visible raw html block content]]\n\n"
                ),
            ),
            source_path=f"type-seven-root-state-{tag_index}.md",
        )
        assert spans(root_type_seven, "indented_code") == [], tag
        assert f"@LLMQuiz({1700 + tag_index})" in llm_raw(root_type_seven), tag
        assert root_type_seven["block_ranges"]["native_quiz"], tag

    for list_label, marker, continuation_indent in (
        ("bullet", "-", "  "),
        ("ordered", "1.", "   "),
    ):
        for suffix_index, suffix in enumerate(
            ("", " ", "  ", "   ", "    ", "\t", " \t")
        ):
            body = (
                "## Empty whitespace item\n"
                + marker
                + suffix
                + "\n"
                + continuation_indent
                + "@Erdhaufen\n"
                + continuation_indent
                + "X\n"
                + continuation_indent
                + "@EndeErdhaufen\n"
            )
            result = mapper.map_text(
                _synthetic_course(["lia-loot"], body),
                source_path=(
                    f"empty-whitespace-{list_label}-{suffix_index}.md"
                ),
            )
            pair = result["environment"]["block_pairs"][0]
            assert pair["valid"] is False, (list_label, repr(suffix))
            assert pair["exclusion_reasons"] == ["marker_in_list"], (
                list_label,
                repr(suffix),
            )
            markers = [
                item
                for item in result["macros"]
                if item["name"] in {"Erdhaufen", "EndeErdhaufen"}
            ]
            assert len(markers) == 2 and all(
                item["inside_list"] for item in markers
            ), (list_label, repr(suffix))

            native = mapper.map_text(
                _synthetic_course(
                    ["lia-loot"],
                    (
                        "## Empty whitespace native\n"
                        + marker
                        + suffix
                        + "\n"
                        + continuation_indent
                        + "[[answer]]\n"
                    ),
                ),
                source_path=(
                    f"empty-whitespace-native-{list_label}-"
                    f"{suffix_index}.md"
                ),
            )
            quiz = native["block_ranges"]["native_quiz"][0]
            assert quiz["container_kind"] == "list", (
                list_label,
                repr(suffix),
            )

        blank_view, _, _, blank_components, _ = (
            mapper._raw_html_container_parts(marker + "     ")
        )
        assert blank_view == "", list_label
        assert blank_components[-1]["content_indent"] == len(marker) + 1
        content_view, _, _, content_components, _ = (
            mapper._raw_html_container_parts(marker + "     content")
        )
        assert content_view == "    content", list_label
        assert content_components[-1]["content_indent"] == len(marker) + 1

    quoted_empty = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## Quoted empty item\n> -  \n"
                ">   @Erdhaufen\n>   X\n>   @EndeErdhaufen\n"
            ),
        ),
        source_path="quoted-empty-whitespace-item.md",
    )
    pair = quoted_empty["environment"]["block_pairs"][0]
    assert pair["valid"] is False
    assert {
        "marker_in_list",
        "marker_in_blockquote",
    }.issubset(pair["exclusion_reasons"])

    deeply_nested_empty = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## Deep empty item\n- > 1.  \n"
                "  >    @Erdhaufen\n"
                "  >    X\n"
                "  >    @EndeErdhaufen\n"
            ),
        ),
        source_path="deep-empty-whitespace-item.md",
    )
    pair = deeply_nested_empty["environment"]["block_pairs"][0]
    assert pair["valid"] is False
    assert {
        "marker_in_list",
        "marker_in_blockquote",
    }.issubset(pair["exclusion_reasons"])

    dedented_empty = mapper.map_text(
        _synthetic_course(
            ["lia-loot"],
            (
                "## Dedented empty item\n-   \n  item\n\n"
                "@Erdhaufen\nX\n@EndeErdhaufen\n"
            ),
        ),
        source_path="dedented-empty-whitespace-item.md",
    )
    pair = dedented_empty["environment"]["block_pairs"][0]
    assert pair["valid"] is True

    mixed_breaks = ("-*-", "*_ *".replace(" ", ""), "_-_", bs + "---", "--x-")
    for offset, candidate in enumerate(mixed_breaks):
        quiz_id = 1800 + offset
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Mixed thematic\nParagraph "
                    + bt
                    + "open\n"
                    + candidate
                    + f"\n@LLMQuiz({quiz_id})\n[[hidden]] "
                    + bt
                    + "\n"
                ),
            ),
            source_path=f"mixed-thematic-{offset}.md",
        )
        assert len(spans(result, "inline_code")) == 1, candidate
        assert f"@LLMQuiz({quiz_id})" not in llm_raw(result), candidate
        assert result["block_ranges"]["native_quiz"] == [], candidate

    for offset, candidate in enumerate(
        ("---", "***", "___", "* * *", "   - - -")
    ):
        quiz_id = 1810 + offset
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## True thematic\nParagraph "
                    + bt
                    + "open\n"
                    + candidate
                    + f"\n@LLMQuiz({quiz_id}) [[visible]] "
                    + bt
                    + "\n"
                ),
            ),
            source_path=f"true-thematic-{offset}.md",
        )
        assert spans(result, "inline_code") == [], candidate
        assert f"@LLMQuiz({quiz_id})" in llm_raw(result), candidate
        assert result["block_ranges"]["native_quiz"], candidate

    quoted_mixed = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Quoted mixed thematic\n> Paragraph "
                + bt
                + "open\n> -*-\n> @LLMQuiz(1820)\n"
                + "> [[hidden]] "
                + bt
                + "\n"
            ),
        ),
        source_path="quoted-mixed-thematic.md",
    )
    assert len(spans(quoted_mixed, "inline_code")) == 1
    assert "@LLMQuiz(1820)" not in llm_raw(quoted_mixed)
    assert quoted_mixed["block_ranges"]["native_quiz"] == []

    mixed_then_indented = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            "## Mixed then indent\nParagraph\n-*-\n    @LLMQuiz(1821)\n",
        ),
        source_path="mixed-thematic-then-indented.md",
    )
    assert spans(mixed_then_indented, "indented_code") == []
    assert "@LLMQuiz(1821)" in llm_raw(mixed_then_indented)

    true_then_indented = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            "## True then indent\nParagraph\n---\n    @LLMQuiz(1822)\n",
        ),
        source_path="true-thematic-then-indented.md",
    )
    assert len(spans(true_then_indented, "indented_code")) == 1
    assert "@LLMQuiz(1822)" not in llm_raw(true_then_indented)

    for offset, (marker_length, info_ticks) in enumerate(((3, 2), (4, 2))):
        quiz_id = 1830 + offset
        invalid_fence = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Invalid fence info\nParagraph "
                    + bt
                    + "open\n"
                    + bt * marker_length
                    + " bad"
                    + bt * info_ticks
                    + "info\n"
                    + f"@LLMQuiz({quiz_id})\n[[hidden]] "
                    + bt
                    + "\n"
                ),
            ),
            source_path=f"invalid-fence-info-owner-{offset}.md",
        )
        assert spans(invalid_fence, "fence") == [], marker_length
        assert len(spans(invalid_fence, "inline_code")) == 1, marker_length
        assert f"@LLMQuiz({quiz_id})" not in llm_raw(invalid_fence)
        assert invalid_fence["block_ranges"]["native_quiz"] == []

    valid_fences = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Valid fence controls\n"
                + bt * 3
                + " info\n@LLMQuiz(1832)\n"
                + bt * 3
                + "\n"
                + bt * 4
                + " info\n@LLMQuiz(1833)\n"
                + bt * 4
                + "\n~~~ info"
                + bt * 2
                + "\n@LLMQuiz(1834)\n~~~\n"
                + "@LLMQuiz(1835)\n[[visible]]\n"
            ),
        ),
        source_path="valid-fence-info-controls.md",
    )
    assert len(spans(valid_fences, "fence")) == 3
    assert llm_raw(valid_fences) == {"@LLMQuiz(1835)"}
    assert valid_fences["block_ranges"]["native_quiz"]

    quoted_invalid_fence = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            (
                "## Quoted invalid fence\n> Paragraph "
                + bt
                + "open\n> "
                + bt * 3
                + " bad"
                + bt * 2
                + "info\n> @LLMQuiz(1836)\n> [[hidden]] "
                + bt
                + "\n"
            ),
        ),
        source_path="quoted-invalid-fence-owner.md",
    )
    assert spans(quoted_invalid_fence, "fence") == []
    assert len(spans(quoted_invalid_fence, "inline_code")) == 1
    assert "@LLMQuiz(1836)" not in llm_raw(quoted_invalid_fence)

    for offset, invalid_char in enumerate((chr(127), chr(31), " ")):
        quiz_id = 1840 + offset
        invalid_autolink = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Invalid URI control\n<http://example.test/"
                    + invalid_char
                    + f"@LLMQuiz({quiz_id})[[visible]]>\n"
                ),
            ),
            source_path=f"invalid-uri-control-{offset}.md",
        )
        assert spans(invalid_autolink, "html_autolink") == [], offset
        assert f"@LLMQuiz({quiz_id})" in llm_raw(invalid_autolink), offset
        assert invalid_autolink["block_ranges"]["native_quiz"], offset

    valid_unicode_autolink = mapper.map_text(
        _synthetic_course(
            ["lia-llm", "lia-loot"],
            "## Valid URI unicode\n<http://example.test/é@LLMQuiz(1843)[[hidden]]>\n",
        ),
        source_path="valid-uri-unicode.md",
    )
    assert len(spans(valid_unicode_autolink, "html_autolink")) == 1
    assert "@LLMQuiz(1843)" not in llm_raw(valid_unicode_autolink)
    assert valid_unicode_autolink["block_ranges"]["native_quiz"] == []

    for offset, value_char in enumerate(("\f", "\v", chr(127))):
        quiz_id = 1850 + offset
        unquoted_control_value = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Unquoted control value\n<input data=x"
                    + value_char
                    + f"@LLMQuiz({quiz_id})>\n"
                ),
            ),
            source_path=f"unquoted-control-value-{offset}.md",
        )
        assert len(spans(unquoted_control_value, "html_tag")) == 1, offset
        assert f"@LLMQuiz({quiz_id})" not in llm_raw(
            unquoted_control_value
        ), offset

    for offset, separator in enumerate((" ", "\t", "\n", "\r\n")):
        quiz_id = 1860 + offset
        invalid_followup = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Invalid attribute followup\n<input data=x"
                    + separator
                    + f"@LLMQuiz({quiz_id})>\n"
                ),
            ),
            source_path=f"invalid-attribute-followup-{offset}.md",
        )
        assert spans(invalid_followup, "html_tag") == [], offset
        assert f"@LLMQuiz({quiz_id})" in llm_raw(invalid_followup), offset

    for offset, invalid_separator in enumerate(("\f", "\v")):
        quiz_id = 1868 + offset
        invalid_tag_separator = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Invalid tag separator\n<input"
                    + invalid_separator
                    + f"data=x @LLMQuiz({quiz_id})>\n"
                ),
            ),
            source_path=f"invalid-tag-separator-{offset}.md",
        )
        assert spans(invalid_tag_separator, "html_tag") == [], offset
        assert f"@LLMQuiz({quiz_id})" in llm_raw(
            invalid_tag_separator
        ), offset

    for offset, value_char in enumerate(("\f", "\v")):
        quiz_id = 1870 + offset
        quoted_control_value = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Quoted control value\n<input data="
                    + dq
                    + "x"
                    + value_char
                    + f"@LLMQuiz({quiz_id})"
                    + dq
                    + ">\n"
                ),
            ),
            source_path=f"quoted-control-value-{offset}.md",
        )
        assert len(spans(quoted_control_value, "html_tag")) == 1, offset
        assert f"@LLMQuiz({quiz_id})" not in llm_raw(
            quoted_control_value
        ), offset

    def ordered_indent_case(
        label: str,
        list_source: str,
        spaces: int,
        quiz_id: int,
        visible: bool,
    ) -> None:
        indentation = " " * spaces
        result = mapper.map_text(
            _synthetic_course(
                ["lia-llm", "lia-loot"],
                (
                    "## Ordered sibling indent\n"
                    + list_source
                    + "\n"
                    + indentation
                    + f"@LLMQuiz({quiz_id})\n"
                    + indentation
                    + "[[answer]]\n"
                ),
            ),
            source_path=f"ordered-sibling-{label}-{spaces}.md",
        )
        indented = spans(result, "indented_code")
        if visible:
            assert indented == [], (label, spaces)
            assert f"@LLMQuiz({quiz_id})" in llm_raw(result), (
                label,
                spaces,
            )
            assert result["block_ranges"]["native_quiz"], (label, spaces)
        else:
            assert len(indented) == 1, (label, spaces)
            assert f"@LLMQuiz({quiz_id})" not in llm_raw(result), (
                label,
                spaces,
            )
            assert result["block_ranges"]["native_quiz"] == [], (
                label,
                spaces,
            )

    for spaces, visible in ((6, True), (7, True), (8, False)):
        ordered_indent_case(
            "one-to-ten-dot",
            "1. foo\n10. bar\n",
            spaces,
            1880 + spaces,
            visible,
        )
    for spaces, visible in ((6, True), (7, False)):
        ordered_indent_case(
            "ten-to-two-dot",
            "10. foo\n2. bar\n",
            spaces,
            1890 + spaces,
            visible,
        )
    for spaces, visible in ((7, True), (8, False)):
        ordered_indent_case(
            "one-to-ten-paren",
            "1) foo\n10) bar\n",
            spaces,
            1900 + spaces,
            visible,
        )
    for spaces, visible in ((7, True), (8, False)):
        ordered_indent_case(
            "delimiter-change-new-list",
            "1. foo\n10) bar\n",
            spaces,
            1910 + spaces,
            visible,
        )
    for spaces, visible in ((5, True), (6, False)):
        ordered_indent_case(
            "ordered-to-bullet",
            "1. foo\n- bar\n",
            spaces,
            1920 + spaces,
            visible,
        )
    for spaces, visible in ((9, True), (10, False)):
        ordered_indent_case(
            "nested-one-to-ten",
            "- 1. foo\n  10. bar\n",
            spaces,
            1930 + spaces,
            visible,
        )
    for spaces, visible in ((14, True), (15, False)):
        ordered_indent_case(
            "nine-digit-marker",
            "1. foo\n123456789. bar\n",
            spaces,
            1940 + spaces,
            visible,
        )
    for spaces, visible in ((6, True), (7, False)):
        ordered_indent_case(
            "ten-digit-nonmarker",
            "1. foo\n1234567890. bar\n",
            spaces,
            1950 + spaces,
            visible,
        )


def main() -> None:
    test_catalog_contract()
    test_synthetic_lexer_and_macro_tree()
    test_every_import_rank_and_n_plus_one_slots()
    test_provider_semantics_and_candidate_contracts()
    test_provider_false_positives_fail_closed()
    test_invalid_environment_and_lootif_ranges()
    test_fence_negative_cases()
    test_indented_code_tabstops_containers_and_continuations()
    test_container_tab_residual_columns()
    test_link_reference_paragraph_and_container_state()
    test_list_switch_and_outer_interrupt_contexts()
    test_multiline_inline_markup_paragraph_and_container_state()
    test_finite_html_tag_paragraph_boundaries()
    test_lootif_trigger_matrix_and_cross_family_lifo()
    test_trigger_witness_hardening()
    test_concealment_inventory_edits_and_remap()
    test_bom_crlf_and_all_position_domains()
    test_nul_commonmark_shadow_and_original_offsets()
    test_native_quiz_drag_and_protected_near_misses()
    test_typed_provider_alternatives_and_near_misses()
    test_protected_and_boundary_hardening()
    test_freeze_audit_fail_closed_regressions()
    test_final_commonmark_owner_and_html_block_regressions()
    results = test_twelve_course_regressions()
    test_corpus_edge_cases(results)
    print(
        "PASS map_course P1: catalog, lexer, exact N+1 imports, "
        "semantic providers, candidates, invalid ranges, BOM/CRLF, "
        "read-only 12-course tree"
    )


if __name__ == "__main__":
    main()
