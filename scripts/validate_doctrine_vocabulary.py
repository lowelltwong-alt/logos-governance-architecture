#!/usr/bin/env python3
"""Validate doctrine-genealogy closed vocabulary contracts."""
from __future__ import annotations

from doctrine_genealogy_validation import (
    EDGE_VERBS,
    FORBIDDEN_EDGE_VERBS,
    ORTHODOXY_STATUSES,
    SCHEMA_DIR,
    TRADITION_SCOPES,
    load_json,
    print_failures_or_pass,
    rel,
    require_schema_comment,
    schema_text_has_only_floor_defaults,
)


def main() -> int:
    failures: list[str] = []
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        schema = load_json(path)
        failures.extend(require_schema_comment(path, schema))
        failures.extend(schema_text_has_only_floor_defaults(path))

    node_schema = load_json(SCHEMA_DIR / "doctrine_node.v1.schema.json")
    edge_schema = load_json(SCHEMA_DIR / "genealogy_edge.v1.schema.json")
    provenance_schema = load_json(SCHEMA_DIR / "doctrine_provenance.v1.schema.json")

    orthodoxy_values = set(
        node_schema["$defs"]["orthodoxy_status"]["enum"]
    ) | set(provenance_schema["properties"]["orthodoxy_status"]["enum"])
    if orthodoxy_values != ORTHODOXY_STATUSES:
        failures.append(f"{rel(SCHEMA_DIR / 'doctrine_node.v1.schema.json')}: orthodoxy_status enum drift")

    tradition_values = set(node_schema["$defs"]["tradition_scope"]["enum"])
    if tradition_values != TRADITION_SCOPES:
        failures.append(f"{rel(SCHEMA_DIR / 'doctrine_node.v1.schema.json')}: tradition_scope enum drift")

    verbs = set(edge_schema["properties"]["verb"]["enum"])
    if verbs != EDGE_VERBS:
        failures.append(f"{rel(SCHEMA_DIR / 'genealogy_edge.v1.schema.json')}: edge verb enum drift")
    if verbs.intersection(FORBIDDEN_EDGE_VERBS):
        failures.append(f"{rel(SCHEMA_DIR / 'genealogy_edge.v1.schema.json')}: forbidden verb present")

    return print_failures_or_pass(
        failures,
        "Doctrine-genealogy vocabulary validation passed.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
