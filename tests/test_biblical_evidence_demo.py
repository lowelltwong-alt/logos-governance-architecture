from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

from scripts.validation_contracts import default_validation_commands


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_biblical_evidence_demo.py"
SPEC = importlib.util.spec_from_file_location("biblical_evidence_demo_validator", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def test_repository_demo_passes() -> None:
    result = validator.validate_repository(ROOT)
    assert result.passed, [finding.render() for finding in result.findings]


def test_demo_validator_is_registered_once() -> None:
    matches = [
        row
        for row in default_validation_commands("python")
        if row["name"] == "biblical_evidence_demonstration"
    ]
    assert matches == [
        {
            "name": "biblical_evidence_demonstration",
            "command": ["python", "scripts/validate_biblical_evidence_demo.py"],
        }
    ]


def test_exact_p66_asset_identity_and_dimensions() -> None:
    path = ROOT / validator.IMAGE_REL
    assert path.stat().st_size == validator.EXPECTED_IMAGE_BYTES
    assert validator.file_sha256(path) == validator.EXPECTED_IMAGE_SHA256
    assert validator.jpeg_dimensions(path) == validator.EXPECTED_IMAGE_DIMENSIONS


def test_p66_ranges_are_four_non_contiguous_segments() -> None:
    documents = validator.load_documents(ROOT)
    source = documents["p66_source"]
    observed = {
        row["segment_id"]: row["passage"] for row in source["coverage_segments"]
    }
    expected = {
        segment_id: values[0]
        for segment_id, values in validator.EXPECTED_SEGMENTS.items()
    }
    assert observed == expected
    assert source["coverage_is_non_contiguous"] is True
    assert source["forbidden_continuous_range"] not in set(observed.values())


def test_every_negative_fixture_is_executed_and_rejected() -> None:
    documents = validator.build_known_valid_fixture_baseline(validator.load_documents(ROOT), ROOT)
    fixture_doc = documents["adversarial_fixtures"]
    baseline = validator.validate_data(
        documents,
        ROOT,
        check_asset=False,
        check_frozen=False,
        check_fixtures=False,
        check_release=False,
    )
    assert baseline.passed, [finding.render() for finding in baseline.findings]
    baseline_findings = set(baseline.findings)
    for fixture in fixture_doc["fixtures"]:
        if fixture["target"] == "strict_parser":
            raw_findings = validator.raw_parser_fixture_findings(fixture["mutation"])
            assert fixture["expected_rule"] in {finding.rule for finding in raw_findings}, fixture["fixture_id"]
            continue
        candidate = validator.apply_fixture_mutation(documents, fixture["mutation"])
        assert validator._canonical_digest(candidate) != validator._canonical_digest(documents)
        result = validator.validate_data(
            candidate,
            ROOT,
            check_asset=False,
            check_frozen=False,
            check_fixtures=False,
            check_release=False,
        )
        rules = {finding.rule for finding in set(result.findings) - baseline_findings}
        assert fixture["expected_rule"] in rules, fixture["fixture_id"]


def test_graph_endpoints_resolve_and_authority_is_none() -> None:
    graph = validator.load_documents(ROOT)["evidence_graph"]
    node_ids = {node["id"] for node in graph["nodes"]}
    for edge in graph["edges"]:
        assert edge["from"] in node_ids
        assert edge["to"] in node_ids
        assert edge["authority_effect"] == "none"
        assert edge["relation"] not in validator.FORBIDDEN_RELATIONS


def test_m7_m8_states_cannot_be_laundered() -> None:
    crosswalk = validator.load_documents(ROOT)["p66_crosswalk"]
    public = crosswalk["source_layers"]["m7_public_metadata"]["durable_candidate"]
    local = crosswalk["source_layers"]["m7_local_corrective_observation"]
    m8 = crosswalk["source_layers"]["m8"]
    assert public["candidate_only"] is True
    assert public["non_authorizing"] is True
    assert public["lifecycle"] == "hold_with_findings"
    assert local["tracked_at_observation"] is False
    assert local["durable"] is False
    assert local["public_endpoint"] is None
    assert m8["john_status"] == "pending_not_built"
    assert m8["convergence_status"] == "not_started"


def test_mesh_research_and_review_roles_are_independent() -> None:
    mesh = validator.load_documents(ROOT)["agent_mesh"]
    invariants = mesh["execution_invariants"]
    assert invariants["single_writer"] is True
    assert invariants["researchers_are_read_only"] is True
    assert invariants["reviewers_are_read_only"] is True
    assert invariants["researcher_cannot_certify_own_citations"] is True
    assert invariants["rights_reviewer_is_distinct_from_asset_researcher"] is True
    assert invariants["maximum_delegation_depth"] == 1


def test_validator_is_offline_and_has_no_process_adapter() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    forbidden = (
        "import requests",
        "import socket",
        "urllib.request",
        "import httpx",
        "import subprocess",
        "os.system",
    )
    assert all(token not in source for token in forbidden)


def test_unknown_extension_policy_is_lossless_and_non_authorizing() -> None:
    catalog = validator.load_documents(ROOT)["node_edge_catalog"]
    policy = catalog["extension_policy"]
    assert policy["closed_world"] is False
    assert policy["unknown_extension_payloads_preserved_losslessly"] is True
    assert policy["unknown_relation_behavior"] == "preserve_but_do_not_traverse_for_authority"
    synthetic = {"future": {"array": [1, "two", None], "flag": True}}
    assert json.loads(json.dumps(synthetic, sort_keys=True)) == synthetic

    documents = validator.load_documents(ROOT)
    documents["evidence_graph"]["nodes"].extend(
        [
            {"id": "ext:test:a", "kind": "external_domain_extension", "label": "Opaque test A", "trust_zone": "proposed", "status": "extension_unreviewed_non_authorizing", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"future": {"node": "a"}}},
            {"id": "ext:test:b", "kind": "external_domain_extension", "label": "Opaque test B", "trust_zone": "proposed", "status": "extension_unreviewed_non_authorizing", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"future": {"node": "b"}}},
        ]
    )
    documents["evidence_graph"]["edges"].append(
        {
            "id": "ext-edge:test:one",
            "from": "ext:test:a",
            "relation": "ext:test:future-domain-link",
            "to": "ext:test:b",
            "authority_effect": "none",
            "extension_relation": True,
            "extension_payload": synthetic,
            "traversable_for_authority": False,
        }
    )
    result = validator.validate_data(
        documents,
        ROOT,
        check_asset=False,
        check_frozen=False,
        check_fixtures=False,
    )
    assert "extension_authority_noninterference" not in {finding.rule for finding in result.findings}
    round_trip = yaml.safe_load(yaml.safe_dump(documents["evidence_graph"], sort_keys=False))
    extension_edge = next(edge for edge in round_trip["edges"] if edge["id"] == "ext-edge:test:one")
    assert extension_edge["extension_payload"] == synthetic
    extension_node = next(node for node in round_trip["nodes"] if node["id"] == "ext:test:a")
    assert extension_node["extension_payload"] == {"future": {"node": "a"}}


