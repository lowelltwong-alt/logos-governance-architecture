#!/usr/bin/env python3
"""Validate Kernel E / V-CODEX-1 theology tripwire coverage."""
from __future__ import annotations

from doctrine_genealogy_validation import (
    EXAMPLE_DIR,
    GATE_TRIGGER_REGISTRY,
    ROOT,
    SCHEMA_DIR,
    load_yaml,
    print_failures_or_pass,
    rel,
    schema_text_has_only_floor_defaults,
    validate_codex_theology_tripwire_record,
)


SEED_PATHS = [
    ROOT / "governance" / "registry" / "entity_ids.yaml",
    GATE_TRIGGER_REGISTRY,
]


def main() -> int:
    failures: list[str] = []
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        failures.extend(schema_text_has_only_floor_defaults(path))

    for path in SEED_PATHS:
        if path.exists():
            failures.extend(
                validate_codex_theology_tripwire_record(
                    load_yaml(path),
                    label=rel(path),
                )
            )

    if EXAMPLE_DIR.exists():
        for path in sorted(EXAMPLE_DIR.rglob("*.yaml")):
            failures.extend(
                validate_codex_theology_tripwire_record(
                    load_yaml(path),
                    label=rel(path),
                )
            )

    return print_failures_or_pass(
        failures,
        "Codex theology tripwire validation passed.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
