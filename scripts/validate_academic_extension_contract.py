#!/usr/bin/env python3
"""Validate the specification-only Academic Extension Contract.

Capability classification: ``portable_core``. The validator is deterministic,
offline, provider-neutral, read-only, and repository-local. A pass proves only
the structural, digest, fixture, authority-ceiling, and dependency invariants
implemented here. It does not prove academic truth, source fitness, doctrine,
expert qualification, runtime readiness, portability to an untested adapter, or
permission to activate, publish, ingest, promote, or migrate anything.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas" / "academic_extensions"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "academic_extensions"
REGISTRY_PATH = ROOT / "governance" / "registry" / "ACADEMIC_DOMAIN_PACK_REGISTRY.yaml"
SCHEMA_REGISTRY_PATH = ROOT / "schemas" / "schema_registry.json"
PACKET_ROOT = (
    ROOT
    / "docs"
    / "roadmap"
    / "logos-stewardship-architecture-buildout"
    / "revisions"
    / "academic-extension-contract-v1"
)
CONTRACT_PATH = ROOT / "docs" / "governance" / "academic-extension-contract.md"
FROZEN_DIGEST_PATH = PACKET_ROOT / "frozen-digests.json"

SCHEMA_FILES = {
    "domain_pack": "domain_pack_manifest.v1.schema.json",
    "assertion": "assertion_envelope.v1.schema.json",
    "source_record": "source_record.v1.schema.json",
    "derived_projection": "derived_projection.v1.schema.json",
    "extension_registry": "extension_registry.v1.schema.json",
}
POSITIVE_FIXTURES = {
    "positive_domain_pack.json": "domain_pack",
    "positive_assertion.json": "assertion",
    "positive_source_record.json": "source_record",
    "positive_derived_projection.json": "derived_projection",
    "positive_extension_registry.json": "extension_registry",
}
EXPECTED_SCHEMA_REGISTRY = {
    "academic_domain_pack_manifest_v1": "schemas/academic_extensions/domain_pack_manifest.v1.schema.json",
    "academic_assertion_envelope_v1": "schemas/academic_extensions/assertion_envelope.v1.schema.json",
    "academic_source_record_v1": "schemas/academic_extensions/source_record.v1.schema.json",
    "academic_derived_projection_v1": "schemas/academic_extensions/derived_projection.v1.schema.json",
    "academic_extension_registry_v1": "schemas/academic_extensions/extension_registry.v1.schema.json",
}
EXPECTED_GATES = {f"AE-HG-{number:03d}" for number in range(1, 9)}
EXPECTED_RISKS = {f"AE-RISK-{number:03d}" for number in range(1, 12)}
REQUIRED_CONTRACT_PHRASES = (
    "not a running system",
    "does not decide doctrine",
    "extension_payload",
    "default_winner: false",
    "invalidate_on_source_digest_drift",
    "non_exact_by_default",
    "registry is intentionally empty",
)
FROZEN_EXCLUSIONS = {
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/academic-extension-contract-v1/frozen-digests.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/academic-extension-contract-v1/validation-receipt.json",
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/academic-extension-contract-v1/independent-review-receipt.md",
}


@dataclass(frozen=True, order=True)
class Finding:
    rule: str
    path: str
    detail: str

    def render(self) -> str:
        return f"{self.rule}: {self.path}: {self.detail}"


@dataclass(frozen=True)
class ValidationResult:
    findings: tuple[Finding, ...]
    metrics: dict[str, int]

    @property
    def passed(self) -> bool:
        return not self.findings


class ContractInputError(RuntimeError):
    """Raised when a required local input cannot be read safely."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractInputError(f"cannot load JSON {path}: {exc}") from exc


def _load_yaml_documents(path: Path) -> list[Any]:
    try:
        return list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractInputError(f"cannot load YAML {path}: {exc}") from exc


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def canonical_file_bytes(path: Path) -> bytes:
    """Return stable file bytes across Git's LF/CRLF checkout conversion.

    UTF-8 text is normalized to LF before hashing. Files that are not valid
    UTF-8 are treated as opaque binary and retain their exact bytes.
    """
    payload = path.read_bytes()
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(canonical_file_bytes(path)).hexdigest()


