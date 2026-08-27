#!/usr/bin/env python3
"""Validate the static Biblical Evidence Graph Demonstration V1.

Capability classification: ``portable_core``. The validator is deterministic,
offline, provider-neutral, read-only, and repository-local. A pass proves only
the encoded file, asset, provenance, rights, graph, mesh, fixture, digest, and
status invariants. It does not prove historical truth, transcription or
translation quality, scholarly consensus, doctrine, expert approval, or runtime
readiness.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_REL = Path(
    "docs/roadmap/logos-stewardship-architecture-buildout/revisions/"
    "biblical-evidence-demonstration-v1"
)
PACKAGE_ROOT = ROOT / PACKAGE_REL
IMAGE_REL = PACKAGE_REL / "assets/p66-cologne-john19-verso.jpg"
EXPECTED_IMAGE_SHA256 = "f7453af8d2523cc358148c7d26072d87b53c991aa03df667f8c5c54c7beef040"
EXPECTED_IMAGE_BYTES = 1083773
EXPECTED_IMAGE_DIMENSIONS = (1802, 1921)
EXPECTED_SEGMENTS = {
    "p66-john19-08-11": ("John.19.8-John.19.11", [f"John.19.{n}" for n in range(8, 12)], "M7_sol-John-057"),
    "p66-john19-13-15": ("John.19.13-John.19.15", [f"John.19.{n}" for n in range(13, 16)], "M7_sol-John-057"),
    "p66-john19-18-20": ("John.19.18-John.19.20", [f"John.19.{n}" for n in range(18, 21)], "M7_sol-John-058"),
    "p66-john19-23-24": ("John.19.23-John.19.24", [f"John.19.{n}" for n in range(23, 25)], "M7_sol-John-058"),
}
EXPECTED_CASES = {
    "sennacherib-lachish",
    "tel-dan",
    "pilate-inscription",
    "jericho-control",
    "hittite-reception-control",
}
EXPECTED_FIXTURE_RULES = {
    "p66_non_contiguous_coverage",
    "p66_asset_identity",
    "p66_rights_attribution",
    "p66_layer_rights_separation",
    "m7_candidate_boundary",
    "m8_pending_boundary",
    "forbidden_relation",
    "academic_claim_boundaries",
    "mesh_independence",
    "mesh_role_permissions",
    "relation_kind_compatibility",
    "trust_zone_authority_path",
    "graph_claim_identity",
    "graph_invariant_consistency",
    "completeness_input_drift",
    "extension_authority_noninterference",
    "crosswalk_provenance_integrity",
    "mesh_governance_contract",
    "document_identity_envelope",
    "graph_identity",
    "duplicate_mapping_key",
}
FORBIDDEN_RELATIONS = {
    "proves_scripture",
    "proves_doctrine",
    "image_directly_translates_to",
    "evidence_count_decides_truth",
    "model_consensus_promotes",
    "graph_reachability_promotes",
    "context_overwrites_canonical",
    "inferred_overwrites_source",
}
METADATA_KEYS = {
    "object_type",
    "trust_zone",
    "lifecycle_status",
    "provenance_note",
    "reason_for_inclusion",
}
EXPECTED_ROLE_MODES = {
    "mesh-coordinator-single-writer": "write_bounded",
    "role-completeness-auditor": "read_only",
    "archaeology-history-researcher": "read_only",
    "manuscript-transmission-researcher": "read_only",
    "source-rights-reviewer": "read_only",
    "citation-source-fitness-checker": "read_only",
    "claim-fidelity-checker": "read_only",
    "graph-contract-engineer": "read_only_design_advice",
    "graph-invariant-red-team": "read_only",
    "privacy-provenance-release-checker": "read_only",
    "human-decision-steward": "decision_packet_only",
}
EXPECTED_ROLE_CLASSES = {
    "mesh-coordinator-single-writer": "orchestrator_writer",
    "role-completeness-auditor": "deterministic_mesh_auditor",
    "archaeology-history-researcher": "neutral_domain_researcher",
    "manuscript-transmission-researcher": "neutral_domain_researcher",
    "source-rights-reviewer": "independent_rights_checker",
    "citation-source-fitness-checker": "independent_academic_checker",
    "claim-fidelity-checker": "independent_semantic_checker",
    "graph-contract-engineer": "graph_engineer",
    "graph-invariant-red-team": "independent_graph_checker",
    "privacy-provenance-release-checker": "independent_release_checker",
    "human-decision-steward": "human_gate_router",
}
EXPECTED_ROLE_CONTRACT_DIGEST = "sha256:4e31fb99b07464d39b9433c9e97e10a81b5f97e35582c1e8650d8fb0e87724bc"
EXPECTED_RELATION_ENDPOINTS = {
    "identifies": ({"source_record"}, {"physical_artifact", "archaeological_context", "text_or_translation_witness"}),
    "depicts": ({"physical_artifact"}, {"historical_claim"}),
    "attests_bounded_claim": ({"source_record", "physical_artifact", "archaeological_context"}, {"historical_claim"}),
    "supports": ({"source_record", "physical_artifact", "archaeological_context", "counterposition"}, {"historical_claim"}),
    "challenges_or_qualifies": ({"source_record", "counterposition", "uncertainty_record"}, {"historical_claim"}),
    "compared_with": ({"historical_claim"}, {"scripture_anchor"}),
    "has_coverage_segment": ({"physical_artifact"}, {"witness_coverage_segment"}),
    "verse_identity_intersects": ({"witness_coverage_segment"}, {"scripture_anchor", "candidate_chunk"}),
    "displayed_through": ({"scripture_anchor"}, {"text_or_translation_witness"}),
    "governed_by_rights": ({"physical_artifact", "text_or_translation_witness"}, {"rights_record"}),
    "requires_review": ({"historical_claim", "physical_artifact", "candidate_chunk", "doctrine_or_tradition_object"}, {"review_gate"}),
    "derived_projection_of": ({"external_domain_extension"}, {"source_record", "historical_claim"}),
}
EXPECTED_GRAPH_STATES = {
    "chunk:m7-public-009": ("M7 public held candidate John-009", "proposed", "candidate_only_non_authorizing"),
    "chunk:m7-local-057": ("M7 local non-durable candidate John-057", "learning-sidecar", "untracked_observation"),
    "chunk:m7-local-058": ("M7 local non-durable candidate John-058", "learning-sidecar", "untracked_observation"),
    "state:m8-john": ("M8 John state", "proposed", "pending_not_built"),
}
EXPECTED_COMPLETENESS_OUTPUT_FIELDS = {
    "phase",
    "input_digests",
    "assigned_roles",
    "missing_roles",
    "rejected_unnecessary_roles",
    "late_discoveries",
    "risk_routing",
    "result",
    "reviewer_independence",
    "reviewer_role",
    "observed_at",
    "changed_input_replay",
    "reviewer_attempt_id",
    "reviewer_evidence_digest",
}
TRUST_ZONES = {"canonical", "tradition-scoped", "proposed", "inferred", "deprecated", "learning-sidecar"}
EXPECTED_DOCUMENT_ENVELOPES = {
    "p66_source": {
        "schema_version": "logos.biblical-evidence.p66-source-pack.v1",
        "object_type": "manuscript_image_source_and_rights_record",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "record_id": "urn:logos:source:p66-cologne-tm61627-verso",
    },
    "archaeology_source_pack": {
        "schema_version": "logos.biblical-evidence.archaeology-source-pack.v1",
        "object_type": "bounded_academic_source_pack",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "pack_id": "urn:logos:source-pack:biblical-evidence-demo-v1",
        "authority_ceiling": "contextual_evidence_only_no_scripture_or_doctrine_promotion",
    },
    "p66_crosswalk": {
        "schema_version": "logos.biblical-evidence.p66-chunk-crosswalk.v1",
        "object_type": "manuscript_translation_chunk_crosswalk",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "crosswalk_id": "urn:logos:crosswalk:p66-cologne-john19-to-candidate-chunks",
    },
    "node_edge_catalog": {
        "schema_version": "logos.biblical-evidence.node-edge-catalog.v1",
        "object_type": "extensible_graph_vocabulary",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "catalog_id": "urn:logos:vocabulary:biblical-evidence-demo-v1",
    },
    "evidence_graph": {
        "schema_version": "logos.biblical-evidence.graph.v1",
        "object_type": "static_claim_mediated_evidence_graph",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "graph_id": "urn:logos:graph:biblical-evidence-demo-v1",
    },
    "query_stories": {
        "schema_version": "logos.biblical-evidence.query-stories.v1",
        "object_type": "bounded_graph_query_contract",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "runtime_status": "not_implemented",
    },
    "agent_mesh": {
        "schema_version": "logos.biblical-evidence.agent-mesh.v3",
        "object_type": "provider_neutral_bounded_academic_agent_mesh",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "mesh_id": "urn:logos:mesh:biblical-evidence-demo-v1",
        "runtime_status": "specification_only_not_activated",
    },
    "completeness_contract": {
        "schema_version": "logos.biblical-evidence.mesh-completeness-audit.v1",
        "object_type": "deterministic_role_completeness_audit_contract",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "audit_id": "urn:logos:audit-contract:biblical-evidence-role-completeness-v1",
    },
    "expert_source_contract": {
        "schema_version": "logos.biblical-evidence.expert-source-pack.v1",
        "object_type": "expert_role_and_source_pack_contract",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
    },
    "adversarial_fixtures": {
        "schema_version": "logos.biblical-evidence.adversarial-fixtures.v1",
        "object_type": "deterministic_negative_fixture_catalog",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
    },
    "acceptance_matrix": {
        "schema_version": "logos.biblical-evidence.acceptance-matrix.v1",
        "object_type": "bounded_acceptance_test_matrix",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
    },
    "asset_attribution": {
        "schema_version": "logos.biblical-evidence.asset-attribution.v1",
        "object_type": "public_asset_attribution_record",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "asset_id": "urn:logos:asset:p66-cologne-john19-verso",
    },
    "source_locator_check": {
        "schema_version": "logos.biblical-evidence.source-locator-check.v1",
        "object_type": "academic_source_locator_check_receipt",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "mutation_performed": False,
    },
    "release_manifest": {
        "schema_version": "logos.biblical-evidence.public-release-manifest.v1",
        "object_type": "public_academic_demonstration_release_manifest",
        "trust_zone": "proposed",
        "lifecycle_status": "active",
        "release_id": "LOGOS-BIBLICAL-EVIDENCE-DEMONSTRATION-V1",
        "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
        "candidate_base_commit": "f159e3f54d96755cd93dc5cfcd069085be4fb2ca",
        "release_status": "validated_static_demonstration",
    },
    "completeness_receipt": {
        "schema_version": "logos.biblical-evidence.mesh-completeness-receipt.v1",
        "object_type": "deterministic_role_completeness_audit_receipt",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "audit_id": "urn:logos:audit-receipt:biblical-evidence-role-completeness-v1",
        "mutation_performed": False,
        "authority_granted": False,
        "status": "pass",
    },
    "validation_receipt": {
        "schema_version": "logos.biblical-evidence.validation-receipt.v1",
        "object_type": "biblical_evidence_demonstration_validation_receipt",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "status": "validated_static_demonstration",
        "mutation_performed": False,
        "authority_granted": False,
    },
}
GOVERNED_ROOT_KEYS = METADATA_KEYS | {"schema_version"}
EXPECTED_DOCUMENT_ROOT_KEYS = {
    "p66_source": GOVERNED_ROOT_KEYS | {"record_id", "object", "asset", "coverage_is_non_contiguous", "coverage_segments", "forbidden_continuous_range", "rights", "layers", "authority", "review"},
    "archaeology_source_pack": GOVERNED_ROOT_KEYS | {"pack_id", "authority_ceiling", "retrieved_on", "source_role_order", "source_catalog", "claim_records", "pack_invariants"},
    "p66_crosswalk": GOVERNED_ROOT_KEYS | {"crosswalk_id", "source_layers", "segments", "invariants"},
    "node_edge_catalog": GOVERNED_ROOT_KEYS | {"catalog_id", "extension_policy", "node_kinds", "relation_kinds", "forbidden_relations", "validation_invariants", "cross_repository_rules", "future_domain_examples"},
    "evidence_graph": GOVERNED_ROOT_KEYS | {"graph_id", "named_graph", "nodes", "edges", "source_claim_edges", "invariants"},
    "query_stories": GOVERNED_ROOT_KEYS | {"runtime_status", "queries"},
    "agent_mesh": GOVERNED_ROOT_KEYS | {"mesh_id", "runtime_status", "portable_core", "tested_runtime_adapters", "model_policy", "execution_invariants", "roles", "conditional_specialist_factory", "mesh_sequence", "risk_routing"},
    "completeness_contract": GOVERNED_ROOT_KEYS | {"audit_id", "phases", "deterministic_inputs", "questions", "outputs", "receipt_semantics", "rerun_triggers", "this_slice_entry_decision"},
    "expert_source_contract": GOVERNED_ROOT_KEYS | {"minimum_role_instruction", "source_fitness", "research_output", "independent_check"},
    "adversarial_fixtures": GOVERNED_ROOT_KEYS | {"fixtures"},
    "acceptance_matrix": GOVERNED_ROOT_KEYS | {"checks"},
    "asset_attribution": GOVERNED_ROOT_KEYS | {"asset_id", "repository_path", "source_filename", "repository_filename", "sha256", "bytes", "dimensions", "credit", "object_label", "source_url", "official_image_url", "license_id", "license_url", "rights_scope", "excluded_rights", "modification_status", "institutional_endorsement", "remote_byte_verification"},
    "source_locator_check": GOVERNED_ROOT_KEYS | {"observed_at", "prior_full_replay_observed_at", "method", "mutation_performed", "summary", "checks", "corrections", "limitations"},
    "release_manifest": GOVERNED_ROOT_KEYS | {"release_id", "work_id", "candidate_base_commit", "release_status", "public_path", "content_status", "validated_structure_metrics", "asset_release", "source_payload_boundary", "authority", "required_release_gates", "frozen_evidence"},
    "completeness_receipt": GOVERNED_ROOT_KEYS | {"audit_id", "mutation_performed", "authority_granted", "changed_input_invalidates_pass", "input_digests", "phase_receipts", "status"},
    "validation_receipt": GOVERNED_ROOT_KEYS | {
        "status",
        "mutation_performed",
        "authority_granted",
        "current_known_blockers",
        "nonclaims",
        "frozen_manifest_sha256",
        "frozen_aggregate_sha256",
    },
}
RESERVED_NODE_PREFIX_TO_KIND = {
    "artifact:": "physical_artifact",
    "chunk:": "candidate_chunk",
    "state:": "candidate_chunk",
    "claim:": "historical_claim",
    "gate:": "review_gate",
    "rights:": "rights_record",
    "scripture:": "scripture_anchor",
    "segment:": "witness_coverage_segment",
    "src:": "source_record",
    "text:": "text_or_translation_witness",
}
EXTERNAL_NODE_KEYS = {
    "id", "kind", "label", "trust_zone", "status", "extension_node",
    "authority_effect", "traversable_for_authority", "extension_payload",
}
EXTERNAL_ID_PATTERN = re.compile(r"^ext:[a-z0-9][a-z0-9._-]*:[a-z0-9][a-z0-9._-]*$")
EXTERNAL_EDGE_ID_PATTERN = re.compile(r"^ext-edge:[a-z0-9][a-z0-9._-]*:[a-z0-9][a-z0-9._-]*$")
EXTERNAL_RELATION_PATTERN = re.compile(r"^ext:[a-z0-9][a-z0-9._-]*:[a-z0-9][a-z0-9._-]*$")
EXTERNAL_PROMOTION_TOKENS = {
    "m7", "m8", "reviewed gold", "built and converged", "canonical",
    "promoted", "proves scripture", "theological authority", "approved",
}
EXPECTED_CATALOG_NODE_KINDS_DIGEST = "sha256:5c9098a043cecf11716170374a4faf31f8bfd93f62b10732337eb9b673ea4589"
EXPECTED_CATALOG_RELATIONS_DIGEST = "sha256:c5cdbc380e31681f342b09e244fbed5f7f8da592dfe02c840741b5e835f115d9"
EXPECTED_CATALOG_EXTENSION_POLICY_DIGEST = "sha256:ac5987ad9dc258313b970ca9099f99551151d54ac8e08c059e580d6f8358358a"
EXPECTED_CATALOG_CROSS_REPOSITORY_DIGEST = "sha256:ec141875714c09f7f0216fa04def089e4c7299b637ab15e205591ae514722938"
EXPECTED_CATALOG_FUTURE_EXAMPLES_DIGEST = "sha256:fe57ec2305cdea9dfa028c67485b605822916e9dcd02735fe90395497e2ba7ab"
EXPECTED_CROSSWALK_SOURCE_LAYERS_DIGEST = "sha256:0e0040de0a8ffabed89626852a1511d51546f20ade1f3764c4d773f6aa3ae2bf"
EXPECTED_CROSSWALK_SEGMENTS_DIGEST = "sha256:43bc3e632ebee744898ba6cd77924bf61b925043ea141f92dbfba11a10ff65db"
EXPECTED_CROSSWALK_INVARIANTS_DIGEST = "sha256:2a17acacb55a4ee01295c42457d3210e4b6ed735bfc02734cc0b462c896d3f71"
EXPECTED_GRAPH_CORE_NODES_DIGEST = "sha256:747e1a237a1b1db1eed816ae46ff5f22c6f1a331f98065ca31842d9ce945ff7a"
EXPECTED_GRAPH_CORE_EDGES_DIGEST = "sha256:fefc1ff98ec2d9cb8f0387569d9d83e2a38f49a86eb739c8a09da0d2c8ed4083"
EXPECTED_GRAPH_SOURCE_CLAIM_EDGES_DIGEST = "sha256:66ddcc8e1b148d1b92aa82ab25d1d0bf8dccad7ab5e7eebe6035d70ccef12d05"
EXPECTED_GRAPH_NAMED_DIGEST = "sha256:3eefad51751fa71fd92b74e5943cadc876ab3a40affad7518a73277bdd0fbb66"
EXPECTED_CORE_EDGE_IDS = {f"e{number:03d}" for number in range(1, 26)}
EXPECTED_MESH_FACTORY_DIGEST = "sha256:9c195792397b0e57886f042ce1082d23063283863984b9db05f5e3ed5d108b86"
EXPECTED_MESH_SEQUENCE_DIGEST = "sha256:6cfa5439de3777e17b0d05c2f5e4e841e6d94a05b4a7143870aca42249f66c0b"
EXPECTED_MESH_RISK_ROUTING_DIGEST = "sha256:cbc59c970bdcd0ac7f7ce2e0d14ecab324553286fb6e3618bd87831052161067"
EXPECTED_MESH_EXECUTION_DIGEST = "sha256:b699eb82c4ff3cb92bccff75d0a29f5e1e3433918b380c5d09d268a6b3bb25bb"
EXPECTED_MESH_MODEL_POLICY_DIGEST = "sha256:e4f08da086dbbd517b074fbd58bf3a65c4a6512b8b7e6d3bf193e9d76f7ff093"
EXPECTED_COMPLETENESS_CONTRACT_DIGEST = "sha256:05b08a51d42f50c50a869512b862211622e5ca62fc079c391bce4cd1218df83f"
EXPECTED_GRAPH_ROOT_KEYS = {
    "schema_version", "object_type", "trust_zone", "lifecycle_status", "provenance_note",
    "reason_for_inclusion", "graph_id", "named_graph", "nodes", "edges", "source_claim_edges", "invariants",
}
EXPECTED_CATALOG_ROOT_KEYS = {
    "schema_version", "object_type", "trust_zone", "lifecycle_status", "provenance_note",
    "reason_for_inclusion", "catalog_id", "extension_policy", "node_kinds", "relation_kinds",
    "forbidden_relations", "validation_invariants", "cross_repository_rules", "future_domain_examples",
}
EXPECTED_CROSSWALK_ROOT_KEYS = {
    "schema_version", "object_type", "trust_zone", "lifecycle_status", "provenance_note",
    "reason_for_inclusion", "crosswalk_id", "source_layers", "segments", "invariants",
}
EXPECTED_MESH_ROOT_KEYS = {
    "schema_version", "object_type", "trust_zone", "lifecycle_status", "provenance_note",
    "reason_for_inclusion", "mesh_id", "runtime_status", "portable_core", "tested_runtime_adapters",
    "model_policy", "execution_invariants", "roles", "conditional_specialist_factory", "mesh_sequence", "risk_routing",
}
ALLOWED_GRAPH_NODE_KEYS = {"id", "kind", "label", "trust_zone", "status", "source_claim_id"}
ALLOWED_UNKNOWN_EDGE_KEYS = {
    "id", "from", "relation", "to", "authority_effect", "extension_relation", "extension_payload", "traversable_for_authority",
}
EXPECTED_COMPLETENESS_RECEIPT_ROOT_KEYS = {
    "schema_version", "object_type", "trust_zone", "lifecycle_status", "provenance_note",
    "reason_for_inclusion", "audit_id", "mutation_performed", "authority_granted",
    "changed_input_invalidates_pass", "input_digests", "phase_receipts", "status",
}
EXPECTED_COMPLETENESS_RISK_ROUTES = {
    "low": "deterministic_validation_and_one_independent_checker",
    "medium": "two_independent_relevant_checkers_and_dissent_metadata",
    "high": "named_human_authority",
    "critical": "fail_closed_no_publication_or_promotion",
}
EXPECTED_REJECTED_UNNECESSARY_ROLES = {"generic_apologist", "generic_theologian"}
EXPECTED_LATE_DISCOVERY_IDS = {
    "academic-source-identity-failures",
    "graph-mesh-semantic-bypasses",
    "receipt-provenance-drift",
}
REVIEW_REPORTS = {
    "academic": {
        "path": "release/independent-academic-review.md",
        "review_id": "urn:logos:review:biblical-evidence-academic-v1",
        "object_type": "independent_academic_source_review_receipt",
        "review_class": "academic_source_fitness",
        "reviewer_role": "citation-source-fitness-checker",
        "reviewer_identity": "codex-subagent-independent-academic-review",
        "attempt_pattern": r"^REVIEW-ACADEMIC-[0-9]{3}$",
        "required_scope": {
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/sources/archaeology-source-pack.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/graph/evidence-graph.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/release/source-locator-check.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/frozen-digests.json",
        },
    },
    "rights": {
        "path": "release/independent-rights-review.md",
        "review_id": "urn:logos:review:biblical-evidence-rights-v1",
        "object_type": "independent_rights_release_review_receipt",
        "review_class": "rights_provenance_and_release",
        "reviewer_role": "source-rights-reviewer",
        "reviewer_identity": "codex-subagent-independent-rights-release-review",
        "attempt_pattern": r"^REVIEW-RIGHTS-[0-9]{3}$",
        "required_scope": {
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/assets/p66-cologne-john19-verso.jpg",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/sources/p66-source-and-rights.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/release/asset-attribution.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/release/public-release-manifest.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/frozen-digests.json",
        },
    },
    "graph_mesh": {
        "path": "release/independent-graph-mesh-review.md",
        "review_id": "urn:logos:review:biblical-evidence-graph-mesh-v1",
        "object_type": "independent_graph_mesh_red_team_receipt",
        "review_class": "graph_mesh_semantic_red_team",
        "reviewer_role": "graph-invariant-red-team",
        "reviewer_identity": "codex-subagent-independent-graph-mesh-red-team",
        "attempt_pattern": r"^REVIEW-GRAPH-MESH-[0-9]{3}$",
        "required_scope": {
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/graph/node-edge-catalog.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/graph/evidence-graph.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/graph/p66-chunk-crosswalk.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/mesh/agent-mesh.v3.json",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/mesh/completeness-audit-contract.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/checks/adversarial-fixtures.yaml",
            "docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/frozen-digests.json",
            "scripts/validate_biblical_evidence_demo.py",
            "tests/test_biblical_evidence_demo.py",
        },
    },
}
REVIEW_FRONTMATTER_KEYS = {
    "schema_version", "object_type", "trust_zone", "lifecycle_status", "provenance_note",
    "reason_for_inclusion", "review_id", "review_class", "reviewer_role", "reviewer_identity",
    "reviewer_attempt_id", "reviewer_independence",
    "independence_basis", "result", "frozen_manifest_sha256", "frozen_aggregate_sha256",
    "reviewed_scope", "reviewed_scope_digests", "blocking_findings", "residual_nonclaims", "mutation_performed",
    "authority_granted", "qualified_human_approval", "observed_at",
}
EXPECTED_LATE_DISCOVERIES = {
    "academic-source-identity-failures": {
        "failure_mode": "misidentified_or_incompletely_bounded_academic_source_records",
        "resolved_by_role_ids": ["archaeology-history-researcher", "citation-source-fitness-checker"],
        "risk_level": "medium",
        "evidence_paths": ["sources/archaeology-source-pack.yaml", "release/source-locator-check.json"],
    },
    "graph-mesh-semantic-bypasses": {
        "failure_mode": "graph_identity_authority_or_completeness_semantic_bypass",
        "resolved_by_role_ids": ["graph-contract-engineer", "graph-invariant-red-team"],
        "risk_level": "medium",
        "evidence_paths": [
            "graph/node-edge-catalog.yaml",
            "graph/evidence-graph.yaml",
            "checks/adversarial-fixtures.yaml",
            "scripts/validate_biblical_evidence_demo.py",
            "tests/test_biblical_evidence_demo.py",
        ],
    },
    "receipt-provenance-drift": {
        "failure_mode": "release_or_completeness_receipt_not_bound_to_current_candidate",
        "resolved_by_role_ids": ["role-completeness-auditor", "privacy-provenance-release-checker"],
        "risk_level": "medium",
        "evidence_paths": [
            "mesh/completeness-audit-contract.yaml",
            "release/public-release-manifest.yaml",
            "scripts/validate_biblical_evidence_demo.py",
        ],
    },
}
LOWER_TRUST_AUTHORITY_SOURCES = {"learning-sidecar", "inferred", "deprecated"}
EXPECTED_SOURCE_FACTS = {
    "oracc-rinap-q003496": {
        "title": "RINAP 3/1 Sennacherib 022, Chicago/Taylor Prism (Q003496)",
        "locator": "https://oracc.museum.upenn.edu/rinap/rinap3/Q003496",
    },
    "bm-lachish-relief-124906": {
        "locator": "https://www.britishmuseum.org/collection/object/W_1856-0909-14_2",
        "object_number": "1856,0909.14 / museum number 124906",
    },
    "atiqot-lachish-gate-2023": {
        "publication_year": 2023,
        "source_role": "primary_inscription_or_excavation_publication",
    },
    "pilate-sherwin-white-1964": {"source_role": "scholarly_review"},
    "jericho-bruins-van-der-plicht-1995": {
        "publication_year": 1995,
        "locator": "https://doi.org/10.1017/S0033822200030666",
    },
    "jericho-nigro-yasine-2024": {
        "publication_year": 2024,
        "locator": "https://iris.uniroma1.it/retrieve/c19bebaa-2701-47df-83b5-25726d821c17/Nigro_interim-report-excavations_2024.pdf",
        "doi": "10.53131/VO2724-587X2024-2_4",
    },
    "jericho-garstang-1935": {
        "publication_year": 1935,
        "locator": "https://www.tandfonline.com/doi/abs/10.1179/peq.1935.67.2.61",
        "doi": "10.1179/peq.1935.67.2.61",
        "title": "The Fall of Bronze Age Jericho",
    },
    "hittites-bryce-2005": {"source_role": "scholarly_monograph"},
    "hittites-lipinski-2012": {
        "publication_year": 2012,
        "locator": "https://czasopisma.kul.pl/index.php/ba/article/view/835",
        "doi": "10.31743/ba.835",
        "title": "Hittites and Hurrians in the Bible",
    },
}
FROZEN_EXCLUSIONS = {
    "frozen-digests.json",
    "validation-receipt.json",
    "release/independent-academic-review.md",
    "release/independent-rights-review.md",
    "release/independent-graph-mesh-review.md",
    "release/exit-completeness-audit.yaml",
    "release/unchanged-head-gate.json",
}
REQUIRED_PACKAGE_FILES = {
    "README.md",
    "SCOPE.md",
    "REPOSITORY_PLACEMENT.md",
    "assets/p66-cologne-john19-verso.jpg",
    "sources/p66-source-and-rights.yaml",
    "sources/archaeology-source-pack.yaml",
    "graph/p66-chunk-crosswalk.yaml",
    "graph/node-edge-catalog.yaml",
    "graph/evidence-graph.yaml",
    "graph/query-stories.yaml",
    "mesh/agent-mesh.v3.json",
    "mesh/completeness-audit-contract.yaml",
    "mesh/expert-source-pack-contract.yaml",
    "prompts/BUILD_SLICE.md",
    "prompts/VERIFY_ACADEMIC_CLAIMS.md",
    "prompts/RED_TEAM_GRAPH.md",
    "checks/adversarial-fixtures.yaml",
    "checks/acceptance-test-matrix.yaml",
    "release/asset-attribution.yaml",
    "release/source-locator-check.json",
    "release/public-release-manifest.yaml",
    "release/independent-academic-review.md",
    "release/independent-rights-review.md",
    "release/independent-graph-mesh-review.md",
    "release/exit-completeness-audit.yaml",
    "frozen-digests.json",
    "validation-receipt.json",
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


class DemoInputError(RuntimeError):
    """A required candidate input cannot be loaded safely."""


class DuplicateKeyError(ValueError):
    """A serialized mapping contains a duplicate member name."""


class StrictSafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate keys recursively."""


