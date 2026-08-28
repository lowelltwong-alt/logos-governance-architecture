#!/usr/bin/env python3
"""
object_type: doctrine_marathon_validator
trust_zone: proposed
lifecycle_status: active
provenance_note: Created on 2026-08-27 by Codex root.
reason_for_inclusion: Deterministically validate the V3 specification, authority
ceiling, role-completeness harness, instance dependencies, review debt, public
nonclaims, negative boundaries, and frozen manifest without launching research.

Passing proves artifact consistency. It does not prove source truth, scholarly
completeness, runtime enforcement, expert competence, or theological correctness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ZERO_DIGEST = "sha256:" + "0" * 64
LOCAL_PATH_RE = re.compile(
    r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]" + r"|/" + r"Users/" + r"|\.codex(?:[/\\]|$))"
)
ADMIN_FILES = {
    "revision-manifest.yaml",
    "FINAL-SAVED-VERSION.yaml",
    "checks/validation-receipt.json",
    "checks/independent-review.json",
    "checks/public-release-authorization.json",
}
FORBIDDEN_GENERATED_PARTS = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache"
}
FORBIDDEN_GENERATED_NAMES = {".coverage", "Thumbs.db", ".DS_Store"}
AUTHORITY_FALSE_FIELDS = {
    "runtime_activation_authorized",
    "research_execution_authorized",
    "source_ingestion_authorized",
    "substantive_doctrine_implementation_authorized",
    "witness_translation_authorized",
    "cross_repository_write_authorized",
    "persistent_agent_activation_authorized",
    "publication_authorized_by_artifact",
    "normative_frame_creation_by_ai",
}
REQUIRED_ROLES = {
    "marathon-controller",
    "doctrine-mesh-completeness-auditor",
    "role-qualification-and-independence-auditor",
    "task-local-role-factory",
    "primary-source-researcher",
    "father-or-corpus-specialist",
    "environment-specialist",
    "citation-locator-verifier",
    "source-fitness-rights-verifier",
    "claim-entailment-context-verifier",
    "original-language-translation-verifier",
    "counterevidence-challenger",
    "dependency-invalidation-checker",
    "authority-plane-auditor",
    "goal-prompt-alignment-auditor",
    "frontier-compounded-error-sentinel",
    "human-risk-router",
    "independent-whole-work-checker",
}
REQUIRED_ROLE_CAPABILITIES = {
    "marathon-controller": {"prompt_alignment_and_authority"},
    "doctrine-mesh-completeness-auditor": {"doctrine_mesh_completeness_and_gap_detection"},
    "role-qualification-and-independence-auditor": {
        "prompt_alignment_and_authority", "role_qualification_and_independence",
    },
    "task-local-role-factory": {"role_qualification_and_independence"},
    "primary-source-researcher": set(),
    "father-or-corpus-specialist": set(),
    "environment-specialist": set(),
    "citation-locator-verifier": {"source_identity_locator_and_rights"},
    "source-fitness-rights-verifier": {
        "privacy_public_boundary_and_custody", "source_identity_locator_and_rights",
    },
    "claim-entailment-context-verifier": {"quotation_context_and_entailment"},
    "original-language-translation-verifier": {"original_language_and_translation_fidelity"},
    "counterevidence-challenger": {"counterevidence_and_alternative_hypotheses"},
    "dependency-invalidation-checker": {"graph_dependency_and_invalidation"},
    "authority-plane-auditor": {
        "privacy_public_boundary_and_custody", "prompt_alignment_and_authority",
        "quotation_context_and_entailment", "tradition_representation",
    },
    "goal-prompt-alignment-auditor": {"prompt_alignment_and_authority"},
    "frontier-compounded-error-sentinel": {
        "counterevidence_and_alternative_hypotheses", "graph_dependency_and_invalidation",
        "prompt_alignment_and_authority",
    },
    "human-risk-router": {"prompt_alignment_and_authority"},
    "independent-whole-work-checker": {
        "prompt_alignment_and_authority", "role_qualification_and_independence",
    },
}
REQUIRED_TRIGGER_IDS = {
    "TR-SOURCE", "TR-LANGUAGE", "TR-ACTOR", "TR-PERIOD", "TR-JEWISH",
    "TR-ANCIENT-CONTEXT", "TR-HIST-LABEL", "TR-NORMATIVE", "TR-INFLUENCE",
    "TR-GRAPH", "TR-DISAGREE", "TR-PROMPT", "TR-PUBLIC", "TR-POST-GAP",
    "TR-TRADITION", "TR-PROPOSITION", "TR-CONTROVERSY", "TR-RISK",
    "TR-DEPENDENCY",
}
CURRENT_STATES = {"ready", "active", "candidate_complete", "accepted"}
NONCURRENT_PREMISE_STATES = {"disputed", "blocked", "stale", "invalidated"}
CONTEXT_EDGE_TYPES = {"contextualized_by", "disputed_by"}
CONTEXT_BLOCKED_CONSUMER_PLANES = {"scripture", "tradition_view", "normative_assessment", "public_projection"}
INDEPENDENCE_DIMENSIONS = {
    "actor_instance", "attempt_id", "prompt_authorship", "answer_context_exposure",
    "source_order", "KnowledgeGuide_digest", "runtime_adapter",
}
EXPECTED_COMPLETENESS_CONTRACT_OBJECT_DIGEST = (
    "sha256:cbd09f221b2ce674daf7f8671ca152c220f45e05f526243a87be1c730ff7c768"
)
EXPECTED_CONSTITUTION_OBJECT_DIGEST = (
    "sha256:a3cf70bb2706e3f1737e16322d9adcabc9b0daee4cbd203702a0b81395d5d8c6"
)
EXPECTED_CAMPAIGN_OBJECT_DIGEST = (
    "sha256:ed2d3f25ec13362e778ff17ff36474b37c665680e91c7bd27bb68f4c5377e045"
)
EXPECTED_AGENT_MESH_OBJECT_DIGEST = (
    "sha256:acc80a7cbb4998d048b708f25c6b41b6670663c3895ccb57b47155c591e84928"
)
EXPECTED_PROMPT_NEUTRALITY_OBJECT_DIGEST = (
    "sha256:a76692d60f6943f1d69e44c5e922b1f4ff518e4a5d62f161b9a6f4f9231c5de6"
)
DESIRED_CONCLUSION_PATTERNS = (
    r"\b(?:your|the)\s+(?:job|task|mandate|goal)\s+is\s+to\s+(?:prove|establish|demonstrate|confirm|defend)\b.{0,80}\b(?:preferred|correct|true|orthodox)\b",
    r"(?<!do not )\b(?:assume|presuppose)\b.{0,80}\b(?:answer|conclusion|position|view)\b",
    r"\b(?:only|solely)\b.{0,40}\b(?:supporting|favorable|confirming)\b.{0,20}\bevidence\b",
)
TRIGGER_REQUIRED_ACTIONS = {
    "TR-SOURCE": {"midflight_completeness_audit", "source_record_gate", "claim_evidence_lineage_gate", "invalidate_affected_consumers"},
    "TR-LANGUAGE": {"midflight_completeness_audit", "source_record_gate", "translation_lineage_gate", "original_language_review_gate"},
    "TR-ACTOR": {"midflight_completeness_audit", "ExpertPack_gate"},
    "TR-PERIOD": {"midflight_completeness_audit", "environment_pack_gate"},
    "TR-JEWISH": {"midflight_completeness_audit", "jewish_context_pack_gate", "later_source_bridge_check", "tradition_nonflattening_check"},
    "TR-ANCIENT-CONTEXT": {"midflight_completeness_audit", "normative_force_none_check"},
    "TR-HIST-LABEL": {"midflight_completeness_audit", "historical_attribution_schema_check", "qualified_source_gate", "human_gate_if_normative"},
    "TR-NORMATIVE": {"midflight_completeness_audit", "NormativeFrame_gate", "human_decision_receipt_gate", "frontier_sentinel"},
    "TR-INFLUENCE": {"midflight_completeness_audit", "influence_hypothesis_schema_check", "contact_and_reception_evidence_check", "alternative_hypothesis_check"},
    "TR-GRAPH": {"midflight_completeness_audit", "reverse_index_rebuild", "weakest_premise_check", "descendant_invalidation"},
    "TR-DISAGREE": {"midflight_completeness_audit", "preserve_named_graph_disagreement", "rerank_review_debt", "frontier_sentinel"},
    "TR-PROMPT": {"midflight_completeness_audit", "fresh_context_gate", "changed_input_revalidation"},
    "TR-PUBLIC": {"midflight_completeness_audit", "privacy_rights_scrub", "nonclaim_check", "unchanged_head_gate"},
    "TR-POST-GAP": {"midflight_completeness_audit", "quarantine", "reverse_consumer_invalidation", "bounded_replay", "blocking_debt"},
    "TR-TRADITION": {"midflight_completeness_audit", "tradition_pack_gate", "self_description_source_check", "tradition_nonflattening_check"},
    "TR-PROPOSITION": {"midflight_completeness_audit", "typed_claim_gate", "claim_evidence_lineage_gate", "counterevidence_route"},
    "TR-CONTROVERSY": {"midflight_completeness_audit", "historical_attribution_schema_check", "preserve_named_graph_disagreement", "counterposition_route"},
    "TR-RISK": {"midflight_completeness_audit", "risk_recomputation", "rerank_review_debt", "frontier_sentinel"},
    "TR-DEPENDENCY": {"midflight_completeness_audit", "reverse_index_rebuild", "weakest_premise_check", "descendant_invalidation", "quarantine"},
}
TRIGGER_REQUIRED_ROLES = {
    "TR-DISAGREE": {"frontier-compounded-error-sentinel"},
}
FRESH_CONTEXT_REQUIRED_CONTROLS = (
    "DOCTRINE_MARATHON_MASTER_PROMPT.md",
    "campaign.yaml",
    "constitution.yaml",
    "firewall/trigger-matrix.yaml",
    "mesh/agent-mesh.v3.json",
    "mesh/completeness-auditor-v3.yaml",
    "state/goal.yaml",
)

_QUALIFICATION_VALIDATION_CACHE: dict[
    tuple[Any, ...], tuple[list[str], dict[str, dict[str, Any]]]
] = {}
_ROLE_ASSIGNMENT_VALIDATION_CACHE: dict[tuple[Any, ...], list[str]] = {}


def load_data(relative: str) -> Any:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def object_digest(value: Any, omit: Iterable[str] = ()) -> str:
    clone = dict(value) if isinstance(value, dict) else value
    if isinstance(clone, dict):
        clone = {key: item for key, item in clone.items() if key not in set(omit)}
    return "sha256:" + hashlib.sha256(canonical_bytes(clone)).hexdigest()


def canonical_file_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    except UnicodeDecodeError:
        return raw


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(canonical_file_bytes(path)).hexdigest()


def resolve_relative(relative: str) -> Path | None:
    if (
        not isinstance(relative, str)
        or not relative
        or "\\" in relative
        or "//" in relative
        or ":" in relative
        or any(ord(character) < 32 or ord(character) == 127 for character in relative)
    ):
        return None
    portable = PurePosixPath(relative)
    if portable.is_absolute() or any(part in {"", ".", ".."} for part in portable.parts):
        return None
    candidate = ROOT.joinpath(*portable.parts).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return candidate


def parse_time(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed


def exact_dependency_state(refs: Iterable[Any]) -> tuple[tuple[str, str], ...]:
    """Content-key local dependencies so validation reuse fails closed on drift."""
    result: list[tuple[str, str]] = []
    for ref in sorted({str(item) for item in refs if isinstance(item, str)}):
        path = resolve_relative(ref)
        result.append((ref, file_digest(path) if path is not None and path.is_file() else "missing"))
    return tuple(result)


def assignment_bundle_dependency_refs(bundle: dict[str, Any]) -> list[Any]:
    """Return the transitive local control inputs for assignment semantics."""
    refs: list[Any] = [
        bundle.get("qualification_registry_ref"),
        "mesh/role-catalog.yaml",
        "mesh/role-assignment-bundle.schema.json",
        "mesh/role-assignment.schema.json",
        "firewall/prompt-neutrality-contract.yaml",
    ]
    for assignment in bundle.get("assignments", []):
        basis = assignment.get("qualification_basis", {})
        if basis.get("kind") == "control_contract":
            refs.append(basis.get("ref"))
        refs.extend(
            row.get("source_ref")
            for row in assignment.get("source_order", [])
            if row.get("source_class") == "control_contract"
        )
        refs.extend(
            row.get("guide_ref")
            for row in assignment.get("knowledge_guide_lineage", [])
        )
        refs.append(assignment.get("task_prompt_ref"))
    return refs


def add(errors: list[str], rule: str, detail: str) -> None:
    errors.append(f"{rule}: {detail}")


def schema_errors(schema: dict[str, Any], instance: Any, label: str) -> list[str]:
    errors: list[str] = []
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # noqa: BLE001
        return [f"schema_invalid: {label}: {exc}"]
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        add(errors, "schema_instance", f"{label} at {location}: {error.message}")
    return errors


def validate_constitution(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    observed_contract_digest = object_digest(value)
    authority = value.get("authority", {})
    for field in sorted(AUTHORITY_FALSE_FIELDS):
        if authority.get(field) is not False:
            add(errors, f"authority_{field}", "must remain false")
    if value.get("mode") != "specification_only":
        add(errors, "authority_mode", "constitution mode must be specification_only")
    invariants = " ".join(value.get("invariants", []))
    for token in ("never rewritten", "distinct", "quarantine", "exactly one next prompt"):
        if token not in invariants:
            add(errors, "constitution_invariant", f"missing invariant token {token!r}")
    if observed_contract_digest != EXPECTED_CONSTITUTION_OBJECT_DIGEST:
        add(
            errors,
            "constitution_contract_integrity",
            "the complete canonical constitution changed: expected "
            f"{EXPECTED_CONSTITUTION_OBJECT_DIGEST}; observed {observed_contract_digest}",
        )
    return errors


def validate_goal(value: dict[str, Any], final: bool) -> list[str]:
    errors = schema_errors(load_data("state/marathon-goal.schema.json"), value, "state/goal.yaml")
    ceiling = value.get("authority_ceiling", {})
    for field in (
        "research_execution_authorized", "source_ingestion_authorized",
        "substantive_doctrine_implementation_authorized", "runtime_activation_authorized",
    ):
        if ceiling.get(field) is not False:
            add(errors, f"goal_authority_{field}", "must remain false")
    terminal = value.get("terminal_contract", {})
    if terminal.get("allowed_statuses") != ["CONTINUE", "BLOCKED", "CAMPAIGN_COMPLETE"]:
        add(errors, "goal_terminal_statuses", "terminal statuses must be exact and ordered")
    if final:
        expected = file_digest(ROOT / "DOCTRINE_MARATHON_MASTER_PROMPT.md")
        if value.get("canonical_prompt_sha256") != expected:
            add(errors, "goal_prompt_digest", f"expected {expected}")
    return errors


def validate_campaign(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    observed_contract_digest = object_digest(value)
    jobs = value.get("jobs", [])
    ids = [job.get("job_id") for job in jobs]
    if len(ids) != len(set(ids)):
        add(errors, "campaign_job_ids", "job IDs must be unique")
    known = set(ids)
    deps = {job.get("job_id"): set(job.get("depends_on", [])) for job in jobs}
    if any(not required <= known for required in deps.values()):
        add(errors, "campaign_unknown_dependency", "every dependency must resolve")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visited:
            return True
        if node in visiting:
            return False
        visiting.add(node)
        if not all(visit(dep) for dep in deps.get(node, set())):
            return False
        visiting.remove(node)
        visited.add(node)
        return True

    if not all(visit(node) for node in known):
        add(errors, "campaign_cycle", "job dependency graph must be acyclic")
    if value.get("first_future_candidate", {}).get("state") != "blocked_pending_future_research_and_source_ingestion_authority":
        add(errors, "campaign_future_gate", "first research candidate must remain blocked")
    if value.get("terminal_statuses") != ["CONTINUE", "BLOCKED", "CAMPAIGN_COMPLETE"]:
        add(errors, "campaign_terminal_statuses", "terminal statuses changed")
    if observed_contract_digest != EXPECTED_CAMPAIGN_OBJECT_DIGEST:
        add(
            errors,
            "campaign_contract_integrity",
            "the complete canonical campaign changed: expected "
            f"{EXPECTED_CAMPAIGN_OBJECT_DIGEST}; observed {observed_contract_digest}",
        )
    return errors


def catalog_capability_ids(catalog: dict[str, Any]) -> set[str]:
    return {
        str(capability)
        for values in catalog.get("capability_families", {}).values()
        for capability in values
        if isinstance(capability, str)
    }


def catalog_gap_ids(catalog: dict[str, Any]) -> set[str]:
    return {
        str(row.get("gap_id"))
        for row in catalog.get("proposed_role_gaps", [])
        if isinstance(row, dict) and isinstance(row.get("gap_id"), str)
    }


def validate_role_catalog(
    catalog: dict[str, Any], constitution: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    known_capabilities = catalog_capability_ids(catalog)
    known_human_gates = set(constitution.get("human_gates", []))
    expert_pack_required_fields = set(
        load_data("mesh/expert-pack.schema.json").get("required", [])
    )
    gaps = catalog.get("proposed_role_gaps", [])
    if not isinstance(gaps, list):
        return ["role_catalog_gap_registry: proposed_role_gaps must be an array"]
    exact_keys = {
        "gap_id", "proposed_capability_id", "status", "named_error_or_source_route",
        "approved_facets_considered", "non_substitutable_by", "why_insufficient",
        "expected_information_gain", "required_expert_pack_fields",
        "checker_capability_ids", "risk_tier", "human_gate_ids",
    }
    gap_ids: list[Any] = []
    proposed_ids: list[Any] = []
    for row in gaps:
        if not isinstance(row, dict) or set(row) != exact_keys:
            add(errors, "role_catalog_gap_shape", "every proposed gap must use the exact typed key set")
            continue
        gap_id = row.get("gap_id")
        proposed_id = row.get("proposed_capability_id")
        gap_ids.append(gap_id)
        proposed_ids.append(proposed_id)
        if row.get("status") != "proposed_unapproved":
            add(errors, "role_catalog_gap_status", f"{gap_id} must remain proposed_unapproved")
        for field in ("named_error_or_source_route", "why_insufficient", "expected_information_gain"):
            if not isinstance(row.get(field), str) or len(row[field].strip()) < 20:
                add(errors, "role_catalog_gap_rationale", f"{gap_id} has a thin {field}")
        considered = set(row.get("approved_facets_considered", []))
        non_substitutable = set(row.get("non_substitutable_by", []))
        checkers = set(row.get("checker_capability_ids", []))
        gates = set(row.get("human_gate_ids", []))
        if not considered or not considered <= known_capabilities:
            add(errors, "role_catalog_gap_considered", f"{gap_id} must name only approved considered facets")
        if not non_substitutable or not non_substitutable <= known_capabilities:
            add(errors, "role_catalog_gap_non_substitutable", f"{gap_id} must name bounded non-substitutes")
        if not checkers or not checkers <= known_capabilities:
            add(errors, "role_catalog_gap_checkers", f"{gap_id} checker capabilities do not resolve")
        if not gates or not gates <= known_human_gates:
            add(errors, "role_catalog_gap_human_gates", f"{gap_id} human gates do not resolve")
        if proposed_id in known_capabilities:
            add(errors, "role_catalog_gap_approval_leak", f"{gap_id} proposed capability is already approved")
        required_pack_fields = row.get("required_expert_pack_fields")
        if (
            not isinstance(required_pack_fields, list)
            or not required_pack_fields
            or len(required_pack_fields) != len(set(required_pack_fields))
            or not set(required_pack_fields) <= expert_pack_required_fields
        ):
            add(errors, "role_catalog_gap_expert_pack", f"{gap_id} needs ExpertPack requirements")
        if row.get("risk_tier") not in {"high", "frontier"}:
            add(errors, "role_catalog_gap_risk", f"{gap_id} requires high/frontier risk")
    if len(gap_ids) != len(set(gap_ids)) or len(proposed_ids) != len(set(proposed_ids)):
        add(errors, "role_catalog_gap_identity", "gap and proposed capability IDs must be unique")
    patristic = next((row for row in gaps if row.get("gap_id") == "DMV3-GAP-PATRISTIC-GREEK"), None)
    required_non_substitutes = {
        "septuagint_and_koine_greek", "original_language_and_translation_fidelity"
    }
    if (
        not isinstance(patristic, dict)
        or patristic.get("proposed_capability_id") != "patristic_greek"
        or not required_non_substitutes <= set(patristic.get("non_substitutable_by", []))
    ):
        add(errors, "role_catalog_patristic_greek_gap", "patristic Greek must remain an explicit non-substitutable gap")
    return errors


def validate_mesh(
    value: dict[str, Any], catalog: dict[str, Any] | None = None
) -> list[str]:
    errors: list[str] = []
    observed_contract_digest = object_digest(value)
    if catalog is None:
        catalog = load_data("mesh/role-catalog.yaml")
    roles = value.get("roles", [])
    ids = [role.get("role_id") for role in roles]
    if set(ids) != REQUIRED_ROLES or len(ids) != len(set(ids)):
        add(errors, "mesh_required_roles", f"expected exact required role set; got {sorted(set(ids))}")
    if value.get("runtime_activation_authorized") is not False:
        add(errors, "mesh_runtime_authority", "runtime activation must remain false")
    if value.get("max_delegation_depth") != 1:
        add(errors, "mesh_delegation_depth", "delegation depth must be one")
    role_map = {role.get("role_id"): role for role in roles}
    factory = role_map.get("task-local-role-factory", {})
    if factory.get("may_dispatch") is not False or factory.get("may_recurse") is not False:
        add(errors, "mesh_role_factory_authority", "factory may neither dispatch nor recurse")
    whole = role_map.get("independent-whole-work-checker", {})
    if whole.get("may_approve_theology") is not False:
        add(errors, "mesh_theology_authority", "independent checker cannot approve theology")
    for role_id in ids:
        if isinstance(role_id, str) and re.search(r"(?:gpt|claude|opus|sonnet|gemini|sol|terra|luna)", role_id, re.I):
            add(errors, "mesh_provider_identity", f"provider/model token in stable role ID {role_id}")
    for role in roles:
        if role.get("role_id") in role.get("checked_by", []):
            add(errors, "mesh_writer_self_check", f"{role.get('role_id')} checks itself")
    capability_contract = value.get("required_role_capabilities", {})
    known_capabilities = catalog_capability_ids(catalog)
    contract_valid = (
        isinstance(capability_contract, dict)
        and set(capability_contract) == set(REQUIRED_ROLE_CAPABILITIES)
    )
    if contract_valid:
        for role_id, required_capabilities in REQUIRED_ROLE_CAPABILITIES.items():
            observed = capability_contract.get(role_id)
            if (
                not isinstance(observed, list)
                or len(observed) != len(set(observed))
                or set(observed) != required_capabilities
                or not set(observed) <= known_capabilities
            ):
                contract_valid = False
                break
    if not contract_valid:
        add(
            errors,
            "mesh_role_capability_contract",
            "required role capabilities must exactly match the governed provider-neutral contract",
        )
    if set(value.get("independence_dimensions", [])) != INDEPENDENCE_DIMENSIONS:
        add(errors, "mesh_independence_dimensions", "all seven declared independence dimensions are mandatory")
    policy = value.get("pairwise_independence_policy", {})
    for field in (
        "derive_correlations_from_assignments", "undisclosed_correlation_is_hard_failure",
        "same_actor_or_attempt_for_writer_and_checker_is_hard_failure",
        "same_runtime_alone_is_not_cross_model_independence",
        "correlated_disclosed_requires_explicit_acceptance_or_block",
        "KnowledgeGuide_may_route_but_may_not_supply_load_bearing_evidence",
    ):
        if policy.get(field) is not True:
            add(errors, "mesh_pairwise_policy", f"{field} must remain true")
    if observed_contract_digest != EXPECTED_AGENT_MESH_OBJECT_DIGEST:
        add(
            errors,
            "mesh_contract_integrity",
            "the complete canonical agent mesh changed: expected "
            f"{EXPECTED_AGENT_MESH_OBJECT_DIGEST}; observed {observed_contract_digest}",
        )
    return errors


def validate_completeness(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    observed_contract_digest = object_digest(value)
    phases = value.get("audit_phases", {})
    if set(phases) != {"entry", "midflight", "exit"}:
        add(errors, "completeness_phases", "entry, midflight, and exit are all mandatory")
    if "without_rederivation" not in str(phases.get("exit", {}).get("may_not_reuse", "")):
        add(errors, "completeness_postflight_rederive", "exit requirements must be independently rederived")
    required_phase_outputs = {
        "entry": {"coverage_plan", "role_assignments", "role_gaps", "omissions", "receipt"},
        "midflight": {"changed_requirements", "affected_roles", "affected_outputs", "gaps", "receipt"},
        "exit": {"final_coverage", "newly_discovered_roles", "replay_scope", "debt_records", "receipt"},
    }
    for phase, required in required_phase_outputs.items():
        observed = phases.get(phase, {}).get("required_outputs", [])
        if set(observed) != required or len(observed) != len(set(observed)):
            add(errors, "completeness_required_outputs", f"{phase} must declare exact outputs {sorted(required)}")
    recovery = value.get("postflight_recovery", {}).get("material_missing_role", [])
    for required in ("quarantine affected outputs", "traverse and quarantine reverse consumers", "schedule bounded replay with qualified role"):
        if required not in recovery:
            add(errors, "completeness_gap_recovery", f"missing action {required}")
    if value.get("deterministic_receipt_does_not_prove") is None:
        add(errors, "completeness_honesty", "semantic nonclaims are required")
    compare = value.get("independence_rules", {}).get("compare_dimensions", [])
    if set(compare) != INDEPENDENCE_DIMENSIONS:
        add(errors, "completeness_independence_dimensions", "pairwise comparison dimensions are incomplete")
    if observed_contract_digest != EXPECTED_COMPLETENESS_CONTRACT_OBJECT_DIGEST:
        add(
            errors,
            "completeness_contract_integrity",
            "the complete canonical contract changed: expected "
            f"{EXPECTED_COMPLETENESS_CONTRACT_OBJECT_DIGEST}; observed "
            f"{observed_contract_digest}",
        )
    return errors


def validate_triggers(value: dict[str, Any], mesh: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids = [row.get("trigger_id") for row in value.get("triggers", [])]
    if set(ids) != REQUIRED_TRIGGER_IDS or len(ids) != len(set(ids)):
        add(errors, "trigger_coverage", f"required trigger set mismatch: {sorted(set(ids))}")
    if value.get("default_action_for_unknown_material_feature") != "block_and_create_role_gap":
        add(errors, "trigger_unknown_default", "unknown material features must block")
    if value.get("changed_input_requires_new_event") is not True:
        add(errors, "trigger_changed_input", "changed inputs require fresh events")
    known_roles = {row.get("role_id") for row in mesh.get("roles", [])}
    known_capabilities = catalog_capability_ids(catalog)
    action_catalog = load_data("firewall/action-checker-requirements.yaml")
    action_rows = action_catalog.get("requirements", [])
    action_ids = [row.get("action_id") for row in action_rows]
    required_action_ids = {
        action
        for trigger in value.get("triggers", [])
        for action in trigger.get("actions", [])
    }
    if (
        action_catalog.get("unknown_action_policy") != "block"
        or set(action_ids) != required_action_ids
        or len(action_ids) != len(set(action_ids))
    ):
        add(errors, "action_requirement_coverage", "action checker catalog must exactly cover every trigger action")
    for requirement in action_rows:
        unknown_action_roles = set(requirement.get("required_roles", [])) - known_roles
        unknown_action_capabilities = set(requirement.get("required_capabilities", [])) - known_capabilities
        if (
            not requirement.get("required_roles")
            or not requirement.get("required_capabilities")
            or unknown_action_roles
            or unknown_action_capabilities
        ):
            add(
                errors,
                "action_requirement_invalid",
                f"{requirement.get('action_id')}: roles={sorted(unknown_action_roles)} capabilities={sorted(unknown_action_capabilities)}",
            )
    for row in value.get("triggers", []):
        trigger_id = row.get("trigger_id")
        actions = row.get("actions", [])
        if not actions or actions[0] != "midflight_completeness_audit":
            add(errors, "trigger_midflight_barrier", f"{trigger_id} must begin with the midflight completeness barrier")
        if len(actions) != len(set(actions)):
            add(errors, "trigger_duplicate_action", f"{trigger_id} repeats an action")
        required_actions = TRIGGER_REQUIRED_ACTIONS.get(trigger_id, set())
        if not required_actions <= set(actions):
            add(errors, "trigger_required_actions", f"{trigger_id} missing {sorted(required_actions - set(actions))}")
        required_roles = TRIGGER_REQUIRED_ROLES.get(trigger_id, set())
        if not required_roles <= set(row.get("required_roles", [])):
            add(errors, "trigger_required_roles", f"{trigger_id} missing {sorted(required_roles - set(row.get('required_roles', [])))}")
        unknown_roles = set(row.get("required_roles", [])) - known_roles
        if unknown_roles:
            add(errors, "trigger_unknown_role", f"{trigger_id}: {sorted(unknown_roles)}")
        unknown_capabilities = set(row.get("required_capabilities", [])) - known_capabilities
        if unknown_capabilities:
            add(errors, "trigger_unknown_capability", f"{trigger_id}: {sorted(unknown_capabilities)}")
        if not row.get("required_roles") and not row.get("required_capabilities"):
            add(errors, "trigger_unstaffed", f"{trigger_id} has no resolvable role or capability")
    return errors


def validate_qualification_registry(value: dict[str, Any], final: bool) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors = schema_errors(
        load_data("mesh/qualification-registry.schema.json"),
        value,
        "mesh/qualification-registry.json",
    )
    specs = {
        "expert_packs": ("expert_pack_id", "mesh/expert-pack.schema.json", "pack_digest"),
        "qualification_receipts": ("receipt_id", "mesh/qualification-receipt.schema.json", "receipt_digest"),
        "correlation_acceptance_receipts": ("receipt_id", "mesh/correlation-acceptance-receipt.schema.json", "receipt_digest"),
    }
    maps: dict[str, dict[str, Any]] = {}
    for collection, (id_field, schema_ref, digest_field) in specs.items():
        rows = value.get(collection, [])
        row_map = {row.get(id_field): row for row in rows}
        maps[collection] = row_map
        if len(row_map) != len(rows):
            add(errors, "qualification_duplicate_id", collection)
        schema = load_data(schema_ref)
        for row in rows:
            label = str(row.get(id_field))
            errors.extend(schema_errors(schema, row, label))
            expected = object_digest(row, omit=(digest_field,))
            if row.get(digest_field) != expected:
                add(errors, "qualification_object_digest", f"{label}: expected {expected}")
    authority = load_data("graph/authority-registry.yaml")
    mesh = load_data("mesh/agent-mesh.v3.json")
    mesh_role_ids = {row.get("role_id") for row in mesh.get("roles", [])}
    for receipt in value.get("qualification_receipts", []):
        receipt_id = str(receipt.get("receipt_id"))
        expected_qualification_input = object_digest({
            "subject_kind": receipt.get("subject_kind"),
            "subject_ref": receipt.get("subject_ref"),
            "subject_scope_digest": receipt.get("subject_scope_digest"),
            "work_unit_id": receipt.get("work_unit_id"),
            "capability_ids": receipt.get("capability_ids"),
            "expert_pack_ref": receipt.get("expert_pack_ref"),
            "expert_pack_digest": receipt.get("expert_pack_digest"),
            "runtime_adapter_digest": receipt.get("runtime_adapter_digest"),
            "qualification_generation": receipt.get("qualification_generation"),
            "reviewer_evidence_role": receipt.get("reviewer_evidence_role"),
            "bootstrap_authorization_ref": receipt.get("bootstrap_authorization_ref"),
            "bootstrap_authorization_digest": receipt.get("bootstrap_authorization_digest"),
            "reviewer_assignment_bundle_ref": receipt.get("reviewer_assignment_bundle_ref"),
            "reviewer_assignment_bundle_digest": receipt.get("reviewer_assignment_bundle_digest"),
            "reviewer_assignment_refs": receipt.get("reviewer_assignment_refs"),
            "fixture_bindings": receipt.get("fixture_bindings"),
        })
        if receipt.get("qualification_input_digest") != expected_qualification_input:
            add(errors, "qualification_input_digest", f"{receipt_id}: expected {expected_qualification_input}")
        try:
            issued_at = parse_time(receipt.get("issued_at"))
            expires_at = receipt.get("expires_at")
            if expires_at is not None and parse_time(expires_at) <= issued_at:
                add(errors, "qualification_receipt_expiry", receipt_id)
        except (TypeError, ValueError) as exc:
            add(errors, "qualification_receipt_time", f"{receipt_id}: {exc}")
        if receipt.get("decision") != "qualified":
            continue
        for binding in receipt.get("fixture_bindings", []):
            fixture_path = resolve_relative(binding.get("ref"))
            if (
                fixture_path is None
                or not fixture_path.is_file()
                or binding.get("digest") != file_digest(fixture_path)
                or binding.get("result") != "pass"
            ):
                add(errors, "qualification_fixture_binding", f"{receipt_id}: {binding.get('ref')}")
        bundle_path = resolve_relative(receipt.get("reviewer_assignment_bundle_ref"))
        if bundle_path is None or not bundle_path.is_file():
            add(errors, "qualification_reviewer_bundle_ref", receipt_id)
            bundle: dict[str, Any] = {}
        else:
            if receipt.get("reviewer_assignment_bundle_digest") != file_digest(bundle_path):
                add(errors, "qualification_reviewer_bundle_digest", receipt_id)
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            errors.extend(schema_errors(load_data("mesh/role-assignment-bundle.schema.json"), bundle, f"{receipt_id} reviewer bundle"))
            if bundle.get("bundle_digest") != object_digest(bundle, omit=("bundle_digest",)):
                add(errors, "qualification_reviewer_bundle_object_digest", receipt_id)
            if bundle.get("fixture_kind") != "runtime_receipt" or bundle.get("runtime_assignments") is not True:
                add(errors, "qualification_reviewer_bundle_runtime", receipt_id)
            try:
                reviewer_bundle_use_at = parse_time(receipt.get("issued_at"))
            except (TypeError, ValueError):
                reviewer_bundle_use_at = None
            generation_zero_bootstrap = (
                receipt.get("qualification_generation") == 0
                and receipt.get("bootstrap_authorization_ref") is not None
                and receipt.get("bootstrap_authorization_ref")
                == receipt.get("human_approval_receipt_ref")
                and receipt.get("bootstrap_authorization_digest")
                == receipt.get("human_approval_receipt_digest")
            )
            reviewer_bundle_contract_errors = validate_role_assignments(
                bundle,
                mesh,
                final=False,
                use_at=reviewer_bundle_use_at,
                contract_only=True,
                bootstrap_mode=generation_zero_bootstrap,
            )
            if reviewer_bundle_contract_errors:
                add(
                    errors,
                    "qualification_reviewer_bundle_contract",
                    f"{receipt_id}: {reviewer_bundle_contract_errors[0]}",
                )
            supporting_registry_path = resolve_relative(bundle.get("qualification_registry_ref"))
            if supporting_registry_path is None or not supporting_registry_path.is_file():
                add(errors, "qualification_reviewer_registry_ref", receipt_id)
            elif bundle.get("qualification_registry_digest") != file_digest(supporting_registry_path):
                add(errors, "qualification_reviewer_registry_digest", receipt_id)
        assignment_schema = load_data("mesh/role-assignment.schema.json")
        assignment_map = {
            f"role-assignment:{row.get('assignment_id')}": row
            for row in bundle.get("assignments", [])
            if isinstance(row, dict)
        }
        reviewer_refs = receipt.get("reviewer_assignment_refs", [])
        reviewers = [assignment_map.get(ref) for ref in reviewer_refs]
        typed_reviewers: list[dict[str, Any]] = []
        if len(reviewer_refs) < 2 or any(row is None for row in reviewers):
            add(errors, "qualification_reviewer_assignment_ref", receipt_id)
        else:
            if receipt.get("subject_kind") == "role_assignment" and receipt.get("subject_ref") in reviewer_refs:
                add(errors, "qualification_reviewer_self_review", receipt_id)
            typed_reviewers = [row for row in reviewers if isinstance(row, dict)]
            for reviewer in typed_reviewers:
                errors.extend(schema_errors(assignment_schema, reviewer, f"{receipt_id} reviewer assignment"))
                if reviewer.get("role_id") not in mesh_role_ids or reviewer.get("work_unit_id") != receipt.get("work_unit_id"):
                    add(errors, "qualification_reviewer_assignment_scope", receipt_id)
                if reviewer.get("status") in {"blocked", "expired", "revoked"}:
                    add(errors, "qualification_reviewer_assignment_status", receipt_id)
                if reviewer.get("source_order_digest") != object_digest(reviewer.get("source_order", [])):
                    add(errors, "qualification_reviewer_source_order", receipt_id)
                if reviewer.get("knowledge_guide_lineage_digest") != object_digest(reviewer.get("knowledge_guide_lineage", [])):
                    add(errors, "qualification_reviewer_guide_lineage", receipt_id)
                if reviewer.get("runtime_adapter_digest") != object_digest(reviewer.get("runtime_adapter", {})):
                    add(errors, "qualification_reviewer_runtime_adapter", receipt_id)
            required_reviewer_roles = {
                "role-qualification-and-independence-auditor",
                "independent-whole-work-checker",
            }
            if not required_reviewer_roles <= {row.get("role_id") for row in typed_reviewers}:
                add(errors, "qualification_reviewer_role_coverage", receipt_id)
            if len({row.get("actor_instance_id") for row in typed_reviewers}) != len(typed_reviewers):
                add(errors, "qualification_reviewer_actor_independence", receipt_id)
            if len({row.get("attempt_id") for row in typed_reviewers}) != len(typed_reviewers):
                add(errors, "qualification_reviewer_attempt_independence", receipt_id)
            reviewer_capabilities = {
                capability
                for row in typed_reviewers
                for capability in row.get("capability_ids", [])
            }
            if not {
                "role_qualification_and_independence",
                "prompt_alignment_and_authority",
            } <= reviewer_capabilities:
                add(errors, "qualification_reviewer_capability_coverage", receipt_id)
            if receipt.get("independence_assessment") != "independent":
                add(errors, "qualification_reviewer_independence", receipt_id)
        decision_ref = split_typed_ref(receipt.get("human_approval_receipt_ref"))
        decision = next((
            row for row in authority.get("human_decision_receipts", [])
            if decision_ref and decision_ref[0] == "human-decision" and row.get("receipt_id") == decision_ref[1]
        ), None)
        if (
            decision is None
            or receipt.get("human_approval_receipt_digest") != decision.get("receipt_digest")
            or decision.get("decision_type") != "qualification_approval"
            or decision.get("subject_ref") != receipt.get("subject_ref")
            or decision.get("subject_digest") != receipt.get("subject_scope_digest")
            or decision.get("scope_digest") != receipt.get("subject_scope_digest")
            or decision.get("authority_scope") != [f"qualification:{receipt.get('subject_kind')}"]
            or decision.get("decision") != "approved"
        ):
            add(errors, "qualification_human_approval", receipt_id)
        else:
            errors.extend(validate_human_decision_receipt(decision, authority))
        generation = receipt.get("qualification_generation")
        if generation == 0:
            if (
                receipt.get("bootstrap_authorization_ref") != receipt.get("human_approval_receipt_ref")
                or receipt.get("bootstrap_authorization_digest") != receipt.get("human_approval_receipt_digest")
            ):
                add(errors, "qualification_bootstrap_authorization", receipt_id)
        elif isinstance(generation, int) and generation > 0:
            try:
                receipt_use_at = parse_time(receipt.get("issued_at"))
            except (TypeError, ValueError):
                receipt_use_at = None
            for reviewer in typed_reviewers:
                parsed_reviewer_receipt = split_typed_ref(reviewer.get("qualification_receipt_ref"))
                reviewer_receipt = (
                    maps["qualification_receipts"].get(parsed_reviewer_receipt[1])
                    if parsed_reviewer_receipt and parsed_reviewer_receipt[0] == "qualification-receipt"
                    else None
                )
                if (
                    reviewer.get("status") != "qualified_for_unit"
                    or reviewer_receipt is None
                    or reviewer_receipt.get("qualification_generation", generation) >= generation
                    or receipt_use_at is None
                    or not qualification_active_at(reviewer_receipt, receipt_use_at)
                ):
                    add(errors, "qualification_generation_chain", f"{receipt_id}: {reviewer.get('assignment_id')}")
    for pack in value.get("expert_packs", []):
        contract = resolve_relative(pack.get("contract_ref"))
        if contract is None or not contract.is_file():
            add(errors, "expert_pack_contract_ref", str(pack.get("expert_pack_id")))
        elif pack.get("contract_digest") != file_digest(contract):
            add(errors, "expert_pack_contract_digest", str(pack.get("expert_pack_id")))
        for binding in pack.get("source_manifest_bindings", []):
            source_manifest = resolve_relative(binding.get("ref"))
            if source_manifest is None or not source_manifest.is_file():
                add(errors, "expert_pack_source_manifest_ref", f"{pack.get('expert_pack_id')}: {binding.get('ref')}")
            elif binding.get("digest") != file_digest(source_manifest):
                add(errors, "expert_pack_source_manifest_digest", f"{pack.get('expert_pack_id')}: {binding.get('ref')}")
        for binding in pack.get("fixture_result_bindings", []):
            fixture_result = resolve_relative(binding.get("ref"))
            if fixture_result is None or not fixture_result.is_file():
                add(errors, "expert_pack_fixture_ref", f"{pack.get('expert_pack_id')}: {binding.get('ref')}")
            elif binding.get("digest") != file_digest(fixture_result):
                add(errors, "expert_pack_fixture_digest", f"{pack.get('expert_pack_id')}: {binding.get('ref')}")
            if pack.get("qualification_state") == "qualified" and binding.get("result") != "pass":
                add(errors, "expert_pack_fixture_result", f"{pack.get('expert_pack_id')}: {binding.get('ref')}")
        expected_scope = object_digest({
            "expert_pack_id": pack.get("expert_pack_id"),
            "revision": pack.get("revision"),
            "pack_kind": pack.get("pack_kind"),
            "contract_ref": pack.get("contract_ref"),
            "contract_digest": pack.get("contract_digest"),
            "capability_ids": pack.get("capability_ids"),
            "scope": pack.get("scope"),
            "exclusions": pack.get("exclusions"),
            "source_manifest_bindings": pack.get("source_manifest_bindings"),
            "fixture_result_bindings": pack.get("fixture_result_bindings"),
        })
        if pack.get("qualification_scope_digest") != expected_scope:
            add(errors, "expert_pack_scope_digest", str(pack.get("expert_pack_id")))
        effective_at: datetime | None = None
        try:
            effective_at = parse_time(pack.get("effective_at"))
            expires_at = pack.get("expires_at")
            if expires_at is not None and parse_time(expires_at) <= effective_at:
                add(errors, "expert_pack_time", str(pack.get("expert_pack_id")))
        except (TypeError, ValueError) as exc:
            add(errors, "expert_pack_time", f"{pack.get('expert_pack_id')}: {exc}")
        receipt_refs = pack.get("qualification_receipt_refs", [])
        receipt_digests = pack.get("qualification_receipt_digests", [])
        if len(receipt_refs) != len(receipt_digests):
            add(errors, "expert_pack_receipt_pairs", str(pack.get("expert_pack_id")))
        if pack.get("qualification_state") == "qualified":
            if not receipt_refs or not receipt_digests:
                add(
                    errors,
                    "expert_pack_qualification_receipt",
                    f"{pack.get('expert_pack_id')}: qualified state requires a typed receipt",
                )
            for ref, digest in zip(receipt_refs, receipt_digests):
                parsed = split_typed_ref(ref)
                receipt = maps["qualification_receipts"].get(parsed[1]) if parsed and parsed[0] == "qualification-receipt" else None
                if (
                    receipt is None
                    or digest != receipt.get("receipt_digest")
                    or receipt.get("subject_kind") != "expert_pack"
                    or receipt.get("subject_ref") != f"expert-pack:{pack.get('expert_pack_id')}"
                    or receipt.get("subject_scope_digest") != expected_scope
                    or receipt.get("expert_pack_ref") != f"expert-pack:{pack.get('expert_pack_id')}"
                    or receipt.get("expert_pack_digest") != expected_scope
                    or set(receipt.get("capability_ids", [])) != set(pack.get("capability_ids", []))
                    or receipt.get("decision") != "qualified"
                    or receipt.get("abstention_fixture_passed") is not True
                ):
                    add(errors, "expert_pack_qualification_receipt", f"{pack.get('expert_pack_id')}: {ref}")
                elif effective_at is None or not qualification_active_at(receipt, effective_at):
                    add(errors, "expert_pack_qualification_time", f"{pack.get('expert_pack_id')}: {ref}")
    for receipt in value.get("correlation_acceptance_receipts", []):
        errors.extend(
            validate_correlation_acceptance_authority(
                receipt, authority, label=str(receipt.get("receipt_id"))
            )
        )
    expected_registry = object_digest(value, omit=("registry_digest",))
    if value.get("registry_digest") != expected_registry:
        add(errors, "qualification_registry_digest", f"expected {expected_registry}")
    if final and value.get("registry_digest") == ZERO_DIGEST:
        add(errors, "qualification_registry_placeholder", "registry digest remains a placeholder")
    return errors, maps


def qualification_active_at(receipt: dict[str, Any], used_at: datetime) -> bool:
    """Return whether a qualified receipt covers one deterministic use time."""
    try:
        issued_at = parse_time(receipt.get("issued_at"))
        expires_at = receipt.get("expires_at")
        return (
            receipt.get("decision") == "qualified"
            and issued_at <= used_at
            and (expires_at is None or used_at <= parse_time(expires_at))
        )
    except (TypeError, ValueError):
        return False


def role_assignment_qualification_scope_digest(value: dict[str, Any]) -> str:
    """Bind qualification to stable assignment inputs without a receipt cycle."""
    return object_digest({
        key: item
        for key, item in value.items()
        if key not in {"qualification_receipt_ref", "qualification_receipt_digest", "status"}
    })


def prompt_review_assignment_scope_digest(value: dict[str, Any]) -> str:
    """Bind prompt review to role, task, sources, context, and expected gain."""
    return object_digest({
        key: value.get(key)
        for key in (
            "assignment_id", "work_unit_id", "assignment_kind", "role_id",
            "capability_ids", "expected_information_gain", "task_prompt_ref",
            "task_prompt_digest", "checks_assignment_ids", "source_order_digest",
            "knowledge_guide_lineage_digest", "runtime_adapter_digest", "independence",
        )
    })


def cached_validate_qualification_registry(
    value: dict[str, Any], final: bool
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    dependency_refs: list[Any] = [
        "mesh/qualification-registry.schema.json",
        "mesh/expert-pack.schema.json",
        "mesh/qualification-receipt.schema.json",
        "mesh/correlation-acceptance-receipt.schema.json",
        "mesh/role-assignment-bundle.schema.json",
        "mesh/role-assignment.schema.json",
        "mesh/agent-mesh.v3.json",
        "mesh/role-catalog.yaml",
        "firewall/prompt-neutrality-contract.yaml",
    ]
    dependency_refs.extend(
        pack.get("contract_ref") for pack in value.get("expert_packs", [])
    )
    for pack in value.get("expert_packs", []):
        dependency_refs.extend(
            binding.get("ref") for binding in pack.get("source_manifest_bindings", [])
        )
        dependency_refs.extend(
            binding.get("ref") for binding in pack.get("fixture_result_bindings", [])
        )
    for receipt in value.get("qualification_receipts", []):
        dependency_refs.append(receipt.get("reviewer_assignment_bundle_ref"))
        dependency_refs.extend(
            binding.get("ref") for binding in receipt.get("fixture_bindings", [])
        )
        reviewer_bundle_path = resolve_relative(
            receipt.get("reviewer_assignment_bundle_ref")
        )
        if reviewer_bundle_path is not None and reviewer_bundle_path.is_file():
            try:
                reviewer_bundle = json.loads(
                    reviewer_bundle_path.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                reviewer_bundle = {}
            dependency_refs.extend(
                assignment_bundle_dependency_refs(reviewer_bundle)
            )
    authority_path = ROOT / "graph/authority-registry.yaml"
    key = (
        str(ROOT.resolve()),
        object_digest(value),
        final,
        file_digest(authority_path) if authority_path.is_file() else "missing",
        exact_dependency_state(dependency_refs),
    )
    cached = _QUALIFICATION_VALIDATION_CACHE.get(key)
    if cached is not None:
        errors, maps = cached
        return list(errors), maps
    result = validate_qualification_registry(value, final)
    _QUALIFICATION_VALIDATION_CACHE[key] = (list(result[0]), result[1])
    return list(result[0]), result[1]


def correlation_acceptance_scope_digest(value: dict[str, Any]) -> str:
    return object_digest({
        "assignment_bundle_id": value.get("assignment_bundle_id"),
        "work_unit_id": value.get("work_unit_id"),
        "checker_assignment_ref": value.get("checker_assignment_ref"),
        "checker_input_digest": value.get("checker_input_digest"),
        "checked_assignment_refs": value.get("checked_assignment_refs"),
        "checked_input_digests": value.get("checked_input_digests"),
        "collision_dimensions": value.get("collision_dimensions"),
        "checker_actor_instance_id": value.get("checker_actor_instance_id"),
        "checker_attempt_id": value.get("checker_attempt_id"),
    })


def validate_correlation_acceptance_authority(
    receipt: dict[str, Any],
    authority: dict[str, Any],
    *,
    label: str,
) -> list[str]:
    """Validate the human trust root even when an acceptance is not yet used."""
    errors: list[str] = []
    expected_scope = correlation_acceptance_scope_digest(receipt)
    decision_ref = split_typed_ref(receipt.get("human_decision_receipt_ref"))
    decision = next((
        row for row in authority.get("human_decision_receipts", [])
        if decision_ref
        and decision_ref[0] == "human-decision"
        and row.get("receipt_id") == decision_ref[1]
    ), None)
    if (
        decision is None
        or receipt.get("human_decision_receipt_digest") != decision.get("receipt_digest")
        or decision.get("decision_type") != "correlation_acceptance_approval"
        or decision.get("subject_ref") != f"correlation-acceptance:{receipt.get('receipt_id')}"
        or decision.get("subject_digest") != expected_scope
        or decision.get("scope_digest") != expected_scope
        or decision.get("authority_scope") != [f"correlation_acceptance:{receipt.get('work_unit_id')}"]
        or decision.get("decision") != "approved"
    ):
        add(errors, "correlation_human_decision", label)
        return errors
    errors.extend(validate_human_decision_receipt(decision, authority))
    try:
        accepted_at = parse_time(receipt.get("issued_at"))
        decision_at = parse_time(decision.get("issued_at"))
        receipt_expiry = receipt.get("expires_at")
        decision_expiry = decision.get("expires_at")
        if accepted_at < decision_at:
            add(errors, "correlation_human_decision_time", "acceptance predates its human decision")
        if receipt_expiry is not None and parse_time(receipt_expiry) <= accepted_at:
            add(errors, "correlation_receipt_expiry", label)
        if decision_expiry is not None and accepted_at > parse_time(decision_expiry):
            add(errors, "correlation_human_decision_time", "human decision expired before acceptance")
    except (TypeError, ValueError) as exc:
        add(errors, "correlation_receipt_time", str(exc))
    return errors


def validate_correlation_acceptance_receipt(
    receipt: dict[str, Any],
    bundle: dict[str, Any],
    checker: dict[str, Any],
    targets: list[dict[str, Any]],
    collisions: set[str],
    authority: dict[str, Any],
    *,
    use_at: datetime | None = None,
) -> list[str]:
    errors = schema_errors(
        load_data("mesh/correlation-acceptance-receipt.schema.json"),
        receipt,
        "correlation acceptance receipt",
    )
    if receipt.get("receipt_digest") != object_digest(receipt, omit=("receipt_digest",)):
        add(errors, "correlation_receipt_digest", str(receipt.get("receipt_id")))
    expected_targets = sorted(
        (
            f"role-assignment:{target.get('assignment_id')}",
            object_digest(target),
        )
        for target in targets
    )
    expected_target_refs = [ref for ref, _digest in expected_targets]
    expected_target_digests = [digest for _ref, digest in expected_targets]
    if (
        receipt.get("assignment_bundle_id") != bundle.get("bundle_id")
        or receipt.get("work_unit_id") != bundle.get("work_unit_id")
        or receipt.get("work_unit_id") != checker.get("work_unit_id")
        or any(target.get("work_unit_id") != receipt.get("work_unit_id") for target in targets)
        or receipt.get("checker_assignment_ref") != f"role-assignment:{checker.get('assignment_id')}"
        or receipt.get("checker_input_digest") != object_digest(checker)
        or receipt.get("checked_assignment_refs") != expected_target_refs
        or receipt.get("checked_input_digests") != expected_target_digests
        or set(receipt.get("collision_dimensions", [])) != collisions
        or receipt.get("checker_actor_instance_id") != checker.get("actor_instance_id")
        or receipt.get("checker_attempt_id") != checker.get("attempt_id")
        or receipt.get("decision") != "accepted_for_bounded_unit"
    ):
        add(errors, "correlation_acceptance_scope", str(receipt.get("receipt_id")))
    errors.extend(
        validate_correlation_acceptance_authority(
            receipt, authority, label=str(receipt.get("receipt_id"))
        )
    )
    if use_at is not None:
        try:
            issued_at = parse_time(receipt.get("issued_at"))
            expires_at = receipt.get("expires_at")
            if use_at < issued_at or (
                expires_at is not None and use_at >= parse_time(expires_at)
            ):
                add(errors, "correlation_acceptance_use_time", str(receipt.get("receipt_id")))
        except (TypeError, ValueError) as exc:
            add(errors, "correlation_acceptance_use_time", str(exc))
    return errors


def assignment_correlation_dimensions(
    checker: dict[str, Any], targets: list[dict[str, Any]]
) -> set[str]:
    """Derive the soft correlation dimensions for one checker relation."""
    collisions: set[str] = set()
    for target in targets:
        if set(checker.get("independence", {}).get("prompt_author_ids", [])) & set(
            target.get("independence", {}).get("prompt_author_ids", [])
        ):
            collisions.add("prompt_authorship")
        if checker.get("independence", {}).get("answer_context_exposure") != "none":
            collisions.add("answer_context_exposure")
        checker_sources = [
            row.get("source_ref") for row in checker.get("source_order", [])
        ]
        target_sources = [
            row.get("source_ref") for row in target.get("source_order", [])
        ]
        if checker_sources == target_sources:
            collisions.add("source_order")
        checker_guides = {
            row.get("guide_digest")
            for row in checker.get("knowledge_guide_lineage", [])
        }
        target_guides = {
            row.get("guide_digest")
            for row in target.get("knowledge_guide_lineage", [])
        }
        if checker_guides & target_guides:
            collisions.add("KnowledgeGuide_digest")
        if checker.get("runtime_adapter", {}).get("runtime_family") == target.get(
            "runtime_adapter", {}
        ).get("runtime_family"):
            collisions.add("runtime_adapter")
    return collisions


def validate_correlation_acceptance_reachability(
    ledger: dict[str, Any],
    qualification_registry: dict[str, Any],
    authority: dict[str, Any],
) -> list[str]:
    """Require each accepted exception to have one exact ledger-reachable use."""
    errors: list[str] = []
    accepted = {
        row.get("receipt_id"): row
        for row in qualification_registry.get("correlation_acceptance_receipts", [])
        if row.get("decision") == "accepted_for_bounded_unit"
    }
    if not accepted:
        return errors
    uses: dict[str, set[tuple[Any, ...]]] = {
        receipt_id: set() for receipt_id in accepted
    }
    bundle_identities: dict[str, set[tuple[str, str]]] = {}
    for event in ledger.get("events", []):
        details = event.get("details", {})
        event_type = event.get("event_type")
        if event_type == "check_completed":
            bundle_ref = details.get("assignment_bundle_ref")
            bundle_digest = details.get("assignment_bundle_digest")
            selected_refs = details.get("reviewer_assignment_refs", [])
        elif event_type in {"completeness_entry", "completeness_midflight"}:
            bundle_ref = details.get("completeness_assignment_bundle_ref")
            bundle_digest = details.get("completeness_assignment_bundle_digest")
            selected_refs = [details.get("completeness_assignment_ref")]
        else:
            continue
        bundle_path = resolve_relative(bundle_ref)
        if (
            bundle_path is None
            or not bundle_path.is_file()
            or bundle_digest != file_digest(bundle_path)
        ):
            continue
        try:
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        bundle_id = bundle.get("bundle_id")
        if not isinstance(bundle_id, str):
            continue
        bundle_identities.setdefault(bundle_id, set()).add(
            (str(bundle_ref), str(bundle_digest))
        )
        assignment_map = {
            f"role-assignment:{row.get('assignment_id')}": row
            for row in bundle.get("assignments", [])
            if isinstance(row, dict)
        }
        try:
            used_at = parse_time(event.get("occurred_at"))
        except (TypeError, ValueError):
            used_at = None
        for checker_ref in selected_refs:
            checker = assignment_map.get(checker_ref)
            if checker is None:
                continue
            acceptance_ref = split_typed_ref(
                checker.get("independence", {}).get(
                    "human_acceptance_receipt_ref"
                )
            )
            receipt = (
                accepted.get(acceptance_ref[1])
                if acceptance_ref and acceptance_ref[0] == "correlation-acceptance"
                else None
            )
            if receipt is None:
                continue
            targets = [
                assignment_map[f"role-assignment:{target_id}"]
                for target_id in checker.get("checks_assignment_ids", [])
                if f"role-assignment:{target_id}" in assignment_map
            ]
            relation_errors = validate_correlation_acceptance_receipt(
                receipt,
                bundle,
                checker,
                targets,
                assignment_correlation_dimensions(checker, targets),
                authority,
                use_at=used_at,
            )
            if relation_errors:
                add(
                    errors,
                    "correlation_acceptance_relation",
                    f"{receipt.get('receipt_id')}: {relation_errors[0]}",
                )
                continue
            target_pairs = tuple(
                sorted(
                    (
                        f"role-assignment:{target.get('assignment_id')}",
                        object_digest(target),
                    )
                    for target in targets
                )
            )
            uses[str(receipt.get("receipt_id"))].add(
                (bundle_id, checker_ref, target_pairs)
            )
    for bundle_id, identities in bundle_identities.items():
        if len(identities) > 1:
            add(
                errors,
                "correlation_bundle_id_collision",
                f"{bundle_id}: {sorted(identities)}",
            )
    for receipt_id, receipt_uses in uses.items():
        if not receipt_uses:
            add(errors, "correlation_acceptance_orphan_active", receipt_id)
        elif len(receipt_uses) > 1:
            add(
                errors,
                "correlation_acceptance_ambiguous_use",
                f"{receipt_id}: {len(receipt_uses)} distinct uses",
            )
    return errors


def validate_role_assignments(
    bundle: dict[str, Any],
    mesh: dict[str, Any],
    final: bool,
    *,
    use_at: datetime | None = None,
    contract_only: bool = False,
    bootstrap_mode: bool = False,
) -> list[str]:
    dependency_refs = assignment_bundle_dependency_refs(bundle)
    role_cache_key = (
        str(ROOT.resolve()),
        object_digest(bundle),
        object_digest(mesh),
        final,
        contract_only,
        bootstrap_mode,
        use_at.isoformat() if use_at is not None else None,
        exact_dependency_state(dependency_refs),
        file_digest(ROOT / "mesh/role-catalog.yaml")
        if (ROOT / "mesh/role-catalog.yaml").is_file()
        else "missing",
        file_digest(ROOT / "graph/authority-registry.yaml")
        if (ROOT / "graph/authority-registry.yaml").is_file()
        else "missing",
    )
    cached_role_errors = _ROLE_ASSIGNMENT_VALIDATION_CACHE.get(role_cache_key)
    if cached_role_errors is not None:
        return list(cached_role_errors)
    errors = schema_errors(load_data("mesh/role-assignment-bundle.schema.json"), bundle, "role assignment bundle")
    registry_ref = bundle.get("qualification_registry_ref")
    registry_path = resolve_relative(registry_ref)
    if registry_path is None or not registry_path.is_file():
        add(errors, "role_assignment_registry_ref", str(registry_ref))
        qualification_registry: dict[str, Any] = {}
    else:
        qualification_registry = (
            json.loads(registry_path.read_text(encoding="utf-8"))
            if registry_path.suffix.lower() == ".json"
            else yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        )
    if contract_only:
        errors.extend(
            schema_errors(
                load_data("mesh/qualification-registry.schema.json"),
                qualification_registry,
                "mesh/qualification-registry.json",
            )
        )
        qualification_maps = {
            "expert_packs": {
                row.get("expert_pack_id"): row
                for row in qualification_registry.get("expert_packs", [])
            },
            "qualification_receipts": {
                row.get("receipt_id"): row
                for row in qualification_registry.get("qualification_receipts", [])
            },
            "correlation_acceptance_receipts": {
                row.get("receipt_id"): row
                for row in qualification_registry.get("correlation_acceptance_receipts", [])
            },
        }
    else:
        registry_errors, qualification_maps = cached_validate_qualification_registry(
            qualification_registry, final
        )
        errors.extend(registry_errors)
    if registry_path is not None and registry_path.is_file() and bundle.get("qualification_registry_digest") != file_digest(registry_path):
        add(errors, "role_assignment_registry_digest", "qualification registry file digest is stale")
    expected_bundle_digest = object_digest(bundle, omit=("bundle_digest",))
    if bundle.get("bundle_digest") != expected_bundle_digest:
        add(errors, "role_assignment_bundle_digest", f"expected {expected_bundle_digest}")
    assignment_schema = load_data("mesh/role-assignment.schema.json")
    role_catalog = load_data("mesh/role-catalog.yaml")
    known_capabilities = catalog_capability_ids(role_catalog)
    assignments = bundle.get("assignments", [])
    role_map = {row.get("role_id"): row for row in mesh.get("roles", [])}
    assignment_map = {row.get("assignment_id"): row for row in assignments}
    if len(assignment_map) != len(assignments):
        add(errors, "role_assignment_id", "assignment IDs must be unique")
    meta_checkers = [
        row for row in assignments
        if row.get("role_id") == "role-qualification-and-independence-auditor"
    ]
    whole_checkers = [
        row for row in assignments
        if row.get("role_id") == "independent-whole-work-checker"
    ]
    if len(meta_checkers) != 1:
        add(errors, "role_assignment_meta_checker_cardinality", "exactly one meta-checker is required")
    if len(whole_checkers) != 1:
        add(errors, "role_assignment_whole_work_checker_cardinality", "exactly one whole-work checker is required")
    if len(meta_checkers) == 1:
        meta = meta_checkers[0]
        expected_targets = set(assignment_map) - {meta.get("assignment_id")}
        if set(meta.get("checks_assignment_ids", [])) != expected_targets:
            add(
                errors,
                "role_assignment_meta_checker_coverage",
                f"{meta.get('assignment_id')}: expected {sorted(expected_targets)}",
            )
    if len(meta_checkers) == 1 and len(whole_checkers) == 1:
        meta_id = meta_checkers[0].get("assignment_id")
        if meta_id not in whole_checkers[0].get("checks_assignment_ids", []):
            add(
                errors,
                "role_assignment_whole_work_checks_meta_checker",
                f"{whole_checkers[0].get('assignment_id')} must check {meta_id}",
            )
    prompt_reviews = bundle.get("prompt_neutrality_reviews", [])
    prompt_review_map = {row.get("review_id"): row for row in prompt_reviews}
    used_prompt_review_ids: set[str] = set()
    if len(prompt_review_map) != len(prompt_reviews):
        add(errors, "role_assignment_prompt_review_ref", "prompt-neutrality review IDs must be unique")
    required_prompt_dimensions = {
        "presupposed_conclusion", "framing", "omitted_alternatives",
        "counterevidence_route", "abstention_path", "authority_transfer",
    }
    for review in prompt_reviews:
        review_id = str(review.get("review_id"))
        expected_review_digest = object_digest(review, omit=("receipt_digest",))
        if review.get("receipt_digest") != expected_review_digest:
            add(errors, "role_assignment_prompt_review_digest", f"{review_id}: expected {expected_review_digest}")
        if set(review.get("review_dimensions", [])) != required_prompt_dimensions:
            add(errors, "role_assignment_prompt_review_scope", f"{review_id}: review dimensions are incomplete")
    if bundle.get("fixture_kind") == "design_time_simulation":
        if bundle.get("runtime_assignments") is not False or bundle.get("authority_effect") != "none":
            add(errors, "role_assignment_fixture_authority", "design fixture cannot activate roles or authority")
        if prompt_reviews or any(
            assignment.get(field) is not None
            for assignment in assignments
            for field in (
                "task_prompt_ref", "task_prompt_digest",
                "prompt_neutrality_review_ref", "prompt_neutrality_review_digest",
            )
        ):
            add(errors, "role_assignment_fixture_prompt_receipt", "design fixtures cannot claim runtime prompt review")
    if bundle.get("fixture_kind") == "runtime_receipt":
        bundle_unit = bundle.get("work_unit_id")
        if any(row.get("work_unit_id") != bundle_unit for row in assignments):
            add(errors, "role_assignment_bundle_work_unit", str(bundle.get("bundle_id")))
        try:
            bundle_issued = parse_time(bundle.get("issued_at"))
            bundle_expires = parse_time(bundle.get("expires_at"))
            if bundle_expires <= bundle_issued:
                add(errors, "role_assignment_bundle_time", str(bundle.get("bundle_id")))
            if use_at is not None and not (bundle_issued <= use_at < bundle_expires):
                add(errors, "role_assignment_bundle_use_time", str(bundle.get("bundle_id")))
        except (TypeError, ValueError) as exc:
            add(errors, "role_assignment_bundle_time", str(exc))
    for assignment in assignments:
        assignment_id = assignment.get("assignment_id", "assignment")
        errors.extend(schema_errors(assignment_schema, assignment, assignment_id))
        role_id = assignment.get("role_id")
        if role_id not in role_map:
            add(errors, "role_assignment_unknown_role", f"{assignment_id}: {role_id}")
        if (
            bundle.get("fixture_kind") == "runtime_receipt"
            and (
                assignment.get("status") not in {"candidate", "qualified_for_unit"}
                if bootstrap_mode
                else assignment.get("status") != "qualified_for_unit"
            )
        ):
            add(
                errors,
                "role_assignment_runtime_status",
                f"{assignment_id}: invalid runtime status for {'generation-zero bootstrap' if bootstrap_mode else 'qualified runtime'}",
            )
        assignment_capabilities = set(assignment.get("capability_ids", []))
        unknown_assignment_capabilities = assignment_capabilities - known_capabilities
        if unknown_assignment_capabilities:
            add(
                errors,
                "role_assignment_unknown_capability",
                f"{assignment_id}: {sorted(unknown_assignment_capabilities)}",
            )
        required_role_capabilities = set(
            mesh.get("required_role_capabilities", {}).get(role_id, [])
        )
        if not required_role_capabilities <= assignment_capabilities:
            add(
                errors,
                "role_assignment_role_capability_mismatch",
                f"{assignment_id}: missing {sorted(required_role_capabilities - assignment_capabilities)}",
            )
        role_class = role_map.get(role_id, {}).get("class")
        if role_class in {"researcher", "subject_specialist", "context_specialist", "language_checker"}:
            if assignment.get("qualification_basis", {}).get("kind") != "expert_pack":
                add(errors, "role_assignment_missing_expert_pack", f"{assignment_id} requires an ExpertPack basis")
        basis = assignment.get("qualification_basis", {})
        if basis.get("kind") == "control_contract":
            path = resolve_relative(basis.get("ref"))
            if path is None or not path.is_file():
                add(errors, "role_assignment_basis_ref", f"{assignment_id}: unresolved control basis")
            elif basis.get("digest") != file_digest(path):
                add(errors, "role_assignment_basis_digest", f"{assignment_id}: {basis.get('ref')}")
        elif basis.get("kind") == "expert_pack":
            parsed = split_typed_ref(basis.get("ref"))
            pack = qualification_maps["expert_packs"].get(parsed[1]) if parsed and parsed[0] == "expert-pack" else None
            if pack is None:
                add(errors, "role_assignment_expert_pack_ref", f"{assignment_id}: {basis.get('ref')}")
            else:
                if basis.get("digest") != pack.get("pack_digest"):
                    add(errors, "role_assignment_expert_pack_digest", assignment_id)
                if not set(assignment.get("capability_ids", [])) <= set(pack.get("capability_ids", [])):
                    add(errors, "role_assignment_expert_pack_capability", assignment_id)
                if basis.get("state") != pack.get("qualification_state"):
                    add(errors, "role_assignment_expert_pack_state", assignment_id)
                if use_at is not None:
                    try:
                        pack_effective = parse_time(pack.get("effective_at"))
                        pack_expiry = pack.get("expires_at")
                        if use_at < pack_effective or (
                            pack_expiry is not None and use_at > parse_time(pack_expiry)
                        ):
                            add(errors, "role_assignment_expert_pack_time", assignment_id)
                    except (TypeError, ValueError) as exc:
                        add(errors, "role_assignment_expert_pack_time", f"{assignment_id}: {exc}")
        source_order = assignment.get("source_order", [])
        if [row.get("ordinal") for row in source_order] != list(range(1, len(source_order) + 1)):
            add(errors, "role_assignment_source_ordinals", f"{assignment_id} source ordinals must be contiguous")
        refs = [row.get("source_ref") for row in source_order]
        if len(refs) != len(set(refs)):
            add(errors, "role_assignment_source_ref", f"{assignment_id} repeats a source reference")
        for row in source_order:
            if row.get("source_class") == "control_contract":
                path = resolve_relative(row.get("source_ref"))
                if path is None or not path.is_file():
                    add(errors, "role_assignment_source_ref", f"{assignment_id}: unresolved {row.get('source_ref')}")
                elif row.get("source_digest") != file_digest(path):
                    add(errors, "role_assignment_source_digest", f"{assignment_id}: {row.get('source_ref')}")
        expected_source_order = object_digest(source_order)
        if assignment.get("source_order_digest") != expected_source_order:
            add(errors, "role_assignment_source_order_digest", f"{assignment_id}: expected {expected_source_order}")
        guides = assignment.get("knowledge_guide_lineage", [])
        for guide in guides:
            path = resolve_relative(guide.get("guide_ref"))
            if path is None or not path.is_file():
                add(errors, "role_assignment_guide_ref", f"{assignment_id}: unresolved {guide.get('guide_ref')}")
            elif guide.get("guide_digest") != file_digest(path):
                add(errors, "role_assignment_guide_digest", f"{assignment_id}: {guide.get('guide_ref')}")
            if guide.get("used_as_evidence") is not False:
                add(errors, "role_assignment_guide_as_evidence", f"{assignment_id}: KnowledgeGuide is routing only")
        expected_guides = object_digest(guides)
        if assignment.get("knowledge_guide_lineage_digest") != expected_guides:
            add(errors, "role_assignment_guide_lineage_digest", f"{assignment_id}: expected {expected_guides}")
        expected_adapter = object_digest(assignment.get("runtime_adapter", {}))
        if assignment.get("runtime_adapter_digest") != expected_adapter:
            add(errors, "role_assignment_runtime_adapter_digest", f"{assignment_id}: expected {expected_adapter}")
        if bundle.get("fixture_kind") == "runtime_receipt":
            prompt_ref = assignment.get("task_prompt_ref")
            prompt_path = resolve_relative(prompt_ref)
            if prompt_path is None or not prompt_path.is_file():
                add(errors, "role_assignment_task_prompt_ref", f"{assignment_id}: {prompt_ref}")
            else:
                if assignment.get("task_prompt_digest") != file_digest(prompt_path):
                    add(errors, "role_assignment_task_prompt_digest", f"{assignment_id}: {prompt_ref}")
                prompt_text = prompt_path.read_text(encoding="utf-8")
                if any(re.search(pattern, prompt_text, re.I | re.S) for pattern in DESIRED_CONCLUSION_PATTERNS):
                    add(errors, "role_assignment_task_prompt_desired_conclusion", assignment_id)
            parsed_review = split_typed_ref(assignment.get("prompt_neutrality_review_ref"))
            review = (
                prompt_review_map.get(parsed_review[1])
                if parsed_review and parsed_review[0] == "prompt-neutrality-review"
                else None
            )
            if review is None:
                add(errors, "role_assignment_prompt_review_ref", assignment_id)
            else:
                used_prompt_review_ids.add(str(review.get("review_id")))
                if assignment.get("prompt_neutrality_review_digest") != review.get("receipt_digest"):
                    add(errors, "role_assignment_prompt_review_digest", assignment_id)
                expected_subject_ref = f"role-assignment:{assignment_id}"
                contract_path = resolve_relative(review.get("neutrality_contract_ref"))
                if (
                    review.get("subject_assignment_ref") != expected_subject_ref
                    or review.get("subject_assignment_scope_digest")
                    != prompt_review_assignment_scope_digest(assignment)
                    or review.get("task_prompt_ref") != prompt_ref
                    or review.get("task_prompt_digest") != assignment.get("task_prompt_digest")
                    or contract_path is None
                    or not contract_path.is_file()
                    or review.get("neutrality_contract_digest") != file_digest(contract_path)
                    or set(review.get("review_dimensions", [])) != required_prompt_dimensions
                    or review.get("authority_effect") != "none"
                ):
                    add(errors, "role_assignment_prompt_review_scope", assignment_id)
                if review.get("decision") != "accepted":
                    add(errors, "role_assignment_prompt_review_decision", assignment_id)
                reviewer_ref = split_typed_ref(review.get("reviewer_assignment_ref"))
                reviewer = (
                    assignment_map.get(reviewer_ref[1])
                    if reviewer_ref and reviewer_ref[0] == "role-assignment"
                    else None
                )
                if (
                    reviewer is None
                    or reviewer is assignment
                    or reviewer.get("work_unit_id") != assignment.get("work_unit_id")
                    or (
                        reviewer.get("status") not in {"candidate", "qualified_for_unit"}
                        if bootstrap_mode
                        else reviewer.get("status") != "qualified_for_unit"
                    )
                    or assignment_id not in reviewer.get("checks_assignment_ids", [])
                    or "prompt_alignment_and_authority" not in reviewer.get("capability_ids", [])
                ):
                    add(errors, "role_assignment_prompt_review_independence", assignment_id)
                try:
                    reviewed_at = parse_time(review.get("reviewed_at"))
                    review_expiry = review.get("expires_at")
                    if review_expiry is not None and parse_time(review_expiry) <= reviewed_at:
                        add(errors, "role_assignment_prompt_review_scope", f"{assignment_id}: invalid review interval")
                    if use_at is not None and (
                        use_at < reviewed_at
                        or (review_expiry is not None and use_at > parse_time(review_expiry))
                    ):
                        add(errors, "role_assignment_prompt_review_scope", f"{assignment_id}: review inactive at use")
                except (TypeError, ValueError) as exc:
                    add(errors, "role_assignment_prompt_review_scope", f"{assignment_id}: {exc}")
        if assignment.get("status") == "qualified_for_unit" and not contract_only:
            parsed_receipt = split_typed_ref(assignment.get("qualification_receipt_ref"))
            receipt = qualification_maps["qualification_receipts"].get(parsed_receipt[1]) if parsed_receipt and parsed_receipt[0] == "qualification-receipt" else None
            if receipt is None or not assignment.get("qualification_receipt_digest"):
                add(errors, "role_assignment_qualification_receipt", f"{assignment_id}: qualification receipt is unresolved")
            else:
                if assignment.get("qualification_receipt_digest") != receipt.get("receipt_digest"):
                    add(errors, "role_assignment_qualification_receipt_digest", f"{assignment_id}: receipt digest mismatch")
                expected_subject = f"role-assignment:{assignment_id}"
                if (
                    receipt.get("subject_kind") != "role_assignment"
                    or receipt.get("subject_ref") != expected_subject
                    or receipt.get("subject_scope_digest") != role_assignment_qualification_scope_digest(assignment)
                    or receipt.get("work_unit_id") != assignment.get("work_unit_id")
                    or set(receipt.get("capability_ids", [])) != set(assignment.get("capability_ids", []))
                    or receipt.get("runtime_adapter_digest") != assignment.get("runtime_adapter_digest")
                    or receipt.get("decision") != "qualified"
                    or receipt.get("abstention_fixture_passed") is not True
                ):
                    add(errors, "role_assignment_qualification_scope", assignment_id)
                if use_at is not None and not qualification_active_at(receipt, use_at):
                    add(errors, "role_assignment_qualification_time", assignment_id)
        if final:
            for field in ("source_order_digest", "knowledge_guide_lineage_digest", "runtime_adapter_digest"):
                if assignment.get(field) == ZERO_DIGEST:
                    add(errors, "role_assignment_placeholder_digest", f"{assignment_id}: {field}")
    orphan_prompt_reviews = set(prompt_review_map) - used_prompt_review_ids
    if orphan_prompt_reviews:
        add(errors, "role_assignment_prompt_review_orphan", str(sorted(orphan_prompt_reviews)))
    for checker in assignments:
        checker_id = checker.get("assignment_id")
        for target_id in checker.get("checks_assignment_ids", []):
            target = assignment_map.get(target_id)
            if target is None:
                add(errors, "role_assignment_unknown_target", f"{checker_id}: {target_id}")
                continue
            if (
                checker.get("role_id") != "role-qualification-and-independence-auditor"
                and checker.get("role_id")
                not in role_map.get(target.get("role_id"), {}).get("checked_by", [])
            ):
                add(errors, "role_assignment_checker_edge", f"{checker_id} cannot check {target_id}")
        if not checker.get("checks_assignment_ids"):
            continue
        targets = [
            assignment_map[target_id]
            for target_id in checker.get("checks_assignment_ids", [])
            if target_id in assignment_map
        ]
        for target_id in checker.get("checks_assignment_ids", []):
            target = assignment_map.get(target_id, {})
            if checker.get("actor_instance_id") == target.get("actor_instance_id"):
                add(errors, "role_assignment_same_actor", f"{checker_id} and {target_id}")
            if checker.get("attempt_id") == target.get("attempt_id"):
                add(errors, "role_assignment_same_attempt", f"{checker_id} and {target_id}")
        collisions = assignment_correlation_dimensions(checker, targets)
        disclosed = set(checker.get("independence", {}).get("correlation_disclosures", []))
        if disclosed != collisions:
            add(errors, "role_assignment_undisclosed_correlation", f"{checker_id}: expected {sorted(collisions)}")
        assessment = checker.get("independence", {}).get("assessment")
        acceptance = checker.get("independence", {}).get("human_acceptance_receipt_ref")
        if collisions and assessment not in {"correlated_disclosed", "blocked"}:
            add(errors, "role_assignment_correlation_assessment", f"{checker_id} cannot claim independence")
        if collisions and assessment == "correlated_disclosed" and not acceptance:
            add(errors, "role_assignment_correlation_acceptance", f"{checker_id} needs acceptance or must block")
        if collisions and assessment == "correlated_disclosed" and acceptance and not contract_only:
            parsed_acceptance = split_typed_ref(acceptance)
            receipt = qualification_maps["correlation_acceptance_receipts"].get(parsed_acceptance[1]) if parsed_acceptance and parsed_acceptance[0] == "correlation-acceptance" else None
            if receipt is None:
                add(errors, "role_assignment_correlation_acceptance", f"{checker_id}: unresolved or wrong-scope receipt")
            else:
                acceptance_errors = validate_correlation_acceptance_receipt(
                    receipt,
                    bundle,
                    checker,
                    targets,
                    collisions,
                    load_data("graph/authority-registry.yaml"),
                    use_at=use_at,
                )
                if acceptance_errors:
                    add(errors, "role_assignment_correlation_acceptance", f"{checker_id}: {acceptance_errors[0]}")
        if not collisions and (assessment != "independent" or acceptance is not None):
            add(errors, "role_assignment_false_correlation", f"{checker_id} has no derived collision")
    _ROLE_ASSIGNMENT_VALIDATION_CACHE[role_cache_key] = list(errors)
    return errors


def check_completed_scope_digest(details: dict[str, Any]) -> str:
    return object_digest(details, omit=("review_receipt_digest",))


def validate_check_completed_event(
    event: dict[str, Any],
    final: bool,
    *,
    consumed_at: datetime | None = None,
    earlier_events: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Validate one non-authorizing, qualified, exact-output review event."""
    errors: list[str] = []
    label = str(event.get("event_id"))
    details = event.get("details", {})
    affected = event.get("affected_ids", [])
    if len(affected) != 1:
        add(errors, "event_review_unit_scope", f"{label}: exactly one work unit is required")
    output_ref = details.get("reviewed_output_ref")
    output_path = resolve_relative(output_ref)
    output_digest = details.get("reviewed_output_digest")
    if output_path is None or not output_path.is_file():
        add(errors, "event_review_output_ref", f"{label}: {output_ref}")
    elif output_digest != file_digest(output_path):
        add(errors, "event_review_output_digest", label)
    if event.get("input_digest") != output_digest:
        add(errors, "event_review_input_digest", label)
    if event.get("authority_ref") != f"review-receipt:{details.get('review_receipt_id')}":
        add(errors, "event_review_authority_ref", label)
    if details.get("review_authority_effect") != "none":
        add(errors, "event_review_authority_effect", label)
    if details.get("decision") != "accepted":
        add(errors, "event_review_decision", label)
    if details.get("review_receipt_digest") != check_completed_scope_digest(details):
        add(errors, "event_review_receipt_digest", label)
    required_capabilities_list = details.get("required_capability_ids", [])
    review_dimensions = details.get("review_dimensions", [])
    if required_capabilities_list != sorted(set(required_capabilities_list)):
        add(errors, "event_review_capability_order", label)
    if review_dimensions != sorted(set(review_dimensions)):
        add(errors, "event_review_dimension_order", label)
    expected_requirements_digest = object_digest({
        "required_capability_ids": required_capabilities_list,
        "review_dimensions": review_dimensions,
    })
    if details.get("review_requirements_digest") != expected_requirements_digest:
        add(errors, "event_review_requirements_digest", label)
    unit_id = affected[0] if len(affected) == 1 else None
    requirement_candidates = [
        prior
        for prior in (earlier_events or [])
        if prior.get("event_type") in {"completeness_entry", "completeness_midflight"}
        and unit_id in prior.get("affected_ids", [])
    ]
    requirement_event = max(
        requirement_candidates,
        key=lambda row: row.get("sequence", 0),
        default=None,
    )
    if (
        requirement_event is None
        or details.get("requirement_event_id") != requirement_event.get("event_id")
        or details.get("requirement_event_hash") != requirement_event.get("event_hash")
        or required_capabilities_list
        != requirement_event.get("details", {}).get("required_capability_ids")
    ):
        add(errors, "event_review_requirement_event", label)
    try:
        reviewed_at = parse_time(details.get("reviewed_at"))
        occurred_at = parse_time(event.get("occurred_at"))
        if reviewed_at != occurred_at:
            add(errors, "event_review_time", f"{label}: reviewed_at must equal occurred_at")
    except (TypeError, ValueError) as exc:
        reviewed_at = None
        add(errors, "event_review_time", f"{label}: {exc}")

    bindings = details.get("evidence_bindings", [])
    if bindings != sorted(bindings, key=lambda item: str(item.get("ref"))):
        add(errors, "event_review_evidence_order", label)
    if len({binding.get("ref") for binding in bindings}) != len(bindings):
        add(errors, "event_review_evidence_ref", label)
    expected_evidence_set_digest = object_digest(bindings)
    if details.get("evidence_set_digest") != expected_evidence_set_digest:
        add(errors, "event_review_evidence_set_digest", label)
    expected_output_binding = {"ref": output_ref, "digest": output_digest}
    if expected_output_binding not in bindings:
        add(errors, "event_review_output_binding", label)
    for binding in bindings:
        path = resolve_relative(binding.get("ref")) if isinstance(binding, dict) else None
        if (
            path is None
            or not path.is_file()
            or binding.get("digest") != file_digest(path)
        ):
            add(errors, "event_review_evidence_binding", f"{label}: {binding.get('ref') if isinstance(binding, dict) else binding}")

    bundle_path = resolve_relative(details.get("assignment_bundle_ref"))
    if bundle_path is None or not bundle_path.is_file():
        add(errors, "event_review_assignment_bundle", label)
        return errors
    if details.get("assignment_bundle_digest") != file_digest(bundle_path):
        add(errors, "event_review_assignment_bundle_digest", label)
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle_errors = validate_role_assignments(
        bundle,
        load_data("mesh/agent-mesh.v3.json"),
        final,
        use_at=consumed_at or reviewed_at,
    )
    if bundle_errors:
        add(errors, "event_review_assignment_bundle_validation", f"{label}: {bundle_errors[0]}")
    if bundle.get("fixture_kind") != "runtime_receipt" or bundle.get("runtime_assignments") is not True:
        add(errors, "event_review_runtime_bundle", label)
    assignment_map = {
        f"role-assignment:{row.get('assignment_id')}": row
        for row in bundle.get("assignments", [])
        if isinstance(row, dict)
    }
    reviewer_refs = details.get("reviewer_assignment_refs", [])
    if reviewer_refs != sorted(set(reviewer_refs)):
        add(errors, "event_review_reviewer_order", label)
    reviewers = [assignment_map.get(ref) for ref in reviewer_refs]
    if len(reviewer_refs) < 2 or any(row is None for row in reviewers):
        add(errors, "event_review_reviewer_ref", label)
        return errors
    typed_reviewers = [row for row in reviewers if isinstance(row, dict)]
    producer_ref = details.get("producer_assignment_ref")
    producer = assignment_map.get(producer_ref)
    if (
        producer is None
        or producer.get("assignment_kind") != "writer"
        or producer.get("work_unit_id") != unit_id
        or producer.get("status") != "qualified_for_unit"
        or details.get("producer_assignment_digest") != object_digest(producer)
    ):
        add(errors, "event_review_producer_assignment", label)
    requirement_details = requirement_event.get("details", {}) if requirement_event else {}
    completeness_ref = requirement_details.get("completeness_assignment_ref")
    completeness_assignment = assignment_map.get(completeness_ref)
    if (
        requirement_details.get("completeness_assignment_bundle_ref")
        != details.get("assignment_bundle_ref")
        or requirement_details.get("completeness_assignment_bundle_digest")
        != details.get("assignment_bundle_digest")
        or completeness_assignment is None
        or completeness_assignment.get("role_id") != "doctrine-mesh-completeness-auditor"
        or completeness_assignment.get("status") != "qualified_for_unit"
        or completeness_assignment.get("work_unit_id") != unit_id
        or requirement_details.get("completeness_assignment_digest")
        != object_digest(completeness_assignment)
    ):
        add(errors, "event_review_completeness_assignment", label)
    if any(
        row.get("status") != "qualified_for_unit" or row.get("work_unit_id") != unit_id
        for row in typed_reviewers
    ):
        add(errors, "event_review_reviewer_qualification", label)
    if producer is not None and any(
        producer.get("assignment_id") not in row.get("checks_assignment_ids", [])
        for row in typed_reviewers
    ):
        add(errors, "event_review_checker_target", label)
    required_roles = {
        "role-qualification-and-independence-auditor",
        "independent-whole-work-checker",
    }
    if not required_roles <= {row.get("role_id") for row in typed_reviewers}:
        add(errors, "event_review_role_coverage", label)
    if len({row.get("actor_instance_id") for row in typed_reviewers}) != len(typed_reviewers):
        add(errors, "event_review_actor_independence", label)
    if len({row.get("attempt_id") for row in typed_reviewers}) != len(typed_reviewers):
        add(errors, "event_review_attempt_independence", label)
    if len(typed_reviewers) == 2:
        first, second = typed_reviewers
        pairwise_collisions = set()
        if set(first.get("independence", {}).get("prompt_author_ids", [])) & set(second.get("independence", {}).get("prompt_author_ids", [])):
            pairwise_collisions.add("prompt_authorship")
        if [row.get("source_ref") for row in first.get("source_order", [])] == [row.get("source_ref") for row in second.get("source_order", [])]:
            pairwise_collisions.add("source_order")
        if {row.get("guide_digest") for row in first.get("knowledge_guide_lineage", [])} & {row.get("guide_digest") for row in second.get("knowledge_guide_lineage", [])}:
            pairwise_collisions.add("KnowledgeGuide_digest")
        if first.get("runtime_adapter", {}).get("runtime_family") == second.get("runtime_adapter", {}).get("runtime_family"):
            pairwise_collisions.add("runtime_adapter")
        if pairwise_collisions:
            add(errors, "event_review_pairwise_independence", f"{label}: {sorted(pairwise_collisions)}")
    capability_union = {
        capability
        for row in typed_reviewers
        for capability in row.get("capability_ids", [])
    }
    required_capabilities = set(required_capabilities_list)
    if not required_capabilities <= capability_union:
        add(errors, "event_review_capability_coverage", f"{label}: {sorted(required_capabilities - capability_union)}")
    decisions = details.get("reviewer_decisions", [])
    decision_map = {
        row.get("reviewer_assignment_ref"): row
        for row in decisions
        if isinstance(row, dict)
    }
    if (
        len(decision_map) != len(decisions)
        or sorted(decision_map) != reviewer_refs
        or decisions != sorted(decisions, key=lambda row: str(row.get("reviewer_assignment_ref")))
    ):
        add(errors, "event_review_decision_coverage", label)
    for reviewer_ref in reviewer_refs:
        reviewer = assignment_map.get(reviewer_ref, {})
        decision = decision_map.get(reviewer_ref, {})
        expected_decision_digest = object_digest(decision, omit=("review_digest",))
        if decision.get("review_digest") != expected_decision_digest:
            add(errors, "event_review_decision_digest", f"{label}: {reviewer_ref}")
        if (
            decision.get("reviewer_assignment_digest") != object_digest(reviewer)
            or decision.get("reviewer_actor_instance_id") != reviewer.get("actor_instance_id")
            or decision.get("reviewer_attempt_id") != reviewer.get("attempt_id")
            or decision.get("reviewed_output_digest") != output_digest
            or decision.get("requirement_event_hash") != details.get("requirement_event_hash")
            or decision.get("review_requirements_digest") != expected_requirements_digest
            or decision.get("evidence_set_digest") != expected_evidence_set_digest
            or decision.get("decision") != "accepted"
        ):
            add(errors, "event_review_decision_scope", f"{label}: {reviewer_ref}")
        try:
            decided_at = parse_time(decision.get("decided_at"))
            expires_at = decision.get("expires_at")
            if reviewed_at is not None and decided_at > reviewed_at:
                add(errors, "event_review_decision_time", f"{label}: {reviewer_ref}")
            check_at = consumed_at or reviewed_at
            if expires_at is not None and (
                parse_time(expires_at) <= decided_at
                or (check_at is not None and check_at > parse_time(expires_at))
            ):
                add(errors, "event_review_decision_expiry", f"{label}: {reviewer_ref}")
        except (TypeError, ValueError) as exc:
            add(errors, "event_review_decision_time", f"{label}: {reviewer_ref}: {exc}")
    return errors


