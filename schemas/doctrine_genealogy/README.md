---
object_type: schema_family_readme
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-07-06 by Codex as PR-3 of the Fable kernel implementation sequence, after PR-2 vocabulary surfaces merged."
reason_for_inclusion: "Give future doctrine-genealogy validators, examples, and repo scaffolds a deterministic map of the non-authorizing schema standards derived from Fable Kernels A-D and owner decisions D1-D10."
---

# Doctrine-Genealogy Schemas

These JSON Schemas are governance-owned standards for the planned
`logos-doctrine-genealogy` repo. They do not create doctrine data records,
source imports, graph truth, reviewed lineage, or a new repository.

Every schema is draft, non-authorizing, and governed by owner decisions D1-D10.
Kernel E applies: schema defaults may use only floor values such as
`unclassified_candidate`, `historical_description`, `retrieval_candidate`, and
`review_status: unreviewed`.

PR-5 worked examples must carry top-level `trust_zone: proposed`,
`lifecycle_status: draft`, and `review_status: unreviewed`. The node, edge, and
packet schemas therefore allow and require those metadata fields without
promoting the example content.

## Schema Files

- `date_block.v1.schema.json` - shared Kernel A4 date discipline.
- `doctrine_provenance.v1.schema.json` - Kernel C1 provenance block.
- `doctrine_node.v1.schema.json` - Kernel A2 node standards for the eight doctrine-genealogy node types.
- `genealogy_edge.v1.schema.json` - Kernel A3 genealogy edge standard.
- `evidence_packet.v1.schema.json` - Kernel D1 evidence packet standard.
- `gate_trigger_registry.v1.yaml` - Kernel C2-C3 gate trigger classes and Scripture-repo policy references.

## Validators

PR-4 wires these validators into `scripts/run_validation_suite.py`:

- `scripts/validate_doctrine_vocabulary.py`
- `scripts/validate_doctrine_provenance.py`
- `scripts/validate_genealogy_edges.py`
- `scripts/validate_evidence_packet.py`
- `scripts/validate_gate_triggers.py`
- `scripts/validate_codex_theology_tripwire.py`

Focused pytest coverage lives in `tests/test_doctrine_genealogy_validators.py`.

Draft schema-conformance examples live in
`../../examples/doctrine_genealogy/`.

## Non-Authorizations

These schemas do not authorize:

- doctrine or genealogy data records;
- source imports;
- Scripture or chunk changes;
- graph, retrieval, or vector truth;
- reviewed-lineage promotion;
- repo creation;
- new relationship verbs, enum values, tradition profiles, or authority rungs.
