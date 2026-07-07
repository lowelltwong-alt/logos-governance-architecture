from __future__ import annotations

from pathlib import Path

from scripts import validate_cross_repo_reference_manifest as validator


def base_standard() -> dict:
    return {
        "object_type": "mirror_freshness_standard",
        "trust_zone": "canonical",
        "lifecycle_status": "active",
        "provenance_note": "test",
        "reason_for_inclusion": "test",
        "schema_version": "mirror_freshness_standard.v1",
        "standard_id": "test",
        "owner": "Lowell Wong",
        "source_repo": "logos-governance-architecture",
        "authority": {
            "defines_mirror_freshness_fields": True,
            "authorizes_scripture_output_change": False,
            "authorizes_chunk_output_change": False,
            "authorizes_source_import": False,
            "authorizes_doctrine_data_records": False,
            "authorizes_theology_authority": False,
        },
        "default_freshness_policy": {
            "missing_referenced_path_blocks_when_source_repo_available": True,
        },
        "required_mirror_fields": ["mirror_id"],
        "required_reference_fields": ["reference_id"],
        "allowed_authority_postures": ["reference_only_not_authority"],
        "allowed_failure_policies": ["fail_closed_when_local_repo_available"],
        "non_authorizations": [
            "scripture_output_change",
            "chunk_output_change",
            "source_import",
            "doctrine_data_records",
            "theology_authority",
        ],
    }


def base_manifest(tmp_path: Path, target_path: str = ".ai/control/policy.yaml") -> dict:
    return {
        "object_type": "cross_repo_reference_manifest",
        "trust_zone": "canonical",
        "lifecycle_status": "active",
        "provenance_note": "test",
        "reason_for_inclusion": "test",
        "schema_version": "cross_repo_reference_manifest.v1",
        "manifest_id": "test",
        "owner": "Lowell Wong",
        "source_repo": "logos-governance-architecture",
        "authority": {
            "records_cross_repo_path_references": True,
            "authorizes_scripture_output_change": False,
            "authorizes_chunk_output_change": False,
            "authorizes_source_import": False,
            "authorizes_doctrine_data_records": False,
            "authorizes_theology_authority": False,
        },
        "local_repo_roots": {
            "logos-scripture-graph": [str(tmp_path / "logos-scripture-graph")],
        },
        "references": [
            {
                "reference_id": "ref-test",
                "source_path": "schemas/doctrine_genealogy/gate_trigger_registry.v1.yaml",
                "source_field": "scripture_repo_refs.test",
                "target_repo": "logos-scripture-graph",
                "target_path": target_path,
                "authority_posture": "reference_only_not_authority",
                "failure_policy": "fail_closed_when_local_repo_available",
            }
        ],
        "non_authorizations": [
            "scripture_output_change",
            "chunk_output_change",
            "source_import",
            "doctrine_data_records",
            "theology_authority",
        ],
    }


def test_manifest_validates_current_gate_registry_refs() -> None:
    standard = validator.load_yaml(validator.STANDARD)
    manifest = validator.load_yaml(validator.MANIFEST)
    gate_registry = validator.load_yaml(validator.GATE_TRIGGER_REGISTRY)
    dependency_map = validator.load_yaml(validator.DEPENDENCY_MAP)

    failures = validator.validate_manifest(
        manifest,
        standard=standard,
        gate_registry=gate_registry,
        dependency_map=dependency_map,
    )

    assert failures == []


def test_manifest_fails_when_local_target_is_missing(tmp_path: Path) -> None:
    repo = tmp_path / "logos-scripture-graph"
    repo.mkdir()
    manifest = base_manifest(tmp_path)

    failures = validator.validate_manifest(
        manifest,
        standard=base_standard(),
        root=tmp_path,
    )

    assert any("missing target path logos-scripture-graph:.ai/control/policy.yaml" in failure for failure in failures)


def test_manifest_allows_unavailable_local_repo_unless_required(tmp_path: Path) -> None:
    manifest = base_manifest(tmp_path)

    optional_failures = validator.validate_manifest(
        manifest,
        standard=base_standard(),
        root=tmp_path,
    )
    required_failures = validator.validate_manifest(
        manifest,
        standard=base_standard(),
        root=tmp_path,
        require_local_repos=True,
    )

    assert optional_failures == []
    assert any("no local repo root found" in failure for failure in required_failures)


def test_manifest_rejects_path_escape(tmp_path: Path) -> None:
    repo = tmp_path / "logos-scripture-graph"
    repo.mkdir()
    manifest = base_manifest(tmp_path, target_path="../outside.yaml")

    failures = validator.validate_manifest(
        manifest,
        standard=base_standard(),
        root=tmp_path,
    )

    assert any("target_path escapes repo root" in failure for failure in failures)


def test_gate_trigger_refs_must_be_manifested(tmp_path: Path) -> None:
    manifest = base_manifest(tmp_path)
    gate_registry = {
        "scripture_repo_refs": {
            "missing": "logos-scripture-graph:.ai/control/missing.yaml",
        }
    }

    failures = validator.validate_manifest(
        manifest,
        standard=base_standard(),
        gate_registry=gate_registry,
        root=tmp_path,
    )

    assert any("gate trigger registry reference missing from manifest" in failure for failure in failures)


def test_upward_child_repo_dependency_is_rejected() -> None:
    dependency_map = {
        "artifacts": [
            {
                "artifact_id": "GD-X",
                "repo": "logos-governance-architecture",
                "depends_on": ["logos-scripture-graph/.ai/control/policy.yaml"],
            }
        ]
    }

    failures = validator.validate_no_upward_child_dependencies(dependency_map)

    assert any("may not point upward to child repo path" in failure for failure in failures)