def validate_completeness_assignment_event(
    event: dict[str, Any], final: bool, *, runtime_required: bool
) -> list[str]:
    """Resolve the exact completeness auditor that selected one requirement set."""
    errors: list[str] = []
    label = str(event.get("event_id"))
    details = event.get("details", {})
    bundle_path = resolve_relative(details.get("completeness_assignment_bundle_ref"))
    if bundle_path is None or not bundle_path.is_file():
        add(errors, "event_completeness_bundle_ref", label)
        return errors
    if details.get("completeness_assignment_bundle_digest") != file_digest(bundle_path):
        add(errors, "event_completeness_bundle_digest", label)
    try:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        add(errors, "event_completeness_bundle_ref", f"{label}: {exc}")
        return errors
    assignment_map = {
        f"role-assignment:{row.get('assignment_id')}": row
        for row in bundle.get("assignments", [])
        if isinstance(row, dict)
    }
    assignment = assignment_map.get(details.get("completeness_assignment_ref"))
    if (
        assignment is None
        or details.get("completeness_assignment_digest") != object_digest(assignment)
    ):
        add(errors, "event_completeness_assignment_ref", label)
        return errors
    if not runtime_required:
        return errors
    try:
        used_at = parse_time(event.get("occurred_at"))
    except (TypeError, ValueError) as exc:
        used_at = None
        add(errors, "event_completeness_assignment_time", f"{label}: {exc}")
    bundle_errors = validate_role_assignments(
        bundle,
        load_data("mesh/agent-mesh.v3.json"),
        final,
        use_at=used_at,
    )
    if bundle_errors:
        add(
            errors,
            "event_completeness_bundle_validation",
            f"{label}: {bundle_errors[0]}",
        )
    affected_ids = event.get("affected_ids", [])
    if (
        bundle.get("fixture_kind") != "runtime_receipt"
        or bundle.get("runtime_assignments") is not True
        or assignment.get("role_id") != "doctrine-mesh-completeness-auditor"
        or assignment.get("status") != "qualified_for_unit"
        or "doctrine_mesh_completeness_and_gap_detection"
        not in assignment.get("capability_ids", [])
        or "doctrine_mesh_completeness_and_gap_detection"
        not in details.get("required_capability_ids", [])
        or assignment.get("work_unit_id") not in affected_ids
    ):
        add(errors, "event_completeness_assignment_qualification", label)
    if event.get("event_type") in {"completeness_entry", "completeness_exit"} and (
        len(affected_ids) != 1
    ):
        add(errors, "event_completeness_unit_scope", label)
    return errors


