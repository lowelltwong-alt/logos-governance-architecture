from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import jsonschema
import pytest
import yaml

from scripts import validate_portfolio_front_door as validator
from scripts.validation_contracts import default_validation_commands


ROOT = Path(__file__).resolve().parents[1]

P66_DEMO_ROOT = Path(
    "docs/roadmap/logos-stewardship-architecture-buildout/"
    "revisions/biblical-evidence-demonstration-v1"
)
P66_PUBLIC_ROUTE = (
    P66_DEMO_ROOT / "assets/p66-cologne-john19-verso.jpg",
    P66_DEMO_ROOT / "sources/p66-source-and-rights.yaml",
    P66_DEMO_ROOT / "graph/p66-chunk-crosswalk.yaml",
    P66_DEMO_ROOT / "graph/evidence-graph.yaml",
    P66_DEMO_ROOT / "graph/node-edge-catalog.yaml",
    P66_DEMO_ROOT / "mesh/agent-mesh.v3.json",
    P66_DEMO_ROOT / "mesh/completeness-audit-contract.yaml",
    P66_DEMO_ROOT / "release/exit-completeness-audit.yaml",
    P66_DEMO_ROOT / "validation-receipt.json",
)
DOCTRINE_MARATHON_ROOT = Path(
    "docs/roadmap/logos-stewardship-architecture-buildout/"
    "revisions/doctrine-marathon-v3"
)
DOCTRINE_MARATHON_HARNESS_PUBLIC_EVIDENCE = (
    DOCTRINE_MARATHON_ROOT / "checks/adversarial-harness-migration.yaml",
    DOCTRINE_MARATHON_ROOT / "checks/ADVERSARIAL_HARNESS_ROOT_FIX.md",
    DOCTRINE_MARATHON_ROOT / "checks/DETERMINISTIC_ADVERSARIAL_HARNESS_CONTRACT.md",
    DOCTRINE_MARATHON_ROOT / "checks/fixtures/strict-isolated-cases.json",
    DOCTRINE_MARATHON_ROOT / "checks/fixtures/aggregate-sentinel-cases.json",
    DOCTRINE_MARATHON_ROOT / "checks/run_adversarial_harness.py",
    DOCTRINE_MARATHON_ROOT / "checks/test_run_adversarial_harness.py",
)
DOCTRINE_MARATHON_PUBLIC_ROUTE = (
    DOCTRINE_MARATHON_ROOT / "README.md",
    DOCTRINE_MARATHON_ROOT / "DOCTRINE_MARATHON_MASTER_PROMPT.md",
    DOCTRINE_MARATHON_ROOT / "state/goal.yaml",
    DOCTRINE_MARATHON_ROOT / "mesh/agent-mesh.v3.json",
    DOCTRINE_MARATHON_ROOT / "mesh/completeness-auditor-v3.yaml",
    DOCTRINE_MARATHON_ROOT / "mesh/examples/design-time-independence-fixture.json",
    DOCTRINE_MARATHON_ROOT / "mesh/role-assignment-bundle.schema.json",
    DOCTRINE_MARATHON_ROOT / "mesh/role-catalog.yaml",
    DOCTRINE_MARATHON_ROOT / "mesh/qualification-registry.json",
    DOCTRINE_MARATHON_ROOT / "mesh/qualification-receipt.schema.json",
    DOCTRINE_MARATHON_ROOT / "mesh/correlation-acceptance-receipt.schema.json",
    DOCTRINE_MARATHON_ROOT / "evidence/evidence-registry.json",
    DOCTRINE_MARATHON_ROOT / "evidence/evidence-review-receipt.schema.json",
    DOCTRINE_MARATHON_ROOT / "research/father-expert-pack-contract.yaml",
    DOCTRINE_MARATHON_ROOT / "research/environment-pack-contract.yaml",
    DOCTRINE_MARATHON_ROOT / "firewall/epistemic-integrity-contract.yaml",
    DOCTRINE_MARATHON_ROOT / "firewall/trigger-matrix.yaml",
    DOCTRINE_MARATHON_ROOT / "firewall/action-checker-requirements.yaml",
    DOCTRINE_MARATHON_ROOT / "firewall/prompt-neutrality-contract.yaml",
    DOCTRINE_MARATHON_ROOT / "events/marathon-event.schema.json",
    DOCTRINE_MARATHON_ROOT / "events/event-ledger.json",
    DOCTRINE_MARATHON_ROOT / "state/fresh-context-verification-receipt.schema.json",
    DOCTRINE_MARATHON_ROOT / "state/examples/initial-weekly-fresh-context-gate.json",
    DOCTRINE_MARATHON_ROOT / "graph/event-driven-invalidation-contract.yaml",
    DOCTRINE_MARATHON_ROOT / "graph/human-identity-authority-root.yaml",
    DOCTRINE_MARATHON_ROOT / "graph/authority-registry.yaml",
    DOCTRINE_MARATHON_ROOT / "debt/initial-review-debt.json",
    DOCTRINE_MARATHON_ROOT / "redteam/premortem.yaml",
    DOCTRINE_MARATHON_ROOT / "redteam/repair-ledger.yaml",
    DOCTRINE_MARATHON_ROOT / "redteam/ai-mistake-escalation-2026-08-27.yaml",
    DOCTRINE_MARATHON_ROOT / "checks/fixtures/negative-cases.json",
    DOCTRINE_MARATHON_ROOT / "revision-manifest.yaml",
    DOCTRINE_MARATHON_ROOT / "FINAL-SAVED-VERSION.yaml",
    DOCTRINE_MARATHON_ROOT / "checks/validation-receipt.json",
    DOCTRINE_MARATHON_ROOT / "checks/independent-review.json",
    DOCTRINE_MARATHON_ROOT / "checks/public-release-authorization.json",
) + DOCTRINE_MARATHON_HARNESS_PUBLIC_EVIDENCE
DOCTRINE_MARATHON_FRONT_DOOR_ROUTE = tuple(
    path
    for path in DOCTRINE_MARATHON_PUBLIC_ROUTE
    if path not in DOCTRINE_MARATHON_HARNESS_PUBLIC_EVIDENCE
)


def test_portfolio_content_digest_is_checkout_newline_stable() -> None:
    assert validator._canonical_content_bytes(b"alpha\nbeta\n") == validator._canonical_content_bytes(
        b"alpha\r\nbeta\r\n"
    )


