#!/usr/bin/env python3
"""Validate boundary-originated governance stop rules."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance" / "LOGOS_REPO_REGISTRY.yaml"

EXPECTED_WARNING = """WARNING: Boundary-layer request conflicts with higher-authority governance.

The requested boundary-layer task appears to require changing or bypassing governance-layer policy, canonical Scripture authority, repository-link contracts, routing policy, trust hierarchy, or canonical scope.

Governance is binding authority, not an obstacle to optimize around.

Do not automate, route, or implement this change from the boundary layer. A human maintainer must review the conflict directly in the higher-authority repository.

Owner-reserved authorization required: only Lowell Wong, as project owner, may authorize a boundary-originated request to change higher-authority governance, canonical Scripture authority, repository-link contracts, canonical scope, trust hierarchy, or cross-repo policy. Contributor consensus, contributor volume, automated recommendation, agent routing, or boundary-layer operational need is not sufficient authority."""


def fail(message: str, failures: list[str]) -> None:
    failures.append(f"FAIL {message}")


def main() -> int:
    failures: list[str] = []
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    boundary = registry.get("boundary_governance_constraint_policy", {})
    owner = registry.get("owner_reserved_authorization", {})

    if boundary.get("policy_id") != "BOUNDARY-GOV-001":
        fail("BOUNDARY-GOV-001 missing from registry", failures)
    if owner.get("policy_id") != "BOUNDARY-GOV-002":
        fail("BOUNDARY-GOV-002 missing from registry", failures)

    for field in [
        "boundary_layer_may_treat_governance_as_blocker",
        "boundary_layer_may_optimize_around_governance",
        "boundary_layer_may_auto_request_governance_change",
        "boundary_layer_may_auto_route_permission_request",
        "boundary_layer_may_bundle_governance_change_with_boundary_work",
    ]:
        if boundary.get(field) is not False:
            fail(f"{field} must be false", failures)

    if boundary.get("required_behavior") != "stop_and_create_human_escalation_warning":
        fail("BOUNDARY-GOV-001 must require stop_and_create_human_escalation_warning", failures)
    if boundary.get("warning_required") is not True:
        fail("BOUNDARY-GOV-001 must require a warning", failures)

    protected = set(boundary.get("protected_targets", []))
    for target in ["logos-governance-architecture", "logos-scripture-graph"]:
        if target not in protected:
            fail(f"protected target missing: {target}", failures)

    forbidden = set(boundary.get("forbidden_boundary_actions", []))
    for action in [
        "weaken_governance_policy_for_boundary_task",
        "bypass_governance_policy",
        "auto_escalate_permission_request",
        "route_approval_request_to_higher_authority_repo",
        "bundle_governance_change_with_boundary_intake",
    ]:
        if action not in forbidden:
            fail(f"forbidden boundary action missing: {action}", failures)

    if owner.get("authorized_owner") != "Lowell Wong":
        fail("authorized_owner must be Lowell Wong", failures)
    for field in [
        "contributor_consensus_sufficient",
        "contributor_volume_sufficient",
        "automated_recommendation_sufficient",
        "agent_routing_sufficient",
        "boundary_layer_need_sufficient",
    ]:
        if owner.get(field) is not False:
            fail(f"{field} must be false", failures)
    for field in [
        "requires_explicit_owner_authorization",
        "authorization_must_occur_in_higher_authority_repo",
    ]:
        if owner.get(field) is not True:
            fail(f"{field} must be true", failures)

    triggers = set(registry.get("global_stop_and_report_triggers", []))
    for trigger in [
        "boundary_layer_treats_governance_as_obstacle",
        "boundary_originated_request_targets_higher_authority_layer",
        "boundary_originated_request_lacks_owner_authorization",
    ]:
        if trigger not in triggers:
            fail(f"stop-and-report trigger missing: {trigger}", failures)

    warning = registry.get("boundary_layer_escalation_warning_text", "").strip()
    if warning != EXPECTED_WARNING:
        fail("required warning text missing or changed in registry", failures)

    docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "AI_FRONT_DOOR.md",
            ROOT / "DATA_FLOW_MAP.md",
            ROOT / "governance" / "LOGOS_REPO_REGISTRY.md",
            ROOT / "governance" / "BOUNDARY_GOVERNANCE_CONSTRAINTS.md",
            ROOT / "governance" / "REPOSITORY_LINK_CONTRACTS.md",
            ROOT / "governance" / "AI_FRONT_DOOR_STANDARD.md",
            ROOT / "governance" / "ADDING_NEW_LOGOS_REPOS.md",
        ]
    )
    for marker in ["BOUNDARY-GOV-001", "BOUNDARY-GOV-002", EXPECTED_WARNING]:
        if marker not in docs:
            fail(f"documentation missing marker: {marker[:60]}", failures)

    lower_docs = docs.lower()
    forbidden_phrases = [
        "fast" + " path",
        "private owner" + " workflow",
        "ai" + "-assisted merging",
        "relaxed" + " rules",
        "boundary repo can" + " override scripture",
        "boundary repo may" + " override scripture",
    ]
    for phrase in forbidden_phrases:
        if phrase in lower_docs:
            fail(f"forbidden phrase present: {phrase}", failures)

    if failures:
        print("Boundary governance stop-rule validation failed.")
        for failure in failures:
            print(failure)
        return 1

    print("Boundary governance stop-rule validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
