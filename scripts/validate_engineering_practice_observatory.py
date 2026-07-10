#!/usr/bin/env python3
"""Validate the Engineering Practice Observatory's governed surfaces."""
from __future__ import annotations

from datetime import date
import pathlib
import sys
from urllib.parse import urlparse

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
STANDARD = ROOT / "governance/ENGINEERING_PRACTICE_OBSERVATORY_STANDARD.yaml"
SOURCES = ROOT / "governance/registry/ENGINEERING_PRACTICE_SOURCE_REGISTRY.yaml"
RECOMMENDATIONS = ROOT / "governance/registry/ENGINEERING_PRACTICE_RECOMMENDATION_REGISTRY.yaml"
LIBRARY = ROOT / "docs/governance/engineering-practice-library"
METADATA = {"object_type", "trust_zone", "lifecycle_status", "provenance_note", "reason_for_inclusion"}
FIT = {"solo_maintainer_fit", "theological_safety", "auditability", "economic_efficiency", "operational_complexity", "future_scalability"}


def load(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    failures: list[str] = []
    documents = {path: load(path) for path in (STANDARD, SOURCES, RECOMMENDATIONS)}
    for path, document in documents.items():
        missing = METADATA - set(document)
        if missing:
            failures.append(f"{path.relative_to(ROOT)} missing metadata: {sorted(missing)}")

    standard, sources_doc, recs_doc = documents.values()
    if standard.get("authority", {}).get("leading_company_practice_is_evidence_not_authority") is not True:
        failures.append("standard must keep leading-company practice evidence-only")
    if standard.get("authority", {}).get("ai_may_satisfy_owner_gate") is not False:
        failures.append("standard must prohibit AI satisfaction of owner gates")

    source_ids: set[str] = set()
    allowed_types = set(sources_doc.get("allowed_source_types", []))
    for source in sources_doc.get("sources", []):
        sid = source.get("source_id", "<missing>")
        if sid in source_ids:
            failures.append(f"duplicate source_id: {sid}")
        source_ids.add(sid)
        if source.get("source_type") not in allowed_types:
            failures.append(f"{sid} uses an unapproved source_type")
        parsed = urlparse(source.get("url", ""))
        if parsed.scheme != "https" or not parsed.netloc:
            failures.append(f"{sid} must use a direct HTTPS source URL")
        try:
            verified = date.fromisoformat(source["last_verified_at"])
            due = date.fromisoformat(source["next_review_due"])
            if due < verified:
                failures.append(f"{sid} next_review_due predates verification")
            if int(source.get("review_cadence_days", 0)) <= 0:
                failures.append(f"{sid} review cadence must be positive")
        except (KeyError, TypeError, ValueError):
            failures.append(f"{sid} has invalid review dates")
        if not str(source.get("authority_posture", "")).endswith("not_governance_authority"):
            failures.append(f"{sid} must remain evidence-only")

    practice_ids: set[str] = set()
    statuses = set(standard.get("recommendation_statuses", []))
    for rec in recs_doc.get("recommendations", []):
        pid = rec.get("practice_id", "<missing>")
        if pid in practice_ids:
            failures.append(f"duplicate practice_id: {pid}")
        practice_ids.add(pid)
        unknown = set(rec.get("evidence_source_ids", [])) - source_ids
        if unknown:
            failures.append(f"{pid} cites unknown sources: {sorted(unknown)}")
        if rec.get("recommendation_status") not in statuses:
            failures.append(f"{pid} has an invalid recommendation status")
        if set(rec.get("fit_dimensions", {})) != FIT:
            failures.append(f"{pid} must assess every required Logos fit dimension")
        if len(rec.get("beginner_explanation", "")) < 40:
            failures.append(f"{pid} needs a substantive beginner explanation")
        if rec.get("owner_decision_required") and rec.get("recommendation_status") not in {"watch", "owner_decision_required"}:
            failures.append(f"{pid} owner-gated recommendation cannot be auto-adopted")
        try:
            date.fromisoformat(rec["next_review_due"])
        except (KeyError, TypeError, ValueError):
            failures.append(f"{pid} has an invalid next_review_due")

    card_text = "\n".join(path.read_text(encoding="utf-8") for path in LIBRARY.glob("*.md"))
    for pid in practice_ids:
        if pid not in card_text:
            failures.append(f"{pid} is not discoverable in the practice library")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("Engineering Practice Observatory validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