def test_raw_validation_result_preserves_order_and_duplicate_identities() -> None:
    findings = [
        validator.Finding("z_rule", "z", "emitted first"),
        validator.Finding("a_rule", "a", "emitted second"),
        validator.Finding("z_rule", "z", "emitted first"),
    ]

    result = validator._raw_validation_result(findings, {"fixture": 1})

    assert result.findings == tuple(findings)
    assert len(result.findings) == 3

    payload = validator._result_payload(result)
    assert payload["findings_raw"] == [
        {"rule": item.rule, "path": item.path, "detail": item.detail}
        for item in findings
    ]
    assert payload["findings"] == [item.render() for item in findings]
    assert len(payload["findings"]) == 3
    assert payload["findings_presentation"] == sorted(
        {item.render() for item in findings}
    )


def test_public_structured_loaders_reject_duplicate_keys(tmp_path: Path) -> None:
    duplicate_json = tmp_path / "duplicate.json"
    duplicate_json.write_text('{"maturity": false, "maturity": true}\n', encoding="utf-8")
    with pytest.raises(validator.PortfolioValidationError, match="duplicate key"):
        validator._load_json(duplicate_json)

    duplicate_yaml = tmp_path / "duplicate.yaml"
    duplicate_yaml.write_text("maturity: false\nmaturity: true\n", encoding="utf-8")
    with pytest.raises(validator.PortfolioValidationError, match="duplicate key"):
        validator._load_yaml(duplicate_yaml)


def test_validation_input_snapshot_changes_with_exact_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "input.txt"
    target.write_text("before\n", encoding="utf-8")
    monkeypatch.setattr(validator, "EXPECTED_PUBLIC_FILES", ("input.txt",))
    monkeypatch.setattr(validator, "EXPECTED_NAVIGATION_FILES", ())

    before, before_count = validator._validation_input_snapshot(tmp_path, {})
    target.write_text("after\n", encoding="utf-8")
    after, after_count = validator._validation_input_snapshot(tmp_path, {})

    assert before_count == after_count
    assert before_count >= 1
    assert before != after


def test_loaded_aggregate_oracle_derives_marathon_paths_from_supplied_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    observed: dict[str, Path] = {}
    monkeypatch.setattr(validator, "EXPECTED_PUBLIC_FILES", ())
    monkeypatch.setattr(validator, "_check_manifest_schema", lambda *args: [])
    monkeypatch.setattr(validator, "_check_receipt_schema", lambda *args: [])
    monkeypatch.setattr(validator, "_check_evidence_references", lambda *args: [])
    monkeypatch.setattr(validator, "_check_repository_inventory", lambda *args: [])
    monkeypatch.setattr(validator, "_check_interrogation_route", lambda *args: [])
    monkeypatch.setattr(validator, "_check_release_scope", lambda *args: ([], {}))
    monkeypatch.setattr(validator, "_check_agent_mesh", lambda *args: [])
    monkeypatch.setattr(validator, "_check_doctrine_freeze", lambda *args: ([], {}))
    monkeypatch.setattr(validator, "_check_portfolio_prose", lambda *args: ([], {}))
    monkeypatch.setattr(validator, "_check_navigation", lambda *args: [])
    monkeypatch.setattr(validator, "_check_receipt_payload", lambda *args: [])

    def fake_marathon(
        manifest: dict, marathon_root: Path, validator_path: Path, root: Path
    ) -> tuple[list[validator.Finding], dict[str, int]]:
        observed["root"] = marathon_root
        observed["validator"] = validator_path
        return [], {}

    monkeypatch.setattr(validator, "_check_marathon_freeze", fake_marathon)
    result = validator._validate_loaded_repository(
        tmp_path, manifest={}, schema={}, portfolio_receipt={}
    )

    expected_root = (
        tmp_path
        / "docs/roadmap/logos-stewardship-architecture-buildout/"
        "revisions/doctrine-marathon-v3"
    ).resolve()
    assert result.findings == ()
    assert observed["root"] == expected_root
    assert observed["validator"] == (
        expected_root / "checks/validate_doctrine_marathon.py"
    )


def test_duplicate_evidence_route_ids_fail_without_dict_collapse(tmp_path: Path) -> None:
    route = {
        "route_id": "duplicate-route",
        "question": "synthetic",
        "start_at": "https://example.invalid/start",
        "then_read": [],
    }
    findings = validator._check_evidence_references(
        {"evidence_routes": [copy.deepcopy(route), copy.deepcopy(route)]},
        tmp_path,
    )
    assert findings == [
        validator.Finding(
            "evidence_route_identity",
            "project-evidence.yaml",
            "evidence route IDs must be non-empty and unique",
        )
    ]


def test_v3_final_replay_accepts_only_the_declared_blocker_in_order() -> None:
    blocker = validator.DECLARED_V3_FINAL_BLOCKER

    assert validator._v3_final_replay_is_exact([blocker]) is True
    assert validator._v3_final_replay_is_exact([blocker, "unexpected"]) is False
    assert validator._v3_final_replay_is_exact([]) is False


def test_evidence_resolver_requires_an_in_root_regular_file(tmp_path: Path) -> None:
    regular = tmp_path / "evidence" / "receipt.json"
    regular.parent.mkdir()
    regular.write_text("{}\n", encoding="utf-8")

    assert validator._resolve_in_root_regular_file(
        tmp_path, Path("evidence/receipt.json")
    ) == regular.resolve(strict=True)
    with pytest.raises(validator.PortfolioValidationError, match="regular file"):
        validator._resolve_in_root_regular_file(tmp_path, Path("evidence"))


def load_manifest() -> dict:
    return yaml.safe_load(
        (ROOT / "docs/portfolio/logos-trust-layer/project-evidence.yaml").read_text(
            encoding="utf-8"
        )
    )


def load_schema() -> dict:
    return json.loads(
        (
            ROOT
            / "docs/portfolio/logos-trust-layer/project-evidence.schema.json"
        ).read_text(encoding="utf-8")
    )


def load_receipt() -> dict:
    return json.loads(
        (
            ROOT
            / "docs/portfolio/logos-trust-layer/validation-receipt.json"
        ).read_text(encoding="utf-8")
    )


def _canonical_loaded_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _marathon_catalog_source_digests() -> dict[str, str]:
    return {
        relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        for relative in (
            (
                DOCTRINE_MARATHON_ROOT
                / "checks/fixtures/negative-cases.json"
            ).as_posix(),
            (
                DOCTRINE_MARATHON_ROOT
                / "checks/fixtures/strict-isolated-cases.json"
            ).as_posix(),
            (
                DOCTRINE_MARATHON_ROOT
                / "checks/fixtures/aggregate-sentinel-cases.json"
            ).as_posix(),
        )
    }