def _construct_unique_mapping(loader: StrictSafeLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    if not isinstance(node, yaml.nodes.MappingNode):
        raise yaml.constructor.ConstructorError(None, None, "expected a mapping node", node.start_mark)
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark, "found an unhashable mapping key", key_node.start_mark
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark, f"duplicate mapping key {key!r}", key_node.start_mark
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key, value in pairs:
        if key in mapping:
            raise DuplicateKeyError(f"duplicate mapping key {key!r}")
        mapping[key] = value
    return mapping


def _strict_yaml_load(text: str, source: str) -> Any:
    try:
        return yaml.load(text, Loader=StrictSafeLoader)
    except yaml.YAMLError as exc:
        raise DemoInputError(f"cannot parse strict YAML {source}: {exc}") from exc


def _strict_json_load(text: str, source: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_strict_json_object)
    except (json.JSONDecodeError, DuplicateKeyError) as exc:
        raise DemoInputError(f"cannot parse strict JSON {source}: {exc}") from exc


DOCUMENT_FILES = {
    "p66_source": "sources/p66-source-and-rights.yaml",
    "archaeology_source_pack": "sources/archaeology-source-pack.yaml",
    "p66_crosswalk": "graph/p66-chunk-crosswalk.yaml",
    "node_edge_catalog": "graph/node-edge-catalog.yaml",
    "evidence_graph": "graph/evidence-graph.yaml",
    "query_stories": "graph/query-stories.yaml",
    "agent_mesh": "mesh/agent-mesh.v3.json",
    "completeness_contract": "mesh/completeness-audit-contract.yaml",
    "expert_source_contract": "mesh/expert-source-pack-contract.yaml",
    "adversarial_fixtures": "checks/adversarial-fixtures.yaml",
    "acceptance_matrix": "checks/acceptance-test-matrix.yaml",
    "asset_attribution": "release/asset-attribution.yaml",
    "source_locator_check": "release/source-locator-check.json",
    "release_manifest": "release/public-release-manifest.yaml",
    "completeness_receipt": "release/exit-completeness-audit.yaml",
    "validation_receipt": "validation-receipt.json",
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise DemoInputError(f"cannot load YAML {path}: {exc}") from exc
    value = _strict_yaml_load(text, str(path))
    if not isinstance(value, dict):
        raise DemoInputError(f"YAML root must be an object: {path}")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise DemoInputError(f"cannot load JSON {path}: {exc}") from exc
    value = _strict_json_load(text, str(path))
    if not isinstance(value, dict):
        raise DemoInputError(f"JSON root must be an object: {path}")
    return value


def load_documents(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    package = root / PACKAGE_REL
    documents: dict[str, dict[str, Any]] = {}
    for key, relative in DOCUMENT_FILES.items():
        path = package / relative
        documents[key] = _load_json(path) if path.suffix == ".json" else _load_yaml(path)
    return documents


def _parse_markdown_frontmatter_text(text: str, source: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise DemoInputError(f"review Markdown lacks YAML frontmatter: {source}")
    try:
        closing = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise DemoInputError(f"review Markdown has unterminated YAML frontmatter: {source}") from exc
    value = _strict_yaml_load("\n".join(lines[1:closing]), f"review frontmatter {source}")
    if not isinstance(value, dict):
        raise DemoInputError(f"review frontmatter root must be an object: {source}")
    return value


def _load_markdown_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise DemoInputError(f"cannot load review Markdown {path}: {exc}") from exc
    return _parse_markdown_frontmatter_text(text, str(path))


def _document_envelope_findings(documents: dict[str, dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    if set(documents) != set(DOCUMENT_FILES) or set(EXPECTED_DOCUMENT_ENVELOPES) != set(DOCUMENT_FILES) or set(EXPECTED_DOCUMENT_ROOT_KEYS) != set(DOCUMENT_FILES):
        findings.append(_finding("document_identity_envelope", "package", "loaded document set differs from the exact release contract"))
    for key, expected in EXPECTED_DOCUMENT_ENVELOPES.items():
        document = documents.get(key, {})
        drift = {
            field: (document.get(field), expected_value)
            for field, expected_value in expected.items()
            if document.get(field) != expected_value
        }
        if drift:
            findings.append(_finding("document_identity_envelope", DOCUMENT_FILES[key], f"identity or authority envelope drifted: {drift}"))
        if set(document) != EXPECTED_DOCUMENT_ROOT_KEYS[key]:
            findings.append(_finding(
                "document_identity_envelope",
                DOCUMENT_FILES[key],
                f"root key set drifted: missing={sorted(EXPECTED_DOCUMENT_ROOT_KEYS[key] - set(document))}, extra={sorted(set(document) - EXPECTED_DOCUMENT_ROOT_KEYS[key])}",
            ))
    return findings


def _safe_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value == value.strip()
        and value.isascii()
        and unicodedata.normalize("NFKC", value) == value
        and value.casefold() == value
    )


def _semantic_skeleton(value: Any) -> str:
    normalized = unicodedata.normalize("NFKC", str(value)).casefold()
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def _evidence_reference_rows(root: Path, relative_paths: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative in relative_paths:
        candidate = root / PACKAGE_REL / relative
        if relative.startswith(("scripts/", "tests/")):
            candidate = root / relative
        rows.append({"path": relative, "sha256": "sha256:" + file_sha256(candidate)})
    return rows


def expected_late_discoveries(root: Path, phase: str) -> list[dict[str, Any]]:
    if phase == "entry":
        return []
    status = "detected_and_routed" if phase == "midflight" else "closed_by_existing_roles"
    publication_allowed = phase == "exit"
    rows: list[dict[str, Any]] = []
    for discovery_id in sorted(EXPECTED_LATE_DISCOVERIES):
        spec = EXPECTED_LATE_DISCOVERIES[discovery_id]
        rows.append({
            "discovery_id": discovery_id,
            "failure_mode": spec["failure_mode"],
            "resolution_code": "existing_role_replay",
            "resolved_by_role_ids": spec["resolved_by_role_ids"],
            "risk_level": spec["risk_level"],
            "evidence_refs": _evidence_reference_rows(root, spec["evidence_paths"]),
            "authority_effect": "none",
            "publication_allowed": publication_allowed,
            "status": status,
        })
    return rows


def jpeg_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise DemoInputError(f"not a JPEG stream: {path}")
    sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    offset = 2
    while offset < len(data):
        while offset < len(data) and data[offset] != 0xFF:
            offset += 1
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in {0x01, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(data):
            break
        length = int.from_bytes(data[offset : offset + 2], "big")
        if length < 2 or offset + length > len(data):
            raise DemoInputError(f"invalid JPEG segment length: {path}")
        if marker in sof_markers:
            if length < 7:
                raise DemoInputError(f"invalid JPEG SOF segment: {path}")
            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")
            return width, height
        offset += length
    raise DemoInputError(f"JPEG dimensions not found: {path}")


def _finding(rule: str, path: str, detail: str) -> Finding:
    return Finding(rule, path, detail)


def _metadata_findings(documents: dict[str, dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    for key, document in documents.items():
        missing = sorted(METADATA_KEYS - set(document))
        if missing:
            findings.append(_finding("required_metadata", DOCUMENT_FILES[key], f"missing {missing}"))
        if document.get("trust_zone") not in TRUST_ZONES:
            findings.append(_finding("required_metadata", DOCUMENT_FILES[key], "invalid trust_zone"))
    return findings


def _asset_findings(documents: dict[str, dict[str, Any]], root: Path, check_asset: bool) -> list[Finding]:
    findings: list[Finding] = []
    path = root / IMAGE_REL
    source = documents["p66_source"]
    attribution = documents["asset_attribution"]
    asset = source.get("asset", {})
    if asset.get("sha256") != EXPECTED_IMAGE_SHA256 or asset.get("bytes") != EXPECTED_IMAGE_BYTES:
        findings.append(_finding("p66_asset_identity", DOCUMENT_FILES["p66_source"], "declared hash or byte count drifted"))
    if (asset.get("width_px"), asset.get("height_px")) != EXPECTED_IMAGE_DIMENSIONS:
        findings.append(_finding("p66_asset_identity", DOCUMENT_FILES["p66_source"], "declared dimensions drifted"))
    if asset.get("remote_sha256") is not None:
        findings.append(_finding("p66_asset_identity", DOCUMENT_FILES["p66_source"], "remote hash must be nested under byte_verification"))
    remote = asset.get("byte_verification", {})
    if remote.get("remote_sha256") != EXPECTED_IMAGE_SHA256 or remote.get("local_remote_match") is not True:
        findings.append(_finding("p66_asset_identity", DOCUMENT_FILES["p66_source"], "remote byte-match evidence is absent or changed"))
    if attribution.get("sha256") != EXPECTED_IMAGE_SHA256 or attribution.get("bytes") != EXPECTED_IMAGE_BYTES:
        findings.append(_finding("p66_asset_identity", DOCUMENT_FILES["asset_attribution"], "attribution record is not bound to exact bytes"))
    if check_asset:
        if not path.is_file():
            findings.append(_finding("p66_asset_identity", str(IMAGE_REL), "image is missing"))
        else:
            if file_sha256(path) != EXPECTED_IMAGE_SHA256 or path.stat().st_size != EXPECTED_IMAGE_BYTES:
                findings.append(_finding("p66_asset_identity", str(IMAGE_REL), "repository bytes do not match the verified official image"))
            try:
                dimensions = jpeg_dimensions(path)
            except DemoInputError as exc:
                findings.append(_finding("p66_asset_identity", str(IMAGE_REL), str(exc)))
            else:
                if dimensions != EXPECTED_IMAGE_DIMENSIONS:
                    findings.append(_finding("p66_asset_identity", str(IMAGE_REL), f"JPEG dimensions are {dimensions!r}"))
    return findings


def _p66_findings(documents: dict[str, dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    source = documents["p66_source"]
    crosswalk = documents["p66_crosswalk"]
    if set(crosswalk) != EXPECTED_CROSSWALK_ROOT_KEYS:
        findings.append(_finding("crosswalk_provenance_integrity", DOCUMENT_FILES["p66_crosswalk"], "crosswalk root fields drifted"))
    if _canonical_digest(crosswalk.get("source_layers", {})) != EXPECTED_CROSSWALK_SOURCE_LAYERS_DIGEST:
        findings.append(_finding("crosswalk_provenance_integrity", DOCUMENT_FILES["p66_crosswalk"], "P66, English, M7, or M8 source-layer identity drifted"))
    if _canonical_digest(crosswalk.get("segments", [])) != EXPECTED_CROSSWALK_SEGMENTS_DIGEST:
        findings.append(_finding("crosswalk_provenance_integrity", DOCUMENT_FILES["p66_crosswalk"], "exact verse, English, or candidate crosswalk content drifted"))
    if _canonical_digest(crosswalk.get("invariants", {})) != EXPECTED_CROSSWALK_INVARIANTS_DIGEST:
        findings.append(_finding("crosswalk_provenance_integrity", DOCUMENT_FILES["p66_crosswalk"], "crosswalk invariants drifted or contradicted the source state"))
    segments = source.get("coverage_segments", [])
    observed = {row.get("segment_id"): row.get("passage") for row in segments if isinstance(row, dict)}
    expected = {key: value[0] for key, value in EXPECTED_SEGMENTS.items()}
    if observed != expected or source.get("coverage_is_non_contiguous") is not True:
        findings.append(_finding("p66_non_contiguous_coverage", DOCUMENT_FILES["p66_source"], "exact four non-contiguous ranges are required"))
    if source.get("forbidden_continuous_range") != "John.19.8-John.19.24":
        findings.append(_finding("p66_non_contiguous_coverage", DOCUMENT_FILES["p66_source"], "forbidden continuous range marker drifted"))
    rights = source.get("rights", {})
    required_rights = {
        "license_id": "CC-BY-4.0",
        "attribution_required": True,
        "license_link_required": True,
        "source_link_required": True,
        "change_indication_required": True,
        "endorsement_implied": False,
    }
    for field, expected_value in required_rights.items():
        if rights.get(field) != expected_value:
            findings.append(_finding("p66_rights_attribution", DOCUMENT_FILES["p66_source"], f"{field} must equal {expected_value!r}"))
    if not rights.get("attribution_text") or "Universität zu Köln" not in rights.get("attribution_text", ""):
        findings.append(_finding("p66_rights_attribution", DOCUMENT_FILES["p66_source"], "required attribution is absent"))
    if rights.get("license_url") != "https://creativecommons.org/licenses/by/4.0/" or not rights.get("source_link_required"):
        findings.append(_finding("p66_rights_attribution", DOCUMENT_FILES["p66_source"], "license/source link requirements drifted"))
    layers = {row.get("layer_id"): row for row in source.get("layers", []) if isinstance(row, dict)}
    english = layers.get("english_translation_display", {})
    if english.get("rights_basis") != "public_domain_eng_web_source_snapshot":
        findings.append(_finding("p66_layer_rights_separation", DOCUMENT_FILES["p66_source"], "English rights must come from eng-web, not image rights"))
    for excluded in ("diplomatic_transcription", "critical_greek_edition"):
        if layers.get(excluded, {}).get("included") is not False:
            findings.append(_finding("p66_layer_rights_separation", DOCUMENT_FILES["p66_source"], f"{excluded} must remain absent"))
    authority = source.get("authority", {})
    if any(value is not False for value in authority.values()):
        findings.append(_finding("p66_layer_rights_separation", DOCUMENT_FILES["p66_source"], "all image and publication authority assertions must be false"))

    cross_segments = crosswalk.get("segments", [])
    cross_by_id = {row.get("segment_id"): row for row in cross_segments if isinstance(row, dict)}
    if set(cross_by_id) != set(EXPECTED_SEGMENTS):
        findings.append(_finding("p66_non_contiguous_coverage", DOCUMENT_FILES["p66_crosswalk"], "crosswalk segment identity drifted"))
    for segment_id, (passage, verses, local_ref) in EXPECTED_SEGMENTS.items():
        row = cross_by_id.get(segment_id, {})
        if row.get("passage") != passage:
            findings.append(_finding("p66_non_contiguous_coverage", DOCUMENT_FILES["p66_crosswalk"], f"{segment_id} passage drifted"))
        observed_verses = [verse.get("verse") for verse in row.get("verses", []) if isinstance(verse, dict)]
        if observed_verses != verses or any(not verse.get("english") for verse in row.get("verses", []) if isinstance(verse, dict)):
            findings.append(_finding("p66_crosswalk_consistency", DOCUMENT_FILES["p66_crosswalk"], f"{segment_id} verse set or English display text drifted"))
        if row.get("m7_durable_candidate_refs") != ["M7_sol-John-009"] or row.get("m7_local_observation_refs") != [local_ref]:
            findings.append(_finding("m7_candidate_boundary", DOCUMENT_FILES["p66_crosswalk"], f"{segment_id} candidate mapping drifted"))
    layers = crosswalk.get("source_layers", {})
    m7 = layers.get("m7_public_metadata", {}).get("durable_candidate", {})
    if m7.get("candidate_only") is not True or m7.get("non_authorizing") is not True or m7.get("lifecycle") != "hold_with_findings":
        findings.append(_finding("m7_candidate_boundary", DOCUMENT_FILES["p66_crosswalk"], "M7 public candidate must remain held, candidate-only, and non-authorizing"))
    local = layers.get("m7_local_corrective_observation", {})
    if local.get("tracked_at_observation") is not False or local.get("durable") is not False or local.get("public_endpoint") is not None or local.get("authority_effect") != "none":
        findings.append(_finding("m7_candidate_boundary", DOCUMENT_FILES["p66_crosswalk"], "local corrective observation must remain non-durable and non-authorizing"))
    m8 = layers.get("m8", {})
    if m8.get("john_status") != "pending_not_built" or m8.get("convergence_status") != "not_started" or m8.get("books_completed") != 22 or m8.get("current_book") != "Isa":
        findings.append(_finding("m8_pending_boundary", DOCUMENT_FILES["p66_crosswalk"], "M8 must remain 22/66, Isa current, John pending, convergence not started"))
    invariants = crosswalk.get("invariants", {})
    if invariants.get("image_to_english_direct_edge_allowed") is not False or invariants.get("authority_effect") != "none":
        findings.append(_finding("p66_layer_rights_separation", DOCUMENT_FILES["p66_crosswalk"], "direct image-to-English authority must remain forbidden"))
    return findings


def _academic_findings(documents: dict[str, dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    pack = documents["archaeology_source_pack"]
    sources = pack.get("source_catalog", [])
    allowed_roles = set(pack.get("source_role_order", []))
    source_ids = [row.get("source_id") for row in sources if isinstance(row, dict)]
    if len(source_ids) != len(set(source_ids)) or any(not value for value in source_ids):
        findings.append(_finding("academic_source_identity", DOCUMENT_FILES["archaeology_source_pack"], "source IDs must be non-empty and unique"))
    for row in sources:
        if not isinstance(row, dict):
            findings.append(_finding("academic_source_fitness", DOCUMENT_FILES["archaeology_source_pack"], "source record must be an object"))
            continue
        locator = row.get("locator")
        if not isinstance(locator, str) or not locator.startswith("https://"):
            findings.append(_finding("academic_source_fitness", DOCUMENT_FILES["archaeology_source_pack"], f"{row.get('source_id')} lacks an HTTPS locator"))
        for field in ("source_role", "title", "responsible_body", "supports", "cannot_establish"):
            if not row.get(field):
                findings.append(_finding("academic_source_fitness", DOCUMENT_FILES["archaeology_source_pack"], f"{row.get('source_id')} lacks {field}"))
        if row.get("source_role") not in allowed_roles:
            findings.append(_finding("academic_source_fitness", DOCUMENT_FILES["archaeology_source_pack"], f"{row.get('source_id')} has unregistered source role {row.get('source_role')!r}"))
    by_source_id = {row.get("source_id"): row for row in sources if isinstance(row, dict)}
    for source_id, expected_fields in EXPECTED_SOURCE_FACTS.items():
        row = by_source_id.get(source_id)
        if row is None:
            findings.append(_finding("academic_source_identity", DOCUMENT_FILES["archaeology_source_pack"], f"required corrected source {source_id} is missing"))
            continue
        drift = {
            field: (row.get(field), expected)
            for field, expected in expected_fields.items()
            if row.get(field) != expected
        }
        if drift:
            findings.append(_finding("academic_source_identity", DOCUMENT_FILES["archaeology_source_pack"], f"{source_id} corrected bibliographic fields drifted: {drift}"))
    claims = pack.get("claim_records", [])
    cases = {row.get("case_id") for row in claims if isinstance(row, dict)}
    if cases != EXPECTED_CASES:
        findings.append(_finding("academic_claim_boundaries", DOCUMENT_FILES["archaeology_source_pack"], f"case set is {sorted(cases)}"))
    source_set = set(source_ids)
    for row in claims:
        if not isinstance(row, dict):
            findings.append(_finding("academic_claim_boundaries", DOCUMENT_FILES["archaeology_source_pack"], "claim record must be an object"))
            continue
        required = ("claim_id", "question", "safe_assertion", "source_refs", "uncertainty", "counterpositions", "cannot_establish", "required_review_classes")
        missing = [field for field in required if not row.get(field)]
        if missing:
            findings.append(_finding("academic_claim_boundaries", DOCUMENT_FILES["archaeology_source_pack"], f"{row.get('claim_id')} lacks {missing}"))
        unknown_refs = sorted(set(row.get("source_refs", [])) - source_set)
        if unknown_refs:
            findings.append(_finding("academic_source_identity", DOCUMENT_FILES["archaeology_source_pack"], f"{row.get('claim_id')} has unknown source refs {unknown_refs}"))
        if row.get("authority_effect") != "none":
            findings.append(_finding("academic_authority_boundary", DOCUMENT_FILES["archaeology_source_pack"], f"{row.get('claim_id')} authority effect is not none"))
    invariants = pack.get("pack_invariants", {})
    if any(invariants.get(field) is not False for field in ("artifact_directly_proves_scripture", "contextual_evidence_establishes_doctrine", "citation_count_decides_truth")):
        findings.append(_finding("academic_authority_boundary", DOCUMENT_FILES["archaeology_source_pack"], "forbidden academic authority shortcut enabled"))
    return findings


def _graph_findings(documents: dict[str, dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    catalog = documents["node_edge_catalog"]
    graph = documents["evidence_graph"]
    if set(catalog) != EXPECTED_CATALOG_ROOT_KEYS:
        findings.append(_finding("graph_invariant_consistency", DOCUMENT_FILES["node_edge_catalog"], "catalog root fields drifted"))
    if _canonical_digest(catalog.get("node_kinds", [])) != EXPECTED_CATALOG_NODE_KINDS_DIGEST:
        findings.append(_finding("graph_invariant_consistency", DOCUMENT_FILES["node_edge_catalog"], "core node-kind contract drifted"))
    if _canonical_digest(catalog.get("relation_kinds", [])) != EXPECTED_CATALOG_RELATIONS_DIGEST:
        findings.append(_finding("relation_kind_compatibility", DOCUMENT_FILES["node_edge_catalog"], "complete registered-relation semantics drifted"))
    if _canonical_digest(catalog.get("extension_policy", {})) != EXPECTED_CATALOG_EXTENSION_POLICY_DIGEST:
        findings.append(_finding("extension_authority_noninterference", DOCUMENT_FILES["node_edge_catalog"], "extension governance contract drifted"))
    if _canonical_digest(catalog.get("cross_repository_rules", {})) != EXPECTED_CATALOG_CROSS_REPOSITORY_DIGEST:
        findings.append(_finding("trust_zone_authority_path", DOCUMENT_FILES["node_edge_catalog"], "cross-repository ownership or trust contract drifted"))
    if _canonical_digest(catalog.get("future_domain_examples", [])) != EXPECTED_CATALOG_FUTURE_EXAMPLES_DIGEST:
        findings.append(_finding("extension_authority_noninterference", DOCUMENT_FILES["node_edge_catalog"], "illustrative future-domain examples drifted or acquired operative semantics"))
    if set(graph) != EXPECTED_GRAPH_ROOT_KEYS:
        findings.append(_finding("graph_invariant_consistency", DOCUMENT_FILES["evidence_graph"], "graph root fields drifted"))
    extension = catalog.get("extension_policy", {})
    if extension.get("closed_world") is not False or extension.get("unknown_extension_payloads_preserved_losslessly") is not True or extension.get("unknown_relation_behavior") != "preserve_but_do_not_traverse_for_authority":
        findings.append(_finding("extension_authority_noninterference", DOCUMENT_FILES["node_edge_catalog"], "extension policy became lossy or authority-traversable"))
    required_extension_fields = {
        "extension_relation_true",
        "extension_payload_present",
        "traversable_for_authority_false",
        "authority_effect_none",
        "existing_endpoints",
    }
    if set(extension.get("unknown_relation_requirements", [])) != required_extension_fields:
        findings.append(_finding("extension_authority_noninterference", DOCUMENT_FILES["node_edge_catalog"], "unknown-relation non-authority requirements drifted"))
    catalog_forbidden = set(catalog.get("forbidden_relations", []))
    if catalog_forbidden != FORBIDDEN_RELATIONS:
        findings.append(_finding("forbidden_relation", DOCUMENT_FILES["node_edge_catalog"], "forbidden relation set differs from the exact non-overlapping contract"))
    catalog_invariants = catalog.get("validation_invariants", {})
    required_catalog_invariants = {
        "registered_relation_endpoint_kinds_enforced",
        "unknown_relations_non_authorizing_and_non_traversable",
        "lower_trust_authority_path_to_canonical_forbidden",
        "source_claim_projection_exact_and_exhaustive",
        "graph_and_source_statuses_cross_checked",
        "evidence_path_to_doctrine_forbidden",
        "document_identity_and_authority_envelopes_exact",
        "reserved_namespace_kind_alignment_enforced",
        "external_node_payload_lossless_and_quarantined",
        "source_claim_identity_kind_and_global_uniqueness_enforced",
        "unknown_relation_identifiers_confusable_safe",
        "forbidden_and_registered_relation_sets_non_overlapping",
    }
    if set(catalog_invariants) != required_catalog_invariants or any(catalog_invariants.get(field) is not True for field in required_catalog_invariants):
        findings.append(_finding("graph_invariant_consistency", DOCUMENT_FILES["node_edge_catalog"], "catalog validation invariants are incomplete or false"))
    relation_rows = [row for row in catalog.get("relation_kinds", []) if isinstance(row, dict)]
    relation_specs = {row.get("relation"): row for row in relation_rows if row.get("relation")}
    if len(relation_specs) != len(relation_rows):
        findings.append(_finding("graph_identity", DOCUMENT_FILES["node_edge_catalog"], "relation kinds must be unique and non-empty"))
    if set(relation_specs) != set(EXPECTED_RELATION_ENDPOINTS):
        findings.append(_finding("relation_kind_compatibility", DOCUMENT_FILES["node_edge_catalog"], "registered relation set differs from the code-pinned release contract"))
    for relation, (expected_from, expected_to) in EXPECTED_RELATION_ENDPOINTS.items():
        spec = relation_specs.get(relation, {})
        if set(spec.get("from_kinds", [])) != expected_from or set(spec.get("to_kinds", [])) != expected_to:
            findings.append(_finding("relation_kind_compatibility", DOCUMENT_FILES["node_edge_catalog"], f"{relation!r} endpoint contract drifted"))
    registered_node_kinds = {
        row.get("kind") for row in catalog.get("node_kinds", []) if isinstance(row, dict) and row.get("kind")
    }
    nodes = graph.get("nodes", [])
    node_ids = [row.get("id") for row in nodes if isinstance(row, dict)]
    node_by_id = {row.get("id"): row for row in nodes if isinstance(row, dict) and row.get("id")}
    node_kinds = {node_id: row.get("kind") for node_id, row in node_by_id.items()}
    if len(node_ids) != len(set(node_ids)) or any(not value for value in node_ids):
        findings.append(_finding("graph_identity", DOCUMENT_FILES["evidence_graph"], "node IDs must be non-empty and unique"))
    core_nodes = [row for row in nodes if isinstance(row, dict) and row.get("kind") != "external_domain_extension"]
    if _canonical_digest(core_nodes) != EXPECTED_GRAPH_CORE_NODES_DIGEST:
        findings.append(_finding("graph_invariant_consistency", DOCUMENT_FILES["evidence_graph"], "released core node identity, label, status, or field contract drifted"))
    observed_candidate_ids = {row.get("id") for row in nodes if isinstance(row, dict) and row.get("kind") == "candidate_chunk"}
    if observed_candidate_ids != set(EXPECTED_GRAPH_STATES):
        candidate_rows = [row for row in nodes if isinstance(row, dict) and row.get("kind") == "candidate_chunk"]
        if any("m7" in str(row.get("id", "")).lower() + str(row.get("label", "")).lower() for row in candidate_rows):
            findings.append(_finding("m7_candidate_boundary", DOCUMENT_FILES["evidence_graph"], "candidate-chunk identity set differs from the exact M7 release set"))
        if any("m8" in str(row.get("id", "")).lower() + str(row.get("label", "")).lower() for row in candidate_rows):
            findings.append(_finding("m8_pending_boundary", DOCUMENT_FILES["evidence_graph"], "candidate-chunk identity set differs from the exact M8 release set"))
    for node_id, node in node_by_id.items():
        if not _safe_identifier(node_id):
            findings.append(_finding("graph_identity", DOCUMENT_FILES["evidence_graph"], f"{node_id!r} is not an exact lowercase ASCII normalized identity"))
        expected_kind = next((kind for prefix, kind in RESERVED_NODE_PREFIX_TO_KIND.items() if str(node_id).startswith(prefix)), None)
        if expected_kind is not None and node.get("kind") != expected_kind:
            findings.append(_finding("graph_identity", DOCUMENT_FILES["evidence_graph"], f"{node_id} uses a reserved namespace for {expected_kind!r}"))
        if node.get("kind") == "external_domain_extension":
            normalized_semantics = _semantic_skeleton(
                " ".join(str(node.get(field, "")) for field in ("id", "label", "status"))
            )
            external_ok = (
                set(node) == EXTERNAL_NODE_KEYS
                and isinstance(node_id, str)
                and EXTERNAL_ID_PATTERN.fullmatch(node_id) is not None
                and isinstance(node.get("label"), str)
                and bool(node.get("label").strip())
                and node.get("label").isascii()
                and unicodedata.normalize("NFKC", node.get("label")) == node.get("label")
                and node.get("trust_zone") == "proposed"
                and node.get("status") == "extension_unreviewed_non_authorizing"
                and node.get("extension_node") is True
                and node.get("authority_effect") == "none"
                and node.get("traversable_for_authority") is False
                and isinstance(node.get("extension_payload"), dict)
                and bool(node.get("extension_payload"))
                and not any(f" {token} " in f" {normalized_semantics} " for token in EXTERNAL_PROMOTION_TOKENS)
            )
            if not external_ok:
                findings.append(_finding("extension_authority_noninterference", DOCUMENT_FILES["evidence_graph"], f"{node_id} external-node envelope, namespace, payload, or non-authority status is invalid"))
        else:
            unexpected_node_keys = set(node) - ALLOWED_GRAPH_NODE_KEYS
            if unexpected_node_keys:
                findings.append(_finding("graph_authority_noninterference", DOCUMENT_FILES["evidence_graph"], f"{node_id} has unreviewed fields {sorted(unexpected_node_keys)}"))
        if node.get("kind") not in registered_node_kinds:
            findings.append(_finding("graph_shape", DOCUMENT_FILES["evidence_graph"], f"{node_id} uses unregistered node kind {node.get('kind')!r}"))
        if node.get("trust_zone") not in TRUST_ZONES:
            findings.append(_finding("trust_zone_authority_path", DOCUMENT_FILES["evidence_graph"], f"{node_id} uses an invalid trust zone"))
        if node.get("kind") != "historical_claim" and "source_claim_id" in node:
            findings.append(_finding("graph_claim_identity", DOCUMENT_FILES["evidence_graph"], f"{node_id} illegally carries source_claim_id outside a historical claim"))
        if node.get("kind") == "scripture_anchor":
            if node.get("trust_zone") != "canonical" or node.get("status") != "identity_pointer_only":
                findings.append(_finding("trust_zone_authority_path", DOCUMENT_FILES["evidence_graph"], f"{node_id} Scripture identity boundary drifted"))
        elif node.get("trust_zone") == "canonical":
            findings.append(_finding("trust_zone_authority_path", DOCUMENT_FILES["evidence_graph"], f"{node_id} non-Scripture node entered the canonical trust zone"))
    edge_ids: list[Any] = []
    traversable_edges: list[tuple[str, str]] = []
    core_edges = [row for row in graph.get("edges", []) if isinstance(row, dict) and row.get("id") in EXPECTED_CORE_EDGE_IDS]
    if {row.get("id") for row in core_edges} != EXPECTED_CORE_EDGE_IDS or _canonical_digest(core_edges) != EXPECTED_GRAPH_CORE_EDGES_DIGEST:
        findings.append(_finding("graph_invariant_consistency", DOCUMENT_FILES["evidence_graph"], "released core edge identity or semantics drifted"))
    for edge in graph.get("edges", []):
        if not isinstance(edge, dict):
            findings.append(_finding("graph_shape", DOCUMENT_FILES["evidence_graph"], "edge must be an object"))
            continue
        edge_ids.append(edge.get("id"))
        relation = edge.get("relation")
        from_id = edge.get("from")
        to_id = edge.get("to")
        endpoints_exist = from_id in node_kinds and to_id in node_kinds
        if not endpoints_exist:
            findings.append(_finding("graph_endpoint", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} has missing endpoint"))
        if relation in FORBIDDEN_RELATIONS:
            findings.append(_finding("forbidden_relation", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} uses {relation!r}"))
        relation_spec = relation_specs.get(relation)
        if relation_spec is None and relation not in FORBIDDEN_RELATIONS:
            normalized_relation = unicodedata.normalize("NFKC", str(relation)).casefold().strip()
            normalized_local_relation = normalized_relation.rsplit(":", 1)[-1]
            semantic_local_relation = _semantic_skeleton(normalized_local_relation)
            protected_relation_semantics = {
                _semantic_skeleton(value) for value in set(relation_specs) | FORBIDDEN_RELATIONS
            }
            unknown_identity_ok = (
                _safe_identifier(relation)
                and EXTERNAL_RELATION_PATTERN.fullmatch(relation) is not None
                and _safe_identifier(edge.get("id"))
                and EXTERNAL_EDGE_ID_PATTERN.fullmatch(edge.get("id")) is not None
                and normalized_relation not in set(relation_specs) | FORBIDDEN_RELATIONS
                and normalized_local_relation not in set(relation_specs) | FORBIDDEN_RELATIONS
                and semantic_local_relation not in protected_relation_semantics
            )
            if not unknown_identity_ok:
                findings.append(_finding("extension_authority_noninterference", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} unknown relation or edge identity is not normalized and namespaced"))
            if set(edge) != ALLOWED_UNKNOWN_EDGE_KEYS:
                findings.append(_finding("extension_authority_noninterference", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} unknown relation outer fields are not exact"))
            extension_ok = (
                edge.get("extension_relation") is True
                and isinstance(edge.get("extension_payload"), dict)
                and bool(edge.get("extension_payload"))
                and edge.get("traversable_for_authority") is False
                and edge.get("authority_effect") == "none"
                and endpoints_exist
            )
            if not extension_ok:
                findings.append(_finding("extension_authority_noninterference", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} unknown relation is not a complete non-authorizing extension"))
        elif relation_spec is not None:
            if edge.get("id") not in EXPECTED_CORE_EDGE_IDS:
                findings.append(_finding("graph_invariant_consistency", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} adds an unreviewed registered-relation edge"))
            from_kind = node_kinds.get(from_id)
            to_kind = node_kinds.get(to_id)
            if from_kind not in set(relation_spec.get("from_kinds", [])) or to_kind not in set(relation_spec.get("to_kinds", [])):
                findings.append(_finding("relation_kind_compatibility", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} uses {relation!r} with {from_kind!r}->{to_kind!r}"))
            if relation_spec.get("authority_effect") != "none":
                findings.append(_finding("graph_authority_noninterference", DOCUMENT_FILES["node_edge_catalog"], f"catalog relation {relation!r} grants authority"))
            if endpoints_exist:
                traversable_edges.append((from_id, to_id))
        if edge.get("authority_effect") != "none":
            findings.append(_finding("graph_authority_noninterference", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} authority effect is not none"))
        from_kind = node_kinds.get(from_id)
        to_kind = node_kinds.get(to_id)
        if relation == "compared_with" and (from_kind != "historical_claim" or to_kind != "scripture_anchor"):
            findings.append(_finding("claim_mediation", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} comparison bypasses a historical claim"))
        if from_kind in {"physical_artifact", "archaeological_context"} and to_kind == "scripture_anchor":
            findings.append(_finding("claim_mediation", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} connects context directly to Scripture"))
        source_node = node_by_id.get(from_id, {})
        target_node = node_by_id.get(to_id, {})
        if source_node.get("trust_zone") in LOWER_TRUST_AUTHORITY_SOURCES and target_node.get("trust_zone") == "canonical":
            findings.append(_finding("trust_zone_authority_path", DOCUMENT_FILES["evidence_graph"], f"{edge.get('id')} connects lower-trust material to canonical identity"))
    if len(edge_ids) != len(set(edge_ids)) or any(not value for value in edge_ids):
        findings.append(_finding("graph_identity", DOCUMENT_FILES["evidence_graph"], "edge IDs must be non-empty and unique"))

    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_by_id}
    for from_id, to_id in traversable_edges:
        adjacency[from_id].append(to_id)

    def reaches(start: str, *, target_kind: str, mediator_kinds: set[str] | None = None) -> bool:
        stack: list[tuple[str, bool]] = [(start, False)]
        seen: set[tuple[str, bool]] = set()
        while stack:
            current, mediated = stack.pop()
            state = (current, mediated)
            if state in seen:
                continue
            seen.add(state)
            for target in adjacency.get(current, []):
                next_mediated = mediated or (node_kinds.get(target) in (mediator_kinds or set()))
                if node_kinds.get(target) == target_kind and (mediator_kinds is None or not next_mediated):
                    return True
                stack.append((target, next_mediated))
        return False

    for node_id, node in node_by_id.items():
        kind = node.get("kind")
        if kind == "physical_artifact" and reaches(node_id, target_kind="scripture_anchor", mediator_kinds={"witness_coverage_segment", "historical_claim"}):
            findings.append(_finding("claim_mediation", DOCUMENT_FILES["evidence_graph"], f"{node_id} reaches Scripture without a witness segment or historical claim"))
        if kind == "archaeological_context" and reaches(node_id, target_kind="scripture_anchor", mediator_kinds={"historical_claim"}):
            findings.append(_finding("claim_mediation", DOCUMENT_FILES["evidence_graph"], f"{node_id} reaches Scripture without a historical claim"))
        if kind in {"physical_artifact", "archaeological_context", "historical_claim"} and reaches(node_id, target_kind="doctrine_or_tradition_object"):
            findings.append(_finding("graph_authority_noninterference", DOCUMENT_FILES["evidence_graph"], f"{node_id} reaches doctrine or tradition material"))
        if node.get("trust_zone") in LOWER_TRUST_AUTHORITY_SOURCES and reaches(node_id, target_kind="scripture_anchor"):
            findings.append(_finding("trust_zone_authority_path", DOCUMENT_FILES["evidence_graph"], f"{node_id} has a path to canonical Scripture"))

    source_pack = documents["archaeology_source_pack"]
    source_ids = {row.get("source_id") for row in source_pack.get("source_catalog", []) if isinstance(row, dict)}
    claim_rows = [row for row in source_pack.get("claim_records", []) if isinstance(row, dict)]
    source_claim_ids = [row.get("claim_id") for row in claim_rows]
    graph_claim_nodes = [row for row in nodes if isinstance(row, dict) and row.get("kind") == "historical_claim"]
    all_source_claim_ids = [row.get("source_claim_id") for row in nodes if isinstance(row, dict) and "source_claim_id" in row]
    if len(all_source_claim_ids) != len(set(all_source_claim_ids)) or any(not _safe_identifier(value) for value in all_source_claim_ids):
        findings.append(_finding("graph_claim_identity", DOCUMENT_FILES["evidence_graph"], "source_claim_id values must be globally unique lowercase ASCII normalized identities"))
    graph_claim_map: dict[str, str] = {}
    for row in graph_claim_nodes:
        source_claim_id = row.get("source_claim_id")
        if not source_claim_id or source_claim_id in graph_claim_map:
            findings.append(_finding("graph_claim_identity", DOCUMENT_FILES["evidence_graph"], f"historical claim {row.get('id')} lacks a unique source_claim_id"))
        else:
            graph_claim_map[source_claim_id] = row.get("id")
    if set(graph_claim_map) != set(source_claim_ids) or len(source_claim_ids) != len(set(source_claim_ids)):
        findings.append(_finding("graph_claim_identity", DOCUMENT_FILES["evidence_graph"], "source-pack and graph historical claim identities are not one-to-one"))
    expected_source_claim_pairs = {
        (source_id, graph_claim_map.get(row.get("claim_id")))
        for row in claim_rows
        for source_id in row.get("source_refs", [])
    }
    observed_source_claim_pairs: list[tuple[Any, Any]] = []
    for edge in graph.get("source_claim_edges", []):
        observed_source_claim_pairs.append((edge.get("source"), edge.get("claim")))
        if edge.get("source") not in source_ids:
            findings.append(_finding("graph_endpoint", DOCUMENT_FILES["evidence_graph"], f"unknown source {edge.get('source')}"))
        if edge.get("claim") not in set(graph_claim_map.values()):
            findings.append(_finding("graph_endpoint", DOCUMENT_FILES["evidence_graph"], f"unknown claim {edge.get('claim')}"))
        if edge.get("relation") not in {"supports", "challenges_or_qualifies"} or edge.get("authority_effect") != "none":
            findings.append(_finding("claim_mediation", DOCUMENT_FILES["evidence_graph"], "source-claim edge violates bounded relation contract"))
        if not edge.get("scope"):
            findings.append(_finding("claim_mediation", DOCUMENT_FILES["evidence_graph"], "source-claim edge lacks a bounded scope"))
    if len(observed_source_claim_pairs) != len(set(observed_source_claim_pairs)) or set(observed_source_claim_pairs) != expected_source_claim_pairs:
        findings.append(_finding("graph_claim_identity", DOCUMENT_FILES["evidence_graph"], "source-claim edge projection is not exact and exhaustive"))
    if _canonical_digest(graph.get("source_claim_edges", [])) != EXPECTED_GRAPH_SOURCE_CLAIM_EDGES_DIGEST:
        findings.append(_finding("graph_claim_identity", DOCUMENT_FILES["evidence_graph"], "source-claim relation polarity, scope, ordering, or authority semantics drifted"))

    expected_m7_ids = {node_id for node_id in EXPECTED_GRAPH_STATES if node_id.startswith("chunk:m7-")}
    observed_m7_ids = {str(node_id) for node_id in node_by_id if str(node_id).startswith("chunk:m7-")}
    if observed_m7_ids != expected_m7_ids:
        findings.append(_finding("m7_candidate_boundary", DOCUMENT_FILES["evidence_graph"], "reserved M7 graph identity set drifted"))
    expected_m8_ids = {node_id for node_id in EXPECTED_GRAPH_STATES if node_id.startswith("state:m8-")}
    observed_m8_ids = {str(node_id) for node_id in node_by_id if str(node_id).startswith("state:m8-")}
    if observed_m8_ids != expected_m8_ids:
        findings.append(_finding("m8_pending_boundary", DOCUMENT_FILES["evidence_graph"], "reserved M8 graph identity set drifted"))
    for node_id, (label, trust_zone, status) in EXPECTED_GRAPH_STATES.items():
        node = node_by_id.get(node_id, {})
        rule = "m8_pending_boundary" if node_id == "state:m8-john" else "m7_candidate_boundary"
        if node.get("label") != label or node.get("trust_zone") != trust_zone or node.get("status") != status:
            findings.append(_finding(rule, DOCUMENT_FILES["evidence_graph"], f"{node_id} state drifted"))
    required_graph_invariants = {
        "every_edge_endpoint_exists",
        "every_edge_authority_effect_is_none",
        "artifacts_reach_scripture_only_through_claim_or_segment_identity",
        "archaeology_reaches_scripture_only_through_historical_claim",
        "no_path_promotes_to_doctrine",
        "m7_candidate_state_preserved",
        "m8_john_pending",
        "convergence_not_started",
    }
    invariants = graph.get("invariants", {})
    if set(invariants) != required_graph_invariants or any(invariants.get(field) is not True for field in required_graph_invariants):
        findings.append(_finding("graph_invariant_consistency", DOCUMENT_FILES["evidence_graph"], "graph invariants are incomplete or false"))
    named = graph.get("named_graph", {})
    if _canonical_digest(named) != EXPECTED_GRAPH_NAMED_DIGEST:
        findings.append(_finding("graph_authority_noninterference", DOCUMENT_FILES["evidence_graph"], "named graph fields or authority semantics drifted"))
    if named.get("promotion_authority") != "none" or named.get("runtime_activated") is not False or named.get("canonical") is not False or named.get("theological_authority") is not False:
        findings.append(_finding("graph_authority_noninterference", DOCUMENT_FILES["evidence_graph"], "named graph authority boundary drifted"))
    return findings


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def completeness_input_digests(documents: dict[str, dict[str, Any]], root: Path = ROOT) -> dict[str, str]:
    scope_records = [
        {
            "path": relative,
            "sha256": file_sha256(root / Path(relative)),
            "bytes": (root / Path(relative)).stat().st_size,
        }
        for relative in expected_frozen_paths(root)
    ]
    transformation_classes = [
        "exact_asset_publication",
        "non_contiguous_verse_identity_crosswalk",
        "source_to_bounded_claim_projection",
        "claim_to_scripture_comparison",
        "specification_only_agent_mesh",
    ]
    source_roles = sorted(set(documents["archaeology_source_pack"].get("source_role_order", [])))
    rights = documents["p66_source"].get("rights", {})
    rights_classes = sorted(
        {rights.get("license_id"), "public_domain_eng_web_source_snapshot", "linked_text_not_licensed_by_image"} - {None}
    )
    relation_classes = sorted(
        row.get("relation")
        for row in documents["node_edge_catalog"].get("relation_kinds", [])
        if isinstance(row, dict) and row.get("relation")
    )
    cases = sorted(
        row.get("case_id")
        for row in documents["archaeology_source_pack"].get("claim_records", [])
        if isinstance(row, dict) and row.get("case_id")
    )
    review_rows = []
    for relative in (
        "release/independent-academic-review.md",
        "release/independent-rights-review.md",
        "release/independent-graph-mesh-review.md",
    ):
        path = root / PACKAGE_REL / relative
        review_rows.append({
            "path": relative,
            "sha256": file_sha256(path) if path.is_file() else None,
            "missing": not path.is_file(),
        })
    execution_fingerprint = {
        "runtime_status": documents["agent_mesh"].get("runtime_status"),
        "portable_core": documents["agent_mesh"].get("portable_core"),
        "tested_runtime_adapters": documents["agent_mesh"].get("tested_runtime_adapters"),
        "model_policy": documents["agent_mesh"].get("model_policy"),
    }
    return {
        "exact_scope_digest": _canonical_digest(scope_records),
        "claim_class_set": _canonical_digest(cases),
        "transformation_class_set": _canonical_digest(transformation_classes),
        "source_role_set": _canonical_digest(source_roles),
        "rights_class_set": _canonical_digest(rights_classes),
        "graph_relation_set": _canonical_digest(relation_classes),
        "risk_register_digest": "sha256:" + file_sha256(root / PACKAGE_REL / DOCUMENT_FILES["acceptance_matrix"]),
        "assigned_role_manifest_digest": _canonical_digest(documents["agent_mesh"].get("roles", [])),
        "frozen_manifest_digest": "sha256:" + file_sha256(root / PACKAGE_REL / "frozen-digests.json"),
        "candidate_base_commit_digest": _canonical_digest(documents["release_manifest"].get("candidate_base_commit")),
        "validator_digest": "sha256:" + file_sha256(root / "scripts/validate_biblical_evidence_demo.py"),
        "focused_test_digest": "sha256:" + file_sha256(root / "tests/test_biblical_evidence_demo.py"),
        "adversarial_fixture_digest": "sha256:" + file_sha256(root / PACKAGE_REL / DOCUMENT_FILES["adversarial_fixtures"]),
        "independent_review_evidence_digest": _canonical_digest(review_rows),
        "execution_environment_fingerprint_digest": _canonical_digest(execution_fingerprint),
    }


def _mesh_findings(documents: dict[str, dict[str, Any]], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    mesh = documents["agent_mesh"]
    if set(mesh) != EXPECTED_MESH_ROOT_KEYS:
        findings.append(_finding("mesh_governance_contract", DOCUMENT_FILES["agent_mesh"], "mesh root fields drifted or acquired hidden authority"))
    invariants = mesh.get("execution_invariants", {})
    if _canonical_digest(invariants) != EXPECTED_MESH_EXECUTION_DIGEST:
        findings.append(_finding("mesh_governance_contract", DOCUMENT_FILES["agent_mesh"], "execution invariants drifted or acquired hidden permissions"))
    required_true = (
        "single_writer",
        "researchers_are_read_only",
        "reviewers_are_read_only",
        "writer_cannot_approve_own_output",
        "researcher_cannot_certify_own_citations",
        "rights_reviewer_is_distinct_from_asset_researcher",
        "high_risk_disagreement_routes_to_human",
        "no_agent_can_promote_scripture_or_doctrine",
        "no_runtime_or_source_ingestion_authority",
    )
    if any(invariants.get(field) is not True for field in required_true):
        findings.append(_finding("mesh_independence", DOCUMENT_FILES["agent_mesh"], "one or more required separation-of-duty invariants are false"))
    if invariants.get("maximum_delegation_depth") != 1 or invariants.get("maximum_parallel_roles", 99) > 4:
        findings.append(_finding("mesh_boundedness", DOCUMENT_FILES["agent_mesh"], "delegation depth or fan-out exceeds contract"))
    roles = mesh.get("roles", [])
    role_id_list = [row.get("role_id") for row in roles if isinstance(row, dict)]
    role_ids = set(role_id_list)
    required_roles = set(EXPECTED_ROLE_MODES)
    if role_ids != required_roles or len(role_id_list) != len(role_ids):
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["agent_mesh"], f"role set differs: missing={sorted(required_roles-role_ids)}, extra={sorted(role_ids-required_roles)}"))
    if _canonical_digest(roles) != EXPECTED_ROLE_CONTRACT_DIGEST:
        findings.append(_finding("mesh_role_instruction_depth", DOCUMENT_FILES["agent_mesh"], "exact reviewed role contracts drifted"))
    for role in roles:
        if len(role.get("knowledge_base_contract", [])) < 4 or len(role.get("may_not", [])) < 3 or len(role.get("purpose", "")) < 60:
            findings.append(_finding("mesh_role_instruction_depth", DOCUMENT_FILES["agent_mesh"], f"{role.get('role_id')} is a thin role instruction"))
        expected_mode = EXPECTED_ROLE_MODES.get(role.get("role_id"))
        if expected_mode is None or role.get("mode") != expected_mode:
            findings.append(_finding("mesh_role_permissions", DOCUMENT_FILES["agent_mesh"], f"{role.get('role_id')} mode is {role.get('mode')!r}, expected {expected_mode!r}"))
        expected_class = EXPECTED_ROLE_CLASSES.get(role.get("role_id"))
        if expected_class is None or role.get("class") != expected_class:
            findings.append(_finding("mesh_role_permissions", DOCUMENT_FILES["agent_mesh"], f"{role.get('role_id')} class is {role.get('class')!r}, expected {expected_class!r}"))
        if role.get("role_id") != "mesh-coordinator-single-writer" and str(role.get("mode", "")).startswith("write"):
            findings.append(_finding("mesh_role_permissions", DOCUMENT_FILES["agent_mesh"], f"{role.get('role_id')} acquired write authority"))
        if role.get("role_id") != "mesh-coordinator-single-writer":
            authority_keys = {
                key
                for key, value in role.items()
                if value and any(token in str(key).lower() for token in ("write", "authority", "approve", "mutate", "effect"))
            }
            if authority_keys:
                findings.append(_finding("mesh_role_permissions", DOCUMENT_FILES["agent_mesh"], f"{role.get('role_id')} acquired authority-bearing fields {sorted(authority_keys)}"))
        if role.get("class") == "neutral_domain_researcher" and not any(str(item).startswith("self_") for item in role.get("may_not", [])):
            findings.append(_finding("mesh_role_permissions", DOCUMENT_FILES["agent_mesh"], f"{role.get('role_id')} can self-certify"))
    rights_role = next((row for row in roles if row.get("role_id") == "source-rights-reviewer"), {})
    required_rights_restrictions = {
        "review_own_asset_research",
        "extend_image_license_to_text",
        "waive_privacy_or_provenance",
    }
    required_rights_knowledge = {"license legal code", "holding-institution rights statement", "content hashes", "public-release boundary"}
    if not required_rights_restrictions <= set(rights_role.get("may_not", [])) or not required_rights_knowledge <= set(rights_role.get("knowledge_base_contract", [])):
        findings.append(_finding("mesh_role_permissions", DOCUMENT_FILES["agent_mesh"], "source-rights-reviewer restrictions or knowledge contract drifted"))
    if mesh.get("runtime_status") != "specification_only_not_activated" or mesh.get("portable_core") is not True or mesh.get("tested_runtime_adapters") != []:
        findings.append(_finding("mesh_boundedness", DOCUMENT_FILES["agent_mesh"], "mesh runtime or portability evidence boundary drifted"))
    model_policy = mesh.get("model_policy", {})
    if _canonical_digest(model_policy) != EXPECTED_MESH_MODEL_POLICY_DIGEST:
        findings.append(_finding("mesh_governance_contract", DOCUMENT_FILES["agent_mesh"], "model policy drifted or acquired publication authority"))
    required_model_policy = {
        "capability_tiers_are_mutable_labels": True,
        "permanent_model_identity_binding": False,
        "frontier_escalation_requires_named_failure_mode": True,
        "ultra_effort_requires_owner_authorization": True,
        "cross_model_diversity_claimed": False,
    }
    if any(model_policy.get(field) != expected for field, expected in required_model_policy.items()):
        findings.append(_finding("mesh_boundedness", DOCUMENT_FILES["agent_mesh"], "provider-neutral model policy drifted"))
    factory = mesh.get("conditional_specialist_factory", {})
    if _canonical_digest(factory) != EXPECTED_MESH_FACTORY_DIGEST:
        findings.append(_finding("mesh_governance_contract", DOCUMENT_FILES["agent_mesh"], "conditional specialist factory drifted or became goal-biased"))
    required_factory_metadata = {"role_id", "triggered_failure_mode", "source_pack", "authority_ceiling", "independent_checker", "expiry_or_exit_condition"}
    candidate_classes = [row.get("class") for row in factory.get("candidate_classes", []) if isinstance(row, dict)]
    if (
        factory.get("default") != "do_not_instantiate"
        or set(factory.get("required_metadata", [])) != required_factory_metadata
        or len(factory.get("selection_questions", [])) < 5
        or len(candidate_classes) != len(set(candidate_classes))
        or any(not row.get("trigger") for row in factory.get("candidate_classes", []) if isinstance(row, dict))
    ):
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["agent_mesh"], "conditional specialist factory is unbounded or under-specified"))
    if _canonical_digest(mesh.get("mesh_sequence", [])) != EXPECTED_MESH_SEQUENCE_DIGEST:
        findings.append(_finding("mesh_governance_contract", DOCUMENT_FILES["agent_mesh"], "mesh sequence drifted or lost its human gate"))
    if _canonical_digest(mesh.get("risk_routing", {})) != EXPECTED_MESH_RISK_ROUTING_DIGEST:
        findings.append(_finding("mesh_governance_contract", DOCUMENT_FILES["agent_mesh"], "risk routing drifted or permits automatic promotion"))
    completeness = documents["completeness_contract"]
    if _canonical_digest(completeness) != EXPECTED_COMPLETENESS_CONTRACT_DIGEST:
        findings.append(_finding("mesh_governance_contract", DOCUMENT_FILES["completeness_contract"], "complete deterministic completeness-audit contract drifted"))
    if completeness.get("phases") != ["entry", "midflight", "exit"] or completeness.get("outputs", {}).get("allowed_results") != ["pass", "fail_closed"]:
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_contract"], "entry/midflight/exit fail-closed contract drifted"))
    if set(completeness.get("outputs", {}).get("required_fields", [])) != EXPECTED_COMPLETENESS_OUTPUT_FIELDS:
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_contract"], "completeness output field contract drifted"))
    if completeness.get("this_slice_entry_decision", {}).get("result") != "pass":
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_contract"], "entry completeness decision is not pass"))
    if set(completeness.get("this_slice_entry_decision", {}).get("required_roles", [])) != required_roles:
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_contract"], "entry decision role set differs from the mesh"))
    required_inputs = {
        "exact_scope_digest",
        "claim_class_set",
        "transformation_class_set",
        "source_role_set",
        "rights_class_set",
        "graph_relation_set",
        "risk_register_digest",
        "assigned_role_manifest_digest",
        "frozen_manifest_digest",
        "candidate_base_commit_digest",
        "validator_digest",
        "focused_test_digest",
        "adversarial_fixture_digest",
        "independent_review_evidence_digest",
        "execution_environment_fingerprint_digest",
    }
    if set(completeness.get("deterministic_inputs", [])) != required_inputs:
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_contract"], "deterministic input set drifted"))
    required_triggers = {
        "scope_digest_change",
        "claim_or_transformation_class_change",
        "source_or_rights_class_change",
        "new_material_disagreement",
        "validator_or_review_finding",
        "runtime_provider_tool_or_model_change",
        "candidate_head_change",
    }
    if set(completeness.get("rerun_triggers", [])) != required_triggers:
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_contract"], "completeness rerun triggers drifted"))
    receipt = documents["completeness_receipt"]
    expected_digests = completeness_input_digests(documents, root)
    if set(receipt) != EXPECTED_COMPLETENESS_RECEIPT_ROOT_KEYS or receipt.get("status") != "pass":
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], "receipt root contract or pass status drifted"))
    if receipt.get("input_digests") != expected_digests or receipt.get("changed_input_invalidates_pass") is not True:
        findings.append(_finding("completeness_input_drift", DOCUMENT_FILES["completeness_receipt"], "receipt inputs do not match the current deterministic candidate"))
    phase_receipts = receipt.get("phase_receipts", [])
    phase_names = [row.get("phase") for row in phase_receipts if isinstance(row, dict)]
    if phase_names != ["entry", "midflight", "exit"]:
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], "entry/midflight/exit receipts are missing or out of order"))
    observed_times: list[datetime] = []
    attempt_ids: list[str] = []
    for expected_phase, phase in zip(("entry", "midflight", "exit"), phase_receipts):
        if not isinstance(phase, dict):
            findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], f"{expected_phase} receipt is not an object"))
            continue
        if set(phase) != EXPECTED_COMPLETENESS_OUTPUT_FIELDS:
            findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], f"{phase.get('phase')} receipt fields differ from the exact contract"))
        assigned = phase.get("assigned_roles", [])
        assigned_valid = (
            isinstance(assigned, list)
            and all(isinstance(role_id, str) and role_id for role_id in assigned)
            and set(assigned) == required_roles
            and len(assigned) == len(required_roles)
        )
        if phase.get("phase") != expected_phase or not isinstance(phase.get("input_digests"), dict) or phase.get("input_digests") != expected_digests or not assigned_valid:
            findings.append(_finding("completeness_input_drift", DOCUMENT_FILES["completeness_receipt"], f"{phase.get('phase')} receipt is stale or role-incomplete"))
        expected_attempt_pattern = rf"^REVIEW-COMPLETENESS-{expected_phase.upper()}-[0-9]{{3}}$"
        attempt_id = phase.get("reviewer_attempt_id")
        if isinstance(attempt_id, str):
            attempt_ids.append(attempt_id)
        if (
            phase.get("result") != "pass"
            or phase.get("reviewer_independence") is not True
            or phase.get("reviewer_role") != "role-completeness-auditor"
            or phase.get("changed_input_replay") is not True
            or not isinstance(attempt_id, str)
            or re.fullmatch(expected_attempt_pattern, attempt_id) is None
            or phase.get("reviewer_evidence_digest") != expected_digests["independent_review_evidence_digest"]
        ):
            findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], f"{phase.get('phase')} did not independently pass"))
        observed_at = phase.get("observed_at")
        try:
            observed_time = datetime.strptime(observed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], f"{phase.get('phase')} lacks an exact UTC observation timestamp"))
        else:
            observed_times.append(observed_time)
            if observed_time > datetime.now(timezone.utc):
                findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], f"{phase.get('phase')} observation timestamp is in the future"))
        rejected = phase.get("rejected_unnecessary_roles")
        rejected_valid = (
            isinstance(rejected, list)
            and all(isinstance(row, dict) and set(row) == {"role", "reason"} and all(isinstance(row[field], str) and row[field] for field in ("role", "reason")) for row in rejected)
        )
        rejected_role_ids = {row.get("role") for row in rejected} if rejected_valid else set()
        rejected_valid = rejected_valid and rejected_role_ids == EXPECTED_REJECTED_UNNECESSARY_ROLES and not (rejected_role_ids & set(assigned if isinstance(assigned, list) else []))
        late = phase.get("late_discoveries")
        late_valid = isinstance(late, list) and late == expected_late_discoveries(root, expected_phase)
        routing = phase.get("risk_routing")
        routing_valid = (
            isinstance(routing, list)
            and all(isinstance(row, dict) and set(row) == {"risk", "route", "status"} and all(isinstance(row[field], str) and row[field] for field in ("risk", "route", "status")) for row in routing)
        )
        routing_map = {row.get("risk"): row.get("route") for row in routing} if routing_valid else {}
        routing_valid = routing_valid and len(routing) == 4 and routing_map == EXPECTED_COMPLETENESS_RISK_ROUTES and all(row.get("status") == "preserved" for row in routing)
        if phase.get("missing_roles") != [] or not rejected_valid or not late_valid or not routing_valid:
            findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], f"{phase.get('phase')} has unresolved missing roles or no risk routing"))
    if len(attempt_ids) != 3 or len(set(attempt_ids)) != 3:
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], "reviewer attempt IDs are missing or reused"))
    if len(observed_times) != 3 or observed_times != sorted(observed_times):
        findings.append(_finding("mesh_role_completeness", DOCUMENT_FILES["completeness_receipt"], "phase observation timestamps are missing or not nondecreasing"))
    if receipt.get("mutation_performed") is not False or receipt.get("authority_granted") is not False:
        findings.append(_finding("mesh_role_permissions", DOCUMENT_FILES["completeness_receipt"], "completeness receipt mutated state or granted authority"))
    return findings