def test_catalog_endpoint_kinds_are_enforced_for_every_registered_relation() -> None:
    documents = validator.load_documents(ROOT)
    result = validator.validate_data(
        validator.apply_fixture_mutation(documents, "add_image_displayed_through_english_edge"),
        ROOT,
        check_asset=False,
        check_frozen=False,
        check_fixtures=False,
    )
    assert "relation_kind_compatibility" in {finding.rule for finding in result.findings}


def test_catalog_cannot_widen_its_own_reviewed_endpoint_contract() -> None:
    documents = validator.load_documents(ROOT)
    changed = validator.apply_fixture_mutation(documents, "widen_displayed_through_and_add_image_edge")
    result = validator.validate_data(changed, ROOT, check_asset=False, check_frozen=False, check_fixtures=False)
    assert "relation_kind_compatibility" in {finding.rule for finding in result.findings}


@pytest.mark.parametrize("mutation, rule", [
    ("set_graph_m7_label_reviewed_gold", "m7_candidate_boundary"),
    ("add_graph_m7_alias_node", "m7_candidate_boundary"),
    ("set_graph_m8_label_built", "m8_pending_boundary"),
    ("add_graph_m8_alias_node", "m8_pending_boundary"),
])
def test_m7_m8_labels_and_aliases_cannot_launder_state(mutation: str, rule: str) -> None:
    documents = validator.load_documents(ROOT)
    changed = validator.apply_fixture_mutation(documents, mutation)
    result = validator.validate_data(changed, ROOT, check_asset=False, check_frozen=False, check_fixtures=False)
    assert rule in {finding.rule for finding in result.findings}


