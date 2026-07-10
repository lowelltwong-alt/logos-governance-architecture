from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json

from scripts import validate_family_work_registry as validator
from scripts import audit_family_work as auditor


def registry() -> dict:
    return validator.load_yaml(validator.REGISTRY)


def test_current_registry_validates() -> None:
    failures, _ = validator.validate_registry(
        registry(), as_of=datetime(2026, 7, 10, 20, 0, tzinfo=timezone.utc)
    )
    assert failures == []


def test_claim_schema_and_validator_require_the_same_fields() -> None:
    schema = json.loads(validator.SCHEMA.read_text(encoding="utf-8"))
    assert set(schema["required"]) == validator.REQUIRED_ITEM


def test_duplicate_active_task_fails_closed() -> None:
    data = registry()
    duplicate = deepcopy(data["work_items"][0])
    duplicate["work_id"] = "WORK-GOV-FAMILY-COORD-002"
    duplicate["branch"] = "codex/duplicate"
    data["work_items"].append(duplicate)

    failures, _ = validator.validate_registry(data)

    assert any("duplicate active task identity" in failure for failure in failures)


def test_exclusive_path_overlap_requires_owner_resolution() -> None:
    data = registry()
    overlapping = deepcopy(data["work_items"][0])
    overlapping.update({
        "work_id": "WORK-GOV-OVERLAP-002",
        "task_id": "OVERLAP-002",
        "objective_key": "overlap_mutant",
        "branch": "codex/overlap-mutant",
        "roadmap_refs": ["OVERLAP-002"],
        "semantic_tags": ["overlap_test"],
        "claimed_paths": ["governance/registry/**"],
        "related_work_ids": [],
    })
    data["work_items"].append(overlapping)

    failures, _ = validator.validate_registry(data)

    assert any("unresolved exclusive path overlap" in failure for failure in failures)


def test_owner_resolution_allows_recorded_parallel_boundary() -> None:
    data = registry()
    left = data["work_items"][0]
    overlapping = deepcopy(left)
    overlapping.update({
        "work_id": "WORK-GOV-OVERLAP-003",
        "task_id": "OVERLAP-003",
        "objective_key": "resolved_overlap_mutant",
        "branch": "codex/resolved-overlap",
        "roadmap_refs": ["OVERLAP-003"],
        "semantic_tags": ["overlap_test"],
        "claimed_paths": ["governance/registry/**"],
        "related_work_ids": [],
        "overlap_resolution_ids": ["OVERLAP-RES-001"],
    })
    left["overlap_resolution_ids"] = ["OVERLAP-RES-001"]
    data["overlap_resolutions"].append({
        "resolution_id": "OVERLAP-RES-001",
        "owner_decision_ref": "owner-test-fixture",
        "affected_work_ids": [left["work_id"], overlapping["work_id"]],
        "decision": "split_paths",
        "decided_at": "2026-07-10T20:00:00Z",
        "rationale": "Test-only owner resolution fixture for deterministic validation.",
    })
    data["work_items"].append(overlapping)

    failures, _ = validator.validate_registry(data)

    assert not any("overlap" in failure.lower() for failure in failures)


def test_stale_lease_warns_but_does_not_auto_abandon() -> None:
    data = registry()
    original_status = data["work_items"][0]["status"]
    data["work_items"][0]["started_at"] = "2026-05-31T00:00:00Z"
    data["work_items"][0]["heartbeat_at"] = "2026-06-01T00:00:00Z"

    failures, warnings = validator.validate_registry(
        data, as_of=datetime(2026, 7, 10, tzinfo=timezone.utc)
    )

    assert failures == []
    assert any("owner reconciliation required" in warning for warning in warnings)
    assert data["work_items"][0]["status"] == original_status


def test_path_overlap_is_conservative_for_globs() -> None:
    assert validator.paths_overlap("governance/registry/**", "governance/registry/file.yaml")
    assert not validator.paths_overlap("governance/registry/**", "docs/roadmap/file.md")


def test_dirty_worktree_is_never_classified_as_cleanup_candidate() -> None:
    classification = auditor.classify(
        primary=False, branch="codex/dirty", dirty=True, detached=False,
        ancestor=True, tree_equivalent=True, ahead=0, pr=None
    )
    assert classification == "preserve_dirty_owner_reconciliation"


def test_clean_merged_worktree_becomes_reviewable_cleanup_candidate() -> None:
    classification = auditor.classify(
        primary=False, branch="codex/merged", dirty=False, detached=False,
        ancestor=True, tree_equivalent=True, ahead=0, pr=None
    )
    assert classification == "merged_or_superseded_cleanup_candidate"


def test_live_audit_blocks_claim_that_overlaps_unregistered_worktree() -> None:
    data = registry()
    claim = data["work_items"][0]
    payload = {"worktrees": [{
        "repo": claim["repo"],
        "worktree_name": "forgotten-work",
        "branch": "codex/forgotten-work",
        "registered_work_ids": [],
        "classification": "preserve_dirty_owner_reconciliation",
        "dirty": True,
        "ahead_of_origin_main": 0,
        "task_candidates": [],
        "dirty_paths": ["governance/registry/FAMILY_WORK_REGISTRY.yaml"],
        "committed_paths_not_on_main": [],
    }]}

    blockers = auditor.claim_blockers(payload, data, claim["work_id"])

    assert any("path overlap" in blocker for blocker in blockers)


def test_recorded_owner_resolution_clears_observed_registered_overlap() -> None:
    data = registry()
    t469 = next(item for item in data["work_items"] if item["work_id"] == "WORK-SCR-T469")
    t469["status"] = "awaiting_review"
    t469["board_column"] = "review"
    t469["completion_evidence"] = []
    payload = {"worktrees": [{
        "repo": "logos-scripture-graph",
        "worktree_name": "preserved-t468",
        "branch": "codex/w2-2-scripture-mirror-freshness",
        "registered_work_ids": ["WORK-SCR-T468-W2-2"],
        "classification": "preserve_dirty_owner_reconciliation",
        "dirty": True,
        "ahead_of_origin_main": 1,
        "task_candidates": ["T468"],
        "dirty_paths": [".ai/control/PROJECT_STATUS.md"],
        "committed_paths_not_on_main": [".ai/control/handoff_ledger.jsonl"],
    }]}

    blockers = auditor.claim_blockers(payload, data, "WORK-SCR-T469")

    assert blockers == []
