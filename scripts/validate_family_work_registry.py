#!/usr/bin/env python3
"""Validate family work claims, leases, lifecycle state, and deterministic overlap."""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance" / "registry" / "FAMILY_WORK_REGISTRY.yaml"
SCHEMA = ROOT / "schemas" / "family-work-claim.schema.json"

STATUSES = {
    "proposed", "ready", "active", "blocked", "awaiting_review", "merged",
    "superseded", "abandoned", "archived",
}
ACTIVE_STATUSES = {"proposed", "ready", "active", "blocked", "awaiting_review"}
BOARD_BY_STATUS = {
    "proposed": "backlog", "ready": "ready", "active": "in_progress",
    "blocked": "blocked", "awaiting_review": "review", "merged": "done",
    "superseded": "archived", "abandoned": "archived", "archived": "archived",
}
CLAIM_MODES = {"exclusive_write", "additive_write", "read_only"}
HIGH_RISK_TAGS = {
    "governance_authority", "scripture_canonical_data", "chunk_output",
    "reviewed_gold", "route_or_evaluator", "textual_critical_decision",
    "source_import", "doctrine_lineage", "graph_retrieval_vector_truth",
    "theology_authority",
}
OVERLAP_DECISIONS = {
    "continue_existing", "extend_existing", "supersede_existing", "split_paths",
    "allow_parallel_with_recorded_boundaries", "abandon_after_preservation",
}
REQUIRED_TOP = {
    "object_type", "trust_zone", "lifecycle_status", "provenance_note",
    "reason_for_inclusion", "schema_version", "registry_id", "owner",
    "standard_ref", "claim_schema_ref", "generated_audit_ref",
    "generated_audit_machine_ref", "enforcement",
    "overlap_resolutions", "work_items",
}
REQUIRED_ITEM = {
    "work_id", "repo", "task_id", "objective_key", "objective", "status",
    "board_column", "claim_mode", "claimed_paths", "semantic_tags",
    "roadmap_refs", "branch", "issue_url", "pr_url", "owner", "agent",
    "started_at", "heartbeat_at", "stale_after_days", "authority_ceiling",
    "dependencies", "related_work_ids", "overlap_resolution_ids",
    "completion_evidence",
}


