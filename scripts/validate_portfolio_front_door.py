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
import os
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
MARATHON_ROOT = (
    ROOT
    / "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3"
)
MARATHON_VALIDATOR_PATH = MARATHON_ROOT / "checks/validate_doctrine_marathon.py"
ARTIFACT_CLASS = "portable_core"
DECLARED_V3_FINAL_BLOCKER = (
    "adversarial_harness_release_gate: V3 cannot release until the aggregate "
    "exact-oracle migration is complete and independently reviewed"
)
MARATHON_HARNESS_EVIDENCE_TARGETS = (
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
    "doctrine-marathon-v3/checks/adversarial-harness-migration.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
    "doctrine-marathon-v3/checks/ADVERSARIAL_HARNESS_ROOT_FIX.md",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
    "doctrine-marathon-v3/checks/DETERMINISTIC_ADVERSARIAL_HARNESS_CONTRACT.md",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
    "doctrine-marathon-v3/checks/fixtures/strict-isolated-cases.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
    "doctrine-marathon-v3/checks/fixtures/aggregate-sentinel-cases.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
    "doctrine-marathon-v3/checks/run_adversarial_harness.py",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
    "doctrine-marathon-v3/checks/test_run_adversarial_harness.py",
)

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
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/README.md",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/revision-manifest.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/FINAL-SAVED-VERSION.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validation-receipt.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/independent-review.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/public-release-authorization.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/examples/design-time-independence-fixture.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/role-catalog.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/qualification-registry.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/events/event-ledger.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/evidence/evidence-registry.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/evidence/evidence-review-receipt.schema.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/firewall/action-checker-requirements.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/firewall/prompt-neutrality-contract.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/state/fresh-context-verification-receipt.schema.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/state/examples/initial-weekly-fresh-context-gate.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/graph/human-identity-authority-root.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/graph/authority-registry.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/redteam/repair-ledger.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/redteam/ai-mistake-escalation-2026-08-27.yaml",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/fixtures/negative-cases.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_validate_doctrine_marathon.py",
    *MARATHON_HARNESS_EVIDENCE_TARGETS,
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


class _DuplicateKeyError(ValueError):
    """Raised when a structured public input contains an ambiguous duplicate key."""


def _reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise _DuplicateKeyError(f"duplicate key {key!r}")
        value[key] = item
    return value


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects last-key-wins ambiguity."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    value: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in value:
            raise _DuplicateKeyError(f"duplicate key {key!r}")
        value[key] = loader.construct_object(value_node, deep=deep)
    return value


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


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


def _raw_validation_result(
    findings: Iterable[Finding], metrics: dict[str, Any]
) -> ValidationResult:
    """Retain exact validator emission order and duplicate finding identities."""

    return ValidationResult(tuple(findings), metrics)


def _v3_final_replay_is_exact(failures: Iterable[Any]) -> bool:
    """Accept only the one declared V3 aggregate-harness release blocker."""

    return tuple(str(failure) for failure in failures) == (
        DECLARED_V3_FINAL_BLOCKER,
    )


def _load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_object_pairs,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, _DuplicateKeyError) as exc:
        raise PortfolioValidationError(f"cannot load JSON {path}: {exc}") from exc


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except (OSError, UnicodeDecodeError, yaml.YAMLError, _DuplicateKeyError) as exc:
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


def _git_merge_free_content_chain(
    root: Path, base_commit: str, content_head: str
) -> list[str]:
    """Return the exact ordered one-parent chain from base (exclusive) to head."""

    for label, commit in (("base", base_commit), ("content head", content_head)):
        if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
            raise PortfolioValidationError(f"release {label} is not an exact commit")
        if _git_revision(root, commit) != commit:
            raise PortfolioValidationError(
                f"release {label} does not resolve to its exact commit"
            )
    reverse_chain: list[str] = []
    seen: set[str] = set()
    current = content_head
    while current != base_commit:
        if current in seen:
            raise PortfolioValidationError("content history contains a parent cycle")
        if len(reverse_chain) >= 256:
            raise PortfolioValidationError("content history exceeds the bounded chain limit")
        seen.add(current)
        parents = _git_parents(root, current)
        if len(parents) != 1:
            raise PortfolioValidationError(
                "content history must be a merge-free first-parent chain"
            )
        reverse_chain.append(current)
        current = parents[0]
    if not reverse_chain:
        raise PortfolioValidationError("content history must contain at least one commit")
    return list(reversed(reverse_chain))


def _validate_content_history_scope(
    root: Path,
    base_commit: str,
    content_chain: Iterable[str],
    cumulative_entries: Iterable[GitDeltaEntry],
) -> None:
    """Reject transient paths and non-additive operations hidden by a cumulative diff."""

    touched_paths: set[str] = set()
    parent = base_commit
    for commit in content_chain:
        entries = _git_delta_entries(root, parent, commit)
        touched_paths.update(entry.path for entry in entries)
        parent = commit
    cumulative_paths = {entry.path for entry in cumulative_entries}
    if touched_paths != cumulative_paths:
        raise PortfolioValidationError(
            "per-commit content paths do not equal the cumulative release scope"
        )


def _check_receipt_content_chain(
    active_increment: dict[str, Any],
    scope: dict[str, Any],
    content_chain: Iterable[str],
    receipt_path: str,
) -> list[Finding]:
    """Bind the receipt to the exact derived content history without omissions."""

    derived = list(content_chain)
    observed = {
        "content_history_mode": active_increment.get("content_history_mode"),
        "content_commit_count": active_increment.get("content_commit_count"),
        "content_commit_chain": active_increment.get("content_commit_chain"),
    }
    expected = {
        "content_history_mode": scope.get("content_history_mode"),
        "content_commit_count": len(derived),
        "content_commit_chain": derived,
    }
    if observed == expected:
        return []
    return [
        Finding(
            "release_scope_content_chain",
            receipt_path,
            "receipt content history does not match the exact derived chain",
        )
    ]


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


def _resolve_in_root_regular_file(root: Path, relative: Path) -> Path:
    """Resolve one public-evidence file without following links or reparse points."""

    try:
        resolved_root = root.resolve(strict=True)
        candidate = root / relative
        current = candidate
        while current != root and current != current.parent:
            if current.is_symlink() or (
                hasattr(os.path, "isjunction") and os.path.isjunction(current)
            ):
                raise PortfolioValidationError(
                    f"evidence path traverses a link or junction: {relative.as_posix()}"
                )
            current = current.parent
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise PortfolioValidationError(
            f"evidence path is missing or unreadable: {relative.as_posix()}"
        ) from exc
    if not resolved.is_relative_to(resolved_root) or not resolved.is_file():
        raise PortfolioValidationError(
            f"evidence path is not an in-root regular file: {relative.as_posix()}"
        )
    return resolved


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