def validate_midflight_action_results(
    event: dict[str, Any],
    expected_actions: list[str],
    expected_subjects: list[str],
    *,
    final: bool,
    runtime_required: bool,
) -> list[str]:
    """Resolve every midflight action to evidence and a capable assignment."""
    errors: list[str] = []
    label = str(event.get("event_id"))
    details = event.get("details", {})
    bundle_ref = details.get("action_assignment_bundle_ref")
    bundle_path = resolve_relative(bundle_ref)
    if bundle_path is None or not bundle_path.is_file():
        add(errors, "event_midflight_action_bundle_ref", f"{label}: {bundle_ref}")
        return errors
    if details.get("action_assignment_bundle_digest") != file_digest(bundle_path):
        add(errors, "event_midflight_action_bundle_digest", label)
    try:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        add(errors, "event_midflight_action_bundle_ref", f"{label}: {exc}")
        return errors
    try:
        use_at = parse_time(event.get("occurred_at"))
    except (TypeError, ValueError):
        use_at = None
    bundle_errors = validate_role_assignments(
        bundle,
        load_data("mesh/agent-mesh.v3.json"),
        final,
        use_at=use_at if runtime_required else None,
    )
    if bundle_errors:
        add(errors, "event_midflight_action_bundle_validation", f"{label}: {bundle_errors[0]}")
    if runtime_required and (
        bundle.get("fixture_kind") != "runtime_receipt"
        or bundle.get("runtime_assignments") is not True
    ):
        add(errors, "event_midflight_action_bundle_runtime", label)
    assignment_map = {
        f"role-assignment:{row.get('assignment_id')}": row
        for row in bundle.get("assignments", [])
        if isinstance(row, dict)
    }
    action_requirements = {
        row.get("action_id"): row
        for row in load_data("firewall/action-checker-requirements.yaml").get(
            "requirements", []
        )
    }
    evidence = evidence_maps(load_data("evidence/evidence-registry.json"))
    action_results = details.get("action_results", [])
    action_ids = [row.get("action_id") for row in action_results]
    if action_ids != expected_actions or len(action_ids) != len(set(action_ids)):
        add(errors, "event_midflight_action_coverage", f"{label}: expected {expected_actions}")
    for result in action_results:
        action_id = result.get("action_id")
        if result.get("subject_ids") != expected_subjects:
            add(errors, "event_midflight_action_scope", f"{label}: {action_id}")
        if result.get("result") != "pass_to_continue":
            add(errors, "event_midflight_action_result", f"{label}: {action_id}")
        expected_result_digest = object_digest(result, omit=("result_digest",))
        if result.get("result_digest") != expected_result_digest:
            add(errors, "event_midflight_action_digest", f"{label}: {action_id}")
        bindings = result.get("evidence_bindings", [])
        binding_refs = [row.get("ref") for row in bindings if isinstance(row, dict)]
        if len(binding_refs) != len(set(binding_refs)):
            add(errors, "event_midflight_action_evidence_ref", f"{label}: {action_id}")
        for binding in bindings:
            expected_digest = resolve_evidence_binding_digest(binding.get("ref"), evidence)
            if expected_digest is None or binding.get("digest") != expected_digest:
                add(errors, "event_midflight_action_evidence_digest", f"{label}: {action_id}: {binding.get('ref')}")
        checker_ref = result.get("checker_assignment_ref")
        checker = assignment_map.get(checker_ref)
        if checker is None:
            add(errors, "event_midflight_action_checker_ref", f"{label}: {action_id}")
            continue
        if result.get("checker_assignment_digest") != object_digest(checker):
            add(errors, "event_midflight_action_checker_digest", f"{label}: {action_id}")
        if (
            result.get("checker_attempt_id") != checker.get("attempt_id")
            or result.get("checker_actor_instance_id") != checker.get("actor_instance_id")
        ):
            add(errors, "event_midflight_action_checker_attempt", f"{label}: {action_id}")
        requirement = action_requirements.get(action_id)
        if requirement is None:
            add(errors, "event_midflight_action_requirement", f"{label}: {action_id}")
            continue
        if (
            checker.get("role_id") not in requirement.get("required_roles", [])
            or not set(requirement.get("required_capabilities", []))
            <= set(checker.get("capability_ids", []))
            or checker.get("status") in {"blocked", "expired", "revoked"}
            or (runtime_required and checker.get("status") != "qualified_for_unit")
        ):
            add(errors, "event_midflight_action_checker_qualification", f"{label}: {action_id}")
    return errors


