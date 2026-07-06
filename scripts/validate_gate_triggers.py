#!/usr/bin/env python3
"""Validate doctrine-genealogy gate trigger registry and future gate-trigger examples."""
from __future__ import annotations

from doctrine_genealogy_validation import (
    GATE_TRIGGER_REGISTRY,
    iter_records,
    load_gate_trigger_registry,
    print_failures_or_pass,
    rel,
    validate_gate_trigger_registry,
    validate_gate_triggers_for_record,
)


def main() -> int:
    failures: list[str] = []
    registry = load_gate_trigger_registry()
    failures.extend(validate_gate_trigger_registry(registry, label=rel(GATE_TRIGGER_REGISTRY)))

    for path, record in iter_records("nodes", "edges"):
        failures.extend(
            validate_gate_triggers_for_record(
                record,
                registry,
                label=rel(path),
            )
        )

    return print_failures_or_pass(
        failures,
        "Gate trigger validation passed.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