PORTFOLIO_ORACLE_SENTINELS = (
    (
        "portfolio-v3-maturity-overclaim",
        validator.Finding(
            "marathon_maturity",
            "project-evidence.yaml",
            "V3 maturity must remain blocked_specification_only until the aggregate exact-oracle migration is complete and independently reviewed",
        ),
        {"manifest", "schema"},
    ),
    (
        "portfolio-v3-migration-gate-erasure",
        validator.Finding(
            "marathon_declared_blocker",
            "project-evidence.yaml",
            "V3 declared final blocker must equal the aggregate exact-oracle release gate",
        ),
        {"manifest", "schema"},
    ),
    (
        "portfolio-v3-authority-elevation",
        validator.Finding(
            "marathon_authority_boundary",
            "project-evidence.yaml",
            "qualified_theological_authority must remain false",
        ),
        {"manifest", "schema"},
    ),
    (
        "portfolio-v3-required-route-omission",
        validator.Finding(
            "marathon_public_evidence_route",
            "project-evidence.yaml",
            "V3 audit route is missing or not exact",
        ),
        {"manifest"},
    ),
    (
        "portfolio-release-chain-drift",
        validator.Finding(
            "release_scope_digest",
            "docs/portfolio/logos-trust-layer/validation-receipt.json",
            "Release 004 active increment did not replay exactly",
        ),
        {"receipt"},
    ),
)


def _mutate_portfolio_oracle_inputs(
    case_id: str,
    manifest: dict,
    schema: dict,
    receipt: dict,
) -> None:
    marathon_schema = schema["$defs"]["doctrineMarathon"]
    marathon = manifest["doctrine_marathon_specification"]
    if case_id == "portfolio-v3-maturity-overclaim":
        marathon["maturity"] = "validated_specification_only"
        marathon_schema["properties"]["maturity"]["const"] = (
            "validated_specification_only"
        )
    elif case_id == "portfolio-v3-migration-gate-erasure":
        marathon.pop("declared_final_blocker")
        marathon_schema["required"].remove("declared_final_blocker")
    elif case_id == "portfolio-v3-authority-elevation":
        marathon["qualified_theological_authority"] = True
        marathon_schema["properties"]["qualified_theological_authority"][
            "const"
        ] = True
    elif case_id == "portfolio-v3-required-route-omission":
        route = next(
            row
            for row in manifest["evidence_routes"]
            if row["route_id"] == "doctrine-marathon-v3-audit"
        )
        route["then_read"].remove(
            (
                DOCTRINE_MARATHON_ROOT
                / "checks/adversarial-harness-migration.yaml"
            ).as_posix()
        )
    elif case_id == "portfolio-release-chain-drift":
        assert receipt["schema_version"] == "logos.portfolio_validation_receipt.v3"
        receipt["release_chain"]["active_increment"]["content_digest"] = (
            "sha256:" + "0" * 64
        )
        receipt["receipt_digest"] = validator._canonical_digest(
            receipt, ("receipt_digest",)
        )
    else:  # pragma: no cover - the parametrized catalog is closed above
        raise AssertionError(case_id)


@pytest.mark.parametrize(
    ("case_id", "expected", "changed_inputs"),
    PORTFOLIO_ORACLE_SENTINELS,
    ids=[row[0] for row in PORTFOLIO_ORACLE_SENTINELS],
)
def test_portfolio_aggregate_oracle_sentinels_are_exact_and_isolated(
    case_id: str,
    expected: validator.Finding,
    changed_inputs: set[str],
) -> None:
    source_digests = _marathon_catalog_source_digests()
    baseline_inputs = {
        "manifest": load_manifest(),
        "schema": load_schema(),
        "receipt": load_receipt(),
    }
    baseline_result = validator._validate_loaded_repository(
        ROOT,
        manifest=baseline_inputs["manifest"],
        schema=baseline_inputs["schema"],
        portfolio_receipt=baseline_inputs["receipt"],
    )
    assert baseline_result.findings == ()
    assert baseline_result.metrics["marathon_component_source_case_count"] == 197
    assert (
        baseline_result.metrics["marathon_aggregate_sentinel_subset_case_count"]
        == 4
    )

    candidate = copy.deepcopy(baseline_inputs)
    before = {
        key: _canonical_loaded_bytes(value)
        for key, value in candidate.items()
    }
    _mutate_portfolio_oracle_inputs(
        case_id,
        candidate["manifest"],
        candidate["schema"],
        candidate["receipt"],
    )
    after = {
        key: _canonical_loaded_bytes(value)
        for key, value in candidate.items()
    }
    assert {key for key in before if before[key] != after[key]} == changed_inputs

    candidate_result = validator._validate_loaded_repository(
        ROOT,
        manifest=candidate["manifest"],
        schema=candidate["schema"],
        portfolio_receipt=candidate["receipt"],
    )
    assert candidate_result.findings == (expected,)
    assert candidate_result.metrics["marathon_component_source_case_count"] == 197
    assert (
        candidate_result.metrics["marathon_aggregate_sentinel_subset_case_count"]
        == 4
    )

    replay_inputs = {
        "manifest": load_manifest(),
        "schema": load_schema(),
        "receipt": load_receipt(),
    }
    replay_result = validator._validate_loaded_repository(
        ROOT,
        manifest=replay_inputs["manifest"],
        schema=replay_inputs["schema"],
        portfolio_receipt=replay_inputs["receipt"],
    )
    assert replay_result.findings == ()
    assert _marathon_catalog_source_digests() == source_digests


def load_p66_yaml(relative_path: str) -> dict:
    return yaml.safe_load(
        (ROOT / P66_DEMO_ROOT / relative_path).read_text(encoding="utf-8")
    )


def load_p66_json(relative_path: str) -> dict:
    return json.loads(
        (ROOT / P66_DEMO_ROOT / relative_path).read_text(encoding="utf-8")
    )


def test_public_portfolio_candidate_passes() -> None:
    result = validator.validate_repository(ROOT)

    assert result.findings == ()
    assert result.metrics["doctrine_managed_files"] == 90
    assert result.metrics["doctrine_static_failures"] == 0
    assert result.metrics["marathon_managed_files"] == 83
    assert result.metrics["marathon_static_failures"] == 1
    assert result.metrics["marathon_unexpected_final_findings"] == 0
    assert result.metrics["mermaid_diagrams"] >= 5
    assert result.metrics["diagram_prose_readings"] == result.metrics["mermaid_diagrams"]


@pytest.mark.parametrize("entry_point", ["PORTFOLIO.md", "AI_FRONT_DOOR.md"])
def test_p66_public_route_is_direct_complete_and_non_translation_claiming(
    entry_point: str,
) -> None:
    text = (ROOT / entry_point).read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    for relative_path in P66_PUBLIC_ROUTE:
        assert (ROOT / relative_path).is_file()
        assert f"({relative_path.as_posix()})" in text

    required_boundaries = (
        "The English display is not translated from the image.",
        "Diplomatic transcription",
        "Greek alignment",
        "textual-variant analysis",
        "witness-specific translation",
        "qualified specialist review",
        "explicit human approval remain future gates",
        "entry, midflight, and exit",
    )
    for boundary in required_boundaries:
        assert boundary.casefold() in normalized.casefold()


