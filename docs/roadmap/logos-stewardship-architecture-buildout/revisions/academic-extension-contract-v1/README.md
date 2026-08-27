---
object_type: academic_extension_contract_revision_packet
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-08-25 as the task-local evidence and replay packet for Academic Extension Contract v1."
reason_for_inclusion: "Keep the exact scope, standards evidence, human gates, mesh, fixtures, and validation receipts together without activating any domain pack."
---

# Academic Extension Contract V1 revision packet

This packet accompanies
[`docs/governance/academic-extension-contract.md`](../../../../governance/academic-extension-contract.md).
It is specification-only. It contains no runtime, source ingestion, real academic
assertions, doctrine changes, approved domain packs, or publication authority.

## Read order

1. `SCOPE.md`
2. `standards-evidence.yaml`
3. `human-decision-gates.yaml`
4. `acceptance-test-matrix.yaml`
5. `mesh/agent-mesh.v2.json`
6. `frozen-digests.json` for reviewed canonical content identities and the exact replay algorithm (UTF-8 line endings normalize to LF; non-UTF-8 files retain exact binary bytes)
7. `validation-receipt.json` after deterministic validation
8. `independent-review-receipt.md` after a non-author review

The canonical machine contracts are under `schemas/academic_extensions/`; the
empty production entry point is
`governance/registry/ACADEMIC_DOMAIN_PACK_REGISTRY.yaml`.