@pytest.mark.parametrize("mutation", ["add_canonical_external_node", "add_canonical_doctrine_node"])
def test_only_scripture_identity_nodes_can_be_canonical(mutation: str) -> None:
    documents = validator.load_documents(ROOT)
    changed = validator.apply_fixture_mutation(documents, mutation)
    result = validator.validate_data(changed, ROOT, check_asset=False, check_frozen=False, check_fixtures=False)
    assert "trust_zone_authority_path" in {finding.rule for finding in result.findings}


@pytest.mark.parametrize("mutation, rule", [
    ("pad_rights_reviewer_purpose", "mesh_role_instruction_depth"),
    ("change_rights_reviewer_class_to_writer", "mesh_role_permissions"),
    ("add_rights_reviewer_write_authority", "mesh_role_permissions"),
])
def test_role_contract_rejects_semantic_and_authority_drift(mutation: str, rule: str) -> None:
    documents = validator.load_documents(ROOT)
    changed = validator.apply_fixture_mutation(documents, mutation)
    result = validator.validate_data(changed, ROOT, check_asset=False, check_frozen=False, check_fixtures=False)
    assert rule in {finding.rule for finding in result.findings}


def test_completeness_receipt_rejects_truth_like_wrong_types() -> None:
    documents = validator.build_known_valid_fixture_baseline(validator.load_documents(ROOT), ROOT)
    changed = validator.apply_fixture_mutation(documents, "set_completeness_semantic_fields_to_wrong_types")
    result = validator.validate_data(changed, ROOT, check_asset=False, check_frozen=False, check_fixtures=False, check_release=False)
    assert "mesh_role_completeness" in {finding.rule for finding in result.findings}


def test_all_machine_document_identity_envelopes_are_exact() -> None:
    documents = validator.build_known_valid_fixture_baseline(validator.load_documents(ROOT), ROOT)
    assert set(validator.EXPECTED_DOCUMENT_ENVELOPES) == set(validator.DOCUMENT_FILES)
    assert validator._document_envelope_findings(documents) == []
    for key, expected in validator.EXPECTED_DOCUMENT_ENVELOPES.items():
        for field, value in expected.items():
            assert documents[key][field] == value
    for key in validator.DOCUMENT_FILES:
        changed = validator.build_known_valid_fixture_baseline(validator.load_documents(ROOT), ROOT)
        changed[key]["theological_authority"] = True
        assert validator._document_envelope_findings(changed), key