def apply_fixture_mutation(documents: dict[str, dict[str, Any]], mutation: str) -> dict[str, dict[str, Any]]:
    changed = copy.deepcopy(documents)
    p66 = changed["p66_source"]
    crosswalk = changed["p66_crosswalk"]
    graph = changed["evidence_graph"]
    pack = changed["archaeology_source_pack"]
    mesh = changed["agent_mesh"]
    catalog = changed["node_edge_catalog"]
    completeness_receipt = changed["completeness_receipt"]
    if mutation == "collapse_four_segments_to_John.19.8-John.19.24":
        p66["coverage_segments"] = [{"segment_id": "p66-john19-08-24", "passage": "John.19.8-John.19.24"}]
    elif mutation == "replace_asset_sha256_with_zero_digest":
        p66["asset"]["sha256"] = "0" * 64
    elif mutation == "remove_attribution_text":
        p66["rights"].pop("attribution_text", None)
    elif mutation == "set_english_translation_rights_basis_to_CC-BY-4.0-image":
        for layer in p66["layers"]:
            if layer.get("layer_id") == "english_translation_display":
                layer["rights_basis"] = "CC-BY-4.0-image"
    elif mutation == "set_m7_candidate_only_false":
        crosswalk["source_layers"]["m7_public_metadata"]["durable_candidate"]["candidate_only"] = False
    elif mutation == "set_m8_convergence_status_complete":
        crosswalk["source_layers"]["m8"]["convergence_status"] = "complete"
    elif mutation == "drift_crosswalk_english_digest":
        crosswalk["source_layers"]["english"]["source_archive_sha256"] = "0" * 64
    elif mutation == "drift_crosswalk_m7_public_head":
        crosswalk["source_layers"]["m7_public_metadata"]["public_ref_head_observed"] = "0" * 40
    elif mutation == "drift_crosswalk_m7_local_digest":
        crosswalk["source_layers"]["m7_local_corrective_observation"]["source_sha256"] = "0" * 64
    elif mutation == "drift_crosswalk_m8_checkpoint":
        crosswalk["source_layers"]["m8"]["checkpoint_head"] = "0" * 40
    elif mutation == "contradict_crosswalk_invariants":
        crosswalk["invariants"]["m7_candidate_only"] = False
        crosswalk["invariants"]["m8_complete"] = True
        crosswalk["invariants"]["convergence_started"] = True
        crosswalk["invariants"]["transcription_claimed_from_image"] = True
    elif mutation in {"add_image_directly_translates_to_edge", "add_proves_scripture_edge", "add_proves_doctrine_edge"}:
        relation = {
            "add_image_directly_translates_to_edge": "image_directly_translates_to",
            "add_proves_scripture_edge": "proves_scripture",
            "add_proves_doctrine_edge": "proves_doctrine",
        }[mutation]
        graph["edges"].append({"id": f"negative-{relation}", "from": "artifact:p66-verso", "relation": relation, "to": "scripture:john19", "authority_effect": "promote"})
    elif mutation == "remove_first_claim_cannot_establish":
        pack["claim_records"][0].pop("cannot_establish", None)
    elif mutation == "remove_first_claim_counterpositions":
        pack["claim_records"][0].pop("counterpositions", None)
    elif mutation == "set_researcher_cannot_certify_own_citations_false":
        mesh["execution_invariants"]["researcher_cannot_certify_own_citations"] = False
    elif mutation == "set_unknown_relation_authority_traversal_allowed":
        catalog["extension_policy"]["unknown_relation_behavior"] = "traverse_for_authority"
    elif mutation == "drift_registered_relation_semantics":
        next(row for row in catalog["relation_kinds"] if row.get("relation") == "compared_with")["comparison_is_not_entailment"] = False
    elif mutation == "disable_extension_human_gate":
        catalog["extension_policy"]["new_core_type_requires_human_architecture_decision"] = False
    elif mutation == "add_image_displayed_through_english_edge":
        graph["edges"].append({"id": "negative-image-display", "from": "artifact:p66-verso", "relation": "displayed_through", "to": "text:eng-web", "authority_effect": "none"})
    elif mutation == "widen_displayed_through_and_add_image_edge":
        next(row for row in catalog["relation_kinds"] if row.get("relation") == "displayed_through")["from_kinds"].append("physical_artifact")
        graph["edges"].append({"id": "negative-catalog-widening", "from": "artifact:p66-verso", "relation": "displayed_through", "to": "text:eng-web", "authority_effect": "none"})
    elif mutation == "add_unknown_edge_outer_promotion_field":
        graph["nodes"].extend([
            {"id": "ext:fixture:negative-a", "kind": "external_domain_extension", "label": "Fixture extension A", "trust_zone": "proposed", "status": "extension_unreviewed_non_authorizing", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"future": "preserved-a"}},
            {"id": "ext:fixture:negative-b", "kind": "external_domain_extension", "label": "Fixture extension B", "trust_zone": "proposed", "status": "extension_unreviewed_non_authorizing", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"future": "preserved-b"}},
        ])
        graph["edges"].append({
            "id": "ext-edge:fixture:negative-promotes",
            "from": "ext:fixture:negative-a",
            "relation": "ext:fixture:future-domain-link",
            "to": "ext:fixture:negative-b",
            "authority_effect": "none",
            "extension_relation": True,
            "extension_payload": {"future": "preserved"},
            "traversable_for_authority": False,
            "promotes": True,
        })
    elif mutation == "add_context_requires_review_doctrine_edge":
        graph["nodes"].extend([
            {"id": "context:negative", "kind": "archaeological_context", "trust_zone": "proposed", "status": "candidate"},
            {"id": "doctrine:negative", "kind": "doctrine_or_tradition_object", "trust_zone": "tradition-scoped", "status": "candidate"},
        ])
        graph["edges"].append({"id": "negative-context-doctrine", "from": "context:negative", "relation": "requires_review", "to": "doctrine:negative", "authority_effect": "none"})
    elif mutation == "add_lower_trust_verse_identity_to_canonical_edge":
        graph["edges"].append({"id": "negative-lower-trust-canonical", "from": "chunk:m7-local-057", "relation": "verse_identity_intersects", "to": "scripture:john19", "authority_effect": "none"})
    elif mutation == "add_canonical_external_node":
        graph["nodes"].append({"id": "external:negative-canonical", "kind": "external_domain_extension", "label": "Negative canonical extension", "trust_zone": "canonical", "status": "candidate"})
    elif mutation == "add_canonical_doctrine_node":
        graph["nodes"].append({"id": "doctrine:negative-canonical", "kind": "doctrine_or_tradition_object", "label": "Negative canonical doctrine", "trust_zone": "canonical", "status": "candidate"})
    elif mutation == "set_graph_m7_status_reviewed_gold":
        next(node for node in graph["nodes"] if node.get("id") == "chunk:m7-public-009")["status"] = "reviewed_gold"
    elif mutation == "set_graph_m7_label_reviewed_gold":
        next(node for node in graph["nodes"] if node.get("id") == "chunk:m7-public-009")["label"] = "M7 reviewed gold John-009"
    elif mutation == "add_graph_m7_alias_node":
        graph["nodes"].append({"id": "chunk:m7-reviewed-alias", "kind": "candidate_chunk", "label": "M7 reviewed alias", "trust_zone": "proposed", "status": "candidate_only_non_authorizing"})
    elif mutation == "add_nonreserved_m7_alias_edge":
        graph["nodes"].append({"id": "candidate:john-reviewed", "kind": "candidate_chunk", "label": "M7 reviewed gold John candidate", "trust_zone": "proposed", "status": "reviewed_gold"})
        graph["edges"].append({"id": "negative-nonreserved-m7", "from": "segment:p66-08-11", "relation": "verse_identity_intersects", "to": "candidate:john-reviewed", "authority_effect": "none"})
    elif mutation == "set_graph_m8_built_and_invariant_false":
        next(node for node in graph["nodes"] if node.get("id") == "state:m8-john")["status"] = "built_and_converged"
        graph["invariants"]["m8_john_pending"] = False
    elif mutation == "set_graph_m8_label_built":
        next(node for node in graph["nodes"] if node.get("id") == "state:m8-john")["label"] = "M8 John built and converged"
    elif mutation == "add_graph_m8_alias_node":
        graph["nodes"].append({"id": "state:m8-john-reviewed-alias", "kind": "candidate_chunk", "label": "M8 John reviewed alias", "trust_zone": "proposed", "status": "pending_not_built"})
    elif mutation == "add_nonreserved_m8_alias_edge":
        graph["nodes"].append({"id": "candidate:john-built", "kind": "candidate_chunk", "label": "M8 John built and converged", "trust_zone": "proposed", "status": "built_and_converged"})
        graph["edges"].append({"id": "negative-nonreserved-m8", "from": "segment:p66-08-11", "relation": "verse_identity_intersects", "to": "candidate:john-built", "authority_effect": "none"})
    elif mutation == "add_hidden_candidate_promotion_fields":
        next(node for node in graph["nodes"] if node.get("id") == "chunk:m7-public-009")["reviewed_gold"] = True
        next(node for node in graph["nodes"] if node.get("id") == "state:m8-john")["convergence_status"] = "complete"
    elif mutation == "add_invented_canonical_scripture_anchor":
        graph["nodes"].append({"id": "scripture:invented-gospel-67", "kind": "scripture_anchor", "label": "Invented canonical Gospel 67", "trust_zone": "canonical", "status": "identity_pointer_only"})
        graph["edges"].append({"id": "negative-invented-scripture", "from": "claim:sennacherib", "relation": "compared_with", "to": "scripture:invented-gospel-67", "authority_effect": "none"})
    elif mutation == "add_canonical_node_theological_authority":
        next(node for node in graph["nodes"] if node.get("id") == "scripture:john19")["theological_authority"] = True
    elif mutation == "add_external_m7_impersonator":
        graph["nodes"].append({"id": "ext:fixture:m7-reviewed", "kind": "external_domain_extension", "label": "M7 reviewed gold John candidate", "trust_zone": "proposed", "status": "extension_unreviewed_non_authorizing", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"opaque": True}})
    elif mutation == "add_external_reserved_scripture_namespace":
        graph["nodes"].append({"id": "scripture:invented-extension", "kind": "external_domain_extension", "label": "Invented extension", "trust_zone": "proposed", "status": "extension_unreviewed_non_authorizing", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"opaque": True}})
    elif mutation == "add_external_promoted_status":
        graph["nodes"].append({"id": "ext:fixture:promoted", "kind": "external_domain_extension", "label": "Future record", "trust_zone": "proposed", "status": "promoted_doctrine", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"opaque": True}})
    elif mutation == "add_external_source_claim_reuse":
        graph["nodes"].append({"id": "ext:fixture:claim-reuse", "kind": "external_domain_extension", "label": "Future record", "trust_zone": "proposed", "status": "extension_unreviewed_non_authorizing", "source_claim_id": "claim-sennacherib-campaign-judah", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"opaque": True}})
    elif mutation == "add_external_confusable_identifier":
        graph["nodes"].append({"id": "ｅｘｔ:fixture:confusable", "kind": "external_domain_extension", "label": "Future record", "trust_zone": "proposed", "status": "extension_unreviewed_non_authorizing", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"opaque": True}})
    elif mutation == "add_external_punctuation_impersonator":
        graph["nodes"].append({"id": "ext:fixture:authority-label", "kind": "external_domain_extension", "label": "theological-authority", "trust_zone": "proposed", "status": "extension_unreviewed_non_authorizing", "extension_node": True, "authority_effect": "none", "traversable_for_authority": False, "extension_payload": {"opaque": True}})
    elif mutation in {"add_unknown_relation_whitespace_spoof", "add_unknown_relation_case_spoof", "add_unknown_relation_confusable_spoof", "add_unknown_relation_protected_tail", "add_unknown_relation_punctuation_spoof"}:
        relation = {
            "add_unknown_relation_whitespace_spoof": "supports ",
            "add_unknown_relation_case_spoof": "PROVES_SCRIPTURE",
            "add_unknown_relation_confusable_spoof": "proves_scripturе",
            "add_unknown_relation_protected_tail": "ext:fixture:supports",
            "add_unknown_relation_punctuation_spoof": "ext:fixture:proves-scripture",
        }[mutation]
        graph["edges"].append({"id": "ext-edge:fixture:spoof", "from": "claim:sennacherib", "relation": relation, "to": "scripture:sennacherib-passages", "authority_effect": "none", "extension_relation": True, "extension_payload": {"opaque": True}, "traversable_for_authority": False})
    elif mutation == "add_forbidden_registered_overlap":
        catalog["forbidden_relations"].append("supports")
    elif mutation == "spoof_machine_document_envelope":
        graph["object_type"] = "canonical_theological_authority_graph"
        graph["trust_zone"] = "canonical"
        graph["lifecycle_status"] = "approved"
        graph["graph_id"] = "urn:logos:graph:approved-doctrine"
    elif mutation == "add_unreviewed_root_authority_field":
        p66["theological_authority"] = True
    elif mutation == "spoof_completeness_root_authority":
        completeness_receipt["object_type"] = "human_approved_theological_authority_receipt"
        completeness_receipt["trust_zone"] = "canonical"
        completeness_receipt["authority_granted"] = True
    elif mutation == "set_graph_invariant_false":
        graph["invariants"]["every_edge_endpoint_exists"] = False
    elif mutation == "link_known_source_to_invented_graph_claim":
        graph["nodes"].append({
            "id": "claim:invented",
            "kind": "historical_claim",
            "source_claim_id": "claim-invented",
            "label": "Invented negative claim",
            "trust_zone": "proposed",
            "status": "candidate",
        })
        graph["source_claim_edges"].append({"source": "bm-sennacherib-prism-91032", "relation": "supports", "claim": "claim:invented", "scope": "negative_fixture", "authority_effect": "none"})
    elif mutation == "corrupt_source_claim_polarity_and_scope":
        edge = next(row for row in graph["source_claim_edges"] if row.get("source") == "pnas-archaeomagnetic-lachish-2022")
        edge["relation"] = "supports"
        edge["scope"] = "proves Scripture and establishes doctrine"
    elif mutation == "relabel_bounded_claim_as_proof":
        next(node for node in graph["nodes"] if node.get("id") == "claim:sennacherib")["label"] = "Archaeology proves Scripture"
    elif mutation == "set_rights_reviewer_write_bounded":
        next(role for role in mesh["roles"] if role.get("role_id") == "source-rights-reviewer")["mode"] = "write_bounded"
    elif mutation == "pad_rights_reviewer_purpose":
        next(role for role in mesh["roles"] if role.get("role_id") == "source-rights-reviewer")["purpose"] += " This padding has no reviewed semantic value."
    elif mutation == "change_rights_reviewer_class_to_writer":
        next(role for role in mesh["roles"] if role.get("role_id") == "source-rights-reviewer")["class"] = "orchestrator_writer"
    elif mutation == "add_rights_reviewer_write_authority":
        next(role for role in mesh["roles"] if role.get("role_id") == "source-rights-reviewer")["write_authority"] = True
    elif mutation == "remove_mesh_human_gate":
        mesh["mesh_sequence"].remove("human_high_risk_disagreement_gate")
    elif mutation == "set_mesh_high_risk_auto_promote":
        mesh["risk_routing"]["high"] = "auto_promote_without_human"
    elif mutation == "add_goal_biased_generic_specialist":
        mesh["conditional_specialist_factory"]["candidate_classes"].append({"class": "generic_apologist", "trigger": "whenever a positive conclusion is desired to prove the Bible is true"})
    elif mutation == "stale_completeness_input_digest":
        completeness_receipt["input_digests"]["exact_scope_digest"] = "sha256:" + "0" * 64
    elif mutation == "set_completeness_semantic_fields_to_wrong_types":
        phases = completeness_receipt.setdefault("phase_receipts", [])
        if not phases:
            phases.append({"phase": "entry"})
        phases[0]["assigned_roles"] = "all roles"
        phases[0]["reviewer_independence"] = "true"
        phases[0]["risk_routing"] = {"critical": "human"}
    elif mutation == "set_completeness_semantic_false_pass":
        phases = completeness_receipt.setdefault("phase_receipts", [])
        if len(phases) != 3:
            raise DemoInputError("semantic completeness fixture requires a known-valid three-phase receipt")
        phases[1]["late_discoveries"][0]["resolution_code"] = "ignored_and_automatically_promoted"
        phases[1]["late_discoveries"][0]["publication_allowed"] = True
    elif mutation == "stale_completeness_validator_digest":
        completeness_receipt["input_digests"]["validator_digest"] = "sha256:" + "0" * 64
    else:
        raise DemoInputError(f"unknown fixture mutation {mutation!r}")
    return changed