def _load_marathon_validator(validator_path: Path) -> ModuleType:
    try:
        spec = importlib.util.spec_from_file_location(
            "logos_doctrine_marathon_static_validator", validator_path
        )
        if spec is None or spec.loader is None:
            raise PortfolioValidationError("cannot create marathon validator module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except (OSError, ImportError, AttributeError) as exc:
        raise PortfolioValidationError(
            f"cannot import marathon validator: {exc}"
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
    definition_by_version = {
        "logos.portfolio_validation_receipt.v2": "portfolioValidationReceiptV2",
        "logos.portfolio_validation_receipt.v3": "portfolioValidationReceiptV3",
    }
    definition = definition_by_version.get(receipt.get("schema_version"))
    if definition is None or definition not in schema.get("$defs", {}):
        return [
            Finding(
                "portfolio_receipt_schema",
                PORTFOLIO_RECEIPT_RELATIVE.as_posix(),
                "unsupported receipt schema version",
            )
        ]
    receipt_schema = {
        "$schema": schema.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        "$ref": f"#/$defs/{definition}",
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
    references.extend(manifest.get("doctrine_marathon_specification", {}).get("evidence", []))

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
        try:
            _resolve_in_root_regular_file(root, relative)
        except PortfolioValidationError as exc:
            findings.append(
                Finding("local_evidence_missing", relative.as_posix(), str(exc))
            )

    routes = manifest.get("evidence_routes", [])
    route_ids = [
        route.get("route_id") for route in routes if isinstance(route, dict)
    ]
    if (
        len(route_ids) != len(routes)
        or any(not isinstance(route_id, str) or not route_id for route_id in route_ids)
        or len(route_ids) != len(set(route_ids))
    ):
        findings.append(
            Finding(
                "evidence_route_identity",
                "project-evidence.yaml",
                "evidence route IDs must be non-empty and unique",
            )
        )
    for route in routes:
        if not isinstance(route, dict):
            continue
        for value in [route.get("start_at", ""), *route.get("then_read", [])]:
            if value.startswith("https://"):
                continue
            try:
                relative = _safe_repo_path(value)
            except PortfolioValidationError as exc:
                findings.append(Finding("route_path", "project-evidence.yaml", str(exc)))
                continue
            try:
                _resolve_in_root_regular_file(root, relative)
            except PortfolioValidationError as exc:
                findings.append(
                    Finding("route_target_missing", relative.as_posix(), str(exc))
                )
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


def _check_marathon_freeze(
    manifest: dict[str, Any], marathon_root: Path, validator_path: Path, root: Path
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    public = manifest.get("doctrine_marathon_specification", {})
    managed_files = [
        path
        for path in marathon_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    if len(managed_files) != public.get("release_file_count"):
        findings.append(
            Finding(
                "marathon_release_count",
                str(marathon_root.relative_to(root)),
                "managed file count does not match public evidence",
            )
        )

    revision = _load_yaml(marathon_root / "revision-manifest.yaml")
    saved_path = marathon_root / "FINAL-SAVED-VERSION.yaml"
    review_path = marathon_root / "checks/independent-review.json"
    saved = _load_yaml(saved_path) if saved_path.is_file() else {}
    receipt = _load_json(marathon_root / "checks/validation-receipt.json")
    review = _load_json(review_path) if review_path.is_file() else {}
    negative_cases = _load_json(
        marathon_root / "checks/fixtures/negative-cases.json"
    )
    strict_isolated_catalog = _load_json(
        marathon_root / "checks/fixtures/strict-isolated-cases.json"
    )
    aggregate_sentinel_catalog = _load_json(
        marathon_root / "checks/fixtures/aggregate-sentinel-cases.json"
    )
    graph = _load_json(marathon_root / "graph/example-graph.json")
    mesh = _load_json(marathon_root / "mesh/agent-mesh.v3.json")
    assignments = _load_json(
        marathon_root / "mesh/examples/design-time-independence-fixture.json"
    )
    qualification = _load_json(marathon_root / "mesh/qualification-registry.json")
    triggers = _load_yaml(marathon_root / "firewall/trigger-matrix.yaml")
    ledger = _load_json(marathon_root / "events/event-ledger.json")
    evidence = _load_json(marathon_root / "evidence/evidence-registry.json")
    debt = _load_json(marathon_root / "debt/initial-review-debt.json")
    repairs = _load_yaml(marathon_root / "redteam/repair-ledger.yaml")
    mistake = _load_yaml(
        marathon_root / "redteam/ai-mistake-escalation-2026-08-27.yaml"
    )

    evidence_record_count = sum(
        len(evidence.get(key, []))
        for key in (
            "source_records",
            "translation_lineages",
            "influence_hypotheses",
            "historical_attributions",
            "claim_records",
            "evidence_review_receipts",
        )
    )
    runtime_assignment_count = (
        len(assignments.get("assignments", []))
        if assignments.get("runtime_assignments") is True
        else 0
    )
    if not isinstance(negative_cases, list) or not all(
        isinstance(row, dict) and isinstance(row.get("case_id"), str)
        for row in negative_cases
    ):
        raise PortfolioValidationError("V3 legacy negative-case catalog is malformed")
    if not isinstance(strict_isolated_catalog, dict) or not isinstance(
        strict_isolated_catalog.get("cases"), list
    ):
        raise PortfolioValidationError("V3 strict isolated-case catalog is malformed")
    strict_isolated_cases = strict_isolated_catalog["cases"]
    if not all(
        isinstance(row, dict) and isinstance(row.get("case_id"), str)
        for row in strict_isolated_cases
    ):
        raise PortfolioValidationError("V3 strict isolated-case catalog lacks stable case IDs")
    if not isinstance(aggregate_sentinel_catalog, dict) or not isinstance(
        aggregate_sentinel_catalog.get("cases"), list
    ):
        raise PortfolioValidationError("V3 aggregate-sentinel catalog is malformed")
    aggregate_sentinel_cases = aggregate_sentinel_catalog["cases"]
    if not all(
        isinstance(row, dict)
        and isinstance(row.get("case_id"), str)
        and isinstance(row.get("source_case_id"), str)
        for row in aggregate_sentinel_cases
    ):
        raise PortfolioValidationError("V3 aggregate-sentinel catalog lacks stable source bindings")
    legacy_case_ids = [row["case_id"] for row in negative_cases]
    strict_isolated_case_ids = [row["case_id"] for row in strict_isolated_cases]
    aggregate_source_case_ids = [
        row["source_case_id"] for row in aggregate_sentinel_cases
    ]
    if len(set(legacy_case_ids)) != len(legacy_case_ids):
        raise PortfolioValidationError("V3 legacy negative-case catalog has duplicate IDs")
    if len(set(strict_isolated_case_ids)) != len(strict_isolated_case_ids):
        raise PortfolioValidationError("V3 strict isolated-case catalog has duplicate IDs")
    if len(set(aggregate_source_case_ids)) != len(aggregate_source_case_ids) or not set(
        aggregate_source_case_ids
    ).issubset(legacy_case_ids):
        raise PortfolioValidationError(
            "V3 aggregate-sentinel cases must be unique named subsets of legacy cases"
        )

    comparisons = {
        "payload_file_count": revision.get("payload_file_count"),
        "administrative_file_count": len(
            revision.get("administrative_files_excluded_from_payload_digest", [])
        ),
        "payload_digest": revision.get("payload_digest"),
        "revision_manifest_file_digest": (
            saved.get("revision_manifest_digest")
            if saved
            else "sha256:"
            + hashlib.sha256(
                _canonical_content_bytes(
                    (marathon_root / "revision-manifest.yaml").read_bytes()
                )
            ).hexdigest()
        ),
        "final_saved_version_digest": saved.get("final_digest"),
        "independent_review_status": (
            review.get("result") if review else "pending_final_receipts"
        ),
        "independence_status": (
            review.get("independence_status")
            if review
            else "pending_non_author_read_only_review"
        ),
        "role_count": len(mesh.get("roles", [])),
        "trigger_count": len(triggers.get("triggers", [])),
        "assignment_fixture_count": len(assignments.get("assignments", [])),
        "runtime_assignment_count": runtime_assignment_count,
        "expert_pack_count": len(qualification.get("expert_packs", [])),
        "qualification_receipt_count": len(
            qualification.get("qualification_receipts", [])
        ),
        "correlation_acceptance_count": len(
            qualification.get("correlation_acceptance_receipts", [])
        ),
        "event_count": len(ledger.get("events", [])),
        "evidence_record_count": evidence_record_count,
        "graph_node_count": len(graph.get("nodes", [])),
        "graph_edge_count": len(graph.get("edges", [])),
        "legacy_component_case_count": len(negative_cases),
        "strict_isolated_component_case_count": len(strict_isolated_cases),
        "component_only_executable_case_count": len(negative_cases)
        + len(strict_isolated_cases),
        "aggregate_sentinel_subset_case_count": len(aggregate_sentinel_cases),
        "negative_case_catalog_count": len(negative_cases),
        "isolated_regression_case_count": len(strict_isolated_cases),
        "negative_case_count": len(negative_cases) + len(strict_isolated_cases),
        "open_expert_review_debt": sum(
            1 for row in debt if row.get("status") == "open"
        ),
        "mistake_receipt_count": len(
            list((marathon_root / "redteam").glob("ai-mistake-escalation-*.yaml"))
        ),
        "corrective_action_count": len(
            mistake.get("capa", {}).get("corrective_actions", [])
        ),
        "preventive_action_count": len(
            mistake.get("capa", {}).get("preventive_actions", [])
        ),
        "repair_ledger_entry_count": len(repairs.get("repairs", [])),
    }
    for field, observed in comparisons.items():
        if public.get(field) != observed:
            findings.append(
                Finding(
                    "marathon_freeze_value",
                    "project-evidence.yaml",
                    f"{field} disagrees with frozen V3 evidence",
                )
            )

    expected_evidence_targets = [
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/README.md",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/role-catalog.yaml",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/examples/design-time-independence-fixture.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/qualification-registry.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/evidence/evidence-registry.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/evidence/evidence-review-receipt.schema.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/firewall/action-checker-requirements.yaml",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/firewall/prompt-neutrality-contract.yaml",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/state/fresh-context-verification-receipt.schema.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/state/examples/initial-weekly-fresh-context-gate.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/graph/human-identity-authority-root.yaml",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/graph/authority-registry.yaml",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/events/event-ledger.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/redteam/repair-ledger.yaml",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/redteam/ai-mistake-escalation-2026-08-27.yaml",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/fixtures/negative-cases.json",
        *MARATHON_HARNESS_EVIDENCE_TARGETS,
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_validate_doctrine_marathon.py",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/revision-manifest.yaml",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/public-release-authorization.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validation-receipt.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/independent-review.json",
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/FINAL-SAVED-VERSION.yaml",
    ]
    observed_evidence_targets = [
        row.get("target")
        for row in public.get("evidence", [])
        if isinstance(row, dict)
    ]
    if observed_evidence_targets != expected_evidence_targets:
        findings.append(
            Finding(
                "marathon_public_evidence_route",
                "project-evidence.yaml",
                "V3 evidence targets must equal the exact public audit set",
            )
        )

    expected_route = {
        "route_id": "doctrine-marathon-v3-audit",
        "question": (
            "How can an independent reviewer reproduce the Doctrine Marathon V3 "
            "control, non-runtime, CAPA, and frozen-release claims?"
        ),
        "start_at": (
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
            "doctrine-marathon-v3/README.md"
        ),
        "then_read": [
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/role-catalog.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/examples/design-time-independence-fixture.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/qualification-registry.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/evidence/evidence-registry.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/evidence/evidence-review-receipt.schema.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/firewall/action-checker-requirements.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/firewall/prompt-neutrality-contract.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/state/fresh-context-verification-receipt.schema.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/state/examples/initial-weekly-fresh-context-gate.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/graph/human-identity-authority-root.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/graph/authority-registry.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/events/event-ledger.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/redteam/repair-ledger.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/redteam/ai-mistake-escalation-2026-08-27.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/fixtures/negative-cases.json",
            *MARATHON_HARNESS_EVIDENCE_TARGETS,
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_validate_doctrine_marathon.py",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/revision-manifest.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/public-release-authorization.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validation-receipt.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/independent-review.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/FINAL-SAVED-VERSION.yaml",
        ],
    }
    matching_routes = [
        row
        for row in manifest.get("evidence_routes", [])
        if isinstance(row, dict)
        and row.get("route_id") == "doctrine-marathon-v3-audit"
    ]
    if matching_routes != [expected_route]:
        findings.append(
            Finding(
                "marathon_public_evidence_route",
                "project-evidence.yaml",
                "V3 audit route is missing or not exact",
            )
        )

    required_commands = {
        "python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validate_doctrine_marathon.py --mode final",
        "python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_validate_doctrine_marathon.py",
        "python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/run_adversarial_harness.py",
        "python -B -m pytest -q --assert=plain -p no:cacheprovider docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_run_adversarial_harness.py",
    }
    observed_commands = set(manifest.get("verification", {}).get("commands", []))
    if not required_commands.issubset(observed_commands):
        findings.append(
            Finding(
                "marathon_public_validation_route",
                "project-evidence.yaml",
                "V3 validation commands are missing from the public replay route",
            )
        )

    expected_false = (
        "cross_provider_verified",
        "runtime_activation_authorized",
        "research_execution_authorized",
        "source_ingestion_authorized",
        "substantive_doctrine_implementation_authorized",
        "completed_doctrine_corpus",
        "qualified_theological_authority",
    )
    for field in expected_false:
        if public.get(field) is not False:
            findings.append(
                Finding(
                    "marathon_authority_boundary",
                    "project-evidence.yaml",
                    f"{field} must remain false",
                )
            )
    design_time_flags = {
        "runtime_assignments": assignments.get("runtime_assignments"),
        "qualification_runtime_records": qualification.get("runtime_records"),
        "event_runtime_records": ledger.get("runtime_events"),
        "evidence_runtime_records": evidence.get("runtime_records"),
    }
    for field, observed in design_time_flags.items():
        if observed is not False:
            findings.append(
                Finding(
                    "marathon_runtime_nonclaim",
                    "project-evidence.yaml",
                    f"{field} must remain false",
                )
            )
    if public.get("maturity") != "blocked_specification_only":
        findings.append(
            Finding(
                "marathon_maturity",
                "project-evidence.yaml",
                "V3 maturity must remain blocked_specification_only until the aggregate exact-oracle migration is complete and independently reviewed",
            )
        )

    expected_oracle_controls = {
        "input_snapshot_bound": True,
        "duplicate_structured_keys_rejected": True,
        "ordered_duplicate_findings_preserved": True,
        "alternate_root_isolated": True,
        "single_receipt_read": True,
        "sentinel_count": 5,
        "sentinel_ids": [
            "portfolio-v3-maturity-overclaim",
            "portfolio-v3-migration-gate-erasure",
            "portfolio-v3-authority-elevation",
            "portfolio-v3-required-route-omission",
            "portfolio-release-chain-drift",
        ],
    }
    if manifest.get("verification", {}).get("oracle_controls") != expected_oracle_controls:
        findings.append(
            Finding(
                "portfolio_oracle_contract",
                "project-evidence.yaml",
                "portfolio oracle controls and five exact sentinels are not bound",
            )
        )
    if public.get("declared_final_blocker") != DECLARED_V3_FINAL_BLOCKER:
        findings.append(
            Finding(
                "marathon_declared_blocker",
                "project-evidence.yaml",
                "V3 declared final blocker must equal the aggregate exact-oracle release gate",
            )
        )
    if receipt.get("result") != "pass" or receipt.get("mode") != "prefinal":
        findings.append(
            Finding(
                "marathon_receipt",
                "checks/validation-receipt.json",
                "unexpected V3 final receipt result",
            )
        )

    module = _load_marathon_validator(validator_path)
    try:
        marathon_failures, metrics = module.validate_all("final")
    except Exception as exc:
        raise PortfolioValidationError(
            f"marathon validator failed to execute: {exc}"
        ) from exc
    if not _v3_final_replay_is_exact(marathon_failures):
        findings.append(
            Finding(
                "marathon_final_replay",
                str(validator_path.relative_to(root)),
                "final replay must contain exactly the declared aggregate exact-oracle release gate and no unexpected findings",
            )
        )
    if metrics.get("payload_file_count") != public.get("payload_file_count"):
        findings.append(
            Finding(
                "marathon_metric",
                "project-evidence.yaml",
                "payload_file_count disagrees with static replay",
            )
        )
    metric_comparisons = {
        "assignment_fixture_count": metrics.get("assignment_fixture_count"),
        "event_count": metrics.get("event_count"),
        "evidence_record_count": metrics.get("evidence_record_count"),
        "graph_node_count": metrics.get("graph_node_count"),
        "graph_edge_count": metrics.get("graph_edge_count"),
        "open_expert_review_debt": metrics.get("open_expert_review_debt"),
    }
    for field, observed in metric_comparisons.items():
        if public.get(field) != observed:
            findings.append(
                Finding(
                    "marathon_metric",
                    "project-evidence.yaml",
                    f"{field} disagrees with final static replay",
                )
            )
    return findings, {
        "marathon_managed_files": len(managed_files),
        "marathon_static_failures": len(marathon_failures),
        "marathon_unexpected_final_findings": int(
            not _v3_final_replay_is_exact(marathon_failures)
        ),
        "marathon_component_source_case_count": len(negative_cases)
        + len(strict_isolated_cases),
        "marathon_aggregate_sentinel_subset_case_count": len(
            aggregate_sentinel_cases
        ),
    }


def _load_json_at_commit(root: Path, commit: str, path: str) -> dict[str, Any]:
    raw = _git_object_bytes(root, commit, path)
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_object_pairs,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, _DuplicateKeyError) as exc:
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


def _scan_content_history(
    root: Path,
    base_commit: str,
    content_chain: Iterable[str],
) -> list[Finding]:
    """Scan every changed text blob in publishable history, not only the final tree."""

    findings: list[Finding] = []
    parent = base_commit
    baseline_cache: dict[str, str | None] = {}
    for commit in content_chain:
        entries = _git_delta_entries(root, parent, commit)
        for entry in entries:
            path = entry.path
            if PurePosixPath(path).suffix.lower() not in TEXT_SUFFIXES:
                continue
            raw = _git_object_bytes(root, commit, path)
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                findings.append(
                    Finding(
                        "release_scope_history_privacy",
                        path,
                        f"text blob at content commit {commit[:12]} is not valid UTF-8",
                    )
                )
                continue
            if path not in baseline_cache:
                baseline_raw = _git_object_bytes_if_present(root, base_commit, path)
                if baseline_raw is None:
                    baseline_cache[path] = ""
                else:
                    try:
                        baseline_cache[path] = baseline_raw.decode("utf-8")
                    except UnicodeDecodeError:
                        baseline_cache[path] = None
            baseline_text = baseline_cache[path]
            if baseline_text is None:
                findings.append(
                    Finding(
                        "release_scope_history_privacy",
                        path,
                        "baseline text is not valid UTF-8, so history comparison is unavailable",
                    )
                )
                continue
            for finding in scan_candidate_added_text(path, text, baseline_text):
                findings.append(
                    Finding(
                        "release_scope_history_privacy",
                        path,
                        f"{finding.rule} at content commit {commit[:12]}: {finding.detail}",
                    )
                )
        parent = commit
    return findings


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


def _check_intermediate_receipt_checkpoint(
    scope: dict[str, Any], root: Path, current_content_head: str
) -> list[Finding]:
    """Replay one superseded pre-publication receipt without granting authority."""

    findings: list[Finding] = []
    checkpoint = scope.get("intermediate_receipt", {})
    receipt_path = PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    base = scope.get("base_commit")
    content_head = checkpoint.get("content_head_commit")
    receipt_commit = checkpoint.get("receipt_commit")
    if any(
        not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None
        for value in (base, content_head, receipt_commit)
    ):
        return [
            Finding(
                "release_scope_intermediate_receipt",
                receipt_path,
                "intermediate checkpoint commits must be exact",
            )
        ]
    assert all(isinstance(value, str) for value in (base, content_head, receipt_commit))

    if (
        _git_parents(root, receipt_commit) != [content_head]
        or _git_delta_entries(root, content_head, receipt_commit)
        != [GitDeltaEntry("M", receipt_path)]
        or not _git_is_ancestor(root, receipt_commit, current_content_head)
        or _git_object_bytes(root, current_content_head, receipt_path)
        != _git_object_bytes(root, receipt_commit, receipt_path)
    ):
        findings.append(
            Finding(
                "release_scope_intermediate_receipt",
                receipt_path,
                "intermediate receipt is not an exact retained direct-parent checkpoint",
            )
        )

    raw = _git_object_bytes(root, receipt_commit, receipt_path)
    payload = _load_json_at_commit(root, receipt_commit, receipt_path)
    if (
        f"sha256:{hashlib.sha256(raw).hexdigest()}"
        != checkpoint.get("receipt_raw_sha256")
        or payload.get("receipt_digest") != checkpoint.get("receipt_digest")
        or payload.get("receipt_digest")
        != _canonical_digest(payload, ("receipt_digest",))
        or _git_tree_sha(root, receipt_commit) != checkpoint.get("receipt_tree_sha")
    ):
        findings.append(
            Finding(
                "release_scope_intermediate_receipt",
                receipt_path,
                "intermediate receipt raw bytes, self-digest, or tree identity drifted",
            )
        )

    if (
        checkpoint.get("status")
        != "superseded_prepublication_non_authorizing_checkpoint"
        or payload.get("schema_version") != "logos.portfolio_validation_receipt.v2"
        or payload.get("receipt_id") != "LOGOS-PORTFOLIO-RELEASE-002"
        or payload.get("status") != "pass_scoped_incremental_release_candidate"
        or payload.get("release_chain", {}).get("prior_release")
        != scope.get("prior_release")
    ):
        findings.append(
            Finding(
                "release_scope_intermediate_receipt",
                receipt_path,
                "intermediate receipt identity, status, or prior-release anchor drifted",
            )
        )
    for field in (
        "runtime_activation_authorized",
        "source_ingestion_authorized",
        "substantive_doctrine_implementation_authorized",
        "completed_doctrine_corpus",
        "qualified_theological_authority_granted",
    ):
        if payload.get(field) is not False:
            findings.append(
                Finding(
                    "release_scope_intermediate_authority",
                    receipt_path,
                    f"intermediate receipt elevated {field}",
                )
            )

    entries = _git_delta_entries(root, base, content_head)
    if any(entry.path == receipt_path for entry in entries):
        findings.append(
            Finding(
                "release_scope_intermediate_receipt",
                receipt_path,
                "intermediate content checkpoint included its own receipt",
            )
        )
    paths = [entry.path for entry in entries]
    operations = Counter(entry.status for entry in entries)
    active = payload.get("release_chain", {}).get("active_increment", {})
    comparisons = {
        "content_head_commit": content_head,
        "content_tree_sha": checkpoint.get("content_tree_sha"),
        "content_path_count": checkpoint.get("content_path_count"),
        "total_release_path_count": checkpoint.get("total_release_path_count"),
        "fingerprinted_content_path_count": checkpoint.get(
            "fingerprinted_content_path_count"
        ),
        "added_path_count": checkpoint.get("added_path_count"),
        "modified_path_count": checkpoint.get("modified_path_count"),
        "deleted_path_count": checkpoint.get("deleted_path_count"),
        "renamed_path_count": checkpoint.get("renamed_path_count"),
        "content_digest": checkpoint.get("content_digest"),
    }
    for field, expected in comparisons.items():
        if active.get(field) != expected:
            findings.append(
                Finding(
                    "release_scope_intermediate_receipt",
                    receipt_path,
                    f"intermediate active_increment.{field} mismatch",
                )
            )
    if (
        active.get("branch_base_commit") != base
        or active.get("canonical_digest_algorithm")
        != scope.get("canonical_digest_algorithm")
        or len(paths) != checkpoint.get("content_path_count")
        or len(paths) + 1 != checkpoint.get("total_release_path_count")
        or len(paths) != checkpoint.get("fingerprinted_content_path_count")
        or operations["A"] != checkpoint.get("added_path_count")
        or operations["M"] != checkpoint.get("modified_path_count")
        or checkpoint.get("deleted_path_count") != 0
        or checkpoint.get("renamed_path_count") != 0
        or _git_tree_sha(root, content_head) != checkpoint.get("content_tree_sha")
        or _git_path_fingerprint(root, content_head, paths)
        != checkpoint.get("content_digest")
    ):
        findings.append(
            Finding(
                "release_scope_intermediate_replay",
                receipt_path,
                "intermediate content scope, operations, tree, or digest did not replay",
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
    intermediate = scope.get("intermediate_receipt", {})
    receipt_intermediate = chain.get("intermediate_receipt", {})
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
    if receipt_intermediate != intermediate:
        findings.append(
            Finding(
                "release_scope_intermediate_receipt",
                receipt_path,
                "release_chain.intermediate_receipt does not match the manifest checkpoint",
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

    findings.extend(
        _check_intermediate_receipt_checkpoint(scope, root, content_head)
    )
    all_entries = _git_delta_entries(root, base, content_head)
    receipt_entries = [entry for entry in all_entries if entry.path == receipt_path]
    if receipt_entries != [GitDeltaEntry("M", receipt_path)]:
        findings.append(
            Finding(
                "release_scope_intermediate_receipt",
                receipt_path,
                "the content checkpoint must retain exactly one pinned intermediate receipt delta",
            )
        )
    entries = [entry for entry in all_entries if entry.path != receipt_path]
    content_paths = [entry.path for entry in entries]
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


def _check_prior_release_003(
    scope: dict[str, Any], root: Path
) -> tuple[list[Finding], list[str]]:
    """Replay the exact integrated Release 003 anchor used by Release 004."""

    findings: list[Finding] = []
    prior = scope.get("prior_release", {})
    receipt_path = PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    exact = {
        "release_id": "LOGOS-PORTFOLIO-RELEASE-003",
        "base_commit": "f159e3f54d96755cd93dc5cfcd069085be4fb2ca",
        "content_head_commit": "6bb775321f93fe97dff5a90a3c3bdca42f42edfb",
        "content_tree_sha": "a9307538e127d87fdc987f6c86921401679286e5",
        "receipt_commit": "424cd882da0ac0f8271254b8c27149acb1f5b571",
        "merge_commit": "f320d8430c10f82d4fdd80567c4d533fa90c25d5",
        "receipt_tree_sha": "565e9b71faff3f7296d35e310ad3c31110403df9",
        "merge_tree_sha": "565e9b71faff3f7296d35e310ad3c31110403df9",
        "receipt_raw_sha256": "sha256:448449c335e7c67295f94195f415b1b3a0952447f1a6057ce1545a2d36f17851",
        "receipt_digest": "sha256:35e046eae2b684c2196bb44dc299e0a8e0882a399738360f25f98156821f2d57",
        "manifest_raw_sha256": "sha256:fe201b881d8b5b62fdb9d862db43eea1b8ae7f4969294355ebbaf50a535b664f",
        "release_chain_digest": "sha256:e3ad5952f884602e472c4070754141afa27a517c090f890eba0be91c3e075d31",
        "content_path_count": 85,
        "total_release_path_count": 86,
        "fingerprinted_content_path_count": 85,
        "added_path_count": 64,
        "modified_path_count": 21,
        "deleted_path_count": 0,
        "renamed_path_count": 0,
        "content_digest": "sha256:7b7a4885889ee32ef38d83cbb1008204c990d34cfce0c7decdfa3fc923be16ab",
        "protected_drift_to_current_base_count": 0,
    }
    for field, expected in exact.items():
        if prior.get(field) != expected:
            findings.append(
                Finding(
                    "release_scope_prior_receipt",
                    receipt_path,
                    f"Release 003 {field} is not the immutable anchor",
                )
            )
    if prior.get("canonical_digest_algorithm") != scope.get(
        "canonical_digest_algorithm"
    ):
        findings.append(
            Finding(
                "release_scope_prior_receipt",
                receipt_path,
                "Release 003 and Release 004 fingerprint algorithms differ",
            )
        )

    prior_base = exact["base_commit"]
    prior_content = exact["content_head_commit"]
    prior_receipt = exact["receipt_commit"]
    prior_merge = exact["merge_commit"]
    entries = _git_delta_entries(root, prior_base, prior_content)
    receipt_entries = [entry for entry in entries if entry.path == receipt_path]
    content_entries = [entry for entry in entries if entry.path != receipt_path]
    content_paths = [entry.path for entry in content_entries]
    release_paths = sorted({*content_paths, receipt_path})
    operations = Counter(entry.status for entry in content_entries)
    if (
        receipt_entries != [GitDeltaEntry("M", receipt_path)]
        or len(content_paths) != exact["content_path_count"]
        or len(release_paths) != exact["total_release_path_count"]
        or operations["A"] != exact["added_path_count"]
        or operations["M"] != exact["modified_path_count"]
        or _git_path_fingerprint(root, prior_content, content_paths)
        != exact["content_digest"]
        or _git_tree_sha(root, prior_content) != exact["content_tree_sha"]
    ):
        findings.append(
            Finding(
                "release_scope_prior_replay",
                receipt_path,
                "Release 003 path set, operations, content digest, or tree did not replay",
            )
        )
    if (
        _git_parents(root, prior_receipt) != [prior_content]
        or _git_delta_entries(root, prior_content, prior_receipt)
        != [GitDeltaEntry("M", receipt_path)]
        or len(_git_parents(root, prior_merge)) != 2
        or _git_parents(root, prior_merge)[1] != prior_receipt
        or _git_tree_sha(root, prior_receipt) != exact["receipt_tree_sha"]
        or _git_tree_sha(root, prior_merge) != exact["merge_tree_sha"]
    ):
        findings.append(
            Finding(
                "release_scope_prior_chain",
                receipt_path,
                "Release 003 direct receipt and normal merge chain did not replay",
            )
        )
    prior_raw = _git_object_bytes(root, prior_receipt, receipt_path)
    prior_payload = _load_json_at_commit(root, prior_receipt, receipt_path)
    prior_chain = prior_payload.get("release_chain", {})
    prior_active = prior_chain.get("active_increment", {})
    manifest_raw = _git_object_bytes(
        root,
        prior_receipt,
        "docs/portfolio/logos-trust-layer/project-evidence.yaml",
    )
    if (
        "sha256:" + hashlib.sha256(prior_raw).hexdigest()
        != exact["receipt_raw_sha256"]
        or prior_payload.get("receipt_digest") != exact["receipt_digest"]
        or prior_payload.get("receipt_digest")
        != _canonical_digest(prior_payload, ("receipt_digest",))
        or _canonical_digest(prior_chain) != exact["release_chain_digest"]
        or "sha256:" + hashlib.sha256(manifest_raw).hexdigest()
        != exact["manifest_raw_sha256"]
        or prior_payload.get("schema_version")
        != "logos.portfolio_validation_receipt.v2"
        or prior_payload.get("receipt_id") != exact["release_id"]
    ):
        findings.append(
            Finding(
                "release_scope_prior_receipt",
                receipt_path,
                "Release 003 receipt, manifest, chain digest, or identity drifted",
            )
        )
    prior_active_expected = {
        "branch_base_commit": prior_base,
        "content_head_commit": prior_content,
        "content_tree_sha": exact["content_tree_sha"],
        "content_path_count": exact["content_path_count"],
        "receipt_path_count": 1,
        "total_release_path_count": exact["total_release_path_count"],
        "fingerprinted_content_path_count": exact["fingerprinted_content_path_count"],
        "added_path_count": exact["added_path_count"],
        "modified_path_count": exact["modified_path_count"],
        "deleted_path_count": 0,
        "renamed_path_count": 0,
        "canonical_digest_algorithm": scope.get("canonical_digest_algorithm"),
        "content_digest": exact["content_digest"],
    }
    if prior_active != prior_active_expected:
        findings.append(
            Finding(
                "release_scope_prior_receipt",
                receipt_path,
                "Release 003 active increment is not exact",
            )
        )
    if _composed_snapshot_drift(
        root, prior_merge, prior_content, prior_receipt, release_paths
    ):
        findings.append(
            Finding(
                "release_scope_prior_merge_tree",
                receipt_path,
                "Release 003 merge bytes differ from its reviewed composition",
            )
        )
    return findings, release_paths


def _release_004_content_entries(
    scope: dict[str, Any], root: Path, content_head: str
) -> tuple[list[Finding], list[GitDeltaEntry], list[str]]:
    findings: list[Finding] = []
    receipt_path = PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    base = scope.get("base_commit", "")
    content_chain: list[str] = []
    try:
        content_chain = _git_merge_free_content_chain(root, base, content_head)
    except PortfolioValidationError as exc:
        findings.append(
            Finding(
                "release_scope_content_chain",
                receipt_path,
                str(exc),
            )
        )
    entries = _git_delta_entries(root, base, content_head)
    if (
        scope.get("content_history_mode")
        != "exact_merge_free_first_parent_chain"
        or scope.get("content_commit_count") != len(content_chain)
    ):
        findings.append(
            Finding(
                "release_scope_content_chain",
                "project-evidence.yaml",
                "Release 004 content-history mode or commit count does not replay exactly",
            )
        )
    if content_chain:
        try:
            _validate_content_history_scope(root, base, content_chain, entries)
        except PortfolioValidationError as exc:
            findings.append(
                Finding(
                    "release_scope_history_scope",
                    receipt_path,
                    str(exc),
                )
            )
    if any(entry.path == receipt_path for entry in entries):
        findings.append(
            Finding(
                "release_scope_content_receipt",
                receipt_path,
                "Release 004 content checkpoint must retain the prior receipt unchanged",
            )
        )
    operations = Counter(entry.status for entry in entries)
    observed = {
        "current_content_path_count": len(entries),
        "total_unique_path_count": len(entries) + 1,
        "receipt_excluded_path_count": len(entries),
        "added_path_count": operations["A"],
        "modified_path_count": operations["M"],
        "deleted_path_count": 0,
        "renamed_path_count": 0,
    }
    for field, value in observed.items():
        if scope.get(field) != value:
            findings.append(
                Finding(
                    "release_scope_path_count",
                    "project-evidence.yaml",
                    f"Release 004 {field} does not match the exact Git delta",
                )
            )
    return findings, entries, content_chain


def _check_release_004_content_checkpoint(
    manifest: dict[str, Any], receipt: dict[str, Any], root: Path
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    scope = manifest.get("release_scope", {})
    prior_findings, _ = _check_prior_release_003(scope, root)
    findings.extend(prior_findings)
    head = _git_revision(root, "HEAD")
    content_findings, entries, content_chain = _release_004_content_entries(
        scope, root, head
    )
    findings.extend(content_findings)
    if content_chain:
        findings.extend(
            _scan_content_history(root, scope.get("base_commit", ""), content_chain)
        )
    prior_receipt = scope.get("prior_release", {}).get("receipt_commit", "")
    receipt_path = PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    if (
        receipt.get("schema_version") != "logos.portfolio_validation_receipt.v2"
        or receipt.get("receipt_id") != "LOGOS-PORTFOLIO-RELEASE-003"
        or _git_object_bytes(root, head, receipt_path)
        != _git_object_bytes(root, prior_receipt, receipt_path)
    ):
        findings.append(
            Finding(
                "release_scope_content_receipt",
                receipt_path,
                "content checkpoint does not preserve the exact Release 003 receipt",
            )
        )
    paths = [entry.path for entry in entries]
    release_paths = sorted({*paths, receipt_path})
    scan_findings, scanned, skipped = _scan_release_snapshot(
        root, scope.get("base_commit", ""), head, prior_receipt, release_paths
    )
    findings.extend(scan_findings)
    return findings, {
        "release_unique_paths": len(release_paths),
        "release_fingerprinted_paths": len(paths),
        "release_text_files_scanned": scanned,
        "release_text_files_skipped": skipped,
    }


def _check_release_004_finalized(
    manifest: dict[str, Any], receipt: dict[str, Any], root: Path
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    scope = manifest.get("release_scope", {})
    chain = receipt.get("release_chain", {})
    active = chain.get("active_increment", {})
    receipt_path = PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    prior_findings, prior_paths = _check_prior_release_003(scope, root)
    findings.extend(prior_findings)
    if (
        chain.get("mode") != "merge_free_first_parent_incremental_v3"
        or chain.get("receipt_path") != receipt_path
        or chain.get("prior_release") != scope.get("prior_release")
        or chain.get("historical_v1")
        != {
            "reference": "project-evidence.yaml#/release_scope/historical_v1",
            "status": "historical_evidence_only",
        }
    ):
        findings.append(
            Finding(
                "release_scope_receipt",
                receipt_path,
                "Release 004 mode, path, or prior anchors are invalid",
            )
        )
    content_head = active.get("content_head_commit")
    if not isinstance(content_head, str) or re.fullmatch(r"[0-9a-f]{40}", content_head) is None:
        findings.append(Finding("release_scope_head", receipt_path, "content head is not exact"))
        return findings, {
            "release_unique_paths": 0,
            "release_fingerprinted_paths": 0,
            "release_text_files_scanned": 0,
            "release_text_files_skipped": 0,
        }
    content_findings, entries, content_chain = _release_004_content_entries(
        scope, root, content_head
    )
    findings.extend(content_findings)
    if content_chain:
        findings.extend(
            _scan_content_history(root, scope.get("base_commit", ""), content_chain)
        )
        findings.extend(
            _check_receipt_content_chain(active, scope, content_chain, receipt_path)
        )
    paths = [entry.path for entry in entries]
    release_paths = sorted({*paths, receipt_path})
    active_expected = {
        "branch_base_commit": scope.get("base_commit"),
        "content_head_commit": content_head,
        "content_tree_sha": _git_tree_sha(root, content_head),
        "content_history_mode": scope.get("content_history_mode"),
        "content_commit_count": len(content_chain),
        "content_commit_chain": content_chain,
        "content_path_count": len(paths),
        "receipt_path_count": 1,
        "total_release_path_count": len(release_paths),
        "fingerprinted_content_path_count": len(paths),
        "added_path_count": Counter(entry.status for entry in entries)["A"],
        "modified_path_count": Counter(entry.status for entry in entries)["M"],
        "deleted_path_count": 0,
        "renamed_path_count": 0,
        "canonical_digest_algorithm": scope.get("canonical_digest_algorithm"),
        "content_digest": _git_path_fingerprint(root, content_head, paths),
    }
    if active != active_expected:
        findings.append(
            Finding(
                "release_scope_digest",
                receipt_path,
                "Release 004 active increment did not replay exactly",
            )
        )
    head = _git_revision(root, "HEAD")
    receipt_commit = _git_latest_path_commit(root, head, receipt_path)
    if (
        _git_parents(root, receipt_commit) != [content_head]
        or _git_delta_entries(root, content_head, receipt_commit)
        != [GitDeltaEntry("M", receipt_path)]
        or not _git_is_ancestor(root, receipt_commit, head)
    ):
        findings.append(
            Finding(
                "release_scope_finalization",
                receipt_path,
                "Release 004 finalization must be a retained receipt-only direct child",
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
            raise PortfolioValidationError(
                f"cannot locate Release 004 merge anchor: {exc}"
            ) from exc
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
                    "HEAD does not retain the normal two-parent Release 004 merge",
                )
            )
        else:
            if _composed_snapshot_drift(
                root, release_anchor, content_head, receipt_commit, release_paths
            ):
                findings.append(
                    Finding(
                        "release_scope_merge_tree",
                        receipt_path,
                        "Release 004 merge bytes differ from the reviewed composition",
                    )
                )
            protected = set(release_paths) | set(prior_paths)
            drift = sorted(
                {entry.path for entry in _git_delta_entries(root, release_anchor, head)}
                & protected
            )
            if drift:
                findings.append(
                    Finding(
                        "release_scope_post_merge_drift",
                        receipt_path,
                        f"{len(drift)} current or prior release paths changed without a fresh receipt",
                    )
                )
    privacy_expected = {
        "mode": "exact_base_candidate_added_occurrences",
        "baseline_commit": scope.get("base_commit"),
        "content_source": "active_increment.content_head_commit",
        "receipt_source": "derived_latest_receipt_commit",
        "candidate_added_finding_count": 0,
        "invalid_utf8_count": 0,
        "repository_wide_privacy_pass_claimed": False,
    }
    external_expected = {
        "baseline_commit": scope.get("base_commit"),
        "path": "tests/test_machine_citation_artifacts.py",
        "rule": "file_uri",
        "occurrence_count": 3,
        "integrated_via_pr": 120,
        "disposition": "unresolved_preexisting_not_waived",
    }
    if chain.get("privacy") != privacy_expected:
        findings.append(Finding("release_scope_privacy_contract", receipt_path, "privacy boundary drifted"))
    if chain.get("external_baseline_finding") != external_expected:
        findings.append(Finding("release_scope_external_baseline", receipt_path, "external baseline record drifted"))
    external_text = _git_object_bytes(
        root, scope.get("base_commit", ""), external_expected["path"]
    ).decode("utf-8")
    if len(FILE_URI.findall(external_text)) != external_expected["occurrence_count"]:
        findings.append(Finding("release_scope_external_baseline", external_expected["path"], "baseline occurrence count drifted"))
    findings.extend(
        _check_historical_v1_evidence(
            scope, root, scope.get("prior_release", {}).get("content_head_commit", "")
        )
    )
    scan_findings, scanned, skipped = _scan_release_snapshot(
        root,
        scope.get("base_commit", ""),
        content_head,
        receipt_commit,
        release_paths,
    )
    findings.extend(scan_findings)
    if skipped != 0:
        findings.append(Finding("release_scope_privacy_contract", receipt_path, "invalid UTF-8 count differs from zero"))
    return findings, {
        "release_unique_paths": len(release_paths),
        "release_fingerprinted_paths": len(paths),
        "release_text_files_scanned": scanned,
        "release_text_files_skipped": skipped,
    }


def _check_release_scope(
    manifest: dict[str, Any], receipt: dict[str, Any], root: Path
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    scope = manifest.get("release_scope", {})
    if scope.get("status") == "chained_incremental_release_candidate":
        if scope.get("release_id") == "LOGOS-PORTFOLIO-RELEASE-004":
            if receipt.get("schema_version") == "logos.portfolio_validation_receipt.v2":
                return _check_release_004_content_checkpoint(manifest, receipt, root)
            return _check_release_004_finalized(manifest, receipt, root)
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
    schema_version = receipt.get("schema_version")
    if schema_version == "logos.portfolio_validation_receipt.v3":
        required = {
            "schema_version": "logos.portfolio_validation_receipt.v3",
            "receipt_id": "LOGOS-PORTFOLIO-RELEASE-004",
            "status": "pass_scoped_incremental_release_candidate",
            "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
            "doctrine_mesh_status": "validated_specification_only",
            "doctrine_marathon_status": "blocked_specification_only",
            "doctrine_marathon_declared_final_blocker": (
                DECLARED_V3_FINAL_BLOCKER
            ),
            "doctrine_marathon_independence_status": (
                "non_author_read_only_cross_provider_unverified"
            ),
        }
    elif schema_version == "logos.portfolio_validation_receipt.v2":
        required = {
            "schema_version": "logos.portfolio_validation_receipt.v2",
            "receipt_id": "LOGOS-PORTFOLIO-RELEASE-003",
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
    if schema_version == "logos.portfolio_validation_receipt.v3":
        authority_fields["research_execution_authorized"] = "research execution"
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


def _validation_input_snapshot(
    root: Path, manifest: dict[str, Any]
) -> tuple[str, int]:
    """Fingerprint every local file the aggregate validator can consult."""

    relative_paths = {
        *EXPECTED_PUBLIC_FILES,
        *EXPECTED_NAVIGATION_FILES,
        PORTFOLIO_RECEIPT_RELATIVE.as_posix(),
    }
    references: list[dict[str, Any]] = []
    for repository in manifest.get("repositories", []):
        if isinstance(repository, dict):
            references.extend(repository.get("evidence", []))
    for capability in manifest.get("capabilities", []):
        if isinstance(capability, dict):
            references.extend(capability.get("evidence", []))
    references.extend(
        manifest.get("doctrine_mesh_specification", {}).get("evidence", [])
    )
    references.extend(
        manifest.get("doctrine_marathon_specification", {}).get("evidence", [])
    )
    for reference in references:
        if not isinstance(reference, dict) or reference.get("kind") == "github_url":
            continue
        try:
            relative_paths.add(
                _safe_repo_path(reference.get("target", "")).as_posix()
            )
        except PortfolioValidationError:
            continue
    for route in manifest.get("evidence_routes", []):
        if not isinstance(route, dict):
            continue
        for value in [route.get("start_at", ""), *route.get("then_read", [])]:
            if isinstance(value, str) and value.startswith("https://"):
                continue
            try:
                relative_paths.add(_safe_repo_path(value).as_posix())
            except PortfolioValidationError:
                continue
    for subtree in (
        Path(
            "docs/roadmap/logos-stewardship-architecture-buildout/"
            "revisions/doctrine-mesh-v2"
        ),
        Path(
            "docs/roadmap/logos-stewardship-architecture-buildout/"
            "revisions/doctrine-marathon-v3"
        ),
    ):
        subtree_root = root / subtree
        if not subtree_root.is_dir():
            continue
        for path in subtree_root.rglob("*"):
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
            ):
                relative_paths.add(path.relative_to(root).as_posix())

    rows: list[dict[str, Any]] = []
    for relative in sorted(relative_paths):
        path = root / relative
        is_junction = bool(getattr(path, "is_junction", lambda: False)())
        if path.is_symlink() or is_junction:
            rows.append({"path": relative, "state": "linked"})
        elif not path.is_file():
            rows.append({"path": relative, "state": "missing_or_nonregular"})
        else:
            try:
                raw = path.read_bytes()
            except OSError as exc:
                raise PortfolioValidationError(
                    f"cannot snapshot validation input {relative}: {exc}"
                ) from exc
            rows.append(
                {
                    "path": relative,
                    "state": "regular",
                    "size": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            )
    digest = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return f"sha256:{digest}", len(rows)


def _validate_loaded_repository(
    root: Path,
    *,
    manifest: dict[str, Any],
    schema: dict[str, Any],
    portfolio_receipt: dict[str, Any],
) -> ValidationResult:
    """Run the one aggregate oracle over already loaded, attempt-local inputs."""

    root = root.resolve()
    packet_root = root / "docs/portfolio/logos-trust-layer"
    manifest_path = packet_root / "project-evidence.yaml"
    doctrine_root = root / "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2"
    doctrine_validator_path = doctrine_root / "checks/validate_doctrine_mesh.py"
    marathon_root = root / "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3"
    marathon_validator_path = marathon_root / "checks/validate_doctrine_marathon.py"

    for relative in EXPECTED_PUBLIC_FILES:
        try:
            _resolve_in_root_regular_file(root, Path(relative))
        except PortfolioValidationError as exc:
            raise PortfolioValidationError(
                f"required public file is missing or unsafe: {relative}: {exc}"
            ) from exc
    if (
        not isinstance(manifest, dict)
        or not isinstance(schema, dict)
        or not isinstance(portfolio_receipt, dict)
    ):
        raise PortfolioValidationError("manifest, schema, and receipt must be objects")

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
    marathon_findings, marathon_metrics = _check_marathon_freeze(
        manifest, marathon_root, marathon_validator_path, root
    )
    findings.extend(marathon_findings)
    prose_findings, prose_metrics = _check_portfolio_prose(root)
    findings.extend(prose_findings)
    findings.extend(_check_navigation(root))
    findings.extend(_check_receipt_payload(portfolio_receipt))

    metrics = {
        "manifest_repositories": len(manifest.get("repositories", [])),
        "manifest_capabilities": len(manifest.get("capabilities", [])),
        **doctrine_metrics,
        **marathon_metrics,
        **release_metrics,
        **prose_metrics,
    }
    return _raw_validation_result(findings, metrics)


def validate_repository(root: Path = ROOT) -> ValidationResult:
    root = root.resolve()
    manifest_path = root / "docs/portfolio/logos-trust-layer/project-evidence.yaml"
    schema_path = root / "docs/portfolio/logos-trust-layer/project-evidence.schema.json"
    seed_manifest = _load_yaml(manifest_path)
    if not isinstance(seed_manifest, dict):
        raise PortfolioValidationError("manifest must be an object")
    snapshot_before, input_count = _validation_input_snapshot(root, seed_manifest)
    manifest = _load_yaml(manifest_path)
    schema = _load_json(schema_path)
    portfolio_receipt = _load_json(root / PORTFOLIO_RECEIPT_RELATIVE)
    if manifest != seed_manifest:
        raise PortfolioValidationError(
            "validation inputs changed while the aggregate snapshot was established"
        )
    result = _validate_loaded_repository(
        root,
        manifest=manifest,
        schema=schema,
        portfolio_receipt=portfolio_receipt,
    )
    snapshot_after, after_count = _validation_input_snapshot(root, manifest)
    findings = list(result.findings)
    if snapshot_after != snapshot_before or after_count != input_count:
        findings.append(
            Finding(
                "validation_input_drift",
                "<aggregate-input-snapshot>",
                "validation inputs changed during the aggregate run",
            )
        )
    return _raw_validation_result(
        findings,
        {**result.metrics, "validation_input_file_count": input_count},
    )


def _result_payload(result: ValidationResult) -> dict[str, Any]:
    return {
        "status": "pass" if result.passed else "fail",
        "artifact_class": ARTIFACT_CLASS,
        "metrics": result.metrics,
        "findings_raw": [
            {"rule": item.rule, "path": item.path, "detail": item.detail}
            for item in result.findings
        ],
        "findings": [item.render() for item in result.findings],
        "findings_presentation": sorted(
            {item.render() for item in result.findings}
        ),
        "mutation_performed": False,
        "authority_granted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = validate_repository(args.root)
    except PortfolioValidationError as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        return 1
    payload = _result_payload(result)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
