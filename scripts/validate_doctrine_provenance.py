#!/usr/bin/env python3
"""Validate doctrine provenance contract and future provenance-bearing examples."""
from __future__ import annotations

from doctrine_genealogy_validation import (
    PROVENANCE_REQUIRED_FIELDS,
    SCHEMA_DIR,
    iter_records,
    load_json,
    print_failures_or_pass,
    rel,
    validate_provenance_block,
)


def main() -> int:
    failures: list[str] = []
    schema = load_json(SCHEMA_DIR / "doctrine_provenance.v1.schema.json")
    required = set(schema.get("required", []))
    if required != PROVENANCE_REQUIRED_FIELDS:
        missing = sorted(PROVENANCE_REQUIRED_FIELDS - required)
        extra = sorted(required - PROVENANCE_REQUIRED_FIELDS)
        failures.append(
            f"{rel(SCHEMA_DIR / 'doctrine_provenance.v1.schema.json')}: required field drift missing={missing} extra={extra}"
        )

    for path, record in iter_records("nodes", "edges"):
        provenance = record.get("doctrine_provenance")
        status = record.get("edge_status")
        if isinstance(provenance, dict):
            failures.extend(
                validate_provenance_block(
                    provenance,
                    relationship_status=status,
                    label=rel(path),
                )
            )
        elif status in {"proposed_relationship", "asserted_relationship"}:
            failures.append(f"{rel(path)}: proposed/asserted record requires doctrine_provenance")

    return print_failures_or_pass(
        failures,
        "Doctrine provenance validation passed.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
