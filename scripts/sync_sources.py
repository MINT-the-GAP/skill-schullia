#!/usr/bin/env python3
"""Synchronize GitHub sources into a local, versioned SchulLia corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CONFIG = SKILL_DIR / "references" / "sources.json"
DEFAULT_CORPUS = SKILL_DIR / "corpus"
USER_AGENT = "schullia-knowledge/0.1"
API_VERSION = "2022-11-28"
SYNC_VERSION = "1"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

KNOWN_TEXT_EXTENSIONS = {
    ".asm", ".bash", ".bat", ".bib", ".c", ".cfg", ".cjs", ".cmd",
    ".conf", ".cpp", ".cs", ".css", ".csv", ".d.ts", ".gradle", ".h",
    ".hpp", ".htm", ".html", ".ini", ".ino", ".java", ".js", ".json",
    ".jsonl", ".jsx", ".kt", ".ld", ".less", ".lua", ".m", ".markdown",
    ".md", ".mjs", ".mm", ".php", ".properties", ".ps1", ".py", ".r",
    ".rb", ".rs", ".s", ".sass", ".scss", ".sh", ".sql", ".svg", ".tex",
    ".toml", ".ts", ".tsv", ".tsx", ".txt", ".vue", ".xml", ".yaml",
    ".yml",
}

KNOWN_BINARY_EXTENSIONS = {
    ".7z", ".a", ".avi", ".bin", ".bmp", ".class", ".dll", ".doc",
    ".docx", ".dylib", ".eot", ".exe", ".flac", ".gif", ".gz", ".ico",
    ".jar", ".jpeg", ".jpg", ".m4a", ".mkv", ".mov", ".mp3", ".mp4",
    ".o", ".obj", ".odg", ".odp", ".ods", ".odt", ".ogg", ".otf",
    ".pdf", ".png", ".ppt", ".pptx", ".so", ".tar", ".tif", ".tiff",
    ".ttf", ".wav", ".wasm", ".webm", ".webp", ".woff", ".woff2", ".xls",
    ".xlsx", ".xz", ".zip",
}

WINDOWS_INVALID = re.compile(r'[<>:"|?*]')
WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class SyncError(RuntimeError):
    """A source could not be synchronized safely."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, path)


def atomic_write_json(path: Path, value: Any) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    atomic_write_bytes(path, (payload + "\n").encode("utf-8"))


def atomic_write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    lines = (
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in records
    )
    atomic_write_bytes(path, ("\n".join(lines) + "\n").encode("utf-8"))


def source_slug(source_id: str) -> str:
    readable = re.sub(r"[^a-z0-9]+", "-", source_id.casefold()).strip("-")[:72]
    digest = hashlib.sha256(source_id.encode("utf-8")).hexdigest()[:10]
    return f"{readable}-{digest}"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def is_probably_text(path: str, data: bytes) -> bool:
    suffixes = PurePosixPath(path).suffixes
    compound_suffix = "".join(suffixes[-2:]).casefold() if len(suffixes) >= 2 else ""
    suffix = PurePosixPath(path).suffix.casefold()
    if compound_suffix in KNOWN_TEXT_EXTENSIONS or suffix in KNOWN_TEXT_EXTENSIONS:
        return True
    if suffix in KNOWN_BINARY_EXTENSIONS:
        return False
    if b"\x00" in data[:8192]:
        return data.startswith((b"\xff\xfe", b"\xfe\xff"))
    sample = data[:65536]
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            sample.decode(encoding)
            return True
        except UnicodeDecodeError:
            continue
    return False


def line_count(data: bytes) -> int | None:
    if not data:
        return 0
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            text = data.decode(encoding)
            return len(text.splitlines())
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None


def safe_windows_relative_path(path: PurePosixPath) -> bool:
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        return False
    for part in path.parts:
        stem = part.split(".", 1)[0].upper()
        if WINDOWS_INVALID.search(part) or part.endswith((" ", ".")) or stem in WINDOWS_RESERVED:
            return False
    return True


def quote_path(path: str) -> str:
    return "/".join(urllib.parse.quote(part, safe="") for part in PurePosixPath(path).parts)