def validate_event_ledger(value: dict[str, Any], final: bool) -> list[str]:
    errors = schema_errors(load_data("events/event-ledger.schema.json"), value, "events/event-ledger.json")
    event_schema = load_data("events/marathon-event.schema.json")
    events = value.get("events", [])
    ids = [event.get("event_id") for event in events]
    if len(ids) != len(set(ids)):
        add(errors, "event_id_unique", "event IDs must be unique")
    previous_hash: str | None = None
    previous_time: datetime | None = None
    by_id: dict[str, dict[str, Any]] = {}
    trigger_by_id = {
        row.get("trigger_id"): row
        for row in load_data("firewall/trigger-matrix.yaml").get("triggers", [])
    }
    dependency_graph_path = ROOT / "graph/example-graph.json"
    dependency_graph = load_data("graph/example-graph.json")
    dependency_reverse = dependency_graph.get("reverse_consumer_index", {})
    dependency_node_ids = {
        node.get("node_id")
        for node in dependency_graph.get("nodes", [])
        if isinstance(node.get("node_id"), str)
    }
    dependency_graph_digest = file_digest(dependency_graph_path)
    capability_catalog = load_data("mesh/role-catalog.yaml")
    known_capabilities = {
        capability
        for rows in capability_catalog.get("capability_families", {}).values()
        for capability in rows
    }
    for index, event in enumerate(events, start=1):
        label = event.get("event_id", f"event[{index}]")
        errors.extend(schema_errors(event_schema, event, label))
        if event.get("sequence") != index:
            add(errors, "event_sequence", f"{label}: expected {index}")
        if event.get("event_id") != f"DMV3-EVENT-{index:04d}":
            add(errors, "event_id_sequence", f"{label}: expected DMV3-EVENT-{index:04d}")
        affected = event.get("affected_ids", [])
        if affected != sorted(set(affected)):
            add(errors, "event_affected_ids", f"{label}: affected IDs must be sorted and unique")
        unknown_affected = sorted(set(affected) - dependency_node_ids)
        if unknown_affected:
            add(errors, "event_affected_ref", f"{label}: unknown graph nodes {unknown_affected}")
        if event.get("prior_event_hash") != previous_hash:
            add(errors, "event_prior_hash", f"{label}: expected {previous_hash}")
        expected_hash = object_digest(event, omit=("event_hash",))
        if event.get("event_hash") != expected_hash:
            add(errors, "event_hash", f"{label}: expected {expected_hash}")
        try:
            occurred = parse_time(event.get("occurred_at"))
            if previous_time is not None and occurred < previous_time:
                add(errors, "event_timestamp_order", f"{label}: timestamp regressed")
            previous_time = occurred
        except (TypeError, ValueError) as exc:
            add(errors, "event_timestamp", f"{label}: {exc}")
        previous_hash = event.get("event_hash")
        if isinstance(event.get("event_id"), str):
            by_id[event["event_id"]] = event
    if value.get("event_count") != len(events):
        add(errors, "event_count", f"expected {len(events)}")
    expected_last = events[-1].get("event_hash") if events else None
    if value.get("last_event_hash") != expected_last:
        add(errors, "event_last_hash", f"expected {expected_last}")
    expected_ledger_hash = object_digest(value, omit=("ledger_hash",))
    if value.get("ledger_hash") != expected_ledger_hash:
        add(errors, "event_ledger_hash", f"expected {expected_ledger_hash}")
    generation = value.get("ledger_generation")
    prior_ref = value.get("prior_snapshot")
    if generation == 0 and prior_ref is not None:
        add(errors, "event_prior_snapshot", "generation zero cannot have a prior snapshot")
    if isinstance(generation, int) and generation > 0:
        if not isinstance(prior_ref, dict):
            add(errors, "event_prior_snapshot", "later generations require a prior snapshot")
        else:
            path = resolve_relative(prior_ref.get("ref"))
            if path is None or not path.is_file():
                add(errors, "event_prior_snapshot_ref", str(prior_ref.get("ref")))
            else:
                if prior_ref.get("digest") != file_digest(path):
                    add(errors, "event_prior_snapshot_digest", str(prior_ref.get("ref")))
                prior = json.loads(path.read_text(encoding="utf-8"))
                if prior.get("ledger_generation") + 1 != generation:
                    add(errors, "event_prior_generation", "generation must increment by one")
                if prior_ref.get("ledger_generation") != prior.get("ledger_generation"):
                    add(errors, "event_prior_metadata", "prior generation metadata differs")
                if prior_ref.get("event_count") != prior.get("event_count") or prior_ref.get("last_event_hash") != prior.get("last_event_hash"):
                    add(errors, "event_prior_metadata", "prior count or hash metadata differs")
                prior_events = prior.get("events", [])
                if len(events) < len(prior_events) or events[:len(prior_events)] != prior_events:
                    add(errors, "event_append_only_prefix", "prior event prefix was removed or rewritten")
    for index, event in enumerate(events):
        event_type = event.get("event_type")
        affected = set(event.get("affected_ids", []))
        earlier = events[:index]
        details = event.get("details", {})
        def overlaps(candidate: dict[str, Any], kind: str) -> bool:
            return candidate.get("event_type") == kind and bool(affected & set(candidate.get("affected_ids", [])))
        if event_type == "completeness_entry" and not any(overlaps(row, "work_unit_classified") for row in earlier):
            add(errors, "event_order_entry", f"{event.get('event_id')} lacks prior classification")
        if event_type == "completeness_entry":
            capabilities = details.get("required_capability_ids", [])
            if capabilities != sorted(set(capabilities)) or not set(capabilities) <= known_capabilities:
                add(errors, "event_requirement_capabilities", f"{event.get('event_id')}: {capabilities}")
            expected_requirement_set = object_digest({
                "coverage_input_digest": details.get("coverage_input_digest"),
                "requirement_and_assignment_refs": details.get("requirement_and_assignment_refs"),
                "completeness_assignment_bundle_ref": details.get("completeness_assignment_bundle_ref"),
                "completeness_assignment_bundle_digest": details.get("completeness_assignment_bundle_digest"),
                "completeness_assignment_ref": details.get("completeness_assignment_ref"),
                "completeness_assignment_digest": details.get("completeness_assignment_digest"),
                "required_capability_ids": capabilities,
            })
            if details.get("requirement_set_digest") != expected_requirement_set:
                add(errors, "event_requirement_set_digest", f"{event.get('event_id')}: expected {expected_requirement_set}")
        if event_type in {"role_assigned", "research_started"} and not any(overlaps(row, "completeness_entry") for row in earlier):
            add(errors, "event_order_entry_barrier", f"{event.get('event_id')} lacks prior completeness entry")
        if event_type == "material_trigger":
            trigger_matrix_id = details.get("trigger_matrix_id")
            trigger_definition = trigger_by_id.get(trigger_matrix_id)
            direct_subjects = details.get("direct_subject_ids", [])
            if direct_subjects != sorted(set(direct_subjects)):
                add(errors, "event_trigger_direct_subjects", f"{event.get('event_id')}: direct subjects must be sorted and unique")
            unknown_subjects = sorted(set(direct_subjects) - dependency_node_ids)
            if unknown_subjects:
                add(errors, "event_trigger_subject_ref", f"{event.get('event_id')}: unknown graph subjects {unknown_subjects}")
            expected_closure = sorted(
                set(direct_subjects)
                | reverse_closure(dependency_reverse, direct_subjects)
            )
            if details.get("dependency_graph_ref") != "graph/example-graph.json" or details.get("dependency_graph_digest") != dependency_graph_digest:
                add(errors, "event_trigger_graph_snapshot", f"{event.get('event_id')}: dependency graph identity is stale")
            if details.get("affected_work_and_consumer_ids") != expected_closure or event.get("affected_ids") != expected_closure:
                add(errors, "event_trigger_full_closure", f"{event.get('event_id')}: expected {expected_closure}")
            expected_closure_digest = object_digest(expected_closure)
            if details.get("closure_digest") != expected_closure_digest:
                add(errors, "event_trigger_closure_digest", f"{event.get('event_id')}: expected {expected_closure_digest}")
            expected_actions = sorted(trigger_definition.get("actions", [])) if trigger_definition else []
            if trigger_definition is None or details.get("required_action_ids") != expected_actions:
                add(errors, "event_trigger_required_actions", f"{event.get('event_id')}: expected {expected_actions}")
        if event_type == "completeness_midflight":
            trigger_id = details.get("prior_trigger_event_id")
            trigger = by_id.get(trigger_id)
            if trigger is None or trigger not in earlier or trigger.get("event_type") != "material_trigger":
                add(errors, "event_order_midflight", f"{event.get('event_id')} does not resolve a prior material trigger")
            else:
                trigger_details = trigger.get("details", {})
                expected_subjects = trigger_details.get("affected_work_and_consumer_ids", [])
                expected_actions = trigger_details.get("required_action_ids", [])
                if (
                    event.get("affected_ids") != expected_subjects
                    or details.get("covered_affected_ids") != expected_subjects
                ):
                    add(errors, "event_midflight_full_closure", f"{event.get('event_id')} does not cover the exact trigger closure")
                if details.get("trigger_event_hash") != trigger.get("event_hash"):
                    add(errors, "event_midflight_trigger_hash", f"{event.get('event_id')} does not bind the trigger hash")
                if details.get("fresh_changed_input_digest") != trigger_details.get("changed_input_digest"):
                    add(errors, "event_midflight_changed_input", f"{event.get('event_id')} changed-input digest differs; a new trigger is required")
                if details.get("dependency_graph_digest") != trigger_details.get("dependency_graph_digest"):
                    add(errors, "event_midflight_graph_snapshot", f"{event.get('event_id')} changed dependency snapshot")
                if details.get("closure_digest") != trigger_details.get("closure_digest"):
                    add(errors, "event_midflight_closure_digest", f"{event.get('event_id')} changed closure identity")
                errors.extend(
                    validate_midflight_action_results(
                        event,
                        expected_actions,
                        expected_subjects,
                        final=final,
                        runtime_required=value.get("runtime_events") is True,
                    )
                )
                expected_requirement_digest = object_digest({
                    "trigger_event_hash": trigger.get("event_hash"),
                    "changed_input_digest": trigger_details.get("changed_input_digest"),
                    "dependency_graph_digest": trigger_details.get("dependency_graph_digest"),
                    "closure_digest": trigger_details.get("closure_digest"),
                    "required_action_ids": expected_actions,
                    "action_assignment_bundle_ref": details.get("action_assignment_bundle_ref"),
                    "action_assignment_bundle_digest": details.get("action_assignment_bundle_digest"),
                    "completeness_assignment_bundle_ref": details.get("completeness_assignment_bundle_ref"),
                    "completeness_assignment_bundle_digest": details.get("completeness_assignment_bundle_digest"),
                    "completeness_assignment_ref": details.get("completeness_assignment_ref"),
                    "completeness_assignment_digest": details.get("completeness_assignment_digest"),
                    "required_capability_ids": details.get("required_capability_ids"),
                })
                if details.get("fresh_requirement_set_digest") != expected_requirement_digest:
                    add(errors, "event_midflight_requirement_digest", f"{event.get('event_id')}: expected {expected_requirement_digest}")
                capabilities = details.get("required_capability_ids", [])
                if capabilities != sorted(set(capabilities)) or not set(capabilities) <= known_capabilities:
                    add(errors, "event_requirement_capabilities", f"{event.get('event_id')}: {capabilities}")
        if event_type == "completeness_exit":
            capabilities = details.get("required_capability_ids", [])
            if capabilities != sorted(set(capabilities)) or not set(capabilities) <= known_capabilities:
                add(errors, "event_requirement_capabilities", f"{event.get('event_id')}: {capabilities}")
            expected_exit_requirement_set = object_digest({
                "final_output_digest": details.get("final_output_digest"),
                "independently_rederived_requirements": details.get("independently_rederived_requirements"),
                "discovered_gap_and_replay_refs": details.get("discovered_gap_and_replay_refs"),
                "completeness_assignment_bundle_ref": details.get("completeness_assignment_bundle_ref"),
                "completeness_assignment_bundle_digest": details.get("completeness_assignment_bundle_digest"),
                "completeness_assignment_ref": details.get("completeness_assignment_ref"),
                "completeness_assignment_digest": details.get("completeness_assignment_digest"),
                "required_capability_ids": capabilities,
            })
            if details.get("requirement_set_digest") != expected_exit_requirement_set:
                add(errors, "event_exit_requirement_set_digest", f"{event.get('event_id')}: expected {expected_exit_requirement_set}")
        if event_type in {
            "completeness_entry",
            "completeness_midflight",
            "completeness_exit",
        }:
            errors.extend(
                validate_completeness_assignment_event(
                    event,
                    final,
                    runtime_required=value.get("runtime_events") is True,
                )
            )
        if event_type == "candidate_created":
            if not any(overlaps(row, "completeness_entry") for row in earlier):
                add(errors, "event_order_candidate", f"{event.get('event_id')} lacks prior completeness entry")
        if event_type == "check_completed":
            errors.extend(
                validate_check_completed_event(
                    event, final, earlier_events=earlier
                )
            )
        if event_type in {"role_assigned", "research_started", "candidate_created", "check_completed", "completeness_exit", "checkpoint_frozen", "terminal_handoff"}:
            for trigger in [row for row in earlier if row.get("event_type") == "material_trigger"]:
                trigger_id = trigger.get("event_id")
                matched = any(
                    row.get("event_type") == "completeness_midflight"
                    and row.get("details", {}).get("prior_trigger_event_id") == trigger_id
                    and row.get("affected_ids") == trigger.get("affected_ids")
                    and row.get("details", {}).get("covered_affected_ids") == trigger.get("affected_ids")
                    and row.get("details", {}).get("fresh_changed_input_digest") == trigger.get("details", {}).get("changed_input_digest")
                    for row in earlier
                )
                if not matched:
                    add(errors, "event_unmatched_trigger", f"{event.get('event_id')} continues past {trigger_id}")
        if event_type == "checkpoint_frozen" and not any(row.get("event_type") == "completeness_exit" for row in earlier):
            add(errors, "event_order_checkpoint", f"{event.get('event_id')} lacks completeness exit")
        if event_type == "terminal_handoff":
            if not any(row.get("event_type") == "checkpoint_frozen" for row in earlier):
                add(errors, "event_order_terminal", f"{event.get('event_id')} lacks frozen checkpoint")
            if index != len(events) - 1:
                add(errors, "event_terminal_last", f"{event.get('event_id')} must be the final event")
    if final and value.get("ledger_hash") == ZERO_DIGEST:
        add(errors, "event_placeholder_digest", "ledger hash remains a placeholder")
    errors.extend(
        validate_correlation_acceptance_reachability(
            value,
            load_data("mesh/qualification-registry.json"),
            load_data("graph/authority-registry.yaml"),
        )
    )
    return errors


