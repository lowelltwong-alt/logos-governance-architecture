#!/usr/bin/env python3
"""Validate the Fable feedback trace matrix.

The matrix is an audit surface only. It records whether Fable feedback has been
implemented, planned, deferred, rejected, or routed to an owner gate. It does not
authorize theology, doctrine data, source imports, Scripture/chunk output, or
graph/retrieval/vector truth.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "roadmap" / "fable-kernels" / "FABLE_FEEDBACK_TRACE_MATRIX.yaml"

REQUIRED_TOP_LEVEL = {
    "object_type",
    "trust_zone",
    "lifecycle_status",
    "provenance_note",
    "reason_for_inclusion",
    "schema_version",
    "matrix_id",
    "owner",
    "source_repo",
    "scope_note",
    "matrix_authority",
    "allowed_dispositions",
    "allowed_risk_categories",
    "source_documents",
    "coverage_groups",
    "entries",
}

REQUIRED_AUTHORITY_FLAGS_FALSE = {
    "authorizes_scripture_output_change",
    "authorizes_chunk_output_change",
    "authorizes_doctrine_data_records",
    "authorizes_source_import",
    "authorizes_reviewed_lineage_promotion",
    "authorizes_graph_retrieval_vector_truth",
    "authorizes_theology_authority",
}

EXPECTED_DISPOSITIONS = {
    "implemented",
    "partially_implemented",
    "planned",
    "deferred_with_reason",
    "rejected_with_reason",
    "needs_owner_decision",
}

CANONICAL_MATRIX_ID = "logos_fable_feedback_trace_matrix"
REQUIRED_CANONICAL_SOURCE_IDS = {
    "owner-master-brief",
    "post-wave2-gap-audit",
}
REQUIRED_CANONICAL_GROUP_IDS = {
    "owner-master-brief-coverage",
    "post-wave2-gap-coverage",
}
REQUIRED_CANONICAL_ENTRY_IDS = {
    *(f"FABLE-REQ-{index:03d}" for index in range(1, 15)),
    *(f"FABLE-POST-{index:03d}" for index in range(1, 16)),
}

REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "title",
    "repo_path",
}

REQUIRED_GROUP_FIELDS = {
    "group_id",
    "source_id",
    "source_section",
    "coverage_entry_ids",
}

REQUIRED_ENTRY_FIELDS = {
    "id",
    "source_group",
    "source_item_ref",
    "feedback_summary",
    "risk_category",
    "affected_repos",
    "disposition",
    "disposition_reason",
    "evidence_refs",
    "next_action",
    "owner_decision_status",
    "target_queue",
    "blocks_work",
    "non_authorizations",
}

PLANNED_DISPOSITIONS = {
    "planned",
    "partially_implemented",
    "needs_owner_decision",
}


class FableFeedbackTraceError(ValueError):
    """Raised when the Fable feedback trace matrix is invalid."""


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
        raise FableFeedbackTraceError(f"{rel(path)}: unreadable YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise FableFeedbackTraceError(f"{rel(path)}: expected YAML mapping")
    return data


def require_fields(data: dict[str, Any], required: set[str], label: str) -> list[str]:
    missing = sorted(required - set(data))
    return [f"{label}: missing required field {field}" for field in missing]


def require_string(value: Any, label: str) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f"{label} must be a non-empty string"]
    return []


def require_string_list(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        return [f"{label} must be a {'possibly empty ' if allow_empty else ''}list"]
    bad_items = [item for item in value if not isinstance(item, str) or not item.strip()]
    if bad_items:
        return [f"{label} must contain only non-empty strings"]
    return []


def validate_matrix(data: dict[str, Any], *, label: str = rel(MATRIX)) -> list[str]:
    failures: list[str] = []
    failures.extend(require_fields(data, REQUIRED_TOP_LEVEL, label))
    if failures:
        return failures

    if data.get("object_type") != "fable_feedback_trace_matrix":
        failures.append(f"{label}: object_type must be fable_feedback_trace_matrix")
    if data.get("trust_zone") != "canonical":
        failures.append(f"{label}: trust_zone must be canonical")
    if data.get("lifecycle_status") != "active":
        failures.append(f"{label}: lifecycle_status must be active")

    authority = data.get("matrix_authority")
    if not isinstance(authority, dict):
        failures.append(f"{label}: matrix_authority must be a mapping")
    else:
        if authority.get("records_feedback_disposition") is not True:
            failures.append(f"{label}: matrix_authority.records_feedback_disposition must be true")
        for field in REQUIRED_AUTHORITY_FLAGS_FALSE:
            if authority.get(field) is not False:
                failures.append(f"{label}: matrix_authority.{field} must be false")

    allowed_dispositions = data.get("allowed_dispositions")
    if set(allowed_dispositions or []) != EXPECTED_DISPOSITIONS:
        failures.append(f"{label}: allowed_dispositions must match {sorted(EXPECTED_DISPOSITIONS)}")

    allowed_risk_categories = data.get("allowed_risk_categories")
    failures.extend(require_string_list(allowed_risk_categories, f"{label}: allowed_risk_categories"))
    risk_categories = set(allowed_risk_categories or [])

    sources = data.get("source_documents")
    if not isinstance(sources, list) or not sources:
        failures.append(f"{label}: source_documents must be a non-empty list")
        sources = []
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        source_label = f"{label}:source_documents[{index}]"
        if not isinstance(source, dict):
            failures.append(f"{source_label}: source must be a mapping")
            continue
        failures.extend(require_fields(source, REQUIRED_SOURCE_FIELDS, source_label))
        source_id = source.get("source_id")
        failures.extend(require_string(source_id, f"{source_label}.source_id"))
        if isinstance(source_id, str):
            if source_id in source_ids:
                failures.append(f"{source_label}: duplicate source_id {source_id}")
            source_ids.add(source_id)

    groups = data.get("coverage_groups")
    if not isinstance(groups, list) or not groups:
        failures.append(f"{label}: coverage_groups must be a non-empty list")
        groups = []
    group_ids: set[str] = set()
    covered_entry_ids: set[str] = set()
    for index, group in enumerate(groups):
        group_label = f"{label}:coverage_groups[{index}]"
        if not isinstance(group, dict):
            failures.append(f"{group_label}: group must be a mapping")
            continue
        failures.extend(require_fields(group, REQUIRED_GROUP_FIELDS, group_label))
        group_id = group.get("group_id")
        failures.extend(require_string(group_id, f"{group_label}.group_id"))
        if isinstance(group_id, str):
            if group_id in group_ids:
                failures.append(f"{group_label}: duplicate group_id {group_id}")
            group_ids.add(group_id)
        source_id = group.get("source_id")
        if isinstance(source_id, str) and source_id not in source_ids:
            failures.append(f"{group_label}: unknown source_id {source_id}")
        coverage_ids = group.get("coverage_entry_ids")
        failures.extend(require_string_list(coverage_ids, f"{group_label}.coverage_entry_ids"))
        if isinstance(coverage_ids, list):
            covered_entry_ids.update(item for item in coverage_ids if isinstance(item, str))

    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        failures.append(f"{label}: entries must be a non-empty list")
        entries = []
    entry_ids: set[str] = set()
    for index, entry in enumerate(entries):
        entry_label = f"{label}:entries[{index}]"
        if not isinstance(entry, dict):
            failures.append(f"{entry_label}: entry must be a mapping")
            continue
        failures.extend(require_fields(entry, REQUIRED_ENTRY_FIELDS, entry_label))
        entry_id = entry.get("id")
        failures.extend(require_string(entry_id, f"{entry_label}.id"))
        if isinstance(entry_id, str):
            if entry_id in entry_ids:
                failures.append(f"{entry_label}: duplicate id {entry_id}")
            entry_ids.add(entry_id)
        source_group = entry.get("source_group")
        if isinstance(source_group, str) and source_group not in group_ids:
            failures.append(f"{entry_label}: unknown source_group {source_group}")
        risk_category = entry.get("risk_category")
        if isinstance(risk_category, str) and risk_category not in risk_categories:
            failures.append(f"{entry_label}: unknown risk_category {risk_category}")
        disposition = entry.get("disposition")
        if disposition not in EXPECTED_DISPOSITIONS:
            failures.append(f"{entry_label}: disposition is not allowed")
        failures.extend(require_string_list(entry.get("affected_repos"), f"{entry_label}.affected_repos"))
        failures.extend(require_string_list(entry.get("evidence_refs"), f"{entry_label}.evidence_refs"))
        failures.extend(require_string_list(entry.get("non_authorizations"), f"{entry_label}.non_authorizations"))
        failures.extend(require_string(entry.get("disposition_reason"), f"{entry_label}.disposition_reason"))
        failures.extend(require_string(entry.get("next_action"), f"{entry_label}.next_action"))
        if not isinstance(entry.get("blocks_work"), bool):
            failures.append(f"{entry_label}.blocks_work must be boolean")

        evidence_refs = entry.get("evidence_refs")
        if disposition == "implemented" and isinstance(evidence_refs, list):
            if any(str(item).lower() in {"tbd", "none", "n/a"} for item in evidence_refs):
                failures.append(f"{entry_label}: implemented entries must cite concrete evidence")
        if disposition in PLANNED_DISPOSITIONS:
            target_queue = entry.get("target_queue")
            if not isinstance(target_queue, str) or not target_queue.strip() or target_queue == "none":
                failures.append(f"{entry_label}: {disposition} entries must name a target_queue")
        if disposition in {"deferred_with_reason", "rejected_with_reason"}:
            reason = entry.get("disposition_reason")
            if not isinstance(reason, str) or len(reason.strip()) < 20:
                failures.append(f"{entry_label}: deferred/rejected entries must carry a substantive reason")
        if disposition == "needs_owner_decision":
            owner_status = entry.get("owner_decision_status")
            if not isinstance(owner_status, str) or "required" not in owner_status:
                failures.append(f"{entry_label}: needs_owner_decision entries must say owner decision is required")

    if data.get("matrix_id") == CANONICAL_MATRIX_ID:
        missing_sources = sorted(REQUIRED_CANONICAL_SOURCE_IDS - source_ids)
        missing_groups = sorted(REQUIRED_CANONICAL_GROUP_IDS - group_ids)
        missing_required_entries = sorted(REQUIRED_CANONICAL_ENTRY_IDS - entry_ids)
        if missing_sources:
            failures.append(f"{label}: required canonical sources missing {', '.join(missing_sources)}")
        if missing_groups:
            failures.append(f"{label}: required canonical coverage groups missing {', '.join(missing_groups)}")
        if missing_required_entries:
            failures.append(
                f"{label}: required owner/post-audit entries missing {', '.join(missing_required_entries)}"
            )

    missing_entries = sorted(covered_entry_ids - entry_ids)
    extra_entries = sorted(entry_ids - covered_entry_ids)
    if missing_entries:
        failures.append(f"{label}: coverage groups reference missing entries {', '.join(missing_entries)}")
    if extra_entries:
        failures.append(f"{label}: entries are not referenced by coverage groups {', '.join(extra_entries)}")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=MATRIX)
    args = parser.parse_args(argv)

    try:
        failures = validate_matrix(load_yaml(args.matrix), label=rel(args.matrix))
    except FableFeedbackTraceError as exc:
        failures = [str(exc)]

    if failures:
        print("Fable feedback trace matrix validation failed.")
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print("Fable feedback trace matrix validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
