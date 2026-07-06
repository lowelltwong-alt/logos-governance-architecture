#!/usr/bin/env python3
"""Shared validation helpers for doctrine-genealogy schema contracts.

These helpers validate contracts and future examples only. They do not create,
promote, or authorize doctrine-genealogy records.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "doctrine_genealogy"
EXAMPLE_DIR = ROOT / "examples" / "doctrine_genealogy"
GATE_TRIGGER_REGISTRY = SCHEMA_DIR / "gate_trigger_registry.v1.yaml"

ORTHODOXY_STATUSES = {
    "orthodox_core",
    "orthodox_permitted_diversity",
    "disputed_within_orthodoxy",
    "heterodox",
    "non_christian_comparative",
    "unclassified_candidate",
}

CLAIM_ROLES = {
    "historical_description",
    "normative_position",
    "comparative_note",
}

TRADITION_SCOPES = {
    "reformed",
    "arminian_wesleyan",
    "baptist",
    "anglican",
    "lutheran",
    "presbyterian",
    "methodist",
    "pentecostal_charismatic",
    "patristic_creedal",
    "roman_catholic",
    "eastern_orthodox",
    "oriental_orthodox",
    "church_of_the_east",
    "pre_division_patristic",
}

AUTHORITY_RUNGS = ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7"]
AUTHORITY_RANK = {rung: index for index, rung in enumerate(AUTHORITY_RUNGS)}

EDGE_VERBS = {
    "derives_from",
    "depends_on",
    "clarifies",
    "modifies",
    "systematizes",
    "reads_back_into",
    "interprets_passage",
    "cites_source",
    "receives",
    "rejects",
    "counters",
    "partially_aligns_with",
    "tensions_with",
}

FORBIDDEN_EDGE_VERBS = {
    "condemns",
    "is_condemned_by",
    "related_to",
    "influences",
    "requires_original_language_review",
    "requires_textual_critical_review",
}

DERIVATION_FAMILY_VERBS = {
    "derives_from",
    "clarifies",
    "modifies",
}

LATER_ACT_VERBS = {
    "reads_back_into",
    "systematizes",
}

EDGE_STATUSES = {
    "retrieval_candidate",
    "derived_view",
    "proposed_relationship",
    "asserted_relationship",
}

REVIEW_STATUSES = {
    "unreviewed",
    "in_review",
    "reviewed",
}

GATE_STATUSES = {
    "not_required",
    "required_pending",
    "complete",
}

PROVENANCE_REQUIRED_FIELDS = {
    "source_basis",
    "claim_role",
    "authority_zone",
    "tradition_scope",
    "orthodoxy_status",
    "orthodoxy_basis_refs",
    "asserted_or_inferred",
    "method",
    "lifecycle_status",
    "review_status",
    "reviewer_or_owner_decision_ref",
    "upstream_deps",
    "known_counterclaims",
    "contested_status",
    "original_language_review",
    "original_language_review_ref",
    "textual_critical_review",
    "textual_critical_review_ref",
    "downstream_risk_note",
    "provenance_note",
}

NON_AUTHORITY_BLOCK = {
    "is_derived_artifact": True,
    "creates_scripture_authority": False,
    "creates_doctrine_authority": False,
    "creates_graph_or_retrieval_truth": False,
    "advisory_material_authority": "none",
}

NON_FLOOR_CLASSIFICATION_FIELDS = {
    "authority_rung",
    "ladder_rung",
    "tradition_scope",
    "verdict",
    "verb",
}

FLOOR_CLASSIFICATION_VALUES = {
    "orthodoxy_status": {"unclassified_candidate"},
    "claim_role": {"historical_description"},
    "edge_status": {"retrieval_candidate"},
    "review_status": {"unreviewed"},
}


class DoctrineGenealogyValidationError(ValueError):
    """Raised when a doctrine-genealogy contract or record is invalid."""


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise DoctrineGenealogyValidationError(f"{rel(path)}: expected JSON object")
    return data


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise DoctrineGenealogyValidationError(f"{rel(path)}: expected YAML object")
    return data


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def collect_enum_values(schema: dict[str, Any], enum_name: str) -> set[str]:
    found: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("enum") and enum_name in str(value.get("title", "")):
                found.update(item for item in value["enum"] if isinstance(item, str))
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(schema)
    return found


def iter_records(*subdirs: str) -> list[tuple[Path, dict[str, Any]]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    if not EXAMPLE_DIR.exists():
        return records
    roots = [EXAMPLE_DIR / subdir for subdir in subdirs] if subdirs else [EXAMPLE_DIR]
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.yaml")):
            records.append((path, load_yaml(path)))
    return records


def require_schema_comment(path: Path, schema: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if schema.get("$comment") != "draft, non-authorizing, owner decisions D1-D10 apply":
        failures.append(f"{rel(path)}: missing required non-authorizing $comment")
    governance = schema.get("x-governance")
    if not isinstance(governance, dict):
        failures.append(f"{rel(path)}: missing x-governance metadata")
        return failures
    for key in (
        "object_type",
        "trust_zone",
        "lifecycle_status",
        "provenance_note",
        "reason_for_inclusion",
    ):
        if not governance.get(key):
            failures.append(f"{rel(path)}: x-governance missing {key}")
    return failures


def schema_text_has_only_floor_defaults(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    forbidden_defaults = [
        '"default": "orthodox_core"',
        '"default": "orthodox_permitted_diversity"',
        '"default": "disputed_within_orthodoxy"',
        '"default": "heterodox"',
        '"default": "non_christian_comparative"',
        '"default": "normative_position"',
        '"default": "asserted_relationship"',
    ]
    for token in forbidden_defaults:
        if token in text:
            failures.append(f"{rel(path)}: forbidden non-floor schema default {token}")
    return failures


def validate_codex_theology_tripwire_record(
    record: Any,
    *,
    label: str,
    inherited_decision_basis: bool = False,
) -> list[str]:
    failures: list[str] = []
    if isinstance(record, dict):
        has_basis = inherited_decision_basis or bool(record.get("decision_basis"))
        for key, value in record.items():
            if key in FLOOR_CLASSIFICATION_VALUES:
                allowed_floor = FLOOR_CLASSIFICATION_VALUES[key]
                if isinstance(value, str) and value not in allowed_floor and not has_basis:
                    failures.append(
                        f"{label}: {key}={value} requires decision_basis under V-CODEX-1"
                    )
            elif key in NON_FLOOR_CLASSIFICATION_FIELDS:
                if value is not None and not has_basis:
                    failures.append(
                        f"{label}: {key}={value} requires decision_basis under V-CODEX-1"
                    )

            child_label = f"{label}.{key}"
            failures.extend(
                validate_codex_theology_tripwire_record(
                    value,
                    label=child_label,
                    inherited_decision_basis=has_basis,
                )
            )
    elif isinstance(record, list):
        for index, item in enumerate(record):
            failures.extend(
                validate_codex_theology_tripwire_record(
                    item,
                    label=f"{label}[{index}]",
                    inherited_decision_basis=inherited_decision_basis,
                )
            )
    return failures


def highest_authority_rung(source_basis: list[dict[str, Any]]) -> str | None:
    rungs = [
        item.get("ladder_rung")
        for item in source_basis
        if isinstance(item, dict) and item.get("ladder_rung") in AUTHORITY_RANK
    ]
    if not rungs:
        return None
    return min(rungs, key=lambda rung: AUTHORITY_RANK[rung])


def validate_provenance_block(
    provenance: dict[str, Any],
    *,
    relationship_status: str | None = None,
    label: str = "record",
) -> list[str]:
    failures: list[str] = []
    missing = sorted(PROVENANCE_REQUIRED_FIELDS - set(provenance))
    if missing:
        failures.append(f"{label}: missing doctrine_provenance fields {', '.join(missing)}")
        return failures

    source_basis = provenance.get("source_basis")
    if not isinstance(source_basis, list) or not source_basis:
        failures.append(f"{label}: source_basis must contain at least one entry")
        source_basis = []
    else:
        for index, source in enumerate(source_basis):
            if not isinstance(source, dict):
                failures.append(f"{label}: source_basis[{index}] must be an object")
                continue
            rung = source.get("ladder_rung")
            if rung not in AUTHORITY_RANK:
                failures.append(f"{label}: source_basis[{index}].ladder_rung is not S0-S7")
            if not source.get("ref"):
                failures.append(f"{label}: source_basis[{index}].ref is required")
            if isinstance(source.get("ref"), str) and source["ref"].startswith(
                ("evidence_packet/", "packet/")
            ):
                failures.append(f"{label}: V-PKT-3 evidence packets may not be source_basis")
            if source.get("citation_mode") not in {"quotation", "paraphrase", "allusion", "summary"}:
                failures.append(f"{label}: source_basis[{index}].citation_mode is invalid")

    if provenance.get("claim_role") not in CLAIM_ROLES:
        failures.append(f"{label}: claim_role is not in the closed vocabulary")
    if provenance.get("authority_zone") not in AUTHORITY_RANK:
        failures.append(f"{label}: authority_zone is not S0-S7")
    if provenance.get("orthodoxy_status") not in ORTHODOXY_STATUSES:
        failures.append(f"{label}: orthodoxy_status is not in the closed vocabulary")
    if provenance.get("review_status") not in REVIEW_STATUSES:
        failures.append(f"{label}: review_status is not in the closed vocabulary")
    if provenance.get("original_language_review") not in GATE_STATUSES:
        failures.append(f"{label}: original_language_review is not in the closed vocabulary")
    if provenance.get("textual_critical_review") not in GATE_STATUSES:
        failures.append(f"{label}: textual_critical_review is not in the closed vocabulary")

    tradition_scope = provenance.get("tradition_scope")
    if tradition_scope is not None and tradition_scope not in TRADITION_SCOPES:
        failures.append(f"{label}: tradition_scope is not in the closed vocabulary")

    expected_zone = highest_authority_rung(source_basis)
    if expected_zone and provenance.get("authority_zone") != expected_zone:
        failures.append(
            f"{label}: authority_zone must equal highest cited source_basis rung {expected_zone}"
        )

    orthodoxy_status = provenance.get("orthodoxy_status")
    basis_refs = provenance.get("orthodoxy_basis_refs")
    if not isinstance(basis_refs, list):
        failures.append(f"{label}: orthodoxy_basis_refs must be a list")
        basis_refs = []

    if orthodoxy_status == "orthodox_core":
        if not basis_refs:
            failures.append(f"{label}: orthodox_core requires orthodoxy_basis_refs")
        if not any(
            isinstance(source, dict) and source.get("ladder_rung") == "S1"
            for source in source_basis
        ):
            failures.append(f"{label}: orthodox_core requires a cited S1 boundary-instrument basis")
        if all(
            isinstance(source, dict)
            and source.get("ladder_rung") in {"S3", "S4", "S5", "S6", "S7"}
            for source in source_basis
        ):
            failures.append(f"{label}: source at S3 or below cannot be sole basis for orthodox_core")

    if orthodoxy_status == "heterodox" and not basis_refs:
        failures.append(f"{label}: heterodox requires at least one assessment/basis ref")

    if provenance.get("claim_role") == "normative_position":
        if tradition_scope is None and orthodoxy_status != "orthodox_core":
            failures.append(
                f"{label}: normative_position without tradition_scope requires orthodox_core"
            )
        if any(
            isinstance(source, dict) and source.get("ladder_rung") == "S6"
            for source in source_basis
        ):
            failures.append(
                f"{label}: S6 scholarly_analysis cannot ground a normative_position"
            )

    if orthodoxy_status != "unclassified_candidate" and any(
        isinstance(source, dict) and source.get("ladder_rung") == "S6"
        for source in source_basis
    ):
        failures.append(
            f"{label}: S6 scholarly_analysis cannot ground orthodoxy_status or boundary classification"
        )

    if relationship_status == "asserted_relationship":
        if provenance.get("original_language_review") == "required_pending":
            failures.append(f"{label}: asserted_relationship cannot have pending original-language gate")
        if provenance.get("textual_critical_review") == "required_pending":
            failures.append(f"{label}: asserted_relationship cannot have pending textual-critical gate")
        if provenance.get("method") == "ai_staged" and provenance.get("review_status") == "unreviewed":
            failures.append(f"{label}: ai_staged + unreviewed cannot be asserted_relationship")
        if not provenance.get("known_counterclaims") and not provenance.get(
            "reviewer_or_owner_decision_ref"
        ):
            failures.append(
                f"{label}: empty known_counterclaims at asserted status requires reviewer_or_owner_decision_ref"
            )

    return failures


def validate_genealogy_edge_record(
    record: dict[str, Any],
    *,
    object_index: dict[str, dict[str, Any]] | None = None,
    label: str = "edge",
) -> list[str]:
    failures: list[str] = []
    verb = record.get("verb")
    if verb in FORBIDDEN_EDGE_VERBS:
        failures.append(f"{label}: forbidden doctrine-genealogy verb {verb}")
    if verb not in EDGE_VERBS:
        failures.append(f"{label}: verb is not in the approved Kernel A3 registry")
    if record.get("edge_status") not in EDGE_STATUSES:
        failures.append(f"{label}: edge_status is not in the closed vocabulary")

    status = record.get("edge_status")
    provenance = record.get("doctrine_provenance")
    if status in {"proposed_relationship", "asserted_relationship"} and not isinstance(provenance, dict):
        failures.append(f"{label}: proposed/asserted edges require doctrine_provenance")
    elif isinstance(provenance, dict):
        failures.extend(
            validate_provenance_block(provenance, relationship_status=status, label=label)
        )

    if object_index and verb in DERIVATION_FAMILY_VERBS:
        subject = object_index.get(str(record.get("subject_ref")))
        obj = object_index.get(str(record.get("object_ref")))
        if subject and obj:
            subject_date = subject.get("date_block", {})
            object_date = obj.get("date_block", {})
            subject_earliest = subject_date.get("date_earliest")
            object_latest = object_date.get("date_latest")
            if (
                isinstance(subject_earliest, int)
                and isinstance(object_latest, int)
                and subject_earliest > object_latest
            ):
                failures.append(
                    f"{label}: V-TIME-1 later-to-earlier derivation requires reads_back_into or systematizes"
                )

    return failures


def validate_evidence_packet_record(record: dict[str, Any], *, label: str = "packet") -> list[str]:
    failures: list[str] = []
    if record.get("non_authority_block") != NON_AUTHORITY_BLOCK:
        failures.append(f"{label}: non_authority_block must match Kernel D1 constants exactly")

    sections = record.get("sections")
    if not isinstance(sections, dict):
        failures.append(f"{label}: sections must be an object")
        sections = {}

    expected_sections = {
        "scripture_refs",
        "boundary_sources",
        "doctrine_objects",
        "advisory_notes",
    }
    missing_sections = sorted(expected_sections - set(sections))
    if missing_sections:
        failures.append(f"{label}: missing sections {', '.join(missing_sections)}")

    for section, rows in sections.items():
        if not isinstance(rows, list):
            failures.append(f"{label}: section {section} must be a list")
            continue
        for index, row in enumerate(rows):
            row_label = f"{label}:{section}[{index}]"
            if not isinstance(row, dict):
                failures.append(f"{row_label}: row must be an object")
                continue
            failures.extend(validate_packet_row(row, section=section, label=row_label))

    for index, row in enumerate(record.get("timeline_view", []) or []):
        if not isinstance(row, dict):
            failures.append(f"{label}:timeline_view[{index}] row must be an object")
            continue
        row_label = f"{label}:timeline_view[{index}]"
        failures.extend(validate_packet_row(row, section="timeline_view", label=row_label))
        if row.get("event_object_type") not in {
            "formulation",
            "assessment",
            "instrument_binding_scope",
        }:
            failures.append(f"{row_label}: timeline row must be a dated event object")
        if not row.get("track"):
            failures.append(f"{row_label}: timeline row requires track")
        date_block = row.get("date_block")
        if not isinstance(date_block, dict) or "date_precision" not in date_block:
            failures.append(f"{row_label}: timeline date precision must be preserved")

    return failures


def validate_packet_row(row: dict[str, Any], *, section: str, label: str) -> list[str]:
    failures: list[str] = []
    for field in ("namespace", "authority_rung", "review_status", "provenance_ref"):
        if field not in row:
            failures.append(f"{label}: missing row-contract field {field}")
    if row.get("authority_rung") not in AUTHORITY_RANK:
        failures.append(f"{label}: authority_rung must be S0-S7")
    if row.get("review_status") not in REVIEW_STATUSES:
        failures.append(f"{label}: review_status is not in the closed vocabulary")

    namespace = row.get("namespace")
    expected_namespace = {
        "scripture_refs": "scripture_",
        "boundary_sources": "boundary_",
        "doctrine_objects": "doctrine_",
        "advisory_notes": "advisory_",
    }.get(section)
    if expected_namespace and namespace != expected_namespace:
        failures.append(f"{label}: namespace must be {expected_namespace}")
    if section != "advisory_notes" and namespace == "advisory_":
        failures.append(f"{label}: advisory refs may appear only in advisory_notes")
    if section == "scripture_refs" and row.get("authority_rung") != "S0":
        failures.append(f"{label}: scripture_refs must remain S0 canonical rows")
    if section == "boundary_sources" and not row.get("trust_tier"):
        failures.append(f"{label}: boundary rows require trust_tier")
    if section == "doctrine_objects":
        if row.get("orthodoxy_status") not in ORTHODOXY_STATUSES:
            failures.append(f"{label}: doctrine rows require orthodoxy_status")
        if row.get("claim_role") not in CLAIM_ROLES:
            failures.append(f"{label}: doctrine rows require claim_role")
    return failures


def load_gate_trigger_registry(path: Path = GATE_TRIGGER_REGISTRY) -> dict[str, Any]:
    return load_yaml(path)


def validate_gate_trigger_registry(registry: dict[str, Any], *, label: str = "gate registry") -> list[str]:
    failures: list[str] = []
    refs = registry.get("scripture_repo_refs")
    if not isinstance(refs, dict):
        return [f"{label}: missing scripture_repo_refs"]
    required_refs = {
        "orthodox_original_language_pressure_dossier_queue",
        "original_language_phrase_context_policy",
        "textual_variant_source_tradition_dossier_queue",
    }
    for key in sorted(required_refs):
        value = refs.get(key)
        if not isinstance(value, str) or not value.startswith("logos-scripture-graph:"):
            failures.append(f"{label}: {key} must be a logos-scripture-graph path reference")

    for section in ("original_language_review", "textual_critical_review"):
        payload = registry.get(section)
        if not isinstance(payload, dict):
            failures.append(f"{label}: missing {section}")
            continue
        classes = payload.get("trigger_classes")
        if not isinstance(classes, list) or not all(isinstance(item, str) and item for item in classes):
            failures.append(f"{label}: {section}.trigger_classes must be a non-empty string list")
    return failures


def validate_gate_triggers_for_record(
    record: dict[str, Any],
    registry: dict[str, Any],
    *,
    label: str = "record",
) -> list[str]:
    failures: list[str] = []
    provenance = record.get("doctrine_provenance", record)
    if not isinstance(provenance, dict):
        return [f"{label}: missing doctrine_provenance for gate validation"]

    triggers = record.get("gate_triggers", provenance.get("gate_triggers", {}))
    if not isinstance(triggers, dict):
        return failures

    original_classes = set(registry["original_language_review"]["trigger_classes"])
    textual_classes = set(registry["textual_critical_review"]["trigger_classes"])
    record_original = set(triggers.get("original_language_review", []) or [])
    record_textual = set(triggers.get("textual_critical_review", []) or [])

    if record_original.intersection(original_classes) and provenance.get("original_language_review") == "not_required":
        failures.append(f"{label}: V-GATE-1 original-language trigger requires pending or complete gate")
    if record_textual.intersection(textual_classes) and provenance.get("textual_critical_review") == "not_required":
        failures.append(f"{label}: V-GATE-1 textual-critical trigger requires pending or complete gate")
    return failures


def print_failures_or_pass(failures: list[str], success_message: str) -> int:
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print(success_message)
    return 0
