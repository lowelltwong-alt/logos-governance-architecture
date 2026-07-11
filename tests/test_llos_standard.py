from __future__ import annotations

import json
from pathlib import Path

from scripts import validate_llos_standard as validator


ROOT = Path(__file__).resolve().parents[1]


def test_llos_standard_passes() -> None:
    assert validator.validate(ROOT) == []


def test_dad_bridge_is_read_only_and_approval_is_not_standing() -> None:
    standard = validator._load_governed_yaml(
        ROOT / "governance/LOGOS_LEARNING_LOOP_OPERATING_STANDARD.yaml"
    )
    bridge = standard["dad_bridge"]
    assert bridge["read_approved_metadata"] is True
    assert bridge["write_inside_logos_repo"] is False
    assert bridge["deliver_to_logos_inbox"] is False
    assert bridge["approval_required_for_every_future_logos_write"] is True
    assert bridge["approval_must_be_fresh_and_explicit"] is True


def test_schema_rejects_authority_bearing_payload_shape() -> None:
    schema = json.loads((ROOT / "schemas/llos/lesson.v1.schema.json").read_text())
    assert schema["properties"]["contains_raw_source_payload"] == {"const": False}
    assert schema["properties"]["contains_theology_claim"] == {"const": False}
    assert schema["properties"]["human_review_required"] == {"const": True}
    assert schema["additionalProperties"] is False


def test_p0_and_irreversible_lessons_have_no_auto_sunset() -> None:
    standard = validator._load_governed_yaml(
        ROOT / "governance/LOGOS_LEARNING_LOOP_OPERATING_STANDARD.yaml"
    )
    assert standard["severity_policy"]["p0_auto_sunset_allowed"] is False
    assert standard["severity_policy"]["catastrophic_or_irreversible_auto_sunset_allowed"] is False
    assert standard["sunset_policy"]["auto_delete_allowed"] is False


def test_communication_is_two_way_without_dad_push_authority() -> None:
    standard = validator._load_governed_yaml(
        ROOT / "governance/LOGOS_LEARNING_LOOP_OPERATING_STANDARD.yaml"
    )
    communication = standard["communication"]
    assert communication["logos_local_may_write_own_outbox"] is True
    assert communication["dad_may_read_approved_logos_outbox"] is True
    assert communication["logos_local_may_read_dad_central_candidates"] is True
    assert communication["dad_push_to_logos_allowed"] is False
    assert communication["dad_direct_logos_inbox_write_allowed"] is False
    assert communication["candidate_return_authorizes_local_change"] is False


def test_dad_repo_write_policy_has_no_standing_approval() -> None:
    policy = json.loads(
        (ROOT / ".digital-asset/dad-write-policy.json").read_text(encoding="utf-8")
    )
    assert policy["dad_write_allowed"] is False
    assert policy["approved_explicit_approval_ids"] == []
    assert policy["logos_local_outbox_write_allowed"] is True
    assert policy["logos_local_dad_central_read_allowed"] is True
    assert policy["dad_push_or_inbox_write_allowed"] is False
    assert policy["rollout_approval_is_standing_write_permission"] is False


def _valid_lesson() -> dict:
    return {
        "lesson_id": "llos:synthetic.guard.1",
        "revision": 1,
        "source_repo": "logos-governance-architecture",
        "authority_owner": "Lowell Wong",
        "category": "authority_boundary",
        "route": "governance",
        "severity": "P1",
        "constitutional": False,
        "status": "candidate",
        "summary": "Synthetic boundary lesson.",
        "applies_when": ["testing the LLOS contract"],
        "does_not_apply_when": ["asserting theology"],
        "danger_if_misapplied": "Could create false authority.",
        "evidence_refs": ["tests/test_llos_standard.py"],
        "validator_refs": ["scripts/validate_llos_standard.py"],
        "changed_paths": [],
        "enforcement_ref": None,
        "prevention": "Run the validator.",
        "stop_condition": "Stop on authority leakage.",
        "authority_ceiling": "candidate_only",
        "reading_cost": 1,
        "irreversibility": "low",
        "blast_radius": "local",
        "sunset_eligible": True,
        "propagation_posture": "local_only",
        "source_hashes": [],
        "contains_raw_source_payload": False,
        "contains_theology_claim": False,
        "human_review_required": True,
        "sunset_review_due": "2027-01-01",
        "catastrophic_or_irreversible": False,
    }


def test_lesson_admission_rejects_path_gate_without_enforcement() -> None:
    lesson = _valid_lesson()
    lesson["changed_paths"] = ["governance/**"]
    assert "changed paths require an enforcement reference" in validator.validate_lesson_record(lesson)


def test_lesson_admission_rejects_p0_sunset_or_usage_style_demotion() -> None:
    lesson = _valid_lesson()
    lesson.update({"severity": "P0", "sunset_eligible": True, "sunset_review_due": "2027-01-01"})
    errors = validator.validate_lesson_record(lesson)
    assert any("cannot be sunset eligible" in error for error in errors)
    assert any("cannot receive a sunset date" in error for error in errors)


def test_lesson_admission_rejects_raw_payload_and_theology_claim() -> None:
    lesson = _valid_lesson()
    lesson["contains_raw_source_payload"] = True
    lesson["contains_theology_claim"] = True
    errors = validator.validate_lesson_record(lesson)
    assert "raw source payload is forbidden" in errors
    assert "theology claim is forbidden" in errors


def test_lesson_admission_accepts_bounded_synthetic_candidate() -> None:
    assert validator.validate_lesson_record(_valid_lesson()) == []
