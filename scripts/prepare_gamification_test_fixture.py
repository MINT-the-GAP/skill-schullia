#!/usr/bin/env python3
"""Explicitly download the pinned historical mapper fixtures outside corpus/."""

from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile

from sync_sources import GitHubClient, load_json, source_slug, sync_repository

ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = ROOT / "skills/schullia-gamification/scripts/test_map_course.py"
SPEC = importlib.util.spec_from_file_location("gamification_fixture_contract", TEST_PATH)
assert SPEC and SPEC.loader
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--force", action="store_true", help="Re-download this test cache")
    arguments = parser.parse_args()
    if arguments.timeout <= 0:
        parser.error("--timeout must be positive")
    cache_parent = (ROOT / ".test-fixtures").resolve()
    destination = contract.HISTORICAL_FIXTURE_ROOT.resolve()
    if (
        not cache_parent.is_relative_to(ROOT.resolve())
        or not destination.is_relative_to(cache_parent)
        or destination == cache_parent
    ):
        raise RuntimeError("Historical fixture destination must remain inside .test-fixtures/")
    if destination.exists() and not arguments.force:
        contract._validate_fixture_provenance(destination)
        print(f"Reused verified historical fixtures: {destination}")
        return

    configuration = load_json(ROOT / "references/sources.json")
    organization = next(
        item for item in configuration["organizations"] if item["login"] == "MINT-the-GAP"
    )
    if not any(
        item["name"] == "Wochenaufgabe" for item in organization["fallback_repositories"]
    ):
        raise RuntimeError("Wochenaufgabe is missing from the canonical source configuration")
    client = GitHubClient(
        os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"), arguments.timeout
    )
    repository = client.repository_metadata("MINT-the-GAP", "Wochenaufgabe")
    repository["default_branch"] = contract.HISTORICAL_REVISION
    cache_parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading historical test revision {contract.HISTORICAL_REVISION}", flush=True)
    with tempfile.TemporaryDirectory(prefix="prepare-", dir=cache_parent) as temporary:
        staging = Path(temporary).resolve()
        sync_repository(
            client, staging, repository, organization["collection"],
            configuration["limits"], force=True, store_binary=False,
        )
        source_tree = (
            staging / "sources" / source_slug(contract.HISTORICAL_SOURCE_ID)
        ).resolve()
        if not source_tree.is_relative_to(staging):
            raise RuntimeError("Staged historical source escaped its temporary directory")
        contract._validate_fixture_provenance(source_tree)
        # Both absolute targets were checked before this optional recursive
        # replacement; the current teaching corpus is outside this cache.
        if destination.exists():
            shutil.rmtree(destination)
        os.replace(source_tree, destination)
    contract._validate_fixture_provenance(destination)
    print(f"Prepared verified historical fixtures: {destination}")


if __name__ == "__main__":
    main()
