from __future__ import annotations

from scripts import doctrine_genealogy_validation as v


def base_provenance(**overrides):
    record = {
        "source_basis": [
            {
                "ref": "instrument/chalcedonian-definition-451",
                "ladder_rung": "S1",
                "citation_locator": "definition",
                "citation_mode": "summary",
            }
        ],
        "claim_role": "historical_description",
        "authority_zone": "S1",
        "tradition_scope": None,
        "orthodoxy_status": "unclassified_candidate",
        "orthodoxy_basis_refs": [],
        "asserted_or_inferred": "inferred",
        "method": "ai_staged",
        "lifecycle_status": "draft",
        "review_status": "unreviewed",
        "reviewer_or_owner_decision_ref": None,
        "upstream_deps": [],
        "known_counterclaims": [],
        "contested_status": "contested",
        "original_language_review": "not_required",
        "original_language_review_ref": None,
        "textual_critical_review": "not_required",
        "textual_critical_review_ref": None,
        "downstream_risk_note": "",
        "provenance_note": "test fixture",
    }
    record.update(overrides)
    return record


def test_kernel_e_schema_defaults_are_floor_only() -> None:
    failures = []
    for path in sorted(v.SCHEMA_DIR.glob("*.json")):
        failures.extend(v.schema_text_has_only_floor_defaults(path))
    assert failures == []


def test_pr5_example_metadata_is_allowed_by_node_edge_and_packet_schemas() -> None:
    node_schema = v.load_json(v.SCHEMA_DIR / "doctrine_node.v1.schema.json")
    edge_schema = v.load_json(v.SCHEMA_DIR / "genealogy_edge.v1.schema.json")
    packet_schema = v.load_json(v.SCHEMA_DIR / "evidence_packet.v1.schema.json")

    for object_type in [
        "doctrine_topic",
        "doctrine_view",
        "formulation",
        "agent",
        "instrument",
        "claim",
        "assessment",
        "controversy",
    ]:
        object_schema = node_schema["$defs"][object_type]
        for field in ["trust_zone", "lifecycle_status", "review_status"]:
            assert field in object_schema["required"], object_type
            assert field in object_schema["properties"], object_type

    for field in ["trust_zone", "lifecycle_status", "review_status"]:
        if field == "review_status":
            assert field in edge_schema["required"]
            assert field in edge_schema["properties"]
        else:
            assert field in edge_schema["required"]
            assert field in edge_schema["properties"]
        assert field in packet_schema["required"]
        assert field in packet_schema["properties"]

    assert "proposed" in node_schema["$defs"]["trust_zone"]["enum"]
    assert "draft" in node_schema["$defs"]["lifecycle_status"]["enum"]
    assert "unreviewed" in node_schema["$defs"]["review_status"]["enum"]


def test_codex_tripwire_requires_decision_basis_for_non_floor_classification() -> None:
    record = {
        "orthodoxy_status": "orthodox_core",
    }

    failures = v.validate_codex_theology_tripwire_record(record, label="fixture")

    assert any("requires decision_basis under V-CODEX-1" in failure for failure in failures)


def test_codex_tripwire_accepts_non_floor_classification_with_decision_basis() -> None:
    record = {
        "decision_basis": ["FABLE-D1-D10-2026-07-06:D1"],
        "orthodoxy_status": "orthodox_core",
        "tradition_scope": "reformed",
    }

    failures = v.validate_codex_theology_tripwire_record(record, label="fixture")

    assert failures == []


def test_orthodox_core_requires_s1_basis() -> None:
    provenance = base_provenance(
        source_basis=[
            {
                "ref": "work/example",
                "ladder_rung": "S4",
                "citation_locator": "1",
                "citation_mode": "summary",
            }
        ],
        authority_zone="S4",
        orthodoxy_status="orthodox_core",
        orthodoxy_basis_refs=["instrument/chalcedonian-definition-451"],
    )

    failures = v.validate_provenance_block(provenance)

    assert any("orthodox_core requires a cited S1" in failure for failure in failures)
    assert any("S3 or below cannot be sole basis" in failure for failure in failures)