def evidence_maps(value: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    return {
        "source-record": {row.get("source_record_id"): row for row in value.get("source_records", [])},
        "translation-lineage": {row.get("translation_lineage_id"): row for row in value.get("translation_lineages", [])},
        "influence-hypothesis": {row.get("hypothesis_id"): row for row in value.get("influence_hypotheses", [])},
        "historical-attribution": {row.get("attribution_id"): row for row in value.get("historical_attributions", [])},
        "claim-record": {row.get("claim_id"): row for row in value.get("claim_records", [])},
        "evidence-review": {row.get("receipt_id"): row for row in value.get("evidence_review_receipts", [])},
    }


def split_typed_ref(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, str) or ":" not in value:
        return None
    kind, identifier = value.split(":", 1)
    return kind, identifier


def source_qualification_scope_digest(value: dict[str, Any]) -> str:
    return object_digest({
        key: value.get(key)
        for key in (
            "source_record_id", "revision", "source_kind", "root_or_derivative",
            "title", "creator_or_custodian", "edition_or_witness_id",
            "stable_locator_uri", "root_source_access", "identity_state",
            "rights_state", "content_digest", "observed_at",
        )
    })


def evidence_review_scope_digest(value: dict[str, Any], kind: str) -> str:
    excluded = {
        "translation-lineage": {
            "review_scope_digest", "specialist_review_receipt_refs",
            "specialist_review_receipt_digests", "human_approval_receipt_ref",
            "human_approval_receipt_digest", "status", "lineage_digest",
        },
        "influence-hypothesis": {
            "review_scope_digest", "specialist_review_receipt_refs",
            "specialist_review_receipt_digests", "status", "hypothesis_digest",
        },
        "historical-attribution": {
            "review_scope_digest", "review_receipt_refs", "review_receipt_digests",
            "review_state", "attribution_digest",
        },
        "claim-record": {
            "review_receipt_refs", "review_receipt_digests", "claim_state",
            "evidence_digest",
        },
    }[kind]
    return object_digest({key: item for key, item in value.items() if key not in excluded})


EVIDENCE_OBJECT_DIGEST_FIELDS = {
    "source-record": "record_digest",
    "translation-lineage": "lineage_digest",
    "influence-hypothesis": "hypothesis_digest",
    "historical-attribution": "attribution_digest",
    "claim-record": "evidence_digest",
    "evidence-review": "receipt_digest",
}


def resolve_evidence_binding_digest(
    ref: Any,
    maps: dict[str, dict[str, dict[str, Any]]],
) -> str | None:
    parsed = split_typed_ref(ref)
    if parsed and parsed[0] in EVIDENCE_OBJECT_DIGEST_FIELDS:
        row = maps.get(parsed[0], {}).get(parsed[1])
        return row.get(EVIDENCE_OBJECT_DIGEST_FIELDS[parsed[0]]) if row else None
    path = resolve_relative(ref)
    return file_digest(path) if path is not None and path.is_file() else None


def _resolved_evidence_reviews(
    errors: list[str],
    *,
    refs: list[Any],
    digests: list[Any],
    maps: dict[str, dict[str, dict[str, Any]]],
    review_kind: str,
    subject_ref: str,
    subject_scope_digest: str,
    label: str,
) -> list[dict[str, Any]]:
    if len(refs) != len(digests):
        add(errors, "evidence_review_pairs", f"{label}: refs and digests differ")
        return []
    results: list[dict[str, Any]] = []
    role_catalog = load_data("mesh/role-catalog.yaml")
    review_capability_requirements = role_catalog.get(
        "evidence_review_capability_requirements", {}
    )
    for ref, digest in zip(refs, digests):
        parsed = split_typed_ref(ref)
        receipt = maps["evidence-review"].get(parsed[1]) if parsed and parsed[0] == "evidence-review" else None
        if receipt is None:
            add(errors, "evidence_review_ref", f"{label}: {ref}")
            continue
        if digest != receipt.get("receipt_digest"):
            add(errors, "evidence_review_digest", f"{label}: {ref}")
        if (
            receipt.get("review_kind") != review_kind
            or receipt.get("subject_ref") != subject_ref
            or receipt.get("subject_scope_digest") != subject_scope_digest
            or receipt.get("decision") not in {"accepted", "qualified"}
            or receipt.get("authority_effect") != "none"
            or receipt.get("independence_assessment") == "blocked"
        ):
            add(errors, "evidence_review_scope", f"{label}: {ref}")
        bundle_path = resolve_relative(receipt.get("assignment_bundle_ref"))
        if bundle_path is None or not bundle_path.is_file():
            add(errors, "evidence_review_assignment_bundle", f"{label}: {ref}")
        else:
            if receipt.get("assignment_bundle_digest") != file_digest(bundle_path):
                add(errors, "evidence_review_assignment_bundle_digest", f"{label}: {ref}")
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            try:
                review_use_at = parse_time(receipt.get("issued_at"))
            except (TypeError, ValueError):
                review_use_at = None
            bundle_errors = validate_role_assignments(
                bundle,
                load_data("mesh/agent-mesh.v3.json"),
                final=False,
                use_at=review_use_at,
            )
            if bundle_errors:
                add(
                    errors,
                    "evidence_review_assignment_bundle_validation",
                    f"{label}: {ref}: {bundle_errors[0]}",
                )
            assignment_map = {
                f"role-assignment:{row.get('assignment_id')}": row
                for row in bundle.get("assignments", [])
            }
            producer_ref = receipt.get("producer_assignment_ref")
            producer = assignment_map.get(producer_ref)
            if producer is None:
                add(errors, "evidence_review_producer_ref", f"{label}: {producer_ref}")
            else:
                if receipt.get("producer_assignment_digest") != object_digest(producer):
                    add(errors, "evidence_review_producer_digest", f"{label}: {producer_ref}")
                if (
                    producer.get("work_unit_id") != receipt.get("work_unit_id")
                    or producer.get("status") != "qualified_for_unit"
                ):
                    add(errors, "evidence_review_producer_ref", f"{label}: producer is not qualified for the work unit")
            if bundle.get("fixture_kind") != "runtime_receipt" or bundle.get("runtime_assignments") is not True:
                add(errors, "evidence_review_design_fixture", f"{label}: {ref}")
            reviewer_refs = receipt.get("reviewer_assignment_refs", [])
            reviewers = [assignment_map.get(reviewer_ref) for reviewer_ref in reviewer_refs]
            if producer_ref in reviewer_refs:
                add(errors, "evidence_review_producer_independence", f"{label}: producer is a reviewer")
            if len(reviewer_refs) < 2 or any(reviewer is None for reviewer in reviewers):
                add(errors, "evidence_review_reviewer_qualification", f"{label}: exact reviewer set is unresolved")
            else:
                typed_reviewers = [reviewer for reviewer in reviewers if isinstance(reviewer, dict)]
                if any(
                    reviewer.get("status") != "qualified_for_unit"
                    or reviewer.get("work_unit_id") != receipt.get("work_unit_id")
                    for reviewer in typed_reviewers
                ):
                    add(errors, "evidence_review_reviewer_qualification", f"{label}: one or more reviewers are not qualified")
                if len({reviewer.get("actor_instance_id") for reviewer in typed_reviewers}) != len(typed_reviewers):
                    add(errors, "evidence_review_actor_independence", label)
                if len({reviewer.get("attempt_id") for reviewer in typed_reviewers}) != len(typed_reviewers):
                    add(errors, "evidence_review_attempt_independence", label)
                if producer is not None and any(
                    producer.get("assignment_id")
                    not in reviewer.get("checks_assignment_ids", [])
                    for reviewer in typed_reviewers
                ):
                    add(errors, "evidence_review_producer_independence", f"{label}: reviewer does not check producer")
                capabilities = {
                    capability
                    for reviewer in typed_reviewers
                    for capability in reviewer.get("capability_ids", [])
                }
                observed_required_capabilities = receipt.get("required_capability_ids", [])
                required_capabilities = set(observed_required_capabilities)
                expected_required_capabilities = set(
                    review_capability_requirements.get(receipt.get("review_kind"), [])
                )
                if (
                    required_capabilities != expected_required_capabilities
                    or len(observed_required_capabilities) != len(required_capabilities)
                ):
                    add(
                        errors,
                        "evidence_review_required_capabilities",
                        f"{label}: expected {sorted(expected_required_capabilities)}",
                    )
                if not required_capabilities <= capabilities:
                    add(errors, "evidence_review_capability_coverage", f"{label}: {sorted(required_capabilities - capabilities)}")
        bindings = receipt.get("evidence_bindings", [])
        binding_refs = [binding.get("ref") for binding in bindings if isinstance(binding, dict)]
        if len(binding_refs) != len(set(binding_refs)):
            add(errors, "evidence_review_binding_ref", f"{label}: duplicate evidence binding")
        subject_binding = {
            "ref": subject_ref,
            "digest": subject_scope_digest,
        }
        if subject_binding not in bindings:
            add(errors, "evidence_review_subject_binding", f"{label}: {subject_ref}")
        for binding in bindings:
            expected_binding_digest = (
                subject_scope_digest
                if binding.get("ref") == subject_ref
                else resolve_evidence_binding_digest(binding.get("ref"), maps)
            )
            if expected_binding_digest is None or binding.get("digest") != expected_binding_digest:
                add(errors, "evidence_review_binding", f"{label}: {binding.get('ref')}")
        try:
            issued = parse_time(receipt.get("issued_at"))
            expires = receipt.get("expires_at")
            if expires is not None and parse_time(expires) <= issued:
                add(errors, "evidence_review_expiry", f"{label}: {ref}")
        except (TypeError, ValueError) as exc:
            add(errors, "evidence_review_time", f"{label}: {exc}")
        if receipt.get("independence_assessment") == "correlated_disclosed":
            parsed_acceptance = split_typed_ref(receipt.get("correlation_acceptance_receipt_ref"))
            acceptance = None
            if parsed_acceptance and parsed_acceptance[0] == "correlation-acceptance":
                qualification_registry = load_data("mesh/qualification-registry.json")
                acceptance = next((
                    row
                    for row in qualification_registry.get("correlation_acceptance_receipts", [])
                    if row.get("receipt_id") == parsed_acceptance[1]
                ), None)
            if acceptance is None:
                add(errors, "evidence_review_correlation_acceptance", f"{label}: {ref}")
            else:
                authority = load_data("graph/authority-registry.yaml")
                acceptance_errors = validate_correlation_acceptance_authority(
                    acceptance, authority, label=str(acceptance.get("receipt_id"))
                )
                if acceptance_errors:
                    add(errors, "evidence_review_correlation_acceptance", f"{label}: {acceptance_errors[0]}")
        elif receipt.get("correlation_acceptance_receipt_ref") is not None:
            add(errors, "evidence_review_false_correlation", f"{label}: {ref}")
        results.append(receipt)
    return results


def validate_evidence_registry(value: dict[str, Any], final: bool) -> list[str]:
    errors = schema_errors(load_data("evidence/evidence-registry.schema.json"), value, "evidence/evidence-registry.json")
    schemas = {
        "source_records": ("source_record_id", load_data("evidence/source-record.schema.json"), "record_digest"),
        "translation_lineages": ("translation_lineage_id", load_data("evidence/translation-lineage.schema.json"), "lineage_digest"),
        "influence_hypotheses": ("hypothesis_id", load_data("graph/influence-hypothesis.schema.json"), "hypothesis_digest"),
        "historical_attributions": ("attribution_id", load_data("graph/historical-attribution.schema.json"), "attribution_digest"),
        "claim_records": ("claim_id", load_data("evidence/claim-record.schema.json"), "evidence_digest"),
        "evidence_review_receipts": ("receipt_id", load_data("evidence/evidence-review-receipt.schema.json"), "receipt_digest"),
    }
    maps = evidence_maps(value)
    for collection, (id_field, schema, digest_field) in schemas.items():
        rows = value.get(collection, [])
        ids = [row.get(id_field) for row in rows]
        if len(ids) != len(set(ids)):
            add(errors, "evidence_duplicate_id", collection)
        for row in rows:
            errors.extend(schema_errors(schema, row, str(row.get(id_field))))
            if digest_field:
                expected = object_digest(row, omit=(digest_field,))
                if row.get(digest_field) != expected:
                    add(errors, "evidence_object_digest", f"{row.get(id_field)} expected {expected}")
    sources = maps["source-record"]
    for source in value.get("source_records", []):
        scope_digest = source_qualification_scope_digest(source)
        if source.get("qualification_scope_digest") != scope_digest:
            add(errors, "source_qualification_scope_digest", str(source.get("source_record_id")))
        reviews = _resolved_evidence_reviews(
            errors,
            refs=source.get("qualification_receipt_refs", []),
            digests=source.get("qualification_receipt_digests", []),
            maps=maps,
            review_kind="source_qualification",
            subject_ref=f"source-record:{source.get('source_record_id')}",
            subject_scope_digest=scope_digest,
            label=str(source.get("source_record_id")),
        )
        if source.get("qualifies_for_load_bearing") is True and not reviews:
            add(errors, "source_qualification_receipt", str(source.get("source_record_id")))
    for lineage in value.get("translation_lineages", []):
        parsed = split_typed_ref(lineage.get("source_record_ref"))
        source = sources.get(parsed[1]) if parsed and parsed[0] == "source-record" else None
        if source is None:
            add(errors, "translation_source_ref", str(lineage.get("translation_lineage_id")))
        else:
            if lineage.get("source_record_digest") != source.get("content_digest") or lineage.get("source_record_object_digest") != source.get("record_digest"):
                add(errors, "translation_source_digest", str(lineage.get("translation_lineage_id")))
        scope_digest = evidence_review_scope_digest(lineage, "translation-lineage")
        if lineage.get("review_scope_digest") != scope_digest:
            add(errors, "translation_review_scope_digest", str(lineage.get("translation_lineage_id")))
        reviews = _resolved_evidence_reviews(
            errors,
            refs=lineage.get("specialist_review_receipt_refs", []),
            digests=lineage.get("specialist_review_receipt_digests", []),
            maps=maps,
            review_kind="translation_fidelity",
            subject_ref=f"translation-lineage:{lineage.get('translation_lineage_id')}",
            subject_scope_digest=scope_digest,
            label=str(lineage.get("translation_lineage_id")),
        )
        if lineage.get("status") in {"specialist_reviewed", "human_approved"} and not reviews:
            add(errors, "translation_specialist_receipt", str(lineage.get("translation_lineage_id")))
    for hypothesis in value.get("influence_hypotheses", []):
        for ref in hypothesis.get("qualified_source_record_refs", []):
            parsed = split_typed_ref(ref)
            source = sources.get(parsed[1]) if parsed and parsed[0] == "source-record" else None
            if source is None or source.get("qualifies_for_load_bearing") is not True:
                add(errors, "influence_unqualified_source", f"{hypothesis.get('hypothesis_id')}: {ref}")
        scope_digest = evidence_review_scope_digest(hypothesis, "influence-hypothesis")
        if hypothesis.get("review_scope_digest") != scope_digest:
            add(errors, "influence_review_scope_digest", str(hypothesis.get("hypothesis_id")))
        reviews = _resolved_evidence_reviews(
            errors,
            refs=hypothesis.get("specialist_review_receipt_refs", []),
            digests=hypothesis.get("specialist_review_receipt_digests", []),
            maps=maps,
            review_kind="influence_hypothesis",
            subject_ref=f"influence-hypothesis:{hypothesis.get('hypothesis_id')}",
            subject_scope_digest=scope_digest,
            label=str(hypothesis.get("hypothesis_id")),
        )
        if hypothesis.get("status") == "human_reviewed" and not reviews:
            add(errors, "influence_specialist_receipt", str(hypothesis.get("hypothesis_id")))
    for attribution in value.get("historical_attributions", []):
        errors.extend(validate_historical_attribution(attribution, sources))
        scope_digest = evidence_review_scope_digest(attribution, "historical-attribution")
        if attribution.get("review_scope_digest") != scope_digest:
            add(errors, "historical_review_scope_digest", str(attribution.get("attribution_id")))
        reviews = _resolved_evidence_reviews(
            errors,
            refs=attribution.get("review_receipt_refs", []),
            digests=attribution.get("review_receipt_digests", []),
            maps=maps,
            review_kind="historical_attribution",
            subject_ref=f"historical-attribution:{attribution.get('attribution_id')}",
            subject_scope_digest=scope_digest,
            label=str(attribution.get("attribution_id")),
        )
        if attribution.get("review_state") == "specialist_reviewed" and not reviews:
            add(errors, "historical_specialist_receipt", str(attribution.get("attribution_id")))
    for claim in value.get("claim_records", []):
        claim_id = str(claim.get("claim_id"))
        bindings = {row.get("source_record_ref"): row for row in claim.get("source_bindings", [])}
        if set(bindings) != set(claim.get("source_record_refs", [])) or len(bindings) != len(claim.get("source_bindings", [])):
            add(errors, "claim_source_bindings", claim_id)
        for ref in claim.get("source_record_refs", []):
            parsed = split_typed_ref(ref)
            source = sources.get(parsed[1]) if parsed and parsed[0] == "source-record" else None
            if source is None:
                add(errors, "claim_source_ref", f"{claim.get('claim_id')}: {ref}")
            elif claim.get("claim_state") == "verified" and source.get("qualifies_for_load_bearing") is not True:
                add(errors, "claim_unqualified_source", f"{claim.get('claim_id')}: {ref}")
            binding = bindings.get(ref, {})
            if source is not None and (
                binding.get("source_content_digest") != source.get("content_digest")
                or binding.get("source_record_digest") != source.get("record_digest")
                or not set(binding.get("exact_locator_refs", [])) <= set(claim.get("exact_locator_refs", []))
            ):
                add(errors, "claim_source_binding_digest", f"{claim_id}: {ref}")
        for field, digest_field, kind, object_digest_field in (
            ("translation_lineage_ref", "translation_lineage_digest", "translation-lineage", "lineage_digest"),
            ("influence_hypothesis_ref", "influence_hypothesis_digest", "influence-hypothesis", "hypothesis_digest"),
            ("historical_attribution_ref", "historical_attribution_digest", "historical-attribution", "attribution_digest"),
        ):
            ref = claim.get(field)
            if ref is not None:
                parsed = split_typed_ref(ref)
                upstream = maps[kind].get(parsed[1]) if parsed and parsed[0] == kind else None
                if upstream is None:
                    add(errors, "claim_lineage_ref", f"{claim.get('claim_id')}: {field}")
                elif claim.get(digest_field) != upstream.get(object_digest_field):
                    add(errors, "claim_lineage_digest", f"{claim_id}: {field}")
        if claim.get("claim_state") == "verified":
            scope_digest = evidence_review_scope_digest(claim, "claim-record")
            reviews = _resolved_evidence_reviews(
                errors,
                refs=claim.get("review_receipt_refs", []),
                digests=claim.get("review_receipt_digests", []),
                maps=maps,
                review_kind="claim_entailment_context",
                subject_ref=f"claim-record:{claim.get('claim_id')}",
                subject_scope_digest=scope_digest,
                label=claim_id,
            )
            if not reviews:
                add(errors, "claim_review_receipt", claim_id)
            dimensions = claim.get("status_dimensions", {})
            required_dimensions = {
                "source_identity": "qualified",
                "source_fitness": "qualified",
                "rights_and_access": "qualified",
                "locator_validity": "verified",
                "context_integrity": "verified",
                "entailment": "verified",
                "human_review": "completed",
            }
            if any(dimensions.get(field) != expected for field, expected in required_dimensions.items()):
                add(errors, "claim_verified_dimensions", claim_id)
            claim_type = claim.get("claim_type")
            if claim_type == "translation":
                parsed = split_typed_ref(claim.get("translation_lineage_ref"))
                lineage = maps["translation-lineage"].get(parsed[1]) if parsed and parsed[0] == "translation-lineage" else None
                if lineage is None or lineage.get("status") not in {"specialist_reviewed", "human_approved"} or dimensions.get("translation_fidelity") != "specialist_reviewed":
                    add(errors, "claim_verified_translation", claim_id)
            if claim_type == "influence_or_causation":
                parsed = split_typed_ref(claim.get("influence_hypothesis_ref"))
                hypothesis = maps["influence-hypothesis"].get(parsed[1]) if parsed and parsed[0] == "influence-hypothesis" else None
                if hypothesis is None or hypothesis.get("status") != "human_reviewed" or dimensions.get("causal_or_influence_support") != "specialist_reviewed":
                    add(errors, "claim_verified_influence", claim_id)
            if claim_type == "historical_attribution":
                parsed = split_typed_ref(claim.get("historical_attribution_ref"))
                attribution = maps["historical-attribution"].get(parsed[1]) if parsed and parsed[0] == "historical-attribution" else None
                if attribution is None or attribution.get("review_state") != "specialist_reviewed":
                    add(errors, "claim_verified_historical", claim_id)
            if claim_type == "normative_assessment":
                authority = load_data("graph/authority-registry.yaml")
                parsed = split_typed_ref(claim.get("normative_frame_ref"))
                frame = next((row for row in authority.get("normative_frames", []) if parsed and parsed[0] == "normative-frame" and row.get("frame_id") == parsed[1]), None)
                if (
                    frame is None
                    or authority.get("normative_authority_active") is not True
                    or authority.get("current_normative_frame_ref") != claim.get("normative_frame_ref")
                    or claim.get("normative_frame_digest") != frame.get("frame_digest")
                    or dimensions.get("normative_admissibility") != "human_frame_verified"
                ):
                    add(errors, "claim_verified_normative", claim_id)
    expected_registry = object_digest(value, omit=("registry_digest",))
    if value.get("registry_digest") != expected_registry:
        add(errors, "evidence_registry_digest", f"expected {expected_registry}")
    if final and value.get("registry_digest") == ZERO_DIGEST:
        add(errors, "evidence_placeholder_digest", "registry hash remains a placeholder")
    return errors


def validate_authority_registry(value: dict[str, Any], final: bool) -> list[str]:
    errors = schema_errors(load_data("graph/authority-registry.schema.json"), value, "graph/authority-registry.yaml")
    root_ref = value.get("human_identity_authority_root_ref")
    root_path = resolve_relative(root_ref)
    identity_root: dict[str, Any] = {}
    if root_path is None or not root_path.is_file():
        add(errors, "authority_identity_root_ref", str(root_ref))
    else:
        identity_root = yaml.safe_load(root_path.read_text(encoding="utf-8"))
        errors.extend(
            schema_errors(
                load_data("graph/human-identity-authority-root.schema.json"),
                identity_root,
                str(root_ref),
            )
        )
        if value.get("human_identity_authority_root_file_digest") != file_digest(root_path):
            add(errors, "authority_identity_root_file_digest", str(root_ref))
        expected_anchor = object_digest(identity_root, omit=("anchor_digest",))
        if (
            identity_root.get("anchor_digest") != expected_anchor
            or value.get("human_identity_authority_root_anchor_digest") != expected_anchor
        ):
            add(errors, "authority_identity_root_anchor_digest", f"expected {expected_anchor}")
        if identity_root.get("active") is True:
            add(
                errors,
                "authority_identity_root_activation_unimplemented",
                "V3 deliberately has no deterministic human-identity activation mechanism; activation requires a separately reviewed control revision",
            )
    qualification_rows = value.get("approver_qualification_receipts", [])
    qualification_map = {row.get("receipt_id"): row for row in qualification_rows}
    if len(qualification_map) != len(qualification_rows):
        add(errors, "authority_qualification_receipt_id", "qualification receipt IDs must be unique")
    for receipt in qualification_rows:
        receipt_id = str(receipt.get("receipt_id"))
        expected_receipt = object_digest(receipt, omit=("receipt_digest",))
        if receipt.get("receipt_digest") != expected_receipt:
            add(errors, "authority_qualification_receipt_digest", f"{receipt_id}: expected {expected_receipt}")
        if (
            identity_root.get("active") is not True
            or identity_root.get("recorded_by_human") is not True
            or identity_root.get("created_by_ai") is not False
            or receipt.get("identity_root_anchor_digest") != identity_root.get("anchor_digest")
            or receipt.get("protected_commit") != identity_root.get("protected_commit")
            or receipt.get("issuer_id") not in identity_root.get("authorized_identity_issuer_ids", [])
            or receipt.get("signer_id") not in identity_root.get("authorized_signer_ids", [])
            or receipt.get("recorded_by_human") is not True
            or receipt.get("created_by_ai") is not False
        ):
            add(errors, "authority_qualification_identity_root", receipt_id)
        for binding in receipt.get("evidence_bindings", []):
            evidence_path = resolve_relative(binding.get("ref"))
            if (
                evidence_path is None
                or not evidence_path.is_file()
                or binding.get("digest") != file_digest(evidence_path)
            ):
                add(errors, "authority_qualification_evidence_binding", f"{receipt_id}: {binding.get('ref')}")
        try:
            issued = parse_time(receipt.get("issued_at"))
            expires = receipt.get("expires_at")
            if expires is not None and parse_time(expires) <= issued:
                add(errors, "authority_qualification_time", receipt_id)
        except (TypeError, ValueError) as exc:
            add(errors, "authority_qualification_time", f"{receipt_id}: {exc}")
    approvers = value.get("qualified_approvers", [])
    ids = [row.get("signer_id") for row in approvers]
    if len(ids) != len(set(ids)):
        add(errors, "authority_duplicate_signer", "qualified signer IDs must be unique")
    expected_approvers = object_digest(approvers)
    if value.get("approver_set_digest") != expected_approvers:
        add(errors, "authority_approver_set_digest", f"expected {expected_approvers}")
    if approvers and identity_root.get("active") is not True:
        add(errors, "authority_identity_root_inactive", "qualified approvers require an active human-recorded root")
    for approver in approvers:
        parsed_qualification = split_typed_ref(approver.get("qualification_receipt_ref"))
        qualification = (
            qualification_map.get(parsed_qualification[1])
            if parsed_qualification and parsed_qualification[0] == "approver-qualification"
            else None
        )
        if qualification is None:
            add(errors, "authority_approver_qualification_ref", str(approver.get("signer_id")))
            continue
        if approver.get("qualification_receipt_digest") != qualification.get("receipt_digest"):
            add(errors, "authority_approver_qualification_digest", str(approver.get("signer_id")))
        if (
            qualification.get("signer_id") != approver.get("signer_id")
            or set(qualification.get("qualification_scope", []))
            != set(approver.get("qualification_scope", []))
            or qualification.get("tradition_or_jurisdiction")
            != approver.get("tradition_or_jurisdiction")
            or qualification.get("issued_at") != approver.get("valid_from")
            or qualification.get("expires_at") != approver.get("valid_until")
        ):
            add(errors, "authority_approver_qualification_scope", str(approver.get("signer_id")))
    receipt_rows = value.get("human_decision_receipts", [])
    frame_rows = value.get("normative_frames", [])
    receipt_map = {row.get("receipt_id"): row for row in receipt_rows}
    frame_map = {row.get("frame_id"): row for row in frame_rows}
    if len(receipt_map) != len(receipt_rows) or len(frame_map) != len(frame_rows):
        add(errors, "authority_embedded_id", "human decision and frame IDs must be unique")
    for receipt in receipt_rows:
        errors.extend(validate_human_decision_receipt(receipt, value))
    for frame in frame_rows:
        errors.extend(validate_normative_frame(frame, value, receipt_map))
    expected_registry = object_digest(value, omit=("registry_digest",))
    if value.get("registry_digest") != expected_registry:
        add(errors, "authority_registry_digest", f"expected {expected_registry}")
    if value.get("normative_authority_active") is False:
        if frame_rows or value.get("current_normative_frame_ref") is not None or value.get("current_normative_frame_digest") is not None:
            add(errors, "authority_unapproved_normative_activation", "inactive normative authority cannot expose a frame")
        if any(
            row.get("decision_type") == "normative_frame_approval"
            and row.get("decision") == "approved"
            for row in receipt_rows
        ):
            add(errors, "authority_normative_inactive", "an approved normative frame decision cannot remain hidden in an inactive registry")
    elif value.get("normative_authority_active") is not True:
        add(errors, "authority_normative_state", "normative authority state must be explicit")
    if final and value.get("metadata", {}).get("lifecycle_status") == "specification_only":
        if approvers or receipt_rows or frame_rows or value.get("normative_authority_active") is not False:
            add(errors, "authority_specification_nonactivation", "the frozen design-time registry must remain empty and non-authorizing")
    if final and (value.get("approver_set_digest") == ZERO_DIGEST or value.get("registry_digest") == ZERO_DIGEST):
        add(errors, "authority_placeholder_digest", "authority registry contains a placeholder digest")
    return errors


def validate_historical_attribution(value: dict[str, Any], source_records: dict[str, dict[str, Any]]) -> list[str]:
    errors = schema_errors(load_data("graph/historical-attribution.schema.json"), value, "historical attribution")
    if str(value.get("label_used", "")).strip().lower() in {"liberal theology", "conservative theology"}:
        add(errors, "historical_generic_label", str(value.get("label_used")))
    if str(value.get("actor_or_community", "")).strip().lower() in {"the church", "the jews", "christians", "jews"}:
        add(errors, "historical_generic_actor", str(value.get("actor_or_community")))
    if str(value.get("exact_locator", "")).strip().lower() in {"n/a", "na", "none", "unknown", "unavailable"}:
        add(errors, "historical_invalid_locator", str(value.get("exact_locator")))
    parsed = split_typed_ref(value.get("source_record_ref"))
    source = source_records.get(parsed[1]) if parsed and parsed[0] == "source-record" else None
    if source is None or source.get("qualifies_for_load_bearing") is not True:
        add(errors, "historical_unqualified_source", str(value.get("source_record_ref")))
    elif value.get("source_record_digest") != source.get("record_digest"):
        add(errors, "historical_source_digest", str(value.get("source_record_ref")))
    return errors


def validate_human_decision_receipt(value: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    errors = schema_errors(load_data("graph/human-decision-receipt.schema.json"), value, "human decision receipt")
    expected = object_digest(value, omit=("receipt_digest",))
    if value.get("receipt_digest") != expected:
        add(errors, "human_decision_digest", f"expected {expected}")
    if value.get("signer_registry_digest") != registry.get("approver_set_digest"):
        add(errors, "human_decision_registry_digest", "signer registry digest mismatch")
    approver_map = {row.get("signer_id"): row for row in registry.get("qualified_approvers", [])}
    allowed = set(approver_map)
    if not set(value.get("signer_ids", [])) <= allowed:
        add(errors, "human_decision_signer", "one or more signers are not qualified in the bound registry")
    if value.get("decision_type") != "normative_frame_approval" and any(
        str(scope).startswith(("normative_frame:", "normative_authority:"))
        for scope in value.get("authority_scope", [])
    ):
        add(errors, "human_decision_scope_escalation", "a non-normative decision claims normative authority")
    attestation_bindings = value.get("attestation_bindings", [])
    attestation_refs = [row.get("ref") for row in attestation_bindings if isinstance(row, dict)]
    if len(attestation_refs) != len(set(attestation_refs)):
        add(errors, "human_decision_attestation_ref", "attestation refs must be unique")
    for binding in attestation_bindings:
        attestation_path = resolve_relative(binding.get("ref"))
        if (
            attestation_path is None
            or not attestation_path.is_file()
            or binding.get("digest") != file_digest(attestation_path)
        ):
            add(errors, "human_decision_attestation_binding", str(binding.get("ref")))
    try:
        issued = parse_time(value.get("issued_at"))
        expires_raw = value.get("expires_at")
        if expires_raw is not None and parse_time(expires_raw) <= issued:
            add(errors, "human_decision_expiry", "expiry must follow issuance")
        for signer_id in value.get("signer_ids", []):
            approver = approver_map.get(signer_id)
            if approver is None:
                continue
            valid_from = parse_time(approver.get("valid_from"))
            valid_until_raw = approver.get("valid_until")
            if (
                value.get("decision_type") not in approver.get("qualification_scope", [])
                or approver.get("tradition_or_jurisdiction") != value.get("tradition_or_jurisdiction")
                or issued < valid_from
                or (valid_until_raw is not None and issued > parse_time(valid_until_raw))
            ):
                add(errors, "human_decision_signer_qualification", str(signer_id))
    except (TypeError, ValueError) as exc:
        add(errors, "human_decision_time", str(exc))
    return errors


def normative_scope_digest(value: dict[str, Any]) -> str:
    return object_digest({
        "frame_id": value.get("frame_id"),
        "revision": value.get("revision"),
        "tradition_or_jurisdiction": value.get("tradition_or_jurisdiction"),
        "canon_scope": value.get("canon_scope"),
        "admitted_authorities": value.get("admitted_authorities"),
        "interpretive_policy_ref": value.get("interpretive_policy_ref"),
    })


def completion_scope_digest(value: dict[str, Any]) -> str:
    """Digest only the human-approved campaign-completion scope, without circular receipt fields."""
    return object_digest({
        "definition_id": value.get("definition_id"),
        "required_horizon_ids": value.get("required_horizon_ids"),
        "required_work_unit_ids": value.get("required_work_unit_ids"),
        "required_claim_ids": value.get("required_claim_ids"),
        "required_output_classes": value.get("required_output_classes"),
        "permitted_residual_risk_classes": value.get("permitted_residual_risk_classes"),
        "effective_at": value.get("effective_at"),
        "expires_at": value.get("expires_at"),
    })


def validate_normative_frame(value: dict[str, Any], registry: dict[str, Any], receipts: dict[str, dict[str, Any]]) -> list[str]:
    errors = schema_errors(load_data("graph/normative-frame.schema.json"), value, "normative frame")
    expected_scope = normative_scope_digest(value)
    if value.get("scope_digest") != expected_scope:
        add(errors, "normative_scope_digest", f"expected {expected_scope}")
    expected_frame = object_digest(value, omit=("frame_digest",))
    if value.get("frame_digest") != expected_frame:
        add(errors, "normative_frame_digest", f"expected {expected_frame}")
    if value.get("authority_registry_digest") != registry.get("approver_set_digest"):
        add(errors, "normative_registry_digest", "frame is not bound to the qualified approver set")
    parsed = split_typed_ref(value.get("human_approval_receipt_ref"))
    receipt = receipts.get(parsed[1]) if parsed and parsed[0] == "human-decision" else None
    if receipt is None:
        add(errors, "normative_receipt_ref", str(value.get("human_approval_receipt_ref")))
    else:
        errors.extend(validate_human_decision_receipt(receipt, registry))
        if value.get("human_approval_receipt_digest") != receipt.get("receipt_digest"):
            add(errors, "normative_receipt_digest", "approval receipt digest mismatch")
        if receipt.get("decision_type") != "normative_frame_approval" or receipt.get("decision") != "approved":
            add(errors, "normative_receipt_decision", "receipt is not an approval of a NormativeFrame")
        if receipt.get("subject_digest") != value.get("scope_digest") or receipt.get("scope_digest") != value.get("scope_digest"):
            add(errors, "normative_receipt_scope", "receipt does not bind the frame scope")
        if set(receipt.get("signer_ids", [])) != set(value.get("approved_by", [])):
            add(errors, "normative_receipt_signers", "frame and receipt signer sets differ")
    if registry.get("normative_authority_active") is not True:
        add(errors, "normative_registry_inactive", "no active normative authority is registered")
    if registry.get("current_normative_frame_ref") != f"normative-frame:{value.get('frame_id')}" or registry.get("current_normative_frame_digest") != value.get("frame_digest"):
        add(errors, "normative_registry_frame", "frame is not the exact active registry frame")
    return errors


def validate_jewish_context_pack(value: dict[str, Any]) -> list[str]:
    errors = schema_errors(load_data("research/jewish-context-pack.schema.json"), value, "Jewish context pack")
    if str(value.get("community_display", "")).strip().lower() in {"the jews", "jews", "ancient jews", "judaism"}:
        add(errors, "jewish_context_flattening", str(value.get("community_display")))
    for later in value.get("later_source_uses", []):
        if len(str(later.get("bridge_method", ""))) < 20 or not later.get("limitations"):
            add(errors, "jewish_context_later_bridge", str(later.get("source_ref")))
    return errors


def derived_reverse_index(graph: dict[str, Any]) -> dict[str, list[str]]:
    node_ids = sorted(node["node_id"] for node in graph.get("nodes", []))
    reverse = {node_id: [] for node_id in node_ids}
    for edge in graph.get("edges", []):
        prerequisite = edge.get("prerequisite_id")
        consumer = edge.get("consumer_id")
        if prerequisite in reverse and consumer in reverse:
            reverse[prerequisite].append(consumer)
    return {key: sorted(set(values)) for key, values in reverse.items()}


def reverse_closure(reverse: dict[str, list[str]], starts: Iterable[str]) -> set[str]:
    result: set[str] = set()
    queue = list(starts)
    while queue:
        node = queue.pop(0)
        for consumer in reverse.get(node, []):
            if consumer not in result:
                result.add(consumer)
                queue.append(consumer)
    return result


def resolve_graph_basis(
    ref: Any,
    records: dict[str, dict[str, dict[str, Any]]],
    qualification_maps: dict[str, dict[str, Any]],
    authority_registry: dict[str, Any],
) -> tuple[str, dict[str, Any] | Path] | None:
    path = resolve_relative(ref)
    if path is not None and path.is_file():
        return "file", path
    parsed = split_typed_ref(ref)
    if parsed is None:
        return None
    kind, identifier = parsed
    if kind in records and identifier in records[kind]:
        return kind, records[kind][identifier]
    qualification_kind = {
        "expert-pack": "expert_packs",
        "qualification-receipt": "qualification_receipts",
        "correlation-acceptance": "correlation_acceptance_receipts",
    }.get(kind)
    if qualification_kind and identifier in qualification_maps.get(qualification_kind, {}):
        return kind, qualification_maps[qualification_kind][identifier]
    authority_collection = {
        "human-decision": ("human_decision_receipts", "receipt_id"),
        "normative-frame": ("normative_frames", "frame_id"),
    }.get(kind)
    if authority_collection:
        collection, id_field = authority_collection
        row = next((
            item
            for item in authority_registry.get(collection, [])
            if item.get(id_field) == identifier
        ), None)
        if row is not None:
            return kind, row
    return None


def resolved_graph_basis_digest(resolved: tuple[str, dict[str, Any] | Path]) -> str | None:
    kind, value = resolved
    if kind == "file" and isinstance(value, Path):
        return file_digest(value)
    if not isinstance(value, dict):
        return None
    digest_field = {
        **EVIDENCE_OBJECT_DIGEST_FIELDS,
        "expert-pack": "pack_digest",
        "qualification-receipt": "receipt_digest",
        "correlation-acceptance": "receipt_digest",
        "human-decision": "receipt_digest",
        "normative-frame": "frame_digest",
    }.get(kind)
    return value.get(digest_field) if digest_field else None


def validate_graph(
    value: dict[str, Any],
    final: bool,
    evidence_registry: dict[str, Any],
    authority_registry: dict[str, Any],
) -> list[str]:
    errors = schema_errors(load_data("graph/instance-dependency-graph.schema.json"), value, "graph/example-graph.json")
    nodes = value.get("nodes", [])
    edges = value.get("edges", [])
    node_ids = [node.get("node_id") for node in nodes]
    if len(node_ids) != len(set(node_ids)):
        add(errors, "graph_node_ids", "node IDs must be unique")
    edge_ids = [edge.get("edge_id") for edge in edges]
    if len(edge_ids) != len(set(edge_ids)):
        add(errors, "graph_edge_ids", "edge IDs must be unique")
    known = set(node_ids)
    if any(edge.get("consumer_id") not in known or edge.get("prerequisite_id") not in known for edge in edges):
        add(errors, "graph_endpoint", "all edge endpoints must exist")
    expected_reverse = derived_reverse_index(value)
    if value.get("reverse_consumer_index") != expected_reverse:
        add(errors, "graph_reverse_index", f"expected generated reverse index {expected_reverse}")
    if value.get("canonical_edge_direction") != "consumer_to_prerequisite":
        add(errors, "graph_direction", "canonical direction changed")
    successors = {node_id: set() for node_id in known}
    load_edges: dict[str, list[dict[str, Any]]] = {node_id: [] for node_id in known}
    node_map = {node.get("node_id"): node for node in nodes}
    for node in nodes:
        content_ref = node.get("content_ref")
        content_path = resolve_relative(content_ref)
        if content_path is None or not content_path.is_file():
            add(errors, "graph_node_content_ref", f"{node.get('node_id')}: {content_ref}")
        elif node.get("content_digest") != file_digest(content_path):
            add(errors, "graph_node_content_digest", f"{node.get('node_id')}: {content_ref}")
    records = evidence_maps(evidence_registry)
    qualification_registry = load_data("mesh/qualification-registry.json")
    qualification_errors, qualification_maps = cached_validate_qualification_registry(
        qualification_registry, final=False
    )
    if qualification_errors:
        add(errors, "graph_qualification_registry", qualification_errors[0])
    for edge in edges:
        if edge.get("load_bearing"):
            successors.get(edge.get("consumer_id"), set()).add(edge.get("prerequisite_id"))
            load_edges.get(edge.get("consumer_id"), []).append(edge)
        if edge.get("edge_type") in CONTEXT_EDGE_TYPES:
            if edge.get("load_bearing") is not False or edge.get("normative_force") != "none":
                add(errors, "graph_context_authority", f"context edge {edge.get('edge_id')} acquired authority")
        consumer = node_map.get(edge.get("consumer_id"), {})
        prerequisite = node_map.get(edge.get("prerequisite_id"), {})
        if prerequisite.get("authority_plane") == "context" and consumer.get("authority_plane") in CONTEXT_BLOCKED_CONSUMER_PLANES:
            if edge.get("load_bearing") is not False or edge.get("normative_force") != "none" or edge.get("edge_type") not in CONTEXT_EDGE_TYPES:
                add(errors, "graph_cross_plane_context", f"{edge.get('edge_id')} directly elevates context into {consumer.get('authority_plane')}")
        basis_refs = edge.get("basis_refs", [])
        resolved_bases = [
            resolve_graph_basis(
                ref, records, qualification_maps, authority_registry
            )
            for ref in basis_refs
        ]
        basis_digests = edge.get("basis_digests", [])
        if len(basis_digests) != len(basis_refs):
            add(errors, "graph_basis_pairs", f"{edge.get('edge_id')}: refs and digests differ")
        if edge.get("load_bearing") and any(item is None for item in resolved_bases):
            unresolved = [
                ref for ref, resolved in zip(basis_refs, resolved_bases)
                if resolved is None
            ]
            add(errors, "graph_basis_ref", f"{edge.get('edge_id')}: {unresolved}")
        for index, resolved in enumerate(resolved_bases):
            if resolved is None or index >= len(basis_digests):
                continue
            expected_basis_digest = resolved_graph_basis_digest(resolved)
            if expected_basis_digest is None or basis_digests[index] != expected_basis_digest:
                add(errors, "graph_basis_digest", f"{edge.get('edge_id')}: {basis_refs[index]}")
        if edge.get("load_bearing"):
            prerequisite_basis = (
                prerequisite.get("content_ref"), prerequisite.get("content_digest")
            )
            if prerequisite_basis not in set(zip(basis_refs, basis_digests)):
                add(
                    errors,
                    "graph_prerequisite_basis",
                    f"{edge.get('edge_id')}: missing exact prerequisite content binding {prerequisite_basis[0]}",
                )
        if edge.get("load_bearing") and any(re.search(r"knowledge.?guide|ai[-_ ]?(?:output|summary)|search[-_ ]?result|snippet", str(ref), re.I) for ref in basis_refs):
            add(errors, "graph_source_laundering", f"{edge.get('edge_id')} uses discovery-only material")
        if edge.get("edge_type") != "influence_hypothesis" and any(re.search(r"(?:influence|borrow(?:ing|ed)?|caus(?:e|al|ation)|continuity)", str(ref), re.I) for ref in basis_refs):
            add(errors, "graph_causation_smuggling", f"{edge.get('edge_id')} encodes causation outside an influence hypothesis")
        typed = [split_typed_ref(ref) for ref in basis_refs]
        if edge.get("edge_type") == "cites_for_evidence":
            source_refs = [item for item in typed if item and item[0] == "source-record"]
            if not source_refs:
                add(errors, "graph_evidence_basis", f"{edge.get('edge_id')} lacks a source record")
            for _, identifier in source_refs:
                if records["source-record"].get(identifier, {}).get("qualifies_for_load_bearing") is not True:
                    add(errors, "graph_evidence_basis", f"{edge.get('edge_id')} has unresolved or unqualified source {identifier}")
        if edge.get("edge_type") == "translated_from":
            kinds = {item[0] for item in typed if item}
            if not {"source-record", "translation-lineage"} <= kinds:
                add(errors, "graph_translation_lineage", f"{edge.get('edge_id')} needs source and translation records")
            for item in typed:
                if item and item[0] in {"source-record", "translation-lineage"} and item[1] not in records[item[0]]:
                    add(errors, "graph_translation_lineage", f"{edge.get('edge_id')} has unresolved {item[0]}:{item[1]}")
        if edge.get("edge_type") == "influence_hypothesis":
            refs = [item for item in typed if item and item[0] == "influence-hypothesis"]
            if not refs or any(identifier not in records["influence-hypothesis"] for _, identifier in refs):
                add(errors, "graph_influence_basis", f"{edge.get('edge_id')} lacks a resolved influence hypothesis")
        if edge.get("edge_type") == "qualified_by" and edge.get("review_state") == "accepted":
            qualification_receipts = [
                value
                for resolved in resolved_bases
                if resolved is not None and resolved[0] == "qualification-receipt"
                for value in [resolved[1]]
                if isinstance(value, dict)
            ]
            try:
                observed_at = parse_time(edge.get("basis_observed_at"))
            except (TypeError, ValueError) as exc:
                observed_at = None
                add(errors, "graph_qualified_basis_time", f"{edge.get('edge_id')}: {exc}")
            if not qualification_receipts:
                add(errors, "graph_qualified_basis", f"{edge.get('edge_id')} lacks a typed qualification receipt")
            elif observed_at is not None and any(
                not qualification_active_at(receipt, observed_at)
                for receipt in qualification_receipts
            ):
                add(errors, "graph_qualified_basis_time", f"{edge.get('edge_id')} uses a stale qualification")
        if edge.get("normative_force") == "frame_scoped":
            active_ref = authority_registry.get("current_normative_frame_ref")
            if authority_registry.get("normative_authority_active") is not True or active_ref not in basis_refs:
                add(errors, "graph_normative_authority", f"{edge.get('edge_id')} lacks the exact active human-approved frame")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visited:
            return True
        if node in visiting:
            return False
        visiting.add(node)
        if not all(visit(item) for item in successors.get(node, set())):
            return False
        visiting.remove(node)
        visited.add(node)
        return True

    if not all(visit(node) for node in known):
        add(errors, "graph_cycle", "load-bearing inference graph must be acyclic")
    taint_cache: dict[str, set[str]] = {}

    def authority_taints(node_id: str, stack: tuple[str, ...] = ()) -> set[str]:
        if node_id in taint_cache:
            return taint_cache[node_id]
        if node_id in stack:
            return {str(node_map.get(node_id, {}).get("authority_plane"))}
        result = {str(node_map.get(node_id, {}).get("authority_plane"))}
        for prerequisite in successors.get(node_id, set()):
            result |= authority_taints(prerequisite, (*stack, node_id))
        taint_cache[node_id] = result
        return result

    def context_witness(node_id: str, stack: tuple[str, ...] = ()) -> list[str] | None:
        if node_id in stack:
            return None
        if node_map.get(node_id, {}).get("authority_plane") == "context":
            return [node_id]
        for prerequisite in sorted(successors.get(node_id, set())):
            witness = context_witness(prerequisite, (*stack, node_id))
            if witness is not None:
                return [node_id, *witness]
        return None

    for node_id, node in node_map.items():
        derived = sorted(authority_taints(node_id))
        if node.get("derived_authority_taints") != derived:
            add(errors, "graph_authority_taints", f"{node_id}: expected {derived}")
        if node.get("authority_plane") in CONTEXT_BLOCKED_CONSUMER_PLANES and "context" in derived:
            witness = context_witness(node_id) or [node_id]
            add(errors, "graph_context_transitive", " -> ".join(witness))
        if node.get("state") == "accepted" and node.get("authority_plane") in {"normative_assessment", "tradition_view"}:
            active_ref = authority_registry.get("current_normative_frame_ref")
            active_digest = authority_registry.get("current_normative_frame_digest")
            if (
                authority_registry.get("normative_authority_active") is not True
                or node.get("normative_frame_ref") != active_ref
                or node.get("normative_frame_digest") != active_digest
            ):
                add(errors, "graph_accepted_normative_frame", f"{node_id} lacks the exact active frame")
            governed_edges = [
                edge
                for edge in load_edges.get(node_id, [])
                if edge.get("edge_type") == "governed_by"
                and edge.get("normative_force") == "frame_scoped"
                and active_ref in edge.get("basis_refs", [])
            ]
            if not governed_edges:
                add(
                    errors,
                    "graph_accepted_normative_edge",
                    f"{node_id} has no exact active-frame governance edge",
                )
    bound_node_files = {
        "DMV3-CONSTITUTION": "constitution.yaml",
        "DMV3-PAT-SOURCEPLAN": "research/patristic-source-qualification-plan.yaml",
        "DMV3-PILOT-1CLEMENT": "campaign.yaml",
        "DMV3-NORMATIVE-FRAME": "graph/normative-frame.schema.json",
        "DMV3-PUBLIC-STATUS": "transparency/public-status.json",
    }
    for node_id, relative in bound_node_files.items():
        if node_map.get(node_id, {}).get("content_digest") != file_digest(ROOT / relative):
            add(errors, "graph_node_content_digest", f"{node_id} does not bind {relative}")
    state_from_node = {
        "planned": "blocked", "blocked": "blocked", "quarantined": "invalidated",
        "review_required": "disputed", "stale": "stale", "invalidated": "invalidated",
        "superseded": "stale",
    }
    state_from_edge = {
        "unreviewed": "candidate", "candidate": "candidate", "accepted": "accepted",
        "disputed": "disputed", "stale": "stale", "rejected": "invalidated",
    }
    severity = {"not_applicable": 0, "accepted": 1, "candidate": 2, "disputed": 3, "blocked": 4, "stale": 5, "invalidated": 6}
    memo: dict[str, str] = {}

    def effective_state(node_id: str, stack: set[str] | None = None) -> str:
        if node_id in memo:
            return memo[node_id]
        stack = set() if stack is None else set(stack)
        if node_id in stack:
            return "invalidated"
        stack.add(node_id)
        node = node_map.get(node_id, {})
        candidates: list[str] = []
        own = state_from_node.get(node.get("state"))
        if own:
            candidates.append(own)
        for edge in load_edges.get(node_id, []):
            prerequisite_state = effective_state(edge.get("prerequisite_id"), stack)
            candidates.append("accepted" if prerequisite_state == "not_applicable" else prerequisite_state)
            candidates.append(state_from_edge.get(edge.get("review_state"), "invalidated"))
        result = max(candidates, key=lambda item: severity[item]) if candidates else "not_applicable"
        memo[node_id] = result
        return result

    for node_id, node in node_map.items():
        expected_weakest = effective_state(node_id)
        if node.get("weakest_premise_state") != expected_weakest:
            add(errors, "graph_weakest_premise_state", f"{node_id} expected {expected_weakest}")
        if node.get("state") in CURRENT_STATES and expected_weakest in NONCURRENT_PREMISE_STATES:
            add(errors, "graph_weakest_premise", f"current consumer {node_id} reaches {expected_weakest} load-bearing premise")
        if node.get("state") == "accepted" and expected_weakest not in {"accepted", "not_applicable"}:
            add(errors, "graph_accepted_strength", f"accepted node {node_id} rests on {expected_weakest}")
    if final:
        for node in nodes:
            if node.get("content_digest") == ZERO_DIGEST:
                add(errors, "graph_placeholder_digest", f"{node.get('node_id')} still has placeholder digest")
        expected_digest = object_digest(value, omit=("graph_digest",))
        if value.get("graph_digest") != expected_digest:
            add(errors, "graph_digest", f"expected {expected_digest}")
    return errors


def validate_debts(
    values: list[dict[str, Any]],
    graph: dict[str, Any],
    catalog: dict[str, Any] | None = None,
    constitution: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    schema = load_data("debt/expert-review-debt.schema.json")
    if catalog is None:
        catalog = load_data("mesh/role-catalog.yaml")
    if constitution is None:
        constitution = load_data("constitution.yaml")
    node_ids = {node.get("node_id") for node in graph.get("nodes", [])}
    known_capabilities = catalog_capability_ids(catalog)
    known_human_gates = set(constitution.get("human_gates", []))
    load_bearing_edges = [
        edge for edge in graph.get("edges", []) if edge.get("load_bearing") is True
    ]
    all_reverse = derived_reverse_index(graph)
    reverse = {node_id: [] for node_id in node_ids if isinstance(node_id, str)}
    for edge in load_bearing_edges:
        prerequisite = edge.get("prerequisite_id")
        consumer = edge.get("consumer_id")
        if prerequisite in reverse and consumer in reverse:
            reverse[prerequisite].append(consumer)
    reverse = {key: sorted(set(consumers)) for key, consumers in reverse.items()}
    seen: set[str] = set()
    for debt in values:
        errors.extend(schema_errors(schema, debt, debt.get("debt_id", "debt")))
        debt_id = debt.get("debt_id")
        if debt_id in seen:
            add(errors, "debt_id", f"duplicate {debt_id}")
        seen.add(debt_id)
        subjects = set(debt.get("subject_node_ids", []))
        unknown_subjects = sorted(subjects - node_ids)
        if unknown_subjects:
            add(errors, "debt_subject_nodes", f"{debt_id} unknown subjects {unknown_subjects}")
        expected_prerequisites = sorted({
            edge.get("prerequisite_id")
            for edge in load_bearing_edges
            if edge.get("consumer_id") in subjects
        })
        if debt.get("direct_load_bearing_prerequisite_ids") != expected_prerequisites:
            add(
                errors,
                "debt_direct_prerequisites",
                f"{debt_id} expected {expected_prerequisites}",
            )
        expected_all = sorted(reverse_closure(all_reverse, subjects) - subjects)
        expected_load_bearing = sorted(reverse_closure(reverse, subjects) - subjects)
        if debt.get("downstream_consumer_ids") != expected_all:
            add(errors, "debt_reverse_consumers", f"{debt_id} expected {expected_all}")
        if debt.get("load_bearing_downstream_consumer_ids") != expected_load_bearing:
            add(errors, "debt_load_bearing_reverse_consumers", f"{debt_id} expected {expected_load_bearing}")
        if debt.get("blast_radius_count") != len(expected_all):
            add(errors, "debt_blast_radius", f"{debt_id} expected {len(expected_all)}")
        if debt.get("load_bearing_blast_radius_count") != len(expected_load_bearing):
            add(errors, "debt_load_bearing_blast_radius", f"{debt_id} expected {len(expected_load_bearing)}")
        if debt.get("blocking") and debt.get("risk_tier") not in {"high", "frontier"}:
            add(errors, "debt_blocking_risk", f"{debt_id} blocking debt must be high or frontier")
        unknown_capabilities = sorted(
            set(debt.get("required_capability_ids", [])) - known_capabilities
        )
        if unknown_capabilities:
            add(
                errors,
                "debt_capability_ids",
                f"{debt_id} unknown capabilities {unknown_capabilities}",
            )
        unknown_human_gates = sorted(
            set(debt.get("required_human_gate_ids", [])) - known_human_gates
        )
        if unknown_human_gates:
            add(
                errors,
                "debt_human_gate_ids",
                f"{debt_id} unknown human gates {unknown_human_gates}",
            )
        gaps = set(debt.get("proposed_role_gap_ids", []))
        known_gaps = catalog_gap_ids(catalog)
        if gaps - known_gaps:
            add(errors, "debt_role_gaps", f"{debt_id} unknown role gaps {sorted(gaps - known_gaps)}")
        if gaps & known_capabilities:
            add(errors, "debt_role_gaps", f"{debt_id} role gaps must not masquerade as known capabilities")
        if gaps and debt.get("status") not in {"open", "blocked_source"}:
            add(errors, "debt_unresolved_gap_status", f"{debt_id} cannot advance with unresolved role gaps")
        if set(debt.get("required_capability_ids", [])) & set(debt.get("required_human_gate_ids", [])):
            add(errors, "debt_capability_gate_conflation", f"{debt_id} capabilities and human gates must be disjoint")
        exact_bindings = (
            ("dependency_graph_ref", "dependency_graph_digest", "graph/example-graph.json", graph),
            ("capability_catalog_ref", "capability_catalog_digest", "mesh/role-catalog.yaml", catalog),
            ("human_gate_registry_ref", "human_gate_registry_digest", "constitution.yaml", constitution),
            ("review_packet_ref", "review_packet_digest", None, None),
            ("acceptance_rubric_ref", "acceptance_rubric_digest", None, None),
        )
        for ref_field, digest_field, exact_ref, expected_object in exact_bindings:
            reference = debt.get(ref_field)
            if exact_ref is not None and reference != exact_ref:
                add(errors, "debt_binding_ref", f"{debt_id} {ref_field} must equal {exact_ref}")
                continue
            path = resolve_relative(reference)
            if path is None or not path.is_file():
                add(errors, "debt_binding_ref", f"{debt_id} unresolved {ref_field}={reference!r}")
                continue
            if debt.get(digest_field) != file_digest(path):
                add(errors, "debt_binding_digest", f"{debt_id} stale {digest_field}")
            if expected_object is not None and load_data(str(reference)) != expected_object:
                add(errors, "debt_binding_input", f"{debt_id} {ref_field} differs from validated input")
        packet_path = resolve_relative(debt.get("review_packet_ref"))
        if packet_path is not None and packet_path.is_file() and packet_path.suffix.lower() in {".yaml", ".yml"}:
            packet = load_data(str(debt.get("review_packet_ref")))
            route = packet.get("first_candidate") if isinstance(packet, dict) else None
            if isinstance(route, dict):
                for field in (
                    "required_capability_ids", "required_human_gate_ids",
                    "proposed_role_gap_ids",
                ):
                    if debt.get(field) != route.get(field):
                        add(errors, "debt_packet_route", f"{debt_id} {field} differs from review packet")
    return errors


def validate_public_status(value: dict[str, Any], final: bool) -> list[str]:
    errors = schema_errors(load_data("transparency/public-safe-status.schema.json"), value, "transparency/public-status.json")
    migration = load_data("checks/adversarial-harness-migration.yaml")
    expected_maturity = migration.get("public_maturity")
    expected_blocker = migration.get("declared_release_blocker", {}).get("identity")
    for field in ("runtime_activated", "research_started", "source_corpus_ingested", "doctrine_corpus_complete", "qualified_theological_authority"):
        if value.get(field) is not False:
            add(errors, f"public_{field}", "must remain false")
    if value.get("human_review_required") is not True:
        add(errors, "public_human_review", "human review must remain required")
    if value.get("maturity") != expected_maturity:
        add(errors, "public_maturity_migration", "public maturity must exactly match the migration gate")
    if value.get("specification_complete") is not False:
        add(errors, "public_specification_complete", "must remain false while the declared release blocker is open")
    if value.get("declared_release_blocker") != expected_blocker:
        add(errors, "public_release_blocker", "must expose the exact migration release blocker")
    return errors


def validate_mistake_escalation(value: dict[str, Any]) -> list[str]:
    """Bind the public CAPA replay claims to the exact current harness inputs."""

    errors: list[str] = []
    replay = value.get("regression_test", {}).get("replay_evidence", {})
    expected = {
        "test_file_sha256": file_digest(ROOT / "checks/test_validate_doctrine_marathon.py"),
        "aggregate_sentinel_catalog_sha256": file_digest(
            ROOT / "checks/fixtures/aggregate-sentinel-cases.json"
        ),
        "aggregate_sentinel_runner_sha256": file_digest(
            ROOT / "checks/run_adversarial_harness.py"
        ),
        "aggregate_sentinel_test_sha256": file_digest(
            ROOT / "checks/test_run_adversarial_harness.py"
        ),
    }
    if replay.get("digest_algorithm") != "canonical_utf8_lf_sha256":
        add(
            errors,
            "mistake_replay_digest_algorithm",
            "replay evidence must declare canonical UTF-8/LF SHA-256",
        )
    for field, digest in expected.items():
        if replay.get(field) != digest:
            add(errors, "mistake_replay_digest", f"stale {field}")
    return errors


def validate_prompt(text: str) -> list[str]:
    errors: list[str] = []
    required = (
        "Chat memory", "entry completeness audit", "midflight", "exit",
        "role-qualification-and-independence-auditor", "HistoricalAttribution",
        "NormativeFrame", "consumer -> prerequisite", "seven days",
        "CONTINUE", "BLOCKED", "CAMPAIGN_COMPLETE", "exactly one copy-ready next prompt",
        "Do not launch a controller",
    )
    for token in required:
        if token not in text:
            add(errors, "prompt_required_control", f"missing {token!r}")
    for pattern in DESIRED_CONCLUSION_PATTERNS:
        if re.search(pattern, text, re.I | re.S):
            add(errors, "prompt_desired_conclusion", f"prompt matches forbidden desired-conclusion family {pattern}")
    neutrality = load_data("firewall/prompt-neutrality-contract.yaml")
    observed_neutrality_digest = object_digest(neutrality)
    if neutrality.get("independent_semantic_alignment_review_required") is not True:
        add(errors, "prompt_semantic_review", "independent semantic alignment review must remain required")
    if neutrality.get("deterministic_lexical_screen_is_only_a_floor") is not True:
        add(errors, "prompt_lexical_nonclaim", "lexical screening cannot be treated as proof of neutrality")
    route_match = re.search(
        r"<!-- BEGIN DETERMINISTIC_TRIGGER_ROUTES -->\s*```yaml\s*(.*?)\s*```\s*"
        r"<!-- END DETERMINISTIC_TRIGGER_ROUTES -->",
        text,
        re.S,
    )
    if route_match is None:
        add(errors, "prompt_trigger_route", "machine-readable trigger routing block is missing")
    else:
        try:
            route = yaml.safe_load(route_match.group(1))
        except yaml.YAMLError as exc:
            add(errors, "prompt_trigger_route", f"trigger routing YAML is invalid: {exc}")
        else:
            expected_ids = sorted(REQUIRED_TRIGGER_IDS)
            if not isinstance(route, dict) or set(route) != {
                "trigger_matrix_ref", "trigger_matrix_digest", "barrier_rule", "trigger_ids"
            }:
                add(errors, "prompt_trigger_route", "trigger routing shape is not exact")
            else:
                if route.get("trigger_matrix_ref") != "firewall/trigger-matrix.yaml":
                    add(errors, "prompt_trigger_route", "trigger matrix reference is not exact")
                if route.get("trigger_matrix_digest") != file_digest(ROOT / "firewall/trigger-matrix.yaml"):
                    add(errors, "prompt_trigger_digest", "trigger matrix digest is stale")
                if route.get("trigger_ids") != expected_ids:
                    add(errors, "prompt_trigger_ids", "prompt trigger IDs do not equal the matrix contract")
                if route.get("barrier_rule") != "exact_changed_input_and_full_reverse_consumer_closure_before_continuation":
                    add(errors, "prompt_trigger_barrier", "prompt barrier rule is not exact")
    if observed_neutrality_digest != EXPECTED_PROMPT_NEUTRALITY_OBJECT_DIGEST:
        add(
            errors,
            "prompt_neutrality_contract_integrity",
            "the complete canonical prompt-neutrality contract changed: expected "
            f"{EXPECTED_PROMPT_NEUTRALITY_OBJECT_DIGEST}; observed {observed_neutrality_digest}",
        )
    return errors


def validate_adversarial_harness_migration(final: bool) -> list[str]:
    errors: list[str] = []
    value = load_data("checks/adversarial-harness-migration.yaml")
    legacy_catalog_ref = "checks/fixtures/negative-cases.json"
    isolated_catalog_ref = "checks/fixtures/strict-isolated-cases.json"
    aggregate_catalog_ref = "checks/fixtures/aggregate-sentinel-cases.json"
    aggregate_runner_ref = "checks/run_adversarial_harness.py"
    aggregate_test_ref = "checks/test_run_adversarial_harness.py"
    legacy_catalog = load_data(legacy_catalog_ref)
    isolated_catalog = load_data(isolated_catalog_ref)
    aggregate_catalog = load_data(aggregate_catalog_ref)
    legacy_ids = [
        row.get("case_id") for row in legacy_catalog if isinstance(row, dict)
    ] if isinstance(legacy_catalog, list) else []
    isolated_rows = isolated_catalog.get("cases", []) if isinstance(isolated_catalog, dict) else []
    isolated_ids = [
        row.get("case_id") for row in isolated_rows if isinstance(row, dict)
    ]
    aggregate_rows = (
        aggregate_catalog.get("cases", [])
        if isinstance(aggregate_catalog, dict)
        else []
    )
    aggregate_ids = [
        row.get("case_id") for row in aggregate_rows if isinstance(row, dict)
    ]
    aggregate_source_ids = [
        row.get("source_case_id") for row in aggregate_rows if isinstance(row, dict)
    ]

    if (
        len(legacy_ids) != len(legacy_catalog)
        or len(set(legacy_ids)) != len(legacy_ids)
        or any(not isinstance(case_id, str) for case_id in legacy_ids)
    ):
        add(errors, "adversarial_harness_inventory", "legacy case IDs are not exact and unique")
    if (
        len(isolated_ids) != len(isolated_rows)
        or len(set(isolated_ids)) != len(isolated_ids)
        or any(not isinstance(case_id, str) for case_id in isolated_ids)
    ):
        add(errors, "adversarial_harness_inventory", "isolated case IDs are not exact and unique")
    if set(legacy_ids) & set(isolated_ids):
        add(errors, "adversarial_harness_inventory", "legacy and isolated case IDs overlap")
    if (
        not isinstance(aggregate_catalog, dict)
        or set(aggregate_catalog) != {"metadata", "schema_version", "assurance_scope", "cases"}
        or aggregate_catalog.get("schema_version")
        != "logos.doctrine-marathon.aggregate-sentinel-catalog.v1"
        or aggregate_catalog.get("assurance_scope")
        != "aggregate_sentinel_only_not_full_legacy_migration"
    ):
        add(errors, "adversarial_harness_sentinel_catalog", "aggregate sentinel catalog identity changed")
    if (
        len(aggregate_ids) != len(aggregate_rows)
        or len(set(aggregate_ids)) != len(aggregate_ids)
        or any(not isinstance(case_id, str) for case_id in aggregate_ids)
    ):
        add(errors, "adversarial_harness_sentinel_catalog", "aggregate sentinel case IDs are not exact and unique")
    component_ids = set(legacy_ids) | set(isolated_ids)
    if (
        len(aggregate_source_ids) != len(aggregate_rows)
        or len(set(aggregate_source_ids)) != len(aggregate_source_ids)
        or any(source_id not in component_ids for source_id in aggregate_source_ids)
    ):
        add(errors, "adversarial_harness_sentinel_mapping", "aggregate sentinels must map bijectively to existing component source cases")

    declared_blocker = {
        "rule": "adversarial_harness_release_gate",
        "identity": (
            "adversarial_harness_release_gate: V3 cannot release until the "
            "aggregate exact-oracle migration is complete and independently reviewed"
        ),
    }
    expected_root = {
        "portable_core_revision": "dad.deterministic_adversarial_harness.v4",
        "registry_discovery_contract_revision": "dad.harness_registry_discovery.v3",
        "receipt_index_contract_revision": "dad.harness_receipt_index.v2",
        "independent_review": "PASS_ACTIVATE",
        "repository_registry_bound": False,
        "repository_adapter_bound": False,
        "ci_provider_installation_verified": False,
    }
    expected_inventory = {
        "legacy_catalog_ref": legacy_catalog_ref,
        "legacy_catalog_digest": file_digest(ROOT / legacy_catalog_ref),
        "legacy_case_ids_digest": object_digest(legacy_ids),
        "legacy_catalog_case_count": len(legacy_ids),
        "isolated_catalog_ref": isolated_catalog_ref,
        "isolated_catalog_digest": file_digest(ROOT / isolated_catalog_ref),
        "isolated_case_ids_digest": object_digest(isolated_ids),
        "isolated_catalog_case_count": len(isolated_ids),
        "component_inventory_case_count": len(legacy_ids) + len(isolated_ids),
        "aggregate_sentinel_catalog_ref": aggregate_catalog_ref,
        "aggregate_sentinel_catalog_digest": file_digest(ROOT / aggregate_catalog_ref),
        "aggregate_sentinel_case_ids_digest": object_digest(aggregate_ids),
        "aggregate_sentinel_case_count": len(aggregate_ids),
        "aggregate_sentinel_runner_ref": aggregate_runner_ref,
        "aggregate_sentinel_runner_digest": file_digest(ROOT / aggregate_runner_ref),
        "aggregate_sentinel_test_ref": aggregate_test_ref,
        "aggregate_sentinel_test_digest": file_digest(ROOT / aggregate_test_ref),
        "total_executable_rows_across_catalogs": len(legacy_ids) + len(isolated_ids) + len(aggregate_ids),
        "unique_source_case_count": len(component_ids),
        "sentinel_count_is_subset_not_inventory_addend": True,
        "portable_v4_conforming_receipt_count": 0,
        "release_evidence_case_count": 0,
    }
    expected_classification = {
        "legacy_catalog": "component_only_non_authorizing_pending_aggregate_adapter",
        "strict_isolated_catalog": "exact_order_component_only_non_authorizing_pending_aggregate_adapter",
        "aggregate_sentinel_catalog": "local_aggregate_subset_non_authorizing_pending_v4_receipts_registry_and_ci",
        "unsupported_manual_migration_bucket_counts_removed": True,
    }
    expected_required = [
        "migrate or exact-digest human-classify every component-only row under the V3 repository registry",
        "create one V4 receipt per governed catalog case with an exact receipt-index bijection",
        "preserve validator emission order before presentation sorting",
        "bind exact finding identities and causal closure for every governed case",
        "retain the exact one-gate declaration for the completion baseline only",
        "reseal dependent digests closures and receipts unless staleness is intended",
        "replay every governed case forward and reverse from fresh baselines",
        "bind runner command catalog snapshots delta graph outputs review and result evidence",
        "install and test an explicit clean-checkout repository discovery adapter and CI gate",
        "obtain independent unchanged-head non-author review of the adapter runner registry receipts and release candidate",
    ]
    expected_nonclaims = [
        "this state file and four-case sentinel are containment evidence not a completed repository harness migration",
        "the independently reviewed reusable V4 root control has not been adapted to the V3 manifest profile",
        "the four aggregate sentinels are a subset of the 197 source cases and are not an inventory addend",
        "component-level exact ordering and local sentinel replay are not V4 receipt or CI coverage",
        "no fixture result establishes doctrine scholarship source fitness or human authority",
    ]
    if value.get("schema_version") != "logos.doctrine_marathon.adversarial_harness_migration.v2":
        add(errors, "adversarial_harness_migration_identity", "schema version changed")
    if value.get("state") != "blocked_pending_full_v4_repository_adapter":
        add(errors, "adversarial_harness_migration_state", "unreviewed state transition")
    if value.get("public_maturity") != "blocked_specification_only":
        add(errors, "adversarial_harness_migration_state", "public maturity must remain blocked specification-only")
    if value.get("declared_release_blocker") != declared_blocker:
        add(errors, "adversarial_harness_release_gate", "declared release blocker identity changed")
    if value.get("release_evidence_eligible") is not False:
        add(errors, "adversarial_harness_release_claim", "unadapted component and sentinel fixtures are not release evidence")
    if value.get("root_control") != expected_root:
        add(errors, "adversarial_harness_root_binding", "root-control boundary changed")
    if value.get("case_inventory") != expected_inventory:
        add(errors, "adversarial_harness_inventory", "source-derived executable inventory changed")
    if value.get("case_classification") != expected_classification:
        add(errors, "adversarial_harness_classification", "case assurance classification changed")
    if value.get("required_before_release") != expected_required or value.get("nonclaims") != expected_nonclaims:
        add(errors, "adversarial_harness_migration_contract", "repair obligations or nonclaims changed")
    if final:
        errors.append(declared_blocker["identity"])
    return errors


def validate_terminal_handoff(terminal: dict[str, Any]) -> list[str]:
    errors = schema_errors(load_data("state/terminal-handoff.schema.json"), terminal, "terminal handoff")
    checkpoint_ref = terminal.get("checkpoint_ref")
    checkpoint_path = resolve_relative(checkpoint_ref)
    if checkpoint_path is None or not checkpoint_path.is_file():
        add(errors, "terminal_checkpoint_ref", str(checkpoint_ref))
        return errors
    expected_checkpoint = file_digest(checkpoint_path)
    if terminal.get("checkpoint_digest") != expected_checkpoint:
        add(errors, "terminal_checkpoint_digest", f"expected {expected_checkpoint}")
    loaded_checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if terminal.get("checkpoint_id") != loaded_checkpoint.get("checkpoint_id"):
        add(errors, "terminal_checkpoint_id", "terminal and checkpoint IDs differ")
    if terminal.get("status") != "CAMPAIGN_COMPLETE" and terminal.get("status") != loaded_checkpoint.get("status"):
        add(errors, "terminal_checkpoint_status", "terminal and checkpoint statuses differ")
    if terminal.get("status") == "CAMPAIGN_COMPLETE":
        if loaded_checkpoint.get("status") != "BLOCKED":
            add(errors, "terminal_completion_checkpoint", "completion must evaluate an immutable pre-completion blocked checkpoint")
        definition_path = resolve_relative(terminal.get("completion_definition_ref"))
        receipt_path = resolve_relative(terminal.get("completion_receipt_ref"))
        if definition_path is None or not definition_path.is_file():
            add(errors, "terminal_completion_definition_ref", str(terminal.get("completion_definition_ref")))
        if receipt_path is None or not receipt_path.is_file():
            add(errors, "terminal_completion_receipt_ref", str(terminal.get("completion_receipt_ref")))
        if definition_path is not None and definition_path.is_file() and receipt_path is not None and receipt_path.is_file():
            definition = json.loads(definition_path.read_text(encoding="utf-8"))
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            errors.extend(schema_errors(load_data("state/campaign-completion-definition.schema.json"), definition, "campaign completion definition"))
            errors.extend(schema_errors(load_data("state/campaign-completion-receipt.schema.json"), receipt, "campaign completion receipt"))
            if terminal.get("completion_definition_digest") != file_digest(definition_path) or definition.get("definition_digest") != object_digest(definition, omit=("definition_digest",)):
                add(errors, "terminal_completion_definition_digest", "completion definition identity is stale")
            if terminal.get("completion_receipt_digest") != file_digest(receipt_path) or receipt.get("receipt_digest") != object_digest(receipt, omit=("receipt_digest",)):
                add(errors, "terminal_completion_receipt_digest", "completion receipt identity is stale")
            if (
                receipt.get("definition_ref") != terminal.get("completion_definition_ref")
                or receipt.get("definition_digest") != definition.get("definition_digest")
                or receipt.get("checkpoint_ref") != checkpoint_ref
                or receipt.get("checkpoint_digest") != expected_checkpoint
            ):
                add(errors, "terminal_completion_binding", "completion receipt does not bind definition and checkpoint")
            expected_units = sorted(definition.get("required_work_unit_ids", []))
            unit_rows = receipt.get("unit_completion_rows", [])
            observed_units = sorted(row.get("unit_id") for row in unit_rows)
            if observed_units != expected_units or terminal.get("completed_unit_ids") != expected_units:
                add(errors, "terminal_completion_unit_coverage", f"expected {expected_units}")

            campaign = load_data("campaign.yaml")
            expected_horizons = sorted(row.get("horizon_id") for row in campaign.get("chronological_horizons", []))
            if sorted(definition.get("required_horizon_ids", [])) != expected_horizons:
                add(errors, "terminal_completion_horizon_coverage", f"expected {expected_horizons}")
            observed_horizons = sorted(set(row.get("horizon_id") for row in unit_rows))
            if observed_horizons != sorted(definition.get("required_horizon_ids", [])):
                add(errors, "terminal_completion_unit_horizons", "unit rows do not cover the exact approved horizons")
            observed_outputs = sorted(set(row.get("output_class") for row in unit_rows))
            if observed_outputs != sorted(definition.get("required_output_classes", [])):
                add(errors, "terminal_completion_output_coverage", "unit rows do not cover the exact approved output classes")

            snapshot_paths = {
                "ledger_snapshot": resolve_relative(receipt.get("ledger_snapshot_ref")),
                "graph_snapshot": resolve_relative(receipt.get("graph_snapshot_ref")),
                "debt_registry": resolve_relative(receipt.get("debt_registry_ref")),
                "evidence_registry": resolve_relative(receipt.get("evidence_registry_ref")),
            }
            snapshot_values: dict[str, Any] = {}
            for key, path in snapshot_paths.items():
                if path is None or not path.is_file():
                    add(errors, f"terminal_completion_{key}_ref", str(receipt.get(f"{key}_ref")))
                    continue
                expected_digest = file_digest(path)
                if receipt.get(f"{key}_digest") != expected_digest:
                    add(errors, f"terminal_completion_{key}_digest", f"expected {expected_digest}")
                snapshot_values[key] = json.loads(path.read_text(encoding="utf-8"))

            ledger = snapshot_values.get("ledger_snapshot", {})
            ledger_events = ledger.get("events", []) if isinstance(ledger, dict) else []
            ledger_by_id = {row.get("event_id"): row for row in ledger_events if isinstance(row, dict)}
            if not ledger_events or receipt.get("ledger_prefix_event_hash") != ledger.get("last_event_hash"):
                add(errors, "terminal_completion_ledger_prefix", "completion receipt does not bind the nonempty exact ledger prefix")
            else:
                terminal_event = ledger_events[-1]
                terminal_details = terminal_event.get("details", {})
                if (
                    terminal_event.get("event_type") != "terminal_handoff"
                    or terminal_details.get("terminal_status") != "CAMPAIGN_COMPLETE"
                    or terminal_details.get("checkpoint_digest") != expected_checkpoint
                    or terminal_details.get("exact_next_prompt_or_explicit_none_if_complete") is not None
                ):
                    add(errors, "terminal_completion_ledger_terminal", "ledger does not end in the exact completion handoff")
                matching_freezes = [
                    row for row in ledger_events[:-1]
                    if row.get("event_type") == "checkpoint_frozen"
                    and row.get("details", {}).get("checkpoint_digest") == expected_checkpoint
                ]
                if len(matching_freezes) != 1:
                    add(errors, "terminal_completion_checkpoint_event", "exactly one prior checkpoint-freeze event must bind the evaluated checkpoint")

            graph = snapshot_values.get("graph_snapshot", {})
            debts = snapshot_values.get("debt_registry", [])
            evidence = snapshot_values.get("evidence_registry", {})
            authority = load_data("graph/authority-registry.yaml")
            try:
                completion_use_at = parse_time(receipt.get("completed_at"))
            except (TypeError, ValueError):
                completion_use_at = None
            for rule, semantic_errors in (
                ("terminal_completion_ledger_validation", validate_event_ledger(ledger, final=False)),
                ("terminal_completion_authority_validation", validate_authority_registry(authority, final=False)),
                ("terminal_completion_evidence_validation", validate_evidence_registry(evidence, final=False)),
                ("terminal_completion_graph_validation", validate_graph(graph, final=False, evidence_registry=evidence, authority_registry=authority)),
                ("terminal_completion_debt_validation", validate_debts(debts if isinstance(debts, list) else [], graph)),
            ):
                if semantic_errors:
                    add(errors, rule, semantic_errors[0])
            open_debts = [
                row for row in debts
                if isinstance(row, dict) and row.get("status") not in {"closed", "superseded"}
            ] if isinstance(debts, list) else []
            expected_blocking = sorted(row.get("debt_id") for row in open_debts if row.get("blocking") is True)
            expected_high_risk = sorted(row.get("debt_id") for row in open_debts if row.get("risk_tier") in {"high", "frontier"})
            if receipt.get("open_blocking_debt_ids") != expected_blocking:
                add(errors, "terminal_completion_blocking_debt", f"expected {expected_blocking}")
            if receipt.get("open_high_risk_debt_ids") != expected_high_risk:
                add(errors, "terminal_completion_high_risk_debt", f"expected {expected_high_risk}")

            graph_nodes = {row.get("node_id"): row for row in graph.get("nodes", [])} if isinstance(graph, dict) else {}
            load_bearing_node_ids: set[str] = set()
            nonaccepted_edge_node_ids: set[str] = set()
            for edge in graph.get("edges", []) if isinstance(graph, dict) else []:
                if edge.get("load_bearing") is True:
                    edge_nodes = {edge.get("consumer_id"), edge.get("prerequisite_id")}
                    load_bearing_node_ids.update(node_id for node_id in edge_nodes if isinstance(node_id, str))
                    if edge.get("review_state") != "accepted":
                        nonaccepted_edge_node_ids.update(node_id for node_id in edge_nodes if isinstance(node_id, str))
            expected_nonfresh = sorted(
                node_id for node_id in load_bearing_node_ids
                if node_id in nonaccepted_edge_node_ids
                or graph_nodes.get(node_id, {}).get("state") != "accepted"
                or graph_nodes.get(node_id, {}).get("weakest_premise_state") not in {"accepted", "not_applicable"}
            )
            if receipt.get("nonfresh_load_bearing_node_ids") != expected_nonfresh:
                add(errors, "terminal_completion_nonfresh_graph", f"expected {expected_nonfresh}")

            claim_map = {
                row.get("claim_id"): row
                for row in evidence.get("claim_records", [])
                if isinstance(row, dict)
            } if isinstance(evidence, dict) else {}
            required_claims = sorted(definition.get("required_claim_ids", []))
            if required_claims != sorted(claim_map):
                add(errors, "terminal_completion_claim_scope", "approved required claims must equal the exact evidence-registry claim set")
            expected_unresolved_claims = sorted(
                claim_id for claim_id in required_claims
                if claim_id not in claim_map or claim_map[claim_id].get("claim_state") != "verified"
            )
            if receipt.get("unresolved_required_claim_ids") != expected_unresolved_claims:
                add(errors, "terminal_completion_unresolved_claims", f"expected {expected_unresolved_claims}")

            for row in unit_rows:
                unit_id = row.get("unit_id")
                output_path = resolve_relative(row.get("terminal_output_ref"))
                if output_path is None or not output_path.is_file():
                    add(errors, "terminal_completion_output_ref", f"{unit_id}: {row.get('terminal_output_ref')}")
                elif row.get("terminal_output_digest") != file_digest(output_path):
                    add(errors, "terminal_completion_output_digest", str(unit_id))
                exit_event = ledger_by_id.get(row.get("exit_audit_event_id"))
                if (
                    exit_event is None
                    or exit_event.get("event_type") != "completeness_exit"
                    or set(exit_event.get("affected_ids", [])) != {unit_id}
                    or row.get("exit_audit_event_hash") != exit_event.get("event_hash")
                    or exit_event.get("details", {}).get("final_output_digest") != row.get("terminal_output_digest")
                ):
                    add(errors, "terminal_completion_exit_audit", str(unit_id))
                    continue
                exit_sequence = exit_event.get("sequence", 0)
                for review_event_id in row.get("qualified_review_event_ids", []):
                    review_event = ledger_by_id.get(review_event_id)
                    if (
                        review_event is None
                        or review_event.get("event_type") != "check_completed"
                        or unit_id not in review_event.get("affected_ids", [])
                        or review_event.get("input_digest") != row.get("terminal_output_digest")
                        or review_event.get("sequence", exit_sequence) >= exit_sequence
                    ):
                        add(errors, "terminal_completion_qualified_review_event", f"{unit_id}: {review_event_id}")
                    elif completion_use_at is not None:
                        review_errors = validate_check_completed_event(
                            review_event,
                            final=False,
                            consumed_at=completion_use_at,
                            earlier_events=ledger_events[:max(0, review_event.get("sequence", 1) - 1)],
                        )
                        if review_errors:
                            add(errors, "terminal_completion_qualified_review_event", f"{unit_id}: {review_errors[0]}")

            decision_ref = split_typed_ref(receipt.get("human_completion_decision_ref"))
            decision = next((row for row in authority.get("human_decision_receipts", []) if decision_ref and decision_ref[0] == "human-decision" and row.get("receipt_id") == decision_ref[1]), None)
            expected_scope = completion_scope_digest(definition)
            exact_authority_scope = [f"campaign_completion:{campaign.get('campaign_id')}"]
            if (
                decision is None
                or receipt.get("human_completion_decision_digest") != decision.get("receipt_digest")
                or decision.get("decision_type") != "campaign_completion_approval"
                or decision.get("decision") != "approved"
                or definition.get("human_approval_receipt_ref") != receipt.get("human_completion_decision_ref")
                or definition.get("human_approval_receipt_digest") != receipt.get("human_completion_decision_digest")
                or definition.get("authority_registry_digest") != file_digest(ROOT / "graph/authority-registry.yaml")
                or decision.get("subject_ref") != f"campaign-completion-scope:{definition.get('definition_id')}"
                or decision.get("subject_digest") != expected_scope
                or decision.get("scope_digest") != expected_scope
                or decision.get("authority_scope") != exact_authority_scope
            ):
                add(errors, "terminal_completion_human_decision", "exact qualified human completion decision is absent")
            else:
                errors.extend(validate_human_decision_receipt(decision, authority))
                try:
                    completed_at = parse_time(receipt.get("completed_at"))
                    effective_at = parse_time(definition.get("effective_at"))
                    definition_expiry = definition.get("expires_at")
                    decision_issued = parse_time(decision.get("issued_at"))
                    decision_expiry = decision.get("expires_at")
                    checkpoint_created = parse_time(loaded_checkpoint.get("created_at"))
                    if completed_at < effective_at or (definition_expiry is not None and completed_at > parse_time(definition_expiry)):
                        add(errors, "terminal_completion_definition_time", "completion is outside the approved definition interval")
                    if completed_at < decision_issued or (decision_expiry is not None and completed_at > parse_time(decision_expiry)):
                        add(errors, "terminal_completion_decision_time", "completion is outside the approval interval")
                    if completed_at < checkpoint_created:
                        add(errors, "terminal_completion_checkpoint_time", "completion predates the evaluated checkpoint")
                    approver_map = {row.get("signer_id"): row for row in authority.get("qualified_approvers", [])}
                    for signer_id in decision.get("signer_ids", []):
                        approver = approver_map.get(signer_id, {})
                        valid_from = parse_time(approver.get("valid_from"))
                        valid_until = approver.get("valid_until")
                        if (
                            "campaign_completion_approval" not in approver.get("qualification_scope", [])
                            or approver.get("tradition_or_jurisdiction") != decision.get("tradition_or_jurisdiction")
                            or completed_at < valid_from
                            or (valid_until is not None and completed_at > parse_time(valid_until))
                        ):
                            add(errors, "terminal_completion_signer_qualification", str(signer_id))
                except (TypeError, ValueError) as exc:
                    add(errors, "terminal_completion_time", str(exc))
    if (
        terminal.get("status") != "CAMPAIGN_COMPLETE"
        and set(terminal.get("blocked_gate_ids", []))
        != set(loaded_checkpoint.get("blocking_gate_ids", []))
    ):
        add(errors, "terminal_blocking_gates", "terminal and checkpoint blocking gates differ")
    return errors


def validate_weekly_gate(weekly: dict[str, Any], checkpoint: dict[str, Any]) -> list[str]:
    errors = schema_errors(load_data("state/weekly-fresh-context-gate.schema.json"), weekly, "weekly fresh-context gate")
    weekly_checkpoint = resolve_relative(weekly.get("checkpoint_ref"))
    if weekly_checkpoint is None or not weekly_checkpoint.is_file():
        add(errors, "weekly_checkpoint_ref", str(weekly.get("checkpoint_ref")))
    elif weekly.get("checkpoint_digest") != file_digest(weekly_checkpoint):
        add(errors, "weekly_checkpoint_digest", str(weekly.get("checkpoint_ref")))
    prompt_path = resolve_relative(weekly.get("canonical_resume_prompt"))
    if prompt_path is None or not prompt_path.is_file():
        add(errors, "weekly_prompt_ref", str(weekly.get("canonical_resume_prompt")))
    elif weekly.get("canonical_resume_prompt_digest") != file_digest(prompt_path):
        add(errors, "weekly_prompt_digest", str(weekly.get("canonical_resume_prompt")))
    try:
        weekly_opened = parse_time(weekly.get("opened_at"))
        weekly_due = parse_time(weekly.get("must_reset_by"))
        if not 0 < (weekly_due - weekly_opened).total_seconds() <= 7 * 24 * 60 * 60:
            add(errors, "weekly_fresh_context_interval", "reset deadline must be within seven days")
        if weekly.get("must_reset_by") != checkpoint.get("fresh_context_due_at"):
            add(errors, "weekly_checkpoint_deadline", "weekly gate and checkpoint deadlines differ")
        verification = weekly.get("verification")
        if weekly.get("result") == "fresh_context_verified" and isinstance(verification, dict):
            started = parse_time(verification.get("fresh_task_started_at"))
            verified = parse_time(verification.get("verified_at"))
            if not weekly_opened <= started <= verified <= weekly_due:
                add(errors, "weekly_verification_deadline", "verification occurred outside the gate interval")
            receipt_ref = verification.get("verification_receipt_ref")
            receipt_path = resolve_relative(receipt_ref)
            if receipt_path is None or not receipt_path.is_file():
                add(errors, "weekly_verification_receipt_ref", str(receipt_ref))
            else:
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                errors.extend(
                    schema_errors(
                        load_data("state/fresh-context-verification-receipt.schema.json"),
                        receipt,
                        str(receipt_ref),
                    )
                )
                if verification.get("verification_receipt_digest") != file_digest(receipt_path):
                    add(errors, "weekly_verification_receipt_file_digest", str(receipt_ref))
                expected_receipt_digest = object_digest(receipt, omit=("receipt_digest",))
                if receipt.get("receipt_digest") != expected_receipt_digest:
                    add(errors, "weekly_verification_receipt_object_digest", str(receipt_ref))
                if (
                    receipt.get("gate_id") != weekly.get("gate_id")
                    or receipt.get("checkpoint_ref") != weekly.get("checkpoint_ref")
                    or receipt.get("checkpoint_digest") != weekly.get("checkpoint_digest")
                    or receipt.get("canonical_resume_prompt") != weekly.get("canonical_resume_prompt")
                    or receipt.get("canonical_resume_prompt_digest") != weekly.get("canonical_resume_prompt_digest")
                    or receipt.get("fresh_task_started_at") != verification.get("fresh_task_started_at")
                    or receipt.get("verified_at") != verification.get("verified_at")
                    or receipt.get("result") != "verified"
                    or receipt.get("authority_effect") != "none"
                ):
                    add(errors, "weekly_verification_receipt_scope", str(receipt_ref))
                control_bindings = receipt.get("reloaded_control_bindings", [])
                control_refs = [row.get("ref") for row in control_bindings]
                if control_refs != list(FRESH_CONTEXT_REQUIRED_CONTROLS):
                    add(errors, "weekly_verification_control_binding", "required controls must be exact and ordered")
                for binding in control_bindings:
                    control_path = resolve_relative(binding.get("ref"))
                    if (
                        control_path is None
                        or not control_path.is_file()
                        or binding.get("digest") != file_digest(control_path)
                    ):
                        add(errors, "weekly_verification_control_binding", str(binding.get("ref")))
                if receipt.get("context_digest") != object_digest(control_bindings):
                    add(errors, "weekly_verification_control_binding", "context digest is stale")
        if weekly.get("result") == "fresh_context_required" and (weekly.get("verification") is not None or weekly.get("continuation_authorized") is not False):
            add(errors, "weekly_required_continuation", "continuation cannot be authorized before verification")
    except (TypeError, ValueError) as exc:
        add(errors, "weekly_time", str(exc))
    return errors


def validate_terminal_examples() -> list[str]:
    errors: list[str] = []
    checkpoint = load_data("state/examples/initial-resume-checkpoint.json")
    terminal = load_data("state/examples/terminal-handoff-blocked.json")
    weekly = load_data("state/examples/initial-weekly-fresh-context-gate.json")
    errors.extend(schema_errors(load_data("state/resume-checkpoint.schema.json"), checkpoint, "initial resume checkpoint"))
    checkpoint_bindings = {
        "goal_digest": "state/goal.yaml",
        "prompt_digest": "DOCTRINE_MARATHON_MASTER_PROMPT.md",
        "constitution_digest": "constitution.yaml",
        "campaign_digest": "campaign.yaml",
        "event_ledger_digest": "events/event-ledger.json",
        "dependency_graph_digest": "graph/example-graph.json",
        "review_debt_digest": "debt/initial-review-debt.json",
    }
    for field, relative in checkpoint_bindings.items():
        expected = file_digest(ROOT / relative)
        if checkpoint.get(field) != expected:
            add(errors, "checkpoint_digest", f"{field} expected {expected}")
    try:
        opened = parse_time(checkpoint["created_at"])
        due = parse_time(checkpoint["fresh_context_due_at"])
        if not 0 < (due - opened).total_seconds() <= 7 * 24 * 60 * 60:
            add(errors, "checkpoint_fresh_context", "fresh context must be due within seven days")
    except (KeyError, TypeError, ValueError) as exc:
        add(errors, "checkpoint_time", str(exc))
    ledger = load_data("events/event-ledger.json")
    expected_last_event_id = ledger.get("events", [])[-1].get("event_id") if ledger.get("events") else None
    if checkpoint.get("last_event_id") != expected_last_event_id:
        add(errors, "checkpoint_last_event", f"expected {expected_last_event_id}")
    errors.extend(validate_terminal_handoff(terminal))
    errors.extend(validate_weekly_gate(weekly, checkpoint))
    return errors


def validate_schemas() -> list[str]:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.schema.json")):
        try:
            Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001
            add(errors, "schema_invalid", f"{path.relative_to(ROOT).as_posix()}: {exc}")
    return errors


def validate_public_boundary() -> list[str]:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix.lower() == ".pyc":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if LOCAL_PATH_RE.search(text):
            add(errors, "public_local_path", relative)
        if re.search(r"(?:sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY)", text):
            add(errors, "public_secret_pattern", relative)
    return errors


def _is_forbidden_generated_path(path: Path) -> bool:
    return (
        bool(FORBIDDEN_GENERATED_PARTS & set(path.parts))
        or path.name in FORBIDDEN_GENERATED_NAMES
        or path.suffix.lower() == ".pyc"
    )


def _is_git_tracked(path: Path) -> bool:
    try:
        repository_root = Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=ROOT,
                text=True,
                stderr=subprocess.PIPE,
            ).strip()
        )
        relative = path.resolve().relative_to(repository_root.resolve()).as_posix()
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=repository_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError, OSError):
        return False


