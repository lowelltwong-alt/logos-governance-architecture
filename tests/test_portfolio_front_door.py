from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from scripts import validate_portfolio_front_door as validator
from scripts.validation_contracts import default_validation_commands


ROOT = Path(__file__).resolve().parents[1]


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


def test_public_portfolio_candidate_passes() -> None:
    result = validator.validate_repository(ROOT)

    assert result.findings == ()
    assert result.metrics["doctrine_managed_files"] == 90
    assert result.metrics["doctrine_static_failures"] == 0
    assert result.metrics["mermaid_diagrams"] >= 5
    assert result.metrics["diagram_prose_readings"] == result.metrics["mermaid_diagrams"]


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


def test_manifest_validates_against_public_schema() -> None:
    jsonschema.Draft202012Validator(
        load_schema(), format_checker=jsonschema.FormatChecker()
    ).validate(load_manifest())


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

    assert errors


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


@pytest.mark.parametrize(
    "value",
    ["/absolute", "../escape", "safe/../escape", "C:/private", "safe\\windows"],
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
