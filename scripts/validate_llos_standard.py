#!/usr/bin/env python3
"""Validate LLOS v1 governance, schema, routes, and the DAD no-write boundary."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
STANDARD = ROOT / "governance/LOGOS_LEARNING_LOOP_OPERATING_STANDARD.yaml"
ROUTES = ROOT / "governance/registry/LLOS_ROUTE_REGISTRY.yaml"
SCHEMA = ROOT / "schemas/llos/lesson.v1.schema.json"


def _load_governed_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        text = parts[2]
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping")
    return data


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    standard = _load_governed_yaml(root / STANDARD.relative_to(ROOT))
    routes = _load_governed_yaml(root / ROUTES.relative_to(ROOT))
    schema = json.loads((root / SCHEMA.relative_to(ROOT)).read_text(encoding="utf-8"))

    if standard.get("surface_version") != "1.0.0":
        errors.append("LLOS surface_version must be 1.0.0")
    if standard.get("loop_stages") != [
        "preflight", "candidate_capture", "admission_review", "local_application",
        "validation", "postflight", "effectiveness_review",
    ]:
        errors.append("LLOS loop stages are incomplete or reordered")
    admission = standard.get("admission", {})
    for key in ("candidate_is_authority", "ai_may_admit", "dad_may_admit"):
        if admission.get(key) is not False:
            errors.append(f"admission.{key} must be false")
    if admission.get("human_review_required") is not True:
        errors.append("admission.human_review_required must be true")

    severity = standard.get("severity_policy", {})
    sunset = standard.get("sunset_policy", {})
    if severity.get("allowed") != ["P0", "P1", "P2", "P3"]:
        errors.append("severity allowlist must be P0-P3")
    if severity.get("p0_auto_sunset_allowed") is not False:
        errors.append("P0 lessons must never auto-sunset")
    if severity.get("catastrophic_or_irreversible_auto_sunset_allowed") is not False:
        errors.append("catastrophic or irreversible lessons must never auto-sunset")
    if sunset.get("auto_delete_allowed") is not False:
        errors.append("lesson auto-delete must be disabled")
    attention = standard.get("attention_budget", {})
    if attention.get("selection_basis") != "route_relevance_and_reading_cost":
        errors.append("attention budget must use route relevance and reading cost")
    if attention.get("raw_p0_count_may_exclude_lesson") is not False:
        errors.append("raw P0 count may not exclude a lesson")
    if attention.get("usage_may_demote_p0_or_constitutional") is not False:
        errors.append("usage may not demote P0 or constitutional lessons")

    bridge = standard.get("dad_bridge", {})
    required_false = (
        "write_inside_logos_repo", "deliver_to_logos_inbox",
        "mutate_logos_contract", "mutate_logos_index",
    )
    for key in required_false:
        if bridge.get(key) is not False:
            errors.append(f"dad_bridge.{key} must be false")
    if bridge.get("approval_required_for_every_future_logos_write") is not True:
        errors.append("every future Logos write must require approval")
    if bridge.get("central_write_root") != "DAD_DATA_ROOT":
        errors.append("DAD bridge may write only under DAD_DATA_ROOT")

    communication = standard.get("communication", {})
    required_true = (
        "logos_local_may_write_own_outbox",
        "dad_may_read_approved_logos_outbox",
        "dad_may_write_central_candidate_records",
        "logos_local_may_read_dad_central_candidates",
        "logos_local_pull_required_for_return_path",
        "local_human_review_required_before_adoption",
    )
    for key in required_true:
        if communication.get(key) is not True:
            errors.append(f"communication.{key} must be true")
    for key in (
        "dad_push_to_logos_allowed",
        "dad_direct_logos_inbox_write_allowed",
        "candidate_return_authorizes_local_change",
    ):
        if communication.get(key) is not False:
            errors.append(f"communication.{key} must be false")

    gate = standard.get("gate_policy", {})
    if gate.get("ai_may_satisfy_owner_gate") is not False:
        errors.append("AI may not satisfy owner gates")
    if gate.get("dad_may_satisfy_owner_gate") is not False:
        errors.append("DAD may not satisfy owner gates")

    route_names = set(routes.get("routes", {}))
    schema_routes = set(schema["properties"]["route"]["enum"])
    if route_names != schema_routes:
        errors.append("schema routes must exactly match LLOS route registry")
    if set(schema.get("required", [])) != set(admission.get("required_fields", [])):
        errors.append("schema required fields must exactly match admission fields")
    if schema["properties"]["contains_raw_source_payload"].get("const") is not False:
        errors.append("lesson schema must reject raw source payloads")
    if schema["properties"]["contains_theology_claim"].get("const") is not False:
        errors.append("lesson schema must reject theology claims")
    if schema["properties"]["human_review_required"].get("const") is not True:
        errors.append("lesson schema must require human review")
    return errors


def validate_lesson_record(record: dict[str, Any], root: Path = ROOT) -> list[str]:
    standard = _load_governed_yaml(root / STANDARD.relative_to(ROOT))
    schema = json.loads((root / SCHEMA.relative_to(ROOT)).read_text(encoding="utf-8"))
    errors: list[str] = []
    missing = sorted(set(schema["required"]) - set(record))
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))
        return errors
    routes = _load_governed_yaml(root / ROUTES.relative_to(ROOT))["routes"]
    route = record.get("route")
    category = record.get("category")
    if route not in routes or category not in routes.get(route, {}).get("categories", []):
        errors.append("route/category is not registered")
    if record.get("contains_raw_source_payload") is not False:
        errors.append("raw source payload is forbidden")
    if record.get("contains_theology_claim") is not False:
        errors.append("theology claim is forbidden")
    if record.get("human_review_required") is not True:
        errors.append("human review must be required")
    if record.get("changed_paths") and not str(record.get("enforcement_ref") or "").strip():
        errors.append("changed paths require an enforcement reference")
    protected = (
        record.get("severity") == "P0"
        or record.get("constitutional") is True
        or record.get("irreversibility") == "catastrophic"
    )
    if protected and record.get("sunset_eligible") is not False:
        errors.append("P0, constitutional, or catastrophic lessons cannot be sunset eligible")
    if protected and record.get("sunset_review_due") not in (None, ""):
        errors.append("P0, constitutional, or catastrophic lessons cannot receive a sunset date")
    if record.get("authority_ceiling") not in {"candidate_only", "workflow_only", "validation_only"}:
        errors.append("authority ceiling is invalid")
    if standard["admission"]["candidate_is_authority"] is not False:
        errors.append("standard authority boundary is invalid")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("LLOS v1 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
