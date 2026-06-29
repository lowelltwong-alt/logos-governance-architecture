#!/usr/bin/env python3
"""Validate the Logos governance dependency map."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "governance" / "GOVERNANCE_DEPENDENCY_MAP.yaml"

WATCHED_PREFIXES = (
    "governance/",
    "docs/governance/",
    "scripts/validation_contracts.py",
    "scripts/run_validation_suite.py",
    "scripts/validate_",
    "AI_FRONT_DOOR.md",
    "AI_TABLE_OF_CONTENTS.md",
    "AI_WORK_START_HERE.md",
    "DATA_FLOW_MAP.md",
    "docs/workflows/",
    ".github/ISSUE_TEMPLATE/",
    ".github/workflows/",
)

REQUIRED_TOP_LEVEL = {
    "object_type",
    "trust_zone",
    "lifecycle_status",
    "provenance_note",
    "reason_for_inclusion",
    "schema_version",
    "map_id",
    "owner",
    "source_repo",
    "map_authority",
    "update_policy",
    "artifacts",
}

REQUIRED_ARTIFACT_FIELDS = {
    "artifact_id",
    "title",
    "repo",
    "paths",
    "object_type",
    "trust_zone",
    "lifecycle_status",
    "authorized_by",
    "owner_decision_ref",
    "depends_on",
    "downstream_controls",
    "mirrored_by",
    "validators",
    "update_triggers",
    "provenance_note",
    "reason_for_inclusion",
}

REQUIRED_ARTIFACT_IDS = {
    "GD-001",
    "GD-002",
    "GD-003",
    "GD-004",
    "GD-005",
    "GD-006",
    "GD-007",
    "GD-008",
    "GD-009",
    "GD-010",
    "GD-013",
    "GD-014",
}

REQUIRED_COVERED_PATHS = {
    "AI_FRONT_DOOR.md",
    "AI_TABLE_OF_CONTENTS.md",
    "governance/LOGOS_REPO_REGISTRY.yaml",
    "governance/REPOSITORY_LINK_CONTRACTS.md",
    "governance/BOUNDARY_GOVERNANCE_CONSTRAINTS.md",
    "governance/EXTERNAL_ADVISORY_AUTHORITY_FIREWALL.md",
    "docs/governance/logos-cross-repo-governance-contract.md",
    "docs/governance/agent-hostile-protection.md",
    "docs/governance/noesis-boundary.md",
    "DATA_FLOW_MAP.md",
    "scripts/validation_contracts.py",
    "scripts/run_validation_suite.py",
    "governance/GOVERNANCE_DEPENDENCY_MAP.yaml",
    "docs/governance/ai-workflow/goal-prompt-premortem-preflight.md",
    "docs/governance/ai-workflow/validation-and-pr-requirements.md",
    "governance/AI_FRONT_DOOR_STANDARD.md",
    "AI_WORK_START_HERE.md",
}

REQUIRED_COMPANION_SURFACES = {
    "governance/GOVERNANCE_DEPENDENCY_MAP.yaml",
    "AI_FRONT_DOOR.md",
    "AI_TABLE_OF_CONTENTS.md",
    "AI_WORK_START_HERE.md",
    "governance/AI_FRONT_DOOR_STANDARD.md",
    "governance/LOGOS_REPO_REGISTRY.yaml",
    ".github/workflows/pr-description-governance-checks.yml",
    "docs/governance/ai-workflow/validation-and-pr-requirements.md",
    "scripts/validate_governance_dependency_map.py",
    "tests/test_governance_dependency_map.py",
}


class DependencyMapError(ValueError):
    """Raised when the governance dependency map is invalid."""


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            parts = text.split("---\n", 2)
            if len(parts) == 3:
                text = parts[1] + "\n" + parts[2]
        data = yaml.safe_load(text)
    except (OSError, yaml.YAMLError) as exc:
        raise DependencyMapError(f"{_rel(path)}: YAML unreadable: {exc}") from exc
    if not isinstance(data, dict):
        raise DependencyMapError(f"{_rel(path)}: expected a YAML mapping")
    return data


def _require_nonempty_string(container: dict[str, Any], key: str, label: str) -> None:
    if not isinstance(container.get(key), str) or not container[key].strip():
        raise DependencyMapError(f"{label}: {key} must be a non-empty string")


def _require_string_list(container: dict[str, Any], key: str, label: str, *, allow_empty: bool = False) -> None:
    value = container.get(key)
    if not isinstance(value, list) or (not allow_empty and not value):
        raise DependencyMapError(f"{label}: {key} must be a {'possibly empty ' if allow_empty else ''}list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise DependencyMapError(f"{label}: {key} must contain only non-empty strings")


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        return normalized[2:]
    return normalized


def _matches_path_rule(path: str, rule: str) -> bool:
    path = _normalize_path(path)
    rule = _normalize_path(rule)
    if rule.endswith("/"):
        return path.startswith(rule)
    return path == rule


def _artifact_coverage(data: dict[str, Any]) -> set[str]:
    coverage: set[str] = set()
    for artifact in data.get("artifacts", []):
        if not isinstance(artifact, dict):
            continue
        for key in ("paths", "validators", "update_triggers"):
            value = artifact.get(key)
            if isinstance(value, list):
                coverage.update(_normalize_path(str(item)) for item in value if str(item).strip())
    return coverage


def _git_changed_files(base_ref: str) -> list[str]:
    try:
        merge_base = subprocess.check_output(
            ["git", "merge-base", "HEAD", base_ref],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        output = subprocess.check_output(
            ["git", "diff", "--name-only", f"{merge_base}...HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [_normalize_path(line) for line in output.splitlines() if line.strip()]


def validate_dependency_map(path: Path = MAP) -> dict[str, Any]:
    data = _read_yaml(path)
    missing_top = sorted(REQUIRED_TOP_LEVEL - set(data))
    if missing_top:
        raise DependencyMapError(f"{_rel(path)}: missing top-level keys {missing_top}")

    if data["object_type"] != "governance_dependency_map":
        raise DependencyMapError(f"{_rel(path)}: object_type must be governance_dependency_map")
    if data["trust_zone"] != "canonical":
        raise DependencyMapError(f"{_rel(path)}: trust_zone must be canonical")
    if data["lifecycle_status"] != "active":
        raise DependencyMapError(f"{_rel(path)}: lifecycle_status must be active")

    authority = data["map_authority"]
    if not isinstance(authority, dict):
        raise DependencyMapError(f"{_rel(path)}: map_authority must be a mapping")
    if authority.get("records_governance_dependencies") is not True:
        raise DependencyMapError(f"{_rel(path)}: map_authority.records_governance_dependencies must be true")
    for forbidden in (
        "authorizes_child_repo_override",
        "authorizes_scripture_data_change",
        "authorizes_boundary_import",
    ):
        if authority.get(forbidden) is not False:
            raise DependencyMapError(f"{_rel(path)}: map_authority.{forbidden} must be false")

    update_policy = data["update_policy"]
    if not isinstance(update_policy, dict):
        raise DependencyMapError(f"{_rel(path)}: update_policy must be a mapping")
    if update_policy.get("changed_path_gate_enabled") is not True:
        raise DependencyMapError(f"{_rel(path)}: update_policy.changed_path_gate_enabled must be true")
    if update_policy.get("validator") != "scripts/validate_governance_dependency_map.py":
        raise DependencyMapError(f"{_rel(path)}: update_policy.validator must be scripts/validate_governance_dependency_map.py")
    _require_string_list(update_policy, "map_update_required_when_paths_change", f"{_rel(path)}: update_policy")
    watched_rules = {_normalize_path(item) for item in update_policy["map_update_required_when_paths_change"]}
    missing_watched = sorted(set(WATCHED_PREFIXES) - watched_rules)
    if missing_watched:
        raise DependencyMapError(f"{_rel(path)}: update_policy missing watched path gate(s) {missing_watched}")
    _require_string_list(
        update_policy,
        "required_companion_surfaces_when_governance_changes",
        f"{_rel(path)}: update_policy",
    )
    companion_surfaces = {
        _normalize_path(item)
        for item in update_policy["required_companion_surfaces_when_governance_changes"]
    }
    missing_companions = sorted(REQUIRED_COMPANION_SURFACES - companion_surfaces)
    if missing_companions:
        raise DependencyMapError(f"{_rel(path)}: update_policy missing companion surface(s) {missing_companions}")

    artifacts = data["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise DependencyMapError(f"{_rel(path)}: artifacts must be a non-empty list")

    artifact_ids: set[str] = set()
    covered_paths: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise DependencyMapError(f"{_rel(path)}: each artifact must be a mapping")
        artifact_id = str(artifact.get("artifact_id", "<missing>"))
        label = f"{_rel(path)}:{artifact_id}"
        missing = sorted(REQUIRED_ARTIFACT_FIELDS - set(artifact))
        if missing:
            raise DependencyMapError(f"{label}: missing keys {missing}")
        if artifact_id in artifact_ids:
            raise DependencyMapError(f"{label}: duplicate artifact_id")
        artifact_ids.add(artifact_id)
        for key in (
            "title",
            "repo",
            "object_type",
            "trust_zone",
            "lifecycle_status",
            "authorized_by",
            "owner_decision_ref",
            "provenance_note",
            "reason_for_inclusion",
        ):
            _require_nonempty_string(artifact, key, label)
        for key in ("paths", "downstream_controls", "mirrored_by", "validators", "update_triggers"):
            _require_string_list(artifact, key, label)
        _require_string_list(artifact, "depends_on", label, allow_empty=True)
        for dependency in artifact["depends_on"]:
            if dependency not in artifact_ids and dependency not in REQUIRED_ARTIFACT_IDS:
                raise DependencyMapError(f"{label}: unknown dependency {dependency}")
        covered_paths.update(_normalize_path(path_value) for path_value in artifact["paths"])

    missing_artifacts = sorted(REQUIRED_ARTIFACT_IDS - artifact_ids)
    if missing_artifacts:
        raise DependencyMapError(f"{_rel(path)}: missing required artifact ids {missing_artifacts}")

    missing_paths = sorted(REQUIRED_COVERED_PATHS - covered_paths)
    if missing_paths:
        raise DependencyMapError(f"{_rel(path)}: required paths missing coverage {missing_paths}")

    return data


def validate_changed_path_gate(
    *,
    changed_files: list[str],
    map_path: Path = MAP,
    map_updated: bool | None = None,
) -> None:
    normalized = [_normalize_path(path) for path in changed_files]
    watched_changed = [
        path for path in normalized
        if any(path.startswith(prefix) for prefix in WATCHED_PREFIXES)
    ]
    if map_updated is None:
        map_rel = _rel(map_path)
        map_updated = map_rel in normalized
    if watched_changed and not map_updated:
        raise DependencyMapError(
            "governance dependency map must be updated when watched paths change: "
            + ", ".join(watched_changed)
        )
    if watched_changed:
        data = validate_dependency_map(map_path)
        coverage = _artifact_coverage(data)
        uncovered = [
            path for path in watched_changed
            if not any(_matches_path_rule(path, rule) for rule in coverage)
        ]
        if uncovered:
            raise DependencyMapError(
                "changed governance paths must be registered in dependency map coverage: "
                + ", ".join(uncovered)
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=MAP)
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--map-updated", choices=["true", "false"], default=None)
    args = parser.parse_args(argv)

    try:
        validate_dependency_map(args.map)
        changed_files = args.changed_file or _git_changed_files(args.base_ref)
        map_updated = None
        if args.map_updated is not None:
            map_updated = args.map_updated == "true"
        validate_changed_path_gate(
            changed_files=changed_files,
            map_path=args.map,
            map_updated=map_updated,
        )
    except DependencyMapError as exc:
        print(f"Governance dependency map validation failed: {exc}", file=sys.stderr)
        return 1

    print("Governance dependency map validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
