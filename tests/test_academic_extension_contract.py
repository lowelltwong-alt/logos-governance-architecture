from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_academic_extension_contract.py"
SPEC = importlib.util.spec_from_file_location("academic_extension_validator", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def test_repository_contract_passes() -> None:
    result = validator.validate_repository(ROOT)
    assert result.passed, [finding.render() for finding in result.findings]


@pytest.mark.parametrize("name,schema_key", sorted(validator.POSITIVE_FIXTURES.items()))
def test_positive_fixtures_conform(name: str, schema_key: str) -> None:
    schemas = validator.load_schemas(ROOT)
    record = json.loads((ROOT / "tests" / "fixtures" / "academic_extensions" / name).read_text(encoding="utf-8"))
    assert validator.schema_errors(record, schemas[schema_key]) == []


@pytest.mark.parametrize(
    "path",
    sorted((ROOT / "tests" / "fixtures" / "academic_extensions").glob("negative_*.json")),
    ids=lambda path: path.stem,
)
def test_adversarial_mutations_are_rejected(path: Path) -> None:
    descriptor = json.loads(path.read_text(encoding="utf-8"))
    fixture_root = ROOT / "tests" / "fixtures" / "academic_extensions"
    base_name = descriptor["base_fixture"]
    base = json.loads((fixture_root / base_name).read_text(encoding="utf-8"))
    candidate = validator._apply_mutation(base, descriptor)
    schemas = validator.load_schemas(ROOT)
    fixtures = {
        name: json.loads((fixture_root / name).read_text(encoding="utf-8"))
        for name in validator.POSITIVE_FIXTURES
    }
    observed = validator.negative_fixture_rules(
        base_name, candidate, fixtures, schemas, ROOT
    )
    assert descriptor["expected_rule"] in observed


def test_source_digest_drift_invalidates_projection() -> None:
    fixture_root = ROOT / "tests" / "fixtures" / "academic_extensions"
    source = json.loads((fixture_root / "positive_source_record.json").read_text(encoding="utf-8"))
    projection = json.loads((fixture_root / "positive_derived_projection.json").read_text(encoding="utf-8"))
    changed = copy.deepcopy(source)
    changed["source_payload"]["version_or_edition"] = "fixture-v2"
    changed_digest = validator.canonical_digest(changed["source_payload"])
    assert changed_digest != projection["source_digest"]
    assert projection["invalidation_policy"] == "invalidate_on_source_digest_drift"


def test_unknown_extension_payload_round_trips_losslessly() -> None:
    path = ROOT / "tests" / "fixtures" / "academic_extensions" / "positive_assertion.json"
    assertion = json.loads(path.read_text(encoding="utf-8"))
    envelope = assertion["extension_payload"]
    payload = envelope["payload_data"]
    assert json.loads(json.dumps(payload, sort_keys=True, ensure_ascii=False)) == payload
    assert envelope["payload_digest"] == validator.canonical_digest(payload)


def test_registry_manifest_identity_cannot_be_laundered_with_consumer_id() -> None:
    fixture_root = ROOT / "tests" / "fixtures" / "academic_extensions"
    fixtures = {
        name: json.loads((fixture_root / name).read_text(encoding="utf-8"))
        for name in validator.POSITIVE_FIXTURES
    }
    candidate = copy.deepcopy(fixtures["positive_extension_registry.json"])
    candidate["packs"][0]["pack_id"] = "academic.registry-mismatch"
    candidate["consumers"][0]["pack_id"] = "academic.registry-mismatch"
    schemas = validator.load_schemas(ROOT)
    rules = validator.negative_fixture_rules(
        "positive_extension_registry.json", candidate, fixtures, schemas, ROOT
    )
    assert "registry_manifest_identity" in rules


def test_production_registry_contains_no_real_pack() -> None:
    documents = validator._load_yaml_documents(
        ROOT / "governance" / "registry" / "ACADEMIC_DOMAIN_PACK_REGISTRY.yaml"
    )
    assert documents[-1]["packs"] == []
    assert documents[-1]["consumers"] == []
    assert documents[-1]["authority_ceiling"] == "registry_is_non_authorizing"


def test_validator_has_no_network_or_process_adapter() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    forbidden = ("import requests", "import socket", "urllib.request", "subprocess", "httpx")
    assert all(token not in source for token in forbidden)


def test_frozen_digest_manifest_replays() -> None:
    assert validator.validate_frozen_digests(ROOT) == []


def test_file_digest_is_stable_across_lf_and_crlf_checkouts(tmp_path: Path) -> None:
    lf_path = tmp_path / "lf.txt"
    crlf_path = tmp_path / "crlf.txt"
    cr_path = tmp_path / "cr.txt"
    lf_path.write_bytes(b"first\nsecond\n")
    crlf_path.write_bytes(b"first\r\nsecond\r\n")
    cr_path.write_bytes(b"first\rsecond\r")

    assert validator.file_digest(lf_path) == validator.file_digest(crlf_path)
    assert validator.file_digest(lf_path) == validator.file_digest(cr_path)


def test_file_digest_preserves_non_utf8_binary_bytes(tmp_path: Path) -> None:
    first_path = tmp_path / "first.bin"
    second_path = tmp_path / "second.bin"
    first_path.write_bytes(b"\xff\r\n")
    second_path.write_bytes(b"\xff\n")

    assert validator.file_digest(first_path) != validator.file_digest(second_path)


def test_duplicate_pack_namespace_is_rejected() -> None:
    fixture_root = ROOT / "tests" / "fixtures" / "academic_extensions"
    registry = json.loads((fixture_root / "positive_extension_registry.json").read_text(encoding="utf-8"))
    duplicate = copy.deepcopy(registry["packs"][0])
    duplicate["pack_id"] = "academic.second-pack"
    registry["packs"].append(duplicate)
    registry["consumers"].append(
        {
            "consumer_id": "synthetic-second-consumer",
            "pack_id": "academic.second-pack",
            "contract_ref": "tests/test_academic_extension_contract.py",
            "compatibility": "tested",
        }
    )
    rules = {finding.rule for finding in validator._registry_semantic_findings(registry, ROOT)}
    assert "pack_namespace_collision" in rules
