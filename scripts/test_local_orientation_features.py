#!/usr/bin/env python3
"""Synthetic feature regressions; no real configuration or source is read."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

import local_orientation_features as features
import local_orientation_metadata as metadata
import local_orientation_tex as tex


ROOT = Path(__file__).resolve().parents[1]
SENTINELS = (
    "PRIVATE_TASK_SENTINEL", "PRIVATE_SOLUTION_SENTINEL",
    "938475610293", "x=PRIVATE_FORMULA_SENTINEL",
)


def source(*subjects):
    return SimpleNamespace(
        subjects=subjects, grades=(7,), learner_groups=(),
        document_types=("worksheet",), archive_policy="exclude",
    )


def ids(payload, dimension):
    return [item["id"] for item in payload["features"][dimension]]


def parse(value, *, subjects=()):
    return tex.parse_tex_text(
        value, source=source(*subjects) if subjects else None,
    ).as_dict()


def test_taxonomy_is_closed_and_canonical() -> None:
    value = features.load_taxonomy()
    assert value["taxonomy_version"] == features.TAXONOMY_VERSION == 1
    assert tuple(value["dimensions"]) == features.FEATURE_DIMENSIONS
    assert set(features.FEATURE_IDS) == set(features.FEATURE_DIMENSIONS)
    assert all(features.FEATURE_IDS[dimension]
               for dimension in features.FEATURE_DIMENSIONS)
    try:
        value["dimensions"]["topic_ids"]["energy"]["terms"] = (
            "private-rule-sentinel",
        )
    except TypeError:
        pass
    else:
        raise AssertionError("cached taxonomy mapping is mutable")
    try:
        value["dimensions"]["topic_ids"]["energy"]["terms"][0] = (
            "private-rule-sentinel"
        )
    except TypeError:
        pass
    else:
        raise AssertionError("cached taxonomy sequence is mutable")
    with tempfile.TemporaryDirectory() as temporary:
        alien = Path(temporary) / "taxonomy.json"
        alien.write_text("{}", encoding="utf-8")
        try:
            features.load_taxonomy(alien)
        except features.FeatureFault as fault:
            assert fault.code == "feature_taxonomy_boundary"
            assert fault.__cause__ is None and fault.__context__ is None
            assert str(alien) not in str(fault) + repr(fault)
        else:
            raise AssertionError("noncanonical taxonomy accepted")


def test_mathematics_and_physics_features() -> None:
    mathematics = parse(
        r"""
\begin{aufgabe}
Berechne 12,5 Prozent und stelle die Daten in einer Tabelle dar.
\begin{enumerate}
\item Bestimme den Prozentsatz.
\item Vergleiche die Ergebnisse.
\end{enumerate}
\end{aufgabe}
""",
        subjects=("mathematics",),
    )
    assert mathematics["schema_version"] == 2
    assert mathematics["parser_version"] == 2
    assert mathematics["features"]["status"] == "classified"
    assert "fractions-percentages" in ids(mathematics, "topic_ids")
    assert "calculation" in ids(mathematics, "task_families")
    assert "decimal" in ids(mathematics, "number_profiles")
    assert "percentage" in ids(mathematics, "number_profiles")
    assert "table" in ids(mathematics, "representations")
    assert ids(mathematics, "complexity_bands") == ["structural-medium"]
    metadata.validate_metadata(mathematics)

    physics = parse(
        r"""
\begin{aufgabe}
Untersuche in einem Experiment Stromstärke und Spannung.
Skizziere das Diagramm der Messwerte.
\end{aufgabe}
""",
        subjects=("physics",),
    )
    assert physics["features"]["status"] == "classified"
    assert "electricity" in ids(physics, "topic_ids")
    assert "investigation" in ids(physics, "task_families")
    assert "experimental" in ids(physics, "context_profiles")
    assert {"diagram", "sketch"}.issubset(ids(physics, "representations"))
    metadata.validate_metadata(physics)


def test_unknown_ambiguous_and_review_required() -> None:
    unknown = parse("Neutraler synthetischer Dokumentrahmen.")
    assert unknown["features"]["status"] == "unknown"
    assert not any(
        unknown["features"][dimension]
        for dimension in features.FEATURE_DIMENSIONS
    )

    ambiguous = parse(
        r"\begin{aufgabe}Vergleiche Gleichung und Stromkreis.\end{aufgabe}"
    )
    assert ambiguous["features"]["status"] == "ambiguous"
    assert {"algebra-equations", "electricity"}.issubset(
        ids(ambiguous, "topic_ids")
    )

    review = parse(
        r"""
