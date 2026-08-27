#!/usr/bin/env python3
"""Validate the public Logos portfolio, evidence packet, and frozen design boundary.

Capability classification: ``portable_core``. This deterministic validator reads
only repository files and imports the doctrine-mesh static validator from the
same revision. It performs no network or model call and writes no files. A pass
proves only the schema, evidence-reference, privacy-pattern, navigation, diagram,
mesh-manifest, and frozen-specification contracts implemented here. It does not
prove semantic or theological correctness, runtime readiness, source authority,
publication authority, or complete security coverage.

Unreadable or malformed inputs fail closed. Material changes to the portfolio,
evidence schema, doctrine-mesh freeze, authority rules, or validation runtime
require a fresh run and review. Rollback consists of removing this command from
the validation contract together with the public packet; rollback cannot erase a
release already fetched by another party.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath, PureWindowsPath
from types import ModuleType
from typing import Any, Iterable

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = ROOT / "docs/portfolio/logos-trust-layer"
MANIFEST_PATH = PACKET_ROOT / "project-evidence.yaml"
SCHEMA_PATH = PACKET_ROOT / "project-evidence.schema.json"
PORTFOLIO_PATH = ROOT / "PORTFOLIO.md"
DOCTRINE_ROOT = (
    ROOT
    / "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2"
)
DOCTRINE_VALIDATOR_PATH = DOCTRINE_ROOT / "checks/validate_doctrine_mesh.py"
ARTIFACT_CLASS = "portable_core"

EXPECTED_REPOSITORIES = {
    "logos-governance-architecture",
    "logos-scripture-graph",
    "logos-boundary-literature",
    "logos-doctrine-genealogy",
}
REQUIRED_INTERROGATION_ROUTE_TOKENS = {
    "governance/LOGOS_REPO_REGISTRY.yaml",
    "LOGOS_FAMILY_MAP.md",
    "logos-chunking-harness",
    "planned, not created",
    "noesis-atlas",
    "external advisory",
    "AI_FRONT_DOOR.md",
    "README.md",
    "snapshot_commit",
    "project-evidence.yaml",
}
EXPECTED_NAVIGATION_FILES = (
    "README.md",
    "AI_FRONT_DOOR.md",
    "AI_TABLE_OF_CONTENTS.md",
    "AI_WORK_START_HERE.md",
)
EXPECTED_PUBLIC_FILES = (
    "PORTFOLIO.md",
    "docs/portfolio/logos-trust-layer/README.md",
    "docs/portfolio/logos-trust-layer/AI-INTERROGATION-PROMPT.md",
    "docs/portfolio/logos-trust-layer/project-evidence.schema.json",
    "docs/portfolio/logos-trust-layer/project-evidence.yaml",
    "docs/portfolio/logos-trust-layer/agent-mesh-manifest.json",
    "docs/portfolio/logos-trust-layer/validation-receipt.json",
    "scripts/validate_portfolio_front_door.py",
    "tests/test_portfolio_front_door.py",
)
REQUIRED_BOUNDARY_TEXT = (
    "validated design, not a running system",
    "not a completed doctrine corpus",
    "not qualified theological authority",
)
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".txt"}
PORTFOLIO_RECEIPT_RELATIVE = Path(
    "docs/portfolio/logos-trust-layer/validation-receipt.json"
)

CHAT_LOCAL_LOCATOR = re.compile(r"turn[0-9]+(?:search|fetch|view)[0-9]+", re.I)
WINDOWS_PRIVATE_PATH = re.compile(
    r"(?i)(?:[a-z]:[\\/](?:users|wt|tmp|git)(?:[\\/]|$)|"
    + "c:"
    + r"/users/)"
)
FILE_URI = re.compile("file" + "://", re.I)
PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
GITHUB_TOKEN = re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")
AWS_ACCESS_KEY = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
GENERIC_SECRET = re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")
SENSITIVE_RULES = (
    ("windows_private_path", WINDOWS_PRIVATE_PATH),
    ("file_uri", FILE_URI),
    ("chat_local_locator", CHAT_LOCAL_LOCATOR),
    ("private_key_marker", PRIVATE_KEY),
    ("github_token_shape", GITHUB_TOKEN),
    ("aws_access_key_shape", AWS_ACCESS_KEY),
    ("generic_secret_shape", GENERIC_SECRET),
)


class PortfolioValidationError(RuntimeError):
    """Raised when a required portfolio input cannot be validated safely."""


@dataclass(frozen=True, order=True)
class Finding:
    rule: str
    path: str
    detail: str

    def render(self) -> str:
        return f"{self.rule}: {self.path}: {self.detail}"


@dataclass(frozen=True, order=True)
class GitDeltaEntry:
    status: str
    path: str


@dataclass(frozen=True)
class ValidationResult:
    findings: tuple[Finding, ...]
    metrics: dict[str, int]

    @property
    def passed(self) -> bool:
        return not self.findings


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PortfolioValidationError(f"cannot load JSON {path}: {exc}") from exc


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise PortfolioValidationError(f"cannot load YAML {path}: {exc}") from exc


def _canonical_digest(value: dict[str, Any], omitted: Iterable[str] = ()) -> str:
    payload = {key: item for key, item in value.items() if key not in set(omitted)}
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _canonical_content_bytes(raw: bytes) -> bytes:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _git_changed_paths(root: Path, base_commit: str, head_commit: str) -> list[str]:
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-only", f"{base_commit}..{head_commit}", "--"],
            cwd=root,
            text=True,
            stderr=subprocess.PIPE,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise PortfolioValidationError(
            f"cannot enumerate release scope {base_commit}..{head_commit}: {exc}"
        ) from exc
    return sorted({path.replace("\\", "/") for path in output.splitlines() if path.strip()})


def _git_delta_entries(
    root: Path, base_commit: str, head_commit: str
) -> list[GitDeltaEntry]:
    """Return a NUL-safe, non-lossy additive/modifying release delta."""

    for label, commit in (("base", base_commit), ("head", head_commit)):
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise PortfolioValidationError(f"release {label} is not an exact commit")
        if _git_revision(root, commit) != commit:
            raise PortfolioValidationError(
                f"release {label} does not resolve to its exact commit"
            )
    try:
        completed = subprocess.run(
            [
                "git",
                "diff",
                "--name-status",
                "-z",
                "--no-renames",
                f"{base_commit}..{head_commit}",
                "--",
            ],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise PortfolioValidationError(f"cannot enumerate exact release delta: {exc}") from exc
    if completed.returncode != 0:
        raise PortfolioValidationError("Git could not enumerate the exact release delta")
    fields = completed.stdout.split(b"\0")
    if not fields or fields[-1] != b"":
        raise PortfolioValidationError("release delta is not NUL terminated")
    fields.pop()
    if len(fields) % 2:
        raise PortfolioValidationError("release delta has an incomplete status/path record")

    entries: list[GitDeltaEntry] = []
    seen: set[str] = set()
    for index in range(0, len(fields), 2):
        try:
            status = fields[index].decode("ascii")
            path = fields[index + 1].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PortfolioValidationError(
                "release delta contains a non-UTF-8 status or path"
            ) from exc
        if status not in {"A", "M"}:
            raise PortfolioValidationError(
                f"release delta contains forbidden or unresolved status {status!r}"
            )
        normalized = _safe_repo_path(path).as_posix()
        if normalized != path:
            raise PortfolioValidationError(f"release path is not canonical: {path!r}")
        if path in seen:
            raise PortfolioValidationError(f"release delta repeats path {path!r}")
        seen.add(path)
        entries.append(GitDeltaEntry(status=status, path=path))
    return sorted(entries, key=lambda entry: entry.path)


@lru_cache(maxsize=512)
def _git_commit_exists_record(resolved_root: str, commit: str) -> bool:
    try:
        completed = subprocess.run(
            ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
            cwd=resolved_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise PortfolioValidationError(
            f"cannot verify immutable Git commit {commit}: {exc}"
        ) from exc
    return completed.returncode == 0


@lru_cache(maxsize=4096)
def _git_object_record(
    resolved_root: str, commit: str, path: str
) -> tuple[bool, bytes]:
    """Cache one immutable Git blob lookup without conflating absence and error."""

    if not _git_commit_exists_record(resolved_root, commit):
        raise PortfolioValidationError(f"immutable Git commit is unavailable: {commit}")
    try:
        completed = subprocess.run(
            ["git", "show", f"{commit}:{path}"],
            cwd=resolved_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise PortfolioValidationError(
            f"cannot execute Git object lookup {commit}:{path}: {exc}"
        ) from exc
    if completed.returncode == 0:
        return True, completed.stdout

    try:
        presence = subprocess.run(
            ["git", "ls-tree", "-z", "--full-tree", commit, "--", path],
            cwd=resolved_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise PortfolioValidationError(
            f"cannot distinguish missing Git path from read error: {exc}"
        ) from exc
    if presence.returncode != 0:
        raise PortfolioValidationError(
            f"cannot inspect immutable Git path {commit}:{path}"
        )
    if not presence.stdout:
        return False, b""
    raise PortfolioValidationError(f"cannot read existing immutable Git blob {commit}:{path}")


def _git_object_lookup(root: Path, commit: str, path: str) -> tuple[bool, bytes]:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise PortfolioValidationError(f"Git object lookup requires an exact commit: {commit}")
    normalized_path = path.replace("\\", "/")
    return _git_object_record(str(root.resolve()), commit, normalized_path)


def _git_object_bytes(root: Path, commit: str, path: str) -> bytes:
    exists, raw = _git_object_lookup(root, commit, path)
    if not exists:
        raise PortfolioValidationError(f"cannot read release object {commit}:{path}")
    return raw


def _git_object_bytes_if_present(root: Path, commit: str, path: str) -> bytes | None:
    """Read an immutable Git blob or return its cached exact-commit absence."""

    exists, raw = _git_object_lookup(root, commit, path)
    return raw if exists else None


def _git_parents(root: Path, commit: str) -> list[str]:
    try:
        line = subprocess.check_output(
            ["git", "rev-list", "--parents", "-n", "1", commit],
            cwd=root,
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise PortfolioValidationError(f"cannot read parents for {commit}: {exc}") from exc
    fields = line.split()
    if not fields or fields[0] != commit:
        raise PortfolioValidationError(f"unexpected parent record for {commit}")
    return fields[1:]


def _git_is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def _git_latest_path_commit(root: Path, head: str, path: str) -> str:
    try:
        commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%H", head, "--", path],
            cwd=root,
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise PortfolioValidationError(
            f"cannot locate the current receipt commit for {path}: {exc}"
        ) from exc
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise PortfolioValidationError(f"current receipt commit is unavailable for {path}")
    return commit


def _git_revision(root: Path, revision: str) -> str:
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "--verify", revision],
            cwd=root,
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise PortfolioValidationError(f"cannot resolve Git revision {revision}: {exc}") from exc
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise PortfolioValidationError(f"Git revision is not an exact commit: {revision}")
    return value


def _git_merge_base(root: Path, left: str, right: str) -> str:
    try:
        value = subprocess.check_output(
            ["git", "merge-base", left, right],
            cwd=root,
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise PortfolioValidationError(
            f"cannot resolve merge base for {left} and {right}: {exc}"
        ) from exc
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise PortfolioValidationError("Git merge base is not an exact commit")
    return value


def _git_tree_sha(root: Path, commit: str) -> str:
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "--verify", f"{commit}^{{tree}}"],
            cwd=root,
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise PortfolioValidationError(f"cannot resolve tree for {commit}: {exc}") from exc
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise PortfolioValidationError(f"Git tree is not exact for {commit}")
    return value


def _git_path_fingerprint(root: Path, commit: str, paths: Iterable[str]) -> str:
    ordered = sorted(paths)
    if len(ordered) != len(set(ordered)):
        raise PortfolioValidationError("cannot fingerprint duplicate release paths")
    rows: list[str] = []
    for path in ordered:
        normalized = _safe_repo_path(path).as_posix()
        if normalized != path:
            raise PortfolioValidationError(f"release path is not canonical: {path!r}")
        raw = _git_object_bytes(root, commit, path)
        digest = hashlib.sha256(_canonical_content_bytes(raw)).hexdigest()
        rows.append(f"{digest}\t{path}\n")
    aggregate = hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()
    return f"sha256:{aggregate}"


def _git_snapshot_fingerprint(
    root: Path,
    base_commit: str,
    content_head_commit: str,
    excluded_paths: Iterable[str] = (),
) -> tuple[list[str], str]:
    paths = _git_changed_paths(root, base_commit, content_head_commit)
    excluded = set(excluded_paths)
    fingerprint_paths = [path for path in paths if path not in excluded]
    rows: list[str] = []
    for path in fingerprint_paths:
        raw = _git_object_bytes(root, content_head_commit, path)
        digest = hashlib.sha256(_canonical_content_bytes(raw)).hexdigest()
        rows.append(f"{digest}\t{path}\n")
    aggregate = hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()
    return paths, f"sha256:{aggregate}"


def _historical_windows_index_digest(
    root: Path,
    commit: str,
    paths: Iterable[str],
    campaign_prefix: str,
) -> str:
    """Replay the preserved V1 Windows-path/index convention without promoting it."""

    normalized_prefix = campaign_prefix.rstrip("/") + "/"
    relative_paths: list[tuple[str, str]] = []
    for path in paths:
        if not path.startswith(normalized_prefix):
            raise PortfolioValidationError(
                f"historical V1 path is outside its campaign root: {path}"
            )
        relative_paths.append((path, path[len(normalized_prefix) :]))
    ordered = sorted(relative_paths, key=lambda row: PureWindowsPath(row[1]))
    rows = [
        {
            "path": relative,
            "sha256": hashlib.sha256(_git_object_bytes(root, commit, path)).hexdigest(),
        }
        for path, relative in ordered
    ]
    encoded = json.dumps(
        rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _safe_repo_path(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise PortfolioValidationError("evidence path is missing")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise PortfolioValidationError(f"unsafe repository path: {value!r}")
    if "\\" in value or any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise PortfolioValidationError(f"non-portable repository path: {value!r}")
    segments = value.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise PortfolioValidationError(f"unsafe repository path: {value!r}")
    invalid_windows_characters = set('<>:"|?*')
    reserved_windows_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{number}" for number in range(1, 10)),
        *(f"LPT{number}" for number in range(1, 10)),
    }
    for segment in segments:
        device_stem = segment.split(".", 1)[0].upper()
        if (
            segment.endswith((" ", "."))
            or any(character in invalid_windows_characters for character in segment)
            or device_stem in reserved_windows_names
        ):
            raise PortfolioValidationError(f"non-portable repository path: {value!r}")
    return Path(*segments)


def _is_private_use(character: str) -> bool:
    code_point = ord(character)
    return (
        0xE000 <= code_point <= 0xF8FF
        or 0xF0000 <= code_point <= 0xFFFFD
        or 0x100000 <= code_point <= 0x10FFFD
    )


def scan_public_text(path: str, text: str) -> list[Finding]:
    """Return privacy/sensitive-pattern findings without echoing matched content."""

    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(_is_private_use(character) for character in line):
            findings.append(Finding("unicode_private_use", path, f"line {line_number}"))
        for rule, pattern in SENSITIVE_RULES:
            if pattern.search(line):
                findings.append(Finding(rule, path, f"line {line_number}"))
    return findings


def _sensitive_occurrences(text: str) -> Counter[tuple[str, str]]:
    occurrences: Counter[tuple[str, str]] = Counter()
    for line in text.splitlines():
        for character in line:
            if _is_private_use(character):
                occurrences[("unicode_private_use", character)] += 1
        for rule, pattern in SENSITIVE_RULES:
            for match in pattern.finditer(line):
                occurrences[(rule, match.group(0))] += 1
    return occurrences


def scan_candidate_added_text(path: str, current: str, baseline: str) -> list[Finding]:
    """Report only sensitive occurrences added above the exact base snapshot."""

    current_occurrences = _sensitive_occurrences(current)
    baseline_occurrences = _sensitive_occurrences(baseline)
    findings: list[Finding] = []
    for (rule, matched_value), count in sorted(current_occurrences.items()):
        added = count - baseline_occurrences.get((rule, matched_value), 0)
        if added > 0:
            findings.append(
                Finding(rule, path, f"{added} candidate-added occurrence(s)")
            )
    return findings


def _load_doctrine_validator(validator_path: Path) -> ModuleType:
    try:
        spec = importlib.util.spec_from_file_location(
            "logos_doctrine_mesh_static_validator", validator_path
        )
        if spec is None or spec.loader is None:
            raise PortfolioValidationError("cannot create doctrine validator module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except (OSError, ImportError, AttributeError) as exc:
        raise PortfolioValidationError(
            f"cannot import doctrine validator: {exc}"
        ) from exc


def _check_manifest_schema(
    manifest: dict[str, Any], schema: dict[str, Any], manifest_path: Path, root: Path
) -> list[Finding]:
    findings: list[Finding] = []
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.path)):
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        findings.append(Finding("manifest_schema", str(manifest_path.relative_to(root)), f"{location}: {error.message}"))
    return findings


def _check_receipt_schema(
    receipt: dict[str, Any], schema: dict[str, Any]
) -> list[Finding]:
    receipt_schema = {
        "$schema": schema.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        "$ref": "#/$defs/portfolioValidationReceiptV2",
        "$defs": schema.get("$defs", {}),
    }
    validator = jsonschema.Draft202012Validator(
        receipt_schema, format_checker=jsonschema.FormatChecker()
    )
    findings: list[Finding] = []
    for error in sorted(validator.iter_errors(receipt), key=lambda item: list(item.path)):
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        findings.append(
            Finding(
                "portfolio_receipt_schema",
                PORTFOLIO_RECEIPT_RELATIVE.as_posix(),
                f"{location}: {error.message}",
            )
        )
    return findings


def _check_evidence_references(manifest: dict[str, Any], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    references: list[dict[str, Any]] = []
    for repository in manifest.get("repositories", []):
        references.extend(repository.get("evidence", []))
    for capability in manifest.get("capabilities", []):
        references.extend(capability.get("evidence", []))
    references.extend(manifest.get("doctrine_mesh_specification", {}).get("evidence", []))

    for reference in references:
        if reference.get("kind") == "github_url":
            target = reference.get("target", "")
            if not target.startswith("https://github.com/lowelltwong-alt/"):
                findings.append(Finding("external_evidence_url", "project-evidence.yaml", "GitHub evidence URL is outside the allowlisted owner"))
            continue
        try:
            relative = _safe_repo_path(reference.get("target", ""))
        except PortfolioValidationError as exc:
            findings.append(Finding("local_evidence_path", "project-evidence.yaml", str(exc)))
            continue
        candidate = root / relative
        if not candidate.exists():
            findings.append(Finding("local_evidence_missing", relative.as_posix(), "referenced evidence does not exist"))

    for route in manifest.get("evidence_routes", []):
        for value in [route.get("start_at", ""), *route.get("then_read", [])]:
            if value.startswith("https://"):
                continue
            try:
                relative = _safe_repo_path(value)
            except PortfolioValidationError as exc:
                findings.append(Finding("route_path", "project-evidence.yaml", str(exc)))
                continue
            if not (root / relative).exists():
                findings.append(Finding("route_target_missing", relative.as_posix(), "route target does not exist"))
    return findings


def _check_repository_inventory(manifest: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    repositories = manifest.get("repositories", [])
    ids = [item.get("repository_id") for item in repositories]
    if set(ids) != EXPECTED_REPOSITORIES or len(ids) != len(set(ids)):
        findings.append(Finding("repository_inventory", "project-evidence.yaml", "repository IDs must equal the four unique Logos public repositories"))

    fields = (
        "tracked_files",
        "json_paths",
        "yaml_paths",
        "schema_like_paths",
        "validator_like_paths",
        "test_like_paths",
    )
    declared_totals = manifest.get("snapshot", {}).get("totals", {})
    for field in fields:
        actual = sum(int(item.get("counts", {}).get(field, 0)) for item in repositories)
        if declared_totals.get(field) != actual:
            findings.append(Finding("repository_total", "project-evidence.yaml", f"{field} total does not equal repository rows"))
    return findings


def _missing_interrogation_route_requirements(
    prompt_text: str, repository_ids: set[str]
) -> list[str]:
    lowered = " ".join(prompt_text.split()).lower()
    required = {
        *REQUIRED_INTERROGATION_ROUTE_TOKENS,
        *repository_ids,
    }
    return sorted(
        token
        for token in required
        if token.lower() not in lowered
    )


def _check_interrogation_route(
    root: Path, manifest: dict[str, Any]
) -> list[Finding]:
    relative = Path(
        "docs/portfolio/logos-trust-layer/AI-INTERROGATION-PROMPT.md"
    )
    try:
        prompt_text = (root / relative).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PortfolioValidationError(
            f"cannot read AI interrogation prompt: {exc}"
        ) from exc

    repository_ids = {
        row["repository_id"]
        for row in manifest.get("repositories", [])
        if isinstance(row, dict) and isinstance(row.get("repository_id"), str)
    }
    missing = _missing_interrogation_route_requirements(
        prompt_text, repository_ids
    )
    if not missing:
        return []

    return [
        Finding(
            "interrogation_route",
            relative.as_posix(),
            "missing required cross-repository route token(s): "
            + ", ".join(missing),
        )
    ]


def _check_agent_mesh(root: Path) -> list[Finding]:
    relative = Path("docs/portfolio/logos-trust-layer/agent-mesh-manifest.json")
    mesh = _load_json(root / relative)
    findings: list[Finding] = []
    if mesh.get("schema_version") != "dad.task_local_agent_mesh_manifest.v1":
        findings.append(Finding("mesh_schema", relative.as_posix(), "unexpected schema version"))
    roles = mesh.get("roles", [])
    role_ids = [role.get("role_id") for role in roles]
    if len(role_ids) != len(set(role_ids)):
        findings.append(Finding("mesh_roles", relative.as_posix(), "duplicate role IDs"))
    if mesh.get("writer_role_id") == mesh.get("checker_role_id"):
        findings.append(Finding("mesh_independence", relative.as_posix(), "writer and checker are identical"))
    if mesh.get("max_delegation_depth") != 1:
        findings.append(Finding("mesh_depth", relative.as_posix(), "delegation depth must remain one"))
    if mesh.get("manifest_digest") != _canonical_digest(mesh, ("manifest_digest",)):
        findings.append(Finding("mesh_digest", relative.as_posix(), "canonical digest mismatch"))
    relation_by_id = {role.get("role_id"): role.get("writer_checker_relation") for role in roles}
    if relation_by_id.get(mesh.get("writer_role_id")) != "writer":
        findings.append(Finding("mesh_writer", relative.as_posix(), "writer role relation is invalid"))
    if relation_by_id.get(mesh.get("checker_role_id")) != "checker":
        findings.append(Finding("mesh_checker", relative.as_posix(), "checker role relation is invalid"))
    return findings


def _check_doctrine_freeze(
    manifest: dict[str, Any], doctrine_root: Path, validator_path: Path, root: Path
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    doctrine = manifest.get("doctrine_mesh_specification", {})
    managed_files = [
        path
        for path in doctrine_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    if len(managed_files) != doctrine.get("release_file_count"):
        findings.append(Finding("doctrine_release_count", str(doctrine_root.relative_to(root)), "managed file count does not match public evidence"))

    revision = _load_yaml(doctrine_root / "revision-manifest.yaml")
    final_saved = _load_yaml(doctrine_root / "FINAL-SAVED-VERSION.yaml")
    receipt = _load_json(doctrine_root / "checks/validation-receipt.json")
    review = _load_json(doctrine_root / "checks/independent-review.json")

    comparisons = {
        "payload_file_count": revision.get("payload_file_count"),
        "payload_digest": revision.get("payload_digest"),
        "revision_manifest_digest": revision.get("manifest_digest"),
        "final_saved_version_digest": final_saved.get("final_digest"),
        "independent_review_status": review.get("status"),
        "independence_status": review.get("independence_status"),
        "cross_provider_verified": review.get("cross_provider_verified"),
    }
    for field, observed in comparisons.items():
        if doctrine.get(field) != observed:
            findings.append(Finding("doctrine_freeze_value", "project-evidence.yaml", f"{field} disagrees with frozen evidence"))

    expected_flags = {
        "runtime_activation_authorized": False,
        "source_ingestion_authorized": False,
        "substantive_doctrine_implementation_authorized": False,
        "completed_doctrine_corpus": False,
        "qualified_theological_authority": False,
    }
    for field, expected in expected_flags.items():
        if doctrine.get(field) is not expected:
            findings.append(Finding("doctrine_authority_boundary", "project-evidence.yaml", f"{field} must remain false"))

    if final_saved.get("publication_authorized") is not doctrine.get("freeze_publication_authorized"):
        findings.append(Finding("doctrine_freeze_publication", "project-evidence.yaml", "freeze-time publication flag disagrees with saved artifact"))
    if receipt.get("status") != "pass_artifact_specification_only":
        findings.append(Finding("doctrine_receipt", "checks/validation-receipt.json", "unexpected specification receipt status"))
    if receipt.get("test_result", {}).get("test_count") != doctrine.get("adversarial_test_count"):
        findings.append(Finding("doctrine_test_count", "checks/validation-receipt.json", "test count disagrees with public evidence"))

    module = _load_doctrine_validator(validator_path)
    try:
        doctrine_failures, checks = module.validate_revision(doctrine_root, "final")
    except Exception as exc:  # fail closed around the revision-owned validator
        raise PortfolioValidationError(f"doctrine validator failed to execute: {exc}") from exc
    for failure in doctrine_failures:
        findings.append(Finding("doctrine_static_validator", str(validator_path.relative_to(root)), str(failure)))

    expected_metrics = {
        "parsed_structured_files": "structured_file_count",
        "mesh_roles": "capability_role_count",
        "domain_profiles": "expert_profile_count",
        "graph_nodes": "graph_node_count",
        "graph_edges": "graph_edge_count",
    }
    for check_key, manifest_key in expected_metrics.items():
        if checks.get(check_key) != doctrine.get(manifest_key):
            findings.append(Finding("doctrine_metric", "project-evidence.yaml", f"{manifest_key} disagrees with static replay"))

    return findings, {
        "doctrine_managed_files": len(managed_files),
        "doctrine_static_failures": len(doctrine_failures),
    }


def _load_json_at_commit(root: Path, commit: str, path: str) -> dict[str, Any]:
    raw = _git_object_bytes(root, commit, path)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PortfolioValidationError(
            f"cannot parse historical JSON {commit}:{path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise PortfolioValidationError(
            f"historical JSON is not an object: {commit}:{path}"
        )
    return value


def _scan_release_snapshot(
    root: Path,
    base_commit: str,
    content_head: str,
    receipt_commit: str,
    release_paths: Iterable[str],
) -> tuple[list[Finding], int, int]:
    findings: list[Finding] = []
    scanned = 0
    skipped = 0
    receipt_path = PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    for path in sorted(set(release_paths)):
        if PurePosixPath(path).suffix.lower() not in TEXT_SUFFIXES:
            continue
        commit = receipt_commit if path == receipt_path else content_head
        raw = _git_object_bytes(root, commit, path)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            skipped += 1
            findings.append(
                Finding(
                    "release_scope_privacy_scan",
                    path,
                    "text-suffixed release file is not valid UTF-8",
                )
            )
            continue
        baseline_raw = _git_object_bytes_if_present(root, base_commit, path)
        if baseline_raw is None:
            baseline_text = ""
        else:
            try:
                baseline_text = baseline_raw.decode("utf-8")
            except UnicodeDecodeError:
                skipped += 1
                findings.append(
                    Finding(
                        "release_scope_privacy_baseline",
                        path,
                        "baseline text is not valid UTF-8, so added-occurrence comparison is unavailable",
                    )
                )
                continue
        scanned += 1
        findings.extend(scan_candidate_added_text(path, text, baseline_text))
    return findings, scanned, skipped


def _composed_snapshot_drift(
    root: Path,
    anchor_commit: str,
    content_head: str,
    receipt_commit: str,
    release_paths: Iterable[str],
) -> list[str]:
    """Return release paths whose integration-anchor bytes differ from review."""

    receipt_path = PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    drift: list[str] = []
    for path in sorted(set(release_paths)):
        expected_commit = receipt_commit if path == receipt_path else content_head
        try:
            expected = _git_object_bytes(root, expected_commit, path)
            observed = _git_object_bytes(root, anchor_commit, path)
        except PortfolioValidationError:
            drift.append(path)
            continue
        if observed != expected:
            drift.append(path)
    return drift


def _is_durable_public_path(path: str, doctrine_prefix: str) -> bool:
    """Identify release surfaces that require a fresh receipt after integration."""

    protected_files = {
        *EXPECTED_PUBLIC_FILES,
        *EXPECTED_NAVIGATION_FILES,
        "scripts/validation_contracts.py",
    }
    return (
        path in protected_files
        or path.startswith("docs/portfolio/logos-trust-layer/")
        or path.startswith(doctrine_prefix)
    )


def _check_historical_v1_evidence(
    scope: dict[str, Any], root: Path, prior_content_head: str
) -> list[Finding]:
    """Replay the preserved V1 portable and Windows-specific evidence."""

    findings: list[Finding] = []
    historical = scope.get("historical_v1", {})
    algorithm = scope.get("canonical_digest_algorithm")
    staged_parent = historical.get("staged_candidate_parent")
    artifact = historical.get("artifact_commit")
    if any(
        not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None
        for value in (staged_parent, artifact)
    ):
        return [
            Finding(
                "release_scope_v1_evidence",
                "project-evidence.yaml",
                "historical V1 commits must be exact",
            )
        ]
    assert isinstance(staged_parent, str) and isinstance(artifact, str)
    if not _git_is_ancestor(root, staged_parent, artifact) or not _git_is_ancestor(
        root, artifact, prior_content_head
    ):
        findings.append(
            Finding(
                "release_scope_v1_evidence",
                "project-evidence.yaml",
                "historical V1 ancestry is not retained in the prior release",
            )
        )

    for field in ("validation_receipt_ref", "independent_review_ref"):
        try:
            relative = _safe_repo_path(historical.get(field, ""))
        except PortfolioValidationError as exc:
            findings.append(
                Finding("release_scope_v1_evidence", "project-evidence.yaml", str(exc))
            )
            continue
        if not (root / relative).is_file():
            findings.append(
                Finding(
                    "release_scope_v1_evidence",
                    relative.as_posix(),
                    "historical V1 evidence path is missing",
                )
            )

    exclusions = tuple(historical.get("portable_replay_excluded_paths", []))
    for path in exclusions:
        try:
            if _safe_repo_path(path).as_posix() != path:
                raise PortfolioValidationError(f"historical exclusion is not canonical: {path!r}")
        except PortfolioValidationError as exc:
            findings.append(
                Finding("release_scope_v1_evidence", "project-evidence.yaml", str(exc))
            )
    historical_paths, portable_digest = _git_snapshot_fingerprint(
        root, staged_parent, artifact, exclusions
    )
    fingerprinted = [path for path in historical_paths if path not in set(exclusions)]
    environment_digest = _historical_windows_index_digest(
        root,
        artifact,
        fingerprinted,
        "docs/roadmap/logos-stewardship-architecture-buildout",
    )
    post_v1_paths = {
        entry.path
        for entry in _git_delta_entries(root, artifact, prior_content_head)
    }
    historical_set = set(historical_paths)
    shared = historical_set & post_v1_paths
    v1_only = historical_set - post_v1_paths
    unchanged_v1_only = {
        path
        for path in v1_only
        if _git_object_bytes(root, artifact, path)
        == _git_object_bytes(root, prior_content_head, path)
    }

    comparisons = {
        "historical_path_count": len(historical_paths),
        "historical_non_receipt_path_count": len(fingerprinted),
        "current_v1_only_paths_unchanged": len(unchanged_v1_only),
        "shared_paths_revalidated": len(shared),
        "portable_replay_digest": portable_digest,
        "historical_non_receipt_digest": environment_digest,
        "portable_replay_algorithm": algorithm,
    }
    for field, observed in comparisons.items():
        if historical.get(field) != observed:
            findings.append(
                Finding(
                    "release_scope_v1_replay",
                    "project-evidence.yaml",
                    f"historical_v1.{field} does not replay",
                )
            )
    if (
        historical.get("historical_receipt_digest_algorithm_id")
        != "windows_pathlib_staged_index_path_sha256_rows.v1"
        or historical.get("historical_receipt_replay_status")
        != "historical_evidence_only"
    ):
        findings.append(
            Finding(
                "release_scope_v1_historical_digest",
                "project-evidence.yaml",
                "historical V1 environment-bound convention is not preserved as evidence only",
            )
        )

    historical_validation = _load_json_at_commit(
        root, artifact, historical.get("validation_receipt_ref", "")
    )
    historical_review = _load_json_at_commit(
        root, artifact, historical.get("independent_review_ref", "")
    )
    expected_digest = historical.get("historical_non_receipt_digest")
    if (
        historical_validation.get("validation_input", {}).get(
            "canonical_path_hash_rows_digest"
        )
        != expected_digest
        or historical_review.get("frozen_input", {}).get(
            "non_receipt_path_hash_rows_digest"
        )
        != expected_digest
    ):
        findings.append(
            Finding(
                "release_scope_v1_evidence",
                "project-evidence.yaml",
                "historical V1 receipts do not agree on their recorded digest",
            )
        )
    return findings


def _check_chained_release_scope(
    manifest: dict[str, Any], receipt: dict[str, Any], root: Path
) -> tuple[list[Finding], dict[str, int]]:
    """Validate one receipt-finalized increment without absorbing other PRs."""

    findings: list[Finding] = []
    scope = manifest.get("release_scope", {})
    chain = receipt.get("release_chain", {})
    active = chain.get("active_increment", {})
    privacy = chain.get("privacy", {})
    external = chain.get("external_baseline_finding", {})
    prior = scope.get("prior_release", {})
    receipt_prior = chain.get("prior_release", {})
    receipt_path = PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    doctrine_prefix = (
        "docs/roadmap/logos-stewardship-architecture-buildout/"
        "revisions/doctrine-mesh-v2/"
    )
    empty_metrics = {
        "release_unique_paths": 0,
        "release_fingerprinted_paths": 0,
        "release_text_files_scanned": 0,
        "release_text_files_skipped": 0,
    }

    if (
        chain.get("mode") != "direct_parent_incremental_v2"
        or chain.get("receipt_path") != receipt_path
    ):
        findings.append(
            Finding(
                "release_scope_receipt",
                receipt_path,
                "release chain mode or canonical receipt path is invalid",
            )
        )

    content_count = scope.get("current_content_path_count")
    total_count = scope.get("total_unique_path_count")
    fingerprinted_count = scope.get("receipt_excluded_path_count")
    if (
        not isinstance(content_count, int)
        or total_count != content_count + 1
        or fingerprinted_count != content_count
    ):
        findings.append(
            Finding(
                "release_scope_arithmetic",
                "project-evidence.yaml",
                "incremental content plus one receipt does not match the declared partition",
            )
        )

    active_comparisons = {
        "branch_base_commit": scope.get("base_commit"),
        "content_path_count": content_count,
        "receipt_path_count": 1,
        "total_release_path_count": total_count,
        "fingerprinted_content_path_count": fingerprinted_count,
        "added_path_count": scope.get("added_path_count"),
        "modified_path_count": scope.get("modified_path_count"),
        "deleted_path_count": scope.get("deleted_path_count"),
        "renamed_path_count": scope.get("renamed_path_count"),
        "canonical_digest_algorithm": scope.get("canonical_digest_algorithm"),
    }
    for field, expected in active_comparisons.items():
        if active.get(field) != expected:
            findings.append(
                Finding(
                    "release_scope_receipt",
                    receipt_path,
                    f"release_chain.active_increment.{field} mismatch",
                )
            )
    if receipt_prior != prior:
        findings.append(
            Finding(
                "release_scope_prior_receipt",
                receipt_path,
                "release_chain.prior_release does not match the manifest chain anchor",
            )
        )
    if prior.get("canonical_digest_algorithm") != scope.get(
        "canonical_digest_algorithm"
    ):
        findings.append(
            Finding(
                "release_scope_prior_receipt",
                receipt_path,
                "prior and current release fingerprints use different canonical algorithms",
            )
        )
    if chain.get("historical_v1") != {
        "reference": "project-evidence.yaml#/release_scope/historical_v1",
        "status": "historical_evidence_only",
    }:
        findings.append(
            Finding(
                "release_scope_v1_evidence",
                receipt_path,
                "historical V1 pointer or evidence-only status is invalid",
            )
        )

    exact_commit_fields = {
        "base_commit": scope.get("base_commit"),
        "content_head_commit": active.get("content_head_commit"),
        "prior_release.receipt_commit": prior.get("receipt_commit"),
        "prior_release.content_head_commit": prior.get("content_head_commit"),
        "prior_release.merge_commit": prior.get("merge_commit"),
        "prior_release.base_commit": prior.get("base_commit"),
    }
    invalid_commits = [
        field
        for field, value in exact_commit_fields.items()
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None
    ]
    if invalid_commits:
        findings.append(
            Finding(
                "release_scope_head",
                receipt_path,
                "non-exact commit field(s): " + ", ".join(invalid_commits),
            )
        )
        return findings, empty_metrics

    base = exact_commit_fields["base_commit"]
    content_head = exact_commit_fields["content_head_commit"]
    prior_receipt = exact_commit_fields["prior_release.receipt_commit"]
    prior_content = exact_commit_fields["prior_release.content_head_commit"]
    prior_merge = exact_commit_fields["prior_release.merge_commit"]
    prior_base = exact_commit_fields["prior_release.base_commit"]
    assert all(
        isinstance(value, str)
        for value in (
            base,
            content_head,
            prior_receipt,
            prior_content,
            prior_merge,
            prior_base,
        )
    )

    if (
        not _git_is_ancestor(root, base, content_head)
        or _git_merge_base(root, base, content_head) != base
    ):
        findings.append(
            Finding(
                "release_scope_ancestry",
                receipt_path,
                "incremental base is not the exact merge base of the content head",
            )
        )

    entries = _git_delta_entries(root, base, content_head)
    content_paths = [entry.path for entry in entries]
    if receipt_path in content_paths:
        findings.append(
            Finding(
                "release_scope_finalization",
                receipt_path,
                "the self-describing receipt changed before its receipt-only finalization commit",
            )
        )
    release_paths = sorted({*content_paths, receipt_path})
    operations = Counter(entry.status for entry in entries)
    observed_counts = {
        "current_content_path_count": len(content_paths),
        "total_unique_path_count": len(release_paths),
        "receipt_excluded_path_count": len(content_paths),
        "added_path_count": operations["A"],
        "modified_path_count": operations["M"],
        "deleted_path_count": 0,
        "renamed_path_count": 0,
    }
    for field, observed in observed_counts.items():
        if scope.get(field) != observed:
            findings.append(
                Finding(
                    "release_scope_path_count",
                    "project-evidence.yaml",
                    f"release_scope.{field} does not match the NUL-safe Git delta",
                )
            )
    content_digest = _git_path_fingerprint(root, content_head, content_paths)
    if (
        active.get("content_digest") != content_digest
        or active.get("content_tree_sha") != _git_tree_sha(root, content_head)
    ):
        findings.append(
            Finding(
                "release_scope_digest",
                receipt_path,
                "incremental content digest or tree identity mismatch",
            )
        )

    head = _git_revision(root, "HEAD")
    receipt_commit = _git_latest_path_commit(root, head, receipt_path)
    if _git_parents(root, receipt_commit) != [content_head]:
        findings.append(
            Finding(
                "release_scope_finalization",
                receipt_path,
                "current receipt was not committed directly on the declared content head",
            )
        )
    try:
        receipt_delta = _git_delta_entries(root, content_head, receipt_commit)
    except PortfolioValidationError as exc:
        findings.append(Finding("release_scope_finalization", receipt_path, str(exc)))
        receipt_delta = []
    if receipt_delta != [GitDeltaEntry("M", receipt_path)]:
        findings.append(
            Finding(
                "release_scope_finalization",
                receipt_path,
                "finalization commit must modify exactly the existing self-describing receipt",
            )
        )
    if not _git_is_ancestor(root, receipt_commit, head):
        findings.append(
            Finding(
                "release_scope_finalization",
                receipt_path,
                "current receipt commit is not retained in HEAD ancestry",
            )
        )

    release_anchor: str | None = receipt_commit
    if head != receipt_commit:
        try:
            merge_candidates = subprocess.check_output(
                [
                    "git",
                    "rev-list",
                    "--merges",
                    "--ancestry-path",
                    f"{receipt_commit}..{head}",
                ],
                cwd=root,
                text=True,
                stderr=subprocess.PIPE,
            ).splitlines()
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            raise PortfolioValidationError(f"cannot locate release merge anchor: {exc}") from exc
        release_anchor = next(
            (
                commit
                for commit in merge_candidates
                if len(_git_parents(root, commit)) == 2
                and _git_parents(root, commit)[1] == receipt_commit
            ),
            None,
        )
        if release_anchor is None:
            findings.append(
                Finding(
                    "release_scope_finalization",
                    receipt_path,
                    "HEAD does not retain a normal two-parent merge with the receipt as feature parent",
                )
            )
        else:
            integration_drift = _composed_snapshot_drift(
                root, release_anchor, content_head, receipt_commit, release_paths
            )
            if integration_drift:
                findings.append(
                    Finding(
                        "release_scope_merge_tree",
                        receipt_path,
                        f"{len(integration_drift)} incremental paths differ at the merge anchor",
                    )
                )
            post_merge_drift = sorted(
                {entry.path for entry in _git_delta_entries(root, release_anchor, head)}
                & set(release_paths)
            )
            if post_merge_drift:
                findings.append(
                    Finding(
                        "release_scope_post_merge_drift",
                        receipt_path,
                        f"{len(post_merge_drift)} exact release paths changed without a fresh receipt",
                    )
                )

    if (
        _git_parents(root, prior_receipt) != [prior_content]
        or _git_delta_entries(root, prior_content, prior_receipt)
        != [GitDeltaEntry("M", receipt_path)]
        or len(_git_parents(root, prior_merge)) != 2
        or _git_parents(root, prior_merge)[1] != prior_receipt
        or not _git_is_ancestor(root, prior_merge, base)
    ):
        findings.append(
            Finding(
                "release_scope_prior_chain",
                receipt_path,
                "prior content, receipt, normal merge, and current-base ancestry is not exact",
            )
        )
    prior_payload_raw = _git_object_bytes(root, prior_receipt, receipt_path)
    prior_payload = _load_json_at_commit(root, prior_receipt, receipt_path)
    prior_digest = prior.get("receipt_digest")
    if (
        f"sha256:{hashlib.sha256(prior_payload_raw).hexdigest()}"
        != prior.get("receipt_raw_sha256")
        or prior_payload.get("receipt_digest") != prior_digest
        or prior_digest != _canonical_digest(prior_payload, ("receipt_digest",))
    ):
        findings.append(
            Finding(
                "release_scope_prior_receipt",
                receipt_path,
                "prior raw receipt or canonical self-digest is not exact",
            )
        )
    prior_full = prior_payload.get("full_pr_composite_scope", {})
    prior_entries = _git_delta_entries(root, prior_base, prior_content)
    prior_release_paths = [entry.path for entry in prior_entries]
    prior_content_paths = [
        path for path in prior_release_paths if path != receipt_path
    ]
    prior_content_digest = _git_path_fingerprint(
        root, prior_content, prior_content_paths
    )
    prior_comparisons = {
        "base_commit": prior_base,
        "content_head_commit": prior_content,
        "path_count": prior.get("path_count"),
        "fingerprinted_path_count": prior.get("fingerprinted_path_count"),
        "algorithm": prior.get("canonical_digest_algorithm"),
        "digest": prior.get("content_digest"),
    }
    for field, expected in prior_comparisons.items():
        if prior_full.get(field) != expected:
            findings.append(
                Finding(
                    "release_scope_prior_receipt",
                    receipt_path,
                    f"prior full_pr_composite_scope.{field} mismatch",
                )
            )
    if (
        len(prior_release_paths) != prior.get("path_count")
        or len(prior_content_paths) != prior.get("fingerprinted_path_count")
        or prior_content_digest != prior.get("content_digest")
    ):
        findings.append(
            Finding(
                "release_scope_prior_replay",
                receipt_path,
                "prior release path count or digest did not replay",
            )
        )
    if (
        _git_tree_sha(root, prior_merge) != prior.get("merge_tree_sha")
        or _git_tree_sha(root, prior_receipt) != prior.get("merge_tree_sha")
    ):
        findings.append(
            Finding(
                "release_scope_prior_merge_tree",
                receipt_path,
                "prior receipt and normal-merge tree identity does not replay",
            )
        )
    prior_merge_drift = _composed_snapshot_drift(
        root, prior_merge, prior_content, prior_receipt, prior_release_paths
    )
    if prior_merge_drift:
        findings.append(
            Finding(
                "release_scope_prior_merge_tree",
                receipt_path,
                f"{len(prior_merge_drift)} prior release paths differ at its merge anchor",
            )
        )
    interrelease_drift = [
        entry.path
        for entry in _git_delta_entries(root, prior_merge, base)
        if _is_durable_public_path(entry.path, doctrine_prefix)
    ]
    if len(interrelease_drift) != prior.get("protected_drift_to_current_base_count"):
        findings.append(
            Finding(
                "release_scope_prior_post_merge_drift",
                receipt_path,
                "protected prior-release drift to the current base does not match zero",
            )
        )

    expected_privacy = {
        "mode": "exact_base_candidate_added_occurrences",
        "baseline_commit": base,
        "content_source": "active_increment.content_head_commit",
        "receipt_source": "derived_latest_receipt_commit",
        "candidate_added_finding_count": 0,
        "invalid_utf8_count": 0,
        "repository_wide_privacy_pass_claimed": False,
    }
    if privacy != expected_privacy:
        findings.append(
            Finding(
                "release_scope_privacy_contract",
                receipt_path,
                "incremental privacy statement does not preserve its exact bounded scope",
            )
        )
    expected_external = {
        "baseline_commit": base,
        "path": "tests/test_machine_citation_artifacts.py",
        "rule": "file_uri",
        "occurrence_count": 3,
        "integrated_via_pr": 120,
        "disposition": "unresolved_preexisting_not_waived",
    }
    if external != expected_external:
        findings.append(
            Finding(
                "release_scope_external_baseline",
                receipt_path,
                "known external baseline finding is not recorded exactly and without waiver",
            )
        )
    external_path = expected_external["path"]
    if external_path in content_paths:
        findings.append(
            Finding(
                "release_scope_external_baseline",
                external_path,
                "external baseline path unexpectedly entered the current release delta",
            )
        )
    external_raw = _git_object_bytes(root, base, external_path)
    try:
        external_text = external_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PortfolioValidationError(
            "known external privacy baseline is not valid UTF-8"
        ) from exc
    if len(FILE_URI.findall(external_text)) != expected_external["occurrence_count"]:
        findings.append(
            Finding(
                "release_scope_external_baseline",
                external_path,
                "known external baseline occurrence count drifted",
            )
        )

    findings.extend(_check_historical_v1_evidence(scope, root, prior_content))
    scan_findings, scanned, skipped = _scan_release_snapshot(
        root, base, content_head, receipt_commit, release_paths
    )
    findings.extend(scan_findings)
    if skipped != privacy.get("invalid_utf8_count"):
        findings.append(
            Finding(
                "release_scope_privacy_contract",
                receipt_path,
                "invalid UTF-8 count differs from the receipt",
            )
        )
    return findings, {
        "release_unique_paths": len(release_paths),
        "release_fingerprinted_paths": len(content_paths),
        "release_text_files_scanned": scanned,
        "release_text_files_skipped": skipped,
    }


def _check_release_scope(
    manifest: dict[str, Any], receipt: dict[str, Any], root: Path
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    scope = manifest.get("release_scope", {})
    if scope.get("status") == "chained_incremental_release_candidate":
        return _check_chained_release_scope(manifest, receipt, root)
    full = receipt.get("full_pr_composite_scope", {})
    post_v1 = receipt.get("post_v1_candidate_slice", {})
    receipt_path = PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    doctrine_prefix = (
        "docs/roadmap/logos-stewardship-architecture-buildout/"
        "revisions/doctrine-mesh-v2/"
    )

    expected_total = (
        scope.get("v1_checkpoint_path_count", 0)
        + scope.get("v2_path_count", 0)
        + scope.get("post_v1_portfolio_path_count", 0)
        - scope.get("shared_path_count", 0)
    )
    if expected_total != scope.get("total_unique_path_count"):
        findings.append(Finding("release_scope_arithmetic", "project-evidence.yaml", "composite path arithmetic mismatch"))
    if scope.get("v1_only_path_count") + scope.get("shared_path_count") != scope.get("v1_checkpoint_path_count"):
        findings.append(Finding("release_scope_arithmetic", "project-evidence.yaml", "V1 path partition mismatch"))
    if scope.get("v2_path_count") + scope.get("post_v1_portfolio_path_count") != scope.get("post_v1_candidate_path_count"):
        findings.append(Finding("release_scope_arithmetic", "project-evidence.yaml", "post-V1 slice arithmetic mismatch"))
    if scope.get("receipt_excluded_path_count") != scope.get("total_unique_path_count", 0) - 1:
        findings.append(Finding("release_scope_arithmetic", "project-evidence.yaml", "composite receipt exclusion mismatch"))
    if scope.get("post_v1_receipt_excluded_path_count") != scope.get("post_v1_candidate_path_count", 0) - 1:
        findings.append(Finding("release_scope_arithmetic", "project-evidence.yaml", "post-V1 receipt exclusion mismatch"))

    historical = scope.get("historical_v1", {})
    for field in ("validation_receipt_ref", "independent_review_ref"):
        try:
            relative = _safe_repo_path(historical.get(field, ""))
        except PortfolioValidationError as exc:
            findings.append(Finding("release_scope_v1_evidence", "project-evidence.yaml", str(exc)))
            continue
        if not (root / relative).is_file():
            findings.append(Finding("release_scope_v1_evidence", relative.as_posix(), "historical V1 evidence path is missing"))

    comparison_fields = {
        "base_commit": scope.get("base_commit"),
        "path_count": scope.get("total_unique_path_count"),
        "fingerprinted_path_count": scope.get("receipt_excluded_path_count"),
        "algorithm": scope.get("canonical_digest_algorithm"),
    }
    for field, expected in comparison_fields.items():
        if full.get(field) != expected:
            findings.append(Finding("release_scope_receipt", PORTFOLIO_RECEIPT_RELATIVE.as_posix(), f"full_pr_composite_scope.{field} mismatch"))
    post_comparisons = {
        "parent_commit": scope.get("v1_checkpoint_commit"),
        "path_count": scope.get("post_v1_candidate_path_count"),
        "fingerprinted_path_count": scope.get("post_v1_receipt_excluded_path_count"),
        "algorithm": scope.get("canonical_digest_algorithm"),
    }
    for field, expected in post_comparisons.items():
        if post_v1.get(field) != expected:
            findings.append(Finding("release_scope_receipt", PORTFOLIO_RECEIPT_RELATIVE.as_posix(), f"post_v1_candidate_slice.{field} mismatch"))

    content_head = full.get("content_head_commit")
    if not isinstance(content_head, str) or not re.fullmatch(r"[0-9a-f]{40}", content_head):
        findings.append(Finding("release_scope_head", PORTFOLIO_RECEIPT_RELATIVE.as_posix(), "content head is not an exact commit"))
        return findings, {
            "release_unique_paths": 0,
            "release_fingerprinted_paths": 0,
            "release_text_files_scanned": 0,
            "release_text_files_skipped": 0,
        }

    base = scope.get("base_commit", "")
    v1 = scope.get("v1_checkpoint_commit", "")
    historical = scope.get("historical_v1", {})
    staged_parent = historical.get("staged_candidate_parent", "")
    for ancestor, descendant, label in (
        (base, staged_parent, "base-to-staged-parent"),
        (staged_parent, v1, "staged-parent-to-v1"),
        (v1, content_head, "v1-to-content-head"),
    ):
        if not _git_is_ancestor(root, ancestor, descendant):
            findings.append(
                Finding(
                    "release_scope_ancestry",
                    receipt_path,
                    f"{label} ancestry is not retained",
                )
            )

    head = _git_revision(root, "HEAD")
    receipt_commit = _git_latest_path_commit(root, head, receipt_path)
    receipt_parents = _git_parents(root, receipt_commit)
    if receipt_parents != [content_head]:
        findings.append(
            Finding(
                "release_scope_finalization",
                receipt_path,
                "current receipt was not committed directly on the declared content head",
            )
        )
    if _git_changed_paths(root, content_head, receipt_commit) != [receipt_path]:
        findings.append(
            Finding(
                "release_scope_finalization",
                receipt_path,
                "finalization commit must change exactly the self-describing receipt",
            )
        )
    if not _git_is_ancestor(root, receipt_commit, head):
        findings.append(
            Finding(
                "release_scope_finalization",
                receipt_path,
                "current receipt commit is not retained in HEAD ancestry",
            )
        )

    head_parents = _git_parents(root, head)
    release_anchor: str | None = receipt_commit
    if head != receipt_commit and receipt_commit in head_parents:
        release_anchor = head
    elif head != receipt_commit:
        try:
            merge_candidates = subprocess.check_output(
                ["git", "rev-list", "--merges", "--ancestry-path", f"{receipt_commit}..{head}"],
                cwd=root,
                text=True,
                stderr=subprocess.PIPE,
            ).splitlines()
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            raise PortfolioValidationError(f"cannot locate release merge anchor: {exc}") from exc
        merge_anchor = next(
            (
                commit
                for commit in merge_candidates
                if receipt_commit in _git_parents(root, commit)
            ),
            None,
        )
        if merge_anchor is None:
            release_anchor = None
            findings.append(
                Finding(
                    "release_scope_finalization",
                    receipt_path,
                    "HEAD is neither the receipt commit nor a descendant of its direct merge anchor",
                )
            )
        else:
            release_anchor = merge_anchor
            protected_drift = [
                path
                for path in _git_changed_paths(root, merge_anchor, head)
                if _is_durable_public_path(path, doctrine_prefix)
            ]
            if protected_drift:
                findings.append(
                    Finding(
                        "release_scope_post_merge_drift",
                        receipt_path,
                        f"{len(protected_drift)} protected release paths changed without a fresh receipt",
                    )
                )

    full_paths, full_digest = _git_snapshot_fingerprint(
        root,
        base,
        content_head,
        (receipt_path,),
    )
    post_paths, post_digest = _git_snapshot_fingerprint(
        root,
        v1,
        content_head,
        (receipt_path,),
    )
    if release_anchor is not None and release_anchor != receipt_commit:
        integration_drift = _composed_snapshot_drift(
            root,
            release_anchor,
            content_head,
            receipt_commit,
            full_paths,
        )
        if integration_drift:
            findings.append(
                Finding(
                    "release_scope_merge_tree",
                    receipt_path,
                    f"{len(integration_drift)} release paths differ at the integration anchor",
                )
            )
    historical_exclusions = tuple(historical.get("portable_replay_excluded_paths", []))
    historical_paths, historical_digest = _git_snapshot_fingerprint(
        root,
        staged_parent,
        v1,
        historical_exclusions,
    )
    historical_fingerprinted_paths = [
        path for path in historical_paths if path not in set(historical_exclusions)
    ]
    historical_environment_digest = _historical_windows_index_digest(
        root,
        v1,
        historical_fingerprinted_paths,
        "docs/roadmap/logos-stewardship-architecture-buildout",
    )

    v1_set = set(historical_paths)
    post_set = set(post_paths)
    shared_paths = v1_set & post_set
    v1_only_paths = v1_set - post_set
    doctrine_paths = {path for path in post_set if path.startswith(doctrine_prefix)}
    post_v1_other_paths = post_set - doctrine_paths
    unchanged_v1_only = {
        path
        for path in v1_only_paths
        if _git_object_bytes(root, v1, path) == _git_object_bytes(root, content_head, path)
    }

    if len(full_paths) != scope.get("total_unique_path_count"):
        findings.append(Finding("release_scope_path_count", PORTFOLIO_RECEIPT_RELATIVE.as_posix(), "full PR path count mismatch"))
    if len(post_paths) != scope.get("post_v1_candidate_path_count"):
        findings.append(Finding("release_scope_path_count", PORTFOLIO_RECEIPT_RELATIVE.as_posix(), "post-V1 path count mismatch"))
    partition_counts = {
        "v1_checkpoint_path_count": len(v1_set),
        "v1_only_path_count": len(v1_only_paths),
        "shared_path_count": len(shared_paths),
        "v2_path_count": len(doctrine_paths),
        "post_v1_portfolio_path_count": len(post_v1_other_paths),
    }
    for field, observed in partition_counts.items():
        if scope.get(field) != observed:
            findings.append(
                Finding(
                    "release_scope_partition",
                    "project-evidence.yaml",
                    f"{field} does not match the Git-object partition",
                )
            )
    if len(unchanged_v1_only) != scope.get("v1_only_path_count"):
        findings.append(
            Finding(
                "release_scope_v1_immutability",
                "project-evidence.yaml",
                "one or more V1-only blobs changed after the frozen checkpoint",
            )
        )
    if len(historical_paths) != historical.get("historical_path_count"):
        findings.append(
            Finding(
                "release_scope_v1_replay",
                "project-evidence.yaml",
                "historical V1 path count mismatch",
            )
        )
    if len(historical_paths) - len(historical_exclusions) != historical.get("historical_non_receipt_path_count"):
        findings.append(
            Finding(
                "release_scope_v1_replay",
                "project-evidence.yaml",
                "historical V1 non-receipt path count mismatch",
            )
        )
    if historical.get("portable_replay_algorithm") != scope.get("canonical_digest_algorithm"):
        findings.append(
            Finding(
                "release_scope_v1_replay",
                "project-evidence.yaml",
                "portable historical replay algorithm is not the declared canonical algorithm",
            )
        )
    if historical_digest != historical.get("portable_replay_digest"):
        findings.append(
            Finding(
                "release_scope_v1_replay",
                "project-evidence.yaml",
                "portable historical V1 digest mismatch",
            )
        )
    if (
        historical.get("historical_receipt_digest_algorithm_id")
        != "windows_pathlib_staged_index_path_sha256_rows.v1"
        or historical.get("historical_receipt_replay_status")
        != "historical_evidence_only"
        or historical_environment_digest
        != historical.get("historical_non_receipt_digest")
    ):
        findings.append(
            Finding(
                "release_scope_v1_historical_digest",
                "project-evidence.yaml",
                "historical staged-index digest or its evidence-only classification is invalid",
            )
        )

    historical_validation = _load_json_at_commit(
        root, v1, historical.get("validation_receipt_ref", "")
    )
    historical_review = _load_json_at_commit(
        root, v1, historical.get("independent_review_ref", "")
    )
    historical_receipt_digest = historical.get("historical_non_receipt_digest")
    if (
        historical_validation.get("validation_input", {}).get("canonical_path_hash_rows_digest")
        != historical_receipt_digest
        or historical_review.get("frozen_input", {}).get("non_receipt_path_hash_rows_digest")
        != historical_receipt_digest
    ):
        findings.append(
            Finding(
                "release_scope_v1_evidence",
                "project-evidence.yaml",
                "historical V1 receipts do not agree on their recorded digest",
            )
        )
    if full_digest != full.get("digest"):
        findings.append(Finding("release_scope_digest", PORTFOLIO_RECEIPT_RELATIVE.as_posix(), "full PR composite digest mismatch"))
    if post_digest != post_v1.get("digest"):
        findings.append(Finding("release_scope_digest", PORTFOLIO_RECEIPT_RELATIVE.as_posix(), "post-V1 slice digest mismatch"))

    scan_findings, scanned, skipped = _scan_release_snapshot(
        root, base, content_head, receipt_commit, full_paths
    )
    findings.extend(scan_findings)
    return findings, {
        "release_unique_paths": len(full_paths),
        "release_fingerprinted_paths": len(full_paths) - 1,
        "release_text_files_scanned": scanned,
        "release_text_files_skipped": skipped,
    }


def _check_portfolio_prose(root: Path) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    try:
        text = (root / "PORTFOLIO.md").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PortfolioValidationError(f"cannot read PORTFOLIO.md: {exc}") from exc
    lowered = text.lower()
    for required in REQUIRED_BOUNDARY_TEXT:
        if required not in lowered:
            findings.append(Finding("portfolio_boundary_text", "PORTFOLIO.md", f"missing required boundary: {required}"))
    mermaid_count = text.count("```mermaid")
    prose_count = text.count("Plain-language reading:")
    if mermaid_count < 5:
        findings.append(Finding("portfolio_diagrams", "PORTFOLIO.md", "at least five Mermaid diagrams are required"))
    if prose_count != mermaid_count:
        findings.append(Finding("portfolio_diagram_accessibility", "PORTFOLIO.md", "each Mermaid diagram needs one plain-language reading"))
    return findings, {"mermaid_diagrams": mermaid_count, "diagram_prose_readings": prose_count}


def _check_navigation(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for relative in EXPECTED_NAVIGATION_FILES:
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise PortfolioValidationError(f"cannot read navigation file {relative}: {exc}") from exc
        if "PORTFOLIO.md" not in text:
            findings.append(Finding("portfolio_navigation", relative, "missing root portfolio link"))
    return findings


def _check_receipt_payload(receipt: dict[str, Any]) -> list[Finding]:
    relative = PORTFOLIO_RECEIPT_RELATIVE
    findings: list[Finding] = []
    if receipt.get("schema_version") == "logos.portfolio_validation_receipt.v2":
        required = {
            "schema_version": "logos.portfolio_validation_receipt.v2",
            "receipt_id": "LOGOS-PORTFOLIO-RELEASE-002",
            "status": "pass_scoped_incremental_release_candidate",
            "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
            "doctrine_mesh_status": "validated_specification_only",
        }
    else:
        required = {
            "schema_version": "logos.portfolio_validation_receipt.v1",
            "status": "pass_release_candidate",
            "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
            "doctrine_mesh_status": "validated_specification_only",
        }
    for field, expected in required.items():
        if receipt.get(field) != expected:
            findings.append(Finding("portfolio_receipt", relative.as_posix(), f"{field} must equal {expected}"))
    authority_fields = {
        "runtime_activation_authorized": "runtime activation",
        "source_ingestion_authorized": "source ingestion",
        "substantive_doctrine_implementation_authorized": "substantive doctrine implementation",
        "completed_doctrine_corpus": "completed doctrine corpus",
        "qualified_theological_authority_granted": "qualified theological authority",
    }
    for field, label in authority_fields.items():
        if receipt.get(field) is not False:
            findings.append(
                Finding(
                    "portfolio_receipt_authority",
                    relative.as_posix(),
                    f"{label} must remain false",
                )
            )
    if receipt.get("receipt_digest") != _canonical_digest(receipt, ("receipt_digest",)):
        findings.append(Finding("portfolio_receipt_digest", relative.as_posix(), "canonical digest mismatch"))
    return findings


def _check_receipt(root: Path) -> list[Finding]:
    return _check_receipt_payload(_load_json(root / PORTFOLIO_RECEIPT_RELATIVE))


def validate_repository(root: Path = ROOT) -> ValidationResult:
    root = root.resolve()
    packet_root = root / "docs/portfolio/logos-trust-layer"
    manifest_path = packet_root / "project-evidence.yaml"
    schema_path = packet_root / "project-evidence.schema.json"
    doctrine_root = root / "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2"
    doctrine_validator_path = doctrine_root / "checks/validate_doctrine_mesh.py"

    for relative in EXPECTED_PUBLIC_FILES:
        if not (root / relative).is_file():
            raise PortfolioValidationError(f"required public file is missing: {relative}")

    manifest = _load_yaml(manifest_path)
    schema = _load_json(schema_path)
    portfolio_receipt = _load_json(root / PORTFOLIO_RECEIPT_RELATIVE)
    if not isinstance(manifest, dict) or not isinstance(schema, dict):
        raise PortfolioValidationError("manifest and schema must be objects")

    findings: list[Finding] = []
    findings.extend(_check_manifest_schema(manifest, schema, manifest_path, root))
    findings.extend(_check_receipt_schema(portfolio_receipt, schema))
    findings.extend(_check_evidence_references(manifest, root))
    findings.extend(_check_repository_inventory(manifest))
    findings.extend(_check_interrogation_route(root, manifest))
    release_findings, release_metrics = _check_release_scope(
        manifest, portfolio_receipt, root
    )
    findings.extend(release_findings)
    findings.extend(_check_agent_mesh(root))
    doctrine_findings, doctrine_metrics = _check_doctrine_freeze(
        manifest, doctrine_root, doctrine_validator_path, root
    )
    findings.extend(doctrine_findings)
    prose_findings, prose_metrics = _check_portfolio_prose(root)
    findings.extend(prose_findings)
    findings.extend(_check_navigation(root))
    findings.extend(_check_receipt(root))

    metrics = {
        "manifest_repositories": len(manifest.get("repositories", [])),
        "manifest_capabilities": len(manifest.get("capabilities", [])),
        **doctrine_metrics,
        **release_metrics,
        **prose_metrics,
    }
    return ValidationResult(tuple(sorted(set(findings))), metrics)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = validate_repository(args.root)
    except PortfolioValidationError as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        return 1
    payload = {
        "status": "pass" if result.passed else "fail",
        "artifact_class": ARTIFACT_CLASS,
        "metrics": result.metrics,
        "findings": [finding.render() for finding in result.findings],
        "mutation_performed": False,
        "authority_granted": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