def test_p66_linked_records_preserve_translation_and_authority_boundaries() -> None:
    source = load_p66_yaml("sources/p66-source-and-rights.yaml")
    crosswalk = load_p66_yaml("graph/p66-chunk-crosswalk.yaml")
    graph = load_p66_yaml("graph/evidence-graph.yaml")
    catalog = load_p66_yaml("graph/node-edge-catalog.yaml")
    mesh = load_p66_json("mesh/agent-mesh.v3.json")
    contract = load_p66_yaml("mesh/completeness-audit-contract.yaml")
    exit_audit = load_p66_yaml("release/exit-completeness-audit.yaml")
    receipt = load_p66_json("validation-receipt.json")

    assert source["rights"]["license_id"] == "CC-BY-4.0"
    assert source["asset"]["byte_verification"]["local_remote_match"] is True
    assert len(source["object_catalog_coverage_segments"]) == 4
    assert source["object_catalog_coverage_is_non_contiguous"] is True
    assert source["authority"]["image_is_translation"] is False
    source_layers = {row["layer_id"]: row for row in source["layers"]}
    assert source_layers["diplomatic_transcription"]["included"] is False
    assert source_layers["critical_greek_edition"]["included"] is False
    assert source_layers["english_translation_display"]["source_ref"] != source[
        "record_id"
    ]

    assert crosswalk["source_layers"]["english"]["rights"] == "public-domain"
    assert crosswalk["source_layers"]["english"]["source_record_ref"] != crosswalk[
        "source_layers"
    ]["p66"]["record_ref"]
    assert crosswalk["invariants"]["image_to_english_direct_edge_allowed"] is False
    assert crosswalk["invariants"]["transcription_claimed_from_image"] is False
    assert crosswalk["invariants"]["m8_complete"] is False
    assert crosswalk["invariants"]["convergence_started"] is False

    assert all(edge["authority_effect"] == "none" for edge in graph["edges"])
    assert graph["invariants"]["no_path_promotes_to_doctrine"] is True
    assert "image_directly_translates_to" in catalog["forbidden_relations"]

    completeness_role = next(
        role for role in mesh["roles"] if role["role_id"] == "role-completeness-auditor"
    )
    assert "entry, midflight, and exit" in completeness_role["purpose"]
    assert contract["phases"] == ["entry", "midflight", "exit"]
    assert [row["phase"] for row in exit_audit["phase_receipts"]] == [
        "entry",
        "midflight",
        "exit",
    ]
    assert all(row["result"] == "pass" for row in exit_audit["phase_receipts"])
    assert exit_audit["status"] == "pass"
    assert receipt["status"] == "validated_static_demonstration"
    assert receipt["authority_granted"] is False
    assert receipt["mutation_performed"] is False


def test_p66_claim_bookkeeping_uses_a_durable_authorization_reference() -> None:
    registry = yaml.safe_load(
        (ROOT / "governance/registry/FAMILY_WORK_REGISTRY.yaml").read_text(
            encoding="utf-8"
        )
    )
    resolution = next(
        row
        for row in registry["overlap_resolutions"]
        if row["resolution_id"] == "OVERLAP-W27-P66-PORTFOLIO-CLARITY-001"
    )
    claim = next(
        row
        for row in registry["work_items"]
        if row["work_id"] == "WORK-GOV-P66-PORTFOLIO-CLARITY-001"
    )

    assert resolution["owner_decision_ref"] == (
        "lowell_owner_authorization_2026-08-27_p66_portfolio_clarity"
    )
    assert "chat" not in resolution["owner_decision_ref"].casefold()
    assert set(claim["claimed_paths"]) == {
        "governance/registry/FAMILY_WORK_REGISTRY.yaml",
        "PORTFOLIO.md",
        "AI_FRONT_DOOR.md",
        "tests/test_portfolio_front_door.py",
    }
    assert "no_source_ingestion_translation" in claim["authority_ceiling"]


def test_portfolio_validator_is_registered_once() -> None:
    matches = [
        item
        for item in default_validation_commands("python")
        if item["name"] == "portfolio_front_door"
    ]

    assert matches == [
        {
            "name": "portfolio_front_door",
            "command": ["python", "scripts/validate_portfolio_front_door.py"],
        }
    ]


def test_doctrine_marathon_validator_is_registered_once() -> None:
    matches = [
        item
        for item in default_validation_commands("python")
        if item["name"] == "doctrine_marathon_v3"
    ]

    assert matches == [
        {
            "name": "doctrine_marathon_v3",
            "command": [
                "python",
                "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validate_doctrine_marathon.py",
                "--mode",
                "final",
            ],
        }
    ]


def test_manifest_validates_against_public_schema() -> None:
    jsonschema.Draft202012Validator(
        load_schema(), format_checker=jsonschema.FormatChecker()
    ).validate(load_manifest())


def test_release_receipt_validates_against_versioned_embedded_schema() -> None:
    assert validator._check_receipt_schema(load_receipt(), load_schema()) == []


def test_release_receipt_schema_rejects_unknown_authority_claim() -> None:
    receipt = copy.deepcopy(load_receipt())
    receipt["publication_authorized"] = True

    findings = validator._check_receipt_schema(receipt, load_schema())

    assert len(findings) == 1
    assert findings[0].rule == "portfolio_receipt_schema"
    assert findings[0].path == validator.PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    assert "Additional properties are not allowed" in findings[0].detail


def test_interrogation_prompt_covers_the_full_governed_repo_route() -> None:
    prompt = (
        ROOT
        / "docs/portfolio/logos-trust-layer/AI-INTERROGATION-PROMPT.md"
    ).read_text(encoding="utf-8")
    prompt = " ".join(prompt.split())
    repository_ids = {
        row["repository_id"] for row in load_manifest()["repositories"]
    }

    assert (
        validator._missing_interrogation_route_requirements(
            prompt, repository_ids
        )
        == []
    )


@pytest.mark.parametrize(
    "removed",
    [
        "logos-governance-architecture",
        "logos-scripture-graph",
        "logos-boundary-literature",
        "logos-doctrine-genealogy",
        "governance/LOGOS_REPO_REGISTRY.yaml",
        "LOGOS_FAMILY_MAP.md",
        "logos-chunking-harness",
        "planned, not created",
        "noesis-atlas",
        "external advisory",
        "AI_FRONT_DOOR.md",
        "README.md",
        "snapshot_commit",
        "project-evidence.yaml",
    ],
)
def test_interrogation_prompt_rejects_missing_route_requirements(
    removed: str,
) -> None:
    prompt = (
        ROOT
        / "docs/portfolio/logos-trust-layer/AI-INTERROGATION-PROMPT.md"
    ).read_text(encoding="utf-8")
    prompt = " ".join(prompt.split())
    repository_ids = {
        row["repository_id"] for row in load_manifest()["repositories"]
    }

    missing = validator._missing_interrogation_route_requirements(
        prompt.replace(removed, ""),
        repository_ids,
    )

    assert removed in missing