\newcommand{\unsafeexample}{Stromkreis}
\begin{aufgabe}Berechne eine Gleichung.\end{aufgabe}
""",
        subjects=("mathematics",),
    )
    assert review["features"]["status"] == "review_required"
    assert "macro_definition" in review["risk_codes"]
    metadata.validate_metadata(review)


def test_decoys_and_solution_content_are_excluded() -> None:
    payload = parse(
        r"""
% Stromkreis 938475610293 PRIVATE_TASK_SENTINEL
\newcommand{\hidden}{Prozent PRIVATE_TASK_SENTINEL}
\begin{verbatim}
Experiment Diagramm PRIVATE_TASK_SENTINEL
\end{verbatim}
\begin{aufgabe}
Nenne eine neutrale Eigenschaft.
\begin{loesung}
Stromkreis 938475610293 x=PRIVATE_FORMULA_SENTINEL
PRIVATE_SOLUTION_SENTINEL
\end{loesung}
\end{aufgabe}
""",
        subjects=("physics",),
    )
    assert "electricity" not in ids(payload, "topic_ids")
    assert "experimental" not in ids(payload, "context_profiles")
    assert "diagram" not in ids(payload, "representations")
    assert not ids(payload, "number_profiles")
    surface = json.dumps(payload["features"], ensure_ascii=False)
    assert all(sentinel not in surface for sentinel in SENTINELS)
    metadata.validate_metadata(payload)


def test_operator_does_not_create_afb_or_raise_structural_complexity() -> None:
    payload = parse(
        r"\begin{aufgabe}Berechne einen Wert.\end{aufgabe}",
        subjects=("mathematics",),
    )
    assert "compute-determine" in ids(payload, "learning_actions")
    assert ids(payload, "complexity_bands") == ["structural-low"]
    assert all(
        "afb" not in identifier and "difficulty" not in identifier
        for dimension in features.FEATURE_DIMENSIONS
        for identifier in ids(payload, dimension)
    )


def test_metadata_rejects_open_or_inconsistent_features() -> None:
    base = parse(
        r"\begin{aufgabe}Berechne Prozentwerte.\end{aufgabe}",
        subjects=("mathematics",),
    )
    mutations = []
    raw = copy.deepcopy(base)
    raw["features"]["raw_text"] = "forbidden"
    mutations.append(raw)
    alien = copy.deepcopy(base)
    alien["features"]["topic_ids"].append({
        "id": "private-topic", "basis": "body_pattern",
        "confidence": "medium",
    })
    mutations.append(alien)
    bad_status = copy.deepcopy(base)
    bad_status["features"]["status"] = "unknown"
    mutations.append(bad_status)
    duplicate = copy.deepcopy(base)
    duplicate["features"]["task_families"] *= 2
    mutations.append(duplicate)
    for value in mutations:
        try:
            metadata.validate_metadata(value)
        except metadata.MetadataFault as fault:
            assert fault.__cause__ is None and fault.__context__ is None
        else:
            raise AssertionError("invalid feature metadata accepted")


def test_feature_failures_and_limits_are_sanitized() -> None:
    secret = "PRIVATE_FEATURE_ERROR_SENTINEL"
    try:
        features.extract_features(
            secret,
            tasks="not-a-sequence",
            solutions=(),
            classification={},
            warning_codes=(),
            risk_codes=(),
        )
    except features.FeatureFault as fault:
        assert fault.code == "feature_input_invalid"
        assert fault.__cause__ is None and fault.__context__ is None
        assert secret not in str(fault) + repr(fault)
    else:
        raise AssertionError("invalid input accepted")
    try:
        features.FeatureLimits(max_seconds=6)
    except features.FeatureFault as fault:
        assert fault.code == "feature_limits_invalid"
    else:
        raise AssertionError("invalid feature limits accepted")


def main() -> int:
    test_taxonomy_is_closed_and_canonical()
    test_mathematics_and_physics_features()
    test_unknown_ambiguous_and_review_required()
    test_decoys_and_solution_content_are_excluded()
    test_operator_does_not_create_afb_or_raise_structural_complexity()
    test_metadata_rejects_open_or_inconsistent_features()
    test_feature_failures_and_limits_are_sanitized()
    print("Local orientation feature tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
