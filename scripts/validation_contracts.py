#!/usr/bin/env python3
"""Shared helpers for contract-backed repository validation."""
from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_REGISTRY_PATH = ROOT / "schemas" / "schema_registry.json"

DEFAULT_VALIDATION_SCOPE_NOTE = (
    "Default validation scope is the shared contract-backed suite used by local, "
    "CI, and semantic-merge. Internal-link validation remains README-only in "
    "Wave B so scope alignment does not silently expand into the broader link "
    "cleanup reserved for Wave C."
)

_FIELD_HEADING_RE = re.compile(r"^### `([^`]+)`$")
_ALLOWED_ITEM_RE = re.compile(r"^- `([^`]+)`$")
_ALIAS_ITEM_RE = re.compile(r"^- `([^`]+)` -> `([^`]+)`$")


def extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    try:
        _, rest = text.split("---\n", 1)
        frontmatter, _ = rest.split("\n---\n", 1)
        return frontmatter
    except ValueError:
        return None


def _coerce_yaml_scalar(raw: str) -> Any:
    value = raw.strip()
    if value in {"null", "~"}:
        return None
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",")]
    return value.strip('"').strip("'")


def parse_simple_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if line.startswith("  - ") or line.startswith("    - "):
            if current_list_key is not None:
                data.setdefault(current_list_key, []).append(
                    line.split("- ", 1)[1].strip().strip('"').strip("'")
                )
            continue

        if line.startswith(" ") or line.startswith("-"):
            continue

        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if value == "":
            data[key] = []
            current_list_key = key
            continue

        data[key] = _coerce_yaml_scalar(value)
        current_list_key = None

    return data


def load_schema_registry(root: pathlib.Path = ROOT) -> dict[str, Any]:
    return json.loads((root / SCHEMA_REGISTRY_PATH.relative_to(ROOT)).read_text(encoding="utf-8"))


def get_contract(registry: dict[str, Any], name: str) -> dict[str, Any]:
    for contract in registry.get("schemas", []):
        if contract.get("name") == name:
            return contract
    raise KeyError(f"Unknown schema contract: {name}")


def load_contract_schema(contract: dict[str, Any], root: pathlib.Path = ROOT) -> dict[str, Any]:
    return json.loads((root / pathlib.Path(contract["path"])).read_text(encoding="utf-8"))


def resolve_contract_paths(contract: dict[str, Any], root: pathlib.Path = ROOT) -> list[pathlib.Path]:
    resolved: dict[str, pathlib.Path] = {}
    for pattern in contract.get("applies_to", []):
        for path in root.glob(pattern):
            if path.is_file():
                resolved[path.as_posix()] = path
    excluded: set[str] = set()
    for pattern in contract.get("exclude_patterns", []):
        for path in root.glob(pattern):
            if path.is_file():
                excluded.add(path.as_posix())
    return [resolved[key] for key in sorted(resolved) if key not in excluded]


def activates_contract(record: dict[str, Any], contract: dict[str, Any]) -> bool:
    activation_keys = contract.get("activation_keys_any", [])
    if not activation_keys:
        return True
    return any(key in record for key in activation_keys)


