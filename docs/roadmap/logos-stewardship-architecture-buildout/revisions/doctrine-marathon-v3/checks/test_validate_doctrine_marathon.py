#!/usr/bin/env python3
"""
object_type: doctrine_marathon_validator_tests
trust_zone: proposed
lifecycle_status: active
provenance_note: Created on 2026-08-27 by Codex root.
reason_for_inclusion: Exercise the positive V3 draft and every declared
adversarial mutation without activating runtime or loading external sources.
"""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import validate_doctrine_marathon as validator  # noqa: E402


SOURCE_ROOT_SENTINELS = (
    "constitution.yaml",
    "mesh/qualification-registry.json",
    "graph/authority-registry.yaml",
    "graph/example-graph.json",
    "events/event-ledger.json",
    "checks/validate_doctrine_marathon.py",
)

STRICT_ISOLATED_CATALOG = HERE / "fixtures" / "strict-isolated-cases.json"


def clear_validator_caches() -> None:
    """Keep isolated cases independent of validation order and prior roots."""
    validator._QUALIFICATION_VALIDATION_CACHE.clear()
    validator._ROLE_ASSIGNMENT_VALIDATION_CACHE.clear()


def write_isolated_json(root: Path, relative: str, value: Any) -> None:
    path = (root / relative).resolve()
    assert path.is_relative_to(root.resolve()), relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


@contextmanager
def isolated_validator_root(prefix: str) -> Iterator[Path]:
    """Copy V3, bind the validator to it, and prove no source sentinel changed."""
    source_root = validator.ROOT
    before = {
        relative: validator.file_digest(source_root / relative)
        for relative in SOURCE_ROOT_SENTINELS
    }
    clear_validator_caches()
    try:
        with tempfile.TemporaryDirectory(prefix=prefix) as temporary:
            root = Path(temporary) / "v3"
            shutil.copytree(source_root, root)
            validator.ROOT = root
            try:
                yield root
            finally:
                validator.ROOT = source_root
                clear_validator_caches()
    finally:
        validator.ROOT = source_root
        clear_validator_caches()
        after = {
            relative: validator.file_digest(source_root / relative)
            for relative in SOURCE_ROOT_SENTINELS
        }
        assert after == before, f"source-root sentinel changed: {before} != {after}"


def rules(errors: list[str]) -> set[str]:
    return {error.split(":", 1)[0] for error in errors}


def load(relative: str) -> Any:
    return validator.load_data(relative)


def historical_candidate() -> dict[str, Any]:
    source = qualified_source()
    value = {
        "schema_version": "logos.doctrine-marathon.historical-attribution.v3",
        "attribution_id": "HATTR-TEST",
        "actor_or_community_ref": "actor:synthetic-actor",
        "actor_or_community": "Synthetic actor",
        "document_or_event_ref": "document:synthetic-document",
        "document_or_event": "Synthetic document",
        "date_or_period": {"display": "undated test", "uncertainty": "synthetic"},
        "label_used": "synthetic label",
        "target_labeled_ref": "proposition:synthetic-target",
        "target_labeled": "synthetic target",
        "target_proposition": "synthetic proposition",
        "source_record_ref": "source-record:SRC-SYNTHETIC-A",
        "source_record_digest": source["record_digest"],
        "exact_locator": "test:1",
        "source_state": "qualified",
        "dispute_state": "unknown",
        "review_scope_digest": validator.ZERO_DIGEST,
        "review_receipt_refs": [],
        "review_receipt_digests": [],
        "review_state": "candidate",
        "normative_force": "none",
        "ai_generated_verdict": False,
        "attribution_digest": validator.ZERO_DIGEST,
    }
    value["review_scope_digest"] = validator.evidence_review_scope_digest(
        value, "historical-attribution"
    )
    value["attribution_digest"] = validator.object_digest(
        value, omit=("attribution_digest",)
    )
    return value


def normative_candidate() -> dict[str, Any]:
    value = {
        "schema_version": "logos.doctrine-marathon.normative-frame.v3",
        "frame_id": "NFRAME-TEST",
        "revision": 1,
        "tradition_or_jurisdiction": "Synthetic test frame",
        "canon_scope": ["synthetic"],
        "admitted_authorities": [{"authority_id": "synthetic", "role": "test", "scope": "test"}],
        "interpretive_policy_ref": "synthetic/policy",
        "scope_digest": validator.ZERO_DIGEST,
        "human_approval_receipt_ref": "human-decision:HDEC-SYNTHETIC",
        "human_approval_receipt_digest": validator.ZERO_DIGEST,
        "authority_registry_digest": validator.ZERO_DIGEST,
        "approved_by": ["HUMAN-SYNTHETIC"],
        "effective_at": "2026-08-27T19:00:00Z",
        "expires_at": None,
        "supersedes_frame_ref": None,
        "status": "human_approved_active",
        "created_by_ai": False,
        "frame_digest": validator.ZERO_DIGEST
    }
    value["scope_digest"] = validator.normative_scope_digest(value)
    return value


def qualified_source() -> dict[str, Any]:
    value = {
        "schema_version": "logos.doctrine-marathon.source-record.v3",
        "source_record_id": "SRC-SYNTHETIC-A",
        "revision": 1,
        "source_kind": "primary_witness",
        "root_or_derivative": "root",
        "title": "Synthetic source fixture",
        "creator_or_custodian": "Synthetic archive",
        "edition_or_witness_id": "SYNTHETIC-WITNESS-A",
        "stable_locator_uri": "https://example.invalid/synthetic-source-a",
        "root_source_access": "directly_reaccessed",
        "identity_state": "qualified",
        "rights_state": "open_license",
        "content_digest": "sha256:" + "a" * 64,
        "observed_at": "2026-08-27T19:00:00Z",
        "qualification_scope_digest": validator.ZERO_DIGEST,
        "qualification_receipt_refs": [],
        "qualification_receipt_digests": [],
        "qualifies_for_load_bearing": True,
        "record_digest": validator.ZERO_DIGEST,
    }
    value["qualification_scope_digest"] = validator.source_qualification_scope_digest(value)
    value["record_digest"] = validator.object_digest(value, omit=("record_digest",))
    return value


def claim_candidate(claim_type: str, state: str = "candidate") -> dict[str, Any]:
    source = qualified_source()
    dimensions = {
        "source_identity": "qualified",
        "source_fitness": "qualified",
        "rights_and_access": "qualified",
        "locator_validity": "verified",
        "quotation_fidelity": "not_applicable",
        "translation_fidelity": "specialist_reviewed" if claim_type == "translation" else "not_applicable",
        "context_integrity": "verified",
        "entailment": "verified",
        "causal_or_influence_support": "specialist_reviewed" if claim_type == "influence_or_causation" else "not_applicable",
        "temporal_fit": "verified",
        "tradition_representation": "not_applicable",
        "normative_admissibility": "human_frame_verified" if claim_type == "normative_assessment" else "not_applicable",
        "human_review": "completed",
    }
    value = {
        "schema_version": "logos.doctrine-marathon.claim-record.v3",
        "claim_id": "CLAIM-SYNTHETIC",
        "claim_type": claim_type,
        "assertion_text": "Synthetic claim used only for adversarial validation.",
        "source_record_refs": ["source-record:SRC-SYNTHETIC-A"],
        "source_bindings": [{
            "source_record_ref": "source-record:SRC-SYNTHETIC-A",
            "source_content_digest": source["content_digest"],
            "source_record_digest": source["record_digest"],
            "exact_locator_refs": ["test:1"],
        }],
        "exact_locator_refs": ["test:1"],
        "quotation_or_transcription_ref": None,
        "translation_lineage_ref": "translation-lineage:TLIN-SYNTHETIC" if claim_type == "translation" else None,
        "translation_lineage_digest": None,
        "influence_hypothesis_ref": "influence-hypothesis:INFL-SYNTHETIC" if claim_type == "influence_or_causation" else None,
        "influence_hypothesis_digest": None,
        "historical_attribution_ref": "historical-attribution:HATTR-SYNTHETIC" if claim_type == "historical_attribution" else None,
        "historical_attribution_digest": None,
        "normative_frame_ref": "normative-frame:NFRAME-SYNTHETIC" if claim_type == "normative_assessment" else None,
        "normative_frame_digest": None,
        "review_receipt_refs": [],
        "review_receipt_digests": [],
        "context_boundary": "Synthetic context boundary for adversarial validation only.",
        "status_dimensions": dimensions,
        "claim_state": state,
        "normative_force": "frame_scoped" if claim_type == "normative_assessment" else "none",
        "evidence_digest": validator.ZERO_DIGEST,
    }
    value["evidence_digest"] = validator.object_digest(value, omit=("evidence_digest",))
    return value


def translation_candidate() -> dict[str, Any]:
    source = qualified_source()
    value = {
        "schema_version": "logos.doctrine-marathon.translation-lineage.v3",
        "translation_lineage_id": "TLIN-SYNTHETIC",
        "source_record_ref": "source-record:SRC-SYNTHETIC-A",
        "source_record_digest": source["content_digest"],
        "source_record_object_digest": source["record_digest"],
        "source_language": "grc",
        "target_language": "en",
        "edition_or_witness_id": "SYNTHETIC-WITNESS-A",
        "segment_locators": ["test:1"],
        "translator_or_method": "synthetic adversarial fixture",
        "generated_by_ai": True,
        "review_scope_digest": validator.ZERO_DIGEST,
        "specialist_review_receipt_refs": [],
        "specialist_review_receipt_digests": [],
        "human_approval_receipt_ref": None,
        "human_approval_receipt_digest": None,
        "status": "candidate",
        "lineage_digest": validator.ZERO_DIGEST,
    }
    value["review_scope_digest"] = validator.evidence_review_scope_digest(
        value, "translation-lineage"
    )
    value["lineage_digest"] = validator.object_digest(value, omit=("lineage_digest",))
    return value


def influence_candidate() -> dict[str, Any]:
    value = {
        "schema_version": "logos.doctrine-marathon.influence-hypothesis.v3",
        "hypothesis_id": "INFL-SYNTHETIC",
        "source_actor_ref": "actor:synthetic-a",
        "target_actor_ref": "actor:synthetic-b",
        "source_period": "synthetic earlier period",
        "target_period": "synthetic later period",
        "contact_evidence_refs": ["source-record:SRC-SYNTHETIC-A"],
        "reception_evidence_refs": ["source-record:SRC-SYNTHETIC-B"],
        "mechanism": "Synthetic possible contact mechanism for adversarial testing.",
        "alternative_hypotheses": ["Synthetic independent development alternative."],
        "counterevidence_refs": ["synthetic:counterevidence"],
        "qualified_source_record_refs": [
            "source-record:SRC-SYNTHETIC-A",
            "source-record:SRC-SYNTHETIC-B",
        ],
        "review_scope_digest": validator.ZERO_DIGEST,
        "specialist_review_receipt_refs": [],
        "specialist_review_receipt_digests": [],
        "confidence": "probable",
        "status": "candidate",
        "normative_force": "none",
        "hypothesis_digest": validator.ZERO_DIGEST,
    }
    value["review_scope_digest"] = validator.evidence_review_scope_digest(
        value, "influence-hypothesis"
    )
    value["hypothesis_digest"] = validator.object_digest(
        value, omit=("hypothesis_digest",)
    )
    return value


