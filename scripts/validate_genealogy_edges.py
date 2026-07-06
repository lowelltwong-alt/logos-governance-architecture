#!/usr/bin/env python3
"""Validate doctrine-genealogy edge contract and future edge examples."""
from __future__ import annotations

from doctrine_genealogy_validation import (
    EDGE_VERBS,
    FORBIDDEN_EDGE_VERBS,
    SCHEMA_DIR,
    iter_records,
    load_json,
    print_failures_or_pass,
    rel,
    validate_genealogy_edge_record,
)


def main() -> int:
    failures: list[str] = []
    schema = load_json(SCHEMA_DIR / "genealogy_edge.v1.schema.json")
    verbs = set(schema["properties"]["verb"]["enum"])
    if verbs != EDGE_VERBS:
        failures.append(f"{rel(SCHEMA_DIR / 'genealogy_edge.v1.schema.json')}: verb registry drift")
    forbidden = set(schema.get("not", {}).get("properties", {}).get("verb", {}).get("enum", []))
    if forbidden != FORBIDDEN_EDGE_VERBS:
        failures.append(f"{rel(SCHEMA_DIR / 'genealogy_edge.v1.schema.json')}: forbidden verb guard drift")

    object_index = {
        record.get("id"): record
        for _, record in iter_records("nodes")
        if isinstance(record.get("id"), str)
    }
    for path, record in iter_records("edges"):
        failures.extend(
            validate_genealogy_edge_record(record, object_index=object_index, label=rel(path))
        )

    return print_failures_or_pass(
        failures,
        "Genealogy edge validation passed.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