def _matches_type(value: Any, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "null":
        return value is None
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "object":
        return isinstance(value, dict)
    return True


def _allowed_types(rule: dict[str, Any]) -> list[str]:
    field_type = rule.get("type")
    if isinstance(field_type, list):
        return [item for item in field_type if isinstance(item, str)]
    if isinstance(field_type, str):
        return [field_type]
    return []


def schema_failures(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    missing = [key for key in schema.get("required", []) if key not in record]
    if missing:
        failures.append(f"missing required keys {', '.join(missing)}")

    properties = schema.get("properties", {})
    for field, rule in properties.items():
        if field not in record:
            continue

        value = record[field]
        allowed_types = _allowed_types(rule)
        if allowed_types and not any(_matches_type(value, kind) for kind in allowed_types):
            failures.append(
                f"{field} has type {type(value).__name__}, expected {' or '.join(allowed_types)}"
            )
            continue

        if isinstance(value, str):
            if "minLength" in rule and len(value) < rule["minLength"]:
                failures.append(
                    f"{field} must be at least {rule['minLength']} characters"
                )
            if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
                failures.append(f"{field} value '{value}' does not match required pattern")
            if "enum" in rule and value not in rule["enum"]:
                failures.append(
                    f"{field} value '{value}' must be one of {', '.join(rule['enum'])}"
                )

        if isinstance(value, list) and isinstance(rule.get("items"), dict):
            item_rule = rule["items"]
            item_types = _allowed_types(item_rule)
            if item_types:
                bad_items = [
                    item for item in value if not any(_matches_type(item, kind) for kind in item_types)
                ]
                if bad_items:
                    failures.append(
                        f"{field} contains items with invalid types; expected {' or '.join(item_types)}"
                    )

    return failures


def extract_graph_object_ids(raw: dict[str, Any]) -> set[str]:
    ids: set[str] = set()

    top_level_id = raw.get("id")
    if isinstance(top_level_id, str) and top_level_id:
        ids.add(top_level_id)

    identity = raw.get("identity")
    if isinstance(identity, dict):
        identity_id = identity.get("id")
        if isinstance(identity_id, str) and identity_id:
            ids.add(identity_id)

    address = raw.get("address")
    if isinstance(address, dict):
        address_id = address.get("id")
        if isinstance(address_id, str) and address_id:
            ids.add(address_id)

    return ids


def iter_string_values(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        for item in value:
            found.extend(iter_string_values(item))
        return found
    if isinstance(value, dict):
        for item in value.values():
            found.extend(iter_string_values(item))
    return found


def count_prefixed_lines(text: str, prefix: str) -> int:
    return sum(1 for line in text.splitlines() if line.startswith(prefix))


def parse_controlled_value_registry(text: str) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    current_field: str | None = None
    current_mode: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        heading = _FIELD_HEADING_RE.match(line)
        if heading:
            current_field = heading.group(1)
            registry[current_field] = {"allowed_values": [], "aliases": {}}
            current_mode = None
            continue

        if current_field is None:
            continue

        if line == "Allowed values:":
            current_mode = "allowed"
            continue

        if line.startswith("Migration aliases"):
            current_mode = "aliases"
            continue

        if line.startswith("### ") or line.startswith("## "):
            current_mode = None
            continue

        if current_mode == "allowed":
            match = _ALLOWED_ITEM_RE.match(line)
            if match:
                registry[current_field]["allowed_values"].append(match.group(1))
            continue

        if current_mode == "aliases":
            match = _ALIAS_ITEM_RE.match(line)
            if match:
                registry[current_field]["aliases"][match.group(1)] = match.group(2)

    return registry


def load_controlled_vocabulary_source(
    registry: dict[str, Any], root: pathlib.Path = ROOT
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    source = registry.get("controlled_vocabulary_source")
    if not isinstance(source, dict) or "path" not in source:
        raise KeyError("schema_registry.json is missing controlled_vocabulary_source metadata")

    parsed = parse_controlled_value_registry(
        (root / pathlib.Path(source["path"])).read_text(encoding="utf-8")
    )
    missing_fields = [
        field for field in source.get("fields", []) if field not in parsed
    ]
    if missing_fields:
        raise KeyError(
            "Controlled vocabulary source is missing fields: " + ", ".join(missing_fields)
        )
    return source, parsed


def default_validation_commands(python_executable: str | None = None) -> list[dict[str, Any]]:
    python = python_executable or sys.executable
    return [
        {
            "name": "node_frontmatter",
            "command": [python, "scripts/validate_node_frontmatter.py"],
        },
        {
            "name": "cross_references",
            "command": [python, "scripts/validate_cross_references.py"],
        },
        {
            "name": "claim_files",
            "command": [python, "scripts/validate_claim_files.py"],
        },
        {
            "name": "controlled_vocabulary",
            "command": [python, "scripts/validate_trust_zone_vocabulary.py"],
        },
        {
            "name": "external_mappings",
            "command": [python, "scripts/validate_external_mappings.py"],
        },
        {
            "name": "internal_links",
            "command": [python, "scripts/validate_internal_links.py"],
        },
        {
            "name": "retrieval_neighborhoods",
            "command": [python, "scripts/validate_retrieval_neighborhoods.py"],
        },
        {
            "name": "governance_metadata",
            "command": [python, "scripts/validate_governance_metadata.py"],
        },
        {
            "name": "cross_repo_governance_contract",
            "command": [python, "scripts/validate_cross_repo_governance_contract.py"],
        },
        {
            "name": "cross_repo_reference_manifest",
            "command": [python, "scripts/validate_cross_repo_reference_manifest.py"],
        },
        {
            "name": "fable_feedback_trace_matrix",
            "command": [python, "scripts/validate_fable_feedback_trace_matrix.py"],
        },
        {
            "name": "legacy_content_ownership_inventory",
            "command": [python, "scripts/validate_legacy_content_ownership_inventory.py"],
        },
        {
            "name": "external_advisory_authority_firewall",
            "command": [python, "scripts/validate_external_advisory_authority_firewall.py"],
        },
        {
            "name": "boundary_governance_stop_rules",
            "command": [python, "scripts/validate_boundary_governance_stop_rules.py"],
        },
        {
            "name": "governance_dependency_map",
            "command": [python, "scripts/validate_governance_dependency_map.py"],
        },
        {
            "name": "doctrine_vocabulary",
            "command": [python, "scripts/validate_doctrine_vocabulary.py"],
        },
        {
            "name": "doctrine_provenance",
            "command": [python, "scripts/validate_doctrine_provenance.py"],
        },
        {
            "name": "genealogy_edges",
            "command": [python, "scripts/validate_genealogy_edges.py"],
        },
        {
            "name": "evidence_packet",
            "command": [python, "scripts/validate_evidence_packet.py"],
        },
        {
            "name": "gate_triggers",
            "command": [python, "scripts/validate_gate_triggers.py"],
        },
        {
            "name": "codex_theology_tripwire",
            "command": [python, "scripts/validate_codex_theology_tripwire.py"],
        },
        {
            "name": "agent_routing_vocabulary",
            "command": [python, "scripts/validate_agent_routing_vocabulary.py"],
        },
        {
            "name": "agent_qualification_fixtures",
            "command": [python, "scripts/validate_agent_qualification_fixtures.py"],
        },
        {
            "name": "independent_study_source_authorization",
            "command": [python, "scripts/validate_independent_study_source_authorization.py"],
        },
    ]
