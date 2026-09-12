#!/usr/bin/env python3
"""Read-only, source-pinned structural profiles of real weekly courses.

Uses the public map_course.map_source entry point. Source order, heading roles
and range membership describe authored structure, not a proven runtime path or
an assessment of pedagogical quality. No corpus code is imported or executed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Sequence

import map_course

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ID = "ghrepo:mint-the-gap/wochenaufgabe"
DEFAULT_SNAPSHOT = ROOT / "skills/schullia-gamification/references/accepted-weekly-courses.json"
OPTIONS_PATH = ROOT / "references/lia-loot-options.json"
COURSE_PATH = re.compile(r"(?P<grade>\d+)/(?P<subject>[^/]+)/Lia(?P=grade)_(?P<week>\d+)\.md")
CONFIGURATIONS = {"Highscore", "Ressourcen", "achievements"}
FAMILIES = {
    "Highscore": "score", "Ressourcen": "resource_configuration",
    "achievements": "achievements", "lootif": "conditional_spawn",
    "Endelootif": "conditional_spawn", "Schatztruhe": "reward",
    "Diamanttruhe": "reward", "Energiekiste": "reward", "Schluessel": "key",
    "Schloss": "lock", "Puzzleteil": "puzzle_piece", "Puzzletor": "puzzle_gate",
    "Lupe": "tool", "Schaufel": "tool", "Giesskanne": "tool",
    "Erdhaufen": "earth", "EndeErdhaufen": "earth", "Erdhaufen.inline": "earth",
    "Pflanze": "plant", "EndePflanze": "plant", "Pflanze.inline": "plant",
    "Portal": "portal", "Einwegportal": "portal", "Unsichtbar": "concealment",
    "Zauberstaub": "concealment", "Geheimfolie": "secret_slide",
}
TASK_TARGETS = {"markerquiz", "kachel", "coordinate", "mathpath", "llm"}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def macro_catalog(options: dict[str, Any]) -> tuple[dict[str, str], set[str]]:
    aliases: dict[str, str] = {}
    closing: set[str] = set()
    for name, specification in options["macros"].items():
        canonical = specification.get("alias_of", name)
        for spelling in [name, *specification.get("aliases", [])]:
            aliases[spelling.casefold()] = canonical
        if "closes" in specification:
            closing.add(canonical)
    return aliases, closing


def source_snapshot(corpus_root: Path) -> tuple[Path, dict[str, Any]]:
    matches = []
    for path in sorted((corpus_root / "sources").glob("*/source.json")):
        source = read_json(path)
        if source.get("source_id") == SOURCE_ID:
            matches.append((path.parent, source))
    if len(matches) != 1:
        raise ValueError(f"Expected one local {SOURCE_ID} snapshot, found {len(matches)}")
    return matches[0]


def contains(span: dict[str, Any], position: int) -> bool:
    return span["char_start"] <= position < span["char_end"]


def sorted_counts(values: Sequence[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def event_profile(macro: dict[str, Any], report: dict[str, Any], aliases: dict[str, str], closing: set[str]) -> dict[str, Any]:
    canonical = aliases[macro["name"].casefold()]
    position = macro["span"]["char_start"]
    placements = []
    for field, label in [("feedback_depth", "feedback"), ("html_depth", "html_container"),
                         ("inside_list", "list"), ("inside_blockquote", "blockquote"),
                         ("inside_table_or_quiz", "table_or_quiz")]:
        if macro.get(field):
            placements.append(label)
    if macro.get("parent_id") is not None:
        placements.append("nested_macro")
    enclosing = []
    for kind in ("environment", "lootif"):
        for block in report["block_ranges"][kind]:
            if contains(block["span"], position):
                enclosing.append({"kind": block.get("kind", kind),
                                  "line_start": block["span"]["line_start"],
                                  "valid": block.get("valid")})
                placements.append("inside_" + block.get("kind", kind))
    if not placements:
        placements.append("standalone" if macro["standalone_line"] else "inline_text")
    return {
        "id": macro["id"], "macro": canonical, "authored_name": macro["name"],
        "family": FAMILIES.get(canonical, "catalogued_other"),
        "is_closing_marker": canonical in closing,
        "line_start": macro["span"]["line_start"],
        "column_start": macro["span"]["column_start"], "line_end": macro["span"]["line_end"],
        "argument_source": macro.get("argument_source"),
        "parent_macro_id": macro.get("parent_id"),
        "placement": sorted(set(placements)), "enclosing_ranges": enclosing,
    }


def lexical_inventory(raw: bytes, mapped: dict[str, Any], aliases: dict[str, str]) -> dict[str, Any]:
    """Expose raw source candidates separately; these are not runtime instances."""
    header_end = mapped["header"]["span"]["line_end"] if mapped["header"] else 0
    macro_pattern = re.compile(r"@(" + "|".join(re.escape(name) for name in aliases) + r")(?![\w.])", re.IGNORECASE)
    headings = []
    macros = []
    for line_number, line in enumerate(raw.decode("utf-8-sig").splitlines(), 1):
        if line_number <= header_end:
            continue
        match = re.match(r"^[ \t]{0,3}(#{1,6})[ \t]+(.+?)\s*$", line)
        if match:
            headings.append({"line_start": line_number, "level": len(match[1]), "title": match[2]})
        for match in macro_pattern.finditer(line):
            macros.append({"line_start": line_number, "column_start": match.start() + 1,
                           "macro": aliases[match[1].casefold()]})
    return {"basis": "Unclassified text matches after the main header; includes possible code, comments and literals. Not actual runtime occurrences.",
            "heading_candidates": headings, "public_macro_text_counts": sorted_counts([item["macro"] for item in macros]),
            "macro_candidates": macros}


def profile_course(raw: bytes, entry: dict[str, Any], options: dict[str, Any], *, report: dict[str, Any] | None = None, allow_additional: bool = False) -> dict[str, Any] | None:
    """Return a full-course profile, or None for an import/placeholder shell."""
    match = COURSE_PATH.fullmatch(entry["path"])
    if not match and not allow_additional:
        return None
    aliases, closing = macro_catalog(options)
    mapped = report if report is not None else map_course.map_source(raw)
    loot = [macro for macro in mapped["macros"]
            if macro["usage_context"] == "body" and macro["name"].casefold() in aliases]
    if not loot:
        return None
    learning_ids = {slide["id"] for slide in mapped["slides"] if slide["role"] == "task_or_station"}
    task_quizzes = [quiz for quiz in mapped["block_ranges"]["native_quiz"] if quiz["slide_id"] in learning_ids]
    task_instances = [instance for target in mapped["provider_targets"]["targets"]
                      if target["canonical_target"] in TASK_TARGETS
                      for instance in target["instances"] if instance.get("slide_id") in learning_ids]
    # These template macros have local task output but no loot surface target.
    placement_catalog = read_json(map_course.DEFAULT_CATALOG)
    for provider in placement_catalog["non_target_imports"]:
        if provider["provider"] not in {"lia-orthography", "lia-Mathe", "lia-pentominos"}:
            continue
        if not any(pattern.casefold() in imported["url"].casefold()
                   for pattern in provider["import_patterns"] for imported in mapped["imports"]):
            continue
        names = {name.casefold() for name in provider["instance_patterns"]}
        task_instances.extend(macro for macro in mapped["macros"]
                              if macro["usage_context"] == "body" and macro["slide_id"] in learning_ids
                              and macro["name"].casefold() in names)
    if not task_quizzes and not task_instances:
        return None
    events = {macro["id"]: event_profile(macro, mapped, aliases, closing) for macro in loot}
    slides = []
    for slide in mapped["slides"]:
        slide_events = [events[macro["id"]] for macro in loot if macro["slide_id"] == slide["id"]]
        families = [event["family"] for event in slide_events if not event["is_closing_marker"]]
        sequence = [family for index, family in enumerate(families) if index == 0 or families[index - 1] != family]
        slides.append({
            "id": slide["id"], "level": slide["level"], "title": slide["title"], "role": slide["role"],
            "line_start": slide["span"]["line_start"], "line_end": slide["span"]["line_end"],
            "native_quiz_count": sum(quiz["slide_id"] == slide["id"] for quiz in mapped["block_ranges"]["native_quiz"]),
            "macro_counts": sorted_counts([event["macro"] for event in slide_events]),
            "family_sequence": sequence, "events": slide_events,
        })
    phase_counts: dict[str, dict[str, int]] = {}
    for slide in slides:
        counter = Counter(phase_counts.get(slide["role"], {}))
        counter.update(event["family"] for event in slide["events"] if not event["is_closing_marker"])
        phase_counts[slide["role"]] = dict(sorted(counter.items()))
    learning_slides = [slide for slide in slides if slide["id"] in learning_ids]
    structural_events = [event for event in events.values() if not event["is_closing_marker"]]
    return {
        "path": entry["path"], "revision_sha": entry["revision_sha"],
        "content_sha256": hashlib.sha256(raw).hexdigest(), "web_url": entry["web_url"],
        "grade": int(match["grade"]) if match else None,
        "subject": match["subject"] if match else None, "week": int(match["week"]) if match else None,
        "course_kind": "numbered_weekly_course" if match else "additional_reviewed_course",
        "slide_count": len(slides), "learning_slide_count": len(learning_slides),
        "native_task_quiz_count": len(task_quizzes), "imported_task_instance_count": len(task_instances),
        "macro_counts": sorted_counts([event["macro"] for event in events.values()]),
        "family_counts": sorted_counts([event["family"] for event in structural_events]),
        "phase_counts": dict(sorted(phase_counts.items())),
        "placement_counts": sorted_counts([placement for event in structural_events for placement in event["placement"]]),
        "environment_counts": mapped["environment"]["counts"],
        "learning_slide_event_counts": [sum(not event["is_closing_marker"] for event in slide["events"]) for slide in learning_slides],
        "configurations": [event for event in structural_events if event["macro"] in CONFIGURATIONS],
        "imports": [{"url": item["url"], "line": item["span"]["line_start"], "order": item["order"],
                     "provider": item["provider"], "relative_to_loot": item["relative_to_loot"]} for item in mapped["imports"]],
        "slides": slides,
        "unassigned_events": [events[macro["id"]] for macro in loot if macro["slide_id"] is None],
        "diagnostics": mapped["diagnostics"],
        "structure_status": "mapper_diagnostics_require_source_review" if mapped["diagnostics"] else "no_mapper_diagnostic",
        "lexical_inventory": lexical_inventory(raw, mapped, aliases),
    }


def build_profiles(corpus_root: Path = ROOT / "corpus", *, course_paths: Sequence[str] = (), include_paths: Sequence[str] = (), strict_includes: bool = True, check_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    # Check mode only needs membership and verified hashes. A matching previous
    # profile is reusable evidence of membership, never a new acceptance grant.
    known_profiles = {item["path"]: item["content_sha256"]
                      for item in (check_snapshot["selection"].get("profiled_courses", check_snapshot["courses"])
                                   if check_snapshot else [])}
    known_other = {item["path"]: item for item in (check_snapshot["selection"].get("other_gamified_paths", [])
                                                 if check_snapshot else [])}
    directory, source = source_snapshot(corpus_root)
    options = read_json(OPTIONS_PATH)
    aliases, _ = macro_catalog(options)
    quick_match = re.compile(r"@(?:" + "|".join(re.escape(name) for name in aliases) + r")(?![\w.])", re.IGNORECASE)
    entries = [json.loads(line) for line in (directory / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if line]
    includes = set(include_paths)
    candidates = [entry for entry in entries if (COURSE_PATH.fullmatch(entry.get("path", "")) or entry.get("path") in includes) and entry.get("stored")]
    profiles = []
    excluded = []
    other_gamified_paths = []
    files_root = (directory / "files").resolve()
    markdown = [entry for entry in entries if entry.get("stored") and entry.get("path", "").lower().endswith(".md")
                and (re.match(r"\d+/", entry["path"]) or entry["path"] in includes)]
    for entry in sorted(markdown, key=lambda item: item["path"]):
        if entry["source_id"] != SOURCE_ID or entry["revision_sha"] != source["revision_sha"]:
            raise ValueError(f"Manifest/source revision mismatch: {entry['path']}")
        path = files_root.joinpath(*PurePosixPath(entry["path"]).parts).resolve()
        if not path.is_relative_to(files_root):
            raise ValueError(f"Unsafe manifest path: {entry['path']}")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["content_sha256"]:
            raise ValueError(f"Corpus file differs from manifest: {entry['path']}")
        is_course_path = bool(COURSE_PATH.fullmatch(entry["path"])) or entry["path"] in includes
        if check_snapshot and known_profiles.get(entry["path"]) == entry["content_sha256"]:
            profiles.append({key: entry[key] for key in ("path", "content_sha256", "revision_sha", "web_url")})
            continue
        previous_other = known_other.get(entry["path"])
        if not is_course_path and previous_other and previous_other.get("content_sha256") == entry["content_sha256"]:
            other_gamified_paths.append({**previous_other, "web_url": entry["web_url"]})
            continue
        if not quick_match.search(raw.decode("utf-8-sig")):
            if is_course_path:
                excluded.append({"path": entry["path"], "reason": "no_public_loot_macro_candidate"})
            continue
        mapped = map_course.map_source(raw)
        if not is_course_path:
            if any(macro["usage_context"] == "body" and macro["name"].casefold() in aliases for macro in mapped["macros"]):
                other_gamified_paths.append({"path": entry["path"], "content_sha256": entry["content_sha256"],
                                            "web_url": entry["web_url"], "reason": "outside_numbered_weekly_path_pattern"})
            continue
        profile = profile_course(raw, entry, options, report=mapped, allow_additional=entry["path"] in includes)
        if profile is None:
            excluded.append({"path": entry["path"], "reason": "no_body_loot_or_no_task_instance"})
        else:
            profiles.append(profile)
    missing_includes = includes - {profile["path"] for profile in profiles}
    if missing_includes and strict_includes:
        raise ValueError("Additional reviewed course lacks task/loot evidence: " + ", ".join(sorted(missing_includes)))
    selected_paths = set(course_paths)
    unknown = selected_paths - {profile["path"] for profile in profiles}
    if unknown:
        raise ValueError("Requested course not profiled: " + ", ".join(sorted(unknown)))
    return {
        "schema_version": 1,
        "source": {key: source[key] for key in ("source_id", "revision_sha", "web_url")},
        "selection": {
            "path_pattern": COURSE_PATH.pattern, "included_paths": sorted(includes),
            "requires": ["public_loot_macro_in_body", "native_quiz_or_catalogued_task_instance_on_task_slide"],
            "candidate_count": len(candidates), "profiled_count": len(profiles),
            "profiled_courses": [{"path": profile["path"], "content_sha256": profile["content_sha256"]} for profile in profiles],
            "excluded": excluded, "other_gamified_paths": other_gamified_paths,
        },
        "limits": ["Source order is not runtime visit order.", "Mapper heading roles are title-based structural labels.",
                   "With mapper diagnostics, inspect originals before using counts or phase sequences for calibration.",
                   "Macro counts include authored occurrences, not expanded targets or actions.",
                   "Placements are non-exclusive range/context observations.",
                   "Profiles do not certify solvability, resources, or pedagogical quality.",
                   "Only an explicitly accepted snapshot establishes the accepted reference set."],
        "courses": [profile for profile in profiles if not selected_paths or profile["path"] in selected_paths],
    }


def compare_snapshot(current: dict[str, Any], accepted: dict[str, Any]) -> dict[str, Any]:
    if accepted.get("schema_version") != current["schema_version"]:
        raise ValueError("Snapshot schema differs; review and regenerate explicitly")
    if accepted["source"]["source_id"] != current["source"]["source_id"]:
        raise ValueError("Accepted snapshot uses a different source")
    now = {item["path"]: item["content_sha256"] for item in current["selection"]["profiled_courses"]}
    prior = {item["path"]: item["content_sha256"] for item in accepted["courses"]}
    observed = {item["path"]: item["content_sha256"] for item in accepted["selection"].get("profiled_courses", accepted["courses"])}
    other_now = {item["path"] for item in current["selection"].get("other_gamified_paths", [])}
    other_prior = {item["path"] for item in accepted["selection"].get("other_gamified_paths", [])}
    result = {
        "new_review_candidates": sorted(other_now - other_prior - observed.keys()),
        "source_revision_changed": current["source"]["revision_sha"] != accepted["source"]["revision_sha"],
        "accepted_revision_sha": accepted["source"]["revision_sha"], "current_revision_sha": current["source"]["revision_sha"],
        "added": sorted(now.keys() - observed.keys()), "removed": sorted(prior.keys() - now.keys()),
        "changed": sorted(path for path in prior.keys() & now.keys() if prior[path] != now[path]),
        "known_unaccepted": sorted((now.keys() & observed.keys()) - prior.keys()),
        "known_unaccepted_changed": sorted(path for path in (now.keys() & observed.keys()) - prior.keys() if now[path] != observed[path]),
    }
    result["matches"] = not any(result[key] for key in ("added", "removed", "changed", "new_review_candidates"))
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", type=Path, default=ROOT / "corpus")
    parser.add_argument("--course", action="append", default=[], help="Relative weekly course path; repeatable")
    parser.add_argument("--include-course", action="append", default=[], help="Explicitly reviewed course outside the numbered path pattern; repeatable")
    parser.add_argument("--json", action="store_true", help="Explicit full profile export to stdout")
    parser.add_argument("--check", nargs="?", type=Path, const=DEFAULT_SNAPSHOT, help="Compare with accepted snapshot; never overwrite it")
    args = parser.parse_args(argv)
    try:
        accepted = read_json(args.check) if args.check else None
        includes = sorted(set(args.include_course) | set(accepted["selection"].get("included_paths", []) if accepted else []))
        profile = build_profiles(args.corpus_root, course_paths=args.course, include_paths=includes, strict_includes=not bool(args.check), check_snapshot=accepted)
        if args.check:
            result = compare_snapshot(profile, accepted)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("Accepted courses: " + ("unchanged" if result["matches"] else "review required"))
                for key in ("added", "removed", "changed", "new_review_candidates", "known_unaccepted_changed"):
                    if result[key]:
                        print(key + ": " + ", ".join(result[key]))
                if result["source_revision_changed"]:
                    print("Source revision changed; acceptance remains attached to unchanged file hashes.")
            return 0 if result["matches"] else 1
        if args.json:
            print(json.dumps(profile, ensure_ascii=False, indent=2))
        else:
            print(f"{profile['source']['source_id']} @ {profile['source']['revision_sha']}")
            print(f"{profile['selection']['profiled_count']} profiled / {profile['selection']['candidate_count']} candidate courses; {len(profile['courses'])} shown")
            print("Course\tSlides\tLearning\tLoot macros\tFamilies\tDiagnostics")
            for course in profile["courses"]:
                print(f"{course['path']}\t{course['slide_count']}\t{course['learning_slide_count']}\t{sum(course['macro_counts'].values())}\t{len(course['family_counts'])}\t{len(course['diagnostics'])}")
            if args.course:
                for course in profile["courses"]:
                    print("\n" + course["path"] + " ? authored slide sequence")
                    for slide in course["slides"]:
                        counts = Counter(label for event in slide["events"] for label in event["placement"])
                        placements = ", ".join(f"{label}:{count}" for label, count in sorted(counts.items())) or "none"
                        families = " > ".join(slide["family_sequence"]) or "none"
                        print(f"L{slide['line_start']} {slide['title']} [{slide['role']}] ? {families}; placement {placements}")
            if profile["selection"]["other_gamified_paths"]:
                print("Other body-loot files (manual scope review): " + ", ".join(item["path"] for item in profile["selection"]["other_gamified_paths"]))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"Profile error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