@pytest.mark.parametrize(
    "field",
    [
        "runtime_activation_authorized",
        "source_ingestion_authorized",
        "substantive_doctrine_implementation_authorized",
        "completed_doctrine_corpus",
        "qualified_theological_authority",
    ],
)
def test_schema_rejects_promoted_doctrine_mesh_authority(field: str) -> None:
    candidate = copy.deepcopy(load_manifest())
    candidate["doctrine_mesh_specification"][field] = True

    errors = list(jsonschema.Draft202012Validator(load_schema()).iter_errors(candidate))

    assert len(errors) == 1
    assert list(errors[0].absolute_path) == ["doctrine_mesh_specification", field]
    assert errors[0].validator == "const"
    assert errors[0].validator_value is False


def test_public_text_scan_detects_private_path_without_echoing_payload() -> None:
    private_path = "".join(("C:", "\\", "Users", "\\", "example", "\\", "private.txt"))
    sensitive = "do-not-echo-this-value"

    findings = validator.scan_public_text("candidate.md", f"{sensitive} {private_path}")

    assert findings == [validator.Finding("windows_private_path", "candidate.md", "line 1")]
    assert sensitive not in findings[0].render()


def test_public_text_scan_detects_chat_local_locator_without_literal_fixture() -> None:
    locator = "".join(("turn", "17", "search", "4"))

    findings = validator.scan_public_text("candidate.md", locator)

    assert findings == [validator.Finding("chat_local_locator", "candidate.md", "line 1")]


def test_candidate_added_scan_suppresses_unchanged_base_finding() -> None:
    private_path = "".join(("C:", "\\", "wt", "\\", "historical"))

    assert validator.scan_candidate_added_text(
        "registry.yaml", private_path, private_path
    ) == []


def test_candidate_added_scan_rejects_new_sensitive_occurrence_without_echo() -> None:
    private_path = "".join(("C:", "\\", "wt", "\\", "new-private"))

    findings = validator.scan_candidate_added_text(
        "candidate.yaml", private_path, "clean baseline"
    )

    assert findings == [
        validator.Finding(
            "windows_private_path",
            "candidate.yaml",
            "1 candidate-added occurrence(s)",
        )
    ]
    assert private_path not in findings[0].render()


def test_release_snapshot_fails_closed_on_invalid_utf8_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        validator,
        "_git_object_bytes",
        lambda _root, _commit, _path: b"\xff",
    )

    findings, scanned, skipped = validator._scan_release_snapshot(
        ROOT,
        "base",
        "content",
        "receipt",
        ["candidate.md"],
    )

    assert findings == [
        validator.Finding(
            "release_scope_privacy_scan",
            "candidate.md",
            "text-suffixed release file is not valid UTF-8",
        )
    ]
    assert scanned == 0
    assert skipped == 1


def test_release_snapshot_fails_closed_on_invalid_utf8_baseline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        validator,
        "_git_object_bytes",
        lambda _root, _commit, _path: b"candidate text",
    )
    monkeypatch.setattr(
        validator,
        "_git_object_bytes_if_present",
        lambda _root, _commit, _path: b"\xff",
    )

    findings, scanned, skipped = validator._scan_release_snapshot(
        ROOT,
        "base",
        "content",
        "receipt",
        ["candidate.md"],
    )

    assert findings == [
        validator.Finding(
            "release_scope_privacy_baseline",
            "candidate.md",
            "baseline text is not valid UTF-8, so added-occurrence comparison is unavailable",
        )
    ]
    assert scanned == 0
    assert skipped == 1


def test_git_object_cache_uses_exact_immutable_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        if command[1:3] == ["cat-file", "-e"]:
            return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")
        commit, path = command[2].split(":", 1)
        calls.append((commit, path))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=f"{commit}:{path}".encode(),
            stderr=b"",
        )

    validator._git_commit_exists_record.cache_clear()
    validator._git_object_record.cache_clear()
    monkeypatch.setattr(validator.subprocess, "run", fake_run)
    try:
        first = validator._git_object_bytes(ROOT, "a" * 40, "one.md")
        repeated = validator._git_object_bytes(ROOT, "a" * 40, "one.md")
        changed_path = validator._git_object_bytes(ROOT, "a" * 40, "two.md")
        changed_commit = validator._git_object_bytes(ROOT, "b" * 40, "one.md")
    finally:
        validator._git_object_record.cache_clear()
        validator._git_commit_exists_record.cache_clear()

    assert first == repeated
    assert changed_path != first
    assert changed_commit != first
    assert calls == [
        ("a" * 40, "one.md"),
        ("a" * 40, "two.md"),
        ("b" * 40, "one.md"),
    ]


def test_git_object_cache_retains_exact_missing_base_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(command[1])
        if command[1:3] == ["cat-file", "-e"]:
            return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")
        if command[1] == "show":
            return subprocess.CompletedProcess(command, 128, stdout=b"", stderr=b"missing")
        return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")

    validator._git_commit_exists_record.cache_clear()
    validator._git_object_record.cache_clear()
    monkeypatch.setattr(validator.subprocess, "run", fake_run)
    try:
        first = validator._git_object_bytes_if_present(ROOT, "a" * 40, "missing.md")
        repeated = validator._git_object_bytes_if_present(ROOT, "a" * 40, "missing.md")
    finally:
        validator._git_object_record.cache_clear()
        validator._git_commit_exists_record.cache_clear()

    assert first is None
    assert repeated is None
    assert calls == ["cat-file", "show", "ls-tree"]


def test_git_object_lookup_does_not_conflate_read_error_with_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        if command[1:3] == ["cat-file", "-e"]:
            return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")
        return subprocess.CompletedProcess(command, 128, stdout=b"", stderr=b"denied")

    validator._git_commit_exists_record.cache_clear()
    validator._git_object_record.cache_clear()
    monkeypatch.setattr(validator.subprocess, "run", fake_run)
    try:
        with pytest.raises(validator.PortfolioValidationError):
            validator._git_object_bytes_if_present(ROOT, "a" * 40, "blocked.md")
    finally:
        validator._git_object_record.cache_clear()
        validator._git_commit_exists_record.cache_clear()