@pytest.mark.parametrize("mutation, rule", [
    ("add_external_m7_impersonator", "extension_authority_noninterference"),
    ("add_external_reserved_scripture_namespace", "graph_identity"),
    ("add_external_promoted_status", "extension_authority_noninterference"),
    ("add_external_source_claim_reuse", "graph_claim_identity"),
    ("add_external_confusable_identifier", "extension_authority_noninterference"),
    ("add_external_punctuation_impersonator", "extension_authority_noninterference"),
])
def test_external_nodes_cannot_impersonate_core_or_authority(mutation: str, rule: str) -> None:
    documents = validator.build_known_valid_fixture_baseline(validator.load_documents(ROOT), ROOT)
    changed = validator.apply_fixture_mutation(documents, mutation)
    result = validator.validate_data(changed, ROOT, check_asset=False, check_frozen=False, check_fixtures=False, check_release=False)
    assert rule in {finding.rule for finding in result.findings}


@pytest.mark.parametrize("mutation", [
    "add_unknown_relation_whitespace_spoof",
    "add_unknown_relation_case_spoof",
    "add_unknown_relation_confusable_spoof",
    "add_unknown_relation_protected_tail",
    "add_unknown_relation_punctuation_spoof",
])
def test_unknown_relations_cannot_visually_spoof_protected_semantics(mutation: str) -> None:
    documents = validator.build_known_valid_fixture_baseline(validator.load_documents(ROOT), ROOT)
    changed = validator.apply_fixture_mutation(documents, mutation)
    result = validator.validate_data(changed, ROOT, check_asset=False, check_frozen=False, check_fixtures=False, check_release=False)
    assert "extension_authority_noninterference" in {finding.rule for finding in result.findings}


def test_structured_late_discoveries_bind_evidence_and_block_midflight_publication() -> None:
    documents = validator.build_known_valid_fixture_baseline(validator.load_documents(ROOT), ROOT)
    phases = documents["completeness_receipt"]["phase_receipts"]
    assert phases[0]["late_discoveries"] == []
    assert phases[1]["late_discoveries"] == validator.expected_late_discoveries(ROOT, "midflight")
    assert phases[2]["late_discoveries"] == validator.expected_late_discoveries(ROOT, "exit")
    assert all(row["publication_allowed"] is False for row in phases[1]["late_discoveries"])
    assert all(row["publication_allowed"] is True for row in phases[2]["late_discoveries"])
    assert all(row["authority_effect"] == "none" for phase in phases for row in phase["late_discoveries"])


def test_review_pass_tokens_without_machine_frontmatter_are_rejected(tmp_path: Path) -> None:
    report = tmp_path / "review.md"
    report.write_text("Quoted instruction: Result: **PASS**\n1eacf8ac7c7f\n", encoding="utf-8")
    with pytest.raises(validator.DemoInputError, match="lacks YAML frontmatter"):
        validator._load_markdown_frontmatter(report)


@pytest.mark.parametrize("mutation", [
    "parse_duplicate_yaml_root_key",
    "parse_duplicate_json_nested_key",
    "parse_duplicate_review_frontmatter_key",
])
def test_duplicate_serialized_mapping_keys_fail_before_semantic_validation(mutation: str) -> None:
    findings = validator.raw_parser_fixture_findings(mutation)
    assert {finding.rule for finding in findings} == {"duplicate_mapping_key"}


def test_source_claim_projection_is_exact_and_exhaustive() -> None:
    documents = validator.load_documents(ROOT)
    graph = documents["evidence_graph"]
    claim_to_graph = {
        node["source_claim_id"]: node["id"]
        for node in graph["nodes"]
        if node.get("kind") == "historical_claim"
    }
    expected = {
        (source_id, claim_to_graph[claim["claim_id"]])
        for claim in documents["archaeology_source_pack"]["claim_records"]
        for source_id in claim["source_refs"]
    }
    observed = {(edge["source"], edge["claim"]) for edge in graph["source_claim_edges"]}
    assert observed == expected