def evidence_registry_candidate(
    *,
    sources: list[dict[str, Any]] | None = None,
    lineages: list[dict[str, Any]] | None = None,
    hypotheses: list[dict[str, Any]] | None = None,
    attributions: list[dict[str, Any]] | None = None,
    claims: list[dict[str, Any]] | None = None,
    reviews: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    value = {
        "metadata": {
            "object_type": "synthetic_evidence_registry",
            "trust_zone": "proposed",
            "lifecycle_status": "test",
            "provenance_note": "Synthetic registry for deterministic adversarial tests.",
            "reason_for_inclusion": "Exercise typed evidence gates without ingesting sources.",
        },
        "schema_version": "logos.doctrine-marathon.evidence-registry.v3",
        "runtime_records": True,
        "source_records": sources or [],
        "translation_lineages": lineages or [],
        "influence_hypotheses": hypotheses or [],
        "historical_attributions": attributions or [],
        "claim_records": claims or [],
        "evidence_review_receipts": reviews or [],
        "registry_digest": validator.ZERO_DIGEST,
    }
    value["registry_digest"] = validator.object_digest(value, omit=("registry_digest",))
    return value


def authority_fixture() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    registry = copy.deepcopy(load("graph/authority-registry.yaml"))
    registry["metadata"] = {
        "object_type": "synthetic_authority_registry",
        "trust_zone": "proposed",
        "lifecycle_status": "test",
        "provenance_note": "Synthetic non-authorizing unit-test fixture.",
        "reason_for_inclusion": "Exercise typed authority rejection paths only.",
    }
    root = load("graph/human-identity-authority-root.yaml")
    qualification = {
        "schema_version": "logos.doctrine-marathon.approver-qualification.v3",
        "receipt_id": "QAPP-SYNTHETIC",
        "signer_id": "HUMAN-SYNTHETIC",
        "issuer_id": "HUMAN-SYNTHETIC",
        "qualification_scope": ["normative_frame_approval"],
        "tradition_or_jurisdiction": "Synthetic test frame",
        "identity_root_anchor_digest": root["anchor_digest"],
        "protected_commit": "a" * 40,
        "evidence_bindings": [{
            "ref": "constitution.yaml",
            "digest": validator.file_digest(validator.ROOT / "constitution.yaml"),
        }],
        "issued_at": "2026-08-27T18:00:00Z",
        "expires_at": None,
        "recorded_by_human": True,
        "created_by_ai": False,
        "receipt_digest": validator.ZERO_DIGEST,
    }
    qualification["receipt_digest"] = validator.object_digest(
        qualification, omit=("receipt_digest",)
    )
    registry["approver_qualification_receipts"] = [qualification]
    registry["qualified_approvers"] = [{
        "signer_id": "HUMAN-SYNTHETIC",
        "qualification_scope": ["normative_frame_approval"],
        "tradition_or_jurisdiction": "Synthetic test frame",
        "qualification_receipt_ref": "approver-qualification:QAPP-SYNTHETIC",
        "qualification_receipt_digest": qualification["receipt_digest"],
        "valid_from": "2026-08-27T18:00:00Z",
        "valid_until": None,
    }]
    registry["approver_set_digest"] = validator.object_digest(registry["qualified_approvers"])
    frame = normative_candidate()
    frame["authority_registry_digest"] = registry["approver_set_digest"]
    receipt = {
        "schema_version": "logos.doctrine-marathon.human-decision-receipt.v3",
        "receipt_id": "HDEC-SYNTHETIC",
        "decision_type": "normative_frame_approval",
        "subject_ref": "normative-frame:NFRAME-TEST",
        "subject_digest": frame["scope_digest"],
        "scope_digest": frame["scope_digest"],
        "tradition_or_jurisdiction": "Synthetic test frame",
        "signer_ids": ["HUMAN-SYNTHETIC"],
        "signer_registry_digest": registry["approver_set_digest"],
        "authority_scope": ["normative_frame_approval"],
        "decision": "approved",
        "issued_at": "2026-08-27T19:00:00Z",
        "expires_at": None,
        "attestation_bindings": [{
            "ref": "constitution.yaml",
            "digest": validator.file_digest(validator.ROOT / "constitution.yaml"),
        }],
        "recorded_by_human": True,
        "created_by_ai": False,
        "receipt_digest": validator.ZERO_DIGEST,
    }
    receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
    frame["human_approval_receipt_digest"] = receipt["receipt_digest"]
    frame["frame_digest"] = validator.object_digest(frame, omit=("frame_digest",))
    registry["current_normative_frame_ref"] = "normative-frame:NFRAME-TEST"
    registry["current_normative_frame_digest"] = frame["frame_digest"]
    registry["human_decision_receipts"] = [receipt]
    registry["normative_frames"] = [frame]
    registry["normative_authority_active"] = True
    registry["registry_digest"] = validator.object_digest(registry, omit=("registry_digest",))
    return registry, receipt, frame


def seal_ledger(value: dict[str, Any]) -> dict[str, Any]:
    prior = None
    for event in value["events"]:
        event["prior_event_hash"] = prior
        event["event_hash"] = validator.object_digest(event, omit=("event_hash",))
        prior = event["event_hash"]
    value["event_count"] = len(value["events"])
    value["last_event_hash"] = prior
    value["ledger_hash"] = validator.object_digest(value, omit=("ledger_hash",))
    return value


def event_ledger_candidate() -> dict[str, Any]:
    digest = "sha256:" + "a" * 64
    graph_digest = validator.file_digest(validator.ROOT / "graph/example-graph.json")
    direct_subjects = ["DMV3-CONSTITUTION"]
    graph = load("graph/example-graph.json")
    closure = sorted(
        set(direct_subjects)
        | validator.reverse_closure(graph["reverse_consumer_index"], direct_subjects)
    )
    closure_digest = validator.object_digest(closure)
    trigger_row = next(
        row
        for row in load("firewall/trigger-matrix.yaml")["triggers"]
        if row["trigger_id"] == "TR-SOURCE"
    )
    required_actions = sorted(trigger_row["actions"])
    assignment_bundle_ref = "mesh/examples/design-time-independence-fixture.json"
    assignment_bundle_digest = validator.file_digest(
        validator.ROOT / assignment_bundle_ref
    )
    completeness_assignment_ref = (
        "role-assignment:DMV3-ROLE-SYNTHETIC-META-CHECKER"
    )
    completeness_assignment = next(
        row
        for row in load(assignment_bundle_ref)["assignments"]
        if f"role-assignment:{row['assignment_id']}" == completeness_assignment_ref
    )
    action_evidence_binding = {
        "ref": "constitution.yaml",
        "digest": validator.file_digest(validator.ROOT / "constitution.yaml"),
    }
    action_results = []
    for action_id in required_actions:
        result = {
            "action_id": action_id,
            "subject_ids": closure,
            "result": "pass_to_continue",
            "evidence_bindings": [action_evidence_binding],
            "checker_assignment_ref": completeness_assignment_ref,
            "checker_assignment_digest": validator.object_digest(
                completeness_assignment
            ),
            "checker_actor_instance_id": completeness_assignment[
                "actor_instance_id"
            ],
            "checker_attempt_id": completeness_assignment["attempt_id"],
            "result_digest": validator.ZERO_DIGEST,
        }
        result["result_digest"] = validator.object_digest(
            result, omit=("result_digest",)
        )
        action_results.append(result)
    required_capabilities = [
        "prompt_alignment_and_authority",
        "role_qualification_and_independence",
    ]
    entry_details = {
        "coverage_input_digest": digest,
        "requirement_and_assignment_refs": ["synthetic/assignment"],
        "completeness_assignment_bundle_ref": assignment_bundle_ref,
        "completeness_assignment_bundle_digest": assignment_bundle_digest,
        "completeness_assignment_ref": completeness_assignment_ref,
        "completeness_assignment_digest": validator.object_digest(completeness_assignment),
        "required_capability_ids": required_capabilities,
        "requirement_set_digest": validator.ZERO_DIGEST,
    }
    entry_details["requirement_set_digest"] = validator.object_digest({
        key: entry_details[key]
        for key in (
            "coverage_input_digest", "requirement_and_assignment_refs",
            "completeness_assignment_bundle_ref", "completeness_assignment_bundle_digest",
            "completeness_assignment_ref", "completeness_assignment_digest",
            "required_capability_ids",
        )
    })
    exit_details = {
        "final_output_digest": digest,
        "independently_rederived_requirements": True,
        "discovered_gap_and_replay_refs": [],
        "completeness_assignment_bundle_ref": assignment_bundle_ref,
        "completeness_assignment_bundle_digest": assignment_bundle_digest,
        "completeness_assignment_ref": completeness_assignment_ref,
        "completeness_assignment_digest": validator.object_digest(
            completeness_assignment
        ),
        "required_capability_ids": required_capabilities,
        "requirement_set_digest": validator.ZERO_DIGEST,
    }
    exit_details["requirement_set_digest"] = validator.object_digest({
        key: exit_details[key]
        for key in (
            "final_output_digest",
            "independently_rederived_requirements",
            "discovered_gap_and_replay_refs",
            "completeness_assignment_bundle_ref",
            "completeness_assignment_bundle_digest",
            "completeness_assignment_ref",
            "completeness_assignment_digest",
            "required_capability_ids",
        )
    })
    events: list[dict[str, Any]] = []
    kinds_and_details = [
        ("work_unit_classified", {}),
        ("completeness_entry", entry_details),
        ("material_trigger", {
            "trigger_matrix_id": "TR-SOURCE",
            "changed_input_digest": digest,
            "dependency_graph_ref": "graph/example-graph.json",
            "dependency_graph_digest": graph_digest,
            "direct_subject_ids": direct_subjects,
            "affected_work_and_consumer_ids": closure,
            "closure_digest": closure_digest,
            "required_action_ids": required_actions,
        }),
        ("completeness_midflight", {
            "prior_trigger_event_id": "DMV3-EVENT-0003",
            "trigger_event_hash": validator.ZERO_DIGEST,
            "fresh_changed_input_digest": digest,
            "dependency_graph_digest": graph_digest,
            "covered_affected_ids": closure,
            "closure_digest": closure_digest,
            "completeness_assignment_bundle_ref": assignment_bundle_ref,
            "completeness_assignment_bundle_digest": assignment_bundle_digest,
            "completeness_assignment_ref": completeness_assignment_ref,
            "completeness_assignment_digest": validator.object_digest(completeness_assignment),
            "required_capability_ids": required_capabilities,
            "fresh_requirement_set_digest": validator.ZERO_DIGEST,
            "action_assignment_bundle_ref": assignment_bundle_ref,
            "action_assignment_bundle_digest": assignment_bundle_digest,
            "action_results": action_results,
        }),
        ("candidate_created", {}),
        ("gap_discovered", {}),
        ("completeness_exit", exit_details),
        ("checkpoint_frozen", {}),
        ("terminal_handoff", {"checkpoint_digest": digest, "terminal_status": "BLOCKED", "exact_next_prompt_or_explicit_none_if_complete": "Synthetic next prompt for validation only."}),
    ]
    for sequence, (event_type, details) in enumerate(kinds_and_details, start=1):
        events.append({
            "event_id": f"DMV3-EVENT-{sequence:04d}",
            "sequence": sequence,
            "occurred_at": f"2026-08-27T19:{sequence:02d}:00Z",
            "event_type": event_type,
            "actor_id": "SYNTHETIC-ACTOR",
            "input_digest": digest,
            "affected_ids": closure,
            "authority_ref": "synthetic/authority",
            "details": details,
            "prior_event_hash": None,
            "event_hash": validator.ZERO_DIGEST,
        })
    ledger = seal_ledger({
        "metadata": {"object_type": "test", "trust_zone": "proposed", "lifecycle_status": "test", "provenance_note": "synthetic", "reason_for_inclusion": "synthetic test only"},
        "schema_version": "logos.doctrine_marathon.event-ledger.v3",
        "campaign_id": "LOGOS-DOCTRINE-MARATHON-003",
        "runtime_events": True,
        "append_only": True,
        "ledger_generation": 0,
        "prior_snapshot": None,
        "event_count": 0,
        "last_event_hash": None,
        "events": events,
        "ledger_hash": validator.ZERO_DIGEST,
    })
    trigger = ledger["events"][2]
    midflight = ledger["events"][3]
    midflight["details"]["trigger_event_hash"] = trigger["event_hash"]
    midflight["details"]["fresh_requirement_set_digest"] = validator.object_digest({
        "trigger_event_hash": trigger["event_hash"],
        "changed_input_digest": trigger["details"]["changed_input_digest"],
        "dependency_graph_digest": trigger["details"]["dependency_graph_digest"],
        "closure_digest": trigger["details"]["closure_digest"],
        "required_action_ids": trigger["details"]["required_action_ids"],
        "action_assignment_bundle_ref": midflight["details"]["action_assignment_bundle_ref"],
        "action_assignment_bundle_digest": midflight["details"]["action_assignment_bundle_digest"],
        "completeness_assignment_bundle_ref": midflight["details"]["completeness_assignment_bundle_ref"],
        "completeness_assignment_bundle_digest": midflight["details"]["completeness_assignment_bundle_digest"],
        "completeness_assignment_ref": midflight["details"]["completeness_assignment_ref"],
        "completeness_assignment_digest": midflight["details"]["completeness_assignment_digest"],
        "required_capability_ids": midflight["details"]["required_capability_ids"],
    })
    return seal_ledger(ledger)


def reseal_event_candidate(value: dict[str, Any]) -> dict[str, Any]:
    """Rebind the synthetic trigger/midflight chain after a scoped mutation."""
    seal_ledger(value)
    trigger = next(
        event for event in value["events"] if event["event_type"] == "material_trigger"
    )
    midflight = next(
        event
        for event in value["events"]
        if event["event_type"] == "completeness_midflight"
    )
    midflight["details"]["trigger_event_hash"] = trigger["event_hash"]
    midflight["details"]["fresh_requirement_set_digest"] = validator.object_digest({
        "trigger_event_hash": trigger["event_hash"],
        "changed_input_digest": trigger["details"]["changed_input_digest"],
        "dependency_graph_digest": trigger["details"]["dependency_graph_digest"],
        "closure_digest": trigger["details"]["closure_digest"],
        "required_action_ids": trigger["details"]["required_action_ids"],
        "action_assignment_bundle_ref": midflight["details"].get(
            "action_assignment_bundle_ref"
        ),
        "action_assignment_bundle_digest": midflight["details"].get(
            "action_assignment_bundle_digest"
        ),
        "completeness_assignment_bundle_ref": midflight["details"].get(
            "completeness_assignment_bundle_ref"
        ),
        "completeness_assignment_bundle_digest": midflight["details"].get(
            "completeness_assignment_bundle_digest"
        ),
        "completeness_assignment_ref": midflight["details"].get(
            "completeness_assignment_ref"
        ),
        "completeness_assignment_digest": midflight["details"].get(
            "completeness_assignment_digest"
        ),
        "required_capability_ids": midflight["details"].get(
            "required_capability_ids"
        ),
    })
    return seal_ledger(value)


def completion_gate_fixture_errors(mutation: str) -> list[str]:
    """Build an internally sealed synthetic completion state and mutate one binding."""
    with isolated_validator_root("dmv3-completion-") as root:
        try:
            def write_json(relative: str, value: Any) -> None:
                write_isolated_json(root, relative, value)

            def make_assignment(
                unit: str,
                phase: str,
                label: str,
                role_id: str,
                assignment_kind: str,
                capability_id: str | list[str],
                control_ref: str,
                checks: list[str],
            ) -> dict[str, Any]:
                assignment_id = f"DMV3-ROLE-{unit.removeprefix('DMV3-SYNTHETIC-')}-{phase}-{label}"
                control_digest = validator.file_digest(root / control_ref)
                source_order = [{
                    "ordinal": 1,
                    "source_ref": control_ref,
                    "source_digest": control_digest,
                    "source_class": "control_contract",
                }]
                guides = [{
                    "guide_ref": control_ref,
                    "guide_digest": control_digest,
                    "usage": "instruction_context",
                    "used_as_evidence": False,
                }]
                runtime_adapter = {
                    "adapter_id": f"SYNTHETIC-{phase}-{label}-ADAPTER",
                    "runtime_family": f"synthetic-{phase.lower()}-{label.lower()}-runtime",
                    "model_revision": f"synthetic-{phase.lower()}-{label.lower()}-revision",
                    "capability_tier": "frontier_reasoning" if assignment_kind == "checker" else "balanced",
                    "reasoning_effort": "synthetic",
                    "tool_profile_digest": "sha256:" + ("a" if label == "WRITER" else "b" if label == "META" else "c") * 64,
                    "context_digest": "sha256:" + ("d" if label == "WRITER" else "e" if label == "META" else "f") * 64,
                    "receipt_ref": f"synthetic:attempt:{unit}:{phase}:{label}",
                }
                value = {
                    "schema_version": "logos.doctrine-marathon.role-assignment.v3",
                    "assignment_id": assignment_id,
                    "work_unit_id": unit,
                    "assignment_kind": assignment_kind,
                    "role_id": role_id,
                    "capability_ids": [capability_id] if isinstance(capability_id, str) else capability_id,
                    "qualification_basis": {
                        "kind": "control_contract",
                        "ref": control_ref,
                        "digest": control_digest,
                        "state": "candidate",
                    },
                    "expected_information_gain": f"Provide bounded synthetic {label.lower()} evidence for the exact {unit} completion-gate regression without asserting source or theological authority.",
                    "qualification_receipt_ref": None,
                    "qualification_receipt_digest": None,
                    "task_prompt_ref": None,
                    "task_prompt_digest": None,
                    "prompt_neutrality_review_ref": None,
                    "prompt_neutrality_review_digest": None,
                    "attempt_id": f"SYNTHETIC-{unit}-{phase}-{label}-ATTEMPT",
                    "actor_instance_id": f"SYNTHETIC-{unit}-{phase}-{label}-ACTOR",
                    "checks_assignment_ids": checks,
                    "source_order": source_order,
                    "source_order_digest": validator.object_digest(source_order),
                    "knowledge_guide_lineage": guides,
                    "knowledge_guide_lineage_digest": validator.object_digest(guides),
                    "runtime_adapter": runtime_adapter,
                    "runtime_adapter_digest": validator.object_digest(runtime_adapter),
                    "independence": {
                        "answer_context_exposure": "none",
                        "prompt_author_ids": [f"SYNTHETIC-{unit}-{phase}-{label}-PROMPT-AUTHOR"],
                        "correlation_disclosures": [],
                        "assessment": "independent",
                        "human_acceptance_receipt_ref": None,
                    },
                    "expires_with_work_unit": True,
                    "status": "candidate",
                }
                return value

            def bind_runtime_prompt_reviews(
                assignments: list[dict[str, Any]], phase: str
            ) -> list[dict[str, Any]]:
                """Bind every runtime assignment to a neutral prompt and peer review."""
                assignment_map = {
                    row["assignment_id"]: row for row in assignments
                }
                meta = next(
                    row for row in assignments
                    if row["role_id"] == "role-qualification-and-independence-auditor"
                )
                whole = next(
                    row for row in assignments
                    if row["role_id"] == "independent-whole-work-checker"
                )
                for assignment in assignments:
                    prompt_ref = (
                        "mesh/task-prompts/"
                        f"{assignment['assignment_id'].lower()}-{phase.lower()}.md"
                    )
                    prompt_path = root / prompt_ref
                    prompt_path.parent.mkdir(parents=True, exist_ok=True)
                    prompt_path.write_text(
                        "Inspect the bounded synthetic inputs independently. "
                        "Report counterevidence, conflicts, and abstain when support "
                        "is insufficient. This test prompt grants no authority.\n",
                        encoding="utf-8",
                    )
                    assignment["task_prompt_ref"] = prompt_ref
                    assignment["task_prompt_digest"] = validator.file_digest(prompt_path)
                reviews: list[dict[str, Any]] = []
                contract_ref = "firewall/prompt-neutrality-contract.yaml"
                contract_digest = validator.file_digest(root / contract_ref)
                dimensions = sorted({
                    "presupposed_conclusion",
                    "framing",
                    "omitted_alternatives",
                    "counterevidence_route",
                    "abstention_path",
                    "authority_transfer",
                })
                for assignment in assignments:
                    reviewer = meta if assignment is whole else whole
                    assert assignment["assignment_id"] in reviewer["checks_assignment_ids"]
                    review_id = (
                        "PNR-"
                        f"{assignment['assignment_id'].removeprefix('DMV3-ROLE-')}-{phase}"
                    )
                    review = {
                        "schema_version": "logos.doctrine-marathon.prompt-neutrality-review.v3",
                        "review_id": review_id,
                        "subject_assignment_ref": f"role-assignment:{assignment['assignment_id']}",
                        "subject_assignment_scope_digest": (
                            validator.prompt_review_assignment_scope_digest(assignment)
                        ),
                        "task_prompt_ref": assignment["task_prompt_ref"],
                        "task_prompt_digest": assignment["task_prompt_digest"],
                        "neutrality_contract_ref": contract_ref,
                        "neutrality_contract_digest": contract_digest,
                        "reviewer_assignment_ref": f"role-assignment:{reviewer['assignment_id']}",
                        "review_dimensions": dimensions,
                        "decision": "accepted",
                        "reviewed_at": "2026-08-27T18:30:00Z",
                        "expires_at": "2026-08-27T21:00:00Z",
                        "authority_effect": "none",
                        "receipt_digest": validator.ZERO_DIGEST,
                    }
                    review["receipt_digest"] = validator.object_digest(
                        review, omit=("receipt_digest",)
                    )
                    assignment["prompt_neutrality_review_ref"] = (
                        f"prompt-neutrality-review:{review_id}"
                    )
                    assignment["prompt_neutrality_review_digest"] = review[
                        "receipt_digest"
                    ]
                    reviews.append(review)
                assert set(assignment_map) == {
                    row["subject_assignment_ref"].split(":", 1)[1]
                    for row in reviews
                }
                return reviews

            def seal_bundle(
                assignments: list[dict[str, Any]],
                registry_ref: str,
                *,
                authority_effect: str = "none",
                prompt_reviews: list[dict[str, Any]] | None = None,
            ) -> dict[str, Any]:
                unit = assignments[0]["work_unit_id"]
                purpose = (
                    "QUALIFICATION-SUPPORT"
                    if "qualification-snapshots/" in registry_ref
                    else "RUNTIME-REVIEW"
                )
                value = {
                    "schema_version": "logos.doctrine-marathon.role-assignment-bundle.v3",
                    "bundle_id": (
                        f"DMV3-BUNDLE-{unit.removeprefix('DMV3-')}-{purpose}"
                    ),
                    "work_unit_id": unit,
                    "issued_at": "2026-08-27T18:20:00Z",
                    "expires_at": "2026-08-27T21:00:00Z",
                    "fixture_kind": "runtime_receipt",
                    "runtime_assignments": True,
                    "authority_effect": authority_effect,
                    "qualification_registry_ref": registry_ref,
                    "qualification_registry_digest": validator.file_digest(root / registry_ref),
                    "assignments": assignments,
                    "prompt_neutrality_reviews": prompt_reviews or [],
                    "bundle_digest": validator.ZERO_DIGEST,
                }
                value["bundle_digest"] = validator.object_digest(value, omit=("bundle_digest",))
                return value

            output_ref = "state/examples/synthetic-completion-output.json"
            write_json(output_ref, {"synthetic": True, "authority_effect": "none"})
            output_digest = validator.file_digest(root / output_ref)
            attestation_ref = "state/examples/synthetic-human-attestation.json"
            write_json(
                attestation_ref,
                {
                    "fixture_kind": "synthetic_non_authorizing_attestation",
                    "authority_effect": "none",
                },
            )
            attestation_digest = validator.file_digest(root / attestation_ref)
            horizons = sorted(
                row["horizon_id"]
                for row in validator.load_data("campaign.yaml")["chronological_horizons"]
            )
            units = [f"DMV3-SYNTHETIC-{horizon}" for horizon in horizons]

            snapshot_ref = "mesh/qualification-snapshots/synthetic-bootstrap.json"
            write_json(snapshot_ref, validator.load_data("mesh/qualification-registry.json"))
            identity_root = {
                "metadata": {
                    "object_type": "synthetic_human_identity_authority_root",
                    "trust_zone": "proposed",
                    "lifecycle_status": "test",
                    "provenance_note": "Synthetic and non-authorizing completion fixture.",
                    "reason_for_inclusion": "Exercise fail-closed identity binding only.",
                },
                "schema_version": "logos.doctrine-marathon.human-identity-authority-root.v3",
                "anchor_id": "DMV3-HUMAN-IDENTITY-AUTHORITY-ROOT",
                "active": True,
                "authorized_identity_issuer_ids": ["HUMAN-SYNTHETIC"],
                "authorized_signer_ids": ["HUMAN-SYNTHETIC"],
                "recorded_by_human": True,
                "created_by_ai": False,
                "protected_commit": "a" * 40,
                "anchor_digest": validator.ZERO_DIGEST,
            }
            identity_root["anchor_digest"] = validator.object_digest(
                identity_root, omit=("anchor_digest",)
            )
            write_json("graph/human-identity-authority-root.yaml", identity_root)
            qualification_scope = [
                "campaign_completion_approval",
                "qualification_approval",
            ]
            approver_qualification = {
                "schema_version": "logos.doctrine-marathon.approver-qualification.v3",
                "receipt_id": "QAPP-SYNTHETIC",
                "signer_id": "HUMAN-SYNTHETIC",
                "issuer_id": "HUMAN-SYNTHETIC",
                "qualification_scope": qualification_scope,
                "tradition_or_jurisdiction": "Synthetic completion test",
                "identity_root_anchor_digest": identity_root["anchor_digest"],
                "protected_commit": identity_root["protected_commit"],
                "evidence_bindings": [{
                    "ref": attestation_ref,
                    "digest": attestation_digest,
                }],
                "issued_at": "2026-08-27T18:00:00Z",
                "expires_at": "2026-08-27T22:00:00Z",
                "recorded_by_human": True,
                "created_by_ai": False,
                "receipt_digest": validator.ZERO_DIGEST,
            }
            approver_qualification["receipt_digest"] = validator.object_digest(
                approver_qualification, omit=("receipt_digest",)
            )
            approvers = [{
                "signer_id": "HUMAN-SYNTHETIC",
                "qualification_scope": qualification_scope,
                "tradition_or_jurisdiction": "Synthetic completion test",
                "qualification_receipt_ref": "approver-qualification:QAPP-SYNTHETIC",
                "qualification_receipt_digest": approver_qualification["receipt_digest"],
                "valid_from": "2026-08-27T18:00:00Z",
                "valid_until": "2026-08-27T22:00:00Z",
            }]
            approver_digest = validator.object_digest(approvers)

            definition_ref = "state/completion-definitions/synthetic.json"
            receipt_ref = "state/completion-receipts/synthetic.json"
            definition = {
                "schema_version": "logos.doctrine-marathon.campaign-completion-definition.v3",
                "definition_id": "DMV3-COMPDEF-SYNTHETIC",
                "required_horizon_ids": horizons,
                "required_work_unit_ids": units,
                "required_claim_ids": ["CLAIM-SYNTHETIC-COMPLETE"],
                "required_output_classes": ["synthetic_output"],
                "permitted_residual_risk_classes": [],
                "human_approval_receipt_ref": "human-decision:HDEC-COMPLETION-SYNTHETIC",
                "human_approval_receipt_digest": validator.ZERO_DIGEST,
                "authority_registry_digest": validator.ZERO_DIGEST,
                "effective_at": "2026-08-27T19:00:00Z",
                "expires_at": "2026-08-27T22:00:00Z",
                "definition_digest": validator.ZERO_DIGEST,
            }
            if mutation == "expired_definition":
                definition["expires_at"] = "2026-08-27T19:45:00Z"

            qualification_receipts: list[dict[str, Any]] = []
            human_decisions: list[dict[str, Any]] = []
            runtime_assignments: dict[str, list[dict[str, Any]]] = {}
            runtime_prompt_reviews_by_unit: dict[str, list[dict[str, Any]]] = {}
            runtime_reviewer_refs: dict[str, list[str]] = {}
            runtime_completeness_refs: dict[str, str] = {}
            for unit in units:
                bootstrap_writer = make_assignment(
                    unit, "BOOT", "WRITER", "task-local-role-factory", "writer",
                    "role_qualification_and_independence", "mesh/role-catalog.yaml", [],
                )
                bootstrap_meta = make_assignment(
                    unit, "BOOT", "META", "role-qualification-and-independence-auditor", "checker",
                    [
                        "prompt_alignment_and_authority",
                        "role_qualification_and_independence",
                    ], "mesh/completeness-auditor-v3.yaml",
                    [bootstrap_writer["assignment_id"]],
                )
                bootstrap_whole = make_assignment(
                    unit, "BOOT", "WHOLE", "independent-whole-work-checker", "checker",
                    [
                        "prompt_alignment_and_authority",
                        "role_qualification_and_independence",
                    ], "constitution.yaml",
                    [bootstrap_writer["assignment_id"]],
                )
                bootstrap_meta["checks_assignment_ids"] = sorted([
                    bootstrap_writer["assignment_id"],
                    bootstrap_whole["assignment_id"],
                ])
                bootstrap_whole["checks_assignment_ids"] = sorted([
                    bootstrap_writer["assignment_id"],
                    bootstrap_meta["assignment_id"],
                ])
                bootstrap_prompt_reviews = bind_runtime_prompt_reviews(
                    [bootstrap_writer, bootstrap_meta, bootstrap_whole], "BOOT"
                )
                support_ref = f"mesh/receipts/{unit.lower()}-qualification-support.json"
                support_bundle = seal_bundle(
                    [bootstrap_writer, bootstrap_meta, bootstrap_whole],
                    snapshot_ref,
                    prompt_reviews=bootstrap_prompt_reviews,
                )
                write_json(support_ref, support_bundle)

                runtime_writer = make_assignment(
                    unit, "RUN", "WRITER", "task-local-role-factory", "writer",
                    "role_qualification_and_independence", "mesh/role-catalog.yaml", [],
                )
                runtime_completeness = make_assignment(
                    unit, "RUN", "COMPLETE", "doctrine-mesh-completeness-auditor", "auditor",
                    "doctrine_mesh_completeness_and_gap_detection", "mesh/completeness-auditor-v3.yaml", [],
                )
                runtime_meta = make_assignment(
                    unit, "RUN", "META", "role-qualification-and-independence-auditor", "checker",
                    [
                        "doctrine_mesh_completeness_and_gap_detection",
                        "prompt_alignment_and_authority",
                        "quotation_context_and_entailment",
                        "role_qualification_and_independence",
                        "source_identity_locator_and_rights",
                    ], "mesh/role-assignment.schema.json",
                    [runtime_writer["assignment_id"]],
                )
                runtime_whole = make_assignment(
                    unit, "RUN", "WHOLE", "independent-whole-work-checker", "checker",
                    [
                        "prompt_alignment_and_authority",
                        "quotation_context_and_entailment",
                        "role_qualification_and_independence",
                        "source_identity_locator_and_rights",
                    ], "constitution.yaml",
                    [runtime_writer["assignment_id"]],
                )
                runtime_meta["checks_assignment_ids"] = sorted([
                    runtime_writer["assignment_id"],
                    runtime_completeness["assignment_id"],
                    runtime_whole["assignment_id"],
                ])
                runtime_whole["checks_assignment_ids"] = sorted([
                    runtime_writer["assignment_id"],
                    runtime_completeness["assignment_id"],
                    runtime_meta["assignment_id"],
                ])
                runtime_prompt_reviews = bind_runtime_prompt_reviews(
                    [runtime_writer, runtime_completeness, runtime_meta, runtime_whole],
                    "RUN",
                )
                for reviewer in (runtime_writer, runtime_completeness, runtime_meta, runtime_whole):
                    reviewer["qualification_basis"]["state"] = "qualified"
                    scope_digest = validator.role_assignment_qualification_scope_digest(reviewer)
                    decision = {
                        "schema_version": "logos.doctrine-marathon.human-decision-receipt.v3",
                        "receipt_id": f"HDEC-QUAL-{reviewer['assignment_id'].removeprefix('DMV3-ROLE-')}",
                        "decision_type": "qualification_approval",
                        "subject_ref": f"role-assignment:{reviewer['assignment_id']}",
                        "subject_digest": scope_digest,
                        "scope_digest": scope_digest,
                        "tradition_or_jurisdiction": "Synthetic completion test",
                        "signer_ids": ["HUMAN-SYNTHETIC"],
                        "signer_registry_digest": approver_digest,
                        "authority_scope": ["qualification:role_assignment"],
                        "decision": "approved",
                        "issued_at": "2026-08-27T18:40:00Z",
                        "expires_at": "2026-08-27T22:00:00Z",
                        "attestation_bindings": [{
                            "ref": attestation_ref,
                            "digest": attestation_digest,
                        }],
                        "recorded_by_human": True,
                        "created_by_ai": False,
                        "receipt_digest": validator.ZERO_DIGEST,
                    }
                    decision["receipt_digest"] = validator.object_digest(decision, omit=("receipt_digest",))
                    human_decisions.append(decision)
                    qrec = {
                        "schema_version": "logos.doctrine-marathon.qualification-receipt.v3",
                        "receipt_id": f"QREC-{reviewer['assignment_id'].removeprefix('DMV3-ROLE-')}",
                        "subject_kind": "role_assignment",
                        "subject_ref": f"role-assignment:{reviewer['assignment_id']}",
                        "subject_scope_digest": scope_digest,
                        "work_unit_id": unit,
                        "capability_ids": reviewer["capability_ids"],
                        "expert_pack_ref": None,
                        "expert_pack_digest": None,
                        "runtime_adapter_digest": reviewer["runtime_adapter_digest"],
                        "qualification_generation": 0,
                        "reviewer_evidence_role": "supporting_non_authorizing",
                        "bootstrap_authorization_ref": f"human-decision:{decision['receipt_id']}",
                        "bootstrap_authorization_digest": decision["receipt_digest"],
                        "qualification_input_digest": validator.ZERO_DIGEST,
                        "reviewer_assignment_bundle_ref": support_ref,
                        "reviewer_assignment_bundle_digest": validator.file_digest(root / support_ref),
                        "reviewer_assignment_refs": sorted([
                            f"role-assignment:{bootstrap_meta['assignment_id']}",
                            f"role-assignment:{bootstrap_whole['assignment_id']}",
                        ]),
                        "fixture_bindings": [{
                            "ref": "constitution.yaml",
                            "digest": validator.file_digest(root / "constitution.yaml"),
                            "result": "pass",
                        }],
                        "decision": "qualified",
                        "abstention_fixture_passed": True,
                        "independence_assessment": "independent",
                        "human_approval_receipt_ref": f"human-decision:{decision['receipt_id']}",
                        "human_approval_receipt_digest": decision["receipt_digest"],
                        "issued_at": "2026-08-27T18:50:00Z",
                        "expires_at": (
                            "2026-08-27T18:55:00Z"
                            if mutation == "expired_reviewer_qualification"
                            and unit == units[0]
                            and reviewer is runtime_meta
                            else "2026-08-27T21:00:00Z"
                        ),
                        "authority_effect": "none",
                        "receipt_digest": validator.ZERO_DIGEST,
                    }
                    qrec["qualification_input_digest"] = validator.object_digest({
                        key: qrec[key]
                        for key in (
                            "subject_kind", "subject_ref", "subject_scope_digest",
                            "work_unit_id", "capability_ids", "expert_pack_ref",
                            "expert_pack_digest", "runtime_adapter_digest",
                            "qualification_generation", "reviewer_evidence_role",
                            "bootstrap_authorization_ref", "bootstrap_authorization_digest",
                            "reviewer_assignment_bundle_ref", "reviewer_assignment_bundle_digest",
                            "reviewer_assignment_refs", "fixture_bindings",
                        )
                    })
                    qrec["receipt_digest"] = validator.object_digest(qrec, omit=("receipt_digest",))
                    qualification_receipts.append(qrec)
                    reviewer["qualification_receipt_ref"] = f"qualification-receipt:{qrec['receipt_id']}"
                    reviewer["qualification_receipt_digest"] = qrec["receipt_digest"]
                    reviewer["status"] = "qualified_for_unit"
                runtime_assignments[unit] = [
                    runtime_writer, runtime_completeness, runtime_meta, runtime_whole
                ]
                runtime_prompt_reviews_by_unit[unit] = runtime_prompt_reviews
                runtime_completeness_refs[unit] = (
                    f"role-assignment:{runtime_completeness['assignment_id']}"
                )
                runtime_reviewer_refs[unit] = sorted([
                    f"role-assignment:{runtime_meta['assignment_id']}",
                    f"role-assignment:{runtime_whole['assignment_id']}",
                ])

            completion_scope = validator.completion_scope_digest(definition)
            completion_decision = {
                "schema_version": "logos.doctrine-marathon.human-decision-receipt.v3",
                "receipt_id": "HDEC-COMPLETION-SYNTHETIC",
                "decision_type": "campaign_completion_approval",
                "subject_ref": "campaign-completion-scope:DMV3-COMPDEF-SYNTHETIC",
                "subject_digest": completion_scope,
                "scope_digest": completion_scope,
                "tradition_or_jurisdiction": "Synthetic completion test",
                "signer_ids": ["HUMAN-SYNTHETIC"],
                "signer_registry_digest": approver_digest,
                "authority_scope": ["campaign_completion:LOGOS-DOCTRINE-MARATHON-003"],
                "decision": "approved",
                "issued_at": "2026-08-27T19:30:00Z",
                "expires_at": "2026-08-27T22:00:00Z",
                "attestation_bindings": [{
                    "ref": attestation_ref,
                    "digest": attestation_digest,
                }],
                "recorded_by_human": True,
                "created_by_ai": False,
                "receipt_digest": validator.ZERO_DIGEST,
            }
            if mutation == "unrelated_human_decision":
                completion_decision["subject_ref"] = "unrelated:subject"
            completion_decision["receipt_digest"] = validator.object_digest(
                completion_decision, omit=("receipt_digest",)
            )
            human_decisions.append(completion_decision)
            authority = {
                "metadata": {
                    "object_type": "synthetic_authority_registry",
                    "trust_zone": "proposed",
                    "lifecycle_status": "test",
                    "provenance_note": "Synthetic completion regression fixture.",
                    "reason_for_inclusion": "Exercise qualification and completion human trust roots without normative authority.",
                },
                "schema_version": "logos.doctrine-marathon.authority-registry.v3",
                "registry_id": "DMV3-AUTHORITY-REGISTRY",
                "human_identity_authority_root_ref": "graph/human-identity-authority-root.yaml",
                "human_identity_authority_root_file_digest": validator.file_digest(
                    root / "graph/human-identity-authority-root.yaml"
                ),
                "human_identity_authority_root_anchor_digest": identity_root[
                    "anchor_digest"
                ],
                "approver_qualification_receipts": [approver_qualification],
                "qualified_approvers": approvers,
                "approver_set_digest": approver_digest,
                "human_decision_receipts": human_decisions,
                "normative_frames": [],
                "normative_authority_active": False,
                "current_normative_frame_ref": None,
                "current_normative_frame_digest": None,
                "registry_digest": validator.ZERO_DIGEST,
            }
            authority["registry_digest"] = validator.object_digest(authority, omit=("registry_digest",))
            write_json("graph/authority-registry.yaml", authority)
            definition["human_approval_receipt_digest"] = completion_decision["receipt_digest"]
            definition["authority_registry_digest"] = validator.file_digest(root / "graph/authority-registry.yaml")
            definition["definition_digest"] = validator.object_digest(definition, omit=("definition_digest",))
            write_json(definition_ref, definition)

            qualification_registry = {
                "metadata": {
                    "object_type": "synthetic_qualification_registry",
                    "trust_zone": "proposed",
                    "lifecycle_status": "test",
                    "provenance_note": "Synthetic completion regression fixture.",
                    "reason_for_inclusion": "Bind exact task-local reviewer qualifications for completion tests.",
                },
                "schema_version": "logos.doctrine-marathon.qualification-registry.v3",
                "runtime_records": True,
                "expert_packs": [],
                "qualification_receipts": qualification_receipts,
                "correlation_acceptance_receipts": [],
                "registry_digest": validator.ZERO_DIGEST,
            }
            qualification_registry["registry_digest"] = validator.object_digest(
                qualification_registry, omit=("registry_digest",)
            )
            write_json("mesh/qualification-registry.json", qualification_registry)

            runtime_bundles: dict[str, tuple[str, dict[str, Any]]] = {}
            for unit in units:
                bundle_ref = f"mesh/receipts/{unit.lower()}-runtime-reviewers.json"
                bundle = seal_bundle(
                    runtime_assignments[unit],
                    "mesh/qualification-registry.json",
                    prompt_reviews=runtime_prompt_reviews_by_unit[unit],
                )
                write_json(bundle_ref, bundle)
                runtime_bundles[unit] = (bundle_ref, bundle)

            graph = validator.load_data("graph/example-graph.json")
            for node in graph["nodes"]:
                if node["node_id"] == "DMV3-NORMATIVE-FRAME":
                    node["state"] = "blocked"
                    node["weakest_premise_state"] = "blocked"
                else:
                    node["state"] = "accepted"
                    node["weakest_premise_state"] = "not_applicable" if node["node_id"] == "DMV3-CONSTITUTION" else "accepted"
            for edge in graph["edges"]:
                edge["review_state"] = "accepted"
                if edge["edge_id"] == "DMV3-E-002":
                    qrec = qualification_receipts[0]
                    prerequisite = next(
                        row for row in graph["nodes"]
                        if row["node_id"] == edge["prerequisite_id"]
                    )
                    edge["basis_refs"] = [
                        prerequisite["content_ref"],
                        f"qualification-receipt:{qrec['receipt_id']}",
                    ]
                    edge["basis_digests"] = [
                        prerequisite["content_digest"],
                        qrec["receipt_digest"],
                    ]
                    edge["basis_observed_at"] = "2026-08-27T19:00:00Z"
            for unit in units:
                graph["nodes"].append({
                    "node_id": unit,
                    "revision_id": "synthetic",
                    "object_type": "synthetic_completed_work_unit",
                    "state": "accepted",
                    "authority_plane": "review",
                    "content_ref": output_ref,
                    "content_digest": output_digest,
                    "weakest_premise_state": "not_applicable",
                    "derived_authority_taints": ["review"],
                    "normative_frame_ref": None,
                    "normative_frame_digest": None,
                })
            graph["reverse_consumer_index"] = validator.derived_reverse_index(graph)
            graph["graph_digest"] = validator.object_digest(graph, omit=("graph_digest",))
            write_json("graph/example-graph.json", graph)
            write_json("debt/initial-review-debt.json", [])

            evidence_unit = units[0]
            evidence_bundle_ref, evidence_bundle = runtime_bundles[evidence_unit]
            evidence_reviewers = runtime_reviewer_refs[evidence_unit]
            evidence_assignment_map = {
                f"role-assignment:{row['assignment_id']}": row
                for row in evidence_bundle["assignments"]
            }
            evidence_producer_ref = next(
                ref for ref, row in evidence_assignment_map.items()
                if row["assignment_kind"] == "writer"
            )

            def evidence_review(
                receipt_id: str,
                review_kind: str,
                subject_ref: str,
                subject_scope_digest: str,
                decision: str,
                bindings: list[dict[str, str]],
            ) -> dict[str, Any]:
                value = {
                    "schema_version": "logos.doctrine-marathon.evidence-review-receipt.v3",
                    "receipt_id": receipt_id,
                    "review_kind": review_kind,
                    "subject_ref": subject_ref,
                    "subject_scope_digest": subject_scope_digest,
                    "work_unit_id": evidence_unit,
                    "assignment_bundle_ref": evidence_bundle_ref,
                    "assignment_bundle_digest": validator.file_digest(root / evidence_bundle_ref),
                    "producer_assignment_ref": evidence_producer_ref,
                    "producer_assignment_digest": validator.object_digest(
                        evidence_assignment_map[evidence_producer_ref]
                    ),
                    "reviewer_assignment_refs": evidence_reviewers,
                    "required_capability_ids": {
                        "source_qualification": ["source_identity_locator_and_rights"],
                        "translation_fidelity": ["original_language_and_translation_fidelity"],
                        "influence_hypothesis": ["counterevidence_and_alternative_hypotheses"],
                        "historical_attribution": [
                            "quotation_context_and_entailment",
                            "tradition_representation",
                        ],
                        "claim_entailment_context": ["quotation_context_and_entailment"],
                    }[review_kind],
                    "review_dimensions": ["context", "identity", "scope"],
                    "evidence_bindings": sorted(bindings, key=lambda item: item["ref"]),
                    "decision": decision,
                    "independence_assessment": "independent",
                    "correlation_acceptance_receipt_ref": None,
                    "issued_at": "2026-08-27T19:35:00Z",
                    "expires_at": "2026-08-27T21:00:00Z",
                    "authority_effect": "none",
                    "receipt_digest": validator.ZERO_DIGEST,
                }
                value["receipt_digest"] = validator.object_digest(value, omit=("receipt_digest",))
                return value

            source = qualified_source()
            source["content_digest"] = output_digest
            source["observed_at"] = "2026-08-27T19:00:00Z"
            source["qualification_scope_digest"] = validator.source_qualification_scope_digest(source)
            source_review = evidence_review(
                "EREV-SYNTHETIC-SOURCE",
                "source_qualification",
                "source-record:SRC-SYNTHETIC-A",
                source["qualification_scope_digest"],
                "qualified",
                [
                    {"ref": "source-record:SRC-SYNTHETIC-A", "digest": source["qualification_scope_digest"]},
                    {"ref": output_ref, "digest": output_digest},
                ],
            )
            if mutation == "unresolved_evidence_binding":
                source_review["evidence_bindings"][1] = {
                    "ref": "missing/synthetic-evidence.json",
                    "digest": validator.ZERO_DIGEST,
                }
                source_review["evidence_bindings"] = sorted(
                    source_review["evidence_bindings"], key=lambda item: item["ref"]
                )
                source_review["receipt_digest"] = validator.object_digest(
                    source_review, omit=("receipt_digest",)
                )
            if mutation == "missing_review_capability":
                source_review["required_capability_ids"] = [
                    "archaeology_epigraphy_numismatics_and_material_culture"
                ]
                source_review["receipt_digest"] = validator.object_digest(
                    source_review, omit=("receipt_digest",)
                )
            source["qualification_receipt_refs"] = ["evidence-review:EREV-SYNTHETIC-SOURCE"]
            source["qualification_receipt_digests"] = [source_review["receipt_digest"]]
            source["record_digest"] = validator.object_digest(source, omit=("record_digest",))

            claim = claim_candidate("synthesis", "verified")
            claim["claim_id"] = "CLAIM-SYNTHETIC-COMPLETE"
            claim["source_bindings"] = [{
                "source_record_ref": "source-record:SRC-SYNTHETIC-A",
                "source_content_digest": source["content_digest"],
                "source_record_digest": source["record_digest"],
                "exact_locator_refs": ["test:1"],
            }]
            claim_scope = validator.evidence_review_scope_digest(claim, "claim-record")
            claim_review = evidence_review(
                "EREV-SYNTHETIC-CLAIM",
                "claim_entailment_context",
                "claim-record:CLAIM-SYNTHETIC-COMPLETE",
                claim_scope,
                "accepted",
                [
                    {"ref": "claim-record:CLAIM-SYNTHETIC-COMPLETE", "digest": claim_scope},
                    {"ref": "source-record:SRC-SYNTHETIC-A", "digest": source["record_digest"]},
                ],
            )
            claim["review_receipt_refs"] = ["evidence-review:EREV-SYNTHETIC-CLAIM"]
            claim["review_receipt_digests"] = [claim_review["receipt_digest"]]
            claim["evidence_digest"] = validator.object_digest(claim, omit=("evidence_digest",))
            evidence_registry = evidence_registry_candidate(
                sources=[source], claims=[claim], reviews=[source_review, claim_review]
            )
            write_json("evidence/evidence-registry.json", evidence_registry)

            checkpoint_ref = "state/examples/initial-resume-checkpoint.json"
            checkpoint = validator.load_data(checkpoint_ref)
            checkpoint_digest = validator.file_digest(root / checkpoint_ref)

            events: list[dict[str, Any]] = []
            event_refs: dict[str, dict[str, str]] = {}

            def append_event(event_type: str, affected_ids: list[str], details: dict[str, Any]) -> dict[str, Any]:
                sequence = len(events) + 1
                occurred_at = f"2026-08-27T19:{sequence:02d}:00Z"
                event = {
                    "event_id": f"DMV3-EVENT-{sequence:04d}",
                    "sequence": sequence,
                    "occurred_at": occurred_at,
                    "event_type": event_type,
                    "actor_id": "SYNTHETIC-COMPLETION-TEST",
                    "input_digest": output_digest,
                    "affected_ids": sorted(affected_ids),
                    "authority_ref": f"review-receipt:{details.get('review_receipt_id')}" if event_type == "check_completed" else "synthetic:test-only",
                    "details": details,
                    "prior_event_hash": None,
                    "event_hash": validator.ZERO_DIGEST,
                }
                events.append(event)
                return event

            for unit in units:
                append_event("work_unit_classified", [unit], {})
                bundle_ref, bundle = runtime_bundles[unit]
                bundle_digest = validator.file_digest(root / bundle_ref)
                assignment_map = {
                    f"role-assignment:{row['assignment_id']}": row
                    for row in bundle["assignments"]
                }
                completeness_ref = runtime_completeness_refs[unit]
                completeness_assignment = assignment_map[completeness_ref]
                capabilities = [
                    "doctrine_mesh_completeness_and_gap_detection",
                    "prompt_alignment_and_authority",
                    "role_qualification_and_independence",
                ]
                entry_details = {
                    "coverage_input_digest": output_digest,
                    "requirement_and_assignment_refs": ["synthetic:requirements"],
                    "completeness_assignment_bundle_ref": bundle_ref,
                    "completeness_assignment_bundle_digest": bundle_digest,
                    "completeness_assignment_ref": completeness_ref,
                    "completeness_assignment_digest": validator.object_digest(
                        completeness_assignment
                    ),
                    "required_capability_ids": capabilities,
                    "requirement_set_digest": validator.ZERO_DIGEST,
                }
                entry_details["requirement_set_digest"] = validator.object_digest({
                    key: entry_details[key]
                    for key in (
                        "coverage_input_digest",
                        "requirement_and_assignment_refs",
                        "completeness_assignment_bundle_ref",
                        "completeness_assignment_bundle_digest",
                        "completeness_assignment_ref",
                        "completeness_assignment_digest",
                        "required_capability_ids",
                    )
                })
                requirement_event = append_event(
                    "completeness_entry", [unit], entry_details
                )
                review_sequence = len(events) + 1
                reviewed_at = f"2026-08-27T19:{review_sequence:02d}:00Z"
                reviewer_refs = runtime_reviewer_refs[unit]
                producer_ref = next(
                    ref
                    for ref, row in assignment_map.items()
                    if row["assignment_kind"] == "writer"
                )
                producer = assignment_map[producer_ref]
                dimensions = ["authority_boundary", "completeness", "output_integrity"]
                requirements_digest = validator.object_digest({
                    "required_capability_ids": capabilities,
                    "review_dimensions": dimensions,
                })
                evidence_bindings = [{"ref": output_ref, "digest": output_digest}]
                evidence_set_digest = validator.object_digest(evidence_bindings)
                reviewer_decisions = []
                for reviewer_ref in reviewer_refs:
                    reviewer = assignment_map[reviewer_ref]
                    decision = {
                        "reviewer_assignment_ref": reviewer_ref,
                        "reviewer_assignment_digest": validator.object_digest(reviewer),
                        "reviewer_actor_instance_id": reviewer["actor_instance_id"],
                        "reviewer_attempt_id": reviewer["attempt_id"],
                        "reviewed_output_digest": output_digest,
                        "requirement_event_hash": validator.ZERO_DIGEST,
                        "review_requirements_digest": requirements_digest,
                        "evidence_set_digest": evidence_set_digest,
                        "decision": "accepted",
                        "decided_at": reviewed_at,
                        "expires_at": "2026-08-27T21:00:00Z",
                        "review_digest": validator.ZERO_DIGEST,
                    }
                    decision["review_digest"] = validator.object_digest(decision, omit=("review_digest",))
                    reviewer_decisions.append(decision)
                review_details = {
                    "review_receipt_id": f"DMV3-REVIEW-{unit.removeprefix('DMV3-')}",
                    "reviewed_output_ref": output_ref,
                    "reviewed_output_digest": output_digest,
                    "requirement_event_id": requirement_event["event_id"],
                    "requirement_event_hash": validator.ZERO_DIGEST,
                    "assignment_bundle_ref": bundle_ref,
                    "assignment_bundle_digest": bundle_digest,
                    "producer_assignment_ref": producer_ref,
                    "producer_assignment_digest": validator.object_digest(producer),
                    "reviewer_assignment_refs": reviewer_refs,
                    "required_capability_ids": capabilities,
                    "review_dimensions": dimensions,
                    "review_requirements_digest": requirements_digest,
                    "evidence_bindings": evidence_bindings,
                    "evidence_set_digest": evidence_set_digest,
                    "reviewer_decisions": reviewer_decisions,
                    "decision": "accepted",
                    "reviewed_at": reviewed_at,
                    "review_authority_effect": "none",
                    "review_receipt_digest": validator.ZERO_DIGEST,
                }
                review_details["review_receipt_digest"] = validator.check_completed_scope_digest(review_details)
                review_event = append_event("check_completed", [unit], review_details)
                exit_details = {
                    "final_output_digest": output_digest,
                    "independently_rederived_requirements": True,
                    "discovered_gap_and_replay_refs": [],
                    "completeness_assignment_bundle_ref": bundle_ref,
                    "completeness_assignment_bundle_digest": bundle_digest,
                    "completeness_assignment_ref": completeness_ref,
                    "completeness_assignment_digest": validator.object_digest(
                        completeness_assignment
                    ),
                    "required_capability_ids": capabilities,
                    "requirement_set_digest": validator.ZERO_DIGEST,
                }
                exit_details["requirement_set_digest"] = validator.object_digest({
                    key: exit_details[key]
                    for key in (
                        "final_output_digest",
                        "independently_rederived_requirements",
                        "discovered_gap_and_replay_refs",
                        "completeness_assignment_bundle_ref",
                        "completeness_assignment_bundle_digest",
                        "completeness_assignment_ref",
                        "completeness_assignment_digest",
                        "required_capability_ids",
                    )
                })
                exit_event = append_event(
                    "completeness_exit", [unit], exit_details
                )
                event_refs[unit] = {
                    "requirement": requirement_event["event_id"],
                    "review": review_event["event_id"],
                    "exit": exit_event["event_id"],
                }
            append_event("checkpoint_frozen", units, {"checkpoint_digest": checkpoint_digest})
            append_event("terminal_handoff", units, {
                "checkpoint_digest": checkpoint_digest,
                "terminal_status": "CAMPAIGN_COMPLETE",
                "exact_next_prompt_or_explicit_none_if_complete": None,
            })
            ledger = {
                "metadata": {
                    "object_type": "synthetic_completion_event_ledger",
                    "trust_zone": "proposed",
                    "lifecycle_status": "test",
                    "provenance_note": "Synthetic in-memory completion regression fixture.",
                    "reason_for_inclusion": "Prove terminal evidence bindings reject sealed fabrications.",
                },
                "schema_version": "logos.doctrine_marathon.event-ledger.v3",
                "campaign_id": "LOGOS-DOCTRINE-MARATHON-003",
                "runtime_events": True,
                "append_only": True,
                "ledger_generation": 0,
                "prior_snapshot": None,
                "event_count": 0,
                "last_event_hash": None,
                "events": events,
                "ledger_hash": validator.ZERO_DIGEST,
            }
            def bind_requirement_hashes() -> None:
                """Seal requirement events before each dependent review, in order."""
                seal_ledger(ledger)
                for bound_unit in units:
                    ledger_by_id = {
                        row["event_id"]: row for row in ledger["events"]
                    }
                    requirement_hash = ledger_by_id[
                        event_refs[bound_unit]["requirement"]
                    ]["event_hash"]
                    review = ledger_by_id[event_refs[bound_unit]["review"]]
                    review["details"]["requirement_event_hash"] = requirement_hash
                    for decision in review["details"]["reviewer_decisions"]:
                        decision["requirement_event_hash"] = requirement_hash
                        decision["review_digest"] = validator.object_digest(
                            decision, omit=("review_digest",)
                        )
                    review["details"]["review_receipt_digest"] = (
                        validator.check_completed_scope_digest(review["details"])
                    )
                    seal_ledger(ledger)

            bind_requirement_hashes()
            if mutation == "self_attested_completion_review":
                review = next(row for row in ledger["events"] if row["event_type"] == "check_completed")
                review["details"] = {}
                review["authority_ref"] = "synthetic:self-attested"
                seal_ledger(ledger)
            if mutation == "forged_reviewer_decision":
                review = next(row for row in ledger["events"] if row["event_type"] == "check_completed")
                decision = review["details"]["reviewer_decisions"][0]
                decision["reviewer_actor_instance_id"] = "SYNTHETIC-FORGED-ACTOR"
                decision["review_digest"] = validator.object_digest(
                    decision, omit=("review_digest",)
                )
                review["details"]["review_receipt_digest"] = validator.check_completed_scope_digest(
                    review["details"]
                )
                seal_ledger(ledger)
            if mutation == "weakened_review_requirement_set":
                review = next(
                    row for row in ledger["events"]
                    if row["event_type"] == "check_completed"
                )
                review["details"]["required_capability_ids"] = [
                    "prompt_alignment_and_authority"
                ]
                review["details"]["review_requirements_digest"] = validator.object_digest({
                    "required_capability_ids": review["details"]["required_capability_ids"],
                    "review_dimensions": review["details"]["review_dimensions"],
                })
                for decision in review["details"]["reviewer_decisions"]:
                    decision["review_requirements_digest"] = review["details"][
                        "review_requirements_digest"
                    ]
                bind_requirement_hashes()
            if mutation == "forged_producer_assignment":
                review = next(
                    row for row in ledger["events"]
                    if row["event_type"] == "check_completed"
                )
                unit = review["affected_ids"][0]
                bundle = runtime_bundles[unit][1]
                assignment_map = {
                    f"role-assignment:{row['assignment_id']}": row
                    for row in bundle["assignments"]
                }
                forged_ref = runtime_completeness_refs[unit]
                review["details"]["producer_assignment_ref"] = forged_ref
                review["details"]["producer_assignment_digest"] = validator.object_digest(
                    assignment_map[forged_ref]
                )
                bind_requirement_hashes()
            if mutation == "wrong_completeness_auditor_assignment":
                entry = next(
                    row for row in ledger["events"]
                    if row["event_type"] == "completeness_entry"
                )
                unit = entry["affected_ids"][0]
                bundle = runtime_bundles[unit][1]
                writer = next(
                    row for row in bundle["assignments"]
                    if row["assignment_kind"] == "writer"
                )
                entry["details"]["completeness_assignment_ref"] = (
                    f"role-assignment:{writer['assignment_id']}"
                )
                entry["details"]["completeness_assignment_digest"] = (
                    validator.object_digest(writer)
                )
                entry["details"]["requirement_set_digest"] = validator.object_digest({
                    key: entry["details"][key]
                    for key in (
                        "coverage_input_digest",
                        "requirement_and_assignment_refs",
                        "completeness_assignment_bundle_ref",
                        "completeness_assignment_bundle_digest",
                        "completeness_assignment_ref",
                        "completeness_assignment_digest",
                        "required_capability_ids",
                    )
                })
                bind_requirement_hashes()
            if mutation == "wrong_exit_completeness_auditor_assignment":
                exit_event = next(
                    row for row in ledger["events"]
                    if row["event_type"] == "completeness_exit"
                )
                unit = exit_event["affected_ids"][0]
                bundle = runtime_bundles[unit][1]
                writer = next(
                    row for row in bundle["assignments"]
                    if row["assignment_kind"] == "writer"
                )
                exit_event["details"]["completeness_assignment_ref"] = (
                    f"role-assignment:{writer['assignment_id']}"
                )
                exit_event["details"]["completeness_assignment_digest"] = (
                    validator.object_digest(writer)
                )
                exit_event["details"]["requirement_set_digest"] = (
                    validator.object_digest({
                        key: exit_event["details"][key]
                        for key in (
                            "final_output_digest",
                            "independently_rederived_requirements",
                            "discovered_gap_and_replay_refs",
                            "completeness_assignment_bundle_ref",
                            "completeness_assignment_bundle_digest",
                            "completeness_assignment_ref",
                            "completeness_assignment_digest",
                            "required_capability_ids",
                        )
                    })
                )
                bind_requirement_hashes()
            write_json("events/event-ledger.json", ledger)

            rows = []
            ledger_by_id = {row["event_id"]: row for row in ledger["events"]}
            for horizon, unit in zip(horizons, units):
                review_id = event_refs[unit]["review"]
                exit_id = event_refs[unit]["exit"]
                rows.append({
                    "unit_id": unit,
                    "horizon_id": horizon,
                    "output_class": "synthetic_output",
                    "terminal_output_ref": output_ref,
                    "terminal_output_digest": output_digest,
                    "exit_audit_event_id": exit_id,
                    "exit_audit_event_hash": ledger_by_id[exit_id]["event_hash"],
                    "qualified_review_event_ids": [review_id],
                    "status": "accepted",
                })
            if mutation == "nonexistent_review_event":
                rows[0]["qualified_review_event_ids"] = ["DMV3-EVENT-9999"]
            if mutation == "fabricated_output_digest":
                rows[0]["terminal_output_digest"] = validator.ZERO_DIGEST
            receipt = {
                "schema_version": "logos.doctrine-marathon.campaign-completion-receipt.v3",
                "receipt_id": "DMV3-COMPREC-SYNTHETIC",
                "definition_ref": definition_ref,
                "definition_digest": definition["definition_digest"],
                "checkpoint_ref": checkpoint_ref,
                "checkpoint_digest": checkpoint_digest,
                "completed_at": "2026-08-27T20:00:00Z",
                "ledger_snapshot_ref": "events/event-ledger.json",
                "ledger_snapshot_digest": validator.file_digest(root / "events/event-ledger.json"),
                "ledger_prefix_event_hash": ledger["last_event_hash"],
                "graph_snapshot_ref": "graph/example-graph.json",
                "graph_snapshot_digest": validator.file_digest(root / "graph/example-graph.json"),
                "debt_registry_ref": "debt/initial-review-debt.json",
                "debt_registry_digest": validator.file_digest(root / "debt/initial-review-debt.json"),
                "evidence_registry_ref": "evidence/evidence-registry.json",
                "evidence_registry_digest": validator.file_digest(root / "evidence/evidence-registry.json"),
                "unit_completion_rows": rows,
                "open_blocking_debt_ids": [],
                "open_high_risk_debt_ids": [],
                "nonfresh_load_bearing_node_ids": [],
                "unresolved_required_claim_ids": [],
                "human_completion_decision_ref": "human-decision:HDEC-COMPLETION-SYNTHETIC",
                "human_completion_decision_digest": completion_decision["receipt_digest"],
                "status": "pass",
                "receipt_digest": validator.ZERO_DIGEST,
            }
            if mutation == "fabricated_snapshot_digest":
                receipt["graph_snapshot_digest"] = validator.ZERO_DIGEST
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
            write_json(receipt_ref, receipt)

            terminal = copy.deepcopy(validator.load_data("state/examples/terminal-handoff-blocked.json"))
            terminal.update({
                "status": "CAMPAIGN_COMPLETE",
                "completed_unit_ids": units,
                "blocked_gate_ids": [],
                "residual_risks": [],
                "completion_definition_ref": definition_ref,
                "completion_definition_digest": validator.file_digest(root / definition_ref),
                "completion_receipt_ref": receipt_ref,
                "completion_receipt_digest": validator.file_digest(root / receipt_ref),
                "next_prompt": None,
            })
            return validator.validate_terminal_handoff(terminal)
        finally:
            clear_validator_caches()


def synthetic_assignment(
    root: Path,
    *,
    assignment_id: str,
    unit: str,
    role_id: str,
    assignment_kind: str,
    capability_ids: list[str],
    control_ref: str,
    checks: list[str],
) -> dict[str, Any]:
    control_digest = validator.file_digest(root / control_ref)
    source_order = [{
        "ordinal": 1,
        "source_ref": control_ref,
        "source_digest": control_digest,
        "source_class": "control_contract",
    }]
    guides = [{
        "guide_ref": control_ref,
        "guide_digest": control_digest,
        "usage": "instruction_context",
        "used_as_evidence": False,
    }]
    runtime_adapter = {
        "adapter_id": f"SYNTHETIC-{assignment_id}-ADAPTER",
        "runtime_family": f"synthetic-{assignment_id.lower()}-runtime",
        "model_revision": f"synthetic-{assignment_id.lower()}-revision",
        "capability_tier": (
            "frontier_reasoning" if assignment_kind == "checker" else "balanced"
        ),
        "reasoning_effort": "synthetic",
        "tool_profile_digest": validator.object_digest({"tool": assignment_id}),
        "context_digest": validator.object_digest({"context": assignment_id}),
        "receipt_ref": f"synthetic:attempt:{assignment_id}",
    }
    return {
        "schema_version": "logos.doctrine-marathon.role-assignment.v3",
        "assignment_id": assignment_id,
        "work_unit_id": unit,
        "assignment_kind": assignment_kind,
        "role_id": role_id,
        "capability_ids": sorted(set(capability_ids)),
        "qualification_basis": {
            "kind": "control_contract",
            "ref": control_ref,
            "digest": control_digest,
            "state": "candidate",
        },
        "expected_information_gain": (
            "Provide bounded synthetic validation evidence for one declared error "
            "class without source, runtime, theological, or publication authority."
        ),
        "qualification_receipt_ref": None,
        "qualification_receipt_digest": None,
        "task_prompt_ref": None,
        "task_prompt_digest": None,
        "prompt_neutrality_review_ref": None,
        "prompt_neutrality_review_digest": None,
        "attempt_id": f"SYNTHETIC-ATTEMPT-{assignment_id}",
        "actor_instance_id": f"SYNTHETIC-ACTOR-{assignment_id}",
        "checks_assignment_ids": sorted(checks),
        "source_order": source_order,
        "source_order_digest": validator.object_digest(source_order),
        "knowledge_guide_lineage": guides,
        "knowledge_guide_lineage_digest": validator.object_digest(guides),
        "runtime_adapter": runtime_adapter,
        "runtime_adapter_digest": validator.object_digest(runtime_adapter),
        "independence": {
            "answer_context_exposure": "none",
            "prompt_author_ids": [f"SYNTHETIC-PROMPT-AUTHOR-{assignment_id}"],
            "correlation_disclosures": [],
            "assessment": "independent",
            "human_acceptance_receipt_ref": None,
        },
        "expires_with_work_unit": True,
        "status": "candidate",
    }


def bind_synthetic_prompt_reviews(
    root: Path, assignments: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    meta = next(
        row for row in assignments
        if row["role_id"] == "role-qualification-and-independence-auditor"
    )
    whole = next(
        row for row in assignments
        if row["role_id"] == "independent-whole-work-checker"
    )
    for assignment in assignments:
        prompt_ref = f"mesh/task-prompts/{assignment['assignment_id'].lower()}.md"
        prompt_path = root / prompt_ref
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(
            "Inspect the synthetic inputs independently, seek counterevidence, "
            "and abstain when support is insufficient. This grants no authority.\n",
            encoding="utf-8",
        )
        assignment["task_prompt_ref"] = prompt_ref
        assignment["task_prompt_digest"] = validator.file_digest(prompt_path)
    dimensions = sorted({
        "presupposed_conclusion",
        "framing",
        "omitted_alternatives",
        "counterevidence_route",
        "abstention_path",
        "authority_transfer",
    })
    contract_ref = "firewall/prompt-neutrality-contract.yaml"
    contract_digest = validator.file_digest(root / contract_ref)
    reviews: list[dict[str, Any]] = []
    for assignment in assignments:
        reviewer = meta if assignment is whole else whole
        assert assignment["assignment_id"] in reviewer["checks_assignment_ids"]
        review_id = f"PNR-{assignment['assignment_id'].removeprefix('DMV3-ROLE-')}"
        review = {
            "schema_version": "logos.doctrine-marathon.prompt-neutrality-review.v3",
            "review_id": review_id,
            "subject_assignment_ref": f"role-assignment:{assignment['assignment_id']}",
            "subject_assignment_scope_digest": (
                validator.prompt_review_assignment_scope_digest(assignment)
            ),
            "task_prompt_ref": assignment["task_prompt_ref"],
            "task_prompt_digest": assignment["task_prompt_digest"],
            "neutrality_contract_ref": contract_ref,
            "neutrality_contract_digest": contract_digest,
            "reviewer_assignment_ref": f"role-assignment:{reviewer['assignment_id']}",
            "review_dimensions": dimensions,
            "decision": "accepted",
            "reviewed_at": "2026-08-27T18:30:00Z",
            "expires_at": "2026-08-27T21:00:00Z",
            "authority_effect": "none",
            "receipt_digest": validator.ZERO_DIGEST,
        }
        review["receipt_digest"] = validator.object_digest(
            review, omit=("receipt_digest",)
        )
        assignment["prompt_neutrality_review_ref"] = (
            f"prompt-neutrality-review:{review_id}"
        )
        assignment["prompt_neutrality_review_digest"] = review["receipt_digest"]
        reviews.append(review)
    return reviews


def seal_synthetic_bundle(
    root: Path,
    assignments: list[dict[str, Any]],
    *,
    bundle_id: str,
    fixture_kind: str,
    prompt_reviews: list[dict[str, Any]] | None = None,
    registry_ref: str = "mesh/qualification-registry.json",
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": "logos.doctrine-marathon.role-assignment-bundle.v3",
        "bundle_id": bundle_id,
        "work_unit_id": assignments[0]["work_unit_id"],
        "issued_at": "2026-08-27T18:20:00Z",
        "expires_at": "2026-08-27T21:00:00Z",
        "fixture_kind": fixture_kind,
        "runtime_assignments": fixture_kind == "runtime_receipt",
        "authority_effect": "none",
        "qualification_registry_ref": registry_ref,
        "qualification_registry_digest": validator.file_digest(root / registry_ref),
        "assignments": assignments,
        "prompt_neutrality_reviews": prompt_reviews or [],
        "bundle_digest": validator.ZERO_DIGEST,
    }
    value["bundle_digest"] = validator.object_digest(value, omit=("bundle_digest",))
    return value


def synthetic_three_role_assignments(
    root: Path, unit: str, prefix: str
) -> list[dict[str, Any]]:
    writer_id = f"DMV3-ROLE-{prefix}-WRITER"
    meta_id = f"DMV3-ROLE-{prefix}-META"
    whole_id = f"DMV3-ROLE-{prefix}-WHOLE"
    writer = synthetic_assignment(
        root,
        assignment_id=writer_id,
        unit=unit,
        role_id="task-local-role-factory",
        assignment_kind="writer",
        capability_ids=["role_qualification_and_independence"],
        control_ref="mesh/role-catalog.yaml",
        checks=[],
    )
    meta = synthetic_assignment(
        root,
        assignment_id=meta_id,
        unit=unit,
        role_id="role-qualification-and-independence-auditor",
        assignment_kind="checker",
        capability_ids=[
            "prompt_alignment_and_authority",
            "quotation_context_and_entailment",
            "role_qualification_and_independence",
            "source_identity_locator_and_rights",
        ],
        control_ref="mesh/role-assignment.schema.json",
        checks=[writer_id, whole_id],
    )
    whole = synthetic_assignment(
        root,
        assignment_id=whole_id,
        unit=unit,
        role_id="independent-whole-work-checker",
        assignment_kind="checker",
        capability_ids=[
            "prompt_alignment_and_authority",
            "quotation_context_and_entailment",
            "role_qualification_and_independence",
            "source_identity_locator_and_rights",
        ],
        control_ref="constitution.yaml",
        checks=[writer_id, meta_id],
    )
    return [writer, meta, whole]


def role_contract_fixture_errors(mutation: str) -> list[str]:
    with isolated_validator_root("dmv3-role-contract-") as root:
        bundle = copy.deepcopy(load("mesh/examples/design-time-independence-fixture.json"))
        baseline = validator.validate_role_assignments(
            bundle, load("mesh/agent-mesh.v3.json"), final=False
        )
        assert not baseline, baseline
        meta = next(
            row for row in bundle["assignments"]
            if row["role_id"] == "role-qualification-and-independence-auditor"
        )
        whole = next(
            row for row in bundle["assignments"]
            if row["role_id"] == "independent-whole-work-checker"
        )
        if mutation == "missing_role_capability":
            whole["capability_ids"].remove("role_qualification_and_independence")
        elif mutation == "meta_coverage":
            meta["checks_assignment_ids"].remove(whole["assignment_id"])
        elif mutation == "whole_checks_meta":
            whole["checks_assignment_ids"].remove(meta["assignment_id"])
        else:
            raise AssertionError(mutation)
        bundle["bundle_digest"] = validator.object_digest(
            bundle, omit=("bundle_digest",)
        )
        return validator.validate_role_assignments(
            bundle, load("mesh/agent-mesh.v3.json"), final=False
        )


def completeness_contract_fixture_errors(mutation: str) -> list[str]:
    value = copy.deepcopy(load("mesh/completeness-auditor-v3.yaml"))
    if mutation == "required_facet":
        value["deterministic_input_feature_vector"]["required_facets"].remove(
            "downstream_consumers"
        )
    elif mutation == "canonicalization":
        value["deterministic_input_feature_vector"]["canonicalization"] = (
            "implementation_defined"
        )
    elif mutation == "phase_receipt_binding":
        value["phase_receipt_binding"].pop("completed_check_requires")
    elif mutation == "nonmaterial_recovery":
        value["postflight_recovery"].pop("nonmaterial_missing_role")
    elif mutation == "hard_fail_code":
        value["hard_fail_codes"].remove("DMCA_MISSING_REVERSE_CONSUMER_QUARANTINE")
    else:
        raise AssertionError(mutation)
    return validator.validate_completeness(value)


def core_contract_fixture_errors(target: str) -> list[str]:
    """Mutate one previously under-validated load-bearing contract field."""
    if target == "constitution":
        value = copy.deepcopy(load("constitution.yaml"))
        value.pop("human_gates")
        return validator.validate_constitution(value)
    if target == "campaign":
        value = copy.deepcopy(load("campaign.yaml"))
        value["fresh_context_max_age_days"] = 30
        return validator.validate_campaign(value)
    if target == "mesh":
        value = copy.deepcopy(load("mesh/agent-mesh.v3.json"))
        value["one_writer_per_artifact"] = False
        return validator.validate_mesh(value, load("mesh/role-catalog.yaml"))
    if target == "prompt_neutrality":
        with isolated_validator_root("dmv3-prompt-neutrality-contract-") as root:
            value = copy.deepcopy(load("firewall/prompt-neutrality-contract.yaml"))
            value["required_neutral_verbs"] = ["prove"]
            path = root / "firewall/prompt-neutrality-contract.yaml"
            path.write_text(
                validator.yaml.safe_dump(value, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            text = (root / "DOCTRINE_MARATHON_MASTER_PROMPT.md").read_text(
                encoding="utf-8"
            )
            return validator.validate_prompt(text)
    raise AssertionError(target)


def test_legacy_adversarial_harness_cannot_authorize_release() -> None:
    assert validator.validate_adversarial_harness_migration(final=False) == []
    errors = validator.validate_adversarial_harness_migration(final=True)
    assert errors == [
        "adversarial_harness_release_gate: V3 cannot release until the aggregate "
        "exact-oracle migration is complete and independently reviewed"
    ]

    migration = load("checks/adversarial-harness-migration.yaml")
    inventory = migration["case_inventory"]
    assert migration["public_maturity"] == "blocked_specification_only"
    assert migration["root_control"] == {
        "portable_core_revision": "dad.deterministic_adversarial_harness.v4",
        "registry_discovery_contract_revision": "dad.harness_registry_discovery.v3",
        "receipt_index_contract_revision": "dad.harness_receipt_index.v2",
        "independent_review": "PASS_ACTIVATE",
        "repository_registry_bound": False,
        "repository_adapter_bound": False,
        "ci_provider_installation_verified": False,
    }
    assert inventory["component_inventory_case_count"] == 197
    assert inventory["aggregate_sentinel_case_count"] == 4
    assert inventory["total_executable_rows_across_catalogs"] == 201
    assert inventory["unique_source_case_count"] == 197
    assert inventory["sentinel_count_is_subset_not_inventory_addend"] is True
    assert inventory["portable_v4_conforming_receipt_count"] == 0
    assert inventory["release_evidence_case_count"] == 0


def test_public_status_is_bound_to_the_exact_blocked_migration_gate() -> None:
    status = load("transparency/public-status.json")
    assert validator.validate_public_status(status, final=False) == []
    assert validator.validate_public_status(status, final=True) == []
    assert status["maturity"] == "blocked_specification_only"
    assert status["specification_complete"] is False
    assert status["declared_release_blocker"] == (
        "adversarial_harness_release_gate: V3 cannot release until the aggregate "
        "exact-oracle migration is complete and independently reviewed"
    )

    overclaim = copy.deepcopy(status)
    overclaim["maturity"] = "validated_specification_only"
    overclaim["specification_complete"] = True
    assert {
        "public_maturity_migration",
        "public_specification_complete",
    } <= rules(validator.validate_public_status(overclaim, final=False))

    erased = copy.deepcopy(status)
    erased["declared_release_blocker"] = ""
    assert "public_release_blocker" in rules(
        validator.validate_public_status(erased, final=False)
    )


def test_mistake_escalation_replay_hashes_are_current_and_algorithm_qualified() -> None:
    value = load("redteam/ai-mistake-escalation-2026-08-27.yaml")
    assert validator.validate_mistake_escalation(value) == []

    stale = copy.deepcopy(value)
    stale["regression_test"]["replay_evidence"]["test_file_sha256"] = (
        "sha256:" + "0" * 64
    )
    assert validator.validate_mistake_escalation(stale) == [
        "mistake_replay_digest: stale test_file_sha256"
    ]

    ambiguous = copy.deepcopy(value)
    ambiguous["regression_test"]["replay_evidence"].pop("digest_algorithm")
    assert validator.validate_mistake_escalation(ambiguous) == [
        "mistake_replay_digest_algorithm: replay evidence must declare canonical UTF-8/LF SHA-256"
    ]


def prompt_runtime_fixture_errors(mutation: str) -> list[str]:
    with isolated_validator_root("dmv3-prompt-runtime-") as root:
        assignments = synthetic_three_role_assignments(
            root, "DMV3-SYNTHETIC-PROMPT", "PROMPT"
        )
        reviews = bind_synthetic_prompt_reviews(root, assignments)
        for assignment in assignments:
            assignment["qualification_basis"]["state"] = "qualified"
            assignment["qualification_receipt_ref"] = (
                f"qualification-receipt:QREC-{assignment['assignment_id'].removeprefix('DMV3-ROLE-')}"
            )
            assignment["qualification_receipt_digest"] = validator.object_digest({
                "synthetic": assignment["assignment_id"]
            })
            assignment["status"] = "qualified_for_unit"
        bundle = seal_synthetic_bundle(
            root,
            assignments,
            bundle_id="DMV3-BUNDLE-SYNTHETIC-PROMPT",
            fixture_kind="runtime_receipt",
            prompt_reviews=reviews,
        )
        baseline = validator.validate_role_assignments(
            bundle,
            load("mesh/agent-mesh.v3.json"),
            final=False,
            use_at=validator.parse_time("2026-08-27T19:00:00Z"),
            contract_only=True,
        )
        assert not baseline, baseline
        subject = assignments[0]
        review = next(
            row for row in reviews
            if row["subject_assignment_ref"]
            == f"role-assignment:{subject['assignment_id']}"
        )
        if mutation == "task_prompt_digest":
            subject["task_prompt_digest"] = validator.ZERO_DIGEST
            review["task_prompt_digest"] = validator.ZERO_DIGEST
            review["subject_assignment_scope_digest"] = (
                validator.prompt_review_assignment_scope_digest(subject)
            )
        elif mutation == "prompt_review_self":
            review["reviewer_assignment_ref"] = (
                f"role-assignment:{subject['assignment_id']}"
            )
        else:
            raise AssertionError(mutation)
        review["receipt_digest"] = validator.object_digest(
            review, omit=("receipt_digest",)
        )
        subject["prompt_neutrality_review_digest"] = review["receipt_digest"]
        bundle["bundle_digest"] = validator.object_digest(
            bundle, omit=("bundle_digest",)
        )
        return validator.validate_role_assignments(
            bundle,
            load("mesh/agent-mesh.v3.json"),
            final=False,
            use_at=validator.parse_time("2026-08-27T19:00:00Z"),
            contract_only=True,
        )


def expert_pack_fixture_errors(mutation: str) -> list[str]:
    with isolated_validator_root("dmv3-expert-pack-") as root:
        source_ref = "mesh/fixtures/synthetic-source-manifest.json"
        fixture_ref = "mesh/fixtures/synthetic-expert-result.json"
        write_isolated_json(root, source_ref, {"synthetic_sources": [], "authority": False})
        write_isolated_json(root, fixture_ref, {"result": "pass", "authority": False})
        pack = {
            "schema_version": "logos.doctrine-marathon.expert-pack.v3",
            "expert_pack_id": "EPACK-SYNTHETIC-RESOLUTION",
            "revision": 1,
            "pack_kind": "father_or_corpus",
            "contract_ref": "research/father-expert-pack-contract.yaml",
            "contract_digest": validator.file_digest(
                root / "research/father-expert-pack-contract.yaml"
            ),
            "capability_ids": ["apostolic_fathers"],
            "scope": ["synthetic corpus resolution only"],
            "exclusions": ["no doctrine, source, runtime, or publication authority"],
            "source_manifest_bindings": [{
                "ref": source_ref,
                "digest": validator.file_digest(root / source_ref),
            }],
            "fixture_result_bindings": [{
                "ref": fixture_ref,
                "digest": validator.file_digest(root / fixture_ref),
                "result": "pass",
            }],
            "qualification_scope_digest": validator.ZERO_DIGEST,
            "qualification_receipt_refs": [],
            "qualification_receipt_digests": [],
            "qualification_state": "candidate",
            "effective_at": "2026-08-27T19:00:00Z",
            "expires_at": None,
            "invalidation_triggers": ["contract, manifest, fixture, or scope changes"],
            "non_authority": {
                "doctrine_authority": False,
                "source_authority": False,
                "runtime_authority": False,
            },
            "pack_digest": validator.ZERO_DIGEST,
        }
        def reseal() -> dict[str, Any]:
            pack["qualification_scope_digest"] = validator.object_digest({
                key: pack[key]
                for key in (
                    "expert_pack_id", "revision", "pack_kind", "contract_ref",
                    "contract_digest", "capability_ids", "scope", "exclusions",
                    "source_manifest_bindings", "fixture_result_bindings",
                )
            })
            pack["pack_digest"] = validator.object_digest(
                pack, omit=("pack_digest",)
            )
            registry = copy.deepcopy(load("mesh/qualification-registry.json"))
            registry["runtime_records"] = True
            registry["expert_packs"] = [pack]
            registry["registry_digest"] = validator.object_digest(
                registry, omit=("registry_digest",)
            )
            return registry
        baseline = validator.validate_qualification_registry(reseal(), final=False)[0]
        assert not baseline, baseline
        if mutation == "source_ref":
            pack["source_manifest_bindings"][0]["ref"] = "mesh/fixtures/missing-source.json"
        elif mutation == "source_digest":
            pack["source_manifest_bindings"][0]["digest"] = validator.ZERO_DIGEST
        elif mutation == "fixture_ref":
            pack["fixture_result_bindings"][0]["ref"] = "mesh/fixtures/missing-result.json"
        elif mutation == "fixture_digest":
            pack["fixture_result_bindings"][0]["digest"] = validator.ZERO_DIGEST
        else:
            raise AssertionError(mutation)
        return validator.validate_qualification_registry(reseal(), final=False)[0]


def graph_prerequisite_fixture_errors() -> list[str]:
    with isolated_validator_root("dmv3-graph-prerequisite-"):
        value = copy.deepcopy(load("graph/example-graph.json"))
        baseline = validator.validate_graph(
            value,
            final=False,
            evidence_registry=load("evidence/evidence-registry.json"),
            authority_registry=load("graph/authority-registry.yaml"),
        )
        assert not baseline, baseline
        edge = next(row for row in value["edges"] if row["edge_id"] == "DMV3-E-001")
        replacement = next(
            row for row in value["nodes"] if row["node_id"] == "DMV3-PUBLIC-STATUS"
        )
        edge["basis_refs"] = [replacement["content_ref"]]
        edge["basis_digests"] = [replacement["content_digest"]]
        value["graph_digest"] = validator.object_digest(value, omit=("graph_digest",))
        return validator.validate_graph(
            value,
            final=False,
            evidence_registry=load("evidence/evidence-registry.json"),
            authority_registry=load("graph/authority-registry.yaml"),
        )


def evidence_binding_fixture_errors(mutation: str) -> list[str]:
    with isolated_validator_root("dmv3-evidence-binding-") as root:
        unit = "DMV3-SYNTHETIC-EVIDENCE"
        output_ref = "evidence/fixtures/synthetic-source-content.json"
        attestation_ref = "evidence/fixtures/synthetic-attestation.json"
        write_isolated_json(root, output_ref, {"synthetic": True, "authority": False})
        write_isolated_json(root, attestation_ref, {"synthetic": True, "authority": False})
        output_digest = validator.file_digest(root / output_ref)
        attestation_digest = validator.file_digest(root / attestation_ref)

        snapshot_ref = "mesh/qualification-snapshots/synthetic-evidence-bootstrap.json"
        write_isolated_json(root, snapshot_ref, load("mesh/qualification-registry.json"))
        support_assignments = synthetic_three_role_assignments(
            root, unit, "EVIDENCE-BOOT"
        )
        support_reviews = bind_synthetic_prompt_reviews(root, support_assignments)
        support_bundle = seal_synthetic_bundle(
            root,
            support_assignments,
            bundle_id="DMV3-BUNDLE-SYNTHETIC-EVIDENCE-BOOT",
            fixture_kind="runtime_receipt",
            prompt_reviews=support_reviews,
            registry_ref=snapshot_ref,
        )
        support_ref = "mesh/receipts/synthetic-evidence-bootstrap.json"
        write_isolated_json(root, support_ref, support_bundle)

        assignments = synthetic_three_role_assignments(
            root, unit, "EVIDENCE-RUN"
        )
        prompt_reviews = bind_synthetic_prompt_reviews(root, assignments)
        approvers = [{
            "signer_id": "HUMAN-SYNTHETIC",
            "qualification_scope": ["qualification_approval"],
            "tradition_or_jurisdiction": "Synthetic evidence test",
            "qualification_receipt_ref": "approver-qualification:QAPP-SYNTHETIC",
            "qualification_receipt_digest": validator.object_digest({"qapp": "synthetic"}),
            "valid_from": "2026-08-27T18:00:00Z",
            "valid_until": "2026-08-27T22:00:00Z",
        }]
        approver_digest = validator.object_digest(approvers)
        human_decisions: list[dict[str, Any]] = []
        qualification_receipts: list[dict[str, Any]] = []
        support_reviewer_refs = sorted([
            f"role-assignment:{row['assignment_id']}"
            for row in support_assignments
            if row["role_id"] in {
                "role-qualification-and-independence-auditor",
                "independent-whole-work-checker",
            }
        ])
        for assignment in assignments:
            assignment["qualification_basis"]["state"] = "qualified"
            scope_digest = validator.role_assignment_qualification_scope_digest(
                assignment
            )
            decision = {
                "schema_version": "logos.doctrine-marathon.human-decision-receipt.v3",
                "receipt_id": (
                    "HDEC-QUAL-"
                    f"{assignment['assignment_id'].removeprefix('DMV3-ROLE-')}"
                ),
                "decision_type": "qualification_approval",
                "subject_ref": f"role-assignment:{assignment['assignment_id']}",
                "subject_digest": scope_digest,
                "scope_digest": scope_digest,
                "tradition_or_jurisdiction": "Synthetic evidence test",
                "signer_ids": ["HUMAN-SYNTHETIC"],
                "signer_registry_digest": approver_digest,
                "authority_scope": ["qualification:role_assignment"],
                "decision": "approved",
                "issued_at": "2026-08-27T18:40:00Z",
                "expires_at": "2026-08-27T22:00:00Z",
                "attestation_bindings": [{
                    "ref": attestation_ref,
                    "digest": attestation_digest,
                }],
                "recorded_by_human": True,
                "created_by_ai": False,
                "receipt_digest": validator.ZERO_DIGEST,
            }
            decision["receipt_digest"] = validator.object_digest(
                decision, omit=("receipt_digest",)
            )
            human_decisions.append(decision)
            qrec = {
                "schema_version": "logos.doctrine-marathon.qualification-receipt.v3",
                "receipt_id": (
                    "QREC-"
                    f"{assignment['assignment_id'].removeprefix('DMV3-ROLE-')}"
                ),
                "subject_kind": "role_assignment",
                "subject_ref": f"role-assignment:{assignment['assignment_id']}",
                "subject_scope_digest": scope_digest,
                "work_unit_id": unit,
                "capability_ids": assignment["capability_ids"],
                "expert_pack_ref": None,
                "expert_pack_digest": None,
                "runtime_adapter_digest": assignment["runtime_adapter_digest"],
                "qualification_generation": 0,
                "reviewer_evidence_role": "supporting_non_authorizing",
                "bootstrap_authorization_ref": f"human-decision:{decision['receipt_id']}",
                "bootstrap_authorization_digest": decision["receipt_digest"],
                "qualification_input_digest": validator.ZERO_DIGEST,
                "reviewer_assignment_bundle_ref": support_ref,
                "reviewer_assignment_bundle_digest": validator.file_digest(
                    root / support_ref
                ),
                "reviewer_assignment_refs": support_reviewer_refs,
                "fixture_bindings": [{
                    "ref": output_ref,
                    "digest": output_digest,
                    "result": "pass",
                }],
                "decision": "qualified",
                "abstention_fixture_passed": True,
                "independence_assessment": "independent",
                "human_approval_receipt_ref": f"human-decision:{decision['receipt_id']}",
                "human_approval_receipt_digest": decision["receipt_digest"],
                "issued_at": "2026-08-27T18:50:00Z",
                "expires_at": "2026-08-27T21:00:00Z",
                "authority_effect": "none",
                "receipt_digest": validator.ZERO_DIGEST,
            }
            qrec["qualification_input_digest"] = validator.object_digest({
                key: qrec[key]
                for key in (
                    "subject_kind", "subject_ref", "subject_scope_digest",
                    "work_unit_id", "capability_ids", "expert_pack_ref",
                    "expert_pack_digest", "runtime_adapter_digest",
                    "qualification_generation", "reviewer_evidence_role",
                    "bootstrap_authorization_ref", "bootstrap_authorization_digest",
                    "reviewer_assignment_bundle_ref",
                    "reviewer_assignment_bundle_digest",
                    "reviewer_assignment_refs", "fixture_bindings",
                )
            })
            qrec["receipt_digest"] = validator.object_digest(
                qrec, omit=("receipt_digest",)
            )
            qualification_receipts.append(qrec)
            assignment["qualification_receipt_ref"] = (
                f"qualification-receipt:{qrec['receipt_id']}"
            )
            assignment["qualification_receipt_digest"] = qrec["receipt_digest"]
            assignment["status"] = "qualified_for_unit"

        authority = {
            "qualified_approvers": approvers,
            "approver_set_digest": approver_digest,
            "human_decision_receipts": human_decisions,
        }
        write_isolated_json(root, "graph/authority-registry.yaml", authority)
        qregistry = copy.deepcopy(load("mesh/qualification-registry.json"))
        qregistry["runtime_records"] = True
        qregistry["qualification_receipts"] = qualification_receipts
        qregistry["registry_digest"] = validator.object_digest(
            qregistry, omit=("registry_digest",)
        )
        write_isolated_json(root, "mesh/qualification-registry.json", qregistry)
        runtime_bundle = seal_synthetic_bundle(
            root,
            assignments,
            bundle_id="DMV3-BUNDLE-SYNTHETIC-EVIDENCE-RUN",
            fixture_kind="runtime_receipt",
            prompt_reviews=prompt_reviews,
        )
        runtime_ref = "mesh/receipts/synthetic-evidence-runtime.json"
        write_isolated_json(root, runtime_ref, runtime_bundle)
        assignment_map = {
            f"role-assignment:{row['assignment_id']}": row
            for row in assignments
        }
        producer_ref = next(
            ref for ref, row in assignment_map.items()
            if row["assignment_kind"] == "writer"
        )
        reviewer_refs = sorted(
            ref for ref, row in assignment_map.items()
            if row["role_id"] in {
                "role-qualification-and-independence-auditor",
                "independent-whole-work-checker",
            }
        )
        source = qualified_source()
        source["content_digest"] = output_digest
        source["observed_at"] = "2026-08-27T19:00:00Z"
        source["qualification_scope_digest"] = (
            validator.source_qualification_scope_digest(source)
        )
        review = {
            "schema_version": "logos.doctrine-marathon.evidence-review-receipt.v3",
            "receipt_id": "EREV-SYNTHETIC-BINDING",
            "review_kind": "source_qualification",
            "subject_ref": "source-record:SRC-SYNTHETIC-A",
            "subject_scope_digest": source["qualification_scope_digest"],
            "work_unit_id": unit,
            "assignment_bundle_ref": runtime_ref,
            "assignment_bundle_digest": validator.file_digest(root / runtime_ref),
            "producer_assignment_ref": producer_ref,
            "producer_assignment_digest": validator.object_digest(
                assignment_map[producer_ref]
            ),
            "reviewer_assignment_refs": reviewer_refs,
            "required_capability_ids": ["source_identity_locator_and_rights"],
            "review_dimensions": ["fitness", "identity", "rights"],
            "evidence_bindings": [
                {
                    "ref": "source-record:SRC-SYNTHETIC-A",
                    "digest": source["qualification_scope_digest"],
                },
                {"ref": output_ref, "digest": output_digest},
            ],
            "decision": "qualified",
            "independence_assessment": "independent",
            "correlation_acceptance_receipt_ref": None,
            "issued_at": "2026-08-27T19:35:00Z",
            "expires_at": "2026-08-27T21:00:00Z",
            "authority_effect": "none",
            "receipt_digest": validator.ZERO_DIGEST,
        }

        def validate_current() -> list[str]:
            review["receipt_digest"] = validator.object_digest(
                review, omit=("receipt_digest",)
            )
            source["qualification_receipt_refs"] = [
                "evidence-review:EREV-SYNTHETIC-BINDING"
            ]
            source["qualification_receipt_digests"] = [review["receipt_digest"]]
            source["record_digest"] = validator.object_digest(
                source, omit=("record_digest",)
            )
            registry = evidence_registry_candidate(
                sources=[source], reviews=[review]
            )
            return validator.validate_evidence_registry(registry, final=False)

        baseline = validate_current()
        assert not baseline, baseline
        if mutation == "producer_digest":
            review["producer_assignment_digest"] = validator.ZERO_DIGEST
        elif mutation == "producer_independence":
            review["producer_assignment_ref"] = reviewer_refs[0]
            review["producer_assignment_digest"] = validator.object_digest(
                assignment_map[reviewer_refs[0]]
            )
        elif mutation == "review_kind_capabilities":
            review["required_capability_ids"] = [
                "prompt_alignment_and_authority",
                "source_identity_locator_and_rights",
            ]
        else:
            raise AssertionError(mutation)
        return validate_current()


def midflight_binding_fixture_errors(mutation: str) -> list[str]:
    with isolated_validator_root("dmv3-midflight-binding-") as root:
        unit = "DMV3-SYNTHETIC-MIDFLIGHT"
        ids = {
            "complete": "DMV3-ROLE-MIDFLIGHT-COMPLETE",
            "source": "DMV3-ROLE-MIDFLIGHT-SOURCE",
            "claim": "DMV3-ROLE-MIDFLIGHT-CLAIM",
            "graph": "DMV3-ROLE-MIDFLIGHT-GRAPH",
            "meta": "DMV3-ROLE-MIDFLIGHT-META",
            "whole": "DMV3-ROLE-MIDFLIGHT-WHOLE",
        }
        assignments = [
            synthetic_assignment(
                root,
                assignment_id=ids["complete"],
                unit=unit,
                role_id="doctrine-mesh-completeness-auditor",
                assignment_kind="auditor",
                capability_ids=["doctrine_mesh_completeness_and_gap_detection"],
                control_ref="mesh/completeness-auditor-v3.yaml",
                checks=[],
            ),
            synthetic_assignment(
                root,
                assignment_id=ids["source"],
                unit=unit,
                role_id="source-fitness-rights-verifier",
                assignment_kind="auditor",
                capability_ids=[
                    "privacy_public_boundary_and_custody",
                    "source_identity_locator_and_rights",
                ],
                control_ref="evidence/source-record.schema.json",
                checks=[],
            ),
            synthetic_assignment(
                root,
                assignment_id=ids["claim"],
                unit=unit,
                role_id="claim-entailment-context-verifier",
                assignment_kind="auditor",
                capability_ids=["quotation_context_and_entailment"],
                control_ref="evidence/claim-record.schema.json",
                checks=[],
            ),
            synthetic_assignment(
                root,
                assignment_id=ids["graph"],
                unit=unit,
                role_id="dependency-invalidation-checker",
                assignment_kind="auditor",
                capability_ids=["graph_dependency_and_invalidation"],
                control_ref="graph/instance-dependency-graph.schema.json",
                checks=[],
            ),
            synthetic_assignment(
                root,
                assignment_id=ids["meta"],
                unit=unit,
                role_id="role-qualification-and-independence-auditor",
                assignment_kind="checker",
                capability_ids=[
                    "prompt_alignment_and_authority",
                    "role_qualification_and_independence",
                ],
                control_ref="mesh/role-assignment.schema.json",
                checks=[
                    ids["complete"], ids["source"], ids["claim"],
                    ids["graph"], ids["whole"],
                ],
            ),
            synthetic_assignment(
                root,
                assignment_id=ids["whole"],
                unit=unit,
                role_id="independent-whole-work-checker",
                assignment_kind="checker",
                capability_ids=[
                    "prompt_alignment_and_authority",
                    "role_qualification_and_independence",
                ],
                control_ref="constitution.yaml",
                checks=[
                    ids["complete"], ids["source"], ids["claim"],
                    ids["graph"], ids["meta"],
                ],
            ),
        ]
        bundle = seal_synthetic_bundle(
            root,
            assignments,
            bundle_id="DMV3-BUNDLE-SYNTHETIC-MIDFLIGHT",
            fixture_kind="design_time_simulation",
        )
        bundle_ref = "mesh/examples/synthetic-midflight-action-bundle.json"
        write_isolated_json(root, bundle_ref, bundle)
        assignment_map = {
            f"role-assignment:{row['assignment_id']}": row
            for row in assignments
        }
        evidence_ref = "events/fixtures/synthetic-action-evidence.json"
        write_isolated_json(root, evidence_ref, {"synthetic": True, "authority": False})
        evidence_digest = validator.file_digest(root / evidence_ref)
        graph = load("graph/example-graph.json")
        direct_subjects = ["DMV3-CONSTITUTION"]
        closure = sorted(
            set(direct_subjects)
            | validator.reverse_closure(
                graph["reverse_consumer_index"], direct_subjects
            )
        )
        trigger = next(
            row for row in load("firewall/trigger-matrix.yaml")["triggers"]
            if row["trigger_id"] == "TR-SOURCE"
        )
        actions = sorted(trigger["actions"])
        checker_by_action = {
            "midflight_completeness_audit": ids["complete"],
            "source_record_gate": ids["source"],
            "claim_evidence_lineage_gate": ids["claim"],
            "invalidate_affected_consumers": ids["graph"],
        }
        action_results: list[dict[str, Any]] = []
        for action_id in actions:
            checker_ref = f"role-assignment:{checker_by_action[action_id]}"
            checker = assignment_map[checker_ref]
            result = {
                "action_id": action_id,
                "subject_ids": closure,
                "result": "pass_to_continue",
                "evidence_bindings": [{
                    "ref": evidence_ref,
                    "digest": evidence_digest,
                }],
                "checker_assignment_ref": checker_ref,
                "checker_assignment_digest": validator.object_digest(checker),
                "checker_actor_instance_id": checker["actor_instance_id"],
                "checker_attempt_id": checker["attempt_id"],
                "result_digest": validator.ZERO_DIGEST,
            }
            result["result_digest"] = validator.object_digest(
                result, omit=("result_digest",)
            )
            action_results.append(result)
        bundle_digest = validator.file_digest(root / bundle_ref)
        completeness_ref = f"role-assignment:{ids['complete']}"
        completeness = assignment_map[completeness_ref]
        capabilities = ["doctrine_mesh_completeness_and_gap_detection"]
        entry_details = {
            "coverage_input_digest": evidence_digest,
            "requirement_and_assignment_refs": ["synthetic:midflight-requirements"],
            "completeness_assignment_bundle_ref": bundle_ref,
            "completeness_assignment_bundle_digest": bundle_digest,
            "completeness_assignment_ref": completeness_ref,
            "completeness_assignment_digest": validator.object_digest(completeness),
            "required_capability_ids": capabilities,
            "requirement_set_digest": validator.ZERO_DIGEST,
        }
        entry_details["requirement_set_digest"] = validator.object_digest({
            key: entry_details[key]
            for key in (
                "coverage_input_digest", "requirement_and_assignment_refs",
                "completeness_assignment_bundle_ref",
                "completeness_assignment_bundle_digest",
                "completeness_assignment_ref", "completeness_assignment_digest",
                "required_capability_ids",
            )
        })
        exit_details = {
            "final_output_digest": evidence_digest,
            "independently_rederived_requirements": True,
            "discovered_gap_and_replay_refs": [],
            "completeness_assignment_bundle_ref": bundle_ref,
            "completeness_assignment_bundle_digest": bundle_digest,
            "completeness_assignment_ref": completeness_ref,
            "completeness_assignment_digest": validator.object_digest(completeness),
            "required_capability_ids": capabilities,
            "requirement_set_digest": validator.ZERO_DIGEST,
        }
        exit_details["requirement_set_digest"] = validator.object_digest({
            key: exit_details[key]
            for key in (
                "final_output_digest", "independently_rederived_requirements",
                "discovered_gap_and_replay_refs",
                "completeness_assignment_bundle_ref",
                "completeness_assignment_bundle_digest",
                "completeness_assignment_ref", "completeness_assignment_digest",
                "required_capability_ids",
            )
        })
        graph_digest = validator.file_digest(root / "graph/example-graph.json")
        closure_digest = validator.object_digest(closure)
        kinds_and_details = [
            ("work_unit_classified", {}),
            ("completeness_entry", entry_details),
            ("material_trigger", {
                "trigger_matrix_id": "TR-SOURCE",
                "changed_input_digest": evidence_digest,
                "dependency_graph_ref": "graph/example-graph.json",
                "dependency_graph_digest": graph_digest,
                "direct_subject_ids": direct_subjects,
                "affected_work_and_consumer_ids": closure,
                "closure_digest": closure_digest,
                "required_action_ids": actions,
            }),
            ("completeness_midflight", {
                "prior_trigger_event_id": "DMV3-EVENT-0003",
                "trigger_event_hash": validator.ZERO_DIGEST,
                "fresh_changed_input_digest": evidence_digest,
                "dependency_graph_digest": graph_digest,
                "covered_affected_ids": closure,
                "closure_digest": closure_digest,
                "completeness_assignment_bundle_ref": bundle_ref,
                "completeness_assignment_bundle_digest": bundle_digest,
                "completeness_assignment_ref": completeness_ref,
                "completeness_assignment_digest": validator.object_digest(completeness),
                "required_capability_ids": capabilities,
                "fresh_requirement_set_digest": validator.ZERO_DIGEST,
                "action_assignment_bundle_ref": bundle_ref,
                "action_assignment_bundle_digest": bundle_digest,
                "action_results": action_results,
            }),
            ("candidate_created", {}),
            ("gap_discovered", {}),
            ("completeness_exit", exit_details),
            ("checkpoint_frozen", {"checkpoint_digest": evidence_digest}),
            ("terminal_handoff", {
                "checkpoint_digest": evidence_digest,
                "terminal_status": "BLOCKED",
                "exact_next_prompt_or_explicit_none_if_complete": (
                    "Synthetic next prompt for isolated validation only."
                ),
            }),
        ]
        events = [{
            "event_id": f"DMV3-EVENT-{sequence:04d}",
            "sequence": sequence,
            "occurred_at": f"2026-08-27T19:{sequence:02d}:00Z",
            "event_type": event_type,
            "actor_id": "SYNTHETIC-MIDFLIGHT-ACTOR",
            "input_digest": evidence_digest,
            "affected_ids": closure,
            "authority_ref": "synthetic:test-only",
            "details": details,
            "prior_event_hash": None,
            "event_hash": validator.ZERO_DIGEST,
        } for sequence, (event_type, details) in enumerate(kinds_and_details, start=1)]
        ledger = {
            "metadata": {
                "object_type": "synthetic_midflight_event_ledger",
                "trust_zone": "proposed",
                "lifecycle_status": "test",
                "provenance_note": "Synthetic non-authorizing isolated fixture.",
                "reason_for_inclusion": "Exercise exact midflight bindings.",
            },
            "schema_version": "logos.doctrine_marathon.event-ledger.v3",
            "campaign_id": "LOGOS-DOCTRINE-MARATHON-003",
            "runtime_events": False,
            "append_only": True,
            "ledger_generation": 0,
            "prior_snapshot": None,
            "event_count": 0,
            "last_event_hash": None,
            "events": events,
            "ledger_hash": validator.ZERO_DIGEST,
        }
        reseal_event_candidate(ledger)
        midflight = next(
            row for row in ledger["events"]
            if row["event_type"] == "completeness_midflight"
        )
        trigger_event = next(
            row for row in ledger["events"] if row["event_type"] == "material_trigger"
        )
        expected_surface_digest = validator.object_digest({
            "trigger_event_hash": trigger_event["event_hash"],
            "changed_input_digest": trigger_event["details"]["changed_input_digest"],
            "dependency_graph_digest": trigger_event["details"]["dependency_graph_digest"],
            "closure_digest": trigger_event["details"]["closure_digest"],
            "required_action_ids": trigger_event["details"]["required_action_ids"],
            "action_assignment_bundle_ref": midflight["details"]["action_assignment_bundle_ref"],
            "action_assignment_bundle_digest": midflight["details"]["action_assignment_bundle_digest"],
            "completeness_assignment_bundle_ref": midflight["details"]["completeness_assignment_bundle_ref"],
            "completeness_assignment_bundle_digest": midflight["details"]["completeness_assignment_bundle_digest"],
            "completeness_assignment_ref": midflight["details"]["completeness_assignment_ref"],
            "completeness_assignment_digest": midflight["details"]["completeness_assignment_digest"],
            "required_capability_ids": midflight["details"]["required_capability_ids"],
        })
        assert (
            midflight["details"]["fresh_requirement_set_digest"]
            == expected_surface_digest
        )
        baseline = validator.validate_midflight_action_results(
            midflight,
            actions,
            closure,
            final=False,
            runtime_required=False,
        )
        assert not baseline, baseline
        if mutation == "action_bundle_digest":
            midflight["details"]["action_assignment_bundle_digest"] = (
                validator.ZERO_DIGEST
            )
        elif mutation == "checker_digest":
            result = midflight["details"]["action_results"][0]
            result["checker_assignment_digest"] = validator.ZERO_DIGEST
            result["result_digest"] = validator.object_digest(
                result, omit=("result_digest",)
            )
        elif mutation == "evidence_digest":
            result = midflight["details"]["action_results"][0]
            result["evidence_bindings"][0]["digest"] = validator.ZERO_DIGEST
            result["result_digest"] = validator.object_digest(
                result, omit=("result_digest",)
            )
        else:
            raise AssertionError(mutation)
        reseal_event_candidate(ledger)
        return validator.validate_midflight_action_results(
            midflight,
            actions,
            closure,
            final=False,
            runtime_required=False,
        )


def weekly_receipt_fixture_errors(mutation: str) -> list[str]:
    with isolated_validator_root("dmv3-weekly-receipt-") as root:
        weekly = copy.deepcopy(load("state/examples/initial-weekly-fresh-context-gate.json"))
        checkpoint = load("state/examples/initial-resume-checkpoint.json")
        controls = [{
            "ref": ref,
            "digest": validator.file_digest(root / ref),
        } for ref in validator.FRESH_CONTEXT_REQUIRED_CONTROLS]
        receipt_ref = "state/fresh-context-receipts/synthetic.json"
        receipt = {
            "schema_version": "logos.doctrine-marathon.fresh-context-verification-receipt.v3",
            "receipt_id": "FCTX-SYNTHETIC",
            "gate_id": weekly["gate_id"],
            "checkpoint_ref": weekly["checkpoint_ref"],
            "checkpoint_digest": weekly["checkpoint_digest"],
            "canonical_resume_prompt": weekly["canonical_resume_prompt"],
            "canonical_resume_prompt_digest": weekly["canonical_resume_prompt_digest"],
            "fresh_task_started_at": "2026-08-28T18:00:00Z",
            "verified_at": "2026-08-28T18:05:00Z",
            "actor_instance_id": "SYNTHETIC-FRESH-CONTEXT-ACTOR",
            "attempt_id": "SYNTHETIC-FRESH-CONTEXT-ATTEMPT",
            "context_digest": validator.object_digest(controls),
            "reloaded_control_bindings": controls,
            "result": "verified",
            "authority_effect": "none",
            "receipt_digest": validator.ZERO_DIGEST,
        }
        receipt["receipt_digest"] = validator.object_digest(
            receipt, omit=("receipt_digest",)
        )
        write_isolated_json(root, receipt_ref, receipt)
        weekly.update({
            "fixture_kind": "runtime_receipt",
            "verification": {
                "fresh_task_started_at": receipt["fresh_task_started_at"],
                "verified_at": receipt["verified_at"],
                "verification_receipt_ref": receipt_ref,
                "verification_receipt_digest": validator.file_digest(root / receipt_ref),
            },
            "continuation_authorized": True,
            "result": "fresh_context_verified",
        })
        baseline = validator.validate_weekly_gate(weekly, checkpoint)
        assert not baseline, baseline
        if mutation == "receipt_file_digest":
            weekly["verification"]["verification_receipt_digest"] = validator.ZERO_DIGEST
        elif mutation == "receipt_object_digest":
            receipt["receipt_digest"] = validator.ZERO_DIGEST
            write_isolated_json(root, receipt_ref, receipt)
            weekly["verification"]["verification_receipt_digest"] = validator.file_digest(
                root / receipt_ref
            )
        elif mutation == "control_binding":
            receipt["reloaded_control_bindings"][0]["digest"] = validator.ZERO_DIGEST
            receipt["context_digest"] = validator.object_digest(
                receipt["reloaded_control_bindings"]
            )
            receipt["receipt_digest"] = validator.object_digest(
                receipt, omit=("receipt_digest",)
            )
            write_isolated_json(root, receipt_ref, receipt)
            weekly["verification"]["verification_receipt_digest"] = validator.file_digest(
                root / receipt_ref
            )
        else:
            raise AssertionError(mutation)
        return validator.validate_weekly_gate(weekly, checkpoint)


def authority_binding_fixture_errors(mutation: str) -> list[str]:
    with isolated_validator_root("dmv3-authority-binding-") as root:
        registry = copy.deepcopy(load("graph/authority-registry.yaml"))
        baseline = validator.validate_authority_registry(registry, final=False)
        assert not baseline, baseline
        if mutation == "identity_root_file_digest":
            registry["human_identity_authority_root_file_digest"] = validator.ZERO_DIGEST
        elif mutation == "identity_root_activation":
            identity_root = copy.deepcopy(
                load("graph/human-identity-authority-root.yaml")
            )
            identity_root.update({
                "active": True,
                "authorized_identity_issuer_ids": ["HUMAN-SYNTHETIC"],
                "authorized_signer_ids": ["HUMAN-SYNTHETIC"],
                "recorded_by_human": True,
                "created_by_ai": False,
                "protected_commit": "a" * 40,
            })
            identity_root["anchor_digest"] = validator.object_digest(
                identity_root, omit=("anchor_digest",)
            )
            write_isolated_json(
                root, "graph/human-identity-authority-root.yaml", identity_root
            )
            registry["human_identity_authority_root_file_digest"] = (
                validator.file_digest(root / "graph/human-identity-authority-root.yaml")
            )
            registry["human_identity_authority_root_anchor_digest"] = identity_root[
                "anchor_digest"
            ]
        elif mutation in {"qualification_root", "qualification_evidence"}:
            qualification = {
                "schema_version": "logos.doctrine-marathon.approver-qualification.v3",
                "receipt_id": "QAPP-SYNTHETIC-INACTIVE",
                "signer_id": "HUMAN-SYNTHETIC",
                "issuer_id": "HUMAN-SYNTHETIC",
                "qualification_scope": ["qualification_approval"],
                "tradition_or_jurisdiction": "Synthetic authority test",
                "identity_root_anchor_digest": registry[
                    "human_identity_authority_root_anchor_digest"
                ],
                "protected_commit": "a" * 40,
                "evidence_bindings": [{
                    "ref": "constitution.yaml",
                    "digest": (
                        validator.ZERO_DIGEST
                        if mutation == "qualification_evidence"
                        else validator.file_digest(root / "constitution.yaml")
                    ),
                }],
                "issued_at": "2026-08-27T18:00:00Z",
                "expires_at": None,
                "recorded_by_human": True,
                "created_by_ai": False,
                "receipt_digest": validator.ZERO_DIGEST,
            }
            qualification["receipt_digest"] = validator.object_digest(
                qualification, omit=("receipt_digest",)
            )
            registry["approver_qualification_receipts"] = [qualification]
        elif mutation == "attestation_binding":
            approvers = [{
                "signer_id": "HUMAN-SYNTHETIC",
                "qualification_scope": ["qualification_approval"],
                "tradition_or_jurisdiction": "Synthetic authority test",
                "qualification_receipt_ref": "approver-qualification:QAPP-SYNTHETIC",
                "qualification_receipt_digest": validator.object_digest({"qapp": True}),
                "valid_from": "2026-08-27T18:00:00Z",
                "valid_until": "2026-08-27T22:00:00Z",
            }]
            decision_registry = {
                "qualified_approvers": approvers,
                "approver_set_digest": validator.object_digest(approvers),
            }
            decision = {
                "schema_version": "logos.doctrine-marathon.human-decision-receipt.v3",
                "receipt_id": "HDEC-SYNTHETIC-ATTESTATION",
                "decision_type": "qualification_approval",
                "subject_ref": "synthetic:subject",
                "subject_digest": validator.object_digest({"subject": True}),
                "scope_digest": validator.object_digest({"scope": True}),
                "tradition_or_jurisdiction": "Synthetic authority test",
                "signer_ids": ["HUMAN-SYNTHETIC"],
                "signer_registry_digest": decision_registry["approver_set_digest"],
                "authority_scope": ["qualification:synthetic"],
                "decision": "approved",
                "issued_at": "2026-08-27T19:00:00Z",
                "expires_at": "2026-08-27T21:00:00Z",
                "attestation_bindings": [{
                    "ref": "constitution.yaml",
                    "digest": validator.file_digest(root / "constitution.yaml"),
                }],
                "recorded_by_human": True,
                "created_by_ai": False,
                "receipt_digest": validator.ZERO_DIGEST,
            }
            decision["receipt_digest"] = validator.object_digest(
                decision, omit=("receipt_digest",)
            )
            decision_baseline = validator.validate_human_decision_receipt(
                decision, decision_registry
            )
            assert not decision_baseline, decision_baseline
            decision["attestation_bindings"][0]["digest"] = validator.ZERO_DIGEST
            decision["receipt_digest"] = validator.object_digest(
                decision, omit=("receipt_digest",)
            )
            return validator.validate_human_decision_receipt(
                decision, decision_registry
            )
        else:
            raise AssertionError(mutation)
        registry["registry_digest"] = validator.object_digest(
            registry, omit=("registry_digest",)
        )
        return validator.validate_authority_registry(registry, final=False)


def jewish_context_candidate() -> dict[str, Any]:
    return {
        "schema_version": "logos.doctrine-marathon.jewish-context-pack.v3",
        "pack_id": "JCTX-SYNTHETIC",
        "community_ref": "community:synthetic-stream",
        "community_display": "Synthetic named Judean stream",
        "period": {"start_display": "synthetic start", "end_display": "synthetic end", "uncertainty": "test only"},
        "geographies": ["Synthetic Judea"],
        "primary_self_or_contemporary_source_refs": ["source-record:SRC-SYNTHETIC-A"],
        "later_source_uses": [],
        "teaching_claim_scope": ["Synthetic teaching claim for schema testing"],
        "internal_diversity_and_disputes": ["Synthetic disagreement preserved for testing"],
        "expert_pack_ref": "synthetic/expert-pack",
        "qualification_receipt_ref": "synthetic/qualification",
        "normative_force": "none",
        "status": "candidate",
        "pack_digest": "sha256:" + "b" * 64,
    }


def admin_fixture() -> tuple[list[dict[str, str]], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str, str, str, str]:
    rows = [
        {"path": "checks/fixtures/negative-cases.json", "sha256": "sha256:" + "1" * 64},
        {"path": "checks/test_validate_doctrine_marathon.py", "sha256": "sha256:" + "2" * 64},
        {"path": "checks/validate_doctrine_marathon.py", "sha256": "sha256:" + "3" * 64},
    ]
    payload = validator.payload_digest(rows)
    manifest = {
        "metadata": {
            "object_type": "doctrine_marathon_revision_manifest",
            "trust_zone": "proposed",
            "lifecycle_status": "frozen_specification_payload",
            "provenance_note": "Synthetic exact-shape manifest used only by adversarial tests.",
            "reason_for_inclusion": "Exercise semantic admin validation after valid checksum recomputation.",
        },
        "schema_version": "logos.doctrine_marathon.revision_manifest.v3",
        "manifest_id": "DMV3-REVISION-003",
        "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
        "revision_id": "doctrine-marathon-v3",
        "revision_root": "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3",
        "parent_revision": {
            "revision_id": "doctrine-mesh-v2",
            "payload_digest": "sha256:6fdc5507d69ed5e6cdeb0aa9b79ed6365aa6b38cce258a0649ee527ba5e15fa8",
            "final_saved_digest": "sha256:1fdff84a9c1a8d34523183e6a8b1fe0ef70c53bde4ad3e054b94faa4a9b3076c",
        },
        "generated_at": "2026-08-27T20:00:00Z",
        "authority": {
            "specification_only": True,
            "runtime_activation_authorized": False,
            "research_execution_authorized": False,
            "source_ingestion_authorized": False,
            "substantive_doctrine_implementation_authorized": False,
            "completed_doctrine_corpus": False,
            "qualified_theological_authority": False,
        },
        "hash_algorithm": "sha256_over_canonical_lf_bytes_for_utf8_raw_bytes_otherwise",
        "payload_list_digest_algorithm": "sha256_over_canonical_compact_json_of_sorted_path_sha256_rows",
        "administrative_files_excluded_from_payload_digest": sorted(validator.ADMIN_FILES),
        "payload_file_count": len(rows),
        "payload_digest": payload,
        "payload_files": rows,
        "manifest_digest": validator.ZERO_DIGEST,
    }
    manifest["manifest_digest"] = validator.object_digest(manifest, omit=("manifest_digest",))
    manifest_file = "sha256:" + "4" * 64
    receipt = {
        "metadata": {
            "object_type": "doctrine_marathon_validation_receipt",
            "trust_zone": "proposed",
            "lifecycle_status": "validated_specification_only",
            "provenance_note": "Synthetic strict-prefinal receipt used only by adversarial tests.",
            "reason_for_inclusion": "Exercise validator, test, fixture, authority, and digest binding.",
        },
        "schema_version": "logos.doctrine_marathon.validation_receipt.v3",
        "receipt_id": "DMV3-VALIDATION-003",
        "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
        "revision_id": "doctrine-marathon-v3",
        "revision_manifest_ref": "revision-manifest.yaml",
        "revision_manifest_digest": manifest_file,
        "revision_manifest_object_digest": manifest["manifest_digest"],
        "payload_file_count": len(rows),
        "payload_digest": payload,
        "validator_ref": "checks/validate_doctrine_marathon.py",
        "validator_digest": rows[2]["sha256"],
        "test_ref": "checks/test_validate_doctrine_marathon.py",
        "test_digest": rows[1]["sha256"],
        "negative_fixture_ref": "checks/fixtures/negative-cases.json",
        "negative_fixture_digest": rows[0]["sha256"],
        "final_replay_command": "python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validate_doctrine_marathon.py --mode final",
        "test_command": "python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_validate_doctrine_marathon.py",
        "mode": "prefinal",
        "result": "pass",
        "error_count": 0,
        "validator_metrics": {
            "payload_file_count": len(rows), "role_count": 18, "trigger_count": 19,
            "assignment_fixture_count": 3, "event_count": 0, "evidence_record_count": 0,
            "graph_node_count": 5, "graph_edge_count": 3,
            "open_expert_review_debt": 2, "error_count": 0,
        },
        "test_result": {
            "status": "pass",
            "negative_case_count": len(load("checks/fixtures/negative-cases.json")),
            "skipped": 0,
        },
        "runtime_activation_authorized": False,
        "research_execution_authorized": False,
        "source_ingestion_authorized": False,
        "substantive_doctrine_implementation_authorized": False,
        "completed_doctrine_corpus": False,
        "qualified_theological_authority": False,
        "mutation_performed": False,
        "observed_at": "2026-08-27T20:00:00Z",
        "receipt_digest": validator.ZERO_DIGEST,
    }
    receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
    review = {
        "metadata": {
            "object_type": "doctrine_marathon_independent_review",
            "trust_zone": "proposed",
            "lifecycle_status": "independently_checked",
            "provenance_note": "Synthetic independent-review record used only by adversarial tests.",
            "reason_for_inclusion": "Exercise reviewer independence, coverage, findings, gates, and digest binding.",
        },
        "schema_version": "logos.doctrine_marathon.independent_review.v3",
        "review_id": "DMV3-INDEPENDENT-REVIEW-003",
        "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
        "revision_id": "doctrine-marathon-v3",
        "revision_manifest_ref": "revision-manifest.yaml",
        "revision_manifest_digest": manifest_file,
        "revision_manifest_object_digest": manifest["manifest_digest"],
        "payload_file_count": len(rows),
        "payload_digest": payload,
        "reviewer_role": "independent-non-author-whole-work-checker",
        "reviewer_actor_instance_id": "synthetic-reviewer-actor",
        "reviewer_attempt_id": "synthetic-review-attempt",
        "author_actor_instance_ids": ["synthetic-author-actor"],
        "author_is_reviewer": False,
        "independence_status": "non_author_read_only_cross_provider_unverified",
        "cross_provider_verified": False,
        "review_scope": "whole_frozen_payload_and_admin_contracts",
        "reviewed_controls": [
            "admin_freeze", "adversarial_cases", "agent_independence", "authority_ceiling",
            "citation_and_source_lineage", "context_normative_firewall",
            "dependency_and_reverse_blast_radius", "event_and_checkpoint_integrity",
            "prompt_neutrality", "public_nonclaims",
        ],
        "unresolved_finding_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
        "resolved_finding_ids": ["SYNTHETIC-RESOLVED"],
        "unresolved_human_gates": [
            "qualified_patristics_and_historical_theology_review",
            "qualified_source_rights_and_textual_review",
            "human_approved_normative_frame",
            "runtime_activation_decision",
            "substantive_doctrine_decision",
        ],
        "declared_release_blocker": (
            "adversarial_harness_release_gate: V3 cannot release until the aggregate "
            "exact-oracle migration is complete and independently reviewed"
        ),
        "result": "pass_blocked_specification_only",
        "runtime_activation_authorized": False,
        "research_execution_authorized": False,
        "source_ingestion_authorized": False,
        "substantive_doctrine_implementation_authorized": False,
        "completed_doctrine_corpus": False,
        "qualified_theological_authority": False,
        "mutation_performed": False,
        "observed_at": "2026-08-27T20:01:00Z",
        "review_digest": validator.ZERO_DIGEST,
    }
    review["review_digest"] = validator.object_digest(review, omit=("review_digest",))
    receipt_file = "sha256:" + "5" * 64
    review_file = "sha256:" + "6" * 64
    authorization = {
        "metadata": {
            "object_type": "doctrine_marathon_public_release_authorization",
            "trust_zone": "proposed",
            "lifecycle_status": "authorized_public_specification_release",
            "provenance_note": "Synthetic bounded public-release authorization used only by adversarial tests.",
            "reason_for_inclusion": "Exercise exact payload, scope, authority-ceiling, and procedural-verification bindings.",
        },
        "schema_version": "logos.doctrine_marathon.public_release_authorization.v3",
        "authorization_id": "DMV3-PUBLIC-RELEASE-003",
        "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
        "revision_id": "doctrine-marathon-v3",
        "revision_root": "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3",
        "status": "authorized_for_one_public_specification_release",
        "authorization_source": "direct_owner_instruction_in_active_codex_task",
        "authorizing_principal": "Lowell Wong",
        "recorded_by": "Codex root",
        "bound_payload": {
            "payload_file_count": len(rows),
            "payload_digest": payload,
            "revision_manifest_ref": "revision-manifest.yaml",
            "revision_manifest_raw_sha256": manifest_file,
            "revision_manifest_object_sha256": manifest["manifest_digest"],
        },
        "release_scope": {
            "content_set": "manifest_payload_plus_exact_final_admin_allowlist",
            "final_admin_allowlist": sorted(validator.ADMIN_FILES),
            "excludes": [
                "all_other_repository_paths",
                "local_machine_artifacts",
                "private_conversations_and_raw_reasoning",
                "restricted_source_content",
                "secrets_credentials_and_signed_links",
            ],
        },
        "authority_limits": {
            "public_artifact_release_only": True,
            "runtime_activation_authorized": False,
            "research_execution_authorized": False,
            "source_ingestion_authorized": False,
            "substantive_doctrine_implementation_authorized": False,
            "completed_doctrine_corpus": False,
            "qualified_theological_authority": False,
        },
        "verification": {
            "attestation_mode": "direct_owner_instruction_procedurally_observed",
            "cryptographic_signature_verified": False,
            "human_identity_credential_verified": False,
            "verification_nonclaim": "This public receipt records a scoped instruction; it is not a cryptographic identity proof.",
        },
        "observed_at": "2026-08-27T20:02:00Z",
        "authorization_digest": validator.ZERO_DIGEST,
    }
    authorization["authorization_digest"] = validator.object_digest(
        authorization, omit=("authorization_digest",)
    )
    authorization_file = "sha256:" + "7" * 64
    saved = {
        "metadata": {
            "object_type": "doctrine_marathon_final_saved_version",
            "trust_zone": "proposed",
            "lifecycle_status": "saved_specification_only",
            "provenance_note": "Synthetic final saved-version record used only by adversarial tests.",
            "reason_for_inclusion": "Exercise the terminal acyclic digest index and authority ceiling.",
        },
        "schema_version": "logos.doctrine_marathon.final_saved_version.v3",
        "save_id": "DMV3-SAVED-003",
        "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
        "revision_id": "doctrine-marathon-v3",
        "status": "saved_specification_only",
        "revision_manifest_ref": "revision-manifest.yaml",
        "revision_manifest_digest": manifest_file,
        "revision_manifest_object_digest": manifest["manifest_digest"],
        "payload_digest": payload,
        "payload_file_count": len(rows),
        "validation_receipt_ref": "checks/validation-receipt.json",
        "validation_receipt_file_digest": receipt_file,
        "validation_receipt_object_digest": receipt["receipt_digest"],
        "independent_review_ref": "checks/independent-review.json",
        "independent_review_file_digest": review_file,
        "independent_review_object_digest": review["review_digest"],
        "public_release_authorization_ref": "checks/public-release-authorization.json",
        "public_release_authorization_file_digest": authorization_file,
        "public_release_authorization_object_digest": authorization["authorization_digest"],
        "artifact_freeze_readiness": "ready_specification_artifact_only",
        "runtime_activation_authorized": False,
        "research_execution_authorized": False,
        "source_ingestion_authorized": False,
        "substantive_doctrine_implementation_authorized": False,
        "completed_doctrine_corpus": False,
        "qualified_theological_authority": False,
        "saved_at": "2026-08-27T20:02:00Z",
        "final_digest": validator.ZERO_DIGEST,
    }
    saved["final_digest"] = validator.object_digest(saved, omit=("final_digest",))
    return rows, manifest, receipt, review, authorization, saved, manifest_file, receipt_file, review_file, authorization_file


def run_case(case: dict[str, str]) -> list[str]:
    target = case["target"]
    mutation = case["mutation"]
    if target == "constitution":
        value = copy.deepcopy(load("constitution.yaml"))
        mapping = {
            "authorize_runtime": "runtime_activation_authorized",
            "authorize_research": "research_execution_authorized",
            "authorize_source_ingestion": "source_ingestion_authorized",
            "authorize_doctrine": "substantive_doctrine_implementation_authorized",
        }
        if mutation == "change_mode":
            value["mode"] = "runtime"
        else:
            value["authority"][mapping[mutation]] = True
        return validator.validate_constitution(value)
    if target == "mesh":
        value = copy.deepcopy(load("mesh/agent-mesh.v3.json"))
        if mutation == "remove_meta_checker":
            value["roles"] = [row for row in value["roles"] if row["role_id"] != "role-qualification-and-independence-auditor"]
        elif mutation == "writer_self_checks":
            value["roles"][0]["checked_by"] = [value["roles"][0]["role_id"]]
        elif mutation == "provider_in_role_id":
            value["roles"][0]["role_id"] = "gpt-controller"
        elif mutation == "factory_dispatches":
            next(row for row in value["roles"] if row["role_id"] == "task-local-role-factory")["may_dispatch"] = True
        elif mutation == "recursive_delegation":
            value["max_delegation_depth"] = 2
        elif mutation == "remove_independence_dimension":
            value["independence_dimensions"].remove("source_order")
        return validator.validate_mesh(value)
    if target == "completeness":
        value = copy.deepcopy(load("mesh/completeness-auditor-v3.yaml"))
        if mutation == "remove_midflight":
            del value["audit_phases"]["midflight"]
        elif mutation == "reuse_preflight_at_exit":
            value["audit_phases"]["exit"]["may_not_reuse"] = "reuse_allowed"
        elif mutation == "omit_reverse_quarantine":
            value["postflight_recovery"]["material_missing_role"].remove("traverse and quarantine reverse consumers")
        elif mutation == "empty_midflight_outputs":
            value["audit_phases"]["midflight"]["required_outputs"] = []
        return validator.validate_completeness(value)
    if target == "triggers":
        value = copy.deepcopy(load("firewall/trigger-matrix.yaml"))
        if mutation == "remove_source_trigger":
            value["triggers"] = [row for row in value["triggers"] if row["trigger_id"] != "TR-SOURCE"]
        elif mutation == "allow_unknown_feature":
            value["default_action_for_unknown_material_feature"] = "continue"
        elif mutation == "reuse_changed_input_event":
            value["changed_input_requires_new_event"] = False
        elif mutation == "empty_actions":
            value["triggers"][0]["actions"] = []
        elif mutation == "unknown_capability":
            next(row for row in value["triggers"] if row["trigger_id"] == "TR-JEWISH")["required_capabilities"] = ["generic_jewish_worlds"]
        elif mutation.startswith("remove_new_trigger_"):
            trigger_id = "TR-" + mutation.removeprefix("remove_new_trigger_").upper()
            value["triggers"] = [
                row for row in value["triggers"] if row["trigger_id"] != trigger_id
            ]
        elif mutation == "risk_without_frontier_sentinel":
            next(row for row in value["triggers"] if row["trigger_id"] == "TR-RISK")["actions"].remove("frontier_sentinel")
        return validator.validate_triggers(value, load("mesh/agent-mesh.v3.json"), load("mesh/role-catalog.yaml"))
    if target == "graph":
        value = copy.deepcopy(load("graph/example-graph.json"))
        if mutation == "omit_reverse_consumer":
            value["reverse_consumer_index"]["DMV3-CONSTITUTION"] = []
        elif mutation == "reverse_canonical_direction":
            value["canonical_edge_direction"] = "prerequisite_to_consumer"
        elif mutation == "context_edge_normative":
            value["edges"].append({"edge_id": "DMV3-E-NEG", "consumer_id": "DMV3-PILOT-1CLEMENT", "prerequisite_id": "DMV3-CONSTITUTION", "edge_type": "contextualized_by", "load_bearing": True, "normative_force": "frame_scoped", "basis_refs": ["synthetic"], "review_state": "candidate"})
            value["reverse_consumer_index"] = validator.derived_reverse_index(value)
        elif mutation == "load_bearing_cycle":
            value["edges"].append({"edge_id": "DMV3-E-NEG", "consumer_id": "DMV3-CONSTITUTION", "prerequisite_id": "DMV3-PAT-SOURCEPLAN", "edge_type": "derived_from", "load_bearing": True, "normative_force": "none", "basis_refs": ["synthetic"], "review_state": "candidate"})
            value["reverse_consumer_index"] = validator.derived_reverse_index(value)
        elif mutation == "current_consumer_blocked_premise":
            next(row for row in value["nodes"] if row["node_id"] == "DMV3-PILOT-1CLEMENT")["state"] = "accepted"
        elif mutation == "stale_weakest_premise":
            next(row for row in value["nodes"] if row["node_id"] == "DMV3-CONSTITUTION")["weakest_premise_state"] = "stale"
        elif mutation == "context_plane_qualified_bypass":
            value["nodes"].append({"node_id": "DMV3-CONTEXT-NEG", "revision_id": "v1", "object_type": "context_record", "state": "accepted", "authority_plane": "context", "content_digest": "sha256:" + "a" * 64, "weakest_premise_state": "not_applicable", "derived_authority_taints": ["context"], "normative_frame_ref": None, "normative_frame_digest": None})
            value["edges"].append({"edge_id": "DMV3-E-NEG", "consumer_id": "DMV3-PUBLIC-STATUS", "prerequisite_id": "DMV3-CONTEXT-NEG", "edge_type": "qualified_by", "load_bearing": True, "normative_force": "none", "basis_refs": ["synthetic/context"], "review_state": "accepted"})
            value["reverse_consumer_index"] = validator.derived_reverse_index(value)
        elif mutation in {"context_historical_public_transitive", "context_historical_normative_transitive"}:
            value["nodes"].extend([
                {"node_id": "DMV3-CONTEXT-NEG", "revision_id": "v1", "object_type": "context_record", "state": "accepted", "authority_plane": "context", "content_digest": "sha256:" + "a" * 64, "weakest_premise_state": "not_applicable", "derived_authority_taints": ["context"], "normative_frame_ref": None, "normative_frame_digest": None},
                {"node_id": "DMV3-HISTORY-NEG", "revision_id": "v1", "object_type": "historical_record", "state": "blocked", "authority_plane": "historical_attribution", "content_digest": "sha256:" + "b" * 64, "weakest_premise_state": "blocked", "derived_authority_taints": ["context", "historical_attribution"], "normative_frame_ref": None, "normative_frame_digest": None},
            ])
            value["edges"].append({"edge_id": "DMV3-E-CTX-HIST", "consumer_id": "DMV3-HISTORY-NEG", "prerequisite_id": "DMV3-CONTEXT-NEG", "edge_type": "derived_from", "load_bearing": True, "normative_force": "none", "basis_refs": ["synthetic/context-chain"], "review_state": "candidate"})
            consumer_id = "DMV3-PUBLIC-STATUS" if mutation.endswith("public_transitive") else "DMV3-NORMATIVE-FRAME"
            value["edges"].append({"edge_id": "DMV3-E-HIST-CONSUMER", "consumer_id": consumer_id, "prerequisite_id": "DMV3-HISTORY-NEG", "edge_type": "derived_from", "load_bearing": True, "normative_force": "none", "basis_refs": ["synthetic/history-chain"], "review_state": "candidate"})
            consumer = next(row for row in value["nodes"] if row["node_id"] == consumer_id)
            consumer["derived_authority_taints"] = sorted(set(consumer["derived_authority_taints"]) | {"context", "historical_attribution"})
            value["reverse_consumer_index"] = validator.derived_reverse_index(value)
        elif mutation == "accepted_normative_without_frame":
            node = next(row for row in value["nodes"] if row["node_id"] == "DMV3-NORMATIVE-FRAME")
            node["state"] = "accepted"
            node["weakest_premise_state"] = "not_applicable"
        elif mutation == "knowledge_guide_basis":
            value["edges"][0]["basis_refs"] = ["KnowledgeGuide:synthetic"]
        elif mutation == "translation_without_lineage":
            value["edges"][0]["edge_type"] = "translated_from"
            value["edges"][0]["basis_refs"] = ["source-record:SRC-MISSING"]
        elif mutation == "causation_as_derived_from":
            value["edges"][0]["basis_refs"] = ["synthetic/influence-claim"]
        elif mutation == "frame_scoped_without_registry":
            value["edges"][0]["normative_force"] = "frame_scoped"
        elif mutation == "placeholder_digest_at_final":
            value["nodes"][0]["content_digest"] = validator.ZERO_DIGEST
        elif mutation == "basis_digest_mismatch":
            value["edges"][0]["basis_digests"][0] = validator.ZERO_DIGEST
        elif mutation == "accepted_qualification_plan_only":
            edge = next(row for row in value["edges"] if row["edge_id"] == "DMV3-E-002")
            edge["review_state"] = "accepted"
            edge["basis_observed_at"] = "2026-08-27T19:00:00Z"
        elif mutation == "nonexistent_load_bearing_basis":
            edge = next(row for row in value["edges"] if row["edge_id"] == "DMV3-E-002")
            edge["basis_refs"] = ["qualification-receipt:QREC-MISSING"]
            edge["basis_digests"] = ["sha256:" + "a" * 64]
        return validator.validate_graph(value, final=mutation == "placeholder_digest_at_final", evidence_registry=load("evidence/evidence-registry.json"), authority_registry=load("graph/authority-registry.yaml"))
    if target == "debt":
        graph = load("graph/example-graph.json")
        value = copy.deepcopy(load("debt/initial-review-debt.json"))
        if mutation == "omit_reverse_consumer":
            value[0]["downstream_consumer_ids"] = []
        elif mutation == "wrong_blast_radius":
            value[0]["blast_radius_count"] = 99
        elif mutation == "blocking_low_risk":
            value[0]["risk_tier"] = "low"
        return validator.validate_debts(value, graph)
    if target == "public":
        value = copy.deepcopy(load("transparency/public-status.json"))
        mapping = {
            "claim_runtime": "runtime_activated",
            "claim_research": "research_started",
            "claim_completed_corpus": "doctrine_corpus_complete",
            "remove_human_review": "human_review_required",
        }
        value[mapping[mutation]] = mutation != "remove_human_review"
        return validator.validate_public_status(value, final=False)
    if target == "prompt":
        text = (validator.ROOT / "DOCTRINE_MARATHON_MASTER_PROMPT.md").read_text(encoding="utf-8")
        if mutation == "remove_normative_frame":
            text = text.replace("NormativeFrame", "Normative-approval-object")
        elif mutation == "desired_conclusion":
            text += "\nYour job is to prove the preferred conclusion.\n"
        elif mutation == "establish_correct":
            text += "\nYour task is to establish that the preferred view is correct.\n"
        elif mutation == "confirm_true":
            text += "\nThe mandate is to confirm that the named position is true.\n"
        elif mutation == "assume_answer":
            text += "\nAssume the answer and collect material afterward.\n"
        elif mutation == "only_supporting":
            text += "\nUse only supporting evidence for the preferred position.\n"
        elif mutation == "remove_trigger_routing_block":
            text = __import__("re").sub(
                r"<!-- BEGIN DETERMINISTIC_TRIGGER_ROUTES -->.*?<!-- END DETERMINISTIC_TRIGGER_ROUTES -->",
                "",
                text,
                flags=__import__("re").S,
            )
        elif mutation == "stale_trigger_routing_digest":
            text = text.replace(
                validator.file_digest(validator.ROOT / "firewall/trigger-matrix.yaml"),
                validator.ZERO_DIGEST,
            )
        return validator.validate_prompt(text)
    if target == "terminal":
        value = copy.deepcopy(load("state/examples/terminal-handoff-blocked.json"))
        if mutation == "blocked_without_next_prompt":
            value["next_prompt"] = None
            return validator.schema_errors(load("state/terminal-handoff.schema.json"), value, "negative terminal")
        if mutation == "dangling_checkpoint":
            value["checkpoint_ref"] = "state/examples/missing.json"
        elif mutation == "checkpoint_digest_mismatch":
            value["checkpoint_digest"] = validator.ZERO_DIGEST
        elif mutation == "status_mismatch":
            value["status"] = "CONTINUE"
        elif mutation == "drop_blocking_gate":
            value["blocked_gate_ids"].pop()
        elif mutation == "forged_campaign_complete":
            value.update({
                "status": "CAMPAIGN_COMPLETE",
                "completed_unit_ids": ["DMV3-SYNTHETIC-UNIT"],
                "blocked_gate_ids": [],
                "residual_risks": [],
                "completion_definition_ref": "state/completion-definitions/missing.json",
                "completion_definition_digest": "sha256:" + "a" * 64,
                "completion_receipt_ref": "state/completion-receipts/missing.json",
                "completion_receipt_digest": "sha256:" + "b" * 64,
                "next_prompt": None,
            })
        return validator.validate_terminal_handoff(value)
    if target == "weekly":
        value = copy.deepcopy(load("state/examples/initial-weekly-fresh-context-gate.json"))
        checkpoint = load("state/examples/initial-resume-checkpoint.json")
        if mutation == "overlong_interval":
            value["must_reset_by"] = "2026-09-04T19:00:00Z"
        elif mutation == "checkpoint_digest_mismatch":
            value["checkpoint_digest"] = validator.ZERO_DIGEST
        elif mutation == "continue_while_required":
            value["continuation_authorized"] = True
        elif mutation == "verification_after_deadline":
            value["result"] = "fresh_context_verified"
            value["continuation_authorized"] = True
            value["verification"] = {"fresh_task_started_at": "2026-09-03T18:00:00Z", "verified_at": "2026-09-04T19:00:00Z", "verification_receipt_ref": "synthetic/receipt", "verification_receipt_digest": "sha256:" + "a" * 64}
        return validator.validate_weekly_gate(value, checkpoint)
    if target == "goal":
        value = copy.deepcopy(load("state/goal.yaml"))
        value["authority_ceiling"]["runtime_activation_authorized"] = True
        return validator.validate_goal(value, final=False)
    if target == "historical":
        value = historical_candidate()
        source = qualified_source()
        if mutation == "ai_heresy_verdict":
            value["ai_generated_verdict"] = True
        elif mutation == "generic_label":
            value["label_used"] = "liberal theology"
        elif mutation == "generic_actor":
            value["actor_or_community"] = "the church"
        elif mutation == "unqualified_source":
            source["qualifies_for_load_bearing"] = False
            source["identity_state"] = "candidate"
        return validator.validate_historical_attribution(value, {source["source_record_id"]: source})
    if target == "normative":
        registry, receipt, value = authority_fixture()
        if mutation == "ai_created_frame":
            value["created_by_ai"] = True
            return validator.schema_errors(load("graph/normative-frame.schema.json"), value, "negative normative frame")
        if mutation == "fabricated_approval":
            return validator.validate_normative_frame(value, load("graph/authority-registry.yaml"), {})
        if mutation == "unlisted_signer":
            receipt["signer_ids"] = ["HUMAN-UNLISTED"]
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
            value["human_approval_receipt_digest"] = receipt["receipt_digest"]
            value["frame_digest"] = validator.object_digest(value, omit=("frame_digest",))
        return validator.validate_normative_frame(value, registry, {receipt["receipt_id"]: receipt})
    if target == "authority":
        registry, receipt, _ = authority_fixture()
        registry["normative_authority_active"] = False
        registry["current_normative_frame_ref"] = None
        registry["current_normative_frame_digest"] = None
        registry["normative_frames"] = []
        if mutation == "approved_normative_while_inactive":
            registry["human_decision_receipts"] = [receipt]
        elif mutation == "nonnormative_scope_escalation":
            receipt["decision_type"] = "qualification_approval"
            receipt["authority_scope"] = ["normative_authority:synthetic"]
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
            registry["qualified_approvers"][0]["qualification_scope"] = ["qualification_approval"]
            registry["approver_set_digest"] = validator.object_digest(registry["qualified_approvers"])
            receipt["signer_registry_digest"] = registry["approver_set_digest"]
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
            registry["human_decision_receipts"] = [receipt]
        registry["registry_digest"] = validator.object_digest(registry, omit=("registry_digest",))
        return validator.validate_authority_registry(registry, final=False)
    if target == "events":
        value = event_ledger_candidate()
        if mutation == "sequence_gap":
            value["events"][2]["sequence"] = 4
        elif mutation == "id_sequence_mismatch":
            value["events"][2]["event_id"] = "DMV3-EVENT-0099"
        elif mutation == "broken_prior_hash":
            value["events"][3]["prior_event_hash"] = validator.ZERO_DIGEST
        elif mutation == "event_hash_mismatch":
            value["events"][1]["actor_id"] = "MUTATED-ACTOR"
        elif mutation == "timestamp_regression":
            value["events"][3]["occurred_at"] = "2026-08-27T18:00:00Z"
        elif mutation == "event_count_mismatch":
            value["event_count"] = 99
        elif mutation == "last_hash_mismatch":
            value["last_event_hash"] = validator.ZERO_DIGEST
        elif mutation == "ledger_hash_mismatch":
            value["ledger_hash"] = validator.ZERO_DIGEST
        elif mutation == "missing_trigger_details":
            del value["events"][2]["details"]["trigger_matrix_id"]
        elif mutation == "unmatched_trigger":
            del value["events"][3]
            for sequence, event in enumerate(value["events"], start=1):
                event["sequence"] = sequence
                event["event_id"] = f"DMV3-EVENT-{sequence:04d}"
            seal_ledger(value)
        elif mutation == "generation_without_snapshot":
            value["ledger_generation"] = 1
            value["ledger_hash"] = validator.object_digest(value, omit=("ledger_hash",))
        elif mutation == "partial_reverse_closure":
            trigger = value["events"][2]
            midflight = value["events"][3]
            partial = trigger["details"]["affected_work_and_consumer_ids"][:-1]
            trigger["affected_ids"] = partial
            trigger["details"]["affected_work_and_consumer_ids"] = partial
            trigger["details"]["closure_digest"] = validator.object_digest(partial)
            midflight["affected_ids"] = partial
            midflight["details"]["covered_affected_ids"] = partial
            midflight["details"]["closure_digest"] = trigger["details"]["closure_digest"]
            for result in midflight["details"]["action_results"]:
                result["subject_ids"] = partial
                result["result_digest"] = validator.object_digest(result, omit=("result_digest",))
            reseal_event_candidate(value)
        elif mutation == "changed_input_after_trigger":
            value["events"][3]["details"]["fresh_changed_input_digest"] = "sha256:" + "b" * 64
            reseal_event_candidate(value)
        elif mutation == "missing_required_action_receipt":
            value["events"][3]["details"]["action_results"].pop()
            reseal_event_candidate(value)
        elif mutation == "changed_graph_snapshot":
            value["events"][2]["details"]["dependency_graph_digest"] = validator.ZERO_DIGEST
            value["events"][3]["details"]["dependency_graph_digest"] = validator.ZERO_DIGEST
            reseal_event_candidate(value)
        elif mutation == "nonexistent_graph_subject":
            trigger = value["events"][2]
            midflight = value["events"][3]
            fake_closure = ["DMV3-NOT-A-GRAPH-NODE"]
            trigger["affected_ids"] = fake_closure
            trigger["details"]["direct_subject_ids"] = fake_closure
            trigger["details"]["affected_work_and_consumer_ids"] = fake_closure
            trigger["details"]["closure_digest"] = validator.object_digest(fake_closure)
            midflight["affected_ids"] = fake_closure
            midflight["details"]["covered_affected_ids"] = fake_closure
            midflight["details"]["closure_digest"] = trigger["details"]["closure_digest"]
            for result in midflight["details"]["action_results"]:
                result["subject_ids"] = fake_closure
                result["result_digest"] = validator.object_digest(result, omit=("result_digest",))
            reseal_event_candidate(value)
        elif mutation == "nontrigger_unknown_affected_id":
            value["events"][0]["affected_ids"] = ["DMV3-NOT-A-GRAPH-NODE"]
            reseal_event_candidate(value)
        elif mutation == "unresolved_trigger_disjoint_continuation":
            del value["events"][3]
            candidate = next(
                event for event in value["events"] if event["event_type"] == "candidate_created"
            )
            candidate["affected_ids"] = ["DMV3-NORMATIVE-FRAME"]
            for sequence, event in enumerate(value["events"], start=1):
                event["sequence"] = sequence
                event["event_id"] = f"DMV3-EVENT-{sequence:04d}"
            seal_ledger(value)
        return validator.validate_event_ledger(value, final=False)
    if target == "completion":
        return completion_gate_fixture_errors(mutation)
    if target == "assignments":
        value = copy.deepcopy(load("mesh/examples/design-time-independence-fixture.json"))
        mesh = load("mesh/agent-mesh.v3.json")
        writer = value["assignments"][0]
        checker = value["assignments"][1]
        if mutation == "missing_source_order":
            del checker["source_order"]
        elif mutation == "noncontiguous_ordinals":
            checker["source_order"][1]["ordinal"] = 3
        elif mutation == "missing_runtime_adapter":
            del checker["runtime_adapter"]
        elif mutation == "guide_used_as_evidence":
            checker["knowledge_guide_lineage"][0]["used_as_evidence"] = True
        elif mutation == "guide_digest_mismatch":
            checker["knowledge_guide_lineage"][0]["guide_digest"] = validator.ZERO_DIGEST
        elif mutation == "same_actor":
            checker["actor_instance_id"] = writer["actor_instance_id"]
        elif mutation == "same_attempt":
            checker["attempt_id"] = writer["attempt_id"]
        elif mutation == "unauthorized_checker":
            checker["role_id"] = "source-fitness-rights-verifier"
        elif mutation == "undisclosed_source_order":
            checker["source_order"] = copy.deepcopy(writer["source_order"])
            checker["source_order_digest"] = validator.object_digest(checker["source_order"])
        elif mutation == "forged_qualification_receipt":
            checker["status"] = "qualified_for_unit"
            checker["qualification_basis"]["state"] = "qualified"
            checker["qualification_receipt_ref"] = "mesh/role-catalog.yaml"
            checker["qualification_receipt_digest"] = validator.ZERO_DIGEST
        elif mutation == "nonexistent_expert_pack":
            writer["role_id"] = "primary-source-researcher"
            writer["qualification_basis"] = {
                "kind": "expert_pack",
                "ref": "expert-pack:EPACK-MISSING",
                "digest": "sha256:" + "a" * 64,
                "state": "candidate",
            }
        elif mutation == "unresolved_correlation_acceptance":
            whole = value["assignments"][2]
            whole["independence"]["assessment"] = "correlated_disclosed"
            whole["independence"]["human_acceptance_receipt_ref"] = "correlation-acceptance:CAREC-MISSING"
        elif mutation == "design_fixture_claims_runtime":
            value["runtime_assignments"] = True
        return validator.validate_role_assignments(value, mesh, final=False)
    if target == "correlation":
        bundle = copy.deepcopy(load("mesh/examples/design-time-independence-fixture.json"))
        bundle["bundle_id"] = "DMV3-BUNDLE-SYNTHETIC-CORRELATION-TEST"
        checker = bundle["assignments"][1]
        bundle["work_unit_id"] = checker["work_unit_id"]
        target_assignment = bundle["assignments"][0]
        collision_set = {"runtime_adapter"}
        receipt = {
            "schema_version": "logos.doctrine-marathon.correlation-acceptance-receipt.v3",
            "receipt_id": "CAREC-SYNTHETIC",
            "assignment_bundle_id": bundle["bundle_id"],
            "work_unit_id": checker["work_unit_id"],
            "checker_assignment_ref": f"role-assignment:{checker['assignment_id']}",
            "checker_input_digest": validator.object_digest(checker),
            "checked_assignment_refs": [f"role-assignment:{target_assignment['assignment_id']}"],
            "checked_input_digests": [validator.object_digest(target_assignment)],
            "collision_dimensions": sorted(collision_set),
            "checker_actor_instance_id": checker["actor_instance_id"],
            "checker_attempt_id": checker["attempt_id"],
            "decision": "accepted_for_bounded_unit",
            "human_decision_receipt_ref": "human-decision:HDEC-MISSING",
            "human_decision_receipt_digest": "sha256:" + "c" * 64,
            "issued_at": "2026-08-27T19:00:00Z",
            "expires_at": None,
            "receipt_digest": validator.ZERO_DIGEST,
        }
        if mutation == "mismatched_bundle_id":
            receipt["assignment_bundle_id"] = "DMV3-BUNDLE-SYNTHETIC-WRONG"
        elif mutation == "cross_unit_target":
            target_assignment["work_unit_id"] = "DMV3-SYNTHETIC-OTHER-UNIT"
            receipt["checked_input_digests"] = [
                validator.object_digest(target_assignment)
            ]
        elif mutation == "altered_target_digest":
            receipt["checked_input_digests"] = [validator.ZERO_DIGEST]
        elif mutation == "post_expiry_use":
            receipt["expires_at"] = "2026-08-27T19:30:00Z"
        receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
        return validator.validate_correlation_acceptance_receipt(
            receipt,
            bundle,
            checker,
            [target_assignment],
            collision_set,
            load("graph/authority-registry.yaml"),
            use_at=(
                validator.parse_time("2026-08-27T20:00:00Z")
                if mutation == "post_expiry_use"
                else None
            ),
        )
    if target == "correlation_reachability":
        return validator.validate_correlation_acceptance_reachability(
            {"events": []},
            {
                "correlation_acceptance_receipts": [{
                    "receipt_id": "CAREC-ORPHAN-VALID-AUTHORITY-SHAPE",
                    "decision": "accepted_for_bounded_unit",
                }]
            },
            load("graph/authority-registry.yaml"),
        )
    if target == "jewish":
        value = jewish_context_candidate()
        if mutation == "generic_community":
            value["community_display"] = "the Jews"
        elif mutation == "later_without_bridge":
            value["later_source_uses"] = [{"source_ref": "source-record:SRC-SYNTHETIC-A", "earlier_target_claim": "Synthetic earlier target claim", "bridge_method": "too short", "limitations": []}]
        return validator.validate_jewish_context_pack(value)
    if target == "evidence":
        if mutation == "unavailable_load_bearing_source":
            value = qualified_source()
            value["root_source_access"] = "unavailable"
            return validator.schema_errors(load("evidence/source-record.schema.json"), value, "negative source")
        if mutation in {"translation_without_lineage", "causal_claim_without_hypothesis"}:
            claim_type = "translation" if mutation == "translation_without_lineage" else "influence_or_causation"
            claim = claim_candidate(claim_type)
            if claim_type == "translation":
                claim["translation_lineage_ref"] = None
            else:
                claim["influence_hypothesis_ref"] = None
            return validator.schema_errors(load("evidence/claim-record.schema.json"), claim, "negative claim")
        if mutation == "self_attested_qualified_source":
            return validator.validate_evidence_registry(
                evidence_registry_candidate(sources=[qualified_source()]), final=False
            )
        if mutation == "verified_translation_candidate_lineage":
            source = qualified_source()
            lineage = translation_candidate()
            claim = claim_candidate("translation", "verified")
            claim["translation_lineage_digest"] = lineage["lineage_digest"]
            claim["evidence_digest"] = validator.object_digest(claim, omit=("evidence_digest",))
            return validator.validate_evidence_registry(
                evidence_registry_candidate(sources=[source], lineages=[lineage], claims=[claim]),
                final=False,
            )
        if mutation == "verified_influence_candidate_hypothesis":
            source_a = qualified_source()
            source_b = copy.deepcopy(source_a)
            source_b["source_record_id"] = "SRC-SYNTHETIC-B"
            source_b["title"] = "Synthetic source fixture B"
            source_b["content_digest"] = "sha256:" + "b" * 64
            source_b["qualification_scope_digest"] = validator.source_qualification_scope_digest(source_b)
            source_b["record_digest"] = validator.object_digest(source_b, omit=("record_digest",))
            hypothesis = influence_candidate()
            claim = claim_candidate("influence_or_causation", "verified")
            claim["influence_hypothesis_digest"] = hypothesis["hypothesis_digest"]
            claim["evidence_digest"] = validator.object_digest(claim, omit=("evidence_digest",))
            return validator.validate_evidence_registry(
                evidence_registry_candidate(sources=[source_a, source_b], hypotheses=[hypothesis], claims=[claim]),
                final=False,
            )
        if mutation == "verified_historical_without_attribution":
            claim = claim_candidate("historical_attribution", "verified")
            return validator.validate_evidence_registry(
                evidence_registry_candidate(sources=[qualified_source()], claims=[claim]),
                final=False,
            )
        if mutation == "verified_normative_unregistered_frame":
            claim = claim_candidate("normative_assessment", "verified")
            return validator.validate_evidence_registry(
                evidence_registry_candidate(sources=[qualified_source()], claims=[claim]),
                final=False,
            )
        if mutation == "claim_missing_status_dimension":
            claim = claim_candidate("synthesis")
            del claim["status_dimensions"]["rights_and_access"]
            return validator.schema_errors(load("evidence/claim-record.schema.json"), claim, "negative claim")
        if mutation in {"review_wrong_scope", "design_fixture_as_review_qualification"}:
            source = qualified_source()
            receipt = {
                "schema_version": "logos.doctrine-marathon.evidence-review-receipt.v3",
                "receipt_id": "EREV-SYNTHETIC",
                "review_kind": "source_qualification",
                "subject_ref": "source-record:SRC-SYNTHETIC-A",
                "subject_scope_digest": ("sha256:" + "b" * 64) if mutation == "review_wrong_scope" else source["qualification_scope_digest"],
                "assignment_bundle_ref": "mesh/examples/design-time-independence-fixture.json",
                "assignment_bundle_digest": validator.file_digest(validator.ROOT / "mesh/examples/design-time-independence-fixture.json"),
                "reviewer_assignment_refs": ["role-assignment:DMV3-ROLE-SYNTHETIC-META-CHECKER"],
                "required_capability_ids": ["role_qualification_and_independence"],
                "review_dimensions": ["identity", "rights", "fitness"],
                "evidence_bindings": [{"ref": "synthetic:evidence", "digest": "sha256:" + "c" * 64}],
                "decision": "qualified",
                "independence_assessment": "independent",
                "correlation_acceptance_receipt_ref": None,
                "issued_at": "2026-08-27T19:00:00Z",
                "expires_at": None,
                "authority_effect": "none",
                "receipt_digest": validator.ZERO_DIGEST,
            }
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
            source["qualification_receipt_refs"] = ["evidence-review:EREV-SYNTHETIC"]
            source["qualification_receipt_digests"] = [receipt["receipt_digest"]]
            source["record_digest"] = validator.object_digest(source, omit=("record_digest",))
            return validator.validate_evidence_registry(
                evidence_registry_candidate(sources=[source], reviews=[receipt]), final=False
            )
        if mutation == "arbitrary_file_as_review_receipt":
            source = qualified_source()
            source["qualification_receipt_refs"] = ["evidence-review:mesh-role-catalog"]
            source["qualification_receipt_digests"] = [validator.ZERO_DIGEST]
            source["record_digest"] = validator.object_digest(source, omit=("record_digest",))
            return validator.validate_evidence_registry(
                evidence_registry_candidate(sources=[source]), final=False
            )
    if target == "qualification":
        value = copy.deepcopy(load("mesh/qualification-registry.json"))
        value["runtime_records"] = True
        pack = {
            "schema_version": "logos.doctrine-marathon.expert-pack.v3",
            "expert_pack_id": "EPACK-SYNTHETIC",
            "revision": 1,
            "pack_kind": "father_or_corpus",
            "contract_ref": "research/father-expert-pack-contract.yaml",
            "contract_digest": validator.file_digest(validator.ROOT / "research/father-expert-pack-contract.yaml"),
            "capability_ids": ["father_corpus_expertise"],
            "scope": ["synthetic corpus"],
            "exclusions": ["no doctrine authority"],
            "source_manifest_bindings": [{"ref": "synthetic:manifest", "digest": "sha256:" + "a" * 64}],
            "fixture_result_bindings": [{"ref": "synthetic:fixture", "digest": "sha256:" + "b" * 64, "result": "pass"}],
            "qualification_scope_digest": validator.ZERO_DIGEST,
            "qualification_receipt_refs": [],
            "qualification_receipt_digests": [],
            "qualification_state": "qualified",
            "effective_at": "2026-08-27T19:00:00Z",
            "expires_at": None,
            "invalidation_triggers": ["source or contract changes"],
            "non_authority": {"doctrine_authority": False, "source_authority": False, "runtime_authority": False},
            "pack_digest": validator.ZERO_DIGEST,
        }
        pack["qualification_scope_digest"] = validator.object_digest({
            key: pack[key]
            for key in (
                "expert_pack_id", "revision", "pack_kind", "contract_ref",
                "contract_digest", "capability_ids", "scope", "exclusions",
                "source_manifest_bindings", "fixture_result_bindings",
            )
        })
        if mutation == "expert_pack_contract_digest_mismatch":
            pack["contract_digest"] = validator.ZERO_DIGEST
        if mutation == "nonexistent_qualification_reviewers":
            bundle_ref = "mesh/examples/design-time-independence-fixture.json"
            fixture_ref = "research/father-expert-pack-contract.yaml"
            receipt = {
                "schema_version": "logos.doctrine-marathon.qualification-receipt.v3",
                "receipt_id": "QREC-SYNTHETIC",
                "subject_kind": "expert_pack",
                "subject_ref": "expert-pack:EPACK-SYNTHETIC",
                "subject_scope_digest": pack["qualification_scope_digest"],
                "work_unit_id": "DMV3-SYNTHETIC-UNIT",
                "capability_ids": pack["capability_ids"],
                "expert_pack_ref": "expert-pack:EPACK-SYNTHETIC",
                "expert_pack_digest": pack["qualification_scope_digest"],
                "runtime_adapter_digest": None,
                "qualification_generation": 0,
                "reviewer_evidence_role": "supporting_non_authorizing",
                "bootstrap_authorization_ref": "human-decision:HDEC-MISSING",
                "bootstrap_authorization_digest": "sha256:" + "c" * 64,
                "qualification_input_digest": validator.ZERO_DIGEST,
                "reviewer_assignment_bundle_ref": bundle_ref,
                "reviewer_assignment_bundle_digest": validator.file_digest(validator.ROOT / bundle_ref),
                "reviewer_assignment_refs": [
                    "role-assignment:DMV3-ROLE-NONEXISTENT-A",
                    "role-assignment:DMV3-ROLE-NONEXISTENT-B",
                ],
                "fixture_bindings": [{
                    "ref": fixture_ref,
                    "digest": validator.file_digest(validator.ROOT / fixture_ref),
                    "result": "pass",
                }],
                "decision": "qualified",
                "abstention_fixture_passed": True,
                "independence_assessment": "independent",
                "human_approval_receipt_ref": "human-decision:HDEC-MISSING",
                "human_approval_receipt_digest": "sha256:" + "c" * 64,
                "issued_at": "2026-08-27T19:00:00Z",
                "expires_at": None,
                "authority_effect": "none",
                "receipt_digest": validator.ZERO_DIGEST,
            }
            receipt["qualification_input_digest"] = validator.object_digest({
                key: receipt[key]
                for key in (
                    "subject_kind", "subject_ref", "subject_scope_digest",
                    "work_unit_id", "capability_ids", "expert_pack_ref",
                    "expert_pack_digest", "runtime_adapter_digest",
                    "qualification_generation", "reviewer_evidence_role",
                    "bootstrap_authorization_ref", "bootstrap_authorization_digest",
                    "reviewer_assignment_bundle_ref",
                    "reviewer_assignment_bundle_digest",
                    "reviewer_assignment_refs", "fixture_bindings",
                )
            })
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
            pack["qualification_receipt_refs"] = ["qualification-receipt:QREC-SYNTHETIC"]
            pack["qualification_receipt_digests"] = [receipt["receipt_digest"]]
            value["qualification_receipts"] = [receipt]
        if mutation == "orphan_correlation_acceptance":
            bundle = copy.deepcopy(load("mesh/examples/design-time-independence-fixture.json"))
            checker = bundle["assignments"][1]
            checked = bundle["assignments"][0]
            acceptance = {
                "schema_version": "logos.doctrine-marathon.correlation-acceptance-receipt.v3",
                "receipt_id": "CAREC-ORPHAN-SYNTHETIC",
                "assignment_bundle_id": "DMV3-BUNDLE-SYNTHETIC-ORPHAN",
                "work_unit_id": checker["work_unit_id"],
                "checker_assignment_ref": f"role-assignment:{checker['assignment_id']}",
                "checker_input_digest": validator.object_digest(checker),
                "checked_assignment_refs": [f"role-assignment:{checked['assignment_id']}"],
                "checked_input_digests": [validator.object_digest(checked)],
                "collision_dimensions": ["runtime_adapter"],
                "checker_actor_instance_id": checker["actor_instance_id"],
                "checker_attempt_id": checker["attempt_id"],
                "decision": "accepted_for_bounded_unit",
                "human_decision_receipt_ref": "human-decision:HDEC-MISSING",
                "human_decision_receipt_digest": "sha256:" + "c" * 64,
                "issued_at": "2026-08-27T19:00:00Z",
                "expires_at": "2026-08-27T20:00:00Z",
                "receipt_digest": validator.ZERO_DIGEST,
            }
            acceptance["receipt_digest"] = validator.object_digest(
                acceptance, omit=("receipt_digest",)
            )
            value["correlation_acceptance_receipts"] = [acceptance]
        pack["pack_digest"] = validator.object_digest(pack, omit=("pack_digest",))
        value["expert_packs"] = [pack]
        value["registry_digest"] = validator.object_digest(value, omit=("registry_digest",))
        return validator.validate_qualification_registry(value, final=False)[0]
    if target == "admin":
        rows, manifest, receipt, review, authorization, saved, manifest_file, receipt_file, review_file, authorization_file = admin_fixture()
        if mutation == "manifest_tamper":
            manifest["schema_version"] = "tampered"
            manifest["manifest_digest"] = validator.object_digest(manifest, omit=("manifest_digest",))
        elif mutation == "validation_receipt_tamper":
            receipt["final_replay_command"] = "python untrusted.py"
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
        elif mutation == "review_tamper":
            review["reviewer_actor_instance_id"] = review["author_actor_instance_ids"][0]
            review["review_digest"] = validator.object_digest(review, omit=("review_digest",))
        elif mutation == "saved_receipt_file_tamper":
            saved["validation_receipt_file_digest"] = validator.ZERO_DIGEST
            saved["final_digest"] = validator.object_digest(saved, omit=("final_digest",))
        elif mutation == "final_self_tamper":
            saved["qualified_theological_authority"] = True
            saved["final_digest"] = validator.object_digest(saved, omit=("final_digest",))
        elif mutation == "review_coverage_tamper":
            review["reviewed_controls"].remove("admin_freeze")
            review["review_digest"] = validator.object_digest(review, omit=("review_digest",))
        elif mutation == "receipt_authority_tamper":
            receipt["runtime_activation_authorized"] = True
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
        elif mutation == "saved_release_authority_tamper":
            saved["public_release_authorization_object_digest"] = validator.ZERO_DIGEST
            saved["final_digest"] = validator.object_digest(saved, omit=("final_digest",))
        elif mutation == "authorization_payload_tamper":
            authorization["bound_payload"]["payload_digest"] = validator.ZERO_DIGEST
            authorization["authorization_digest"] = validator.object_digest(authorization, omit=("authorization_digest",))
            saved["public_release_authorization_object_digest"] = authorization["authorization_digest"]
            saved["final_digest"] = validator.object_digest(saved, omit=("final_digest",))
        elif mutation == "authorization_ceiling_tamper":
            authorization["authority_limits"]["runtime_activation_authorized"] = True
            authorization["authorization_digest"] = validator.object_digest(authorization, omit=("authorization_digest",))
            saved["public_release_authorization_object_digest"] = authorization["authorization_digest"]
            saved["final_digest"] = validator.object_digest(saved, omit=("final_digest",))
        elif mutation == "manifest_exclusion_tamper":
            manifest["administrative_files_excluded_from_payload_digest"].pop()
            manifest["manifest_digest"] = validator.object_digest(manifest, omit=("manifest_digest",))
        elif mutation == "receipt_validator_digest_tamper":
            receipt["validator_digest"] = validator.ZERO_DIGEST
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
        elif mutation == "review_cross_provider_tamper":
            review["cross_provider_verified"] = True
            review["review_digest"] = validator.object_digest(review, omit=("review_digest",))
        elif mutation == "manifest_unknown_field":
            manifest["unreviewed_escape_hatch"] = True
            manifest["manifest_digest"] = validator.object_digest(manifest, omit=("manifest_digest",))
        elif mutation == "receipt_work_id_tamper":
            receipt["work_id"] = "WORK-UNAUTHORIZED"
            receipt["receipt_digest"] = validator.object_digest(receipt, omit=("receipt_digest",))
        return validator.validate_admin_records(
            manifest, receipt, review, authorization, saved, rows,
            manifest_file, receipt_file, review_file, authorization_file,
        )
    if target == "privacy":
        synthetic_path = "C" + ":" + "\\" + "private\\artifact"
        return ["public_local_path: synthetic"] if validator.LOCAL_PATH_RE.search(synthetic_path) else []
    raise AssertionError(f"unknown target {target}")


def strict_isolated_cases() -> list[tuple[str, Any, set[str]]]:
    """New repair regressions: one clean isolated positive, then one mutation."""
    return [
        (
            "ISO-ROLE-CAPABILITY",
            lambda: role_contract_fixture_errors("missing_role_capability"),
            {"role_assignment_role_capability_mismatch"},
        ),
        (
            "ISO-ROLE-META-COVERAGE",
            lambda: role_contract_fixture_errors("meta_coverage"),
            {"role_assignment_meta_checker_coverage"},
        ),
        (
            "ISO-ROLE-WHOLE-CHECKS-META",
            lambda: role_contract_fixture_errors("whole_checks_meta"),
            {"role_assignment_whole_work_checks_meta_checker"},
        ),
        (
            "ISO-COMPLETENESS-REQUIRED-FACET",
            lambda: completeness_contract_fixture_errors("required_facet"),
            {"completeness_contract_integrity"},
        ),
        (
            "ISO-COMPLETENESS-CANONICALIZATION",
            lambda: completeness_contract_fixture_errors("canonicalization"),
            {"completeness_contract_integrity"},
        ),
        (
            "ISO-COMPLETENESS-PHASE-BINDING",
            lambda: completeness_contract_fixture_errors("phase_receipt_binding"),
            {"completeness_contract_integrity"},
        ),
        (
            "ISO-COMPLETENESS-NONMATERIAL-RECOVERY",
            lambda: completeness_contract_fixture_errors("nonmaterial_recovery"),
            {"completeness_contract_integrity"},
        ),
        (
            "ISO-COMPLETENESS-HARD-FAIL-CODE",
            lambda: completeness_contract_fixture_errors("hard_fail_code"),
            {"completeness_contract_integrity"},
        ),
        (
            "ISO-CONSTITUTION-HUMAN-GATES",
            lambda: core_contract_fixture_errors("constitution"),
            {"constitution_contract_integrity"},
        ),
        (
            "ISO-CAMPAIGN-FRESH-CONTEXT",
            lambda: core_contract_fixture_errors("campaign"),
            {"campaign_contract_integrity"},
        ),
        (
            "ISO-MESH-ONE-WRITER",
            lambda: core_contract_fixture_errors("mesh"),
            {"mesh_contract_integrity"},
        ),
        (
            "ISO-PROMPT-NEUTRALITY-VERBS",
            lambda: core_contract_fixture_errors("prompt_neutrality"),
            {"prompt_neutrality_contract_integrity"},
        ),
        (
            "ISO-PROMPT-DIGEST",
            lambda: prompt_runtime_fixture_errors("task_prompt_digest"),
            {"role_assignment_task_prompt_digest"},
        ),
        (
            "ISO-PROMPT-REVIEW-INDEPENDENCE",
            lambda: prompt_runtime_fixture_errors("prompt_review_self"),
            {"role_assignment_prompt_review_independence"},
        ),
        (
            "ISO-EXPERT-SOURCE-REF",
            lambda: expert_pack_fixture_errors("source_ref"),
            {"expert_pack_source_manifest_ref"},
        ),
        (
            "ISO-EXPERT-SOURCE-DIGEST",
            lambda: expert_pack_fixture_errors("source_digest"),
            {"expert_pack_source_manifest_digest"},
        ),
        (
            "ISO-EXPERT-FIXTURE-REF",
            lambda: expert_pack_fixture_errors("fixture_ref"),
            {"expert_pack_fixture_ref"},
        ),
        (
            "ISO-EXPERT-FIXTURE-DIGEST",
            lambda: expert_pack_fixture_errors("fixture_digest"),
            {"expert_pack_fixture_digest"},
        ),
        (
            "ISO-GRAPH-PREREQUISITE-BASIS",
            graph_prerequisite_fixture_errors,
            {"graph_prerequisite_basis"},
        ),
        (
            "ISO-EVIDENCE-PRODUCER-DIGEST",
            lambda: evidence_binding_fixture_errors("producer_digest"),
            {"evidence_review_producer_digest"},
        ),
        (
            "ISO-EVIDENCE-PRODUCER-INDEPENDENCE",
            lambda: evidence_binding_fixture_errors("producer_independence"),
            {"evidence_review_producer_independence"},
        ),
        (
            "ISO-EVIDENCE-REVIEW-KIND-CAPABILITIES",
            lambda: evidence_binding_fixture_errors("review_kind_capabilities"),
            {"evidence_review_required_capabilities"},
        ),
        (
            "ISO-MIDFLIGHT-ACTION-BUNDLE-DIGEST",
            lambda: midflight_binding_fixture_errors("action_bundle_digest"),
            {"event_midflight_action_bundle_digest"},
        ),
        (
            "ISO-MIDFLIGHT-CHECKER-DIGEST",
            lambda: midflight_binding_fixture_errors("checker_digest"),
            {"event_midflight_action_checker_digest"},
        ),
        (
            "ISO-MIDFLIGHT-EVIDENCE-DIGEST",
            lambda: midflight_binding_fixture_errors("evidence_digest"),
            {"event_midflight_action_evidence_digest"},
        ),
        (
            "ISO-WEEKLY-RECEIPT-FILE-DIGEST",
            lambda: weekly_receipt_fixture_errors("receipt_file_digest"),
            {"weekly_verification_receipt_file_digest"},
        ),
        (
            "ISO-WEEKLY-RECEIPT-OBJECT-DIGEST",
            lambda: weekly_receipt_fixture_errors("receipt_object_digest"),
            {"weekly_verification_receipt_object_digest"},
        ),
        (
            "ISO-WEEKLY-CONTROL-BINDING",
            lambda: weekly_receipt_fixture_errors("control_binding"),
            {"weekly_verification_control_binding"},
        ),
        (
            "ISO-AUTHORITY-ROOT-FILE-DIGEST",
            lambda: authority_binding_fixture_errors("identity_root_file_digest"),
            {"authority_identity_root_file_digest"},
        ),
        (
            "ISO-AUTHORITY-ACTIVATION-FAIL-CLOSED",
            lambda: authority_binding_fixture_errors("identity_root_activation"),
            {"authority_identity_root_activation_unimplemented"},
        ),
        (
            "ISO-AUTHORITY-QUALIFICATION-ROOT",
            lambda: authority_binding_fixture_errors("qualification_root"),
            {"authority_qualification_identity_root"},
        ),
        (
            "ISO-AUTHORITY-QUALIFICATION-EVIDENCE",
            lambda: authority_binding_fixture_errors("qualification_evidence"),
            {
                "authority_qualification_identity_root",
                "authority_qualification_evidence_binding",
            },
        ),
        (
            "ISO-HUMAN-DECISION-ATTESTATION",
            lambda: authority_binding_fixture_errors("attestation_binding"),
            {"human_decision_attestation_binding"},
        ),
    ]


def bind_strict_isolated_cases() -> list[tuple[str, Any, str, tuple[str, ...]]]:
    catalog = json.loads(STRICT_ISOLATED_CATALOG.read_text(encoding="utf-8"))
    assert set(catalog) == {
        "metadata", "schema_version", "assurance_use", "cases"
    }
    assert catalog["schema_version"] == (
        "logos.doctrine_marathon.strict_isolated_case_catalog.v1"
    )
    assert catalog["assurance_use"] == "none_pending_aggregate_adapter"

    executable = strict_isolated_cases()
    declared = catalog["cases"]
    assert [row[0] for row in executable] == [row["case_id"] for row in declared], (
        "strict isolated executable IDs drifted from the exact catalog"
    )

    bound: list[tuple[str, Any, str, tuple[str, ...]]] = []
    for (case_id, runner, legacy_expected_rules), row in zip(
        executable, declared, strict=True
    ):
        assert set(row) == {
            "case_id", "intended_rule", "expected_findings_ordered"
        }, case_id
        expected_findings = tuple(row["expected_findings_ordered"])
        assert expected_findings, case_id
        expected_rules = {finding.split(":", 1)[0] for finding in expected_findings}
        assert expected_rules == legacy_expected_rules, (
            f"{case_id} exact catalog no longer matches its retained rule contract"
        )
        assert expected_findings[0].split(":", 1)[0] == row["intended_rule"], (
            f"{case_id} intended rule is not the exact primary finding"
        )
        bound.append((case_id, runner, row["intended_rule"], expected_findings))
    return bound


def run_strict_isolated_cases(
    cases: list[tuple[str, Any, str, tuple[str, ...]]]
) -> dict[str, tuple[str, ...]]:
    observed_by_id: dict[str, tuple[str, ...]] = {}
    for case_id, runner, intended_rule, expected_findings in cases:
        clear_validator_caches()
        observed = runner()
        assert tuple(observed) == expected_findings, (
            f"{case_id} expected exact ordered findings {expected_findings}, "
            f"got {tuple(observed)}"
        )
        assert observed[0].split(":", 1)[0] == intended_rule, (
            f"{case_id} intended rule {intended_rule} was not primary: {observed}"
        )
        observed_by_id[case_id] = tuple(observed)
        clear_validator_caches()
    return observed_by_id


def main() -> int:
    isolated_cases = bind_strict_isolated_cases()
    forward = run_strict_isolated_cases(isolated_cases)
    reverse = run_strict_isolated_cases(list(reversed(isolated_cases)))
    assert forward == reverse, f"isolated cases are order-dependent: {forward} != {reverse}"
    clear_validator_caches()
    authority_baseline = validator.validate_authority_registry(
        load("graph/authority-registry.yaml"), final=False
    )
    assert not authority_baseline, (
        "inactive authority baseline failed:\n" + "\n".join(authority_baseline)
    )
    completion_baseline_errors = completion_gate_fixture_errors("valid")
    assert len(completion_baseline_errors) == 1 and completion_baseline_errors[0].startswith(
        "terminal_completion_authority_validation: "
        "authority_identity_root_activation_unimplemented:"
    ), (
        "completion fixture did not fail closed at the deliberate identity-root gate:\n"
        + "\n".join(completion_baseline_errors)
    )
    cases = json.loads((HERE / "fixtures/negative-cases.json").read_text(encoding="utf-8"))
    seen: set[str] = set()
    for case in cases:
        assert case["case_id"] not in seen
        seen.add(case["case_id"])
        observed = run_case(case)
        assert case["expected_rule"] in rules(observed), f"{case['case_id']} expected {case['expected_rule']}, got {observed}"
    assert len(cases) >= 30
    clear_validator_caches()
    baseline_errors, metrics = validator.validate_all("draft")
    assert not baseline_errors, "draft baseline failed:\n" + "\n".join(baseline_errors)
    clear_validator_caches()
    prefinal_errors, _prefinal_metrics = validator.validate_all("prefinal")
    assert not prefinal_errors, (
        "strict prefinal baseline failed:\n" + "\n".join(prefinal_errors)
    )
    final_result: dict[str, Any] | None = None
    if all((validator.ROOT / relative).is_file() for relative in validator.ADMIN_FILES):
        final_errors, final_metrics = validator.validate_all("final")
        migration = load("checks/adversarial-harness-migration.yaml")
        if migration.get("release_evidence_eligible") is False:
            expected_release_blocker = (
                "adversarial_harness_release_gate: V3 cannot release until the "
                "aggregate exact-oracle migration is complete and independently reviewed"
            )
            assert final_errors == [expected_release_blocker], (
                "blocked specification must retain exactly the named final-release "
                f"blocker, got {final_errors}"
            )
            final_result = {
                "status": "blocked_expected_aggregate_migration",
                "primary_finding": final_errors[0],
                "finding_count": len(final_errors),
                "metrics": final_metrics,
            }
        else:
            assert not final_errors, (
                "final integration baseline failed:\n" + "\n".join(final_errors)
            )
            final_result = final_metrics
    print(json.dumps({
        "status": "pass",
        "positive_baseline": metrics,
        "inactive_authority_baseline": "pass",
        "completion_fixture": "expected_fail_closed_identity_root_activation_unimplemented",
        "catalog_negative_cases_passed": len(cases),
        "isolated_exact_negative_cases_passed": len(isolated_cases),
        "isolated_order_independence": "forward_and_reverse_pass",
        "total_negative_cases_passed": len(cases) + len(isolated_cases),
        "final_integration_state": final_result,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
