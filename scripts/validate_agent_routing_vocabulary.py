#!/usr/bin/env python3
"""Fail-closed checks for the non-runtime agent routing vocabulary."""
from __future__ import annotations

import pathlib
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
VOCABULARY_PATH = ROOT / "governance" / "registry" / "agent_routing_vocabulary.yaml"

EXPECTED_WORK_CLASSES = {"W0_mechanical", "W1_bounded_engineering", "W2_specialist_research", "W3_cross_domain_architecture"}
EXPECTED_AUTHORITY_CLASSES = {"A0_observation_only", "A1_candidate_only", "A2_review_preparation", "A3_human_reserved"}
EXPECTED_EFFORT_BANDS = {"E0_minimal", "E1_low", "E2_standard", "E3_high", "E4_maximum"}
EXPECTED_INDEPENDENCE = {"I0_not_required", "I1_independent_adapter", "I2_human_reviewer"}
EXPECTED_SPECIALIST_DOMAINS = {
    "koine_greek",
    "biblical_hebrew_aramaic",
    "textual_criticism_codices",
    "archaeology_history",
    "theology_hermeneutics",
    "ontology_cross_repo_architecture",
}
EXPECTED_ESCALATIONS = {
    "ambiguity",
    "missing_evidence",
    "source_conflict",
    "failed_qualification",
    "authority_pressure",
    "scope_expansion",
    "independence_unavailable",
    "cost_pressure_on_safety_controls",
}


def _load(path: pathlib.Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("vocabulary must be a mapping")
    return data


def _require_exact_keys(data: dict[str, Any], field: str, expected: set[str], failures: list[str]) -> None:
    value = data.get(field)
    if not isinstance(value, dict):
        failures.append(f"{field} must be a mapping")
        return
    actual = set(value)
    if actual != expected:
        failures.append(f"{field} must contain exactly {sorted(expected)}; found {sorted(actual)}")


def validate(path: pathlib.Path = VOCABULARY_PATH) -> list[str]:
    data = _load(path)
    failures: list[str] = []
    for field, expected in {
        "object_type": "agent_routing_vocabulary",
        "trust_zone": "canonical",
        "lifecycle_status": "active",
        "standard_id": "logos_agent_routing_vocabulary_v1",
        "routing_rule": "lowest_total_cost_among_currently_qualified_adapters",
    }.items():
        if data.get(field) != expected:
            failures.append(f"{field} must be {expected!r}")

    authority = data.get("authority")
    expected_authority = {
        "runtime_orchestration_authorized": False,
        "provider_or_model_assignment_authorized": False,
        "ai_may_satisfy_human_or_owner_gates": False,
        "doctrine_or_scripture_authority_authorized": False,
        "source_import_authorized": False,
        "graph_retrieval_vector_truth_authorized": False,
    }
    if not isinstance(authority, dict):
        failures.append("authority must be a mapping")
    else:
        for field, expected in expected_authority.items():
            if authority.get(field) is not expected:
                failures.append(f"authority.{field} must be false")

    _require_exact_keys(data, "work_classes", EXPECTED_WORK_CLASSES, failures)
    _require_exact_keys(data, "authority_classes", EXPECTED_AUTHORITY_CLASSES, failures)
    _require_exact_keys(data, "effort_bands", EXPECTED_EFFORT_BANDS, failures)
    _require_exact_keys(data, "independence_requirements", EXPECTED_INDEPENDENCE, failures)

    authority_classes = data.get("authority_classes", {})
    if isinstance(authority_classes, dict):
        a3 = authority_classes.get("A3_human_reserved")
        if not isinstance(a3, dict) or a3.get("ai_may_satisfy_gate") is not False:
            failures.append("A3_human_reserved must forbid AI gate satisfaction")

    domains = data.get("specialist_domain_requirements")
    if not isinstance(domains, list):
        failures.append("specialist_domain_requirements must be a list")
    else:
        domain_ids = {item.get("domain_id") for item in domains if isinstance(item, dict)}
        if domain_ids != EXPECTED_SPECIALIST_DOMAINS:
            failures.append("specialist_domain_requirements must contain exactly the approved domain set")
        for item in domains:
            if not isinstance(item, dict) or item.get("minimum_qualification") != "domain_fixture_and_source_safe_packet_pass":
                failures.append("every specialist domain requires fixture-backed qualification")
            elif item.get("independence_requirement") != "I1_independent_adapter":
                failures.append("every specialist domain requires independent adapter review")

    if set(data.get("escalation_triggers", [])) != EXPECTED_ESCALATIONS:
        failures.append("escalation_triggers must contain exactly the approved trigger set")

    adapter_rules = data.get("adapter_rules")
    required_adapter_rules = {
        "current_aliases_are_non_authorizing": True,
        "qualification_evidence_required_before_durable_role_assignment": True,
        "alias_expiry_and_requalification_required": True,
        "provider_terms_forbidden_in_durable_role_cards": True,
    }
    if not isinstance(adapter_rules, dict):
        failures.append("adapter_rules must be a mapping")
    else:
        for field, expected in required_adapter_rules.items():
            if adapter_rules.get(field) is not expected:
                failures.append(f"adapter_rules.{field} must be true")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Agent routing vocabulary validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