def test_s6_cannot_ground_normative_position() -> None:
    provenance = base_provenance(
        source_basis=[
            {
                "ref": "work/modern-analysis",
                "ladder_rung": "S6",
                "citation_locator": "p. 1",
                "citation_mode": "summary",
            }
        ],
        authority_zone="S6",
        claim_role="normative_position",
        orthodoxy_status="orthodox_permitted_diversity",
        tradition_scope="reformed",
    )

    failures = v.validate_provenance_block(provenance)

    assert any("S6 scholarly_analysis cannot ground a normative_position" in failure for failure in failures)
    assert any("S6 scholarly_analysis cannot ground orthodoxy_status" in failure for failure in failures)


def test_asserted_relationship_cannot_have_pending_gate() -> None:
    provenance = base_provenance(
        method="human_authored",
        review_status="reviewed",
        reviewer_or_owner_decision_ref="owner:test",
        original_language_review="required_pending",
    )

    failures = v.validate_provenance_block(
        provenance,
        relationship_status="asserted_relationship",
    )

    assert any("pending original-language gate" in failure for failure in failures)


def test_evidence_packet_cannot_be_source_basis() -> None:
    provenance = base_provenance(
        source_basis=[
            {
                "ref": "evidence_packet/trinity-development",
                "ladder_rung": "S6",
                "citation_locator": "generated",
                "citation_mode": "summary",
            }
        ],
        authority_zone="S6",
    )

    failures = v.validate_provenance_block(provenance)

    assert any("V-PKT-3" in failure for failure in failures)


def test_forbidden_condemnation_edge_is_rejected() -> None:
    edge = {
        "verb": "condemns",
        "edge_status": "retrieval_candidate",
    }

    failures = v.validate_genealogy_edge_record(edge)

    assert any("forbidden doctrine-genealogy verb condemns" in failure for failure in failures)
    assert any("not in the approved Kernel A3" in failure for failure in failures)


def test_v_time_rejects_later_to_earlier_derivation_without_later_act_verb() -> None:
    edge = {
        "subject_ref": "formulation/later",
        "verb": "derives_from",
        "object_ref": "formulation/earlier",
        "edge_status": "retrieval_candidate",
    }
    object_index = {
        "formulation/later": {"date_block": {"date_earliest": 451}},
        "formulation/earlier": {"date_block": {"date_latest": 325}},
    }

    failures = v.validate_genealogy_edge_record(edge, object_index=object_index)

    assert any("V-TIME-1" in failure for failure in failures)


def test_evidence_packet_requires_exact_non_authority_block() -> None:
    packet = {
        "non_authority_block": {
            **v.NON_AUTHORITY_BLOCK,
            "creates_doctrine_authority": True,
        },
        "sections": {
            "scripture_refs": [],
            "boundary_sources": [],
            "doctrine_objects": [],
            "advisory_notes": [],
        },
    }

    failures = v.validate_evidence_packet_record(packet)

    assert any("non_authority_block" in failure for failure in failures)


def test_advisory_rows_are_quarantined_to_advisory_notes() -> None:
    row = {
        "namespace": "advisory_",
        "authority_rung": "S7",
        "review_status": "unreviewed",
        "provenance_ref": "advisory/noesis",
    }

    failures = v.validate_packet_row(row, section="doctrine_objects", label="row")

    assert any("advisory refs may appear only in advisory_notes" in failure for failure in failures)


def test_gate_trigger_registry_references_scripture_repo_paths() -> None:
    registry = v.load_gate_trigger_registry()

    failures = v.validate_gate_trigger_registry(registry)

    assert failures == []
    for value in registry["scripture_repo_refs"].values():
        assert value.startswith("logos-scripture-graph:")


def test_gate_trigger_forces_original_language_gate() -> None:
    registry = v.load_gate_trigger_registry()
    record = {
        "doctrine_provenance": base_provenance(original_language_review="not_required"),
        "gate_triggers": {
            "original_language_review": ["specific_lemma_or_term"],
        },
    }

    failures = v.validate_gate_triggers_for_record(record, registry)

    assert any("original-language trigger requires" in failure for failure in failures)
