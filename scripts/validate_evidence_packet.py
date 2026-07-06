#!/usr/bin/env python3
"""Validate evidence-packet contract and future evidence-packet examples."""
from __future__ import annotations

from doctrine_genealogy_validation import (
    NON_AUTHORITY_BLOCK,
    SCHEMA_DIR,
    iter_records,
    load_json,
    print_failures_or_pass,
    rel,
    validate_evidence_packet_record,
)


def main() -> int:
    failures: list[str] = []
    schema = load_json(SCHEMA_DIR / "evidence_packet.v1.schema.json")
    block_props = schema["properties"]["non_authority_block"]["properties"]
    actual = {
        key: rule.get("const")
        for key, rule in block_props.items()
    }
    if actual != NON_AUTHORITY_BLOCK:
        failures.append(f"{rel(SCHEMA_DIR / 'evidence_packet.v1.schema.json')}: non_authority_block const drift")

    for path, record in iter_records("evidence_packets"):
        failures.extend(validate_evidence_packet_record(record, label=rel(path)))

    return print_failures_or_pass(
        failures,
        "Evidence packet validation passed.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