def raw_parser_fixture_findings(mutation: str) -> list[Finding]:
    cases = {
        "parse_duplicate_yaml_root_key": lambda: _strict_yaml_load(
            "object_type: canonical_theological_authority_graph\nobject_type: static_claim_mediated_evidence_graph\n",
            "duplicate-yaml-root-fixture",
        ),
        "parse_duplicate_json_nested_key": lambda: _strict_json_load(
            '{"nested":{"authority_granted":true,"authority_granted":false}}',
            "duplicate-json-nested-fixture",
        ),
        "parse_duplicate_review_frontmatter_key": lambda: _parse_markdown_frontmatter_text(
            "---\nresult: fail_closed\nresult: pass\n---\n# Review\n",
            "duplicate-review-frontmatter-fixture",
        ),
    }
    if mutation not in cases:
        raise DemoInputError(f"unknown raw parser fixture {mutation!r}")
    try:
        cases[mutation]()
    except DemoInputError as exc:
        if "duplicate mapping key" in str(exc):
            return [_finding("duplicate_mapping_key", "strict-parser-fixture", mutation)]
        return [_finding("fixture_execution", "strict-parser-fixture", f"{mutation}: unexpected parser failure: {exc}")]
    return []


def build_known_valid_fixture_baseline(
    documents: dict[str, dict[str, Any]], root: Path = ROOT
) -> dict[str, dict[str, Any]]:
    """Return a synthetic receipt-complete baseline for differential negative tests.

    The synthetic receipts never leave memory and grant no authority. They let
    component fixtures prove that their own mutation introduces a new finding
    even while the on-disk release receipts are intentionally pending.
    """
    baseline = copy.deepcopy(documents)
    digest_path = root / PACKAGE_REL / "frozen-digests.json"
    digest_manifest = _load_json(digest_path)
    baseline["validation_receipt"] = {
        "schema_version": "logos.biblical-evidence.validation-receipt.v1",
        "object_type": "biblical_evidence_demonstration_validation_receipt",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "provenance_note": "Synthetic in-memory fixture baseline; never serialized or authority-bearing.",
        "reason_for_inclusion": "Prevent pre-existing pending-release findings from satisfying negative fixtures.",
        "status": "validated_static_demonstration",
        "mutation_performed": False,
        "authority_granted": False,
        "current_known_blockers": [],
        "nonclaims": ["synthetic fixture baseline grants no publication, academic, or theological authority"],
        "frozen_manifest_sha256": "sha256:" + file_sha256(digest_path),
        "frozen_aggregate_sha256": digest_manifest["aggregate_sha256"],
    }
    expected_digests = completeness_input_digests(baseline, root)
    role_ids = [row["role_id"] for row in baseline["agent_mesh"]["roles"]]
    rejected = [
        {"role": "generic_apologist", "reason": "No apologetic conclusion is in scope; the role would add goal bias without closing a release failure mode."},
        {"role": "generic_theologian", "reason": "No doctrine synthesis or promotion is in scope; a separate human theological authority gate remains required."},
    ]
    risk_routing = [
        {"risk": risk, "route": route, "status": "preserved"}
        for risk, route in EXPECTED_COMPLETENESS_RISK_ROUTES.items()
    ]
    phase_times = {
        "entry": "2026-08-26T17:00:00Z",
        "midflight": "2026-08-26T18:00:00Z",
        "exit": "2026-08-26T19:00:00Z",
    }
    phase_receipts = []
    for index, phase in enumerate(("entry", "midflight", "exit"), start=1):
        phase_receipts.append({
            "phase": phase,
            "input_digests": copy.deepcopy(expected_digests),
            "assigned_roles": list(role_ids),
            "missing_roles": [],
            "rejected_unnecessary_roles": copy.deepcopy(rejected),
            "late_discoveries": expected_late_discoveries(root, phase),
            "risk_routing": copy.deepcopy(risk_routing),
            "result": "pass",
            "reviewer_independence": True,
            "reviewer_role": "role-completeness-auditor",
            "observed_at": phase_times[phase],
            "changed_input_replay": True,
            "reviewer_attempt_id": f"REVIEW-COMPLETENESS-{phase.upper()}-{index:03d}",
            "reviewer_evidence_digest": expected_digests["independent_review_evidence_digest"],
        })
    baseline["completeness_receipt"] = {
        "schema_version": "logos.biblical-evidence.mesh-completeness-receipt.v1",
        "object_type": "deterministic_role_completeness_audit_receipt",
        "trust_zone": "proposed",
        "lifecycle_status": "draft",
        "provenance_note": "Synthetic in-memory known-valid baseline for differential adversarial fixture execution.",
        "reason_for_inclusion": "Prevent pending release evidence from producing vacuous completeness fixture passes.",
        "audit_id": "urn:logos:audit-receipt:biblical-evidence-role-completeness-v1",
        "mutation_performed": False,
        "authority_granted": False,
        "changed_input_invalidates_pass": True,
        "input_digests": expected_digests,
        "phase_receipts": phase_receipts,
        "status": "pass",
    }
    return baseline


