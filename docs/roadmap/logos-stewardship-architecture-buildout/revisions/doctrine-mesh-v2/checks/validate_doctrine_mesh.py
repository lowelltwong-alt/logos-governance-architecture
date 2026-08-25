#!/usr/bin/env python3
"""
object_type: doctrine_mesh_revision_validator
trust_zone: proposed
lifecycle_status: active
provenance_note: Created on 2026-08-24 by Codex root.
reason_for_inclusion: Deterministically validate the saved whole-doctrine mesh,
audit-event presence, authority boundaries, negative cases, and frozen digests.

This validator proves that required audit executions left exact, ordered,
hash-bound evidence. It does not prove that an auditor identified every useful
expert or that any candidate doctrinal claim is true.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ADMIN_FILES = {
    "revision-manifest.yaml",
    "checks/validation-receipt.json",
    "checks/independent-review.json",
    "fable/fable-review-manifest.yaml",
    "FINAL-SAVED-VERSION.yaml",
}
REQUIRED_ROLES = {
    "doctrine-mesh-completeness-auditor",
    "doctrine-task-local-role-factory",
    "bounded-domain-researcher",
    "citation-locator-verifier",
    "source-authority-verifier",
    "claim-entailment-verifier",
    "counterevidence-challenger",
    "tradition-representation-auditor",
    "goal-alignment-authority-auditor",
    "doctrine-evidence-integrator",
    "risk-human-gate-router",
    "independent-whole-work-checker",
}
REQUIRED_TAXONOMY_IDS = {
    "DOM-HEBREW-TEXT", "DOM-SEPTUAGINT", "DOM-NT-TEXT", "DOM-SECOND-TEMPLE",
    "DOM-QUMRAN", "DOM-JEWISH-MYSTICISM", "DOM-TWO-POWERS", "DOM-EGYPT",
    "DOM-ASSYRIOLOGY", "DOM-BABYLON-RELIGION", "DOM-ARCHAEOLOGY",
    "DOM-PLATO", "DOM-ARISTOTLE", "DOM-CULTURAL-GENEALOGY",
    "DOM-GREEK-PATRISTICS", "DOM-LATIN-PATRISTICS", "DOM-COUNCILS",
    "DOM-HERESIOLOGY", "DOM-AUGUSTINE", "DOM-AQUINAS", "DOM-CATHOLIC",
    "DOM-LUTHER", "DOM-LUTHERAN", "DOM-REFORMED", "DOM-PRESBYTERIAN",
    "DOM-ANGLICAN", "DOM-ANABAPTIST", "DOM-BAPTIST", "DOM-WESLEYAN",
    "DOM-PENTECOSTAL",
}
TIER_RANK = {"low": 0, "medium": 1, "high": 2, "frontier": 3}
RISK_TAG_FLOORS = {
    "formatting_or_locator_metadata_no_authority_effect": "low",
    "bounded_descriptive_history": "medium",
    "task_local_role_composition": "medium",
    "non_normative_ancient_context": "medium",
    "doctrine_interpretation": "high",
    "tradition_or_Jewish_community_representation": "high",
    "disputed_source_fitness": "high",
    "historical_influence_or_cultural_genealogy": "high",
    "human_expert_gap": "high",
    "canon_normativity_orthodoxy_heresy": "frontier",
    "cross_repository_authority_or_topology": "frontier",
    "systemic_autonomy_or_controller_change": "frontier",
    "private_restricted_or_credentialed_corpus": "frontier",
    "irreversible_publication": "frontier",
}
SURFACE_REQUIRED_TAG = {
    "none": "formatting_or_locator_metadata_no_authority_effect",
    "formatting_or_locator_metadata": "formatting_or_locator_metadata_no_authority_effect",
    "descriptive_history": "bounded_descriptive_history",
    "task_local_role_composition": "task_local_role_composition",
    "ancient_non_normative_context": "non_normative_ancient_context",
    "scripture_interpretation": "doctrine_interpretation",
    "doctrine_interpretation": "doctrine_interpretation",
    "tradition_representation": "tradition_or_Jewish_community_representation",
    "Jewish_community_representation": "tradition_or_Jewish_community_representation",
    "disputed_source_fitness": "disputed_source_fitness",
    "historical_influence": "historical_influence_or_cultural_genealogy",
    "rights_privacy": "disputed_source_fitness",
    "canon_normativity_orthodoxy_heresy": "canon_normativity_orthodoxy_heresy",
    "cross_repository_authority_or_topology": "cross_repository_authority_or_topology",
    "systemic_autonomy_or_controller": "systemic_autonomy_or_controller_change",
    "private_restricted_or_credentialed_corpus": "private_restricted_or_credentialed_corpus",
    "irreversible_publication": "irreversible_publication",
}
BUDGET_DIMENSIONS = (
    "wall_clock_seconds", "tokens", "cost_minor_units", "storage_bytes",
    "network_requests", "assignments", "audit_events", "generated_profiles",
    "human_packets",
)
CAPABILITY_CLASSES = {
    "portable_core",
    "runtime_adapter",
    "project_governance_instance",
    "revision_evidence",
}
CAMPAIGN_GATE_RULES = {
    "DMG-001": ("source_lock_valid", "pass"),
    "DMG-002": ("schema_valid", "pass"),
    "DMG-003": ("manual_audit_receipt_pass", "pass"),
    "DMG-004": ("dormant_factory_contract_valid", "pass"),
    "DMG-005": ("specification_contract_valid", "pass"),
    "DMG-006": ("all_human_gates_blocked", "blocked_human"),
    "DMG-007": ("manual_audit_receipt_pass", "pass"),
    "DMG-008": ("manual_audit_receipt_pass", "pass"),
    "DMG-009": ("independent_specification_review_pass", "pass_specification_only"),
    "DMG-010": ("dormant_manual_review_packet_valid", "packet_integrity_pass_external_review_not_sent"),
}


def load_data(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def is_volatile_runtime_file(relative_path: Path) -> bool:
    """Exclude interpreter caches from the authored, portable freeze payload."""
    return relative_path.suffix.lower() == ".pyc" or "__pycache__" in relative_path.parts


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def object_digest(value: Any, omit: Iterable[str] = ()) -> str:
    clone = copy.deepcopy(value)
    for key in omit:
        if isinstance(clone, dict):
            clone.pop(key, None)
    return "sha256:" + hashlib.sha256(canonical_bytes(clone)).hexdigest()


def canonical_file_bytes(path: Path) -> bytes:
    """Normalize valid UTF-8 newlines; preserve invalid-UTF-8 bytes exactly."""
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(canonical_file_bytes(path)).hexdigest()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def schema_errors(schema: dict[str, Any], instance: Any, label: str) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{label}: schema error at {location}: {error.message}")
    return errors


def check_schema(schema: dict[str, Any], label: str) -> list[str]:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # noqa: BLE001 - malformed schemas must fail closed
        return [f"schema: invalid {label}: {exc}"]
    return []


def repository_relative_segments(value: object) -> tuple[str, ...] | None:
    """Parse a canonical, portable repository-relative path without filesystem access."""
    if not isinstance(value, str) or not value:
        return None
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        return None
    if "\\" in value or any(ord(character) < 32 or ord(character) == 127 for character in value):
        return None
    segments = value.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        return None
    return tuple(segments)


def is_strict_path_descendant(child: tuple[str, ...], parent: tuple[str, ...]) -> bool:
    """Return true only when child is below parent at a complete path-segment boundary."""
    return len(child) > len(parent) and child[: len(parent)] == parent


def acyclic(role_ids: set[str], roles: list[dict[str, Any]]) -> bool:
    dependencies = {role["role_id"]: set(role.get("dependencies", [])) for role in roles}
    if any(not deps <= role_ids for deps in dependencies.values()):
        return False
    temporary: set[str] = set()
    permanent: set[str] = set()

    def visit(node: str) -> bool:
        if node in permanent:
            return True
        if node in temporary:
            return False
        temporary.add(node)
        if not all(visit(dep) for dep in dependencies[node]):
            return False
        temporary.remove(node)
        permanent.add(node)
        return True

    return all(visit(node) for node in role_ids)


def graph_acyclic(node_ids: set[str], edges: list[dict[str, Any]], ignored_types: set[str]) -> bool:
    successors = {node_id: set() for node_id in node_ids}
    for edge in edges:
        if edge.get("type") in ignored_types:
            continue
        source = edge.get("from")
        target = edge.get("to")
        if source not in successors or target not in successors:
            return False
        successors[source].add(target)
    temporary: set[str] = set()
    permanent: set[str] = set()

    def visit(node: str) -> bool:
        if node in permanent:
            return True
        if node in temporary:
            return False
        temporary.add(node)
        if not all(visit(target) for target in successors[node]):
            return False
        temporary.remove(node)
        permanent.add(node)
        return True

    return all(visit(node) for node in node_ids)


def compute_risk_floor(tags: list[str]) -> str:
    if not tags or any(tag not in RISK_TAG_FLOORS for tag in tags):
        raise ValueError("unknown or missing risk tag")
    return max((RISK_TAG_FLOORS[tag] for tag in tags), key=TIER_RANK.__getitem__)


def decision_record_digest(record: dict[str, Any]) -> str:
    clone = copy.deepcopy(record)
    clone.get("identity", {}).pop("record_hash", None)
    return object_digest(clone)


def validate_decision_semantics(record: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    identity = record.get("identity", {}).get("decision_id", "unknown")
    scope = record.get("scope", {})
    risk = record.get("risk", {})
    review = record.get("review", {})
    authority = record.get("authority", {})
    try:
        submitted_tags = scope.get("risk_tags", [])
        surfaces = scope.get("protected_surfaces", [])
        required_tags = {SURFACE_REQUIRED_TAG[surface] for surface in surfaces if surface in SURFACE_REQUIRED_TAG}
        if any(surface not in SURFACE_REQUIRED_TAG for surface in surfaces) or not required_tags <= set(submitted_tags):
            failures.append(f"decision: protected-surface risk tag missing {identity}")
        expected_floor = compute_risk_floor(submitted_tags)
        if risk.get("computed_minimum_floor") != expected_floor:
            failures.append(f"decision: computed floor mismatch {identity}")
    except ValueError:
        failures.append(f"decision: invalid risk tags {identity}")
    triggers = set(scope.get("materiality_triggers", []))
    expected_material = bool(scope.get("downstream_consumers")) or bool(triggers - {"no_material_trigger"})
    if expected_material and scope.get("material") is not True:
        failures.append(f"decision: materiality underdeclared {identity}")
    if not expected_material and scope.get("material") is not False:
        failures.append(f"decision: materiality overdeclared without trigger {identity}")
    actor_ids = [review.get("writer_actor_instance_id")]
    actor_ids.extend(review.get("checker_actor_instance_ids", []))
    actor_ids.extend(review.get("challenger_actor_instance_ids", []))
    if None in actor_ids or len(actor_ids) != len(set(actor_ids)):
        failures.append(f"decision: actor independence collision {identity}")
    floor = risk.get("computed_minimum_floor")
    if scope.get("material") and floor in {"high", "frontier"} and not authority.get("valid_receipt_refs"):
        failures.append(f"decision: high-risk material decision lacks human receipt {identity}")
    if risk.get("slicing_check_status") != "pass_bundle_complete":
        failures.append(f"decision: bundle slicing check not passed {identity}")
    return failures


def validate_decision_chain(records: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    by_id: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        identity = record.get("identity", {})
        decision_id = identity.get("decision_id", "unknown")
        by_id.setdefault(decision_id, []).append(record)
        if identity.get("record_hash") != decision_record_digest(record):
            failures.append(f"decision: record hash mismatch {decision_id} revision {identity.get('revision')}")
    for decision_id, revisions in by_id.items():
        ordered = sorted(revisions, key=lambda item: item.get("identity", {}).get("revision", 0))
        expected_revisions = list(range(1, len(ordered) + 1))
        actual_revisions = [item.get("identity", {}).get("revision") for item in ordered]
        if actual_revisions != expected_revisions:
            failures.append(f"decision: revision sequence mismatch {decision_id}")
        prior_hash: str | None = None
        for record in ordered:
            if record.get("identity", {}).get("prior_hash") != prior_hash:
                failures.append(f"decision: prior hash mismatch {decision_id} revision {record.get('identity', {}).get('revision')}")
            prior_hash = record.get("identity", {}).get("record_hash")
    return failures


def validate_qualification_semantics(receipt: dict[str, Any], evaluation_at: datetime) -> list[str]:
    failures: list[str] = []
    receipt_id = receipt.get("receipt_id", "unknown")
    try:
        observed_at = parse_time(receipt["observed_at"])
        expires_at = parse_time(receipt["expires_at"])
    except (KeyError, TypeError, ValueError):
        return [f"qualification: invalid time {receipt_id}"]
    if expires_at <= observed_at:
        failures.append(f"qualification: expiry not after observation {receipt_id}")
    if receipt.get("status") == "qualified_exact_revision":
        if expires_at <= evaluation_at:
            failures.append(f"qualification: qualified receipt expired {receipt_id}")
        if receipt.get("deterministic_results", {}).get("failed") != 0 or receipt.get("meets_all_thresholds") is not True:
            failures.append(f"qualification: qualified receipt failed thresholds {receipt_id}")
    if receipt.get("receipt_digest") != object_digest(receipt, ("receipt_digest",)):
        failures.append(f"qualification: receipt digest mismatch {receipt_id}")
    return failures


def validate_budget_ledger_semantics(
    ledger: dict[str, Any],
    predecessor: dict[str, Any] | None = None,
    prior_journal_entries: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Validate arithmetic and hash-chain properties JSON Schema cannot express."""
    failures: list[str] = []
    ledger_id = ledger.get("ledger_id", "unknown")
    if ledger.get("ledger_digest") != object_digest(ledger, ("ledger_digest",)):
        failures.append(f"budget: ledger digest mismatch {ledger_id}")
    sequence = ledger.get("sequence")
    if predecessor is None:
        if sequence != 1 or ledger.get("previous_ledger_digest") is not None:
            failures.append(f"budget: initial sequence or predecessor mismatch {ledger_id}")
        base_consumed = {dimension: 0 for dimension in BUDGET_DIMENSIONS}
        base_reserved = {dimension: 0 for dimension in BUDGET_DIMENSIONS}
    else:
        if ledger.get("ledger_id") != predecessor.get("ledger_id") or ledger.get("campaign_id") != predecessor.get("campaign_id"):
            failures.append(f"budget: predecessor identity mismatch {ledger_id}")
        if sequence != predecessor.get("sequence", 0) + 1:
            failures.append(f"budget: predecessor sequence mismatch {ledger_id}")
        if ledger.get("previous_ledger_digest") != predecessor.get("ledger_digest"):
            failures.append(f"budget: predecessor digest mismatch {ledger_id}")
        if ledger.get("authorized_ceiling") != predecessor.get("authorized_ceiling"):
            failures.append(f"budget: authorized ceiling changed {ledger_id}")
        base_consumed = predecessor.get("consumed", {})
        base_reserved = predecessor.get("reserved", {})

    entries = ledger.get("journal_entries", [])
    for field in ("debit_id", "idempotency_key", "attempt_id"):
        values = [entry.get(field) for entry in entries]
        if None in values or len(values) != len(set(values)):
            failures.append(f"budget: duplicate or missing {field} {ledger_id}")
        prior_values = {entry.get(field) for entry in (prior_journal_entries or [])}
        if any(value in prior_values for value in values):
            failures.append(f"budget: reused {field} across snapshots {ledger_id}")
    work_units = ledger.get("work_units", [])
    unit_ids = [row.get("work_unit_id") for row in work_units]
    if None in unit_ids or len(unit_ids) != len(set(unit_ids)):
        failures.append(f"budget: duplicate or missing work unit {ledger_id}")

    for dimension in BUDGET_DIMENSIONS:
        try:
            consumed = ledger["consumed"][dimension]
            reserved = ledger["reserved"][dimension]
            remaining = ledger["remaining"][dimension]
            ceiling = ledger["authorized_ceiling"][dimension]
            delta_consumed = sum(entry["consumed_delta"][dimension] for entry in entries)
            delta_reserved = sum(entry["reserved_delta"][dimension] for entry in entries)
            unit_consumed = sum(row["consumed"][dimension] for row in work_units)
            unit_reserved = sum(row["reserved"][dimension] for row in work_units)
            if consumed + reserved + remaining != ceiling:
                failures.append(f"budget: ceiling reconciliation mismatch {ledger_id} {dimension}")
            if consumed != base_consumed[dimension] + delta_consumed:
                failures.append(f"budget: consumed journal mismatch {ledger_id} {dimension}")
            if reserved != base_reserved[dimension] + delta_reserved:
                failures.append(f"budget: reserved journal mismatch {ledger_id} {dimension}")
            if consumed != unit_consumed or reserved != unit_reserved:
                failures.append(f"budget: work-unit reconciliation mismatch {ledger_id} {dimension}")
        except (KeyError, TypeError):
            failures.append(f"budget: missing dimension {ledger_id} {dimension}")
    for entry in entries:
        entry_type = entry.get("entry_type")
        consumed_delta = entry.get("consumed_delta", {})
        reserved_delta = entry.get("reserved_delta", {})
        if entry_type == "reservation" and (
            any(consumed_delta.get(dimension) != 0 for dimension in BUDGET_DIMENSIONS)
            or any(reserved_delta.get(dimension, -1) < 0 for dimension in BUDGET_DIMENSIONS)
        ):
            failures.append(f"budget: invalid reservation delta {entry.get('debit_id')}")
        if entry_type == "debit" and any(reserved_delta.get(dimension, 1) > 0 for dimension in BUDGET_DIMENSIONS):
            failures.append(f"budget: debit increases reservation {entry.get('debit_id')}")
        if entry_type == "release" and (
            any(consumed_delta.get(dimension) != 0 for dimension in BUDGET_DIMENSIONS)
            or any(reserved_delta.get(dimension, 1) > 0 for dimension in BUDGET_DIMENSIONS)
        ):
            failures.append(f"budget: invalid release delta {entry.get('debit_id')}")
    return failures