def test_nul_safe_git_delta_preserves_status_and_rejects_deletion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(validator, "_git_revision", lambda _root, revision: revision)

    def successful_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=b"M\0safe.md\0A\0new.json\0",
            stderr=b"",
        )

    monkeypatch.setattr(validator.subprocess, "run", successful_run)
    assert validator._git_delta_entries(ROOT, "a" * 40, "b" * 40) == [
        validator.GitDeltaEntry("A", "new.json"),
        validator.GitDeltaEntry("M", "safe.md"),
    ]

    def deletion_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            command, 0, stdout=b"D\0removed.md\0", stderr=b""
        )

    monkeypatch.setattr(validator.subprocess, "run", deletion_run)
    with pytest.raises(validator.PortfolioValidationError):
        validator._git_delta_entries(ROOT, "a" * 40, "b" * 40)


@pytest.mark.parametrize(
    "payload",
    [
        b"M\0duplicate.md\0A\0duplicate.md\0",
        b"M\0unterminated.md",
        b"M\0unsafe\\path.md\0",
        b"M\0bad-utf8-\xff.md\0",
    ],
)
def test_nul_safe_git_delta_rejects_ambiguous_paths(
    monkeypatch: pytest.MonkeyPatch, payload: bytes
) -> None:
    monkeypatch.setattr(validator, "_git_revision", lambda _root, revision: revision)
    monkeypatch.setattr(
        validator.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(
            command, 0, stdout=payload, stderr=b""
        ),
    )

    with pytest.raises(validator.PortfolioValidationError):
        validator._git_delta_entries(ROOT, "a" * 40, "b" * 40)


@pytest.mark.parametrize(
    "value",
    [
        "/absolute",
        "../escape",
        "safe/../escape",
        "C:/private",
        "safe\\windows",
        "safe//child",
        "safe/./child",
        "safe/child/",
        "safe/control\nchild",
        "safe/CON",
        "safe/name:stream",
    ],
)
def test_nonportable_evidence_paths_fail_closed(value: str) -> None:
    with pytest.raises(validator.PortfolioValidationError):
        validator._safe_repo_path(value)


def test_repository_count_totals_are_reproducible_from_rows() -> None:
    manifest = load_manifest()
    fields = (
        "tracked_files",
        "json_paths",
        "yaml_paths",
        "schema_like_paths",
        "validator_like_paths",
        "test_like_paths",
    )

    for field in fields:
        assert manifest["snapshot"]["totals"][field] == sum(
            repository["counts"][field] for repository in manifest["repositories"]
        )


def test_chained_incremental_release_scope_is_replayable_and_fails_on_count_drift() -> None:
    manifest = load_manifest()
    receipt = load_receipt()
    findings, metrics = validator._check_release_scope(manifest, receipt, ROOT)

    assert findings == []
    assert metrics["release_unique_paths"] == 142
    assert metrics["release_fingerprinted_paths"] == 141
    assert metrics["release_text_files_scanned"] > 0
    assert metrics["release_text_files_skipped"] == 0

    drifted = copy.deepcopy(manifest)
    drifted["release_scope"]["total_unique_path_count"] = 141
    findings, _ = validator._check_release_scope(drifted, receipt, ROOT)
    assert any(finding.rule == "release_scope_path_count" for finding in findings)


def test_release_scope_rejects_a_stale_content_head() -> None:
    manifest = load_manifest()
    receipt = copy.deepcopy(load_receipt())
    current_content_head = receipt["release_chain"]["active_increment"][
        "content_head_commit"
    ]
    receipt["release_chain"]["active_increment"]["content_head_commit"] = (
        validator._git_parents(ROOT, current_content_head)[0]
    )

    findings, _ = validator._check_release_scope(manifest, receipt, ROOT)

    assert any(finding.rule == "release_scope_finalization" for finding in findings)


def test_release_scope_rejects_a_mismatched_prior_release_snapshot() -> None:
    manifest = load_manifest()
    receipt = copy.deepcopy(load_receipt())
    receipt["release_chain"]["prior_release"]["total_release_path_count"] -= 1

    findings, _ = validator._check_release_scope(manifest, receipt, ROOT)

    assert any(finding.rule == "release_scope_receipt" for finding in findings)


def test_release_scope_rejects_prior_receipt_digest_drift() -> None:
    manifest = load_manifest()
    receipt = copy.deepcopy(load_receipt())
    receipt["release_chain"]["prior_release"]["receipt_digest"] = (
        "sha256:" + "0" * 64
    )

    findings, _ = validator._check_release_scope(manifest, receipt, ROOT)

    assert any(finding.rule == "release_scope_receipt" for finding in findings)


def test_release_scope_rejects_a_changed_chain_anchor() -> None:
    manifest = copy.deepcopy(load_manifest())
    receipt = load_receipt()
    manifest["release_scope"]["prior_release"]["merge_commit"] = manifest[
        "release_scope"
    ]["prior_release"]["receipt_commit"]

    findings, _ = validator._check_release_scope(manifest, receipt, ROOT)

    assert any(finding.rule == "release_scope_prior_receipt" for finding in findings)


def test_release_scope_requires_the_chained_incremental_mode() -> None:
    manifest = load_manifest()
    receipt = copy.deepcopy(load_receipt())
    receipt["release_chain"]["mode"] = "unbounded_cumulative"

    findings, _ = validator._check_release_scope(manifest, receipt, ROOT)

    assert any(finding.rule == "release_scope_receipt" for finding in findings)


def test_historical_v1_digest_is_reproduced_without_promoting_its_convention() -> None:
    historical = load_manifest()["release_scope"]["historical_v1"]
    paths = validator._git_changed_paths(
        ROOT,
        historical["staged_candidate_parent"],
        historical["artifact_commit"],
    )
    fingerprinted = [
        path for path in paths if path not in historical["portable_replay_excluded_paths"]
    ]

    digest = validator._historical_windows_index_digest(
        ROOT,
        historical["artifact_commit"],
        fingerprinted,
        "docs/roadmap/logos-stewardship-architecture-buildout",
    )

    assert historical["historical_receipt_replay_status"] == "historical_evidence_only"
    assert digest == historical["historical_non_receipt_digest"]


def test_composed_snapshot_drift_detects_merge_tree_change(monkeypatch: pytest.MonkeyPatch) -> None:
    receipt_path = validator.PORTFOLIO_RECEIPT_RELATIVE.as_posix()
    objects = {
        ("content", "PORTFOLIO.md"): b"reviewed portfolio",
        ("receipt", receipt_path): b"reviewed receipt",
        ("merge", "PORTFOLIO.md"): b"changed during merge",
        ("merge", receipt_path): b"reviewed receipt",
    }

    monkeypatch.setattr(
        validator,
        "_git_object_bytes",
        lambda _root, commit, path: objects[(commit, path)],
    )

    assert validator._composed_snapshot_drift(
        ROOT,
        "merge",
        "content",
        "receipt",
        [receipt_path, "PORTFOLIO.md"],
    ) == ["PORTFOLIO.md"]