def test_crosswalk_provenance_and_m8_checkpoint_are_exact() -> None:
    documents = validator.load_documents(ROOT)
    crosswalk = documents["p66_crosswalk"]
    assert validator._canonical_digest(crosswalk["source_layers"]) == validator.EXPECTED_CROSSWALK_SOURCE_LAYERS_DIGEST
    assert validator._canonical_digest(crosswalk["segments"]) == validator.EXPECTED_CROSSWALK_SEGMENTS_DIGEST
    assert validator._canonical_digest(crosswalk["invariants"]) == validator.EXPECTED_CROSSWALK_INVARIANTS_DIGEST
    assert crosswalk["source_layers"]["m8"] == {
        "repository": "lowelltwong-alt/logos-scripture-graph",
        "branch": "scratch/t423-m8-fable",
        "checkpoint_head": "35dc82b391ae8971e059c405edf0f3df77489f3e",
        "books_completed": 22,
        "books_total": 66,
        "current_book": "Isa",
        "john_status": "pending_not_built",
        "convergence_status": "not_started",
    }


def test_core_graph_catalog_and_source_claim_semantics_are_digest_pinned() -> None:
    documents = validator.load_documents(ROOT)
    graph = documents["evidence_graph"]
    catalog = documents["node_edge_catalog"]
    assert validator._canonical_digest(catalog["node_kinds"]) == validator.EXPECTED_CATALOG_NODE_KINDS_DIGEST
    assert validator._canonical_digest(catalog["relation_kinds"]) == validator.EXPECTED_CATALOG_RELATIONS_DIGEST
    assert validator._canonical_digest(graph["nodes"]) == validator.EXPECTED_GRAPH_CORE_NODES_DIGEST
    assert validator._canonical_digest(graph["edges"]) == validator.EXPECTED_GRAPH_CORE_EDGES_DIGEST
    assert validator._canonical_digest(graph["source_claim_edges"]) == validator.EXPECTED_GRAPH_SOURCE_CLAIM_EDGES_DIGEST


def test_completeness_inputs_bind_code_reviews_base_and_execution_fingerprint() -> None:
    documents = validator.load_documents(ROOT)
    digests = validator.completeness_input_digests(documents, ROOT)
    assert {
        "frozen_manifest_digest",
        "candidate_base_commit_digest",
        "validator_digest",
        "focused_test_digest",
        "adversarial_fixture_digest",
        "independent_review_evidence_digest",
        "execution_environment_fingerprint_digest",
    } <= set(digests)
    assert all(value.startswith("sha256:") and len(value) == 71 for value in digests.values())


def test_all_machine_documents_parse() -> None:
    package = ROOT / validator.PACKAGE_REL
    for path in package.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in {".yaml", ".yml"}:
            assert yaml.safe_load(path.read_text(encoding="utf-8")) is not None
        elif path.suffix == ".json":
            assert json.loads(path.read_text(encoding="utf-8")) is not None


def test_frozen_manifest_covers_exact_non_receipt_package() -> None:
    manifest_path = ROOT / validator.PACKAGE_REL / "frozen-digests.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    observed = {row["path"] for row in manifest["files"]}
    assert observed == set(validator.expected_frozen_paths(ROOT))
    assert validator._frozen_findings(ROOT) == []


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "extra", "malformed", "reordered"])
def test_frozen_manifest_rejects_invalid_row_sets(tmp_path: Path, mutation: str) -> None:
    source = ROOT / validator.PACKAGE_REL
    target = tmp_path / validator.PACKAGE_REL
    shutil.copytree(source, target)
    manifest_path = target / "frozen-digests.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if mutation == "duplicate":
        manifest["files"].append(dict(manifest["files"][0]))
    elif mutation == "missing":
        manifest["files"].pop()
    elif mutation == "extra":
        manifest["files"].append({"path": "unexpected.txt", "sha256": "0" * 64, "bytes": 0})
    elif mutation == "malformed":
        manifest["files"].append({"sha256": "0" * 64, "bytes": 0})
    else:
        manifest["files"][0], manifest["files"][1] = manifest["files"][1], manifest["files"][0]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    findings = validator._frozen_findings(tmp_path)
    assert "frozen_digest_manifest" in {finding.rule for finding in findings}
