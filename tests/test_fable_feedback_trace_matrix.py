from __future__ import annotations

from copy import deepcopy

from scripts import validate_fable_feedback_trace_matrix as validator


def base_matrix() -> dict:
    return {
        "object_type": "fable_feedback_trace_matrix",
        "trust_zone": "canonical",
        "lifecycle_status": "active",
        "provenance_note": "test",
        "reason_for_inclusion": "test",
        "schema_version": "fable_feedback_trace_matrix.v1",
        "matrix_id": "test",
        "owner": "Lowell Wong",
        "source_repo": "logos-governance-architecture",
        "scope_note": "test",
        "matrix_authority": {
            "records_feedback_disposition": True,
            "authorizes_scripture_output_change": False,
            "authorizes_chunk_output_change": False,
            "authorizes_doctrine_data_records": False,
            "authorizes_source_import": False,
            "authorizes_reviewed_lineage_promotion": False,
            "authorizes_graph_retrieval_vector_truth": False,
            "authorizes_theology_authority": False,
        },
        "allowed_dispositions": sorted(validator.EXPECTED_DISPOSITIONS),
        "allowed_risk_categories": ["auditability"],
        "source_documents": [
            {
                "source_id": "source",
                "title": "Source",
                "repo_path": "docs/roadmap/fable-kernels/README.md",
            }
        ],
        "coverage_groups": [
            {
                "group_id": "group",
                "source_id": "source",
                "source_section": "section",
                "coverage_entry_ids": ["ENTRY-001"],
            }
        ],
        "entries": [
            {
                "id": "ENTRY-001",
                "source_group": "group",
                "source_item_ref": "item",
                "feedback_summary": "summary",
                "risk_category": "auditability",
                "affected_repos": ["logos-governance-architecture"],
                "disposition": "implemented",
                "disposition_reason": "Implemented by test fixture.",
                "evidence_refs": ["docs/roadmap/fable-kernels/README.md"],
                "next_action": "Keep current.",
                "owner_decision_status": "not_required",
                "target_queue": "none",
                "blocks_work": False,
                "non_authorizations": ["theology_authority"],
            }
        ],
    }


def test_current_trace_matrix_validates() -> None:
    matrix = validator.load_yaml(validator.MATRIX)
    assert validator.validate_matrix(matrix) == []


def test_missing_coverage_entry_fails() -> None:
    matrix = base_matrix()
    matrix["coverage_groups"][0]["coverage_entry_ids"] = ["ENTRY-001", "ENTRY-002"]

    failures = validator.validate_matrix(matrix)

    assert any("coverage groups reference missing entries ENTRY-002" in failure for failure in failures)


def test_uncovered_entry_fails() -> None:
    matrix = base_matrix()
    extra = deepcopy(matrix["entries"][0])
    extra["id"] = "ENTRY-002"
    matrix["entries"].append(extra)

    failures = validator.validate_matrix(matrix)

    assert any("entries are not referenced by coverage groups ENTRY-002" in failure for failure in failures)


def test_planned_entry_requires_target_queue() -> None:
    matrix = base_matrix()
    entry = matrix["entries"][0]
    entry["disposition"] = "planned"
    entry["target_queue"] = "none"

    failures = validator.validate_matrix(matrix)

    assert any("planned entries must name a target_queue" in failure for failure in failures)


def test_authority_flags_must_remain_false() -> None:
    matrix = base_matrix()
    matrix["matrix_authority"]["authorizes_theology_authority"] = True

    failures = validator.validate_matrix(matrix)

    assert any("matrix_authority.authorizes_theology_authority must be false" in failure for failure in failures)
