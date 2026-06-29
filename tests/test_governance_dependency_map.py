from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts import validate_governance_dependency_map as validator


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "governance" / "GOVERNANCE_DEPENDENCY_MAP.yaml"


def load_map() -> dict:
    return validator.validate_dependency_map(MAP)


def test_dependency_map_validates_and_is_non_authorizing() -> None:
    data = validator.validate_dependency_map(MAP)

    assert data["object_type"] == "governance_dependency_map"
    assert data["trust_zone"] == "canonical"
    assert data["map_authority"]["records_governance_dependencies"] is True
    assert data["map_authority"]["authorizes_child_repo_override"] is False
    assert data["map_authority"]["authorizes_scripture_data_change"] is False
    assert data["map_authority"]["authorizes_boundary_import"] is False


def test_required_artifacts_are_present() -> None:
    data = load_map()
    by_id = {artifact["artifact_id"]: artifact for artifact in data["artifacts"]}

    assert by_id["GD-001"]["object_type"] == "governance_front_door"
    assert by_id["GD-002"]["object_type"] == "logos_repo_registry"
    assert by_id["GD-003"]["object_type"] == "repository_link_contracts"
    assert by_id["GD-004"]["object_type"] == "boundary_governance_stop_rules"
    assert by_id["GD-005"]["object_type"] == "external_advisory_authority_firewall"
    assert by_id["GD-007"]["object_type"] == "governance_validation_suite"
    assert by_id["GD-011"]["object_type"] == "anti_guessing_evidence_discipline"
    assert by_id["GD-013"]["object_type"] == "goal_prompt_premortem_preflight"
    assert by_id["GD-014"]["object_type"] == "governance_map_update_gate"


def test_required_paths_are_covered() -> None:
    data = validator.validate_dependency_map(MAP)
    paths = set()
    for artifact in data["artifacts"]:
        paths.update(artifact["paths"])

    assert "AI_FRONT_DOOR.md" in paths
    assert "governance/LOGOS_REPO_REGISTRY.yaml" in paths
    assert "governance/REPOSITORY_LINK_CONTRACTS.md" in paths
    assert "governance/BOUNDARY_GOVERNANCE_CONSTRAINTS.md" in paths
    assert "governance/EXTERNAL_ADVISORY_AUTHORITY_FIREWALL.md" in paths
    assert "docs/governance/anti-guessing-and-evidence-discipline.md" in paths
    assert "docs/governance/ai-workflow/goal-prompt-premortem-preflight.md" in paths
    assert "docs/governance/ai-workflow/validation-and-pr-requirements.md" in paths
    assert "governance/AI_FRONT_DOOR_STANDARD.md" in paths
    assert "AI_WORK_START_HERE.md" in paths
    assert "scripts/validation_contracts.py" in paths


def test_goal_prompt_premortem_preflight_is_governed_dependency_surface() -> None:
    data = load_map()
    by_id = {artifact["artifact_id"]: artifact for artifact in data["artifacts"]}
    artifact = by_id["GD-013"]

    assert artifact["owner_decision_ref"] == "docs/governance/ai-workflow/goal-prompt-premortem-preflight.md"
    assert artifact["depends_on"] == ["GD-001", "GD-007", "GD-008", "GD-009", "GD-012"]
    assert "AI_TABLE_OF_CONTENTS.md" in artifact["paths"]
    assert "premortem_red_team_fix_loop_requirement" in artifact["downstream_controls"]
    assert "owner_permission_preservation" in artifact["downstream_controls"]
    assert "stale_branch_parallel_agent_and_merge_hazard_check" in artifact["downstream_controls"]
    assert "logos-scripture-graph/.ai/control/chunking_agent_preflight.yaml" in artifact["mirrored_by"]
    assert "docs/governance/ai-workflow/goal-prompt-premortem-preflight.md" in artifact["update_triggers"]
    assert "AI_TABLE_OF_CONTENTS.md" in artifact["update_triggers"]


def test_governance_map_update_gate_records_companion_surfaces() -> None:
    data = load_map()
    by_id = {artifact["artifact_id"]: artifact for artifact in data["artifacts"]}
    artifact = by_id["GD-014"]
    update_policy = data["update_policy"]

    assert artifact["owner_decision_ref"] == "governance/GOVERNANCE_DEPENDENCY_MAP.yaml"
    assert "governance_dependency_map_correction_required" in artifact["downstream_controls"]
    assert "front_door_and_toc_discovery_surface_review_required" in artifact["downstream_controls"]
    assert "docs/governance/ai-workflow/validation-and-pr-requirements.md" in artifact["paths"]
    assert "scripts/validate_governance_dependency_map.py" in artifact["validators"]
    assert "tests/test_governance_dependency_map.py" in artifact["validators"]
    assert "governance/GOVERNANCE_DEPENDENCY_MAP.yaml" in update_policy["required_companion_surfaces_when_governance_changes"]
    assert "AI_FRONT_DOOR.md" in update_policy["required_companion_surfaces_when_governance_changes"]
    assert "AI_TABLE_OF_CONTENTS.md" in update_policy["required_companion_surfaces_when_governance_changes"]
    assert "AI_WORK_START_HERE.md" in update_policy["required_companion_surfaces_when_governance_changes"]


def test_changed_path_gate_requires_map_update_for_governance_paths() -> None:
    with pytest.raises(validator.DependencyMapError, match="must be updated"):
        validator.validate_changed_path_gate(
            changed_files=["governance/LOGOS_REPO_REGISTRY.yaml"],
            map_updated=False,
        )


def test_changed_path_gate_requires_registered_coverage_for_governance_paths() -> None:
    with pytest.raises(validator.DependencyMapError, match="registered in dependency map coverage"):
        validator.validate_changed_path_gate(
            changed_files=[
                "docs/governance/unregistered-new-governance-rule.md",
                "governance/GOVERNANCE_DEPENDENCY_MAP.yaml",
            ],
            map_updated=None,
        )


def test_changed_path_gate_passes_when_map_is_updated() -> None:
    validator.validate_changed_path_gate(
        changed_files=[
            "governance/LOGOS_REPO_REGISTRY.yaml",
            "governance/GOVERNANCE_DEPENDENCY_MAP.yaml",
        ],
        map_updated=None,
    )


def test_changed_path_gate_ignores_unwatched_paths() -> None:
    validator.validate_changed_path_gate(
        changed_files=["README.md", "docs/roadmap/theological-buildout-roadmap.md"],
        map_updated=False,
    )