def validate_generated_inventory() -> tuple[list[str], int]:
    """Reject generated artifacts that could enter the public Git snapshot.

    Ignored local interpreter caches are counted but are not represented as frozen
    public evidence. Exact staged/release-scope validation independently prevents
    them from entering the release. A generated path already tracked by Git is a
    hard failure.
    """

    errors: list[str] = []
    local_only = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not _is_forbidden_generated_path(path):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if _is_git_tracked(path):
            add(errors, "freeze_tracked_generated_path", relative)
        else:
            local_only += 1
    return errors, local_only


def payload_files() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or _is_forbidden_generated_path(path):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative not in ADMIN_FILES:
            result.append(path)
    return sorted(result, key=lambda item: item.relative_to(ROOT).as_posix())


def payload_rows() -> list[dict[str, str]]:
    return [{"path": path.relative_to(ROOT).as_posix(), "sha256": file_digest(path)} for path in payload_files()]


def payload_digest(rows: list[dict[str, str]]) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(rows)).hexdigest()


def _admin_shape(
    errors: list[str],
    rule: str,
    value: Any,
    expected_keys: set[str],
) -> bool:
    if not isinstance(value, dict):
        add(errors, rule, "record must be an object")
        return False
    observed = set(value)
    if observed != expected_keys:
        missing = sorted(expected_keys - observed)
        extra = sorted(observed - expected_keys)
        add(errors, rule, f"missing={missing}; extra={extra}")
        return False
    return True


