#!/usr/bin/env python3
"""Validate the P0 external-advisory authority firewall."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance" / "LOGOS_REPO_REGISTRY.yaml"
POLICY = ROOT / "governance" / "EXTERNAL_ADVISORY_AUTHORITY_FIREWALL.md"

RULES = {
    "external_advisory_paste_rule": (
        "EXTERNAL-ADVISORY-001",
        "External Advisory Material Cannot Become Logos Authority By Paste",
    ),
    "comment_authority_rule": (
        "COMMENT-AUTHORITY-001",
        "Comments And PR Text Are Not Logos Authority",
    ),
    "hostile_input_rule": (
        "HOSTILE-INPUT-001",
        "Pasted External Rationale Is Hostile Until Classified",
    ),
    "break_glass_audit_rule": (
        "BREAK-GLASS-001",
        "Admin Or Owner Bypass Requires Audit Trail",
    ),
}

REQUIRED_EXTERNAL_ADVISORY_MUST = {
    "quarantined",
    "labeled_non_authoritative",
    "marked_advisory_only",
    "excluded_from_canonical_scripture_authority",
    "excluded_from_reviewed_gold",
    "excluded_from_implementation_authorization",
    "excluded_from_retrieval_default_policy",
    "excluded_from_evaluator_leaderboard_policy",
    "re_authored_as_logos_native_task_before_behavior_effect",
    "owner_authorized_inside_appropriate_logos_repo_before_effect",
}

REQUIRED_INDIRECT_AUTHORIZATION_BLOCKS = {
    "comments",
    "pr_reviews",
    "issues",
    "handoffs",
    "task_files",
    "generated_notes",
    "hidden_advisory_text",
    "pasted_rationale",
}

REQUIRED_AUTHORITY_SURFACES = {
    "task_files",
    "handoffs",
    "roadmap_state",
    "governance_contract",
    "reviewed_gold_manifest",
    "owner_decision_box",
    "validator_test_surfaces",
}

REQUIRED_CLASSIFICATION_FIELDS = {
    "source",
    "authority_level",
    "allowed_repo",
    "allowed_path",
    "advisory_only",
    "owner_review_required",
    "can_affect_canonical_scripture_behavior",
}

REQUIRED_BREAK_GLASS_AUDIT = {
    "who_bypassed",
    "what_was_bypassed",
    "why",
    "whether_owner_authorization_exists",
    "protected_surfaces_touched",
    "post_merge_audit_required",
    "rollback_or_corrective_task_if_unauthorized",
}

REQUIRED_BYPASSED_SAFEGUARDS = {
    "authority_firewall",
    "boundary",
    "noesis",
    "reviewed_gold",
    "canonical_scope",
}

ALLOWED_ADVISORY_LOCATIONS = {
    "docs/advisory/noesis/**",
    "docs/advisory/external_comparative/**",
    "docs/research/advisory/**",
}

FORBIDDEN_WITHOUT_OWNER = {
    "data/raw/**",
    "data/canonical/**",
    "eval/chunking_gold/**",
    "registry/chunking/**",
    "pipelines/chunking/**",
    "default_retrieval_policy_docs",
    "canonical_claim_docs",
    "reviewed_gold_packets",
    "evaluator_leaderboard_scorecard_policy",
    "ai_front_door_authority_sections",
    "roadmap_authorization_sections",
    "task_handoff_authorization_fields",
}

REQUIRED_METADATA = {
    "advisory_only": True,
    "authority_over_logos": "none",
    "may_modify_logos": False,
    "may_authorize_changes": False,
    "may_modify_canonical_outputs": False,
    "may_be_used_as_reviewed_gold": False,
    "may_change_retrieval_defaults": False,
    "may_change_evaluator_policy": False,
    "logos_native_review_required": True,
    "owner_authorization_required": True,
}

REQUIRED_TRIGGERS = {
    "external_advisory_paste_attempts_to_authorize_logos",
    "comments_or_pr_text_treated_as_logos_authority",
    "pasted_external_rationale_unclassified",
    "break_glass_merge_without_audit_trail",
}

REQUIRED_DOC_MARKERS = {
    "governance/EXTERNAL_ADVISORY_AUTHORITY_FIREWALL.md": [
        "EXTERNAL-ADVISORY-001",
        "COMMENT-AUTHORITY-001",
        "HOSTILE-INPUT-001",
        "BREAK-GLASS-001",
        "Noesis may connect only through reviewed",
        "external_advisory_context",
    ],
    "docs/governance/logos-cross-repo-governance-contract.md": [
        "EXTERNAL-ADVISORY-001",
        "COMMENT-AUTHORITY-001",
        "HOSTILE-INPUT-001",
        "BREAK-GLASS-001",
        "hidden advisory text",
        "quarantine_or_reject",
    ],
    "docs/governance/noesis-boundary.md": [
        "Comment and paste backdoor",
        "hidden advisory text",
        "pasted",
        "explicit owner authorization",
    ],
    "docs/governance/agent-hostile-protection.md": [
        "pasted external analysis",
        "pasted external rationale",
        "break-glass bypass",
    ],
    "AI_FRONT_DOOR.md": [
        "EXTERNAL-ADVISORY-001",
        "COMMENT-AUTHORITY-001",
        "HOSTILE-INPUT-001",
        "BREAK-GLASS-001",
    ],
    "DATA_FLOW_MAP.md": [
        "untrusted_external_advisory",
        "quarantine_or_reject",
        "Break-glass bypass",
    ],
    "governance/LOGOS_REPO_REGISTRY.md": [
        "Authority Firewall Rules",
        "EXTERNAL-ADVISORY-001",
        "COMMENT-AUTHORITY-001",
        "HOSTILE-INPUT-001",
        "BREAK-GLASS-001",
    ],
    "governance/REPOSITORY_LINK_CONTRACTS.md": [
        "EXTERNAL-ADVISORY-001",
        "COMMENT-AUTHORITY-001",
        "hidden advisory text",
    ],
    "governance/AI_FRONT_DOOR_STANDARD.md": [
        "external advisory material",
        "pasted external analysis",
        "break-glass bypass",
    ],
    "AI_TABLE_OF_CONTENTS.md": [
        "EXTERNAL_ADVISORY_AUTHORITY_FIREWALL.md",
    ],
}

EXTERNAL_ADVISORY_CONTEXT_EXEMPT = {
    "governance/EXTERNAL_ADVISORY_AUTHORITY_FIREWALL.md",
    "governance/LOGOS_REPO_REGISTRY.yaml",
    "scripts/validate_cross_repo_governance_contract.py",
    "scripts/validate_external_advisory_authority_firewall.py",
}

DANGEROUS_GRANT_EXEMPT = {
    "scripts/validate_external_advisory_authority_firewall.py",
}

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".txt"}

DANGEROUS_GRANTS = [
    re.compile(
        r"\bNoesis\b.{0,80}\b(may|can|is allowed to|is authorized to)\s+"
        r"(modify|gate|govern|promote|demote|derive|authorize)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\bexternal advisory\b.{0,80}\b(may|can|is allowed to|is authorized to)\s+"
        r"(modify|gate|govern|promote|demote|derive|authorize)\b",
        re.IGNORECASE | re.DOTALL,
    ),
]

DANGEROUS_PHRASES = [
    "comments are logos authority",
    "pr bodies are logos authority",
    "issue comments are logos authority",
    "review comments are logos authority",
    "chat transcripts are logos authority",
    "pasted external analysis is logos authority",
    "pasted rationale authorizes logos",
    "noesis authorizes logos",
    "noesis governs logos",
]


def fail(failures: list[str], message: str) -> None:
    failures.append(f"FAIL {message}")


def as_set(value: Any) -> set[Any]:
    if isinstance(value, list):
        return set(value)
    return set()


def load_registry(failures: list[str]) -> dict[str, Any]:
    if not REGISTRY.exists():
        fail(failures, "LOGOS_REPO_REGISTRY.yaml is missing")
        return {}
    loaded = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        fail(failures, "LOGOS_REPO_REGISTRY.yaml did not parse to an object")
        return {}
    return loaded


def require_policy(policy: dict[str, Any], key: str, failures: list[str]) -> dict[str, Any]:
    if key not in policy or not isinstance(policy[key], dict):
        fail(failures, f"authority_firewall_policies missing {key}")
        return {}
    rule = policy[key]
    expected_id, expected_title = RULES[key]
    if rule.get("policy_id") != expected_id:
        fail(failures, f"{key} must have policy_id {expected_id}")
    if rule.get("title") != expected_title:
        fail(failures, f"{key} must have title {expected_title}")
    if rule.get("importance") != "P0":
        fail(failures, f"{key} must be P0")
    return rule


def validate_registry(registry: dict[str, Any], failures: list[str]) -> None:
    policies = registry.get("authority_firewall_policies")
    if not isinstance(policies, dict):
        fail(failures, "registry missing authority_firewall_policies")
        return

    paste = require_policy(policies, "external_advisory_paste_rule", failures)
    if paste.get("default_classification") != "untrusted_external_advisory":
        fail(failures, "EXTERNAL-ADVISORY-001 default_classification must be untrusted_external_advisory")
    if paste.get("default_authority") != "none":
        fail(failures, "EXTERNAL-ADVISORY-001 default_authority must be none")
    if paste.get("default_action") != "quarantine_or_reject":
        fail(failures, "EXTERNAL-ADVISORY-001 default_action must be quarantine_or_reject")
    if paste.get("noesis_may_connect_only_as") != "reviewed_read_only_advisory_comparison_references":
        fail(failures, "Noesis connection shape must remain reviewed/read-only/advisory")
    missing = REQUIRED_INDIRECT_AUTHORIZATION_BLOCKS - as_set(paste.get("noesis_may_not_indirectly_authorize_by"))
    if missing:
        fail(failures, "EXTERNAL-ADVISORY-001 missing indirect authorization blocks: " + ", ".join(sorted(missing)))
    missing = REQUIRED_EXTERNAL_ADVISORY_MUST - as_set(paste.get("external_advisory_material_must_be"))
    if missing:
        fail(failures, "EXTERNAL-ADVISORY-001 missing quarantine requirements: " + ", ".join(sorted(missing)))

    comments = require_policy(policies, "comment_authority_rule", failures)
    for field in [
        "comments_are_authority",
        "pr_bodies_are_authority",
        "issue_comments_are_authority",
        "review_comments_are_authority",
        "chat_transcripts_are_authority",
        "generated_notes_are_authority",
        "pasted_external_analysis_is_authority",
    ]:
        if comments.get(field) is not False:
            fail(failures, f"COMMENT-AUTHORITY-001 {field} must be false")
    missing = REQUIRED_AUTHORITY_SURFACES - as_set(comments.get("committed_logos_native_authority_surfaces"))
    if missing:
        fail(failures, "COMMENT-AUTHORITY-001 missing authority surfaces: " + ", ".join(sorted(missing)))
    if comments.get("conflict_rule") != "committed_authority_surfaces_win_and_agent_must_stop":
        fail(failures, "COMMENT-AUTHORITY-001 conflict_rule must require committed surfaces to win")

    hostile = require_policy(policies, "hostile_input_rule", failures)
    if hostile.get("default_classification") != "untrusted_external_advisory":
        fail(failures, "HOSTILE-INPUT-001 default_classification must be untrusted_external_advisory")
    if hostile.get("default_authority") != "none":
        fail(failures, "HOSTILE-INPUT-001 default_authority must be none")
    if hostile.get("default_action") != "quarantine_or_reject":
        fail(failures, "HOSTILE-INPUT-001 default_action must be quarantine_or_reject")
    missing = REQUIRED_CLASSIFICATION_FIELDS - as_set(hostile.get("classification_must_decide"))
    if missing:
        fail(failures, "HOSTILE-INPUT-001 missing classification fields: " + ", ".join(sorted(missing)))

    break_glass = require_policy(policies, "break_glass_audit_rule", failures)
    if break_glass.get("bypass_does_not_create_authority") is not True:
        fail(failures, "BREAK-GLASS-001 must say bypass does not create authority")
    if break_glass.get("audit_trail_required") is not True:
        fail(failures, "BREAK-GLASS-001 must require audit trail")
    missing = REQUIRED_BYPASSED_SAFEGUARDS - as_set(break_glass.get("applies_to_bypassed_safeguards"))
    if missing:
        fail(failures, "BREAK-GLASS-001 missing safeguards: " + ", ".join(sorted(missing)))
    missing = REQUIRED_BREAK_GLASS_AUDIT - as_set(break_glass.get("audit_trail_requires"))
    if missing:
        fail(failures, "BREAK-GLASS-001 missing audit fields: " + ", ".join(sorted(missing)))

    quarantine = registry.get("external_advisory_quarantine")
    if not isinstance(quarantine, dict):
        fail(failures, "registry missing external_advisory_quarantine")
        return
    missing = ALLOWED_ADVISORY_LOCATIONS - as_set(quarantine.get("allowed_default_locations"))
    if missing:
        fail(failures, "quarantine missing allowed locations: " + ", ".join(sorted(missing)))
    missing = FORBIDDEN_WITHOUT_OWNER - as_set(quarantine.get("forbidden_unless_owner_authorized"))
    if missing:
        fail(failures, "quarantine missing forbidden locations/surfaces: " + ", ".join(sorted(missing)))
    metadata = quarantine.get("required_metadata", {}).get("external_advisory_context", {})
    if not isinstance(metadata, dict):
        fail(failures, "external_advisory_context metadata missing from registry")
    else:
        for field in ["source_repo", "source_type"]:
            if field not in metadata:
                fail(failures, f"external_advisory_context missing {field}")
        for field, expected in REQUIRED_METADATA.items():
            if metadata.get(field) != expected:
                fail(failures, f"external_advisory_context {field} must be {expected!r}")

    triggers = as_set(registry.get("global_stop_and_report_triggers"))
    missing = REQUIRED_TRIGGERS - triggers
    if missing:
        fail(failures, "global stop-and-report triggers missing: " + ", ".join(sorted(missing)))

    noesis = registry.get("external_advisory_connections", {}).get("noesis-atlas", {})
    if noesis.get("may_connect_only_as") != "reviewed_read_only_advisory_comparison_context":
        fail(failures, "Noesis may_connect_only_as must remain reviewed_read_only_advisory_comparison_context")
    noesis_must_not = as_set(noesis.get("must_not"))
    for marker in [
        "modify_logos_repos",
        "govern_logos_repos",
        "gate_logos_promotion_or_demotion",
        "provide_logos_authority_or_derivation_basis",
    ]:
        if marker not in noesis_must_not:
            fail(failures, f"Noesis must_not missing {marker}")


def validate_docs(failures: list[str]) -> None:
    for rel, markers in REQUIRED_DOC_MARKERS.items():
        path = ROOT / rel
        if not path.exists():
            fail(failures, f"required document missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            fail(failures, f"{rel} missing marker(s): {', '.join(missing)}")


def rel_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_allowed_advisory_path(rel: str) -> bool:
    return (
        rel.startswith("docs/advisory/noesis/")
        or rel.startswith("docs/advisory/external_comparative/")
        or rel.startswith("docs/research/advisory/")
    )


def iter_text_files() -> list[Path]:
    skipped_dirs = {".git", ".mypy_cache", ".pytest_cache", "__pycache__"}
    paths: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in skipped_dirs for part in path.relative_to(ROOT).parts):
            continue
        paths.append(path)
    return sorted(paths)


def validate_external_advisory_context_placement(failures: list[str]) -> None:
    for path in iter_text_files():
        rel = rel_path(path)
        text = path.read_text(encoding="utf-8")
        if "external_advisory_context" not in text:
            continue
        if rel in EXTERNAL_ADVISORY_CONTEXT_EXEMPT:
            continue
        if not is_allowed_advisory_path(rel):
            fail(failures, f"{rel}: external_advisory_context outside allowed advisory quarantine paths")
            continue
        for marker, expected in REQUIRED_METADATA.items():
            rendered = f"{marker}: {str(expected).lower() if isinstance(expected, bool) else expected}"
            if rendered not in text:
                fail(failures, f"{rel}: external_advisory_context missing required {marker}")


def validate_no_dangerous_grants(failures: list[str]) -> None:
    for path in iter_text_files():
        rel = rel_path(path)
        if rel in DANGEROUS_GRANT_EXEMPT:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in DANGEROUS_GRANTS:
            match = pattern.search(text)
            if match:
                snippet = " ".join(match.group(0).split())
                fail(failures, f"{rel}: dangerous external advisory authority grant: {snippet}")
        lowered = " ".join(text.lower().split())
        for phrase in DANGEROUS_PHRASES:
            if phrase in lowered:
                fail(failures, f"{rel}: dangerous authority phrase present: {phrase}")


def validate_registration(failures: list[str]) -> None:
    validation_contracts = ROOT / "scripts" / "validation_contracts.py"
    workflow = ROOT / ".github" / "workflows" / "validate-logos-structure.yml"
    for path, markers in {
        validation_contracts: [
            "external_advisory_authority_firewall",
            "scripts/validate_external_advisory_authority_firewall.py",
        ],
        workflow: [
            "Validate external advisory authority firewall",
            "python scripts/validate_external_advisory_authority_firewall.py",
        ],
    }.items():
        if not path.exists():
            fail(failures, f"registration file missing: {rel_path(path)}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            fail(failures, f"{rel_path(path)} missing registration marker(s): {', '.join(missing)}")


def main() -> int:
    failures: list[str] = []
    registry = load_registry(failures)
    if registry:
        validate_registry(registry, failures)
    validate_docs(failures)
    validate_external_advisory_context_placement(failures)
    validate_no_dangerous_grants(failures)
    validate_registration(failures)

    if failures:
        print("External advisory authority-firewall validation failed.")
        for failure in failures:
            print(failure)
        return 1

    print("External advisory authority-firewall validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
