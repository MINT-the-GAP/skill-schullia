#!/usr/bin/env python3
"""Dependency-free regressions for the optional local-overlay boundary."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import check_local_orientation_leaks as leaks
import local_orientation_config as config

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
AVAILABLE = "lokal verf\u00fcgbar"
NOT_CONFIGURED = "lokal nicht konfiguriert"
NOT_REACHABLE = "lokal nicht erreichbar"
EXCLUDED = "lokal wegen Sicherheitspr\u00fcfung ausgeschlossen"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, env=os.environ.copy(), text=True,
        encoding="utf-8", errors="replace", capture_output=True, check=False,
    )


def git(repo: Path, *args: str, check: bool = True):
    result = run(["git", *args], repo)
    if check and result.returncode:
        raise AssertionError(f"git failed with {result.returncode}: {args[0]}")
    return result


def init_repo(repo: Path) -> None:
    repo.mkdir(parents=True)
    git(repo, "init", "--quiet")
    git(repo, "config", "user.name", "Synthetic Test")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    git(repo, "config", "core.autocrlf", "false")
    (repo / ".gitignore").write_text(
        "/.schullia-local/\n", encoding="utf-8"
    )
    git(repo, "add", ".gitignore")


def create_directory_link(link: Path, target: Path) -> bool:
    try:
        link.symlink_to(target, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        if os.name != "nt":
            return False
    result = run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        link.parent,
    )
    return result.returncode == 0


def layout(base: Path) -> tuple[Path, Path, Path]:
    repo = base / "public-repository"
    source = base / "external-source"
    (source / "mathematics" / "grade-7").mkdir(parents=True)
    init_repo(repo)
    return repo, source, base / "local-config.json"


def valid(source: Path, enabled: bool = True) -> dict[str, object]:
    return {
        "schema_version": 1,
        "enabled": enabled,
        "usage_context": "orientation-only",
        "state_directory": ".schullia-local/state",
        "sources": [{
            "id": "source-one",
            "root": str(source),
            "include": ["mathematics/grade-7"],
            "exclude": ["mathematics/grade-7/archive"],
            "allowed_extensions": [".tex"],
            "subjects": ["mathematics"],
            "grades": [7],
            "archive_policy": "exclude",
            "risk_policy": {
                "allow_exams": False,
                "allow_third_party": False,
                "allow_administrative": False,
                "allow_personal_data": False,
            },
        }],
    }


def evaluate(repo: Path, path: Path):
    return config.validate_configuration(repo, explicit_config=path, environ={})


def assert_sanitized(result) -> None:
    public = json.dumps(result.as_dict(), ensure_ascii=False)
    for private_key in ('"root"', '"sources"', '"include"', '"exclude"'):
        assert private_key not in public


def test_configuration_states() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, path = layout(base)
        assert config.validate_configuration(repo, environ={}).availability_state == NOT_CONFIGURED
        assert evaluate(repo, base / "missing.json").availability_state == NOT_REACHABLE
        write_json(path, valid(source, False))
        assert evaluate(repo, path).availability_state == NOT_CONFIGURED
        write_json(path, valid(source))
        result = evaluate(repo, path)
        assert result.availability_state == AVAILABLE
        payload = result.as_dict()
        assert payload["capabilities"] == {
            "configuration": "implemented",
            "candidate_selection": "implemented",
            "tex_parser": "implemented",
            "local_metadata_schema": "implemented",
            "include_resolution": "implemented",
            "local_index": "implemented",
            "local_search": "implemented",
            "federated_search": "implemented",
            "controlled_feature_extraction": "implemented",
            "orientation_guidance": "implemented",
            "canonical_skill_routing": "implemented",
            "transactional_activation": "implemented",
            "near_copy_gate": "implemented",
            "acceptance_witness": "implemented",
        }
        assert payload["local_search_performed"] is False
        assert payload["orientation_profile_prepared"] is False
        assert payload["local_orientation_used"] is False
        assert_sanitized(result)
        write_json(path, valid(base / "unreachable"))
        assert evaluate(repo, path).availability_state == NOT_REACHABLE


def test_validated_source_api() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, path = layout(base)
        value = valid(source)
        write_json(path, value)
        result, sources = config.load_validated_sources(
            repo, explicit_config=path, environ={}
        )
        assert result.availability_state == AVAILABLE
        assert len(sources) == 1
        validated = sources[0]
        assert validated.source_id == "source-one"
        assert validated.root == source.resolve()
        assert validated.include == ("mathematics/grade-7",)
        assert validated.exclude == ("mathematics/grade-7/archive",)
        assert validated.allowed_extensions == (".tex",)
        assert validated.subjects == ("mathematics",)
        assert validated.grades == (7,)
        public_repr = repr(validated)
        assert str(source) not in public_repr
        assert validated.include[0] not in public_repr
        assert validated.source_id not in public_repr
        assert "count" not in public_repr
        try:
            validated.source_id = "changed"
        except (AttributeError, TypeError):
            pass
        else:
            raise AssertionError("validated_source_mutable")

        disabled = valid(base / "disabled-root-must-not-be-touched", False)
        write_json(path, disabled)
        original_path_check = config._path_chain_has_link

        def forbidden_path_check(_candidate: Path) -> bool:
            raise AssertionError("disabled_source_root_touched")

        config._path_chain_has_link = forbidden_path_check
        try:
            disabled_result, disabled_sources = config.load_validated_sources(
                repo, explicit_config=path, environ={}
            )
        finally:
            config._path_chain_has_link = original_path_check
        assert disabled_result.availability_state == NOT_CONFIGURED
        assert disabled_sources == ()


def test_configuration_discovery_precedence() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, _source, _path = layout(base)
        default = repo / ".schullia-local" / "config.json"
        environment = base / "environment.json"
        explicit = base / "explicit.json"
        for candidate in (default, environment, explicit):
            write_json(candidate, {})
        selected, origin = config.discover_config(
            repo,
            explicit_config=explicit,
            environ={config.ENVIRONMENT_VARIABLE: str(environment)},
        )
        assert selected == explicit and origin == "explicit"
        selected, origin = config.discover_config(
            repo,
            environ={config.ENVIRONMENT_VARIABLE: str(environment)},
        )
        assert selected == environment and origin == "environment"
        selected, origin = config.discover_config(repo, environ={})
        assert selected == default and origin == "default"


def test_validator_does_not_open_or_mutate_source_documents() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, path = layout(base)
        document = source / "mathematics" / "grade-7" / "synthetic.tex"
        document.write_bytes(b"synthetic private fixture")
        write_json(path, valid(source))
        before = (
            document.read_bytes(),
            document.stat().st_size,
            document.stat().st_mtime_ns,
            sorted(item.relative_to(source).as_posix() for item in source.rglob("*")),
        )
        original_open = Path.open
        resolved_source = source.resolve()

        def guarded_open(candidate: Path, *args, **kwargs):
            try:
                candidate.resolve().relative_to(resolved_source)
            except (OSError, ValueError):
                return original_open(candidate, *args, **kwargs)
            raise AssertionError("source_document_opened")

        Path.open = guarded_open
        try:
            result = evaluate(repo, path)
        finally:
            Path.open = original_open
        after = (
            document.read_bytes(),
            document.stat().st_size,
            document.stat().st_mtime_ns,
            sorted(item.relative_to(source).as_posix() for item in source.rglob("*")),
        )
        assert result.availability_state == AVAILABLE
        assert after == before


def test_invalid_configs_and_boundaries() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, path = layout(base)
        cases = []
        for key, value in (
            ("schema_version", 2), ("schema_version", True),
            ("usage_context", "task-content"),
            ("enabled", "yes"),
        ):
            case = valid(source)
            case[key] = value
            cases.append(case)
        for include in (
            [],
            ["../outside"],
            [str(base.resolve())],
            ["."],
            [" whitespace "],
            ["folder:stream"],
        ):
            case = valid(source)
            case["sources"][0]["include"] = include
            cases.append(case)
        inside = repo / "source"
        (inside / "mathematics" / "grade-7").mkdir(parents=True)
        for unsafe in (inside, base, Path(repo.anchor)):
            cases.append(valid(unsafe))
        for number, case in enumerate(cases):
            candidate = path.with_name(f"invalid-{number}.json")
            write_json(candidate, case)
            result = evaluate(repo, candidate)
            assert result.availability_state == EXCLUDED, (
                number,
                result.as_dict(),
            )
            assert_sanitized(result)
        path.write_text("{malformed", encoding="utf-8")
        assert evaluate(repo, path).availability_state == EXCLUDED


def test_local_config_and_symlink_boundary() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, _path = layout(base)
        local_path = repo / ".schullia-local" / "config.json"
        write_json(local_path, valid(source))
        assert evaluate(repo, local_path).availability_state == AVAILABLE
        git(repo, "add", "--force", ".schullia-local/config.json")
        assert evaluate(repo, local_path).availability_state == EXCLUDED
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, path = layout(base)
        outside = base / "outside"
        outside.mkdir()
        link = source / "mathematics" / "linked-grade"
        if not create_directory_link(link, outside):
            return
        value = valid(source)
        value["sources"][0]["include"] = ["mathematics/linked-grade"]
        write_json(path, value)
        assert evaluate(repo, path).availability_state == EXCLUDED
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, path = layout(base)
        linked_parent = repo / "linked-source"
        if not create_directory_link(linked_parent, source):
            return
        value = valid(linked_parent / "mathematics")
        value["sources"][0]["include"] = ["grade-7"]
        value["sources"][0]["exclude"] = ["grade-7/archive"]
        write_json(path, value)
        assert evaluate(repo, path).availability_state == EXCLUDED


def test_needle_loader_rejects_local_zone_link_before_read() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, _path = layout(base)
        external_zone = base / "external-zone"
        external_zone.mkdir()
        external_config = external_zone / "config.json"
        write_json(external_config, valid(source))
        if not create_directory_link(repo / ".schullia-local", external_zone):
            return
        original_open = Path.open

        def guarded_open(candidate: Path, *args, **kwargs):
            if candidate.resolve(strict=False) == external_config.resolve():
                raise AssertionError("unsafe_local_config_read")
            return original_open(candidate, *args, **kwargs)

        Path.open = guarded_open
        try:
            needles = config.private_config_needles(repo, environ={})
        finally:
            Path.open = original_open
        assert needles == []


def test_real_ignore_rule_and_clean_gate() -> None:
    result = git(
        ROOT, "check-ignore", "--no-index",
        ".schullia-local/config.json", check=False,
    )
    assert result.returncode == 0, result.stderr
    with tempfile.TemporaryDirectory() as temporary:
        repo = Path(temporary) / "repo"
        init_repo(repo)
        (repo / "README.md").write_text(
            "https://example.invalid/course and public/relative/path\n",
            encoding="utf-8",
        )
        git(repo, "add", "README.md")
        assert leaks.scan_repository(repo, environ={}).clean


def test_force_add_and_forbidden_sources() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        repo = Path(temporary) / "repo"
        init_repo(repo)
        artifact = repo / ".schullia-local" / "config.json"
        write_json(artifact, {"synthetic": True})
        git(repo, "add", "--force", ".schullia-local/config.json")
        assert not leaks.scan_repository(repo, environ={}).clean
        git(repo, "commit", "--quiet", "-m", "synthetic artifact")
        assert not leaks.scan_repository(repo, environ={}).clean
    for suffix in (".tex", ".ltx", ".sty", ".cls", ".bib"):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            init_repo(repo)
            candidate = repo / ("synthetic" + suffix)
            candidate.write_text("synthetic fixture\n", encoding="utf-8")
            git(repo, "add", candidate.name)
            assert not leaks.scan_repository(repo, environ={}).clean


def test_only_canonical_public_local_json_is_allowed() -> None:
    allowed = {
        "references/local-orientation-feature-taxonomy.json",
        "references/local-orientation-near-copy-policy.json",
    }
    for path in allowed:
        assert "local_configuration_artifact" not in leaks._path_findings(path)
    for path in (
        "local-orientation-feature-taxonomy.json",
        "local-orientation-near-copy-policy.json",
        "references/local-orientation-private.json",
        "assets/local-orientation-feature-taxonomy.json",
        "assets/local-orientation-near-copy-policy.json",
    ):
        assert "local_configuration_artifact" in leaks._path_findings(path)


def test_index_worktree_and_untracked_content() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        repo = Path(temporary) / "repo"
        init_repo(repo)
        needle = "".join(["synthetic", "-private", "-root", "-token"])
        indexed = repo / "index-only.txt"
        indexed.write_text(needle, encoding="utf-8")
        git(repo, "add", indexed.name)
        indexed.write_text("clean worktree\n", encoding="utf-8")
        assert not leaks.scan_repository(
            repo, environ={}, private_needles=[needle]
        ).clean
        git(repo, "reset", "--quiet")
        tracked = repo / "tracked.txt"
        tracked.write_text("clean index\n", encoding="utf-8")
        git(repo, "add", tracked.name)
        tracked.write_text(needle, encoding="utf-8")
        assert not leaks.scan_repository(
            repo, environ={}, private_needles=[needle]
        ).clean
        tracked.write_text("clean worktree\n", encoding="utf-8")
        (repo / "candidate.txt").write_text(needle, encoding="utf-8")
        assert not leaks.scan_repository(
            repo, environ={}, private_needles=[needle]
        ).clean


def test_local_rule_values_are_private_needles() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, path = layout(base)
        value = valid(source)
        write_json(path, value)
        rule = value["sources"][0]["include"][0]
        candidate = repo / "candidate.txt"
        candidate.write_text(rule, encoding="utf-8")
        git(repo, "add", candidate.name)
        report = leaks.scan_repository(
            repo, explicit_config=path, environ={}
        )
        assert report.findings.get("configured_private_value", 0) >= 1
        assert rule not in json.dumps(report.as_dict(), ensure_ascii=False)


def synthetic_absolute_paths() -> tuple[str, ...]:
    windows = "".join(["Q", ":", "\\", "SyntheticUser", "\\", "private"])
    unc = "".join(["\\", "\\", "synthetic-server", "\\", "share"])
    unix = "/" + "/".join(["home", "synthetic-user", "private"])
    macos = "/" + "/".join(["Users", "synthetic-user", "private"])
    root_home = "/" + "/".join(["root", "private"])
    wsl = "/" + "/".join(["mnt", "q", "Users", "synthetic-user", "private"])
    server = "/" + "/".join(["srv", "synthetic-private", "material"])
    optional = "/" + "/".join(["opt", "synthetic-private", "material"])
    volume = "/" + "/".join(["Volumes", "synthetic-private", "material"])
    mount = "/" + "/".join(["mnt", "synthetic-private", "material"])
    variable = "/" + "/".join(["var", "synthetic-private", "material"])
    private_users = "/" + "/".join(
        ["private", "Users", "synthetic-user", "private"]
    )
    file_uri = "".join(["file:", "//", server])
    variable_uri = "".join(["file:", "//", variable])
    private_users_uri = "".join(["file:", "//", private_users])
    return (
        windows,
        unc,
        unix,
        macos,
        root_home,
        wsl,
        server,
        optional,
        volume,
        mount,
        variable,
        private_users,
        file_uri,
        variable_uri,
        private_users_uri,
    )


def test_absolute_paths_and_sanitized_output() -> None:
    for private_value in synthetic_absolute_paths():
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            init_repo(repo)
            name = "".join(["private", "-candidate", ".txt"])
            (repo / name).write_text(private_value, encoding="utf-8")
            git(repo, "add", name)
            report = leaks.scan_repository(repo, environ={})
            assert not report.clean
            public = json.dumps(report.as_dict(), ensure_ascii=False)
            assert private_value not in public
            assert name not in public
    with tempfile.TemporaryDirectory() as temporary:
        repo = Path(temporary) / "repo"
        init_repo(repo)
        name = "binary-path-candidate.bin"
        private_value = "/" + "/".join(
            ["home", "synthetic-user", "private"]
        )
        (repo / name).write_bytes(
            b"synthetic-binary\x00" + private_value.encode("ascii")
        )
        git(repo, "add", name)
        report = leaks.scan_repository(repo, environ={})
        assert not report.clean
        public = json.dumps(report.as_dict(), ensure_ascii=False)
        assert private_value not in public
        assert name not in public
    for private_value in synthetic_absolute_paths():
        if "/" not in private_value:
            continue
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            init_repo(repo)
            name = "".join(["slash-escaped", "-candidate", ".txt"])
            payload = json.dumps({"path": private_value}).replace("/", "\\/")
            (repo / name).write_text(payload, encoding="utf-8")
            git(repo, "add", name)
            report = leaks.scan_repository(repo, environ={})
            assert not report.clean
            public = json.dumps(report.as_dict(), ensure_ascii=False)
            assert private_value not in public
            assert name not in public
    with tempfile.TemporaryDirectory() as temporary:
        repo = Path(temporary) / "repo"
        init_repo(repo)
        name = "".join(["unicode-escaped", "-candidate", ".txt"])
        private_value = "/" + "/".join(
            ["home", "synthetic-user", "private"]
        )
        payload = json.dumps({"path": private_value}).replace(
            "/", "\\u002f"
        )
        (repo / name).write_text(payload, encoding="utf-8")
        git(repo, "add", name)
        report = leaks.scan_repository(repo, environ={})
        assert not report.clean
        public = json.dumps(report.as_dict(), ensure_ascii=False)
        assert private_value not in public
        assert name not in public
    for private_value in synthetic_absolute_paths():
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            init_repo(repo)
            name = "".join(["json", "-candidate", ".txt"])
            (repo / name).write_text(
                json.dumps({"path": private_value}), encoding="utf-8"
            )
            git(repo, "add", name)
            report = leaks.scan_repository(repo, environ={})
            assert not report.clean
            public = json.dumps(report.as_dict(), ensure_ascii=False)
            assert private_value not in public
            assert name not in public


def test_cli_sanitization_and_real_repo_gate() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repo, source, path = layout(base)
        write_json(path, valid(source))
        commands = [
            [sys.executable, str(SCRIPTS / "local_orientation_config.py"),
             "--repo-root", str(repo), "--config", str(path), "--json"],
            [sys.executable, str(SCRIPTS / "check_local_orientation_leaks.py"),
             "--repo-root", str(repo), "--config", str(path), "--json"],
        ]
        for command in commands:
            result = run(command, repo)
            output = result.stdout + result.stderr
            assert result.returncode == 0, output
            assert str(source) not in output
        argument_sentinel = "PRIVATE_ARGUMENT_SENTINEL"
        for script in (
            "local_orientation_config.py",
            "check_local_orientation_leaks.py",
        ):
            result = run(
                [sys.executable, str(SCRIPTS / script),
                 "--" + argument_sentinel],
                repo,
            )
            output = result.stdout + result.stderr
            assert result.returncode == 2
            assert argument_sentinel not in output
        missing = base / "missing.json"
        report = leaks.scan_repository(
            ROOT, explicit_config=missing, environ={}
        )
        assert report.clean, report.as_dict()


def main() -> int:
    test_configuration_states()
    test_validated_source_api()
    test_configuration_discovery_precedence()
    test_validator_does_not_open_or_mutate_source_documents()
    test_invalid_configs_and_boundaries()
    test_local_config_and_symlink_boundary()
    test_needle_loader_rejects_local_zone_link_before_read()
    test_real_ignore_rule_and_clean_gate()
    test_force_add_and_forbidden_sources()
    test_only_canonical_public_local_json_is_allowed()
    test_index_worktree_and_untracked_content()
    test_local_rule_values_are_private_needles()
    test_absolute_paths_and_sanitized_output()
    test_cli_sanitization_and_real_repo_gate()
    print("Local orientation security tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