def test_durable_public_path_protects_root_navigation_but_not_shared_registry() -> None:
    doctrine_prefix = (
        "docs/roadmap/logos-stewardship-architecture-buildout/"
        "revisions/doctrine-mesh-v2/"
    )

    assert validator._is_durable_public_path("AI_FRONT_DOOR.md", doctrine_prefix)
    assert validator._is_durable_public_path("README.md", doctrine_prefix)
    assert validator._is_durable_public_path("scripts/validation_contracts.py", doctrine_prefix)
    assert validator._is_durable_public_path(
        f"{doctrine_prefix}README.md", doctrine_prefix
    )
    assert not validator._is_durable_public_path(
        "governance/registry/FAMILY_WORK_REGISTRY.yaml", doctrine_prefix
    )


@pytest.mark.parametrize(
    "field",
    [
        "runtime_activation_authorized",
        "source_ingestion_authorized",
        "substantive_doctrine_implementation_authorized",
        "completed_doctrine_corpus",
        "qualified_theological_authority_granted",
    ],
)
def test_portfolio_receipt_rejects_authority_elevation(field: str) -> None:
    receipt = copy.deepcopy(load_receipt())
    receipt[field] = True
    receipt["receipt_digest"] = validator._canonical_digest(
        receipt, ("receipt_digest",)
    )

    findings = validator._check_receipt_payload(receipt)

    assert findings == [
        validator.Finding(
            "portfolio_receipt_authority",
            validator.PORTFOLIO_RECEIPT_RELATIVE.as_posix(),
            {
                "runtime_activation_authorized": "runtime activation",
                "source_ingestion_authorized": "source ingestion",
                "substantive_doctrine_implementation_authorized": (
                    "substantive doctrine implementation"
                ),
                "completed_doctrine_corpus": "completed doctrine corpus",
                "qualified_theological_authority_granted": (
                    "qualified theological authority"
                ),
            }[field]
            + " must remain false",
        )
    ]


def test_release_mesh_keeps_one_writer_and_distinct_checker() -> None:
    mesh = json.loads(
        (
            ROOT
            / "docs/portfolio/logos-trust-layer/agent-mesh-manifest.json"
        ).read_text(encoding="utf-8")
    )

    assert mesh["writer_role_id"] != mesh["checker_role_id"]
    assert mesh["max_delegation_depth"] == 1
    assert mesh["authority"]["execution_authority"] is False
    assert mesh["manifest_digest"] == validator._canonical_digest(
        mesh, ("manifest_digest",)
    )


def test_doctrine_mesh_freeze_retains_specification_only_flags() -> None:
    doctrine = load_manifest()["doctrine_mesh_specification"]

    assert doctrine["maturity"] == "validated_specification_only"
    assert doctrine["release_file_count"] == 90
    assert doctrine["payload_file_count"] == 85
    assert doctrine["cross_provider_verified"] is False
    assert doctrine["runtime_activation_authorized"] is False
    assert doctrine["source_ingestion_authorized"] is False
    assert doctrine["substantive_doctrine_implementation_authorized"] is False
    assert doctrine["completed_doctrine_corpus"] is False
    assert doctrine["qualified_theological_authority"] is False


def test_doctrine_marathon_v3_is_directly_routed_and_non_authorizing() -> None:
    marathon = load_manifest()["doctrine_marathon_specification"]

    assert marathon["maturity"] == "blocked_specification_only"
    assert marathon["declared_final_blocker"] == validator.DECLARED_V3_FINAL_BLOCKER
    assert (
        marathon["final_replay_status"]
        == "blocked_by_declared_aggregate_exact_oracle_gate"
    )
    assert marathon["release_file_count"] == 83
    assert marathon["payload_file_count"] == 78
    assert marathon["administrative_file_count"] == 5
    assert marathon["role_count"] == 18
    assert marathon["trigger_count"] == 19
    assert marathon["assignment_fixture_count"] == 3
    assert marathon["runtime_assignment_count"] == 0
    assert marathon["expert_pack_count"] == 0
    assert marathon["qualification_receipt_count"] == 0
    assert marathon["correlation_acceptance_count"] == 0
    assert marathon["event_count"] == 0
    assert marathon["evidence_record_count"] == 0
    assert marathon["mistake_receipt_count"] == 1
    assert marathon["corrective_action_count"] == 6
    assert marathon["preventive_action_count"] == 5
    assert marathon["repair_ledger_entry_count"] == 40
    assert marathon["legacy_component_case_count"] == 164
    assert marathon["strict_isolated_component_case_count"] == 33
    assert marathon["component_only_executable_case_count"] == 197
    assert marathon["aggregate_sentinel_subset_case_count"] == 4
    assert marathon["negative_case_catalog_count"] == 164
    assert marathon["isolated_regression_case_count"] == 33
    assert marathon["negative_case_count"] == 197
    assert marathon["open_expert_review_debt"] == 2
    assert marathon["independent_review_status"] == "pass_blocked_specification_only"
    assert (
        marathon["independence_status"]
        == "non_author_read_only_cross_provider_unverified"
    )
    assert marathon["cross_provider_verified"] is False
    assert marathon["runtime_activation_authorized"] is False
    assert marathon["research_execution_authorized"] is False
    assert marathon["source_ingestion_authorized"] is False
    assert marathon["substantive_doctrine_implementation_authorized"] is False
    assert marathon["completed_doctrine_corpus"] is False
    assert marathon["qualified_theological_authority"] is False

    for relative in DOCTRINE_MARATHON_PUBLIC_ROUTE:
        assert (ROOT / relative).is_file()

    evidence_targets = tuple(
        row["target"]
        for row in marathon["evidence"]
        if row["target"]
        in {path.as_posix() for path in DOCTRINE_MARATHON_HARNESS_PUBLIC_EVIDENCE}
    )
    assert evidence_targets == tuple(
        path.as_posix() for path in DOCTRINE_MARATHON_HARNESS_PUBLIC_EVIDENCE
    )
    audit_route = next(
        row
        for row in load_manifest()["evidence_routes"]
        if row["route_id"] == "doctrine-marathon-v3-audit"
    )
    route_harness_targets = tuple(
        path
        for path in audit_route["then_read"]
        if path
        in {item.as_posix() for item in DOCTRINE_MARATHON_HARNESS_PUBLIC_EVIDENCE}
    )
    assert route_harness_targets == tuple(
        path.as_posix() for path in DOCTRINE_MARATHON_HARNESS_PUBLIC_EVIDENCE
    )
    assert (
        "python -B -m pytest -q --assert=plain -p no:cacheprovider "
        "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
        "doctrine-marathon-v3/checks/test_run_adversarial_harness.py"
        in load_manifest()["verification"]["commands"]
    )
    commands = load_manifest()["verification"]["commands"]
    assert all(command.startswith("python -B ") for command in commands)
    assert all(
        "-p no:cacheprovider" in command
        for command in commands
        if "-m pytest" in command
    )
    assert load_manifest()["verification"]["oracle_controls"] == {
        "input_snapshot_bound": True,
        "duplicate_structured_keys_rejected": True,
        "ordered_duplicate_findings_preserved": True,
        "alternate_root_isolated": True,
        "single_receipt_read": True,
        "sentinel_count": 5,
        "sentinel_ids": [row[0] for row in PORTFOLIO_ORACLE_SENTINELS],
    }

    front_door = (ROOT / "AI_FRONT_DOOR.md").read_text(encoding="utf-8")
    for relative in DOCTRINE_MARATHON_FRONT_DOOR_ROUTE:
        assert f"({relative.as_posix()})" in front_door

    for entry_point in (
        "PORTFOLIO.md",
        "AI_FRONT_DOOR.md",
        "AI_TABLE_OF_CONTENTS.md",
        "AI_WORK_START_HERE.md",
        "docs/portfolio/logos-trust-layer/README.md",
        "docs/portfolio/logos-trust-layer/AI-INTERROGATION-PROMPT.md",
    ):
        text = (ROOT / entry_point).read_text(encoding="utf-8")
        assert "doctrine-marathon-v3" in text
        for immutable in (
            "revision-manifest.yaml",
            "FINAL-SAVED-VERSION.yaml",
            "checks/validation-receipt.json",
            "checks/independent-review.json",
            "checks/public-release-authorization.json",
            "checks/fixtures/negative-cases.json",
        ):
            assert immutable in text


