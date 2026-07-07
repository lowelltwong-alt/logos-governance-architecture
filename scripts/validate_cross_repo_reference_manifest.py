#!/usr/bin/env python3
"""Validate cross-repo reference freshness manifests.

The validator is structural only. It verifies that governed references point to
real local files when sibling repositories are available; it does not authorize
child-repo edits, source imports, Scripture output changes, or theology claims.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "governance" / "CROSS_REPO_REFERENCE_MANIFEST.yaml"
STANDARD = ROOT / "governance" / "MIRROR_FRESHNESS_STANDARD.yaml"
GATE_TRIGGER_REGISTRY = ROOT / "schemas" / "doctrine_genealogy" / "gate_trigger_registry.v1.yaml"
DEPENDENCY_MAP = ROOT / "governance" / "GOVERNANCE_DEPENDENCY_MAP.yaml"

REQUIRED_MANIFEST_FIELDS = {
    "object_type",
    "trust_zone",
    "lifecycle_status",
    "provenance_note",
    "reason_for_inclusion",
    "schema_version",
    "manifest_id",
    "owner",
    "source_repo",
    "authority",
    "local_repo_roots",
    "references",
    "non_authorizations",
}

REQUIRED_STANDARD_FIELDS = {
    "object_type",
    "trust_zone",
    "lifecycle_status",
    "provenance_note",
    "reason_for_inclusion",
    "schema_version",
    "standard_id",
    "owner",
    "source_repo",
    "authority",
    "default_freshness_policy",
    "required_mirror_fields",
    "required_reference_fields",
    "allowed_authority_postures",
    "allowed_failure_policies",
    "non_authorizations",
}

REQUIRED_REFERENCE_FIELDS = {
    "reference_id",
    "source_path",
    "source_field",
    "target_repo",
    "target_path",
    "authority_posture",
    "failure_policy",
}

FORBIDDEN_UPWARD_DEPENDENCY_PREFIXES = (
    "logos-scripture-graph/",
    "logos-boundary-literature/",
    "logos-doctrine-genealogy/",
    "noesis-atlas/",
)

NON_AUTHORIZATIONS = {
    "scripture_output_change",
    "chunk_output_change",
    "source_import",
    "doctrine_data_records",
    "theology_authority",
}


class CrossRepoReferenceError(ValueError):
    """Raised when the cross-repo reference manifest is invalid."""


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            parts = text.split("---\n", 2)
            if len(parts) == 3:
                text = parts[1] + "\n" + parts[2]
        data = yaml.safe_load(text)
    except (OSError, yaml.YAMLError) as exc:
        raise CrossRepoReferenceError(f"{rel(path)}: unreadable YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise CrossRepoReferenceError(f"{rel(path)}: expected YAML mapping")
    return data


def require_fields(data: dict[str, Any], required: set[str], label: str) -> list[str]:
    missing = sorted(required - set(data))
    return [f"{label}: missing required field {field}" for field in missing]


def require_non_authorizing(data: dict[str, Any], label: str) -> list[str]:
    failures: list[str] = []
    authority = data.get("authority")
    if not isinstance(authority, dict):
        failures.append(f"{label}: authority must be a mapping")
        return failures
    for key, value in authority.items():
        if key.startswith("authorizes_") and value is not False:
            failures.append(f"{label}: authority.{key} must be false")

    non_authorizations = data.get("non_authorizations")
    if not isinstance(non_authorizations, list):
        failures.append(f"{label}: non_authorizations must be a list")
        return failures
    missing = sorted(NON_AUTHORIZATIONS - set(non_authorizations))
    if missing:
        failures.append(f"{label}: missing non_authorizations {', '.join(missing)}")
    return failures


def validate_standard(standard: dict[str, Any], *, label: str = rel(STANDARD)) -> list[str]:
    failures = require_fields(standard, REQUIRED_STANDARD_FIELDS, label)
    if standard.get("object_type") != "mirror_freshness_standard":
        failures.append(f"{label}: object_type must be mirror_freshness_standard")
    if standard.get("trust_zone") != "canonical":
        failures.append(f"{label}: trust_zone must be canonical")
    if standard.get("lifecycle_status") != "active":
        failures.append(f"{label}: lifecycle_status must be active")
    failures.extend(require_non_authorizing(standard, label))

    for field in ("required_mirror_fields", "required_reference_fields", "allowed_authority_postures", "allowed_failure_policies"):
        value = standard.get(field)
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            failures.append(f"{label}: {field} must be a non-empty string list")

    policy = standard.get("default_freshness_policy")
    if not isinstance(policy, dict):
        failures.append(f"{label}: default_freshness_policy must be a mapping")
    elif policy.get("missing_referenced_path_blocks_when_source_repo_available") is not True:
        failures.append(
            f"{label}: missing_referenced_path_blocks_when_source_repo_available must be true"
        )
    return failures


def parse_repo_reference(value: str) -> tuple[str, str] | None:
    if ":" not in value:
        return None
    repo, target = value.split(":", 1)
    if not repo or not target:
        return None
    return repo, target


def safe_target_path(repo_root: Path, target_path: str) -> Path:
    normalized = Path(target_path.replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts:
        raise CrossRepoReferenceError(f"target_path escapes repo root: {target_path}")
    resolved = (repo_root / normalized).resolve()
    repo_resolved = repo_root.resolve()
    try:
        resolved.relative_to(repo_resolved)
    except ValueError as exc:
        raise CrossRepoReferenceError(f"target_path escapes repo root: {target_path}") from exc
    return resolved


def resolve_repo_root(repo: str, roots: dict[str, Any], *, root: Path = ROOT) -> tuple[Path | None, list[Path]]:
    raw_candidates = roots.get(repo)
    if isinstance(raw_candidates, str):
        candidates = [raw_candidates]
    elif isinstance(raw_candidates, list):
        candidates = [item for item in raw_candidates if isinstance(item, str)]
    else:
        candidates = []

    resolved_candidates = [(root / candidate).resolve() for candidate in candidates]
    for candidate in resolved_candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate, resolved_candidates
    return None, resolved_candidates


def gate_registry_refs(gate_registry: dict[str, Any]) -> set[tuple[str, str]]:
    refs = gate_registry.get("scripture_repo_refs")
    if not isinstance(refs, dict):
        return set()
    parsed: set[tuple[str, str]] = set()
    for value in refs.values():
        if isinstance(value, str):
            parsed_value = parse_repo_reference(value)
            if parsed_value:
                parsed.add(parsed_value)
    return parsed


def validate_manifest(
    manifest: dict[str, Any],
    *,
    standard: dict[str, Any] | None = None,
    gate_registry: dict[str, Any] | None = None,
    dependency_map: dict[str, Any] | None = None,
    root: Path = ROOT,
    require_local_repos: bool = False,
    label: str = rel(MANIFEST),
) -> list[str]:
    failures = require_fields(manifest, REQUIRED_MANIFEST_FIELDS, label)
    if manifest.get("object_type") != "cross_repo_reference_manifest":
        failures.append(f"{label}: object_type must be cross_repo_reference_manifest")
    if manifest.get("trust_zone") != "canonical":
        failures.append(f"{label}: trust_zone must be canonical")
    if manifest.get("lifecycle_status") != "active":
        failures.append(f"{label}: lifecycle_status must be active")
    failures.extend(require_non_authorizing(manifest, label))

    roots = manifest.get("local_repo_roots")
    if not isinstance(roots, dict):
        failures.append(f"{label}: local_repo_roots must be a mapping")
        roots = {}

    references = manifest.get("references")
    if not isinstance(references, list) or not references:
        failures.append(f"{label}: references must be a non-empty list")
        references = []

    allowed_postures = set((standard or {}).get("allowed_authority_postures", []))
    allowed_policies = set((standard or {}).get("allowed_failure_policies", []))
    manifest_pairs: set[tuple[str, str]] = set()
    seen_ids: set[str] = set()

    for index, reference in enumerate(references):
        ref_label = f"{label}:references[{index}]"
        if not isinstance(reference, dict):
            failures.append(f"{ref_label}: reference must be a mapping")
            continue
        failures.extend(require_fields(reference, REQUIRED_REFERENCE_FIELDS, ref_label))
        reference_id = reference.get("reference_id")
        if isinstance(reference_id, str):
            if reference_id in seen_ids:
                failures.append(f"{ref_label}: duplicate reference_id {reference_id}")
            seen_ids.add(reference_id)
        target_repo = reference.get("target_repo")
        target_path = reference.get("target_path")
        if not isinstance(target_repo, str) or not target_repo:
            failures.append(f"{ref_label}: target_repo must be a non-empty string")
            continue
        if not isinstance(target_path, str) or not target_path:
            failures.append(f"{ref_label}: target_path must be a non-empty string")
            continue
        manifest_pairs.add((target_repo, target_path))
        if allowed_postures and reference.get("authority_posture") not in allowed_postures:
            failures.append(f"{ref_label}: authority_posture is not allowed")
        if allowed_policies and reference.get("failure_policy") not in allowed_policies:
            failures.append(f"{ref_label}: failure_policy is not allowed")

        repo_root, candidates = resolve_repo_root(target_repo, roots, root=root)
        if repo_root is None:
            if require_local_repos:
                rendered = ", ".join(path.as_posix() for path in candidates) or "<none>"
                failures.append(f"{ref_label}: no local repo root found for {target_repo}: {rendered}")
            continue
        try:
            resolved_target = safe_target_path(repo_root, target_path)
        except CrossRepoReferenceError as exc:
            failures.append(f"{ref_label}: {exc}")
            continue
        if not resolved_target.exists():
            failures.append(f"{ref_label}: missing target path {target_repo}:{target_path}")

    if gate_registry is not None:
        missing_pairs = sorted(gate_registry_refs(gate_registry) - manifest_pairs)
        for repo, target in missing_pairs:
            failures.append(f"{label}: gate trigger registry reference missing from manifest: {repo}:{target}")

    if dependency_map is not None:
        failures.extend(validate_no_upward_child_dependencies(dependency_map))

    return failures


def validate_no_upward_child_dependencies(
    dependency_map: dict[str, Any],
    *,
    label: str = rel(DEPENDENCY_MAP),
) -> list[str]:
    failures: list[str] = []
    artifacts = dependency_map.get("artifacts")
    if not isinstance(artifacts, list):
        return [f"{label}: artifacts must be a list for upward dependency lint"]
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if artifact.get("repo") != "logos-governance-architecture":
            continue
        artifact_id = artifact.get("artifact_id", "<missing>")
        depends_on = artifact.get("depends_on", [])
        if not isinstance(depends_on, list):
            failures.append(f"{label}:{artifact_id}: depends_on must be a list")
            continue
        for dependency in depends_on:
            if isinstance(dependency, str) and dependency.startswith(FORBIDDEN_UPWARD_DEPENDENCY_PREFIXES):
                failures.append(
                    f"{label}:{artifact_id}: depends_on may not point upward to child repo path {dependency}"
                )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--standard", type=Path, default=STANDARD)
    parser.add_argument("--gate-registry", type=Path, default=GATE_TRIGGER_REGISTRY)
    parser.add_argument("--dependency-map", type=Path, default=DEPENDENCY_MAP)
    parser.add_argument("--require-local-repos", action="store_true")
    args = parser.parse_args(argv)

    failures: list[str] = []
    try:
        standard = load_yaml(args.standard)
        manifest = load_yaml(args.manifest)
        gate_registry = load_yaml(args.gate_registry)
        dependency_map = load_yaml(args.dependency_map)
        failures.extend(validate_standard(standard, label=rel(args.standard)))
        failures.extend(
            validate_manifest(
                manifest,
                standard=standard,
                gate_registry=gate_registry,
                dependency_map=dependency_map,
                require_local_repos=args.require_local_repos,
                label=rel(args.manifest),
            )
        )
    except CrossRepoReferenceError as exc:
        failures.append(str(exc))

    if failures:
        print("Cross-repo reference manifest validation failed.")
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print("Cross-repo reference manifest validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