def _admin_metadata(
    errors: list[str],
    value: Any,
    *,
    object_type: str,
    lifecycle_status: str,
    rule: str,
) -> None:
    keys = {
        "object_type",
        "trust_zone",
        "lifecycle_status",
        "provenance_note",
        "reason_for_inclusion",
    }
    if not _admin_shape(errors, rule, value, keys):
        return
    if (
        value.get("object_type") != object_type
        or value.get("trust_zone") != "proposed"
        or value.get("lifecycle_status") != lifecycle_status
        or not isinstance(value.get("provenance_note"), str)
        or len(value["provenance_note"]) < 30
        or not isinstance(value.get("reason_for_inclusion"), str)
        or len(value["reason_for_inclusion"]) < 30
    ):
        add(errors, rule, "metadata identity, trust, lifecycle, or explanatory prose is invalid")


def _admin_time(errors: list[str], rule: str, value: Any) -> None:
    try:
        parse_time(value)
    except (TypeError, ValueError) as exc:
        add(errors, rule, str(exc))


def validate_admin_records(
    manifest: dict[str, Any],
    receipt: dict[str, Any],
    review: dict[str, Any],
    authorization: dict[str, Any],
    saved: dict[str, Any],
    rows: list[dict[str, str]],
    manifest_file_digest: str,
    receipt_file_digest: str,
    review_file_digest: str,
    authorization_file_digest: str,
) -> list[str]:
    errors: list[str] = []
    manifest_keys = {
        "metadata", "schema_version", "manifest_id", "work_id", "revision_id",
        "revision_root", "parent_revision", "generated_at", "authority",
        "hash_algorithm", "payload_list_digest_algorithm",
        "administrative_files_excluded_from_payload_digest", "payload_file_count",
        "payload_digest", "payload_files", "manifest_digest",
    }
    receipt_keys = {
        "metadata", "schema_version", "receipt_id", "work_id", "revision_id",
        "revision_manifest_ref", "revision_manifest_digest",
        "revision_manifest_object_digest", "payload_file_count", "payload_digest",
        "validator_ref", "validator_digest", "test_ref", "test_digest",
        "negative_fixture_ref", "negative_fixture_digest",
        "final_replay_command", "test_command", "mode", "result", "error_count",
        "validator_metrics", "test_result", "runtime_activation_authorized",
        "research_execution_authorized", "source_ingestion_authorized",
        "substantive_doctrine_implementation_authorized", "completed_doctrine_corpus",
        "qualified_theological_authority", "mutation_performed", "observed_at",
        "receipt_digest",
    }
    review_keys = {
        "metadata", "schema_version", "review_id", "work_id", "revision_id",
        "revision_manifest_ref", "revision_manifest_digest",
        "revision_manifest_object_digest", "payload_file_count", "payload_digest",
        "reviewer_role", "reviewer_actor_instance_id", "reviewer_attempt_id",
        "author_actor_instance_ids", "author_is_reviewer", "independence_status",
        "cross_provider_verified", "review_scope", "reviewed_controls",
        "unresolved_finding_counts", "resolved_finding_ids", "unresolved_human_gates",
        "declared_release_blocker", "result", "runtime_activation_authorized", "research_execution_authorized",
        "source_ingestion_authorized", "substantive_doctrine_implementation_authorized",
        "completed_doctrine_corpus", "qualified_theological_authority",
        "mutation_performed", "observed_at", "review_digest",
    }
    authorization_keys = {
        "metadata", "schema_version", "authorization_id", "work_id",
        "revision_id", "revision_root", "status", "authorization_source",
        "authorizing_principal", "recorded_by", "bound_payload",
        "release_scope", "authority_limits", "verification", "observed_at",
        "authorization_digest",
    }
    saved_keys = {
        "metadata", "schema_version", "save_id", "work_id", "revision_id", "status",
        "revision_manifest_ref", "revision_manifest_digest",
        "revision_manifest_object_digest", "payload_digest", "payload_file_count",
        "validation_receipt_ref", "validation_receipt_file_digest",
        "validation_receipt_object_digest", "independent_review_ref",
        "independent_review_file_digest", "independent_review_object_digest",
        "public_release_authorization_ref",
        "public_release_authorization_file_digest",
        "public_release_authorization_object_digest", "artifact_freeze_readiness",
        "runtime_activation_authorized", "research_execution_authorized",
        "source_ingestion_authorized", "substantive_doctrine_implementation_authorized",
        "completed_doctrine_corpus", "qualified_theological_authority", "saved_at",
        "final_digest",
    }
    _admin_shape(errors, "manifest_shape", manifest, manifest_keys)
    _admin_shape(errors, "validation_receipt_shape", receipt, receipt_keys)
    _admin_shape(errors, "independent_review_shape", review, review_keys)
    _admin_shape(errors, "public_release_authorization_shape", authorization, authorization_keys)
    _admin_shape(errors, "final_saved_shape", saved, saved_keys)
    _admin_metadata(
        errors,
        manifest.get("metadata"),
        object_type="doctrine_marathon_revision_manifest",
        lifecycle_status="frozen_specification_payload",
        rule="manifest_metadata",
    )
    _admin_metadata(
        errors,
        receipt.get("metadata"),
        object_type="doctrine_marathon_validation_receipt",
        lifecycle_status="validated_specification_only",
        rule="validation_receipt_metadata",
    )
    _admin_metadata(
        errors,
        review.get("metadata"),
        object_type="doctrine_marathon_independent_review",
        lifecycle_status="independently_checked",
        rule="independent_review_metadata",
    )
    _admin_metadata(
        errors,
        authorization.get("metadata"),
        object_type="doctrine_marathon_public_release_authorization",
        lifecycle_status="authorized_public_specification_release",
        rule="public_release_authorization_metadata",
    )
    _admin_metadata(
        errors,
        saved.get("metadata"),
        object_type="doctrine_marathon_final_saved_version",
        lifecycle_status="saved_specification_only",
        rule="final_saved_metadata",
    )
    identity = {
        "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
        "revision_id": "doctrine-marathon-v3",
    }
    manifest_identity = {
        **identity,
        "schema_version": "logos.doctrine_marathon.revision_manifest.v3",
        "manifest_id": "DMV3-REVISION-003",
        "revision_root": (
            "docs/roadmap/logos-stewardship-architecture-buildout/"
            "revisions/doctrine-marathon-v3"
        ),
    }
    for field, expected in manifest_identity.items():
        if manifest.get(field) != expected:
            add(errors, "manifest_identity", f"{field} must equal {expected}")
    if manifest.get("parent_revision") != {
        "revision_id": "doctrine-mesh-v2",
        "payload_digest": "sha256:6fdc5507d69ed5e6cdeb0aa9b79ed6365aa6b38cce258a0649ee527ba5e15fa8",
        "final_saved_digest": "sha256:1fdff84a9c1a8d34523183e6a8b1fe0ef70c53bde4ad3e054b94faa4a9b3076c",
    }:
        add(errors, "manifest_parent", "parent Doctrine Mesh V2 identity is not exact")
    if manifest.get("authority") != {
        "specification_only": True,
        "runtime_activation_authorized": False,
        "research_execution_authorized": False,
        "source_ingestion_authorized": False,
        "substantive_doctrine_implementation_authorized": False,
        "completed_doctrine_corpus": False,
        "qualified_theological_authority": False,
    }:
        add(errors, "manifest_authority", "specification-only authority ceiling is not exact")
    if manifest.get("hash_algorithm") != "sha256_over_canonical_lf_bytes_for_utf8_raw_bytes_otherwise":
        add(errors, "manifest_hash_algorithm", "unexpected file digest algorithm")
    if manifest.get("payload_list_digest_algorithm") != "sha256_over_canonical_compact_json_of_sorted_path_sha256_rows":
        add(errors, "manifest_hash_algorithm", "unexpected payload-list digest algorithm")
    if manifest.get("administrative_files_excluded_from_payload_digest") != sorted(ADMIN_FILES):
        add(errors, "manifest_admin_exclusions", "administrative exclusion list is not exact")
    _admin_time(errors, "manifest_generated_at", manifest.get("generated_at"))
    if rows != sorted(rows, key=lambda row: row.get("path", "")):
        add(errors, "manifest_file_rows", "payload rows must be path-sorted")
    if len({row.get("path") for row in rows}) != len(rows):
        add(errors, "manifest_file_rows", "payload paths must be unique")
    for row in rows:
        if set(row) != {"path", "sha256"} or not isinstance(row.get("path"), str) or not DIGEST_RE.fullmatch(str(row.get("sha256", ""))):
            add(errors, "manifest_file_rows", "every payload row needs only path and SHA-256")
    if manifest.get("payload_files") != rows:
        add(errors, "manifest_file_rows", "manifest rows do not equal exact payload")
    if manifest.get("payload_file_count") != len(rows):
        add(errors, "manifest_file_count", f"expected {len(rows)}")
    expected_payload = payload_digest(rows)
    if manifest.get("payload_digest") != expected_payload:
        add(errors, "manifest_payload_digest", f"expected {expected_payload}")
    expected_manifest_object = object_digest(manifest, omit=("manifest_digest",))
    if manifest.get("manifest_digest") != expected_manifest_object:
        add(errors, "manifest_object_digest", f"expected {expected_manifest_object}")
    expected_manifest_file = manifest_file_digest
    receipt_identity = {
        **identity,
        "schema_version": "logos.doctrine_marathon.validation_receipt.v3",
        "receipt_id": "DMV3-VALIDATION-003",
        "revision_manifest_ref": "revision-manifest.yaml",
        "validator_ref": "checks/validate_doctrine_marathon.py",
        "test_ref": "checks/test_validate_doctrine_marathon.py",
        "negative_fixture_ref": "checks/fixtures/negative-cases.json",
        "final_replay_command": (
            "python -B docs/roadmap/logos-stewardship-architecture-buildout/"
            "revisions/doctrine-marathon-v3/checks/validate_doctrine_marathon.py --mode final"
        ),
        "test_command": (
            "python -B docs/roadmap/logos-stewardship-architecture-buildout/"
            "revisions/doctrine-marathon-v3/checks/test_validate_doctrine_marathon.py"
        ),
    }
    for field, expected in receipt_identity.items():
        if receipt.get(field) != expected:
            add(errors, "validation_receipt_identity", f"{field} must equal {expected}")
    row_digests = {row.get("path"): row.get("sha256") for row in rows}
    if (
        receipt.get("validator_digest") != row_digests.get(receipt.get("validator_ref"))
        or receipt.get("test_digest") != row_digests.get(receipt.get("test_ref"))
        or receipt.get("negative_fixture_digest")
        != row_digests.get(receipt.get("negative_fixture_ref"))
    ):
        add(errors, "validation_receipt_validator", "validator, test, or fixture digest does not bind the payload row")
    if receipt.get("result") != "pass" or receipt.get("mode") != "prefinal" or receipt.get("error_count") != 0:
        add(errors, "validation_receipt_result", "receipt must record a zero-error strict prefinal pass")
    if receipt.get("payload_file_count") != len(rows):
        add(errors, "validation_receipt_payload", "receipt payload file count is stale")
    if receipt.get("payload_digest") != expected_payload:
        add(errors, "validation_receipt_payload", "receipt payload digest is stale")
    if receipt.get("revision_manifest_digest") != expected_manifest_file or receipt.get("revision_manifest_object_digest") != expected_manifest_object:
        add(errors, "validation_receipt_manifest", "receipt manifest identity is stale")
    expected_receipt_object = object_digest(receipt, omit=("receipt_digest",))
    if receipt.get("receipt_digest") != expected_receipt_object:
        add(errors, "validation_receipt_digest", f"expected {expected_receipt_object}")
    expected_metrics = {
        "payload_file_count": len(rows),
        "role_count": 18,
        "trigger_count": 19,
        "assignment_fixture_count": 3,
        "event_count": 0,
        "evidence_record_count": 0,
        "graph_node_count": 5,
        "graph_edge_count": 3,
        "open_expert_review_debt": 2,
        "error_count": 0,
    }
    if receipt.get("validator_metrics") != expected_metrics:
        add(errors, "validation_receipt_metrics", "validator metrics are not the exact frozen result")
    expected_negative_count = len(load_data("checks/fixtures/negative-cases.json"))
    if receipt.get("test_result") != {
        "status": "pass",
        "negative_case_count": expected_negative_count,
        "skipped": 0,
    }:
        add(errors, "validation_receipt_tests", "adversarial test result is not exact")
    for field in (
        "runtime_activation_authorized", "research_execution_authorized",
        "source_ingestion_authorized", "substantive_doctrine_implementation_authorized",
        "completed_doctrine_corpus", "qualified_theological_authority",
        "mutation_performed",
    ):
        if receipt.get(field) is not False:
            add(errors, f"validation_receipt_{field}", "must remain false")
    _admin_time(errors, "validation_receipt_observed_at", receipt.get("observed_at"))
    review_identity = {
        **identity,
        "schema_version": "logos.doctrine_marathon.independent_review.v3",
        "review_id": "DMV3-INDEPENDENT-REVIEW-003",
        "revision_manifest_ref": "revision-manifest.yaml",
        "reviewer_role": "independent-non-author-whole-work-checker",
        "independence_status": "non_author_read_only_cross_provider_unverified",
        "review_scope": "whole_frozen_payload_and_admin_contracts",
    }
    for field, expected in review_identity.items():
        if review.get(field) != expected:
            add(errors, "independent_review_identity", f"{field} must equal {expected}")
    if (
        review.get("result") != "pass_blocked_specification_only"
        or review.get("author_is_reviewer") is not False
    ):
        add(
            errors,
            "independent_review_result",
            "independent non-author review must pass only the transparently blocked specification",
        )
    if review.get("declared_release_blocker") != (
        "adversarial_harness_release_gate: V3 cannot release until the aggregate "
        "exact-oracle migration is complete and independently reviewed"
    ):
        add(
            errors,
            "independent_review_release_blocker",
            "review must retain the exact aggregate-harness release blocker",
        )
    if review.get("payload_file_count") != len(rows):
        add(errors, "independent_review_payload", "review payload file count is stale")
    if review.get("payload_digest") != expected_payload:
        add(errors, "independent_review_payload", "review payload digest is stale")
    if review.get("revision_manifest_digest") != expected_manifest_file or review.get("revision_manifest_object_digest") != expected_manifest_object:
        add(errors, "independent_review_manifest", "review manifest identity is stale")
    expected_review_object = object_digest(review, omit=("review_digest",))
    if review.get("review_digest") != expected_review_object:
        add(errors, "independent_review_digest", f"expected {expected_review_object}")
    reviewer_actor = review.get("reviewer_actor_instance_id")
    reviewer_attempt = review.get("reviewer_attempt_id")
    authors = review.get("author_actor_instance_ids")
    if (
        not isinstance(reviewer_actor, str) or len(reviewer_actor) < 8
        or not isinstance(reviewer_attempt, str) or len(reviewer_attempt) < 8
        or not isinstance(authors, list) or not authors
        or reviewer_actor in authors
        or len(authors) != len(set(authors))
    ):
        add(errors, "independent_review_identity", "reviewer actor/attempt must be explicit and distinct from every author")
    required_controls = {
        "authority_ceiling", "admin_freeze", "agent_independence",
        "citation_and_source_lineage", "context_normative_firewall",
        "dependency_and_reverse_blast_radius", "event_and_checkpoint_integrity",
        "prompt_neutrality", "public_nonclaims", "adversarial_cases",
    }
    controls = review.get("reviewed_controls")
    if not isinstance(controls, list) or set(controls) != required_controls or len(controls) != len(required_controls):
        add(errors, "independent_review_controls", "review coverage must equal the ten required control families")
    if review.get("unresolved_finding_counts") != {
        "critical": 0, "high": 0, "medium": 0, "low": 0
    }:
        add(errors, "independent_review_findings", "a passing review must have zero unresolved findings")
    if not isinstance(review.get("resolved_finding_ids"), list):
        add(errors, "independent_review_findings", "resolved finding IDs must be explicit")
    human_gates = review.get("unresolved_human_gates")
    required_human_gates = {
        "qualified_patristics_and_historical_theology_review",
        "qualified_source_rights_and_textual_review",
        "human_approved_normative_frame",
        "runtime_activation_decision",
        "substantive_doctrine_decision",
    }
    if not isinstance(human_gates, list) or not required_human_gates.issubset(set(human_gates)):
        add(errors, "independent_review_human_gates", "required unresolved human gates are missing")
    if review.get("cross_provider_verified") is not False:
        add(errors, "independent_review_cross_provider", "cross-provider independence is not verified")
    for field in (
        "runtime_activation_authorized", "research_execution_authorized",
        "source_ingestion_authorized", "substantive_doctrine_implementation_authorized",
        "completed_doctrine_corpus", "qualified_theological_authority",
        "mutation_performed",
    ):
        if review.get(field) is not False:
            add(errors, f"independent_review_{field}", "must remain false")
    _admin_time(errors, "independent_review_observed_at", review.get("observed_at"))
    authorization_identity = {
        **identity,
        "schema_version": "logos.doctrine_marathon.public_release_authorization.v3",
        "authorization_id": "DMV3-PUBLIC-RELEASE-003",
        "revision_root": (
            "docs/roadmap/logos-stewardship-architecture-buildout/"
            "revisions/doctrine-marathon-v3"
        ),
        "status": "authorized_for_one_public_specification_release",
        "authorization_source": "direct_owner_instruction_in_active_codex_task",
        "authorizing_principal": "Lowell Wong",
        "recorded_by": "Codex root",
    }
    for field, expected in authorization_identity.items():
        if authorization.get(field) != expected:
            add(errors, "public_release_authorization_identity", f"{field} must equal {expected}")
    expected_bound_payload = {
        "payload_file_count": len(rows),
        "payload_digest": expected_payload,
        "revision_manifest_ref": "revision-manifest.yaml",
        "revision_manifest_raw_sha256": expected_manifest_file,
        "revision_manifest_object_sha256": expected_manifest_object,
    }
    if authorization.get("bound_payload") != expected_bound_payload:
        add(errors, "public_release_authorization_payload", "authorization does not bind the exact frozen payload and manifest")
    expected_release_scope = {
        "content_set": "manifest_payload_plus_exact_final_admin_allowlist",
        "final_admin_allowlist": sorted(ADMIN_FILES),
        "excludes": [
            "all_other_repository_paths",
            "local_machine_artifacts",
            "private_conversations_and_raw_reasoning",
            "restricted_source_content",
            "secrets_credentials_and_signed_links",
        ],
    }
    if authorization.get("release_scope") != expected_release_scope:
        add(errors, "public_release_authorization_scope", "release scope or exclusions are not exact")
    expected_limits = {
        "public_artifact_release_only": True,
        "runtime_activation_authorized": False,
        "research_execution_authorized": False,
        "source_ingestion_authorized": False,
        "substantive_doctrine_implementation_authorized": False,
        "completed_doctrine_corpus": False,
        "qualified_theological_authority": False,
    }
    if authorization.get("authority_limits") != expected_limits:
        add(errors, "public_release_authorization_ceiling", "authorization exceeds the public specification release")
    expected_verification = {
        "attestation_mode": "direct_owner_instruction_procedurally_observed",
        "cryptographic_signature_verified": False,
        "human_identity_credential_verified": False,
        "verification_nonclaim": "This public receipt records a scoped instruction; it is not a cryptographic identity proof.",
    }
    if authorization.get("verification") != expected_verification:
        add(errors, "public_release_authorization_verification", "procedural verification disclosure is not exact")
    expected_authorization_object = object_digest(
        authorization, omit=("authorization_digest",)
    )
    if authorization.get("authorization_digest") != expected_authorization_object:
        add(errors, "public_release_authorization_digest", f"expected {expected_authorization_object}")
    _admin_time(errors, "public_release_authorization_observed_at", authorization.get("observed_at"))
    saved_identity = {
        **identity,
        "schema_version": "logos.doctrine_marathon.final_saved_version.v3",
        "save_id": "DMV3-SAVED-003",
        "status": "saved_specification_only",
        "revision_manifest_ref": "revision-manifest.yaml",
        "validation_receipt_ref": "checks/validation-receipt.json",
        "independent_review_ref": "checks/independent-review.json",
        "public_release_authorization_ref": "checks/public-release-authorization.json",
        "artifact_freeze_readiness": "ready_specification_artifact_only",
    }
    for field, expected in saved_identity.items():
        if saved.get(field) != expected:
            add(errors, "final_saved_identity", f"{field} must equal {expected}")
    if saved.get("revision_manifest_digest") != expected_manifest_file or saved.get("revision_manifest_object_digest") != expected_manifest_object:
        add(errors, "final_manifest_digest", f"expected {expected_manifest_file}")
    if saved.get("payload_digest") != expected_payload or saved.get("payload_file_count") != len(rows):
        add(errors, "final_payload", "final saved payload identity is stale")
    expected_receipt_file = receipt_file_digest
    expected_review_file = review_file_digest
    if saved.get("validation_receipt_file_digest") != expected_receipt_file or saved.get("validation_receipt_object_digest") != expected_receipt_object:
        add(errors, "final_validation_receipt_digest", "saved validation receipt identity is stale")
    if saved.get("independent_review_file_digest") != expected_review_file or saved.get("independent_review_object_digest") != expected_review_object:
        add(errors, "final_independent_review_digest", "saved review identity is stale")
    if (
        saved.get("public_release_authorization_file_digest")
        != authorization_file_digest
        or saved.get("public_release_authorization_object_digest")
        != expected_authorization_object
    ):
        add(errors, "final_public_release_authorization_digest", "saved authorization identity is stale")
    expected_final = object_digest(saved, omit=("final_digest",))
    if saved.get("final_digest") != expected_final:
        add(errors, "final_self_digest", f"expected {expected_final}")
    for field in (
        "runtime_activation_authorized", "research_execution_authorized",
        "source_ingestion_authorized", "substantive_doctrine_implementation_authorized",
        "completed_doctrine_corpus", "qualified_theological_authority",
    ):
        if saved.get(field) is not False:
            add(errors, f"final_{field}", "must remain false")
    _admin_time(errors, "final_saved_at", saved.get("saved_at"))
    return errors


