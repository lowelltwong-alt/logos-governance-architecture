#!/usr/bin/env python3
"""Validate that every scoped legacy content file has one future ownership disposition."""
from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "governance" / "LEGACY_CONTENT_OWNERSHIP_INVENTORY.yaml"
ALLOWED_DISPOSITIONS = {
    "migrate_to_scripture",
    "migrate_to_boundary",
    "migrate_to_doctrine_genealogy",
    "retain_as_governance_architecture",
    "reference_only",
    "compatibility_redirect",
}
TARGET_BY_DISPOSITION = {
    "migrate_to_scripture": "logos-scripture-graph",
    "migrate_to_boundary": "logos-boundary-literature",
    "migrate_to_doctrine_genealogy": "logos-doctrine-genealogy",
    "retain_as_governance_architecture": "logos-governance-architecture",
    "reference_only": "logos-governance-architecture",
    "compatibility_redirect": "logos-governance-architecture",
}
REQUIRED_TOP_LEVEL = {
    "object_type", "trust_zone", "lifecycle_status", "provenance_note", "reason_for_inclusion",
    "schema_version", "inventory_id", "owner", "owner_authorization_id", "scope_status",
    "content_move_authorized", "content_delete_authorized", "new_doctrine_record_authorized",
    "source_import_authorized", "scripture_or_chunk_output_authorized", "graph_retrieval_vector_truth_authorized",
    "source_link_preservation_required", "allowed_dispositions", "scope_roots", "entries",
    "pre_migration_stop_rules", "validators",
}
REQUIRED_ENTRY = {"entry_id", "path_globs", "disposition", "target_repo", "reason", "provenance_refs"}


class InventoryError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            parts = text.split("---\n", 2)
            if len(parts) == 3:
                text = parts[1] + "\n" + parts[2]
        data = yaml.safe_load(text)
    except (OSError, yaml.YAMLError) as exc:
        raise InventoryError(f"{path}: unreadable YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise InventoryError(f"{path}: expected YAML mapping")
    return data


def _require_nonempty_strings(value: Any, label: str, failures: list[str]) -> None:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item.strip() for item in value):
        failures.append(f"{label} must be a non-empty string list")


def validate_inventory(root: Path, data: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - set(data))
    if missing:
        return [f"inventory missing required fields: {', '.join(missing)}"]
    if data["object_type"] != "legacy_content_ownership_inventory":
        failures.append("object_type must be legacy_content_ownership_inventory")
    if data["trust_zone"] != "canonical" or data["lifecycle_status"] != "active":
        failures.append("inventory must be canonical and active")
    if data["scope_status"] != "inventory_only":
        failures.append("scope_status must be inventory_only")
    for key in (
        "content_move_authorized", "content_delete_authorized", "new_doctrine_record_authorized",
        "source_import_authorized", "scripture_or_chunk_output_authorized", "graph_retrieval_vector_truth_authorized",
    ):
        if data.get(key) is not False:
            failures.append(f"{key} must be false")
    if data.get("source_link_preservation_required") is not True:
        failures.append("source_link_preservation_required must be true")
    if set(data["allowed_dispositions"] or []) != ALLOWED_DISPOSITIONS:
        failures.append("allowed_dispositions must match the controlled set")

    roots = data["scope_roots"]
    _require_nonempty_strings(roots, "scope_roots", failures)
    entries = data["entries"]
    if not isinstance(entries, list) or not entries:
        return failures + ["entries must be a non-empty list"]

    entry_ids: set[str] = set()
    parsed_entries: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        label = f"entries[{index}]"
        if not isinstance(entry, dict):
            failures.append(f"{label} must be a mapping")
            continue
        missing_entry = sorted(REQUIRED_ENTRY - set(entry))
        if missing_entry:
            failures.append(f"{label} missing required fields: {', '.join(missing_entry)}")
            continue
        entry_id = entry["entry_id"]
        if not isinstance(entry_id, str) or not entry_id:
            failures.append(f"{label}.entry_id must be a non-empty string")
        elif entry_id in entry_ids:
            failures.append(f"{label}: duplicate entry_id {entry_id}")
        else:
            entry_ids.add(entry_id)
        _require_nonempty_strings(entry["path_globs"], f"{label}.path_globs", failures)
        _require_nonempty_strings(entry["provenance_refs"], f"{label}.provenance_refs", failures)
        disposition = entry["disposition"]
        if disposition not in ALLOWED_DISPOSITIONS:
            failures.append(f"{label}.disposition is not allowed")
        elif entry["target_repo"] != TARGET_BY_DISPOSITION[disposition]:
            failures.append(f"{label}.target_repo does not match disposition {disposition}")
        if not isinstance(entry["reason"], str) or len(entry["reason"].strip()) < 20:
            failures.append(f"{label}.reason must be substantive")
        parsed_entries.append(entry)

    all_files: list[str] = []
    for root_path in roots if isinstance(roots, list) else []:
        absolute = root / root_path
        if not absolute.is_dir():
            failures.append(f"scope root missing: {root_path}")
            continue
        all_files.extend(path.relative_to(root).as_posix() for path in absolute.rglob("*") if path.is_file())

    matched_by_entry = {entry.get("entry_id", "<invalid>"): 0 for entry in parsed_entries}
    for path in sorted(all_files):
        matches = [
            entry for entry in parsed_entries
            if any(fnmatch.fnmatchcase(path, pattern) for pattern in entry.get("path_globs", []))
        ]
        if len(matches) != 1:
            failures.append(f"{path}: expected exactly one ownership disposition, found {len(matches)}")
        else:
            matched_by_entry[matches[0]["entry_id"]] += 1
    for entry_id, count in matched_by_entry.items():
        if count == 0:
            failures.append(f"{entry_id}: path_globs match no scoped files")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=INVENTORY)
    args = parser.parse_args(argv)
    try:
        failures = validate_inventory(ROOT, _load(args.inventory))
    except InventoryError as exc:
        print(f"LEGACY CONTENT OWNERSHIP INVENTORY FAILED: {exc}", file=sys.stderr)
        return 1
    if failures:
        print("LEGACY CONTENT OWNERSHIP INVENTORY FAILED:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Legacy content ownership inventory validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
