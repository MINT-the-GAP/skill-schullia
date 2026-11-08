#!/usr/bin/env python3
"""Validate the optional, unversioned local orientation configuration.

The validator reads configuration and filesystem metadata only. It never
opens source documents. Diagnostics are deliberately sanitized.

Exit codes: 0 available or not configured, 1 unreachable or excluded,
2 operational error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent.parent
LOCAL_ZONE = ".schullia-local"
DEFAULT_CONFIG = Path(LOCAL_ZONE) / "config.json"
STATE_DIRECTORY = f"{LOCAL_ZONE}/state"
ENVIRONMENT_VARIABLE = "SCHULLIA_LOCAL_CONFIG"

STATE_AVAILABLE = "lokal verf\u00fcgbar"
STATE_NOT_CONFIGURED = "lokal nicht konfiguriert"
STATE_UNREACHABLE = "lokal nicht erreichbar"
STATE_EXCLUDED = "lokal wegen Sicherheitspr\u00fcfung ausgeschlossen"

SOURCE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
METADATA_TOKEN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SUBJECTS = {"mathematics", "physics"}
ARCHIVE_POLICIES = {"exclude", "deprioritize"}
RISK_KEYS = {
    "allow_exams",
    "allow_third_party",
    "allow_administrative",
    "allow_personal_data",
}
TOP_LEVEL_KEYS = {
    "schema_version",
    "enabled",
    "usage_context",
    "state_directory",
    "sources",
}
SOURCE_KEYS = {
    "id",
    "root",
    "include",
    "exclude",
    "allowed_extensions",
    "subjects",
    "grades",
    "learner_groups",
    "document_types",
    "archive_policy",
    "risk_policy",
}
SOURCE_REQUIRED = {
    "id",
    "root",
    "include",
    "exclude",
    "allowed_extensions",
    "subjects",
    "archive_policy",
    "risk_policy",
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class ConfigFault(ValueError):
    """A sanitized configuration or boundary failure."""

    def __init__(self, code: str, state: str = STATE_EXCLUDED):
        super().__init__(code)
        self.code = code
        self.state = state


@dataclass(frozen=True)
class ValidationResult:
    availability_state: str
    reason_code: str
    source_count: int = 0
    allowlist_entry_count: int = 0

    @property
    def accepted(self) -> bool:
        return self.availability_state in {
            STATE_AVAILABLE,
            STATE_NOT_CONFIGURED,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "availability_state": self.availability_state,
            "reason_code": self.reason_code,
            "source_count": self.source_count,
            "allowlist_entry_count": self.allowlist_entry_count,
            "capabilities": {
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
            },
            "local_search_performed": False,
            "orientation_profile_prepared": False,
            "local_orientation_used": False,
        }


@dataclass(frozen=True, repr=False)
class ValidatedSource:
    """An active source whose configuration and filesystem boundary passed.

    The absolute root is intentionally excluded from ``repr``. Instances are
    an in-process capability for the candidate selector, never a public
    diagnostic or serialization format.
    """

    source_id: str
    root: Path
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    allowed_extensions: tuple[str, ...]
    subjects: tuple[str, ...]
    grades: tuple[int, ...]
    learner_groups: tuple[str, ...]
    document_types: tuple[str, ...]
    archive_policy: str

    def __repr__(self) -> str:
        return "ValidatedSource(<local-only>)"


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(
        attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _link(path: Path) -> bool:
    try:
        if path.is_symlink() or _reparse(path):
            return True
        isjunction = getattr(os.path, "isjunction", None)
        return bool(isjunction and isjunction(path))
    except OSError:
        return True


def _path_chain_has_link(path: Path) -> bool:
    try:
        absolute = path.absolute()
    except OSError:
        return True
    parts = absolute.parts
    if not parts:
        return True
    current = Path(parts[0])
    for part in parts[1:]:
        current = current / part
        if _link(current):
            return True
    return False


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise ConfigFault("git_unavailable") from exc


def _repo_local_config_is_safe(repo: Path, config: Path) -> bool:
    relative = config.relative_to(repo).as_posix()
    if not relative.startswith(f"{LOCAL_ZONE}/"):
        return False
    ignored = _git(repo, "check-ignore", "-q", "--", relative)
    tracked = _git(repo, "ls-files", "--error-unmatch", "--", relative)
    return ignored.returncode == 0 and tracked.returncode != 0


def discover_config(
    repo_root: Path,
    explicit_config: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> tuple[Path | None, str]:
    repo = repo_root.resolve()
    env = os.environ if environ is None else environ
    if explicit_config is not None:
        return explicit_config.expanduser(), "explicit"
    configured = env.get(ENVIRONMENT_VARIABLE, "").strip()
    if configured:
        return Path(configured).expanduser(), "environment"
    default = repo / DEFAULT_CONFIG
    if default.exists():
        return default, "default"
    return None, "absent"


def _read_json(config: Path) -> Any:
    try:
        if config.stat().st_size > 1_000_000:
            raise ConfigFault("configuration_too_large")
        return json.loads(config.read_text(encoding="utf-8-sig"))
    except ConfigFault:
        raise
    except (OSError, UnicodeError) as exc:
        raise ConfigFault("configuration_unreadable", STATE_UNREACHABLE) from exc
    except json.JSONDecodeError as exc:
        raise ConfigFault("configuration_invalid_json") from exc


def _string_list(
    value: object,
    code: str,
    *,
    nonempty: bool = False,
    unique: bool = True,
) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ConfigFault(code)
    if nonempty and not value:
        raise ConfigFault(code)
    if unique and len(value) != len(set(value)):
        raise ConfigFault(code)
    return value


def _valid_relative_rule(value: str, *, include: bool) -> None:
    if (
        not value
        or len(value) > 1024
        or value != value.strip()
        or value in {".", "./"}
        or "\x00" in value
        or "\\" in value
        or ":" in value
    ):
        raise ConfigFault("relative_rule_invalid")
    if PureWindowsPath(value).is_absolute():
        raise ConfigFault("relative_rule_absolute")
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        raise ConfigFault("relative_rule_traversal")
    if include and value.casefold() in {"*", "**", "**/*"}:
        raise ConfigFault("include_rule_too_broad")


def _static_prefix(rule: str) -> tuple[str, ...]:
    parts = []
    for part in PurePosixPath(rule).parts:
        if any(token in part for token in "*?["):
            break
        parts.append(part)
    return tuple(parts)


def _check_rule_boundary(root: Path, rule: str) -> None:
    current = root
    for part in _static_prefix(rule):
        current = current / part
        if current.exists() and _link(current):
            raise ConfigFault("allowlist_link_boundary")
        try:
            resolved = current.resolve(strict=False)
        except OSError as exc:
            raise ConfigFault("allowlist_boundary_unresolved") from exc
        if not _inside(resolved, root):
            raise ConfigFault("allowlist_boundary_escape")


def _looks_absolute(value: str) -> bool:
    return (
        Path(value).is_absolute()
        or PureWindowsPath(value).is_absolute()
        or value.startswith(("/", "\\"))
    )


def _is_broad_root(path: Path) -> bool:
    anchor = Path(path.anchor)
    if path == anchor:
        return True
    try:
        home = Path.home().resolve()
    except OSError:
        home = Path("__unavailable_home__")
    return path == home


def _validate_optional_metadata(source: Mapping[str, object]) -> None:
    grades = source.get("grades", [])
    if (
        not isinstance(grades, list)
        or any(type(item) is not int or not 5 <= item <= 13 for item in grades)
        or len(grades) != len(set(grades))
    ):
        raise ConfigFault("grades_invalid")
    groups = _string_list(source.get("learner_groups", []), "learner_groups_invalid")
    if any(not item or len(item) > 80 or "\x00" in item for item in groups):
        raise ConfigFault("learner_groups_invalid")
    document_types = _string_list(
        source.get("document_types", []), "document_types_invalid"
    )
    if any(not METADATA_TOKEN.fullmatch(item) for item in document_types):
        raise ConfigFault("document_types_invalid")


def _validate_source(
    source: object,
    repo: Path,
    *,
    check_paths: bool,
) -> tuple[Path | None, int]:
    if not isinstance(source, dict):
        raise ConfigFault("source_invalid")
    keys = set(source)
    if not SOURCE_REQUIRED.issubset(keys) or not keys.issubset(SOURCE_KEYS):
        raise ConfigFault("source_fields_invalid")

    source_id = source.get("id")
    if not isinstance(source_id, str) or not SOURCE_ID.fullmatch(source_id):
        raise ConfigFault("source_id_invalid")

    root_value = source.get("root")
    if (
        not isinstance(root_value, str)
        or not root_value
        or len(root_value) > 4096
        or "\x00" in root_value
        or not _looks_absolute(root_value)
    ):
        raise ConfigFault("source_root_invalid")

    includes = _string_list(
        source.get("include"), "include_rules_invalid", nonempty=True
    )
    excludes = _string_list(source.get("exclude"), "exclude_rules_invalid")
    for rule in includes:
        _valid_relative_rule(rule, include=True)
    for rule in excludes:
        _valid_relative_rule(rule, include=False)

    extensions = _string_list(
        source.get("allowed_extensions"),
        "allowed_extensions_invalid",
        nonempty=True,
    )
    if extensions != [".tex"]:
        raise ConfigFault("allowed_extensions_invalid")

    subjects = _string_list(source.get("subjects"), "subjects_invalid", nonempty=True)
    if not set(subjects).issubset(SUBJECTS):
        raise ConfigFault("subjects_invalid")
    if source.get("archive_policy") not in ARCHIVE_POLICIES:
        raise ConfigFault("archive_policy_invalid")

    risk = source.get("risk_policy")
    if not isinstance(risk, dict) or set(risk) != RISK_KEYS:
        raise ConfigFault("risk_policy_invalid")
    if any(type(risk[key]) is not bool or risk[key] for key in RISK_KEYS):
        raise ConfigFault("risk_policy_not_default_deny")
    _validate_optional_metadata(source)

    if not check_paths:
        return None, len(includes)

    raw_root = Path(root_value).expanduser()
    try:
        lexical_root = raw_root.absolute()
    except OSError as exc:
        raise ConfigFault("source_root_unresolved") from exc
    if _inside(lexical_root, repo) or _inside(repo, lexical_root):
        raise ConfigFault("source_repository_overlap")
    if _path_chain_has_link(raw_root):
        raise ConfigFault("source_root_link_boundary")
    try:
        root = raw_root.resolve(strict=False)
    except OSError as exc:
        raise ConfigFault("source_root_unresolved") from exc
    if _is_broad_root(root):
        raise ConfigFault("source_root_too_broad")
    if _inside(root, repo) or _inside(repo, root):
        raise ConfigFault("source_repository_overlap")
    if not root.exists():
        raise ConfigFault("source_unreachable", STATE_UNREACHABLE)
    if not root.is_dir() or not os.access(root, os.R_OK | os.X_OK):
        raise ConfigFault("source_unreadable", STATE_UNREACHABLE)
    for rule in includes:
        _check_rule_boundary(root, rule)
    return root, len(includes)


def _materialize_validated_source(
    source: Mapping[str, object], root: Path
) -> ValidatedSource:
    """Build the private in-process capability after all validation passed."""
    return ValidatedSource(
        source_id=str(source["id"]),
        root=root,
        include=tuple(str(item) for item in source["include"]),
        exclude=tuple(str(item) for item in source["exclude"]),
        allowed_extensions=tuple(
            str(item) for item in source["allowed_extensions"]
        ),
        subjects=tuple(str(item) for item in source["subjects"]),
        grades=tuple(int(item) for item in source.get("grades", [])),
        learner_groups=tuple(
            str(item) for item in source.get("learner_groups", [])
        ),
        document_types=tuple(
            str(item) for item in source.get("document_types", [])
        ),
        archive_policy=str(source["archive_policy"]),
    )


def _validate_top_level(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ConfigFault("configuration_not_object")
    if set(value) != TOP_LEVEL_KEYS:
        raise ConfigFault("configuration_fields_invalid")
    schema_version = value.get("schema_version")
    if (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, (int, float))
        or schema_version != 1
    ):
        raise ConfigFault("schema_version_unsupported")
    if type(value.get("enabled")) is not bool:
        raise ConfigFault("enabled_invalid")
    if value.get("usage_context") != "orientation-only":
        raise ConfigFault("usage_context_invalid")
    if value.get("state_directory") != STATE_DIRECTORY:
        raise ConfigFault("state_directory_invalid")
    if not isinstance(value.get("sources"), list):
        raise ConfigFault("sources_invalid")
    return value


def _state_boundary(repo: Path) -> None:
    local = repo / LOCAL_ZONE
    state = repo / STATE_DIRECTORY
    if local.exists() and _link(local):
        raise ConfigFault("local_zone_link_boundary")
    try:
        resolved_state = state.resolve(strict=False)
        resolved_local = local.resolve(strict=False)
    except OSError as exc:
        raise ConfigFault("state_boundary_unresolved") from exc
    if not _inside(resolved_state, resolved_local):
        raise ConfigFault("state_boundary_escape")


def load_validated_sources(
    repo_root: Path = ROOT,
    explicit_config: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> tuple[ValidationResult, tuple[ValidatedSource, ...]]:
    """Validate once and return capabilities only for an active source set.

    Disabled, missing, unreachable, or excluded configurations always return
    an empty source tuple. In particular, disabled source roots are never
    resolved, traversed, or tested for existence.
    """
    repo = repo_root.resolve()
    config, _origin = discover_config(repo, explicit_config, environ)
    if config is None:
        return (
            ValidationResult(STATE_NOT_CONFIGURED, "configuration_absent"),
            (),
        )
    if not config.exists():
        return (
            ValidationResult(STATE_UNREACHABLE, "configuration_unreachable"),
            (),
        )

    try:
        _state_boundary(repo)
        if _link(config):
            raise ConfigFault("configuration_link_boundary")
        resolved_config = config.resolve(strict=False)
        if _inside(resolved_config, repo) and not _repo_local_config_is_safe(
            repo, resolved_config
        ):
            raise ConfigFault("repository_local_configuration_unsafe")
        value = _validate_top_level(_read_json(resolved_config))

        sources = value["sources"]
        assert isinstance(sources, list)
        enabled = bool(value["enabled"])
        if enabled and not sources:
            raise ConfigFault("active_sources_empty")

        identifiers: set[str] = set()
        roots: set[Path] = set()
        validated_sources: list[ValidatedSource] = []
        allowlist_count = 0
        for source in sources:
            root, count = _validate_source(source, repo, check_paths=enabled)
            assert isinstance(source, dict)
            identifier = source["id"]
            assert isinstance(identifier, str)
            if identifier in identifiers:
                raise ConfigFault("source_id_duplicate")
            identifiers.add(identifier)
            allowlist_count += count
            if root is not None:
                if root in roots:
                    raise ConfigFault("source_root_duplicate")
                roots.add(root)
                validated_sources.append(
                    _materialize_validated_source(source, root)
                )

        if not enabled:
            return (
                ValidationResult(
                    STATE_NOT_CONFIGURED,
                    "configuration_disabled",
                    len(sources),
                    allowlist_count,
                ),
                (),
            )
        return (
            ValidationResult(
                STATE_AVAILABLE,
                "configuration_valid",
                len(sources),
                allowlist_count,
            ),
            tuple(validated_sources),
        )
    except ConfigFault as exc:
        return ValidationResult(exc.state, exc.code), ()


def validate_configuration(
    repo_root: Path = ROOT,
    explicit_config: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> ValidationResult:
    result, _sources = load_validated_sources(
        repo_root,
        explicit_config=explicit_config,
        environ=environ,
    )
    return result


def private_config_needles(
    repo_root: Path = ROOT,
    explicit_config: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> list[str]:
    """Return private root strings internally for the leak gate, without output."""
    repo = repo_root.resolve()
    try:
        _state_boundary(repo)
        config, _origin = discover_config(repo, explicit_config, environ)
    except (ConfigFault, OSError):
        return []
    if config is None or not config.exists() or _link(config):
        return []
    try:
        lexical_config = config.absolute()
        if _inside(lexical_config, repo):
            if not _repo_local_config_is_safe(repo, lexical_config):
                return []
        elif _path_chain_has_link(config):
            return []
        value = _read_json(config.resolve(strict=False))
    except (ConfigFault, OSError):
        return []
    if not isinstance(value, dict) or not isinstance(value.get("sources"), list):
        return []
    roots = []
    for source in value["sources"]:
        if not isinstance(source, dict):
            continue
        root = source.get("root")
        if isinstance(root, str) and len(root.strip()) >= 4:
            roots.append(root.strip())
        for key in ("include", "exclude"):
            rules = source.get(key)
            if not isinstance(rules, list):
                continue
            roots.extend(
                rule.strip()
                for rule in rules
                if isinstance(rule, str) and len(rule.strip()) >= 4
            )
    return roots


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, _message):
        raise ConfigFault("arguments_invalid")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args(argv)


def _print_result(result: ValidationResult, as_json: bool) -> None:
    payload = result.as_dict()
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    print(
        "STATE "
        f"{result.availability_state}; "
        f"reason={result.reason_code}; "
        f"sources={result.source_count}; "
        f"allowlist_entries={result.allowlist_entry_count}; "
        "candidate_selection=implemented; "
        "tex_parser=implemented; "
        "local_metadata_schema=implemented; "
        "include_resolution=implemented; "
        "local_index=implemented; "
        "local_search=implemented; "
        "federated_search=implemented; "
        "controlled_feature_extraction=implemented; "
        "orientation_guidance=implemented; "
        "canonical_skill_routing=implemented"
    )


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        result = validate_configuration(
            args.repo_root,
            explicit_config=args.config,
            environ=os.environ,
        )
    except ConfigFault as fault:
        print(
            f"ERROR local_orientation_config {fault.code}",
            file=sys.stderr,
        )
        return 2
    except Exception:
        payload = {
            "availability_state": STATE_EXCLUDED,
            "reason_code": "configuration_operational_error",
        }
        if args.as_json:
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        else:
            print(
                "ERROR local_orientation_config configuration_operational_error",
                file=sys.stderr,
            )
        return 2
    _print_result(result, args.as_json)
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