def validate_manifest_and_receipts(final: bool) -> list[str]:
    errors: list[str] = []
    required = [
        "revision-manifest.yaml",
        "checks/validation-receipt.json",
        "checks/independent-review.json",
        "checks/public-release-authorization.json",
        "FINAL-SAVED-VERSION.yaml",
    ]
    if not final:
        return errors
    for relative in required:
        if not (ROOT / relative).is_file():
            add(errors, "freeze_missing_admin", relative)
    if errors:
        return errors
    return validate_admin_records(
        load_data("revision-manifest.yaml"),
        load_data("checks/validation-receipt.json"),
        load_data("checks/independent-review.json"),
        load_data("checks/public-release-authorization.json"),
        load_data("FINAL-SAVED-VERSION.yaml"),
        payload_rows(),
        file_digest(ROOT / "revision-manifest.yaml"),
        file_digest(ROOT / "checks/validation-receipt.json"),
        file_digest(ROOT / "checks/independent-review.json"),
        file_digest(ROOT / "checks/public-release-authorization.json"),
    )


def validate_no_linked_paths() -> list[str]:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        is_junction = bool(getattr(path, "is_junction", lambda: False)())
        if path.is_symlink() or is_junction:
            add(
                errors,
                "freeze_linked_path",
                f"{path.relative_to(ROOT).as_posix()} must be a regular in-tree path",
            )
    return errors


def validate_all(mode: str = "draft") -> tuple[list[str], dict[str, Any]]:
    final = mode == "final"
    strict_payload = mode in {"prefinal", "final"}
    errors: list[str] = []
    constitution = load_data("constitution.yaml")
    goal = load_data("state/goal.yaml")
    campaign = load_data("campaign.yaml")
    mesh = load_data("mesh/agent-mesh.v3.json")
    catalog = load_data("mesh/role-catalog.yaml")
    assignments = load_data("mesh/examples/design-time-independence-fixture.json")
    completeness = load_data("mesh/completeness-auditor-v3.yaml")
    triggers = load_data("firewall/trigger-matrix.yaml")
    ledger = load_data("events/event-ledger.json")
    evidence = load_data("evidence/evidence-registry.json")
    authority = load_data("graph/authority-registry.yaml")
    graph = load_data("graph/example-graph.json")
    debts = load_data("debt/initial-review-debt.json")
    public = load_data("transparency/public-status.json")
    mistake = load_data("redteam/ai-mistake-escalation-2026-08-27.yaml")
    prompt = (ROOT / "DOCTRINE_MARATHON_MASTER_PROMPT.md").read_text(encoding="utf-8")
    errors.extend(validate_schemas())
    errors.extend(validate_constitution(constitution))
    errors.extend(validate_goal(goal, strict_payload))
    errors.extend(validate_campaign(campaign))
    errors.extend(validate_role_catalog(catalog, constitution))
    errors.extend(validate_mesh(mesh, catalog))
    errors.extend(validate_role_assignments(assignments, mesh, strict_payload))
    errors.extend(validate_completeness(completeness))
    errors.extend(validate_triggers(triggers, mesh, catalog))
    errors.extend(validate_event_ledger(ledger, strict_payload))
    errors.extend(validate_evidence_registry(evidence, strict_payload))
    errors.extend(validate_authority_registry(authority, strict_payload))
    errors.extend(validate_graph(graph, strict_payload, evidence, authority))
    errors.extend(validate_debts(debts, graph, catalog, constitution))
    errors.extend(validate_public_status(public, strict_payload))
    errors.extend(validate_mistake_escalation(mistake))
    errors.extend(validate_prompt(prompt))
    # Prefinal freezes a truthful blocked specification. The deliberate
    # repository-adapter blocker belongs only to the public final-release gate;
    # all other strict payload checks still run in prefinal mode.
    errors.extend(validate_adversarial_harness_migration(final))
    errors.extend(validate_terminal_examples())
    errors.extend(validate_public_boundary())
    errors.extend(validate_no_linked_paths())
    generated_errors, _local_generated_count = validate_generated_inventory()
    errors.extend(generated_errors)
    errors.extend(validate_manifest_and_receipts(final))
    metrics = {
        "mode": mode,
        "payload_file_count": len(payload_files()),
        "role_count": len(mesh.get("roles", [])),
        "trigger_count": len(triggers.get("triggers", [])),
        "assignment_fixture_count": len(assignments.get("assignments", [])),
        "event_count": len(ledger.get("events", [])),
        "evidence_record_count": sum(len(evidence.get(field, [])) for field in ("source_records", "translation_lineages", "influence_hypotheses", "claim_records")),
        "graph_node_count": len(graph.get("nodes", [])),
        "graph_edge_count": len(graph.get("edges", [])),
        "open_expert_review_debt": sum(1 for row in debts if row.get("status") == "open"),
        "error_count": len(errors),
    }
    return errors, metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("draft", "prefinal", "final"), default="draft")
    args = parser.parse_args()
    errors, metrics = validate_all(args.mode)
    print(json.dumps({"status": "pass" if not errors else "fail", "metrics": metrics, "errors": sorted(errors)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
