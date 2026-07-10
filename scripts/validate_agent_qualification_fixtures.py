#!/usr/bin/env python3
"""Fail-closed validation for source-safe adapter qualification fixtures."""
from __future__ import annotations

import pathlib
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "governance" / "registry" / "agent_qualification_fixture_manifest.yaml"
REGISTER_PATH = ROOT / "governance" / "registry" / "current_adapter_qualification_register.yaml"

EXPECTED_FIXTURES = {
    "FQ-01-deterministic-import",
    "FQ-02-validator-mutant",
    "FQ-03-authority-boundary",
    "FQ-04-koine-context",
    "FQ-05-hebrew-aramaic-context",
    "FQ-06-textual-criticism",
    "FQ-07-archaeology-history",
    "FQ-08-doctrine-genealogy",
    "FQ-09-lens-smuggling",
    "FQ-10-cross-repo-release",
    "FQ-11-independent-red-team",
    "FQ-12-economy-escalation",
}
EXPECTED_ADAPTERS = {
    "alias-sol",
    "alias-terra",
    "alias-luna",
    "effort-low",
    "effort-high",
    "effort-ultra",
}


def _load(path: pathlib.Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must be a mapping")
    return data


def validate(
    manifest_path: pathlib.Path = MANIFEST_PATH,
    register_path: pathlib.Path = REGISTER_PATH,
) -> list[str]:
    manifest = _load(manifest_path)
    register = _load(register_path)
    failures: list[str] = []

    if manifest.get("object_type") != "agent_qualification_fixture_manifest":
        failures.append("fixture manifest has the wrong object_type")
    if manifest.get("source_safe_only") is not True:
        failures.append("fixture manifest must be source_safe_only")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list):
        failures.append("fixtures must be a list")
    else:
        fixture_ids = {item.get("fixture_id") for item in fixtures if isinstance(item, dict)}
        if fixture_ids != EXPECTED_FIXTURES or len(fixtures) != len(EXPECTED_FIXTURES):
            failures.append("fixture manifest must contain exactly the fixed qualification pack")
        for fixture in fixtures:
            if not isinstance(fixture, dict) or fixture.get("source_safe") is not True:
                failures.append("every fixture must be source-safe")

    if register.get("object_type") != "current_adapter_qualification_register":
        failures.append("qualification register has the wrong object_type")
    if register.get("qualification_result_expiry_days") != 30:
        failures.append("qualification_result_expiry_days must be 30")
    records = register.get("adapter_records")
    if not isinstance(records, list):
        failures.append("adapter_records must be a list")
    else:
        adapter_ids = {item.get("adapter_id") for item in records if isinstance(item, dict)}
        if adapter_ids != EXPECTED_ADAPTERS or len(records) != len(EXPECTED_ADAPTERS):
            failures.append("register must contain exactly the current aliases and effort adapters")
        for record in records:
            if not isinstance(record, dict):
                failures.append("adapter record must be a mapping")
                continue
            adapter_id = record.get("adapter_id", "<unknown>")
            expected = {
                "runtime_adapter_available": False,
                "qualification_status": "not_run",
                "execution_blocker": "no_callable_adapter_runtime_in_current_governance_workspace",
                "required_fixture_ids": [],
                "completed_fixture_ids": [],
                "role_assignment_authorized": False,
                "eligible_work_classes": [],
                "eligible_specialist_domains": [],
            }
            for field, value in expected.items():
                if record.get(field) != value:
                    failures.append(f"{adapter_id}.{field} must remain {value!r} without a captured run")
            for metric in ("total_cost_usd", "elapsed_seconds", "defect_count", "escalation_quality", "qualification_expires_at"):
                if record.get(metric) is not None:
                    failures.append(f"{adapter_id}.{metric} must be null until a real fixture run is captured")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Agent qualification fixture validation passed; all current adapters remain unqualified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