class GitHubClient:
    def __init__(self, token: str | None, timeout: float):
        self.token = token
        self.timeout = timeout
        self.rate_limit_remaining: str | None = None
        self.rate_limit_reset: str | None = None
        self.api_rate_limited = False

    def _headers(self, *, api: bool) -> dict[str, str]:
        headers = {"User-Agent": USER_AGENT}
        if api:
            headers.update({
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": API_VERSION,
            })
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request(self, url: str, *, api: bool = False) -> urllib.response.addinfourl:
        request = urllib.request.Request(url, headers=self._headers(api=api))
        try:
            response = urllib.request.urlopen(request, timeout=self.timeout)
        except urllib.error.HTTPError as exc:
            detail = exc.read(2048).decode("utf-8", errors="replace")
            reset = exc.headers.get("X-RateLimit-Reset")
            if api:
                self.rate_limit_remaining = exc.headers.get("X-RateLimit-Remaining")
                self.rate_limit_reset = reset
                if exc.code == 403 and (
                    self.rate_limit_remaining == "0" or "rate limit" in detail.casefold()
                ):
                    self.api_rate_limited = True
            suffix = f"; rate-limit reset={reset}" if reset else ""
            raise SyncError(f"HTTP {exc.code} for {url}{suffix}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise SyncError(f"Network error for {url}: {exc.reason}") from exc
        if api:
            self.rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
            self.rate_limit_reset = response.headers.get("X-RateLimit-Reset")
        return response

    def api_json(self, endpoint: str) -> Any:
        if self.api_rate_limited:
            raise SyncError(
                f"GitHub REST API rate limit is exhausted; reset={self.rate_limit_reset}"
            )
        url = endpoint if endpoint.startswith("https://") else f"https://api.github.com{endpoint}"
        with self.request(url, api=True) as response:
            return json.loads(response.read().decode("utf-8"))

    def list_org_repositories(self, organization: str) -> list[dict[str, Any]]:
        repositories: list[dict[str, Any]] = []
        page = 1
        while True:
            encoded = urllib.parse.quote(organization, safe="")
            batch = self.api_json(
                f"/orgs/{encoded}/repos?type=public&sort=full_name&per_page=100&page={page}"
            )
            if not isinstance(batch, list):
                raise SyncError(f"Unexpected repository response for organization {organization}")
            repositories.extend(batch)
            if len(batch) < 100:
                return repositories
            page += 1

    def repository_metadata(self, owner: str, repo: str) -> dict[str, Any]:
        encoded_owner = urllib.parse.quote(owner, safe="")
        encoded_repo = urllib.parse.quote(repo, safe="")
        try:
            return self.api_json(f"/repos/{encoded_owner}/{encoded_repo}")
        except SyncError:
            return {
                "_metadata_fallback": True,
                "owner": {"login": owner},
                "name": repo,
                "html_url": f"https://github.com/{owner}/{repo}",
                "pushed_at": None,
                "license": None,
                "archived": False,
                "fork": False,
                "description": None,
            }

    def resolve_revision(self, owner: str, repo: str, ref: str) -> str:
        encoded_owner = urllib.parse.quote(owner, safe="")
        encoded_repo = urllib.parse.quote(repo, safe="")
        encoded_ref = urllib.parse.quote(ref, safe="")
        try:
            commit = self.api_json(
                f"/repos/{encoded_owner}/{encoded_repo}/commits/{encoded_ref}"
            )
            return commit["sha"]
        except (KeyError, SyncError):
            return self.git_revision(owner, repo, ref)

    def git_revision(self, owner: str, repo: str, ref: str) -> str:
        url = f"https://github.com/{owner}/{repo}.git"
        environment = os.environ.copy()
        environment["GIT_TERMINAL_PROMPT"] = "0"
        try:
            result = subprocess.run(
                ["git", "ls-remote", url, f"refs/heads/{ref}"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
                env=environment,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SyncError(f"git ls-remote failed for {owner}/{repo}@{ref}: {exc}") from exc
        if result.returncode != 0:
            raise SyncError(
                f"git ls-remote failed for {owner}/{repo}@{ref}: {result.stderr.strip()}"
            )
        first = next((line for line in result.stdout.splitlines() if line.strip()), "")
        revision = first.split("\t", 1)[0].strip()
        if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
            raise SyncError(f"Branch not found for {owner}/{repo}@{ref}")
        return revision.casefold()

    def download(self, url: str, destination: Path, max_bytes: int) -> int:
        destination.parent.mkdir(parents=True, exist_ok=True)
        total = 0
        with self.request(url, api=False) as response, destination.open("wb") as handle:
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > max_bytes:
                raise SyncError(f"Download exceeds configured limit ({declared} > {max_bytes}): {url}")
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise SyncError(f"Download exceeded configured limit ({max_bytes} bytes): {url}")
                handle.write(chunk)
        return total

    def read_bytes(self, url: str, max_bytes: int) -> bytes:
        with self.request(url, api=False) as response:
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > max_bytes:
                raise SyncError(f"File exceeds configured limit ({declared} > {max_bytes}): {url}")
            data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise SyncError(f"File exceeded configured limit ({max_bytes} bytes): {url}")
        return data


def source_paths(corpus: Path, source_id: str) -> tuple[Path, Path]:
    root = corpus / "sources"
    return root / source_slug(source_id), corpus / ".staging" / source_slug(source_id)


def previous_source(corpus: Path, source_id: str) -> dict[str, Any] | None:
    final_dir, _ = source_paths(corpus, source_id)
    return load_json(final_dir / "source.json")


def refresh_cached_repository_metadata(
    corpus: Path,
    source_id: str,
    previous: dict[str, Any],
    repository: dict[str, Any],
) -> dict[str, Any]:
    if repository.get("_metadata_fallback"):
        return previous
    updated = dict(previous)
    license_info = repository.get("license") or {}
    values = {
        "pushed_at": repository.get("pushed_at"),
        "license_spdx": license_info.get("spdx_id"),
        "license_name": license_info.get("name"),
        "archived": bool(repository.get("archived")),
        "fork": bool(repository.get("fork")),
        "description": repository.get("description"),
    }
    for key, value in values.items():
        if value is not None:
            updated[key] = value
    if updated != previous:
        final_dir, _ = source_paths(corpus, source_id)
        atomic_write_json(final_dir / "source.json", updated)
    return updated


def prepare_stage(corpus: Path, source_id: str) -> Path:
    _, stage_dir = source_paths(corpus, source_id)
    staging_root = (corpus / ".staging").resolve()
    resolved = stage_dir.resolve()
    if staging_root not in resolved.parents:
        raise SyncError(f"Unsafe staging path: {resolved}")
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    (stage_dir / "files").mkdir(parents=True, exist_ok=True)
    return stage_dir


def commit_stage(corpus: Path, source_id: str, stage_dir: Path) -> None:
    final_dir, expected_stage = source_paths(corpus, source_id)
    sources_root = (corpus / "sources").resolve()
    if stage_dir.resolve() != expected_stage.resolve() or sources_root not in final_dir.resolve().parents:
        raise SyncError("Refusing to replace an unexpected source directory")
    final_dir.parent.mkdir(parents=True, exist_ok=True)
    if final_dir.exists():
        shutil.rmtree(final_dir)
    os.replace(stage_dir, final_dir)


def write_staged_source(
    stage_dir: Path,
    source: dict[str, Any],
    records: list[dict[str, Any]],
) -> None:
    source["file_count"] = len(records)
    source["text_file_count"] = sum(1 for record in records if record.get("is_text"))
    source["binary_file_count"] = sum(1 for record in records if not record.get("is_text"))
    atomic_write_json(stage_dir / "source.json", source)
    atomic_write_jsonl(stage_dir / "manifest.jsonl", sorted(records, key=lambda item: item["path"]))


def archive_entry_kind(info: zipfile.ZipInfo) -> str:
    mode = info.external_attr >> 16
    if stat.S_ISLNK(mode):
        return "symlink"
    return "file"


def extract_repository_archive(
    archive_path: Path,
    stage_dir: Path,
    source: dict[str, Any],
    limits: dict[str, int],
    store_binary: bool,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    total_extracted = 0
    with zipfile.ZipFile(archive_path) as archive:
        entries = archive.infolist()
        if len(entries) > int(limits["max_entries"]):
            raise SyncError(f"Archive contains too many entries: {len(entries)}")
        for info in entries:
            name = info.filename.replace("\\", "/")
            archive_path_parts = PurePosixPath(name)
            if archive_path_parts.is_absolute() or ".." in archive_path_parts.parts:
                raise SyncError(f"Unsafe path in archive: {name}")
            if info.is_dir() or len(archive_path_parts.parts) < 2:
                continue
            relative = PurePosixPath(*archive_path_parts.parts[1:])
            if not safe_windows_relative_path(relative):
                records.append({
                    "source_id": source["source_id"],
                    "collection": source["collection"],
                    "path": relative.as_posix(),
                    "entry_kind": archive_entry_kind(info),
                    "size_bytes": int(info.file_size),
                    "is_text": False,
                    "stored": False,
                    "content_state": "unsupported_windows_path",
                    "revision_sha": source["revision_sha"],
                })
                continue
            total_extracted += int(info.file_size)
            if total_extracted > int(limits["max_extracted_bytes"]):
                raise SyncError(
                    f"Archive expands beyond configured limit ({limits['max_extracted_bytes']} bytes)"
                )
            data = archive.read(info)
            is_text = is_probably_text(relative.as_posix(), data)
            should_store = store_binary or is_text
            local_relpath = None
            if should_store:
                local_path = stage_dir / "files" / Path(*relative.parts)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(data)
                local_relpath = (Path("sources") / source_slug(source["source_id"]) / "files" / Path(*relative.parts)).as_posix()
            encoded_path = quote_path(relative.as_posix())
            record = {
                "source_id": source["source_id"],
                "collection": source["collection"],
                "path": relative.as_posix(),
                "entry_kind": archive_entry_kind(info),
                "size_bytes": len(data),
                "git_blob_sha1": git_blob_sha1(data),
                "content_sha256": hashlib.sha256(data).hexdigest(),
                "is_text": is_text,
                "line_count": line_count(data) if is_text else None,
                "stored": should_store,
                "content_state": "stored" if should_store else "binary_metadata_only",
                "local_relpath": local_relpath,
                "lfs_pointer": data.startswith(b"version https://git-lfs.github.com/spec/v1"),
                "revision_sha": source["revision_sha"],
                "raw_url": (
                    f"https://raw.githubusercontent.com/{source['owner']}/{source['repo']}/"
                    f"{source['revision_sha']}/{encoded_path}"
                ),
                "web_url": (
                    f"https://github.com/{source['owner']}/{source['repo']}/blob/"
                    f"{source['revision_sha']}/{encoded_path}"
                ),
            }
            records.append(record)
    return records


def sync_repository(
    client: GitHubClient,
    corpus: Path,
    repo: dict[str, Any],
    collection: str,
    limits: dict[str, int],
    force: bool,
    store_binary: bool,
) -> tuple[str, dict[str, Any]]:
    owner = repo["owner"]["login"]
    name = repo["name"]
    source_id = f"ghrepo:{owner.casefold()}/{name.casefold()}"
    previous = previous_source(corpus, source_id)
    if (
        not force
        and previous
        and repo.get("pushed_at") is not None
        and previous.get("pushed_at") == repo.get("pushed_at")
        and previous.get("default_branch") == repo.get("default_branch")
    ):
        return "skipped", previous

    encoded_owner = urllib.parse.quote(owner, safe="")
    encoded_repo = urllib.parse.quote(name, safe="")
    revision = client.resolve_revision(owner, name, repo["default_branch"])
    if not force and previous and previous.get("revision_sha") == revision:
        previous = refresh_cached_repository_metadata(
            corpus, source_id, previous, repo
        )
        return "skipped", previous

    stage_dir = prepare_stage(corpus, source_id)
    archive_path = stage_dir / "source.zip"
    archive_url = f"https://codeload.github.com/{encoded_owner}/{encoded_repo}/zip/{revision}"
    try:
        client.download(archive_url, archive_path, int(limits["max_archive_bytes"]))
        license_info = repo.get("license") or {}
        source = {
            "schema_version": 1,
            "sync_version": SYNC_VERSION,
            "source_id": source_id,
            "source_kind": "github_repo",
            "collection": collection,
            "usage_context": "task-content",
            "owner": owner,
            "repo": name,
            "configured_ref": repo["default_branch"],
            "default_branch": repo["default_branch"],
            "revision_sha": revision,
            "pushed_at": repo.get("pushed_at"),
            "synced_at": utc_now(),
            "web_url": repo.get("html_url"),
            "archive_url": archive_url,
            "license_spdx": license_info.get("spdx_id"),
            "license_name": license_info.get("name"),
            "archived": bool(repo.get("archived")),
            "fork": bool(repo.get("fork")),
            "description": repo.get("description"),
        }
        records = extract_repository_archive(
            archive_path, stage_dir, source, limits, store_binary=store_binary
        )
        archive_path.unlink(missing_ok=True)
        write_staged_source(stage_dir, source, records)
        commit_stage(corpus, source_id, stage_dir)
        return "changed", source
    except Exception:
        if stage_dir.exists():
            shutil.rmtree(stage_dir)
        raise


def sync_fixed_file(
    client: GitHubClient,
    corpus: Path,
    definition: dict[str, Any],
    limits: dict[str, int],
    force: bool,
) -> tuple[str, dict[str, Any]]:
    source_id = definition["id"]
    owner = definition["owner"]
    repo_name = definition["repo"]
    configured_ref = definition["ref"]
    path = PurePosixPath(definition["path"])
    if not safe_windows_relative_path(path):
        raise SyncError(f"Unsafe configured file path: {path}")
    encoded_owner = urllib.parse.quote(owner, safe="")
    encoded_repo = urllib.parse.quote(repo_name, safe="")
    repo = client.repository_metadata(owner, repo_name)
    previous = previous_source(corpus, source_id)
    if (
        not force
        and previous
        and repo.get("pushed_at") is not None
        and previous.get("pushed_at") == repo.get("pushed_at")
        and previous.get("configured_ref") == configured_ref
    ):
        return "skipped", previous

    revision = client.resolve_revision(owner, repo_name, configured_ref)
    if not force and previous and previous.get("revision_sha") == revision:
        previous = refresh_cached_repository_metadata(
            corpus, source_id, previous, repo
        )
        return "skipped", previous

    pinned_url = (
        f"https://raw.githubusercontent.com/{encoded_owner}/{encoded_repo}/{revision}/"
        f"{quote_path(path.as_posix())}"
    )
    data = client.read_bytes(pinned_url, int(limits["max_index_file_bytes"]))
    if not is_probably_text(path.as_posix(), data):
        raise SyncError(f"Configured template reference is not text: {source_id}")

    stage_dir = prepare_stage(corpus, source_id)
    try:
        local_path = stage_dir / "files" / Path(*path.parts)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
        license_info = repo.get("license") or {}
        source = {
            "schema_version": 1,
            "sync_version": SYNC_VERSION,
            "source_id": source_id,
            "source_kind": "github_file",
            "collection": definition.get("collection", "template-reference"),
            "usage_context": "documentation",
            "owner": repo["owner"]["login"],
            "repo": repo["name"],
            "configured_ref": configured_ref,
            "path": path.as_posix(),
            "revision_sha": revision,
            "pushed_at": repo.get("pushed_at"),
            "synced_at": utc_now(),
            "web_url": f"{repo['html_url']}/blob/{revision}/{quote_path(path.as_posix())}",
            "requested_url": definition.get("requested_url"),
            "raw_url": pinned_url,
            "license_spdx": license_info.get("spdx_id"),
            "license_name": license_info.get("name"),
            "archived": bool(repo.get("archived")),
            "fork": bool(repo.get("fork")),
            "description": repo.get("description"),
        }
        local_relpath = (
            Path("sources") / source_slug(source_id) / "files" / Path(*path.parts)
        ).as_posix()
        record = {
            "source_id": source_id,
            "collection": source["collection"],
            "path": path.as_posix(),
            "entry_kind": "file",
            "size_bytes": len(data),
            "git_blob_sha1": git_blob_sha1(data),
            "content_sha256": hashlib.sha256(data).hexdigest(),
            "is_text": True,
            "line_count": line_count(data),
            "stored": True,
            "content_state": "stored",
            "local_relpath": local_relpath,
            "lfs_pointer": False,
            "revision_sha": revision,
            "raw_url": pinned_url,
            "web_url": source["web_url"],
        }
        write_staged_source(stage_dir, source, [record])
        commit_stage(corpus, source_id, stage_dir)
        return "changed", source
    except Exception:
        if stage_dir.exists():
            shutil.rmtree(stage_dir)
        raise


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def rebuild_combined_files(corpus: Path, states: dict[str, dict[str, Any]]) -> None:
    sources: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    source_root = corpus / "sources"
    if source_root.exists():
        for directory in sorted(path for path in source_root.iterdir() if path.is_dir()):
            source = load_json(directory / "source.json")
            if not source:
                continue
            state = states.get(source["source_id"], {})
            source["state"] = state.get("state", "current")
            source["last_attempt_at"] = state.get("last_attempt_at")
            source["last_error"] = state.get("error")
            sources.append(source)
            files.extend(read_jsonl(directory / "manifest.jsonl"))
    atomic_write_json(corpus / "sources.json", sorted(sources, key=lambda item: item["source_id"]))
    atomic_write_jsonl(
        corpus / "files.jsonl",
        sorted(files, key=lambda item: (item["source_id"], item["path"])),
    )


def config_sha256(config: dict[str, Any]) -> str:
    payload = json.dumps(
        config, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def last_run_is_fresh(
    corpus: Path, max_age_hours: float, expected_config_sha256: str
) -> bool:
    if max_age_hours <= 0:
        return False
    state_document = load_json(corpus / "state.json", {})
    if state_document.get("config_sha256") != expected_config_sha256:
        return False
    report = load_json(corpus / "sync-report.json", {})
    stamp = report.get("finished_at")
    if not stamp or report.get("failures"):
        return False
    try:
        finished = datetime.fromisoformat(stamp)
    except ValueError:
        return False
    return datetime.now(timezone.utc) - finished < timedelta(hours=max_age_hours)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--force", action="store_true", help="Refresh every configured source")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Only synchronize a source ID, repository name, or owner/repository pair",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument(
        "--metadata-only-binary",
        action="store_true",
        help="Inventory binary files without storing their bytes",
    )
    parser.add_argument(
        "--max-age-hours",
        type=float,
        default=0,
        help="Skip all network checks when the last complete sync is younger than this",
    )
    parser.add_argument(
        "--offline-rebuild",
        action="store_true",
        help="Rebuild combined manifests without contacting GitHub",
    )
    return parser.parse_args(argv)


def wanted(selection: list[str], source_id: str, owner: str, repo: str) -> bool:
    if not selection:
        return True
    candidates = {source_id.casefold(), repo.casefold(), f"{owner}/{repo}".casefold()}
    return any(item.casefold() in candidates for item in selection)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_json(args.config)
    if not config or config.get("schema_version") != 1:
        print(f"Invalid or unsupported source configuration: {args.config}", file=sys.stderr)
        return 1
    corpus = args.corpus.resolve()
    corpus.mkdir(parents=True, exist_ok=True)
    state_document = load_json(corpus / "state.json", {"schema_version": 1, "sources": {}})
    states: dict[str, dict[str, Any]] = state_document.setdefault("sources", {})
    current_config_sha256 = config_sha256(config)

    if args.offline_rebuild:
        rebuild_combined_files(corpus, states)
        print(f"Rebuilt combined manifests from {corpus}")
        return 0
    if last_run_is_fresh(corpus, args.max_age_hours, current_config_sha256):
        report = load_json(corpus / "sync-report.json", {})
        report["last_check_at"] = utc_now()
        report["changed"] = []
        report["skipped"] = ["freshness_window"]
        atomic_write_json(corpus / "sync-report.json", report)
        print(f"Corpus is within the requested freshness window: {corpus}")
        return 0

    token = os.environ.get(args.token_env) or os.environ.get("GH_TOKEN")
    client = GitHubClient(token=token, timeout=args.timeout)
    limits = config["limits"]
    report: dict[str, Any] = {
        "schema_version": 1,
        "sync_version": SYNC_VERSION,
        "started_at": utc_now(),
        "finished_at": None,
        "changed": [],
        "skipped": [],
        "retired": [],
        "warnings": [],
        "failures": [],
    }
    configured_ids: set[str] = set()
    fatal_discovery_error = False

    for organization in config.get("organizations", []):
        login = organization["login"]
        try:
            repositories = client.list_org_repositories(login)
        except Exception as exc:
            fallback = organization.get("fallback_repositories", [])
            if not fallback:
                fatal_discovery_error = True
                report["failures"].append({"source_id": f"org:{login}", "error": str(exc)})
                continue
            report["warnings"].append({
                "source_id": f"org:{login}",
                "warning": f"REST discovery failed; using configured fallback list: {exc}",
            })
            repositories = [
                {
                    "_metadata_fallback": True,
                    "owner": {"login": login},
                    "name": item["name"],
                    "default_branch": item["default_branch"],
                    "html_url": f"https://github.com/{login}/{item['name']}",
                    "pushed_at": None,
                    "license": None,
                    "archived": False,
                    "fork": False,
                    "description": None,
                }
                for item in fallback
            ]
        for repo in repositories:
            if repo.get("fork") and not organization.get("include_forks", True):
                continue
            if repo.get("archived") and not organization.get("include_archived", True):
                continue
            source_id = f"ghrepo:{repo['owner']['login'].casefold()}/{repo['name'].casefold()}"
            configured_ids.add(source_id)
            if not wanted(args.source, source_id, repo["owner"]["login"], repo["name"]):
                continue
            attempt = utc_now()
            try:
                status, _ = sync_repository(
                    client,
                    corpus,
                    repo,
                    organization.get("collection", login.casefold()),
                    limits,
                    args.force,
                    store_binary=not args.metadata_only_binary,
                )
                states[source_id] = {"state": "current", "last_attempt_at": attempt, "error": None}
                report[status].append(source_id)
                print(f"{status:7} {source_id}")
            except Exception as exc:
                cached = previous_source(corpus, source_id) is not None
                states[source_id] = {
                    "state": "stale" if cached else "unavailable",
                    "last_attempt_at": attempt,
                    "error": str(exc),
                }
                report["failures"].append({"source_id": source_id, "error": str(exc)})
                print(f"failed  {source_id}: {exc}", file=sys.stderr)

    for definition in config.get("files", []):
        source_id = definition["id"]
        configured_ids.add(source_id)
        if not wanted(args.source, source_id, definition["owner"], definition["repo"]):
            continue
        attempt = utc_now()
        try:
            status, _ = sync_fixed_file(
                client, corpus, definition, limits, force=args.force
            )
            states[source_id] = {"state": "current", "last_attempt_at": attempt, "error": None}
            report[status].append(source_id)
            print(f"{status:7} {source_id}")
        except Exception as exc:
            cached = previous_source(corpus, source_id) is not None
            states[source_id] = {
                "state": "stale" if cached else "unavailable",
                "last_attempt_at": attempt,
                "error": str(exc),
            }
            report["failures"].append({"source_id": source_id, "error": str(exc)})
            print(f"failed  {source_id}: {exc}", file=sys.stderr)

    if not args.source and not fatal_discovery_error:
        for source_id, state in list(states.items()):
            if source_id not in configured_ids and state.get("state") != "retired":
                states[source_id] = {
                    **state,
                    "state": "retired",
                    "last_attempt_at": utc_now(),
                    "error": "Source is no longer present in the configured discovery scope",
                }
                report["retired"].append(source_id)

    report["finished_at"] = utc_now()
    report["rate_limit_remaining"] = client.rate_limit_remaining
    report["rate_limit_reset"] = client.rate_limit_reset
    state_document["last_run_at"] = report["finished_at"]
    state_document["config_sha256"] = current_config_sha256
    atomic_write_json(corpus / "state.json", state_document)
    rebuild_combined_files(corpus, states)
    atomic_write_json(corpus / "sync-report.json", report)
    print(
        f"Sync complete: {len(report['changed'])} changed, {len(report['skipped'])} unchanged, "
        f"{len(report['failures'])} failed"
    )
    return 2 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