def test_doctrine_marathon_v3_meta_audit_graph_and_terminal_contracts() -> None:
    mesh = json.loads(
        (ROOT / DOCTRINE_MARATHON_ROOT / "mesh/agent-mesh.v3.json").read_text(
            encoding="utf-8"
        )
    )
    role_ids = {role["role_id"] for role in mesh["roles"]}
    assert "role-qualification-and-independence-auditor" in role_ids
    assert "doctrine-mesh-completeness-auditor" in role_ids
    assert "frontier-compounded-error-sentinel" in role_ids

    assignments = json.loads(
        (
            ROOT
            / DOCTRINE_MARATHON_ROOT
            / "mesh/examples/design-time-independence-fixture.json"
        ).read_text(encoding="utf-8")
    )["assignments"]
    by_role = {row["role_id"]: row for row in assignments}
    assert list(by_role).count("role-qualification-and-independence-auditor") == 1
    assert list(by_role).count("independent-whole-work-checker") == 1
    factory_id = by_role["task-local-role-factory"]["assignment_id"]
    meta = by_role["role-qualification-and-independence-auditor"]
    whole = by_role["independent-whole-work-checker"]
    assert set(meta["checks_assignment_ids"]) == {
        factory_id,
        whole["assignment_id"],
    }
    assert set(whole["checks_assignment_ids"]) == {
        factory_id,
        meta["assignment_id"],
    }

    action_requirements = yaml.safe_load(
        (
            ROOT
            / DOCTRINE_MARATHON_ROOT
            / "firewall/action-checker-requirements.yaml"
        ).read_text(encoding="utf-8")
    )
    assert action_requirements["unknown_action_policy"] == "block"
    assert all(row["required_roles"] for row in action_requirements["requirements"])
    assert all(
        row["required_capabilities"] for row in action_requirements["requirements"]
    )

    evidence_review_schema = json.loads(
        (
            ROOT
            / DOCTRINE_MARATHON_ROOT
            / "evidence/evidence-review-receipt.schema.json"
        ).read_text(encoding="utf-8")
    )
    assert {
        "producer_assignment_ref",
        "producer_assignment_digest",
    }.issubset(evidence_review_schema["required"])

    event_schema = json.loads(
        (
            ROOT / DOCTRINE_MARATHON_ROOT / "events/marathon-event.schema.json"
        ).read_text(encoding="utf-8")
    )
    action_result = event_schema["properties"]["details"]["properties"][
        "action_results"
    ]["items"]
    assert {
        "evidence_bindings",
        "checker_assignment_ref",
        "checker_assignment_digest",
    }.issubset(action_result["required"])

    prompt_contract = yaml.safe_load(
        (
            ROOT
            / DOCTRINE_MARATHON_ROOT
            / "firewall/prompt-neutrality-contract.yaml"
        ).read_text(encoding="utf-8")
    )
    assert prompt_contract["deterministic_lexical_screen_is_only_a_floor"] is True
    assert prompt_contract["independent_semantic_alignment_review_required"] is True
    assert "No lexical rule proves a prompt neutral" in prompt_contract["semantic_nonclaim"]

    weekly = json.loads(
        (
            ROOT
            / DOCTRINE_MARATHON_ROOT
            / "state/examples/initial-weekly-fresh-context-gate.json"
        ).read_text(encoding="utf-8")
    )
    assert weekly["verification"] is None
    assert weekly["continuation_authorized"] is False
    assert weekly["result"] == "fresh_context_required"

    identity_root = yaml.safe_load(
        (
            ROOT
            / DOCTRINE_MARATHON_ROOT
            / "graph/human-identity-authority-root.yaml"
        ).read_text(encoding="utf-8")
    )
    authority_registry = yaml.safe_load(
        (
            ROOT / DOCTRINE_MARATHON_ROOT / "graph/authority-registry.yaml"
        ).read_text(encoding="utf-8")
    )
    assert identity_root["active"] is False
    assert identity_root["recorded_by_human"] is False
    assert authority_registry["qualified_approvers"] == []
    assert authority_registry["normative_frames"] == []
    assert authority_registry["normative_authority_active"] is False

    graph = json.loads(
        (ROOT / DOCTRINE_MARATHON_ROOT / "graph/example-graph.json").read_text(
            encoding="utf-8"
        )
    )
    assert graph["canonical_edge_direction"] == "consumer_to_prerequisite"
    assert graph["reverse_index_generated"] is True

    goal = yaml.safe_load(
        (ROOT / DOCTRINE_MARATHON_ROOT / "state/goal.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert goal["terminal_contract"]["allowed_statuses"] == [
        "CONTINUE",
        "BLOCKED",
        "CAMPAIGN_COMPLETE",
    ]
    assert goal["authority_ceiling"]["runtime_activation_authorized"] is False