def validate_job_binding_semantics(
    binding: dict[str, Any],
    ledger_snapshot_index: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Validate participant, claim-scope, and ledger bindings beyond JSON Schema."""
    failures: list[str] = []
    assignment_id = binding.get("assignment_id", "unknown")
    roles = binding.get("roles", {})
    writer = roles.get("writer", {})
    checkers = roles.get("checkers", [])
    challengers = roles.get("challengers", [])
    participants = [writer, *checkers, *challengers]
    for field in ("actor_instance_id", "independence_group"):
        values = [participant.get(field) for participant in participants]
        if None in values or len(values) != len(set(values)):
            failures.append(f"job: participant {field} collision {assignment_id}")
    claimed_scope = binding.get("claimed_scope_ref", "")
    claimed_segments = repository_relative_segments(claimed_scope)
    if claimed_segments is None:
        failures.append(f"job: invalid claimed scope path {assignment_id}")
    writer_scope = writer.get("write_scope")
    if (
        not isinstance(writer_scope, list)
        or len(writer_scope) != 1
        or repository_relative_segments(writer_scope[0]) is None
    ):
        failures.append(f"job: invalid writer write scope path {assignment_id}")
    if writer_scope != [claimed_scope]:
        failures.append(f"job: writer scope does not equal claimed scope {assignment_id}")
    if any(participant.get("write_scope") for participant in [*checkers, *challengers]):
        failures.append(f"job: checker or challenger has write scope {assignment_id}")
    effect_scope = binding.get("data_and_effects", {}).get("write_scope")
    if (
        not isinstance(effect_scope, list)
        or len(effect_scope) != 1
        or repository_relative_segments(effect_scope[0]) is None
    ):
        failures.append(f"job: invalid effect write scope path {assignment_id}")
    if effect_scope != [claimed_scope]:
        failures.append(f"job: effect write scope does not equal claimed scope {assignment_id}")
    claim_digest = binding.get("work_claim_digest")
    for input_artifact in binding.get("inputs", []):
        if repository_relative_segments(input_artifact.get("canonical_path", "")) is None:
            failures.append(f"job: invalid input canonical path {assignment_id}")
    for output in binding.get("outputs", []):
        output_segments = repository_relative_segments(output.get("canonical_path", ""))
        if output_segments is None:
            failures.append(f"job: invalid output canonical path {assignment_id}")
        elif claimed_segments is None or not is_strict_path_descendant(output_segments, claimed_segments):
            failures.append(f"job: output does not descend from claimed scope {assignment_id}")
        if output.get("work_claim_digest") != claim_digest:
            failures.append(f"job: output work-claim digest mismatch {assignment_id}")
    budget = binding.get("budget_binding", {})
    if budget.get("campaign_id") != binding.get("campaign_id"):
        failures.append(f"job: budget campaign mismatch {assignment_id}")
    if ledger_snapshot_index is not None:
        ledger_ref = budget.get("ledger_snapshot_ref")
        ledger = ledger_snapshot_index.get(ledger_ref)
        if ledger is None:
            failures.append(f"job: missing budget ledger snapshot {assignment_id}")
            return failures
        if (
            budget.get("ledger_snapshot_digest") != ledger.get("ledger_digest")
            or budget.get("ledger_id") != ledger.get("ledger_id")
            or budget.get("ledger_sequence") != ledger.get("sequence")
            or budget.get("campaign_id") != ledger.get("campaign_id")
        ):
            failures.append(f"job: budget ledger identity or digest mismatch {assignment_id}")
        entries = ledger.get("journal_entries", [])
        controller = binding.get("controller", {})

        def matching_entry(entry_type: str, ref_field: str, digest_field: str) -> dict[str, Any] | None:
            return next(
                (
                    entry for entry in entries
                    if entry.get("entry_type") == entry_type
                    and entry.get("assignment_id") == assignment_id
                    and entry.get("work_unit_id") == binding.get("work_unit_id")
                    and entry.get("lease_fence") == controller.get("lease_fence")
                    and entry.get("receipt_ref") == budget.get(ref_field)
                    and entry.get("receipt_digest") == budget.get(digest_field)
                ),
                None,
            )

        reservation = matching_entry("reservation", "reservation_receipt_ref", "reservation_receipt_digest")
        if budget.get("reservation_receipt_ref") is not None:
            if reservation is None or reservation.get("idempotency_key") != budget.get("reservation_idempotency_key"):
                failures.append(f"job: reservation journal binding mismatch {assignment_id}")
        if budget.get("debit_receipt_ref") is not None and matching_entry("debit", "debit_receipt_ref", "debit_receipt_digest") is None:
            failures.append(f"job: debit journal binding mismatch {assignment_id}")
    return failures


def validate_campaign_gate(root: Path, gate: dict[str, Any]) -> list[str]:
    """Parse and semantically validate one exact final campaign gate artifact."""
    failures: list[str] = []
    gate_id = gate.get("gate_id", "unknown")
    expected = CAMPAIGN_GATE_RULES.get(gate_id)
    if expected is None:
        return [f"campaign: unknown gate {gate_id}"]
    if (gate.get("validation_rule"), gate.get("result_required")) != expected:
        failures.append(f"campaign: rule or result mismatch {gate_id}")
    ref = gate.get("evidence")
    path = root / ref if isinstance(ref, str) else root / "__missing__"
    if not path.is_file():
        failures.append(f"campaign: missing gate evidence {ref}")
        return failures
    try:
        evidence = load_data(path)
    except Exception as exc:  # noqa: BLE001 - gate evidence must parse
        failures.append(f"campaign: unreadable gate evidence {gate_id}: {exc}")
        return failures

    rule = gate.get("validation_rule")
    if rule == "source_lock_valid":
        if evidence.get("schema_version") != "logos_doctrine_mesh_source_lock.v2":
            failures.append(f"campaign: source-lock type mismatch {gate_id}")
    elif rule == "schema_valid":
        failures.extend(check_schema(evidence, f"campaign gate {gate_id}"))
    elif rule == "manual_audit_receipt_pass":
        schema = load_data(root / "mesh/audit-receipt.schema.json")
        failures.extend(schema_errors(schema, evidence, f"campaign gate {gate_id}"))
        expected_phase = {"DMG-003": "preflight", "DMG-007": "midflight", "DMG-008": "postflight"}[gate_id]
        if evidence.get("status") != "pass" or evidence.get("phase") != expected_phase or evidence.get("execution_class") != "manual_specification_coverage_review":
            failures.append(f"campaign: audit receipt result mismatch {gate_id}")
    elif rule == "dormant_factory_contract_valid":
        if evidence.get("current_activation") is not False or evidence.get("factory_may_dispatch_or_own_lease") is not False:
            failures.append(f"campaign: role factory is not dormant {gate_id}")
    elif rule == "specification_contract_valid":
        metadata = evidence.get("metadata", {})
        if metadata.get("lifecycle_status") != "specification_only" or evidence.get("authority_boundary") is None:
            failures.append(f"campaign: expert-pack contract is not specification-only {gate_id}")
    elif rule == "all_human_gates_blocked":
        gates = evidence.get("gates", [])
        if not gates or evidence.get("default_status") != "blocked_human" or any(row.get("status") != "blocked_human" for row in gates):
            failures.append(f"campaign: human gates are not all blocked {gate_id}")
    elif rule == "independent_specification_review_pass":
        schema = load_data(root / "governance/independent-specification-review.schema.json")
        failures.extend(schema_errors(schema, evidence, f"campaign gate {gate_id}"))
        if evidence.get("status") != "pass_specification_only" or evidence.get("runtime_activation_authorized") is not False or evidence.get("research_authorized") is not False:
            failures.append(f"campaign: independent review result mismatch {gate_id}")
        revision_manifest = load_data(root / "revision-manifest.yaml")
        if evidence.get("revision_manifest_digest") != revision_manifest.get("manifest_digest") or evidence.get("payload_digest") != revision_manifest.get("payload_digest"):
            failures.append(f"campaign: independent review manifest binding mismatch {gate_id}")
        lineage_path = root / evidence.get("review_lineage_ref", "__missing__")
        if not lineage_path.is_file() or evidence.get("review_lineage_digest") != file_digest(lineage_path):
            failures.append(f"campaign: independent review lineage binding mismatch {gate_id}")
        if evidence.get("review_digest") != object_digest(evidence, ("review_digest",)):
            failures.append(f"campaign: independent review digest mismatch {gate_id}")
    elif rule == "dormant_manual_review_packet_valid":
        schema = load_data(root / "governance/fable-review-manifest.schema.json")
        failures.extend(schema_errors(schema, evidence, f"campaign gate {gate_id}"))
        if evidence.get("packet_integrity_status") != "pass" or evidence.get("external_review_status") != "not_sent":
            failures.append(f"campaign: Fable packet state mismatch {gate_id}")
        reference_fields = (
            ("brief_ref", "brief_digest", True),
            ("validation_receipt_ref", "validation_receipt_digest", True),
            ("independent_review_ref", "independent_review_digest", True),
        )
        for ref_field, digest_field, raw_file_digest in reference_fields:
            target = root / evidence.get(ref_field, "__missing__")
            if not target.is_file() or (raw_file_digest and evidence.get(digest_field) != file_digest(target)):
                failures.append(f"campaign: Fable packet binding mismatch {gate_id} {ref_field}")
        revision_manifest = load_data(root / "revision-manifest.yaml")
        if evidence.get("revision_manifest_digest") != revision_manifest.get("manifest_digest"):
            failures.append(f"campaign: Fable revision binding mismatch {gate_id}")
        if evidence.get("manifest_digest") != object_digest(evidence, ("manifest_digest",)):
            failures.append(f"campaign: Fable manifest digest mismatch {gate_id}")
        validation_path = root / evidence.get("validation_receipt_ref", "__missing__")
        if validation_path.is_file():
            validation_receipt = load_data(validation_path)
            validation_schema = load_data(root / "governance/specification-validation-receipt.schema.json")
            failures.extend(schema_errors(validation_schema, validation_receipt, f"campaign gate {gate_id} validation receipt"))
            if (
                validation_receipt.get("status") != "pass_artifact_specification_only"
                or validation_receipt.get("revision_manifest_digest") != revision_manifest.get("manifest_digest")
                or validation_receipt.get("payload_digest") != revision_manifest.get("payload_digest")
                or validation_receipt.get("receipt_digest") != object_digest(validation_receipt, ("receipt_digest",))
            ):
                failures.append(f"campaign: Fable validation receipt semantic mismatch {gate_id}")
    else:
        failures.append(f"campaign: unsupported validation rule {gate_id} {rule}")
    return failures


def validate_internal_markdown_links(root: Path) -> list[str]:
    failures: list[str] = []
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            raw_target = match.group(1).strip().strip("<>")
            if not raw_target or raw_target.startswith(("#", "http://", "https://", "mailto:", "{")):
                continue
            target_text = raw_target.split("#", 1)[0]
            target = (path.parent / target_text).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                failures.append(f"links: target escapes revision root in {path.relative_to(root).as_posix()}: {raw_target}")
                continue
            if not target.exists():
                failures.append(f"links: missing target in {path.relative_to(root).as_posix()}: {raw_target}")
    return failures


def validate_audit_bundle(
    root: Path,
    events_override: list[dict[str, Any]] | None = None,
    receipts_override: list[dict[str, Any]] | None = None,
    attempts_override: list[dict[str, Any]] | None = None,
    timeline_override: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []
    event_schema = load_data(root / "mesh/audit-event.schema.json")
    receipt_schema = load_data(root / "mesh/audit-receipt.schema.json")
    gap_schema = load_data(root / "mesh/role-gap.schema.json")
    coverage_schema = load_data(root / "mesh/coverage-plan.schema.json")
    lineage_schema = load_data(root / "mesh/attempt-lineage.schema.json")
    ledger = load_data(root / "evidence/event-ledger.json")
    events = copy.deepcopy(events_override if events_override is not None else ledger["events"])
    receipt_paths = sorted((root / "evidence/receipts").glob("*.json"))
    receipts = copy.deepcopy(receipts_override if receipts_override is not None else [load_data(path) for path in receipt_paths])
    attempt_registry = load_data(root / "evidence/execution-attempts.json")
    attempts = copy.deepcopy(attempts_override if attempts_override is not None else attempt_registry["attempts"])
    timeline = copy.deepcopy(timeline_override if timeline_override is not None else load_data(root / "evidence/timeline.json"))

    if not events:
        return ["audit: event ledger is empty"]
    if [event.get("sequence") for event in events] != list(range(1, len(events) + 1)):
        failures.append("audit: event sequences are not contiguous and ordered")
    phases = [event.get("phase") for event in events]
    if phases[0] != "preflight" or phases[-1] != "postflight" or "midflight" not in phases:
        failures.append("audit: required preflight, midflight, and postflight phase order is absent")

    event_by_id: dict[str, dict[str, Any]] = {}
    prior_event_id: str | None = None
    prior_emitted_at: datetime | None = None
    for event in events:
        failures.extend(schema_errors(event_schema, event, f"event {event.get('event_id')}"))
        event_id = event.get("event_id")
        if event_id in event_by_id:
            failures.append(f"audit: duplicate event ID {event_id}")
        event_by_id[event_id] = event
        if event.get("event_digest") != object_digest(event, ("event_digest",)):
            failures.append(f"audit: event digest mismatch {event_id}")
        if event.get("required_before_event_id") != prior_event_id:
            failures.append(f"audit: event predecessor mismatch {event_id}")
        try:
            emitted_at = parse_time(event["emitted_at"])
            if prior_emitted_at is not None and emitted_at < prior_emitted_at:
                failures.append(f"audit: event timestamp order mismatch {event_id}")
            prior_emitted_at = emitted_at
        except (KeyError, TypeError, ValueError):
            failures.append(f"audit: invalid event timestamp {event_id}")
        prior_event_id = event_id
        input_ref = event.get("input_manifest_ref", "")
        input_path = root / input_ref
        if not input_path.is_file():
            failures.append(f"audit: missing input manifest {input_ref}")
        else:
            manifest = load_data(input_path)
            digest = object_digest(manifest, ("manifest_digest",))
            if manifest.get("manifest_digest") != digest:
                failures.append(f"audit: input manifest self-digest mismatch {input_ref}")
            if event.get("input_manifest_digest") != digest:
                failures.append(f"audit: stale input manifest digest for {event_id}")

    receipts_by_event: dict[str, list[dict[str, Any]]] = {event_id: [] for event_id in event_by_id}
    receipt_ids: set[str] = set()
    attempt_ids_seen: set[str] = set()
    sorted_receipts = sorted(receipts, key=lambda item: item.get("sequence", 0))
    prior_digest: str | None = None
    for receipt in sorted_receipts:
        receipt_id = receipt.get("receipt_id")
        failures.extend(schema_errors(receipt_schema, receipt, f"receipt {receipt_id}"))
        if receipt_id in receipt_ids:
            failures.append(f"audit: duplicate receipt ID {receipt_id}")
        receipt_ids.add(receipt_id)
        event_id = receipt.get("event_id")
        if event_id not in event_by_id:
            failures.append(f"audit: orphan receipt {receipt_id} for {event_id}")
            continue
        receipts_by_event[event_id].append(receipt)
        event = event_by_id[event_id]
        for field in ("event_digest", "sequence", "phase", "execution_class", "work_unit_id", "work_unit_revision", "input_manifest_ref", "input_manifest_digest"):
            if receipt.get(field) != event.get(field):
                failures.append(f"audit: receipt/event {field} mismatch for {receipt_id}")
        if receipt.get("receipt_digest") != object_digest(receipt, ("receipt_digest",)):
            failures.append(f"audit: receipt digest mismatch {receipt_id}")
        if receipt.get("previous_receipt_digest") != prior_digest:
            failures.append(f"audit: receipt hash-chain mismatch {receipt_id}")
        prior_digest = receipt.get("receipt_digest")
        try:
            started_at = parse_time(receipt["started_at"])
            auditor_completed_at = parse_time(receipt["auditor_completed_at"])
            checker_started_at = parse_time(receipt["checker_started_at"])
            checker_completed_at = parse_time(receipt["checker_completed_at"])
            completed_at = parse_time(receipt["completed_at"])
            emitted_at = parse_time(event["emitted_at"])
            if not (emitted_at <= started_at <= auditor_completed_at <= checker_started_at <= checker_completed_at <= completed_at):
                failures.append(f"audit: invalid receipt time window {receipt_id}")
        except (KeyError, TypeError, ValueError):
            failures.append(f"audit: invalid receipt timestamp {receipt_id}")
        attempt_id = receipt.get("auditor_attempt_id")
        if attempt_id in attempt_ids_seen:
            failures.append(f"audit: reused auditor attempt ID {attempt_id}")
        attempt_ids_seen.add(attempt_id)
        expected_adapter_ref = f"evidence/execution-attempts.json#{attempt_id}"
        if receipt.get("execution_attempt_ref") != expected_adapter_ref:
            failures.append(f"audit: execution attempt ref mismatch {receipt_id}")
        if receipt.get("auditor_role_id") == receipt.get("checker_role_id"):
            failures.append(f"audit: auditor/checker collision {receipt_id}")
        for ref_field, digest_field in (("coverage_plan_ref", "coverage_plan_digest"), ("role_gap_registry_ref", "role_gap_registry_digest")):
            ref = receipt.get(ref_field, "")
            path = root / ref
            if not path.is_file():
                failures.append(f"audit: missing output {ref} for {receipt_id}")
                continue
            if receipt.get(digest_field) != file_digest(path):
                failures.append(f"audit: output digest mismatch {ref} for {receipt_id}")
        gap_ref = receipt.get("role_gap_registry_ref", "")
        gap_path = root / gap_ref
        if gap_path.is_file():
            gap_registry = load_data(gap_path)
            if gap_registry.get("audit_event_id") != event_id:
                failures.append(f"audit: gap registry event mismatch {gap_ref}")
            gap_ids = [gap.get("gap_id") for gap in gap_registry.get("gaps", [])]
            if len(gap_ids) != len(set(gap_ids)):
                failures.append(f"audit: duplicate gap ID in {gap_ref}")
            for gap in gap_registry.get("gaps", []):
                failures.extend(schema_errors(gap_schema, gap, f"gap {gap.get('gap_id')}"))
                if gap.get("audit_event_id") != event_id:
                    failures.append(f"audit: gap event mismatch {gap.get('gap_id')}")
        coverage_ref = receipt.get("coverage_plan_ref", "")
        coverage_path = root / coverage_ref
        if coverage_path.is_file():
            coverage = load_data(coverage_path)
            failures.extend(schema_errors(coverage_schema, coverage, f"coverage {coverage_ref}"))
            for field in ("audit_event_id", "phase", "input_manifest_ref", "input_manifest_digest"):
                expected = event_id if field == "audit_event_id" else event.get(field)
                if coverage.get(field) != expected:
                    failures.append(f"audit: coverage {field} mismatch {coverage_ref}")

    for event_id, matching in receipts_by_event.items():
        if len(matching) != 1:
            failures.append(f"audit: event {event_id} has {len(matching)} receipts; expected exactly 1")

    attempt_by_id: dict[str, dict[str, Any]] = {}
    for attempt in attempts:
        attempt_id = attempt.get("attempt_id")
        failures.extend(schema_errors(lineage_schema, attempt, f"attempt {attempt_id}"))
        if attempt_id in attempt_by_id:
            failures.append(f"audit: duplicate execution attempt {attempt_id}")
        attempt_by_id[attempt_id] = attempt
        if attempt.get("actor_role_id") == attempt.get("checker_role_id"):
            failures.append(f"audit: execution attempt self-check collision {attempt_id}")
        if attempt.get("actor_instance_id") == attempt.get("checker_instance_id"):
            failures.append(f"audit: execution attempt actor collision {attempt_id}")
    for receipt in receipts:
        attempt_id = receipt.get("auditor_attempt_id")
        attempt = attempt_by_id.get(attempt_id)
        if attempt is None:
            failures.append(f"audit: receipt references missing attempt {attempt_id}")
        elif attempt.get("event_id") != receipt.get("event_id"):
            failures.append(f"audit: attempt event mismatch {attempt_id}")
        else:
            if attempt.get("actor_role_id") != receipt.get("auditor_role_id"):
                failures.append(f"audit: attempt actor mismatch {attempt_id}")
            if attempt.get("checker_role_id") != receipt.get("checker_role_id"):
                failures.append(f"audit: attempt checker mismatch {attempt_id}")
            if attempt.get("execution_class") != receipt.get("execution_class"):
                failures.append(f"audit: attempt execution class mismatch {attempt_id}")
            try:
                if parse_time(attempt["started_at"]) != parse_time(receipt["started_at"]) or parse_time(attempt["completed_at"]) != parse_time(receipt["completed_at"]):
                    failures.append(f"audit: attempt time mismatch {attempt_id}")
                for time_field in ("auditor_completed_at", "checker_started_at", "checker_completed_at"):
                    if parse_time(attempt[time_field]) != parse_time(receipt[time_field]):
                        failures.append(f"audit: attempt {time_field} mismatch {attempt_id}")
            except (KeyError, TypeError, ValueError):
                failures.append(f"audit: invalid attempt timestamp {attempt_id}")

    if sorted_receipts:
        pre = next((item for item in sorted_receipts if item.get("phase") == "preflight"), None)
        post = next((item for item in sorted_receipts if item.get("phase") == "postflight"), None)
        mids = [item for item in sorted_receipts if item.get("phase") == "midflight"]
        try:
            first_lease = parse_time(timeline["first_writer_lease_at"])
            last_worker = parse_time(timeline["last_worker_or_checker_receipt_at"])
            completion_gate = parse_time(timeline["completion_gate_evaluated_at"])
        except (KeyError, TypeError, ValueError):
            return failures + ["audit: invalid lifecycle timeline"]
        if pre is None or parse_time(pre["auditor_completed_at"]) > first_lease:
            failures.append("audit: preflight auditor did not complete before first writer lease")
        if pre is not None and pre.get("execution_class") == "controller_execution_audit" and parse_time(pre["checker_completed_at"]) > first_lease:
            failures.append("audit: controller preflight checker did not complete before first writer lease")
        for mid in mids:
            event = event_by_id.get(mid.get("event_id"))
            if event and parse_time(mid["completed_at"]) < parse_time(event["emitted_at"]):
                failures.append(f"audit: midflight receipt predates trigger {mid.get('receipt_id')}")
        if post is None or parse_time(post["completed_at"]) < last_worker:
            failures.append("audit: postflight did not complete after worker/checker receipts")
        if post is None or parse_time(post["completed_at"]) > completion_gate:
            failures.append("audit: postflight did not complete before completion gate")

    return failures


def validate_revision(root: Path, mode: str) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    checks: dict[str, Any] = {}
    campaign = load_data(root / "campaign.yaml")
    try:
        qualification_evaluation_at = parse_time(campaign["artifact_qualification_evaluation_at"])
    except (KeyError, TypeError, ValueError):
        failures.append("qualification: campaign evaluation snapshot is missing or invalid")
        qualification_evaluation_at = datetime.min.replace(tzinfo=timezone.utc)
    checks["qualification_evaluation_at"] = qualification_evaluation_at.isoformat()

    parseable_files = sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".json", ".yaml", ".yml"})
    parsed: dict[Path, Any] = {}
    for path in parseable_files:
        try:
            parsed[path] = load_data(path)
        except Exception as exc:  # noqa: BLE001 - validator must report malformed evidence
            failures.append(f"parse: {path.relative_to(root).as_posix()}: {exc}")
    checks["parsed_structured_files"] = len(parsed)

    for path, data in parsed.items():
        rel = path.relative_to(root).as_posix()
        if rel.endswith(".schema.json"):
            metadata = data.get("x-logos-metadata") if isinstance(data, dict) else None
        else:
            metadata = data.get("metadata") if isinstance(data, dict) else None
        if rel == "mesh/agent-mesh.v2.json" or rel.startswith("evidence/receipts/"):
            continue
        if not isinstance(metadata, dict):
            failures.append(f"metadata: missing metadata for {rel}")
            continue
        for field in ("object_type", "trust_zone", "lifecycle_status", "provenance_note", "reason_for_inclusion"):
            if not metadata.get(field):
                failures.append(f"metadata: {rel} missing {field}")

    for path, data in parsed.items():
        rel = path.relative_to(root).as_posix()
        if rel.endswith(".schema.json") and isinstance(data, dict):
            failures.extend(check_schema(data, rel))

    mesh = load_data(root / "mesh/agent-mesh.v2.json")
    roles = mesh.get("roles", [])
    role_ids = [role.get("role_id") for role in roles]
    if len(role_ids) != len(set(role_ids)):
        failures.append("mesh: duplicate role IDs")
    if not REQUIRED_ROLES <= set(role_ids):
        failures.append(f"mesh: required roles missing {sorted(REQUIRED_ROLES - set(role_ids))}")
    if mesh.get("writer_role_id") == mesh.get("checker_role_id"):
        failures.append("mesh: writer/checker collision")
    if mesh.get("max_delegation_depth") != 1:
        failures.append("mesh: delegation depth must equal 1")
    if not acyclic(set(role_ids), roles):
        failures.append("mesh: dependency graph is cyclic or has missing endpoints")
    if mesh.get("factory_dispatch_authority") is not False or mesh.get("sole_future_dispatcher") != "qualified_controller_runtime_adapter":
        failures.append("mesh: factory/controller dispatch boundary invalid")
    for ref_field in ("job_binding_schema_ref", "job_binding_contract_ref", "controller_runtime_receipt_schema_ref", "attempt_lineage_schema_ref"):
        ref = mesh.get(ref_field, "")
        if not ref or not (root / ref).is_file():
            failures.append(f"mesh: missing referenced contract {ref_field}")
    if mode == "final" and mesh.get("manifest_digest") != object_digest(mesh, ("manifest_digest",)):
        failures.append("mesh: manifest digest mismatch")
    if mode == "final" and mesh.get("source_snapshot_digest") != file_digest(root / "source-lock.yaml"):
        failures.append("mesh: source snapshot digest mismatch")
    for role in roles:
        stable = role.get("role_id", "").lower()
        if any(name in stable for name in ("opus", "fable", "openai", "anthropic", "gpt", "claude", "sol", "terra", "luna")):
            failures.append(f"mesh: provider/model name in stable role ID {stable}")
    checks["mesh_roles"] = len(roles)

    taxonomy = load_data(root / "mesh/expertise-taxonomy.yaml")
    discovered_ids: set[str] = set()
    for family in taxonomy.get("domain_profiles", {}).values():
        for item in family:
            discovered_ids.add(item["profile_id"])
    missing_taxonomy = REQUIRED_TAXONOMY_IDS - discovered_ids
    if missing_taxonomy:
        failures.append(f"taxonomy: required profiles missing {sorted(missing_taxonomy)}")
    checks["domain_profiles"] = len(discovered_ids)

    graph = load_data(root / "graph/doctrine-mesh-graph.yaml")
    graph_nodes = graph.get("nodes", [])
    graph_edges = graph.get("edges", [])
    node_ids = [node.get("node_id") for node in graph_nodes]
    edge_ids = [edge.get("edge_id") for edge in graph_edges]
    allowed_node_types = set(graph.get("node_types", []))
    allowed_edge_types = {
        edge_type
        for plane in ("vertical", "horizontal", "depth", "temporal")
        for edge_type in graph.get("edge_types", {}).get(plane, [])
    }
    forbidden_edges = set(graph.get("edge_types", {}).get("forbidden_load_bearing", []))
    if len(node_ids) != len(set(node_ids)):
        failures.append("graph: duplicate node IDs")
    if len(edge_ids) != len(set(edge_ids)):
        failures.append("graph: duplicate edge IDs")
    for node in graph_nodes:
        if node.get("type") not in allowed_node_types:
            failures.append(f"graph: unknown node type {node.get('type')} on {node.get('node_id')}")
    for edge in graph_edges:
        edge_type = edge.get("type")
        if edge.get("from") not in set(node_ids) or edge.get("to") not in set(node_ids):
            failures.append(f"graph: missing endpoint on {edge.get('edge_id')}")
        if edge_type not in allowed_edge_types or edge_type in forbidden_edges:
            failures.append(f"graph: forbidden or unknown edge type {edge_type} on {edge.get('edge_id')}")
        if edge_type in {"contextualizes", "documents_reception"} and edge.get("authority") != "no_normative_force":
            failures.append(f"graph: context edge has normative force on {edge.get('edge_id')}")
        if edge_type == "delegates_to" and edge.get("from") != "N-CONTROLLER":
            failures.append(f"graph: non-controller dispatch on {edge.get('edge_id')}")
        if edge.get("from") in {"N-JEWISH-CONTEXT", "N-EXTERNAL-CONTEXT"} and edge.get("to") == "N-DOCTRINE" and edge_type not in {"contextualizes", "documents_reception"}:
            failures.append(f"graph: boundary-to-doctrine authority bypass on {edge.get('edge_id')}")
    delegated_targets = {edge.get("to") for edge in graph_edges if edge.get("type") == "delegates_to"}
    if any(edge.get("from") in delegated_targets for edge in graph_edges if edge.get("type") == "delegates_to"):
        failures.append("graph: recursive or depth-two dispatch path")
    horizontal_cycle_types = set(graph.get("edge_types", {}).get("horizontal", []))
    if not graph_acyclic(set(node_ids), graph_edges, horizontal_cycle_types):
        failures.append("graph: non-horizontal cycle or missing endpoint")
    checks["graph_nodes"] = len(graph_nodes)
    checks["graph_edges"] = len(graph_edges)

    decision_schema = load_data(root / "governance/decision-record.schema.json")
    decision_paths = sorted((root / "evidence/decisions").glob("*.json")) if (root / "evidence/decisions").is_dir() else []
    decision_records: list[dict[str, Any]] = []
    for path in decision_paths:
        record = load_data(path)
        decision_records.append(record)
        failures.extend(schema_errors(decision_schema, record, f"decision {path.name}"))
        failures.extend(validate_decision_semantics(record))
    failures.extend(validate_decision_chain(decision_records))
    checks["decision_records"] = len(decision_paths)

    qualification_schema = load_data(root / "research/qualification-receipt.schema.json")
    qualification_paths = sorted((root / "evidence/qualifications").glob("*.json")) if (root / "evidence/qualifications").is_dir() else []
    for path in qualification_paths:
        receipt = load_data(path)
        failures.extend(schema_errors(qualification_schema, receipt, f"qualification {path.name}"))
        failures.extend(validate_qualification_semantics(receipt, qualification_evaluation_at))
    checks["qualification_receipts"] = len(qualification_paths)

    source_schema = load_data(root / "research/evidence-source-manifest.schema.json")
    source_paths = sorted((root / "evidence/sources").glob("*.json")) if (root / "evidence/sources").is_dir() else []
    for path in source_paths:
        failures.extend(schema_errors(source_schema, load_data(path), f"source manifest {path.name}"))
    checks["evidence_source_manifests"] = len(source_paths)

    budget_schema = load_data(root / "governance/campaign-budget-ledger.schema.json")
    budget_paths = sorted((root / "evidence/budgets").glob("*.json")) if (root / "evidence/budgets").is_dir() else []
    budget_rows = [(path, load_data(path)) for path in budget_paths]
    predecessor_by_ledger: dict[str, dict[str, Any]] = {}
    journal_history_by_ledger: dict[str, list[dict[str, Any]]] = {}
    ledger_snapshot_index: dict[str, dict[str, Any]] = {}
    for path, ledger in sorted(budget_rows, key=lambda item: (item[1].get("ledger_id", ""), item[1].get("sequence", 0))):
        failures.extend(schema_errors(budget_schema, ledger, f"budget ledger {ledger.get('ledger_id')}:{ledger.get('sequence')}"))
        ledger_id = ledger.get("ledger_id", "")
        predecessor = predecessor_by_ledger.get(ledger_id)
        failures.extend(validate_budget_ledger_semantics(ledger, predecessor, journal_history_by_ledger.get(ledger_id, [])))
        predecessor_by_ledger[ledger_id] = ledger
        journal_history_by_ledger.setdefault(ledger_id, []).extend(ledger.get("journal_entries", []))
        ledger_snapshot_index[path.relative_to(root).as_posix()] = ledger
    checks["budget_ledger_snapshots"] = len(budget_paths)

    job_schema = load_data(root / "mesh/job-binding.schema.json")
    job_paths = sorted((root / "evidence/job-bindings").glob("*.json")) if (root / "evidence/job-bindings").is_dir() else []
    for path in job_paths:
        binding = load_data(path)
        failures.extend(schema_errors(job_schema, binding, f"job binding {path.name}"))
        failures.extend(validate_job_binding_semantics(binding, ledger_snapshot_index))
    checks["job_bindings"] = len(job_paths)

    constitution = load_data(root / "constitution.yaml")
    for field in ("execution_authorized", "controller_selected", "unattended_operation_authorized", "research_execution_authorized", "source_ingestion_authorized", "cross_repository_write_authorized", "promotion_or_publication_authorized"):
        if constitution.get(field) is not False:
            failures.append(f"authority: constitution {field} must remain false")
    autonomy = load_data(root / "governance/autonomy-envelope.yaml")
    if autonomy.get("current_activation") is not False:
        failures.append("authority: autonomy envelope is active")
    human_gates = load_data(root / "governance/human-gates.yaml")
    if any(gate.get("status") != "blocked_human" for gate in human_gates.get("gates", [])):
        failures.append("authority: a doctrine-mesh human gate is not blocked")
    boundaries = load_data(root / "governance/authority-and-storage-boundaries.yaml")
    for plane in ("jewish_historical_context", "external_ancient_context", "governance_and_campaign"):
        if boundaries["planes"][plane].get("normative_christian_doctrine_authority") != "none":
            failures.append(f"authority: {plane} acquired normative doctrine authority")
    if boundaries["doctrine_reference_fields"]["normative_support_refs"].get("boundary_ids_allowed") is not False:
        failures.append("authority: boundary IDs allowed in normative support refs")

    if (root / "evidence/event-ledger.json").is_file() and constitution.get("controller_selected") is False:
        ledger = load_data(root / "evidence/event-ledger.json")
        attempts = load_data(root / "evidence/execution-attempts.json").get("attempts", [])
        if any(event.get("execution_class") != "manual_specification_coverage_review" for event in ledger.get("events", [])):
            failures.append("authority: dormant controller has controller-execution audit event")
        if any(attempt.get("execution_class") != "manual_specification_coverage_review" for attempt in attempts):
            failures.append("authority: dormant controller has controller-execution attempt")

    source_lock = load_data(root / "source-lock.yaml")
    parent = source_lock["parent_checkpoint"]["commit"]
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        parent_tree = subprocess.check_output(["git", "rev-parse", f"{parent}^{{tree}}"], cwd=root, text=True).strip()
        subprocess.run(["git", "cat-file", "-e", f"{parent}^{{commit}}"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", parent, head], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if mode == "final" and ancestry.returncode != 0:
            failures.append(f"source-lock: parent {parent} is not an ancestor of revision HEAD {head}")
        tree_declaration = source_lock["parent_checkpoint"].get("parent_tree_digest")
        if mode == "final" and tree_declaration != f"git-tree-sha1:{parent_tree}":
            failures.append("source-lock: parent tree digest mismatch")
    except (OSError, subprocess.CalledProcessError) as exc:
        failures.append(f"source-lock: Git parent verification failed: {exc}")
    for row in source_lock.get("inputs", []):
        try:
            blob = subprocess.check_output(["git", "show", f"{parent}:{row['path']}"], cwd=root)
        except (OSError, subprocess.CalledProcessError):
            failures.append(f"source-lock: missing parent blob {row['path']}")
            continue
        blob_digest = hashlib.sha256(blob).hexdigest()
        if mode == "final" and row.get("sha256") != blob_digest:
            failures.append(f"source-lock: parent blob digest mismatch {row['path']}")

    ledger_path = root / "evidence/event-ledger.json"
    if ledger_path.is_file():
        audit_failures = validate_audit_bundle(root)
        failures.extend(audit_failures)
        checks["audit_failures"] = len(audit_failures)
    elif mode == "final":
        failures.append("audit: evidence/event-ledger.json is missing")
        checks["audit_failures"] = 1
    else:
        checks["audit_status"] = "pending_final_evidence"

    all_text_files = sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".json", ".py"})
    deprecated_label = "habi" + "tat"
    pending_token = "pending_" + "freeze"
    zero_digest = "sha256:" + ("0" * 64)
    for path in all_text_files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        if deprecated_label in text.lower():
            failures.append(f"hygiene: deprecated project label in {rel}")
        if re.search(r"(?i)[A-Z]:[\\/]Users[\\/]", text):
            failures.append(f"hygiene: absolute workstation path in {rel}")
        if re.search(r"(?im)^\s*(question|objective|mission)\s*:\s*[^\n]*(prove|show that|establish that|demonstrate that|confirm that|validate that|substantiate that|defend that|refute that|expose that)\b", text):
            failures.append(f"alignment: leading desired-conclusion assignment in {rel}")
        if mode == "final" and (pending_token in text or zero_digest in text):
            failures.append(f"freeze: pending or zero digest in {rel}")

    link_failures = validate_internal_markdown_links(root)
    failures.extend(link_failures)
    checks["internal_markdown_link_failures"] = len(link_failures)

    gate_evidence = [gate.get("evidence") for gate in campaign.get("gates", [])]
    if mode == "final":
        gate_ids = [gate.get("gate_id") for gate in campaign.get("gates", [])]
        if set(gate_ids) != set(CAMPAIGN_GATE_RULES) or len(gate_ids) != len(set(gate_ids)):
            failures.append("campaign: final gate set is incomplete or duplicated")
        for gate in campaign.get("gates", []):
            failures.extend(validate_campaign_gate(root, gate))
    checks["campaign_gate_evidence_refs"] = len(gate_evidence)

    manifest_path = root / "revision-manifest.yaml"
    if mode == "final":
        if not manifest_path.is_file():
            failures.append("freeze: revision-manifest.yaml missing")
        else:
            manifest = load_data(manifest_path)
            declared = manifest.get("payload_files", [])
            declared_map = {row["path"]: row["sha256"] for row in declared}
            if len(declared_map) != len(declared):
                failures.append("freeze: duplicate payload file declaration")
            if any(row.get("capability_class") not in CAPABILITY_CLASSES for row in declared):
                failures.append("freeze: missing or invalid payload capability class")
            actual_payload = sorted(
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
                if path.is_file()
                and path.relative_to(root).as_posix() not in ADMIN_FILES
                and not is_volatile_runtime_file(path.relative_to(root))
            )
            if sorted(declared_map) != actual_payload:
                failures.append("freeze: payload file list does not match filesystem")
            for rel, digest in declared_map.items():
                if digest != file_digest(root / rel):
                    failures.append(f"freeze: payload digest mismatch {rel}")
            expected_payload_digest = object_digest(declared)
            if manifest.get("payload_digest") != expected_payload_digest:
                failures.append("freeze: aggregate payload digest mismatch")
            if manifest.get("manifest_digest") != object_digest(manifest, ("manifest_digest",)):
                failures.append("freeze: revision manifest digest mismatch")

    final_saved_path = root / "FINAL-SAVED-VERSION.yaml"
    if mode == "final":
        if not final_saved_path.is_file():
            failures.append("freeze: FINAL-SAVED-VERSION.yaml missing")
        else:
            final_saved = load_data(final_saved_path)
            final_schema = load_data(root / "governance/final-saved-version.schema.json")
            failures.extend(schema_errors(final_schema, final_saved, "final saved version"))
            manifest = load_data(manifest_path)
            if (
                final_saved.get("revision_manifest_digest") != manifest.get("manifest_digest")
                or final_saved.get("payload_digest") != manifest.get("payload_digest")
                or final_saved.get("payload_file_count") != manifest.get("payload_file_count")
            ):
                failures.append("freeze: final saved revision binding mismatch")
            final_refs = (
                ("validation_receipt_ref", "validation_receipt_file_digest", "validation_receipt_object_digest", "receipt_digest"),
                ("independent_review_ref", "independent_review_file_digest", "independent_review_object_digest", "review_digest"),
                ("fable_manifest_ref", "fable_manifest_file_digest", "fable_manifest_object_digest", "manifest_digest"),
                ("postflight_receipt_ref", "postflight_receipt_file_digest", "postflight_receipt_object_digest", "receipt_digest"),
            )
            for ref_field, file_field, object_field, object_key in final_refs:
                target = root / final_saved.get(ref_field, "__missing__")
                if not target.is_file():
                    failures.append(f"freeze: final saved reference missing {ref_field}")
                    continue
                target_data = load_data(target)
                if final_saved.get(file_field) != file_digest(target) or final_saved.get(object_field) != target_data.get(object_key):
                    failures.append(f"freeze: final saved reference binding mismatch {ref_field}")
            if final_saved.get("final_digest") != object_digest(final_saved, ("final_digest",)):
                failures.append("freeze: final saved digest mismatch")

    return failures, checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the saved doctrine mesh v2 revision.")
    parser.add_argument("--mode", choices=("draft", "final"), default="final")
    args = parser.parse_args()
    failures, checks = validate_revision(ROOT, args.mode)
    result = {
        "schema_version": "logos.doctrine_mesh_validation_result.v2",
        "status": ("pass_artifact_specification_only" if args.mode == "final" and not failures else "pass_draft_non_authorizing" if args.mode == "draft" and not failures else "fail"),
        "mode": args.mode,
        "artifact_freeze_readiness": ("ready_specification_artifact_only" if args.mode == "final" and not failures else "not_ready_draft_only" if args.mode == "draft" else "not_ready"),
        "runtime_activation_readiness": "blocked_specification_only_requires_separate_semantic_fixtures_qualification_and_human_authority",
        "root": "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2",
        "checks": checks,
        "failure_count": len(failures),
        "failures": failures,
        "determinism_claim": "audit execution presence and exact contract replay only",
        "epistemic_completeness_claim": "not_proven_requires_independent_review",
        "mutation_performed": False,
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