def schema_errors(instance: Any, schema: dict[str, Any]) -> list[str]:
    validator = jsonschema.Draft202012Validator(schema)
    return [
        error.message
        for error in sorted(
            validator.iter_errors(instance),
            key=lambda item: "/".join(str(part) for part in item.path),
        )
    ]


def load_schemas(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    return {
        key: _load_json(root / "schemas" / "academic_extensions" / filename)
        for key, filename in SCHEMA_FILES.items()
    }


def _apply_mutation(base: Any, descriptor: dict[str, Any]) -> Any:
    candidate = copy.deepcopy(base)
    path = descriptor.get("path")
    if not isinstance(path, list) or not path:
        raise ContractInputError("negative fixture path must be a non-empty array")
    cursor = candidate
    for segment in path[:-1]:
        if isinstance(cursor, list) and isinstance(segment, int):
            cursor = cursor[segment]
        elif isinstance(cursor, dict) and isinstance(segment, str):
            cursor = cursor[segment]
        else:
            raise ContractInputError(f"invalid mutation path segment: {segment!r}")
    final = path[-1]
    operation = descriptor.get("operation")
    if operation not in {"add", "replace", "remove"}:
        raise ContractInputError(f"unsupported mutation operation: {operation!r}")
    if isinstance(cursor, list) and isinstance(final, int):
        if operation == "remove":
            del cursor[final]
        else:
            cursor[final] = descriptor.get("value")
    elif isinstance(cursor, dict) and isinstance(final, str):
        if operation in {"replace", "remove"} and final not in cursor:
            raise ContractInputError(f"mutation target does not exist: {final}")
        if operation == "remove":
            del cursor[final]
        else:
            cursor[final] = descriptor.get("value")
    else:
        raise ContractInputError(f"invalid final mutation path: {final!r}")
    return candidate


def _assertion_semantic_findings(
    assertion: dict[str, Any], path: str = "positive_assertion.json"
) -> list[Finding]:
    findings: list[Finding] = []
    roles = [row.get("role") for row in assertion.get("roles", []) if isinstance(row, dict)]
    if len(roles) != len(set(roles)):
        findings.append(Finding("nary_role_uniqueness", path, "role names must be unique within an assertion"))
    graph_id = assertion.get("named_graph", {}).get("graph_id")
    alternatives = assertion.get("hypothesis", {}).get("alternatives", [])
    if graph_id in alternatives:
        findings.append(Finding("hypothesis_self_reference", path, "an alternative hypothesis graph cannot be the assertion's own graph"))
    extension = assertion.get("extension_payload", {})
    payload = extension.get("payload_data")
    if isinstance(payload, dict):
        if extension.get("payload_digest") != canonical_digest(payload):
            findings.append(Finding("extension_payload_digest", path, "payload digest does not match the exact unknown JSON value"))
        round_tripped = json.loads(json.dumps(payload, sort_keys=True, ensure_ascii=False))
        if round_tripped != payload:
            findings.append(Finding("lossless_extension_roundtrip", path, "unknown extension payload changed during canonical round-trip"))
    return findings


def _safe_repo_file(root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        return None
    candidate = Path(relative)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        return None
    resolved_root = root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        return None
    return resolved


def _registry_semantic_findings(
    registry: dict[str, Any], root: Path, path: str = "positive_extension_registry.json"
) -> list[Finding]:
    findings: list[Finding] = []
    packs = [row for row in registry.get("packs", []) if isinstance(row, dict)]
    consumers = [row for row in registry.get("consumers", []) if isinstance(row, dict)]
    pack_ids = [row.get("pack_id") for row in packs]
    manifest_refs = [row.get("manifest_ref") for row in packs]
    if len(pack_ids) != len(set(pack_ids)):
        findings.append(Finding("pack_identity_collision", path, "pack IDs must be unique"))
    if len(manifest_refs) != len(set(manifest_refs)):
        findings.append(Finding("manifest_ref_collision", path, "manifest references must be unique"))

    namespaces: list[str] = []
    for row in packs:
        manifest_path = _safe_repo_file(root, row.get("manifest_ref"))
        if manifest_path is None or not manifest_path.is_file():
            findings.append(Finding("manifest_ref_invalid", path, f"invalid or missing manifest for {row.get('pack_id')}"))
            continue
        manifest = _load_json(manifest_path)
        if file_digest(manifest_path) != row.get("manifest_digest"):
            findings.append(Finding("registry_manifest_digest", path, f"manifest digest mismatch for {row.get('pack_id')}"))
        if manifest.get("pack_id") != row.get("pack_id"):
            findings.append(Finding("registry_manifest_identity", path, f"registry and manifest pack IDs differ for {row.get('pack_id')}"))
        if manifest.get("status") != row.get("status"):
            findings.append(Finding("registry_manifest_status", path, f"registry and manifest status differ for {row.get('pack_id')}"))
        namespace = manifest.get("namespace")
        if isinstance(namespace, str):
            namespaces.append(namespace)
        for schema_ref in manifest.get("extension_schemas", []):
            schema_path = _safe_repo_file(root, schema_ref)
            if schema_path is None or not schema_path.is_file():
                findings.append(Finding("manifest_schema_ref", path, f"invalid or missing extension schema {schema_ref!r}"))
    if len(namespaces) != len(set(namespaces)):
        findings.append(Finding("pack_namespace_collision", path, "pack namespaces must be unique"))

    consumer_ids = [row.get("consumer_id") for row in consumers]
    if len(consumer_ids) != len(set(consumer_ids)):
        findings.append(Finding("consumer_identity_collision", path, "consumer IDs must be unique"))
    consumer_pack_ids = [row.get("pack_id") for row in consumers]
    unknown_consumers = sorted(str(item) for item in set(consumer_pack_ids) - set(pack_ids))
    if unknown_consumers:
        findings.append(Finding("unknown_consumer_pack", path, ", ".join(unknown_consumers)))
    missing_consumers = sorted(str(item) for item in set(pack_ids) - set(consumer_pack_ids))
    if missing_consumers:
        findings.append(Finding("reverse_consumer_closure", path, ", ".join(missing_consumers)))
    for row in consumers:
        contract_path = _safe_repo_file(root, row.get("contract_ref"))
        if contract_path is None or not contract_path.is_file():
            findings.append(Finding("consumer_contract_ref", path, f"invalid or missing consumer contract for {row.get('consumer_id')}"))
    return findings


def negative_fixture_rules(
    base_name: str,
    candidate: dict[str, Any],
    fixtures: dict[str, Any],
    schemas: dict[str, dict[str, Any]],
    root: Path = ROOT,
) -> set[str]:
    rules: set[str] = set()
    if schema_errors(candidate, schemas[POSITIVE_FIXTURES[base_name]]):
        rules.add("schema_validation")
    if base_name == "positive_assertion.json":
        rules.update(item.rule for item in _assertion_semantic_findings(candidate))
    elif base_name == "positive_extension_registry.json":
        rules.update(item.rule for item in _registry_semantic_findings(candidate, root))
    elif base_name == "positive_source_record.json":
        if candidate.get("record_digest") != canonical_digest(candidate.get("source_payload")):
            rules.add("source_digest")
    elif base_name == "positive_derived_projection.json":
        if candidate.get("projection_digest") != canonical_digest(candidate.get("projection_payload")):
            rules.add("projection_digest")
        source = fixtures["positive_source_record.json"]
        if candidate.get("source_digest") != source.get("record_digest"):
            rules.add("source_drift")
    return rules


def _semantic_fixture_findings(
    fixtures: dict[str, Any], fixture_root: Path, root: Path, kernel_digest: str
) -> list[Finding]:
    findings: list[Finding] = []
    source = fixtures["positive_source_record.json"]
    projection = fixtures["positive_derived_projection.json"]
    assertion = fixtures["positive_assertion.json"]
    pack = fixtures["positive_domain_pack.json"]
    registry = fixtures["positive_extension_registry.json"]

    expected_source_digest = canonical_digest(source["source_payload"])
    if source["record_digest"] != expected_source_digest:
        findings.append(Finding("source_digest", "positive_source_record.json", "record_digest does not match canonical source_payload"))
    if projection["source_record_ref"] != source["source_record_id"]:
        findings.append(Finding("projection_source_ref", "positive_derived_projection.json", "source record reference does not match fixture source"))
    if projection["source_digest"] != source["record_digest"]:
        findings.append(Finding("source_drift", "positive_derived_projection.json", "projection is not pinned to the exact source digest"))
    if projection["projection_digest"] != canonical_digest(projection["projection_payload"]):
        findings.append(Finding("projection_digest", "positive_derived_projection.json", "projection digest does not match canonical payload"))

    findings.extend(_assertion_semantic_findings(assertion))

    if pack["kernel_compatibility"]["kernel_digest"] != kernel_digest:
        findings.append(Finding("fixture_kernel_digest", "positive_domain_pack.json", "pack does not pin the exact kernel digest"))
    if registry["kernel_contract"]["digest"] != kernel_digest:
        findings.append(Finding("fixture_registry_kernel_digest", "positive_extension_registry.json", "fixture registry does not pin the exact kernel digest"))
    if file_digest(fixture_root / "positive_domain_pack.json") != registry["packs"][0]["manifest_digest"]:
        findings.append(Finding("fixture_manifest_digest", "positive_extension_registry.json", "pack manifest digest does not match canonical fixture content"))
    findings.extend(_registry_semantic_findings(registry, root))
    if assertion["domain_pack_id"] != pack["pack_id"]:
        findings.append(Finding("fixture_pack_link", "positive_assertion.json", "assertion pack does not match the synthetic pack"))
    if source["source_record_id"] not in assertion["provenance"]["source_record_refs"]:
        findings.append(Finding("fixture_source_link", "positive_assertion.json", "assertion does not cite the synthetic source record"))
    return findings


def _validate_metadata_documents(metadata: Any, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    required = {"object_type", "trust_zone", "lifecycle_status", "provenance_note", "reason_for_inclusion"}
    if not isinstance(metadata, dict):
        return [Finding("governance_metadata", path.as_posix(), "metadata document must be an object")]
    missing = sorted(required - set(metadata))
    if missing:
        findings.append(Finding("governance_metadata", path.as_posix(), "missing " + ", ".join(missing)))
    return findings


def validate_frozen_digests(root: Path = ROOT) -> list[Finding]:
    path = root / FROZEN_DIGEST_PATH.relative_to(ROOT)
    manifest = _load_json(path)
    findings: list[Finding] = []
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        return [Finding("frozen_digest_rows", path.as_posix(), "files must be a non-empty array")]
    row_paths = [row.get("path") for row in rows if isinstance(row, dict)]
    if len(row_paths) != len(rows) or row_paths != sorted(row_paths) or len(row_paths) != len(set(row_paths)):
        findings.append(Finding("frozen_digest_order", path.as_posix(), "paths must be complete, unique, and sorted"))
    if manifest.get("path_count") != len(rows):
        findings.append(Finding("frozen_digest_count", path.as_posix(), "path_count does not match files"))
    if set(manifest.get("excluded_self_referential_paths", [])) != FROZEN_EXCLUSIONS:
        findings.append(Finding("frozen_digest_exclusions", path.as_posix(), "self-referential exclusions differ from the exact contract"))
    if not re.fullmatch(r"[0-9a-f]{40}", str(manifest.get("candidate_base_commit", ""))):
        findings.append(Finding("frozen_digest_base", path.as_posix(), "candidate base must be an exact commit"))
    for row in rows:
        relative = row.get("path") if isinstance(row, dict) else None
        candidate = _safe_repo_file(root, relative)
        if candidate is None or not candidate.is_file() or relative in FROZEN_EXCLUSIONS:
            findings.append(Finding("frozen_digest_path", path.as_posix(), f"invalid frozen path {relative!r}"))
            continue
        if row.get("sha256") != file_digest(candidate):
            findings.append(Finding("frozen_digest_file", str(relative), "canonical-content SHA-256 mismatch"))
    if manifest.get("content_digest") != canonical_digest(rows):
        findings.append(Finding("frozen_digest_aggregate", path.as_posix(), "content digest does not match canonical files array"))
    if manifest.get("algorithm") != "sha256(canonical_json(sorted([{path,sha256(canonical_utf8_lf_bytes_or_raw_binary_bytes)}])))":
        findings.append(Finding("frozen_digest_algorithm", path.as_posix(), "algorithm identifier is not exact"))
    return findings


def validate_repository(root: Path = ROOT) -> ValidationResult:
    findings: list[Finding] = []
    metrics: dict[str, int] = {}
    try:
        schemas = load_schemas(root)
        for key, schema in schemas.items():
            try:
                jsonschema.Draft202012Validator.check_schema(schema)
            except jsonschema.SchemaError as exc:
                findings.append(Finding("invalid_schema", SCHEMA_FILES[key], exc.message))
        schema_ids = [schema.get("$id") for schema in schemas.values()]
        if len(schema_ids) != len(set(schema_ids)):
            findings.append(Finding("schema_id_collision", "schemas/academic_extensions", "schema $id values must be unique"))
        metrics["schemas_checked"] = len(schemas)

        schema_registry = _load_json(root / "schemas" / "schema_registry.json")
        registered = {row.get("name"): row.get("path") for row in schema_registry.get("schemas", [])}
        for name, expected_path in EXPECTED_SCHEMA_REGISTRY.items():
            if registered.get(name) != expected_path:
                findings.append(Finding("schema_registry", "schemas/schema_registry.json", f"{name} must map to {expected_path}"))

        registry_documents = _load_yaml_documents(root / "governance" / "registry" / "ACADEMIC_DOMAIN_PACK_REGISTRY.yaml")
        if len(registry_documents) != 2:
            findings.append(Finding("registry_documents", "governance/registry/ACADEMIC_DOMAIN_PACK_REGISTRY.yaml", "expected metadata and data documents"))
            metadata, production_registry = {}, {}
        else:
            metadata, production_registry = registry_documents
        findings.extend(_validate_metadata_documents(metadata, REGISTRY_PATH))
        for message in schema_errors(production_registry, schemas["extension_registry"]):
            findings.append(Finding("production_registry_schema", "governance/registry/ACADEMIC_DOMAIN_PACK_REGISTRY.yaml", message))
        if production_registry.get("packs") != [] or production_registry.get("consumers") != []:
            findings.append(Finding("production_registry_not_empty", "governance/registry/ACADEMIC_DOMAIN_PACK_REGISTRY.yaml", "this revision may not activate or register a real pack"))
        findings.extend(
            _registry_semantic_findings(
                production_registry,
                root,
                "governance/registry/ACADEMIC_DOMAIN_PACK_REGISTRY.yaml",
            )
        )
        expected_kernel_digest = file_digest(root / "schemas" / "schema_registry.json")
        observed_kernel_digest = production_registry.get("kernel_contract", {}).get("digest")
        if observed_kernel_digest != expected_kernel_digest:
            findings.append(Finding("kernel_digest", "governance/registry/ACADEMIC_DOMAIN_PACK_REGISTRY.yaml", "recorded kernel digest does not match canonical schema_registry.json content"))

        fixtures = {name: _load_json(root / "tests" / "fixtures" / "academic_extensions" / name) for name in POSITIVE_FIXTURES}
        for name, schema_key in POSITIVE_FIXTURES.items():
            for message in schema_errors(fixtures[name], schemas[schema_key]):
                findings.append(Finding("positive_fixture_schema", f"tests/fixtures/academic_extensions/{name}", message))
        findings.extend(
            _semantic_fixture_findings(
                fixtures,
                root / "tests" / "fixtures" / "academic_extensions",
                root,
                expected_kernel_digest,
            )
        )
        metrics["positive_fixtures_checked"] = len(fixtures)

        negative_paths = sorted((root / "tests" / "fixtures" / "academic_extensions").glob("negative_*.json"))
        for path in negative_paths:
            descriptor = _load_json(path)
            base_name = descriptor.get("base_fixture")
            if base_name not in fixtures:
                findings.append(Finding("negative_fixture_base", path.name, "unknown base fixture"))
                continue
            candidate = _apply_mutation(fixtures[base_name], descriptor)
            observed_rules = negative_fixture_rules(
                base_name, candidate, fixtures, schemas, root
            )
            expected_rule = descriptor.get("expected_rule")
            if not isinstance(expected_rule, str) or expected_rule not in observed_rules:
                findings.append(
                    Finding(
                        "negative_fixture_not_rejected",
                        path.name,
                        f"expected {expected_rule!r}; observed {sorted(observed_rules)}",
                    )
                )
        metrics["negative_fixtures_checked"] = len(negative_paths)

        gates = _load_yaml_documents(root / PACKET_ROOT.relative_to(ROOT) / "human-decision-gates.yaml")[-1]
        gate_rows = gates.get("gates", []) if isinstance(gates, dict) else []
        gate_ids = {row.get("gate_id") for row in gate_rows if isinstance(row, dict)}
        if gate_ids != EXPECTED_GATES or any(row.get("status") != "blocked_human" for row in gate_rows):
            findings.append(Finding("human_gate_set", "human-decision-gates.yaml", "all eight exact gates must remain blocked_human"))

        matrix = _load_yaml_documents(root / PACKET_ROOT.relative_to(ROOT) / "acceptance-test-matrix.yaml")[-1]
        risk_rows = matrix.get("rows", []) if isinstance(matrix, dict) else []
        risk_ids = {row.get("risk_id") for row in risk_rows if isinstance(row, dict)}
        if risk_ids != EXPECTED_RISKS:
            findings.append(Finding("acceptance_risk_set", "acceptance-test-matrix.yaml", "expected the exact eleven red-team risks"))

        standards = _load_yaml_documents(root / PACKET_ROOT.relative_to(ROOT) / "standards-evidence.yaml")[-1]
        source_rows = standards.get("sources", []) if isinstance(standards, dict) else []
        source_ids = [row.get("standard_id") for row in source_rows if isinstance(row, dict)]
        if len(source_ids) != 9 or len(source_ids) != len(set(source_ids)):
            findings.append(Finding("standards_evidence", "standards-evidence.yaml", "expected nine unique official-source records"))
        if any(not str(row.get("official_url", "")).startswith("https://") for row in source_rows):
            findings.append(Finding("standards_url", "standards-evidence.yaml", "every standards record needs an HTTPS official URL"))

        mesh = _load_json(root / PACKET_ROOT.relative_to(ROOT) / "mesh" / "agent-mesh.v2.json")
        mesh_payload = {key: value for key, value in mesh.items() if key != "manifest_digest"}
        if mesh.get("manifest_digest") != canonical_digest(mesh_payload):
            findings.append(Finding("mesh_digest", "mesh/agent-mesh.v2.json", "manifest digest mismatch"))
        role_ids = {row.get("role_id") for row in mesh.get("roles", [])}
        if role_ids != {"academic-extension-writer", "academic-extension-checker", "human-campaign-sponsor"}:
            findings.append(Finding("mesh_role_set", "mesh/agent-mesh.v2.json", "unexpected current role set"))

        contract_text = (root / "docs" / "governance" / "academic-extension-contract.md").read_text(encoding="utf-8")
        contract_text_folded = contract_text.casefold()
        for phrase in REQUIRED_CONTRACT_PHRASES:
            if phrase.casefold() not in contract_text_folded:
                findings.append(Finding("contract_boundary_text", "docs/governance/academic-extension-contract.md", f"missing phrase {phrase!r}"))
        findings.extend(validate_frozen_digests(root))
        metrics["human_gates_checked"] = len(gate_rows)
        metrics["red_team_risks_checked"] = len(risk_rows)
        metrics["standards_records_checked"] = len(source_rows)
    except (ContractInputError, OSError, KeyError, TypeError, IndexError, jsonschema.SchemaError) as exc:
        findings.append(Finding("input_error", ".", str(exc)))
    return ValidationResult(tuple(sorted(set(findings))), metrics)


def _render(result: ValidationResult) -> dict[str, Any]:
    return {
        "status": "pass" if result.passed else "fail",
        "capability_classification": "portable_core",
        "network_used": False,
        "mutation_performed": False,
        "metrics": result.metrics,
        "findings": [finding.render() for finding in result.findings],
        "nonclaims": [
            "no academic or theological truth established",
            "no source or domain pack approved",
            "no runtime or interoperability adapter qualified",
            "no human gate closed",
        ],
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = validate_repository(args.root.resolve())
    print(json.dumps(_render(result), indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
