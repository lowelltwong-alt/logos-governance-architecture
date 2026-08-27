from __future__ import annotations

import copy
import json
import subprocess
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


def load_receipt() -> dict:
    return json.loads(
        (
            ROOT
            / "docs/portfolio/logos-trust-layer/validation-receipt.json"
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


def test_git_object_cache_uses_exact_immutable_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        commit, path = command[2].split(":", 1)
        calls.append((commit, path))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=f"{commit}:{path}".encode(),
            stderr=b"",
        )

    validator._git_object_record.cache_clear()
    monkeypatch.setattr(validator.subprocess, "run", fake_run)
    try:
        first = validator._git_object_bytes(ROOT, "a" * 40, "one.md")
        repeated = validator._git_object_bytes(ROOT, "a" * 40, "one.md")
        changed_path = validator._git_object_bytes(ROOT, "a" * 40, "two.md")
        changed_commit = validator._git_object_bytes(ROOT, "b" * 40, "one.md")
    finally:
        validator._git_object_record.cache_clear()

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
    calls = 0

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(command, 128, stdout=b"", stderr=b"missing")

    validator._git_object_record.cache_clear()
    monkeypatch.setattr(validator.subprocess, "run", fake_run)
    try:
        first = validator._git_object_bytes_if_present(ROOT, "a" * 40, "missing.md")
        repeated = validator._git_object_bytes_if_present(ROOT, "a" * 40, "missing.md")
    finally:
        validator._git_object_record.cache_clear()

    assert first is None
    assert repeated is None
    assert calls == 1


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


def test_full_pr_release_scope_is_replayable_and_fails_on_count_drift() -> None:
    manifest = load_manifest()
    receipt = load_receipt()
    findings, metrics = validator._check_release_scope(manifest, receipt, ROOT)

    assert findings == []
    assert metrics["release_unique_paths"] == 207
    assert metrics["release_fingerprinted_paths"] == 206
    assert metrics["release_text_files_scanned"] > 0
    assert metrics["release_text_files_skipped"] == 0

    drifted = copy.deepcopy(manifest)
    drifted["release_scope"]["total_unique_path_count"] = 111
    findings, _ = validator._check_release_scope(drifted, receipt, ROOT)
    assert any(finding.rule == "release_scope_arithmetic" for finding in findings)


def test_release_scope_rejects_a_stale_content_head() -> None:
    manifest = load_manifest()
    receipt = copy.deepcopy(load_receipt())
    receipt["full_pr_composite_scope"]["content_head_commit"] = manifest[
        "release_scope"
    ]["v1_checkpoint_commit"]

    findings, _ = validator._check_release_scope(manifest, receipt, ROOT)

    assert any(finding.rule == "release_scope_finalization" for finding in findings)


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

    assert any(finding.rule == "portfolio_receipt_authority" for finding in findings)


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
