#!/usr/bin/env python3
"""Validate OD-C-OPEN-A purpose, rights boundaries, and source candidates."""
from __future__ import annotations

import pathlib
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUTHORIZATION_PATH = ROOT / "governance" / "INDEPENDENT_STUDY_SOURCE_AUTHORIZATION.yaml"
CANDIDATE_PATH = ROOT / "governance" / "registry" / "BIBLE_SOURCE_ACQUISITION_CANDIDATES.yaml"

EXPECTED_PURPOSES = {
    "independent_scholarly_research",
    "self_education",
    "personal_bible_study",
    "church_and_ministry_study",
    "lay_theological_scholarship",
    "teaching",
    "other_noncommercial_educational_purposes",
}
EXPECTED_QUALITY_BASIS = {"evidence", "provenance", "reproducibility", "source_competence", "review"}
EXPECTED_CANDIDATES = {"eng-web", "grc-sblgnt", "hbo-oshb-wlc", "eng-lxx2012"}


def _load(path: pathlib.Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must be a mapping")
    return data


def validate(
    authorization_path: pathlib.Path = AUTHORIZATION_PATH,
    candidate_path: pathlib.Path = CANDIDATE_PATH,
) -> list[str]:
    authorization = _load(authorization_path)
    candidates = _load(candidate_path)
    failures: list[str] = []

    if authorization.get("decision_id") != "OD-C-OPEN-A":
        failures.append("decision_id must be OD-C-OPEN-A")
    if authorization.get("trust_zone") != "canonical" or authorization.get("lifecycle_status") != "active":
        failures.append("OD-C-OPEN-A must remain canonical and active")
    if set(authorization.get("recognized_purposes", [])) != EXPECTED_PURPOSES:
        failures.append("recognized_purposes must preserve the complete owner-authorized set")
    if set(authorization.get("quality_evaluation_basis", [])) != EXPECTED_QUALITY_BASIS:
        failures.append("quality_evaluation_basis must preserve evidence-based review criteria")

    institutional = authorization.get("institutional_requirements")
    if not isinstance(institutional, dict) or any(value is not False for value in institutional.values()):
        failures.append("no institutional affiliation or credential may be required")

    escalation = authorization.get("optional_institutional_access_escalation")
    if not isinstance(escalation, dict):
        failures.append("optional institutional access escalation must be defined")
    else:
        for field in (
            "owner_contact_required_before_use",
            "account_holder_voluntary_participation_required",
            "exact_institution_and_provider_terms_review_required",
        ):
            if escalation.get(field) is not True:
                failures.append(f"optional_institutional_access_escalation.{field} must be true")
        for field in (
            "credential_storage_authorized",
            "credential_sharing_authorized",
            "automated_login_or_harvesting_authorized",
            "institutional_access_authorizes_source_import",
            "institutional_access_authorizes_ai_transmission",
        ):
            if escalation.get(field) is not False:
                failures.append(f"optional_institutional_access_escalation.{field} must be false")

    rights = authorization.get("rights_boundaries")
    if not isinstance(rights, dict) or any(value is not False for value in rights.values()):
        failures.append("recognized research purposes must not override rights restrictions")

    governance_actions = authorization.get("authorized_governance_actions")
    if not isinstance(governance_actions, dict) or any(value is not True for value in governance_actions.values()):
        failures.append("all named governance-only source actions must remain enabled")

    content_authority = authorization.get("content_authority")
    if not isinstance(content_authority, dict) or any(value is not False for value in content_authority.values()):
        failures.append("OD-C-OPEN-A must not authorize source content or semantic authority")

    register_authority = candidates.get("register_authority")
    if not isinstance(register_authority, dict):
        failures.append("candidate register authority must be a mapping")
    else:
        if register_authority.get("records_preliminary_rights_observations_only") is not True:
            failures.append("candidate register must remain preliminary only")
        for field in (
            "authorizes_source_text_import",
            "authorizes_public_distribution",
            "authorizes_ai_transmission",
            "authorizes_preferred_reading_or_source_tradition",
        ):
            if register_authority.get(field) is not False:
                failures.append(f"register_authority.{field} must be false")

    records = candidates.get("candidates")
    if not isinstance(records, list):
        failures.append("candidates must be a list")
    else:
        ids = {record.get("candidate_id") for record in records if isinstance(record, dict)}
        if ids != EXPECTED_CANDIDATES or len(records) != len(EXPECTED_CANDIDATES):
            failures.append("candidate register must contain exactly the approved preliminary set")
        for record in records:
            if not isinstance(record, dict):
                failures.append("candidate record must be a mapping")
                continue
            candidate_id = record.get("candidate_id", "<unknown>")
            if record.get("rights_review_status") != "preliminary_official_source_observation":
                failures.append(f"{candidate_id} must remain a preliminary rights observation")
            for field in ("source_url", "official_rights_url"):
                if not str(record.get(field, "")).startswith("https://"):
                    failures.append(f"{candidate_id}.{field} must use an HTTPS official source")
            if record.get("owner_source_use_review_required") is not True:
                failures.append(f"{candidate_id} must require owner source-use review")
            for field in (
                "license_snapshot_captured",
                "source_text_present",
                "import_authorized",
                "distribution_authorized",
                "ai_transmission_authorized",
            ):
                if record.get(field) is not False:
                    failures.append(f"{candidate_id}.{field} must remain false in rights preflight")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Independent-study source authorization validation passed; no source import is authorized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