class RegistryError(ValueError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RegistryError(f"{path}: unreadable YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryError(f"{path}: expected YAML mapping")
    return data


def normalize_path(value: str) -> str:
    path = value.replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    return str(PurePosixPath(path)) if path else path


def _literal_prefix(pattern: str) -> str:
    normalized = normalize_path(pattern)
    wildcard = min(
        [normalized.find(char) for char in "*[?" if char in normalized] or [len(normalized)]
    )
    return normalized[:wildcard].rstrip("/")


def paths_overlap(left: str, right: str) -> bool:
    """Conservatively detect overlap between two repo-relative paths/globs."""
    a, b = normalize_path(left), normalize_path(right)
    if a in {"**", "*"} or b in {"**", "*"}:
        return True
    a_glob = any(char in a for char in "*[?")
    b_glob = any(char in b for char in "*[?")
    if not a_glob and not b_glob:
        return a == b or a.startswith(b.rstrip("/") + "/") or b.startswith(a.rstrip("/") + "/")
    if not a_glob and fnmatch.fnmatchcase(a, b):
        return True
    if not b_glob and fnmatch.fnmatchcase(b, a):
        return True
    a_prefix, b_prefix = _literal_prefix(a), _literal_prefix(b)
    if not a_prefix or not b_prefix:
        return True
    return (
        a_prefix == b_prefix
        or a_prefix.startswith(b_prefix.rstrip("/") + "/")
        or b_prefix.startswith(a_prefix.rstrip("/") + "/")
    )


def _nonempty_strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def _parse_time(value: Any, label: str, failures: list[str]) -> datetime | None:
    if not isinstance(value, str):
        failures.append(f"{label} must be an ISO-8601 string")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        failures.append(f"{label} must be a valid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        failures.append(f"{label} must include a timezone")
        return None
    return parsed


def _resolved_together(left: dict[str, Any], right: dict[str, Any], valid_ids: set[str]) -> bool:
    shared = set(left.get("overlap_resolution_ids", [])) & set(right.get("overlap_resolution_ids", []))
    return bool(shared & valid_ids)


def validate_registry(data: dict[str, Any], *, as_of: datetime | None = None) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    missing = sorted(REQUIRED_TOP - set(data))
    if missing:
        return [f"registry missing required fields: {', '.join(missing)}"], warnings
    if data.get("object_type") != "family_work_registry":
        failures.append("object_type must be family_work_registry")
    if data.get("trust_zone") != "canonical" or data.get("lifecycle_status") != "active":
        failures.append("registry must be canonical and active")
    if data.get("standard_ref") != "governance/FAMILY_WORK_COORDINATION_STANDARD.yaml":
        failures.append("standard_ref must point to the family coordination standard")
    if data.get("claim_schema_ref") != "schemas/family-work-claim.schema.json":
        failures.append("claim_schema_ref must point to the claim schema")
    if data.get("generated_audit_machine_ref") != "reports/FAMILY_WORKTREE_AUDIT_2026-07-10.yaml":
        failures.append("generated_audit_machine_ref must point to the machine-readable audit")
    for key in ("standard_ref", "claim_schema_ref", "generated_audit_ref", "generated_audit_machine_ref"):
        value = data.get(key)
        if isinstance(value, str) and not (ROOT / value).is_file():
            failures.append(f"{key} points to missing file {value}")

    resolutions = data.get("overlap_resolutions")
    if not isinstance(resolutions, list):
        failures.append("overlap_resolutions must be a list")
        resolutions = []
    resolution_ids: set[str] = set()
    for index, resolution in enumerate(resolutions):
        label = f"overlap_resolutions[{index}]"
        if not isinstance(resolution, dict):
            failures.append(f"{label} must be a mapping")
            continue
        required = {"resolution_id", "owner_decision_ref", "affected_work_ids", "decision", "decided_at", "rationale"}
        missing_resolution = sorted(required - set(resolution))
        if missing_resolution:
            failures.append(f"{label} missing fields: {', '.join(missing_resolution)}")
            continue
        resolution_id = resolution["resolution_id"]
        if not isinstance(resolution_id, str) or not resolution_id:
            failures.append(f"{label}.resolution_id must be non-empty")
        elif resolution_id in resolution_ids:
            failures.append(f"duplicate overlap resolution {resolution_id}")
        else:
            resolution_ids.add(resolution_id)
        if resolution.get("decision") not in OVERLAP_DECISIONS:
            failures.append(f"{label}.decision is not controlled")
        if not _nonempty_strings(resolution.get("affected_work_ids")) or len(resolution["affected_work_ids"]) < 2:
            failures.append(f"{label}.affected_work_ids must name at least two work IDs")
        _parse_time(resolution.get("decided_at"), f"{label}.decided_at", failures)
        if not isinstance(resolution.get("rationale"), str) or len(resolution["rationale"].strip()) < 20:
            failures.append(f"{label}.rationale must be substantive")

    items = data.get("work_items")
    if not isinstance(items, list) or not items:
        return failures + ["work_items must be a non-empty list"], warnings

    work_ids: set[str] = set()
    task_keys: set[tuple[str, str]] = set()
    parsed: list[dict[str, Any]] = []
    now = as_of or datetime.now(timezone.utc)
    for index, item in enumerate(items):
        label = f"work_items[{index}]"
        if not isinstance(item, dict):
            failures.append(f"{label} must be a mapping")
            continue
        missing_item = sorted(REQUIRED_ITEM - set(item))
        if missing_item:
            failures.append(f"{label} missing fields: {', '.join(missing_item)}")
            continue
        work_id = item["work_id"]
        if not isinstance(work_id, str) or not work_id.startswith("WORK-"):
            failures.append(f"{label}.work_id must start with WORK-")
        elif work_id in work_ids:
            failures.append(f"duplicate work_id {work_id}")
        else:
            work_ids.add(work_id)
        task_key = (str(item["repo"]), str(item["task_id"]))
        if item["status"] in ACTIVE_STATUSES and task_key in task_keys:
            failures.append(f"duplicate active task identity {task_key[0]}:{task_key[1]}")
        elif item["status"] in ACTIVE_STATUSES:
            task_keys.add(task_key)
        if item["status"] not in STATUSES:
            failures.append(f"{label}.status is not controlled")
        elif item["board_column"] != BOARD_BY_STATUS[item["status"]]:
            failures.append(f"{label}.board_column does not match status {item['status']}")
        if item["claim_mode"] not in CLAIM_MODES:
            failures.append(f"{label}.claim_mode is not controlled")
        for key in ("claimed_paths", "semantic_tags", "roadmap_refs", "dependencies", "related_work_ids", "overlap_resolution_ids", "completion_evidence"):
            if not _nonempty_strings(item[key]) and item[key] != []:
                failures.append(f"{label}.{key} must be a string list")
        if not item["claimed_paths"] or not item["semantic_tags"]:
            failures.append(f"{label} requires claimed_paths and semantic_tags")
        if len(set(map(normalize_path, item["claimed_paths"]))) != len(item["claimed_paths"]):
            failures.append(f"{label}.claimed_paths contains duplicates")
        if not isinstance(item["stale_after_days"], int) or item["stale_after_days"] < 1:
            failures.append(f"{label}.stale_after_days must be a positive integer")
        started = _parse_time(item["started_at"], f"{label}.started_at", failures)
        heartbeat = _parse_time(item["heartbeat_at"], f"{label}.heartbeat_at", failures)
        if started and heartbeat and heartbeat < started:
            failures.append(f"{label}.heartbeat_at cannot precede started_at")
        if heartbeat and item["status"] in {"active", "blocked", "awaiting_review"}:
            age_days = (now - heartbeat.astimezone(timezone.utc)).total_seconds() / 86400
            if age_days > item["stale_after_days"]:
                warnings.append(f"{work_id} lease is stale by {age_days - item['stale_after_days']:.1f} days; owner reconciliation required")
        if item["status"] not in ACTIVE_STATUSES and not item["completion_evidence"]:
            failures.append(f"{label} terminal status requires completion_evidence")
        unknown_resolutions = set(item["overlap_resolution_ids"]) - resolution_ids
        if unknown_resolutions:
            failures.append(f"{label} references unknown overlap resolutions: {', '.join(sorted(unknown_resolutions))}")
        parsed.append(item)

    for item in parsed:
        for related in item["related_work_ids"] + item["dependencies"]:
            if related not in work_ids:
                failures.append(f"{item['work_id']} references unknown work ID {related}")
    item_by_id = {item["work_id"]: item for item in parsed}
    for resolution in resolutions:
        if not isinstance(resolution, dict) or "resolution_id" not in resolution:
            continue
        resolution_id = resolution["resolution_id"]
        for affected in resolution.get("affected_work_ids", []):
            if affected not in item_by_id:
                failures.append(f"{resolution_id} references unknown affected work ID {affected}")
            elif resolution_id not in item_by_id[affected]["overlap_resolution_ids"]:
                failures.append(f"{affected} must reference affecting resolution {resolution_id}")

    active = [item for item in parsed if item["status"] in ACTIVE_STATUSES]
    for index, left in enumerate(active):
        for right in active[index + 1:]:
            if left["repo"] != right["repo"] or _resolved_together(left, right, resolution_ids):
                continue
            shared_roadmap = set(left["roadmap_refs"]) & set(right["roadmap_refs"])
            if shared_roadmap:
                failures.append(f"{left['work_id']} and {right['work_id']} share active roadmap target(s) {sorted(shared_roadmap)} without an owner resolution")
            overlaps = [
                f"{a} <-> {b}" for a in left["claimed_paths"] for b in right["claimed_paths"]
                if paths_overlap(a, b)
            ]
            if overlaps and "exclusive_write" in {left["claim_mode"], right["claim_mode"]}:
                failures.append(f"{left['work_id']} and {right['work_id']} have unresolved exclusive path overlap: {overlaps[0]}")
            elif overlaps and left["claim_mode"] != "read_only" and right["claim_mode"] != "read_only":
                failures.append(f"{left['work_id']} and {right['work_id']} have unresolved additive path overlap: {overlaps[0]}")
            risky = set(left["semantic_tags"]) & set(right["semantic_tags"]) & HIGH_RISK_TAGS
            if risky:
                failures.append(f"{left['work_id']} and {right['work_id']} share high-risk tag(s) {sorted(risky)} without an owner resolution")
    return failures, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-stale", action="store_true")
    parser.add_argument("--require-branch", help="Require exactly one active claim for this PR branch.")
    args = parser.parse_args(argv)
    try:
        data = load_yaml(args.registry)
        failures, warnings = validate_registry(data)
    except RegistryError as exc:
        failures, warnings = [str(exc)], []
    if args.fail_on_stale:
        failures.extend(warnings)
    if args.require_branch:
        branch_matches = [
            item for item in data.get("work_items", [])
            if item.get("branch") == args.require_branch and item.get("status") in ACTIVE_STATUSES
        ] if "data" in locals() else []
        if len(branch_matches) != 1:
            failures.append(
                f"branch {args.require_branch} requires exactly one active governed work claim; found {len(branch_matches)}"
            )
    if args.json:
        print(json.dumps({"failures": failures, "warnings": warnings}, indent=2))
    else:
        for warning in warnings:
            print(f"WARN {warning}")
        if failures:
            print("FAMILY WORK REGISTRY FAILED:", file=sys.stderr)
            print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        else:
            print("Family work registry validation passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