def _fixture_findings(documents: dict[str, dict[str, Any]], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    baseline_documents = build_known_valid_fixture_baseline(documents, root)
    fixture_doc = baseline_documents["adversarial_fixtures"]
    baseline = validate_data(
        baseline_documents,
        root,
        check_asset=False,
        check_frozen=False,
        check_fixtures=False,
        check_release=False,
    )
    baseline_findings = set(baseline.findings)
    if baseline_findings:
        findings.append(_finding(
            "fixture_baseline_invalid",
            DOCUMENT_FILES["adversarial_fixtures"],
            "negative fixtures require a known-valid semantic baseline; pre-existing findings cannot satisfy a fixture",
        ))
        return findings
    observed_rules: set[str] = set()
    fixture_ids: set[str] = set()
    for fixture in fixture_doc.get("fixtures", []):
        fixture_id = fixture.get("fixture_id")
        if not fixture_id or fixture_id in fixture_ids:
            findings.append(_finding("fixture_identity", DOCUMENT_FILES["adversarial_fixtures"], "fixture IDs must be unique and non-empty"))
        fixture_ids.add(fixture_id)
        expected_rule = fixture.get("expected_rule")
        observed_rules.add(expected_rule)
        if fixture.get("target") == "strict_parser":
            raw_findings = raw_parser_fixture_findings(fixture.get("mutation"))
            if expected_rule not in {item.rule for item in raw_findings}:
                findings.append(_finding("fixture_expected_rejection", DOCUMENT_FILES["adversarial_fixtures"], f"{fixture_id} did not produce {expected_rule}"))
            continue
        try:
            changed = apply_fixture_mutation(baseline_documents, fixture.get("mutation"))
        except DemoInputError as exc:
            findings.append(_finding("fixture_execution", DOCUMENT_FILES["adversarial_fixtures"], f"{fixture_id}: {exc}"))
            continue
        if _canonical_digest(changed) == _canonical_digest(baseline_documents):
            findings.append(_finding("fixture_execution", DOCUMENT_FILES["adversarial_fixtures"], f"{fixture_id}: mutation did not change the semantic candidate"))
            continue
        result = validate_data(
            changed,
            root,
            check_asset=False,
            check_frozen=False,
            check_fixtures=False,
            check_release=False,
        )
        new_findings = set(result.findings) - baseline_findings
        rules = {item.rule for item in new_findings}
        if expected_rule not in rules:
            findings.append(_finding("fixture_expected_rejection", DOCUMENT_FILES["adversarial_fixtures"], f"{fixture_id} did not produce {expected_rule}"))
    if not EXPECTED_FIXTURE_RULES <= observed_rules:
        findings.append(_finding("fixture_coverage", DOCUMENT_FILES["adversarial_fixtures"], f"missing rule coverage {sorted(EXPECTED_FIXTURE_RULES - observed_rules)}"))
    return findings


def _review_receipt_findings(root: Path, manifest_hash: str, aggregate_hash: Any) -> list[Finding]:
    findings: list[Finding] = []
    attempt_ids: list[str] = []
    for review_name, spec in REVIEW_REPORTS.items():
        relative = spec["path"]
        path = root / PACKAGE_REL / relative
        try:
            receipt = _load_markdown_frontmatter(path)
        except DemoInputError as exc:
            findings.append(_finding("release_evidence_consistency", relative, str(exc)))
            continue
        if set(receipt) != REVIEW_FRONTMATTER_KEYS:
            findings.append(_finding("release_evidence_consistency", relative, "machine review receipt fields differ from the exact contract"))
        expected_envelope = {
            "schema_version": "logos.biblical-evidence.independent-review-receipt.v1",
            "object_type": spec["object_type"],
            "trust_zone": "proposed",
            "lifecycle_status": "draft",
            "review_id": spec["review_id"],
            "review_class": spec["review_class"],
            "reviewer_role": spec["reviewer_role"],
            "reviewer_identity": spec["reviewer_identity"],
            "reviewer_independence": True,
            "independence_basis": "read_only_non_author_no_candidate_mutation",
            "result": "pass",
            "frozen_manifest_sha256": "sha256:" + manifest_hash,
            "frozen_aggregate_sha256": aggregate_hash,
            "blocking_findings": [],
            "mutation_performed": False,
            "authority_granted": False,
            "qualified_human_approval": False,
        }
        drift = {
            field: (receipt.get(field), expected)
            for field, expected in expected_envelope.items()
            if receipt.get(field) != expected
        }
        if drift:
            findings.append(_finding("release_evidence_consistency", relative, f"review identity, result, digest, or authority envelope drifted: {drift}"))
        if not all(isinstance(receipt.get(field), str) and receipt.get(field) for field in ("provenance_note", "reason_for_inclusion")):
            findings.append(_finding("release_evidence_consistency", relative, "review receipt lacks governed provenance metadata"))
        reviewed_scope = receipt.get("reviewed_scope")
        if (
            not isinstance(reviewed_scope, list)
            or len(reviewed_scope) != len(set(reviewed_scope))
            or set(reviewed_scope) != spec["required_scope"]
        ):
            findings.append(_finding("release_evidence_consistency", relative, "reviewed scope is incomplete, duplicated, or wrong-typed"))
        expected_scope_digests = [
            {"path": scope_path, "sha256": "sha256:" + file_sha256(root / scope_path)}
            for scope_path in sorted(spec["required_scope"])
        ]
        if receipt.get("reviewed_scope_digests") != expected_scope_digests:
            findings.append(_finding("release_evidence_consistency", relative, "reviewed scope digests do not bind the exact repository files"))
        residual_nonclaims = receipt.get("residual_nonclaims")
        if not isinstance(residual_nonclaims, list) or not residual_nonclaims or not all(isinstance(value, str) and value for value in residual_nonclaims):
            findings.append(_finding("release_nonclaim_boundary", relative, "review receipt lacks explicit residual nonclaims"))
        attempt_id = receipt.get("reviewer_attempt_id")
        if isinstance(attempt_id, str):
            attempt_ids.append(attempt_id)
        if not isinstance(attempt_id, str) or re.fullmatch(spec["attempt_pattern"], attempt_id) is None:
            findings.append(_finding("release_evidence_consistency", relative, "reviewer attempt identity is invalid"))
        try:
            observed_at = datetime.strptime(receipt.get("observed_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            findings.append(_finding("release_evidence_consistency", relative, "review observation timestamp is not exact UTC"))
        else:
            if observed_at > datetime.now(timezone.utc):
                findings.append(_finding("release_evidence_consistency", relative, "review observation timestamp is in the future"))
    if len(attempt_ids) != len(REVIEW_REPORTS) or len(set(attempt_ids)) != len(REVIEW_REPORTS):
        findings.append(_finding("release_evidence_consistency", "release", "review attempt identities are missing or reused"))
    return findings


def _release_findings(documents: dict[str, dict[str, Any]], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    manifest = documents["release_manifest"]
    locator_receipt = documents["source_locator_check"]
    status = manifest.get("content_status", {})
    false_fields = (
        "runtime_activated",
        "completed_archaeology_corpus",
        "completed_manuscript_corpus",
        "completed_doctrine_corpus",
        "qualified_theological_authority",
        "m7_reviewed_gold",
        "m8_john_built",
        "m7_m8_converged",
    )
    if any(status.get(field) is not False for field in false_fields):
        findings.append(_finding("release_nonclaim_boundary", DOCUMENT_FILES["release_manifest"], "one or more required nonclaims became true"))
    authority = manifest.get("authority", {})
    if any(authority.get(field) is not False for field in ("publication_promotes_claims", "publication_approves_doctrine", "publication_approves_transcription_or_translation", "publication_activates_agents_or_graph")):
        findings.append(_finding("release_nonclaim_boundary", DOCUMENT_FILES["release_manifest"], "publication authority expanded"))
    if manifest.get("asset_release", {}).get("exact_sha256") != EXPECTED_IMAGE_SHA256:
        findings.append(_finding("p66_asset_identity", DOCUMENT_FILES["release_manifest"], "release manifest image hash drifted"))
    expected_metrics = {
        "academic_source_records": len(documents["archaeology_source_pack"].get("source_catalog", [])),
        "bounded_claim_cases": len(documents["archaeology_source_pack"].get("claim_records", [])),
        "graph_nodes": len(documents["evidence_graph"].get("nodes", [])),
        "graph_edges_including_source_claim_projection": len(documents["evidence_graph"].get("edges", [])) + len(documents["evidence_graph"].get("source_claim_edges", [])),
        "separated_mesh_roles": len(documents["agent_mesh"].get("roles", [])),
        "adversarial_fixtures": len(documents["adversarial_fixtures"].get("fixtures", [])),
    }
    if manifest.get("validated_structure_metrics") != expected_metrics:
        findings.append(_finding("release_evidence_consistency", DOCUMENT_FILES["release_manifest"], "validated structure metrics differ from the candidate"))
    expected_source_ids = {
        row.get("source_id")
        for row in documents["archaeology_source_pack"].get("source_catalog", [])
        if isinstance(row, dict)
    }
    locator_checks = locator_receipt.get("checks", [])
    observed_source_ids = {
        row.get("source_id") for row in locator_checks if isinstance(row, dict)
    }
    locator_summary = locator_receipt.get("summary", {})
    if observed_source_ids != expected_source_ids or locator_summary.get("source_count") != len(expected_source_ids):
        findings.append(_finding("source_locator_receipt", DOCUMENT_FILES["source_locator_check"], "source-ID coverage differs from the source pack"))
    if locator_summary.get("dead_or_unresolved") != 0 or any(row.get("http_status") in {0, 404, 410} for row in locator_checks if isinstance(row, dict)):
        findings.append(_finding("source_locator_receipt", DOCUMENT_FILES["source_locator_check"], "one or more source locators is recorded dead or unresolved"))
    if locator_receipt.get("mutation_performed") is not False or len(locator_receipt.get("corrections", [])) != locator_summary.get("bibliographic_corrections_before_freeze"):
        findings.append(_finding("source_locator_receipt", DOCUMENT_FILES["source_locator_check"], "receipt mutation or correction accounting drifted"))
    status_counts = {
        200: sum(row.get("http_status") == 200 for row in locator_checks if isinstance(row, dict)),
        403: sum(row.get("http_status") == 403 for row in locator_checks if isinstance(row, dict)),
        405: sum(row.get("http_status") == 405 for row in locator_checks if isinstance(row, dict)),
    }
    if (
        locator_summary.get("resolved_http_200") != status_counts[200]
        or locator_summary.get("access_controlled_http_403") != status_counts[403]
        or locator_summary.get("method_not_allowed_http_405") != status_counts[405]
        or sum(status_counts.values()) != len(locator_checks)
    ):
        findings.append(_finding("source_locator_receipt", DOCUMENT_FILES["source_locator_check"], "HTTP status accounting is not exact"))
    receipt = documents["validation_receipt"]
    digest_path = root / PACKAGE_REL / "frozen-digests.json"
    try:
        digest_manifest = _load_json(digest_path)
    except DemoInputError as exc:
        findings.append(_finding("release_evidence_consistency", DOCUMENT_FILES["validation_receipt"], str(exc)))
        digest_manifest = {}
    if manifest.get("release_status") != "validated_static_demonstration" or status.get("validated_static_design") is not True:
        findings.append(_finding("release_evidence_consistency", DOCUMENT_FILES["release_manifest"], "release is not marked as validated static design"))
    if receipt.get("status") != manifest.get("release_status") or receipt.get("current_known_blockers") != []:
        findings.append(_finding("release_evidence_consistency", DOCUMENT_FILES["validation_receipt"], "validation receipt and release manifest status disagree or blockers remain"))
    if receipt.get("authority_granted") is not False or receipt.get("mutation_performed") is not False:
        findings.append(_finding("release_nonclaim_boundary", DOCUMENT_FILES["validation_receipt"], "validation receipt grants authority or records mutation"))
    if (
        receipt.get("frozen_manifest_sha256") != "sha256:" + file_sha256(digest_path)
        or receipt.get("frozen_aggregate_sha256") != digest_manifest.get("aggregate_sha256")
    ):
        findings.append(_finding("release_evidence_consistency", DOCUMENT_FILES["validation_receipt"], "validation receipt is not bound to the current frozen manifest"))
    current_manifest_hash = file_sha256(digest_path)
    findings.extend(_review_receipt_findings(root, current_manifest_hash, digest_manifest.get("aggregate_sha256")))
    readme_path = root / PACKAGE_REL / "README.md"
    try:
        readme = readme_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        findings.append(_finding("package_navigation", "README.md", str(exc)))
        return findings
    required_phrases = (
        "not a running",
        "not a completed archaeological corpus",
        "not a completed doctrine",
        "M7/M8 convergence: not started",
        "Licensed [CC BY 4.0]",
        EXPECTED_IMAGE_SHA256,
    )
    lowered = readme.lower()
    for phrase in required_phrases:
        if phrase.lower() not in lowered:
            findings.append(_finding("release_nonclaim_boundary", "README.md", f"missing phrase {phrase!r}"))
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme):
        if target.startswith(("http://", "https://", "#")):
            continue
        if not (readme_path.parent / target).resolve().is_file():
            findings.append(_finding("package_navigation", "README.md", f"missing local link target {target}"))
    return findings


def expected_frozen_paths(root: Path = ROOT) -> list[str]:
    package = root / PACKAGE_REL
    paths: list[str] = []
    if not package.is_dir():
        return paths
    for path in package.rglob("*"):
        if not path.is_file():
            continue
        relative_package = path.relative_to(package).as_posix()
        if relative_package in FROZEN_EXCLUSIONS:
            continue
        paths.append((PACKAGE_REL / relative_package).as_posix())
    return sorted(paths)


def _frozen_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    path = root / PACKAGE_REL / "frozen-digests.json"
    if not path.is_file():
        return [_finding("frozen_digest_manifest", str(path.relative_to(root)), "manifest is missing")]
    try:
        manifest = _load_json(path)
    except DemoInputError as exc:
        return [_finding("frozen_digest_manifest", str(path.relative_to(root)), str(exc))]
    expected = expected_frozen_paths(root)
    rows = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(rows, list):
        return [_finding("frozen_digest_manifest", str(path.relative_to(root)), "files must be an array")]
    raw_paths: list[str] = []
    malformed_rows: list[int] = []
    for index, row in enumerate(rows):
        relative = row.get("path") if isinstance(row, dict) else None
        if not isinstance(relative, str) or not relative:
            malformed_rows.append(index)
            continue
        raw_paths.append(relative)
    if malformed_rows:
        findings.append(_finding("frozen_digest_manifest", str(path.relative_to(root)), f"rows with invalid paths: {malformed_rows}"))
    if len(rows) != len(expected):
        findings.append(_finding("frozen_digest_manifest", str(path.relative_to(root)), f"row count differs: expected={len(expected)}, observed={len(rows)}"))
    duplicate_paths = sorted({relative for relative in raw_paths if raw_paths.count(relative) > 1})
    if duplicate_paths:
        findings.append(_finding("frozen_digest_manifest", str(path.relative_to(root)), f"duplicate paths: {duplicate_paths}"))
    if raw_paths != sorted(raw_paths):
        findings.append(_finding("frozen_digest_manifest", str(path.relative_to(root)), "paths are not sorted"))
    observed = {
        row["path"]: row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("path"), str) and row.get("path")
    }
    if set(observed) != set(expected):
        findings.append(_finding("frozen_digest_manifest", str(path.relative_to(root)), f"path set differs: missing={sorted(set(expected)-set(observed))}, extra={sorted(set(observed)-set(expected))}"))
    for relative in sorted(set(expected) & set(observed)):
        target = root / Path(relative)
        row = observed[relative]
        if row.get("sha256") != file_sha256(target) or row.get("bytes") != target.stat().st_size:
            findings.append(_finding("frozen_digest_mismatch", relative, "hash or byte count differs"))
    if manifest.get("asset_sha256") != EXPECTED_IMAGE_SHA256:
        findings.append(_finding("p66_asset_identity", str(path.relative_to(root)), "asset digest pin drifted"))
    canonical_rows = [observed[relative] for relative in sorted(observed)]
    if manifest.get("file_count") != len(expected) or manifest.get("aggregate_sha256") != _canonical_digest(canonical_rows):
        findings.append(_finding("frozen_digest_manifest", str(path.relative_to(root)), "file count or aggregate digest differs"))
    if set(manifest.get("excluded_paths", [])) != FROZEN_EXCLUSIONS:
        findings.append(_finding("frozen_digest_manifest", str(path.relative_to(root)), "exclusion set differs from validator policy"))
    return findings


def validate_data(
    documents: dict[str, dict[str, Any]],
    root: Path = ROOT,
    *,
    check_asset: bool = True,
    check_frozen: bool = True,
    check_fixtures: bool = True,
    check_release: bool = True,
) -> ValidationResult:
    findings: list[Finding] = []
    findings.extend(_document_envelope_findings(documents))
    findings.extend(_metadata_findings(documents))
    findings.extend(_asset_findings(documents, root, check_asset))
    findings.extend(_p66_findings(documents))
    findings.extend(_academic_findings(documents))
    findings.extend(_graph_findings(documents))
    findings.extend(_mesh_findings(documents, root))
    if check_release:
        findings.extend(_release_findings(documents, root))
    if check_fixtures:
        findings.extend(_fixture_findings(documents, root))
    if check_frozen:
        findings.extend(_frozen_findings(root))
    return ValidationResult(
        findings=tuple(sorted(set(findings))),
        metrics={
            "documents": len(documents),
            "sources": len(documents["archaeology_source_pack"].get("source_catalog", [])),
            "academic_claims": len(documents["archaeology_source_pack"].get("claim_records", [])),
            "graph_nodes": len(documents["evidence_graph"].get("nodes", [])),
            "graph_edges": len(documents["evidence_graph"].get("edges", [])) + len(documents["evidence_graph"].get("source_claim_edges", [])),
            "mesh_roles": len(documents["agent_mesh"].get("roles", [])),
            "negative_fixtures": len(documents["adversarial_fixtures"].get("fixtures", [])),
            "frozen_files": len(expected_frozen_paths(root)),
        },
    )


def validate_repository(root: Path = ROOT) -> ValidationResult:
    findings: list[Finding] = []
    package = root / PACKAGE_REL
    for relative in sorted(REQUIRED_PACKAGE_FILES):
        if not (package / relative).is_file():
            findings.append(_finding("required_file", (PACKAGE_REL / relative).as_posix(), "file is missing"))
    try:
        documents = load_documents(root)
    except DemoInputError as exc:
        findings.append(_finding("input_error", str(PACKAGE_REL), str(exc)))
        return ValidationResult(tuple(findings), {"documents": 0})
    result = validate_data(documents, root)
    return ValidationResult(tuple(sorted(set(findings) | set(result.findings))), result.metrics)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit a machine-readable receipt")
    args = parser.parse_args()
    try:
        result = validate_repository(ROOT)
    except (OSError, DemoInputError) as exc:
        payload = {"status": "error", "error": str(exc)}
        print(json.dumps(payload, indent=2) if args.json else f"ERROR: {exc}")
        return 2
    payload = {
        "status": "pass" if result.passed else "fail",
        "validator": "validate_biblical_evidence_demo.py",
        "offline": True,
        "mutation_performed": False,
        "metrics": result.metrics,
        "findings": [finding.render() for finding in result.findings],
        "nonclaims": [
            "historical truth",
            "transcription or translation accuracy",
            "scholarly consensus",
            "qualified expert or theological approval",
            "runtime readiness",
        ],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif result.passed:
        print("Biblical evidence demonstration validation passed.")
        print(json.dumps(result.metrics, sort_keys=True))
    else:
        print("Biblical evidence demonstration validation failed:")
        for finding in result.findings:
            print(f"- {finding.render()}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
